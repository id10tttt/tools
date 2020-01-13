#!/usr/bin/env bash

if ! [ $(id -u) = 0 ]; then
   echo "The script need to be run as sudo." >&2
   exit 1
fi

if [ $SUDO_USER ]; then
    real_user=$SUDO_USER
else
    real_user=$(whoami)
fi

# install ca-certificates apt-transport-https gnupg2 to add key and suport https
apt install ca-certificates apt-transport-https gnupg2 sudo -y

# delcare key
wine_key='76F1A20FF987672F'
skype_key='1F3045A5DF7587C3'
google_key='7721F63BD38B4796'
vbox_key1='A2F683C52980AECF'
vbox_key2='54422A4B98AB5139'
docker_key='8D81803C0EBFCD88'
visual_code_key='EB3E94ADBE1229CF'
etcher_key='379CE192D401AB61'

# add key
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys $vbox_key1
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys $vbox_key2

# replace source.list
echo "
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ testing main contrib non-free
deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ testing main contrib non-free
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ testing-updates main contrib non-free
deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ testing-updates main contrib non-free
# deb https://mirrors.tuna.tsinghua.edu.cn/debian/ testing-backports main contrib non-free
# deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ testing-backports main contrib non-free
deb https://mirrors.tuna.tsinghua.edu.cn/debian-security testing-security main contrib non-free
deb-src https://mirrors.tuna.tsinghua.edu.cn/debian-security testing-security main contrib non-free

deb http://httpredir.debian.org/debian/ testing main contrib non-free
deb http://ftp.de.debian.org/debian testing main non-free
" >/etc/apt/sources.list

# visual code
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys $visual_code_key
echo "
### THIS FILE IS AUTOMATICALLY CONFIGURED ###
# You may comment out this entry, but any other modifications may be lost.
deb [arch=amd64] http://packages.microsoft.com/repos/vscode stable main
" > /etc/apt/sources.list.d/vscode.list

# wine
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys $wine_key
echo "
deb https://dl.winehq.org/wine-builds/debian/ testing main
" > /etc/apt/sources.list.d/wine.list

# skype
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys $skype_key
echo "
deb [arch=amd64] https://repo.skype.com/deb stable main
" > /etc/apt/sources.list.d/skype-stable.list

# etcher
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys $etcher_key
echo "
deb https://deb.etcher.io stable etcher
" > /etc/apt/sources.list.d/balena-etcher.list

# chrome
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys $google_key
echo "
### THIS FILE IS AUTOMATICALLY CONFIGURED ###
# You may comment out this entry, but any other modifications may be lost.
deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main
" > /etc/apt/sources.list.d/google-chrome.list

# docker
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys $docker_key
echo "
deb [arch=amd64] https://download.docker.com/linux/debian buster stable
" > /etc/apt/sources.list.d/docker.list

# upgrade system
apt update && apt upgrade -y

# install software
apt install -y fortunes-zh fortunes tilix flameshot gcc make g++ vim git aria2 vlc apt-transport-https \
 gnome-software-plugin-flatpak gnome-software-plugin-snap fonts-wqy-microhei balena-etcher-electron \
fonts-wqy-zenhei unrar unzip p7zip gnome-nettool curl sl gimp nmap linux-headers-$(uname -r) plymouth plymouth-themes \
firmware-linux fonts-symbola ipython3 python3-venv python3-pip libncurses5 vlc libkmod-dev initramfs-tools-core \
remmina papirus-icon-theme kdenlive i8kutils youtube-dl arc-theme screenfetch skypeforlinux google-chrome-stable \
python3-babel python3-dateutil python3-decorator \
python3-docutils python3-feedparser python3-gevent python3-html2text python3-jinja2 python3-lxml python3-mako \
python3-mock python3-ofxparse python3-passlib python3-pil python3-psutil python3-psycopg2 python3-pydot python3-pyparsing \
python3-pypdf2 python3-reportlab python3-requests python3-serial python3-tz python3-usb python3-vatnumber python3-celery \
python3-werkzeug python3-xlsxwriter python3-zeep python3-num2words python3-pyldap python3-vobject python3-wheel python3-opencv \
node-clean-css node-less nodejs npm postgresql-12 proxychains4 filezilla firmware-linux-nonfree firmware-linux-free  \
libx11-6 libx11-dev libxtst6 psmisc build-essential ufw libaio1 libcanberra-gtk-module build-essential libqt5opengl5 \
gnome-boxes ideviceinstaller python3-imobiledevice libimobiledevice-utils libimobiledevice6 libplist3 ifuse usbmuxd \
mc iftop testdisk libxml2-dev libxslt1-dev libsasl2-dev python3-dev libldap2-dev libssl-dev \
software-properties-common fonts-noto-cjk fonts-noto-core fonts-noto-unhinted \
ttf-unifont unifont ttf-mscorefonts-installer redis wkhtmltopdf \
python-dbus python-gobject libpq-dev

# npm install
npm install -g less-plugin-clean-css less

# install docker
apt-get remove docker docker-engine docker.io containerd runc
apt-get install docker-ce docker-ce-cli containerd.io

sudo -u $real_user mkdir ~/.pip
sudo -u $real_user echo "
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
" > ~/.pip/pip.conf

mkdir ~/.pip
echo "
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
" > ~/.pip/pip.conf