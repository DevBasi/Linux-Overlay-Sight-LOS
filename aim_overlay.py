
"""
LOS — Linux Overlay Sight · crosshair overlay for KDE Plasma / XWayland
Stays above fullscreen XWayland apps (Wine, Stalcraft X, etc.)
"""

import sys
import json
import os
import locale
import ctypes
import ctypes.util
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
    "cursor_lock":   False,
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
        "win_title":        "LOS — Настройки",
        "grp_cross":        "Прицел",
        "grp_color":        "Цвет",
        "grp_opacity":      "Прозрачность",
        "lbl_style":        "Стиль:",
        "lbl_size":         "Размер:",
        "lbl_thick":        "Толщина:",
        "lbl_gap":          "Зазор:",
        "lbl_color":        "Цвет:",
        "lbl_outline":      "Обводка",
        "lbl_ol_col":       "Цвет обводки:",
        "pick_color":       "Выбор цвета",
        "disable":          "Выключить",
        "enable":           "Включить",
        "settings":         "Настройки…",
        "quit":             "Выход",
        "status_on":        "вкл",
        "status_off":       "выкл",
        "cursor_lock_on":   "Блокировать курсор на экране",
        "cursor_lock_off":  "Разблокировать курсор",
        "cursor_lock_na":   "Блокировка курсора (недоступно)",
    },
    "en": {
        "win_title":        "LOS — Settings",
        "grp_cross":        "Crosshair",
        "grp_color":        "Color",
        "grp_opacity":      "Opacity",
        "lbl_style":        "Style:",
        "lbl_size":         "Size:",
        "lbl_thick":        "Thickness:",
        "lbl_gap":          "Gap:",
        "lbl_color":        "Color:",
        "lbl_outline":      "Outline",
        "lbl_ol_col":       "Outline color:",
        "pick_color":       "Pick color",
        "disable":          "Disable",
        "enable":           "Enable",
        "settings":         "Settings…",
        "quit":             "Quit",
        "status_on":        "on",
        "status_off":       "off",
        "cursor_lock_on":   "Lock cursor to screen",
        "cursor_lock_off":  "Unlock cursor",
        "cursor_lock_na":   "Lock cursor (unavailable)",
    },
}

def T(key: str) -> str:
    return _S[LANG].get(key, key)


def load_config() -> dict:
    try:
        return {**DEFAULTS, **json.loads(CONFIG_PATH.read_text())}
    except Exception:
        return dict(DEFAULTS)


def save_config(cfg: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))



class CursorLocker:
    """Keeps the cursor within the primary screen using XTestFakeMotionEvent.

    XWarpPointer from an unfocused/transparent window can be silently ignored by
    KWin on Wayland. XTest synthetic events are a different path: KWin treats them
    as real hardware input and forwards them through the Wayland pointer pipeline,
    so the cursor actually moves regardless of who has focus or an active grab.

    Reads position via XQueryPointer (reliable on XWayland), moves via XTest,
    checks at ~60 Hz.
    """

    _INTERVAL_MS = 16

    def __init__(self) -> None:
        self._timer = QTimer()
        self._timer.timeout.connect(self._clamp)
        self._bounds: tuple[int, int, int, int] | None = None
        self._display = None
        self._root: int = 0
        self._libX11 = None
        self._libXtst = None
        self.available = False
        self._init()

    def _init(self) -> None:
        try:
            libX11 = ctypes.CDLL(ctypes.util.find_library("X11") or "libX11.so.6")
            libX11.XOpenDisplay.restype  = ctypes.c_void_p
            libX11.XOpenDisplay.argtypes = [ctypes.c_char_p]
            libX11.XDefaultRootWindow.restype  = ctypes.c_ulong
            libX11.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
            libX11.XFlush.restype  = ctypes.c_int
            libX11.XFlush.argtypes = [ctypes.c_void_p]
            libX11.XQueryPointer.restype = ctypes.c_int

            display_name = os.environ.get("DISPLAY", ":0").encode()
            display = libX11.XOpenDisplay(display_name)
            if not display:
                return
            self._display = display
            self._root    = libX11.XDefaultRootWindow(display)
            self._libX11  = libX11

            libXtst = ctypes.CDLL(ctypes.util.find_library("Xtst") or "libXtst.so.6")
            libXtst.XTestFakeMotionEvent.restype  = ctypes.c_int
            libXtst.XTestFakeMotionEvent.argtypes = [
                ctypes.c_void_p,  
                ctypes.c_int,    
                ctypes.c_int,     
                ctypes.c_int,     
                ctypes.c_ulong,   
            ]
            self._libXtst = libXtst
            self.available = True
        except Exception:
            pass

    def _cursor_pos(self) -> tuple[int, int] | None:
        if not self._libX11 or not self._display:
            return None
        root_ret = ctypes.c_ulong()
        child_ret = ctypes.c_ulong()
        root_x = ctypes.c_int()
        root_y = ctypes.c_int()
        win_x  = ctypes.c_int()
        win_y  = ctypes.c_int()
        mask   = ctypes.c_uint()
        self._libX11.XQueryPointer(
            self._display, self._root,
            ctypes.byref(root_ret), ctypes.byref(child_ret),
            ctypes.byref(root_x),   ctypes.byref(root_y),
            ctypes.byref(win_x),    ctypes.byref(win_y),
            ctypes.byref(mask),
        )
        return root_x.value, root_y.value

    def lock(self, x: int, y: int, w: int, h: int) -> bool:
        self._bounds = (x, y, x + w - 1, y + h - 1)
        self._timer.start(self._INTERVAL_MS)
        return True

    def unlock(self) -> None:
        self._timer.stop()
        self._bounds = None

    def _clamp(self) -> None:
        if self._bounds is None:
            return
        xmin, ymin, xmax, ymax = self._bounds
        pos = self._cursor_pos()
        if pos is None:
            return
        px, py = pos
        nx = max(xmin, min(xmax, px))
        ny = max(ymin, min(ymax, py))
        if nx != px or ny != py:
            self._libXtst.XTestFakeMotionEvent(self._display, 0, nx, ny, 0)
            self._libX11.XFlush(self._display)



class CrosshairOverlay(QWidget):
    def __init__(self, cfg: dict) -> None:
        super().__init__()
        self.cfg = cfg
        self._build_window()

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
        self.setGeometry(geom)

        self._raise_timer = QTimer(self)
        self._raise_timer.timeout.connect(self.raise_)
        self._raise_timer.start(250)

    def apply(self, cfg: dict) -> None:
        self.cfg = cfg
        self.update()


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
    def __init__(self, overlay: CrosshairOverlay, cfg: dict, locker: CursorLocker) -> None:
        self.overlay = overlay
        self.cfg = cfg
        self._locker = locker
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

        self._toggle_act = QAction(T("disable"), menu)
        self._toggle_act.triggered.connect(self._toggle)
        menu.addAction(self._toggle_act)

        if self._locker.available:
            lock_label = (T("cursor_lock_off")
                          if self.cfg.get("cursor_lock", False)
                          else T("cursor_lock_on"))
            self._lock_act = QAction(lock_label, menu)
        else:
            self._lock_act = QAction(T("cursor_lock_na"), menu)
            self._lock_act.setEnabled(False)
        self._lock_act.triggered.connect(self._toggle_cursor_lock)
        menu.addAction(self._lock_act)

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

    def _toggle_cursor_lock(self) -> None:
        self.cfg["cursor_lock"] = not self.cfg.get("cursor_lock", False)
        if self.cfg["cursor_lock"]:
            geom = QApplication.primaryScreen().geometry()
            self._locker.lock(geom.x(), geom.y(), geom.width(), geom.height())
            self._lock_act.setText(T("cursor_lock_off"))
        else:
            self._locker.unlock()
            self._lock_act.setText(T("cursor_lock_on"))
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

    locker = CursorLocker()
    if cfg.get("cursor_lock", False) and locker.available:
        geom = QApplication.primaryScreen().geometry()
        locker.lock(geom.x(), geom.y(), geom.width(), geom.height())

    app.aboutToQuit.connect(locker.unlock)

    _tray = TrayController(overlay, cfg, locker)  # keep alive

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
