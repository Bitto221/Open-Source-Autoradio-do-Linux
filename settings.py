import sys
import subprocess
import shutil

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QSlider, QGroupBox
)
from PyQt5.QtCore import Qt

import style


class Settings(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setFixedSize(800, 480)
        self.setObjectName("mainWindow")
        self.setStyleSheet(style.stylesheet())
        self.init_ui()

    def init_ui(self):
        main = QVBoxLayout()

        title = QLabel("Nastavení systému")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("title")
        main.addWidget(title)

        main.addWidget(self.wifi_section())
        main.addWidget(self.bluetooth_section())
        main.addWidget(self.audio_section())
        main.addWidget(self.system_section())

        self.setLayout(main)

    def section_box(self, title):
        box = QGroupBox(title)
        layout = QVBoxLayout()
        box.setLayout(layout)
        return box

    def wifi_section(self):
        box = self.section_box("Wi-Fi")

        btn = QPushButton("Otevřít nastavení Wi-Fi")
        btn.clicked.connect(self.open_wifi_settings)

        box.layout().addWidget(btn)
        return box

    def open_wifi_settings(self):
        if shutil.which("nm-connection-editor"):
            subprocess.Popen(["nm-connection-editor"])
        else:
            print("Chybí nm-connection-editor (sudo apt install network-manager-gnome)")

    def bluetooth_section(self):
        box = self.section_box("Bluetooth")

        btn = QPushButton("Otevřít nastavení Bluetooth")
        btn.clicked.connect(self.open_bluetooth_settings)

        box.layout().addWidget(btn)
        return box

    def open_bluetooth_settings(self):
        if shutil.which("blueman-manager"):
            subprocess.Popen(["blueman-manager"])
        else:
            print("Chybí blueman (sudo apt install blueman)")

    def audio_section(self):
        box = self.section_box("Zvuk")

        volume = QSlider(Qt.Horizontal)
        volume.setRange(0, 100)
        volume.setValue(70)
        volume.valueChanged.connect(self.set_volume)

        box.layout().addWidget(volume)
        return box

    def set_volume(self, value):
        if shutil.which("pactl"):
            subprocess.Popen([
                "pactl", "set-sink-volume",
                "@DEFAULT_SINK@", f"{value}%"
            ])
        else:
            print("Chybí pactl (pulseaudio-utils nebo pipewire-pulse)")

    def system_section(self):
        box = self.section_box("Systém")

        btn = QPushButton("Go to Linux")
        btn.clicked.connect(self.go_to_linux)

        box.layout().addWidget(btn)
        return box

    def go_to_linux(self):
        subprocess.Popen(["pkill", "-f", "main.py"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Settings()
    win.show()
    sys.exit(app.exec_())