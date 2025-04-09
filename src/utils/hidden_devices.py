import json
import os
from utils.logger import LogLevel, Logger

HIDDEN_DEVICES_FILE = os.path.join(
    os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
    "better-control",
    "hidden_devices.json"
)

class HiddenDevices:
    def __init__(self, logging: Logger):
        self.logging = logging
        self.devices = set()
        self._ensure_config_dir()
        self.load()

    def _ensure_config_dir(self):
        """Ensure config directory exists"""
        try:
            os.makedirs(os.path.dirname(HIDDEN_DEVICES_FILE), exist_ok=True)
        except Exception as e:
            self.logging.log_error(f"Error creating config dir: {e}")

    def load(self) -> bool:
        """Load hidden devices from file"""
        try:
            if os.path.exists(HIDDEN_DEVICES_FILE):
                with open(HIDDEN_DEVICES_FILE, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.devices = set(data)
                        return True
            return False
        except Exception as e:
            self.logging.log_error(f"Error loading hidden devices: {e}")
            return False

    def save(self) -> bool:
        """Save hidden devices to file"""
        try:
            temp_path = HIDDEN_DEVICES_FILE + '.tmp'
            with open(temp_path, 'w') as f:
                json.dump(list(self.devices), f)
            
            # Verify the file is valid
            with open(temp_path, 'r') as f:
                json.load(f)
            
            # Atomic replace
            os.replace(temp_path, HIDDEN_DEVICES_FILE)
            return True
        except Exception as e:
            self.logging.log_error(f"Error saving hidden devices: {e}")
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except:
                pass
            return False

    def add(self, device_id: str) -> bool:
        """Add a device to hidden set"""
        self.devices.add(device_id)
        return self.save()

    def remove(self, device_id: str) -> bool:
        """Remove a device from hidden set"""
        self.devices.discard(device_id)
        return self.save()

    def contains(self, device_id: str) -> bool:
        """Check if device is hidden"""
        return device_id in self.devices
        
    def __iter__(self):
        """Allow iteration over hidden device IDs"""
        return iter(self.devices)
