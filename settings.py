import sys
import subprocess
import shutil

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QSlider, QGroupBox
)
from PyQt5.QtCore import Qt, QTimer

import style
from app_launcher import open_bluetooth_manager, open_wifi_settings as _open_wifi_settings


class Settings(QWidget):
    def __init__(self, parent=None, on_exit=None):
        super().__init__(parent)
        self.setObjectName("mainWindow")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(style.stylesheet())
        # Called when the user taps "Ukončit aplikaci". Defaults to
        # closing just this Qt process; the shell can pass its own
        # callback (e.g. QApplication.quit) when embedding this page.
        self.on_exit = on_exit or QApplication.quit

        # Debounces pactl calls while the volume slider is being
        # dragged - without this, every intermediate value while
        # sliding would spawn its own subprocess.
        self._pending_volume = None
        self._volume_timer = QTimer(self)
        self._volume_timer.setSingleShot(True)
        self._volume_timer.setInterval(120)
        self._volume_timer.timeout.connect(self._apply_volume)

        self.init_ui()

    def init_ui(self):
        main = QVBoxLayout()
        main.setContentsMargins(30, 16, 30, 16)
        main.setSpacing(10)

        subtitle = QLabel("NASTAVENÍ")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        main.addWidget(subtitle)

        title = QLabel("Nastavení systému")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("title")
        main.addWidget(title)

        row1 = QHBoxLayout()
        row1.addWidget(self.wifi_section())
        row1.addWidget(self.bluetooth_section())
        main.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(self.audio_section())
        row2.addWidget(self.system_section())
        main.addLayout(row2)

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
        _open_wifi_settings()

    def bluetooth_section(self):
        box = self.section_box("Bluetooth")

        btn = QPushButton("Otevřít nastavení Bluetooth")
        btn.clicked.connect(self.open_bluetooth_settings)

        box.layout().addWidget(btn)
        return box

    def open_bluetooth_settings(self):
        open_bluetooth_manager()

    def audio_section(self):
        box = self.section_box("Zvuk")

        volume = QSlider(Qt.Horizontal)
        volume.setRange(0, 100)
        volume.setValue(70)
        volume.valueChanged.connect(self.set_volume)

        box.layout().addWidget(volume)
        return box

    def set_volume(self, value):
        # Just remember the latest value and (re)start the debounce
        # timer - _apply_volume() does the actual pactl call once the
        # slider settles, instead of once per intermediate tick.
        self._pending_volume = value
        self._volume_timer.start()

    def _apply_volume(self):
        if self._pending_volume is None:
            return
        if shutil.which("pactl"):
            subprocess.Popen([
                "pactl", "set-sink-volume",
                "@DEFAULT_SINK@", f"{self._pending_volume}%"
            ])
        else:
            print("Chybí pactl (pulseaudio-utils nebo pipewire-pulse)")

    def system_section(self):
        box = self.section_box("Systém")

        btn = QPushButton("Ukončit aplikaci")
        btn.clicked.connect(lambda: self.on_exit())

        box.layout().addWidget(btn)
        return box


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Settings()
    win.setWindowTitle("Settings")
    win.setFixedSize(800, 480)
    win.show()
    sys.exit(app.exec_())
