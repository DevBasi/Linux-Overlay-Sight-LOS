<div align="center">

# Linux Overlay Sight

**Crosshair overlay for Linux · KDE Plasma · XWayland**

Draws a crosshair on top of any game — including fullscreen mode via Wine/Proton

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.0%2B-41CD52?style=flat-square&logo=qt&logoColor=white)](https://pypi.org/project/PyQt6)
[![Platform](https://img.shields.io/badge/Platform-Linux-FCC624?style=flat-square&logo=linux&logoColor=black)](https://kernel.org)
[![DE](https://img.shields.io/badge/KDE_Plasma-Wayland%20%2F%20X11-1D99F3?style=flat-square&logo=kde&logoColor=white)](https://kde.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[🇺🇸 **English**] · [🇷🇺 **Русский**](README.md)

</div>

---

## Why

Some games don't show a crosshair in certain situations — shooters, MMORPGs with third-person view. A physical sticker on the monitor is ugly. LOS is a software alternative: an invisible OS-level window with a single crosshair point exactly at the screen center.

Works above **fullscreen** games via Wine / Proton on **XWayland** — where most other solutions break.

---

## Features

| | |
|---|---|
| 🎯 **4 crosshair styles** | dot · cross · dot+cross · circle |
| 🎨 **Color** | any HEX, separate outline color |
| 🔆 **Opacity** | slider 50–255 |
| 📐 **Size / thickness / gap** | fine-tuning for each parameter |
| 🖱️ **System tray** | quick toggle with double click |
| 💾 **Auto-save** | settings written to `~/.config/los.json` |
| 🔒 **Isolated environment** | venv, nothing extra installed system-wide |
| 👻 **Click-through** | mouse clicks pass through, game controls as normal |

---

## Requirements

- Linux with **KDE Plasma** (X11 or Wayland + XWayland)
- **Python 3.8+**
- **xprop** — usually pre-installed (`xorg-xprop` on Arch)
- Game running via **Wine / Proton** (XWayland window)

> Also works on pure X11 (without Wayland).

---

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/los.git
cd los
./setup.sh
```

`setup.sh` creates an isolated Python venv and installs the only dependency — PyQt6. Your system stays clean.

---

## Usage

```bash
./run.sh
```

A crosshair icon appears in the system tray. The crosshair is immediately visible on screen.

### Tray controls

| Action | Result |
|---|---|
| Right click → Settings… | Open settings panel |
| Right click → Quit | Close the application |

---

## Settings

<img width="770" height="638" alt="image" src="https://github.com/user-attachments/assets/9a685d31-b838-4ab5-ba52-beab08a77f7a" />

In the settings dialog:

- **Style** — choose from 4 variants
- **Size** — dot radius or line length
- **Thickness** — line width (for crosses and circle)
- **Gap** — center offset (for crosses)
- **Color** — clickable swatch → color picker
- **Outline** — dark border around the crosshair, improves readability on bright backgrounds
- **Opacity** — from semi-transparent to fully opaque

All changes apply instantly and save automatically.

---

## FAQ

<details>
<summary><b>Will I get banned?</b></summary>

**Technically — unlikely.**

The game's anti-cheat runs *inside* Wine as a Windows process. It only sees the Wine environment: DLLs, game memory, Windows API. Our overlay is a Linux process with an X11 window. From the anti-cheat's perspective it **doesn't exist**: no DLL injection, no render hook, no memory reading.

A physical crosshair sticker on your monitor gives the same effect — and nobody bans for that.

That said, always check the specific game's Terms of Service.

</details>

<details>
<summary><b>Doesn't work on Wayland without XWayland</b></summary>

Native Wayland without the XWayland layer is not supported. Make sure XWayland is active (enabled by default in KDE Plasma).

</details>

<details>
<summary><b>Crosshair is off-center on multi-monitor setups</b></summary>

The overlay currently spans the primary monitor. For monitor selection — open an issue or PR.

</details>

<details>
<summary><b>Where are settings stored?</b></summary>

```
~/.config/los.json
```

Can be edited manually or deleted to reset to defaults.

</details>

---

## Project structure

```
los/
├── aim_overlay.py   # entire app (~300 lines, single file)
├── setup.sh         # create venv + install PyQt6
├── run.sh           # launch script
└── .venv/           # isolated environment (not in git)
```

---

## License

[MIT](LICENSE) — do whatever you want.
