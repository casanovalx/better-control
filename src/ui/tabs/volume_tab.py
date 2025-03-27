#!/usr/bin/env python3

import gi  # type: ignore
import subprocess
import threading
import time

from utils.logger import LogLevel, Logger

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib  # type: ignore

from tools.volume import (
    get_volume,
    set_volume,
    get_mute_state,
    toggle_mute,
    get_sinks,
    get_sources,
    get_applications,
    set_application_volume,
    move_application_to_sink,
    set_default_sink,
    set_default_source,
    get_mic_volume,
    set_mic_volume,
    get_mic_mute_state,
    toggle_mic_mute,
    get_sink_name_by_id,
    get_application_mute_state,
    toggle_application_mute,
    get_source_outputs,
    get_application_mic_mute_state,
    toggle_application_mic_mute,
    get_application_mic_volume,
    set_application_mic_volume,
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

        self.is_visible = False  # Track tab visibility

        # Get the default icon theme
        self.icon_theme = Gtk.IconTheme.get_default()

        # Create header box with title and refresh button
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header_box.set_hexpand(True)

        # Create title box with icon and label
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # Add volume icon
        volume_icon = Gtk.Image.new_from_icon_name(
            "audio-volume-high-symbolic", Gtk.IconSize.DIALOG
        )
        title_box.pack_start(volume_icon, False, False, 0)

        # Add title
        volume_label = Gtk.Label()
        volume_label.set_markup(
            "<span weight='bold' size='large'>Audio Settings</span>"
        )
        volume_label.set_halign(Gtk.Align.START)
        title_box.pack_start(volume_label, False, False, 0)

        header_box.pack_start(title_box, True, True, 0)

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

        # Volume control (slider + mute button) in horizontal box
        volume_control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        # Volume slider
        self.volume_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0, 100, 1
        )
        self.volume_scale.set_value(get_volume(self.logging))
        self.volume_scale.connect("value-changed", self.on_volume_changed)
        # Improve slider responsiveness
        self.volume_scale.set_draw_value(True)
        self.volume_scale.set_value_pos(Gtk.PositionType.RIGHT)
        self.volume_scale.set_increments(1, 5)  # Small step, page increment
        volume_control_box.pack_start(self.volume_scale, True, True, 0)

        # Mute button
        self.mute_button = Gtk.Button()
        self.update_mute_button()
        self.mute_button.connect("clicked", self.on_mute_clicked)
        volume_control_box.pack_start(self.mute_button, False, False, 0)

        volume_box.pack_start(volume_control_box, True, True, 0)

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

        # Mic control (slider + mute button) in horizontal box
        mic_control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        # Mic slider
        self.mic_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.mic_scale.set_value(get_mic_volume(self.logging))
        self.mic_scale.connect("value-changed", self.on_mic_volume_changed)
        # Improve slider responsiveness
        self.mic_scale.set_draw_value(True)
        self.mic_scale.set_value_pos(Gtk.PositionType.RIGHT)
        self.mic_scale.set_increments(1, 5)  # Small step, page increment
        mic_control_box.pack_start(self.mic_scale, True, True, 0)

        # Mic mute button
        self.mic_mute_button = Gtk.Button()
        self.update_mic_mute_button()
        self.mic_mute_button.connect("clicked", self.on_mic_mute_clicked)
        mic_control_box.pack_start(self.mic_mute_button, False, False, 0)

        mic_box.pack_start(mic_control_box, True, True, 0)

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
        app_label.set_markup("<b>Applications Output Volume</b>")
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

        # Applications using microphone
        mic_app_label = Gtk.Label()
        mic_app_label.set_markup("<b>Applications Input Volume</b>")
        mic_app_label.set_halign(Gtk.Align.START)
        mic_app_label.set_margin_top(15)
        content_box.pack_start(mic_app_label, False, True, 0)

        mic_app_frame = Gtk.Frame()
        mic_app_frame.set_shadow_type(Gtk.ShadowType.IN)
        mic_app_frame.set_margin_top(5)
        self.mic_app_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.mic_app_box.set_margin_start(10)
        self.mic_app_box.set_margin_end(10)
        self.mic_app_box.set_margin_top(10)
        self.mic_app_box.set_margin_bottom(10)
        mic_app_frame.add(self.mic_app_box)
        content_box.pack_start(mic_app_frame, True, True, 0)

        scroll_window.add(content_box)
        self.pack_start(scroll_window, True, True, 0)

        # Initialize UI state
        self.update_device_lists()
        self.update_mute_buttons()
        self.update_application_list()
        self.update_mic_application_list()

        # Initialize pulse audio monitoring variables
        self.pulse_thread = None
        self.should_monitor = False  # Don't start monitoring until tab is visible

        # Start with initial data refresh
        self.update_volumes()

        # Always start monitoring on initialization to ensure the app works
        # even if map signal doesn't fire correctly
        self.should_monitor = True
        self.start_pulse_monitoring()

        # Connect map/unmap signals for smart monitoring when tab becomes visible/hidden
        self.connect("map", self.on_tab_shown)
        self.connect("unmap", self.on_tab_hidden)

        # Connect destroy signal for proper cleanup
        self.connect_destroy_signal()

    def on_tab_shown(self, widget):
        """Called when the tab becomes visible"""
        self.is_visible = True
        self.update_volumes()

        # Only start monitoring if not already active
        if (
            not self.should_monitor
            or not self.pulse_thread
            or not self.pulse_thread.is_alive()
        ):
            self.should_monitor = True
            self.start_pulse_monitoring()

    def on_tab_hidden(self, widget):
        """Called when the tab is hidden"""
        self.is_visible = False

    def start_pulse_monitoring(self):
        """Start the PulseAudio monitoring thread for real-time updates"""
        # Only start if not already monitoring
        if self.pulse_thread is None or not self.pulse_thread.is_alive():
            self.should_monitor = True
            self.pulse_thread = threading.Thread(
                target=self.monitor_pulse_events, daemon=True
            )
            self.pulse_thread.start()
            self.logging.log(LogLevel.Info, "Started real-time PulseAudio monitoring")
        else:
            self.logging.log(LogLevel.Info, "PulseAudio monitoring already active")

    def stop_pulse_monitoring(self):
        """Stop the PulseAudio monitoring thread"""
        self.should_monitor = False
        if self.pulse_thread and self.pulse_thread.is_alive():
            self.pulse_thread.join(1.0)  # Wait for the thread to terminate with timeout
            self.pulse_thread = None
        self.logging.log(LogLevel.Info, "Stopped PulseAudio monitoring")

    def monitor_pulse_events(self):
        """Simple periodic monitoring instead of event-based monitoring"""
        try:
            # Use a simple timeout-based refresh approach
            self.logging.log(LogLevel.Info, "Starting periodic (1-second) audio refresh")
            
            # Set up the periodic refresh
            refresh_counter = 0
            while self.should_monitor:
                # Sleep for a second
                time.sleep(1)
                
                # Skip updates if the tab is not visible
                if not self.is_visible:
                    continue
                    
                # Schedule UI update on the main thread
                GLib.idle_add(self.refresh_audio_state, refresh_counter)
                
                # Increment counter for selective updates
                refresh_counter = (refresh_counter + 1) % 10
                
            self.logging.log(LogLevel.Info, "Periodic audio refresh stopped")
            
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Error in audio monitor: {e}")
            # Attempt to restart the monitoring after a short delay
            if self.should_monitor:
                GLib.timeout_add(5000, self.restart_pulse_monitoring)
    
    def refresh_audio_state(self, counter):
        """Update audio state based on a counter (to distribute heavy operations)"""
        try:
            # Always update volume and mute states unless user is actively adjusting them
            updating_volume = hasattr(self, "_volume_change_timeout_id") and self._volume_change_timeout_id
            updating_mic = hasattr(self, "_mic_volume_change_timeout_id") and self._mic_volume_change_timeout_id
            
            # Update main volume if not being adjusted by user
            if not updating_volume:
                self.volume_scale.set_value(get_volume(self.logging))
                self.update_mute_button()
                
            # Update mic volume if not being adjusted by user
            if not updating_mic:
                self.mic_scale.set_value(get_mic_volume(self.logging))
                self.update_mic_mute_button()
            
            # Distribute heavier operations across different refresh cycles
            if counter % 3 == 0:  # Every 3 seconds
                self.update_device_lists()
                
            if counter % 2 == 0:  # Every 2 seconds
                self.update_application_list()
                
            if counter % 2 == 1:  # Alternate with app list (also every 2 seconds)
                self.update_mic_application_list()
                
        except Exception as e:
            self.logging.log(LogLevel.Error, f"Error refreshing audio state: {e}")
            
        return False  # Don't repeat via GLib (we're manually scheduling)
        
    def restart_pulse_monitoring(self):
        """Restart the pulse monitoring if it crashed"""
        if self.should_monitor and (
            not self.pulse_thread or not self.pulse_thread.is_alive()
        ):
            self.logging.log(LogLevel.Info, "Restarting audio monitoring")
            self.start_pulse_monitoring()
        return False  # Don't repeat this timeout

    def update_device_lists(self):
        """Update output and input device lists and sync dropdown with the actual default sink."""
        try:
            self.logging.log(LogLevel.Info, "Updating audio device lists...")

            # Get the currently active sink
            current_sink = subprocess.getoutput("pactl get-default-sink").strip()
            self.logging.log(
                LogLevel.Info, f"Current active output sink: {current_sink}"
            )

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
                    self.logging.log(
                        LogLevel.Info,
                        f"Adding output sink: {sink['name']} ({sink['description']})",
                    )
                    self.output_combo.append(sink["name"], sink["description"])
                    if sink["name"] == current_sink:
                        active_index = i

                if active_index != -1:
                    self.output_combo.set_active(active_index)
                else:
                    self.output_combo.set_active(0)  # Default to first item

            # Get the currently active input source (microphone)
            current_source = subprocess.getoutput("pactl get-default-source").strip()
            self.logging.log(
                LogLevel.Info, f"Current active input source: {current_source}"
            )

            # Input devices (microphones)
            self.input_combo.remove_all()
            sources = get_sources(self.logging)

            if not sources:
                self.logging.log(LogLevel.Warn, "No input sources found!")
                self.input_combo.append("no-source", "No Input Devices Found")
                self.input_combo.set_active(0)
            else:
                active_index = -1
                source_count = 0  # Track actual position in dropdown
                for i, source in enumerate(sources):
                    if "monitor" not in source["name"].lower():  # Skip monitor sources
                        self.logging.log(
                            LogLevel.Info,
                            f"Adding input source: {source['name']} ({source['description']})",
                        )
                        self.input_combo.append(source["name"], source["description"])
                        if source["name"] == current_source:
                            active_index = source_count
                        source_count += 1

                if active_index != -1:
                    self.input_combo.set_active(active_index)
                else:
                    self.input_combo.set_active(0)  # Default to first item

        except Exception as e:
            self.logging.log(LogLevel.Error, f"Failed updating device lists: {e}")

    def update_mute_buttons(self):
        """Update mute button labels"""
        self.update_mute_button()

        # Update mic mute button
        self.update_mic_mute_button()

    def update_mute_button(self):
        """Update speaker mute button icon"""
        speaker_muted = get_mute_state(self.logging)
        if speaker_muted:
            mute_icon = Gtk.Image.new_from_icon_name(
                "audio-volume-muted-symbolic", Gtk.IconSize.BUTTON
            )
            self.mute_button.set_tooltip_text("Unmute Speakers")
        else:
            mute_icon = Gtk.Image.new_from_icon_name(
                "audio-volume-high-symbolic", Gtk.IconSize.BUTTON
            )
            self.mute_button.set_tooltip_text("Mute Speakers")
        self.mute_button.set_image(mute_icon)

    def _configure_slider(self, scale):
        """Configure a volume slider with common settings for better performance"""
        scale.set_draw_value(True)
        scale.set_value_pos(Gtk.PositionType.RIGHT)
        scale.set_increments(1, 5)  # Small step, page increment
        scale.set_size_request(150, -1)  # Set minimum width
        return scale
        
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
            # Get available sinks for output selection
            sinks = get_sinks(self.logging)
            sink_options = [(sink["name"], sink["description"]) for sink in sinks]

            for app in apps:
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                box.set_margin_bottom(5)

                # App icon - try multiple sources with fallbacks
                icon = None

                # Try icon from app info first
                if "icon" in app:
                    icon_name = app["icon"]
                    if self.is_visible:
                        self.logging.log(
                            LogLevel.Debug, f"Trying app icon: {icon_name}"
                        )
                    if self.icon_exists(icon_name):
                        icon = Gtk.Image.new_from_icon_name(
                            icon_name, Gtk.IconSize.MENU
                        )

                # If icon is not valid or not found, try binary name as icon
                if not icon:
                    if "binary" in app:
                        binary_name = app["binary"].lower()
                        if self.is_visible:
                            self.logging.log(
                                LogLevel.Debug, f"Trying binary icon: {binary_name}"
                            )
                        if self.icon_exists(binary_name):
                            icon = Gtk.Image.new_from_icon_name(
                                binary_name, Gtk.IconSize.MENU
                            )

                # If still not valid, try app name as icon (normalized)
                if not icon:
                    app_icon_name = app["name"].lower().replace(" ", "-")
                    if self.is_visible:
                        self.logging.log(
                            LogLevel.Debug,
                            f"Trying normalized name icon: {app_icon_name}",
                        )
                    if self.icon_exists(app_icon_name):
                        icon = Gtk.Image.new_from_icon_name(
                            app_icon_name, Gtk.IconSize.MENU
                        )

                # Try some common app-specific mappings
                if not icon:
                    app_name = app["name"].lower()

                    # Map of known application names to their icon names
                    app_icon_map = {
                        "firefox": "firefox",
                        "chrome": "google-chrome",
                        "chromium": "chromium",
                        "spotify": "spotify",
                        "mpv": "mpv",
                        "vlc": "vlc",
                        "telegram": "telegram",
                        "discord": "discord",
                        "steam": "steam",
                        "brave": "brave",
                        "audacious": "audacious",
                        "clementine": "clementine",
                        "deadbeef": "deadbeef",
                        "rhythmbox": "rhythmbox",
                    }

                    # Check for partial matches in app name
                    for key, icon_name in app_icon_map.items():
                        if key in app_name and self.icon_exists(icon_name):
                            icon = Gtk.Image.new_from_icon_name(
                                icon_name, Gtk.IconSize.MENU
                            )
                            break

                # Last resort: fallback to generic audio icon
                if not icon:
                    icon = Gtk.Image.new_from_icon_name(
                        "audio-x-generic-symbolic", Gtk.IconSize.MENU
                    )

                box.pack_start(icon, False, False, 0)

                # App name
                name_label = Gtk.Label(label=app["name"])
                name_label.set_halign(Gtk.Align.START)
                box.pack_start(name_label, True, True, 0)

                # Volume control container (slider + mute button)
                volume_control_box = Gtk.Box(
                    orientation=Gtk.Orientation.HORIZONTAL, spacing=5
                )

                # Volume slider - use the helper method
                scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
                self._configure_slider(scale)
                scale.set_value(app["volume"])
                scale.connect("value-changed", self.on_app_volume_changed, app["id"])
                volume_control_box.pack_start(scale, True, True, 0)

                # App mute button - positioned right after the slider
                app_muted = get_application_mute_state(app["id"], self.logging)
                app_mute_button = Gtk.Button()
                if app_muted:
                    mute_icon = Gtk.Image.new_from_icon_name(
                        "audio-volume-muted-symbolic", Gtk.IconSize.BUTTON
                    )
                    app_mute_button.set_tooltip_text("Unmute")
                else:
                    mute_icon = Gtk.Image.new_from_icon_name(
                        "audio-volume-high-symbolic", Gtk.IconSize.BUTTON
                    )
                    app_mute_button.set_tooltip_text("Mute")
                app_mute_button.set_image(mute_icon)
                app_mute_button.connect("clicked", self.on_app_mute_clicked, app["id"])
                volume_control_box.pack_start(app_mute_button, False, False, 0)

                # Add volume control box to main box
                box.pack_start(volume_control_box, False, True, 0)

                # Output device selector
                output_combo = Gtk.ComboBoxText()
                output_combo.set_tooltip_text(
                    "Select output device for this application"
                )

                # Populate the output device dropdown
                for sink_name, sink_desc in sink_options:
                    output_combo.append(sink_name, sink_desc)

                # Get the current sink name for this application
                current_sink_name = ""
                if "sink" in app:
                    current_sink_name = get_sink_name_by_id(app["sink"], self.logging)
                    if self.is_visible:
                        self.logging.log(
                            LogLevel.Debug,
                            f"App {app['name']} is using sink ID: {app['sink']}, name: {current_sink_name}",
                        )

                # Set the active sink in the dropdown
                if current_sink_name:
                    # Find the index of the current sink in the options
                    for i, (sink_name, _) in enumerate(sink_options):
                        if sink_name == current_sink_name:
                            output_combo.set_active(i)
                            break
                    else:
                        # If not found, default to first option
                        output_combo.set_active(0)
                else:
                    # Default to first option
                    output_combo.set_active(0)

                # Connect the changed signal
                output_combo.connect("changed", self.on_app_output_changed, app["id"])

                box.pack_start(output_combo, False, True, 0)

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
        
        # Use debounce mechanism to avoid excessive updates
        if hasattr(self, "_volume_change_timeout_id") and self._volume_change_timeout_id:
            GLib.source_remove(self._volume_change_timeout_id)
            
        # Set a small timeout to aggregate rapid changes
        # Store the current value for the delayed handler
        self._pending_volume = value
        self._volume_change_timeout_id = GLib.timeout_add(50, self._apply_volume_change)
            
    def _apply_volume_change(self):
        """Apply the volume change after debouncing"""
        if hasattr(self, "_pending_volume"):
            value = self._pending_volume
            # Update the volume immediately when user changes slider
            set_volume(value, self.logging)
            # Force update of mute button to ensure it's in sync when unmuting via volume change
            if value > 0 and get_mute_state(self.logging):
                GLib.idle_add(self.update_mute_button)
            
        # Reset the timeout ID
        self._volume_change_timeout_id = None
        return False  # Don't repeat

    def on_mute_clicked(self, button):
        """Handle mute button clicks"""
        toggle_mute(self.logging)
        self.update_mute_buttons()

    def on_quick_volume_clicked(self, button, volume):
        """Handle quick volume button clicks"""
        set_volume(volume, self.logging)
        self.volume_scale.set_value(volume)

    def on_mic_volume_changed(self, scale):
        """Handle microphone volume scale changes"""
        value = int(scale.get_value())
        
        # Use debounce mechanism to avoid excessive updates
        if hasattr(self, "_mic_volume_change_timeout_id") and self._mic_volume_change_timeout_id:
            GLib.source_remove(self._mic_volume_change_timeout_id)
            
        # Set a small timeout to aggregate rapid changes
        # Store the current value for the delayed handler
        self._pending_mic_volume = value
        self._mic_volume_change_timeout_id = GLib.timeout_add(50, self._apply_mic_volume_change)
            
    def _apply_mic_volume_change(self):
        """Apply the microphone volume change after debouncing"""
        if hasattr(self, "_pending_mic_volume"):
            value = self._pending_mic_volume
            # Update the volume with the aggregated value
            set_mic_volume(value, self.logging)
            
        # Reset the timeout ID
        self._mic_volume_change_timeout_id = None
        return False  # Don't repeat

    def on_mic_mute_clicked(self, button):
        """Handle microphone mute button clicks"""
        toggle_mic_mute(self.logging)
        self.update_mic_mute_button()

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
        
        # Use per-app debouncing mechanism with a dictionary
        # Create the tracking dictionary if it doesn't exist
        if not hasattr(self, "_app_volume_timeouts"):
            self._app_volume_timeouts = {}
            self._pending_app_volumes = {}
            
        # Cancel previous timeout if exists
        if app_id in self._app_volume_timeouts and self._app_volume_timeouts[app_id]:
            GLib.source_remove(self._app_volume_timeouts[app_id])
            
        # Store the pending value and create a new timeout
        self._pending_app_volumes[app_id] = value
        self._app_volume_timeouts[app_id] = GLib.timeout_add(
            50, 
            lambda: self._apply_app_volume_change(app_id)
        )
            
    def _apply_app_volume_change(self, app_id):
        """Apply the application volume change after debouncing"""
        if hasattr(self, "_pending_app_volumes") and app_id in self._pending_app_volumes:
            value = self._pending_app_volumes[app_id]
            # Apply the volume change
            set_application_volume(app_id, value, self.logging)
            
        # Reset the timeout ID
        if hasattr(self, "_app_volume_timeouts"):
            self._app_volume_timeouts[app_id] = None
            
        return False  # Don't repeat

    def on_app_output_changed(self, combo, app_id):
        """Handle application output device changes"""
        device_id = combo.get_active_id()
        if device_id:
            try:
                # First check if the application still exists
                app_exists = False
                apps = get_applications(self.logging)
                for app in apps:
                    if app["id"] == app_id:
                        app_exists = True
                        break

                if app_exists:
                    move_application_to_sink(app_id, device_id, self.logging)
                    self.logging.log(
                        LogLevel.Info,
                        f"Moving application {app_id} to sink {device_id}",
                    )
                else:
                    self.logging.log(
                        LogLevel.Warn,
                        f"Cannot move application {app_id}, it no longer exists",
                    )
                    # Force refresh to remove stale apps
                    self.update_application_list()
            except Exception as e:
                self.logging.log(
                    LogLevel.Error, f"Failed moving application to sink: {e}"
                )
                # Force refresh to ensure UI is in sync with actual state
                self.update_application_list()

    def on_app_mute_clicked(self, button, app_id):
        """Handle application mute button clicks"""
        toggle_application_mute(app_id, self.logging)
        self.update_application_list()

    def on_app_mic_volume_changed(self, scale, app_id):
        """Handle application microphone volume changes"""
        value = int(scale.get_value())
        
        # Use per-app debouncing mechanism with a dictionary
        # Create the tracking dictionary if it doesn't exist
        if not hasattr(self, "_app_mic_volume_timeouts"):
            self._app_mic_volume_timeouts = {}
            self._pending_app_mic_volumes = {}
            
        # Cancel previous timeout if exists
        if app_id in self._app_mic_volume_timeouts and self._app_mic_volume_timeouts[app_id]:
            GLib.source_remove(self._app_mic_volume_timeouts[app_id])
            
        # Store the pending value and create a new timeout
        self._pending_app_mic_volumes[app_id] = value
        self._app_mic_volume_timeouts[app_id] = GLib.timeout_add(
            50, 
            lambda: self._apply_app_mic_volume_change(app_id)
        )
            
    def _apply_app_mic_volume_change(self, app_id):
        """Apply the application microphone volume change after debouncing"""
        if hasattr(self, "_pending_app_mic_volumes") and app_id in self._pending_app_mic_volumes:
            value = self._pending_app_mic_volumes[app_id]
            # Apply the volume change
            set_application_mic_volume(app_id, value, self.logging)
            
        # Reset the timeout ID
        if hasattr(self, "_app_mic_volume_timeouts"):
            self._app_mic_volume_timeouts[app_id] = None
            
        return False  # Don't repeat

    def on_app_mic_mute_clicked(self, button, app_id):
        """Handle application microphone mute button clicks"""
        toggle_application_mic_mute(app_id, self.logging)
        self.update_mic_application_list()

    def icon_exists(self, icon_name):
        """Check if an icon exists in the icon theme"""
        return self.icon_theme.has_icon(icon_name)

    def update_mic_mute_button(self):
        """Update microphone mute button"""
        mic_muted = get_mic_mute_state(self.logging)
        if mic_muted:
            mute_icon = Gtk.Image.new_from_icon_name(
                "microphone-disabled-symbolic", Gtk.IconSize.BUTTON
            )
            self.mic_mute_button.set_tooltip_text("Unmute Microphone")
        else:
            mute_icon = Gtk.Image.new_from_icon_name(
                "microphone-sensitivity-high-symbolic", Gtk.IconSize.BUTTON
            )
            self.mic_mute_button.set_tooltip_text("Mute Microphone")
        self.mic_mute_button.set_image(mute_icon)

    def update_mic_application_list(self):
        """Update microphone application list"""
        # Remove existing controls
        for child in self.mic_app_box.get_children():
            self.mic_app_box.remove(child)

        # Add controls for each application using microphone
        mic_apps = get_source_outputs(self.logging)
        if not mic_apps:
            # Show "No applications using microphone" message
            no_mic_apps_label = Gtk.Label()
            no_mic_apps_label.set_markup("<i>No applications using microphone</i>")
            no_mic_apps_label.set_halign(Gtk.Align.START)
            no_mic_apps_label.set_margin_top(5)
            no_mic_apps_label.set_margin_bottom(5)
            self.mic_app_box.pack_start(no_mic_apps_label, False, True, 0)
        else:
            for app in mic_apps:
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                box.set_margin_bottom(5)

                # App icon
                icon = None

                # Try icon from app info first
                if "icon" in app:
                    icon_name = app["icon"]
                    if self.is_visible:
                        self.logging.log(
                            LogLevel.Debug, f"Trying app icon: {icon_name}"
                        )
                    if self.icon_exists(icon_name):
                        icon = Gtk.Image.new_from_icon_name(
                            icon_name, Gtk.IconSize.MENU
                        )

                # If icon is not valid or not found, try binary name as icon
                if not icon:
                    if "binary" in app:
                        binary_name = app["binary"].lower()
                        if self.is_visible:
                            self.logging.log(
                                LogLevel.Debug, f"Trying binary icon: {binary_name}"
                            )
                        if self.icon_exists(binary_name):
                            icon = Gtk.Image.new_from_icon_name(
                                binary_name, Gtk.IconSize.MENU
                            )

                # Last resort: fallback to generic audio icon
                if not icon:
                    icon = Gtk.Image.new_from_icon_name(
                        "audio-input-microphone-symbolic", Gtk.IconSize.MENU
                    )

                box.pack_start(icon, False, False, 0)

                # App name
                name_label = Gtk.Label(label=app["name"])
                name_label.set_halign(Gtk.Align.START)
                box.pack_start(name_label, True, True, 0)

                # Mic control container
                mic_control_box = Gtk.Box(
                    orientation=Gtk.Orientation.HORIZONTAL, spacing=5
                )

                # Volume slider
                volume = get_application_mic_volume(app["id"], self.logging)
                scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
                self._configure_slider(scale)
                scale.set_value(volume)
                scale.connect(
                    "value-changed", self.on_app_mic_volume_changed, app["id"]
                )
                mic_control_box.pack_start(scale, True, True, 0)

                # Mic mute button
                app_mic_muted = get_application_mic_mute_state(app["id"], self.logging)
                app_mic_mute_button = Gtk.Button()
                if app_mic_muted:
                    mute_icon = Gtk.Image.new_from_icon_name(
                        "microphone-disabled-symbolic", Gtk.IconSize.BUTTON
                    )
                    app_mic_mute_button.set_tooltip_text(
                        "Unmute Microphone for this application"
                    )
                else:
                    mute_icon = Gtk.Image.new_from_icon_name(
                        "microphone-sensitivity-high-symbolic", Gtk.IconSize.BUTTON
                    )
                    app_mic_mute_button.set_tooltip_text(
                        "Mute Microphone for this application"
                    )
                app_mic_mute_button.set_image(mute_icon)
                app_mic_mute_button.connect(
                    "clicked", self.on_app_mic_mute_clicked, app["id"]
                )
                mic_control_box.pack_start(app_mic_mute_button, False, False, 0)

                # Add mic control box to main box
                box.pack_start(mic_control_box, False, False, 0)

                self.mic_app_box.pack_start(box, False, True, 0)

        self.mic_app_box.show_all()

    def connect_destroy_signal(self):
        """Connect to the destroy signal to clean up resources when the widget is destroyed"""

        def on_destroy(*args):
            self.logging.log(
                LogLevel.Info, "Volume tab is being destroyed, cleaning up resources"
            )
            self.stop_pulse_monitoring()

        self.connect("destroy", on_destroy)

    def __del__(self):
        """Ensure resources are cleaned up when the object is garbage collected"""
        try:
            self.stop_pulse_monitoring()
        except:
            pass
