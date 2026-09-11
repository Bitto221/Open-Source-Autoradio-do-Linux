#!/bin/bash
# Vypne GNOME služby na pozadí, které appka vůbec nepotřebuje, ale
# běžná desktopová instalace je má zapnuté defaultně. Cíleně NEVYPÍNÁ
# gnome-shell/mutter samotné - to je přesně to, díky čemu teď appka
# funguje spolehlivě (fullscreen, dotyková klávesnice, Bluetooth), jen
# odstraňuje zátěž navíc kolem toho, co appka nikdy nevyužije.
#
# Bezpečné spustit i opakovaně. Každý krok jde jednotlivě vrátit zpět -
# viz komentáře. Spouštěj jako běžný uživatel, jednotlivé kroky si o
# heslo řeknou přes sudo, kde je potřeba:
#   ./trim-gnome.sh

set -e

echo "==> Vypínám indexování souborů (Tracker) - appka žádné"
echo "    vyhledávání v souborech/Nautilus prohlížeči nepoužívá..."
# Název jednotek se liší podle verze Trackeru (2.x vs 3.x) - zkusíme
# obě varianty, chybějící jen tiše přeskočíme.
for unit in tracker-miner-fs-3.service tracker-extract-3.service \
            tracker-miner-rss-3.service tracker-writeback-3.service \
            tracker-xdg-portal-3.service tracker-miner-fs.service \
            tracker-store.service tracker-extract.service; do
    systemctl --user mask "$unit" 2>/dev/null || true
done
systemctl --user stop 'tracker-*' 2>/dev/null || true
if command -v tracker3 &>/dev/null; then
    tracker3 reset --hard 2>/dev/null || true
elif command -v tracker &>/dev/null; then
    tracker reset --hard 2>/dev/null || true
fi

echo "==> Vypínám kontrolu/stahování aktualizací na pozadí..."
gsettings set org.gnome.software download-updates false 2>/dev/null || true
gsettings set org.gnome.software download-updates-notify false 2>/dev/null || true
systemctl --user mask gnome-software.service 2>/dev/null || true
sudo systemctl mask packagekit.service 2>/dev/null || true
# Jen časovač automatického obnovování snapů, ne snapd samotné - snap
# balíčky (pokud nějaké systém používá) dál fungují, jen se
# nekontrolují pořád na pozadí.
sudo systemctl disable --now snapd.refresh.timer 2>/dev/null || true

echo "==> Vypínám hlášení pádů a sběr diagnostiky (Ubuntu)..."
sudo systemctl disable --now whoopsie.service 2>/dev/null || true
sudo systemctl disable --now apport.service 2>/dev/null || true

echo "==> Vypínám kontakty/kalendář (Evolution Data Server) - appka"
echo "    nepoužívá GNOME kalendář ani kontakty..."
systemctl --user mask evolution-source-registry.service \
    evolution-calendar-factory.service \
    evolution-addressbook-factory.service 2>/dev/null || true

echo "==> Vypínám sdílení souborů/plochy a zálohování na pozadí..."
systemctl --user mask gnome-remote-desktop.service 2>/dev/null || true
systemctl --user mask gnome-user-share.service 2>/dev/null || true
systemctl --user mask deja-dup-monitor.service 2>/dev/null || true

echo "==> Vypínám animace GNOME (drobná úspora, appka běží fullscreen"
echo "    a stejně je přes ně vidět málokdy)..."
gsettings set org.gnome.desktop.interface enable-animations false 2>/dev/null || true

echo
echo "Hotovo. Restart appky/desky se nevyžaduje, změny se projeví"
echo "postupně samy (většina služeb prostě příště nenaběhne)."
echo
echo "Návrat kteréhokoliv kroku zpět: 'systemctl --user unmask <jednotka>'"
echo "(nebo 'sudo systemctl unmask <jednotka>' pro systémové), případně"
echo "zpátky přes gsettings s hodnotou 'true' místo 'false'."
