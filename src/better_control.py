#!/usr/bin/env python3

import os
import subprocess
import gi  # type: ignore
import sys
import threading
from utils.arg_parser import ArgParse, sprint
from utils.pair import Pair
from utils.logger import LogLevel, Logger

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # type: ignore
from ui.main_window import BetterControl
from utils.dependencies import check_all_dependencies
from tools.bluetooth import restore_last_sink


if __name__ == "__main__":
    arg_parser = ArgParse(sys.argv)

    if arg_parser.find_arg(("-h", "--help")):
        arg_parser.print_help_msg(sys.stdout)

    if arg_parser.find_arg(("-v", "--version")):
        sprint(sys.stdout, "5.3")
        exit(0)

    logging = Logger(arg_parser)

    if arg_parser.find_arg(("-f", "--force")) and not check_all_dependencies(logging):
        logging.log(
            LogLevel.Error,
            "Missing required dependencies. Please install them and try again.",
        )

    # Prevents startup delay
    audio_thread = threading.Thread(target=restore_last_sink, args=(logging,), daemon=True)
    audio_thread.start()

    try:
        win = BetterControl(arg_parser, logging)
        win.set_default_size(900, 600)
        win.resize(900, 600)
        win.connect("destroy", Gtk.main_quit)
        win.show_all()

        # Hyprland shenanigans
        if "hyprland" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower():
            subprocess.run(
                [
                    "hyprctl",
                    "keyword",
                    "windowrule",
                    "float,class:^(better_control.py)$",
                ]
            )

        Gtk.main()
    except Exception as e:
        logging.log(LogLevel.Error, f"Error starting application: {e}")
        sys.exit(1)
