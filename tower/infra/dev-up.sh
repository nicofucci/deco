#!/usr/bin/env bash
set -euo pipefail

# Ir a la carpeta raíz del proyecto (un nivel arriba de infra/)
cd "$(dirname "${BASH_SOURCE[0]}")/.."

echo "🚀 Levantando stack Deco-Security (DB, Redis, Orchestrator)..."
docker compose pull || true
docker compose up -d

echo "✅ Stack levantado. Servicios esperados:"
echo "  - deco-sec-db"
echo "  - deco-sec-redis"
echo "  - deco-sec-orchestrator (expuesto en http://127.0.0.1:19001)"
