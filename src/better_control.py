#!/usr/bin/env python3 

import os
import subprocess
import gi  # type: ignore
import sys
import logging
from utils.arg_parser import ArgParse, eprint

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # type: ignore

from ui.main_window import BetterControl
from utils.dependencies import check_all_dependencies

if __name__ == "__main__":
    arg_parser = ArgParse(sys.argv)

    if arg_parser.find_arg(("-h", "--help")):
        arg_parser.print_help_msg(sys.stdout)

    if arg_parser.find_arg(("-v", "--version")):
        eprint(sys.stdout, "5.3")
        exit(0)

    if arg_parser.find_arg(("-f", "--force")) and not check_all_dependencies():
        logging.error("Missing required dependencies. Please install them and try again.")
        sys.exit(1)

     # Configure logging
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s [LOG] %(message)s", datefmt="%H:%M:%S"
    )

    try:
        # Create the main window
        win = BetterControl(arg_parser)
        win.set_default_size(1000, 700)
        win.resize(1000, 700)  # Ensure correct placement
        win.connect("destroy", Gtk.main_quit)
        win.show_all()

        # Ensure Hyprland floating works
        if "hyprland" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower():
            subprocess.run(
                ["hyprctl", "keyword", "windowrulev2", "float,class:^(better_control.py)$"]
            )

        Gtk.main()
    except Exception as e:
        logging.error(f"Error starting application: {e}")
        sys.exit(1)
