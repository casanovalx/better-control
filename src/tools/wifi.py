#!/usr/bin/env python3

from pathlib import Path
import qrcode
import subprocess
from typing import List, Dict

import qrcode.constants
from utils.logger import LogLevel, Logger


def get_wifi_status(logging: Logger) -> bool:
    """Get WiFi power status

    Returns:
        bool: True if WiFi is enabled, False otherwise
    """
    try:
        result = subprocess.run(
            ["nmcli", "radio", "wifi"], capture_output=True, text=True
        )
        return result.stdout.strip().lower() == "enabled"
    except Exception as e:
        logging.log(LogLevel.Error, f"Failed getting WiFi status: {e}")
        return False


def set_wifi_power(enabled: bool, logging: Logger) -> None:
    """Set WiFi power state

    Args:
        enabled (bool): True to enable, False to disable
    """
    try:
        state = "on" if enabled else "off"
        subprocess.run(["nmcli", "radio", "wifi", state], check=True)
    except subprocess.CalledProcessError as e:
        logging.log(LogLevel.Error, f"Failed setting WiFi power: {e}")


def get_wifi_networks(logging: Logger) -> List[Dict[str, str]]:
    """Get list of available WiFi networks

    Returns:
        List[Dict[str, str]]: List of network dictionaries
    """
    try:
        # Check if WiFi is supported on this system
        result = subprocess.run(
            ["nmcli", "-t", "-f", "DEVICE,TYPE", "device"],
            capture_output=True,
            text=True,
        )
        wifi_interfaces = [line for line in result.stdout.split("\n") if "wifi" in line]
        if not wifi_interfaces:
            logging.log(LogLevel.Warn, "WiFi is not supported on this machine")
            return []

        # Use --terse mode and specific fields for more reliable parsing
        result = subprocess.run(
            [
                "nmcli",
                "-t",
                "-f",
                "IN-USE,SSID,SIGNAL,SECURITY",
                "device",
                "wifi",
                "list",
            ],
            capture_output=True,
            text=True,
        )
        output = result.stdout
        networks = []
        for line in output.split("\n"):
            if not line.strip():
                continue
            # Split by ':' since we're using terse mode
            parts = line.split(":")
            if len(parts) >= 4:
                in_use = "*" in parts[0]
                ssid = parts[1]
                signal = parts[2] if parts[2].strip() else "0"
                security = parts[3] if parts[3].strip() != "" else "none"
                # Only add networks with valid SSIDs
                if ssid and ssid.strip():
                    networks.append(
                        {
                            "in_use": in_use,
                            "ssid": ssid.strip(),
                            "signal": signal.strip(),
                            "security": security.strip(),
                        }
                    )
        return networks
    except Exception as e:
        logging.log(LogLevel.Error, f"Failed getting WiFi networks: {e}")
        return []


def get_connection_info(ssid: str, logging: Logger) -> Dict[str, str]:
    """Get information about a WiFi connection

    Args:
        ssid (str): Network SSID

    Returns:
        Dict[str, str]: Dictionary containing connection information
    """
    try:
        result = subprocess.run(
            ["nmcli", "-t", "--show-secrets", "connection", "show", ssid], capture_output=True, text=True
        )
        output = result.stdout
        info = {}
        for line in output.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        password = info.get("802-11-wireless-security.psk", "Hidden")
        info["password"] = password
        return info
    except Exception as e:
        logging.log(LogLevel.Error, f"Failed getting connection info: {e}")
        return {}


def connect_network(
    ssid: str, logging: Logger, password: str = "", remember: bool = True
) -> bool:
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
        logging.log(LogLevel.Error, f"Failed connecting to network: {e}")
        return False


def disconnect_network(ssid: str, logging: Logger) -> bool:
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
        logging.log(LogLevel.Error, f"Failed disconnecting from network: {e}")
        return False


def forget_network(ssid: str, logging: Logger) -> bool:
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
        logging.log(LogLevel.Error, f"Failed removing network: {e}")
        return False


def get_network_speed(logging: Logger) -> Dict[str, float]:
    """Get current network speed

    Returns:
        Dict[str, float]: Dictionary with upload and download speeds in Mbps
    """
    try:
        # Get WiFi interface name
        result = subprocess.run(
            ["nmcli", "-t", "-f", "DEVICE,TYPE", "device"],
            capture_output=True,
            text=True,
        )
        output = result.stdout
        wifi_lines = [line for line in output.split("\n") if "wifi" in line]

        if not wifi_lines:
            # Return zeros with the expected keys when WiFi is not supported
            logging.log(LogLevel.Warn, "WiFi is not supported on this machine")
            return {"rx_bytes": 0, "tx_bytes": 0, "wifi_supported": False}

        interface = wifi_lines[0].split(":")[0]

        # Get current bytes
        with open(f"/sys/class/net/{interface}/statistics/rx_bytes") as f:
            rx_bytes = int(f.read())
        with open(f"/sys/class/net/{interface}/statistics/tx_bytes") as f:
            tx_bytes = int(f.read())
        return {"rx_bytes": rx_bytes, "tx_bytes": tx_bytes, "wifi_supported": True}
    except Exception as e:
        logging.log(LogLevel.Error, f"Failed getting network speed: {e}")
        return {"rx_bytes": 0, "tx_bytes": 0, "wifi_supported": False}

def generate_wifi_qrcode(ssid: str, password: str, security: str, logging:Logger) -> str:
    """Generate qr_code for the wifi
    
    Returns:
        str: path to generated qr code image 
    """
    
    try:
        temp_dir = Path("/tmp/better-control")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        qr_code_path = temp_dir / f"{ssid}.png"
        if qr_code_path.exists():
            logging.log(LogLevel.Info, f"found qr code for {ssid} at {qr_code_path}")
            return str(qr_code_path)
        
        security_type = "WPA" if security.lower() != "none" else "nopass"
        wifi_string = f"WIFI:T:{security_type};S:{ssid};P:{password};;"
        
        # generate the qr code
        qr_code = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=2,
        )
        qr_code.add_data(wifi_string)
        qr_code.make(fit=True)
        
        # create qr code image
        qr_code_image = qr_code.make_image(fill_color="black", back_color="white")
        qr_code_image.save(qr_code_path)
        
        logging.log(LogLevel.Info, f"generated qr code for {ssid} at {qr_code_path}")
        return str(qr_code_path)
        
    except Exception as e:
        logging.log(LogLevel.Error, f"Failed to generate qr code for {ssid} : {e}")