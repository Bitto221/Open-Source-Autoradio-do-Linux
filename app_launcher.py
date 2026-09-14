import shutil
import subprocess
import threading
import time


def _wmctrl_available():
    return shutil.which("wmctrl") is not None


def _force_fullscreen_when_ready(window_title, timeout=8):

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
    return open_gnome_settings_panel(
        "sound",
        fallbacks=[["pavucontrol"]]
    )


def set_bluetooth_discoverable(enabled):

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
