#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

def load_animations_css():
    """Load global animations CSS"""
    css_provider = Gtk.CssProvider()
    css = """
    /* Basic transitions */
    button {
        transition: opacity 200ms ease;
    }

    button:hover {
        opacity: 0.9;
    }

    /* Fade-in animation class */
    .fade-in {
        animation: fade-in-animation 300ms ease forwards;
    }

    @keyframes fade-in-animation {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    /* Spinner animation */
    spinner {
        opacity: 0.8;
    }

    /* Power button animations */
    .power-button:hover {
        opacity: 0.9;
    }
    
    /* settings icon animation */
    .roate-gear {
        -gtk-icon-transform: rotate(0deg);
    }
    .rotate-gear-active {
        -gtk-icon-transform: rotate(26deg);
    }
    """

    css_provider.load_from_data(css.encode())

    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    return css_provider

def add_animation_classes(widget, animation_class):
    """Add animation class to widget"""
    widget.get_style_context().add_class(animation_class)

def animate_widget_show(widget, animation_type="fade-in"):
    """Animate widget appearance

    Args:
        widget: The widget to animate
        animation_type: Type of animation (fade-in, slide-in-right, slide-in-left, slide-in-up)
    """
    # Make sure widget is visible
    widget.show_all()

    # Add animation class
    add_animation_classes(widget, animation_type)

    # Remove class after animation completes
    def remove_animation_class():
        widget.get_style_context().remove_class(animation_type)
        return False

    # Schedule class removal after animation duration
    GLib.timeout_add(350, remove_animation_class)
