import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl

URL = "https://www.google.com"


class WebApp(QWidget):
    """General web browsing, embedded directly in the shell
    (QWebEngineView) - same reasoning as YouTube/YouTube Music: a
    separate chromium-browser process has to cold-start an entire new
    browser (its own renderer/GPU process, shared libraries, profile)
    every time, which is why it felt noticeably slower to open than the
    embedded pages that reuse the QtWebEngine runtime already running
    inside this same process. Embedding it here also means it shares
    the exact same fullscreen presentation as every other page - no
    separate window, no GNOME top bar flashing in."""

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
    window = WebApp()
    window.setWindowTitle("Web")
    window.setFixedSize(800, 480)
    window.show()
    sys.exit(app.exec_())

# hotový kod
# verze 2.0 - vestavěné okno, ne samostatný chromium proces
