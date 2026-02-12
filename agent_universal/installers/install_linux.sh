#!/bin/bash
set -euo pipefail

# Deco-Security Agent Installer (Linux, systemd)
# Idempotent: safe to re-run, preserves existing config.

INSTALL_DIR="/opt/deco/agent_universal"
SRC_DIR="$INSTALL_DIR/src"
CONFIG_DIR="/etc/deco-security-agent"
CONFIG_FILE="$CONFIG_DIR/config.json"
SERVICE_FILE="/etc/systemd/system/deco-security-agent.service"
LOG_DIR="/var/log/deco-security-agent"

ORCH_URL="${DECO_ORCHESTRATOR_URL:-http://127.0.0.1:8001}"
API_KEY="${X_CLIENT_API_KEY:-${DECO_CLIENT_API_KEY:-}}"
AGENT_MODE="${AGENT_MODE:-prod}"
AGENT_VERSION="${AGENT_VERSION:-2.0.0-universal}"

echo "[Installer] Deco-Security Agent (Linux)"

if [[ $EUID -ne 0 ]]; then
  echo "ERROR: run as root (needed for systemd + /etc writes)." >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is required." >&2
  exit 1
fi

# Prepare directories
mkdir -p "$CONFIG_DIR" "$LOG_DIR"

# Seed config if missing
if [[ ! -f "$CONFIG_FILE" ]]; then
  cat >"$CONFIG_FILE" <<EOF
{
  "orchestrator_url": "$ORCH_URL",
  "api_key": "${API_KEY}",
  "agent_id": null,
  "agent_mode": "$AGENT_MODE",
  "agent_version": "$AGENT_VERSION",
  "last_sync": null,
  "last_error": null
}
EOF
  chmod 600 "$CONFIG_FILE"
  echo "[Installer] Created config at $CONFIG_FILE"
else
  echo "[Installer] Config exists, keeping $CONFIG_FILE"
fi

# Service unit
echo "[Installer] Writing systemd unit..."
cat >"$SERVICE_FILE" <<EOF
[Unit]
Description=Deco-Security Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$SRC_DIR
Environment=PYTHONUNBUFFERED=1
Environment=DECO_ORCHESTRATOR_URL=$ORCH_URL
Environment=AGENT_MODE=$AGENT_MODE
Environment=AGENT_VERSION=$AGENT_VERSION
ExecStart=/usr/bin/python3 $SRC_DIR/main.py
Restart=always
RestartSec=5
StandardOutput=append:$LOG_DIR/service.log
StandardError=append:$LOG_DIR/service.log

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable deco-security-agent
systemctl restart deco-security-agent || true

echo "[Installer] Done. Check status with: python3 $SRC_DIR/main.py status"
