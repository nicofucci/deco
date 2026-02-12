#!/bin/bash
set -e

# Deco-Security Cloudflare Tunnel Setup
# This script helps you expose the Orchestrator API securely.

CLOUDFLARED="/opt/deco/tools/cloudflared"
TUNNEL_NAME="deco-tunnel"
API_PORT=19001

echo "🌐 Deco-Security Cloudflare Tunnel Setup"
echo "========================================"

# 1. Login
echo "[*] Step 1: Authentication"
echo "    Please log in to Cloudflare in the browser window that opens (or copy the URL)."
$CLOUDFLARED tunnel login

# 2. Create Tunnel
echo -e "\n[*] Step 2: Creating Tunnel '$TUNNEL_NAME'..."
if $CLOUDFLARED tunnel list | grep -q "$TUNNEL_NAME"; then
    echo "    Tunnel already exists."
else
    $CLOUDFLARED tunnel create "$TUNNEL_NAME"
fi

# 3. Configure Ingress
echo -e "\n[*] Step 3: Configuring Ingress..."
echo "    We need to route traffic from a subdomain (e.g., api.deco-security.com) to http://localhost:$API_PORT"
read -p "    Enter the full hostname you want to use (e.g., api.deco-security.com): " HOSTNAME

if [ -z "$HOSTNAME" ]; then
    echo "    Error: Hostname cannot be empty."
    exit 1
fi

# Create config.yml
mkdir -p ~/.cloudflared
cat <<EOF > ~/.cloudflared/config.yml
tunnel: $TUNNEL_NAME
credentials-file: /home/$(whoami)/.cloudflared/$(ls ~/.cloudflared | grep .json | head -n 1)

ingress:
  - hostname: $HOSTNAME
    service: http://localhost:$API_PORT
  - service: http_status:404
EOF

# 4. Route DNS
echo -e "\n[*] Step 4: Routing DNS..."
$CLOUDFLARED tunnel route dns "$TUNNEL_NAME" "$HOSTNAME"

# 5. Run Tunnel
echo -e "\n[*] Step 5: Starting Tunnel..."
echo "    Tunnel is starting. You can now use https://$HOSTNAME in your Agent configuration."
echo "    Press Ctrl+C to stop."
$CLOUDFLARED tunnel run "$TUNNEL_NAME"
