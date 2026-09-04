import sys
import os
import json
import subprocess

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QToolButton, QFrame,
    QVBoxLayout, QHBoxLayout, QSlider, QLabel
)
from PyQt5.QtCore import Qt, QTimer

import style

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRESETS_FILE = os.path.join(BASE_DIR, "fm_presets.json")
MAX_PRESETS = 6


def load_presets():
    try:
        with open(PRESETS_FILE) as f:
            data = json.load(f)
            return [float(x) for x in data][:MAX_PRESETS]
    except Exception:
        return []


def save_presets(presets):
    try:
        with open(PRESETS_FILE, "w") as f:
            json.dump(presets, f)
    except Exception:
        pass


class FmRadio(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("mainWindow")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.process = None
        self.audio = None
        self.freq = 100.2
        self.is_playing = False
        self.presets = load_presets()

        self.freq_timer = QTimer()
        self.freq_timer.setSingleShot(True)
        self.freq_timer.setInterval(500)
        self.freq_timer.timeout.connect(self._restart_if_playing)

        page_title = QLabel("FM RÁDIO")
        page_title.setObjectName("subtitle")
        page_title.setAlignment(Qt.AlignCenter)

        self.label = QLabel(f"{self.freq:.1f} MHz")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setObjectName("title")
        self.label.setFont(style.digital_font(52))

        lcd = QFrame()
        lcd.setObjectName("lcdPanel")
        lcd_layout = QVBoxLayout(lcd)
        lcd_layout.setContentsMargins(20, 14, 20, 14)
        lcd_layout.addWidget(self.label)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(880, 1080)
        self.slider.setValue(int(self.freq * 10))
        self.slider.valueChanged.connect(self.change_freq)

        self.play_btn = QPushButton("▶  Play")
        self.stop_btn = QPushButton("■  Stop")
        self.play_btn.clicked.connect(self.start_radio)
        self.stop_btn.clicked.connect(self.stop_radio)

        self.save_btn = QPushButton("💾  Uložit stanici")
        self.save_btn.setObjectName("ghost")
        self.save_btn.clicked.connect(self.save_current_preset)

        self.delete_btn = QPushButton("🗑")
        self.delete_btn.setObjectName("ghost")
        self.delete_btn.setToolTip("Smazat uloženou stanici na této frekvenci")
        self.delete_btn.clicked.connect(self.delete_current_preset)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(16)
        btn_row.addWidget(self.play_btn)
        btn_row.addWidget(self.stop_btn)
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.delete_btn)

        presets_label = QLabel("OBLÍBENÉ STANICE")
        presets_label.setObjectName("label")
        presets_label.setAlignment(Qt.AlignCenter)

        self.preset_row = QHBoxLayout()
        self.preset_row.setSpacing(10)
        self.preset_buttons = []
        for i in range(MAX_PRESETS):
            btn = QToolButton()
            btn.setObjectName("preset")
            btn.setFixedSize(88, 46)
            btn.clicked.connect(lambda checked, idx=i: self.preset_clicked(idx))
            self.preset_buttons.append(btn)
            self.preset_row.addWidget(btn)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 16, 30, 16)
        layout.addWidget(page_title)
        layout.addStretch()
        layout.addWidget(lcd)
        layout.addWidget(self.slider)
        layout.addStretch()
        layout.addLayout(btn_row)
        layout.addSpacing(14)
        layout.addWidget(presets_label)
        layout.addLayout(self.preset_row)
        self.setLayout(layout)
        self.setStyleSheet(style.stylesheet())

        self.refresh_presets()

    # ------------------------------------------------------------------
    # playback
    # ------------------------------------------------------------------

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
            self.play_btn.setText("▶  Hraje")

        except FileNotFoundError as e:
            print(f"[CHYBA] Příkaz nenalezen: {e}")
        except Exception as e:
            print(f"[CHYBA] Nepodařilo se spustit rádio: {e}")

    def stop_radio(self):
        self.is_playing = False
        self.play_btn.setText("▶  Play")

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
        self.refresh_presets()

    def _restart_if_playing(self):
        if self.is_playing:
            self.start_radio()

    # ------------------------------------------------------------------
    # presets
    # ------------------------------------------------------------------

    def preset_clicked(self, index):
        if index < len(self.presets):
            freq = self.presets[index]
            self.slider.setValue(int(round(freq * 10)))
        elif index == len(self.presets):
            # tapped the empty "add" slot - save the current frequency
            self.save_current_preset()

    def save_current_preset(self):
        freq = round(self.freq, 1)
        if freq in self.presets:
            return
        if len(self.presets) >= MAX_PRESETS:
            return
        self.presets.append(freq)
        self.presets.sort()
        save_presets(self.presets)
        self.refresh_presets()

    def delete_current_preset(self):
        freq = round(self.freq, 1)
        if freq in self.presets:
            self.presets.remove(freq)
            save_presets(self.presets)
            self.refresh_presets()

    def refresh_presets(self):
        current = round(self.freq, 1)
        for i, btn in enumerate(self.preset_buttons):
            if i < len(self.presets):
                freq = self.presets[i]
                btn.setText(f"{freq:.1f}")
                btn.setEnabled(True)
                btn.setProperty("active", freq == current)
            else:
                btn.setText("＋" if i == len(self.presets) else "—")
                btn.setEnabled(i == len(self.presets))
                btn.setProperty("active", False)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        can_save = (current not in self.presets) and len(self.presets) < MAX_PRESETS
        self.save_btn.setEnabled(can_save)
        self.delete_btn.setEnabled(current in self.presets)

    def closeEvent(self, event):
        self.stop_radio()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = FmRadio()
    w.setWindowTitle("FM Radio")
    w.setFixedSize(800, 480)
    w.setWindowFlags(Qt.Window)
    w.show()
    sys.exit(app.exec_())
