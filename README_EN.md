<div align="center">

<img src="assets/linux-overlay-sight-256.png" alt="Linux Overlay Sight" width="128" height="128">

# Linux Overlay Sight

**Crosshair overlay for Linux · KDE Plasma · XWayland**

Draws a crosshair on top of any game — including fullscreen mode via Wine/Proton

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.4%2B-41CD52?style=flat-square&logo=qt&logoColor=white)](https://pypi.org/project/PyQt6)
[![Platform](https://img.shields.io/badge/Platform-Linux-FCC624?style=flat-square&logo=linux&logoColor=black)](https://kernel.org)
[![DE](https://img.shields.io/badge/KDE_Plasma-Wayland%20%2F%20X11-1D99F3?style=flat-square&logo=kde&logoColor=white)](https://kde.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[🇺🇸 **English**] · [🇷🇺 **Русский**](README.md)

</div>

---

## Why

Some games don't show a crosshair in certain situations — shooters, third-person MMOs. A physical sticker on the monitor is ugly. LOS is a software alternative: an invisible OS-level window with a crosshair exactly at the screen center.

Works above **fullscreen** games via Wine / Proton on **XWayland** — where most other solutions break.

---

## Features

| | |
|---|---|
| 🎯 **4 crosshair styles** | dot · cross · dot+cross · circle |
| 🎨 **Color** | any HEX, separate outline color |
| 🔆 **Opacity** | slider 50–255 |
| 📐 **Size / thickness / gap** | fine-tuning for each parameter |
| 🖱️ **System tray** | quick toggle via double click |
| 💾 **Auto-save** | settings written to `~/.config/los.json` |
| 👻 **Click-through** | mouse clicks pass through, game controls as normal |
| 🖥️ **Multi-monitor safe** | game pointer no longer escapes to a second monitor |

---

## Installation

### 🅰 Arch / CachyOS / Manjaro (AUR)

```bash
# stable
yay -S linux-overlay-sight

# bleeding edge (latest commit on main)
yay -S linux-overlay-sight-git
```

### 🅱 AppImage (any distribution)

```bash
wget https://github.com/DevBasi/Linux-Overlay-Sight-LOS/releases/latest/download/linux-overlay-sight-x86_64.AppImage
chmod +x linux-overlay-sight-*.AppImage
./linux-overlay-sight-*.AppImage
```

### 🅲 pip / pipx

```bash
pipx install linux-overlay-sight
linux-overlay-sight
```

### 🅳 From source (development)

```bash
git clone https://github.com/DevBasi/Linux-Overlay-Sight-LOS.git
cd Linux-Overlay-Sight-LOS
./setup.sh
./run.sh
```

---

## Requirements

- Linux with **KDE Plasma** (Wayland + XWayland recommended) or any X11 DE
- **Python 3.9+**
- **PyQt6 ≥ 6.4**
- Game running through **Wine / Proton** (XWayland window)

> GNOME / Hyprland / sway may work, but it's tested on KDE Plasma 6.

---

## Usage

After install, the command `linux-overlay-sight` (or the short alias `los`) is on `PATH`, and a launcher appears in the application menu.

```bash
linux-overlay-sight         # GUI
linux-overlay-sight --help
linux-overlay-sight --version
```

A crosshair icon appears in the system tray. The crosshair is immediately visible on screen.

### Tray controls

| Action | Result |
|---|---|
| Double-click | Toggle crosshair on / off |
| Right click → Settings… | Open settings panel |
| Right click → Quit | Close the application |

---

## Settings

<img width="770" height="638" alt="settings" src="https://github.com/user-attachments/assets/9a685d31-b838-4ab5-ba52-beab08a77f7a" />

- **Style** — dot / cross / dot+cross / circle
- **Size** — dot radius or line length
- **Thickness** — line width (for crosses and circle)
- **Gap** — center offset (for crosses)
- **Color / Outline** — clickable swatch → color picker
- **Opacity** — from semi-transparent to fully opaque

All changes apply instantly and save automatically to `~/.config/los.json`.

---

## FAQ

<details>
<summary><b>Will I get banned?</b></summary>

**Technically — unlikely.**

The game's anti-cheat runs *inside* Wine as a Windows process. It only sees the Wine environment: DLLs, game memory, Windows API. Our overlay is a Linux process with an X11 window. From the anti-cheat's perspective it **doesn't exist**: no DLL injection, no render hook, no memory reading.

That said, always check the specific game's ToS.

</details>

<details>
<summary><b>Cursor escapes to a second monitor</b></summary>

Fixed in 1.0.0: the overlay is now a small (400×400) centered window that no longer breaks the game's pointer grab. If you still see the issue, please file a bug with `kwin_wayland --version`.

</details>

<details>
<summary><b>Doesn't work on pure Wayland without XWayland</b></summary>

Native Wayland without XWayland is unsupported — there's no equivalent of `WindowTransparentForInput` + `X11BypassWindowManagerHint`. Make sure XWayland is active (default on KDE Plasma).

</details>

<details>
<summary><b>Where are settings stored?</b></summary>

```
~/.config/los.json
```

Edit manually or delete to reset to defaults. The path follows `$XDG_CONFIG_HOME` and can be overridden via `--config PATH`.

</details>

---

## Project structure

```
.
├── aim_overlay.py                       # entire app (~450 lines, single file)
├── pyproject.toml                       # package definition (hatchling)
├── setup.sh / run.sh                    # dev scripts (venv)
├── assets/
│   ├── linux-overlay-sight.svg          # vector icon
│   └── linux-overlay-sight-*.png        # raster icons 16…512 px
├── packaging/
│   ├── linux-overlay-sight.desktop      # menu launcher
│   ├── aur/PKGBUILD                     # stable AUR
│   ├── aur-git/PKGBUILD                 # AUR -git
│   └── appimage/build.sh                # AppImage build script
└── .github/workflows/                   # CI + release automation
```

---

## Publishing guide

This is a step-by-step playbook for cutting a release and pushing it to AUR, GitHub Releases and PyPI.

### 0 · One-time setup

| Channel | Setup |
|---|---|
| **PyPI**   | On PyPI, configure a **trusted publisher** that points at this GitHub repo's `release.yml` (project: `linux-overlay-sight`, env: `pypi`). No tokens needed. |
| **AUR**    | Create AUR account, upload your SSH pubkey, then `git clone ssh://aur@aur.archlinux.org/linux-overlay-sight.git` (and the same for `-git`). |
| **GitHub** | The `release.yml` workflow uses `GITHUB_TOKEN` — already provisioned. |

### 1 · Bump the version

Edit both:

* `pyproject.toml` — `version = "X.Y.Z"`
* `aim_overlay.py` — `__version__ = "X.Y.Z"`

Commit:

```bash
git add pyproject.toml aim_overlay.py
git commit -m "Release vX.Y.Z"
```

### 2 · Tag and push

```bash
git tag vX.Y.Z
git push origin main vX.Y.Z
```

The push triggers `.github/workflows/release.yml`, which:

1. Builds the **wheel + sdist** (`python -m build`).
2. Builds the **AppImage** (`packaging/appimage/build.sh`).
3. Creates a **GitHub Release** with all artifacts and auto-generated notes.
4. Publishes the wheel and sdist to **PyPI** via the trusted publisher.

### 3 · Update AUR

After the GitHub release exists, the tarball URL is stable. Update the AUR packages:

```bash
# 1. Update PKGBUILD in this repo (sync version)
sed -i 's/^pkgver=.*/pkgver=X.Y.Z/' packaging/aur/PKGBUILD

# 2. Compute the new tarball sha256 and patch sha256sums=()
url="https://github.com/DevBasi/Linux-Overlay-Sight-LOS/archive/refs/tags/vX.Y.Z.tar.gz"
sha=$(curl -sL "$url" | sha256sum | cut -d' ' -f1)
sed -i "s/^sha256sums=.*/sha256sums=('$sha')/" packaging/aur/PKGBUILD

# 3. Push to the AUR repo (separate git remote)
cp packaging/aur/PKGBUILD     ~/aur/linux-overlay-sight/PKGBUILD
cd ~/aur/linux-overlay-sight
makepkg --printsrcinfo > .SRCINFO
makepkg -si      # local test build
git add PKGBUILD .SRCINFO
git commit -m "Update to X.Y.Z"
git push
```

`linux-overlay-sight-git` doesn't need version bumps — its `pkgver()` runs from `HEAD` on each rebuild. Push it once, that's it.

### 4 · Verify

* AppImage runs on a clean Ubuntu/Fedora VM.
* `pipx install linux-overlay-sight` from PyPI installs the new version.
* `yay -S linux-overlay-sight` upgrades cleanly.

---

## License

[MIT](LICENSE) — do whatever you want.
