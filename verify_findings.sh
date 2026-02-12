#!/bin/bash

# Config
API_URL="http://127.0.0.1:19001"
CLIENT_API_KEY="cc1ac00c5e114f487a4363cb5c0cfb62e9765f9ca1e3c7f274f6f96c12519432" # Reusing from previous phase
AGENT_ID="bb7ebf96-1098-4033-97d9-f244931d1a57" # Reusing from previous phase

echo "🔥 1. Creating a new ScanJob for Verification..."
JOB_RESP=$(curl -s -X POST $API_URL/api/jobs \
  -H "Content-Type: application/json" \
  -H "X-Client-API-Key: $CLIENT_API_KEY" \
  -d '{
    "client_id":"IGNORADO",
    "agent_id":null,
    "type":"discovery",
    "target":"10.0.0.50"
  }')
JOB_ID=$(echo $JOB_RESP | jq -r '.id')
echo "   Job ID: $JOB_ID"

echo "🔥 2. Uploading Simulated Result with Critical Ports..."
curl -s -X POST $API_URL/api/results \
  -H "Content-Type: application/json" \
  -H "X-Client-API-Key: $CLIENT_API_KEY" \
  -d "{
    \"scan_job_id\": \"$JOB_ID\",
    \"agent_id\": \"$AGENT_ID\",
    \"raw_data\": {
      \"tool\": \"nmap-simulado\",
      \"target\": \"10.0.0.50\",
      \"hostname\": \"critical-server\",
      \"open_ports\": [22, 80, 445, 3389]
    },
    \"summary\": {
      \"status\": \"OK\"
    }
  }" | jq

echo "🔥 3. Verifying Findings..."
curl -s -X GET $API_URL/api/findings \
  -H "X-Client-API-Key: $CLIENT_API_KEY" | jq
