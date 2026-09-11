#!/bin/bash
# Nastaví Autoradio tak, aby se spustilo automaticky na celou obrazovku
# HNED PO PŘIHLÁŠENÍ do normální GNOME session (na rozdíl od
# install-kiosk.sh, který GNOME/GDM úplně vypíná a běží jen s holým X
# serverem + matchboxem). Tenhle přístup se v reálném provozu ukázal
# spolehlivější - dotyková klávesnice, párování Bluetooth a fullscreen
# okna fungují správně, protože běží skutečný gnome-shell místo
# minimalistického matchboxu.
#
# Spouštěj jako běžný uživatel (BEZ sudo) - autostart a gsettings jsou
# nastavení jednoho uživatelského účtu, ne systémová. Jednotlivé kroky
# uvnitř, co potřebují oprávnění správce (apt, GDM konfigurace), si o
# heslo řeknou samy přes sudo:
#   ./install-gnome-autostart.sh

set -e

if [ "$(id -u)" = "0" ]; then
    echo "Nespouštěj tohle přes sudo/jako root - spusť to jako běžný"
    echo "uživatel, pod kterým se appka má spouštět."
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"

echo "Appka je v: $APP_DIR"
echo

# 1) Bluetooth audio - ať telefon může na desku streamovat hudbu
#    (A2DP sink). bt-agent navíc potvrzuje párování na pozadí - GNOME
#    má obvykle svého vlastního agenta, tenhle běží jako záloha.
# Zároveň `wmctrl` - appka ho používá, aby i skutečně externí programy
# (welle.io, GNOME Maps) šly přepnout do stejného fullscreen vzhledu
# bez GNOME horní lišty, stejně jako appka sama.
echo "==> Instaluji podporu pro Bluetooth audio a wmctrl (vyžaduje sudo)..."
sudo apt-get update
sudo apt-get install --no-install-recommends -y bluez bluez-tools wmctrl || true
sudo apt-get install --no-install-recommends -y pulseaudio-module-bluetooth || \
    echo "    (pulseaudio-module-bluetooth nedostupné - přeskakuji, deska možná používá PipeWire)"
sudo apt-get install --no-install-recommends -y libspa-0.2-bluetooth || \
    echo "    (libspa-0.2-bluetooth nedostupné - přeskakuji, deska možná používá PulseAudio)"

# 2) Autostart appky + Bluetooth agenta po přihlášení
echo "==> Instaluji autostart appky..."
mkdir -p "$HOME/.config/autostart"
sed "s#__APP_DIR__#$APP_DIR#" "$SCRIPT_DIR/autoradio.desktop" \
    > "$HOME/.config/autostart/autoradio.desktop"
cp "$SCRIPT_DIR/bt-agent-autostart.desktop" \
    "$HOME/.config/autostart/bt-agent-autostart.desktop"
chmod +x "$SCRIPT_DIR/run_autoradio.sh"

# 3) GNOME nesmí displej uspávat, uzamykat ani zhasínat - appka běží
#    fullscreen a jiná obrazovka/klávesnice u toho není
echo "==> Vypínám uspávání a zamykání obrazovky..."
gsettings set org.gnome.desktop.session idle-delay 0
gsettings set org.gnome.desktop.screensaver lock-enabled false
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type 'nothing' 2>/dev/null || true
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-battery-type 'nothing' 2>/dev/null || true

# 4) Přepnout GDM session z Wayland na X11 (Xorg). Důvod: appka i
#    `wmctrl` (viz krok 1) jsou nástroje pro X11 - pod čistým Waylandem
#    běží appka jen přes XWayland kompatibilitu, kde se chování
#    dotykové klávesnice i wmctrl dá nespolehlivé. Pod X11 obojí funguje
#    napřímo a předvídatelně.
echo "==> Přepínám GNOME session na X11 (vyžaduje sudo)..."
for GDM_CONF in /etc/gdm3/custom.conf /etc/gdm/custom.conf; do
    if [ -f "$GDM_CONF" ]; then
        if grep -q "^#\?WaylandEnable=" "$GDM_CONF"; then
            sudo sed -i 's/^#\?WaylandEnable=.*/WaylandEnable=false/' "$GDM_CONF"
        else
            sudo sed -i '/^\[daemon\]/a WaylandEnable=false' "$GDM_CONF"
        fi
        echo "    upraveno: $GDM_CONF"
    fi
done

# 5) Dotyková klávesnice - vestavěná GNOME klávesnice (Screen
#    Keyboard). Poznámka k omezením: GNOME nedává zvenčí žádný způsob,
#    jak ji ručně vyvolat na povel (potvrzeno přímo vývojářem
#    gnome-shellu - žádné D-Bus rozhraní pro tohle neexistuje) - jen se
#    sama zobrazí, když appka/stránka sama signalizuje aktivní textové
#    pole. Appka nastavuje `QT_ACCESSIBILITY=1` a Chromium
#    `--force-renderer-accessibility` (viz run_autoradio.sh), aby tohle
#    fungovalo jak pro appku samotnou, tak pro vestavěné YouTube/Web.
echo "==> Zapínám vestavěnou dotykovou klávesnici GNOME..."
gsettings set org.gnome.desktop.a11y.applications screen-keyboard-enabled true

echo
echo "Hotovo. Zbývá už jen ručně:"
echo
echo "1) Nastavení -> Uživatelé -> zapnout 'Automatické přihlášení'"
echo "   pro tvůj účet (potřebuje heslo správce, jde jen přes GUI)."
echo
echo "2) sudo reboot"
echo
echo "Po restartu by ses měl rovnou přihlásit (na X11, ne Wayland) a"
echo "appka by měla naskočit sama na celou obrazovku, přes normální"
echo "GNOME desktop na pozadí."
echo
echo "Pro test hned teď (bez restartu), stačí appku spustit ručně:"
echo "  $APP_DIR/kiosk/run_autoradio.sh"
echo "(přepnutí na X11 se ale projeví až po odhlášení/restartu)"
echo
echo "Zrušení autostartu appky (kdykoliv v budoucnu):"
echo "  rm ~/.config/autostart/autoradio.desktop"
echo "  rm ~/.config/autostart/bt-agent-autostart.desktop"
echo
echo "Návrat na Wayland (kdykoliv v budoucnu):"
echo "  sudo sed -i 's/^WaylandEnable=false/WaylandEnable=true/' /etc/gdm3/custom.conf"
echo "  sudo reboot"
