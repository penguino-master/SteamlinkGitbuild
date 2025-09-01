#!/bin/bash
set -e

APP_DIR="/opt/steamlink-gui"
REPO_URL="https://github.com/penguino-master/SteamlinkGitbuild.git"

echo "🔹 Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip git

if [ ! -d "$APP_DIR" ]; then
    echo "🔹 Cloning repo to $APP_DIR..."
    sudo git clone "$REPO_URL" "$APP_DIR"
else
    echo "🔹 Repo exists, pulling latest changes..."
    cd "$APP_DIR"
    sudo git pull
fi

echo "🔹 Installing Python dependencies..."
cd "$APP_DIR"
sudo pip3 install -r requirements.txt

echo "🔹 Creating steamlink-gui launcher..."
sudo tee /usr/local/bin/steamlink-gui > /dev/null <<EOF
#!/bin/bash
cd $APP_DIR
python3 main.py
EOF
sudo chmod +x /usr/local/bin/steamlink-gui

echo "✅ Installation complete! Run 'steamlink-gui' to start the app."
