#!/usr/bin/env python3

import gi
import logging
import subprocess
import threading
from gi.repository import Gtk, GLib # type: ignore
from utils.translations import get_translations

class USBGuardTab(Gtk.Box):
    def __init__(self, logging, txt):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.logging = logging
        self.txt = txt
        self.set_margin_start(10)
        self.set_margin_end(10)
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        
        # Header with icon and title in one line
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        usb_icon = Gtk.Image.new_from_icon_name("drive-removable-media-symbolic", Gtk.IconSize.DIALOG)
        ctx = usb_icon.get_style_context()
        ctx.add_class("usb-icon")
        
        def on_enter(widget, event):
            ctx.add_class("usb-icon-animate")
        
        def on_leave(widget, event):
            ctx.remove_class("usb-icon-animate")
        
        # Wrap in event box for hover detection
        icon_event_box = Gtk.EventBox()
        icon_event_box.add(usb_icon)
        icon_event_box.connect("enter-notify-event", on_enter)
        icon_event_box.connect("leave-notify-event", on_leave)
        
        header_box.pack_start(icon_event_box, False, False, 0)

        usb_label = Gtk.Label()
        usb_label.set_markup(f"<span weight='bold' size='large'>USBGuard</span>")
        usb_label.set_halign(Gtk.Align.START)
        header_box.pack_start(usb_label, False, False, 0)
        
        self.pack_start(header_box, False, False, 0)
        
        # Status label
        self.status_label = Gtk.Label()
        self.pack_start(self.status_label, False, False, 0)
        
        # Device list
        self.device_list = Gtk.ListBox()
        self.device_list.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.device_list)
        self.pack_start(scrolled, True, True, 0)
        
        # Control buttons
        button_box = Gtk.Box(spacing=10)
        self.refresh_button = Gtk.Button(label=get_translations().refresh)
        self.refresh_button.connect("clicked", self.refresh_devices)
        button_box.pack_start(self.refresh_button, False, False, 0)
        
        self.policy_button = Gtk.Button(label=get_translations().policy)
        self.policy_button.connect("clicked", self.show_policy_dialog)
        button_box.pack_start(self.policy_button, False, False, 0)
        
        self.pack_end(button_box, False, False, 0)
        
        # Initial refresh
        self.refresh_devices(None)
        
        # Auto-refresh thread
        self.refresh_thread_running = True
        threading.Thread(target=self.auto_refresh_devices, daemon=True).start()
    
    def auto_refresh_devices(self):
        while self.refresh_thread_running:
            GLib.idle_add(self.refresh_devices, None)
            threading.Event().wait(5)  # Refresh every 5 seconds
    
    def refresh_devices(self, widget):
        try:
            # Check if USBGuard is running
            output = subprocess.check_output(["systemctl", "is-active", "usbguard"],
                                  stderr=subprocess.PIPE).decode('utf-8')
            
            # Get device list with better error handling
            result = subprocess.run(["usbguard", "list-devices"],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 check=True)
            self.update_device_list(result.stdout.decode('utf-8'))
            self.status_label.set_text("")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8') if e.stderr else "Unknown error"
            
            # Handle specific permission denied error
            if "Operation not permitted" in error_msg:
                error_display = (
                    "<b>USBGuard Permission Required</b>\n\n"
                    "- USBGuard requires your user to have access to it to avoid running Better Control with sudo.\n\n"
                    '- To grant permission, please check this script:\n'
                    '   <a href="https://github.com/quantumvoid0/better-control/blob/main/src/utils/usbguard_permissions.sh">'
                    'https://github.com/qunatumvoid0/better-control/blob/main/src/utils/usbguard_permissions.sh</a>\n\n'
                    "- You can run the script or manually apply the commands. Check the source if you're skeptical - we got nothing to hide."
                )

            else:
                error_display = get_translations().usbguard_error
            
            if hasattr(self.logging, 'log_error'):
                self.logging.log_error(f"USBGuard error: {error_msg}")
            else:
                print(f"USBGuard error: {error_msg}")
            self.show_error(error_display)
        except FileNotFoundError:
            if hasattr(self.logging, 'log_error'):
                self.logging.log_error("USBGuard not installed")
            else:
                print("USBGuard not installed")
            self.show_error(get_translations().usbguard_not_installed)

    # Common vendor and product mappings
    VENDOR_MAP = {
        "0x8086": "Intel",
        "0x8087": "Intel",
        "0x045e": "Microsoft",
        "0x046d": "Logitech",
        "0x04f2": "Chicony",
        "0x05ac": "Apple",
        "0x093a": "Pixart",
        "0x0b05": "ASUS",
        "0x0cf3": "Qualcomm",
        "0x1532": "Razer",
        "0x2109": "VIA Labs"
    }

    PRODUCT_TYPE_MAP = {
        "0x0001": "Keyboard",
        "0x0002": "Mouse",
        "0x0003": "Combo Keyboard/Mouse",
        "0x0004": "Game Controller",
        "0x0005": "Pen Tablet",
        "0x0006": "Scanner",
        "0x0007": "Camera",
        "0x0008": "Printer",
        "0x0009": "Storage",
        "0x000a": "Audio",
        "0x000b": "Network"
    }

    def update_device_list(self, devices_str):
        # Clear existing devices
        for child in self.device_list.get_children():
            self.device_list.remove(child)
        
        if not devices_str.strip():
            self.show_error(get_translations().no_devices)
            return
        
        # Add new devices
        for line in devices_str.splitlines():
            if not line.strip():
                continue
                
            parts = line.split()
            if len(parts) < 3:
                continue
                
            device_id = parts[0].split(":")[0]
            status = parts[1]
            device_info = " ".join(parts[2:])
            
            # Parse device info for better display
            try:
                # Extract vendor and product IDs if available
                vendor_id = "Unknown"
                product_id = "Unknown"
                if "idVendor=" in device_info and "idProduct=" in device_info:
                    vendor_id = device_info.split("idVendor=")[1].split()[0]
                    product_id = device_info.split("idProduct=")[1].split()[0]
                    
                # Get human-readable names (default to raw IDs if not available)
                vendor_name = self.VENDOR_MAP.get(vendor_id.lower(), vendor_id)
                product_type = self.PRODUCT_TYPE_MAP.get(product_id[:6].lower(), "USB Device") if product_id != "Unknown" else "USB Device"
                
                # Get human-readable status and some visul enhancements
                status_text = {
                    "allow": "✅ Allowed",
                    "block": "❌ Blocked",
                    "reject": "🚫 Rejected"
                }.get(status.lower(), f"({status})")
                
                # Create formatted display text
                display_text = f"""
<b>{product_type}</b>
ID: {device_id}
Status: {status_text}
Manufacturer: {vendor_name}
Type: {product_type}
"""
                if "serial=" in device_info:
                    serial = device_info.split("serial=")[1].split()[0]
                    display_text += f"Serial: {serial}\n"
                
                # Add any additional info with proper line wrapping
                display_text += f"\n<small>{device_info.replace(' ', '&#160;')}</small>"
                
            except Exception as e:
                display_text = f"{device_info} ({status})"
                if hasattr(self.logging, 'log_error'):
                    self.logging.log_error(f"Failed to parse device info: {e}")
            
            row = Gtk.ListBoxRow()
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            box.set_margin_start(10)
            box.set_margin_end(10)
            box.set_margin_top(5)
            box.set_margin_bottom(5)
            
            # Device info with proper wrapping
            info_label = Gtk.Label()
            info_label.set_markup(display_text.strip())
            info_label.set_halign(Gtk.Align.START)
            info_label.set_hexpand(True)
            info_label.set_use_markup(True)
            info_label.set_line_wrap(True)
            info_label.set_max_width_chars(60)  # Limit line length
            box.pack_start(info_label, True, True, 0)
            
            # Action buttons
            if status == "block":
                allow_btn = Gtk.Button(label=get_translations().allow)
                allow_btn.connect("clicked", self.on_allow_device, device_id)
                box.pack_start(allow_btn, False, False, 0)
            else:
                block_btn = Gtk.Button(label=get_translations().block)
                block_btn.connect("clicked", self.on_block_device, device_id)
                box.pack_start(block_btn, False, False, 0)
            
            row.add(box)
            self.device_list.add(row)
        
        self.device_list.show_all()
    
    def on_allow_device(self, widget, device_id):
        try:
            subprocess.run(["usbguard", "allow-device", device_id], check=True)
            self.refresh_devices(None)
        except subprocess.CalledProcessError as e:
            if hasattr(self.logging, 'log_error'):
                self.logging.log_error(f"Failed to allow device: {e}")
            else:
                print(f"Failed to allow device: {e}")
            self.show_error(get_translations().operation_failed)
    
    def on_block_device(self, widget, device_id):
        try:
            subprocess.run(["usbguard", "block-device", device_id], check=True)
            self.refresh_devices(None)
        except subprocess.CalledProcessError as e:
            if hasattr(self.logging, 'log_error'):
                self.logging.log_error(f"Failed to block device: {e}")
            else:
                print(f"Failed to block device: {e}")
            self.show_error(get_translations().operation_failed)
    
    def show_policy_dialog(self, widget):
        dialog = Gtk.Dialog(title="USBGuard Policy", 
                          parent=self.get_toplevel(),
                          flags=Gtk.DialogFlags.MODAL)
        dialog.add_button("Close", Gtk.ResponseType.CLOSE)
        
        try:
            policy = subprocess.check_output(["usbguard", "list-rules"]).decode('utf-8')
            textview = Gtk.TextView()
            textview.set_editable(False)
            textview.set_cursor_visible(False)
            textview.get_buffer().set_text(policy)
            
            scrolled = Gtk.ScrolledWindow()
            scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scrolled.add(textview)
            
            dialog.get_content_area().pack_start(scrolled, True, True, 0)
            dialog.set_default_size(600, 400)
            dialog.show_all()
            dialog.run()
            dialog.destroy()
        except subprocess.CalledProcessError as e:
            if hasattr(self.logging, 'log_error'):
                self.logging.log_error(f"Failed to get policy: {e}")
            else:
                print(f"Failed to get policy: {e}")
            self.show_error(get_translations().policy_error)
    
    def show_error(self, message):
        for child in self.device_list.get_children():
            self.device_list.remove(child)

        label = Gtk.Label()
        label.set_markup(message)
        label.set_line_wrap(True)
        label.set_selectable(True)
        label.set_use_markup(True)
        label.set_halign(Gtk.Align.START)
        label.set_valign(Gtk.Align.START)
        label.set_xalign(0)
        label.set_yalign(0)
        label.set_margin_top(10)
        label.set_margin_bottom(10)
        label.set_margin_start(10)
        label.set_margin_end(10)
        label.set_max_width_chars(80)
        label.set_track_visited_links(True)

        self.device_list.add(label)
        self.device_list.show_all()

        
    def on_destroy(self, widget):
        self.refresh_thread_running = False
