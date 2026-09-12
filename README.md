Open Source Autoradio do Linux
==============================
Autorádio pro Linux (Orange Pi 5 Pro a podobné desky), postavené na PyQt5. Běží jako jedno stálé okno (`main.py`) - jednotlivé aplikace jsou "vestavěné stránky" v `QStackedWidget`, mezi kterými appka přepíná okamžitě, bez zakládání nového procesu. Jen skutečně externí programy (welle-io pro DAB, Navit pro Navigaci) se spouští jako samostatný proces, protože jinak to nejde - ale i ty appka přepne do stejného fullscreen vzhledu jako zbytek appky.

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
Spouštěč nativní aplikace **welle-io** (`welle-io`), stejně jako u ostatních skutečně externích programů (Navigace/Navit) - appka jen otevře/zaostří jeho okno a přes `wmctrl` ho přepne na celou obrazovku, ať kolem něj není vidět GNOME horní lišta.

Appka měla dřív vlastní DAB modul napsaný nad bezhlavým `welle-cli` (viz historie verzí), ale v praxi se ukázalo jednodušší a spolehlivější použít rovnou skutečné GUI `welle-io` - má vlastní seznam stanic, slideshow obrázky i lepší zpracování metadat, než co by dávalo smysl znovu stavět v Pythonu.

**Důležité:** DAB a FM Rádio sdílí stejný SDR dongle - najednou může fungovat jen jeden z nich. Pokud `welle-io` po spuštění nenajde žádné stanice, zkontroluj, že zrovna nehraje FM Rádio.

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
Spouštěč nativní aplikace **Navit** (`navit`) - appka ho přes `wmctrl` navíc přepne do fullscreen, aby vypadal stejně jako zbytek appky, bez GNOME lišty kolem.

Navit je vybraný záměrně místo GNOME Maps - je to navigační software navržený přímo pro "carputer" nasazení (touchscreen rozhraní, offline mapy, hlasové pokyny), a hlavně: **umí číst polohu přímo z `gpsd`**, úplně bez GeoClue2. To je zásadní rozdíl oproti GNOME Maps, které polohu berou výhradně přes GeoClue2 - tenhle systémový mezikrok (a jeho propojení s USB GPS přijímačem přes `gps-share`) se v praxi ukázal jako křehký a náchylný na těžko viditelné chyby (špatná oprávnění na socketu, chybějící "agent" pro potvrzení přístupu). Navit se čtením přímo z `gpsd` celé téhle vrstvě vyhne.

**Kompletní nastavení (přijímač VK-162, u-blox čip):**

**1. Ověř, že hardware sám o sobě funguje:**
```
sudo apt install gpsd gpsd-clients
sudo gpsd /dev/ttyACM0 -F /var/run/gpsd.sock
cgps -s
```
(Za `/dev/ttyACM0` dosaď skutečné zařízení - zjistíš ho přes `ls /dev/ttyACM* /dev/ttyUSB*` po připojení, nebo `dmesg | tail` hned po zapojení.) `cgps` by měl ukázat souřadnice, jakmile přijímač "chytí" satelity - venku i pár desítek sekund, u okna to VK-162 zvládne i uvnitř, v hlubším vnitrozemí budovy nemusí chytit vůbec.

**2. Nastav `gpsd` jako trvalou službu** (ne jednorázové spuštění z kroku 1 - to bylo jen pro test):
```
sudo tee /etc/default/gpsd > /dev/null << 'EOF'
START_DAEMON="true"
DEVICES="/dev/ttyACM0"
GPSD_OPTIONS="-n"
USBAUTO="true"
EOF
sudo systemctl enable --now gpsd.socket
sudo systemctl restart gpsd
cgps -s
```
(`-n` = nečekat na první příkaz od klienta, začít číst GPS hned po startu - jinak by `gpsd` mohl vypadat "prázdný", dokud se k němu něco nepřipojí.)

**3. Nainstaluj Navit a vytvoř si vlastní konfiguraci:**
```
sudo apt install navit-gui-internal navit-graphics-gtk-drawing-area navit-data
navit
```
Samotný balíček `navit` na Ubuntu/Debianu neobsahuje žádné grafické rozhraní vůbec - je rozdělený na víc balíčků zvlášť. `navit-gui-internal` je vlastní odlehčené rozhraní Navitu (lepší pro dotykovou obrazovku než starší `navit-gui-gtk`), `navit-graphics-gtk-drawing-area` je vykreslovací vrstva, kterou obě rozhraní potřebují. Bez těchhle balíčků `navit` spadne hned po startu s `FATAL: No GUI available.`

Zavři ho (appka ho pak stejně spouští sama). **Navit si výchozí konfiguraci do `~/.navit/` sám nezkopíruje** - jen čte tu, co je nainstalovaná systémově. Zkopíruj si ji ručně, ať máš vlastní kopii k úpravám:
```
ls -la /etc/navit/navit.xml /usr/share/navit/navit.xml 2>/dev/null
mkdir -p ~/.navit
cp /etc/navit/navit.xml ~/.navit/navit.xml
# pokud tenhle soubor na tvém systému neexistuje, zkus místo něj:
# cp /usr/share/navit/navit.xml ~/.navit/navit.xml
```

**4. Uprav `~/.navit/navit.xml`** - najdi řádek `<vehicle ...>` a uprav/přidej:
```xml
<vehicle name="GPS" profilename="car" enabled="yes" active="1" source="gpsd://localhost" follow="1"/>
```
(`follow="1"` = mapa se posouvá s tebou při každé aktualizaci polohy, ne až na okraji obrazovky.) Ověř zároveň, že `profilename="car"` odkazuje na skutečně existující profil: `grep -n "<vehicleprofile" ~/.navit/navit.xml` by měl ukázat mimo jiné `<vehicleprofile name="car"`.

**5. Stáhni a přidej mapová data** - Navit v balíčku žádné mapy neobsahuje. Ověřený postup (přes vlastní `maptool` Navitu, ne přes nějaké tlačítko v appce - žádné takové jednoduché "stáhnout mapu" menu v aktuální verzi není):
```
sudo apt install maptool
cd ~
wget https://download.geofabrik.de/europe/czech-republic-latest.osm.pbf
maptool --protobuf -i czech-republic-latest.osm.pbf czech-republic.bin
```
(Za "czech-republic" dosaď svůj region - seznam všech zemí/oblastí je na `https://download.geofabrik.de/`. Soubor pro ČR má přes 900 MB, převod `maptool`em chvíli potrvá - u dokončeného převodu uvidíš na konci `PROGRESS: Phase 14: done`. Spoustu varování typu `OSM Warning: ... turn restriction ...` uvidíš u každé mapy tohohle rozsahu - jsou neškodná, týkají se pár jednotlivých křižovatek v datech OSM, ne tvého souboru.)

Pak do `~/.navit/navit.xml` najdi element `<mapset>` s komentářem "Mapset template for OpenStreetMap" a vlož/nahraď dovnitř (cesta musí být absolutní, `~` se v XML nerozbaluje):
```xml
<mapset enabled="yes">
    <map type="binfile" enabled="yes" data="/home/orangepi/czech-republic.bin"/>
</mapset>
```
Restartuj Navit - bez tohohle kroku appka ukáže jen prázdnou/šedou mapu bez ohledu na to, jak dobře GPS funguje.

**6. Vypni ukázkovou mapu** - výchozí konfigurace má ještě jeden aktivní mapset s ukázkovými daty (`<xi:include href="$NAVIT_SHAREDIR/maps/*.xml"/>`), který na Ubuntu/Debianu ukazuje na neexistující soubor (balíček žádnou ukázkovou mapu neobsahuje) - v logu se to projeví neškodnou hláškou `Unable to include '...maps/*.xml'`, ale pro pořádek ho vypni, ať je jasné, že appka pracuje jen s tvými reálnými daty:
```
grep -n '<mapset enabled="yes">' ~/.navit/navit.xml
```
Najdi ten, co obsahuje `$NAVIT_SHAREDIR/maps/*.xml` (ne ten s tvou mapou z kroku 5) a přepni na `<mapset enabled="no">`.

**7. Zkontroluj, že aktivní layout je skutečný mapový styl, ne jen styl trasy** - výchozí konfigurace má `default_layout="Car"` na řádku s `<navit ...>` (najdeš přes `grep -n "<navit " ~/.navit/navit.xml`). To musí odpovídat jménu **plnohodnotného** layoutu (desítky vrstev - silnice, voda, budovy, popisky), ne odlehčenému layoutu jako "Route" (ten kreslí jen vypočtenou trasu, nic jiného - pokud by byl označený jako `active="1"`, přebije `default_layout` a appka by ukazovala prázdnou mapu i se správnými daty). Ověření:
```
grep -n '<layout name=' ~/.navit/navit.xml
```
Měl bys vidět `<layout name="Car"` **bez** `active="1"` u "Route" (pokud tam `active="1"` je, smaž ho - stačí jeden konflikt a appka nekreslí nic).

**8. Nastav češtinu** (nepovinné, ale usnadní vyhledávání měst/adres bez nutnosti pokaždé zadávat zemi) - najdi na začátku souboru:
```xml
<config xmlns:xi="http://www.w3.org/2001/XInclude">
```
a změň na:
```xml
<config xmlns:xi="http://www.w3.org/2001/XInclude" language="cs_CZ">
```

**9. Přidej OSD panel** (nepovinné, ale pro dotykový headunit se hodí - tlačítka zoomu, rychlost, kompas, název ulice, zbývající čas/vzdálenost) - najdi v souboru sekci s `<osd ... command="gui.menu()" .../>` a za ni vlož:
```xml
<osd enabled="yes" type="button" x="-96" y="-96" command="zoom_in()" src="zoom_in.xpm"/>
<osd enabled="yes" type="button" x="0" y="-96" command="zoom_out()" src="zoom_out.xpm"/>
<osd enabled="yes" type="text" label="${vehicle.position_speed}" x="10" y="10" font_size="800" w="205" h="55" align="4" background_color="#1b0877cc"/>
<osd enabled="yes" type="compass" align="0" font_size="350" x="10" y="70" w="100" h="100" background_color="#1b0877cc"/>
<osd enabled="yes" type="text" label="${navigation.item.street_name}" x="-400" y="10" align="0" background_color="#1b0877cc" font_size="550" w="390" h="40"/>
<osd enabled="yes" type="gps_status" x="-60" y="100" w="50" h="40" background_color="#1b0877cc"/>
<osd enabled="yes" type="text" label="Cíl za ${navigation.item.destination_time[remaining]}" x="100" y="-30" w="270" h="30" background_color="#1b0877cc"/>
<osd enabled="yes" type="text" label="Zbývá ${navigation.item.destination_length[named]}" x="370" y="-30" w="270" h="30" background_color="#1b0877cc"/>
```
Souřadnice (`x`, `y`, `w`, `h`) jsou v pixelech - kladná hodnota `x`/`y` počítá zleva/shora, záporná zprava/zdola. Hodnoty výše jsou startovní bod pro obrazovku 800×480 - klidně uprav podle toho, jak to vypadá na tvém displeji.

Po tomhle by Navit měl ukazovat tvoji reálnou polohu, plnohodnotnou mapu, a umět naplánovat trasu s hlasovými pokyny.

**Trasa hlásí `no route found, pos blocked`?** Znamená to, že Navit nedokáže tvoji aktuální pozici napojit na žádný projízdný úsek silnice pro aktuální profil vozidla. Nejčastější příčiny: (a) GPS pozice neleží dost blízko žádné nakreslené silnici (typicky při testování uvnitř budovy/dvora) - přibliž mapu a zkontroluj, jestli zelená tečka leží přímo na silnici; (b) `profilename` u `<vehicle>` neodpovídá žádnému skutečnému `<vehicleprofile name="...">` (viz krok 4). Rychlý test bez závislosti na živé GPS pozici: naplánuj trasu mezi dvěma ručně vybranými adresami/městy v menu appky - pokud tohle funguje, problém je jen v přesnosti/poloze aktuální GPS pozice, ne v konfiguraci.

**Chceš radši GNOME Maps?** Pořád to jde - je to jen otázka změnit `navigace.py` (`COMMAND = ["gnome-maps"]`) a propojit GPS s GeoClue2 přes nástroj `gps-share` (unix socket, `network-nmea` zdroj v `/etc/geoclue/conf.d/`, plus explicitní povolení aplikace bez GNOME agenta). Přesné kroky už tahle verze README neobsahuje - byly součástí staršího řešení, které jsme kvůli němu nakonec opustili (viz Historie verzí, v13-v24) - je to řešitelné, jen podstatně komplikovanější a náchylnější na chyby, které se špatně diagnostikují, protože selhávají potichu bez chybové hlášky.

## Potřebné knihovny
Tento seznam odpovídá tomu, co appka v aktuální podobě opravdu volá v kódu (`main.py` a moduly, které importuje/spouští) - žádné položky navíc "pro jistotu". Balíčky jsou pojmenované podle Ubuntu/Debianu (na jiné distribuci ARM desky se názvy mohou lišit).

**Python a PyQt5:**
 - `python3`
 - `python3-pip`
 - `python3-pyqt5` - základ celého UI
 - `python3-pyqt5.qtwebengine` - vestavěné YouTube, YouTube Music a Web (`QWebEngineView`)
 - `python3-vlc` - Python vazby na VLC, používá hudební přehrávač
 - `python3-requests` - modul Počasí (OpenWeatherMap API)
 - `python3-dbus` - modul BT Hudba (čte info o přehrávané skladbě a ovládá přehrávání přes BlueZ AVRCP na systémové D-Bus sběrnici)

**Systémové programy, které appka spouští:**
 - `vlc` - přehrávání videa (Video modul) i podkladová knihovna pro `python3-vlc` (Hudba)
 - `rtl-sdr` (poskytuje `rtl_fm`) + SDR dongle a anténa - FM Rádio modul. Funguje otestovaně i s RTL-SDR V4 (viz poznámka o V4 níže, kdyby přesto byly problémy se signálem).
 - `alsa-utils` (poskytuje `aplay`) - výstup zvuku z FM Rádia
 - `welle.io` - DAB modul (appka spouští celou GUI aplikaci `welle-io`, ne jen bezhlavý `welle-cli` - viz poznámka o QML modulech níže, kdyby se nespustila)
 - `navit-gui-internal`, `navit-graphics-gtk-drawing-area`, `navit-data` - Navigace modul. Samotný balíček `navit` na Ubuntu/Debianu neobsahuje GUI vůbec - je potřeba nainstalovat i tyhle. Nepotřebuje `gnome-maps`/GeoClue2 - čte GPS přímo z `gpsd` (viz níže).
 - `maptool` - převod stažených OpenStreetMap dat (Geofabrik) do binárního formátu, který Navit umí zobrazit - jinak appka ukáže jen prázdnou mapu, i když GPS funguje správně
 - `gpsd`, `gpsd-clients` - GPS přijímač ("GPS mouse") - Navit se na běžící `gpsd` napojuje přímo (`gpsd://localhost`), takže `gpsd` tu není jen pro test, ale musí běžet trvale jako služba - viz modul Navigace výše.
 - `wmctrl` - doporučeno pro DAB a Navigaci: když je okno welle-io/Navit už otevřené, appka ho jen přepne do popředí místo spouštění druhé instance, a navíc ho přepne do fullscreen (stejně jako appka samotná), aby kolem něj nebylo vidět GNOME horní lištu. Bez `wmctrl` oba moduly pořád fungují, jen jako běžné okno s GNOME lištou kolem.
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
    navit-gui-internal navit-graphics-gtk-drawing-area navit-data maptool gpsd \
    gpsd-clients wmctrl gnome-control-center network-manager-gnome \
    pavucontrol bluez bluez-tools pulseaudio-utils

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

**Poznámka k welle.io (DAB):** appka spouští celou GUI aplikaci `welle-io`. Pokud se nespustí vůbec (ani přímo v terminálu mimo appku), skoro jistě chybí QML moduly - je to Qt/QML aplikace. Spusť `welle-io` přímo v terminálu a přečti si chybovou hlášku (`module "XYZ" is not installed`), ať víš, který balíček přesně chybí. Na Qt6 systémech (ověřeno na Orange Pi 5 Pro/Armbian) pomůže `sudo apt install qml6-module-qtcore qml6-module-qtquick-dialogs`, na starších Qt5 systémech `qml-module-qtquick2 qml-module-qtquick-controls qml-module-qtquick-controls2 qml-module-qtquick-dialogs qml-module-qtquick-layouts qml-module-qtgraphicaleffects qml-module-qtcharts`.

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

**Doporučený způsob: appka nad běžícím GNOME (`install-gnome-autostart.sh`).** Appka se spustí automaticky hned po přihlášení do normální GNOME session a běží přes celou obrazovku nad ní. V reálném provozu (ověřeno na Orange Pi 5 Pro) se ukázalo být spolehlivější než alternativa níže - fullscreen okna, dotyková klávesnice i párování Bluetooth fungují správně, protože běží skutečný `gnome-shell` s plnou podporou window manageru. Volitelný skript `trim-gnome.sh` (viz níže) pak zvládne většinu té "ceny navíc" (spotřeba paměti/CPU běžícího GNOME) srazit dolů bez ztráty těchhle výhod.

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

**Pokud jsi zvolil variantu bez GNOME**, GNOME klávesnice bez gnome-shellu vůbec nefunguje, takže instalátor tam pořád používá `onboard` - ten funguje nezávisle na desktop prostředí. V reálném provozu se ale ukázalo, že se `onboard` pod `matchbox` může vykreslovat nespolehlivě a ořezaně - v tom případě je jednodušší přejít na variantu s GNOME výše. Appka sama v žádném režimu nemá tlačítko pro ruční zapnutí/vypnutí klávesnice (dřív mělo, ale bez fungujícího protějšku na GNOME straně to bylo jen matoucí mrtvé tlačítko - bylo odstraněné). Pro `onboard` jde klávesnici ručně přepnout přes `dbus-send --session --type=method_call --dest=org.onboard.Onboard /org/onboard/Onboard/Keyboard org.onboard.Onboard.Keyboard.ToggleVisible` v terminálu, kdyby to bylo někdy potřeba mimo appku.

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

- **v29 (finální verze)** - Kompletní průchod celým README a projektem. Sekce Navigace přepsaná a doplněná o ověřené kroky z externího návodu (OpenStreetMap Wiki, Navit/Ubuntu): vypnutí ukázkové mapy, nastavení češtiny, OSD panel pro dotykovou obrazovku (zoom tlačítka, rychlost, kompas, název ulice, zbývající čas/vzdálenost) - GPS připojení zůstalo u `gpsd` (VK-162 je kabelová USB myš, návod počítá s Bluetooth GPS). Zahrnuty i všechny poznatky z reálného ladění (`default_layout` musí odpovídat plnohodnotnému stylu jako "Car", ne odlehčenému stylu trasy jako "Route"; `no route found, pos blocked` = GPS pozice mimo silnici nebo špatný profil vozidla). Opravené poslední zapomenuté zmínky GNOME Maps v popisech, které už neodpovídaly skutečnému kódu (DAB a Navigace dávno spouští `welle-io`/`navit`, ne GNOME aplikace).

- **v28** - Oprava syntaxe `maptool` v kroku 5 (Navigace) - `maptool` bere vstupní soubor přes `-i` a `--protobuf`, ne jako druhý holý argument (`Only one non-option argument allowed.`). Opraveno na `maptool --protobuf -i vstup.osm.pbf výstup.bin`.

- **v27** - Oprava kroku 3 v postupu pro Navigaci - mylně jsem předpokládal, že Navit si při prvním spuštění sám zkopíruje výchozí konfiguraci do `~/.navit/navit.xml`. Ve skutečnosti čte jen systémově nainstalovanou konfiguraci (`/etc/navit/navit.xml` nebo `/usr/share/navit/navit.xml`) a do domovské složky nic nekopíruje - proto tam soubor předtím nebyl vůbec k nalezení. Krok teď obsahuje ruční zkopírování výchozí konfigurace.

- **v26** - Opravený postup pro mapová data v Navitu - dřív zmíněné menu "Mapy → Stáhnout mapu" v aktuální verzi neexistuje/nebylo ověřené. Nahrazeno skutečně zdokumentovaným postupem: stažení výřezu z Geofabriku (`.osm.pbf`) a převod vlastním nástrojem `maptool` (nový balíček v seznamu závislostí) do binárního formátu, který se pak přidá do `~/.navit/navit.xml`.

- **v25** - Oprava instalace Navitu - balíček `navit` na Ubuntu/Debianu neobsahuje žádné grafické rozhraní (`FATAL: No GUI available.` hned po spuštění), je nutně potřeba i `navit-gui-internal` a `navit-graphics-gtk-drawing-area` zvlášť. Aktualizované ve všech třech místech v README (hlavní instalační příkaz, seznam knihoven, krok 3 v postupu pro Navigaci).

- **v24** - Navigace přepnutá z GNOME Maps na **Navit** - navigační software navržený přímo pro carputer nasazení, s vlastním čtením GPS přímo z `gpsd`, bez GeoClue2. Řeší to napořád celou třídu problémů, se kterými jsme se prokousávali (`gps-share`, oprávnění na socketu, GeoClue2 agent) - Navit se GeoClue2 vůbec netýká. GNOME Maps zůstává zdokumentované jako alternativa pro toho, kdo by ji přesto chtěl.

- **v23** - Opravená skutečná příčina, proč GNOME Maps nikdy nedostávaly polohu z GPS i po správné konfiguraci GeoClue2 (viz sekce Navigace): `gps-share` běží jako root a vytvářel unix socket s právy `755` (root:root), na který systémový účet `geoclue` neměl zápisové právo - připojení k unixovému socketu bez zápisu selže úplně potichu, bez chyby v logu, takže to vypadalo jako "nic nefunguje, ale nikde není vidět proč". Přidané `UMask=0000` do systemd jednotky `gps-share.service`, ať socket vznikne s právy `666` a `geoclue` se k němu dostane.

- **v22** - DAB vrácený zpět na spouštěč skutečné aplikace `welle-io` (vlastní modul nad `welle-cli` z v19 se v praxi ukázal jako zbytečná komplikace navíc - `welle-io` má vlastní seznam stanic, slideshow i lepší metadata). Odstraněné mrtvé tlačítko pro ruční zapnutí/vypnutí klávesnice v docku - GNOME variantě k ničemu nepomáhalo (žádné API pro to neexistuje) a jen matlo.
- **v21** - Oprava neviditelného textu v rozbalovacím seznamu kanálů DAB (bílý text na bílém pozadí - Qt nestyluje rozbalený seznam automaticky stejně jako zavřené pole, potřebuje vlastní pravidlo). Kompletní kontrola kódu napříč celou appkou i README - pár zastaralých komentářů/hlášek opravených na přesný current stav (žádné funkční chyby nenalezené mimo tu s DAB seznamem).
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
