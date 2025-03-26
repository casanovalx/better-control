import logging
import subprocess
import gi # type: ignore
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk # type: ignore

class WiFiNetworkRow(Gtk.ListBoxRow):
    def __init__(self, network_info):
        super().__init__()
        self.set_margin_top(5)
        self.set_margin_bottom(5)
        self.set_margin_start(10)
        self.set_margin_end(10)

        # Parse network information
        parts = network_info.split()
        self.is_connected = "*" in parts[0]

        # More reliable SSID extraction
        if len(parts) > 1:
            # Find SSID - sometimes it's after the * mark in different positions
            # For connected networks, using a more reliable method to extract SSID
            if self.is_connected:
                # Try to get the proper SSID from nmcli connection show --active
                try:
                    active_connections = subprocess.getoutput(
                        "nmcli -t -f NAME,DEVICE connection show --active"
                    ).split("\n")
                    for conn in active_connections:
                        if ":" in conn and "wifi" in subprocess.getoutput(
                            f"nmcli -t -f TYPE connection show '{conn.split(':')[0]}'"
                        ):
                            self.ssid = conn.split(":")[0]
                            break
                    else:
                        # Fallback to position-based extraction
                        self.ssid = parts[1]
                except Exception as e:
                    logging.error(f"Error getting active connection name: {e}")
                    self.ssid = parts[1]
            else:
                # For non-connected networks, use the second column
                self.ssid = parts[1]
        else:
            self.ssid = "Unknown"

        # Determine security type more precisely
        if "WPA2" in network_info:
            self.security = "WPA2"
        elif "WPA3" in network_info:
            self.security = "WPA3"
        elif "WPA" in network_info:
            self.security = "WPA"
        elif "WEP" in network_info:
            self.security = "WEP"
        else:
            self.security = "Open"

        # Improved signal strength extraction
        signal_value = 0
        try:
            # Now that we use a consistent format with -f, SIGNAL should be in column 7 (index 6)
            if len(parts) > 6 and parts[6].isdigit():
                signal_value = int(parts[6])
                self.signal_strength = f"{signal_value}%"
            else:
                # Fallback: scan through values for something that looks like signal strength
                for i, p in enumerate(parts):
                    # Look for a number between 0-100 that's likely the signal strength
                    if p.isdigit() and 0 <= int(p) <= 100:
                        # Skip if this is likely to be the channel number (typically at index 4)
                        if i != 4:  # Skip CHAN column
                            signal_value = int(p)
                            self.signal_strength = f"{signal_value}%"
                            break
                else:
                    # No valid signal found
                    self.signal_strength = "0%"
        except (IndexError, ValueError) as e:
            logging.error(f"Error parsing signal strength from {parts}: {e}")
            self.signal_strength = "0%"
            signal_value = 0

        # Determine signal icon based on signal strength percentage
        if signal_value >= 80:
            icon_name = "network-wireless-signal-excellent-symbolic"
        elif signal_value >= 60:
            icon_name = "network-wireless-signal-good-symbolic"
        elif signal_value >= 40:
            icon_name = "network-wireless-signal-ok-symbolic"
        elif signal_value > 0:
            icon_name = "network-wireless-signal-weak-symbolic"
        else:
            icon_name = "network-wireless-signal-none-symbolic"

        # Determine security icon
        if self.security != "Open":
            security_icon = "network-wireless-encrypted-symbolic"
        else:
            security_icon = "network-wireless-symbolic"

        # Main container for the row
        container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.add(container)

        # Network icon
        wifi_icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
        container.pack_start(wifi_icon, False, False, 0)

        # Left side with SSID and security
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)

        ssid_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        ssid_label = Gtk.Label(label=self.ssid)
        ssid_label.set_halign(Gtk.Align.START)
        if self.is_connected:
            ssid_label.set_markup(f"<b>{self.ssid}</b>")
        ssid_box.pack_start(ssid_label, True, True, 0)

        if self.is_connected:
            connected_label = Gtk.Label(label=" (Connected)")
            connected_label.get_style_context().add_class("success-label")
            ssid_box.pack_start(connected_label, False, False, 0)

        left_box.pack_start(ssid_box, False, False, 0)

        details_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        security_image = Gtk.Image.new_from_icon_name(
            security_icon, Gtk.IconSize.SMALL_TOOLBAR
        )
        details_box.pack_start(security_image, False, False, 0)

        security_label = Gtk.Label(label=self.security)
        security_label.set_halign(Gtk.Align.START)
        security_label.get_style_context().add_class("dim-label")
        details_box.pack_start(security_label, False, False, 0)

        left_box.pack_start(details_box, False, False, 0)

        container.pack_start(left_box, True, True, 0)

        # Right side with signal strength
        signal_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        signal_box.set_halign(Gtk.Align.END)

        signal_label = Gtk.Label(label=self.signal_strength)
        signal_box.pack_start(signal_label, False, False, 0)

        container.pack_end(signal_box, False, False, 0)

        # Store original network info for connection handling
        self.original_network_info = network_info

    def get_ssid(self):
        return self.ssid

    def get_security(self):
        return self.security

    def get_original_network_info(self):
        return self.original_network_info

    def is_secured(self):
        return self.security != "Open"
