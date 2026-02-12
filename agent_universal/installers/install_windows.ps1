<# 
Deco-Security Agent Installer (Windows, PowerShell)
Idempotent: safe to re-run; preserves existing config at %ProgramData%\DecoSecurityAgent\config.json

Requirements:
- PowerShell 5+
- Python 3.x available in PATH (or adapt to bundled EXE if provided)
- Run as Administrator
#>

$ErrorActionPreference = "Stop"

function Write-Info($msg) { Write-Host "[Installer] $msg" }

if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltinRole] "Administrator")) {
    throw "Run this installer as Administrator."
}

$InstallDir = "C:\ProgramData\DecoSecurityAgent"
$ConfigFile = Join-Path $InstallDir "config.json"
$LogDir = Join-Path $InstallDir "logs"
$ServiceName = "DecoSecurityAgent"

$OrchUrl = $env:DECO_ORCHESTRATOR_URL
if (-not $OrchUrl) { $OrchUrl = "http://127.0.0.1:8001" }
$ApiKey = $env:X_CLIENT_API_KEY
$AgentMode = $env:AGENT_MODE
if (-not $AgentMode) { $AgentMode = "prod" }
$AgentVersion = $env:AGENT_VERSION
if (-not $AgentVersion) { $AgentVersion = "2.0.0-universal" }

Write-Info "Preparing directories..."
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

if (-not (Test-Path $ConfigFile)) {
    Write-Info "Creating config at $ConfigFile"
    @{
        orchestrator_url = $OrchUrl
        api_key          = $ApiKey
        agent_id         = $null
        agent_mode       = $AgentMode
        agent_version    = $AgentVersion
        last_sync        = $null
        last_error       = $null
    } | ConvertTo-Json | Set-Content -Path $ConfigFile -Encoding UTF8
} else {
    Write-Info "Config exists, keeping $ConfigFile"
}

$Python = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $Python) { $Python = Get-Command python -ErrorAction SilentlyContinue }
if (-not $Python) { throw "Python 3 is required in PATH." }

Write-Info "Registering Windows Service $ServiceName"
$Exec = "$($Python.Source) $PSScriptRoot\..\src\main.py"
sc.exe create $ServiceName binPath= "cmd /c $Exec" start= auto DisplayName= "Deco-Security Agent" | Out-Null
sc.exe failure $ServiceName reset= 30 actions= restart/5000 | Out-Null

Write-Info "Service registered. Start with: Start-Service $ServiceName"
