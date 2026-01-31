import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QFileDialog, QSlider, QHBoxLayout, QVBoxLayout
)
from PyQt5.QtCore import Qt

class FM_radio(QWidget):
    def __init__(self):
        super().__init__()

        # UI
        self.setWindowTitle("FM Radio") 
        self.setFixedSize(800, 480)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FM_radio()
    window.show()
    sys.exit(app.exec_())