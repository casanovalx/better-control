#!/usr/bin/env python3

import gi
import subprocess
import os
import logging
from gi.repository import Gtk, GLib

from utils.system import get_battery_status

class BatteryTab(Gtk.Box):
    def __init__(self, parent=None):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=10)
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
            logging.error(f"Failed to get current power plan: {e}")

        matching_label = next(
            (label for label, value in self.power_modes.items() if value == saved_mode),
            "Balanced",
        )
        if matching_label:
            self.power_mode_dropdown.set_active(list(self.power_modes.keys()).index(matching_label))
        else:
            logging.warning(f"Warning: Unknown power mode '{saved_mode}', defaulting to Balanced")
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
                    logging.error(error_message)
                    if self.parent:
                        self.parent.show_error_dialog(error_message)
                else:
                    logging.info(f"Power mode changed to: {selected_mode} ({mode_value})")

            except subprocess.CalledProcessError as e:
                error_message = f"Failed to set power mode: {e}"
                logging.error(error_message)
                if self.parent:
                    self.parent.show_error_dialog(error_message)

            except FileNotFoundError:
                error_message = "powerprofilesctl is not installed or not found in PATH."
                logging.error(error_message)
                if self.parent:
                    self.parent.show_error_dialog(error_message)

    def refresh_battery_info(self, button=None):
        """Refresh battery information. Can be triggered by button press."""
        if button:
            logging.info("Manual refresh of battery information requested")

        # Clear content box
        for child in self.content_box.get_children():
            self.content_box.remove(child)

        # Create a grid to hold the batteries in a 2x2 layout
        batteries_grid = Gtk.Grid()
        batteries_grid.set_column_spacing(20)
        batteries_grid.set_row_spacing(20)
        batteries_grid.set_halign(Gtk.Align.CENTER)
        self.content_box.pack_start(batteries_grid, False, False, 0)

        # Counter for batteries found and position tracking
        batteries_found = 0

        # First check if we can get battery info from /sys/class/power_supply
        battery_paths = []
        for i in range(10):  # Check for BAT0 through BAT9
            path = f"/sys/class/power_supply/BAT{i}"
            if os.path.exists(path):
                battery_paths.append(path)

        # Create battery sections
        for path in battery_paths:
            batteries_found += 1
            battery_num = os.path.basename(path).replace("BAT", "")

            # Calculate grid position (2x2 layout)
            grid_x = (batteries_found - 1) % 2
            grid_y = (batteries_found - 1) // 2

            # Create a grid for this battery
            battery_grid = Gtk.Grid()
            battery_grid.set_column_spacing(15)
            battery_grid.set_row_spacing(10)
            battery_grid.set_margin_bottom(15)

            # Add battery title
            title = f"Battery {battery_num}"
            # Try to get model name for a better title
            if os.path.exists(f"{path}/model_name"):
                try:
                    with open(f"{path}/model_name", "r") as f:
                        model = f.read().strip()
                        if model:
                            title = f"{model} (BAT{battery_num})"
                except:
                    pass

            title_label = Gtk.Label(xalign=0)
            title_label.set_markup(f"<span weight='bold'>{title}</span>")
            battery_grid.attach(title_label, 0, 0, 2, 1)

            row = 1
            battery_info = {}

            # Get battery information
            try:
                if os.path.exists(f"{path}/capacity"):
                    with open(f"{path}/capacity", "r") as f:
                        capacity = f.read().strip()
                        battery_info["Charge"] = f"{capacity}%"

                if os.path.exists(f"{path}/status"):
                    with open(f"{path}/status", "r") as f:
                        status = f.read().strip()
                        battery_info["State"] = status

                if os.path.exists(f"{path}/energy_full") and os.path.exists(f"{path}/energy_full_design"):
                    with open(f"{path}/energy_full", "r") as f:
                        energy_full = float(f.read().strip())
                    with open(f"{path}/energy_full_design", "r") as f:
                        energy_full_design = float(f.read().strip())
                    capacity_health = (energy_full / energy_full_design) * 100
                    battery_info["Capacity"] = f"{capacity_health:.1f}%"

                if os.path.exists(f"{path}/power_now"):
                    with open(f"{path}/power_now", "r") as f:
                        power_now = float(f.read().strip()) / 1000000  # Convert to W
                        battery_info["Power"] = f"{power_now:.2f} W"

                if os.path.exists(f"{path}/voltage_now"):
                    with open(f"{path}/voltage_now", "r") as f:
                        voltage_now = float(f.read().strip()) / 1000000  # Convert to V
                        battery_info["Voltage"] = f"{voltage_now:.2f} V"

                if os.path.exists(f"{path}/cycle_count"):
                    with open(f"{path}/cycle_count", "r") as f:
                        cycle_count = f.read().strip()
                        battery_info["Cycles"] = cycle_count

                if os.path.exists(f"{path}/technology"):
                    with open(f"{path}/technology", "r") as f:
                        technology = f.read().strip()
                        battery_info["Technology"] = technology

                if os.path.exists(f"{path}/manufacturer"):
                    with open(f"{path}/manufacturer", "r") as f:
                        manufacturer = f.read().strip()
                        battery_info["Manufacturer"] = manufacturer

                if os.path.exists(f"{path}/serial_number"):
                    with open(f"{path}/serial_number", "r") as f:
                        serial = f.read().strip()
                        battery_info["Serial"] = serial

            except Exception as e:
                logging.error(f"Error reading battery info: {e}")

            # Add all available information to grid
            for key, value in battery_info.items():
                key_label = Gtk.Label(xalign=0)
                key_label.set_markup(f"<b>{key}:</b>")
                battery_grid.attach(key_label, 0, row, 1, 1)

                value_label = Gtk.Label(xalign=0)
                value_label.set_text(value)
                battery_grid.attach(value_label, 1, row, 1, 1)
                row += 1

            # Add this battery grid to the main batteries grid in a 2x2 layout
            batteries_grid.attach(battery_grid, grid_x, grid_y, 1, 1)

        # If no battery files were found, show "No battery detected" message
        if not batteries_found:
            no_battery_label = Gtk.Label(xalign=0)
            no_battery_label.set_text("No battery detected")
            no_battery_label.set_margin_top(10)
            no_battery_label.set_margin_bottom(10)
            self.content_box.pack_start(no_battery_label, False, False, 0)

        # Add separator and power mode section
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.content_box.pack_start(separator, False, False, 10)

        # Add the power mode box at the bottom
        self.content_box.pack_start(self.power_mode_box, False, False, 0)

        # Show all updated widgets
        self.content_box.show_all()
        return True  # Keep the timer active