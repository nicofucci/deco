#!/bin/bash
# demo_smoke.sh
# Final smoke test for Deco-Security Grid

LOG_FILE="/opt/deco/SEGUIMIENTO_PROYECTO/SMOKE_2025-12-17.txt"

echo "==================================================" | tee $LOG_FILE
echo "   DECO SECURITY - FINAL SMOKE TEST OF SYSTEMS    " | tee -a $LOG_FILE
echo "==================================================" | tee -a $LOG_FILE
echo "Timestamp: $(date)" | tee -a $LOG_FILE

# 0. Public API Health
echo -e "\n[0] Checking Public API (https://api.deco-security.com)..." | tee -a $LOG_FILE
PUBLIC_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://api.deco-security.com/health)
if [ "$PUBLIC_CODE" == "200" ]; then
    echo "SUCCESS: Public API is UP (HTTP 200)" | tee -a $LOG_FILE
else
    echo "FAILURE: Public API is DOWN (HTTP $PUBLIC_CODE)" | tee -a $LOG_FILE
fi

echo -e "\n[1] Checking Orchestrator Health (Port 8001)..." | tee -a $LOG_FILE
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/health)
if [ "$HTTP_CODE" == "200" ]; then
    echo "SUCCESS: Orchestrator is UP (HTTP 200)" | tee -a $LOG_FILE
    curl -s http://127.0.0.1:8001/health | tee -a $LOG_FILE
else
    echo "FAILURE: Orchestrator is DOWN (HTTP $HTTP_CODE)" | tee -a $LOG_FILE
fi

# 2. Database Tables
echo -e "\n[2] Checking Database Tables..." | tee -a $LOG_FILE
TABLE_COUNT=$(docker exec deco-sec-db psql -U postgres -d deco_security -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';" | xargs)
echo "Tables found: $TABLE_COUNT" | tee -a $LOG_FILE
if [ "$TABLE_COUNT" -gt 20 ]; then
     echo "SUCCESS: Database populated (>20 tables)" | tee -a $LOG_FILE
else
     echo "FAILURE: Database looks empty ($TABLE_COUNT tables)" | tee -a $LOG_FILE
fi

# 3. Master Console
echo -e "\n[3] Checking Master Console (Port 3006)..." | tee -a $LOG_FILE
CONSOLE_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3006)
if [ "$CONSOLE_CODE" == "200" ] || [ "$CONSOLE_CODE" == "307" ]; then 
    echo "SUCCESS: Master Console is Accessible (HTTP $CONSOLE_CODE)" | tee -a $LOG_FILE
else
    echo "FAILURE: Master Console is DOWN (HTTP $CONSOLE_CODE)" | tee -a $LOG_FILE
fi

# 4. Windows Agent Installer
echo -e "\n[4] verifying Final Windows Installer..." | tee -a $LOG_FILE
INSTALLER="/opt/deco/agent_win_builder/dist/DecoSecurityAgent-Setup-FINAL.exe"
if [ -f "$INSTALLER" ]; then
    echo "SUCCESS: Installer exists at $INSTALLER" | tee -a $LOG_FILE
    ls -lh "$INSTALLER" | tee -a $LOG_FILE
    sha256sum "$INSTALLER" | tee -a $LOG_FILE
else
    echo "FAILURE: Installer NOT FOUND!" | tee -a $LOG_FILE
fi

echo -e "\n==================================================" | tee -a $LOG_FILE
echo "               SMOKE TEST COMPLETE                " | tee -a $LOG_FILE
echo "==================================================" | tee -a $LOG_FILE
