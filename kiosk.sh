#!/bin/bash
cd /opt/steamlink-gui

# Kill remnants
pkill -f python3 2>/dev/null

# LinuxFB: Direct framebuffer, no X
export QT_QPA_PLATFORM=linuxfb
export QT_QPA_FB_CONSOLE=/dev/tty1
export QT_QPA_LINUXFB_BUFFER_SIZE=1920x1080

# HDMI wake/blank off (Zero 2 W)
echo 0 | sudo tee /sys/class/graphics/fb0/blank >/dev/null
vcgencmd display_power 1

# Launch GUI
python3 main.py

echo "Kiosk exited—console ready."