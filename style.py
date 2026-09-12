import json
import os

from PyQt5.QtGui import QFont, QFontDatabase


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SETTINGS_FILE = os.path.join(BASE_DIR, "theme_settings.json")

WALLPAPER_DIR = os.path.join(BASE_DIR, "wallpapers")


DEFAULT_COLOR = "#6a4df4"

DEFAULT_WALLPAPER = os.path.join(
    WALLPAPER_DIR,
    "purple.jpg"
)

# Central place for the theme catalogue so main.py, themes.py and anything
# else that needs it stays in sync (single source of truth).
THEMES = {
    "Purple": ("#6a4df4", "purple.jpg"),
    "Red":    ("#ff0033", "red.jpg"),
    "Blue":   ("#0099ff", "blue.jpg"),
    "Green":  ("#00cc66", "green.jpg"),
    "Orange": ("#ff8800", "orange.jpg"),
    "Pink":   ("#ff00aa", "pink.jpg"),
}


# ---------------------------------------------------------------------------
# theme persistence
# ---------------------------------------------------------------------------

def save_theme(color, wallpaper):

    data = {
        "main_color": color,
        "wallpaper": wallpaper
    }

    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f)


def load_theme():
    """Always reads theme_settings.json fresh from disk, so callers see
    the current theme even if it changed since the app started."""

    if not os.path.exists(SETTINGS_FILE):

        save_theme(
            DEFAULT_COLOR,
            DEFAULT_WALLPAPER
        )

    try:

        with open(SETTINGS_FILE, "r") as f:

            data = json.load(f)

            return {
                "color": data.get(
                    "main_color",
                    DEFAULT_COLOR
                ),

                "wallpaper": data.get(
                    "wallpaper",
                    DEFAULT_WALLPAPER
                )
            }

    except Exception:

        return {
            "color": DEFAULT_COLOR,
            "wallpaper": DEFAULT_WALLPAPER
        }


# Kept for backwards compatibility with any code importing these directly.
# They reflect the theme at *import time* - use get_color()/get_wallpaper()
# if you need the live value after a theme change.
THEME = load_theme()
MAIN_COLOR = THEME["color"]
WALLPAPER = THEME["wallpaper"]


def get_color():
    return load_theme()["color"]


def get_wallpaper():
    return load_theme()["wallpaper"]


def refresh():
    """Re-reads the theme file and updates the module level shortcuts.
    Call this after save_theme() so old-style `style.MAIN_COLOR` usages
    (and this module's own stylesheet builders) reflect the new theme."""
    global THEME, MAIN_COLOR, WALLPAPER
    THEME = load_theme()
    MAIN_COLOR = THEME["color"]
    WALLPAPER = THEME["wallpaper"]
    return THEME


# ---------------------------------------------------------------------------
# color helpers
# ---------------------------------------------------------------------------

def _clamp(v):
    return max(0, min(255, int(v)))


def hex_to_rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def rgba(color, alpha):
    r, g, b = hex_to_rgb(color)
    return f"rgba({r}, {g}, {b}, {alpha})"


def lighten(color, amount=0.35):
    """Mix a hex color with white - used for neon 'glow' accents."""
    r, g, b = hex_to_rgb(color)
    r = _clamp(r + (255 - r) * amount)
    g = _clamp(g + (255 - g) * amount)
    b = _clamp(b + (255 - b) * amount)
    return f"#{r:02x}{g:02x}{b:02x}"


def darken(color, amount=0.35):
    r, g, b = hex_to_rgb(color)
    r = _clamp(r * (1 - amount))
    g = _clamp(g * (1 - amount))
    b = _clamp(b * (1 - amount))
    return f"#{r:02x}{g:02x}{b:02x}"


# ---------------------------------------------------------------------------
# fonts - retro "digital dashboard" look with safe fallbacks
# ---------------------------------------------------------------------------

_DIGITAL_CANDIDATES = [
    "Share Tech Mono", "DSEG7 Classic", "Digital-7", "Consolas",
    "DejaVu Sans Mono", "Courier New", "Monospace"
]

_RETRO_CANDIDATES = [
    "Orbitron", "Eurostile", "Segoe UI", "Verdana", "Arial"
]


def _first_available(candidates, fallback):
    try:
        families = set(QFontDatabase().families())
    except Exception:
        return fallback
    for name in candidates:
        if name in families:
            return name
    return fallback


def digital_font(size=28, bold=True):
    family = _first_available(_DIGITAL_CANDIDATES, "Consolas")
    f = QFont(family, size, QFont.Bold if bold else QFont.Normal)
    f.setLetterSpacing(QFont.PercentageSpacing, 110)
    return f


def title_font(size=32):
    family = _first_available(_RETRO_CANDIDATES, "Arial")
    return QFont(family, size, QFont.Bold)


def normal_font(size=14):
    family = _first_available(_RETRO_CANDIDATES, "Arial")
    return QFont(family, size)


# ---------------------------------------------------------------------------
# stylesheets
# ---------------------------------------------------------------------------

def stylesheet(color=None):
    """Global stylesheet applied to every embedded page. Retro dashboard
    look: dark glass panels, neon accent borders/hover glow."""

    color = color or get_color()
    glow = lighten(color, 0.35)
    dim = rgba(color, 90)
    btn_grad = "qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #1c1c2c, stop:1 #101018)"
    btn_grad_hover = f"qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 {rgba(color, 70)}, stop:1 {rgba(color, 40)})"

    return f"""

    QWidget#mainWindow {{
        background-color: #0a0a12;
        color: #f2f2f7;
    }}

    QWidget#page {{
        background: transparent;
        color: #f2f2f7;
    }}

    QLabel {{
        color: #f2f2f7;
        background: transparent;
    }}

    QGroupBox {{
        color: {glow};
        font-size: 17px;
        font-weight: bold;
        border: 2px solid {dim};
        border-radius: 16px;
        margin-top: 14px;
        padding-top: 18px;
        background-color: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 rgba(22, 22, 36, 200), stop:1 rgba(14, 14, 22, 200));
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 14px;
        padding: 0 8px;
        color: {glow};
    }}

    QCheckBox {{
        color: #f2f2f7;
        background: transparent;
        font-size: 16px;
    }}

    QComboBox {{
        color: white;
        background-color: #14141f;
        border: 1px solid {dim};
        border-radius: 10px;
        padding: 6px;
    }}

    QComboBox QAbstractItemView {{
        background-color: #14141f;
        color: #f2f2f7;
        border: 1px solid {dim};
        selection-background-color: {color};
        selection-color: #0a0a12;
        outline: none;
    }}

    QLabel#title {{
        font-size: 34px;
        font-weight: bold;
        color: {glow};
        background: transparent;
    }}

    QLabel#subtitle {{
        font-size: 16px;
        color: {rgba('#ffffff', 170)};
        background: transparent;
        letter-spacing: 2px;
    }}

    QLabel#label {{
        font-size: 14px;
        color: #cfcfe0;
        background: transparent;
    }}

    QFrame#lcdPanel {{
        background-color: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 #060609, stop:1 #0e0e16);
        border: 2px solid {dim};
        border-radius: 20px;
    }}

    QPushButton {{
        background-color: {btn_grad};
        border: 1px solid {dim};
        border-radius: 24px;
        font-size: 20px;
        color: #f2f2f7;
        min-width: 52px;
        min-height: 52px;
        padding: 4px 10px;
    }}

    QPushButton:hover {{
        background-color: {btn_grad_hover};
        border: 1px solid {glow};
    }}

    QPushButton:pressed {{
        background-color: {color};
        color: #0a0a12;
    }}

    QPushButton:disabled {{
        background-color: #121218;
        border: 1px solid #23232f;
        color: #55556a;
    }}

    QPushButton#add {{
        background-color: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 {glow}, stop:1 {color});
        border: none;
        color: #0a0a12;
        font-size: 24px;
        font-weight: bold;
    }}

    QPushButton#add:hover {{
        background-color: {glow};
    }}

    QPushButton#openfile {{
        background-color: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 {glow}, stop:1 {color});
        border: none;
        color: #0a0a12;
        border-radius: 20px;
        font-size: 19px;
        font-weight: bold;
    }}

    QPushButton#openfile:hover {{
        background-color: {glow};
    }}

    QPushButton#ghost {{
        background: transparent;
        border: 1px solid {dim};
    }}

    QPushButton#ghost:hover {{
        border: 1px solid {glow};
        background-color: rgba(255,255,255,12);
    }}

    QSlider::groove:horizontal {{
        height: 6px;
        background: #1a1a24;
        border-radius: 3px;
    }}

    QSlider::sub-page:horizontal {{
        height: 6px;
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {color}, stop:1 {glow});
        border-radius: 3px;
    }}

    QSlider::handle:horizontal {{
        width: 20px;
        background: {glow};
        margin: -8px 0;
        border-radius: 10px;
        border: 2px solid #0a0a12;
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
    }}

    QScrollBar::handle:vertical {{
        background: {dim};
        border-radius: 4px;
    }}

    QToolButton#preset {{
        background-color: {btn_grad};
        border: 1px solid {dim};
        border-radius: 12px;
        color: #cfcfe0;
        font-size: 13px;
        font-weight: bold;
    }}

    QToolButton#preset:hover {{
        border: 1px solid {glow};
    }}

    QToolButton#preset:disabled {{
        color: #4d4d5e;
        border: 1px dashed {dim};
        background-color: transparent;
    }}

    QToolButton#preset[active="true"] {{
        background-color: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 {glow}, stop:1 {color});
        color: #0a0a12;
        border: 1px solid {glow};
    }}

    QListWidget#queueList {{
        background-color: rgba(10, 10, 18, 210);
        border: 1px solid {dim};
        border-radius: 14px;
        color: #e8e8f0;
        font-size: 14px;
        padding: 4px;
    }}

    QListWidget#queueList::item {{
        padding: 6px 10px;
        border-radius: 8px;
    }}

    QListWidget#queueList::item:selected {{
        background-color: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 {glow}, stop:1 {color});
        color: #0a0a12;
        font-weight: bold;
    }}

    QListWidget#queueList::item:hover:!selected {{
        background-color: rgba(255,255,255,18);
    }}
    """


def shell_stylesheet(wallpaper=None):
    """Background for the persistent app shell (wallpaper behind the
    status bar / stack / dock)."""
    wallpaper = wallpaper or get_wallpaper()
    wallpaper = wallpaper.replace("\\", "/")

    return f"""
    QWidget#shellBackground {{
        background-color: #05050a;
        background-image: url("{wallpaper}");
        background-repeat: no-repeat;
        background-position: center;
    }}
    QWidget#shellOverlay {{
        background-color: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 rgba(3, 3, 8, 150),
            stop:0.12 rgba(3, 3, 8, 60),
            stop:0.85 rgba(3, 3, 8, 60),
            stop:1 rgba(3, 3, 8, 160));
    }}
    """


def topbar_stylesheet(color=None):
    color = color or get_color()
    glow = lighten(color, 0.35)

    return f"""
    QWidget#topBar {{
        background-color: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 rgba(10, 10, 20, 245), stop:1 rgba(6, 6, 14, 235));
        border-bottom: 2px solid {rgba(color, 200)};
    }}
    QWidget#clockChip {{
        background-color: rgba(0, 0, 0, 130);
        border: 1px solid {rgba(color, 110)};
        border-radius: 9px;
    }}
    QLabel#clock {{
        color: {glow};
        background: transparent;
    }}
    QLabel#dateLbl {{
        color: #b9b9cf;
        background: transparent;
        letter-spacing: 1px;
    }}
    QLabel#pageTitle {{
        color: #f2f2f7;
        background: transparent;
        font-weight: bold;
        letter-spacing: 3px;
    }}
    QLabel#dot {{
        color: {color};
        background: transparent;
    }}
    QToolButton#btIcon {{
        background: transparent;
        border: none;
        border-radius: 8px;
        padding: 2px;
    }}
    QToolButton#btIcon:hover {{
        background-color: {rgba(color, 60)};
    }}
    """


def dock_stylesheet(color=None):
    color = color or get_color()
    glow = lighten(color, 0.35)
    dim = rgba(color, 70)

    return f"""
    QWidget#dockBar {{
        background-color: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 rgba(10, 10, 18, 235), stop:1 rgba(6, 6, 12, 248));
        border-top: 2px solid {rgba(color, 200)};
    }}

    QToolButton#dockIcon {{
        background: transparent;
        border: 1px solid transparent;
        border-radius: 12px;
        padding: 3px;
    }}

    QToolButton#dockIcon:hover {{
        background-color: rgba(255,255,255,18);
        border: 1px solid {dim};
    }}

    QToolButton#dockIcon:checked {{
        background-color: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 {rgba(color, 85)}, stop:1 {rgba(color, 45)});
        border: 1px solid {glow};
    }}

    QToolButton#homeBtn {{
        background-color: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 {glow}, stop:1 {color});
        border: 2px solid {glow};
        border-radius: 27px;
    }}

    QToolButton#homeBtn:hover {{
        background-color: {glow};
    }}

    QToolButton#homeBtn:pressed {{
        background-color: {darken(color, 0.25)};
    }}
    """


def home_tile_stylesheet(color=None):
    color = color or get_color()
    glow = lighten(color, 0.35)
    dim = rgba(color, 60)

    return f"""
    QToolButton#tile {{
        background-color: qradialgradient(cx:0.5, cy:0.22, radius:0.9, fx:0.5, fy:0.22,
            stop:0 rgba(34, 30, 52, 200), stop:1 rgba(12, 12, 20, 195));
        border: 1px solid {dim};
        border-radius: 22px;
        color: #f2f2f7;
        font-size: 12px;
        font-weight: 600;
        padding-top: 6px;
    }}
    QToolButton#tile:hover {{
        background-color: qradialgradient(cx:0.5, cy:0.22, radius:0.9, fx:0.5, fy:0.22,
            stop:0 {rgba(color, 70)}, stop:1 rgba(20, 20, 32, 220));
        border: 1px solid {glow};
    }}
    QToolButton#tile:pressed {{
        background-color: {rgba(color, 130)};
        border: 1px solid {glow};
    }}
    """
