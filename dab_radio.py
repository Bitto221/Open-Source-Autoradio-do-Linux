import sys
import os
import shutil
import subprocess
import time

import vlc

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QComboBox, QLabel,
    QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QTimer

import style

try:
    import requests
except Exception:
    requests = None

WEB_PORT = 7979
BASE_URL = f"http://127.0.0.1:{WEB_PORT}"

# Standard Band III DAB/DAB+ channel raster (ETSI) - a fixed broadcasting
# standard, the same list everywhere, not something that needs updating
# per country/region.
CHANNELS = [
    f"{n}{letter}"
    for n in range(5, 13)
    for letter in "ABCD"
] + [f"13{letter}" for letter in "ABCDEF"]


class DabRadio(QWidget):
    """Own DAB/DAB+ tuner UI, backed by `welle-cli` (welle.io's headless
    CLI) instead of reimplementing DAB demodulation - that's serious DSP
    (OFDM, Reed-Solomon, MPEG decode) that a rewrite here couldn't
    realistically match. welle-cli does the demodulation and exposes a
    small web server (station list as JSON, one MP3 stream URL per
    station); this page just talks to that, the same way weather.py
    talks to an HTTP API and music_player.py plays audio via VLC.

    Shares the RTL-SDR dongle with FM Rádio - only one of the two can
    actually be demodulating at a time. Like FM Rádio, playback keeps
    running in the background when you switch to another page (that's
    intentional - a car radio doesn't stop when you open a menu) and
    only stops when Stop is pressed or the app closes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("mainWindow")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.process = None
        self.current_sid = None
        self._poll_attempts = 0

        try:
            self.vlc_instance = vlc.Instance("--no-video", "--quiet")
            self.player = self.vlc_instance.media_player_new()
        except Exception:
            self.vlc_instance = None
            self.player = None

        subtitle = QLabel("DAB")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        self.channel_box = QComboBox()
        self.channel_box.addItems(CHANNELS)
        self.channel_box.setCurrentText("12C")

        self.tune_btn = QPushButton("🔍  Vyhledat stanice")
        self.stop_btn = QPushButton("■  Stop")

        top = QHBoxLayout()
        top.addWidget(subtitle)

        tune_row = QHBoxLayout()
        tune_row.setSpacing(12)
        tune_row.addWidget(QLabel("Kanál:"))
        tune_row.addWidget(self.channel_box)
        tune_row.addWidget(self.tune_btn)
        tune_row.addWidget(self.stop_btn)

        self.status = QLabel("Vyber kanál a klepni na Vyhledat stanice")
        self.status.setObjectName("label")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setWordWrap(True)

        self.now_playing = QLabel("")
        self.now_playing.setObjectName("title")
        self.now_playing.setAlignment(Qt.AlignCenter)
        self.now_playing.setStyleSheet("font-size: 22px;")

        self.station_list = QListWidget()
        self.station_list.setObjectName("queueList")

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 16, 30, 16)
        layout.addLayout(top)
        layout.addLayout(tune_row)
        layout.addWidget(self.now_playing)
        layout.addWidget(self.status)
        layout.addWidget(self.station_list, 1)

        self.setLayout(layout)
        self.setStyleSheet(style.stylesheet())

        self.tune_btn.clicked.connect(self.start_scan)
        self.stop_btn.clicked.connect(self.stop_playback_only)
        self.station_list.itemClicked.connect(self._play_selected)

        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._poll_stations)

        self._set_playing_controls_enabled(False)

    # ------------------------------------------------------------------
    # visibility - only the station-list polling pauses when the page
    # isn't shown, same reasoning as BT Hudba. Playback itself (like FM
    # Rádio) is left running so it keeps playing while browsing other
    # pages - the whole point of a radio app.
    # ------------------------------------------------------------------

    def hideEvent(self, event):
        super().hideEvent(event)
        self.poll_timer.stop()

    # ------------------------------------------------------------------
    # tuning / station discovery
    # ------------------------------------------------------------------

    def start_scan(self):
        if requests is None:
            self.status.setText("Chybí knihovna python3-requests.")
            return

        if not shutil.which("welle-cli"):
            self.status.setText(
                "Chybí welle-cli (součást balíčku welle.io)."
            )
            return

        self._stop_welle_cli()
        self.station_list.clear()
        self.now_playing.setText("")
        self._set_playing_controls_enabled(False)

        channel = self.channel_box.currentText()
        self.status.setText(f"Ladím kanál {channel}, hledám stanice...")

        try:
            self.process = subprocess.Popen(
                ["welle-cli", "-c", channel, "-w", str(WEB_PORT)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            self.status.setText(f"[CHYBA] Nepodařilo se spustit welle-cli: {e}")
            return

        self._poll_attempts = 0
        self.poll_timer.start(2000)

    def _poll_stations(self):
        self._poll_attempts += 1

        if self.process is not None and self.process.poll() is not None:
            # welle-cli already exited - most likely the RTL-SDR dongle
            # is busy (e.g. FM Rádio is currently playing) or missing.
            self.poll_timer.stop()
            self.status.setText(
                "welle-cli neběží. Zkontroluj, že FM Rádio zrovna "
                "nehraje (obě appky sdílí stejný SDR přijímač) a že je "
                "dongle připojený."
            )
            return

        services = self._fetch_services()

        if services:
            self.poll_timer.stop()
            self.station_list.clear()
            for label, sid in services:
                item = QListWidgetItem(label)
                item.setData(Qt.UserRole, sid)
                self.station_list.addItem(item)
            self.status.setText(f"Nalezeno stanic: {len(services)}")
            return

        if self._poll_attempts >= 15:
            self.poll_timer.stop()
            self.status.setText(
                "Na tomhle kanálu se nepodařilo najít žádné stanice "
                "(slabý signál nebo prázdný kanál). Zkus jiný kanál."
            )

    def _fetch_services(self):
        try:
            r = requests.get(f"{BASE_URL}/mux.json", timeout=2)
            r.raise_for_status()
            data = r.json()
        except Exception:
            return []

        raw = data.get("services") or data.get("service") or []
        out = []
        for s in raw:
            sid = (
                s.get("sid") or s.get("id")
                or s.get("SId") or s.get("serviceId")
            )
            label = s.get("label") or s.get("name") or s.get("Label")
            if sid is not None and label:
                out.append((str(label).strip(), str(sid)))
        return out

    # ------------------------------------------------------------------
    # playback
    # ------------------------------------------------------------------

    def _play_selected(self, item):
        if self.player is None:
            self.status.setText("Chybí knihovna python3-vlc.")
            return

        sid = item.data(Qt.UserRole)
        self.current_sid = sid
        url = f"{BASE_URL}/mp3/{sid}"

        media = self.vlc_instance.media_new(url)
        self.player.set_media(media)
        self.player.play()

        self.now_playing.setText(item.text())
        self.status.setText("▶  Přehrává se")
        self._set_playing_controls_enabled(True)

    def stop_playback_only(self):
        """Stops audio playback but leaves welle-cli (and the station
        list) running, so you can pick a different station without
        re-scanning the channel."""
        if self.player is not None:
            self.player.stop()
        self.now_playing.setText("")
        self.status.setText("■  Zastaveno")

    def _stop_welle_cli(self):
        if self.player is not None:
            try:
                self.player.stop()
            except Exception:
                pass

        if self.process is not None:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            except Exception:
                pass
            self.process = None

    def _set_playing_controls_enabled(self, enabled):
        self.stop_btn.setEnabled(enabled)

    def stop_playback(self):
        """Called when the app itself is closing - releases the SDR
        dongle and the welle-cli process, unlike leaving this page for
        another one (see hideEvent above), which intentionally keeps
        DAB playing in the background."""
        self._stop_welle_cli()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DabRadio()
    window.setWindowTitle("DAB")
    window.setFixedSize(800, 480)
    window.show()
    sys.exit(app.exec_())

# hotový kod
# verze 1.0 - vlastní DAB/DAB+ modul nad welle-cli (nahrazuje spouštěč
# externího welle.io GUI)
