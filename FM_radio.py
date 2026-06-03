import sys
import subprocess
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QVBoxLayout, QSlider, QLabel
)
from PyQt5.QtCore import Qt, QTimer
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
        self.is_playing = False

        self.freq_timer = QTimer()
        self.freq_timer.setSingleShot(True)
        self.freq_timer.setInterval(500)
        self.freq_timer.timeout.connect(self._restart_if_playing)

        self.label = QLabel(f"{self.freq:.1f} MHz")
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
        self.stop_radio()

        cmd = [
            "rtl_fm",
            "-f", f"{self.freq}M",
            "-M", "wfm",
            "-s", "200k",
            "-r", "48000",
            "-g", "25",
            "-E", "deemp",
            "-"
        ]

        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )

            self.audio = subprocess.Popen(
                ["aplay", "-r", "48000", "-f", "S16_LE", "-t", "raw", "-c", "1", "-B", "500000"],
                stdin=self.process.stdout,
                stderr=subprocess.DEVNULL
            )

            self.is_playing = True
            self.play_btn.setText("▶ Hraje")

        except FileNotFoundError as e:
            print(f"[CHYBA] Příkaz nenalezen: {e}")
        except Exception as e:
            print(f"[CHYBA] Nepodařilo se spustit rádio: {e}")

    def stop_radio(self):
        self.is_playing = False
        self.play_btn.setText("Play")

        for proc in [self.audio, self.process]:
            if proc:
                try:
                    proc.terminate()
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                except Exception:
                    pass

        self.process = None
        self.audio = None

    def change_freq(self, value):
        self.freq = value / 10
        self.label.setText(f"{self.freq:.1f} MHz")
        self.freq_timer.start()

    def _restart_if_playing(self):
        if self.is_playing:
            self.start_radio()

    def closeEvent(self, event):
        self.stop_radio()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = FmRadio()
    w.show()
    sys.exit(app.exec_())