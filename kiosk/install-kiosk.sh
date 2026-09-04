#!/bin/bash
# Vypne automatické spouštění GNOME (GDM) a místo toho nastaví Autoradio
# tak, aby po startu desky naskočilo samo, na celou obrazovku, bez
# přihlašovací obrazovky a bez celého GNOME desktopu okolo.
#
# Spouštěj jako: sudo ./install-kiosk.sh
# (spouštěj přes sudo jako běžný uživatel, ne přihlášený rovnou jako
#  root - skript si zjistí tvého uživatele z $SUDO_USER)
#
# Vrácení zpět (chceš-li se vrátit ke GNOME): viz konec tohoto souboru,
# nebo README.md, sekce "Kiosk režim".

set -e

if [ -z "$SUDO_USER" ]; then
    echo "Spusť tento skript přes 'sudo ./install-kiosk.sh' (ne jako root přímo)."
    exit 1
fi

USER_NAME="$SUDO_USER"
USER_HOME=$(getent passwd "$USER_NAME" | cut -d: -f6)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"

echo "Uživatel:        $USER_NAME"
echo "Domovská složka: $USER_HOME"
echo "Appka je v:      $APP_DIR"
echo

# 1) Odlehčený okenní manažer - GNOME/gnome-shell už po tomhle kroku
#    nepoběží, takže potřebujeme něco, co bude spravovat okna místo
#    něj (appka sama fullscreen okno nepotřebuje, ale např. okno
#    Nastavení Wi-Fi/Bluetooth ano). Zároveň instalujeme `onboard`
#    (dotyková klávesnice), `dbus-x11` (D-Bus session bez desktop
#    prostředí) a `at-spi2-core` (aby onboard poznal, kdy je aktivní
#    textové pole - viz krok 2 níže). X server, xinit a
#    gnome-control-center/NetworkManager/blueman už na desce s GNOME
#    jsou - apt jen přeskočí, co už je nainstalované.
echo "==> Instaluji okenní manažer, dotykovou klávesnici a závislosti..."
apt-get update
apt-get install --no-install-recommends -y \
    xserver-xorg xinit x11-xserver-utils matchbox-window-manager unclutter \
    onboard at-spi2-core dbus-x11 dconf-cli

# 2) Výchozí nastavení klávesnice `onboard`: automaticky se zobrazit
#    při kliknutí do textového pole a ukotvit dole na obrazovce (ne
#    volně plovoucí okno). Nastavuje se přes dconf systémový profil,
#    což funguje spolehlivě i bez toho, aby uživatel měl zrovna
#    přihlášenou grafickou session (na rozdíl od `gsettings set`).
echo "==> Nastavuji automatické zobrazování klávesnice..."
mkdir -p /etc/dconf/profile
if [ ! -f /etc/dconf/profile/user ]; then
    cat > /etc/dconf/profile/user <<'EOF'
user-db:user
system-db:local
EOF
fi

mkdir -p /etc/dconf/db/local.d
cat > /etc/dconf/db/local.d/01-onboard <<'EOF'
[org/onboard]
auto-show-enabled=true

[org/onboard/window]
docking-enabled=true
docking-edge='bottom'
EOF
dconf update

# 3) Vypnutí GDM (grafického přihlašovacího okna GNOME), aby se po
#    startu nespouštěl celý desktop. `display-manager.service` je
#    univerzální alias na to, co je zrovna aktivní (GDM/GDM3/LightDM/
#    SDDM), takže to funguje bez ohledu na přesný název balíčku.
if systemctl list-unit-files display-manager.service &>/dev/null; then
    echo "==> Vypínám GDM / GNOME přihlašovací obrazovku..."
    systemctl disable --now display-manager.service || true
else
    echo "==> Žádný displej manager (GDM) nenalezen, přeskakuji."
fi

# 4) Automatické přihlášení na tty1 (appka naskočí bez nutnosti se
#    ručně přihlašovat po zapnutí)
echo "==> Nastavuji automatické přihlášení na tty1..."
mkdir -p /etc/systemd/system/getty@tty1.service.d
sed "s/__USERNAME__/$USER_NAME/" "$SCRIPT_DIR/getty-autologin.conf" \
    > /etc/systemd/system/getty@tty1.service.d/override.conf
systemctl daemon-reload

# 5) ~/.xinitrc - co se spustí, když se na tty1 zavolá `startx`
echo "==> Instaluji ~/.xinitrc..."
sed "s#__APP_DIR__#$APP_DIR#" "$SCRIPT_DIR/xinitrc" > "$USER_HOME/.xinitrc"
chmod +x "$USER_HOME/.xinitrc"
chown "$USER_NAME:$USER_NAME" "$USER_HOME/.xinitrc"

chmod +x "$SCRIPT_DIR/run_autoradio.sh"

# 6) Po přihlášení na tty1 automaticky spustit `startx` (jen pokud ještě
#    X neběží a je to opravdu tty1 - jinak by se startx spouštěl i přes
#    ssh nebo na dalších konzolích)
MARKER="# >>> autoradio kiosk autostart >>>"
if ! grep -qF "$MARKER" "$USER_HOME/.bash_profile" 2>/dev/null; then
    echo "==> Přidávám autostart do ~/.bash_profile..."
    cat >> "$USER_HOME/.bash_profile" <<EOF

$MARKER
if [ -z "\$DISPLAY" ] && [ "\$(tty)" = "/dev/tty1" ]; then
    exec startx -- -nocursor
fi
# <<< autoradio kiosk autostart <<<
EOF
    chown "$USER_NAME:$USER_NAME" "$USER_HOME/.bash_profile"
else
    echo "==> ~/.bash_profile už autostart obsahuje, přeskakuji."
fi

echo
echo "Hotovo. Po restartu (sudo reboot) by appka měla naskočit"
echo "automaticky na celou obrazovku, MÍSTO GNOME - žádná"
echo "přihlašovací obrazovka, žádný desktop."
echo
echo "Dotyková klávesnice (onboard) se nastavila tak, aby se sama"
echo "zobrazovala při psaní. Appka má navíc vlastní ikonku klávesnice"
echo "v dolní liště pro ruční zapnutí/vypnutí, kdyby se automatické"
echo "zobrazení někde nespustilo."
echo
echo "Pro ruční test hned teď (bez restartu):"
echo "  sudo systemctl restart getty@tty1"
echo "  # pak se přepni na tty1 (Ctrl+Alt+F1)"
echo
echo "Návrat ke GNOME (kdykoliv v budoucnu):"
echo "  sudo systemctl enable --now display-manager.service"
echo "  sudo rm /etc/systemd/system/getty@tty1.service.d/override.conf"
echo "  sudo systemctl daemon-reload"
