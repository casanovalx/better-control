#!/usr/bin/env python3

import dbus
import dbus.mainloop.glib
from gi.repository import GLib
import typing
import logging
import subprocess

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
        """Find the first available Bluetooth adapter

        Returns:
            str: DBus path of the adapter
        """
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
        """Get Bluetooth power status

        Returns:
            bool: True if Bluetooth is powered on, False otherwise
        """
        try:
            if not self.adapter:
                return False
            powered = self.adapter.Get(BLUEZ_ADAPTER_INTERFACE, "Powered")
            return bool(powered)
        except Exception as e:
            logging.error(f"Error getting Bluetooth status: {e}")
            return False

    def set_bluetooth_power(self, enabled: bool) -> None:
        """Set Bluetooth power state

        Args:
            enabled (bool): True to power on, False to power off
        """
        try:
            if not self.adapter:
                return
            self.adapter.Set(BLUEZ_ADAPTER_INTERFACE, "Powered", dbus.Boolean(enabled))
        except Exception as e:
            logging.error(f"Error setting Bluetooth power: {e}")

    def get_devices(self) -> typing.List[typing.Dict[str, str]]:
        """Get list of all known Bluetooth devices (both paired and discovered)

        Returns:
            typing.List[typing.Dict[str, str]]: List of device dictionaries with MAC and name
        """
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
        """Connect to a Bluetooth device and display a notification with battery percentage.

        Args:
            device_path (str): DBus path of the device

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            device = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, device_path),
                BLUEZ_DEVICE_INTERFACE
            )
            device.Connect()

            # Fetch battery percentage
            battery_level = "Unknown"
            try:
                properties = dbus.Interface(
                    self.bus.get_object(BLUEZ_SERVICE_NAME, device_path),
                    DBUS_PROP_IFACE
                )
                battery_level = properties.Get(BLUEZ_DEVICE_INTERFACE, "BatteryPercentage")
            except Exception:
                logging.warning(f"Battery percentage not available for device: {device_path}")

            # Send notification with battery percentage
            subprocess.run(["notify-send", "Control Center",
                            f"Bluetooth Device Connected\nBattery: {battery_level}%"])

            return True
        except Exception as e:
            logging.error(f"Error connecting to device: {e}")
            return False


    def disconnect_device(self, device_path: str) -> bool:
        """Disconnect from a Bluetooth device

        Args:
            device_path (str): DBus path of the device

        Returns:
            bool: True if disconnection successful, False otherwise
        """
        try:
            device = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, device_path),
                BLUEZ_DEVICE_INTERFACE
            )
            device.Disconnect()
            subprocess.run(["notify-send", "Control Center","Bluetooth Device Disconnected"])
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

# Convenience functions that use the global manager
def get_bluetooth_status() -> bool:
    return get_bluetooth_manager().get_bluetooth_status()

def set_bluetooth_power(enabled: bool) -> None:
    get_bluetooth_manager().set_bluetooth_power(enabled)

def get_devices() -> typing.List[typing.Dict[str, str]]:
    return get_bluetooth_manager().get_devices()

def start_discovery() -> None:
    get_bluetooth_manager().start_discovery()

def stop_discovery() -> None:
    get_bluetooth_manager().stop_discovery()

def connect_device(device_path: str) -> bool:
    return get_bluetooth_manager().connect_device(device_path)

def disconnect_device(device_path: str) -> bool:
    return get_bluetooth_manager().disconnect_device(device_path)

