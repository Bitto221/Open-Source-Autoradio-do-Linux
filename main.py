import sys
import os
import traceback

from PyQt5.QtWidgets import (
    QApplication, QWidget, QToolButton, QGridLayout,
    QLabel, QVBoxLayout, QHBoxLayout, QStackedWidget, QFrame
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt, QTimer, QDateTime

import style

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(BASE_DIR, "icons")

sys.path.insert(0, BASE_DIR)


# ---------------------------------------------------------------------------
# App catalogue
#
# kind = "embed"    -> a QWidget page built in-process and swapped into the
#                       central QStackedWidget (no new python window!)
# kind = "external" -> a real external program / browser that needs its own
#                       OS window (welle-io, gnome-maps, chromium, ...)
# ---------------------------------------------------------------------------

APPS = [
    {"id": "music",    "label": "Hudba",     "icon": "music_player.png",  "kind": "embed"},
    {"id": "youtube",  "label": "YouTube",   "icon": "youtube.png",       "kind": "embed"},
    {"id": "ytmusic",  "label": "YT Music",  "icon": "youtube_music.png", "kind": "embed"},
    {"id": "fm",       "label": "FM Rádio",  "icon": "fm.png",            "kind": "embed"},
    {"id": "video",    "label": "Video",     "icon": "vlc.png",           "kind": "embed"},
    {"id": "dab",      "label": "DAB",       "icon": "dab.png",           "kind": "external"},
    {"id": "weather",  "label": "Počasí",    "icon": "weather.png",       "kind": "embed"},
    {"id": "web",      "label": "Web",       "icon": "browser.png",       "kind": "external"},
    {"id": "settings", "label": "Nastavení", "icon": "settings.png",      "kind": "embed"},
    {"id": "themes",   "label": "Vzhled",    "icon": "themes.png",        "kind": "embed"},
    {"id": "btmusic",  "label": "BT Hudba",  "icon": "btmusic.png",       "kind": "embed"},
    {"id": "nav",      "label": "Navigace",  "icon": "navigation.png",    "kind": "external"},
]

# order the bottom dock shortcuts show up in: first half - HOME - second half
DOCK_ORDER = [a["id"] for a in APPS]


def _safe_import(module_name, attr):
    """Best-effort import so a missing optional dependency (python-vlc,
    requests, PyQtWebEngine, ...) disables just that one app tile instead
    of crashing the whole launcher."""
    try:
        module = __import__(module_name)
        return getattr(module, attr)
    except Exception:
        traceback.print_exc()
        return None


MusicPlayer = _safe_import("music_player", "MusicPlayer")
FmRadio = _safe_import("FM_radio", "FmRadio")
VideoPlayer = _safe_import("video", "VideoPlayer")
WeatherApp = _safe_import("weather", "WeatherApp")
Settings = _safe_import("settings", "Settings")
ThemeSelector = _safe_import("themes", "ThemeSelector")
BluetoothPlayer = _safe_import("bluetooth_player", "BluetoothPlayer")
YouTubeApp = _safe_import("youtube", "YouTubeApp")
YouTubeMusicApp = _safe_import("youtube_music", "YouTubeMusicApp")

import web
import DAB
import navigace
from app_launcher import toggle_onscreen_keyboard

EXTERNAL_LAUNCHERS = {
    "web": web.launch,
    "dab": DAB.launch,
    "nav": navigace.launch,
}

# Heavy pages (embedded browser engine / network call on first use) are
# only built the first time the user actually opens them - keeps startup
# fast instead of spinning up several web engine instances up front.
EAGER_FACTORIES = {
    "music":    (MusicPlayer, "Hudba"),
    "fm":       (FmRadio, "FM Rádio"),
    "video":    (VideoPlayer, "Video"),
    "settings": (Settings, "Nastavení"),
    "themes":   (ThemeSelector, "Vzhled"),
    "btmusic":  (BluetoothPlayer, "BT Hudba"),
}

LAZY_FACTORIES = {
    "weather": (WeatherApp, "Počasí"),
    "youtube": (YouTubeApp, "YouTube"),
    "ytmusic": (YouTubeMusicApp, "YT Music"),
}


class UnavailablePage(QWidget):
    """Shown instead of a page whose optional dependency is missing, so
    the launcher keeps working even with an incomplete install."""

    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.setObjectName("mainWindow")
        self.setAttribute(Qt.WA_StyledBackground, True)

        title = QLabel(f"{label} není dostupné")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)

        hint = QLabel("Chybí potřebný modul / knihovna pro tuto aplikaci.")
        hint.setObjectName("label")
        hint.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addStretch()

        self.setStyleSheet(style.stylesheet())


class LoadingPlaceholder(QWidget):
    """Reserves a page's slot in the stack until its (heavier) real
    widget is built on first visit - see MainWindow._ensure_loaded."""

    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.setObjectName("mainWindow")
        self.setAttribute(Qt.WA_StyledBackground, True)

        title = QLabel(f"Načítání – {label}…")
        title.setObjectName("label")
        title.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addWidget(title)
        layout.addStretch()

        self.setStyleSheet(style.stylesheet())


class HomeScreen(QWidget):
    """The Android-launcher style grid of app tiles."""

    def __init__(self, on_launch, parent=None):
        super().__init__(parent)
        self.setObjectName("page")
        self.on_launch = on_launch
        self.tiles = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(30, 18, 30, 10)
        outer.setSpacing(10)

        heading = QLabel("VYBERTE APLIKACI")
        heading.setObjectName("subtitle")
        heading.setAlignment(Qt.AlignCenter)
        outer.addWidget(heading)

        outer.addStretch()

        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setAlignment(Qt.AlignCenter)

        cols = 4
        for index, app in enumerate(APPS):
            row, col = divmod(index, cols)

            tile = QToolButton()
            tile.setObjectName("tile")
            tile.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            tile.setIcon(QIcon(os.path.join(ICON_PATH, app["icon"])))
            tile.setIconSize(QSize(52, 52))
            tile.setFixedSize(150, 100)
            tile.setText(app["label"])
            tile.clicked.connect(lambda checked, a=app["id"]: self.on_launch(a))

            self.tiles.append(tile)
            grid.addWidget(tile, row, col)

        outer.addLayout(grid)
        outer.addStretch()

        self.restyle()

    def restyle(self):
        qss = style.home_tile_stylesheet()
        for tile in self.tiles:
            tile.setStyleSheet(qss)


class MainWindow(QWidget):
    TOPBAR_HEIGHT = 36
    DOCK_HEIGHT = 64

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Autoradio")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setObjectName("shellBackground")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.page_index = {}     # app id -> stacked widget index
        self.page_widget = {}    # app id -> widget instance
        self.dock_buttons = {}   # app id / "home" -> QToolButton

        self._build_ui()
        self.apply_theme(style.get_color(), style.get_wallpaper())

        self.showFullScreen()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        overlay = QWidget()
        overlay.setObjectName("shellOverlay")
        overlay.setAttribute(Qt.WA_StyledBackground, True)
        root.addWidget(overlay)

        shell = QVBoxLayout(overlay)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)

        shell.addWidget(self._build_topbar())

        self.stack = QStackedWidget()
        # Hard cap on the content area's height so that no single page's
        # content (e.g. once real data loads and labels/images grow) can
        # ever inflate the whole window and push the dock bar off the
        # bottom of the screen - worst case a page's own content clips,
        # but the dock/topbar chrome always stays put and visible.
        screen = QApplication.primaryScreen()
        if screen is not None:
            available_height = screen.size().height() - self.TOPBAR_HEIGHT - self.DOCK_HEIGHT
            self.stack.setFixedHeight(max(available_height, 200))
        shell.addWidget(self.stack, 1)

        shell.addWidget(self._build_dock())

        self.home = HomeScreen(self.go_to)
        self._register_page("home", self.home)

        self._register_embedded_apps()

    def _build_topbar(self):
        bar = QWidget()
        bar.setObjectName("topBar")
        bar.setAttribute(Qt.WA_StyledBackground, True)
        bar.setFixedHeight(self.TOPBAR_HEIGHT)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(18, 0, 14, 0)

        self.date_label = QLabel()
        self.date_label.setObjectName("dateLbl")

        self.page_title = QLabel("DOMŮ")
        self.page_title.setObjectName("pageTitle")
        self.page_title.setAlignment(Qt.AlignCenter)

        self.time_label = QLabel()
        self.time_label.setObjectName("clock")
        self.time_label.setFont(style.digital_font(16))

        clock_chip = QWidget()
        clock_chip.setObjectName("clockChip")
        clock_chip.setAttribute(Qt.WA_StyledBackground, True)
        clock_layout = QHBoxLayout(clock_chip)
        clock_layout.setContentsMargins(12, 3, 12, 3)
        clock_layout.addWidget(self.time_label)

        layout.addWidget(self.date_label, 1, Qt.AlignLeft)
        layout.addWidget(self.page_title, 2, Qt.AlignCenter)
        layout.addWidget(clock_chip, 1, Qt.AlignRight)

        timer = QTimer(self)
        timer.timeout.connect(self._update_datetime)
        timer.start(1000)
        self._update_datetime()

        return bar

    def _build_dock(self):
        bar = QWidget()
        bar.setObjectName("dockBar")
        bar.setAttribute(Qt.WA_StyledBackground, True)
        bar.setFixedHeight(self.DOCK_HEIGHT)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(5)
        layout.addStretch()

        half = len(DOCK_ORDER) // 2
        left_ids = DOCK_ORDER[:half]
        right_ids = DOCK_ORDER[half:]

        by_id = {a["id"]: a for a in APPS}

        for app_id in left_ids:
            layout.addWidget(self._make_dock_button(by_id[app_id]))

        layout.addSpacing(8)
        layout.addWidget(self._make_home_button())
        layout.addSpacing(8)

        for app_id in right_ids:
            layout.addWidget(self._make_dock_button(by_id[app_id]))

        layout.addSpacing(10)
        layout.addWidget(self._make_dock_divider())
        layout.addSpacing(10)
        layout.addWidget(self._make_keyboard_button())

        layout.addStretch()
        return bar

    def _make_dock_divider(self):
        # Thin vertical separator so the keyboard quick-action reads as
        # "not a page" and is visually set apart from the app icons.
        line = QFrame()
        line.setObjectName("dockDivider")
        line.setFixedSize(1, 30)
        return line

    def _make_dock_button(self, app):
        btn = QToolButton()
        btn.setObjectName("dockIcon")
        btn.setIcon(QIcon(os.path.join(ICON_PATH, app["icon"])))
        btn.setIconSize(QSize(24, 24))
        btn.setFixedSize(40, 40)
        btn.setToolTip(app["label"])
        btn.setCheckable(app["kind"] == "embed")
        btn.clicked.connect(lambda checked, a=app["id"]: self.go_to(a))
        self.dock_buttons[app["id"]] = btn
        return btn

    def _make_home_button(self):
        btn = QToolButton()
        btn.setObjectName("homeBtn")
        btn.setIcon(QIcon(os.path.join(ICON_PATH, "home.png")))
        btn.setIconSize(QSize(28, 28))
        btn.setFixedSize(50, 50)
        btn.setToolTip("Domů")
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self.go_to("home"))
        self.dock_buttons["home"] = btn
        return btn

    def _make_keyboard_button(self):
        # Manual show/hide for the on-screen (touch) keyboard. The
        # keyboard (onboard) is set up to pop up on its own when a text
        # field gets focus - this button is the fallback/override for
        # the cases where auto-show doesn't trigger.
        btn = QToolButton()
        btn.setObjectName("dockIcon")
        btn.setIcon(QIcon(os.path.join(ICON_PATH, "keyboard.png")))
        btn.setIconSize(QSize(24, 24))
        btn.setFixedSize(40, 40)
        btn.setToolTip("Dotyková klávesnice")
        btn.setCheckable(False)
        btn.clicked.connect(lambda: toggle_onscreen_keyboard())
        return btn

    # ------------------------------------------------------------------
    # page registration
    # ------------------------------------------------------------------

    def _register_page(self, app_id, widget):
        idx = self.stack.addWidget(widget)
        self.page_index[app_id] = idx
        self.page_widget[app_id] = widget

    def _instantiate(self, app_id, cls, label):
        if cls is None:
            return UnavailablePage(label)
        try:
            if app_id == "settings":
                return cls(on_exit=self.quit_app)
            if app_id == "themes":
                return cls(on_theme_changed=self.apply_theme)
            return cls()
        except Exception:
            # construction can fail for environment reasons even when the
            # module imported fine (e.g. VLC plugin cache not ready,
            # audio device missing) - fall back instead of crashing the
            # whole launcher.
            traceback.print_exc()
            return UnavailablePage(label)

    def _register_embedded_apps(self):
        # built immediately - lightweight, no network/engine startup cost
        for app_id, (cls, label) in EAGER_FACTORIES.items():
            widget = self._instantiate(app_id, cls, label)
            self._register_page(app_id, widget)

        # reserved now, built lazily on first visit (see _ensure_loaded)
        self.lazy_factories = dict(LAZY_FACTORIES)
        for app_id, (cls, label) in LAZY_FACTORIES.items():
            self._register_page(app_id, LoadingPlaceholder(label))

    def _ensure_loaded(self, app_id):
        if app_id not in self.lazy_factories:
            return

        cls, label = self.lazy_factories.pop(app_id)
        idx = self.page_index[app_id]
        old_widget = self.stack.widget(idx)

        widget = self._instantiate(app_id, cls, label)
        widget.setStyleSheet(style.stylesheet(style.get_color()))

        self.stack.removeWidget(old_widget)
        old_widget.deleteLater()
        self.stack.insertWidget(idx, widget)
        self.page_widget[app_id] = widget

    # ------------------------------------------------------------------
    # navigation
    # ------------------------------------------------------------------

    def go_to(self, app_id):
        app = next((a for a in APPS if a["id"] == app_id), None)

        if app_id != "home" and app and app["kind"] == "external":
            launcher = EXTERNAL_LAUNCHERS.get(app_id)
            if launcher:
                try:
                    launcher()
                except Exception as e:
                    print(f"[CHYBA] Spuštění '{app_id}' selhalo: {e}")
            # external apps get their own OS window - don't change our
            # stack, just briefly reflect the tap and move focus back.
            btn = self.dock_buttons.get(app_id)
            if btn:
                btn.setChecked(False)
            return

        self._ensure_loaded(app_id)

        if app_id in self.page_index:
            self.stack.setCurrentIndex(self.page_index[app_id])

        label = "DOMŮ" if app_id == "home" else next(
            (a["label"] for a in APPS if a["id"] == app_id), app_id
        ).upper()
        self.page_title.setText(label)

        for key, btn in self.dock_buttons.items():
            if btn.isCheckable():
                btn.setChecked(key == app_id)

    # ------------------------------------------------------------------
    # theme + misc
    # ------------------------------------------------------------------

    def apply_theme(self, color, wallpaper):
        style.refresh()

        self.setStyleSheet(style.shell_stylesheet(wallpaper))
        self.findChild(QWidget, "topBar").setStyleSheet(style.topbar_stylesheet(color))
        self.findChild(QWidget, "dockBar").setStyleSheet(style.dock_stylesheet(color))
        self.home.restyle()

        global_qss = style.stylesheet(color)
        for widget in self.page_widget.values():
            widget.setStyleSheet(global_qss)

    def _update_datetime(self):
        now = QDateTime.currentDateTime()
        self.date_label.setText(now.toString("dd.MM.yyyy"))
        self.time_label.setText(now.toString("HH:mm:ss"))

    def quit_app(self):
        QApplication.quit()

    def closeEvent(self, event):
        fm = self.page_widget.get("fm")
        if fm is not None and hasattr(fm, "stop_radio"):
            fm.stop_radio()

        for app_id in ("music", "youtube", "ytmusic"):
            widget = self.page_widget.get(app_id)
            if widget is not None and hasattr(widget, "stop_playback"):
                widget.stop_playback()

        # Weather's fetch runs in a background QThread - if one is still
        # in flight when the app quits, Qt would try to destroy it while
        # running, which is a hard crash ("QThread: Destroyed while
        # thread is still running"). Give it a moment to finish first.
        weather = self.page_widget.get("weather")
        fetcher = getattr(weather, "_fetcher", None)
        if fetcher is not None and fetcher.isRunning():
            fetcher.wait(3000)

        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

# hotový kod
# verze 10.0 - odebrány vestavěné Mapy (nahrazuje je Navigace/GNOME Maps),
# přidán BT Hudba - zobrazení a ovládání aktuálně přehrávané skladby
# streamované z telefonu přes Bluetooth (AVRCP/BlueZ)
