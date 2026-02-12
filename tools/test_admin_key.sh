#!/bin/bash

# Load Master Key from .env
source /opt/deco/tower/.env.deco_security

MASTER_KEY=$DECO_ADMIN_MASTER_KEY
API_URL="http://127.0.0.1:19001"

echo "Testing Admin Access with Key: $MASTER_KEY"
echo "Endpoint: $API_URL/api/admin/overview"

curl -i -X GET "$API_URL/api/admin/overview" \
  -H "X-Admin-Master-Key: $MASTER_KEY"

echo -e "\n"
