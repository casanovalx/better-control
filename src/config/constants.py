#!/usr/bin/env python3

import os

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
    (
        "gammastep",
        "Blue Light Filter",
        "- Debian/Ubuntu: sudo apt install gammastep\n- Arch Linux: sudo pacman -S gammastep\n- Fedora: sudo dnf install gammastep",
    ),
]