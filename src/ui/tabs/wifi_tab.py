#!/usr/bin/env python3

import gi # type: ignore
import threading
import logging
import subprocess

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib # type: ignore

from tools.wifi import (
    get_wifi_status,
    set_wifi_power,
    get_wifi_networks,
    connect_network,
    disconnect_network,
    forget_network,
    get_network_speed
)

class WiFiTab(Gtk.Box):
    """WiFi settings tab"""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        logging.info("Initializing WiFi tab")
        self.set_margin_start(15)
        self.set_margin_end(15)
        self.set_margin_top(15)
        self.set_margin_bottom(15)
        self.set_hexpand(True)
        self.set_vexpand(True)

        # Check if WiFi is supported
        result = subprocess.run(["nmcli", "-t", "-f", "DEVICE,TYPE", "device"], capture_output=True, text=True)
        wifi_interfaces = [line for line in result.stdout.split('\n') if "wifi" in line]
        self.wifi_supported = bool(wifi_interfaces)
        
        if not self.wifi_supported:
            logging.warning("WiFi is not supported on this machine")

        # Create header box with title and refresh button
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header_box.set_hexpand(True)

        # Create title box with icon and label
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # Add wifi icon
        wifi_icon = Gtk.Image.new_from_icon_name("network-wireless-symbolic", Gtk.IconSize.DIALOG)
        title_box.pack_start(wifi_icon, False, False, 0)

        # Add title
        wifi_label = Gtk.Label()
        wifi_label.set_markup("<span weight='bold' size='large'>Wi-Fi Networks</span>")
        wifi_label.set_halign(Gtk.Align.START)
        title_box.pack_start(wifi_label, False, False, 0)

        header_box.pack_start(title_box, True, True, 0)

        # Add refresh button
        refresh_button = Gtk.Button()
        refresh_icon = Gtk.Image.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON)
        refresh_button.set_image(refresh_icon)
        refresh_button.set_tooltip_text("Refresh Networks")
        refresh_button.connect("clicked", self.on_refresh_clicked)
        
        # Disable refresh button if WiFi is not supported
        if not self.wifi_supported:
            refresh_button.set_sensitive(False)
            
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

        # WiFi power switch
        power_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        power_label = Gtk.Label(label="Wi-Fi")
        power_label.set_markup("<b>Wi-Fi</b>")
        power_label.set_halign(Gtk.Align.START)
        self.power_switch = Gtk.Switch()
        
        if self.wifi_supported:
            self.power_switch.set_active(get_wifi_status())
            self.power_switch.connect("notify::active", self.on_power_switched)
        else:
            self.power_switch.set_sensitive(False)
            
        power_box.pack_start(power_label, False, True, 0)
        power_box.pack_end(self.power_switch, False, True, 0)
        content_box.pack_start(power_box, False, True, 0)

        # Network speed
        speed_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        speed_box.set_margin_top(10)
        speed_box.set_margin_bottom(5)
        speed_label = Gtk.Label()
        speed_label.set_markup("<b>Connection Speed</b>")
        speed_label.set_halign(Gtk.Align.START)
        speed_box.pack_start(speed_label, True, True, 0)
        content_box.pack_start(speed_box, False, True, 0)
        speed_values_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.upload_label = Gtk.Label(label="Upload: 0 Mbps")
        self.upload_label.set_halign(Gtk.Align.START)
        self.download_label = Gtk.Label(label="Download: 0 Mbps")
        self.download_label.set_halign(Gtk.Align.START)
        speed_values_box.pack_start(self.download_label, False, True, 0)
        speed_values_box.pack_start(self.upload_label, False, True, 0)
        content_box.pack_start(speed_values_box, False, True, 0)

        # Network list section
        networks_label = Gtk.Label()
        networks_label.set_markup("<b>Available Networks</b>")
        networks_label.set_halign(Gtk.Align.START)
        networks_label.set_margin_top(15)
        content_box.pack_start(networks_label, False, True, 0)

        # Network list
        networks_frame = Gtk.Frame()
        networks_frame.set_shadow_type(Gtk.ShadowType.IN)
        self.networks_box = Gtk.ListBox()
        self.networks_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        networks_frame.add(self.networks_box)
        content_box.pack_start(networks_frame, True, True, 0)

        # Action buttons
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        action_box.set_margin_top(10)
        connect_button = Gtk.Button(label="Connect")
        connect_button.connect("clicked", self.on_connect_clicked)
        action_box.pack_start(connect_button, True, True, 0)

        disconnect_button = Gtk.Button(label="Disconnect")
        disconnect_button.connect("clicked", self.on_disconnect_clicked)
        action_box.pack_start(disconnect_button, True, True, 0)

        forget_button = Gtk.Button(label="Forget")
        forget_button.connect("clicked", self.on_forget_clicked)
        action_box.pack_start(forget_button, True, True, 0)

        content_box.pack_start(action_box, False, True, 0)
        scroll_window.add(content_box)
        self.pack_start(scroll_window, True, True, 0)

        # Initial network list population is now deferred
        # self.update_network_list()  <- This line is removed

        # Start network speed updates
        GLib.timeout_add_seconds(1, self.update_network_speed)

        # Previous speed values for calculation
        self.prev_rx_bytes = 0
        self.prev_tx_bytes = 0

    def load_networks(self):
        """Load WiFi networks list - to be called after all tabs are loaded"""
        logging.info("Loading WiFi networks after tabs initialization")
        # Add a loading indicator
        row = Gtk.ListBoxRow()
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)

        spinner = Gtk.Spinner()
        spinner.start()
        box.pack_start(spinner, False, False, 0)

        label = Gtk.Label(label="Loading networks...")
        label.set_halign(Gtk.Align.START)
        box.pack_start(label, True, True, 0)

        row.add(box)
        self.networks_box.add(row)
        self.networks_box.show_all()

        # Start network scan in background thread
        thread = threading.Thread(target=self._load_networks_thread)
        thread.daemon = True
        thread.start()
    def _load_networks_thread(self):
        """Background thread to load WiFi networks"""
        try:
            # Get networks
            networks = get_wifi_networks()
            logging.info(f"Found {len(networks)} WiFi networks")
            # Update UI in main thread
            GLib.idle_add(self._update_networks_in_ui, networks)
        except Exception as e:
            logging.error(f"Error loading WiFi networks: {e}")
            # Show error in UI
            GLib.idle_add(self._show_network_error, str(e))
    def _update_networks_in_ui(self, networks):
        """Update UI with networks (called in main thread)"""
        try:
            # Clear existing networks
            for child in self.networks_box.get_children():
                self.networks_box.remove(child)
            # No networks found case
            if not networks:
                row = Gtk.ListBoxRow()
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                box.set_margin_start(10)
                box.set_margin_end(10)
                box.set_margin_top(10)
                box.set_margin_bottom(10)

                # Check if WiFi is supported by looking at the interfaces
                result = subprocess.run(["nmcli", "-t", "-f", "DEVICE,TYPE", "device"], capture_output=True, text=True)
                wifi_interfaces = [line for line in result.stdout.split('\n') if "wifi" in line]
                if not wifi_interfaces:
                    # WiFi not supported
                    error_icon = Gtk.Image.new_from_icon_name("dialog-error-symbolic", Gtk.IconSize.MENU)
                    box.pack_start(error_icon, False, False, 0)
                    label = Gtk.Label(label="WiFi is not supported on this machine")
                else:
                    label = Gtk.Label(label="No networks found")
                
                label.set_halign(Gtk.Align.START)
                box.pack_start(label, True, True, 0)

                row.add(box)
                self.networks_box.add(row)
                self.networks_box.show_all()
                return False
            # Add networks
            for network in networks:
                row = Gtk.ListBoxRow()
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                box.set_margin_start(10)
                box.set_margin_end(10)
                box.set_margin_top(6)
                box.set_margin_bottom(6)

                # Signal strength indicator icon
                try:
                    signal_strength = int(network["signal"])
                except (ValueError, TypeError):
                    signal_strength = 0  # Default to lowest if conversion fails
                if signal_strength >= 80:
                    icon_name = "network-wireless-signal-excellent-symbolic"
                elif signal_strength >= 60:
                    icon_name = "network-wireless-signal-good-symbolic"
                elif signal_strength >= 40:
                    icon_name = "network-wireless-signal-ok-symbolic"
                elif signal_strength > 0:
                    icon_name = "network-wireless-signal-weak-symbolic"
                else:
                    icon_name = "network-wireless-signal-none-symbolic"
                signal_icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
                box.pack_start(signal_icon, False, False, 0)

                # Network name and details container
                info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
                # Network name
                name_label = Gtk.Label()
                name_label.set_halign(Gtk.Align.START)
                if network["in_use"]:
                    name_label.set_markup(f"<b>{GLib.markup_escape_text(network['ssid'])}</b>")
                else:
                    name_label.set_text(network['ssid'])
                info_box.pack_start(name_label, False, True, 0)

                # Network details (security and signal strength)
                details_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                # Security info
                security_text = network["security"]
                if security_text.lower() == "none":
                    security_text = "Open"
                details_label = Gtk.Label()
                details_label.set_markup(
                    f'<small>{GLib.markup_escape_text(security_text)} • Signal: {signal_strength}%</small>'
                )
                details_label.set_halign(Gtk.Align.START)
                details_box.pack_start(details_label, False, True, 0)
                info_box.pack_start(details_box, False, True, 0)
                box.pack_start(info_box, True, True, 0)

                # Connected indicator (moved before security icon)
                if network["in_use"]:
                    connected_icon = Gtk.Image.new_from_icon_name("emblem-ok-symbolic", Gtk.IconSize.MENU)
                    connected_label = Gtk.Label(label="Connected")
                    connected_label.get_style_context().add_class("dim-label")
                    connected_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                    connected_box.pack_start(connected_icon, False, False, 0)
                    connected_box.pack_start(connected_label, False, False, 0)
                    box.pack_start(connected_box, False, True, 0)

                # Security icon
                if network["security"].lower() != "none":
                    lock_icon = Gtk.Image.new_from_icon_name("system-lock-screen-symbolic", Gtk.IconSize.MENU)
                    box.pack_end(lock_icon, False, False, 0)

                row.add(box)
                self.networks_box.add(row)

            self.networks_box.show_all()
        except Exception as e:
            logging.error(f"Error updating networks in UI: {e}")
            self._show_network_error(str(e))

        return False  # Required for GLib.idle_add

    def _show_network_error(self, error_message):
        """Show an error message in the networks list"""
        # Clear existing networks
        for child in self.networks_box.get_children():
            self.networks_box.remove(child)
        # Add error message
        row = Gtk.ListBoxRow()
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)

        error_icon = Gtk.Image.new_from_icon_name("dialog-error-symbolic", Gtk.IconSize.MENU)
        box.pack_start(error_icon, False, False, 0)

        label = Gtk.Label(label=f"Error loading networks: {error_message}")
        label.set_halign(Gtk.Align.START)
        box.pack_start(label, True, True, 0)

        row.add(box)
        self.networks_box.add(row)
        self.networks_box.show_all()

        return False  # Required for GLib.idle_add

    def update_network_list(self):
        """Update the list of WiFi networks"""
        logging.info("Refreshing WiFi networks list")

        # Clear existing networks
        for child in self.networks_box.get_children():
            self.networks_box.remove(child)

        # Add loading indicator
        row = Gtk.ListBoxRow()
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)

        spinner = Gtk.Spinner()
        spinner.start()
        box.pack_start(spinner, False, False, 0)

        label = Gtk.Label(label="Loading networks...")
        label.set_halign(Gtk.Align.START)
        box.pack_start(label, True, True, 0)

        row.add(box)
        self.networks_box.add(row)
        self.networks_box.show_all()

        # Start network scan in background thread
        thread = threading.Thread(target=self._load_networks_thread)
        thread.daemon = True
        thread.start()

    def update_network_speed(self):
        """Update network speed display"""
        speed = get_network_speed()
        
        # Check if WiFi is supported
        if "wifi_supported" in speed and not speed["wifi_supported"]:
            self.download_label.set_text("Download: N/A")
            self.upload_label.set_text("Upload: N/A")
            return True  # Continue the timer
            
        rx_bytes = speed["rx_bytes"]
        tx_bytes = speed["tx_bytes"]

        if self.prev_rx_bytes > 0 and self.prev_tx_bytes > 0:
            rx_speed = (rx_bytes - self.prev_rx_bytes) / 1024 / 1024  # Convert to Mbps
            tx_speed = (tx_bytes - self.prev_tx_bytes) / 1024 / 1024  # Convert to Mbps
            self.download_label.set_text(f"Download: {rx_speed:.1f} Mbps")
            self.upload_label.set_text(f"Upload: {tx_speed:.1f} Mbps")

        self.prev_rx_bytes = rx_bytes
        self.prev_tx_bytes = tx_bytes

        return True  # Continue the timer

    def on_power_switched(self, switch, gparam):
        """Handle WiFi power switch toggle"""
        state = switch.get_active()
        logging.info(f"Setting WiFi power: {'ON' if state else 'OFF'}")
        # Run power toggle in a background thread to avoid UI freezing
        def power_toggle_thread():
            try:
                set_wifi_power(state)
                if state:
                    # If Wi-Fi was turned on, update networks list
                    GLib.idle_add(self.update_network_list)
            except Exception as e:
                logging.error(f"Error setting WiFi power: {e}")
        # Start thread
        thread = threading.Thread(target=power_toggle_thread)
        thread.daemon = True
        thread.start()

    def on_refresh_clicked(self, button):
        """Handle refresh button click"""
        logging.info("Manual refresh of WiFi networks requested")
        self.update_network_list()

    def on_connect_clicked(self, button):
        """Handle connect button click"""
        row = self.networks_box.get_selected_row()
        if row is None:
            return

        box = row.get_child()
        info_box = box.get_children()[1]
        name_label = info_box.get_children()[0]
        ssid = name_label.get_text()
        # If network name is formatted with markup, strip the markup
        if not ssid:
            ssid = name_label.get_label()
            ssid = ssid.replace("<b>", "").replace("</b>", "")

        logging.info(f"Connecting to WiFi network: {ssid}")

        # Show connecting indicator in list
        for child in self.networks_box.get_children():
            if child == row:
                # Update the selected row to show connecting status
                old_box = child.get_child()
                child.remove(old_box)
                new_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                new_box.set_margin_start(10)
                new_box.set_margin_end(10)
                new_box.set_margin_top(6)
                new_box.set_margin_bottom(6)
                # Add spinner
                spinner = Gtk.Spinner()
                spinner.start()
                new_box.pack_start(spinner, False, False, 0)
                # Add label
                connecting_label = Gtk.Label(label=f"Connecting to {ssid}...")
                connecting_label.set_halign(Gtk.Align.START)
                new_box.pack_start(connecting_label, True, True, 0)

                child.add(new_box)
                child.show_all()
                break

        # Try connecting in background thread
        def connect_thread():
            try:
                # First try to connect without password
                success = connect_network(ssid)
                if success:
                    # Successfully connected
                    GLib.idle_add(self.update_network_list)
                    return
                # If connection failed, show password dialog on main thread
                GLib.idle_add(self._show_password_dialog, ssid)
            except Exception as e:
                logging.error(f"Error connecting to network: {e}")
                GLib.idle_add(self.update_network_list)  # Refresh to clear connecting status
        # Start connection thread
        thread = threading.Thread(target=connect_thread)
        thread.daemon = True
        thread.start()
    def _show_password_dialog(self, ssid):
        """Show password dialog for secured networks"""
        networks = get_wifi_networks()
        network = next((n for n in networks if n["ssid"] == ssid), None)
        if network and network["security"].lower() != "none":
            dialog = Gtk.Dialog(
                title=f"Connect to {ssid}",
                parent=self.get_toplevel(),
                flags=0,
                buttons=(
                    Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                    Gtk.STOCK_OK, Gtk.ResponseType.OK
                )
            )

            box = dialog.get_content_area()
            box.set_spacing(10)
            box.set_margin_start(10)
            box.set_margin_end(10)
            box.set_margin_top(10)
            box.set_margin_bottom(10)

            password_label = Gtk.Label(label="Password:")
            box.add(password_label)

            password_entry = Gtk.Entry()
            password_entry.set_visibility(False)
            password_entry.set_invisible_char("●")
            box.add(password_entry)

            remember_check = Gtk.CheckButton(label="Remember this network")
            remember_check.set_active(True)
            box.add(remember_check)

            dialog.show_all()
            response = dialog.run()

            if response == Gtk.ResponseType.OK:
                password = password_entry.get_text()
                remember = remember_check.get_active()
                dialog.destroy()
                # Connect with password in background thread
                def connect_with_password_thread():
                    try:
                        if connect_network(ssid, password, remember):
                            GLib.idle_add(self.update_network_list)
                        else:
                            # Failed to connect, just refresh UI to clear status
                            GLib.idle_add(self.update_network_list)
                    except Exception as e:
                        logging.error(f"Error connecting to network with password: {e}")
                        GLib.idle_add(self.update_network_list)
                thread = threading.Thread(target=connect_with_password_thread)
                thread.daemon = True
                thread.start()
            else:
                dialog.destroy()
                # User cancelled, refresh UI to clear status
                self.update_network_list()
        else:
            # No security or network not found, just refresh UI
            self.update_network_list()
        return False  # Required for GLib.idle_add

    def on_disconnect_clicked(self, button):
        """Handle disconnect button click"""
        row = self.networks_box.get_selected_row()
        if row is None:
            return

        box = row.get_child()
        info_box = box.get_children()[1]
        name_label = info_box.get_children()[0]
        ssid = name_label.get_text()
        # If network name is formatted with markup, strip the markup
        if not ssid:
            ssid = name_label.get_label()
            ssid = ssid.replace("<b>", "").replace("</b>", "")

        logging.info(f"Disconnecting from WiFi network: {ssid}")

        # Show disconnecting indicator
        for child in self.networks_box.get_children():
            if child == row:
                # Update the selected row to show disconnecting status
                old_box = child.get_child()
                child.remove(old_box)
                new_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                new_box.set_margin_start(10)
                new_box.set_margin_end(10)
                new_box.set_margin_top(6)
                new_box.set_margin_bottom(6)
                # Add spinner
                spinner = Gtk.Spinner()
                spinner.start()
                new_box.pack_start(spinner, False, False, 0)
                # Add label
                disconnecting_label = Gtk.Label(label=f"Disconnecting from {ssid}...")
                disconnecting_label.set_halign(Gtk.Align.START)
                new_box.pack_start(disconnecting_label, True, True, 0)

                child.add(new_box)
                child.show_all()
                break

        # Run disconnect in separate thread
        thread = threading.Thread(target=self._disconnect_thread, args=(ssid,))
        thread.daemon = True
        thread.start()

    def on_forget_clicked(self, button):
        """Handle forget button click"""
        row = self.networks_box.get_selected_row()
        if row is None:
            return

        box = row.get_child()
        info_box = box.get_children()[1]
        name_label = info_box.get_children()[0]
        ssid = name_label.get_text()
        # If network name is formatted with markup, strip the markup
        if not ssid:
            ssid = name_label.get_label()
            ssid = ssid.replace("<b>", "").replace("</b>", "")
        logging.info(f"Forgetting WiFi network: {ssid}")

        dialog = Gtk.MessageDialog(
            transient_for=self.get_toplevel(),
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Forget network {ssid}?"
        )
        dialog.format_secondary_text(
            "This will remove all saved settings for this network."
        )

        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            # Show forgetting indicator
            for child in self.networks_box.get_children():
                if child == row:
                    # Update the selected row to show forgetting status
                    old_box = child.get_child()
                    child.remove(old_box)
                    new_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                    new_box.set_margin_start(10)
                    new_box.set_margin_end(10)
                    new_box.set_margin_top(6)
                    new_box.set_margin_bottom(6)
                    # Add spinner
                    spinner = Gtk.Spinner()
                    spinner.start()
                    new_box.pack_start(spinner, False, False, 0)
                    # Add label
                    forgetting_label = Gtk.Label(label=f"Forgetting {ssid}...")
                    forgetting_label.set_halign(Gtk.Align.START)
                    new_box.pack_start(forgetting_label, True, True, 0)

                    child.add(new_box)
                    child.show_all()
                    break

            # Run forget in background thread
            def forget_thread():
                try:
                    if forget_network(ssid):
                        GLib.idle_add(self.update_network_list)
                    else:
                        # Failed to forget, just refresh UI
                        GLib.idle_add(self.update_network_list)
                except Exception as e:
                    logging.error(f"Error forgetting network: {e}")
                    GLib.idle_add(self.update_network_list)
            thread = threading.Thread(target=forget_thread)
            thread.daemon = True
            thread.start()

    def _disconnect_thread(self, ssid):
        """Thread function to disconnect from a WiFi network"""
        try:
            if disconnect_network(ssid):
                GLib.idle_add(self.update_network_list)
                logging.info(f"Successfully disconnected from {ssid}")
            else:
                logging.error(f"Failed to disconnect from {ssid}")
                GLib.idle_add(self.update_network_list)
        except Exception as e:
            logging.error(f"Error disconnecting from network: {e}")
            GLib.idle_add(self.update_network_list)
