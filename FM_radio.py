import sys
import subprocess
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QVBoxLayout, QSlider, QLabel
)
from PyQt5.QtCore import Qt

import style

class FmRadio(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FM Radio")
        self.setFixedSize(800, 480)
        self.setWindowFlags(Qt.Window)

        self.setObjectName("mainWindow")

        self.process = None
        self.audio = None
        self.freq = 100.2

        # UI
        self.label = QLabel(f"{self.freq} MHz")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setObjectName("title")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(880, 1080)
        self.slider.setValue(int(self.freq * 10))
        self.slider.valueChanged.connect(self.change_freq)

        self.play_btn = QPushButton("Play")
        self.stop_btn = QPushButton("Stop")

        self.play_btn.clicked.connect(self.start_radio)
        self.stop_btn.clicked.connect(self.stop_radio)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.play_btn)
        layout.addWidget(self.stop_btn)
        self.setLayout(layout)

        self.setStyleSheet(style.stylesheet())

    def start_radio(self):
        self.stop_radio() # Vždy nejdřív zastavíme starý proces
        time.sleep(0.2)

        # Příkaz pro RTL-SDR Blog V4
        # -E deemp odstraní pískání, -dc odstraní šum na pozadí
        cmd = [
            "rtl_fm",
            "-f", f"{self.freq}M",
            "-M", "wfm",
            "-s", "200k",
            "-r", "48000",
            "-g", "25",
            "-E", "deemp",
            "-dc",
            "-"
        ]

        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        # Audio výstup - sjednoceno na 48kHz (pro Orange Pi lepší)
        self.audio = subprocess.Popen(
            ["aplay", "-r", "48000", "-f", "S16_LE", "-t", "raw", "-c", "1", "-B", "500000"],
            stdin=self.process.stdout
        )

    def stop_radio(self):
        if self.process:
            self.process.terminate()
            if self.audio:
                self.audio.terminate()
            
            try:
                self.process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.process.kill()
            
            self.process = None
            self.audio = None

    def change_freq(self, value):
        self.freq = value / 10
        self.label.setText(f"{self.freq} MHz")
        # Pokud rádio hraje, restartujeme ho při změně frekvence
        if self.process:
            self.start_radio()

    def closeEvent(self, event):
        self.stop_radio()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = FmRadio()
    w.show()
    sys.exit(app.exec_())
# připravený hod na test
# verze 6.34