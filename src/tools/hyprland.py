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
    
    # Reload Hyprland
    subprocess.run(["hyprctl", "reload"])