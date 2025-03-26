#!/usr/bin/env python3

import subprocess
import typing
import logging
import re

def get_volume() -> int:
    """Get current volume level

    Returns:
        int: Volume percentage
    """
    try:
        output = subprocess.getoutput("pactl get-sink-volume @DEFAULT_SINK@")
        volume = int(output.split("/")[1].strip().strip("%"))
        return volume
    except Exception as e:
        logging.error(f"Error getting volume: {e}")
        return 0

def set_volume(value: int) -> None:
    """Set volume level

    Args:
        value (int): Volume percentage
    """
    try:
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{value}%"], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error setting volume: {e}")

def get_mute_state() -> bool:
    """Get mute state

    Returns:
        bool: True if muted, False otherwise
    """
    try:
        output = subprocess.getoutput("pactl get-sink-mute @DEFAULT_SINK@")
        return "yes" in output.lower()
    except Exception as e:
        logging.error(f"Error getting mute state: {e}")
        return False

def toggle_mute() -> None:
    """Toggle mute state"""
    try:
        subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error toggling mute: {e}")

def get_sinks() -> typing.List[typing.Dict[str, str]]:
    """Get list of audio sinks (output devices)

    Returns:
        typing.List[typing.Dict[str, str]]: List of sink dictionaries
    """
    try:
        output = subprocess.getoutput("pactl list sinks")
        sinks = []
        current_sink = {}

        for line in output.split("\n"):
            if line.startswith("Sink #"):
                if current_sink:
                    sinks.append(current_sink)
                current_sink = {"id": line.split("#")[1].strip()}
            elif ":" in line and current_sink:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                if key == "Name":
                    current_sink["name"] = value
                elif key == "Description":
                    current_sink["description"] = value

        if current_sink:
            sinks.append(current_sink)

        return sinks
    except Exception as e:
        logging.error(f"Error getting sinks: {e}")
        return []

def get_sources() -> typing.List[typing.Dict[str, str]]:
    """Get list of audio sources (input devices)

    Returns:
        typing.List[typing.Dict[str, str]]: List of source dictionaries
    """
    try:
        output = subprocess.getoutput("pactl list sources")
        sources = []
        current_source = {}

        for line in output.split("\n"):
            if line.startswith("Source #"):
                if current_source:
                    sources.append(current_source)
                current_source = {"id": line.split("#")[1].strip()}
            elif ":" in line and current_source:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                if key == "Name":
                    current_source["name"] = value
                elif key == "Description":
                    current_source["description"] = value

        if current_source:
            sources.append(current_source)

        return sources
    except Exception as e:
        logging.error(f"Error getting sources: {e}")
        return []

def get_applications() -> typing.List[typing.Dict[str, str]]:
    """Get list of applications playing audio

    Returns:
        typing.List[typing.Dict[str, str]]: List of application dictionaries
    """
    try:
        output = subprocess.getoutput("pactl list sink-inputs")
        apps = []
        current_app = {}

        for line in output.split("\n"):
            line = line.strip()
            if line.startswith("Sink Input #"):
                if current_app:
                    # Only add apps that have a name and volume
                    if "name" in current_app and "volume" in current_app:
                        apps.append(current_app)
                current_app = {"id": line.split("#")[1].strip()}
            elif ":" in line and current_app:
                key, value = [x.strip() for x in line.split(":", 1)]

                # Application name
                if "application.name" in key:
                    current_app["name"] = value.strip('"')
                elif "media.name" in key and "name" not in current_app:
                    # Fallback to media.name if application.name is not available
                    current_app["name"] = value.strip('"')
                elif "application.process.binary" in key and "name" not in current_app:
                    # Fallback to process name if no other name is available
                    current_app["name"] = value.strip('"')
                # Application icon
                elif "application.icon_name" in key:
                    current_app["icon"] = value.strip('"')
                # Volume
                elif "Volume:" in key:
                    try:
                        # Extract volume percentage from format like "front-left: 65536 / 100% / -0.00 dB,   front-right: 65536 / 100% / -0.00 dB"
                        volume_match = re.search(r"(\d+)%", value)
                        if volume_match:
                            current_app["volume"] = int(volume_match.group(1))
                    except (ValueError, IndexError) as e:
                        logging.warning(f"Error parsing volume from '{value}': {e}")
                        current_app["volume"] = 100  # Default to 100% if parsing fails

        # Add the last app if it exists and has required fields
        if current_app and "name" in current_app and "volume" in current_app:
            apps.append(current_app)

        return apps
    except Exception as e:
        logging.error(f"Error getting applications: {e}")
        return []

def set_application_volume(app_id: str, value: int) -> None:
    """Set volume for a specific application

    Args:
        app_id (str): Application sink input ID
        value (int): Volume percentage
    """
    try:
        subprocess.run(["pactl", "set-sink-input-volume", app_id, f"{value}%"], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error setting application volume: {e}")

def set_default_sink(sink_name: str) -> None:
    """Set default audio output device

    Args:
        sink_name (str): Sink name
    """
    try:
        subprocess.run(["pactl", "set-default-sink", sink_name], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error setting default sink: {e}")

def set_default_source(source_name: str) -> None:
    """Set default audio input device

    Args:
        source_name (str): Source name
    """
    try:
        subprocess.run(["pactl", "set-default-source", source_name], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error setting default source: {e}")

def get_mic_volume() -> int:
    """Get microphone volume level

    Returns:
        int: Volume percentage
    """
    try:
        output = subprocess.getoutput("pactl get-source-volume @DEFAULT_SOURCE@")
        volume = int(output.split("/")[1].strip().strip("%"))
        return volume
    except Exception as e:
        logging.error(f"Error getting mic volume: {e}")
        return 0

def set_mic_volume(value: int) -> None:
    """Set microphone volume level

    Args:
        value (int): Volume percentage
    """
    try:
        subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", f"{value}%"], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error setting mic volume: {e}")

def get_mic_mute_state() -> bool:
    """Get microphone mute state

    Returns:
        bool: True if muted, False otherwise
    """
    try:
        output = subprocess.getoutput("pactl get-source-mute @DEFAULT_SOURCE@")
        return "yes" in output.lower()
    except Exception as e:
        logging.error(f"Error getting mic mute state: {e}")
        return False

def toggle_mic_mute() -> None:
    """Toggle microphone mute state"""
    try:
        subprocess.run(["pactl", "set-source-mute", "@DEFAULT_SOURCE@", "toggle"], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error toggling mic mute: {e}")