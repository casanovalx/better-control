#!/bin/bash
# A simple script to install or uninstall Better Control on your OS
echo "your version : 6.10.2"
echo " "
echo "This script is still under development to improve it if you find any errors head over to 'https://github.com/quantumvoid0/better-control/issues' and open an issue on it"
echo " "

set -e

install_arch() {
        rm -rf ~/better-control-git
        git clone https://aur.archlinux.org/better-control-git.git
        cd better-control-git
        makepkg -si --noconfirm
        rm -rf ~/better-control-git
        echo "✅ Installation complete. You can run Better Control using the command 'control' or open the better-control app."
}

install_debian() {
    echo "⬇️Installing dependencies for Debian-based systems..."
    sudo apt update
    sudo apt install -y libgtk-3-dev network-manager bluez bluez-utils pulseaudio brightnessctl python3-gi python3-dbus python3 power-profiles-daemon gammastep python3-requests python3-qrcode python3-setproctitle python3-pil usbguard

    git clone https://github.com/quantumvoid0/better-control.git
    cd better-control
    make
    sudo make install
    rm -rf ~/better-control
    echo "✅ Installation complete. You can run Better Control using the command 'control' or open the better-control app."
}

install_fedora() {
    echo "⬇️Installing dependencies for Fedora-based systems..."
    sudo dnf install -y gtk3 NetworkManager bluez bluez-utils pulseaudio brightnessctl python3-gobject python3-dbus python3 power-profiles-daemon gammastep python3-requests python3-qrcode python3-setproctitle python3-pillow usbguard

    git clone https://github.com/quantumvoid0/better-control.git
    cd better-control
    make
    sudo make install
    rm -rf ~/better-control
    echo "✅ Installation complete. You can run Better Control using the command 'control' or open the better-control app."
}

install_void() {
    echo "⬇️Installing dependencies for Void Linux..."
    sudo xbps-install -Sy NetworkManager pulseaudio brightnessctl python3-gobject python3-dbus python3 power-profiles-daemon gammastep python3-requests python3-qrcode gtk+3 bluez python3-Pillow usbguard python3-pip
    pip install setproctitle

    git clone https://github.com/quantumvoid0/better-control.git
    cd better-control
    make
    sudo make install
    rm -rf ~/better-control
    echo "✅ Installation complete. You can run Better Control using the command 'control' or open the better-control app."
}

install_alpine() {
    echo "⬇️Installing dependencies for Alpine Linux..."
    sudo apk add gtk3 networkmanager bluez bluez-utils pulseaudio brightnessctl py3-gobject py3-dbus python3 power-profiles-daemon gammastep py3-requests py3-qrcode py3-pip py3-setuptools gcc musl-dev python3-dev py3-pillow
    pip install setproctitle

    git clone https://github.com/quantumvoid0/better-control.git
    cd better-control
    make
    sudo make install
    rm -rf ~/better-control
    echo "✅ Installation complete. You can run Better Control using the command 'control' or open the better-control app."
}

uninstall_arch() {
    echo "Uninstalling better-control-git on Arch Linux..."
    sudo rm /usr/bin/betterctl
    sudo pacman -R --noconfirm better-control-git
}

uninstall_others() {
    echo "Uninstalling better-control on other distros..."
    git clone https://github.com/quantumvoid0/better-control
    cd better-control
    sudo make uninstall
    rm -rf ~/better-control
    echo "✅ Uninstallation complete."
}

detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    else
        echo "unknown"
    fi
}

confirm() {
    # Prompt for yes/no confirmation
    while true; do
        read -p "$1 [y/n]: " yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes or no. (Y for yes and N for no)";;
        esac
    done
}

echo "Do you want to install or uninstall or update Better Control?"
echo "type 'i' for install and 'u' for uninstall and 'update' for update"
read -r choice

case "$choice" in
    i|I|install)
        echo "Starting installation..."
        detect_os_id=$(detect_os)
        case "$detect_os_id" in
            arch|endeavouros|manjaro)
                install_arch
                ;;
            debian|ubuntu|linuxmint|pop)
                install_debian
                ;;
            fedora|rhel)
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
                echo "❌ Unsupported distro: $detect_os_id please open an issue on the GitHub repository on this and well add your distro."
                exit 1
                ;;
        esac
        ;;
    u|U|uninstall)
        echo "You chose to uninstall Better Control."
        if confirm "Are you sure you want to uninstall? Y for yes , N for no"; then
            detect_os_id=$(detect_os)
            case "$detect_os_id" in
                arch|endeavouros|manjaro)
                    uninstall_arch
                    ;;
                *)
                    uninstall_others
                    ;;
            esac
            echo "✅ Uninstallation complete."
        else
            echo "❌ Uninstallation cancelled."
        fi
        ;;

    update|Update)
        echo "Starting update (uninstall and reinstall)..."
        detect_os_id=$(detect_os)
        case "$detect_os_id" in
            arch|endeavouros|manjaro)
                echo "Uninstalling on Arch-based distro..."
                uninstall_arch
                echo "Installing on Arch-based distro..."
                install_arch
                ;;
            debian|ubuntu|linuxmint|pop)
                echo "Uninstalling on Debian-based distro..."
                uninstall_others
                echo "Installing on Debian-based distro..."
                install_debian
                ;;
            fedora|rhel)
                echo "Uninstalling on Fedora-based distro..."
                uninstall_others
                echo "Installing on Fedora-based distro..."
                install_fedora
                ;;
            void)
                echo "Uninstalling on Void Linux..."
                uninstall_others
                echo "Installing on Void Linux..."
                install_void
                ;;
            alpine)
                echo "Uninstalling on Alpine Linux..."
                uninstall_others
                echo "Installing on Alpine Linux..."
                install_alpine
                ;;
            nixos)
                echo "❄️ Detected NixOS. This package has an unofficial flake here:"
                echo "https://github.com/Rishabh5321/better-control-flake"
                ;;
            *)
                echo "❌ Unsupported distro: $detect_os_id please open an issue on the GitHub repository on this and well add your distro."
                exit 1
                ;;
        esac
        echo "✅ Update complete."
        ;;

        

    *)
        echo "Invalid choice. Please run the script again and choose 'install' or 'uninstall'."
        exit 1
        ;;
esac
