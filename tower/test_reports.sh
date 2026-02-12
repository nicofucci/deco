#!/bin/bash

ORCH_URL="http://127.0.0.1:19001"
MASTER_KEY="DECO-231908!@"
CLIENT_ID="0fe5d919-edc1-4e5e-affc-a9e2fc1652f8" # Cliente Demo QA

echo "📄 Testing Reports Engine..."

# 1. Generate Executive Report
echo "[*] Generating Executive Report..."
EXEC_RESP=$(curl -s -X POST "$ORCH_URL/api/reports/generate/$CLIENT_ID?type=executive" \
  -H "X-Admin-Master-Key: $MASTER_KEY")
echo "    Response: $EXEC_RESP"

# 2. Generate Technical Report
echo "[*] Generating Technical Report..."
TECH_RESP=$(curl -s -X POST "$ORCH_URL/api/reports/generate/$CLIENT_ID?type=technical" \
  -H "X-Admin-Master-Key: $MASTER_KEY")
echo "    Response: $TECH_RESP"

# 3. Download Report (if successful)
FILENAME=$(echo $EXEC_RESP | grep -o '"filename": *"[^"]*"' | cut -d'"' -f4)
if [ ! -z "$FILENAME" ]; then
    echo "[*] Downloading $FILENAME..."
    curl -s -X GET "$ORCH_URL/api/reports/download/$FILENAME" -o /tmp/$FILENAME
    if [ -f "/tmp/$FILENAME" ]; then
        echo "    ✅ Download successful: /tmp/$FILENAME"
        ls -lh /tmp/$FILENAME
    else
        echo "    ❌ Download failed"
    fi
else
    echo "    ⚠️ Could not parse filename from response"
fi
