#!/usr/bin/env bash
cd "$(dirname "$0")"

# Ensure python3-nmap is not needed as we use subprocess, but check for requests
# In a real scenario we would use a venv
# pip install -r requirements.txt

# Check for nmap
if ! command -v nmap &> /dev/null; then
    echo "❌ Nmap could not be found. Please install it (sudo apt install nmap)."
    exit 1
fi

echo "🚀 Starting Deco-Agent..."
python3 agent.py
