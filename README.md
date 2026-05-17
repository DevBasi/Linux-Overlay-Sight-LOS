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

[🇷🇺 **Русский**] · [🇺🇸 **English**](README_EN.md)

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
wget https://github.com/DevBasi/Linux-Overlay-Sight-LOS/releases/latest/download/linux-overlay-sight-1.0.0-x86_64.AppImage
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
├── setup.sh / run.sh                    # dev-скрипты (venv)
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

## Гайд для мейнтейнеров

Полный пошаговый сценарий релиза. Релиз идёт в **два** канала: GitHub Release (AppImage) и AUR.

### 0 · Разовая настройка

| Канал | Что нужно |
|---|---|
| **GitHub Release** | Ничего — workflow использует встроенный `GITHUB_TOKEN`. |
| **AUR**            | Аккаунт + SSH-ключ (см. ниже). |

#### 0a · Аккаунт AUR и SSH-ключ (один раз, ~5 минут)

1. **Зарегься на AUR**: https://aur.archlinux.org/register/. Username любой (например `devbasi`).

2. **Сгенери SSH-ключ** если его ещё нет:

   ```bash
   # Пропусти если ~/.ssh/id_ed25519.pub уже существует
   ssh-keygen -t ed25519 -C "aur@твоя-почта.tld"
   # жми Enter на путь по умолчанию, опционально задай passphrase
   ```

   Создаётся два файла:
   - `~/.ssh/id_ed25519`      ← приватный ключ, **никому не показывай**
   - `~/.ssh/id_ed25519.pub`  ← публичный, его вставишь в AUR

3. **Скопируй публичный ключ**:

   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

   Получишь строку вида `ssh-ed25519 AAAA... aur@почта`. Скопируй всё целиком.

4. **Вставь в профиль AUR**: https://aur.archlinux.org/account/ (после логина) → поле **SSH Public Key** → вставить → **Update**.

5. **Проверь что соединение работает**:

   ```bash
   ssh aur@aur.archlinux.org help
   ```
   Должно показать help, а не «Permission denied».

6. **Клонь пустые AUR-репозитории**. AUR создаёт репо лениво — при первом push, но клонить можно сразу (просто получишь "empty repository").

   ```bash
   mkdir -p ~/aur
   cd ~/aur
   git clone ssh://aur@aur.archlinux.org/linux-overlay-sight.git
   git clone ssh://aur@aur.archlinux.org/linux-overlay-sight-git.git
   ```

### 1 · Бамп версии

В трёх файлах поправь версию:

* `pyproject.toml` — `version = "X.Y.Z"`
* `aim_overlay.py` — `__version__ = "X.Y.Z"`
* `packaging/aur/PKGBUILD` — `pkgver=X.Y.Z`

```bash
git add pyproject.toml aim_overlay.py packaging/aur/PKGBUILD
git commit -m "Release vX.Y.Z"
```

### 2 · Тег и push

```bash
git tag vX.Y.Z
git push origin main vX.Y.Z
```

Push тега триггерит `.github/workflows/release.yml`:

1. Собирается **AppImage** через `packaging/appimage/build.sh`.
2. Создаётся **GitHub Release** с AppImage и автоматическими release notes.

Прогресс: https://github.com/DevBasi/Linux-Overlay-Sight-LOS/actions.

### 3 · Push стабильного PKGBUILD в AUR

После того как GitHub Release появился (tarball-URL стал доступен):

```bash
# Посчитай sha256 архива исходников
url="https://github.com/DevBasi/Linux-Overlay-Sight-LOS/archive/refs/tags/vX.Y.Z.tar.gz"
sha=$(curl -sL "$url" | sha256sum | cut -d' ' -f1)

# Скопируй PKGBUILD и впиши sha
cp packaging/aur/PKGBUILD ~/aur/linux-overlay-sight/PKGBUILD
sed -i "s/^sha256sums=.*/sha256sums=('$sha')/" ~/aur/linux-overlay-sight/PKGBUILD

cd ~/aur/linux-overlay-sight

# Локальный тест сборки — ловит ошибки в зависимостях ДО того как их увидят юзеры
makepkg -si

# Сгенерь metadata
makepkg --printsrcinfo > .SRCINFO

# Закоммить и запушь
git add PKGBUILD .SRCINFO
git commit -m "Update to X.Y.Z"
git push
```

### 4 · `-git` пакет — один push навсегда

`linux-overlay-sight-git` не требует обновления версии — его `pkgver()` читает текущий `HEAD` из main при каждой пересборке. Зальёшь один раз:

```bash
cp packaging/aur-git/PKGBUILD ~/aur/linux-overlay-sight-git/PKGBUILD
cd ~/aur/linux-overlay-sight-git
makepkg --printsrcinfo > .SRCINFO
makepkg -si
git add PKGBUILD .SRCINFO
git commit -m "Initial import"
git push
```

После этого юзеры получают свежий commit автоматически при `yay -S linux-overlay-sight-git`.

### 5 · Проверка

* Скачай AppImage из GitHub Release, запусти на чистой VM.
* `yay -S linux-overlay-sight` — ставит новую стабильную.
* `yay -S linux-overlay-sight-git` — собирает из последнего commit.

---

## Лицензия

[MIT](LICENSE) — делайте что хотите.
