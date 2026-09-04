import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl

URL = "https://www.youtube.com/"


class YouTubeApp(QWidget):
    """YouTube embedded directly in the shell (QWebEngineView) so it opens
    instantly and shares the same frame/format as the other pages -
    no separate chromium window, no browser chrome."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("mainWindow")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(URL))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.browser)

    def go_home(self):
        self.browser.setUrl(QUrl(URL))

    def stop_playback(self):
        try:
            self.browser.setUrl(QUrl("about:blank"))
        except Exception:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeApp()
    window.setWindowTitle("YouTube")
    window.setFixedSize(800, 480)
    window.show()
    sys.exit(app.exec_())

# hotový kod
# verze 4.0 - vestavěné okno, ne samostatný chromium proces
