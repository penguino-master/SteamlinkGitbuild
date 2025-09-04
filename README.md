# Steamlink GUI

A lightweight launcher app for the **Raspberry Pi Zero 2 W**, designed to make living-room setups simple.  
Launch apps like **Steam Link** or **Kodi** using a controller, keyboard, or mouse with a clean PyQt6-based interface.

---

## 📦 Features
- Optimized for **Raspberry Pi Zero 2 W**
- Controller support via `pygame`
- Vertical app tiles with icons
- Easy customization via `programs.txt`
- Simple one-command install, update, and autostart

---

Requirements

- Raspberry Pi Zero 2 W running **Raspberry Pi OS (Lite or Desktop)**
- Python 3.9+ installed (installed automatically by the script)
- Internet connection for first install
- PyQt6 (Installed with program )

---

Installation

Run these on your Pi to install Steamlink GUI:

```bash
sudo apt install python3-pyqt6

sudo curl -sSL https://raw.githubusercontent.com/penguino-master/SteamlinkGitbuild/main/install.sh | bash
```

Note for PI os LITE users:

PI os lite doesn't come with the ability to display a gui application off the bat, so a few more things
need to be installed to get that to work:

```bash
sudo apt update
sudo apt install -y --no-install-recommends \
    xserver-xorg \
    x11-xserver-utils \
    xinit \
    openbox \
    fonts-dejavu-core
```

You will also have to create this file:

```bash
echo 'steamlink-gui' > ~/.xinitrc
```

You can test to see if the xserver runs with startx, but the next steps will have the app and it's xserver run on startup.

---

Setup Enable on startup

You can make the Steamlink GUI command run on startup by creating a systemctl service, which can be created by doing the following:

```bash
sudo tee /etc/systemd/system/steamlink.service > /dev/null <<EOF
[Unit]
Description=Steamlink GUI (X11 Kiosk)
After=systemd-user-sessions.service

[Service]
User=pi
PAMName=login
Environment=XAUTHORITY=/home/pi/.Xauthority
Environment=DISPLAY=:0
ExecStart=/usr/bin/startx
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

And can be enabled with these (can be toggled on/off with 'systemctl disable' ):

```bash
sudo systemctl daemon-reload

sudo systemctl enable steamlink-gui

sudo systemctl start steamlink-gui
```

Adding external applications to the program can be achieved by changing the programs.txt file located in the
installation directory (/opt/steamlink-gui). The programs should be added in format: Name | command | Icon.png
where the command is the command needed to open the app, and the icon links to the png file stored in the icons
folder. The icon you use must be in 2:3 aspect ratio, and 200:300 resolution. The filetype should be .png, but
might work with other formats.

The current programs supported by the app are:

Steam Link | steamlink | steamlink.png

An example of an additional program could be retropi, in which it would look like:

Retro Pie | emulationstation | RetroPI.png

---

Uninstalling

Running the following commands will uninstall Steamlink GUI from your system:

```bash
sudo rm -rf /opt/steamlink-gui

sudo rm /usr/local/bin/steamlink-gui
```

The following will remove the steamlink-gui systemctl service:

```bash
sudo systemctl disable steamlink-gui

sudo rm /etc/systemd/system/steamlink-gui.service
``` 