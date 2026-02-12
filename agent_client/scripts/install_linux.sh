#!/bin/bash

# Deco-Security Agent Installer (Linux)
# Usage: sudo ./install_linux.sh <CLIENT_API_KEY> <ORCH_URL>

API_KEY=$1
ORCH_URL=${2:-"http://127.0.0.1:19001"}
INSTALL_DIR="/opt/deco/agent_client"
USER="decoagent"

if [ -z "$API_KEY" ]; then
    echo "Usage: sudo ./install_linux.sh <CLIENT_API_KEY> [ORCH_URL]"
    exit 1
fi

echo "[*] Installing Deco-Security Agent..."

# 1. Dependencies
echo "[*] Checking dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "[!] Python3 not found. Installing..."
    apt-get update && apt-get install -y python3 python3-pip
fi
if ! command -v nmap &> /dev/null; then
    echo "[!] Nmap not found. Installing..."
    apt-get update && apt-get install -y nmap
fi

# 2. Create User
if ! id "$USER" &>/dev/null; then
    echo "[*] Creating user $USER..."
    useradd -r -s /bin/false $USER
fi

# 3. Copy Files
echo "[*] Copying files to $INSTALL_DIR..."
mkdir -p $INSTALL_DIR
cp -r ../agent $INSTALL_DIR/
chown -R $USER:$USER $INSTALL_DIR

# 4. Config
echo "[*] Creating configuration..."
mkdir -p /etc/deco-agent
cat <<EOF > /etc/deco-agent/config.env
CLIENT_API_KEY=$API_KEY
ORCH_URL=$ORCH_URL
HEARTBEAT_INTERVAL=30
EOF
chown $USER:$USER /etc/deco-agent/config.env
chmod 600 /etc/deco-agent/config.env

# 5. Systemd Service
echo "[*] Creating systemd service..."
cat <<EOF > /etc/systemd/system/deco-agent.service
[Unit]
Description=Deco-Security Agent
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/agent/main.py
Restart=always
RestartSec=10
EnvironmentFile=/etc/deco-agent/config.env

[Install]
WantedBy=multi-user.target
EOF

# 6. Enable & Start
echo "[*] Starting service..."
systemctl daemon-reload
systemctl enable deco-agent
systemctl restart deco-agent

echo "[+] Installation Complete! Agent is running."
