#!/bin/bash

# Test Deco-Security Agent Locally
# This script runs the agent in the current terminal (debug mode)

# 1. Setup Environment
export PYTHONPATH=$PYTHONPATH:$(pwd)
TEST_API_KEY="TEST_KEY_12345"

echo "🧪 Starting Agent Test..."
echo "API Key: $TEST_API_KEY"

# 2. Register (Simulate Install)
echo "[*] Registering Agent..."
python3 agent_main.py --api-key "$TEST_API_KEY"

# 3. Run Agent
echo "[*] Running Agent (Press Ctrl+C to stop)..."
python3 agent_main.py
