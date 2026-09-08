Open Source Autoradio do Linux
==============================

## Novinky ve verzi 10 (opravy po testu na reálném zařízení)
- **Hudební přehrávač**: tlačítko „+" neotvíralo dialog pro výběr souboru pod kiosk prostředím (matchbox) - vynucený `DontUseNativeDialog` + velikost dialogu shodná s celoobrazovkovým hlavním oknem způsobovaly, že se dialog otevřel za hlavním oknem. Přepsáno na stejné, ověřeně funkční volání jako u Videa.
- **Počasí**: po načtení dat (velká ikona + digitální font) mohl layout narůst nad dostupnou výšku a zatlačit dolní lištu mimo obrazovku. Zúžený layout Počasí + přidaná pojistka v `main.py` (pevný strop výšky obsahové oblasti), která tohle napříč všemi stránkami znemožňuje do budoucna.
- **Bluetooth**: ikonka v docku teď dělá něco jiného než tlačítko v Nastavení - přepíná viditelnost/párovatelnost desky (`bluetoothctl discoverable/pairable`), aby ji telefon našel a mohl na ni streamovat zvuk (deska jako Bluetooth reproduktor / A2DP sink), místo aby jen otevírala GNOME panel pro správu spárovaných zařízení. Doplněné potřebné systémové balíčky pro Bluetooth audio.
- **RTL-SDR V4**: upřesněná poznámka v README - na testovaném zařízení funguje běžný balíček `rtl-sdr` s V4 dongle bez úprav, ovladač ze zdroje je potřeba jen výjimečně.

## Novinky ve verzi 9
- **README**: doplněné varování a přesný postup pro **RTL-SDR V4** - balíčkový `rtl-sdr` z apt repozitářů tenhle dongle často neumí správně inicializovat (jiný tuner než starší V3), takže by FM Rádio modul mohl hlásit prázdné pásmo, špatnou frekvenci nebo zkreslený zvuk. Přidaný návod na instalaci aktualizovaného ovladače (fork RTL-SDR Blog) ze zdroje, včetně blacklistu výchozího DVB-T ovladače.

## Novinky ve verzi 8
- **README**: sekce "Potřebné knihovny" teď obsahuje i balíčky pro kiosk režim (`xserver-xorg`, `matchbox-window-manager`, `onboard`...), včetně vlastního `apt install` příkazu - dřív byly zmíněné jen uvnitř instalačního skriptu, teď je vidět úplný přehled na jednom místě.

## Novinky ve verzi 7
- Přidaná složka **kiosk/** s jednorázovým instalátorem (`install-kiosk.sh`) pro nasazení bez GNOME desktopu - appka po zapnutí desky naskočí sama na celou obrazovku, žádná přihlašovací obrazovka, žádný spuštěný gnome-shell. GDM se dá kdykoliv zase zapnout zpět, viz README sekce "Kiosk režim".
- Přidaná **dotyková klávesnice** (`onboard`) - v kiosk režimu se nastaví tak, aby se sama zobrazovala při psaní kdekoliv v appce (vlastní dialogy, vestavěné YouTube/Mapy) i v externích GTK oknech (např. zadání Wi-Fi hesla). V dolní liště přibyla i ikonka pro ruční zapnutí/vypnutí klávesnice, kdyby se automatické zobrazení někde nespustilo.

## Novinky ve verzi 6
- Kompletní kontrola kódu a opravy drobných nekonzistencí.
- **README opraveno** - sekce "Potřebné knihovny" teď odpovídá tomu, co appka opravdu volá (odebrané nepoužívané položky jako QML moduly, Pillow, OSRM/docker; doplněné skutečně používané `python3-pyqt5.qtwebengine`, `rtl-sdr`, `wmctrl`, `gnome-control-center`). Opravena i sekce o YouTube (už neběží přes Chromium, ale vestavěně) a Navigaci (žádné OSRM, jen spouštěč GNOME Maps).
- **Vyšperkovaný design** - jemné gradienty na tlačítkách, dlaždicích a liště namísto plochých barev, digitální hodiny v horní liště dostaly vlastní "LCD" rámeček, frekvence FM rádia je teď v podsvíceném displeji připomínajícím skutečné autorádio, počasí má hezčí "chipy" pro vlhkost/vítr, a mezi ikonami aplikací a Bluetooth zkratkou v docku přibyla tenká oddělovací čárka. Vše zůstává odlehčené (žádné náročné grafické efekty), aby appka běžela svižně i na slabším ARM hardwaru.

## Novinky ve verzi 5
- **Spotify odebrán.** Nefungoval kvůli tomu, že Spotify Web Player v embedded prohlížeči hlásí chybu (typicky kvůli DRM/Widevine, které Qt WebEngine defaultně nemá) - takže jsem ho z appky úplně odstranil, aby zbytečně nezabíral místo na ploše.
- **Oprava hudebního přehrávače** - tlačítko „+" (výběr skladby) se dřív po spuštění první písničky schovalo a už nešlo přidat/změnit skladbu bez restartu appky. Teď zůstává vidět a funkční po celou dobu.
- Menší oprava odolnosti: pokud se aplikaci (např. hudebnímu přehrávači kvůli VLC) nepodaří inicializovat i přesto, že modul jde naimportovat, appka to teď zachytí a zobrazí hlášku „není dostupné" místo pádu celé aplikace.
- K **OpenTune** (open-source YouTube Music klient pro Android) - prověřil jsem to a jde o reálný projekt, ale jeho webová verze běží přes cizí cloudovou emulaci (Appetize.io), která má jen pár desítek minut zdarma měsíčně, potřebuje stálé rychlé připojení a není myšlená pro celodenní používání v autě. Proto jsem místo toho embedovaný Android emulátor nedělal - appka už ale obsahuje vestavěné **YouTube Music**, což je přesně ten stejný katalog, který OpenTune sám používá, jen bez zbytečné emulace.

## Novinky ve verzi 4
- **Spotify** přibyl jako další aplikace - běží stejně jako YouTube/YouTube Music vestavěně přes `QWebEngineView` (Spotify Web Player), takže funguje i na ARM zařízeních bez instalace nativního Spotify klienta.
- **Bluetooth ikonka** se přesunula z horní lišty do spodního docku a má teď stejný styl jako ostatní ikonky aplikací (černobílá "sticker" ikona, žádný modrý odznak).
- Tlačítka **Wi-Fi** a **Bluetooth** v Nastavení (i ikonka v docku) teď primárně otevírají nativní panely **GNOME nastavení** (`gnome-control-center wifi` / `gnome-control-center bluetooth`), protože aplikace běží na GNOME. Pokud by `gnome-control-center` chybělo, zkusí se `nm-connection-editor` / `blueman-manager` jako záloha.

## Novinky ve verzi 3
- **YouTube a YouTube Music** už neotevírají samostatné okno Chromia. Běží přímo vestavěné v aplikaci (přes `QWebEngineView`, stejně jako Mapy), takže naskočí rychle a mají stejný formát/rámeček jako ostatní stránky - žádná cizí horní lišta prohlížeče.
- Těžší stránky (YouTube, YouTube Music, Mapy, Počasí) se teď sestavují **líně** - až při prvním otevření, ne hned při startu. Aplikace tak naskočí rychleji.
- **FM Rádio** umí ukládat oblíbené stanice (až 6) - tlačítkem *Uložit stanici* nebo klepnutím na prázdný slot `+`. Klepnutím na uloženou stanici se na ni rádio naladí, `🗑` uloženou stanici smaže.
- V horní liště přibyla **ikonka Bluetooth** pro rychlé otevření párování/nastavení zvukového výstupu přes Bluetooth (stejná akce jako v Nastavení, jen o klepnutí blíž).

## Novinky ve verzi 2 (jednotné okno + retro vzhled)
Aplikace nyní běží jako **jedno stálé okno** (`main.py`), ne jako sada oken, která se pořád znovu spouští jako nový python proces. Vlastní PyQt aplikace (Hudba, FM Rádio, Video, Počasí, Nastavení, Vzhled, Mapy) jsou "vestavěné stránky" v `QStackedWidget` a přepínají se okamžitě bez zakládání nového procesu. Jen skutečně externí programy (Chromium pro YouTube/YT Music/Web, welle.io pro DAB, gnome-maps pro Navigaci) se pořád spouští jako samostatný proces, protože jinak to nejde.

Přibyla i **spodní lišta (dock)** s domečkem uprostřed pro rychlý návrat na hlavní obrazovku a rychlé přepínání mezi ostatními aplikacemi jedním klepnutím - podobně jako u Android autorádií. Nahoře je stavový pruh s datem, časem a názvem aktuální stránky. Celý vzhled je předělaný do tmavého "retro" digitálního stylu (`style.py`), který se dá stále přebarvit v modulu **Vzhled** - barva i tapeta se teď navíc aplikují okamžitě, bez restartu aplikace.

Spuštění je stále stejné - `python3 main.py`.

## Základní moduly
Tento program obsahuje spoustu různých modulů. Většina běží v Pythonu a využívá PyQt5 s příslušnými potřebnými moduly. Hlavní desktop aplikace je **main.py**. Po spuštění tohoto kódu se spustí okno, kde lze vybrat různé aplikace. Ikony použité v desktop aplikaci jsem stáhnul z https://icons8.com/, ikony pro Domů a Bluetooth jsem dokreslil ve stejném stylu.

![desktop](printscreen/desktop.jpg)

Na hlavní obrazovce je nahoře stavový pruh s *datem* a *časem* a dole lišta (dock) pro rychlé přepínání mezi aplikacemi.

Hudební přehrávač
----------------------------------
Prvním modulem je hudební přehrávač lokální hudby, který je celý napsaný v Pythonu. Všechny moduly mají společný *StyleSheet*.

![desktop](printscreen/music_player.jpg)

Vzhled všech aplikací je jednotný a čistý. Výhodou je, že v případě potřeby jiného stylu lze tento styl jednoduše změnit pro všechny moduly najednou v souboru *style.py*.

Youtube a YouTube Music
----------------------------------
YouTube a YouTube Music běží přímo vestavěné v aplikaci přes `QWebEngineView` (stejně jako Mapy) - žádné samostatné okno Chromia, žádná cizí horní lišta prohlížeče. Sestavují se navíc líně, až při prvním otevření, takže appka naskočí rychle. Adresu, na kterou se stránka otevře, lze změnit v `youtube.py` / `youtube_music.py` (proměnná `URL`).

FM Radio
----------------------------------
Dalším modulem je FM Rádio, napsané taky celé v Pythonu. Pro funkci tohoto rádia je potřeba SDR dongle. Já jsem si vybral RTL-SDR V4. Nejdůležitější věc je ale anténa, která dělá tak 80 % kvality zvuku. Oblíbené stanice si appka ukládá do souboru *fm_presets.json*.

**Poznámka k V4:** RTL-SDR V4 používá jiný tuner (R828D) než starší V3. Na testovaném zařízení (viz sekce "Potřebné knihovny") funguje běžný balíček `rtl-sdr` s V4 dongle bez problémů. Pokud by přesto FM Rádio hlásilo žádný signál, špatnou frekvenci nebo zkreslený zvuk, řešením je aktualizovaný ovladač - viz box v sekci "Potřebné knihovny".

![desktop](printscreen/FM_radio.jpg)

Video přehrávač
----------------------------------
Dalším modulem je jednoduché okno jako spouštěč VLC přehrávače. Uživatel vyvolá okno, kde si vybere soubor, který chce přehrát, a ten se pak spustí pomocí VLC na celou obrazovku.

DAB
----------------------------------
Další modul není můj vlastní program - na přehrávání DAB jsem použil **Welle.io**. Je to jednoduchý program, který funguje skvěle na přehrávání DAB z RTL-SDR.

Počasí
----------------------------------
Dalším modulem je počasí, které je také vytvořené celé v Pythonu. Funguje to tak, že modul má svůj API klíč, kterým se hlásí na stránku https://openweathermap.org/, ze které bere data. V Pythonu je nastavené, aby to bralo údaje pro Prahu. Bere to údaje o teplotě, rychlosti větru, vlhkosti a o tom, zda je zataženo nebo polojasno atd., a k tomu přiřazuje odpovídající obrázek ze složky icons/weather. Všechny tyto údaje si appka ukládá do souboru *weather_cache.json*. Když není připojení k internetu, načte údaje z tohoto souboru a vypíše je i s datem a časem posledního uložení.

![desktop](printscreen/pocasi.jpg)

Vyhledávač
----------------------------------
Dalším modulem je jenom spouštěč Chromium Browseru (obecné vyhledávání - google.com).

Nastavení
----------------------------------
Dalším modulem je nastavení. Tlačítka Wi-Fi a Bluetooth otevírají přímo příslušný panel nativního **GNOME nastavení** (`gnome-control-center wifi` / `gnome-control-center bluetooth`), protože appka cílí na GNOME desktop. Pokud by `gnome-control-center` na zařízení chybělo, zkusí se jako záloha `nm-connection-editor` / `blueman-manager`. Stejná Bluetooth akce je pro rychlý přístup i jako ikonka ve spodní liště (docku). Program dál dokáže ovládat hlasitost pomocí knihovny *pulseaudio* (`pactl`). Poslední tlačítko je na vypnutí desktop aplikace. Tato funkce je určená pro projekty, kde poběží aplikace na fullscreen a nebude ji možno jinak vypnout.

![desktop](printscreen/nastaveni.jpg)

Barvy (Vzhled)
----------------------------------
Dalším modulem je ovládání témat. Na výběr je 6 barev: **fialová**, **červená**, **modrá**, **zelená**, **oranžová** a **růžová**. K jednotlivým barvám patří příslušné tapety. Nová barva i tapeta se aplikují okamžitě, bez restartu appky.

![desktop](printscreen/barvy.jpg)

Mapy
----------------------------------
Dalším modulem je jednoduché vestavěné zobrazení webových map (OpenStreetMap přes Leaflet), které funguje jen s připojením k internetu.

Navigace
----------------------------------
Posledním modulem je navigace - spouštěč nativní aplikace **GNOME Maps** (`gnome-maps`), stejně jako u ostatních skutečně externích programů (welle.io, prohlížeč). Pro plnohodnotné offline trasování by šlo `navigace.py` rozšířit o vlastní offline řešení (např. přes OSRM), ale v aktuální podobě appka žádný takový vlastní navigační modul neobsahuje - `navigace.py` jen otevře/zaostří okno GNOME Maps.

![desktop](printscreen/navigace.jpg)

## Potřebné knihovny
Tento seznam odpovídá tomu, co appka v aktuální podobě opravdu volá v kódu (`main.py` a moduly, které importuje/spouští) - žádné položky navíc "pro jistotu". Balíčky jsou pojmenované podle Ubuntu/Debianu (na jiné distribuci ARM desky se názvy mohou lišit).

**Python a PyQt5:**
 - `python3`
 - `python3-pip`
 - `python3-pyqt5` - základ celého UI
 - `python3-pyqt5.qtwebengine` - vestavěné YouTube, YouTube Music a Mapy (`QWebEngineView`)
 - `python3-vlc` - Python vazby na VLC, používá hudební přehrávač
 - `python3-requests` - modul Počasí (OpenWeatherMap API)

**Systémové programy, které appka spouští:**
 - `vlc` - přehrávání videa (Video modul) i podkladová knihovna pro `python3-vlc` (hudební přehrávač)
 - `rtl-sdr` (poskytuje `rtl_fm`) + SDR dongle a anténa - FM Rádio modul. Funguje otestovaně i s RTL-SDR V4 (viz poznámka o V4 u FM Radio modulu výše a box níže, kdyby přesto byly problémy se signálem).
 - `alsa-utils` (poskytuje `aplay`) - výstup zvuku z FM Rádia
 - `welle.io` - DAB modul
 - `gnome-maps` - Navigace modul
 - `chromium-browser` - modul Web (obecné vyhledávání/prohlížení)
 - `wmctrl` - doporučeno pro externí moduly (Web, DAB, Navigace): když je okno už otevřené, appka ho jen přepne do popředí místo spouštění druhé instance. Bez `wmctrl` to pořád funguje, jen se okno pokaždé spustí znovu.
 - `gnome-control-center` - Wi-Fi a Bluetooth v Nastavení (appka cílí na GNOME desktop)
 - `network-manager-gnome` (poskytuje `nm-connection-editor`) - záložní Wi-Fi nástroj, pokud by `gnome-control-center` chybělo
 - `blueman` (poskytuje `blueman-manager`) - záložní Bluetooth nástroj, pokud by `gnome-control-center` chybělo
 - `bluez` (poskytuje `bluetoothctl`) - ikonka Bluetooth v dolní liště (zviditelnění desky pro párování z telefonu)
 - `pulseaudio-module-bluetooth` **nebo** `libspa-0.2-bluetooth` - aby deska uměla přijímat a přehrávat zvuk streamovaný z telefonu přes Bluetooth (A2DP sink); podle toho, jestli systém používá PulseAudio, nebo PipeWire
 - `pulseaudio-utils` nebo `pipewire-pulse` (poskytuje `pactl`) - ovládání hlasitosti v Nastavení

**Bluetooth: párování vs. deska jako Bluetooth reproduktor** - v appce jsou dvě různé věci: tlačítko "Otevřít nastavení Bluetooth" v Nastavení otevírá `gnome-control-center` pro správu/mazání spárovaných zařízení. Ikonka Bluetooth v dolní liště dělá něco jiného - zviditelní desku (`bluetoothctl discoverable/pairable on`), aby ji telefon vůbec našel a mohl se k ní připojit a streamovat na ni hudbu (deska pak funguje jako Bluetooth reproduktor / A2DP sink). Samotné zviditelnění ale nestačí, pokud chybí balíček pro Bluetooth audio (viz řádek výše) - bez něj se telefon může spárovat, ale zvuk by nešel přehrát.

**Jen pro kiosk režim** (viz sekce "Kiosk režim" níže - běh appky bez GNOME desktopu, s automatickým startem):
 - `xserver-xorg`, `xinit`, `x11-xserver-utils` - holý X server, appka nepotřebuje celý desktop
 - `matchbox-window-manager` - odlehčený okenní manažer (žádný panel, žádná plocha)
 - `unclutter` - schová kurzor myši, když se nehýbe (appka je určená pro dotykovou obrazovku)
 - `onboard` - dotyková klávesnice, samostatně fungující i bez GNOME
 - `at-spi2-core` - aby `onboard` poznal, kdy je aktivní textové pole (auto-show)
 - `dbus-x11` (poskytuje `dbus-launch`) - D-Bus session sběrnice bez desktop prostředí
 - `dconf-cli` - nastavení výchozích hodnot pro `onboard` (auto-show, ukotvení)

Instalace na Ubuntu/Debianu (uprav podle skutečně nainstalovaného desktopu):
```
sudo apt install python3 python3-pip python3-pyqt5 python3-pyqt5.qtwebengine \
    python3-vlc python3-requests vlc rtl-sdr alsa-utils welle.io gnome-maps \
    chromium-browser wmctrl gnome-control-center network-manager-gnome \
    blueman bluez pulseaudio-utils

# jedno z těchto dvou, podle toho jestli systém běží na PulseAudio nebo
# PipeWire (nutné, aby šel na desku streamovat zvuk z telefonu):
sudo apt install pulseaudio-module-bluetooth
# nebo:
sudo apt install libspa-0.2-bluetooth
```

**Poznámka k RTL-SDR V4:** V4 používá jiný tuner (R828D) než starší V3 a u některých systémů/starších verzí balíčku `rtl-sdr` býval problém (žádný signál, špatná frekvence, zkreslený zvuk) - vyžadovalo to aktualizovaný ovladač (fork RTL-SDR Blog). Na aktuálních systémech uvedených v tomhle READMU ale balíčkový `rtl-sdr` s V4 dongle otestovaně funguje bez problémů, takže postup níže potřebuješ jen v případě, že bys s obyčejným `rtl-sdr` narazil na některý z těch příznaků:
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

# ať kernel dongle nezabere jako DVB-T TV tuner dřív, než ho chytí rtl_fm
echo 'blacklist dvb_usb_rtl28xxu' | sudo tee /etc/modprobe.d/blacklist-rtlsdr.conf
sudo reboot
```
Tenhle ovladač je zpětně kompatibilní i se staršími dongly (V3 a generickými), takže ho klidně použij i bez V4.

Pro appku samotnou stačí balíčky výše. Chceš-li rovnou i kiosk režim (appka po startu naskočí sama, bez GNOME), přidej ještě:
```
sudo apt install xserver-xorg xinit x11-xserver-utils matchbox-window-manager \
    unclutter onboard at-spi2-core dbus-x11 dconf-cli
```
Tenhle druhý příkaz spouštět nemusíš ručně - `kiosk/install-kiosk.sh` (viz sekce "Kiosk režim") ho zavolá za tebe automaticky. Je tu uvedený hlavně pro přehled, co všechno kiosk režim navíc potřebuje.

S těmito knihovnami by appka měla fungovat správně. Pokud na zařízení nějaká volitelná knihovna (`python3-vlc`, `python3-pyqt5.qtwebengine`, `python3-requests`) chybí, appka to sama pozná a místo pádu zobrazí pro danou stránku hlášku „není dostupné" - zbytek appky běží dál.

## Kiosk režim (bez GNOME, automatický start)
Pro nasazení v autě appka nepotřebuje kolem sebe celý desktop (GNOME/XFCE/KDE) - jen X server a appku samotnou přes celou obrazovku. Ve složce `kiosk/` je připravený jednorázový instalátor, který:

1. Vypne grafické přihlašovací okno (GDM a tedy i celý GNOME desktop), aby se po startu desky nespouštělo.
2. Nastaví automatické přihlášení na tty1 (žádné zadávání hesla).
3. Nainstaluje odlehčený okenní manažer *matchbox* (žádný panel, žádná plocha - jen správa oken, aby fungovala i okna Nastavení Wi-Fi/Bluetooth).
4. Nainstaluje a nastaví dotykovou klávesnici *onboard* (viz níže).
5. Nainstaluje podporu pro Bluetooth audio (`bluez` + `pulseaudio-module-bluetooth`/`libspa-0.2-bluetooth`), aby ikonka Bluetooth v docku mohla desku zviditelnit a telefon na ni mohl streamovat zvuk.
6. Appku spustí automaticky přes `startx` hned po přihlášení, na celou obrazovku.

Balíčky, které kiosk režim navíc potřebuje, jsou v sekci "Potřebné knihovny" výše ("Jen pro kiosk režim"). Instalátor si je nainstaluje sám, ruční instalace není potřeba.

Použití (na desce, kde appka leží např. v `/home/orangepi/Autoradio`):
```
cd /home/orangepi/Autoradio/kiosk
chmod +x install-kiosk.sh
sudo ./install-kiosk.sh
sudo reboot
```

Po restartu appka naskočí sama, bez přihlašovací obrazovky a bez GNOME. `gnome-control-center`, `nm-connection-editor` i `blueman-manager` v Nastavení fungují dál normálně - matchbox jen spravuje jejich okna, GNOME shell k tomu není potřeba.

**Návrat ke GNOME** (kdykoliv v budoucnu, např. pro ladění):
```
sudo systemctl enable --now display-manager.service
sudo rm /etc/systemd/system/getty@tty1.service.d/override.conf
sudo systemctl daemon-reload
sudo reboot
```

### Dotyková klávesnice
Instalátor nastaví *onboard* (funguje i bez GNOME, na rozdíl od vestavěné GNOME klávesnice, která potřebuje gnome-shell). Je nastavená tak, aby:
- se sama zobrazila při kliknutí do jakéhokoliv textového pole - appky samotné, GTK dialogů (např. zadání Wi-Fi hesla), i vestavěného YouTube/YouTube Music/Map,
- byla ukotvená dole na obrazovce (ne volně plovoucí okno).

Appka má navíc v dolní liště vlastní ikonku klávesnice pro ruční zapnutí/vypnutí - pro případ, že by se automatické zobrazení v nějakém konkrétním poli nespustilo (typicky u některých webových stránek, kde web sám nedá včas najevo, že se jedná o textové pole).

Pokud by se auto-show nechoval podle očekávání, dá se doladit i graficky: `onboard-settings` (potřebuje balíček `onboard` s podporou GUI nastavení).

*Jedná se o verzi 10.*
