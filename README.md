<div align="center">

# Linux Overlay Sight

**Кроссхейр-оверлей для Linux · KDE Plasma · XWayland**

Рисует точку прицела поверх любой игры — включая полноэкранный режим через Wine/Proton

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.0%2B-41CD52?style=flat-square&logo=qt&logoColor=white)](https://pypi.org/project/PyQt6)
[![Platform](https://img.shields.io/badge/Platform-Linux-FCC624?style=flat-square&logo=linux&logoColor=black)](https://kernel.org)
[![DE](https://img.shields.io/badge/KDE_Plasma-Wayland%20%2F%20X11-1D99F3?style=flat-square&logo=kde&logoColor=white)](https://kde.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[🇷🇺 **Русский**] · [🇺🇸 **English**](README_EN.md)

</div>

---

## Зачем

Некоторые жанры (шутеры, MMO с видом от третьего лица) не показывают прицел в определённых ситуациях. AIM Overlay — программная замена: невидимое для системы окно с одним пикселем прицела ровно по центру экрана.

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
| 💾 **Автосохранение** | настройки пишутся в `~/.config/aim-overlay.json` |
| 🔒 **Изолированная среда** | venv, ничего лишнего в систему |
| 👻 **Клик-сквозь** | мышь проходит насквозь, игра управляется как обычно |

---

## Требования

- Linux с **KDE Plasma** (X11 или Wayland + XWayland)
- **Python 3.8+**
- **xprop** — обычно уже стоит (`xorg-xprop` на Arch)
- Игра запускается через **Wine / Proton** (XWayland-окно)

> На чистом X11 (без Wayland) тоже работает.

---

## Установка

```bash
git clone https://github.com/DevBasi/Linux-Overlay-Sight-LOS.git
cd Linux-Overlay-Sight-LOS
./setup.sh
```

`setup.sh` создаёт изолированный Python venv и устанавливает единственную зависимость — PyQt6. Система остаётся чистой.

---

## Запуск

```bash
./run.sh
```

В системном трее появится иконка прицела. Прицел сразу виден на экране.

### Управление из трея

| Действие | Результат |
|---|---|
| ПКМ → Настройки… | Открыть панель настроек |
| ПКМ → Выход | Закрыть приложение |

---

## Настройки

<img width="770" height="638" alt="image" src="https://github.com/user-attachments/assets/9a685d31-b838-4ab5-ba52-beab08a77f7a" />


В диалоге настроек:

- **Стиль** — выбор из 4 вариантов
- **Размер** — радиус точки или длина линий
- **Толщина** — толщина линий (для крестов и окружности)
- **Зазор** — отступ от центра (для крестов)
- **Цвет** — кликабельный swatch → color picker
- **Обводка** — тёмный контур вокруг прицела, улучшает читаемость на светлых фонах
- **Прозрачность** — от полупрозрачного до полностью непрозрачного

Все изменения применяются мгновенно и сохраняются автоматически.

<br clear="right">

---

## FAQ

<details>
<summary><b>Меня забанят?</b></summary>

**Технически — маловероятно.**

Античит игры работает *внутри* Wine как Windows-процесс. Он видит только Wine-окружение: DLL, память игры, Windows API. Наш оверлей — Linux-процесс с X11-окном. С точки зрения Windows-античита он **не существует**: нет инжекта DLL, нет хука рендера, нет чтения памяти.

Тем не менее, рекомендуется ознакомиться с правилами конкретной игры.

</details>

<details>
<summary><b>Не работает на Wayland без XWayland</b></summary>

Нативный Wayland без XWayland-прослойки не поддерживается. Убедитесь, что XWayland активен (по умолчанию включён в KDE Plasma).

</details>

<details>
<summary><b>Прицел не по центру на многомониторной конфигурации</b></summary>

Сейчас оверлей растягивается на первичный монитор. Для выбора монитора — откройте issue или PR.

</details>

<details>
<summary><b>Где хранятся настройки?</b></summary>

```
~/.config/aim-overlay.json
```

Можно редактировать вручную или удалить для сброса к дефолтам.

</details>

---

## Структура проекта

```
aim-overlay/
├── aim_overlay.py   # всё приложение (~280 строк, один файл)
├── setup.sh         # создание venv + установка PyQt6
├── run.sh           # запуск
└── .venv/           # изолированное окружение (не в git)
```

---

## Лицензия

[MIT](LICENSE) — делайте что хотите.

---

<div align="center">

</div>
