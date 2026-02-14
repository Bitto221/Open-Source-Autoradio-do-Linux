import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QFileDialog, QSlider, QHBoxLayout, QVBoxLayout
)
from PyQt5.QtCore import Qt

import style

class CarSettings(QWidget):
    def __init__(self):
        super().__init__()

        # UI
        self.setWindowTitle("Colors") 
        self.setFixedSize(800, 480)

        self.title = QLabel("Barvy")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setObjectName("title")

        self.color1_btn = QPushButton("Modrá")
        self.color2_btn = QPushButton("Fialová")
        self.color3_btn = QPushButton("Červená")
        self.color4_btn = QPushButton("Zelená")

        # Layout
        controls = QHBoxLayout()
        controls.setSpacing(20)
        controls.addStretch()
        controls.addWidget(self.color1_btn)
        controls.addWidget(self.color2_btn)
        controls.addWidget(self.color3_btn)
        controls.addWidget(self.color4_btn)
        controls.addStretch()

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addStretch()
        layout.addLayout(controls)

        self.setLayout(layout)


        # STYLE
        self.setStyleSheet(style.stylesheet())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CarSettings()
    window.show()
    sys.exit(app.exec_())