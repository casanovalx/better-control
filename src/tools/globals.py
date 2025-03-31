#!/usr/bin/env python3
import os

def get_current_session():  
    if "hyprland" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower():
        return "Hyprland"
    elif "sway" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower():
        return "sway"
    else:
        return False
    