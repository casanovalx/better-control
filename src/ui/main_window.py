#!/usr/bin/env python3

import gi
import logging

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from ui.tabs.battery_tab import BatteryTab
from ui.tabs.bluetooth_tab import BluetoothTab
from ui.tabs.display_tab import DisplayTab
from ui.tabs.volume_tab import VolumeTab
from ui.tabs.wifi_tab import WiFiTab
from ui.tabs.settings_tab import SettingsTab
from config.settings import load_settings, save_settings

class BetterControl(Gtk.Window):
    """Main application window"""

    def __init__(self, args):
        super().__init__(title="Better Control")
        self.set_default_size(600, 400)
        
        logging.info("Initializing Better Control application")

        # Load settings
        self.settings = load_settings()
        logging.info("Settings loaded")

        # Create notebook for tabs
        self.notebook = Gtk.Notebook()
        self.add(self.notebook)
        
        # Track tabs for visibility management
        self.tabs = {}
        self.tab_pages = {}

        # Create tabs
        self.create_tabs()
        
        # Add settings button to the notebook action area
        self.create_settings_button()

        # Apply initial tab visibility and order
        self.apply_tab_visibility()
        self.apply_tab_order()

        # Set active tab based on command line arguments
        if args.volume:
            self.notebook.set_current_page(0)
        elif args.wifi:
            self.notebook.set_current_page(1)
        elif args.bluetooth:
            self.notebook.set_current_page(2)
        elif args.battery:
            self.notebook.set_current_page(3)
        elif args.display:
            self.notebook.set_current_page(4)
        else:
            # Use last active tab from settings
            last_tab = self.settings.get("last_active_tab", 0)
            self.notebook.set_current_page(last_tab)

        # Connect signals
        self.connect("destroy", self.on_destroy)
        self.notebook.connect("switch-page", self.on_tab_switched)

    def create_tabs(self):
        """Create all tabs"""
        logging.info("Creating application tabs")
        # Create tab instances
        self.tabs["Volume"] = VolumeTab()
        self.tabs["Wi-Fi"] = WiFiTab()
        self.tabs["Bluetooth"] = BluetoothTab()
        self.tabs["Battery"] = BatteryTab()
        self.tabs["Display"] = DisplayTab()
        logging.info("All tabs created successfully")

    def apply_tab_visibility(self):
        """Apply tab visibility settings"""
        visibility = self.settings.get("visibility", {})
        
        # Iterate through all tabs
        for tab_name, tab in self.tabs.items():
            # Default to showing tab if no setting exists
            should_show = visibility.get(tab_name, True)
            
            # Get the current position if it exists
            page_num = -1
            for i in range(self.notebook.get_n_pages()):
                if self.notebook.get_nth_page(i) == tab:
                    page_num = i
                    break
            
            # Apply visibility
            if should_show and page_num == -1:
                # Need to add the tab
                page_num = self.notebook.append_page(
                    tab, 
                    self.create_tab_label(tab_name, self.get_icon_for_tab(tab_name))
                )
                self.tab_pages[tab_name] = page_num
            elif not should_show and page_num != -1:
                # Need to remove the tab
                self.notebook.remove_page(page_num)
                # Update page numbers for tabs after this one
                for name, num in self.tab_pages.items():
                    if num > page_num:
                        self.tab_pages[name] = num - 1

    def apply_tab_order(self):
        """Apply tab order settings"""
        # Get current tab order from settings or use default
        tab_order = self.settings.get("tab_order", ["Volume", "Wi-Fi", "Bluetooth", "Battery", "Display"])
        
        # Reorder tabs according to settings
        for tab_name in tab_order:
            if tab_name in self.tabs and tab_name in self.tab_pages:
                # Get current page number
                current_page = self.tab_pages[tab_name]
                # Move tab to end (will be reordered in correct position)
                self.notebook.reorder_child(self.tabs[tab_name], -1)
                # Update page numbers
                for name, num in self.tab_pages.items():
                    if num > current_page:
                        self.tab_pages[name] = num - 1
                self.tab_pages[tab_name] = len(self.tab_pages)

    def get_icon_for_tab(self, tab_name):
        """Get icon name for a tab"""
        icons = {
            "Volume": "audio-volume-high-symbolic",
            "Wi-Fi": "network-wireless-symbolic",
            "Bluetooth": "bluetooth-symbolic",
            "Battery": "battery-good-symbolic",
            "Display": "video-display-symbolic",
            "Settings": "preferences-system-symbolic"
        }
        return icons.get(tab_name, "application-x-executable-symbolic")

    def create_settings_button(self):
        """Create settings button in the notebook action area"""
        settings_button = Gtk.Button()
        settings_icon = Gtk.Image.new_from_icon_name(
            "preferences-system-symbolic", Gtk.IconSize.BUTTON
        )
        settings_button.set_image(settings_icon)
        settings_button.set_tooltip_text("Settings")
        
        # Connect the clicked signal
        settings_button.connect("clicked", self.toggle_settings_panel)
        
        # Add to the notebook action area
        self.notebook.set_action_widget(settings_button, Gtk.PackType.END)
        settings_button.show_all()
        
        print("Settings button created and attached to notebook")

    def toggle_settings_panel(self, widget):
        """Toggle the settings panel visibility"""
        print("Settings button clicked, opening settings dialog")
        
        try:
            # Create a dialog window for settings
            dialog = Gtk.Dialog(
                title="Settings", 
                parent=self, 
                flags=Gtk.DialogFlags.MODAL,
                buttons=(
                    Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE
                )
            )
            dialog.set_default_size(500, 400)
            dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
            
            # Create a fresh instance of the settings tab to use in the dialog
            settings_tab = SettingsTab()
            settings_tab.connect("tab-visibility-changed", self.on_tab_visibility_changed)
            settings_tab.connect("tab-order-changed", self.on_tab_order_changed)
            
            # Add the settings content to the dialog's content area
            content_area = dialog.get_content_area()
            content_area.add(settings_tab)
            content_area.set_border_width(10)
            
            # Show the dialog and all its contents
            dialog.show_all()
            
            # Run the dialog
            response = dialog.run()
            
            if response == Gtk.ResponseType.CLOSE:
                print("Settings dialog closed")
            
            # Clean up the dialog
            dialog.destroy()
            
        except Exception as e:
            print(f"Error in toggle_settings_panel: {e}")
            import traceback
            traceback.print_exc()

    def on_tab_visibility_changed(self, widget, tab_name, visible):
        """Handle tab visibility changed signal from settings tab"""
        # Update settings
        if "visibility" not in self.settings:
            self.settings["visibility"] = {}
        self.settings["visibility"][tab_name] = visible
        save_settings(self.settings)
        
        # Apply the change
        if tab_name in self.tabs:
            tab = self.tabs[tab_name]
            page_num = -1
            
            # Find current page number if tab is present
            for i in range(self.notebook.get_n_pages()):
                if self.notebook.get_nth_page(i) == tab:
                    page_num = i
                    break
                    
            if visible and page_num == -1:
                # Need to add the tab
                page_num = self.notebook.append_page(
                    tab, 
                    self.create_tab_label(tab_name, self.get_icon_for_tab(tab_name))
                )
                self.tab_pages[tab_name] = page_num
            elif not visible and page_num != -1:
                # Need to remove the tab
                self.notebook.remove_page(page_num)
                # Update page numbers for tabs after this one
                for name, num in self.tab_pages.items():
                    if num > page_num:
                        self.tab_pages[name] = num - 1

    def on_tab_order_changed(self, widget, tab_order):
        """Handle tab order changed signal from settings tab"""
        # Update settings
        self.settings["tab_order"] = tab_order
        save_settings(self.settings)
        
        # Apply the new order
        self.apply_tab_order()

    def create_tab_label(self, text: str, icon_name: str) -> Gtk.Box:
        """Create a tab label with icon and text

        Args:
            text (str): Tab label text
            icon_name (str): Icon name

        Returns:
            Gtk.Box: Box containing icon and label
        """
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
        label = Gtk.Label(label=text)
        box.pack_start(icon, False, False, 0)
        box.pack_start(label, False, False, 0)
        box.show_all()
        return box

    def on_destroy(self, window):
        """Save settings and quit"""
        # Save current tab
        self.settings["last_active_tab"] = self.notebook.get_current_page()
        # Save settings
        save_settings(self.settings)
        logging.info("Application shutting down, settings saved")

    def on_tab_switched(self, notebook, page, page_num):
        """Handle tab switching"""
        # Save current tab
        self.settings["last_active_tab"] = page_num
        save_settings(self.settings)
        
        # Get tab name for logging
        for tab_name, tab_index in self.tab_pages.items():
            if tab_index == page_num:
                logging.info(f"Switched to {tab_name} tab")
                break 