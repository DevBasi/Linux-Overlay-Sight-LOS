#!/usr/bin/env python3
"""
AIM Overlay — crosshair overlay for KDE Plasma / XWayland
Stays above fullscreen XWayland apps (Wine, Stalcraft X, etc.)
"""

import sys
import json
import os
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

# ── Config ────────────────────────────────────────────────────────────────────

CONFIG_PATH = Path.home() / ".config" / "aim-overlay.json"

DEFAULTS: dict = {
    "color":         "#00FF41",
    "outline_color": "#000000",
    "style":         "dot",      # dot | cross | dot+cross | circle
    "size":          5,
    "thickness":     2,
    "gap":           4,
    "opacity":       230,
    "outline":       True,
    "enabled":       True,
}

STYLE_LABELS = ["dot", "cross", "dot+cross", "circle"]


def load_config() -> dict:
    try:
        return {**DEFAULTS, **json.loads(CONFIG_PATH.read_text())}
    except Exception:
        return dict(DEFAULTS)


def save_config(cfg: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))


# ── Overlay window ─────────────────────────────────────────────────────────────

class CrosshairOverlay(QWidget):
    def __init__(self, cfg: dict) -> None:
        super().__init__()
        self.cfg = cfg
        self._build_window()

    def _build_window(self) -> None:
        # X11BypassWindowManagerHint = override-redirect: the window bypasses KWin
        # and lives at the top of the raw X stacking order, above Wine/Proton
        # fullscreen windows which are also override-redirect.
        # A 250 ms timer keeps re-raising us whenever the game redraws its window.
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.X11BypassWindowManagerHint
            | Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        geom = QApplication.primaryScreen().geometry()
        self.setGeometry(geom)

        self._raise_timer = QTimer(self)
        self._raise_timer.timeout.connect(self.raise_)
        self._raise_timer.start(250)

    def apply(self, cfg: dict) -> None:
        self.cfg = cfg
        self.update()

    # ── paint ──────────────────────────────────────────────────────────────────

    def paintEvent(self, _event) -> None:
        if not self.cfg.get("enabled", True):
            return

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.width()  // 2
        cy = self.height() // 2

        color   = _rgba(self.cfg["color"],         self.cfg["opacity"])
        outline = _rgba(self.cfg["outline_color"], self.cfg["opacity"])
        do_ol   = self.cfg["outline"]

        style = self.cfg["style"]
        size  = self.cfg["size"]
        thick = self.cfg["thickness"]
        gap   = self.cfg["gap"]

        if style in ("dot", "dot+cross"):
            _draw_dot(p, cx, cy, size, color, outline if do_ol else None)
        if style in ("cross", "dot+cross"):
            _draw_cross(p, cx, cy, size, thick, gap, color, outline if do_ol else None)
        if style == "circle":
            _draw_circle(p, cx, cy, size, thick, color, outline if do_ol else None)

        p.end()


# ── Drawing primitives ─────────────────────────────────────────────────────────

def _rgba(hex_color: str, alpha: int) -> QColor:
    c = QColor(hex_color)
    c.setAlpha(alpha)
    return c


def _draw_dot(p: QPainter, cx, cy, r, color, outline) -> None:
    if outline:
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(outline))
        p.drawEllipse(QPoint(cx, cy), r + 1, r + 1)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(color))
    p.drawEllipse(QPoint(cx, cy), r, r)


def _draw_cross(p: QPainter, cx, cy, size, thick, gap, color, outline) -> None:
    arms = size * 5

    def lines(pen: QPen) -> None:
        p.setPen(pen)
        p.drawLine(cx - arms, cy,   cx - gap,  cy)
        p.drawLine(cx + gap,  cy,   cx + arms, cy)
        p.drawLine(cx,  cy - arms,  cx,  cy - gap)
        p.drawLine(cx,  cy + gap,   cx,  cy + arms)

    if outline:
        pen = QPen(outline, thick + 2, Qt.PenStyle.SolidLine,
                   Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        lines(pen)

    pen = QPen(color, thick, Qt.PenStyle.SolidLine,
               Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    lines(pen)


def _draw_circle(p: QPainter, cx, cy, size, thick, color, outline) -> None:
    r = size * 6
    if outline:
        p.setPen(QPen(outline, thick + 2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QPoint(cx, cy), r, r)
    p.setPen(QPen(color, thick))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawEllipse(QPoint(cx, cy), r, r)


# ── Settings dialog ────────────────────────────────────────────────────────────

class SettingsDialog(QDialog):
    def __init__(self, cfg: dict, parent=None) -> None:
        super().__init__(parent)
        self.cfg = dict(cfg)
        self.setWindowTitle("AIM Overlay — Settings")
        self.setMinimumWidth(380)
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)

        # ── Crosshair group ──
        ch_box = QGroupBox("Прицел")
        form = QFormLayout(ch_box)

        self.style_cb = QComboBox()
        self.style_cb.addItems(STYLE_LABELS)
        self.style_cb.setCurrentText(self.cfg["style"])
        form.addRow("Стиль:", self.style_cb)

        self.size_sp = QSpinBox(); self.size_sp.setRange(1, 30)
        self.size_sp.setValue(self.cfg["size"])
        form.addRow("Размер:", self.size_sp)

        self.thick_sp = QSpinBox(); self.thick_sp.setRange(1, 10)
        self.thick_sp.setValue(self.cfg["thickness"])
        form.addRow("Толщина:", self.thick_sp)

        self.gap_sp = QSpinBox(); self.gap_sp.setRange(0, 20)
        self.gap_sp.setValue(self.cfg["gap"])
        form.addRow("Зазор:", self.gap_sp)

        root.addWidget(ch_box)

        # ── Color group ──
        col_box = QGroupBox("Цвет")
        col_form = QFormLayout(col_box)

        self.color_btn = _make_swatch(self.cfg["color"])
        self.color_btn.clicked.connect(
            lambda: self._pick("color", self.color_btn))
        col_form.addRow("Цвет:", self.color_btn)

        self.outline_chk = QCheckBox("Обводка")
        self.outline_chk.setChecked(self.cfg["outline"])
        col_form.addRow("", self.outline_chk)

        self.outline_btn = _make_swatch(self.cfg["outline_color"])
        self.outline_btn.clicked.connect(
            lambda: self._pick("outline_color", self.outline_btn))
        col_form.addRow("Цвет обводки:", self.outline_btn)

        root.addWidget(col_box)

        # ── Opacity group ──
        op_box = QGroupBox("Прозрачность")
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

        # ── Buttons ──
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _pick(self, key: str, btn: QPushButton) -> None:
        c = QColorDialog.getColor(
            QColor(self.cfg[key]), self, "Выбор цвета",
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


# ── Tray icon ──────────────────────────────────────────────────────────────────

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


# ── Tray controller ────────────────────────────────────────────────────────────

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
        status = "вкл" if self.cfg["enabled"] else "выкл"
        self.tray.setToolTip(f"AIM Overlay [{status}]")

    def _build_menu(self) -> None:
        menu = QMenu()

        self._toggle_act = QAction("Выключить", menu)
        self._toggle_act.triggered.connect(self._toggle)
        menu.addAction(self._toggle_act)

        settings_act = QAction("Настройки…", menu)
        settings_act.triggered.connect(self._open_settings)
        menu.addAction(settings_act)

        menu.addSeparator()

        quit_act = QAction("Выход", menu)
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
            "Включить" if not self.cfg["enabled"] else "Выключить"
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


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    # Force XWayland so _NET_WM_WINDOW_TYPE tricks work above Wine fullscreen
    if "WAYLAND_DISPLAY" in os.environ and "QT_QPA_PLATFORM" not in os.environ:
        os.environ["QT_QPA_PLATFORM"] = "xcb"

    app = QApplication(sys.argv)
    app.setApplicationName("AIM Overlay")
    app.setQuitOnLastWindowClosed(False)

    cfg     = load_config()
    overlay = CrosshairOverlay(cfg)
    overlay.show()

    _tray = TrayController(overlay, cfg)  # keep alive

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
