Open Source Autoradio do Linux
==============================
Autorádio pro Linux (Orange Pi 5 Pro a podobné desky), postavené na PyQt5. Běží jako jedno stálé okno (`main.py`) - jednotlivé aplikace jsou "vestavěné stránky" v `QStackedWidget`, mezi kterými appka přepíná okamžitě, bez zakládání nového procesu. Jen skutečně externí program (GNOME Maps pro Navigaci) se spouští jako samostatný proces, protože jinak to nejde - ale i ten appka přepne do stejného fullscreen vzhledu jako zbytek appky.

![desktop](printscreen/desktop.jpg)

## Základní moduly
Většina modulů běží celá v Pythonu a využívá PyQt5. Ikony použité v appce jsem stáhnul z https://icons8.com/, ikony pro Domů, Bluetooth a BT Hudbu jsem dokreslil ve stejném stylu. Nahoře je stavový pruh s *datem* a *časem*, dole lišta (dock) pro rychlé přepínání mezi aplikacemi - všechny moduly mají společný *StyleSheet* (`style.py`), takže jde vzhled celé appky změnit na jednom místě.

Hudební přehrávač
----------------------------------
Přehrávač lokální hudby (mp3/wav/ogg/flac - cokoliv, co zvládne VLC), napsaný celý v Pythonu nad `python-vlc`. Tlačítko "+" umožňuje vybrat víc skladeb najednou - vytvoří se z nich fronta, kterou appka po dohrání aktuální skladby sama posouvá na další. Kliknutím na skladbu v seznamu se na ni dá skočit přímo, tlačítka Předchozí/Další frontu posouvají ručně, koš vyprázdní celou frontu. Progress bar (a s ním spojené pravidelné dotazování VLC na pozici) běží jen dokud je stránka Hudba opravdu na obrazovce - přehrávání samotné jede dál na pozadí i při přepnutí na jinou appku.

![desktop](printscreen/music_player.jpg)

Youtube a YouTube Music
----------------------------------
Běží přímo vestavěné v aplikaci přes `QWebEngineView` - žádné samostatné okno Chromia, žádná cizí horní lišta prohlížeče kolem. Sestavují se líně, až při prvním otevření (ne hned při startu appky), takže appka naskočí rychle - jakmile jednou stránku otevřeš, zůstává už sestavená a další přepnutí na ni je okamžité. Adresu, na kterou se stránka otevře, lze změnit v `youtube.py` / `youtube_music.py` (proměnná `URL`).

FM Radio
----------------------------------
FM Rádio, napsané celé v Pythonu nad `rtl_fm` (z balíčku `rtl-sdr`) a `aplay`. Pro funkci je potřeba SDR dongle - otestováno s RTL-SDR V4 (viz poznámka o V4 v sekci Potřebné knihovny, kdyby přesto nastal problém se signálem). Nejdůležitější věc pro kvalitu příjmu je ale anténa, která dělá tak 80 % výsledného zvuku.

Až 6 oblíbených stanic se dá uložit tlačítkem "Uložit stanici" (nebo klepnutím na prázdný slot), appka je drží v souboru *fm_presets.json* i po restartu. Přebarvování tlačítek oblíbených stanic (aby se zvýraznila ta aktuálně naladěná) se přepočítává až po zastavení posuvníku frekvence na 0,5 s, ne při každém posunu - jinak by to při plynulém tažení dělalo zbytečnou práci desítkykrát za sekundu.

![desktop](printscreen/FM_radio.jpg)

Video přehrávač
----------------------------------
Jednoduché okno jako spouštěč VLC přehrávače - appka jen zprostředkuje výběr souboru, samotné přehrávání pak běží ve vlastním okně VLC na celou obrazovku. Video by šlo teoreticky vykreslovat přímo uvnitř appky (embedovaný VLC widget), ale spolehlivost takového přístupu silně závisí na konkrétní kombinaci GPU/mesa ovladačů na ARM desce - předání práce samotnému VLC (který má vlastní, dobře odladěný pipeline pro hardwarové dekódování) je robustnější volba.

DAB
----------------------------------
Vlastní DAB/DAB+ modul, napsaný stejným stylem jako ostatní appky - ne jen spouštěč cizího programu. Skutečné DAB/DAB+ demodulování (OFDM, Reed-Solomonovo FEC, MPEG dekódování) je ale seriózní DSP práce, kterou by nedávalo smysl znovu psát od nuly v Pythonu - místo toho appka na pozadí spouští **`welle-cli`** (bezhlavá varianta stejného enginu, který pohání welle.io), a s ním mluví přesně tak, jak appka mluví i s ostatními službami: přes malý webserver, který `welle-cli` sám nabízí.

Jak to funguje: appka spustí `welle-cli -c <kanál> -w 7979` na pozadí, pak se stejně jako modul Počasí (přes `requests`) ptá na `http://127.0.0.1:7979/mux.json`, dokud `welle-cli` nenajde na daném kanálu nějaké stanice. Jakmile je najde, appka je ukáže v seznamu - klepnutím na stanici appka pustí `http://127.0.0.1:7979/mp3/<SID>` přes VLC (`python-vlc`), stejně jako by pustila lokální soubor v Hudbě. Kanál se vybírá ze standardního rastru Band III (5A-13F) v rozbalovací nabídce.

Dotazování na seznam stanic (`/mux.json`) se stejně jako u BT Hudby zastavuje, když stránka DAB není na obrazovce - ale samotné přehrávání (stejně jako u FM Rádia) běží dál na pozadí i při přepnutí jinam, dokud nezmáčkneš Stop.

**Důležité:** DAB a FM Rádio sdílí stejný SDR dongle - najednou může demodulovat jen jeden z nich. Pokud `welle-cli` po klepnutí na "Vyhledat stanice" hned spadne (appka to pozná a napíše), zkontroluj, že zrovna nehraje FM Rádio.

Počasí
----------------------------------
Modul má svůj API klíč, kterým se hlásí na https://openweathermap.org/, odkud bere data pro Prahu (teplota, rychlost větru, vlhkost, oblačnost) a k tomu přiřazuje odpovídající obrázek ze složky `icons/weather`. Síťový dotaz běží v samostatném vlákně (`QThread`), takže i kdyby internet byl pomalý nebo úplně nedostupný, zbytek appky zůstane plynulý. Všechny naposledy stažené údaje appka ukládá do *weather_cache.json* - když není připojení k internetu, načte je odtamtud a napíše k nim datum a čas posledního uložení, ať je jasné, že jde o starší data.

Vyhledávač (Web)
----------------------------------
Obecné prohlížení webu - stejně jako YouTube/YouTube Music běží vestavěně přes `QWebEngineView`, ne jako samostatný proces Chromia (dřívější řešení bylo znatelně pomalejší na otevření a jako samostatné okno ukazovalo GNOME lištu kolem sebe). Výchozí adresa (`https://www.google.com`) se dá změnit v `web.py` (proměnná `URL`).

Nastavení
----------------------------------
Tlačítko Wi-Fi otevírá přímo panel nativního **GNOME nastavení** (`gnome-control-center wifi`), pokud by chybělo, zkusí se jako záloha `nm-connection-editor`. Tlačítko **Výstup zvuku** otevírá panel Zvuku (`gnome-control-center sound`, záložně `pavucontrol`) pro výběr výstupního zařízení (jack, USB zvukovka, HDMI, spárovaný Bluetooth reproduktor...) - párování Bluetooth samotné se řeší přímo v modulu BT Hudba, tady je to jen výběr, kam má jít zvuk. Posuvník hlasitosti ovládá `pactl` a je debouncovaný stejně jako FM přebarvování - `pactl` se zavolá až po zastavení tažení, ne při každém pixelu. Poslední tlačítko appku rovnou ukončí - určené pro nasazení, kde appka běží na celou obrazovku a jinak by nebyla čím zavřít.

![desktop](printscreen/nastaveni.jpg)

Barvy (Vzhled)
----------------------------------
Ovládání témat - 6 barev (**fialová**, **červená**, **modrá**, **zelená**, **oranžová**, **růžová**), ke každé patří odpovídající tapeta na domovské obrazovce. Nová barva i tapeta se aplikují okamžitě po klepnutí, bez restartu appky - přebarví se rázem celá appka (dock, lišty, tlačítka), protože všechny sdílí jeden centrální `style.py`.

![desktop](printscreen/barvy.jpg)

BT Hudba
----------------------------------
Ukazuje **co se právě přehrává na telefonu připojeném přes Bluetooth** - název skladby, interpreta, album a stav přehrávání, plus tlačítka Předchozí/Přehrát-Pauza/Další. Tlačítko **"Zviditelnit pro párování"** zapíná/vypíná viditelnost desky pro spárování z telefonu (`bluetoothctl discoverable/pairable on`) - je to jediné tlačítko s Bluetooth tématem v appce, párování a přehrávání zvuku jsou ale ve skutečnosti tři různé věci, které musí fungovat zaráz (zviditelnění, potvrzení párování přes `bt-agent`, a samotný zvukový Bluetooth modul) - podrobný rozpis je v sekci Potřebné knihovny níže, kdyby přehrávání z telefonu nešlo.

Funguje to přes **BlueZ AVRCP** rozhraní (`org.bluez.MediaPlayer1` na systémové D-Bus sběrnici) - jakmile telefon streamuje hudbu do desky přes Bluetooth (A2DP), BlueZ automaticky zpřístupní i informace o přehrávané skladbě a dálkové ovládání, ať už je telefon Android nebo iPhone. Modul se na tohle rozhraní jen dívá, nepotřebuje žádné vlastní párování navíc. Data se obnovují každé 2 sekundy, ale jen dokud je stránka opravdu na obrazovce (viz sekce Výkon) - dřív běželo tohle dotazování na pozadí pořád, což appku pravidelně krátce zasekávalo.

Navigace
----------------------------------
Spouštěč nativní aplikace **GNOME Maps** (`gnome-maps`) - appka ho přes `wmctrl` navíc přepne do fullscreen, aby vypadal stejně jako zbytek appky, bez GNOME lišty kolem. Pro určení polohy s USB GPS přijímačem ("GPS mouse") viz podrobný postup níže.

**Určování polohy s GPS přijímačem VK-162 ("GPS mouse", u-blox čip):** GNOME Maps si polohu bere ze systémové služby **GeoClue2**, která o USB GPS zařízení sama o sobě neví. VK-162 je založený na u-blox čipu a hlásí se jako standardní USB sériové zařízení (`/dev/ttyACM0`), takže funguje bez jakýchkoliv driverů - jen ho je potřeba propojit s GeoClue2. Postup:

**1. Ověř, že hardware sám o sobě funguje** (nezávisle na GNOME Maps):
```
sudo apt install gpsd gpsd-clients
sudo gpsd /dev/ttyACM0 -F /var/run/gpsd.sock
cgps -s
```
(Za `/dev/ttyACM0` dosaď skutečné zařízení - zjistíš ho přes `ls /dev/ttyACM* /dev/ttyUSB*` po připojení, nebo `dmesg | tail` hned po zapojení.) `cgps` by měl ukázat souřadnice, jakmile přijímač "chytí" satelity - venku i pár desítek sekund, u okna to VK-162 zvládne i uvnitř, v hlubším vnitrozemí budovy nemusí chytit vůbec.

**2. Propoj GPS s GeoClue2 přes `gps-share`** - malý nástroj postavený přímo pro tenhle účel (na rozdíl od `gpsd` umí data poslat rovnou do GeoClue2 přes unix socket, který GeoClue2 podporuje nativně):
```
sudo apt install cargo libudev-dev pkg-config build-essential git
git clone https://github.com/zeenix/gps-share.git
cd gps-share
cargo build --release
sudo cp target/release/gps-share /usr/local/bin/
```

**3. Spouštěj `gps-share` jako systémovou službu**, ať běží na pozadí od startu:
```
sudo tee /etc/systemd/system/gps-share.service > /dev/null << 'EOF'
[Unit]
Description=GPS to GeoClue2 bridge (gps-share)
After=multi-user.target

[Service]
ExecStart=/usr/local/bin/gps-share -s /var/run/gps-share.sock -b 9600 -a -x /dev/ttyACM0
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now gps-share.service
```
(`-s` = poslouchej na unix socketu, `-b 9600` = rychlost VK-162, `-a` = nezveřejňovat přes Avahi na síť, `-x` = neposlouchat na TCP - v autě stačí čistě lokální socket, žádné sdílení po síti.)

**4. Řekni GeoClue2, ať ten socket používá:**
```
sudo mkdir -p /etc/geoclue/conf.d
sudo tee /etc/geoclue/conf.d/99-gps-share.conf > /dev/null << 'EOF'
[network-nmea]
enable=true
nmea-socket=/var/run/gps-share.sock
EOF
sudo systemctl restart geoclue
```

**5. Povol appkám přístup k poloze bez agenta** - GeoClue2 běžně nechá o povolení rozhodovat běžící "agent" (na běžném GNOME desktopu je to gnome-shell, který se zeptá "povolit této appce polohu?"). Pokud appka běží v režimu bez gnome-shellu, žádný agent neexistuje a GeoClue2 by defaultně zamítl úplně všechny požadavky na polohu (`AccessDenied: Geolocation disabled for UID 1000`). Řešení je obejít potřebu agenta explicitním povolením konkrétních aplikací:
```
sudo tee /etc/geoclue/conf.d/99-allow-apps.conf > /dev/null << 'EOF'
[where-am-i]
allowed=true
system=false
users=

[org.gnome.Maps]
allowed=true
system=false
users=
EOF
sudo systemctl restart geoclue
```
(Pokud appka běží v doporučeném režimu nad GNOME - viz sekce Automatický start - gnome-shell už agenta poskytuje sám a tenhle krok není potřeba.)

**6. Ověř, že GeoClue2 polohu skutečně má** (ukáže ji ještě předtím, než vůbec otevřeš GNOME Maps):
```
sudo apt install geoclue-2-demo
/usr/libexec/geoclue-2.0/demos/where-am-i
```
Měly by se objevit reálné souřadnice s `Description: GPS` (ne `GeoIP`). Pokud furt ukazuje jen přibližnou polohu podle IP adresy, zkontroluj `journalctl -u gps-share -u geoclue` - tam uvidíš, jestli `gps-share` vůbec dostává data z GPS.

Jakmile `where-am-i` ukáže správnou polohu, GNOME Maps ji použije automaticky - není potřeba nic dalšího nastavovat.

## Potřebné knihovny
Tento seznam odpovídá tomu, co appka v aktuální podobě opravdu volá v kódu (`main.py` a moduly, které importuje/spouští) - žádné položky navíc "pro jistotu". Balíčky jsou pojmenované podle Ubuntu/Debianu (na jiné distribuci ARM desky se názvy mohou lišit).

**Python a PyQt5:**
 - `python3`
 - `python3-pip`
 - `python3-pyqt5` - základ celého UI
 - `python3-pyqt5.qtwebengine` - vestavěné YouTube, YouTube Music a Web (`QWebEngineView`)
 - `python3-vlc` - Python vazby na VLC, používá hudební přehrávač i DAB modul (přehrávání staženého MP3 streamu z `welle-cli`)
 - `python3-requests` - modul Počasí (OpenWeatherMap API) i DAB (dotazování `welle-cli` na seznam stanic)
 - `python3-dbus` - modul BT Hudba (čte info o přehrávané skladbě a ovládá přehrávání přes BlueZ AVRCP na systémové D-Bus sběrnici)

**Systémové programy, které appka spouští:**
 - `vlc` - přehrávání videa (Video modul) i podkladová knihovna pro `python3-vlc` (Hudba, DAB)
 - `rtl-sdr` (poskytuje `rtl_fm`) + SDR dongle a anténa - FM Rádio modul. Funguje otestovaně i s RTL-SDR V4 (viz poznámka o V4 níže, kdyby přesto byly problémy se signálem).
 - `alsa-utils` (poskytuje `aplay`) - výstup zvuku z FM Rádia
 - `welle.io` (balíček poskytuje i `welle-cli`) - DAB modul. Appka používá jen bezhlavou `welle-cli` část, ne GUI aplikaci welle.io samotnou, takže QML runtime moduly (potřebné jen pro GUI) appka nevyžaduje.
 - `gnome-maps` - Navigace modul
 - `gpsd`, `gpsd-clients` - ověření, že GPS přijímač ("GPS mouse") sám o sobě funguje, nezávisle na GNOME Maps - viz modul Navigace výše
 - `cargo`, `libudev-dev`, `pkg-config`, `build-essential`, `git` - sestavení `gps-share` ze zdroje (propojuje GPS s GeoClue2/GNOME Maps)
 - `geoclue-2-demo` - ověření, že GeoClue2 (a tedy GNOME Maps) reálně dostává polohu z GPS
 - `wmctrl` - doporučeno pro Navigaci: když je okno GNOME Maps už otevřené, appka ho jen přepne do popředí místo spouštění druhé instance, a navíc ho přepne do fullscreen (stejně jako appka samotná), aby kolem něj nebylo vidět GNOME horní lištu. Bez `wmctrl` modul pořád funguje, jen jako běžné okno s GNOME lištou kolem.
 - `gnome-control-center` - Wi-Fi a Výstup zvuku v Nastavení (appka cílí na GNOME desktop)
 - `network-manager-gnome` (poskytuje `nm-connection-editor`) - záložní Wi-Fi nástroj, pokud by `gnome-control-center` chybělo
 - `pavucontrol` - záložní nástroj pro výběr výstupního zařízení zvuku, pokud by `gnome-control-center` chybělo
 - `bluez` (poskytuje `bluetoothctl`) - zviditelnění desky pro párování (tlačítko v modulu BT Hudba) i modul BT Hudba samotný
 - `pulseaudio-module-bluetooth` **nebo** `libspa-0.2-bluetooth` - aby deska uměla přijímat a přehrávat zvuk streamovaný z telefonu přes Bluetooth (A2DP sink); podle toho, jestli systém používá PulseAudio, nebo PipeWire
 - `pulseaudio-utils` nebo `pipewire-pulse` (poskytuje `pactl`) - ovládání hlasitosti v Nastavení

Instalace na Ubuntu/Debianu (uprav podle skutečně nainstalovaného desktopu):
```
sudo apt install python3 python3-pip python3-pyqt5 python3-pyqt5.qtwebengine \
    python3-vlc python3-requests python3-dbus vlc rtl-sdr alsa-utils welle.io \
    gnome-maps wmctrl gnome-control-center network-manager-gnome pavucontrol \
    bluez bluez-tools pulseaudio-utils

# jedno z těchto dvou, podle toho jestli systém běží na PulseAudio nebo
# PipeWire (nutné, aby šel na desku streamovat zvuk z telefonu):
sudo apt install pulseaudio-module-bluetooth
# nebo:
sudo apt install libspa-0.2-bluetooth
```

**Bluetooth: párování vs. deska jako Bluetooth reproduktor** - tlačítko "Zviditelnit pro párování" v modulu BT Hudba zviditelní desku (`bluetoothctl discoverable/pairable on`), aby ji telefon vůbec našel a mohl se k ní připojit a streamovat na ni hudbu (deska pak funguje jako Bluetooth reproduktor / A2DP sink). Žádné samostatné "spravovat spárovaná zařízení" tlačítko v Nastavení už není (nahrazené tlačítkem Výstup zvuku) - pro zapomenutí/odstranění starého spárování použij přímo `bluetoothctl remove <MAC adresa>` v terminálu.

Aby přehrávání z telefonu fungovalo, jsou potřeba tři různé věci najednou - pokud nejde, projdi je popořadě:
1. **Zviditelnění** - tlačítko v modulu BT Hudba, jen říká telefonu "tady jsem".
2. **Potvrzení párování** - bez běžícího "agenta" nemá BlueZ, kdo by příchozí párování potvrdil, takže by se telefon nespároval, i když desku najde. V obou automatických režimech (`kiosk/install-gnome-autostart.sh` i `kiosk/install-kiosk.sh`) se o tohle stará `bt-agent` (balíček `bluez-tools`), který běží na pozadí a páry potvrzuje automaticky. Pokud appku spouštíš mimo tyhle skripty, spusť si `bt-agent -c NoInputNoOutput &` ručně (nebo párování jednou potvrď přes `gnome-control-center`/`bluetoothctl`).
3. **Přehrávání zvuku** - i po úspěšném spárování potřebuje systém balíček pro Bluetooth audio (`pulseaudio-module-bluetooth` nebo `libspa-0.2-bluetooth`, viz výše) - bez něj se telefon spáruje, ale zvuk nikam nepůjde. Ověření, že modul opravdu běží: `pactl list modules short | grep bluetooth` (PulseAudio) nebo `wpctl status` (PipeWire - Bluetooth zařízení by se mělo objevit v sekci Audio/Sinks po připojení telefonu). Které zařízení je aktuálně výstupní se dá zkontrolovat/přepnout přímo v appce - Nastavení → Výstup zvuku.

Pokud i po tomhle telefon nenabídne desku jako reproduktor v přehrávání hudby, zkontroluj na telefonu, že se skutečně připojil profil "Média/Audio" (A2DP), ne jen "Telefonní hovory" (HFP) - některé telefony je nabízí zvlášť.

**Jen pro kiosk režim bez GNOME** (viz sekce "Automatický start" níže):
 - `xserver-xorg`, `xinit`, `x11-xserver-utils` - holý X server, appka nepotřebuje celý desktop
 - `matchbox-window-manager` - odlehčený okenní manažer (žádný panel, žádná plocha)
 - `unclutter` - schová kurzor myši, když se nehýbe (appka je určená pro dotykovou obrazovku)
 - `onboard` - dotyková klávesnice, samostatně fungující i bez GNOME
 - `at-spi2-core` - aby `onboard` poznal, kdy je aktivní textové pole (auto-show)
 - `dbus-x11` (poskytuje `dbus-launch`) - D-Bus session sběrnice bez desktop prostředí
 - `dconf-cli` - nastavení výchozích hodnot pro `onboard` (auto-show, ukotvení)

Instalátor si tyhle balíčky nainstaluje sám (`kiosk/install-kiosk.sh`), ruční instalace není potřeba - jsou tu uvedené jen pro přehled.

**Poznámka k welle.io/welle-cli (DAB):** appka spouští jen `welle-cli`, ne GUI aplikaci welle.io - žádné QML moduly navíc tedy nejsou potřeba. Kdybys ale chtěl zprovoznit i samotné GUI welle.io (mimo appku, jen pro ladění signálu), na Qt6 systémech (ověřeno na Orange Pi 5 Pro/Armbian) pomůže `sudo apt install qml6-module-qtcore qml6-module-qtquick-dialogs`, na starších Qt5 systémech `qml-module-qtquick2 qml-module-qtquick-controls qml-module-qtquick-controls2 qml-module-qtquick-dialogs qml-module-qtquick-layouts qml-module-qtgraphicaleffects qml-module-qtcharts`. Spusť `welle-io` přímo v terminálu a přečti si chybovou hlášku (`module "XYZ" is not installed`), ať víš, který balíček přesně chybí.

**Poznámka k RTL-SDR V4:** V4 používá jiný tuner (R828D) než starší V3 a u některých systémů/starších verzí balíčku `rtl-sdr` býval problém (žádný signál, špatná frekvence, zkreslený zvuk) - vyžadovalo to aktualizovaný ovladač (fork RTL-SDR Blog). Na aktuálních systémech uvedených v tomhle READMU ale balíčkový `rtl-sdr` s V4 dongle otestovaně funguje bez problémů (jak pro FM Rádio, tak pro DAB), takže postup níže potřebuješ jen v případě, že bys s obyčejným `rtl-sdr` narazil na některý z těch příznaků:
```
sudo apt purge '^librtlsdr'
sudo rm -rvf /usr/lib/librtlsdr* /usr/include/rtl-sdr* /usr/local/lib/librtlsdr* \
    /usr/local/include/rtl-sdr* /usr/local/include/rtl_* /usr/local/bin/rtl_*

sudo apt install libusb-1.0-0-dev git cmake pkg-config build-essential

git clone https://github.com/rtlsdrblog/rtl-sdr-blog
cd rtl-sdr-blog
mkdir build && cd build
cmake ../ -DINSTALL_UDEV_RULES=ON
make
sudo make install
sudo cp ../rtl-sdr.rules /etc/udev/rules.d/
sudo ldconfig

# ať kernel dongle nezabere jako DVB-T TV tuner dřív, než ho chytí rtl_fm/welle-cli
echo 'blacklist dvb_usb_rtl28xxu' | sudo tee /etc/modprobe.d/blacklist-rtlsdr.conf
sudo reboot
```
Tenhle ovladač je zpětně kompatibilní i se staršími dongly (V3 a generickými), takže ho klidně použij i bez V4.

S těmito knihovnami by appka měla fungovat správně. Pokud na zařízení nějaká volitelná knihovna (`python3-vlc`, `python3-pyqt5.qtwebengine`, `python3-requests`, `python3-dbus`) chybí, appka to sama pozná a místo pádu zobrazí pro danou stránku hlášku „není dostupné" - zbytek appky běží dál.

## Výkon
Pár míst v appce dělá pravidelně se opakující práci na pozadí (kontrola BT přehrávače, aktualizace progress baru u hudby, dotazování DAB na seznam stanic, síťový dotaz na počasí) - u těch platí jedno pravidlo: **nic z toho neběží, když se to zrovna nedívá na obrazovku, a nic z toho neblokuje zbytek appky, když to běží**.

- **BT Hudba, Hudba, DAB** - dotazování/aktualizace běží jen dokud je daná stránka opravdu zobrazená (`showEvent`/`hideEvent` zastaví a znovu spustí příslušný časovač). Dřív běželo dotazování BT přehrávače na pozadí pořád, i na úplně jiné stránce - každé 1,5 s to udělalo blokující D-Bus dotaz přímo v GUI vlákně, což se projevovalo jako pravidelné krátké zaseknutí celé appky bez ohledu na to, co uživatel zrovna dělal. **Samotné přehrávání** (FM Rádio, DAB, Hudba) se od tohohle liší záměrně - to běží dál na pozadí i po přepnutí na jinou stránku, přesně jak by se čekalo od rádia v autě.
- **FM Rádio** - přebarvování 6 tlačítek oblíbených stanic (aby se zvýraznila ta aktuálně naladěná) se dřív přepočítávalo při každičkém posunu posuvníku frekvence - při plynulém tažení to bylo klidně desítkykrát za sekundu. Teď se to (stejně jako restart rádia) čeká, až se posuvník na 0,5 s zastaví. Stejný princip platí pro posuvník hlasitosti v Nastavení.
- **Počasí** - síťový dotaz na openweathermap.org běží v samostatném vlákně (`QThread`), takže i kdyby internet byl pomalý nebo nedostupný (dotaz čeká až 5 sekund), zbytek appky zůstane plynulý - bez tohohle by se GUI na tu dobu úplně zaseklo hned po otevření stránky. Appka při ukončení navíc počká, až se případně ještě běžící dotaz dokončí, než se okno doopravdy zavře - bez toho hrozil tvrdý pád při zavírání appky uprostřed dotazu.
- **DAB a FM Rádio sdílí jeden SDR dongle** - to není otázka výkonu appky, ale fyzického hardwaru: najednou může demodulovat jen jeden z nich (viz modul DAB výše).

## Automatický start (bez nutnosti se přihlašovat/spouštět appku ručně)
Pro nasazení v autě appka nemá běžet jen tehdy, když ji někdo ručně spustí - má naskočit sama, na celou obrazovku, hned po zapnutí desky. Ve složce `kiosk/` jsou dva různé způsoby, jak toho dosáhnout - liší se v tom, jestli pod appkou běží normální GNOME desktop, nebo ne.

**Doporučený způsob: appka nad běžícím GNOME (`install-gnome-autostart.sh`).** Appka se spustí automaticky hned po přihlášení do normální GNOME session a běží přes celou obrazovku nad ní. V reálném provozu (ověřeno na Orange Pi 5 Pro) se ukázalo být spolehlivější než alternativa níže - fullscreen okna, dotyková klávesnice i párování Bluetooth fungují správně, protože běží skutečný `gnome-shell` s plnou podporou window manageru, a GeoClue2 (poloha pro GNOME Maps) funguje bez dalšího dolaďování, protože `gnome-shell` běží jako jeho agent automaticky. Volitelný skript `trim-gnome.sh` (viz níže) pak zvládne většinu té "ceny navíc" (spotřeba paměti/CPU běžícího GNOME) srazit dolů bez ztráty těchhle výhod.

**Alternativa: appka bez GNOME vůbec (`install-kiosk.sh`).** Bez GDM/gnome-shellu, jen holý X server + odlehčený okenní manažer *matchbox* + appka. V teorii úspornější, ale v reálném testování se ukázaly problémy - dotyková klávesnice (`onboard`) se špatně vykresluje a nezabírá celou obrazovku, a některá okna se chovají nespolehlivě, protože `matchbox` nemá plnou podporu pro fullscreen/dialogová okna jako skutečný desktop. Necháváme ho zdokumentovaný pro slabší desky, ale defaultně doporučujeme variantu s GNOME výše.

### Automatický start nad GNOME (doporučeno)

Postup:
```
cd /home/orangepi/Autoradio/kiosk
chmod +x install-gnome-autostart.sh
./install-gnome-autostart.sh
```
(Bez `sudo` - spouští se jako běžný uživatel, protože jde o nastavení jeho vlastního účtu; jednotlivé kroky uvnitř, co potřebují oprávnění správce, si o heslo řeknou samy.)

Skript:
1. Nainstaluje podporu pro Bluetooth audio (`bluez`, `bluez-tools`, `pulseaudio-module-bluetooth`/`libspa-0.2-bluetooth`) a `wmctrl`.
2. Nastaví appku (a záložního `bt-agent` pro automatické potvrzování párování) jako GNOME autostart aplikace (`~/.config/autostart/`).
3. Vypne uspávání/zamykání obrazovky.
4. Přepne GNOME session z Wayland na X11 (`WaylandEnable=false` v GDM konfiguraci) - appka i `wmctrl` jsou nástroje pro X11; pod Waylandem běží appka jen přes XWayland kompatibilitu, kde bylo chování dotykové klávesnice i `wmctrl` nespolehlivé.
5. Zapne vestavěnou dotykovou klávesnici GNOME (viz sekce Dotyková klávesnice níže).

Poslední krok je ruční, jde jen přes GUI: **Nastavení → Uživatelé → zapnout "Automatické přihlášení"** pro tvůj účet. Pak `sudo reboot` - appka by po restartu měla naskočit sama, na celou obrazovku, přímo po přihlášení (teď už na X11, ne na Wayland).

**Zrušení autostartu appky** (appka zmizí, GNOME desktop zůstává normální):
```
rm ~/.config/autostart/autoradio.desktop
rm ~/.config/autostart/bt-agent-autostart.desktop
```

**Návrat na Wayland** (kdykoliv v budoucnu):
```
sudo sed -i 's/^WaylandEnable=false/WaylandEnable=true/' /etc/gdm3/custom.conf
sudo reboot
```

### Omezení zátěže GNOME
Appka běží nad plným GNOME kvůli spolehlivosti (viz výše), ale běžná desktopová instalace má zapnutou spoustu služeb na pozadí, které appka nikdy nevyužije - indexování souborů, kontrola aktualizací, kalendář/kontakty, sdílení plochy, hlášení pádů... Skript `kiosk/trim-gnome.sh` tohle všechno vypne, **aniž by sahal na `gnome-shell`/`mutter` samotné** - to je přesně to, co appce zajišťuje spolehlivý fullscreen, dotykovou klávesnici a Bluetooth, takže to zůstává beze změny.

```
cd ~/Autoradio/kiosk
chmod +x trim-gnome.sh
./trim-gnome.sh
```

Konkrétně vypne/maskuje: indexování souborů (Tracker), kontrolu a stahování aktualizací na pozadí (GNOME Software, PackageKit, časovač automatického obnovování snapů), hlášení pádů (`whoopsie`, `apport`), synchronizaci kalendáře/kontaktů (Evolution Data Server), sdílení plochy/souborů a zálohování na pozadí, a animace uživatelského rozhraní (appka běží fullscreen, takže je stejně vidí málokdy). Každý krok jde nezávisle vrátit zpět - viz komentáře přímo ve skriptu (`systemctl unmask`, případně gsettings zpátky na `true`). Skript je bezpečné spustit i opakovaně, nic nerozbije už rozběhnutou appku ani není potřeba po něm restart.

### Automatický start bez GNOME (alternativa, viz caveaty výše)
Ve složce `kiosk/` je jednorázový instalátor, který:

1. Vypne grafické přihlašovací okno (GDM a tedy i celý GNOME desktop), aby se po startu desky nespouštělo.
2. Nastaví automatické přihlášení na tty1 (žádné zadávání hesla).
3. Nainstaluje odlehčený okenní manažer *matchbox* (žádný panel, žádná plocha - jen správa oken, aby fungovala i okna Nastavení Wi-Fi/Bluetooth).
4. Nainstaluje a nastaví dotykovou klávesnici *onboard* (viz níže).
5. Nainstaluje podporu pro Bluetooth audio, aby telefon mohl na desku streamovat hudbu a modul BT Hudba mohl desku zviditelnit pro párování.
6. Appku spustí automaticky přes `startx` hned po přihlášení, na celou obrazovku.

Balíčky, které tenhle režim navíc potřebuje, jsou v sekci "Potřebné knihovny" výše. Instalátor si je nainstaluje sám, ruční instalace není potřeba.

```
cd /home/orangepi/Autoradio/kiosk
chmod +x install-kiosk.sh
sudo ./install-kiosk.sh
sudo reboot
```

Po restartu appka naskočí sama, bez přihlašovací obrazovky a bez GNOME. `gnome-control-center`, `nm-connection-editor` i `blueman-manager` v Nastavení fungují dál normálně - matchbox jen spravuje jejich okna, GNOME shell k tomu není potřeba.

**Návrat ke GNOME** (kdykoliv v budoucnu, např. pro přechod na variantu výše):
```
sudo systemctl enable --now display-manager.service
sudo rm /etc/systemd/system/getty@tty1.service.d/override.conf
sudo systemctl daemon-reload
sudo reboot
```

### Dotyková klávesnice
**Pokud jsi zvolil automatický start nad GNOME** (doporučeno), appka používá výhradně vestavěnou klávesnici GNOME (Screen Keyboard) - žádný `onboard` navíc. `install-gnome-autostart.sh` ji zapne automaticky (`org.gnome.desktop.a11y.applications screen-keyboard-enabled`), včetně přepnutí session na X11 (viz výše), pod kterým appka spolehlivě signalizuje aktivní textové pole přes accessibility rozhraní (`QT_ACCESSIBILITY=1` a Chromium `--force-renderer-accessibility`, oboje už appka nastavuje sama v `run_autoradio.sh`). Dá se doladit v Nastavení → Přístupnost → Klávesnice na obrazovce.

Důležité omezení, o kterém stojí za to vědět: GNOME nedává zvenčí žádný spolehlivý způsob, jak tuhle klávesnici ručně vyvolat na povel - potvrzeno přímo vývojářem gnome-shellu (žádné D-Bus rozhraní pro to neexistuje, jen automatické zobrazení na focus). Appka proto v tomhle režimu nemá žádné tlačítko na ruční zapnutí/vypnutí klávesnice - pokud by se auto-show v nějakém konkrétním poli nespustilo, jinou možnost než zkusit kliknout znovu / do jiného pole bohužel není.

**Pokud jsi zvolil variantu bez GNOME**, GNOME klávesnice bez gnome-shellu vůbec nefunguje, takže instalátor tam pořád používá `onboard` - ten funguje nezávisle na desktop prostředí a má navíc vlastní D-Bus rozhraní pro ruční zapnutí/vypnutí, které appka využívá přes ikonku klávesnice v dolní liště. V reálném provozu se ale ukázalo, že se `onboard` pod `matchbox` může vykreslovat nespolehlivě a ořezaně - v tom případě je jednodušší přejít na variantu s GNOME výše. Ikonka klávesnice v dolní liště je proto v appce natrvalo - v GNOME režimu jen nemá co ovládat (`onboard` tam neběží), takže klepnutí na ni v tichosti nic neudělá.

### Fyzické tlačítko napájení
Pokud má deska/displej připojené fyzické tlačítko napájení (ACPI power key), stojí za to nastavit, aby jen rovnou vypnulo zařízení, místo aby čekalo na potvrzení v nějakém dialogu:

```
sudo sed -i 's/^#\?HandlePowerKey=.*/HandlePowerKey=poweroff/' /etc/systemd/logind.conf
sudo systemctl restart systemd-logind
```
Ověření: `grep HandlePowerKey /etc/systemd/logind.conf` by měl ukázat `HandlePowerKey=poweroff` bez `#` na začátku. (Pokud by řádek úplně chyběl - neobvyklé - přidej ho ručně: `echo "HandlePowerKey=poweroff" | sudo tee -a /etc/systemd/logind.conf`.)

Appka běžící nad GNOME (doporučená varianta) navíc potřebuje potlačit vlastní potvrzovací dialog GNOME při odhlášení/vypnutí:
```
gsettings set org.gnome.SessionManager logout-prompt false
```

## Historie verzí
Stručný přehled - podrobnosti k jednotlivým bodům jsou popsané výš u příslušných modulů/sekcí.

- **v20** - GNOME autostart už nepoužívá `onboard` vůbec, jen vestavěnou GNOME klávesnici (Screen Keyboard) - ověřeno, že GNOME nemá žádné rozhraní pro ruční vyvolání klávesnice zvenčí, takže appka v tomhle režimu nemá ani tlačítko pro ruční zapnutí/vypnutí. `onboard` zůstává jen u alternativní bare-X varianty (`install-kiosk.sh`), kde GNOME klávesnice bez gnome-shellu nefunguje.
- **v19** - Vlastní modul DAB (nahrazuje spouštěč welle.io GUI, viz modul DAB výše), skript `trim-gnome.sh` na omezení zátěže GNOME, README přeorganizované (historie verzí přesunutá sem na konec, popisy modulů rozšířené).
- **v18** - Fullscreen napříč appkami (welle.io/GNOME Maps přes `wmctrl`), Web vestavěný místo externího Chromia, spolehlivější dotyková klávesnice (přepnutí na X11 + `onboard` vedle GNOME klávesnice), Nastavení: Bluetooth tlačítko nahrazené Výstupem zvuku, fronta v hudebním přehrávači.
- **v17** - Doporučený automatický start nad běžícím GNOME (`install-gnome-autostart.sh`) místo bare-X kiosku - spolehlivější fullscreen, klávesnice i GeoClue2.
- **v16** - GeoClue2 v kiosk režimu bez agenta - explicitní povolení aplikací v `/etc/geoclue/conf.d/`.
- **v15** - Oprava pravidelného zasekávání appky (BT Hudba dotazovalo na pozadí i mimo obrazovku), sloučení Bluetooth ikonek do jedné.
- **v14** - Odebrané vestavěné Mapy (duplicita s Navigací), nový modul BT Hudba.
- **v13** - Podrobný postup pro GPS VK-162 (`gps-share` + GeoClue2 + GNOME Maps).
- **v12** - Potvrzené opravy z reálného nasazení: welle.io Qt6 QML fix, fyzické tlačítko napájení.
- **v11**, **v10** - Opravy po testu na reálném zařízení (chybějící soubor v hudebním přehrávači, layout Počasí, Bluetooth zviditelnění).
- **v9** - Odebrání Spotify (nefunkční), oprava hudebního přehrávače, Bluetooth ikonka v docku.
- **v8** - Dotyková klávesnice (`onboard`) v kiosk režimu.
- **v7** - Přidaný kiosk režim (automatický start bez GNOME, přes `matchbox`).
- **v6** - Kontrola kódu a README, vyšperkovaný retro vzhled (gradienty, LCD panely).
- **v5** - Odebrání Spotify (první pokus), odolnost appky vůči chybějícím volitelným knihovnám.
- **v4** - Ukládání oblíbených stanic ve FM Rádiu, Bluetooth ikonka.
- **v3** - YouTube a YouTube Music vestavěné (`QWebEngineView`) místo spouštění Chromia.
- **v2** - Přechod z více oken na jedno stálé okno (`QStackedWidget`), dock s domečkem, retro vzhled.
