#!/usr/bin/env python3

import gi # type: ignore
import subprocess
import logging

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk # type: ignore

from utils.settings import load_settings, save_settings

class DisplayTab(Gtk.Box):
    """Display settings tab"""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margin_start(15)
        self.set_margin_end(15)
        self.set_margin_top(15)
        self.set_margin_bottom(15)
        self.set_hexpand(True)
        self.set_vexpand(True)

        # Create header box with title and refresh button
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header_box.set_hexpand(True)

        # Create title box with icon and label
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # Add display icon
        display_icon = Gtk.Image.new_from_icon_name("video-display-symbolic", Gtk.IconSize.DIALOG)
        title_box.pack_start(display_icon, False, False, 0)

        # Add title
        display_label = Gtk.Label()
        display_label.set_markup("<span weight='bold' size='large'>Display Settings</span>")
        display_label.set_halign(Gtk.Align.START)
        title_box.pack_start(display_label, False, False, 0)

        header_box.pack_start(title_box, True, True, 0)

        # Add refresh button
        refresh_button = Gtk.Button()
        refresh_icon = Gtk.Image.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON)
        refresh_button.set_image(refresh_icon)
        refresh_button.set_tooltip_text("Refresh Display Settings")
        refresh_button.connect("clicked", self.refresh_display_settings)
        header_box.pack_end(refresh_button, False, False, 0)

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

        # Brightness section
        brightness_label = Gtk.Label()
        brightness_label.set_markup("<b>Screen Brightness</b>")
        brightness_label.set_halign(Gtk.Align.START)
        content_box.pack_start(brightness_label, False, True, 0)

        # Brightness control
        brightness_frame = Gtk.Frame()
        brightness_frame.set_shadow_type(Gtk.ShadowType.IN)
        brightness_frame.set_margin_top(5)
        brightness_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        brightness_box.set_margin_start(10)
        brightness_box.set_margin_end(10)
        brightness_box.set_margin_top(10)
        brightness_box.set_margin_bottom(10)

        # Brightness scale
        self.brightness_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0, 100, 1
        )
        self.brightness_scale.set_value(self.get_current_brightness())
        self.brightness_scale.set_value_pos(Gtk.PositionType.RIGHT)
        self.brightness_scale.connect("value-changed", self.on_brightness_changed)
        brightness_box.pack_start(self.brightness_scale, True, True, 0)

        # Quick brightness buttons
        brightness_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        for value in [0, 25, 50, 75, 100]:
            button = Gtk.Button(label=f"{value}%")
            button.connect("clicked", self.on_brightness_button_clicked, value)
            brightness_buttons.pack_start(button, True, True, 0)

        brightness_box.pack_start(brightness_buttons, False, False, 0)
        brightness_frame.add(brightness_box)
        content_box.pack_start(brightness_frame, False, True, 0)

        # Blue light filter section
        bluelight_label = Gtk.Label()
        bluelight_label.set_markup("<b>Blue Light Filter</b>")
        bluelight_label.set_halign(Gtk.Align.START)
        bluelight_label.set_margin_top(15)
        content_box.pack_start(bluelight_label, False, True, 0)

        # Blue light control
        bluelight_frame = Gtk.Frame()
        bluelight_frame.set_shadow_type(Gtk.ShadowType.IN)
        bluelight_frame.set_margin_top(5)
        bluelight_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        bluelight_box.set_margin_start(10)
        bluelight_box.set_margin_end(10)
        bluelight_box.set_margin_top(10)
        bluelight_box.set_margin_bottom(10)

        # Blue light scale
        self.bluelight_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 2500, 6500, 100
        )
        settings = load_settings()
        saved_gamma = settings.get("gamma", 6500)
        self.bluelight_scale.set_value(saved_gamma)
        self.bluelight_scale.set_value_pos(Gtk.PositionType.RIGHT)
        self.bluelight_scale.connect("value-changed", self.on_bluelight_changed)
        # Invert the scale direction (high value on left, low value on right)
        self.bluelight_scale.set_inverted(True)
        bluelight_box.pack_start(self.bluelight_scale, True, True, 0)

        # Quick blue light buttons
        bluelight_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        # Map percentage to temperature values (inverted: 0% = off = 6500K, 100% = max = 2500K)
        temp_values = {
            "0%": 6500,
            "25%": 5500,
            "50%": 4500,
            "75%": 3500,
            "100%": 2500
        }

        for label, value in temp_values.items():
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_bluelight_button_clicked, value)
            bluelight_buttons.pack_start(button, True, True, 0)

        bluelight_box.pack_start(bluelight_buttons, False, False, 0)
        bluelight_frame.add(bluelight_box)
        content_box.pack_start(bluelight_frame, False, True, 0)

        scroll_window.add(content_box)
        self.pack_start(scroll_window, True, True, 0)

    def get_current_brightness(self):
        """Get current brightness level"""
        try:
            output = subprocess.getoutput("brightnessctl get")
            max_brightness = subprocess.getoutput("brightnessctl max")
            return int((int(output) / int(max_brightness)) * 100)
        except Exception as e:
            logging.error(f"Error getting brightness: {e}")
            return 50

    def set_brightness(self, value):
        """Set brightness level"""
        try:
            max_brightness = int(subprocess.getoutput("brightnessctl max"))
            actual_value = int((value / 100) * max_brightness)
            subprocess.run(["brightnessctl", "s", f"{actual_value}"])
        except Exception as e:
            logging.error(f"Error setting brightness: {e}")

    def on_brightness_changed(self, scale):
        """Handle brightness scale changes"""
        value = scale.get_value()
        self.set_brightness(value)

    def on_brightness_button_clicked(self, button, value):
        """Handle brightness button clicks"""
        self.brightness_scale.set_value(value)
        self.set_brightness(value)

    def on_bluelight_changed(self, scale):
        """Handle blue light filter scale changes"""
        temperature = int(scale.get_value())
        settings = load_settings()
        settings["gamma"] = temperature
        save_settings(settings)

        # Kill any existing gammastep process
        subprocess.run(
            ["pkill", "-f", "gammastep"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # Start new gammastep process with new temperature
        subprocess.Popen(
            ["gammastep", "-O", str(temperature)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def on_bluelight_button_clicked(self, button, value):
        """Handle blue light filter button clicks"""
        self.bluelight_scale.set_value(value)

    def refresh_display_settings(self, button=None):
        """Refresh display settings"""
        logging.info("Manual refresh of display settings requested")

        # Block the value-changed signal before updating the brightness slider
        self.brightness_scale.disconnect_by_func(self.on_brightness_changed)

        # Update brightness slider with current value
        current_brightness = self.get_current_brightness()
        self.brightness_scale.set_value(current_brightness)

        # Reconnect the value-changed signal
        self.brightness_scale.connect("value-changed", self.on_brightness_changed)

        # Reload settings from file
        settings = load_settings()
        saved_gamma = settings.get("gamma", 6500)
        self.bluelight_scale.set_value(saved_gamma)

        logging.info(f"Display settings refreshed - Brightness: {current_brightness}%, Blue light: {saved_gamma}K")
