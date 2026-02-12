#!/bin/bash

ORCH_URL="http://127.0.0.1:19001"
MASTER_KEY="DECO-231908!@"
CLIENT_ID="0fe5d919-edc1-4e5e-affc-a9e2fc1652f8" # Cliente Demo QA

echo "💳 Testing Billing Engine..."

# 1. List Plans
echo "[*] Listing Plans..."
PLANS_RESP=$(curl -s -X GET "$ORCH_URL/api/billing/plans" \
  -H "X-Admin-Master-Key: $MASTER_KEY")
echo "    Response: $PLANS_RESP"

# 2. Subscribe to Pro
echo "[*] Subscribing to Pro..."
SUB_RESP=$(curl -s -X POST "$ORCH_URL/api/billing/subscribe" \
  -H "X-Admin-Master-Key: $MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"client_id\": \"$CLIENT_ID\", \"plan_id\": \"pro\"}")
echo "    Response: $SUB_RESP"

# 3. Check Status
echo "[*] Checking Status..."
STATUS_RESP=$(curl -s -X GET "$ORCH_URL/api/billing/status/$CLIENT_ID" \
  -H "X-Admin-Master-Key: $MASTER_KEY")
echo "    Response: $STATUS_RESP"

# 4. Get Portal URL
echo "[*] Getting Portal URL..."
PORTAL_RESP=$(curl -s -X GET "$ORCH_URL/api/billing/portal/$CLIENT_ID" \
  -H "X-Admin-Master-Key: $MASTER_KEY")
echo "    Response: $PORTAL_RESP"
