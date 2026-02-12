#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${ORCHESTRATOR_API_URL:-http://127.0.0.1:18001}"

health=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health" || echo "ERR")
printf "Orchestrator API (%s/health): %s\n" "$BASE_URL" "$health"

if [ "$health" != "200" ]; then
  echo "Detalle:" >&2
  curl -v "$BASE_URL/health" || true
fi
