#!/bin/bash
set -euo pipefail

# Deco Tower - Global Startup Script (V3)
# Starts the full Docker stack.

LOG_FILE="/opt/deco/logs/start_tower_$(date +%F_%H-%M).log"
mkdir -p /opt/deco/logs

echo "🚀 Starting Deco Tower System (V3 Stack)..." | tee -a "$LOG_FILE"

# 1. Start Docker Stack
echo "[*] Launching Docker V3 Stack..." | tee -a "$LOG_FILE"
cd /opt/deco/docker
# Ensure we pull/build if needed, or just up
docker compose up -d >> "$LOG_FILE" 2>&1

echo "    ⏳ Waiting for Orchestrator API to be healthy..." | tee -a "$LOG_FILE"
MAX_RETRIES=60
COUNT=0
# Orchestrator is on port 18001 mapped to host
while ! curl -s http://localhost:18001/doc > /dev/null; do
    sleep 2
    COUNT=$((COUNT+1))
    if [ $COUNT -ge $MAX_RETRIES ]; then
        echo "⚠️ Timed out waiting for Orchestrator API on port 18001." | tee -a "$LOG_FILE"
        break
    fi
    echo -n "."
done

echo -e "\n✅ Stack Startup Command Completed." | tee -a "$LOG_FILE"

echo "🎉 System Status:" | tee -a "$LOG_FILE"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | tee -a "$LOG_FILE"

echo "   - Master Console: http://localhost:3006" | tee -a "$LOG_FILE"
echo "   - Partner Console: http://localhost:3007" | tee -a "$LOG_FILE"
echo "   - Client Console: http://localhost:3005" | tee -a "$LOG_FILE"
echo "   - Orchestrator API: http://localhost:18001" | tee -a "$LOG_FILE"
