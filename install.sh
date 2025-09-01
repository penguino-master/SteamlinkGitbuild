#!/bin/bash
set -e

echo "🔧 Installing Steamlink GUI system-wide for Raspberry Pi OS..."

# Update and install dependencies
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-pyqt5 \
    python3-pyqt5.qtsvg \
    python3-pygame \
    git

# Upgrade pip and allow system installs
python3 -m pip install --upgrade pip setuptools wheel --break-system-packages

# Create target directory
sudo mkdir -p /opt/steamlink-gui
sudo cp -r ./* /opt/steamlink-gui/

# Make launcher command
echo '#!/bin/bash
python3 /opt/steamlink-gui/main.py' | sudo tee /usr/local/bin/steamlink-gui > /dev/null
sudo chmod +x /usr/local/bin/steamlink-gui

echo "✅ Install complete!"
echo "Run the app with: steamlink-gui"
