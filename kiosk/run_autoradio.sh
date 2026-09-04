#!/bin/bash
# Spouští Autoradio v kiosk režimu (bez GNOME desktopu).
# Volá se z ~/.xinitrc - neupravuj cesty ručně, install-kiosk.sh je
# dosadí automaticky.

set -e

# Složka, ve které leží tento skript = podsložka kiosk/ uvnitř projektu,
# takže main.py je o úroveň výš.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"

cd "$APP_DIR"

# Hardwarová akcelerace videa pro vestavěné YouTube/YouTube Music/Mapy
# (QtWebEngine/Chromium). Účinnost závisí na GPU/mesa ovladači na
# konkrétní desce - pokud by appka kvůli tomu nešla spustit nebo video
# "problikávalo", tenhle řádek zkus zakomentovat.
#
# --force-renderer-accessibility: donutí Chromium hned zpřístupnit
# textová pole (vyhledávání na YouTube apod.) dotykové klávesnici
# (onboard) - bez toho by se klávesnice ve webových stránkách mohla
# zobrazit až se zpožděním nebo vůbec.
export QTWEBENGINE_CHROMIUM_FLAGS="--enable-accelerated-video-decode --ignore-gpu-blocklist --enable-gpu-rasterization --use-gl=egl --force-renderer-accessibility"

# Zapne přístupnostní rozhraní i pro Qt část appky (vlastní dialogy),
# aby na jejich textová pole taky reagovala dotyková klávesnice.
export QT_ACCESSIBILITY=1

exec python3 main.py
