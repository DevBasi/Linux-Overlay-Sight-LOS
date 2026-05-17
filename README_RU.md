<div align="center">

<img src="assets/linux-overlay-sight-256.png" alt="Linux Overlay Sight" width="128" height="128">

# Linux Overlay Sight

**Кроссхейр-оверлей для Linux · KDE Plasma · XWayland**

Рисует точку прицела поверх любой игры — включая полноэкранный режим через Wine/Proton

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.4%2B-41CD52?style=flat-square&logo=qt&logoColor=white)](https://pypi.org/project/PyQt6)
[![Platform](https://img.shields.io/badge/Platform-Linux-FCC624?style=flat-square&logo=linux&logoColor=black)](https://kernel.org)
[![DE](https://img.shields.io/badge/KDE_Plasma-Wayland%20%2F%20X11-1D99F3?style=flat-square&logo=kde&logoColor=white)](https://kde.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[🇺🇸 **English**](README.md) · [🇷🇺 **Русский**]

</div>

---

## Зачем

Некоторые жанры (шутеры, MMO с видом от третьего лица) не показывают прицел в определённых ситуациях. Linux Overlay Sight — программная замена: невидимое для системы окно с прицелом ровно по центру экрана.

Работает поверх **полноэкранных** игр через Wine / Proton на **XWayland** — там, где большинство других решений ломается.

---

## Возможности

| | |
|---|---|
| 🎯 **4 стиля прицела** | точка · крест · точка+крест · окружность |
| 🎨 **Цвет** | любой HEX, отдельно цвет обводки |
| 🔆 **Прозрачность** | слайдер 50–255 |
| 📐 **Размер / толщина / зазор** | точная настройка каждого параметра |
| 🖱️ **Системный трей** | быстрое вкл/выкл двойным кликом |
| 💾 **Автосохранение** | настройки в `~/.config/los.json` |
| 👻 **Клик-сквозь** | мышь проходит насквозь, игра управляется как обычно |
| 🖥️ **Multi-monitor safe** | курсор игры не «утекает» на соседний монитор |

---

## Установка

### 🅰 Arch / CachyOS / Manjaro (AUR)

```bash
# stable
yay -S linux-overlay-sight

# bleeding edge (последний commit из main)
yay -S linux-overlay-sight-git
```

### 🅱 AppImage (любой дистрибутив)

```bash
wget https://github.com/DevBasi/Linux-Overlay-Sight-LOS/releases/latest/download/linux-overlay-sight-1.0.2-x86_64.AppImage
chmod +x linux-overlay-sight-*.AppImage
./linux-overlay-sight-*.AppImage
```

### 🅲 Из исходников (для разработки)

```bash
git clone https://github.com/DevBasi/Linux-Overlay-Sight-LOS.git
cd Linux-Overlay-Sight-LOS
./setup.sh
./run.sh
```

---

## Требования

- Linux с **KDE Plasma** (Wayland + XWayland — рекомендуется) или любым DE на X11
- **Python 3.9+**
- **PyQt6 ≥ 6.4**
- Игра запускается через **Wine / Proton** (XWayland-окно)

> На GNOME / Hyprland / sway работа возможна, но протестировано на KDE Plasma 6.

---

## Запуск

После установки команда `linux-overlay-sight` (или короткая `los`) появится в PATH. Также появится ярлык в меню приложений.

```bash
linux-overlay-sight        # GUI
linux-overlay-sight --help
linux-overlay-sight --version
```

В системном трее появится иконка прицела. Прицел сразу виден на экране.

### Управление из трея

| Действие | Результат |
|---|---|
| Двойной клик ЛКМ | Вкл / Выкл прицел |
| ПКМ → Настройки… | Открыть панель настроек |
| ПКМ → Выход | Закрыть приложение |

---

## Настройки

<img width="770" height="638" alt="settings" src="https://github.com/user-attachments/assets/9a685d31-b838-4ab5-ba52-beab08a77f7a" />

- **Стиль** — точка / крест / точка+крест / окружность
- **Размер** — радиус точки или длина линий
- **Толщина** — толщина линий (для крестов и окружности)
- **Зазор** — отступ от центра (для крестов)
- **Цвет / Обводка** — кликабельный swatch → color picker
- **Прозрачность** — от полупрозрачного до полностью непрозрачного

Все изменения применяются мгновенно и сохраняются автоматически в `~/.config/los.json`.

---

## FAQ

<details>
<summary><b>Меня забанят?</b></summary>

**Технически — маловероятно.**

Античит игры работает *внутри* Wine как Windows-процесс. Он видит только Wine-окружение: DLL, память игры, Windows API. Наш оверлей — Linux-процесс с X11-окном. С точки зрения Windows-античита он **не существует**: нет инжекта DLL, нет хука рендера, нет чтения памяти.

Тем не менее, ознакомьтесь с правилами конкретной игры.

</details>

<details>
<summary><b>Курсор «вылетает» на второй монитор</b></summary>

Исправлено в 1.0.0: окно оверлея теперь маленькое (400×400) по центру первичного монитора и больше не ломает pointer-grab игры. Если проблема осталась — пришлите вывод `kwin_wayland --version` в issue.

</details>

<details>
<summary><b>Не работает на чистом Wayland без XWayland</b></summary>

Нативный Wayland без XWayland не поддерживается — нет аналогов `WindowTransparentForInput` + `X11BypassWindowManagerHint`. Убедитесь, что XWayland активен (по умолчанию в KDE Plasma).

</details>

<details>
<summary><b>Где хранятся настройки?</b></summary>

```
~/.config/los.json
```

Можно редактировать вручную или удалить для сброса к дефолтам. Путь переопределяется через `$XDG_CONFIG_HOME` или флаг `--config PATH`.

</details>

---

## Структура проекта

```
.
├── aim_overlay.py                       # всё приложение (~450 строк, один файл)
├── pyproject.toml                       # описание пакета (hatchling)
├── setup.sh / run.sh                    # dev scripts (venv)
├── assets/
│   ├── linux-overlay-sight.svg          # векторная иконка
│   └── linux-overlay-sight-*.png        # растровые иконки 16…512 px
├── packaging/
│   ├── linux-overlay-sight.desktop      # ярлык для меню
│   ├── aur/PKGBUILD                     # стабильный AUR
│   ├── aur-git/PKGBUILD                 # AUR -git
│   └── appimage/build.sh                # сборка AppImage
└── .github/workflows/                   # CI + release
```

---

## Лицензия

[MIT](LICENSE) — делайте что хотите.
