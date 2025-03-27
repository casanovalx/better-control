import os
import subprocess
import gi  
import sys
import threading
import logging  
import requests 
from utils.arg_parser import ArgParse, sprint
from utils.pair import Pair
from utils.Logging import LogLevel, Logging
from .logging import LogLevel, Logging


gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  
from ui.main_window import BetterControl
from utils.dependencies import check_all_dependencies
from tools.bluetooth import restore_last_sink

localdesktop = "/usr/share/applications/better-control.desktop"
githubdesktop = "https://raw.githubusercontent.com/quantumvoid0/better-control/refs/heads/main/src/control.desktop"

def get_version_from_desktop(file_path):
    try:
        with open(file_path, "r") as f:
            for line in f:
                if line.startswith("Version="):
                    return line.strip().split("=")[1]
    except Exception:
        return None  

def get_latest_version_from_github(logger):
    """Fetches the latest .desktop file from GitHub and extracts the version."""
    try:
        response = requests.get(githubdesktop, timeout=5)
        response.raise_for_status()

        for line in response.text.splitlines():
            if line.startswith("Version="):
                return line.strip().split("=")[1]
    except Exception as e:
        logger.log(LogLevel.Warn, f"Failed to fetch latest version from GitHub: {e}")
    return None

def check_for_updates(logger, win):
    """Compare installed and latest versions, and show update popup if needed"""
    installed_version = get_version_from_desktop(localdesktop)
    latest_version = get_latest_version_from_github(logger)

    if installed_version and latest_version:
        logger.log(LogLevel.Info, f"Installed: {installed_version}, Latest: {latest_version}")
        if installed_version != latest_version:
            show_update_popup(win, latest_version, logger)  #pas logger

def show_update_popup(win, new_version, logger):
    """Displays a GTK popup when an update is available"""
    dialog = Gtk.MessageDialog(
        transient_for=win,  
        flags=0,
        message_type=Gtk.MessageType.INFO,
        buttons=Gtk.ButtonsType.OK,
        text="New Update Available!",
    )
    logger.log(LogLevel.Warn, "Update available") 
    dialog.format_secondary_text(f"A new version ({new_version}) is available.\nPlease update via GitHub or AUR.")
    dialog.run()
    dialog.destroy()

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
