#!/usr/bin/env python3

import json
import os
import logging

# Get configuration directory from XDG standard or fallback to ~/.config
CONFIG_DIR = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
CONFIG_PATH = os.path.join(CONFIG_DIR, "better-control")
SETTINGS_FILE = os.path.join(CONFIG_PATH, "settings.json")

# Dependencies used by the program
DEPENDENCIES = [
    (
        "powerprofilesctl",
        "Power Profiles Control",
        "- Debian/Ubuntu: sudo apt install power-profiles-daemon\n- Arch Linux: sudo pacman -S power-profiles-daemon\n- Fedora: sudo dnf install power-profiles-daemon",
    ),
    (
        "nmcli",
        "Network Manager CLI",
        "- Install NetworkManager package for your distro",
    ),
    (
        "bluetoothctl",
        "Bluetooth Control",
        "- Debian/Ubuntu: sudo apt install bluez\n- Arch Linux: sudo pacman -S bluez bluez-utils\n- Fedora: sudo dnf install bluez",
    ),
    (
        "pactl",
        "PulseAudio Control",
        "- Install PulseAudio or PipeWire depending on your distro",
    ),
    (
        "brightnessctl",
        "Brightness Control",
        "- Debian/Ubuntu: sudo apt install brightnessctl\n- Arch Linux: sudo pacman -S brightnessctl\n- Fedora: sudo dnf install brightnessctl",
    ),
]

def load_settings() -> dict:
    """Load settings from the settings file
    
    Returns:
        dict: Dictionary containing settings
    """
    settings = {"visibility": {}, "positions": {}}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                # Handle legacy format (just visibility settings)
                if isinstance(data, dict) and not ("visibility" in data and "positions" in data):
                    settings["visibility"] = data
                else:
                    settings = data
        except Exception as e:
            logging.error(f"Error loading settings: {e}")
    return settings

def save_settings(settings: dict) -> None:
    """Save settings to the settings file
    
    Args:
        settings (dict): Settings to save
    """
    try:
        # Ensure the config directory exists
        os.makedirs(CONFIG_PATH, exist_ok=True)
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        logging.error(f"Error saving settings: {e}") 