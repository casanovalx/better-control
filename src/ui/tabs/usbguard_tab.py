#!/usr/bin/env python3

import gi
import logging
import subprocess
import threading
from gi.repository import Gtk, GLib  # type: ignore
from utils.translations import get_translations

class USBGuardTab(Gtk.Box):
    def __init__(self, logging, txt):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.logging = logging
        self.txt = txt
        self.previous_devices = None  # Initialize as None to skip first refresh
        self.set_margin_start(10)
        self.set_margin_end(10)
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        
        # Main header container
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        # Top row: Icon, title and refresh button
        top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        usb_icon = Gtk.Image.new_from_icon_name("drive-removable-media-symbolic", Gtk.IconSize.DIALOG)
        ctx = usb_icon.get_style_context()
        ctx.add_class("usb-icon")
        
        def on_enter(widget, event):
            ctx.add_class("usb-icon-animate")
        
        def on_leave(widget, event):
            ctx.remove_class("usb-icon-animate")
        
        icon_event_box = Gtk.EventBox()
        icon_event_box.add(usb_icon)
        icon_event_box.connect("enter-notify-event", on_enter)
        icon_event_box.connect("leave-notify-event", on_leave)
        
        top_row.pack_start(icon_event_box, False, False, 0)

        usb_label = Gtk.Label()
        usb_label.set_markup(f"<span weight='bold' size='large'>USBGuard</span>")
        usb_label.set_halign(Gtk.Align.START)
        top_row.pack_start(usb_label, False, False, 0)
        
        # Status indicator
        self.status_indicator = Gtk.Label()
        self.status_indicator.set_margin_start(10)
        top_row.pack_start(self.status_indicator, False, False, 0)
        
        # Spacer
        top_row.pack_start(Gtk.Box(), True, True, 0)
        
        # Refresh button
        self.refresh_button = Gtk.Button.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON)
        self.refresh_button.set_tooltip_text(get_translations().refresh)
        self.refresh_button.connect("clicked", self.refresh_devices)
        top_row.pack_end(self.refresh_button, False, False, 0)
        
        header_box.pack_start(top_row, False, False, 0)
        
        # Bottom row: Status label and toggle switch with spacing
        bottom_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        bottom_row.set_margin_top(14)  
        bottom_row.set_margin_start(3)  
        bottom_row.set_margin_end(3)  
        
        # Status label aligned left
        status_label = Gtk.Label()
        status_label.set_markup("<b>USBGuard Status</b>")
        status_label.set_halign(Gtk.Align.START)
        status_label.set_margin_start(10)  # Additional left margin
        bottom_row.pack_start(status_label, False, False, 0)
        
        # Spacer to push switch to right
        bottom_row.pack_start(Gtk.Box(), True, True, 0)
        
        # Power switch
        self.power_switch = Gtk.Switch()
        self.power_switch.set_margin_end(10)  # Additional right margin
        self.power_switch.connect("notify::active", self.on_power_switched)
        bottom_row.pack_end(self.power_switch, False, False, 0)
        
        header_box.pack_start(bottom_row, False, False, 0)
        self.pack_start(header_box, False, False, 0)
        
        # Initial service status check
        self.check_service_status()
        
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
            # First check if USBGuard is installed
            try:
                subprocess.run(["which", "usbguard"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError:
                self.status_label.set_markup(
                    "<span foreground='red'>"
                    "USBGuard is not installed. Please install it first."
                    "</span>"
                )
                return
                
            # Then check service status
            self.check_service_status()
            
            if not self.power_switch.get_active():
                self.status_label.set_markup(
                    "<span foreground='orange'>"
                    "USBGuard service is not running. Enable it to manage devices."
                    "</span>"
                )
                return
                
            # Get device list with better error handling
            result = subprocess.run(["usbguard", "list-devices"],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 check=True)
            current_devices = result.stdout.decode('utf-8')
            self.check_device_changes(current_devices)
            self.update_device_list(current_devices)
            self.status_label.set_text("")
            
            # Show loading spinner on refresh button
            if widget:
                spinner = Gtk.Spinner()
                spinner.start()
                widget.set_image(spinner)
                GLib.timeout_add(1000, self.reset_refresh_button, widget)
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
            
            # Create device row with compact layout
            row = Gtk.ListBoxRow()
            row.set_margin_start(5)
            row.set_margin_end(5)
            row.set_margin_top(2)
            row.set_margin_bottom(2)
            
            # Main container box
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            box.set_margin_start(10)
            box.set_margin_end(10)
            box.set_margin_top(5)
            box.set_margin_bottom(5)
            
            # Device icon based on type
            icon_name = {
                "Keyboard": "input-keyboard-symbolic",
                "Mouse": "input-mouse-symbolic",
                "Storage": "drive-harddisk-symbolic",
                "Audio": "audio-headphones-symbolic",
                "Network": "network-wired-symbolic",
                "Printer": "printer-symbolic",
                "Camera": "camera-web-symbolic"
            }.get(product_type, "drive-removable-media-symbolic")
            
            icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DIALOG)
            icon.set_margin_end(10)
            box.pack_start(icon, False, False, 0)
            
            # Device info in vertical box
            info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            
            # Device name and status
            name_label = Gtk.Label()
            name_label.set_markup(f"<b>{vendor_name} {product_type}</b>")
            name_label.set_halign(Gtk.Align.START)
            name_label.set_xalign(0)
            info_box.pack_start(name_label, False, False, 0)
            
            # Status indicator
            status_label = Gtk.Label()
            status_label.set_markup({
                "allow": f"<span foreground='green'>✓ {get_translations().allowed}</span>",
                "block": f"<span foreground='red'>✗ {get_translations().blocked}</span>",
                "reject": f"<span foreground='orange'>⚠ {get_translations().rejected}</span>"
            }.get(status.lower(), status))
            status_label.set_halign(Gtk.Align.START)
            status_label.set_xalign(0)
            info_box.pack_start(status_label, False, False, 0)
            
            box.pack_start(info_box, True, True, 0)
            
            # Action buttons with icons
            btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            
            if status == "block":
                allow_btn = Gtk.Button.new_from_icon_name("emblem-ok-symbolic", Gtk.IconSize.BUTTON)
                allow_btn.set_tooltip_text(get_translations().allow)
                allow_btn.connect("clicked", self.on_allow_device, device_id)
                btn_box.pack_start(allow_btn, False, False, 0)
            else:
                block_btn = Gtk.Button.new_from_icon_name("action-unavailable-symbolic", Gtk.IconSize.BUTTON)
                block_btn.set_tooltip_text(get_translations().block)
                block_btn.connect("clicked", self.on_block_device, device_id)
                btn_box.pack_start(block_btn, False, False, 0)
            
            box.pack_end(btn_box, False, False, 0)
            row.add(box)
            self.device_list.add(row)
        
        self.device_list.show_all()
    
    def on_allow_device(self, widget, device_id):
        try:
            # Temporarily disable notifications
            prev_devices = self.previous_devices
            self.previous_devices = None
            
            subprocess.run(["usbguard", "allow-device", device_id], check=True)
            
            # Show immediate notification
            dialog = Gtk.MessageDialog(
                transient_for=self.get_toplevel(),
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text=self.txt.permission_allowed
            )
            dialog.set_icon_name("drive-removable-media-symbolic")
            dialog.run()
            dialog.destroy()
            
            # Restore device tracking
            self.previous_devices = prev_devices
            
        except subprocess.CalledProcessError as e:
            if hasattr(self.logging, 'log_error'):
                self.logging.log_error(f"Failed to allow device: {e}")
            else:
                print(f"Failed to allow device: {e}")
            self.show_error(get_translations().operation_failed)
    
    def on_block_device(self, widget, device_id):
        try:
            # Temporarily disable notifications
            prev_devices = self.previous_devices
            self.previous_devices = None
            
            subprocess.run(["usbguard", "block-device", device_id], check=True)
            
            # Show immediate notification
            dialog = Gtk.MessageDialog(
                transient_for=self.get_toplevel(),
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text=self.txt.permission_blocked
            )
            dialog.set_icon_name("drive-removable-media-symbolic")
            dialog.run()
            dialog.destroy()
            
            # Restore device tracking
            self.previous_devices = prev_devices
            
        except subprocess.CalledProcessError as e:
            if hasattr(self.logging, 'log_error'):
                self.logging.log_error(f"Failed to block device: {e}")
            else:
                print(f"Failed to block device: {e}")
            self.show_error(get_translations().operation_failed)
        

    def show_policy_dialog(self, widget):
        # Store current selection
        current_selection = self.device_list.get_selected_row()
        
        dialog = Gtk.Dialog(title="USBGuard Policy", 
                        parent=self.get_toplevel(),
                        flags=Gtk.DialogFlags.MODAL)
        dialog.add_button("Close", Gtk.ResponseType.CLOSE)
        
        try:
            # Get policy with timeout
            policy = subprocess.check_output(
                ["usbguard", "list-rules"],
                timeout=5
            ).decode('utf-8').strip()

            # Insert this block to show instructions if no rules exist
            if not policy:
                policy = (
                    "⚠️⚠️ No USBGuard policy rules found ⚠️⚠️.\n\n"
                    "please run this to generate policy rules\n\n"
                    "sudo usbguard generate-policy > rules.conf\n"
                    "sudo cp rules.conf /etc/usbguard/rules.conf\n"
                    "sudo systemctl restart usbguard"

                )

            # Create text view with monospace font
            textview = Gtk.TextView()
            textview.set_editable(False)
            textview.set_cursor_visible(False)
            textview.set_monospace(True)
            textview.get_buffer().set_text(policy)

            # Configure scrolling
            scrolled = Gtk.ScrolledWindow()
            scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scrolled.add(textview)

            # Add to dialog
            content = dialog.get_content_area()
            content.pack_start(scrolled, True, True, 0)
            content.set_margin_start(10)
            content.set_margin_end(10)
            content.set_margin_top(10)
            content.set_margin_bottom(10)

            dialog.set_default_size(600, 400)
            dialog.show_all()

            # Run dialog and restore selection
            dialog.run()
            dialog.destroy()

            if current_selection:
                self.device_list.select_row(current_selection)

        except subprocess.TimeoutExpired:
            self.show_error("Policy retrieval timed out")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
            self.show_error(f"Failed to get policy:\n{error_msg}")
            if hasattr(self.logging, 'log_error'):
                self.logging.log_error(f"Policy error: {error_msg}")


            # Create text view with monospace font
            textview = Gtk.TextView()
            textview.set_editable(False)
            textview.set_cursor_visible(False)
            textview.set_monospace(True)
            textview.get_buffer().set_text(policy)

            # Configure scrolling
            scrolled = Gtk.ScrolledWindow()
            scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scrolled.add(textview)

            # Add to dialog
            content = dialog.get_content_area()
            content.pack_start(scrolled, True, True, 0)
            content.set_margin_start(10)
            content.set_margin_end(10)
            content.set_margin_top(10)
            content.set_margin_bottom(10)

            dialog.set_default_size(600, 400)
            dialog.show_all()

            # Run dialog and restore selection
            dialog.run()
            dialog.destroy()

            if current_selection:
                self.device_list.select_row(current_selection)

        except subprocess.TimeoutExpired:
            self.show_error("Policy retrieval timed out")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
            self.show_error(f"Failed to get policy:\n{error_msg}")
            if hasattr(self.logging, 'log_error'):
                self.logging.log_error(f"Policy error: {error_msg}")


    
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

        
    def check_device_changes(self, current_devices):
        """Check for device changes and trigger notifications"""
        current_set = set(device.strip() for device in current_devices.splitlines() if device.strip())
        
        # Skip first refresh (initial device list)
        if self.previous_devices is None:
            self.previous_devices = current_set
            return
            
        # New devices
        for device in current_set - self.previous_devices:
            try:
                device_name = device.split()[2]
                dialog = Gtk.MessageDialog(
                    transient_for=self.get_toplevel(),
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text=self.txt.usb_connected.format(device=device_name)
                )
                dialog.set_icon_name("drive-removable-media-symbolic")
                dialog.run()
                dialog.destroy()
            except IndexError:
                continue
        
        # Removed devices
        for device in self.previous_devices - current_set:
            try:
                device_name = device.split()[2]
                dialog = Gtk.MessageDialog(
                    transient_for=self.get_toplevel(),
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text=self.txt.usb_disconnected.format(device=device_name)
                )
                dialog.set_icon_name("drive-removable-media-symbolic")
                dialog.run()
                dialog.destroy()
            except IndexError:
                continue
        
        self.previous_devices = current_set

    def check_service_status(self):
        """Check and update USBGuard service status"""
        try:
            output = subprocess.check_output(["systemctl", "is-active", "usbguard"]).decode('utf-8').strip()
            is_active = output == "active"

            # Temporarily block signal so we don’t trigger on_power_switched
            self.power_switch.handler_block_by_func(self.on_power_switched)
            self.power_switch.set_active(is_active)
            self.power_switch.handler_unblock_by_func(self.on_power_switched)

            self.status_indicator.set_markup(
                f"<span foreground='{'green' if is_active else 'red'}'>"
                f"{'● Active' if is_active else '○ Inactive'}"
                f"</span>"
            )
        except subprocess.CalledProcessError:
            self.power_switch.handler_block_by_func(self.on_power_switched)
            self.power_switch.set_active(False)
            self.power_switch.handler_unblock_by_func(self.on_power_switched)

            self.status_indicator.set_markup("<span foreground='red'>○ Service Error</span>")

    def on_power_switched(self, switch, gparam):
        """Handle USBGuard service power switch changes"""
        try:
            if switch.get_active():
                subprocess.run(["pkexec", "systemctl", "start", "usbguard"], check=True)
            else:
                subprocess.run(["pkexec", "systemctl", "stop", "usbguard"], check=True)
            GLib.timeout_add(500, self.check_service_status)
        except subprocess.CalledProcessError as e:
            self.logging.log_error(f"Failed to change USBGuard service state: {e}")
            self.check_service_status()


    def reset_refresh_button(self, button):
        """Reset refresh button after operation"""
        button.set_image(Gtk.Image.new_from_icon_name(
            "view-refresh-symbolic", 
            Gtk.IconSize.BUTTON
        ))
        return False  # Remove timeout

    def on_destroy(self, widget):
        self.refresh_thread_running = False
