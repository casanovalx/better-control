#!/usr/bin/env python3

from pathlib import Path
import subprocess

CONFIG_FILES = [
    Path.home() / ".config/hypr/hyprland.conf",
    Path.home() / ".config/hypr/autostart.conf"
        ]

def get_hyprland_startup_apps():
    """Retrieve apps started using exec-once in Hyprland"""
    startup_apps = {}
    for hypr_config in CONFIG_FILES:
        if hypr_config.exists():
            with open(hypr_config, "r") as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                stripped = line.strip()
                if "exec-once" in stripped:
                    enabled = not stripped.startswith("#")
                    
                    cleared_line = stripped.lstrip("#").strip()
                    if "=" in cleared_line:
                        parts = cleared_line.split("=", 1)
                        command = parts[1].strip().strip('"')
                    else:
                        parts = cleared_line.split(None, 1)
                        if len(parts) > 1:
                            command = parts[1].strip().strip('"')
                        else:
                            continue
                    startup_apps[command] = {
                        "name": command,
                        "type": "hyprland",
                        "path": hypr_config,
                        "line_index": i,
                        "enabled": enabled
                    }
    return startup_apps

def toggle_hyprland_startup(command):
    """Toggle the startup state of command in Hyprland config"""
    apps = get_hyprland_startup_apps()
    if command not in apps:
        print(f"Command '{command}' not found in Hyprland autostart apps.")
        return
    
    app_info = apps[command]
    config_path = app_info["path"]
    
    with open(config_path, "r") as f:
        lines = f.readlines()
    
    if app_info["enabled"]:
        # Comment out the line to disable the app
        lines[app_info["line_index"]] = f"# {lines[app_info['line_index']].lstrip('# ').strip()}\n"
        print(f"Disabled startup for: {command}")
    else:
        # Uncomment the line to enable the app
        lines[app_info["line_index"]] = lines[app_info["line_index"]].lstrip("# ").strip() + "\n"
        print(f"Enabled startup for: {command}")
    
    with open(config_path, "w") as f:
        f.writelines(lines)
    
    # Reload hyprland
    subprocess.run(["hyprctl", "reload"])
    
def get_hyprland_displays() -> dict:
    """Get current displays and their transforms from hyprctl monitors
    Returns:
        dict: Dictionary with display names as keys and transforms as values for each display
    """
    try:
        result = subprocess.run(["hyprctl", "monitors"], capture_output=True, text=True)
        if result.returncode != 0:
            return {}
            
        displays = {}
        current_display = None
        
        for line in result.stdout.split('\n'):
            line = line.strip()
            if line.startswith('Monitor'):
                current_display = line.split()[1]
            elif 'transform:' in line and current_display:
                transform = int(line.split(':')[1].strip())
                displays[current_display] = transform
                current_display = None
                
        return displays
    except Exception as e:
        print(f"Error getting Hyprland displays: {e}")
        return {}
    
def set_hyprland_transform(display: str, orientation: str) -> bool:
    """Set display transform in Hyprland

    Args:
        display: Display name (e.g. 'eDP-1')
        orientation: Desired orientation ('normal: 0', 'right:1 ', 'inverted: 2', 'left: 3')
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        transform_map = {
            "normal": 0,
            "right": 1,
            "inverted": 2,
            "left": 3
        }
        
        transform = transform_map.get(orientation.lower(), 0)
        
        # hyprctl command to transform display 
        cmd = [
            "hyprctl",
            "keyword",
            f"monitor {display},preferred,auto,1,transform,{transform}"
        ]
        
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0

    except Exception as e:
        print(f"Error setting Hyprland transform: {e}")
        return False


def get_hyprland_rotation():
    try:
        result = subprocess.run(["hyprctl", "monitors"], capture_output=True, text=True)
        output = result.stdout

        for line in output.splitlines():
            if "transform:" in line:
                transform_value = int(line.strip().split(":")[1].strip())
                transform_map = {
                    0: "normal",
                    1: "right",
                    2: "inverted",
                    3: "left"
                }
                return transform_map.get(transform_value, f"unknown ({transform_value})")
    except Exception as e:
        return f"Error: {e}"