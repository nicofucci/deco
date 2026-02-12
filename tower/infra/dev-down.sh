#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

echo "🧹 Deteniendo stack Deco-Security..."
docker compose down

echo "✅ Stack detenido."
