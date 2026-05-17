"""Linux Overlay Sight — crosshair overlay for KDE Plasma / XWayland."""

from __future__ import annotations

import argparse
import json
import locale
import os
import re
import sys
from pathlib import Path

from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import (
    QAction, QBrush, QColor, QIcon, QPainter, QPen, QPixmap,
)
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QColorDialog, QComboBox, QDialog,
    QDialogButtonBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QMenu, QMessageBox, QPushButton, QSlider, QSpinBox,
    QSystemTrayIcon, QVBoxLayout, QWidget,
)


# ─── Constants ──────────────────────────────────────────────────────

__version__ = "1.0.1"
APP_ID      = "linux-overlay-sight"

CONFIG_PATH = Path(
    os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config")
) / "los.json"

DEFAULTS: dict = {
    "color":         "#00FF41",
    "outline_color": "#000000",
    "style":         "dot",
    "size":          5,
    "thickness":     2,
    "gap":           4,
    "opacity":       230,
    "outline":       True,
    "enabled":       True,
}

STYLE_LABELS = ("dot", "cross", "dot+cross", "circle")

_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
_RANGES = {
    "size":      (1, 30),
    "thickness": (1, 10),
    "gap":       (0, 20),
    "opacity":   (50, 255),
}


# ─── i18n ───────────────────────────────────────────────────────────

def _detect_lang() -> str:
    for var in ("LANG", "LANGUAGE", "LC_ALL", "LC_MESSAGES"):
        if os.environ.get(var, "").startswith("ru"):
            return "ru"
    try:
        code = locale.getlocale()[0] or ""
        if code.startswith("ru"):
            return "ru"
    except Exception:
        pass
    return "en"


LANG = _detect_lang()

_S: dict = {
    "ru": {
        "win_title":   "LOS — Настройки",
        "grp_cross":   "Прицел",
        "grp_color":   "Цвет",
        "grp_opacity": "Прозрачность",
        "lbl_style":   "Стиль:",
        "lbl_size":    "Размер:",
        "lbl_thick":   "Толщина:",
        "lbl_gap":     "Зазор:",
        "lbl_color":   "Цвет:",
        "lbl_outline": "Обводка",
        "lbl_ol_col":  "Цвет обводки:",
        "pick_color":  "Выбор цвета",
        "disable":     "Выключить",
        "enable":      "Включить",
        "settings":    "Настройки…",
        "quit":        "Выход",
        "status_on":   "вкл",
        "status_off":  "выкл",
        "tray_missing_title": "Системный трей недоступен",
        "tray_missing_body":  "В системе не найден systray. LOS продолжит работу, но управлять через значок не получится.",
    },
    "en": {
        "win_title":   "LOS — Settings",
        "grp_cross":   "Crosshair",
        "grp_color":   "Color",
        "grp_opacity": "Opacity",
        "lbl_style":   "Style:",
        "lbl_size":    "Size:",
        "lbl_thick":   "Thickness:",
        "lbl_gap":     "Gap:",
        "lbl_color":   "Color:",
        "lbl_outline": "Outline",
        "lbl_ol_col":  "Outline color:",
        "pick_color":  "Pick color",
        "disable":     "Disable",
        "enable":      "Enable",
        "settings":    "Settings…",
        "quit":        "Quit",
        "status_on":   "on",
        "status_off":  "off",
        "tray_missing_title": "System tray unavailable",
        "tray_missing_body":  "No system tray detected. LOS will keep running, but tray controls won't be available.",
    },
}


def T(key: str) -> str:
    return _S[LANG].get(key, key)


# ─── Config ─────────────────────────────────────────────────────────

def _sanitize(cfg: dict) -> dict:
    out: dict = {}
    for k, default in DEFAULTS.items():
        v = cfg.get(k, default)
        if k in ("color", "outline_color"):
            v = v if isinstance(v, str) and _HEX_RE.match(v) else default
        elif k == "style":
            v = v if v in STYLE_LABELS else default
        elif k in ("outline", "enabled"):
            v = bool(v) if isinstance(v, bool) else default
        elif k in _RANGES:
            lo, hi = _RANGES[k]
            v = v if isinstance(v, int) and lo <= v <= hi else default
        out[k] = v
    return out


def load_config() -> dict:
    try:
        raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("config root must be an object")
    except Exception:
        return dict(DEFAULTS)
    return _sanitize(raw)


def save_config(cfg: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(_sanitize(cfg), indent=2),
        encoding="utf-8",
    )


# ─── Icons ──────────────────────────────────────────────────────────

def _app_icon() -> QIcon:
    icon = QIcon.fromTheme(APP_ID)
    if not icon.isNull():
        return icon

    here = Path(__file__).resolve().parent
    candidates = (
        here / "assets" / "linux-overlay-sight.svg",
        here / "assets" / "linux-overlay-sight.png",
        Path("/usr/share/icons/hicolor/scalable/apps/linux-overlay-sight.svg"),
        Path("/usr/share/icons/hicolor/256x256/apps/linux-overlay-sight.png"),
        Path("/usr/share/pixmaps/linux-overlay-sight.png"),
    )
    for p in candidates:
        if p.is_file():
            return QIcon(str(p))

    return _make_tray_icon(DEFAULTS["color"])


def _make_tray_icon(hex_color: str) -> QIcon:
    if not _HEX_RE.match(hex_color or ""):
        hex_color = DEFAULTS["color"]

    px = QPixmap(22, 22)
    px.fill(Qt.GlobalColor.transparent)

    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    c = QColor(hex_color)
    p.setPen(QPen(c, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))

    cx, cy = 11, 11
    p.drawLine(cx - 7, cy, cx - 2, cy)
    p.drawLine(cx + 2, cy, cx + 7, cy)
    p.drawLine(cx, cy - 7, cx, cy - 2)
    p.drawLine(cx, cy + 2, cx, cy + 7)

    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(c))
    p.drawEllipse(QPoint(cx, cy), 2, 2)
    p.end()

    return QIcon(px)


# ─── Drawing primitives ─────────────────────────────────────────────

def _draw_dot(p: QPainter, cx: int, cy: int, r: int,
              color: QColor, outline: QColor | None) -> None:
    p.setPen(Qt.PenStyle.NoPen)
    if outline is not None:
        p.setBrush(QBrush(outline))
        p.drawEllipse(QPoint(cx, cy), r + 1, r + 1)
    p.setBrush(QBrush(color))
    p.drawEllipse(QPoint(cx, cy), r, r)


def _draw_cross(p: QPainter, cx: int, cy: int, size: int, gap: int,
                pen_color: QPen, pen_outline: QPen | None) -> None:
    arms = size * 5

    def _lines() -> None:
        p.drawLine(cx - arms, cy, cx - gap,  cy)
        p.drawLine(cx + gap,  cy, cx + arms, cy)
        p.drawLine(cx, cy - arms, cx, cy - gap)
        p.drawLine(cx, cy + gap,  cx, cy + arms)

    if pen_outline is not None:
        p.setPen(pen_outline)
        _lines()
    p.setPen(pen_color)
    _lines()


def _draw_circle(p: QPainter, cx: int, cy: int, size: int,
                 pen_color: QPen, pen_outline: QPen | None) -> None:
    r = size * 6
    p.setBrush(Qt.BrushStyle.NoBrush)
    if pen_outline is not None:
        p.setPen(pen_outline)
        p.drawEllipse(QPoint(cx, cy), r, r)
    p.setPen(pen_color)
    p.drawEllipse(QPoint(cx, cy), r, r)


# ─── Overlay window ─────────────────────────────────────────────────

class CrosshairOverlay(QWidget):
    _SIDE = 400

    def __init__(self, cfg: dict) -> None:
        super().__init__()
        self.cfg = cfg
        self._color       = QColor()
        self._outline_col = QColor()
        self._pen_color   = QPen()
        self._pen_outline = QPen()
        self._build_window()
        self._rebuild_cache()

    def _build_window(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.X11BypassWindowManagerHint
            | Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        geom = QApplication.primaryScreen().geometry()
        s = self._SIDE
        self.setGeometry(
            geom.x() + (geom.width()  - s) // 2,
            geom.y() + (geom.height() - s) // 2,
            s, s,
        )

        self._raise_timer = QTimer(self)
        self._raise_timer.timeout.connect(self.raise_)
        self._raise_timer.start(1000)

    def _rebuild_cache(self) -> None:
        alpha = self.cfg["opacity"]
        thick = self.cfg["thickness"]

        self._color = QColor(self.cfg["color"])
        self._color.setAlpha(alpha)

        self._outline_col = QColor(self.cfg["outline_color"])
        self._outline_col.setAlpha(alpha)

        self._pen_color = QPen(
            self._color, thick, Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin,
        )
        self._pen_outline = QPen(
            self._outline_col, thick + 2, Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin,
        )

    def apply(self, cfg: dict) -> None:
        self.cfg = cfg
        self._rebuild_cache()
        self.update()

    def paintEvent(self, _event) -> None:
        if not self.cfg.get("enabled", True):
            return

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.width()  // 2
        cy = self.height() // 2
        style   = self.cfg["style"]
        size    = self.cfg["size"]
        gap     = self.cfg["gap"]
        outline = self.cfg["outline"]
        ol_col  = self._outline_col if outline else None
        ol_pen  = self._pen_outline if outline else None

        if style in ("dot", "dot+cross"):
            _draw_dot(p, cx, cy, size, self._color, ol_col)
        if style in ("cross", "dot+cross"):
            _draw_cross(p, cx, cy, size, gap, self._pen_color, ol_pen)
        if style == "circle":
            _draw_circle(p, cx, cy, size, self._pen_color, ol_pen)

        p.end()


# ─── Settings dialog ────────────────────────────────────────────────

def _make_swatch(hex_color: str) -> QPushButton:
    btn = QPushButton()
    btn.setFixedSize(64, 24)
    _apply_swatch(btn, hex_color)
    return btn


def _apply_swatch(btn: QPushButton, hex_color: str) -> None:
    safe = hex_color if _HEX_RE.match(hex_color or "") else DEFAULTS["color"]
    btn.setStyleSheet(
        f"background-color: {safe}; border: 1px solid #666; border-radius: 3px;"
    )


class SettingsDialog(QDialog):
    def __init__(self, cfg: dict, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.cfg = dict(cfg)
        self.setWindowTitle(T("win_title"))
        self.setMinimumWidth(380)
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.addWidget(self._cross_box())
        root.addWidget(self._color_box())
        root.addWidget(self._opacity_box())

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _cross_box(self) -> QGroupBox:
        box  = QGroupBox(T("grp_cross"))
        form = QFormLayout(box)

        self.style_cb = QComboBox()
        self.style_cb.addItems(STYLE_LABELS)
        self.style_cb.setCurrentText(self.cfg["style"])
        form.addRow(T("lbl_style"), self.style_cb)

        self.size_sp = QSpinBox(); self.size_sp.setRange(*_RANGES["size"])
        self.size_sp.setValue(self.cfg["size"])
        form.addRow(T("lbl_size"), self.size_sp)

        self.thick_sp = QSpinBox(); self.thick_sp.setRange(*_RANGES["thickness"])
        self.thick_sp.setValue(self.cfg["thickness"])
        form.addRow(T("lbl_thick"), self.thick_sp)

        self.gap_sp = QSpinBox(); self.gap_sp.setRange(*_RANGES["gap"])
        self.gap_sp.setValue(self.cfg["gap"])
        form.addRow(T("lbl_gap"), self.gap_sp)

        return box

    def _color_box(self) -> QGroupBox:
        box  = QGroupBox(T("grp_color"))
        form = QFormLayout(box)

        self.color_btn = _make_swatch(self.cfg["color"])
        self.color_btn.clicked.connect(lambda: self._pick("color", self.color_btn))
        form.addRow(T("lbl_color"), self.color_btn)

        self.outline_chk = QCheckBox(T("lbl_outline"))
        self.outline_chk.setChecked(self.cfg["outline"])
        form.addRow("", self.outline_chk)

        self.outline_btn = _make_swatch(self.cfg["outline_color"])
        self.outline_btn.clicked.connect(
            lambda: self._pick("outline_color", self.outline_btn)
        )
        form.addRow(T("lbl_ol_col"), self.outline_btn)

        return box

    def _opacity_box(self) -> QGroupBox:
        box = QGroupBox(T("grp_opacity"))
        row = QHBoxLayout(box)

        self.opacity_sl = QSlider(Qt.Orientation.Horizontal)
        self.opacity_sl.setRange(*_RANGES["opacity"])
        self.opacity_sl.setValue(self.cfg["opacity"])

        self.opacity_lbl = QLabel(str(self.cfg["opacity"]))
        self.opacity_lbl.setFixedWidth(30)
        self.opacity_sl.valueChanged.connect(
            lambda v: self.opacity_lbl.setText(str(v))
        )

        row.addWidget(self.opacity_sl)
        row.addWidget(self.opacity_lbl)
        return box

    def _pick(self, key: str, btn: QPushButton) -> None:
        c = QColorDialog.getColor(
            QColor(self.cfg[key]), self, T("pick_color"),
            QColorDialog.ColorDialogOption.DontUseNativeDialog,
        )
        if c.isValid():
            self.cfg[key] = c.name().upper()
            _apply_swatch(btn, self.cfg[key])

    def result_config(self) -> dict:
        return _sanitize({
            **self.cfg,
            "style":     self.style_cb.currentText(),
            "size":      self.size_sp.value(),
            "thickness": self.thick_sp.value(),
            "gap":       self.gap_sp.value(),
            "opacity":   self.opacity_sl.value(),
            "outline":   self.outline_chk.isChecked(),
        })


# ─── Tray ───────────────────────────────────────────────────────────

class TrayController:
    def __init__(self, overlay: CrosshairOverlay, cfg: dict) -> None:
        self.overlay = overlay
        self.cfg = cfg
        self.tray = QSystemTrayIcon()
        self._refresh_icon()
        self._build_menu()
        self.tray.show()

    def _refresh_icon(self) -> None:
        icon = _app_icon()
        if icon.isNull():
            icon = _make_tray_icon(self.cfg["color"])
        self.tray.setIcon(icon)
        status = T("status_on") if self.cfg["enabled"] else T("status_off")
        self.tray.setToolTip(f"LOS [{status}]")

    def _build_menu(self) -> None:
        menu = QMenu()

        self._toggle_act = QAction(
            T("disable") if self.cfg["enabled"] else T("enable"), menu
        )
        self._toggle_act.triggered.connect(self._toggle)
        menu.addAction(self._toggle_act)

        settings_act = QAction(T("settings"), menu)
        settings_act.triggered.connect(self._open_settings)
        menu.addAction(settings_act)

        menu.addSeparator()

        quit_act = QAction(T("quit"), menu)
        quit_act.triggered.connect(QApplication.quit)
        menu.addAction(quit_act)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_activated)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._toggle()

    def _toggle(self) -> None:
        self.cfg["enabled"] = not self.cfg["enabled"]
        self._toggle_act.setText(
            T("enable") if not self.cfg["enabled"] else T("disable")
        )
        self.overlay.apply(self.cfg)
        self._refresh_icon()
        save_config(self.cfg)

    def _open_settings(self) -> None:
        dlg = SettingsDialog(self.cfg)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.cfg = dlg.result_config()
            self.overlay.apply(self.cfg)
            self._refresh_icon()
            save_config(self.cfg)


# ─── Entry point ────────────────────────────────────────────────────

def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="linux-overlay-sight",
        description="Crosshair overlay for Linux games (KDE Plasma / XWayland).",
    )
    p.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__version__}",
    )
    p.add_argument(
        "--config", metavar="PATH", type=Path, default=None,
        help=f"override config path (default: {CONFIG_PATH})",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    if args.config is not None:
        global CONFIG_PATH
        CONFIG_PATH = args.config.expanduser().resolve()

    if "WAYLAND_DISPLAY" in os.environ and "QT_QPA_PLATFORM" not in os.environ:
        os.environ["QT_QPA_PLATFORM"] = "xcb"

    app = QApplication(sys.argv[:1])
    app.setApplicationName("LOS")
    app.setApplicationDisplayName("Linux Overlay Sight")
    app.setDesktopFileName(APP_ID)
    app.setApplicationVersion(__version__)
    app.setWindowIcon(_app_icon())
    app.setQuitOnLastWindowClosed(False)

    cfg     = load_config()
    overlay = CrosshairOverlay(cfg)
    overlay.show()

    if QSystemTrayIcon.isSystemTrayAvailable():
        _tray = TrayController(overlay, cfg)  # noqa: F841
    else:
        QMessageBox.warning(None, T("tray_missing_title"), T("tray_missing_body"))

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
