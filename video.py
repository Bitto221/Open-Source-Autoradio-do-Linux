import sys
import subprocess
import shutil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QFileDialog, QLabel, QVBoxLayout
)
from PyQt5.QtCore import Qt
import style


class VideoPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("mainWindow")
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(24)

        subtitle = QLabel("VIDEO")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        title = QLabel("Video přehrávač")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("title")

        hint = QLabel("Vybraný soubor se otevře ve VLC na celou obrazovku")
        hint.setObjectName("label")
        hint.setAlignment(Qt.AlignCenter)

        self.btn = QPushButton("📁  Vybrat video")
        self.btn.setFixedSize(360, 80)
        self.btn.setObjectName("openfile")
        self.btn.clicked.connect(self.open_file)

        layout.addWidget(subtitle)
        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addSpacing(20)
        layout.addWidget(self.btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

        self.setStyleSheet(style.stylesheet())

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Vyberte video",
            "",
            "Video (*.mp4 *.mkv *.avi *.mov)"
        )

        if not file_path:
            return

        if not shutil.which("vlc"):
            print("[CHYBA] Program 'vlc' nebyl nalezen. Nainstalujte ho (sudo apt install vlc).")
            return

        try:
            subprocess.Popen([
                "vlc",
                "--fullscreen",
                "--no-video-title-show",
                file_path
            ])
        except Exception as e:
            print(f"[CHYBA] Nepodařilo se spustit VLC: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoPlayer()
    window.setWindowTitle("Video Player")
    window.setFixedSize(800, 480)
    window.setWindowFlags(Qt.Window)
    window.show()
    sys.exit(app.exec_())

# hotový kod
# verze 6.0
