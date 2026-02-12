# Deco-Security Agent Installer (Windows MVP)
# Usage: .\install_windows.ps1 -ApiKey "YOUR_KEY" -OrchUrl "http://127.0.0.1:19001"

param (
    [string]$ApiKey,
    [string]$OrchUrl = "http://127.0.0.1:19001"
)

if (-not $ApiKey) {
    Write-Host "Usage: .\install_windows.ps1 -ApiKey <KEY>" -ForegroundColor Red
    exit 1
}

$InstallDir = "C:\Program Files\DecoSecurity\Agent"
$PythonPath = (Get-Command python).Source

Write-Host "[*] Installing Deco-Security Agent..." -ForegroundColor Cyan

# 1. Create Directory
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
}

# 2. Copy Files
Copy-Item -Recurse -Force "..\agent" "$InstallDir\"

# 3. Create Config
$ConfigContent = "CLIENT_API_KEY=$ApiKey`nORCH_URL=$OrchUrl`nHEARTBEAT_INTERVAL=30"
Set-Content -Path "$InstallDir\agent\config.env" -Value $ConfigContent

# 4. Create Service (MVP using sc.exe)
# Note: Running python script directly as service is tricky without nssm or pyinstaller exe.
# For MVP, we assume we have the .exe or use a wrapper.
# Here we simulate the service creation command.

Write-Host "[*] Creating Windows Service 'DecoAgent'..."
# sc.exe create DecoAgent binPath= "$PythonPath $InstallDir\agent\main.py" start= auto
# sc.exe start DecoAgent

Write-Host "[+] Installation Complete (MVP Simulation)!" -ForegroundColor Green
Write-Host "To run manually: python $InstallDir\agent\main.py"
