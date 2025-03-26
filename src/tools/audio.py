import subprocess
import shutil
from typing import Optional

from utils.logger import LogLevel, Logger


def get_current_volume(logging: Logger) -> int:
    """Get the current volume level.

    Returns:
        int: Current volume level (0-100)
    """
    try:
        output = subprocess.getoutput("pactl get-sink-volume @DEFAULT_SINK@")
        volume = int(output.split("/")[1].strip().strip("%"))
        return volume
    except Exception as e:
        logging.log(LogLevel.Error, f"Failed getting volume: {e}")
        return 50


def get_current_mic_volume(logging: Logger) -> int:
    """Get the current microphone volume level.

    Returns:
        int: Current microphone volume level (0-100)
    """
    try:
        output = subprocess.getoutput("pactl get-source-volume @DEFAULT_SOURCE@")
        volume = int(output.split("/")[1].strip().strip("%"))
        return volume
    except Exception as e:
        logging.log(LogLevel.Error, f"Failed getting mic volume: {e}")
        return 50


def set_volume_level(value: int, logging: Logger) -> None:
    """Set the speaker volume to a specific level.

    Args:
        value (int): Volume level to set (0-100)
    """
    if shutil.which("pactl"):
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{value}%"])
    else:
        logging.log(LogLevel.Error, 
            "pactl is missing. Please check our GitHub page to see all dependencies and install them"
        )


def set_mic_level(value: int, logging: Logger) -> None:
    """Set the microphone volume to a specific level.

    Args:
        value (int): Volume level to set (0-100)
    """
    if shutil.which("pactl"):
        subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", f"{value}%"])
    else:
        logging.log(LogLevel.Error, 
            "pactl is missing. Please check our GitHub page to see all dependencies and install them"
        )


def is_muted(logging: Logger, audio_type: str = "sink") -> bool:
    """Check if the audio sink or source is currently muted.

    Args:
        audio_type (str): "sink" for speaker, "source" for microphone

    Returns:
        bool: True if muted, False otherwise
    """
    try:
        if audio_type == "sink":
            output = subprocess.getoutput("pactl get-sink-mute @DEFAULT_SINK@")
        elif audio_type == "source":
            output = subprocess.getoutput("pactl get-source-mute @DEFAULT_SOURCE@")
        else:
            raise ValueError("Invalid audio_type. Use 'sink' or 'source'.")

        return "yes" in output.lower()
    except Exception as e:
        logging.log(LogLevel.Error, f"Failed checking mute state: {e}")
        return False


def toggle_mute(logging: Logger, audio_type: str = "sink") -> None:
    """Toggle mute state for speaker or microphone.

    Args:
        audio_type (str): "sink" for speaker, "source" for microphone
    """
    if not shutil.which("pactl"):
        logging.log(LogLevel.Error, 
            "pactl is missing. Please check our GitHub page to see all dependencies and install them"
        )
        return

    try:
        if audio_type == "sink":
            subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
        elif audio_type == "source":
            subprocess.run(["pactl", "set-source-mute", "@DEFAULT_SOURCE@", "toggle"])
        else:
            raise ValueError("Invalid audio_type. Use 'sink' or 'source'.")
    except Exception as e:
        logging.log(LogLevel.Error, f"Failed toggling mute: {e}")


def get_sink_icon_name(sink_name: str, description: str) -> str:
    """Determine the appropriate icon for an audio output device.

    Args:
        sink_name (str): Name of the audio sink
        description (str): Description of the audio sink

    Returns:
        str: Icon name to use
    """
    sink_name_lower = sink_name.lower()
    description_lower = description.lower() if description else ""

    # Check for headphones
    if any(
        term in sink_name_lower or term in description_lower
        for term in ["headphone", "headset", "earphone", "earbud"]
    ):
        return "audio-headphones-symbolic"

    # Check for Bluetooth devices
    if (
        "bluetooth" in sink_name_lower
        or "bluez" in sink_name_lower
        or "bt" in description_lower
    ):
        return "bluetooth-symbolic"

    # Check for HDMI/DisplayPort outputs (typically TV or monitors)
    if any(
        term in sink_name_lower or term in description_lower
        for term in ["hdmi", "displayport", "dp", "tv"]
    ):
        return "video-display-symbolic"

    # Check for USB audio interfaces
    if "usb" in sink_name_lower or "usb" in description_lower:
        return "audio-card-symbolic"

    # Default to speaker
    return "audio-speakers-symbolic"


def get_source_icon_name(source_name: str, description: str) -> str:
    """Determine the appropriate icon for an audio input device.

    Args:
        source_name (str): Name of the audio source
        description (str): Description of the audio source

    Returns:
        str: Icon name to use
    """
    source_name_lower = source_name.lower()
    description_lower = description.lower() if description else ""

    # Check for webcam microphones
    if (
        "cam" in source_name_lower
        or "cam" in description_lower
        or "webcam" in description_lower
    ):
        return "camera-web-symbolic"

    # Check for headset microphones
    if any(
        term in source_name_lower or term in description_lower
        for term in ["headset", "headphone"]
    ):
        return "audio-headset-symbolic"

    # Check for Bluetooth microphones
    if (
        "bluetooth" in source_name_lower
        or "bluez" in source_name_lower
        or "bt" in description_lower
    ):
        return "bluetooth-symbolic"

    # Check for USB microphones
    if "usb" in source_name_lower or "usb" in description_lower:
        return "audio-input-microphone-symbolic"

    # Default to generic microphone
    return "audio-input-microphone-symbolic"


def get_app_icon_name(app_name: str, provided_icon_name: str) -> Optional[str]:
    """Map application names to appropriate icon names.

    Args:
        app_name (str): Name of the application
        provided_icon_name (str): Icon name provided by the application

    Returns:
        str: Icon name to use
    """
    # First check if the provided icon name exists
    if provided_icon_name and provided_icon_name != "":
        return provided_icon_name

    # Map common application names to icons
    icon_map = {
        "Firefox": "firefox",
        "firefox": "firefox",
        "Brave": "brave-browser",
        "brave": "brave-browser",
        "Chromium": "chromium",
        "chromium": "chromium",
        "Google Chrome": "google-chrome",
        "chrome": "google-chrome",
        "Spotify": "spotify",
        "spotify": "spotify",
        "VLC": "vlc",
        "vlc": "vlc",
        "mpv": "mpv",
        "MPV": "mpv",
        "Discord": "discord",
        "discord": "discord",
        "Telegram": "telegram",
        "telegram": "telegram",
        "Zoom": "zoom",
        "zoom": "zoom",
    }

    # Check if the app name is in our mapping
    for key in icon_map:
        if key in app_name:
            return icon_map[key]

    # Return a generic audio icon as fallback
    return "audio-x-generic-symbolic"
