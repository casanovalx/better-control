import os
import subprocess
import gi  
import sys
import threading
import logging  
import requests 
from utils.arg_parser import ArgParse, sprint
from utils.pair import Pair

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  
from ui.main_window import BetterControl
from utils.dependencies import check_all_dependencies
from tools.bluetooth import restore_last_sink


if __name__ == "__main__":
    arg_parser = ArgParse(sys.argv)  
    logger = Logging(arg_parser)  

    if arg_parser.find_arg(("-h", "--help")):
        arg_parser.print_help_msg(sys.stdout)

    if arg_parser.find_arg(("-v", "--version")):
        sprint(sys.stdout, "5.3")
        exit(0)

    if arg_parser.find_arg(("-f", "--force")) and not check_all_dependencies(logger):
        logger.log(
            LogLevel.Error,
            "Missing required dependencies. Please install them and try again.",
        )

    # Prevents startup delay
    audio_thread = threading.Thread(target=restore_last_sink, args=(logger,), daemon=True)
    audio_thread.start()

    try:
        win = BetterControl(arg_parser, logger)  
        win.set_default_size(1000, 700)
        win.resize(1000, 700)
        win.connect("destroy", Gtk.main_quit)
        win.show_all()

        # Check for updates
        check_for_updates(logger, win)

        # Hyprland floating window rule
        if "hyprland" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower():
            subprocess.run(
                ["hyprctl", "keyword", "windowrule", "float,class:^(better_control.py)$"]
            )

        Gtk.main()
    except Exception as e:
        logger.log(LogLevel.Error, f"Error starting application: {e}")  
        sys.exit(1)
