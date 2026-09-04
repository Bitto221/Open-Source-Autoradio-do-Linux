import sys
import os

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QToolButton,
    QGridLayout,
    QVBoxLayout,
    QLabel
)

from PyQt5.QtCore import Qt, QSize

import style


class ThemeSelector(QWidget):

    def __init__(self, parent=None, on_theme_changed=None):
        super().__init__(parent)

        # Called with (color, wallpaper_path) right after a theme is
        # picked, so the shell can restyle everything live - no more
        # killing and relaunching the whole app.
        self.on_theme_changed = on_theme_changed

        self.setObjectName("mainWindow")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(style.stylesheet())

        subtitle = QLabel("VZHLED")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        title = QLabel("Vyberte motiv")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 16, 30, 16)
        layout.addWidget(subtitle)
        layout.addWidget(title)
        layout.addSpacing(10)

        grid = QGridLayout()
        grid.setSpacing(18)

        cols = 3
        for index, (name, (color, wallpaper_file)) in enumerate(style.THEMES.items()):

            wallpaper = os.path.join(style.WALLPAPER_DIR, wallpaper_file)

            btn = QToolButton()
            btn.setText(name)
            btn.setCheckable(False)
            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            btn.setFixedSize(150, 100)
            btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: {style.rgba(color, 60)};
                    border: 2px solid {color};
                    border-radius: 18px;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QToolButton:hover {{
                    background-color: {style.rgba(color, 110)};
                    border: 2px solid {style.lighten(color, 0.35)};
                }}
            """)

            btn.clicked.connect(
                lambda checked, c=color, w=wallpaper: self.select_theme(c, w)
            )

            row, col = divmod(index, cols)
            grid.addWidget(btn, row, col, alignment=Qt.AlignCenter)

        layout.addLayout(grid)
        layout.addStretch()

        self.setLayout(layout)

    def select_theme(self, color, wallpaper):

        style.save_theme(color, wallpaper)
        style.refresh()

        if self.on_theme_changed:
            self.on_theme_changed(color, wallpaper)
        else:
            # standalone mode - just restyle this window as a preview
            self.setStyleSheet(style.stylesheet())


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ThemeSelector()
    window.setWindowTitle("Themes")
    window.setFixedSize(800, 480)
    window.show()

    sys.exit(app.exec_())
