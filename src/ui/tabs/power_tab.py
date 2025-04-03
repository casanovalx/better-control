#!/usr/bin/env python3

import gi  # type: ignore
gi.require_version('Gtk', '3.0')
import subprocess
from gi.repository import Gtk, GLib, Gdk  # type: ignore
from utils.logger import LogLevel, Logger

class PowerTab(Gtk.Box):
    """Power management tab with suspend, shutdown and reboot options"""

    def __init__(self, logging: Logger):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        self.logging = logging

        # Set margins to match other tabs
        self.set_margin_start(15)
        self.set_margin_end(15)
        self.set_margin_top(15)
        self.set_margin_bottom(15)
        self.set_hexpand(True)
        self.set_vexpand(True)
        
        # Create header box with title
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header_box.set_hexpand(True)
        header_box.set_margin_bottom(10)

        # Create title box with icon and label
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        # Add power icon with larger size
        power_icon = Gtk.Image.new_from_icon_name(
            "system-shutdown-symbolic", Gtk.IconSize.DIALOG
        )
        title_box.pack_start(power_icon, False, False, 0)

        # Add title with better styling
        title_label = Gtk.Label()
        title_label.set_markup(
            "<span weight='bold' size='large'>Power Management</span>"
        )
        title_label.get_style_context().add_class("header-title")
        title_label.set_halign(Gtk.Align.START)
        title_box.pack_start(title_label, False, False, 0)

        header_box.pack_start(title_box, True, True, 0)
        self.pack_start(header_box, False, False, 0)
        
        # Create a description label
        description = Gtk.Label()
        description.set_markup("<span>Select a power option below:</span>")
        description.set_halign(Gtk.Align.START)
        description.set_margin_bottom(15)
        self.pack_start(description, False, False, 0)
        
        # Create a container for power buttons
        power_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        power_box.set_halign(Gtk.Align.CENTER)
        power_box.set_valign(Gtk.Align.CENTER)
        power_box.set_vexpand(True)
        
        # Suspend button
        suspend_box = self._create_power_button(
            "Suspend",
            "system-suspend-symbolic",
            "Suspend the system (sleep)",
            self.on_suspend_clicked
        )
        power_box.pack_start(suspend_box, False, False, 0)
        
        # Reboot button
        reboot_box = self._create_power_button(
            "Reboot",
            "system-reboot-symbolic",
            "Restart the system",
            self.on_reboot_clicked
        )
        power_box.pack_start(reboot_box, False, False, 0)
        
        # Shutdown button
        shutdown_box = self._create_power_button(
            "Shutdown",
            "system-shutdown-symbolic",
            "Power off the system",
            self.on_shutdown_clicked
        )
        power_box.pack_start(shutdown_box, False, False, 0)
        
        self.pack_start(power_box, True, True, 0)
        
    def _create_power_button(self, label_text, icon_name, tooltip, callback):
        """Create a power button with icon and label"""
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.CENTER)
        
        button = Gtk.Button()
        button.set_tooltip_text(tooltip)
        button.connect("clicked", callback)
        
        # Set up button contents
        content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
        label = Gtk.Label(label=label_text)
        label.set_halign(Gtk.Align.START)
        
        content_box.pack_start(icon, False, False, 0)
        content_box.pack_start(label, False, False, 0)
        
        button.add(content_box)
        button.set_size_request(150, 50)
        
        button_box.pack_start(button, False, False, 0)
        return button_box
    
    def on_suspend_clicked(self, widget):
        """Handle suspend button click"""
        self.logging.log(LogLevel.Info, "Suspend button clicked, running systemctl suspend")
        try:
            subprocess.Popen(["systemctl", "suspend"])
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed to suspend: {e}")
    
    def on_reboot_clicked(self, widget):
        """Handle reboot button click"""
        self.logging.log(LogLevel.Info, "Reboot button clicked, running systemctl reboot")
        try:
            subprocess.Popen(["systemctl", "reboot"])
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed to reboot: {e}")
    
    def on_shutdown_clicked(self, widget):
        """Handle shutdown button click"""
        self.logging.log(LogLevel.Info, "Shutdown button clicked, running systemctl poweroff")
        try:
            subprocess.Popen(["systemctl", "poweroff"])
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed to shutdown: {e}") 