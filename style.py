import json
import os

from PyQt5.QtGui import QFont


# ===== CESTY =====

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SETTINGS_FILE = os.path.join(BASE_DIR, "theme_settings.json")

WALLPAPER_DIR = os.path.join(BASE_DIR, "wallpapers")


# ===== VÝCHOZÍ =====

DEFAULT_COLOR = "#6a4df4"

DEFAULT_WALLPAPER = os.path.join(
    WALLPAPER_DIR,
    "purple.jpg"
)


# ===== ULOŽENÍ =====

def save_theme(color, wallpaper):

    data = {
        "main_color": color,
        "wallpaper": wallpaper
    }

    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f)


# ===== NAČTENÍ =====

def load_theme():

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

    except:

        return {
            "color": DEFAULT_COLOR,
            "wallpaper": DEFAULT_WALLPAPER
        }


# ===== AKTUÁLNÍ TÉMA =====

THEME = load_theme()

MAIN_COLOR = THEME["color"]

WALLPAPER = THEME["wallpaper"]


# ===== FONTY =====

def title_font():
    return QFont("Arial", 36, QFont.Bold)


def normal_font():
    return QFont("Arial", 14)


# ===== STYL =====

def stylesheet():

    return f"""

    QWidget#mainWindow {{

        background-color: black;
        border-image: url("{WALLPAPER}") 0 0 0 0 stretch stretch;
        color: white;

    }}

    QLabel {{

        color: white;
        background: transparent;

    }}

    QGroupBox {{

        color: white;
        font-size: 18px;
        font-weight: bold;
        border: 2px solid rgba(255,255,255,40);
        border-radius: 16px;
        margin-top: 12px;
        padding-top: 16px;
        background-color: rgba(0,0,0,120);

    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 14px;
        padding: 0 6px 0 6px;
        color: white;
    }}
    QCheckBox {{
        color: white;
        background: transparent;
        font-size: 18px;

    }}

    QComboBox {{
        color: white;
        background-color: #1c1c28;
        border-radius: 10px;
        padding: 6px;

    }}

    QLabel#title {{
        font-size: 46px;
        font-weight: bold;
        color: white;
        background: transparent;
    }}

    QLabel#label {{
        font-size: 14px;
        color: white;
        background: transparent;
    }}

    QPushButton {{
        background-color: #1c1c28;
        border-radius: 28px;
        font-size: 22px;
        color: white;
        min-width: 56px;
        min-height: 56px;
    }}

    QPushButton:hover {{
        background-color: {MAIN_COLOR};
    }}

    QPushButton#add {{
        background-color: {MAIN_COLOR};
        font-size: 26px;
    }}

    QPushButton#openfile {{
        background-color: {MAIN_COLOR};
        color: white;
        border-radius: 20px;
        font-size: 20px;
    }}

    QSlider::groove:horizontal {{
        height: 6px;
        background: #2a2a38;
        border-radius: 3px;
    }}

    QSlider::handle:horizontal {{
        width: 18px;
        background: {MAIN_COLOR};
        margin: -6px 0;
        border-radius: 9px;
    }}

    """