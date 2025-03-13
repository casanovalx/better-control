# Copyright (C) 2025 quantumvoid0 (https://github.com/quantumvoid0)
# This program is licensed under the terms of the GNU General Public License v3.
# See LICENSE for the full license text (https://github.com/quantumvoid0/better-control/LICENSE).
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.


import gi
import os
import logging
import shutil
import time
from pydbus import SystemBus
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, GLib, Gdk  
import subprocess
gi.require_version('Pango', '1.0')  # Specify Pango version
from gi.repository import Gtk, Pango

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Ensure it logs INFO level
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("Better Control is running.")



class HyprlandSettingsApp(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Control Center")
        self.set_default_size(1000, 700)
        self.set_resizable(False)

        # Main container
        self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(self.main_container)

        # Notebook for tabs
        notebook = Gtk.Notebook()
        notebook.set_scrollable(True)
        self.main_container.pack_start(notebook, True, True, 0)

        # Wi-Fi Tab
        wifi_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        wifi_box.set_margin_top(10)
        wifi_box.set_margin_bottom(10)
        wifi_box.set_margin_start(10)
        wifi_box.set_margin_end(10)
        wifi_box.set_hexpand(True)
        wifi_box.set_vexpand(True)

        self.wifi_listbox = Gtk.ListBox()
        self.wifi_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        wifi_box.pack_start(self.wifi_listbox, True, True, 0)

        wifi_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        wifi_button_box.set_hexpand(True)
        wifi_button_box.set_vexpand(False)

        refresh_wifi_button = Gtk.Button(label="Refresh")
        refresh_wifi_button.connect("clicked", self.refresh_wifi)
        wifi_button_box.pack_start(refresh_wifi_button, False, False, 0)

        connect_wifi_button = Gtk.Button(label="Connect")
        connect_wifi_button.connect("clicked", self.connect_wifi)
        wifi_button_box.pack_start(connect_wifi_button, False, False, 0)

        forget_wifi_button = Gtk.Button(label="Forget")
        forget_wifi_button.connect("clicked", self.forget_wifi)
        wifi_button_box.pack_start(forget_wifi_button, False, False, 0)

        disconnect_wifi_button = Gtk.Button(label="Disconnect")
        disconnect_wifi_button.connect("clicked", self.disconnect_wifi)
        wifi_button_box.pack_start(disconnect_wifi_button, False, False, 0)

        wifi_box.pack_start(wifi_button_box, False, False, 0)

        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)  
        self.password_entry.set_placeholder_text("Enter Wi-Fi password")
        wifi_box.pack_start(self.password_entry, False, False, 0)

        scrolled_wifi = Gtk.ScrolledWindow()
        scrolled_wifi.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_wifi.add(wifi_box)
        notebook.append_page(scrolled_wifi, Gtk.Label(label="Wi-Fi"))

        # Bluetooth Tab
        bluetooth_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        bluetooth_box.set_margin_top(10)
        bluetooth_box.set_margin_bottom(10)
        bluetooth_box.set_margin_start(10)
        bluetooth_box.set_margin_end(10)
        bluetooth_box.set_hexpand(True)
        bluetooth_box.set_vexpand(True)

        self.bt_listbox = Gtk.ListBox()
        self.bt_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        bluetooth_box.pack_start(self.bt_listbox, True, True, 0)

        bluetooth_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        bluetooth_button_box.set_hexpand(True)
        bluetooth_button_box.set_vexpand(False)

        enable_bt_button = Gtk.Button(label="Enable Bluetooth")
        enable_bt_button.connect("clicked", self.enable_bluetooth)
        bluetooth_button_box.pack_start(enable_bt_button, False, False, 0)

        disable_bt_button = Gtk.Button(label="Disable Bluetooth")
        disable_bt_button.connect("clicked", self.disable_bluetooth)
        bluetooth_button_box.pack_start(disable_bt_button, False, False, 0)

        refresh_bt_button = Gtk.Button(label="Refresh Devices")
        refresh_bt_button.connect("clicked", self.refresh_bluetooth)
        bluetooth_button_box.pack_start(refresh_bt_button, False, False, 0)

        bluetooth_box.pack_start(bluetooth_button_box, False, False, 0)

        scrolled_bt = Gtk.ScrolledWindow()
        scrolled_bt.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_bt.add(bluetooth_box)
        notebook.append_page(scrolled_bt, Gtk.Label(label="Bluetooth"))

        # Volume Tab
        volume_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        volume_box.set_margin_top(10)
        volume_box.set_margin_bottom(10)
        volume_box.set_margin_start(10)
        volume_box.set_margin_end(10)
        volume_box.set_hexpand(True)
        volume_box.set_vexpand(True)

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(True)
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        volume_box.pack_start(grid, True, True, 0)

        mainlabel = Gtk.Label(label="Quick Controls")
        self.apply_css(mainlabel)

        volume_label = Gtk.Label(label="Speaker Volume")
        self.apply_css(volume_label)
        mic_label = Gtk.Label(label="Microphone Volume")  
        self.apply_css(mic_label)
        volume_label.set_xalign(0)
        mic_label.set_xalign(0)
        mainlabel.set_xalign(0)

        refresh_app_volume_button = Gtk.Button(label="Refresh Applications")
        #refresh_app_volume_button.connect("clicked", self.refresh_app_volume)
        volume_box.pack_start(refresh_app_volume_button, False, False, 0)

        GLib.timeout_add_seconds(1, self.refresh_app_volume_realtime) 

        self.volume_button = Gtk.Button(label=f"Mute/Unmute Speaker")
        self.volume_button.connect("clicked", self.mute)
        self.volume_button.set_vexpand(False)  # Prevent vertical expansion
        self.volume_button.set_valign(Gtk.Align.START)  # Align to the top

        self.volume_mic = Gtk.Button(label=f"Mute/Unmute Mic")
        self.volume_mic.connect("clicked", self.micmute)
        self.volume_mic.set_vexpand(False)  # Prevent vertical expansion
        self.volume_mic.set_valign(Gtk.Align.START)  # Align to the top
        # Volume Buttons
        self.volume_zero = Gtk.Button(label="0%")
        self.volume_zero.set_size_request(60, 45)  # Fixed button size
        self.volume_zero.set_vexpand(False)  # Prevent vertical expansion
        self.volume_zero.set_valign(Gtk.Align.START)  # Align to the top
        self.volume_zero.connect("clicked", self.vzero)

        self.volume_tfive = Gtk.Button(label="25%")
        self.volume_tfive.set_size_request(60, 45)  # Fixed button size
        self.volume_tfive.set_vexpand(False)  # Prevent vertical expansion
        self.volume_tfive.set_valign(Gtk.Align.START)  # Align to the top
        self.volume_tfive.connect("clicked", self.vtfive)

        self.volume_fifty = Gtk.Button(label="50%")
        self.volume_fifty.set_size_request(60, 45)  # Fixed button size
        self.volume_fifty.set_vexpand(False)  # Prevent vertical expansion
        self.volume_fifty.set_valign(Gtk.Align.START)  # Align to the top
        self.volume_fifty.connect("clicked", self.vfifty)

        self.volume_sfive = Gtk.Button(label="75%")
        self.volume_sfive.set_size_request(60, 45)  # Fixed button size
        self.volume_sfive.set_vexpand(False)  # Prevent vertical expansion
        self.volume_sfive.set_valign(Gtk.Align.START)  # Align to the top
        self.volume_sfive.connect("clicked", self.vsfive)

        self.volume_hund = Gtk.Button(label="100%")
        self.volume_hund.set_size_request(60, 45)  # Fixed button size
        self.volume_hund.set_vexpand(False)  # Prevent vertical expansion
        self.volume_hund.set_valign(Gtk.Align.START)  # Align to the top
        self.volume_hund.connect("clicked", self.vhund)

        # Microphone Buttons
        self.mic_zero = Gtk.Button(label="0%")
        self.mic_zero.set_size_request(60, 45)  # Fixed button size
        self.mic_zero.set_vexpand(False)  # Prevent vertical expansion
        self.mic_zero.set_valign(Gtk.Align.START)  # Align to the top
        self.mic_zero.connect("clicked", self.mzero)

        self.mic_tfive = Gtk.Button(label="25%")
        self.mic_tfive.set_size_request(60, 45)  # Fixed button size
        self.mic_tfive.set_vexpand(False)  # Prevent vertical expansion
        self.mic_tfive.set_valign(Gtk.Align.START)  # Align to the top
        self.mic_tfive.connect("clicked", self.mtfive)

        self.mic_fifty = Gtk.Button(label="50%")
        self.mic_fifty.set_size_request(60, 45)  # Fixed button size
        self.mic_fifty.set_vexpand(False)  # Prevent vertical expansion
        self.mic_fifty.set_valign(Gtk.Align.START)  # Align to the top
        self.mic_fifty.connect("clicked", self.mfifty)

        self.mic_sfive = Gtk.Button(label="75%")
        self.mic_sfive.set_size_request(60, 45)  # Fixed button size
        self.mic_sfive.set_vexpand(False)  # Prevent vertical expansion
        self.mic_sfive.set_valign(Gtk.Align.START)  # Align to the top
        self.mic_sfive.connect("clicked", self.msfive)

        self.mic_hund = Gtk.Button(label="100%")
        self.mic_hund.set_size_request(60, 45)  # Fixed button size
        self.mic_hund.set_vexpand(False)  # Prevent vertical expansion
        self.mic_hund.set_valign(Gtk.Align.START)  # Align to the top
        self.mic_hund.connect("clicked", self.mhund)

        self.volume_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.volume_scale.set_hexpand(True)  
        self.volume_scale.set_value(self.get_current_volume())
        self.volume_scale.set_value_pos(Gtk.PositionType.LEFT)  
        self.volume_scale.connect("value-changed", self.set_volume)

        self.mic_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.mic_scale.set_hexpand(True)  
        self.mic_scale.set_value_pos(Gtk.PositionType.BOTTOM)  
        self.mic_scale.set_value(self.get_current_mic_volume())
        self.mic_scale.connect("value-changed", self.set_mic_volume)
        self.mic_scale.set_value_pos(Gtk.PositionType.LEFT)

        grid.attach(self.volume_zero, 0, 2, 1, 1)
        grid.attach(self.volume_tfive, 1, 2, 1, 1)        
        grid.attach(self.volume_fifty, 2, 2, 1, 1)
        grid.attach(self.volume_sfive, 3, 2, 1, 1)
        grid.attach(self.volume_hund, 4, 2, 1, 1)

        grid.attach(self.mic_zero, 0, 6, 1, 1)
        grid.attach(self.mic_tfive, 1, 6, 1, 1)        
        grid.attach(self.mic_fifty, 2, 6, 1, 1)
        grid.attach(self.mic_sfive, 3, 6, 1, 1)
        grid.attach(self.mic_hund, 4, 6, 1, 1)

        grid.attach(self.volume_mic, 0, 10, 1, 1)
        grid.attach(self.volume_button, 1, 10, 1, 1)
        grid.attach(volume_label, 0, 1, 5, 1)  
        grid.attach(mic_label, 0, 5, 5, 1)  
        grid.attach(self.volume_scale, 0, 3, 5, 1) 
        grid.attach(self.mic_scale,0,7,5,1)
        grid.attach(mainlabel,0,9,5,1)

        scrolled_volume = Gtk.ScrolledWindow()
        scrolled_volume.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_volume.add(volume_box)
        notebook.append_page(scrolled_volume, Gtk.Label(label="Volume"))

        # Brightness Tab
        brightness_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        brightness_box.set_margin_top(10)
        brightness_box.set_margin_bottom(10)
        brightness_box.set_margin_start(10)
        brightness_box.set_margin_end(10)
        brightness_box.set_hexpand(True)
        brightness_box.set_vexpand(True)

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)  # Make columns evenly spaced
        grid.set_row_homogeneous(False)    # Rows can have different heights
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        brightness_box.pack_start(grid, True, True, 0)

        # Brightness Buttons
        self.brightness_zero = Gtk.Button(label="0%")
        self.brightness_zero.set_size_request(80, 30)
        self.brightness_zero.connect("clicked", self.zero)
        self.brightness_zero.set_vexpand(False)
        self.brightness_zero.set_valign(Gtk.Align.START)

        self.brightness_tfive = Gtk.Button(label="25%")
        self.brightness_tfive.set_size_request(80, 30)
        self.brightness_tfive.connect("clicked", self.tfive)
        self.brightness_tfive.set_vexpand(False)
        self.brightness_tfive.set_valign(Gtk.Align.START)

        self.brightness_fifty = Gtk.Button(label="50%")
        self.brightness_fifty.set_size_request(80, 30)
        self.brightness_fifty.connect("clicked", self.fifty)
        self.brightness_fifty.set_vexpand(False)
        self.brightness_fifty.set_valign(Gtk.Align.START)

        self.brightness_sfive = Gtk.Button(label="75%")
        self.brightness_sfive.set_size_request(80, 30)
        self.brightness_sfive.connect("clicked", self.sfive)
        self.brightness_sfive.set_vexpand(False)
        self.brightness_sfive.set_valign(Gtk.Align.START)

        self.brightness_hund = Gtk.Button(label="100%")
        self.brightness_hund.set_size_request(80, 30)
        self.brightness_hund.connect("clicked", self.hund)
        self.brightness_hund.set_vexpand(False)
        self.brightness_hund.set_valign(Gtk.Align.START)

        # Attach buttons to the grid
        grid.attach(self.brightness_zero, 0, 0, 1, 1)   # Column 0, Row 0
        grid.attach(self.brightness_tfive, 1, 0, 1, 1)  # Column 1, Row 0
        grid.attach(self.brightness_fifty, 2, 0, 1, 1)  # Column 2, Row 0
        grid.attach(self.brightness_sfive, 3, 0, 1, 1)  # Column 3, Row 0
        grid.attach(self.brightness_hund, 4, 0, 1, 1)   # Column 4, Row 0

        # Brightness Slider
        self.brightness_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.brightness_scale.set_hexpand(True)
        self.brightness_scale.set_value(self.get_current_brightness())
        self.brightness_scale.set_value_pos(Gtk.PositionType.BOTTOM)
        self.brightness_scale.connect("value-changed", self.set_brightness)

        # Attach the slider below the buttons
        grid.attach(self.brightness_scale, 0, 1, 5, 1)  # Column 0, Row 1, spans 5 columns

        notebook.append_page(brightness_box, Gtk.Label(label="Brightness"))

        #Application Volume Tab
        app_volume_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        app_volume_box.set_margin_top(10)
        app_volume_box.set_margin_bottom(10)
        app_volume_box.set_margin_start(10)
        app_volume_box.set_margin_end(10)
        app_volume_box.set_hexpand(True)
        app_volume_box.set_vexpand(True)

        self.app_volume_listbox = Gtk.ListBox()
        self.app_volume_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        app_volume_box.pack_start(self.app_volume_listbox, True, True, 0)

        refresh_app_volume_button = Gtk.Button(label="Refresh Applications")
        refresh_app_volume_button.connect("clicked", self.refresh_app_volume)
        app_volume_box.pack_start(refresh_app_volume_button, False, False, 0)

        scrolled_app_volume = Gtk.ScrolledWindow()
        scrolled_app_volume.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_app_volume.add(app_volume_box)
        notebook.append_page(scrolled_app_volume, Gtk.Label(label="Application Volume"))

        self.update_button_labels()

    

    def apply_css(self, widget):
    # Define the CSS style
        css = """
        label {
            font-size: 20px; /* Change this value to your desired font size */
        }
        """

        # Load the CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css.encode())

        # Apply the CSS to the widget
        context = widget.get_style_context()
        context.add_provider(
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def enable_bluetooth(self, button):
        if not shutil.which("bluetoothctl"):
            self.show_error("BlueZ is not installed. Install it with:\n\nsudo pacman -S bluez bluez-utils")
            return  

        print("Enabling Bluetooth...")
        subprocess.run(["systemctl", "start", "bluetooth"])

        for _ in range(5):
            bt_status = subprocess.run(["systemctl", "is-active", "bluetooth"], capture_output=True, text=True).stdout.strip()
            if bt_status == "active":
                print("Bluetooth enabled.")
                return
            subprocess.run(["sleep", "1"])  

        self.show_error("Failed to enable Bluetooth. Make sure BlueZ is installed.")

    def disable_bluetooth(self, button):
        print("Disabling Bluetooth...")
        subprocess.run(["systemctl", "stop", "bluetooth"])
        print("Bluetooth disabled.")


    def refresh_bluetooth(self, button):
        """ Refreshes the list of Bluetooth devices (paired + nearby) """
        self.bt_listbox.foreach(lambda row: self.bt_listbox.remove(row))

        bt_status = subprocess.run(
            ["systemctl", "is-active", "bluetooth"], capture_output=True, text=True
        ).stdout.strip()

        if bt_status != "active":
            self.show_error("Bluetooth is disabled. Enable it first.")
            return

        # Scan for devices
        subprocess.run(["bluetoothctl", "scan", "on"], capture_output=True, text=True)
        time.sleep(5)
        subprocess.run(["bluetoothctl", "scan", "off"], capture_output=True, text=True)

        # Get paired + detected devices
        output = subprocess.run(["bluetoothctl", "devices"], capture_output=True, text=True).stdout.strip()
        devices = output.split("\n")

        if not devices or devices == [""]:
            self.show_error("No Bluetooth devices found.")
            return

        for device in devices:
            parts = device.split(" ")
            if len(parts) < 2:
                continue
            mac_address = parts[1]
            device_name = " ".join(parts[2:]) if len(parts) > 2 else mac_address

            # Try to check if the device is connected
            try:
                status_output = subprocess.getoutput(f"bluetoothctl info {mac_address}")
                is_connected = "Connected: yes" in status_output
            except Exception as e:
                print(f"Error checking status for {mac_address}: {e}")
                is_connected = False  # Default to not connected if check fails

            row = Gtk.ListBoxRow()
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

            label = Gtk.Label(label=device_name, xalign=0)
            box.pack_start(label, True, True, 0)

            if not is_connected:
                connect_button = Gtk.Button(label="Connect")
                connect_button.connect("clicked", self.connect_bluetooth_device, mac_address)
                box.pack_start(connect_button, False, False, 0)

            if is_connected:
                disconnect_button = Gtk.Button(label="Disconnect")
                disconnect_button.connect("clicked", self.disconnect_bluetooth_device, mac_address)
                box.pack_start(disconnect_button, False, False, 0)

            row.add(box)
            self.bt_listbox.add(row)

        self.bt_listbox.show_all()



    def show_error(self, message):
        """ Displays an error message in a popup """
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.run()
        dialog.destroy()

    def connect_bluetooth_device(self, button, mac_address):
        """ Connects to a selected Bluetooth device """
        try:
            subprocess.run(["bluetoothctl", "pair", mac_address], capture_output=True, text=True)
            subprocess.run(["bluetoothctl", "connect", mac_address], capture_output=True, text=True)
            
            # ✅ Refresh the UI after connecting
            self.refresh_bluetooth(None)  
        except Exception as e:
            self.show_error(f"Error connecting to {mac_address}: {e}")


    def disconnect_bluetooth_device(self, button, mac_address):
        """ Disconnects from a selected Bluetooth device """
        try:
            subprocess.run(["bluetoothctl", "disconnect", mac_address], capture_output=True, text=True)
            
            # ✅ Refresh the UI after disconnecting
            self.refresh_bluetooth(None)  
        except Exception as e:
            self.show_error(f"Error disconnecting from {mac_address}: {e}")


    def forget_bluetooth_device(self, button, mac_address):
        """ Removes a Bluetooth device from known devices """
        try:
            subprocess.run(["bluetoothctl", "remove", mac_address], capture_output=True, text=True)
        except Exception as e:
            self.show_error(f"Error forgetting {mac_address}: {e}")

    def mzero(self,button):
        subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", "0%"])
        self.mic_scale.set_value(0)

    def mtfive(self,button):
        subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", "25%"])
        self.mic_scale.set_value(25)

    def mfifty(self,button):
        subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", "50%"])
        self.mic_scale.set_value(50)

    def msfive(self,button):
       subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", "75%"])    
       self.mic_scale.set_value(75)

    def mhund(self,button):
        subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", "100%"])
        self.mic_scale.set_value(100)

    def vzero(self,button):
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "0%"])
        self.volume_scale.set_value(0)

    def vtfive(self,button):
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "25%"])
        self.volume_scale.set_value(25)

    def vfifty(self,button):
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "50%"])
        self.volume_scale.set_value(50)

    def vsfive(self,button):
       subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "75%"])    
       self.volume_scale.set_value(75)

    def vhund(self,button):
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "100%"])
        self.volume_scale.set_value(100)

    def zero(self,button):
        subprocess.run(['brightnessctl', 's', '0'])
        self.brightness_scale.set_value(0)

    def tfive(self,button):
        subprocess.run(['brightnessctl', 's', '25'])
        self.brightness_scale.set_value(25)

    def fifty(self,button):
        subprocess.run(['brightnessctl', 's', '50'])
        self.brightness_scale.set_value(50)

    def sfive(self,button):
        subprocess.run(['brightnessctl', 's', '75'])
        self.brightness_scale.set_value(75)

    def hund(self,button):
        subprocess.run(['brightnessctl', 's', '100'])
        self.brightness_scale.set_value(100)

    def set_mic_volume(self, scale):
        new_volume = int(scale.get_value())
        subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", f"{new_volume}%"])

    def get_current_mic_volume(self):
        try:
            output = subprocess.run(["pactl", "get-source-volume", "@DEFAULT_SOURCE@"], capture_output=True, text=True).stdout
            return int(output.split()[4].replace("%", ""))
        except Exception as e:
            print("Error getting mic volume:", e)
            return 50  

    def refresh_wifi(self, button):
        self.wifi_listbox.foreach(lambda row: self.wifi_listbox.remove(row))
        networks = subprocess.getoutput("nmcli dev wifi").split("\n")[1:]
        for network in networks:
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=network)
            row.add(label)
            label.set_xalign(0)
            self.wifi_listbox.add(row)
        self.wifi_listbox.show_all()

    def connect_wifi(self, button):
        selected_row = self.wifi_listbox.get_selected_row()
        if not selected_row:
            print("No Wi-Fi network selected.")
            return

        ssid = selected_row.get_child().get_text().split()[1]
        print(f"Selected SSID: {ssid}")

        if "secured" in selected_row.get_child().get_text().lower():
            print("Network is secured. Using password from input field...")
            password = self.password_entry.get_text()
            if not password:
                print("No password entered.")
                return

            try:
                result = subprocess.run(
                    ["nmcli", "dev", "wifi", "connect", ssid, "password", password],
                    check=True,
                    capture_output=True,
                    text=True
                )
                print(f"Successfully connected: {result.stdout}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to connect: {e.stderr}")
        else:
            print("Network is unsecured. Attempting to connect...")
            try:
                result = subprocess.run(
                    ["nmcli", "dev", "wifi", "connect", ssid],
                    check=True,
                    capture_output=True,
                    text=True
                )
                print(f"Successfully connected: {result.stdout}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to connect: {e.stderr}")

    def forget_wifi(self, button):
        selected_row = self.wifi_listbox.get_selected_row()
        if not selected_row:
            return
        ssid = selected_row.get_child().get_text().split()[1]
        try:
            connections = subprocess.getoutput(f"nmcli -t -f NAME,UUID connection show | grep '{ssid}'").split("\n")
            if not connections or not connections[0]:  
                dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text=f"No saved connection found for '{ssid}'."
                )
                dialog.run()
                dialog.destroy()
                return
            uuid = connections[0].split(":")[1]
            subprocess.run(["nmcli", "connection", "delete", "uuid", uuid], check=True)
            self.refresh_wifi(None)  
        except subprocess.CalledProcessError as e:
            print(f"Failed to forget network: {e}")

    def disconnect_wifi(self, button):
        try:
            subprocess.run(["nmcli", "dev", "disconnect", "wlo1"], check=True)  
        except subprocess.CalledProcessError as e:
            print(f"Failed to disconnect: {e}")

    def get_current_volume(self):
        output = subprocess.getoutput("pactl get-sink-volume @DEFAULT_SINK@")
        volume = int(output.split("/")[1].strip().strip("%"))
        return volume

    def set_volume(self, scale):
        value = int(scale.get_value())
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{value}%"])

    def get_current_brightness(self):
        output = subprocess.getoutput("brightnessctl get")
        max_brightness = subprocess.getoutput("brightnessctl max")
        return int((int(output) / int(max_brightness)) * 100)

    def set_brightness(self, scale):
        value = int(scale.get_value())
        subprocess.run(["brightnessctl", "set", f"{value}%"])

    def is_muted(self, audio_type="sink"):
        """
        Check if the audio sink or source is currently muted.
        :param audio_type: "sink" for speaker, "source" for microphone
        :return: True if muted, False otherwise
        """
        try:
            if audio_type == "sink":
                output = subprocess.getoutput("pactl get-sink-mute @DEFAULT_SINK@")
            elif audio_type == "source":
                output = subprocess.getoutput("pactl get-source-mute @DEFAULT_SOURCE@")
            else:
                raise ValueError("Invalid audio_type. Use 'sink' or 'source'.")

            return "yes" in output.lower()
        except Exception as e:
            print(f"Error checking mute state: {e}")
            return False

    def update_button_labels(self):
        """
        Update the labels of the mute/unmute buttons based on the current mute state.
        """
        try:

            if self.is_muted("sink"):
                self.volume_button.set_label("Unmute Speaker")
            else:
                self.volume_button.set_label("Mute Speaker")

            if self.is_muted("source"):
                self.volume_mic.set_label("Unmute Mic")
            else:
                self.volume_mic.set_label("Mute Mic")
        except Exception as e:
            print(f"Error updating button labels: {e}")

    def mute(self, button):
        """
        Toggle mute/unmute for the speaker dynamically and update the button label.
        """
        try:
            subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
            print("Speaker mute state toggled.")

            self.update_button_labels()
        except Exception as e:
            print(f"Error toggling speaker mute state: {e}")

    def micmute(self, button):
        """
        Toggle mute/unmute for the microphone dynamically and update the button label.
        """
        try:
            subprocess.run(["pactl", "set-source-mute", "@DEFAULT_SOURCE@", "toggle"])
            print("Microphone mute state toggled.")

            self.update_button_labels()
        except Exception as e:
            print(f"Error toggling microphone mute state: {e}")

    def refresh_app_volume(self, button=None):
        """Refresh the list of applications playing audio and create sliders for them."""
        # Clear the existing list
        self.app_volume_listbox.foreach(lambda row: self.app_volume_listbox.remove(row))

        # Get the list of currently playing audio streams
        try:
            output = subprocess.getoutput("pactl list sink-inputs")
            print("Raw output from pactl list sink-inputs:")  # Debugging
            print(output)  # Debugging

            sink_inputs = output.split("Sink Input #")[1:]  # Split by sink inputs
            print(f"Found {len(sink_inputs)} sink inputs")  # Debugging

            for sink_input in sink_inputs:
                lines = sink_input.split("\n")
                sink_input_id = lines[0].strip()  # Get the sink input ID
                print(f"Processing sink input {sink_input_id}")  # Debugging

                app_name = "Unknown Application"
                media_name = "Unknown Media"
                volume_percent = 50  # Default volume if not found

                # Extract application name, media name, and volume
                for line in lines:
                    if "application.name" in line:
                        app_name = line.split("=")[1].strip().strip('"')
                    if "media.name" in line:
                        media_name = line.split("=")[1].strip().strip('"')
                    if "Volume:" in line:
                        # Extract volume percentage from the line
                        volume_parts = line.split("/")
                        if len(volume_parts) >= 2:
                            volume_percent = int(volume_parts[1].strip().strip("%"))

                print(f"Found application: {app_name} - {media_name} (Volume: {volume_percent}%)")  # Debugging

                # Create a row for each application
                row = Gtk.ListBoxRow()
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                box.set_margin_start(10)
                box.set_margin_end(10)
                box.set_margin_top(5)
                box.set_margin_bottom(5)

                # Create a label for the application and media name
                label = Gtk.Label(label=f"{app_name} - {media_name}")
                label.set_xalign(0)
                box.pack_start(label, True, True, 0)

                # Create a slider for volume control
                scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
                scale.set_hexpand(True)
                scale.set_value(volume_percent)  # Set initial volume
                scale.connect("value-changed", self.set_app_volume, app_name, media_name)  # Pass app_name and media_name
                box.pack_start(scale, True, True, 0)

                row.add(box)
                self.app_volume_listbox.add(row)

            self.app_volume_listbox.show_all()

        except Exception as e:
            print(f"Error refreshing application volume list: {e}")

    def get_app_volume(self, sink_input_id):
        """Get the current volume of an application."""
        try:
            output = subprocess.getoutput(f"pactl get-sink-input-volume {sink_input_id}")
            if "No such entity" in output or "No valid command specified" in output:
                raise ValueError(f"Sink input {sink_input_id} no longer exists or is invalid.")

            # Extract the volume percentage
            volume_parts = output.split("/")
            if len(volume_parts) < 2:  # Ensure the output has the expected format
                raise ValueError(f"Unexpected output format for sink input {sink_input_id}: {output}")

            volume = int(volume_parts[1].strip().strip("%"))
            return volume
        except ValueError as e:
            # Re-raise the exception to skip this sink input
            raise e
        except Exception as e:
            print(f"Error getting volume for sink input {sink_input_id}: {e}")
            return 50  # Default volume

    def set_app_volume(self, scale, app_name, media_name):
        """Set the volume of an application by its name and media name."""
        try:
            new_volume = int(scale.get_value())

            # Refresh the list of sink inputs
            output = subprocess.getoutput("pactl list sink-inputs")
            sink_inputs = output.split("Sink Input #")[1:]  # Split by sink inputs

            for sink_input in sink_inputs:
                lines = sink_input.split("\n")
                sink_input_id = lines[0].strip()  # Get the sink input ID

                # Check if this sink input belongs to the target application and media
                current_app_name = None
                current_media_name = None
                for line in lines:
                    if "application.name" in line:
                        current_app_name = line.split("=")[1].strip().strip('"')
                    if "media.name" in line:
                        current_media_name = line.split("=")[1].strip().strip('"')

                if current_app_name == app_name and current_media_name == media_name:
                    # Set the volume for this sink input
                    result = subprocess.run(
                        ["pactl", "set-sink-input-volume", sink_input_id, f"{new_volume}%"],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode != 0:
                        print(f"Failed to set volume for sink input {sink_input_id}: {result.stderr}")
                    else:
                        print(f"Volume set to {new_volume}% for {app_name} - {media_name} (sink input {sink_input_id})")
                    return  # Exit after setting the volume

            print(f"Failed to find sink input for application: {app_name} - {media_name}")

        except Exception as e:
            print(f"Error setting volume for {app_name} - {media_name}: {e}")

    def refresh_app_volume_realtime(self):
        """Refresh the list of applications playing audio in real-time."""
        try:
            # Get the current list of sink inputs
            output = subprocess.getoutput("pactl list sink-inputs")
            sink_inputs = output.split("Sink Input #")[1:]  # Split by sink inputs

            # Check if the list of sink inputs has changed
            current_sink_inputs = []
            for sink_input in sink_inputs:
                lines = sink_input.split("\n")
                sink_input_id = lines[0].strip()  # Get the sink input ID
                current_sink_inputs.append(sink_input_id)

            # Compare with the previous list of sink inputs
            if hasattr(self, "previous_sink_inputs") and self.previous_sink_inputs == current_sink_inputs:
                return True  # No changes, skip UI update

            # Update the previous list of sink inputs
            self.previous_sink_inputs = current_sink_inputs

            # Refresh the UI
            self.refresh_app_volume(None)

        except Exception as e:
            print(f"Error refreshing application volume list in real-time: {e}")

        return True  # Continue the timeout

if __name__ == "__main__":
    win = HyprlandSettingsApp()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


# Hey there!
# 
# First of all, thank you for checking out this project. I truly hope
# that Better Control is useful to you and that it helps you in your
# work or personal projects. If you have any suggestions,
# issues, or want to collaborate, don't hesitate to reach out.
#
# Stay awesome! - reach out to me on
# "quantumvoid._" <-- discord
# "quantumvoid_" <-- reddit
