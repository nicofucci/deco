#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "🚀 Starting Deco-Security Partner Console..."
npm install
npm run dev -- -p 3007
