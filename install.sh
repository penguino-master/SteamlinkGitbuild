#!/bin/bash
set -e

REPO_URL="https://github.com/penguino-master/SteamlinkGitbuild.git"
INSTALL_DIR="/opt/steamlink-gui"

echo "🔧 Installing Steamlink GUI system-wide for Raspberry Pi OS..."

# Install system dependencies
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-pyqt5 \
    python3-pyqt5.qtsvg \
    python3-pygame \
    git

# Upgrade pip
python3 -m pip install --upgrade pip setuptools wheel --break-system-packages

# Clone or update the repo
if [ -d "$INSTALL_DIR" ]; then
    echo "🔄 Updating existing installation..."
    sudo git -C "$INSTALL_DIR" pull
else
    echo "⬇️ Cloning repository..."
    sudo git clone "$REPO_URL" "$INSTALL_DIR"
fi

# Create launcher script
echo '#!/bin/bash
python3 /opt/steamlink-gui/main.py' | sudo tee /usr/local/bin/steamlink-gui > /dev/null
sudo chmod +x /usr/local/bin/steamlink-gui

echo "✅ Installation complete!"
echo "Run the app with: steamlink-gui"
