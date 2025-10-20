#!/bin/bash
set -e

REPO_URL="https://github.com/penguino-master/SteamlinkGitbuild.git"
INSTALL_DIR="/opt/steamlink-gui"
USER_HOME=$(eval echo ~${SUDO_USER:-$USER})
LAUNCHER="/usr/local/bin/steamlink-gui"

echo "🔧 Installing/Updating Steamlink GUI for Raspberry Pi OS..."

# Check for Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "⚠️ Warning: This script is designed for Raspberry Pi. Non-Pi hardware may not fully support all features."
fi

# Check for internet connectivity
if ! ping -c 1 github.com &>/dev/null; then
    echo "❌ Error: No internet connection. Please connect to the internet and try again."
    exit 1
fi

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt update || { echo "❌ Failed to update apt. Check your sources or internet."; exit 1; }
sudo apt install -y \
    python3 \
    python3-pip \
    python3-pyqt6 \
    python3-pyqt6.qtsvg \
    python3-pygame \
    pulseaudio-utils \
    bluez \
    raspi-config \
    git || { echo "❌ Failed to install dependencies. Check apt logs."; exit 1; }

# Upgrade pip and ensure Python tools
echo "🔧 Upgrading pip and Python tools..."
python3 -m pip install --upgrade pip setuptools wheel --break-system-packages || { echo "❌ Failed to upgrade pip."; exit 1; }

# Clone or update the repo
if [ -d "$INSTALL_DIR" ]; then
    echo "🔄 Updating existing installation..."
    sudo git -C "$INSTALL_DIR" fetch
    sudo git -C "$INSTALL_DIR" reset --hard origin/main || { echo "❌ Failed to update git repo. Check permissions or conflicts."; exit 1; }
else
    echo "⬇️ Cloning repository..."
    sudo git clone "$REPO_URL" "$INSTALL_DIR" || { echo "❌ Failed to clone repo. Check URL or authentication."; exit 1; }
fi

# Set permissions for the install directory
sudo chown -R ${SUDO_USER:-$USER}:${SUDO_USER:-$USER} "$INSTALL_DIR"
sudo chmod -R u+rw "$INSTALL_DIR"

# Ensure icons and programs.txt exist
if [ ! -d "$INSTALL_DIR/icons" ]; then
    sudo -u ${SUDO_USER:-$USER} mkdir -p "$INSTALL_DIR/icons"
fi
if [ ! -f "$INSTALL_DIR/programs.txt" ]; then
    echo "Steam Link|steamlink|steamlink.png" | sudo -u ${SUDO_USER:-$USER} tee "$INSTALL_DIR/programs.txt" > /dev/null
fi

# Install Steam Link if not present
if ! command -v steamlink &>/dev/null; then
    echo "📦 Installing Steam Link..."
    sudo apt install -y steamlink || echo "⚠️ Warning: Failed to install steamlink. Install manually if needed."
fi

# Create launcher script with DISPLAY handling
echo '#!/bin/bash
# Ensure DISPLAY is set for GUI
if [ -z "$DISPLAY" ]; then
    export DISPLAY=:0
fi
# Start X11 if not running
if ! pgrep -x "Xorg" > /dev/null; then
    startx -- :0 &
    sleep 2
fi
# Run the app
python3 /opt/steamlink-gui/main.py' | sudo tee "$LAUNCHER" > /dev/null
sudo chmod +x "$LAUNCHER"

echo "✅ Installation complete!"
echo "Run the app with: steamlink-gui"
echo "Note: Ensure a display is connected (HDMI) and Bluetooth/controller are enabled if needed."