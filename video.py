import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QFileDialog, QLabel, QVBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Player")
        self.setFixedSize(800, 480)
        self.setStyleSheet("background-color: #0e0e0e;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Video přehrávač")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #bb86fc;")
        title.setAlignment(Qt.AlignCenter)

        self.btn = QPushButton("📁 Vybrat video (USB / disk)")
        self.btn.setFixedSize(360, 80)
        self.btn.setFont(QFont("Arial", 16))
        self.btn.setStyleSheet("""
            QPushButton {
                background-color: #bb86fc;
                color: black;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #d0a8ff;
            }
        """)
        self.btn.clicked.connect(self.open_file)

        layout.addWidget(title)
        layout.addSpacing(40)
        layout.addWidget(self.btn)

        self.setLayout(layout)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Vyber video",
            "/media",   # 👈 zde jsou USB disky
            "Video (*.mp4 *.mkv *.avi *.mov)"
        )

        if file_path:
            subprocess.Popen([
                "vlc",
                "--fullscreen",
                "--no-video-title-show",
                file_path
            ])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoPlayer()
    window.show()
    sys.exit(app.exec_())