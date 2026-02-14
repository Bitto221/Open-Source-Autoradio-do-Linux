from PyQt5.QtGui import QFont

# BARVY
MAIN_COLOR = "#6a4df4"

# FONTY
def title_font():
    return QFont("Arial", 36, QFont.Bold)

def normal_font():
    return QFont("Arial", 14)

# STYLESHEET
def stylesheet():
    return f"""
    QWidget {{
        background-color: "#000000";
        color: "#ffffff";
        font-family: Arial;
    }}

    QLabel#title {{
        font-size: 46px;
        font-weight: bold;
    }}

    QLabel#label {{
        font-size: 14px;
        color: "#b0b0b0";
    }}

    QPushButton {{
        background-color: "#1c1c28";
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
    QPushButton#openfile{{
        background-color: {MAIN_COLOR};
        color: white;
        border-radius: 20px;
        font-size: 20px;
    }}
    """
