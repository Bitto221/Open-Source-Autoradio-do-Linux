import sys

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt, QTimer

import style

try:
    import dbus
except Exception:
    dbus = None


STATUS_LABELS = {
    "playing": "▶  Přehrává se",
    "paused": "⏸  Pozastaveno",
    "stopped": "■  Zastaveno",
    "forward-seek": "⏩  Přetáčení vpřed",
    "reverse-seek": "⏪  Přetáčení vzad",
    "error": "Chyba přehrávání",
}


class BluetoothPlayer(QWidget):
    """Shows the track currently playing on a phone connected over
    Bluetooth (A2DP + AVRCP), read from BlueZ's org.bluez.MediaPlayer1
    D-Bus interface - works with any Bluetooth adapter BlueZ can see,
    including a plain USB dongle. Requires a phone actually streaming
    audio to this device (see README - párování a A2DP)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("mainWindow")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.bus = None
        self.player_path = None

        if dbus is not None:
            try:
                self.bus = dbus.SystemBus()
            except Exception:
                self.bus = None

        subtitle = QLabel("BLUETOOTH")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("lcdPanel")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(26, 20, 26, 20)
        card_layout.setSpacing(6)

        self.title = QLabel("Není připojené žádné zařízení")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setWordWrap(True)
        self.title.setStyleSheet("font-size: 24px;")

        self.artist = QLabel("")
        self.artist.setAlignment(Qt.AlignCenter)
        self.artist.setWordWrap(True)
        self.artist.setStyleSheet("color: #cccccc; font-size: 16px; background: transparent;")

        self.album = QLabel("")
        self.album.setAlignment(Qt.AlignCenter)
        self.album.setWordWrap(True)
        self.album.setStyleSheet("color: #93939f; font-size: 13px; background: transparent;")

        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setFont(style.normal_font(14))

        card_layout.addWidget(self.title)
        card_layout.addWidget(self.artist)
        card_layout.addWidget(self.album)
        card_layout.addSpacing(4)
        card_layout.addWidget(self.status)

        controls = QHBoxLayout()
        controls.setSpacing(18)
        controls.addStretch()
        self.prev_btn = QPushButton("⏮")
        self.play_btn = QPushButton("⏯")
        self.next_btn = QPushButton("⏭")
        for b in (self.prev_btn, self.play_btn, self.next_btn):
            controls.addWidget(b)
        controls.addStretch()

        self.prev_btn.clicked.connect(lambda: self._call("Previous"))
        self.play_btn.clicked.connect(self._toggle_play)
        self.next_btn.clicked.connect(lambda: self._call("Next"))

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 16, 30, 16)
        layout.addWidget(subtitle)
        layout.addStretch()
        layout.addWidget(card)
        layout.addSpacing(18)
        layout.addLayout(controls)
        layout.addStretch()
        self.setLayout(layout)
        self.setStyleSheet(style.stylesheet())

        self._set_controls_enabled(False)
        self._current_status = ""

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(1500)
        self.refresh()

    # ------------------------------------------------------------------
    # BlueZ D-Bus lookups
    # ------------------------------------------------------------------

    def _find_player(self):
        """Returns (object_path, properties_dict) for the first BlueZ
        MediaPlayer1 object found (i.e. a connected device offering
        AVRCP media info), or None if none is available right now."""
        if self.bus is None:
            return None

        try:
            manager = dbus.Interface(
                self.bus.get_object("org.bluez", "/"),
                "org.freedesktop.DBus.ObjectManager"
            )
            objects = manager.GetManagedObjects()
            for path, interfaces in objects.items():
                if "org.bluez.MediaPlayer1" in interfaces:
                    return str(path), interfaces["org.bluez.MediaPlayer1"]
        except Exception:
            pass

        return None

    def _call(self, method_name):
        if not self.player_path or self.bus is None:
            return
        try:
            player = dbus.Interface(
                self.bus.get_object("org.bluez", self.player_path),
                "org.bluez.MediaPlayer1"
            )
            getattr(player, method_name)()
        except Exception as e:
            print(f"[CHYBA] Bluetooth ovládání přehrávání selhalo: {e}")

    def _toggle_play(self):
        if self._current_status == "playing":
            self._call("Pause")
        else:
            self._call("Play")

    # ------------------------------------------------------------------
    # UI refresh
    # ------------------------------------------------------------------

    def _set_controls_enabled(self, enabled):
        for b in (self.prev_btn, self.play_btn, self.next_btn):
            b.setEnabled(enabled)

    def refresh(self):
        found = self._find_player()

        if not found:
            self.player_path = None
            self._current_status = ""
            self.title.setText("Není připojené žádné zařízení")
            self.artist.setText("")
            self.album.setText("")
            self.status.setText(
                "Spáruj telefon a spusť na něm hudbu"
                if self.bus is not None else
                ("Nelze se připojit k D-Bus" if dbus is not None else "Chybí python3-dbus")
            )
            self._set_controls_enabled(False)
            return

        path, props = found
        self.player_path = path

        track = props.get("Track", {}) or {}
        title = str(track.get("Title", "")) or "Neznámá skladba"
        artist = str(track.get("Artist", ""))
        album = str(track.get("Album", ""))
        status = str(props.get("Status", ""))

        self.title.setText(title)
        self.artist.setText(artist)
        self.album.setText(album)
        self.status.setText(STATUS_LABELS.get(status, status))
        self._current_status = status
        self._set_controls_enabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BluetoothPlayer()
    window.setWindowTitle("Bluetooth")
    window.setFixedSize(800, 480)
    window.show()
    sys.exit(app.exec_())

# hotový kod
# verze 1.0 - nahrazuje vestavěné Mapy (ty řeší Navigace/GNOME Maps)
