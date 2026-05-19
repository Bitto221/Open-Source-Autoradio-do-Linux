import sys
import os
import subprocess

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel
)

from PyQt5.QtCore import Qt

import style


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class ThemeSelector(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Themes")
        self.setFixedSize(800, 480)

        self.setObjectName("mainWindow")

        self.setStyleSheet(style.stylesheet())

        title = QLabel("Select Theme")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()

        layout.addWidget(title)

        # ===== TÉMATA =====

        themes = {

            "Purple": (
                "#6a4df4",
                "purple.jpg"
            ),

            "Red": (
                "#ff0033",
                "red.jpg"
            ),

            "Blue": (
                "#0099ff",
                "blue.jpg"
            ),

            "Green": (
                "#00cc66",
                "green.jpg"
            ),

            "Orange": (
                "#ff8800",
                "orange.jpg"
            ),

            "Pink": (
                "#ff00aa",
                "pink.jpg"
            )
        }

        for name, data in themes.items():

            color = data[0]

            wallpaper = os.path.join(
                style.WALLPAPER_DIR,
                data[1]
            )

            btn = QPushButton(name)

            btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 20px;
                font-size: 24px;
                padding: 18px;
            }}
            """)

            btn.clicked.connect(

                lambda checked,
                c=color,
                w=wallpaper:

                self.select_theme(c, w)
            )

            layout.addWidget(btn)

        self.setLayout(layout)

    # ===== ZMĚNA TÉMATU =====

    def select_theme(self, color, wallpaper):

        # uloží nové téma
        style.save_theme(color, wallpaper)

        # zavře starý launcher
        subprocess.run([
            "pkill",
            "-f",
            "main.py"
        ])

        # znovu spustí launcher
        subprocess.Popen([
            sys.executable,
            os.path.join(BASE_DIR, "main.py")
        ])

        # zavře themes okno
        QApplication.quit()


# ===== START =====

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = ThemeSelector()
    window.show()

    sys.exit(app.exec_())