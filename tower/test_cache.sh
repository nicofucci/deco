#!/bin/bash

ORCH_URL="http://127.0.0.1:19001"
MASTER_KEY="DECO-231908!@"

echo "🚀 Testing Redis Cache..."

# 1. First Call (Cache Miss)
echo "[*] First Call (Cache Miss)..."
start_time=$(date +%s%N)
curl -s -o /dev/null -X GET "$ORCH_URL/api/admin/global-stats" -H "X-Admin-Master-Key: $MASTER_KEY"
end_time=$(date +%s%N)
duration=$((($end_time - $start_time)/1000000))
echo "    Time: ${duration}ms"

# 2. Second Call (Cache Hit)
echo "[*] Second Call (Cache Hit)..."
start_time=$(date +%s%N)
curl -s -o /dev/null -X GET "$ORCH_URL/api/admin/global-stats" -H "X-Admin-Master-Key: $MASTER_KEY"
end_time=$(date +%s%N)
duration=$((($end_time - $start_time)/1000000))
echo "    Time: ${duration}ms"

if [ $duration -lt 50 ]; then
    echo "    ✅ Cache is working!"
else
    echo "    ⚠️ Cache might not be working (or network latency)."
fi
