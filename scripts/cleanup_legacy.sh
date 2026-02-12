#!/bin/bash
set -euo pipefail

BACKUP_DIR="$HOME/deco_backup_legacy_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "Iniciando limpieza de rutas redundantes..."
echo "Los archivos se moverán a: $BACKUP_DIR"

# Lista de directorios a mover
DIRS_TO_MOVE=(
  "$HOME/agent"
  "$HOME/deco"
  "$HOME/services"
  "$HOME/agent_core"
)

# Crear README en backup
cat <<EOF > "$BACKUP_DIR/README.md"
# Backup Legacy Deco-Gravity
Fecha: $(date)

Este directorio contiene versiones antiguas y redundantes de Deco-Gravity que fueron removidas de $HOME para normalizar la instalación en /opt/deco.

## Contenido:
- agent/: Versión monolítica antigua.
- deco/: Instalación parcial.
- services/: Scripts de desarrollo desordenados.
- agent_core/: Núcleo antiguo (Python monolith).

Los servicios systemd asociados (voice-server, xtts-server, agent_core, etc.) fueron detenidos y deshabilitados antes de mover estos archivos.
EOF

for dir in "${DIRS_TO_MOVE[@]}"; do
  if [ -d "$dir" ]; then
    echo "Moviendo $dir -> $BACKUP_DIR/"
    mv "$dir" "$BACKUP_DIR/"
  else
    echo "Directorio $dir no encontrado, saltando."
  fi
done

echo "Limpieza completada."
echo "La única ruta activa del proyecto es ahora: /opt/deco"
