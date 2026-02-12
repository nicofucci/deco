#!/bin/bash

ORCH_URL="http://127.0.0.1:19001"
MASTER_KEY="DECO-231908!@"

echo "🛡️ Testing Risk Panel Backend..."

# 1. Risk Radar
echo "[*] Fetching Risk Radar Data..."
RADAR_RESP=$(curl -s -X GET "$ORCH_URL/api/admin/risk-radar" \
  -H "X-Admin-Master-Key: $MASTER_KEY")
echo "    Response: $RADAR_RESP"

# 2. Network Topology
echo "[*] Fetching Network Topology..."
TOPOLOGY_RESP=$(curl -s -X GET "$ORCH_URL/api/admin/network-topology" \
  -H "X-Admin-Master-Key: $MASTER_KEY")
echo "    Response: $TOPOLOGY_RESP"
