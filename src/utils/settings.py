#!/usr/bin/env python3

import json
import os
from utils.logger import LogLevel, Logger

CONFIG_DIR = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
CONFIG_PATH = os.path.join(CONFIG_DIR, "better-control")
SETTINGS_FILE = os.path.join(CONFIG_PATH, "settings.json")

def ensure_config_dir(logging: Logger) -> None:
    """Ensure the config directory exists

    Args:
        logging (Logger): Logger instance
    """
    try:
        logging.log(LogLevel.Info, f"Ensuring config directory exists at {CONFIG_PATH}")
        os.makedirs(CONFIG_PATH, exist_ok=True)
        logging.log(LogLevel.Info, f"Config directory check complete")
    except Exception as e:
        logging.log(LogLevel.Error, f"Error creating config directory: {e}")

def load_settings(logging: Logger) -> dict:
    """Load settings from the settings file

    Returns:
        dict: Dictionary containing settings
    """
    # Ensure config directory exists before attempting to load settings
    ensure_config_dir(logging)

    settings = {"visibility": {}, "positions": {}}
    logging.log(LogLevel.Info, f"Loading settings from {SETTINGS_FILE}")
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                # Handle legacy format (just visibility settings)
                if isinstance(data, dict) and not ("visibility" in data and "positions" in data):
                    settings["visibility"] = data
                    logging.log(LogLevel.Info, "Loaded legacy format settings")
                else:
                    settings = data
                    logging.log(LogLevel.Info, f"Loaded settings: {list(settings.keys())}")
                    if "language" in settings:
                        logging.log(LogLevel.Info, f"Language setting found: {settings['language']}")
                    else:
                        logging.log(LogLevel.Warn, "No language setting found in settings file")
        except Exception as e:
            logging.log(LogLevel.Error, f"Error loading settings: {e}")
    else:
        logging.log(LogLevel.Warn, f"Settings file not found at {SETTINGS_FILE}, using defaults")
    return settings

def save_settings(settings: dict, logging: Logger) -> None:
    """Save settings to the settings file
    Args:
        settings (dict): Settings to save
    """
    try:
        # Ensure the config directory exists
        ensure_config_dir(logging)

        # Log what we're saving
        logging.log(LogLevel.Info, f"Saving settings to {SETTINGS_FILE}")
        logging.log(LogLevel.Info, f"Settings keys: {list(settings.keys())}")

        # Ensure language setting is preserved
        if "language" in settings:
            logging.log(LogLevel.Info, f"Saving language setting: {settings['language']}")
        else:
            # Try to load existing settings to preserve language
            if os.path.exists(SETTINGS_FILE):
                try:
                    with open(SETTINGS_FILE, "r") as f:
                        existing_settings = json.load(f)
                        if "language" in existing_settings:
                            settings["language"] = existing_settings["language"]
                            logging.log(LogLevel.Info, f"Preserved existing language setting: {settings['language']}")
                except Exception as e:
                    logging.log(LogLevel.Error, f"Error loading existing settings: {e}")
            else:
                logging.log(LogLevel.Warn, "No language setting found in settings to save")

        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
            logging.log(LogLevel.Info, "Settings saved successfully")

    except Exception as e:
        logging.log(LogLevel.Error, f"Error saving settings: {e}")
