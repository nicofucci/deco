#!/bin/bash
# Test script for Linux Build Validation

echo "Validating Linux Agent Build..."

# 1. Check Service Status
if systemctl is-active --quiet deco-security-agent; then
    echo "[PASS] Service is running."
else
    echo "[FAIL] Service is NOT running."
fi

# 2. Check User
if id "decoagent" &>/dev/null; then
    echo "[PASS] User 'decoagent' exists."
else
    echo "[FAIL] User 'decoagent' missing."
fi

# 3. Check Files
if [ -f "/opt/deco-security-agent/main.py" ]; then
    echo "[PASS] Agent files installed."
else
    echo "[FAIL] Agent files missing."
fi

# 4. Check Logs
LOG_FILE="/var/log/deco-security-agent/agent.log"
# Fallback log location check
if [ ! -f "$LOG_FILE" ]; then
    LOG_FILE="/opt/deco-security-agent/logs/agent.log"
fi

if [ -f "$LOG_FILE" ]; then
    echo "[PASS] Log file exists at $LOG_FILE."
    tail -n 5 "$LOG_FILE"
else
    echo "[WARN] Log file not found yet (service might be starting)."
fi
