#!/usr/bin/env python3

import gi

from utils.logger import LogLevel, Logger
from utils.translations import English, Spanish, Portuguese, French # type: ignore

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject # type: ignore

from utils.settings import load_settings, save_settings


class SettingsTab(Gtk.Box):
    """Tab for application settings"""
    __gsignals__ = {
        'tab-visibility-changed': (GObject.SignalFlags.RUN_LAST, None, (str, bool,)),
        'tab-order-changed': (GObject.SignalFlags.RUN_LAST, None, (GObject.TYPE_PYOBJECT,)),
    }

    def __init__(self, logging: Logger, txt: English|Spanish|Portuguese|French):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.txt = txt
        self.logging = logging

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)
        self.set_hexpand(True)
        self.set_vexpand(True)

        # Load settings
        self.settings = load_settings(logging)

        # No scroll window - pack content directly to ensure all is visible
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.content_box.set_margin_top(10)
        self.content_box.set_margin_bottom(10)
        self.content_box.set_margin_start(10)
        self.content_box.set_margin_end(10)
        # Ensure content can expand properly
        self.content_box.set_hexpand(True)
        self.content_box.set_vexpand(True)
        self.pack_start(self.content_box, True, True, 0)

        self.populate_settings()

        self.show_all()

        self.logging.log(LogLevel.Info, "Settings UI has been created and populated")

    def populate_settings(self):
        """Populate the settings tab with options"""
        # Remove existing children if any
        for child in self.content_box.get_children():
            self.content_box.remove(child)

        # Header with Settings title and icon
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.set_margin_bottom(20)
        header_box.set_halign(Gtk.Align.START)  # Align to start
        header_box.set_hexpand(True)

        settings_icon = Gtk.Image.new_from_icon_name(
            "preferences-system-symbolic", Gtk.IconSize.DIALOG
        )
        ctx = settings_icon.get_style_context()
        ctx.add_class("settings-icon")
        
        def on_enter(widget, event):
            ctx.add_class("settings-icon-animate")
        
        def on_leave(widget, event):
            ctx.remove_class("settings-icon-animate")
        
        # Wrap in event box for hover detection
        icon_event_box = Gtk.EventBox()
        icon_event_box.add(settings_icon)
        icon_event_box.connect("enter-notify-event", on_enter)
        icon_event_box.connect("leave-notify-event", on_leave)
        
        header_box.pack_start(icon_event_box, False, False, 0)

        settings_label = Gtk.Label(label=self.txt.settings_title)
        settings_label.set_markup(f"<span size='x-large' weight='bold'>{self.txt.settings_title}</span>")
        header_box.pack_start(settings_label, False, False, 0)

        self.content_box.pack_start(header_box, False, False, 0)

        # Create a frame for the tab settings section
        settings_frame = Gtk.Frame()
        settings_frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        # Allow the frame to size to its contents
        settings_frame.set_hexpand(True)
        settings_frame.set_vexpand(True)
        settings_frame.set_margin_top(5)
        settings_frame.set_margin_bottom(5)
        self.content_box.pack_start(settings_frame, True, True, 10)

        # Tab settings section
        self.tab_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.tab_section.set_margin_top(10)
        self.tab_section.set_margin_bottom(10)
        self.tab_section.set_margin_start(10)
        self.tab_section.set_margin_end(10)
        # Allow the section to size to its contents
        self.tab_section.set_hexpand(True)
        self.tab_section.set_vexpand(True)
        settings_frame.add(self.tab_section)

        section_label = Gtk.Label(label=self.txt.settings_tab_settings)
        section_label.set_markup(f"<span weight='bold'>{self.txt.settings_tab_settings}</span>")
        section_label.set_halign(Gtk.Align.START)
        self.tab_section.pack_start(section_label, False, False, 0)

        # Create a switch for each tab
        tabs = ["Volume", "Wi-Fi", "Bluetooth", "Battery", "Display", "Power", "Autostart", "USBGuard"]
        self.tab_switches = {}
        self.tab_rows = {}

        for tab_name in tabs:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            row.set_hexpand(True)  # Allow the row to expand horizontally
            row.set_margin_top(2)
            row.set_margin_bottom(2)

            # Add up/down buttons
            button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
            button_box.set_valign(Gtk.Align.CENTER)

            up_button = Gtk.Button()
            up_button.set_image(Gtk.Image.new_from_icon_name("go-up-symbolic", Gtk.IconSize.BUTTON))
            up_button.set_relief(Gtk.ReliefStyle.NONE)
            up_button.connect("clicked", self.on_move_up_clicked, tab_name)
            button_box.pack_start(up_button, False, False, 0)
            down_button = Gtk.Button()
            down_button.set_image(Gtk.Image.new_from_icon_name("go-down-symbolic", Gtk.IconSize.BUTTON))
            down_button.set_relief(Gtk.ReliefStyle.NONE)
            down_button.connect("clicked", self.on_move_down_clicked, tab_name)
            button_box.pack_start(down_button, False, False, 0)

            # Make buttons more compact
            up_button.set_size_request(24, 24)
            down_button.set_size_request(24, 24)

            row.pack_start(button_box, False, False, 0)

            # Add tab name and switch
            label = Gtk.Label(label=f"{self.txt.show} {tab_name} tab")
            label.set_halign(Gtk.Align.START)
            # Allow label to expand and fill horizontally
            row.pack_start(label, True, True, 0)

            switch = Gtk.Switch()
            # Get visibility from settings or default to True
            visible = self.settings.get("visibility", {}).get(tab_name, True)
            switch.set_active(visible)
            switch.connect("notify::active", self.on_tab_visibility_changed, tab_name)
            # Set switch size
            switch.set_size_request(40, 20)
            switch.set_valign(Gtk.Align.CENTER)
            switch_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
            switch_box.set_size_request(50, 24)
            switch_box.set_valign(Gtk.Align.CENTER)
            switch_box.pack_start(switch, True, False, 0)
            row.pack_end(switch_box, False, False, 0)
            self.tab_switches[tab_name] = switch
            self.tab_rows[tab_name] = row

        # Add rows in the correct order
        self.update_ui_order()

        # Add separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_top(10)
        separator.set_margin_bottom(10)
        self.tab_section.pack_start(separator, False, False, 0)

        # Add language selection
        lang_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        lang_box.set_margin_top(10)
        lang_box.set_margin_bottom(10)

        lang_label = Gtk.Label(label=self.txt.settings_language)
        lang_label.set_halign(Gtk.Align.START)

        lang_combo = Gtk.ComboBoxText()
        # Add Default option at the top - this will use the system's $LANG environment variable
        # If the system language is not supported, it will fall back to English
        lang_combo.append("default", "Default (System)")
        lang_combo.append("en", "English")
        lang_combo.append("es", "Español")
        lang_combo.append("pt", "Português")
        lang_combo.append("fr", "Français")
        lang_combo.append("id", "Bahasa Indonesia")
        lang_combo.set_active_id(self.settings.get("language"))
        lang_combo.connect("changed", self.on_language_changed)

        lang_box.pack_start(lang_label, True, True, 0)
        lang_box.pack_end(lang_combo, False, False, 0)

        self.tab_section.pack_start(lang_box, False, False, 0)

    def update_ui_order(self):
        """Update the order of rows in the UI to match the current tab order"""
        # Get current tab order
        tab_order = self.settings.get("tab_order", ["Volume", "Wi-Fi", "Bluetooth", "Battery", "Display", "Power", "Autostart", "USBGuard"])

        # Make sure all known tabs are in the tab_order
        all_tabs = ["Volume", "Wi-Fi", "Bluetooth", "Battery", "Display", "Power", "Autostart", "USBGuard"]
        for tab in all_tabs:
            if tab not in tab_order:
                # If we're adding Autostart for the first time, put it before USBGuard
                if tab == "Autostart":
                    # Find the position of USBGuard
                    if "USBGuard" in tab_order:
                        autostart_index = tab_order.index("USBGuard")
                        tab_order.insert(autostart_index, tab)
                    else:
                        tab_order.append(tab)
                # If we're adding USBGuard for the first time, put it at the end
                elif tab == "USBGuard":
                    tab_order.append(tab)
                else:
                    tab_order.append(tab)

        # Update the settings with the modified order
        self.settings["tab_order"] = tab_order
        # Save the settings to the file
        save_settings(self.settings, self.logging)

        # Remove all rows from the section
        for row in self.tab_section.get_children():
            if isinstance(row, Gtk.Box) and row != self.tab_section.get_children()[0]:  # Skip the label
                self.tab_section.remove(row)
        # Add rows back in the correct order
        for tab_name in tab_order:
            if tab_name in self.tab_rows:
                # Ensure each row has proper expansion properties
                self.tab_rows[tab_name].set_hexpand(True)
                self.tab_rows[tab_name].set_margin_top(4)
                self.tab_rows[tab_name].set_margin_bottom(4)
                self.tab_section.pack_start(self.tab_rows[tab_name], False, False, 2)

    def on_tab_visibility_changed(self, switch, gparam, tab_name):
        """Handle tab visibility changes"""
        active = switch.get_active()

        # Ensure visibility dict exists
        if "visibility" not in self.settings:
            self.settings["visibility"] = {}

        # Update settings
        self.settings["visibility"][tab_name] = active
        save_settings(self.settings, self.logging)

        # Emit signal to notify the main window
        self.emit("tab-visibility-changed", tab_name, active)

    def on_move_up_clicked(self, button, tab_name):
        """Handle move up button click"""
        # Get current tab order
        tab_order = self.settings.get("tab_order", ["Volume", "Wi-Fi", "Bluetooth", "Battery", "Display", "Power", "Autostart", "USBGuard"])
        # Find current index
        current_index = tab_order.index(tab_name)
        if current_index > 0:
            # Swap with previous tab
            tab_order[current_index], tab_order[current_index - 1] = tab_order[current_index - 1], tab_order[current_index]

            # Update settings
            self.settings["tab_order"] = tab_order
            save_settings(self.settings, self.logging)

            # Update UI order
            self.update_ui_order()

            # Emit signal to notify the main window
            self.emit("tab-order-changed", tab_order)

    def on_move_down_clicked(self, button, tab_name):
        """Handle move down button click"""
        # Get current tab order
        tab_order = self.settings.get("tab_order", ["Volume", "Wi-Fi", "Bluetooth", "Battery", "Display", "Power", "Autostart", "USBGuard"])

        # Find current index
        current_index = tab_order.index(tab_name)

        # Don't allow moving down if it's already the last tab
        if current_index >= len(tab_order) - 1:
            return

        # Swap with next tab
        tab_order[current_index], tab_order[current_index + 1] = tab_order[current_index + 1], tab_order[current_index]

        # Update settings
        self.settings["tab_order"] = tab_order
        save_settings(self.settings, self.logging)

        # Update UI order
        self.update_ui_order()

        # Emit signal to notify the main window
        self.emit("tab-order-changed", tab_order)

    def save_window_size(self, width: int, height: int):
        """Save window size to settings

        Args:
            width (int): Window width
            height (int): Window height
        """
        # We're no longer directly controlling size through settings,
        # but we'll still save the last used size for reference
        if "window_size" not in self.settings:
            self.settings["window_size"] = {}

        self.settings["window_size"]["settings_width"] = width
        self.settings["window_size"]["settings_height"] = height
        save_settings(self.settings, self.logging)
        self.logging.log(LogLevel.Info, f"Saved reference window size: {width}x{height}")

    def on_language_changed(self, combo):
        """Handle language changes"""
        lang = combo.get_active_id()
        self.settings["language"] = lang
        self.logging.log(LogLevel.Info, f"Language changed to {lang}, saving settings")

        # Make sure the language setting is at the top level of the settings dictionary
        if "language" not in self.settings:
            self.logging.log(LogLevel.Warn, "Language key not in settings, adding it")

        # Save settings
        save_settings(self.settings, self.logging)

        # Verify settings were saved
        saved_settings = load_settings(self.logging)
        if saved_settings.get("language") == lang:
            self.logging.log(LogLevel.Info, f"Language setting verified: {saved_settings.get('language')}")
        else:
            self.logging.log(LogLevel.Error, f"Language setting not saved correctly. Expected: {lang}, Got: {saved_settings.get('language')}")

            # Force the language setting in the file
            self.logging.log(LogLevel.Info, "Forcing language setting in configuration file")
            saved_settings["language"] = lang
            save_settings(saved_settings, self.logging)

        # Update the main window's settings as well
        parent_window = self.get_toplevel()
        if hasattr(parent_window, 'settings'):
            parent_window.settings["language"] = lang
            self.logging.log(LogLevel.Info, f"Updated main window's language setting to {lang}")

        # Show restart dialog
        dialog = Gtk.MessageDialog(
            transient_for=self.get_toplevel(),
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=self.txt.settings_language_changed
        )
        dialog.format_secondary_text(
            self.txt.settings_language_changed_restart
        )
        dialog.run()
        dialog.destroy()
