#!/usr/bin/env python3

import os
import subprocess
from typing import Any
import gi  # type: ignore
import sys
import threading
import warnings
from setproctitle import setproctitle
import signal
from utils.arg_parser import ArgParse, sprint
from utils.pair import Pair
from utils.logger import LogLevel, Logger
from utils.settings import load_settings, ensure_config_dir
from utils.translations import English, Spanish, Portuguese, get_translations
from utils.warning_suppressor import suppress_specific_warnings

# Initialize GTK before imports
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, GLib, Gdk  # type: ignore

# Initialize GDK threading - using context manager to suppress specific deprecation warnings
with suppress_specific_warnings(DeprecationWarning, "Gdk.threads_init is deprecated"):
    Gdk.threads_init()

from ui.main_window import BetterControl
from utils.dependencies import check_all_dependencies
from tools.bluetooth import restore_last_sink
from ui.css.animations import load_animations_css

# Set up signal handling
def signal_handler(sig, frame):
    print("Exiting gracefully...")
    if Gtk.main_level() > 0:
        Gtk.main_quit()
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize environment for GTK
    os.environ['PYTHONUNBUFFERED'] = '1'  # Prevent buffering issues

    # Prevent segfault with some environment variables
    os.environ['DBUS_FATAL_WARNINGS'] = '0'  # Prevent DBus warnings from crashing
    os.environ['GST_GL_XINITTHREADS'] = '1'  # For systems using GLX

    # Additional environment variables to prevent memory issues
    os.environ['G_SLICE'] = 'always-malloc'  # Use standard malloc instead of custom allocator
    os.environ['MALLOC_CHECK_'] = '2'  # Enable memory allocation checking
    os.environ['MALLOC_PERTURB_'] = '0'  # Initialize allocated memory with zeros

    arg_parser = ArgParse(sys.argv)

    if arg_parser.find_arg(("-h", "--help")):
        arg_parser.print_help_msg(sys.stdout)
        sys.exit(0)

    logging = Logger(arg_parser)
    logging.log(LogLevel.Info, "Starting Better Control")

    # Create necessary directories at startup
    # 1. Ensure config directory exists
    ensure_config_dir(logging)

    # 2. Create temp directory for QR codes and other temporary files
    try:
        temp_dir = os.path.join("/tmp", "better-control")
        os.makedirs(temp_dir, exist_ok=True)
        logging.log(LogLevel.Info, f"Created temporary directory at {temp_dir}")
    except Exception as e:
        logging.log(LogLevel.Error, f"Error creating temporary directory: {e}")

    # Load settings after ensuring directories exist
    settings = load_settings(logging)
    lang = settings.get("language", "en")
    logging.log(LogLevel.Info, f"Loaded language setting from settings: {lang}")
    txt = get_translations(logging, lang)

    # Load animations CSS globally
    animations_css = load_animations_css()
    logging.log(LogLevel.Info, "Loaded animations CSS")

    if not check_all_dependencies(logging) and not arg_parser.find_arg(("-f", "--force")):
        logging.log(
            LogLevel.Error,
            "Missing required dependencies. Please install them and try again or use -f to force start.",
        )
        sys.exit(1)

    # Use a try/except to catch any errors during startup
    try:
        # Small delay to ensure all initialization is complete
        import time
        time.sleep(0.1)  # 100ms delay

        # Create the GTK window with proper error handling
        logging.log(LogLevel.Info, "Creating main window")
        win = BetterControl(txt, arg_parser, logging)
        logging.log(LogLevel.Info, "Main window created successfully")

        # Set the proctitle to "better-control" so that it can show up under top, pidof, etc with this name
        setproctitle("better-control")

        # Prevents startup delay - ensure thread is properly managed
        # Only start the audio thread after window creation to avoid race conditions
        audio_thread = threading.Thread(target=restore_last_sink, args=(logging,), daemon=True)
        audio_thread.start()

        option: Any = []
        if arg_parser.find_arg(("-s", "--size")):
            option = arg_parser.option_arg(("-s", "--size"))

            if option == None or 'x' not in option:
                logging.log(LogLevel.Error, "Invalid window size")
                exit(1)
            else:
                option = option.split('x')
        else:
            option = [900, 600]

        win.set_default_size(int(option[0]), int(option[1]))
        win.resize(int(option[0]), int(option[1]))
        win.connect("destroy", Gtk.main_quit)
        win.show_all()

        # Make the window float on hyprland
        if "hyprland" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower():
            try:
                subprocess.run(
                    [
                        "hyprctl",
                        "keyword",
                        "windowrule",
                        "float,class:^(better_control.py)$",
                    ],
                    check=False  # Don't raise exception if command fails
                )
            except Exception as e:
                logging.log(LogLevel.Warn, f"Failed to set hyprland window rule: {e}")

        # Make the window float on sway
        elif "sway" in os.environ.get("SWAYSOCK", "").lower():
            try:
                subprocess.run(
                    [
                        "swaymsg",
                        "for_window",
                        '[app_id="^better_control.py$"]',
                        "floating",
                        "enable"
                    ],
                    check=False  # Don't raise exception if command fails
                )
            except Exception as e:
                logging.log(LogLevel.Warn, f"Failed to set sway window rule: {e}")

        # Start GTK main loop with error handling and proper thread synchronization
        # Use context manager to suppress specific deprecation warnings
        with suppress_specific_warnings(DeprecationWarning, "Gdk.threads_enter is deprecated"):
            Gdk.threads_enter()
        try:
            Gtk.main()
        except KeyboardInterrupt:
            logging.log(LogLevel.Info, "Keyboard interrupt detected, exiting...")
            Gtk.main_quit()
            sys.exit(0)
        except Exception as e:
            logging.log(LogLevel.Error, f"Error in GTK main loop: {e}")
            sys.exit(1)
        finally:
            # Always leave GDK threading context
            with suppress_specific_warnings(DeprecationWarning, "Gdk.threads_leave is deprecated"):
                Gdk.threads_leave()

    except Exception as e:
        logging.log(LogLevel.Error, f"Fatal error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
