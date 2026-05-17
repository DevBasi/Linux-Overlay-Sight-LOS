
"""
LOS — Linux Overlay Sight · crosshair overlay for KDE Plasma / XWayland
Stays above fullscreen XWayland apps (Wine, Stalcraft X, etc.)
"""

import sys
import json
import os
import locale
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QWidget, QSystemTrayIcon, QMenu,
    QColorDialog, QDialog, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLabel, QPushButton, QSpinBox,
    QComboBox, QSlider, QCheckBox, QGroupBox, QDialogButtonBox,
)
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QAction, QIcon, QPixmap,
)


CONFIG_PATH = Path.home() / ".config" / "los.json"

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

STYLE_LABELS = ["dot", "cross", "dot+cross", "circle"]


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
    },
}

def T(key: str) -> str:
    return _S[LANG].get(key, key)


def load_config() -> dict:
    try:
        cfg = {**DEFAULTS, **json.loads(CONFIG_PATH.read_text())}
    except Exception:
        return dict(DEFAULTS)
    return {k: cfg[k] for k in DEFAULTS}


def save_config(cfg: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    keep = {k: cfg.get(k, DEFAULTS[k]) for k in DEFAULTS}
    CONFIG_PATH.write_text(json.dumps(keep, indent=2))



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

        ol_col = self._outline_col if outline else None
        ol_pen = self._pen_outline if outline else None

        if style in ("dot", "dot+cross"):
            _draw_dot(p, cx, cy, size, self._color, ol_col)
        if style in ("cross", "dot+cross"):
            _draw_cross(p, cx, cy, size, gap, self._pen_color, ol_pen)
        if style == "circle":
            _draw_circle(p, cx, cy, size, self._pen_color, ol_pen)

        p.end()


def _draw_dot(p: QPainter, cx, cy, r, color, outline) -> None:
    p.setPen(Qt.PenStyle.NoPen)
    if outline is not None:
        p.setBrush(QBrush(outline))
        p.drawEllipse(QPoint(cx, cy), r + 1, r + 1)
    p.setBrush(QBrush(color))
    p.drawEllipse(QPoint(cx, cy), r, r)


def _draw_cross(p: QPainter, cx, cy, size, gap, pen_color, pen_outline) -> None:
    arms = size * 5
    if pen_outline is not None:
        p.setPen(pen_outline)
        p.drawLine(cx - arms, cy, cx - gap,  cy)
        p.drawLine(cx + gap,  cy, cx + arms, cy)
        p.drawLine(cx, cy - arms, cx, cy - gap)
        p.drawLine(cx, cy + gap,  cx, cy + arms)
    p.setPen(pen_color)
    p.drawLine(cx - arms, cy, cx - gap,  cy)
    p.drawLine(cx + gap,  cy, cx + arms, cy)
    p.drawLine(cx, cy - arms, cx, cy - gap)
    p.drawLine(cx, cy + gap,  cx, cy + arms)


def _draw_circle(p: QPainter, cx, cy, size, pen_color, pen_outline) -> None:
    r = size * 6
    p.setBrush(Qt.BrushStyle.NoBrush)
    if pen_outline is not None:
        p.setPen(pen_outline)
        p.drawEllipse(QPoint(cx, cy), r, r)
    p.setPen(pen_color)
    p.drawEllipse(QPoint(cx, cy), r, r)



class SettingsDialog(QDialog):
    def __init__(self, cfg: dict, parent=None) -> None:
        super().__init__(parent)
        self.cfg = dict(cfg)
        self.setWindowTitle(T("win_title"))
        self.setMinimumWidth(380)
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)

        ch_box = QGroupBox(T("grp_cross"))
        form = QFormLayout(ch_box)

        self.style_cb = QComboBox()
        self.style_cb.addItems(STYLE_LABELS)
        self.style_cb.setCurrentText(self.cfg["style"])
        form.addRow(T("lbl_style"), self.style_cb)

        self.size_sp = QSpinBox(); self.size_sp.setRange(1, 30)
        self.size_sp.setValue(self.cfg["size"])
        form.addRow(T("lbl_size"), self.size_sp)

        self.thick_sp = QSpinBox(); self.thick_sp.setRange(1, 10)
        self.thick_sp.setValue(self.cfg["thickness"])
        form.addRow(T("lbl_thick"), self.thick_sp)

        self.gap_sp = QSpinBox(); self.gap_sp.setRange(0, 20)
        self.gap_sp.setValue(self.cfg["gap"])
        form.addRow(T("lbl_gap"), self.gap_sp)

        root.addWidget(ch_box)

        col_box = QGroupBox(T("grp_color"))
        col_form = QFormLayout(col_box)

        self.color_btn = _make_swatch(self.cfg["color"])
        self.color_btn.clicked.connect(
            lambda: self._pick("color", self.color_btn))
        col_form.addRow(T("lbl_color"), self.color_btn)

        self.outline_chk = QCheckBox(T("lbl_outline"))
        self.outline_chk.setChecked(self.cfg["outline"])
        col_form.addRow("", self.outline_chk)

        self.outline_btn = _make_swatch(self.cfg["outline_color"])
        self.outline_btn.clicked.connect(
            lambda: self._pick("outline_color", self.outline_btn))
        col_form.addRow(T("lbl_ol_col"), self.outline_btn)

        root.addWidget(col_box)

        op_box = QGroupBox(T("grp_opacity"))
        op_row = QHBoxLayout(op_box)
        self.opacity_sl = QSlider(Qt.Orientation.Horizontal)
        self.opacity_sl.setRange(50, 255)
        self.opacity_sl.setValue(self.cfg["opacity"])
        self.opacity_lbl = QLabel(str(self.cfg["opacity"]))
        self.opacity_lbl.setFixedWidth(30)
        self.opacity_sl.valueChanged.connect(
            lambda v: self.opacity_lbl.setText(str(v)))
        op_row.addWidget(self.opacity_sl)
        op_row.addWidget(self.opacity_lbl)
        root.addWidget(op_box)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _pick(self, key: str, btn: QPushButton) -> None:
        c = QColorDialog.getColor(
            QColor(self.cfg[key]), self, T("pick_color"),
            QColorDialog.ColorDialogOption.DontUseNativeDialog,
        )
        if c.isValid():
            self.cfg[key] = c.name().upper()
            _apply_swatch(btn, self.cfg[key])

    def result_config(self) -> dict:
        return {
            **self.cfg,
            "style":     self.style_cb.currentText(),
            "size":      self.size_sp.value(),
            "thickness": self.thick_sp.value(),
            "gap":       self.gap_sp.value(),
            "opacity":   self.opacity_sl.value(),
            "outline":   self.outline_chk.isChecked(),
        }


def _make_swatch(hex_color: str) -> QPushButton:
    btn = QPushButton()
    btn.setFixedSize(64, 24)
    _apply_swatch(btn, hex_color)
    return btn


def _apply_swatch(btn: QPushButton, hex_color: str) -> None:
    btn.setStyleSheet(
        f"background-color: {hex_color}; border: 1px solid #666; border-radius: 3px;"
    )



def _make_tray_icon(hex_color: str) -> QIcon:
    px = QPixmap(22, 22)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    c = QColor(hex_color)
    pen = QPen(c, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    cx, cy = 11, 11
    p.drawLine(cx - 7, cy,   cx - 2, cy)
    p.drawLine(cx + 2, cy,   cx + 7, cy)
    p.drawLine(cx, cy - 7,   cx, cy - 2)
    p.drawLine(cx, cy + 2,   cx, cy + 7)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(c))
    p.drawEllipse(QPoint(cx, cy), 2, 2)
    p.end()
    return QIcon(px)


class TrayController:
    def __init__(self, overlay: CrosshairOverlay, cfg: dict) -> None:
        self.overlay = overlay
        self.cfg = cfg
        self.tray = QSystemTrayIcon()
        self._refresh_icon()
        self._build_menu()
        self.tray.show()

    def _refresh_icon(self) -> None:
        self.tray.setIcon(_make_tray_icon(self.cfg["color"]))
        status = T("status_on") if self.cfg["enabled"] else T("status_off")
        self.tray.setToolTip(f"LOS [{status}]")

    def _build_menu(self) -> None:
        menu = QMenu()

        self._toggle_act = QAction(
            T("disable") if self.cfg["enabled"] else T("enable"), menu)
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



def main() -> None:
    if "WAYLAND_DISPLAY" in os.environ and "QT_QPA_PLATFORM" not in os.environ:
        os.environ["QT_QPA_PLATFORM"] = "xcb"

    app = QApplication(sys.argv)
    app.setApplicationName("LOS")
    app.setQuitOnLastWindowClosed(False)

    cfg     = load_config()
    overlay = CrosshairOverlay(cfg)
    overlay.show()

    _tray = TrayController(overlay, cfg)  

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
