import os
import subprocess
import gi  
import sys
import threading
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

    if arg_parser.find_arg(("-h", "--help")):
        arg_parser.print_help_msg(sys.stdout)

    if arg_parser.find_arg(("-v", "--version")):
        sprint(sys.stdout, "5.3")
        exit(0)

    if arg_parser.find_arg(("-f", "--force")) and not check_all_dependencies():
        print("Missing required dependencies. Please install them and try again.")
        exit(1)

    # Prevents startup delay
    audio_thread = threading.Thread(target=restore_last_sink, daemon=True)
    audio_thread.start()

    try:
        win = BetterControl(arg_parser, None)  # Pass None as logging is removed
        win.set_default_size(1000, 700)
        win.resize(1000, 700)
        win.connect("destroy", Gtk.main_quit)
        win.show_all()

        # Check for updates
        check_for_updates(win)

        # Hyprland floating window rule
        if "hyprland" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower():
            subprocess.run(
                ["hyprctl", "keyword", "windowrule", "float,class:^(better_control.py)$"]
            )

        Gtk.main()
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)
