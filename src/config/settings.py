#!/usr/bin/env python3

import json
import os
import logging
import constants
from constants import CONFIG_PATH, SETTINGS_FILE

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