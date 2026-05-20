import sys
import json
import requests
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame
)

from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt

import style


API_KEY = "4e51d8b7ce09f005478ff9f2fe9411c0"
CITY = "Prague"

CACHE_FILE = "weather_cache.json"


class WeatherApp(QWidget):

    def __init__(self):
        super().__init__()

        # WINDOW
        self.setWindowTitle("Weather")
        self.setFixedSize(800, 480)

        self.setObjectName("mainWindow")

        # STYLE
        self.setStyleSheet(style.stylesheet())

        # UI
        self.init_ui()

        # DATA
        self.load_weather()

    # ================= UI =================

    def init_ui(self):

        main = QVBoxLayout()

        main.setSpacing(15)

        # TITLE
        title = QLabel("Počasí")

        title.setObjectName("title")

        title.setAlignment(Qt.AlignCenter)

        main.addWidget(title)

        # TIME
        self.time = QLabel("")

        self.time.setObjectName("label")

        self.time.setAlignment(Qt.AlignCenter)

        main.addWidget(self.time)

        # CARD
        card = QFrame()

        card.setStyleSheet("""
        QFrame {

            background-color: rgba(15, 15, 15, 210);

            border-radius: 24px;

        }
        """)

        card_layout = QVBoxLayout(card)

        card_layout.setSpacing(10)

        # ICON
        self.icon = QLabel()

        self.icon.setAlignment(Qt.AlignCenter)

        # TEMP
        self.temp = QLabel("-- °C")

        self.temp.setAlignment(Qt.AlignCenter)

        self.temp.setStyleSheet("""
        color: white;
        font-size: 42px;
        background: transparent;
        """)

        # DESC
        self.desc = QLabel("")

        self.desc.setAlignment(Qt.AlignCenter)

        self.desc.setStyleSheet("""
        color: #cccccc;
        font-size: 18px;
        background: transparent;
        """)

        # INFO
        info = QHBoxLayout()

        self.humidity = QLabel()

        self.wind = QLabel()

        for lbl in (self.humidity, self.wind):

            lbl.setAlignment(Qt.AlignCenter)

            lbl.setStyleSheet("""
            color: white;
            font-size: 18px;
            background: transparent;
            """)

            info.addWidget(lbl)

        # ADD
        card_layout.addWidget(self.icon)
        card_layout.addWidget(self.temp)
        card_layout.addWidget(self.desc)
        card_layout.addLayout(info)

        main.addWidget(card)

        self.setLayout(main)

    # ================= CACHE =================

    def save_cache(self, data):

        data["_cached_at"] = datetime.now().strftime(
            "%d.%m.%Y %H:%M"
        )

        with open(CACHE_FILE, "w") as f:

            json.dump(data, f)

    # ================= LOAD =================

    def load_weather(self):

        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={CITY}"
            f"&appid={API_KEY}"
            f"&units=metric"
            f"&lang=cs"
        )

        try:

            r = requests.get(url, timeout=5)

            r.raise_for_status()

            data = r.json()

            self.save_cache(data)

            self.time.setText(
                f"Aktualizováno {data['_cached_at']}"
            )

        except:

            try:

                with open(CACHE_FILE) as f:

                    data = json.load(f)

                self.time.setText(
                    f"Offline data {data['_cached_at']}"
                )

            except:

                self.desc.setText(
                    "Počasí není dostupné"
                )

                return

        self.update_ui(data)

    # ================= UPDATE =================

    def update_ui(self, data):

        self.temp.setText(
            f"{data['main']['temp']:.1f} °C"
        )

        self.desc.setText(
            data['weather'][0]['description']
        )

        self.humidity.setText(
            f"Vlhkost {data['main']['humidity']} %"
        )

        self.wind.setText(
            f"Vítr {data['wind']['speed']} m/s"
        )

        icon = data['weather'][0]['main'].lower()

        file = {

            "clear": "clear.png",
            "clouds": "clouds.png",
            "rain": "rain.png",
            "snow": "snow.png"

        }.get(icon, "clouds.png")

        pix = QPixmap(f"icons/weather/{file}")

        self.icon.setPixmap(

            pix.scaled(
                120,
                120,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )


# ================= START =================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    win = WeatherApp()

    win.show()

    sys.exit(app.exec_())
# hotovy kod
# verze 4.7