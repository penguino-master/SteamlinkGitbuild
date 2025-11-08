#!/bin/bash

# Perms for FB (one-time, but idempotent)
sudo chmod 666 /dev/fb0 2>/dev/null
sudo usermod -a -G video $USER 2>/dev/null

# Fire it
cd /opt/steamlink-gui && ./kiosk.sh