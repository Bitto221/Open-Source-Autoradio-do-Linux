Open Source Autoradio do Linux
==============================

## Zakldaní moduly
Tento program obsahuje spoustu různych modulu. Většina běží v pythonu a využíva PyQt5 s příslušnými potřebnými moduly. Halvni desktop aplikce je **main.py**. Po spuštení tohoto kodu se spustí okno, kde lze vybrat různé aplikace. Ikony použité na desktop aplikce jsem stáhnul z https://icons8.com/.

![desktop](printscreen/desktop.jpg)

Na této hlavní obrazovce je dole lišta obsahující *čas* a *datum*. 

Hudební přehrávač
----------------------------------
Prvním modulem je hudební prehráváč lokální hudby, který je celý napsaný v Pythonu. Všechný moduly mají společný *StyleSheet*.

![desktop](printscreen/music_player.jpg)

Vzheld všech aplikcí je velmi jednoducý a čistý. Výhodou je, že v případě potřebý jiného style, lze tento styl jednoduše zmenit pro všechny jednoduše v souboru *style.py*.

Youtube
----------------------------------
Dalšími dvěmi aplikacemi jsou jen spouštěče Youtube a Youtube Music v Chromium browser. Zde není problém změnit odkaz na cokoliv jiného.

FM Radio
----------------------------------
Dalším modulem je FM Radio napsané taky celé v Pythonu. Pro funkci tohoto radia je potřeba SDR doungle. Ja jsem si vybral RTL-SDR V4, protože je dobře odladěné. Nejduležitější veci je ale antená, která dělá tak 80% zvuku.

![desktop](printscreen/FM_radio.jpg)

Video přehrávač
----------------------------------
Dalším modulem je jednoduché okno jako spouštěč VLC přehrávače. Uživately vyjede okno, kde si vybere soubor, který chce přehrát a pak se tento soubor spustí pomocí VLC.

DAB
----------------------------------
Dalším modulem neni můj vlastní program, ale na přehrávání DAB jsem použil **Welle.io**. Je to jednoduchý program, který funguje skvěle na přehrávání DAB z RTL-SDR. 

Počasí
----------------------------------
Dalším modulem je počací, které je také vytvořené celé v Pythonu. Funguje to tak, že modul má svuj API key, kterým se hlasí na stránku https://openweathermap.org/ ze které bere data. V Pythonu je nastavené aby to bralu údaje pro Prahu. Bere to udáje o teplotě, rychlosti větru, vlhkosti a o tomzda je zataženo nebo polojasno atd. a k tomu přiřazuje určitý obrázek ze složky icons/weather. Všechny tyto údaje si to ukláda do souboru *weather_cache.json*. Když není připojení k internetu, tak to načte údaje ze souboru a vypíše je. Napíše i datum a čas uložení.

![desktop](printscreen/pocasi.jpg)

Vyhledávač
----------------------------------
Dalším modulem je jenom spouštěč Chromium Browser.

Nastavení
----------------------------------
dalším modulem je nastavení. Tento program otevírá nastevní Wi-Fi a Bluethoot a dokaže ovládat hlasitos pomocí knihovný *pulseaudio*. POslední tlačítko je na vypnutí desktop aplikce. Tato funkce je určená pro projekty, kde poběží aplikace na fullscreen a nebude ji možno jinak vypnout. 

![desktop](printscreen/nastaveni.jpg)

Barvy
----------------------------------
Dalším module je ovládání Témat. Na váběr je 6 barev: **fialová**, **červená**, **modrá**, **zelená**, **oranžová** a **růžová**. K jedotlivým barvam jsoutám určité tapety.

![desktop](printscreen/barvy.jpg)

Mapy
----------------------------------
Dalším modulem je jednoduché otevírání web map, které funguje jen s připojením k internetu.

Navigace
----------------------------------
Posledním module je navigace, která funguje i offline s offline mapami. Je to asi nejsložitéjší modul. Využívá stažené mapy, které spouští přes soubor *navigace.html*. Python soubor *navigace.py* slouží jen pro start programu. Přes osrm je udělané vypočítání trasy.

![desktop](printscreen/navigace.jpg)

## Potřebné knihovny
Pro spravnou funkci celého auto rádia je potřeba stahnou knihovny. Zde jsou rozepsané moduly, které funguji v Ubuntu:
 - python3
 - python3-pip
 - python3-pyqt5
 - python3-pyqt5.qtmultimedia
 - python3-pyqt5.qtquick
 - python3-pyqt5.qtwebengine
 - vlc
 - python3-vlc
 - requests
 - pillow
 - qml-module-qtquick-controls2
 - qml-module-qtquick-layouts
 - qml-module-qtquick-window2
 - qml-module-qtquick2
 - qml-module-qtgraphicaleffects
 - qmlscene
 - network-manager
 - blueman
 - bluez
 - alsa-utils
 - pulseaudio
 - brightnessctl
 - welle.io
 - network-manager-gnome
 - dbus-x11
 - osrm-backend
 - docker.io

 S těmito knihovnami by to mělo fungovat správně.
 *Jedná se o verzi 1.1*
