#!/usr/bin/env python3

import dbus
import dbus.mainloop.glib
from gi.repository import GLib  # type: ignore
import logging
import subprocess
from typing import Dict, List

BLUEZ_SERVICE_NAME = 'org.bluez'
BLUEZ_ADAPTER_INTERFACE = 'org.bluez.Adapter1'
BLUEZ_DEVICE_INTERFACE = 'org.bluez.Device1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'


class BluetoothManager:
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()
        self.mainloop = GLib.MainLoop()
        try:
            self.adapter_path = self.find_adapter()
            self.adapter = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, self.adapter_path),
                DBUS_PROP_IFACE
            )
        except Exception as e:
            logging.error(f"Error initializing Bluetooth: {e}")
            self.adapter = None
            self.adapter_path = None

    def find_adapter(self) -> str:
        """Find the first available Bluetooth adapter"""
        remote_om = dbus.Interface(
            self.bus.get_object(BLUEZ_SERVICE_NAME, '/'),
            DBUS_OM_IFACE
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
            logging.error(f"Error getting Bluetooth status: {e}")
            return False

    def set_bluetooth_power(self, enabled: bool) -> None:
        """Set Bluetooth power state"""
        try:
            if not self.adapter:
                return
            self.adapter.Set(BLUEZ_ADAPTER_INTERFACE, "Powered", dbus.Boolean(enabled))
        except Exception as e:
            logging.error(f"Error setting Bluetooth power: {e}")

    def get_devices(self) -> List[Dict[str, str]]:
        """Get list of all known Bluetooth devices"""
        try:
            if not self.adapter:
                return []

            remote_om = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                DBUS_OM_IFACE
            )
            objects = remote_om.GetManagedObjects()
            devices = []
            for path, interfaces in objects.items():
                if BLUEZ_DEVICE_INTERFACE not in interfaces:
                    continue

                properties = interfaces[BLUEZ_DEVICE_INTERFACE]
                if not properties.get("Name", None):
                    continue

                devices.append({
                    'mac': properties.get("Address", ""),
                    'name': properties.get("Name", ""),
                    'paired': properties.get("Paired", False),
                    'connected': properties.get("Connected", False),
                    'trusted': properties.get("Trusted", False),
                    'icon': properties.get("Icon", ""),
                    'path': path
                })
            return devices
        except Exception as e:
            logging.error(f"Error getting devices: {e}")
            return []

    def start_discovery(self) -> None:
        """Start scanning for Bluetooth devices"""
        try:
            if not self.adapter:
                return
            adapter = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, self.adapter_path),
                BLUEZ_ADAPTER_INTERFACE
            )
            adapter.StartDiscovery()
        except Exception as e:
            logging.error(f"Error starting discovery: {e}")

    def stop_discovery(self) -> None:
        """Stop scanning for Bluetooth devices"""
        try:
            if not self.adapter:
                return
            adapter = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, self.adapter_path),
                BLUEZ_ADAPTER_INTERFACE
            )
            adapter.StopDiscovery()
        except Exception as e:
            logging.error(f"Error stopping discovery: {e}")


    def connect_device(self, device_path: str) -> bool:
        """Connect to a Bluetooth device and set it as default audio sink."""
        try:
            device = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, device_path),
                BLUEZ_DEVICE_INTERFACE
            )
            device.Connect()

            # Wait for PulseAudio to register the device
            import time
            time.sleep(2)

            # Fetch device name
            device_name = "Bluetooth Device"

            properties = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, device_path),
                DBUS_PROP_IFACE
            )
            device_name = properties.Get(BLUEZ_DEVICE_INTERFACE, "Alias")

            # Find Bluetooth sink
            output = subprocess.getoutput("pactl list short sinks")
            bt_sink = None
            for line in output.split("\n"):
                if "bluez_output" in line:
                    bt_sink = line.split()[1]
                    break

            if bt_sink:
                subprocess.run(["pactl", "set-default-sink", bt_sink], check=True)

                # Save the Bluetooth sink
                with open("/tmp/last_sink.txt", "w") as f:
                    f.write(bt_sink)

                # Move all running apps to new sink
                output = subprocess.getoutput("pactl list short sink-inputs")
                for line in output.split("\n"):
                    if line.strip():
                        app_id = line.split()[0]
                        subprocess.run(["pactl", "move-sink-input", app_id, bt_sink], check=True)

            # Send notification with battery percentage
            subprocess.run(["notify-send", "Control Center",
                            f"{device_name} Connected"])

            return True
        except Exception as e:
            logging.error(f"Error connecting to device: {e}")
            return False

    def disconnect_device(self, device_path: str) -> bool:
        """Disconnect from a Bluetooth device"""
        try:
            device = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, device_path),
                BLUEZ_DEVICE_INTERFACE
            )
            properties = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, device_path),
                DBUS_PROP_IFACE
            )
            # Fetch device name
            device_name = "Bluetooth Device"
            device_name = properties.Get(BLUEZ_DEVICE_INTERFACE, "Name")
            device.Disconnect()

            subprocess.run(["notify-send", "Control Center", f"{device_name} Disconnected"])

            return True
        except Exception as e:
            logging.error(f"Error disconnecting from device: {e}")
            return False


# Create a global instance of the BluetoothManager
_manager = None

def get_bluetooth_manager() -> BluetoothManager:
    """Get or create the global BluetoothManager instance"""
    global _manager
    if _manager is None:
        _manager = BluetoothManager()
    return _manager

import time
import subprocess
import logging

def restore_last_sink():
    """Restore last used sink and prevent it from switching back to speakers."""
    try:
        with open("/tmp/last_sink.txt", "r") as f:
            last_sink = f.read().strip()

        # Check if the sink still exists
        output = subprocess.getoutput("pactl list short sinks")
        available_sinks = [line.split()[1] for line in output.split("\n") if line.strip()]

        if last_sink in available_sinks:
            logging.info(f"Restoring audio to {last_sink}...")

            # Set Bluetooth as the default sink multiple times
            for _ in range(3):  # Repeat 3 times to fight auto-switching
                subprocess.run(["pactl", "set-default-sink", last_sink], check=True)
                time.sleep(1)

            # Verify if the change was successful
            time.sleep(1)
            current_sink = subprocess.getoutput("pactl get-default-sink").strip()
            if current_sink != last_sink:
                logging.warning(f"Sink reverted to {current_sink}, forcing {last_sink} again...")
                subprocess.run(["pactl", "set-default-sink", last_sink], check=True)

            # Move all running applications to Bluetooth sink
            output = subprocess.getoutput("pactl list short sink-inputs")
            for line in output.split("\n"):
                if line.strip():
                    app_id = line.split()[0]
                    subprocess.run(["pactl", "move-sink-input", app_id, last_sink], check=True)

            logging.info(f"Successfully restored audio to {last_sink}.")

            # 🔹 Prevent PipeWire from overriding the sink
            subprocess.run(["pactl", "set-sink-option", last_sink, "device.headroom", "1"], check=False)

    except FileNotFoundError:
        logging.info("No previous sink saved.")
    except Exception as e:
        logging.error(f"Error restoring last sink: {e}")



# Convenience functions using the global manager
def get_bluetooth_status() -> bool:
    return get_bluetooth_manager().get_bluetooth_status()

def set_bluetooth_power(enabled: bool) -> None:
    get_bluetooth_manager().set_bluetooth_power(enabled)

def get_devices() -> List[Dict[str, str]]:
    return get_bluetooth_manager().get_devices()

def start_discovery() -> None:
    get_bluetooth_manager().start_discovery()

def stop_discovery() -> None:
    get_bluetooth_manager().stop_discovery()

def connect_device(device_path: str) -> bool:
    return get_bluetooth_manager().connect_device(device_path)

def disconnect_device(device_path: str) -> bool:
    return get_bluetooth_manager().disconnect_device(device_path)
