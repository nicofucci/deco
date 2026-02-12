#!/bin/bash

ORCH_URL="http://127.0.0.1:19001"
MASTER_KEY="DECO-231908!@"

echo "🧠 Testing AI Engine..."

# 1. Train Model
echo "[*] Training Model..."
TRAIN_RESP=$(curl -v -X POST "$ORCH_URL/api/ai/train" \
  -H "X-Admin-Master-Key: $MASTER_KEY")
echo "    Response: $TRAIN_RESP"

# 2. Predict Low Risk
echo "[*] Predicting Low Risk (Severity: low)..."
PRED_LOW=$(curl -v -X POST "$ORCH_URL/api/ai/predict" \
  -H "Content-Type: application/json" \
  -d '{"severity": "low", "title": "Web Server"}')
echo "    Response: $PRED_LOW"

# 3. Predict High Risk
echo "[*] Predicting High Risk (Severity: critical)..."
PRED_HIGH=$(curl -v -X POST "$ORCH_URL/api/ai/predict" \
  -H "Content-Type: application/json" \
  -d '{"severity": "critical", "title": "RDP Exposed"}')
echo "    Response: $PRED_HIGH"
