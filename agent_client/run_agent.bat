@echo off
echo Deco-Security Agent Launcher
echo ----------------------------

if exist config\config.json goto run
if exist config.json goto run

echo Configuration not found.
set /p APIKEY="Enter Client API Key: "
set /p URL="Enter Orchestrator URL (default: http://api.deco-security.com): "
if "%URL%"=="" set URL=http://api.deco-security.com

python agent_main.py --api-key %APIKEY% --url %URL%
echo Configuration saved. Starting agent...

:run
python agent_main.py
pause
