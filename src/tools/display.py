#!/usr/bin/env python3

import subprocess
from typing import Dict, List
import logging

def get_brightness() -> int:
    """Get the current brightness level

    Returns:
        int: current brightness percentage
    """
    try:
        output = subprocess.getoutput("brightnessctl g")
        max_brightness = int(subprocess.getoutput("brightnessctl m"))
        current_brightness = int(output)
        return int((current_brightness / max_brightness) * 100)
    except Exception as e:
        logging.error(f"Error getting brightness: {e}")
        return 0

def set_brightness(value: int) -> None:
    """Set the brightness level

    Args:
        value (int): brightness percentage to set
    """
    try:
        subprocess.run(["brightnessctl", "s", f"{value}%"], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error setting brightness: {e}")

def get_displays() -> List[str]:
    """Get list of connected displays

    Returns:
        List[str]: List of display names
    """
    try:
        output = subprocess.getoutput("xrandr --query")
        displays = []
        for line in output.split("\n"):
            if " connected" in line:
                displays.append(line.split()[0])
        return displays
    except Exception as e:
        logging.error(f"Error getting displays: {e}")
        return []

def get_display_info(display: str) -> Dict[str, str]:
    """Get information about a specific display

    Args:
        display (str): Display name

    Returns:
        Dict[str, str]: Dictionary containing display information
    """
    try:
        output = subprocess.getoutput(f"xrandr --query --verbose | grep -A10 {display}")
        info = {}
        for line in output.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        return info
    except Exception as e:
        logging.error(f"Error getting display info: {e}")
        return {}
