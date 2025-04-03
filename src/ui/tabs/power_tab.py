#!/usr/bin/env python3

import gi  # type: ignore
gi.require_version('Gtk', '3.0')
import subprocess
import json
import os
from gi.repository import Gtk, GLib, Gdk  # type: ignore
from utils.logger import LogLevel, Logger

class PowerTab(Gtk.Box):
    """Power management tab with suspend, shutdown and reboot options"""

    def __init__(self, logging: Logger):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        self.logging = logging
        
        # Set default button visibility
        self.config_file = os.path.expanduser("~/.config/better-control/power_settings.json")
        self.active_buttons = self._load_settings()

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
        header_box.set_margin_bottom(20)

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
            "<span weight='bold' size='x-large'>Power Management</span>"
        )
        title_label.get_style_context().add_class("header-title")
        title_label.set_halign(Gtk.Align.START)
        title_box.pack_start(title_label, False, False, 0)

        header_box.pack_start(title_box, True, True, 0)
        
        # Create settings button
        settings_button = Gtk.Button()
        settings_button.set_tooltip_text("Configure Power Menu")
        settings_icon = Gtk.Image.new_from_icon_name(
            "emblem-system-symbolic", Gtk.IconSize.MENU
        )
        settings_button.add(settings_icon)
        settings_button.get_style_context().add_class("flat")
        settings_button.connect("clicked", self.on_settings_clicked)
        header_box.pack_end(settings_button, False, False, 0)
        
        self.pack_start(header_box, False, False, 0)
        
        # Grid container
        self.grid_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.grid_container.set_hexpand(True)
        self.grid_container.set_vexpand(True)
        
        # Define power options with metadata
        self.power_options = [
            {
                "id": "lock",
                "label": "Lock",
                "icon": "system-lock-screen-symbolic",
                "tooltip": "Lock the screen",
                "callback": self.on_lock_clicked,
                "color": "#4A90D9"
            },
            {
                "id": "logout",
                "label": "Logout",
                "icon": "system-log-out-symbolic",
                "tooltip": "Log out of the current session",
                "callback": self.on_logout_clicked,
                "color": "#729FCF"
            },
            {
                "id": "suspend",
                "label": "Suspend",
                "icon": "system-suspend-symbolic",
                "tooltip": "Suspend the system (sleep)",
                "callback": self.on_suspend_clicked,
                "color": "#8DB67A"
            },
            {
                "id": "hibernate",
                "label": "Hibernate",
                "icon": "document-save-symbolic",
                "tooltip": "Hibernate the system",
                "callback": self.on_hibernate_clicked,
                "color": "#AD7FA8"
            },
            {
                "id": "reboot",
                "label": "Reboot",
                "icon": "system-reboot-symbolic",
                "tooltip": "Restart the system",
                "callback": self.on_reboot_clicked,
                "color": "#F8C146"
            },
            {
                "id": "shutdown",
                "label": "Shutdown",
                "icon": "system-shutdown-symbolic",
                "tooltip": "Power off the system",
                "callback": self.on_shutdown_clicked,
                "color": "#EF5350"
            }
        ]
        
        # Build the grid with active buttons
        self._build_power_grid()
        self.pack_start(self.grid_container, True, True, 0)
        
        # Create settings popover
        self.settings_popover = Gtk.Popover()
        self.settings_popover.set_position(Gtk.PositionType.BOTTOM)
        self.settings_popover.set_relative_to(settings_button)
        
        # Create content for settings popover
        self._create_settings_content()
        
        # Add CSS for styling
        self._add_css()
    
    def _load_settings(self):
        """Load power menu button settings"""
        default_settings = {
            "lock": True,
            "logout": True,
            "suspend": True,
            "hibernate": True,
            "reboot": True,
            "shutdown": True
        }
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                # Create default settings file
                with open(self.config_file, 'w') as f:
                    json.dump(default_settings, f, indent=2)
                return default_settings
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed to load power settings: {e}")
            return default_settings
    
    def _save_settings(self):
        """Save power menu button settings"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.active_buttons, f, indent=2)
            self.logging.log(LogLevel.Info, "Power menu settings saved")
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed to save power settings: {e}")
    
    def _build_power_grid(self):
        """Build the power buttons grid based on active buttons"""
        # Clear existing children
        for child in self.grid_container.get_children():
            self.grid_container.remove(child)
        
        # Create new grid
        grid = Gtk.Grid()
        grid.set_row_spacing(20)
        grid.set_column_spacing(20)
        grid.set_row_homogeneous(True)
        grid.set_column_homogeneous(True)
        grid.set_halign(Gtk.Align.FILL)
        grid.set_valign(Gtk.Align.FILL)
        grid.set_hexpand(True)
        grid.set_vexpand(True)
        
        # Filter and add only active buttons
        active_options = [option for option in self.power_options 
                          if self.active_buttons.get(option["id"], True)]
        
        # Calculate optimal grid dimensions to make it as square as possible
        num_buttons = len(active_options)
        
        # Determine best grid dimensions based on number of buttons
        if num_buttons <= 1:
            columns = 1
        elif num_buttons == 2:
            columns = 2  # 2 in a row
        elif num_buttons <= 4:
            columns = 2  # 2x2 grid
        elif num_buttons <= 6:
            columns = 3  # 3x2 grid
        elif num_buttons <= 9:
            columns = 3  # 3x3 grid
        elif num_buttons <= 12:
            columns = 4  # 3x4 grid
        else:
            columns = 4  # Default for larger numbers
        
        # Adjust button size based on grid dimensions
        button_size = 140 if columns <= 2 else 120
        
        # Create and arrange buttons in a grid
        for i, option in enumerate(active_options):
            button = self._create_power_button(
                option["label"],
                option["icon"],
                option["tooltip"],
                option["callback"],
                option["color"],
                button_size
            )
            
            row = i // columns
            col = i % columns
            
            grid.attach(button, col, row, 1, 1)
        
        self.grid_container.pack_start(grid, True, True, 0)
        self.grid_container.show_all()
    
    def _create_settings_content(self):
        """Create content for settings popover"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        
        # Add title
        title = Gtk.Label(label="Configure Power Menu Buttons")
        title.set_halign(Gtk.Align.START)
        title.set_markup("<b>Configure Power Menu Buttons</b>")
        box.pack_start(title, False, False, 5)
        
        # Add separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        box.pack_start(separator, False, False, 5)
        
        # Create a checkbox for each power option
        self.option_switches = {}
        for option in self.power_options:
            option_id = option["id"]
            option_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            
            # Create icon
            icon = Gtk.Image.new_from_icon_name(option["icon"], Gtk.IconSize.MENU)
            option_box.pack_start(icon, False, False, 0)
            
            # Create label
            label = Gtk.Label(label=option["label"])
            label.set_halign(Gtk.Align.START)
            option_box.pack_start(label, True, True, 0)
            
            # Create switch
            switch = Gtk.Switch()
            switch.set_active(self.active_buttons.get(option_id, True))
            switch.connect("notify::active", self.on_option_toggled, option_id)
            
            self.option_switches[option_id] = switch
            option_box.pack_end(switch, False, False, 0)
            box.pack_start(option_box, False, False, 5)
        
        # Add separator
        separator2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        box.pack_start(separator2, False, False, 5)
        
        # Add apply button
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        button_box.set_halign(Gtk.Align.END)
        
        apply_button = Gtk.Button(label="Apply")
        apply_button.connect("clicked", self.on_apply_settings)
        button_box.pack_end(apply_button, False, False, 0)
        
        box.pack_start(button_box, False, False, 5)
        
        box.show_all()
        self.settings_popover.add(box)
        
    def on_option_toggled(self, switch, gparam, option_id):
        """Handle option switch toggle"""
        self.active_buttons[option_id] = switch.get_active()
    
    def on_apply_settings(self, button):
        """Handle apply button click"""
        self._save_settings()
        self._build_power_grid()
        self.settings_popover.popdown()
        
    def on_settings_clicked(self, button):
        """Handle settings button click"""
        self.settings_popover.popup()
        
    def _add_css(self):
        """Add CSS styling for power buttons"""
        css_provider = Gtk.CssProvider()
        css = """
        .power-button {
            border-radius: 12px;
            transition: all 200ms ease;
        }
        
        .power-button:hover {
            opacity: 0.9;
        }
        
        .power-button-label {
            color: white;
            font-weight: bold;
            font-size: 14px;
            text-shadow: 0px 1px 2px rgba(0, 0, 0, 0.5);
        }
        
        .power-button-icon {
            color: white;
            -gtk-icon-shadow: 0px 1px 2px rgba(0, 0, 0, 0.5);
        }
        """
        css_provider.load_from_data(css.encode())
        
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
    def _create_power_button(self, label_text, icon_name, tooltip, callback, color, size=120):
        """Create a styled power button with icon and label"""
        button = Gtk.Button()
        button.set_tooltip_text(tooltip)
        button.connect("clicked", callback)
        button.set_size_request(size, size)
        
        # Apply CSS class
        button.get_style_context().add_class("power-button")
        
        # Add custom background color
        button_style = f".power-button {{ background-color: {color}; }}"
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(button_style.encode())
        button.get_style_context().add_provider(
            css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        # Set up button contents
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content_box.set_halign(Gtk.Align.CENTER)
        content_box.set_valign(Gtk.Align.CENTER)
        
        # Create larger icon
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DIALOG)
        icon.get_style_context().add_class("power-button-icon")
        content_box.pack_start(icon, False, False, 0)
        
        # Create label
        label = Gtk.Label(label=label_text)
        label.get_style_context().add_class("power-button-label")
        content_box.pack_start(label, False, False, 0)
        
        button.add(content_box)
        
        return button
    
    def on_lock_clicked(self, widget):
        """Handle lock button click"""
        self.logging.log(LogLevel.Info, "Lock button clicked, running loginctl lock-session")
        try:
            subprocess.Popen(["loginctl", "lock-session"])
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed to lock: {e}")
            
    def on_logout_clicked(self, widget):
        """Handle logout button click"""
        self.logging.log(LogLevel.Info, "Logout button clicked, running loginctl terminate-user $USER")
        try:
            import os
            username = os.environ.get('USER', os.environ.get('USERNAME'))
            subprocess.Popen(["loginctl", "terminate-user", username])
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed to logout: {e}")
    
    def on_suspend_clicked(self, widget):
        """Handle suspend button click"""
        self.logging.log(LogLevel.Info, "Suspend button clicked, running systemctl suspend")
        try:
            subprocess.Popen(["systemctl", "suspend"])
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed to suspend: {e}")
            
    def on_hibernate_clicked(self, widget):
        """Handle hibernate button click"""
        self.logging.log(LogLevel.Info, "Hibernate button clicked, running systemctl hibernate")
        try:
            subprocess.Popen(["systemctl", "hibernate"])
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed to hibernate: {e}")
    
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