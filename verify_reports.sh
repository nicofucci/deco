#!/bin/bash

# Config
API_URL="http://127.0.0.1:19001"
CLIENT_API_KEY="cc1ac00c5e114f487a4363cb5c0cfb62e9765f9ca1e3c7f274f6f96c12519432"

echo "🔥 1. Requesting Executive Report..."
REPORT_JSON=$(curl -s -X GET "$API_URL/api/reports/executive" \
  -H "X-Client-API-Key: $CLIENT_API_KEY")

echo "   Response received."

# Extract content
CONTENT=$(echo $REPORT_JSON | jq -r '.content')

if [ "$CONTENT" == "null" ]; then
    echo "❌ Error: Report content is null."
    echo $REPORT_JSON
    exit 1
fi

echo "🔥 2. Validating Content..."
echo "---------------------------------------------------"
echo "$CONTENT" | head -n 20
echo "---------------------------------------------------"

if [[ "$CONTENT" == *"Informe Ejecutivo"* ]]; then
    echo "✅ Report contains expected header."
else
    echo "❌ Report header missing."
fi

if [[ "$CONTENT" == *"Nivel de Riesgo Global"* ]]; then
    echo "✅ Risk level section found."
else
    echo "❌ Risk level section missing."
fi
