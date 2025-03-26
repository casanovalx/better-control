#!/usr/bin/env python3

import gi
import sys
import logging
import argparse

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from ui.main_window import BetterControl
from utils.dependencies import check_all_dependencies

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Better Control - A system control center.")

    # Volume
    parser.add_argument("--volume", "-v", action="store_true", help="Start with the Volume tab open.")

    # Wifi
    parser.add_argument("--wifi", "-w", action="store_true", help="Start with the Wi-Fi tab open.")

    # Bluetooth
    parser.add_argument("--bluetooth", "-b", action="store_true", help="Start with the Bluetooth tab open.")

    # Battery
    parser.add_argument("--battery", "-B", action="store_true", help="Start with the Battery tab open.")

    # Display
    parser.add_argument("--display", "-d", action="store_true", help="Start with the Display tab open.")

    # Force dependencies
    parser.add_argument("--force", "-f", action="store_true", help="Forces all dependencies to be installed.")

    return parser.parse_args()

def main():
    """Main entry point of the application"""
    # Parse command line arguments
    args = parse_arguments()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [LOG] %(message)s',
        datefmt='%H:%M:%S'
    )

    # Check dependencies if --force is used
    if args.force and not check_all_dependencies():
        logging.error("Missing required dependencies. Please install them and try again.")
        sys.exit(1)

    try:
        # Create and show the main window
        win = BetterControl(args)
        win.connect("destroy", Gtk.main_quit)
        win.show_all()
        Gtk.main()
    except Exception as e:
        logging.error(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()