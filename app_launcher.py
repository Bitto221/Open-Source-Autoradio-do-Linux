import shutil
import subprocess


def _wmctrl_available():
    return shutil.which("wmctrl") is not None


def app_run_or_focus(window_title, start_command):
    """Focuses an already running window with the given title (via wmctrl),
    or starts start_command if no such window exists. Used for external
    programs (browser, DAB app, navigation) that open their own window.

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
                return
        except Exception:
            pass

    try:
        subprocess.Popen(start_command)
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


def open_bluetooth_manager():
    """Opens GNOME's own Bluetooth settings panel so the user can
    pair/select a device for audio playback. Shared by the Settings page
    and the quick Bluetooth icon in the dock."""
    return open_gnome_settings_panel(
        "bluetooth",
        fallbacks=[["blueman-manager"], ["blueberry"]]
    )


def toggle_onscreen_keyboard():
    """Shows/hides the on-screen (touch) keyboard - `onboard`, started
    alongside the kiosk session (see kiosk/xinitrc), is set up to
    auto-show itself when a text field gets focus. This is the manual
    fallback/override for cases where auto-show doesn't trigger (some
    web page fields, some dialogs) - one tap toggles it directly via
    onboard's D-Bus interface.

    Never raises - if onboard isn't running/installed, this just prints
    a message instead of crashing the app."""

    if shutil.which("dbus-send"):
        try:
            result = subprocess.run(
                ["dbus-send", "--session", "--type=method_call",
                 "--dest=org.onboard.Onboard",
                 "/org/onboard/Onboard/Keyboard",
                 "org.onboard.Onboard.Keyboard.ToggleVisible"],
                capture_output=True, timeout=3
            )
            if result.returncode == 0:
                return True
        except Exception:
            pass

    print(
        "Dotyková klávesnice (onboard) neběží nebo není nainstalovaná "
        "(sudo apt install onboard)."
    )
    return False
