#!/bin/bash

ORCH_URL="http://127.0.0.1:19001"
MASTER_KEY="DECO-231908!@"
CLIENT_ID="0fe5d919-edc1-4e5e-affc-a9e2fc1652f8" # Cliente Demo QA

echo "🚀 Testing Advanced Modules..."

# 1. Threat Intel
echo "[*] Testing Threat Intel (IP Reputation)..."
IP="192.168.1.10" # Should be malicious (ends in 0)
INTEL_RESP=$(curl -s -X GET "$ORCH_URL/api/intel/ip/$IP" \
  -H "X-Admin-Master-Key: $MASTER_KEY")
echo "    Response: $INTEL_RESP"

# 2. SIEM Config
echo "[*] Configuring SIEM Webhook..."
SIEM_RESP=$(curl -s -X POST "$ORCH_URL/api/admin/siem-config" \
  -H "X-Admin-Master-Key: $MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"client_id\": \"$CLIENT_ID\", \"webhook_url\": \"https://webhook.site/test\"}")
echo "    Response: $SIEM_RESP"
