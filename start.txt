Orangepi
cd "/home/orangepi/Documents/Projekt 4.B/"
python3 main.py

Notebook
cd "/home/linusmisa/Projekty/Projekt 4.B/"
python3 main.py


Packs:
sudo apt install -y \
python3 \
python3-pip \
python3-pyqt5 \
python3-pyqt5.qtmultimedia \
python3-pyqt5.qtquick \
python3-pyqt5.qtwebengine

sudo apt install -y vlc python3-vlc

pip install requests

pip install pillow

sudo apt install -y \
qml-module-qtquick-controls2 \
qml-module-qtquick-layouts \
qml-module-qtquick-window2 \
qml-module-qtquick2 \
qml-module-qtgraphicaleffects \
qmlscene

sudo apt install -y \
network-manager \
blueman \
bluez \
alsa-utils \
pulseaudio \
brightnessctl

python3-pyqt5.qtwebengine
welle.io
sudo apt install gnome-control-center
sudo apt install network-manager network-manager-gnome
sudo apt install bluez blueman
sudo apt install brightnessctl

sudo apt install dbus-x11

sudo apt update
sudo apt install osrm-backend -y

sudo apt update
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER  # aby šel Docker spustit bez sudo

mkdir ~/osrm-data && cd ~/osrm-data
wget https://download.geofabrik.de/europe/czech-republic-latest.osm.pbf
