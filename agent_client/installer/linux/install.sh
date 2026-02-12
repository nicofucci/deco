#!/bin/bash
set -e

# Deco-Security Agent Installer for Linux
# Usage: sudo ./install.sh <API_KEY>

API_KEY=$1

if [ -z "$API_KEY" ]; then
    echo "Usage: sudo ./install.sh <API_KEY>"
    exit 1
fi

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

INSTALL_DIR="/opt/deco-agent"
BIN_DIR="$INSTALL_DIR/bin"
MODULES_DIR="$INSTALL_DIR/modules"
SERVICE_FILE="/etc/systemd/system/deco-agent.service"

echo "Installing Deco-Security Agent..."

# 1. Create Directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$MODULES_DIR"
mkdir -p "/etc/deco-security"
mkdir -p "/var/log/deco-agent"

# 2. Copy Files (Assuming running from source root)
# In a real distribution, this would copy from the unpacked archive
SOURCE_DIR=$(dirname "$0")/../..
cp "$SOURCE_DIR/agent_main.py" "$INSTALL_DIR/"
cp "$SOURCE_DIR/config.py" "$INSTALL_DIR/"
cp "$SOURCE_DIR/updater.py" "$INSTALL_DIR/"
cp -r "$SOURCE_DIR/modules/"* "$MODULES_DIR/"

# 3. Install Dependencies (Minimal)
# Assuming python3 is installed. We might need to create a venv.
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Installing..."
    apt-get update && apt-get install -y python3 python3-pip
fi

# Install python requests if not present
pip3 install requests --break-system-packages || pip3 install requests

# 4. Configure API Key
python3 "$INSTALL_DIR/agent_main.py" --api-key "$API_KEY"

# 5. Create Systemd Service
cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=Deco-Security Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/agent_main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 6. Enable and Start Service
systemctl daemon-reload
systemctl enable deco-agent
systemctl start deco-agent

echo "Deco-Security Agent installed and started successfully."
