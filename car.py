import sys
import os
import vlc
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QFileDialog, QSlider, QHBoxLayout, QVBoxLayout
)
from PyQt5.QtCore import Qt, QTimer

class CarSettings(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Car Settings") 
        self.setFixedSize(800, 480)

        self.title = QLabel("BMW E36")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setObjectName("car")

        self.switch1_btn = QPushButton("Switch1")
        self.switch2_btn = QPushButton("Switch2")
        self.switch3_btn = QPushButton("Switch3")


        controls = QHBoxLayout()
        controls.setSpacing(20)
        controls.addStretch()
        controls.addWidget(self.switch1_btn)
        controls.addWidget(self.switch2_btn)
        controls.addWidget(self.switch3_btn)
        controls.addStretch()

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addStretch()
        layout.addLayout(controls)

        self.setLayout(layout)


        # ===== STYLE =====
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CarSettings()
    window.show()
    sys.exit(app.exec_())