import sys
import os
import vlc

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QFileDialog, QSlider, QHBoxLayout, QVBoxLayout
)
from PyQt5.QtCore import Qt, QTimer

import style


class MusicPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("mainWindow")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.vlc_instance = vlc.Instance("--no-video", "--quiet")
        self.player = self.vlc_instance.media_player_new()
        self.player.audio_set_volume(100)

        page_title = QLabel("HUDBA")
        page_title.setObjectName("subtitle")
        page_title.setAlignment(Qt.AlignCenter)

        self.title = QLabel("Vyberte skladbu")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setObjectName("title")
        self.title.setWordWrap(True)

        self.add_btn = QPushButton("＋")
        self.add_btn.setObjectName("add")
        self.add_btn.setToolTip("Vybrat / změnit skladbu")

        self.play_btn = QPushButton("▶")
        self.pause_btn = QPushButton("⏸")
        self.stop_btn = QPushButton("■")

        self.progress = QSlider(Qt.Horizontal)
        self.progress.setRange(0, 1000)

        top = QHBoxLayout()
        top.addWidget(page_title)
        top.addStretch()
        top.addWidget(self.add_btn)

        controls = QHBoxLayout()
        controls.setSpacing(20)
        controls.addStretch()
        controls.addWidget(self.play_btn)
        controls.addWidget(self.pause_btn)
        controls.addWidget(self.stop_btn)
        controls.addStretch()

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(30, 20, 30, 20)
        self.layout.addLayout(top)
        self.layout.addStretch()
        self.layout.addWidget(self.title)
        self.layout.addStretch()
        self.layout.addWidget(self.progress)
        self.layout.addLayout(controls)

        self.setLayout(self.layout)

        self.add_btn.clicked.connect(self.select_song)
        self.play_btn.clicked.connect(self.player.play)
        self.pause_btn.clicked.connect(self.player.pause)
        self.stop_btn.clicked.connect(self.player.stop)
        self.progress.sliderMoved.connect(self.set_position)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(400)

        self.setStyleSheet(style.stylesheet())

    def select_song(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("Audio (*.mp3 *.wav *.ogg *.flac)")
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setFixedSize(800, 480)

        if dialog.exec_():
            file = dialog.selectedFiles()[0]
            self.load_song(file)

    def load_song(self, file):
        media = self.vlc_instance.media_new(file)
        self.player.set_media(media)
        self.title.setText(os.path.basename(file))
        self.player.play()

    def update_progress(self):
        if self.player.is_playing():
            length = self.player.get_length()
            if length > 0:
                pos = self.player.get_time() / length
                self.progress.setValue(int(pos * 1000))

    def set_position(self, value):
        self.player.set_position(value / 1000)

    def stop_playback(self):
        """Called by the shell when leaving the page / closing the app."""
        try:
            self.player.stop()
        except Exception:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicPlayer()
    window.setWindowTitle("Music Player")
    window.setFixedSize(800, 480)
    window.setWindowFlags(Qt.Window)
    window.show()
    sys.exit(app.exec_())

# hotový kod
# verze 8.0
