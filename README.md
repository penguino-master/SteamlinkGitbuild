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

---

Setup Enable on startup

You can make the Steamlink GUI command run on startup by creating a systemctl service, which can be created by doing the following:

```bash
sudo tee /etc/systemd/system/steamlink-gui.service > /dev/null <<EOF
[Unit]
Description=Steamlink GUI
After=graphical.target

[Service]
ExecStart=/usr/local/bin/steamlink-gui
Restart=always
User=pi
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/pi/.Xauthority

[Install]
WantedBy=graphical.target
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
Kodi | kodi | kodi.png

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