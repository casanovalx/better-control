#!/bin/bash
############################# 
# download this script
# run this script with sudo
#############################


# USBGuard Permission Setup Script
echo "=== USBGuard Permission Setup ==="
echo "This will configure your system to allow USBGuard access"

# Verify root
if [ "$(id -u)" -ne 0 ]; then
    echo "Please run this script with sudo or as root"
    exit 1
fi

# Create usbguard group if needed
echo -n "Creating usbguard group... "
groupadd usbguard 2>/dev/null || true
echo "Done"

# Add user to groups
echo -n "Adding user to usbguard and plugdev groups... "
usermod -aG usbguard,plugdev $(logname)
echo "Done"

# Create udev rule
echo -n "Creating udev rules... "
echo 'SUBSYSTEM=="usb", MODE="0664", GROUP="plugdev"' > /etc/udev/rules.d/99-usbguard.rules
echo "Done"

# Configure IPC permissions
echo -n "Updating USBGuard configuration... "
sed -i '/^IPCAllowedUsers=/ s/$/ '$(logname)'/' /etc/usbguard/usbguard-daemon.conf
sed -i '/^IPCAllowedGroups=/ s/$/ usbguard/' /etc/usbguard/usbguard-daemon.conf
echo "Done"

# Reload udev
echo -n "Reloading udev rules... "
udevadm control --reload-rules
echo "Done"

# Restart service
echo -n "Restarting USBGuard... "
systemctl restart usbguard
echo "Done"

echo ""
echo "Setup complete! Please:"
echo "1. Log out and back in for changes to take effect"
echo "2. Run: python src/better_control.py"
echo ""
echo "Note: You may need to reconnect USB devices after this setup"
