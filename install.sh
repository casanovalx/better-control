#!/bin/bash
# A simple script to install Better Control on ur OS
echo " "
echo "This script is still under development to improve it if you find any errors head over to 'https://github.com/quantumvoid0/better-control/issues' and open an issue on it"
echo " "

set -e

install_arch() {
    if command -v yay >/dev/null 2>&1; then
        echo "✅ yay found! Installing with yay..."
        yay -S --noconfirm better-control-git
    else
        echo "⚠️ yay not found. Falling back to manual AUR install..."
        git clone https://aur.archlinux.org/better-control-git.git
        cd better-control-git
        makepkg -si --noconfirm
    fi
}

install_debian() {
    echo "⬇️Installing dependencies for Debian-based systems..."
    sudo apt update
    sudo apt install -y libgtk-3-dev network-manager bluez bluez-utils pulseaudio brightnessctl python3-gi python3-dbus python3 power-profiles-daemon gammastep python3-requests python3-qrcode python3-setproctitle python3-pil usbguard

    git clone https://github.com/quantumvoid0/better-control.git
    cd better-control
    make
    sudo make install
}

install_fedora() {
    echo "⬇️Installing dependencies for Fedora-based systems..."
    sudo dnf install -y gtk3 NetworkManager bluez bluez-utils pulseaudio brightnessctl python3-gobject python3-dbus python3 power-profiles-daemon gammastep python3-requests python3-qrcode python3-setproctitle python3-pillow usbguard

    git clone https://github.com/quantumvoid0/better-control.git
    cd better-control
    make
    sudo make install
}

install_void() {
    echo "⬇️Installing dependencies for Void Linux..."
    sudo xbps-install -Sy NetworkManager pulseaudio brightnessctl python3-gobject python3-dbus python3 power-profiles-daemon gammastep python3-requests python3-qrcode gtk+3 bluez python3-Pillow usbguard python3-pip
    pip install setproctitle

    git clone https://github.com/quantumvoid0/better-control.git
    cd better-control
    make
    sudo make install
}

install_alpine() {
    echo "⬇️Installing dependencies for Alpine Linux..."
    sudo apk add gtk3 networkmanager bluez bluez-utils pulseaudio brightnessctl py3-gobject py3-dbus python3 power-profiles-daemon gammastep py3-requests py3-qrcode py3-pip py3-setuptools gcc musl-dev python3-dev py3-pillow
    pip install setproctitle

    git clone https://github.com/quantumvoid0/better-control.git
    cd better-control
    make
    sudo make install
}

detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        case "$ID" in
            arch | endeavouros | manjaro)
                install_arch
                ;;
            debian | ubuntu | linuxmint | pop)
                install_debian
                ;;
            fedora | rhel)
                install_fedora
                ;;
            void)
                install_void
                ;;
            alpine)
                install_alpine
                ;;
            nixos)
                echo "❄️ Detected NixOS. This package has an unofficial flake here:"
                echo "https://github.com/Rishabh5321/better-control-flake"
                ;;
            *)
                echo "❌ Unsupported distro: $ID"
                exit 1
                ;;
        esac
    else
        echo "❌ Unable to detect OS. /etc/os-release missing. You can head over to 'https://github.com/quantumvoid0/better-control' and manually build the app"
        exit 1
    fi
}

detect_os

