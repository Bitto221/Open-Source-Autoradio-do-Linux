import sys
import os
import vlc

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QToolButton,
    QFileDialog, QSlider, QHBoxLayout, QVBoxLayout, QListWidget,
    QListWidgetItem
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

        # Queue - a simple list of file paths + which one is current.
        self.queue = []
        self.current_index = -1

        page_title = QLabel("HUDBA")
        page_title.setObjectName("subtitle")
        page_title.setAlignment(Qt.AlignCenter)

        self.add_btn = QPushButton("＋")
        self.add_btn.setObjectName("add")
        self.add_btn.setToolTip("Přidat skladby do fronty")

        self.clear_btn = QPushButton("🗑")
        self.clear_btn.setObjectName("ghost")
        self.clear_btn.setToolTip("Vyprázdnit frontu")

        self.title = QLabel("Vyberte skladby")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setObjectName("title")
        self.title.setWordWrap(True)

        self.prev_btn = QPushButton("⏮")
        self.play_btn = QPushButton("▶")
        self.pause_btn = QPushButton("⏸")
        self.stop_btn = QPushButton("■")
        self.next_btn = QPushButton("⏭")

        self.progress = QSlider(Qt.Horizontal)
        self.progress.setRange(0, 1000)

        self.queue_list = QListWidget()
        self.queue_list.setObjectName("queueList")
        self.queue_list.setFixedHeight(130)

        top = QHBoxLayout()
        top.addWidget(page_title)
        top.addStretch()
        top.addWidget(self.clear_btn)
        top.addWidget(self.add_btn)

        controls = QHBoxLayout()
        controls.setSpacing(16)
        controls.addStretch()
        controls.addWidget(self.prev_btn)
        controls.addWidget(self.play_btn)
        controls.addWidget(self.pause_btn)
        controls.addWidget(self.stop_btn)
        controls.addWidget(self.next_btn)
        controls.addStretch()

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(30, 16, 30, 16)
        self.layout.addLayout(top)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.progress)
        self.layout.addLayout(controls)
        self.layout.addSpacing(6)
        self.layout.addWidget(self.queue_list)

        self.setLayout(self.layout)

        self.add_btn.clicked.connect(self.select_songs)
        self.clear_btn.clicked.connect(self.clear_queue)
        self.prev_btn.clicked.connect(self.play_previous)
        self.play_btn.clicked.connect(self.player.play)
        self.pause_btn.clicked.connect(self.player.pause)
        self.stop_btn.clicked.connect(self.player.stop)
        self.next_btn.clicked.connect(lambda: self.play_next(auto=False))
        self.progress.sliderMoved.connect(self.set_position)
        self.queue_list.itemDoubleClicked.connect(self._row_activated)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)

        self.setStyleSheet(style.stylesheet())
        self._refresh_queue_controls()

    def showEvent(self, event):
        # Playback itself (VLC) keeps running regardless - this timer
        # only drives the on-screen progress bar and auto-advance, so
        # there's no reason to keep polling it while some other page
        # is on screen.
        super().showEvent(event)
        self.update_progress()
        self.timer.start(400)

    def hideEvent(self, event):
        super().hideEvent(event)
        self.timer.stop()

    # ------------------------------------------------------------------
    # queue management
    # ------------------------------------------------------------------

    def select_songs(self):
        # Uses the same simple static dialog call as video.py (which
        # works reliably) instead of a manually built QFileDialog -
        # forcing DontUseNativeDialog + a fixed size matching the
        # fullscreen main window could open the dialog behind it under
        # a bare window manager (no decorations to bring it to front).
        # getOpenFileNames (plural) lets the user select several songs
        # at once, appended to the queue.
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Vyberte skladby",
            "",
            "Audio (*.mp3 *.wav *.ogg *.flac)"
        )

        if not files:
            return

        was_empty = len(self.queue) == 0
        self.queue.extend(files)
        self._refresh_queue_list()

        if was_empty:
            self._play_index(0)

    def clear_queue(self):
        self.player.stop()
        self.queue = []
        self.current_index = -1
        self.title.setText("Vyberte skladby")
        self._refresh_queue_list()

    def _row_activated(self, item):
        idx = self.queue_list.row(item)
        self._play_index(idx)

    def play_next(self, auto=False):
        if not self.queue:
            return
        if self.current_index + 1 < len(self.queue):
            self._play_index(self.current_index + 1)
        elif not auto:
            # manual "next" at the end of the queue - nothing further
            pass

    def play_previous(self):
        if not self.queue:
            return
        if self.current_index > 0:
            self._play_index(self.current_index - 1)

    def _play_index(self, index):
        if index < 0 or index >= len(self.queue):
            return
        self.current_index = index
        file = self.queue[index]
        media = self.vlc_instance.media_new(file)
        self.player.set_media(media)
        self.title.setText(os.path.basename(file))
        self.player.play()
        self._refresh_queue_list()

    def _refresh_queue_list(self):
        self.queue_list.clear()
        for i, file in enumerate(self.queue):
            item = QListWidgetItem(os.path.basename(file))
            self.queue_list.addItem(item)
            if i == self.current_index:
                item.setSelected(True)
                self.queue_list.setCurrentItem(item)
        self._refresh_queue_controls()

    def _refresh_queue_controls(self):
        has_queue = len(self.queue) > 0
        self.clear_btn.setEnabled(has_queue)
        self.prev_btn.setEnabled(has_queue and self.current_index > 0)
        self.next_btn.setEnabled(
            has_queue and self.current_index + 1 < len(self.queue)
        )

    # ------------------------------------------------------------------
    # playback / progress
    # ------------------------------------------------------------------

    def update_progress(self):
        if self.player.get_state() == vlc.State.Ended:
            self.play_next(auto=True)
            return

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
# verze 9.0 - výběr více skladeb najednou a fronta přehrávání
