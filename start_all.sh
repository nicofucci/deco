#!/bin/bash
echo "Starting Deco-Security Services..."

# Start Core Stack (Orchestrator, DB, Redis)
cd /opt/deco/tower
docker compose up -d

# Start Agent Runtime Stack (Jarvis, etc.)
cd /opt/deco/docker
docker compose up -d

echo "All services started."
