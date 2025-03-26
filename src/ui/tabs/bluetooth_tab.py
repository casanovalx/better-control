#!/usr/bin/env python3

import gi  # type: ignore

from utils.logger import LogLevel, Logger

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib  # type: ignore

from tools.bluetooth import (
    get_bluetooth_status,
    set_bluetooth_power,
    get_devices,
    start_discovery,
    stop_discovery,
    connect_device,
    disconnect_device,
)
from ui.widgets.bluetooth_device_row import BluetoothDeviceRow


class BluetoothTab(Gtk.Box):
    """Bluetooth settings tab"""

    def __init__(self, logging: Logger):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.logging = logging

        self.set_margin_start(15)
        self.set_margin_end(15)
        self.set_margin_top(15)
        self.set_margin_bottom(15)
        self.set_hexpand(True)
        self.set_vexpand(True)

        # State tracking
        self.is_discovering = False
        self.discovery_timeout_id = None
        self.discovery_check_id = None

        # Create header box with title and refresh button
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header_box.set_hexpand(True)

        # Create title box with icon and label
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # Add bluetooth icon
        bluetooth_icon = Gtk.Image.new_from_icon_name(
            "bluetooth-symbolic", Gtk.IconSize.DIALOG
        )
        title_box.pack_start(bluetooth_icon, False, False, 0)

        # Add title
        bluetooth_label = Gtk.Label()
        bluetooth_label.set_markup(
            "<span weight='bold' size='large'>Bluetooth Devices</span>"
        )
        bluetooth_label.set_halign(Gtk.Align.START)
        title_box.pack_start(bluetooth_label, False, False, 0)

        header_box.pack_start(title_box, True, True, 0)

        # Add scan button
        self.scan_button = Gtk.Button()
        scan_icon = Gtk.Image.new_from_icon_name(
            "view-refresh-symbolic", Gtk.IconSize.BUTTON
        )
        self.scan_button.set_image(scan_icon)
        self.scan_button.set_tooltip_text("Scan for Devices")
        self.scan_button.connect("clicked", self.on_scan_clicked)
        # Set initial visibility based on Bluetooth status
        self.scan_button.set_visible(get_bluetooth_status(self.logging))
        header_box.pack_end(self.scan_button, False, False, 0)

        self.pack_start(header_box, False, False, 0)

        # Create scrollable content
        scroll_window = Gtk.ScrolledWindow()
        scroll_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_window.set_vexpand(True)

        # Create main content box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content_box.set_margin_top(10)
        content_box.set_margin_bottom(10)
        content_box.set_margin_start(10)
        content_box.set_margin_end(10)

        # Bluetooth power switch
        power_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        power_label = Gtk.Label(label="Bluetooth")
        power_label.set_markup("<b>Bluetooth</b>")
        power_label.set_halign(Gtk.Align.START)
        self.power_switch = Gtk.Switch()
        self.power_switch.set_active(get_bluetooth_status(self.logging))
        self.power_switch.connect("notify::active", self.on_power_switched)
        power_box.pack_start(power_label, False, True, 0)
        power_box.pack_end(self.power_switch, False, True, 0)
        content_box.pack_start(power_box, False, True, 0)

        # Device list section
        devices_label = Gtk.Label()
        devices_label.set_markup("<b>Available Devices</b>")
        devices_label.set_halign(Gtk.Align.START)
        devices_label.set_margin_top(15)
        content_box.pack_start(devices_label, False, True, 0)

        # Device list
        devices_frame = Gtk.Frame()
        devices_frame.set_shadow_type(Gtk.ShadowType.IN)
        self.devices_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.devices_box.set_margin_start(10)
        self.devices_box.set_margin_end(10)
        self.devices_box.set_margin_top(10)
        self.devices_box.set_margin_bottom(10)

        devices_frame.add(self.devices_box)
        content_box.pack_start(devices_frame, True, True, 0)

        scroll_window.add(content_box)
        self.pack_start(scroll_window, True, True, 0)

        # Initial device list population
        self.update_device_list()

        # Set up periodic device list updates
        GLib.timeout_add(2000, self.periodic_update)

    def update_device_list(self):
        """Update the list of Bluetooth devices"""
        # Clear existing devices
        for child in self.devices_box.get_children():
            self.devices_box.remove(child)

        # Only add devices if Bluetooth is enabled
        if get_bluetooth_status(self.logging):
            # Add devices
            devices = get_devices(self.logging)
            for device in devices:
                device_row = BluetoothDeviceRow(device)
                device_row.connect_button.connect(
                    "clicked", self.on_connect_clicked, device["path"]
                )
                device_row.disconnect_button.connect(
                    "clicked", self.on_disconnect_clicked, device["path"]
                )
                self.devices_box.pack_start(device_row, False, True, 0)

        self.devices_box.show_all()

    def periodic_update(self):
        """Update the device list periodically"""
        self.update_device_list()
        return True  # Keep the timer active

    def on_power_switched(self, switch, gparam):
        """Handle Bluetooth power switch changes

        Args:
            switch (Gtk.Switch): The power switch widget
            gparam: GObject parameter
        """
        is_enabled = switch.get_active()
        set_bluetooth_power(is_enabled, self.logging)
        # Update UI based on Bluetooth state
        if is_enabled:
            # Bluetooth enabled - show scan button
            self.scan_button.set_visible(True)
            # Update device list
            self.update_device_list()
        else:
            # Bluetooth disabled - hide scan button
            self.scan_button.set_visible(False)
            # Clear all devices from the list
            for child in self.devices_box.get_children():
                self.devices_box.remove(child)
            self.devices_box.show_all()
            # If we're discovering, stop it
            if self.is_discovering:
                self.stop_scan(self.scan_button)

    def on_scan_clicked(self, button):
        """Handle scan button clicks

        Args:
            button (Gtk.Button): The scan button widget
        """
        # If already scanning, stop the scan
        if self.is_discovering:
            self.stop_scan(button)
            return

        self.logging.log(LogLevel.Info, "Starting Bluetooth device scan")
        # Disable button during scan
        button.set_sensitive(False)
        button.set_label("Scanning...")

        # Start discovery
        try:
            start_discovery(self.logging)
            self.is_discovering = True
        except Exception as e:
            self.logging.log(
                LogLevel.Error, f"Failed to start Bluetooth discovery: {e}"
            )
            button.set_label("Scan for Devices")
            button.set_sensitive(True)
            return

        # Store the start time
        self.scan_start_time = GLib.get_monotonic_time()

        # Schedule periodic checks
        def check_scan_status():
            if not self.is_discovering:
                return False

            current_time = GLib.get_monotonic_time()
            elapsed_seconds = (
                current_time - self.scan_start_time
            ) / 1000000  # Convert to seconds
            # If scan has been running for more than 30 seconds, force stop
            if elapsed_seconds > 30:
                self.logging.log(
                    LogLevel.Warn, "Bluetooth scan timeout reached. Forcing stop."
                )
                self.stop_scan(button)
                return False
            return True

        # Add periodic check every 5 seconds
        if self.discovery_check_id:
            GLib.source_remove(self.discovery_check_id)
        self.discovery_check_id = GLib.timeout_add_seconds(5, check_scan_status)

        # Schedule stopping discovery after 10 seconds
        def stop_scan():
            if self.is_discovering:
                self.stop_scan(button)
            return False

        if self.discovery_timeout_id:
            GLib.source_remove(self.discovery_timeout_id)
        self.discovery_timeout_id = GLib.timeout_add_seconds(10, stop_scan)

    def stop_scan(self, button):
        """Stop the Bluetooth discovery process

        Args:
            button (Gtk.Button): The scan button widget
        """
        self.logging.log(LogLevel.Info, "Stopping Bluetooth device scan")
        if not self.is_discovering:
            button.set_sensitive(True)
            button.set_label("Scan for Devices")
            return

        try:
            stop_discovery(self.logging)
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed to stop Bluetooth discovery: {e}")
        finally:
            self.is_discovering = False
            if self.discovery_timeout_id:
                GLib.source_remove(self.discovery_timeout_id)
                self.discovery_timeout_id = None
            if self.discovery_check_id:
                GLib.source_remove(self.discovery_check_id)
                self.discovery_check_id = None
            button.set_sensitive(True)
            button.set_label("Scan for Devices")
            self.update_device_list()

    def on_connect_clicked(self, button, device_path):
        """Handle device connect button clicks

        Args:
            button (Gtk.Button): The connect button widget
            device_path (str): DBus path of the device
        """
        if connect_device(device_path, self.logging):
            self.update_device_list()

    def on_disconnect_clicked(self, button, device_path):
        """Handle device disconnect button clicks

        Args:
            button (Gtk.Button): The disconnect button widget
            device_path (str): DBus path of the device
        """
        if disconnect_device(device_path, self.logging):
            self.update_device_list()
