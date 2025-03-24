# Better-Control 🛠️   
							
A GTK-themed control panel for Linux 🐧

<img src="https://github.com/user-attachments/assets/b219415d-3dbf-4471-990d-bc8cd0f021c1" width="500">

> **Note:** The application follows your system GTK theme for a native and integrated look.

## What's New
- now you can open directly into tabs with parameters like `control --volume` or `control --display` , you can use this to link to waybar modules or just easier access.
- if you have a wirless peripheral device on a desktop , they battery wont show as system battery.

> **Note:** This project is under active development. Contributions, feature requests, ideas, and testers are welcome!

## Installation ✅

### Prerequisites
Before installing, make sure you have `git` and `base-devel` installed.

### Dependencies

- **GTK 3** - UI framework
- **NetworkManager** - Wi-Fi & Ethernet management
- **BlueZ & BlueZ Utils** - Bluetooth support
- **PipeWire Pulse** - Audio control
- **Brightnessctl** - Screen brightness control
- **Power-profiles-daemon** - Battery management
- **Gammastep** - Blue light filter
- **Python Libraries** - python-gobject, python-pydbus, python3, psutil

> **Tip:** If you don't need a specific feature, you can safely omit its corresponding dependency and hide its tab in the settings.

### Installing Dependencies

#### Arch-based Distributions
> This will directly install dependencies and the app , no further steps required for arch based distros.
```
yay -S better-control-git
```

#### Debian-based Distributions
```
sudo apt update && sudo apt install -y libgtk-3-dev network-manager bluez bluez-utils pipewire-pulse brightnessctl python3-gi python3-dbus python3 python3-pydbus power-profiles-daemon python3-psutil gammastep
```

#### Fedora-based Distributions
```
sudo dnf install -y gtk3 NetworkManager bluez bluez-utils pipewire-pulse brightnessctl python3-gobject python3-dbus python3 python3-pydbus power-profiles-daemon python3-psutil gammastep
```

#### Void Linux
```
sudo xbps-install -S gtk3 NetworkManager bluez bluez-utils pipewire-pulse brightnessctl python3-gobject python3-dbus python3-pydbus python3 power-profiles-daemon python3-psutil gammastep
```

#### Alpine Linux
```
sudo apk add gtk3 networkmanager bluez bluez-utils pipewire-pulse brightnessctl py3-gobject py3-dbus py3-pydbus python3 power-profiles-daemon py3-psutil gammastep
```

### Installation Steps
```
git clone https://github.com/quantumvoid0/better-control
cd better-control
sudo make install
sudo rm -rf ~/better-control
```

## Uninstallation ❌

### It's the same steps for every distro except arch
```
git clone https://github.com/quantumvoid0/better-control
cd better-control
sudo make uninstall
sudo rm -rf ~/better-control
```
### For arch based users 
```
yay -Rns better-control-git
```

## Compatibility 📄

Better-Control has been tested on Arch Linux with Hyprland, GNOME, and KDE Plasma. It should work on most Linux distributions with minor adjustments.

| **Category** | **Compatibility** |
|--------------|-------------------|
| **Operating System** | Linux |
| **Distributions** | Arch-based, Fedora-based, Debian-based, Void, Alpine |
| **Desktop Environments** | GNOME (tested), KDE Plasma (tested with GTK support), XFCE, LXDE/LXQT |
| **Window Managers** | Hyprland (tested), Sway, i3, Openbox, Fluxbox |
| **Display Protocol** | Wayland (recommended), X11 (partial functionality) |

> If you test Better-Control on a different setup, please share your experience in the discussions or issues section.

[![BetterControl](https://img.shields.io/badge/🐧-999999?style=for-the-badge&logo=BetterControl&label=BetterControl&labelColor=333333)](https://aur.archlinux.org/packages/better-control-git)
