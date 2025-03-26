#!/usr/bin/env python3

import dbus
import dbus.mainloop.glib
from gi.repository import GLib  # type: ignore
import subprocess
from typing import Dict, List

from utils.logger import LogLevel, Logger

BLUEZ_SERVICE_NAME = "org.bluez"
BLUEZ_ADAPTER_INTERFACE = "org.bluez.Adapter1"
BLUEZ_DEVICE_INTERFACE = "org.bluez.Device1"
DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
DBUS_PROP_IFACE = "org.freedesktop.DBus.Properties"


class BluetoothManager:
    def __init__(self, logging: Logger):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.logging = logging
        self.bus = dbus.SystemBus()
        self.mainloop = GLib.MainLoop()
        try:
            self.adapter_path = self.find_adapter()
            self.adapter = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, self.adapter_path),
                DBUS_PROP_IFACE,
            )
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed initializing Bluetooth: {e}")
            self.adapter = None
            self.adapter_path = None

    BATTERY_INTERFACE = "org.bluez.Battery1"

    def get_device_battery(self, device_path: str) -> int:
        """Retrieve battery percentage for a Bluetooth device using busctl."""
        try:
            cmd = [
                "busctl",
                "get-property",
                "org.bluez",
                device_path,
                "org.bluez.Battery1",
                "Percentage",
            ]

            # Run the command and capture the output
            output = subprocess.run(
                cmd, capture_output=True, text=True, check=True
            ).stdout.strip()

            # Extract the battery percentage (e.g., "y 100" -> 100)
            battery_value = int(output.split()[-1])
            return battery_value

        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed retrieving battery info: {e}")
            return -1  # Indicate battery info is unavailable

    def find_adapter(self) -> str:
        """Find the first available Bluetooth adapter"""
        remote_om = dbus.Interface(
            self.bus.get_object(BLUEZ_SERVICE_NAME, "/"), DBUS_OM_IFACE
        )
        objects = remote_om.GetManagedObjects()

        for o, props in objects.items():
            if BLUEZ_ADAPTER_INTERFACE in props:
                return o

        raise Exception("No Bluetooth adapter found")

    def get_bluetooth_status(self) -> bool:
        """Get Bluetooth power status"""
        try:
            if not self.adapter:
                return False
            powered = self.adapter.Get(BLUEZ_ADAPTER_INTERFACE, "Powered")
            return bool(powered)
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed getting Bluetooth status: {e}")
            return False

    def set_bluetooth_power(self, enabled: bool) -> None:
        """Set Bluetooth power state"""
        try:
            if not self.adapter:
                return
            self.adapter.Set(BLUEZ_ADAPTER_INTERFACE, "Powered", dbus.Boolean(enabled))
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed setting Bluetooth power: {e}")

    def get_devices(self) -> List[Dict[str, str]]:
        """Get list of all known Bluetooth devices"""
        try:
            if not self.adapter:
                return []

            remote_om = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, "/"), DBUS_OM_IFACE
            )
            objects = remote_om.GetManagedObjects()
            devices = []
            for path, interfaces in objects.items():
                if BLUEZ_DEVICE_INTERFACE not in interfaces:
                    continue

                properties = interfaces[BLUEZ_DEVICE_INTERFACE]
                if not properties.get("Name", None):
                    continue

                devices.append(
                    {
                        "mac": properties.get("Address", ""),
                        "name": properties.get("Name", ""),
                        "paired": properties.get("Paired", False),
                        "connected": properties.get("Connected", False),
                        "trusted": properties.get("Trusted", False),
                        "icon": properties.get("Icon", ""),
                        "path": path,
                    }
                )
            return devices
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed getting devices: {e}")
            return []

    def start_discovery(self) -> None:
        """Start scanning for Bluetooth devices"""
        try:
            if not self.adapter:
                return
            adapter = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, self.adapter_path),
                BLUEZ_ADAPTER_INTERFACE,
            )
            adapter.StartDiscovery()
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed starting discovery: {e}")

    def stop_discovery(self) -> None:
        """Stop scanning for Bluetooth devices"""
        try:
            if not self.adapter:
                return
            adapter = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, self.adapter_path),
                BLUEZ_ADAPTER_INTERFACE,
            )
            adapter.StopDiscovery()
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed stopping discovery: {e}")

    def connect_device(self, device_path: str) -> bool:
        """Connect to a Bluetooth device, set it as the default audio sink, and fetch battery info."""
        try:
            device = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, device_path),
                BLUEZ_DEVICE_INTERFACE,
            )
            device.Connect()

            # Wait for the device to register
            import time

            time.sleep(2)

            # Fetch device name
            properties = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, device_path), DBUS_PROP_IFACE
            )
            device_name = properties.Get(BLUEZ_DEVICE_INTERFACE, "Alias")

            # Fetch battery percentage
            battery_percentage = self.get_device_battery(device_path)
            battery_info = (
                f"Battery: {battery_percentage}%"
                if isinstance(battery_percentage, int) and battery_percentage >= 0
                else ""
            )

            # Send notification
            subprocess.run(
                [
                    "notify-send",
                    "Bluetooth Device Connected",
                    f"{device_name} is connected\n{battery_info}",
                ]
            )

            return True
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed connecting to device: {e}")
            return False

    def disconnect_device(self, device_path: str) -> bool:
        """Disconnect from a Bluetooth device"""
        try:
            device = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, device_path),
                BLUEZ_DEVICE_INTERFACE,
            )
            properties = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, device_path), DBUS_PROP_IFACE
            )
            # Fetch device name
            device_name = "Bluetooth Device"
            device_name = properties.Get(BLUEZ_DEVICE_INTERFACE, "Name")
            device.Disconnect()

            subprocess.run(
                ["notify-send", "Control Center", f"{device_name} Disconnected"]
            )

            return True
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed disconnecting from device: {e}")
            return False


# Create a global instance of the BluetoothManager
_manager = None


def get_bluetooth_manager(logging: Logger) -> BluetoothManager:
    """Get or create the global BluetoothManager instance"""
    global _manager
    if _manager is None:
        _manager = BluetoothManager(logging)
    return _manager


import time
import subprocess
import logging


def restore_last_sink(logging: Logger):
    """Restore last used sink and prevent it from switching back to speakers."""
    try:
        with open("/tmp/last_sink.txt", "r") as f:
            last_sink = f.read().strip()

        # Check if the sink still exists
        output = subprocess.getoutput("pactl list short sinks")
        available_sinks = [
            line.split()[1] for line in output.split("\n") if line.strip()
        ]

        if last_sink in available_sinks:
            logging.log(LogLevel.Info, f"Restoring audio to {last_sink}...")

            # Set Bluetooth as the default sink multiple times
            for _ in range(3):  # Repeat 3 times to fight auto-switching
                subprocess.run(["pactl", "set-default-sink", last_sink], check=True)
                time.sleep(1)

            # Verify if the change was successful
            time.sleep(1)
            current_sink = subprocess.getoutput("pactl get-default-sink").strip()
            if current_sink != last_sink:
                logging.log(
                    LogLevel.Warn,
                    f"Sink reverted to {current_sink}, forcing {last_sink} again...",
                )
                subprocess.run(["pactl", "set-default-sink", last_sink], check=True)

            # Move all running applications to Bluetooth sink
            output = subprocess.getoutput("pactl list short sink-inputs")
            for line in output.split("\n"):
                if line.strip():
                    app_id = line.split()[0]
                    subprocess.run(
                        ["pactl", "move-sink-input", app_id, last_sink], check=True
                    )

            logging.log(LogLevel.Info, f"Successfully restored audio to {last_sink}.")

            # 🔹 Prevent PipeWire from overriding the sink
            subprocess.run(
                ["pactl", "set-sink-option", last_sink, "device.headroom", "1"],
                check=False,
            )

    except FileNotFoundError:
        logging.log(LogLevel.Info, "No previous sink saved.")
    except Exception as e:
        logging.log(LogLevel.Error, f"Failed restoring last sink: {e}")


# Convenience functions using the global manager
def get_bluetooth_status(logging: Logger) -> bool:
    return get_bluetooth_manager(logging).get_bluetooth_status()


def set_bluetooth_power(enabled: bool, logging: Logger) -> None:
    get_bluetooth_manager(logging).set_bluetooth_power(enabled)


def get_devices(logging: Logger) -> List[Dict[str, str]]:
    return get_bluetooth_manager(logging).get_devices()


def start_discovery(logging: Logger) -> None:
    get_bluetooth_manager(logging).start_discovery()


def stop_discovery(logging: Logger) -> None:
    get_bluetooth_manager(logging).stop_discovery()


def connect_device(device_path: str, logging: Logger) -> bool:
    return get_bluetooth_manager(logging).connect_device(device_path)


def disconnect_device(device_path: str, logging: Logger) -> bool:
    return get_bluetooth_manager(logging).disconnect_device(device_path)
