#!/usr/bin/env python3

import logging
import timeit
import traceback
import gi  # type: ignore
import threading
import sys
 
from utils.arg_parser import ArgParse

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk  # type: ignore

from ui.tabs.autostart_tab import AutostartTab
from ui.tabs.battery_tab import BatteryTab
from ui.tabs.bluetooth_tab import BluetoothTab
from ui.tabs.display_tab import DisplayTab
from ui.tabs.power_tab import PowerTab
from ui.tabs.volume_tab import VolumeTab
from ui.tabs.wifi_tab import WiFiTab
from ui.tabs.settings_tab import SettingsTab
from utils.settings import load_settings, save_settings
from utils.logger import LogLevel, Logger


class BetterControl(Gtk.Window):

    def __init__(self, arg_parser: ArgParse, logging: Logger) -> None:
        super().__init__(title="Better Control")

        self.logging = logging
        self.set_default_size(600, 400)
        self.logging.log(LogLevel.Info, "Initializing application")

        # Apply custom CSS to remove button focus/selection outline
        css_provider = Gtk.CssProvider()
        css = b"""
            button {
                outline: none;
                -gtk-outline-radius: 0;
                border: none;
            }
            button:focus, button:hover, button:active {
                outline: none;
                box-shadow: none;
                border: none;
            }
            notebook tab {
                outline: none;
            }
            notebook tab:focus {
                outline: none;
            }
            /* Make selections invisible */
            selection {
                background-color: transparent;
                color: inherit;
            }
            *:selected {
                background-color: transparent;
                color: inherit;
            }
            textview text selection {
                background-color: transparent;
            }
            entry selection {
                background-color: transparent;
            }
            label selection {
                background-color: transparent;
            }
            treeview:selected {
                background-color: transparent;
            }
            menuitem:selected {
                background-color: transparent;
            }
            listbox row:selected {
                background-color: transparent;
            }
        """
        css_provider.load_from_data(css)
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.settings = load_settings(logging)
        self.logging.log(LogLevel.Info, "Settings loaded")

        self.notebook = Gtk.Notebook()
        self.add(self.notebook)
        
        # Connect key-press-event to disable tab selection with Tab key
        self.notebook.connect("key-press-event", self.on_notebook_key_press)
        # Also connect key-press-event to the main window to catch all tab presses
        self.connect("key-press-event", self.on_key_press)

        self.tabs = {}
        self.tab_pages = {}

        self.loading_spinner = Gtk.Spinner()
        self.loading_spinner.start()

        self.loading_label = Gtk.Label(label="Loading tabs...")
        loading_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        loading_box.set_halign(Gtk.Align.CENTER)
        loading_box.set_valign(Gtk.Align.CENTER)
        loading_box.pack_start(self.loading_spinner, False, False, 0)
        loading_box.pack_start(self.loading_label, False, False, 0)
        self.loading_page = self.notebook.append_page(
            loading_box, Gtk.Label(label="Loading...")
        )

        self.create_tabs_async()
        self.create_settings_button()
        self.arg_parser = arg_parser

        self.connect("destroy", self.on_destroy)
        self.notebook.connect("switch-page", self.on_tab_switched)

    def create_tabs_async(self):
        """Create all tabs asynchronously"""
        self.logging.log(LogLevel.Info, "Starting asynchronous tab creation")
        # Start a thread to create tabs in the background
        thread = threading.Thread(target=self._create_tabs_thread)
        thread.daemon = True
        thread.start()

    def _create_tabs_thread(self):
        """Thread function to create tabs"""
        # Create all tabs
        tab_classes = {
            "Volume": VolumeTab,
            "Wi-Fi": WiFiTab,
            "Bluetooth": BluetoothTab,
            "Battery": BatteryTab,
            "Display": DisplayTab,
            "Power": PowerTab,
            "Autostart": AutostartTab,
        }
        
        # Track if thread is still running to avoid segfaults during shutdown
        self.tabs_thread_running = True
        
        # Create tabs one by one
        for tab_name, tab_class in tab_classes.items():
            try:
                # Check if thread should still run
                if not hasattr(self, 'tabs_thread_running') or not self.tabs_thread_running:
                    self.logging.log(LogLevel.Info, "Tab creation thread stopped")
                    return
                    
                # Create the tab
                self.logging.log(LogLevel.Debug, f"Starting to create {tab_name} tab")
                tab = tab_class(self.logging)
                self.logging.log(LogLevel.Debug, f"Successfully created {tab_name} tab instance")

                # Update UI from main thread safely
                GLib.idle_add(self._add_tab_to_ui, tab_name, tab)

                # Small delay to avoid blocking the UI
                GLib.usleep(10000)  # 10ms delay

            except Exception as e:
                error_msg = f"Failed creating {tab_name} tab: {e}"
                self.logging.log(LogLevel.Error, error_msg)
                # Print full traceback to stderr
                import traceback
                traceback.print_exc()
                print(f"FATAL ERROR: {error_msg}", file=sys.stderr)

        # Complete initialization on main thread
        GLib.idle_add(self._finish_tab_loading)
        
        # Mark thread as completed
        self.tabs_thread_running = False

    def _add_tab_to_ui(self, tab_name, tab):
        """Add a tab to the UI (called from main thread)"""
        self.tabs[tab_name] = tab

        # Make sure tab is visible
        tab.show_all()

        # Check visibility settings
        visibility = self.settings.get("visibility", {})
        should_show = visibility.get(tab_name, True)

        if should_show:
            # Add tab to notebook with proper label
            page_num = self.notebook.append_page(
                tab, self.create_tab_label(tab_name, self.get_icon_for_tab(tab_name))
            )
            self.tab_pages[tab_name] = page_num

        self.logging.log(LogLevel.Info, f"Created {tab_name} tab")
        return False  # Required for GLib.idle_add

    def _finish_tab_loading(self):
        """Finish tab loading by applying visibility and order (on main thread)"""
        try:
            self.logging.log(LogLevel.Info, "All tabs created, finalizing UI")
    
            # Ensure all tabs are present in the tab_order setting
            tab_order = self.settings.get("tab_order", ["Volume", "Wi-Fi", "Bluetooth", "Battery", "Display", "Power", "Autostart"])
            
            # Make sure all created tabs are in the tab_order
            for tab_name in self.tabs.keys():
                if tab_name not in tab_order:
                    # If we're adding Power for the first time, put it before Autostart
                    if tab_name == "Power":
                        # Find the position of Autostart
                        if "Autostart" in tab_order:
                            autostart_index = tab_order.index("Autostart")
                            tab_order.insert(autostart_index, tab_name)
                        else:
                            tab_order.append(tab_name)
                    # If we're adding Autostart for the first time, put it at the end
                    elif tab_name == "Autostart":
                        tab_order.append(tab_name)
                    else:
                        tab_order.append(tab_name)
            
            # Update the settings with the complete tab list
            self.settings["tab_order"] = tab_order
    
            # Apply tab order (visibility is already applied)
            try:
                self.apply_tab_order()
            except Exception as e:
                self.logging.log(LogLevel.Error, f"Error applying tab order: {e}")
    
            # Show all tabs to ensure content is visible
            self.show_all()
    
            # Log tab page numbers for debugging
            self.logging.log(
                LogLevel.Debug, f"Tab pages: {self.tab_pages}"
            )
    
            # Initialize the active tab
            active_tab = None
            
            # Set active tab based on command line arguments
            if (self.arg_parser.find_arg(("-V", "--volume")) or self.arg_parser.find_arg(("-v", ""))) and "Volume" in self.tab_pages:
                page_num = self.tab_pages["Volume"]
                self.logging.log(LogLevel.Info, f"Setting active tab to Volume (page {page_num})")
                self.notebook.set_current_page(page_num)
                active_tab = "Volume"
            elif self.arg_parser.find_arg(("-w", "--wifi")) and "Wi-Fi" in self.tab_pages:
                page_num = self.tab_pages["Wi-Fi"]
                self.logging.log(LogLevel.Info, f"Setting active tab to Wi-Fi (page {page_num})")
                self.notebook.set_current_page(page_num)
                active_tab = "Wi-Fi"
            elif (
                self.arg_parser.find_arg(("-a", "--autostart"))
                and "Autostart" in self.tab_pages
            ):
                page_num = self.tab_pages["Autostart"]
                self.logging.log(LogLevel.Info, f"Setting active tab to Autostart (page {page_num})")
                self.notebook.set_current_page(page_num)
                active_tab = "Autostart"
            elif (
                self.arg_parser.find_arg(("-b", "--bluetooth"))
                and "Bluetooth" in self.tab_pages
            ):
                page_num = self.tab_pages["Bluetooth"]
                self.logging.log(LogLevel.Info, f"Setting active tab to Bluetooth (page {page_num})")
                self.notebook.set_current_page(page_num)
                active_tab = "Bluetooth"
            elif (
                self.arg_parser.find_arg(("-B", "--battery"))
                and "Battery" in self.tab_pages
            ):
                page_num = self.tab_pages["Battery"]
                self.logging.log(LogLevel.Info, f"Setting active tab to Battery (page {page_num})")
                self.notebook.set_current_page(page_num)
                active_tab = "Battery"
            elif (
                self.arg_parser.find_arg(("-d", "--display"))
                and "Display" in self.tab_pages
            ):
                page_num = self.tab_pages["Display"]
                self.logging.log(LogLevel.Info, f"Setting active tab to Display (page {page_num})")
                self.notebook.set_current_page(page_num)
                active_tab = "Display"
            elif (
                self.arg_parser.find_arg(("-p", "--power"))
                and "Power" in self.tab_pages
            ):
                page_num = self.tab_pages["Power"]
                self.logging.log(LogLevel.Info, f"Setting active tab to Power (page {page_num})")
                self.notebook.set_current_page(page_num)
                active_tab = "Power"
            else:
                # Use last active tab from settings
                last_tab = self.settings.get("last_active_tab", 0)
                if last_tab < self.notebook.get_n_pages():
                    self.notebook.set_current_page(last_tab)
                    # Find which tab is at this position
                    for tab_name, tab_page in self.tab_pages.items():
                        if tab_page == last_tab:
                            active_tab = tab_name
                            break
            
            # Set visibility status on the active tab
            if active_tab == "Wi-Fi" and active_tab in self.tabs:
                self.tabs[active_tab].tab_visible = True
                
            # Load WiFi networks if WiFi tab is active
            if "Wi-Fi" in self.tabs and active_tab == "Wi-Fi":
                try:
                    self.tabs["Wi-Fi"].load_networks()
                except Exception as e:
                    self.logging.log(LogLevel.Error, f"Error loading WiFi networks: {e}")
            
            # Remove loading tab with proper error handling
            try:
                if self.loading_page < self.notebook.get_n_pages():
                    self.notebook.remove_page(self.loading_page)
            except Exception as e:
                self.logging.log(LogLevel.Error, f"Error removing loading page: {e}")
            
            # Connect page switch signal to handle tab visibility
            self.notebook.connect("switch-page", self.on_tab_switched)
            
            # Store strong references to prevent GC issues
            self._keep_refs = True  # Flag to indicate we're keeping references
            
            self.logging.log(LogLevel.Info, "Tab loading finished successfully")
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Critical error finalizing UI: {e}")
            import traceback
            traceback.print_exc()

        return False  # Required for GLib.idle_add

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
                tab.show_all()  # Ensure tab is visible
                page_num = self.notebook.append_page(
                    tab,
                    self.create_tab_label(tab_name, self.get_icon_for_tab(tab_name)),
                )
                self.tab_pages[tab_name] = page_num
                self.notebook.show_all()  # Ensure notebook updates
            elif not should_show and page_num != -1:
                # Need to remove the tab
                self.notebook.remove_page(page_num)
                # Update page numbers for tabs after this one
                for name, num in self.tab_pages.items():
                    if num > page_num:
                        self.tab_pages[name] = num - 1
                # Remove from tab_pages
                if tab_name in self.tab_pages:
                    del self.tab_pages[tab_name]

    def apply_tab_order(self):
        """Apply tab order settings"""
        # Get current tab order from settings or use default
        tab_order = self.settings.get(
            "tab_order", ["Volume", "Wi-Fi", "Bluetooth", "Battery", "Display", "Power", "Autostart"]
        )
        
        # Make sure all tabs are present in the tab_order
        for tab_name in self.tabs.keys():
            if tab_name not in tab_order:
                # If we're adding Power for the first time, put it before Autostart
                if tab_name == "Power":
                    # Find the position of Autostart
                    if "Autostart" in tab_order:
                        autostart_index = tab_order.index("Autostart")
                        tab_order.insert(autostart_index, tab_name)
                    else:
                        tab_order.append(tab_name)
                # If we're adding Autostart for the first time, put it at the end
                elif tab_name == "Autostart":
                    tab_order.append(tab_name)
                else:
                    tab_order.append(tab_name)
        
        # Update the settings with the modified order
        self.settings["tab_order"] = tab_order
        
        # Log the desired tab order
        self.logging.log(LogLevel.Debug, f"Applying tab order: {tab_order}")
        
        # Clear the tab_pages mapping
        self.tab_pages = {}
        
        # Remove all tabs from the notebook while preserving them
        tab_widgets = {}
        for tab_name, tab in self.tabs.items():
            for i in range(self.notebook.get_n_pages()):
                if self.notebook.get_nth_page(i) == tab:
                    self.notebook.remove_page(i)
                    tab_widgets[tab_name] = tab
                    break
        
        # Re-add tabs in the correct order
        for i, tab_name in enumerate(tab_order):
            if tab_name in self.tabs and tab_name in tab_widgets:
                # Add tab to notebook with proper label
                page_num = self.notebook.append_page(
                    self.tabs[tab_name],
                    self.create_tab_label(tab_name, self.get_icon_for_tab(tab_name))
                )
                self.tab_pages[tab_name] = page_num
                self.logging.log(LogLevel.Debug, f"Tab {tab_name} added at position {page_num}")
        
        # Show all tabs
        self.notebook.show_all()

    def get_icon_for_tab(self, tab_name):
        """Get icon name for a tab"""
        icons = {
            "Volume": "audio-volume-high-symbolic",
            "Wi-Fi": "network-wireless-symbolic",
            "Bluetooth": "bluetooth-symbolic",
            "Battery": "battery-good-symbolic",
            "Display": "video-display-symbolic",
            "Settings": "preferences-system-symbolic",
            "Power": "system-shutdown-symbolic",
            "Autostart": "system-run-symbolic",
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

        self.logging.log(
            LogLevel.Info, "Settings button created and attached to notebook"
        )

    def toggle_settings_panel(self, widget):
        self.logging.log(
            LogLevel.Info, "Settings button clicked, opening settings dialog"
        )

        try:
            dialog = Gtk.Dialog(
                title="Settings",
                parent=self,
                flags=Gtk.DialogFlags.MODAL,
                buttons=(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE),
            )
            dialog.set_default_size(500, 400)
            dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
            # Create a fresh instance of the settings tab to use in the dialog
            settings_tab = SettingsTab(self.logging)
            settings_tab.connect(
                "tab-visibility-changed", self.on_tab_visibility_changed
            )
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
                self.logging.log(LogLevel.Info, "Settings dialog closed")

            # Clean up the dialog
            dialog.destroy()

        except Exception as e:
            self.logging.log(LogLevel.Error, f"Error in toggle_settings_panel: {e}")
            traceback.print_exc()

    def on_tab_visibility_changed(self, widget, tab_name, visible):
        """Handle tab visibility changed signal from settings tab"""
        # Update settings
        if "visibility" not in self.settings:
            self.settings["visibility"] = {}
        self.settings["visibility"][tab_name] = visible
        save_settings(self.settings, self.logging)
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
                tab.show_all()  # Ensure tab is visible

                # First append the tab to the notebook
                page_num = self.notebook.append_page(
                    tab,
                    self.create_tab_label(tab_name, self.get_icon_for_tab(tab_name)),
                )
                self.tab_pages[tab_name] = page_num

                # Then reorder it according to the tab_order setting
                tab_order = self.settings.get(
                    "tab_order", ["Volume", "Wi-Fi", "Bluetooth", "Battery", "Display", "Power", "Autostart"]
                )
                if tab_name in tab_order:
                    # Find the desired position for this tab
                    target_position = 0
                    for t in tab_order:
                        if t == tab_name:
                            break
                        # Only count tabs that are currently visible
                        if t in self.tab_pages:
                            target_position += 1

                    # Reorder the tab to its correct position
                    if target_position != page_num:
                        self.notebook.reorder_child(tab, target_position)

                        # Update page numbers in self.tab_pages
                        for name, num in self.tab_pages.items():
                            if name == tab_name:
                                self.tab_pages[name] = target_position
                            elif num >= target_position and num < page_num:
                                self.tab_pages[name] = num + 1

                self.notebook.show_all()  # Ensure notebook updates
            elif not visible and page_num != -1:
                # Need to remove the tab
                self.notebook.remove_page(page_num)
                # Update page numbers for tabs after this one
                for name, num in self.tab_pages.items():
                    if num > page_num:
                        self.tab_pages[name] = num - 1
                # Remove from tab_pages
                if tab_name in self.tab_pages:
                    del self.tab_pages[tab_name]

    def on_tab_order_changed(self, widget, tab_order):
        """Handle tab order changed signal from settings tab"""
        self.settings["tab_order"] = tab_order
        save_settings(self.settings, self.logging)
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


    def on_tab_switched(self, notebook, page, page_num):
        """Handle tab switching"""
        
        # Update tab visibility status 
        for tab_name, tab in self.tabs.items():
            # Check if this tab is at the current page number
            is_visible = self.tab_pages.get(tab_name) == page_num
            
            # If tab has tab_visible property (WiFi tab), update it
            if hasattr(tab, 'tab_visible'):
                tab.tab_visible = is_visible

        # Save the active tab setting
        self.settings["last_active_tab"] = page_num
        save_settings(self.settings, self.logging)

    def on_notebook_key_press(self, widget, event):
        """Prevent tab selection with Tab key"""
        # Get keyval from event
        keyval = event.keyval
        # Prevent Tab key (65289) and Shift+Tab (65056)
        if keyval in (65289, 65056):
            # Stop propagation of the event
            return True  # Event handled, don't propagate
        return False  # Let other handlers process the event

    def on_key_press(self, widget, event):
        """Prevent tab selection globally"""
        keyval = event.keyval
        state = event.state
        
        if keyval in (65289, 65056):  # Tab and Shift+Tab
            return True  # Stop propagation
        # on shift + s show settings dialog
        if keyval in (115, 83) and state & Gdk.ModifierType.SHIFT_MASK:
            # show settings dialog
            self.toggle_settings_panel(None)
            return True
        #  ctrl + q or q will quit the application
        if keyval in (113, 81) or  (keyval == 113 and state & Gdk.ModifierType.CONTROL_MASK):
            self.logging.log(LogLevel.Info, "Application quitted")
            Gtk.main_quit()
        return False  # Let other handlers process the event

    def on_destroy(self, window):
        """Save settings and quit"""
        self.logging.log(LogLevel.Info, "Application shutting down")
        
        # Stop any ongoing tab creation
        if hasattr(self, 'tabs_thread_running'):
            self.tabs_thread_running = False
        
        # Save the current tab before exiting
        self.settings["last_active_tab"] = self.notebook.get_current_page()

        # Ensure Autostart is in the tab_order setting before saving
        if "tab_order" in self.settings:
            tab_order = self.settings["tab_order"]
            # Make sure all known tabs are included
            all_tabs = ["Volume", "Wi-Fi", "Bluetooth", "Battery", "Display", "Power", "Autostart"]
            for tab_name in all_tabs:
                if tab_name not in tab_order:
                    # If we're adding Autostart for the first time, put it at the end
                    if tab_name == "Autostart":
                        tab_order.append(tab_name)
                    else:
                        tab_order.append(tab_name)
            self.settings["tab_order"] = tab_order

        # Signal all tabs to clean up their resources
        for tab_name, tab in self.tabs.items():
            if hasattr(tab, 'on_destroy'):
                try:
                    tab.on_destroy(None)
                except Exception as e:
                    self.logging.log(LogLevel.Error, f"Error destroying {tab_name} tab: {e}")

        # Stop any monitoring threads
        if hasattr(self, "monitor_pulse_events_running"):
            self.monitor_pulse_events_running = False
        if hasattr(self, "load_networks_thread_running"):
            self.load_networks_thread_running = False

        # Ensure logging is set up
        if not hasattr(self, "logging") or not self.logging:
            self.logging = logging.getLogger("BetterControl")
            handler = logging.StreamHandler(sys.__stdout__)  
            handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s", "%H:%M:%S"))
            self.logging.addHandler(handler)
            self.logging.setLevel(logging.Info)

        # Save settings in a separate thread to avoid blocking
        try:
            save_thread = threading.Thread(target=save_settings, args=(self.settings, self.logging))
            save_thread.daemon = True  # Allow Python to exit without waiting for thread
            save_thread.start()
            # Wait briefly for the thread to complete, but don't block shutdown
            save_thread.join(timeout=0.5)
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Error saving settings: {e}")

        self.logging.log(LogLevel.Info, "Application shutdown complete")

        # Close any file descriptors
        if hasattr(self.logging, "flush"):
            self.logging.flush()

        # Use try/except to avoid errors during shutdown
        try:
            sys.stdout = open('/dev/null', 'w')
            sys.stderr = open('/dev/null', 'w')
        except Exception:
            pass

        # Let GTK know we're quitting
        Gtk.main_quit()
        