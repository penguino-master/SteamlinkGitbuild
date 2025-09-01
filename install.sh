#!/bin/bash
set -e

echo "🔧 Installing Steamlink GUI system-wide..."

# Update and install dependencies
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-pyqt6 \
    python3-pyqt6.qt6 \
    python3-pyqt6.qt6webkit \
    python3-pygame \
    git

# Upgrade pip and allow system installs
python3 -m pip install --upgrade pip setuptools wheel --break-system-packages

# Install any additional Python packages not in apt
python3 -m pip install \
    requests \
    --break-system-packages

# Create target directory
sudo mkdir -p /opt/steamlink-gui
sudo cp -r ./* /opt/steamlink-gui/

# Make launcher command
echo '#!/bin/bash
python3 /opt/steamlink-gui/main.py' | sudo tee /usr/local/bin/steamlink-gui > /dev/null
sudo chmod +x /usr/local/bin/steamlink-gui

echo "✅ Install complete!"
echo "You can run the app with: steamlink-gui"
