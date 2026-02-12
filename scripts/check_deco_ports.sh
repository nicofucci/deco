#!/usr/bin/env bash
set -euo pipefail

endpoints=(
  "3005|Consola Cliente|http://127.0.0.1:3005"
  "3006|Consola Master|http://127.0.0.1:3006"
  "3007|Consola Partner|http://127.0.0.1:3007"
  "18001|API Orquestador|http://127.0.0.1:18001/health"
)

printf "%-6s | %-18s | %-45s | %-6s\n" "Puerto" "Servicio" "URL" "HTTP"
printf -- "%.0s-" {1..86}; echo

for entry in "${endpoints[@]}"; do
  IFS='|' read -r port name url <<<"$entry"
  status=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "ERR")
  printf "%-6s | %-18s | %-45s | %-6s\n" "$port" "$name" "$url" "$status"
done

echo
echo "Nota: ejecutar manualmente con 'bash /opt/deco/scripts/check_deco_ports.sh'. Añadir a cron si se desea monitorizar."
