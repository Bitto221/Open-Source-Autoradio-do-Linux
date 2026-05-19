import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QGridLayout,
    QLabel, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QSize, Qt, QTimer, QDateTime

import style
import app_launcher

BASE_DIR = os.path.dirname(__file__)
ICON_PATH = os.path.join(BASE_DIR, "icons")
WALLPAPER_DIR = os.path.join(BASE_DIR, "wallpapers")

APPS = [
    {"file": "music_player.py", "icon": "music_player.png"},
    {"file": "youtube.py", "icon": "youtube.png"},
    {"file": "youtube_music.py", "icon": "youtube_music.png"},
    {"file": "FM_radio.py", "icon": "fm.png"},

    {"file": "video.py", "icon": "vlc.png"},
    {"file": "DAB.py", "icon": "dab.png"},
    {"file": "weather.py", "icon": "weather.png"},
    {"file": "web.py", "icon": "browser.png"},

    {"file": "settings.py", "icon": "settings.png"},
    {"file": "themes.py", "icon": "themes.png"},
    {"file": "map.py", "icon": "map.png"},
    {"file": "navigace.py", "icon": "navigation.png"},
]


class Launcher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Launcher")
        self.setFixedSize(800, 480)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet(f"""
        QWidget#central {{
            background-image: url("{style.WALLPAPER}");
            background-repeat: no-repeat;
            background-position: center;
        }}
        QWidget {{
            background: transparent;
        }}
        """)

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        central = QWidget()
        central.setObjectName("central")
        central.setAttribute(Qt.WA_StyledBackground, True)

        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(20, 20, 20, 0)

        grid = QGridLayout()
        grid.setSpacing(25)

        cols = 4
        for index, app in enumerate(APPS):
            row = index // cols
            col = index % cols

            btn = QPushButton()
            btn.setIcon(QIcon(os.path.join(ICON_PATH, app["icon"])))
            btn.setIconSize(QSize(96, 96))
            btn.setFixedSize(120, 120)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 40);
                    border-radius: 20px;
                }
            """)
            btn.clicked.connect(lambda checked, f=app["file"]: self.launch_app(f))

            grid.addWidget(btn, row, col, alignment=Qt.AlignCenter)

        central_layout.addLayout(grid)
        central_layout.addStretch()

        bottom_bar = QWidget()
        bottom_bar.setFixedHeight(40)
        bottom_bar.setStyleSheet("background-color: black;")

        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(15, 0, 15, 0)

        self.date_label = QLabel()
        self.date_label.setFont(QFont("Arial", 14))
        self.date_label.setStyleSheet("color: white;")

        self.time_label = QLabel()
        self.time_label.setFont(QFont("Arial", 16))
        self.time_label.setStyleSheet("color: white;")

        bottom_layout.addWidget(self.date_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.time_label)

        main_layout.addWidget(central)
        main_layout.addWidget(bottom_bar)

        timer = QTimer(self)
        timer.timeout.connect(self.update_datetime)
        timer.start(1000)
        self.update_datetime()

    def update_datetime(self):
        now = QDateTime.currentDateTime()
        self.date_label.setText(now.toString("dd.MM.yyyy"))
        self.time_label.setText(now.toString("HH:mm"))

    def launch_app(self, file):

        window_titles = {

            "music_player.py": "Music Player",
            "DAB.py": "DAB",
            "web.py": "Web",
            "themes.py": "Themes",
            "youtube.py": "YouTube",
            "youtube_music.py": "YouTube Music",
            "video.py": "Video Player",
            "weather.py": "Weather",
            "FM_radio.py": "FM Radio",
            "map.py": "Maps",
            "settings.py": "Settings",
            "navigation.py": "Navigation"

        }

        title = window_titles.get(file, file)

        app_launcher.app_run_or_focus(

            title,

            [
                sys.executable,
                os.path.join(BASE_DIR, file)
            ]
    )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = Launcher()
    launcher.show()
    sys.exit(app.exec_())

# hotový kod
# verze 5.2