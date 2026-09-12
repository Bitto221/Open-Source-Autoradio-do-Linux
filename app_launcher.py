import shutil
import subprocess
import threading
import time


def _wmctrl_available():
    return shutil.which("wmctrl") is not None


def _force_fullscreen_when_ready(window_title, timeout=8):
    """Waits (in the background - never blocks the GUI) for a window
    with this title to appear, then forces it into the same EWMH
    fullscreen state our own app uses (`_NET_WM_STATE_FULLSCREEN` via
    wmctrl). Purely cosmetic: makes truly-external programs (welle.io,
    GNOME Maps) present the same borderless, GNOME-top-bar-free look as
    every embedded page, instead of popping up as an ordinary window
    with the desktop chrome visible around it.

    Requires wmctrl and a real X11 (or XWayland-visible) window - safe
    to call unconditionally, it just does nothing if either is missing."""

    if not _wmctrl_available():
        return

    def _worker():
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                result = subprocess.run(
                    ["wmctrl", "-l"],
                    stdout=subprocess.PIPE,
                    text=True,
                    timeout=2
                )
                if window_title.lower() in result.stdout.lower():
                    subprocess.run(
                        ["wmctrl", "-r", window_title, "-b", "add,fullscreen"],
                        timeout=2
                    )
                    return
            except Exception:
                pass
            time.sleep(0.3)

    threading.Thread(target=_worker, daemon=True).start()


def app_run_or_focus(window_title, start_command, fullscreen=True):
    """Focuses an already running window with the given title (via wmctrl),
    or starts start_command if no such window exists. Used for external
    programs (DAB app, navigation) that open their own window.

    By default also forces that window fullscreen once it appears (see
    _force_fullscreen_when_ready) so it visually matches the rest of the
    app instead of showing GNOME's top bar around it - pass
    fullscreen=False to skip this for programs that shouldn't be
    fullscreen.

    Never raises - if the external program isn't installed on this
    machine, we print a helpful message instead of crashing the whole
    launcher."""

    if _wmctrl_available():
        try:
            result = subprocess.run(
                ["wmctrl", "-l"],
                stdout=subprocess.PIPE,
                text=True
            )

            if window_title.lower() in result.stdout.lower():
                subprocess.run(["wmctrl", "-a", window_title])
                if fullscreen:
                    _force_fullscreen_when_ready(window_title)
                return
        except Exception:
            pass

    try:
        subprocess.Popen(start_command)
        if fullscreen:
            _force_fullscreen_when_ready(window_title)
    except FileNotFoundError:
        print(
            f"[CHYBA] Program '{start_command[0]}' nebyl nalezen. "
            f"Nainstalujte ho, nebo upravte COMMAND v příslušném souboru."
        )
    except Exception as e:
        print(f"[CHYBA] Nepodařilo se spustit '{start_command[0]}': {e}")


def open_gnome_settings_panel(panel, fallbacks=None):
    """Opens a specific panel of GNOME Settings (gnome-control-center) -
    this app targets a GNOME desktop, so its own native settings UI is
    the primary choice. Falls back to alternative tools if
    gnome-control-center isn't available for some reason."""

    if shutil.which("gnome-control-center"):
        try:
            subprocess.Popen(["gnome-control-center", panel])
            return True
        except Exception:
            pass

    for candidate in (fallbacks or []):
        if shutil.which(candidate[0]):
            try:
                subprocess.Popen(candidate)
                return True
            except Exception:
                continue

    print(
        f"Nelze otevřít nastavení '{panel}' - chybí gnome-control-center "
        f"(sudo apt install gnome-control-center)."
    )
    return False


def open_wifi_settings():
    """Opens GNOME's own Wi-Fi settings panel."""
    return open_gnome_settings_panel(
        "wifi",
        fallbacks=[["nm-connection-editor"]]
    )


def open_audio_output_settings():
    """Opens the Sound settings panel so the user can pick which output
    device (jack, USB sound card, HDMI, a connected Bluetooth speaker
    once paired, ...) plays audio. Replaces the old direct Bluetooth
    button in Settings - pairing itself is handled by BT Hudba's own
    "Zviditelnit pro párování" button; this is for choosing where the
    sound actually comes out."""
    return open_gnome_settings_panel(
        "sound",
        fallbacks=[["pavucontrol"]]
    )


def set_bluetooth_discoverable(enabled):
    """Makes this device itself discoverable and pairable over Bluetooth,
    so a phone can find *it* and connect to stream audio to it (the
    Orange Pi acting as an A2DP sink / Bluetooth speaker) - a different
    goal from open_gnome_settings_panel("bluetooth"), which is for
    pairing/managing devices the other way around. Toggled by the
    "Zviditelnit pro párování" button in BT Hudba.

    This only handles visibility/pairability - actually receiving and
    playing the audio once connected depends on the system's Bluetooth
    audio stack (PipeWire+WirePlumber or PulseAudio with
    pulseaudio-module-bluetooth) being installed, see README.

    Never raises - if bluetoothctl isn't available, prints a message
    instead of crashing the app."""

    if not shutil.which("bluetoothctl"):
        print(
            "Chybí bluetoothctl (balíček bluez) - Bluetooth nelze "
            "zviditelnit."
        )
        return False

    state = "on" if enabled else "off"

    try:
        subprocess.run(["bluetoothctl", "power", "on"], timeout=5)
        subprocess.run(["bluetoothctl", "pairable", state], timeout=5)
        subprocess.run(["bluetoothctl", "discoverable", state], timeout=5)
        return True
    except Exception as e:
        print(f"[CHYBA] Nepodařilo se nastavit viditelnost Bluetooth: {e}")
        return False
