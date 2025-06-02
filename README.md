<div align="center">

# ⚙️ Better Control

<img src="https://github.com/user-attachments/assets/3ae2383d-971b-4280-bd64-6c6c18dd05de" width="900">

### *A sleek GTK-themed control panel for Linux* 🐧

[![AUR Package](https://img.shields.io/badge/AUR-better--control--git-429768?style=flat-square&logo=archlinux&logoColor=white&labelColor=444)](https://aur.archlinux.org/packages/better-control-git)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-429768.svg?style=flat-square&logo=github&labelColor=444)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/better-ecosystem/better-control?style=flat-square&color=429768&logo=starship&labelColor=444)](https://github.com/better-ecosystem/better-control/stargazers)
[![Latest Release](https://img.shields.io/github/v/release/better-ecosystem/better-control.svg?style=flat-square&color=429768&logo=speedtest&label=latest-release&labelColor=444)](https://github.com/better-ecosystem/better-control/releases/latest)

</div>

---

> [!IMPORTANT]
> 🚧 This project is under active development. Contributions, feature requests, ideas, and testers are welcome!

---

## ✨ Features

- 🔄 Seamless integration with your desktop environment
- 📱 Modern, clean interface for system controls
- 🎚️ Quick access to common system settings and tons of features
- 🌙 Respects your system's light/dark theme settings
- 🧩 Modular design - use only what you need and remove the ones you don't use (see dependencies for more info)

<details>
<summary><b>Dependencies</b></summary>

Before installing, ensure you have `git` and `base-devel` installed.

### Core Dependencies

| Dependency | Purpose |
|------------|---------|
| **GTK 3** | UI framework |
| **Python Libraries** | python-gobject, python-dbus, python-psutil, python-setproctitle |

### Feature-Specific Dependencies

| Feature | Required Packages |
|---------|------------------|
| **Wi-Fi Management** | NetworkManager, python-qrcode |
| **Bluetooth** | BlueZ & BlueZ Utils |
| **Audio Control** | PipeWire or PulseAudio |
| **Brightness** | brightnessctl |
| **Power Management** | power-profiles-daemon, upower |
| **Blue Light Filter** | gammastep |
| **USBGuard** | USBGuard |
| **Pillow** | For QR Code on Wi-Fi |

> [!TIP]
> If you don't need a specific feature, you can safely omit its corresponding dependency and hide its tab in the settings.

</details>

---

## 💾 Installation & Uninstallation

### 🚀 Quick Install (Recommended)

The easiest way to install Better Control is using our automated installer script:

```bash
bash <(curl -s https://raw.githubusercontent.com/better-ecosystem/better-control/refs/heads/main/betterctl.sh)
```

**What this script does:**
- Uses [AUR](https://aur.archlinux.org/packages/better-control-git) for Arch-based distributions
- Uses [Makefile](https://github.com/better-ecosystem/better-control/blob/main/Makefile) for other distributions
- Automatically installs all required dependencies

> [!TIP]
> **Security conscious?** You can review the installer script [here](https://raw.githubusercontent.com/better-ecosystem/better-control/refs/heads/main/betterctl.sh) before running it.

**Supported Distributions:**
- 🔵 Arch-based (Arch, Manjaro, EndeavourOS, etc.)
- 🟠 Debian-based (Ubuntu, Linux Mint, Pop!_OS, etc.)
- 🔴 Fedora-based (Fedora, openSUSE, etc.)
- 🟢 Void Linux
- 🏔️ Alpine Linux

### 🔧 Manual Installation

For users who prefer manual installation or need more control over the process:

```bash
git clone https://github.com/better-ecosystem/better-control
cd better-control
sudo make install
```

**For Arch Linux users**, Better Control is also available on the AUR:

```bash
yay -S better-control-git
```

> [!IMPORTANT]
> When building manually, ensure you have all [dependencies](#dependencies) installed beforehand.

<details>
<summary><b>➡️ Nix/NixOS (Distro Independent) (Unofficial)</b></summary>

Better Control is available in the `nixpkgs` repository.

**On NixOS:**

```bash
nix-env -iA nixos.better-control
```

**On Non-NixOS:**

```bash
# without flakes:
nix-env -iA nixpkgs.better-control
# with flakes:
nix profile install nixpkgs#better-control
```

⚠️ **Bleeding edge (Unstable):** This flake will update to the latest commit automatically: [Better Control Flake](https://github.com/Rishabh5321/better-control-flake)

</details>

### 🔄 Updates & Uninstallation

After installation, you can manage Better Control using the `betterctl` command:

```bash
betterctl  # Interactive menu for update/uninstall options
```

---

## 🫴 Usage

Use the `control` or `better-control` command to run the GUI application. Use `control --help` or `better-control --help` to see more specific launch commands you can use with tools like waybar.

You can use `betterctl` to update or uninstall the application.

### Keybindings

| Keybinding | Action |
|------------|--------|
| `Shift + S` | Open Settings Dialog |
| `Q` or `Ctrl + Q` | Quit Application |

---

## 📚 Contribution

If you want to contribute, see [CONTRIBUTING.md](https://github.com/better-ecosystem/better-control/blob/main/CONTRIBUTING.md)

## 📄 License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) for more details.

---

## 🧪 Compatibility Matrix

Better Control has been tested on Arch Linux with Hyprland, GNOME, and KDE Plasma. It should work on most Linux distributions with minor adjustments.

<table>
  <tr>
    <th align="center" width="200">Category</th>
    <th align="center">Compatibility</th>
  </tr>
  <tr>
    <td align="center"><b>Operating System</b></td>
    <td align="center">Linux</td>
  </tr>
  <tr>
    <td align="center"><b>Distributions</b></td>
    <td align="center">Arch-based ✓ • Fedora-based ✓ • Debian-based ✓ • Void ✓ • Alpine ✓</td>
  </tr>
  <tr>
    <td align="center"><b>Desktop Environments</b></td>
    <td align="center">GNOME (tested) ✓ • KDE Plasma (tested) ✓ • XFCE • LXDE/LXQT</td>
  </tr>
  <tr>
    <td align="center"><b>Window Managers</b></td>
    <td align="center">Hyprland (tested) ✓ • Sway (tested) ✓ • i3 • Openbox • Fluxbox</td>
  </tr>
  <tr>
    <td align="center"><b>Display Protocol</b></td>
    <td align="center">Wayland (recommended) ✓ • X11 (partial functionality)</td>
  </tr>
</table>

> [!NOTE]
> If you test Better Control on a different setup, please share your experience in the discussions or issues section.

---

### Made with ❤️ for the Linux community

[Report Bug](https://github.com/better-ecosystem/better-control/issues) •
[Request Feature](https://github.com/better-ecosystem/better-control/discussions) •
[Contribute](https://github.com/better-ecosystem/better-control/tree/main?tab=readme-ov-file#--contribution)
