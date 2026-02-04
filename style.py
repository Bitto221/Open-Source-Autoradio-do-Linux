# style.py
from PyQt5.QtGui import QFont

# BARVY
BG = "#000000"
CARD = "#1c1c28"
PRIMARY = "#6a4df4"
TEXT = "#ffffff"
SUBTEXT = "#b0b0b0"

# FONTY
def title_font():
    return QFont("Arial", 36, QFont.Bold)

def normal_font():
    return QFont("Arial", 14)

# STYLESHEET
def stylesheet():
    return f"""
    QWidget {{
        background-color: {BG};
        color: {TEXT};
        font-family: Arial;
    }}

    QLabel#title {{
        font-size: 36px;
        font-weight: bold;
    }}

    QLabel#label {{
        font-size: 14px;
        color: {SUBTEXT};
    }}

    QPushButton {{
        background-color: {CARD};
        border-radius: 28px;
        font-size: 22px;
        color: white;
        min-width: 56px;
        min-height: 56px;
    }}

    QPushButton:hover {{
        background-color: {PRIMARY};
    }}

    QPushButton#add {{
        background-color: {PRIMARY};
        font-size: 26px;
    }}

    QSlider::groove:horizontal {{
        height: 6px;
        background: #2a2a38;
        border-radius: 3px;
    }}

    QSlider::handle:horizontal {{
        width: 18px;
        background: {PRIMARY};
        margin: -6px 0;
        border-radius: 9px;
    }}
    """
