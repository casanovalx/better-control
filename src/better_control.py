#!/usr/bin/env python3

import os
import subprocess
import gi  # type: ignore
import sys
import logging
import argparse

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # type: ignore

from ui.main_window import BetterControl
from utils.dependencies import check_all_dependencies

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Better Control - A system control center."
    )

    parser.add_argument(
        "--volume", "-v", action="store_true", help="Start with the Volume tab open."
    )
    parser.add_argument(
        "--wifi", "-w", action="store_true", help="Start with the Wi-Fi tab open."
    )
    parser.add_argument(
        "--bluetooth", "-b", action="store_true", help="Start with the Bluetooth tab open."
    )
    parser.add_argument(
        "--battery", "-B", action="store_true", help="Start with the Battery tab open."
    )
    parser.add_argument(
        "--display", "-d", action="store_true", help="Start with the Display tab open."
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Forces all dependencies to be installed.",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s [LOG] %(message)s", datefmt="%H:%M:%S"
    )

    # Check dependencies if --force is used
    if args.force and not check_all_dependencies():
        logging.error("Missing required dependencies. Please install them and try again.")
        sys.exit(1)

    try:
        # Create the main window
        win = BetterControl(args)
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
