import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QSlider, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class Settings(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nastavení")
        self.setFixedSize(800, 480)
        self.setStyleSheet("background-color: #0b0b0b; color: white;")
        self.init_ui()

    def init_ui(self):
        main = QVBoxLayout()

        title = QLabel("Nastavení systému")
        title.setFont(QFont("Arial", 22))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #a855f7;")
        main.addWidget(title)

        main.addWidget(self.wifi_section())
        main.addWidget(self.bluetooth_section())
        main.addWidget(self.audio_section())
        main.addWidget(self.brightness_section())
        self.setLayout(main)

    # ---------------- WIFI ----------------
    def wifi_section(self):
        box = self.section_box("Wi-Fi")

        btn = QPushButton("Otevřít nastavení Wi-Fi")
        btn.clicked.connect(lambda: self.open_settings("wifi"))
        box.layout().addWidget(btn)

        return box

    # ---------------- BLUETOOTH ----------------
    def bluetooth_section(self):
        box = self.section_box("Bluetooth")

        btn = QPushButton("Otevřít nastavení Bluetooth")
        btn.clicked.connect(lambda: self.open_settings("bluetooth"))
        box.layout().addWidget(btn)

        return box

    # ---------------- AUDIO ----------------
    def audio_section(self):
        box = self.section_box("Zvuk")

        volume = QSlider(Qt.Horizontal)
        volume.setRange(0, 100)
        volume.setValue(70)
        volume.valueChanged.connect(self.set_volume)

        box.layout().addWidget(volume)

        return box

    # ---------------- BRIGHTNESS ----------------
    def brightness_section(self):
        box = self.section_box("Jas displeje")

        bright = QSlider(Qt.Horizontal)
        bright.setRange(10, 100)
        bright.setValue(80)
        bright.valueChanged.connect(self.set_brightness)

        box.layout().addWidget(bright)
        return box

    # ---------------- HELPERS ----------------
    def section_box(self, title):
        box = QGroupBox(title)
        box.setFont(QFont("Arial", 14))
        box.setStyleSheet("""
            QGroupBox {
                border: 1px solid #333;
                border-radius: 12px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                color: #a855f7;
            }
        """)
        layout = QVBoxLayout()
        box.setLayout(layout)
        return box

    def open_settings(self, section):
        try:
            if section == "wifi":
                subprocess.Popen(["gnome-control-center", "wifi"])
            elif section == "bluetooth":
                subprocess.Popen(["gnome-control-center", "bluetooth"])
        except:
            pass

    def set_volume(self, value):
        subprocess.Popen(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{value}%"])

    def set_brightness(self, value):
        try:
            subprocess.Popen(["brightnessctl", "set", f"{value}%"])
        except:
            pass



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Settings()
    win.show()
    sys.exit(app.exec_())