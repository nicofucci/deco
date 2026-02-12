#!/bin/bash

# Config
DASHBOARD_DIR="/opt/deco/dashboard_security"
PORT=3005

echo "🚀 Initializing Deco-Security Dashboard..."

cd "$DASHBOARD_DIR"

# Ensure dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "⚠️ .env.local not found. Creating default..."
    echo "NEXT_PUBLIC_ORCHESTRATOR_URL=http://127.0.0.1:19001" > .env.local
    echo "MASTER_KEY=DECO-231908!@" >> .env.local
fi

echo "🔥 Starting Next.js Dev Server on port $PORT..."
# Run in background or foreground? The user might want to see output.
# But for automation, maybe background.
# The prompt says "Lanzar dev server".
# We'll run it with nohup so it stays alive if the shell closes, but user can kill it.

nohup npm run dev -- -p $PORT > dashboard.log 2>&1 &
PID=$!

echo "✅ Dashboard started with PID $PID"
echo "🌐 Access at: http://127.0.0.1:$PORT"
echo "📜 Logs: $DASHBOARD_DIR/dashboard.log"
