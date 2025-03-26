#!/usr/bin/env python3

import gi # type: ignore
import subprocess
import os
import re
from gi.repository import Gtk, GLib # type: ignore
from utils.logger import LogLevel, Logger


class BatteryTab(Gtk.Box):
    def __init__(self, logging: Logger, parent=None):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.logging = logging

        self.set_margin_top(15)
        self.set_margin_bottom(15)
        self.set_margin_start(15)
        self.set_margin_end(15)
        self.set_hexpand(True)
        self.set_vexpand(True)

        self.parent = parent

        # Create header box with title and refresh button
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header_box.set_hexpand(True)

        # Create title box with icon and label
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # Add battery icon - increase size to match other tabs
        battery_icon = Gtk.Image.new_from_icon_name("battery-good-symbolic", Gtk.IconSize.DIALOG)
        title_box.pack_start(battery_icon, False, False, 0)

        # Add title
        self.battery_label = Gtk.Label()
        self.battery_label.set_markup("<span weight='bold' size='large'>Battery Metrics</span>")
        self.battery_label.set_halign(Gtk.Align.START)
        title_box.pack_start(self.battery_label, False, False, 0)

        header_box.pack_start(title_box, True, True, 0)

        # Add refresh button
        refresh_button = Gtk.Button()
        refresh_icon = Gtk.Image.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON)
        refresh_button.set_image(refresh_icon)
        refresh_button.set_tooltip_text("Refresh Battery Information")
        refresh_button.connect("clicked", self.refresh_battery_info)
        header_box.pack_end(refresh_button, False, False, 0)

        self.pack_start(header_box, False, False, 0)

        # Create scrollable content
        scroll_window = Gtk.ScrolledWindow()
        scroll_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_window.set_vexpand(True)

        # Create main content box - store as instance variable to update later
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.content_box.set_margin_top(10)
        self.content_box.set_margin_bottom(10)
        self.content_box.set_margin_start(10)
        self.content_box.set_margin_end(10)

        # Power mode section
        self.power_mode_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        self.power_mode_label = Gtk.Label(label="Select Power Mode:")
        self.power_mode_label.set_halign(Gtk.Align.START)
        self.power_mode_label.set_markup("<b>Select Power Mode:</b>")
        self.power_mode_box.pack_start(self.power_mode_label, False, False, 0)

        # Mode selection dropdown
        dropdown_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        dropdown_box.set_margin_top(5)

        self.power_mode_dropdown = Gtk.ComboBoxText()
        self.power_modes = {
            "Power Saving": "power-saver",
            "Balanced": "balanced",
            "Performance": "performance",
        }

        for mode in self.power_modes.keys():
            self.power_mode_dropdown.append_text(mode)

        # Get saved mode from settings
        saved_mode = "balanced"  # Default to balanced
        try:
            # Get current power plan using powerprofilesctl
            result = subprocess.run("powerprofilesctl get", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                current_plan = result.stdout.strip()
                # Map powerprofilesctl output to our modes
                plan_mapping = {
                    "power-saver": "Power Saving",
                    "balanced": "Balanced",
                    "performance": "Performance"
                }
                if current_plan in plan_mapping:
                    saved_mode = current_plan
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed to get current power plan: {e}")

        matching_label = next(
            (label for label, value in self.power_modes.items() if value == saved_mode),
            "Balanced",
        )
        if matching_label:
            self.power_mode_dropdown.set_active(list(self.power_modes.keys()).index(matching_label))
        else:
            self.logging.log(LogLevel.Warn, f"Unknown power mode '{saved_mode}', defaulting to Balanced")
            self.power_mode_dropdown.set_active(list(self.power_modes.keys()).index("Balanced"))

        dropdown_box.pack_start(self.power_mode_dropdown, True, True, 0)
        self.power_mode_box.pack_start(dropdown_box, False, False, 0)

        scroll_window.add(self.content_box)
        self.pack_start(scroll_window, True, True, 0)

        self.power_mode_dropdown.connect("changed", self.set_power_mode)

        # Initial refresh
        self.refresh_battery_info()
        GLib.timeout_add_seconds(10, self.refresh_battery_info)

    def set_power_mode(self, widget):
        """Handle power mode change using powerprofilesctl."""
        selected_mode = widget.get_active_text()
        if selected_mode in self.power_modes:
            mode_value = self.power_modes[selected_mode]

            try:
                command = f"powerprofilesctl set {mode_value}"
                result = subprocess.run(command, shell=True, capture_output=True, text=True)

                if result.returncode != 0:
                    error_message = "powerprofilesctl is missing. Please check our GitHub page to see all dependencies and install them."
                    self.logging.log(LogLevel.Error, error_message)
                    if self.parent:
                        self.parent.show_error_dialog(error_message)
                else:
                    self.logging.log(LogLevel.Info, f"Power mode changed to: {selected_mode} ({mode_value})")

            except subprocess.CalledProcessError as e:
                error_message = f"Failed to set power mode: {e}"
                self.logging.log(LogLevel.Error, error_message)
                if self.parent:
                    self.parent.show_error_dialog(error_message)

            except FileNotFoundError:
                error_message = "powerprofilesctl is not installed or not found in PATH."
                self.logging.log(LogLevel.Error, error_message)
                if self.parent:
                    self.parent.show_error_dialog(error_message)

    def get_battery_devices(self):
        """Get list of battery devices from UPower."""
        devices = []
        try:
            # List all UPower devices
            result = subprocess.run("upower -e", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    # Only include battery devices
                    if 'battery' in line.lower():
                        devices.append(line)
            return devices
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed to get UPower devices: {e}")
            return []

    def parse_upower_output(self, output):
        """Parse the output of upower -i command into a dictionary."""
        info = {}
        current_section = None
        
        for line in output.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a main property line (contains a colon)
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Skip empty values
                if not value:
                    continue
                    
                # Map UPower keys to more user-friendly labels
                key_mapping = {
                    'native-path': 'Path',
                    'vendor': 'Manufacturer', 
                    'model': 'Model',
                    'serial': 'Serial',
                    'power supply': 'Power Supply',
                    'updated': 'Last Updated',
                    'has history': 'Has History',
                    'has statistics': 'Has Statistics',
                    'present': 'Present',
                    'rechargeable': 'Rechargeable',
                    'state': 'State',
                    'warning-level': 'Warning Level',
                    'energy': 'Energy',
                    'energy-empty': 'Energy Empty',
                    'energy-full': 'Energy Full',
                    'energy-full-design': 'Energy Full Design',
                    'energy-rate': 'Energy Rate',
                    'voltage': 'Voltage',
                    'time to empty': 'Time to Empty',
                    'time to full': 'Time to Full',
                    'percentage': 'Charge',
                    'capacity': 'Capacity',
                    'technology': 'Technology',
                    'icon-name': 'Icon Name'
                }
                
                display_key = key_mapping.get(key, key.capitalize())
                info[display_key] = value
                
        return info

    def refresh_battery_info(self, button=None):
        """Refresh battery information using UPower."""
        if button:
            self.logging.log(LogLevel.Info, "Manual refresh of battery information requested")
            
        # Clear content box
        for child in self.content_box.get_children():
            self.content_box.remove(child)

        # Add the power mode box at the top
        self.content_box.pack_start(self.power_mode_box, False, False, 0)

        # Add separator after the power mode section
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.content_box.pack_start(separator, False, False, 10)

        # Get list of battery devices
        battery_devices = self.get_battery_devices()
        
        if not battery_devices:
            # No battery found
            no_battery_label = Gtk.Label(xalign=0)
            no_battery_label.set_text("No battery detected")
            no_battery_label.set_margin_top(10)
            no_battery_label.set_margin_bottom(10)
            self.content_box.pack_start(no_battery_label, False, False, 0)
        else:
            # Create a grid to hold the batteries
            batteries_grid = Gtk.Grid()
            batteries_grid.set_column_spacing(20)
            batteries_grid.set_row_spacing(20)
            batteries_grid.set_halign(Gtk.Align.CENTER)
            self.content_box.pack_start(batteries_grid, False, False, 0)
            
            # Process each battery
            for i, device_path in enumerate(battery_devices):
                try:
                    # Run upower command for this battery
                    result = subprocess.run(f"upower -i {device_path}", shell=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        battery_info = self.parse_upower_output(result.stdout)
                        
                        # Calculate grid position (2x2 layout)
                        grid_x = i % 2
                        grid_y = i // 2
                        
                        # Create a frame for this battery
                        battery_frame = Gtk.Frame()
                        battery_frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
                        
                        # Create grid for battery info
                        battery_grid = Gtk.Grid()
                        battery_grid.set_column_spacing(15)
                        battery_grid.set_row_spacing(8)
                        battery_grid.set_margin_top(10)
                        battery_grid.set_margin_bottom(10)
                        battery_grid.set_margin_start(10)
                        battery_grid.set_margin_end(10)
                        
                        # Add battery title
                        title = f"Battery {os.path.basename(device_path)}"
                        if 'Model' in battery_info:
                            title = f"{battery_info['Model']}"
                        
                        title_label = Gtk.Label(xalign=0)
                        title_label.set_markup(f"<span weight='bold'>{title}</span>")
                        battery_grid.attach(title_label, 0, 0, 2, 1)
                        
                        # Display priority fields first
                        priority_fields = ['Charge', 'State', 'Capacity', 'Time to Empty', 'Time to Full', 
                                          'Energy Rate', 'Voltage', 'Technology', 'Manufacturer']
                        
                        row = 1
                        # First add priority fields
                        for key in priority_fields:
                            if key in battery_info:
                                key_label = Gtk.Label(xalign=0)
                                key_label.set_markup(f"<b>{key}:</b>")
                                battery_grid.attach(key_label, 0, row, 1, 1)

                                value_label = Gtk.Label(xalign=0)
                                value_label.set_text(battery_info[key])
                                battery_grid.attach(value_label, 1, row, 1, 1)
                                row += 1
                        
                        # Then add remaining fields
                        for key, value in battery_info.items():
                            if key not in priority_fields and key != 'Model':  # Skip model as it's in the title
                                key_label = Gtk.Label(xalign=0)
                                key_label.set_markup(f"<b>{key}:</b>")
                                battery_grid.attach(key_label, 0, row, 1, 1)

                                value_label = Gtk.Label(xalign=0)
                                value_label.set_text(value)
                                battery_grid.attach(value_label, 1, row, 1, 1)
                                row += 1
                        
                        battery_frame.add(battery_grid)
                        batteries_grid.attach(battery_frame, grid_x, grid_y, 1, 1)
                        
                except Exception as e:
                    self.logging.log(LogLevel.Error, f"Error processing battery {device_path}: {e}")
        
        # Show all updated widgets
        self.content_box.show_all()
        return True  # Keep the timer active
