#!/bin/bash
set -e

REPO_URL="https://github.com/penguino-master/SteamlinkGitbuild.git"
INSTALL_DIR="/opt/steamlink-gui"
USER_HOME=$(eval echo ~${SUDO_USER:-$USER})
LAUNCHER="/usr/local/bin/steamlink-gui"
KIOSK_LAUNCHER="/usr/local/bin/steamlink-kiosk"

echo "🔧 Installing Steamlink GUI for Pi Zero 2 W..."

# Pi check/internet
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "⚠️ Non-Pi hardware—features may vary."
fi
if ! ping -c 1 github.com &>/dev/null; then
    echo "❌ No net—bail."
    exit 1
fi

# Deps (add FB/video)
sudo apt update
sudo apt install -y python3 python3-pip python3-pyqt6 python3-pygame pulseaudio-utils bluez raspi-config git libgles2-mesa libegl1-mesa

# Clone/update repo
if [ -d "$INSTALL_DIR" ]; then
    echo "🔄 Updating..."
    sudo git -C "$INSTALL_DIR" pull origin main
else
    echo "⬇️ Cloning..."
    sudo git clone "$REPO_URL" "$INSTALL_DIR"
fi

# Perms/icons/programs.txt
sudo chown -R ${SUDO_USER:-$USER}:${SUDO_USER:-$USER} "$INSTALL_DIR"
sudo chmod -R u+rw "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/icons"
echo "Steam Link|steamlink|steamlink.png" > "$INSTALL_DIR/programs.txt"

# Auto-chmod scripts (kiosk.sh and steamlink-kiosk.sh)
sudo chmod +x "$INSTALL_DIR/kiosk.sh" "$INSTALL_DIR/steamlink-kiosk.sh" 2>/dev/null || true  # Idempotent, ignores if missing

# Clean up any temp home dir leftovers (e.g., ~/steamlink or ~/SteamlinkGitbuild)
TEMP_HOME_DIR="$USER_HOME/steamlink"
if [ -d "$TEMP_HOME_DIR" ]; then
    echo "🧹 Cleaning up temp ~/steamlink dir..."
    rm -rf "$TEMP_HOME_DIR"
fi
TEMP_GIT_DIR="$USER_HOME/SteamlinkGitbuild"
if [ -d "$TEMP_GIT_DIR" ]; then
    echo "🧹 Cleaning up temp ~/SteamlinkGitbuild dir..."
    rm -rf "$TEMP_GIT_DIR"
fi

# Steamlink if missing
if ! command -v steamlink; then
    sudo apt install -y steamlink
fi

# FB perms (Zero 2 W)
sudo usermod -a -G video ${SUDO_USER:-$USER}
sudo chmod 666 /dev/fb0 2>/dev/null || true

# HDMI config (append if not set)
if ! grep -q "hdmi_mode=82" /boot/config.txt; then
    echo "[all]" | sudo tee -a /boot/config.txt
    echo "hdmi_force_hotplug=1" | sudo tee -a /boot/config.txt
    echo "hdmi_group=2" | sudo tee -a /boot/config.txt
    echo "hdmi_mode=82" | sudo tee -a /boot/config.txt
fi

# Launcher: steamlink-gui (runs kiosk.sh)
cat > "$LAUNCHER" << EOF
#!/bin/bash
export DISPLAY=:0  # Fallback for X if needed
cd $INSTALL_DIR && ./kiosk.sh
EOF
sudo chmod +x "$LAUNCHER"

# Kiosk launcher
cat > "$KIOSK_LAUNCHER" << EOF
#!/bin/bash
$USER_HOME/steamlink-kiosk.sh
EOF
sudo chmod +x "$KIOSK_LAUNCHER"

# Autostart: Console to kiosk
echo "@reboot sleep 10 && $KIOSK_LAUNCHER" | crontab -

echo "✅ Done! Run: steamlink-gui (X fallback) or steamlink-kiosk (FB direct)."
echo "Reboot for autostart."