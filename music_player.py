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
    def __init__(self):
        super().__init__()

        # WINDOW
        self.setWindowTitle("Music Player")
        self.setFixedSize(800, 480)
        self.setWindowFlags(Qt.Window)

        self.vlc_instance = vlc.Instance("--no-video", "--quiet")
        self.player = self.vlc_instance.media_player_new()
        self.player.audio_set_volume(80)

        # UI
        self.title = QLabel("Select a song")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setObjectName("title")

        self.add_btn = QPushButton("＋")
        self.add_btn.setObjectName("add")

        self.play_btn = QPushButton("▶")
        self.pause_btn = QPushButton("⏸")
        self.stop_btn = QPushButton("■")

        self.progress = QSlider(Qt.Horizontal)
        self.progress.setRange(0, 1000)

        self.volume = QSlider(Qt.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(80)

        vol_label = QLabel("Volume")
        vol_label.setObjectName("label")

        # LAYOUT
        top = QHBoxLayout()
        top.addStretch()
        top.addWidget(self.add_btn)

        controls = QHBoxLayout()
        controls.setSpacing(20)
        controls.addStretch()
        controls.addWidget(self.play_btn)
        controls.addWidget(self.pause_btn)
        controls.addWidget(self.stop_btn)
        controls.addStretch()

        volume_layout = QHBoxLayout()
        volume_layout.addWidget(vol_label)
        volume_layout.addWidget(self.volume)

        self.layout = QVBoxLayout()
        self.layout.addLayout(top)
        self.layout.addStretch()
        self.layout.addWidget(self.title)
        self.layout.addStretch()
        self.layout.addWidget(self.progress)
        self.layout.addLayout(controls)
        self.layout.addLayout(volume_layout)

        self.setLayout(self.layout)

        # SIGNALS
        self.add_btn.clicked.connect(self.select_song)
        self.play_btn.clicked.connect(self.player.play)
        self.pause_btn.clicked.connect(self.player.pause)
        self.stop_btn.clicked.connect(self.player.stop)
        self.progress.sliderMoved.connect(self.set_position)
        self.volume.valueChanged.connect(self.set_volume)

        # TIMER
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(400)

        # STYLE
        self.setStyleSheet(style.stylesheet())

    # LOGIC

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

        # schovej tlačítko add
        self.add_btn.hide()

    def update_progress(self):
        if self.player.is_playing():
            length = self.player.get_length()
            if length > 0:
                pos = self.player.get_time() / length
                self.progress.setValue(int(pos * 1000))

    def set_position(self, value):
        self.player.set_position(value / 1000)

    def set_volume(self, value):
        self.player.audio_set_volume(value)


# ENTRY
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicPlayer()
    window.show()
    sys.exit(app.exec_())
# je potřea dodelat app_louncher
