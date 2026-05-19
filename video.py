import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QFileDialog, QLabel, QVBoxLayout
)
from PyQt5.QtCore import Qt
import style

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        # WINDOW
        self.setWindowTitle("Video Player")
        self.setFixedSize(800, 480)
        self.setWindowFlags(Qt.Window)

        self.setObjectName("mainWindow")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # UI
        title = QLabel("Video přehrávač")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("title")

        self.btn = QPushButton("📁 Vybrat video")
        self.btn.setFixedSize(360, 80)
        self.btn.setObjectName("openfile")
        self.btn.clicked.connect(self.open_file)

        layout.addWidget(title)
        layout.addSpacing(40)
        layout.addWidget(self.btn)

        self.setLayout(layout)

        # STYLE
        self.setStyleSheet(style.stylesheet())


    # LOGIC
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Video (*.mp4 *.mkv *.avi *.mov)"
        )

        if file_path:
            subprocess.Popen([
                "vlc",
                "--fullscreen",
                "--no-video-title-show",
                file_path
            ])


# ENTRY
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoPlayer()
    window.show()
    sys.exit(app.exec_())
# htový kod
# verze 5.5