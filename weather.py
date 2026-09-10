import sys
import os
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

from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal

import style

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

API_KEY = "4e51d8b7ce09f005478ff9f2fe9411c0"
CITY = "Prague"

CACHE_FILE = os.path.join(BASE_DIR, "weather_cache.json")


class _WeatherFetcher(QThread):
    """Does the actual HTTP request off the GUI thread - requests.get()
    blocking for up to its 5s timeout right in the middle of the app's
    main thread would freeze the whole UI the moment this page opens."""

    succeeded = pyqtSignal(dict)
    failed = pyqtSignal()

    def run(self):
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
            self.succeeded.emit(r.json())
        except Exception:
            self.failed.emit()


class WeatherApp(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("mainWindow")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(style.stylesheet())
        self._fetcher = None
        self.init_ui()
        self.load_weather()

    def init_ui(self):

        main = QVBoxLayout()
        main.setContentsMargins(24, 10, 24, 10)
        main.setSpacing(4)

        title = QLabel("POČASÍ")
        title.setObjectName("subtitle")
        title.setAlignment(Qt.AlignCenter)
        main.addWidget(title)

        self.city = QLabel(CITY)
        self.city.setObjectName("title")
        self.city.setAlignment(Qt.AlignCenter)
        self.city.setStyleSheet("font-size: 26px;")
        main.addWidget(self.city)

        self.time = QLabel("")
        self.time.setObjectName("label")
        self.time.setAlignment(Qt.AlignCenter)
        main.addWidget(self.time)

        card = QFrame()
        card.setObjectName("lcdPanel")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 10, 20, 10)
        card_layout.setSpacing(2)
        self.icon = QLabel()
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setFixedHeight(70)
        self.temp = QLabel("-- °C")
        self.temp.setAlignment(Qt.AlignCenter)
        self.temp.setFont(style.digital_font(28))

        self.temp.setStyleSheet(f"""
        color: {style.lighten(style.get_color(), 0.35)};
        background: transparent;
        """)

        self.desc = QLabel("")
        self.desc.setAlignment(Qt.AlignCenter)
        self.desc.setStyleSheet("""
        color: #cccccc;
        font-size: 15px;
        background: transparent;
        """)

        info = QHBoxLayout()
        info.setSpacing(12)
        self.humidity = QLabel()
        self.wind = QLabel()

        chip_style = f"""
        color: white;
        font-size: 13px;
        font-weight: 600;
        background-color: {style.rgba(style.get_color(), 55)};
        border: 1px solid {style.rgba(style.get_color(), 130)};
        border-radius: 12px;
        padding: 4px 14px;
        """
        for lbl in (self.humidity, self.wind):
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(chip_style)
            info.addWidget(lbl)
        info.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(self.icon)
        card_layout.addWidget(self.temp)
        card_layout.addWidget(self.desc)
        card_layout.addSpacing(2)
        card_layout.addLayout(info)
        main.addWidget(card)
        self.setLayout(main)

    def save_cache(self, data):
        data["_cached_at"] = datetime.now().strftime(
            "%d.%m.%Y %H:%M"
        )

        with open(CACHE_FILE, "w") as f:
            json.dump(data, f)

    def load_weather(self):
        # Kick off the request in the background; UI updates happen in
        # _on_fetch_succeeded/_on_fetch_failed once it's done, back on
        # the GUI thread (Qt queues the signal delivery automatically).
        if self._fetcher is not None and self._fetcher.isRunning():
            return

        self._fetcher = _WeatherFetcher(self)
        self._fetcher.succeeded.connect(self._on_fetch_succeeded)
        self._fetcher.failed.connect(self._on_fetch_failed)
        self._fetcher.start()

    def _on_fetch_succeeded(self, data):
        self.save_cache(data)
        self.time.setText(f"Aktualizováno {data['_cached_at']}")
        self.update_ui(data)

    def _on_fetch_failed(self):
        try:
            with open(CACHE_FILE) as f:
                data = json.load(f)
            self.time.setText(f"Offline data {data['_cached_at']}")
            self.update_ui(data)
        except Exception:
            self.desc.setText("Počasí není dostupné")

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
            "snow": "snow.png",
            "mist": "mist.png",
            "fog": "mist.png",
            "haze": "mist.png"
        }.get(icon, "clouds.png")

        pix = QPixmap(os.path.join(BASE_DIR, "icons", "weather", file))

        self.icon.setPixmap(
            pix.scaled(
                64,
                64,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = WeatherApp()
    win.setWindowTitle("Weather")
    win.setFixedSize(800, 480)
    win.show()
    sys.exit(app.exec_())

# hotovy kod
# verze 6.0 - síťový dotaz běží na pozadí (QThread), už neblokuje GUI
# vlákno při otevření stránky
