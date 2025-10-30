# Steamlink GUI

A lightweight, controller-friendly GUI application for Raspberry Pi, built with **PyQt6**, **Pygame**, and Python. This app provides a user interface to control various aspects of a Raspberry Pi running Debian GNU/Linux 12 (bookworm), with a focus on launching applications like **Steam Link**, managing Bluetooth devices, adjusting volume, and configuring system settings (e.g., resolution, shutdown).

The app is optimized for a semi-headless setup (boots to CLI but supports a graphical display via X11) and is navigable via keyboard or game controller, making it ideal for a Steam Link-focused media center on a Raspberry Pi 4B.

## Features
- **Application Launcher**: Launch apps like Steam Link from a grid of icons, configured via `programs.txt`.
- **Bluetooth Management**: Scan, pair, connect, and forget Bluetooth devices using `bluetoothctl`.
- **Volume Control**: Adjust system volume and mute state with a visual progress bar, powered by `pactl`.
- **System Options**: Restart, shut down, or exit the app; change display resolution (1080p/1440p) via `tvservice`.
- **Controller Support**: Navigate menus with a USB/Bluetooth game controller (D-pad, A/B buttons).
- **Dark Theme**: Modern, high-contrast UI with animated buttons for a polished look.
- **Full-Screen Interface**: Optimized for HDMI displays in a semi-headless environment.

## Prerequisites
- **Hardware**: Raspberry Pi (tested on Pi 4B, 2GB+ RAM recommended).
- **Operating System**: Debian GNU/Linux 12 (bookworm) with the full desktop environment installed, configured to boot to CLI (semi-headless).
- **Display**: HDMI monitor/TV connected for GUI rendering.
- **Input**: Keyboard or USB/Bluetooth game controller (e.g., Xbox, PlayStation).
- **Internet**: Required for initial installation (package downloads and Git cloning).
- **Filesystem**:
  - Ensure the Pi user (e.g., `pi`) has write access to `/opt/steamlink-gui`.
  - Optional: Place app icons in an `icons/` directory and list apps in `programs.txt`.

## Installation
The provided `install.sh` script automates dependency installation, clones/updates the repository, and sets up a system-wide launcher.

### Step 1: Clone the Repository
Clone this repository to your Raspberry Pi:
```bash
git clone https://github.com/penguino-master/SteamlinkGitbuild.git
cd SteamlinkGitbuild
```

### Step 2: Run the Installation Script
1. Make the script executable:
   ```bash
   chmod +x install.sh
   ```
2. Run the script with sudo (installs to `/opt/steamlink-gui` and requires root for package installation):
   ```bash
   sudo ./install.sh
   ```
   The script will:
   - Install dependencies: `python3`, `python3-pyqt6`, `python3-pygame`, `pulseaudio-utils`, `bluez`, `raspi-config`, `steamlink`.
   - Clone or update the repo to `/opt/steamlink-gui`.
   - Create a launcher at `/usr/local/bin/steamlink-gui`.
   - Set up a default `programs.txt` with a Steam Link entry.

### Step 3: Verify Installation
After the script completes, you’ll see:
```
✅ Installation complete!
Run the app with: steamlink-gui
```
Test the app:
```bash
steamlink-gui
```
This launches the GUI in full-screen mode. Use a controller (D-pad, A/B buttons) or keyboard (arrows, Enter, Esc) to navigate.

## Usage
- **Launch the App**: Run `steamlink-gui` from the terminal.
- **Navigation**:
  - **Sidebar Menu**: Select options (Applications, Bluetooth, Volume, System) with Up/Down arrows or D-pad.
  - **Enter Menu**: Press Right arrow, A button, or Enter to enter a menu.
  - **Back**: Press Left arrow, B button, or Esc to return to the sidebar.
- **Applications**: Click app tiles (e.g., Steam Link) to launch programs listed in `programs.txt`.
- **Bluetooth**: Scan for devices, pair, connect, or forget devices.
- **Volume**: Adjust volume (+/- 5%) or toggle mute.
- **System**: Restart, shut down, or exit the app; change resolution (1080p/1440p, HDMI only).

### Configuring Applications
Edit `programs.txt` in `/opt/steamlink-gui` to add apps. Format:
```
App Name|command|icon_filename
```
Example for Steam Link:
```
Steam Link|steamlink|steamlink.png
```
- Place icon files (e.g., `steamlink.png`) in `/opt/steamlink-gui/icons/`.
- Icons should be PNG/JPG, sized for a 200x300px tile (2:3 ratio).

## Auto-Start on Boot
To launch the app automatically on boot:
1. Edit the user’s crontab:
   ```bash
   crontab -e
   ```
2. Add:
   ```bash
   @reboot sleep 5 && /usr/local/bin/steamlink-gui
   ```
   The `sleep 5` ensures X11 initializes before the app starts.

## Troubleshooting
- **GUI Fails to Start**:
  - Ensure an HDMI display is connected.
  - Check X11: `echo $DISPLAY` (should show `:0`). If empty, run `export DISPLAY=:0` or `startx &`.
  - View X11 logs: `cat /var/log/Xorg.0.log`.
- **Dependencies Missing**:
  - Verify: `dpkg -l | grep -E 'python3-pyqt6|python3-pygame|pulseaudio|bluez|raspi-config'`.
  - Re-run `sudo ./install.sh`.
- **Volume Control Fails**:
  - Ensure PulseAudio is running: `pulseaudio --start`.
  - Test: `pactl info`.
- **Bluetooth Issues**:
  - Ensure Bluetooth service is active: `sudo systemctl start bluetooth`.
  - Test: `bluetoothctl list`.
- **Steam Link Not Launching**:
  - Verify installation: `command -v steamlink`.
  - Install manually: `sudo apt install steamlink`.
- **Git Errors**:
  - If the repo is private, set up SSH keys or HTTPS credentials:
    ```bash
    git config --global credential.helper store
    ```
  - Test: `git ls-remote https://github.com/penguino-master/SteamlinkGitbuild.git`.
- **Logs**: Run with `steamlink-gui 2> error.log` and check `error.log` or `journalctl -f`.

## Development
- **Dependencies**: See `install.sh` for the full list (`python3-pyqt6`, `python3-pygame`, etc.).
- **Code Structure**:
  - `main.py`: Entry point, sets global dark theme.
  - `gui_mainmenu.py`: Main UI with sidebar and stacked layout.
  - `menu_application.py`: App launcher grid.
  - `menu_bluetooth.py`: Bluetooth device management.
  - `menu_volume.py`: Volume control with `pactl`.
  - `menu_system.py`: System controls (restart, shutdown, resolution).
  - `animated_button.py`: Custom button with animations.
  - `controller.py`: Pygame-based controller input handling.
- **Contributing**: Fork, modify, and submit pull requests to this repository.

## Notes
- Designed for Raspberry Pi 4B on Debian GNU/Linux 12 (bookworm, semi-headless).
- Requires an X11 display server (auto-started by the launcher if needed).
- Tested with HDMI displays and USB/Bluetooth controllers.
- For fully headless setups, run a VNC server:
  ```bash
  sudo apt install tightvncserver
  vncserver :1 -geometry 1920x1080 -depth 16
  export DISPLAY=:1
  steamlink-gui
  ```

## License
MIT License (or specify your preferred license).# Steamlink GUI