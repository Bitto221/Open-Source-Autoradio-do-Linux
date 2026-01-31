import sys
import json
import requests
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QHBoxLayout, QFrame
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt

API_KEY = "4e51d8b7ce09f005478ff9f2fe9411c0"
CITY = "Prague"
CACHE_FILE = "weather_cache.json"

BG = "#000000"
CARD = "#111111"
ACCENT = "#6a4df4"
TEXT = "#ffffff"
SUB = "#aaaaaa"


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 480)
        self.setStyleSheet(f"background-color: {BG};")
        self.init_ui()
        self.load_weather()

    def init_ui(self):
        main = QVBoxLayout()
        main.setSpacing(15)

        title = QLabel("Počasí")
        title.setFont(QFont("Arial", 40, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {ACCENT};")
        main.addWidget(title)

        self.time = QLabel("")
        self.time.setAlignment(Qt.AlignCenter)
        self.time.setStyleSheet(f"color: {SUB};")
        main.addWidget(self.time)

        card = QFrame()
        card.setStyleSheet(f"""
            background-color: {CARD};
            border-radius: 24px;
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)

        self.icon = QLabel(alignment=Qt.AlignCenter)

        self.temp = QLabel("-- °C")
        self.temp.setFont(QFont("Arial", 42))
        self.temp.setAlignment(Qt.AlignCenter)
        self.temp.setStyleSheet(f"color: {TEXT};")

        self.desc = QLabel("")
        self.desc.setAlignment(Qt.AlignCenter)
        self.desc.setStyleSheet(f"color: {SUB};")

        info = QHBoxLayout()
        self.humidity = QLabel()
        self.wind = QLabel()
        for lbl in (self.humidity, self.wind):
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"color: {TEXT};")
            info.addWidget(lbl)

        card_layout.addWidget(self.icon)
        card_layout.addWidget(self.temp)
        card_layout.addWidget(self.desc)
        card_layout.addLayout(info)

        main.addWidget(card)
        self.setLayout(main)

    def save_cache(self, data):
        data["_cached_at"] = datetime.now().strftime("%d.%m.%Y %H:%M")
        with open(CACHE_FILE, "w") as f:
            json.dump(data, f)

    def load_weather(self):
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={CITY}&appid={API_KEY}&units=metric&lang=cs"
        )

        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            data = r.json()
            self.save_cache(data)
            self.time.setText(f"Aktualizováno {data['_cached_at']}")
        except:
            try:
                with open(CACHE_FILE) as f:
                    data = json.load(f)
                self.time.setText(
                    f"Offline – poslední data {data['_cached_at']}"
                )
            except:
                self.desc.setText("Počasí není dostupné")
                return

        self.update_ui(data)

    def update_ui(self, data):
        self.temp.setText(f"{data['main']['temp']:.1f} °C")
        self.desc.setText(data['weather'][0]['description'])
        self.humidity.setText(f"Vlhkost {data['main']['humidity']} %")
        self.wind.setText(f"Vítr {data['wind']['speed']} m/s")

        icon = data['weather'][0]['main'].lower()
        file = {
            "clear": "clear.png",
            "clouds": "clouds.png",
            "rain": "rain.png",
            "snow": "snow.png"
        }.get(icon, "clouds.png")

        pix = QPixmap(f"icons/weather/{file}")
        self.icon.setPixmap(
            pix.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = WeatherApp()
    win.show()
    sys.exit(app.exec_())
