#!/bin/bash

# Deco-Security Agent Uninstaller

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

echo "Uninstalling Deco-Security Agent..."

systemctl stop deco-agent
systemctl disable deco-agent
rm /etc/systemd/system/deco-agent.service
systemctl daemon-reload

rm -rf /opt/deco-agent
rm -rf /etc/deco-security
rm -rf /var/log/deco-agent

echo "Uninstallation complete."
