#!/usr/bin/env python3

import subprocess
from typing import List, Dict
import logging

def get_wifi_status() -> bool:
    """Get WiFi power status

    Returns:
        bool: True if WiFi is enabled, False otherwise
    """
    try:
        output = subprocess.getoutput("nmcli radio wifi")
        return output.strip().lower() == "enabled"
    except Exception as e:
        logging.error(f"Error getting WiFi status: {e}")
        return False

def set_wifi_power(enabled: bool) -> None:
    """Set WiFi power state

    Args:
        enabled (bool): True to enable, False to disable
    """
    try:
        state = "on" if enabled else "off"
        subprocess.run(["nmcli", "radio", "wifi", state], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error setting WiFi power: {e}")

def get_wifi_networks() -> List[Dict[str, str]]:
    """Get list of available WiFi networks

    Returns:
        List[Dict[str, str]]: List of network dictionaries
    """
    try:
        # Use --terse mode and specific fields for more reliable parsing
        output = subprocess.getoutput("nmcli -t -f IN-USE,SSID,SIGNAL,SECURITY device wifi list")
        networks = []
        for line in output.split('\n'):
            if not line.strip():
                continue
            # Split by ':' since we're using terse mode
            parts = line.split(':')
            if len(parts) >= 4:
                in_use = "*" in parts[0]
                ssid = parts[1]
                signal = parts[2] if parts[2].strip() else "0"
                security = parts[3] if parts[3].strip() != "" else "none"
                # Only add networks with valid SSIDs
                if ssid and ssid.strip():
                    networks.append({
                        "in_use": in_use,
                        "ssid": ssid.strip(),
                        "signal": signal.strip(),
                        "security": security.strip()
                    })
        return networks
    except Exception as e:
        logging.error(f"Error getting WiFi networks: {e}")
        return []

def get_connection_info(ssid: str) -> Dict[str, str]:
    """Get information about a WiFi connection

    Args:
        ssid (str): Network SSID

    Returns:
        Dict[str, str]: Dictionary containing connection information
    """
    try:
        output = subprocess.getoutput(f"nmcli -t connection show '{ssid}'")
        info = {}
        for line in output.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        return info
    except Exception as e:
        logging.error(f"Error getting connection info: {e}")
        return {}

def connect_network(ssid: str, password: str = "", remember: bool = True) -> bool:
    """Connect to a WiFi network

    Args:
        ssid (str): Network SSID
        password (str, optional): Network password. Defaults to None.
        remember (bool, optional): Whether to save the connection. Defaults to True.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        # First try to connect using saved connection
        try:
            subprocess.run(["nmcli", "con", "up", ssid], check=True)
            return True
        except subprocess.CalledProcessError:
            # If saved connection fails, try with password if provided
            if password:
                cmd = ["nmcli", "device", "wifi", "connect", ssid, "password", password]
                if not remember:
                    cmd.extend(["--temporary"])
                subprocess.run(cmd, check=True)
                return True
            return False
    except subprocess.CalledProcessError as e:
        logging.error(f"Error connecting to network: {e}")
        return False

def disconnect_network(ssid: str) -> bool:
    """Disconnect from a WiFi network

    Args:
        ssid (str): Network SSID

    Returns:
        bool: True if disconnection successful, False otherwise
    """
    try:
        subprocess.run(["nmcli", "connection", "down", ssid], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error disconnecting from network: {e}")
        return False

def forget_network(ssid: str) -> bool:
    """Remove a saved WiFi network

    Args:
        ssid (str): Network SSID

    Returns:
        bool: True if removal successful, False otherwise
    """
    try:
        subprocess.run(["nmcli", "connection", "delete", ssid], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error removing network: {e}")
        return False

def get_network_speed() -> Dict[str, float]:
    """Get current network speed

    Returns:
        Dict[str, float]: Dictionary with upload and download speeds in Mbps
    """
    try:
        # Get WiFi interface name
        output = subprocess.getoutput("nmcli -t -f DEVICE,TYPE device | grep wifi")
        if not output:
            return {"upload": 0.0, "download": 0.0}

        interface = output.split(":")[0]

        # Get current bytes
        with open(f"/sys/class/net/{interface}/statistics/rx_bytes") as f:
            rx_bytes = int(f.read())
        with open(f"/sys/class/net/{interface}/statistics/tx_bytes") as f:
            tx_bytes = int(f.read())
        return {
            "rx_bytes": rx_bytes,
            "tx_bytes": tx_bytes
        }
    except Exception as e:
        logging.error(f"Error getting network speed: {e}")
        return {"rx_bytes": 0, "tx_bytes": 0}
