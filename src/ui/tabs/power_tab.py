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
        self.custom_commands = self.active_buttons.get("commands", {})

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
            "shutdown": True,
            "commands": {
                "lock": "loginctl lock-session",
                "logout": "loginctl terminate-user $USER",
                "suspend": "systemctl suspend",
                "hibernate": "systemctl hibernate",
                "reboot": "systemctl reboot",
                "shutdown": "systemctl poweroff"
            }
        }
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)
                    
                    # Ensure commands exist in settings
                    if "commands" not in settings:
                        settings["commands"] = default_settings["commands"]
                    
                    return settings
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
        
        # Create notebook for tabs
        notebook = Gtk.Notebook()
        notebook.set_size_request(400, 300)
        
        # ===== Visibility Tab =====
        visibility_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        visibility_box.set_margin_start(10)
        visibility_box.set_margin_end(10)
        visibility_box.set_margin_top(10)
        visibility_box.set_margin_bottom(10)
        
        visibility_label = Gtk.Label()
        visibility_label.set_markup("<b>Show/Hide Buttons</b>")
        visibility_label.set_halign(Gtk.Align.START)
        visibility_box.pack_start(visibility_label, False, False, 0)
        
        # Add separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        visibility_box.pack_start(separator, False, False, 5)
        
        # Create a switch for each power option
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
            visibility_box.pack_start(option_box, False, False, 5)
        
        # Add visibility tab
        visibility_tab_label = Gtk.Label(label="Buttons")
        notebook.append_page(visibility_box, visibility_tab_label)
        
        # ===== Commands Tab =====
        commands_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        commands_box.set_margin_start(10)
        commands_box.set_margin_end(10)
        commands_box.set_margin_top(10)
        commands_box.set_margin_bottom(10)
        
        commands_label = Gtk.Label()
        commands_label.set_markup("<b>Customize Commands</b>")
        commands_label.set_halign(Gtk.Align.START)
        commands_box.pack_start(commands_label, False, False, 0)
        
        # Add separator
        commands_separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        commands_box.pack_start(commands_separator, False, False, 5)
        
        # Create command entry for each power option
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_vexpand(True)
        
        commands_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        self.command_entries = {}
        for option in self.power_options:
            option_id = option["id"]
            
            # Get default command for this option
            default_cmd = ""
            if option_id == "lock":
                default_cmd = "loginctl lock-session"
            elif option_id == "logout":
                default_cmd = "loginctl terminate-user $USER"
            elif option_id == "suspend":
                default_cmd = "systemctl suspend"
            elif option_id == "hibernate":
                default_cmd = "systemctl hibernate"
            elif option_id == "reboot":
                default_cmd = "systemctl reboot"
            elif option_id == "shutdown":
                default_cmd = "systemctl poweroff"
            
            # Get current saved command or use default
            current_cmd = self.active_buttons.get("commands", {}).get(option_id, default_cmd)
            
            # Option label
            cmd_label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            
            icon = Gtk.Image.new_from_icon_name(option["icon"], Gtk.IconSize.MENU)
            cmd_label_box.pack_start(icon, False, False, 0)
            
            label = Gtk.Label(label=f"{option['label']} Command:")
            label.set_halign(Gtk.Align.START)
            cmd_label_box.pack_start(label, True, True, 0)
            
            commands_list_box.pack_start(cmd_label_box, False, False, 0)
            
            # Command entry
            entry = Gtk.Entry()
            entry.set_text(current_cmd)
            entry.set_tooltip_text(f"Command to execute when {option['label']} button is clicked")
            
            self.command_entries[option_id] = entry
            commands_list_box.pack_start(entry, False, False, 0)
            
            # Reset button
            reset_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            reset_box.set_halign(Gtk.Align.END)
            
            reset_button = Gtk.Button()
            reset_button.set_tooltip_text(f"Reset to default command")
            
            reset_icon = Gtk.Image.new_from_icon_name("edit-undo-symbolic", Gtk.IconSize.MENU)
            reset_button.add(reset_icon)
            reset_button.connect("clicked", self.on_reset_command, option_id, entry, default_cmd)
            
            reset_box.pack_end(reset_button, False, False, 0)
            commands_list_box.pack_start(reset_box, False, False, 0)
            
            # Add separator between entries
            if option != self.power_options[-1]:
                cmd_separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                commands_list_box.pack_start(cmd_separator, False, False, 5)
        
        scrolled_window.add(commands_list_box)
        commands_box.pack_start(scrolled_window, True, True, 0)
        
        # Add commands tab
        commands_tab_label = Gtk.Label(label="Commands")
        notebook.append_page(commands_box, commands_tab_label)
        
        box.pack_start(notebook, True, True, 0)
        
        # Add apply button
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(10)
        
        apply_button = Gtk.Button(label="Apply")
        apply_button.connect("clicked", self.on_apply_settings)
        button_box.pack_end(apply_button, False, False, 0)
        
        box.pack_start(button_box, False, False, 0)
        
        box.show_all()
        self.settings_popover.add(box)
    
    def on_option_toggled(self, switch, gparam, option_id):
        """Handle option switch toggle"""
        self.active_buttons[option_id] = switch.get_active()
    
    def on_reset_command(self, button, option_id, entry, default_cmd):
        """Reset command to default value"""
        entry.set_text(default_cmd)
    
    def on_apply_settings(self, button):
        """Handle apply button click"""
        # Get current commands from entries
        commands = {}
        for option_id, entry in self.command_entries.items():
            commands[option_id] = entry.get_text()
        
        # Save commands to settings
        self.active_buttons["commands"] = commands
        
        # Update custom commands
        self.custom_commands = commands
        
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
    
    def _execute_command(self, command):
        """Execute a custom command"""
        try:
            # Handle special case for USER substitution
            if "$USER" in command:
                import os
                username = os.environ.get('USER', os.environ.get('USERNAME', ''))
                command = command.replace("$USER", username)
            
            self.logging.log(LogLevel.Info, f"Executing command: {command}")
            subprocess.Popen(command.split())
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed to execute command: {e}")
    
    def on_lock_clicked(self, widget):
        """Handle lock button click"""
        command = self.custom_commands.get("lock", "loginctl lock-session")
        self.logging.log(LogLevel.Info, f"Lock button clicked, running: {command}")
        self._execute_command(command)
            
    def on_logout_clicked(self, widget):
        """Handle logout button click"""
        command = self.custom_commands.get("logout", "loginctl terminate-user $USER")
        self.logging.log(LogLevel.Info, f"Logout button clicked, running: {command}")
        self._execute_command(command)
    
    def on_suspend_clicked(self, widget):
        """Handle suspend button click"""
        command = self.custom_commands.get("suspend", "systemctl suspend")
        self.logging.log(LogLevel.Info, f"Suspend button clicked, running: {command}")
        self._execute_command(command)
            
    def on_hibernate_clicked(self, widget):
        """Handle hibernate button click"""
        command = self.custom_commands.get("hibernate", "systemctl hibernate")
        self.logging.log(LogLevel.Info, f"Hibernate button clicked, running: {command}")
        self._execute_command(command)
    
    def on_reboot_clicked(self, widget):
        """Handle reboot button click"""
        command = self.custom_commands.get("reboot", "systemctl reboot")
        self.logging.log(LogLevel.Info, f"Reboot button clicked, running: {command}")
        self._execute_command(command)
    
    def on_shutdown_clicked(self, widget):
        """Handle shutdown button click"""
        command = self.custom_commands.get("shutdown", "systemctl poweroff")
        self.logging.log(LogLevel.Info, f"Shutdown button clicked, running: {command}")
        self._execute_command(command) 