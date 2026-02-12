#!/bin/bash
set -euo pipefail

echo "🛑 Stopping Deco Tower System..."

# Stop Frontends
echo "[*] Stopping Frontend Consoles..."
fuser -k 3006/tcp || true
fuser -k 3007/tcp || true
fuser -k 3005/tcp || true
echo "✅ Frontends stopped."

# Stop Backend
echo "[*] Stopping Backend Services..."
cd /opt/deco/tower
docker compose stop
echo "✅ Backend stopped."

echo "👋 System shutdown complete."
