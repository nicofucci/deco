#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

echo "🗄️ Inicializando base de datos Deco-Security (creando tablas)..."

# Ejecutamos el script de inicialización dentro del contenedor que YA está corriendo
docker exec deco-sec-orchestrator python -m app.db.init_db

echo "✅ Base de datos inicializada."
