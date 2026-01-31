import sys
import os
import vlc
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QFileDialog, QSlider, QHBoxLayout, QVBoxLayout
)
from PyQt5.QtCore import Qt, QTimer


class MusicPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("OpenTune Player")
        self.setFixedSize(800, 480)

        # VLC
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.player.audio_set_volume(80)

        # UI
        self.title = QLabel("No song selected")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setObjectName("title")

        self.add_btn = QPushButton("＋")
        self.add_btn.setObjectName("add")

        self.play_btn = QPushButton("▶")
        self.pause_btn = QPushButton("⏸")
        self.stop_btn = QPushButton("■")

        for b in (self.play_btn, self.pause_btn, self.stop_btn):
            b.setObjectName("control")

        # progress
        self.progress = QSlider(Qt.Horizontal)
        self.progress.setObjectName("progress")
        self.progress.setRange(0, 1000)

        # volume
        self.volume = QSlider(Qt.Horizontal)
        self.volume.setObjectName("volume")
        self.volume.setRange(0, 100)
        self.volume.setValue(80)

        vol_label = QLabel("Volume")
        vol_label.setObjectName("label")

        # Layout
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

        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addStretch()
        layout.addWidget(self.title)
        layout.addStretch()
        layout.addWidget(self.progress)
        layout.addLayout(controls)
        layout.addLayout(volume_layout)

        self.setLayout(layout)

        # Signals
        self.add_btn.clicked.connect(self.open_file)
        self.play_btn.clicked.connect(self.player.play)
        self.pause_btn.clicked.connect(self.player.pause)
        self.stop_btn.clicked.connect(self.player.stop)
        self.progress.sliderMoved.connect(self.set_position)
        self.volume.valueChanged.connect(self.set_volume)

        # timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(400)

        self.media = None

        # STYLE
        self.setStyleSheet("""
        QWidget {
            background-color: #0f0f14;
            color: #ffffff;
            font-family: Arial;
        }

        QLabel#title {
            font-size: 28px;
            font-weight: bold;
        }

        QLabel#label {
            font-size: 14px;
            color: #b0b0b0;
        }

        QPushButton {
            background-color: #1c1c28;
            border-radius: 28px;
            font-size: 22px;
            color: white;
            min-width: 56px;
            min-height: 56px;
        }

        QPushButton:hover {
            background-color: #6a4df4;
        }

        QPushButton#add {
            background-color: #6a4df4;
            font-size: 26px;
        }

        QSlider::groove:horizontal {
            height: 6px;
            background: #2a2a38;
            border-radius: 3px;
        }

        QSlider::handle:horizontal {
            width: 18px;
            background: #6a4df4;
            margin: -6px 0;
            border-radius: 9px;
        }
        """)

    # Functions

    def open_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Select song", "", "Audio (*.mp3 *.wav *.ogg *.flac)"
        )
        if file:
            self.media = self.instance.media_new(file)
            self.player.set_media(self.media)
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

    def set_volume(self, value):
        self.player.audio_set_volume(value)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicPlayer()
    window.show()
    sys.exit(app.exec_())
