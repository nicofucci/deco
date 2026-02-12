#!/bin/bash

# Config
API_URL="http://127.0.0.1:19001"
# Usamos una API Key de cliente conocida (del seed o fases previas)
CLIENT_API_KEY="cc1ac00c5e114f487a4363cb5c0cfb62e9765f9ca1e3c7f274f6f96c12519432"

# Directorio del agente
AGENT_DIR="/opt/deco/agent_kali"

echo "🔥 1. Preparing Agent Environment..."
# Limpiar config previa para forzar registro
rm -f "$AGENT_DIR/config.json"
# Pasar API Key por ENV
export DECO_CLIENT_API_KEY="$CLIENT_API_KEY"

echo "🔥 2. Starting Agent in Background..."
cd "$AGENT_DIR"
# Ejecutamos en background y guardamos PID
nohup python3 agent.py > logs/test_run.log 2>&1 &
AGENT_PID=$!
echo "   Agent PID: $AGENT_PID"

echo "   Waiting 5s for registration..."
sleep 5

# Verificar si se creó config.json
if [ -f "config.json" ]; then
    echo "✅ Agent registered successfully (config.json created)."
    cat config.json
else
    echo "❌ Agent failed to register."
    cat logs/test_run.log
    kill $AGENT_PID
    exit 1
fi

AGENT_ID=$(jq -r '.agent_id' config.json)

echo "🔥 3. Creating a ScanJob for the Agent..."
# Target localhost para que sea rápido y seguro
JOB_RESP=$(curl -s -X POST "$API_URL/api/jobs" \
  -H "Content-Type: application/json" \
  -H "X-Client-API-Key: $CLIENT_API_KEY" \
  -d "{
    \"client_id\":\"IGNORADO\",
    \"agent_id\": \"$AGENT_ID\",
    \"type\":\"discovery\",
    \"target\":\"127.0.0.1\"
  }")
JOB_ID=$(echo $JOB_RESP | jq -r '.id')
echo "   Job ID: $JOB_ID"

echo "🔥 4. Waiting for Job Completion (max 30s)..."
for i in {1..6}; do
    sleep 5
    STATUS_RESP=$(curl -s -X GET "$API_URL/api/jobs" -H "X-Client-API-Key: $CLIENT_API_KEY")
    # Filtrar nuestro job
    JOB_STATUS=$(echo $STATUS_RESP | jq -r ".[] | select(.id==\"$JOB_ID\") | .status")
    echo "   Current Status: $JOB_STATUS"
    
    if [ "$JOB_STATUS" == "done" ]; then
        echo "✅ Job completed!"
        break
    fi
    
    if [ "$i" -eq 6 ]; then
        echo "❌ Timeout waiting for job completion."
        echo "   Agent Logs:"
        tail -n 20 logs/agent.log
        kill $AGENT_PID
        exit 1
    fi
done

echo "🔥 5. Verifying Findings..."
FINDINGS_RESP=$(curl -s -X GET "$API_URL/api/findings" -H "X-Client-API-Key: $CLIENT_API_KEY")
echo "   Findings count: $(echo $FINDINGS_RESP | jq '. | length')"
echo $FINDINGS_RESP | jq .

echo "🔥 6. Cleaning Up..."
kill $AGENT_PID
echo "✅ Test Completed Successfully."
