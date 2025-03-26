#!/usr/bin/env python3

import gi # type: ignore
import subprocess

from utils.logger import LogLevel, Logger

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib # type: ignore

from tools.volume import (
    get_volume,
    set_volume,
    get_mute_state,
    toggle_mute,
    get_sinks,
    get_sources,
    get_applications,
    set_application_volume,
    set_default_sink,
    set_default_source,
    get_mic_volume,
    set_mic_volume,
    get_mic_mute_state,
    toggle_mic_mute,
)

class VolumeTab(Gtk.Box):
    """Volume settings tab"""

    def __init__(self, logging: Logger):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.logging = logging
        self.set_margin_start(15)
        self.set_margin_end(15)
        self.set_margin_top(15)
        self.set_margin_bottom(15)
        self.set_hexpand(True)
        self.set_vexpand(True)

        # Create header box with title and refresh button
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header_box.set_hexpand(True)

        # Create title box with icon and label
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # Add volume icon
        volume_icon = Gtk.Image.new_from_icon_name("audio-volume-high-symbolic", Gtk.IconSize.DIALOG)
        title_box.pack_start(volume_icon, False, False, 0)

        # Add title
        volume_label = Gtk.Label()
        volume_label.set_markup("<span weight='bold' size='large'>Audio Settings</span>")
        volume_label.set_halign(Gtk.Align.START)
        title_box.pack_start(volume_label, False, False, 0)

        header_box.pack_start(title_box, True, True, 0)

        # Add refresh button
        refresh_button = Gtk.Button()
        refresh_icon = Gtk.Image.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON)
        refresh_button.set_image(refresh_icon)
        refresh_button.set_tooltip_text("Refresh Audio Devices")
        refresh_button.connect("clicked", self.on_refresh_clicked)
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

        # Output device selection
        output_section_label = Gtk.Label()
        output_section_label.set_markup("<b>Output Device</b>")
        output_section_label.set_halign(Gtk.Align.START)
        content_box.pack_start(output_section_label, False, True, 0)

        output_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        output_box.set_margin_top(5)
        output_label = Gtk.Label(label="Device:")
        self.output_combo = Gtk.ComboBoxText()
        self.output_combo.connect("changed", self.on_output_changed)
        output_box.pack_start(output_label, False, True, 0)
        output_box.pack_start(self.output_combo, True, True, 0)
        content_box.pack_start(output_box, False, True, 0)

        # Volume control
        volume_frame = Gtk.Frame()
        volume_frame.set_shadow_type(Gtk.ShadowType.IN)
        volume_frame.set_margin_top(10)
        volume_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        volume_box.set_margin_start(10)
        volume_box.set_margin_end(10)
        volume_box.set_margin_top(10)
        volume_box.set_margin_bottom(10)

        # Volume title
        volume_title = Gtk.Label()
        volume_title.set_markup("<b>Speaker Volume</b>")
        volume_title.set_halign(Gtk.Align.START)
        volume_box.pack_start(volume_title, False, True, 0)

        # Volume slider
        self.volume_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0, 100, 1
        )
        self.volume_scale.set_value(get_volume(self.logging))
        self.volume_scale.connect("value-changed", self.on_volume_changed)
        volume_box.pack_start(self.volume_scale, True, True, 0)

        # Mute button
        self.mute_button = Gtk.Button()
        self.mute_button.connect("clicked", self.on_mute_clicked)
        volume_box.pack_start(self.mute_button, False, True, 0)

        # Quick volume buttons
        quick_volume_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        volumes = [0, 25, 50, 75, 100]
        for vol in volumes:
            button = Gtk.Button(label=f"{vol}%")
            button.connect("clicked", self.on_quick_volume_clicked, vol)
            quick_volume_box.pack_start(button, True, True, 0)
        volume_box.pack_start(quick_volume_box, False, True, 0)

        volume_frame.add(volume_box)
        content_box.pack_start(volume_frame, False, True, 0)

        # Input device selection
        input_section_label = Gtk.Label()
        input_section_label.set_markup("<b>Input Device</b>")
        input_section_label.set_halign(Gtk.Align.START)
        input_section_label.set_margin_top(15)
        content_box.pack_start(input_section_label, False, True, 0)

        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        input_box.set_margin_top(5)
        input_label = Gtk.Label(label="Device:")
        self.input_combo = Gtk.ComboBoxText()
        self.input_combo.connect("changed", self.on_input_changed)
        input_box.pack_start(input_label, False, True, 0)
        input_box.pack_start(self.input_combo, True, True, 0)
        content_box.pack_start(input_box, False, True, 0)

        # Microphone control
        mic_frame = Gtk.Frame()
        mic_frame.set_shadow_type(Gtk.ShadowType.IN)
        mic_frame.set_margin_top(10)
        mic_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        mic_box.set_margin_start(10)
        mic_box.set_margin_end(10)
        mic_box.set_margin_top(10)
        mic_box.set_margin_bottom(10)

        # Mic title
        mic_title = Gtk.Label()
        mic_title.set_markup("<b>Microphone Volume</b>")
        mic_title.set_halign(Gtk.Align.START)
        mic_box.pack_start(mic_title, False, True, 0)

        # Mic slider
        self.mic_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0, 100, 1
        )
        self.mic_scale.set_value(get_mic_volume(self.logging))
        self.mic_scale.connect("value-changed", self.on_mic_volume_changed)
        mic_box.pack_start(self.mic_scale, True, True, 0)

        # Mic mute button
        self.mic_mute_button = Gtk.Button()
        self.mic_mute_button.connect("clicked", self.on_mic_mute_clicked)
        mic_box.pack_start(self.mic_mute_button, False, True, 0)

        # Quick mic volume buttons
        quick_mic_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        for vol in volumes:
            button = Gtk.Button(label=f"{vol}%")
            button.connect("clicked", self.on_quick_mic_volume_clicked, vol)
            quick_mic_box.pack_start(button, True, True, 0)
        mic_box.pack_start(quick_mic_box, False, True, 0)

        mic_frame.add(mic_box)
        content_box.pack_start(mic_frame, False, True, 0)

        # Application volumes
        app_label = Gtk.Label()
        app_label.set_markup("<b>Application Volumes</b>")
        app_label.set_halign(Gtk.Align.START)
        app_label.set_margin_top(15)
        content_box.pack_start(app_label, False, True, 0)

        app_frame = Gtk.Frame()
        app_frame.set_shadow_type(Gtk.ShadowType.IN)
        app_frame.set_margin_top(5)
        self.app_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.app_box.set_margin_start(10)
        self.app_box.set_margin_end(10)
        self.app_box.set_margin_top(10)
        self.app_box.set_margin_bottom(10)
        app_frame.add(self.app_box)
        content_box.pack_start(app_frame, True, True, 0)

        scroll_window.add(content_box)
        self.pack_start(scroll_window, True, True, 0)

        # Initialize UI state
        self.update_device_lists()
        self.update_mute_buttons()
        self.update_application_list()

    def update_device_lists(self):
        """Update output and input device lists and sync dropdown with the actual default sink."""
        try:
            self.logging.log(LogLevel.Info, "Updating audio device lists...")

            # Get the currently active sink
            current_sink = subprocess.getoutput("pactl get-default-sink").strip()
            self.logging.log(LogLevel.Info, f"Current active output sink: {current_sink}")

            # Output devices (speakers/headphones)
            self.output_combo.remove_all()
            sinks = get_sinks(self.logging)

            if not sinks:
                self.logging.log(LogLevel.Warn, "No output sinks found!")
                self.output_combo.append("no-sink", "No Output Devices Found")
                self.output_combo.set_active(0)
            else:
                active_index = -1
                for i, sink in enumerate(sinks):
                    self.logging.log(LogLevel.Info, f"Adding output sink: {sink['name']} ({sink['description']})")
                    self.output_combo.append(sink["name"], sink["description"])
                    if sink["name"] == current_sink:
                        active_index = i

                if active_index != -1:
                    self.output_combo.set_active(active_index)
                else:
                    self.output_combo.set_active(0)  # Default to first item

            # Get the currently active input source (microphone)
            current_source = subprocess.getoutput("pactl get-default-source").strip()
            self.logging.log(LogLevel.Info, f"Current active input source: {current_source}")

            # Input devices (microphones)
            self.input_combo.remove_all()
            sources = get_sources(self.logging)

            if not sources:
                self.logging.log(LogLevel.Warn, "No input sources found!")
                self.input_combo.append("no-source", "No Input Devices Found")
                self.input_combo.set_active(0)
            else:
                active_index = -1
                for i, source in enumerate(sources):
                    if "monitor" not in source["name"].lower():  # Skip monitor sources
                        self.logging.log(LogLevel.Info, f"Adding input source: {source['name']} ({source['description']})")
                        self.input_combo.append(source["name"], source["description"])
                        if source["name"] == current_source:
                            active_index = i

                if active_index != -1:
                    self.input_combo.set_active(active_index)
                else:
                    self.input_combo.set_active(0)  # Default to first item

        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed updating device lists: {e}")


    def update_mute_buttons(self):
        """Update mute button labels"""
        speaker_muted = get_mute_state(self.logging)
        self.mute_button.set_label("Unmute" if speaker_muted else "Mute")

        mic_muted = get_mic_mute_state(self.logging)
        self.mic_mute_button.set_label("Unmute Mic" if mic_muted else "Mute Mic")

    def update_application_list(self):
        """Update application volume controls"""
        # Remove existing controls
        for child in self.app_box.get_children():
            self.app_box.remove(child)

        # Add controls for each application
        apps = get_applications(self.logging)
        if not apps:
            # Show "No applications playing audio" message
            no_apps_label = Gtk.Label()
            no_apps_label.set_markup("<i>No applications playing audio</i>")
            no_apps_label.set_halign(Gtk.Align.START)
            no_apps_label.set_margin_top(5)
            no_apps_label.set_margin_bottom(5)
            self.app_box.pack_start(no_apps_label, False, True, 0)
        else:
            for app in apps:
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                box.set_margin_bottom(5)

                # App icon
                icon_name = app.get("icon", "audio-x-generic-symbolic")
                icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
                box.pack_start(icon, False, False, 0)

                # App name
                name_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
                name_label = Gtk.Label(label=app["name"])
                name_label.set_halign(Gtk.Align.START)
                name_box.pack_start(name_label, False, True, 0)

                box.pack_start(name_box, True, True, 0)

                # Volume slider
                scale = Gtk.Scale.new_with_range(
                    Gtk.Orientation.HORIZONTAL, 0, 100, 1
                )
                scale.set_size_request(150, -1)  # Set minimum width
                scale.set_value(app["volume"])
                scale.connect("value-changed", self.on_app_volume_changed, app["id"])
                box.pack_start(scale, False, True, 0)

                self.app_box.pack_start(box, False, True, 0)

        self.app_box.show_all()

    def update_volumes(self):
        """Update volume displays"""
        try:
            # Update main volume
            self.volume_scale.set_value(get_volume(self.logging))

            # Update mic volume
            self.mic_scale.set_value(get_mic_volume(self.logging))

            # Update mute buttons
            self.update_mute_buttons()

            # Update application list
            self.update_application_list()

        except Exception as e:
            self.logging.log(LogLevel.Error, f"Error updating volumes: {e}")

    def on_volume_changed(self, scale):
        """Handle volume scale changes"""
        value = int(scale.get_value())
        set_volume(value, self.logging)

    def on_mute_clicked(self, button):
        """Handle mute button clicks"""
        toggle_mute(self.logging)
        self.update_mute_buttons()

    def on_quick_volume_clicked(self, volume):
        """Handle quick volume button clicks"""
        set_volume(volume, self.logging)
        self.volume_scale.set_value(volume)

    def on_mic_volume_changed(self, scale):
        """Handle microphone volume scale changes"""
        value = int(scale.get_value())
        set_mic_volume(value, self.logging)

    def on_mic_mute_clicked(self):
        """Handle microphone mute button clicks"""
        toggle_mic_mute(self.logging)
        self.update_mute_buttons()

    def on_quick_mic_volume_clicked(self, button, volume):
        """Handle quick microphone volume button clicks"""
        set_mic_volume(volume, self.logging)
        self.mic_scale.set_value(volume)

    def on_output_changed(self, combo):
        """Handle output device selection changes"""
        device_id = combo.get_active_id()
        if device_id:
            set_default_sink(device_id, self.logging)

    def on_input_changed(self, combo):
        """Handle input device selection changes"""
        device_id = combo.get_active_id()
        if device_id:
            set_default_source(device_id, self.logging)

    def on_app_volume_changed(self, scale, app_id):
        """Handle application volume changes"""
        value = int(scale.get_value())
        set_application_volume(app_id, value, self.logging)

    def on_refresh_clicked(self):
        """Handle refresh button click"""
        self.logging.log(LogLevel.Info, "Manual refresh of audio devices requested")
        self.update_device_lists()
        self.update_application_list()
        self.update_mute_buttons()
        self.update_volumes()

    def on_auto_refresh(self):
        """Automatically refresh audio device lists and UI every 3 seconds."""
        self.logging.log(LogLevel.Info, "Auto-refreshing audio settings...")
        self.update_device_lists()
        self.update_application_list()
        self.update_mute_buttons()
        self.update_volumes()

        GLib.timeout_add(3000, self.on_auto_refresh)