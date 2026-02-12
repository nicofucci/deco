# Install Service Script (NSSM Strategy)
# Requires nssm.exe in the same directory or in PATH.

$WorkDir = "C:\Program Files\DecoSecurityAgent"
$ExePath = "$WorkDir\DecoSecurityAgent.exe"
$NssmPath = "$PSScriptRoot\nssm.exe"

# 1. Check Admin
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "You must run this script as Administrator!"
    exit
}

# 2. Create Directory
New-Item -ItemType Directory -Force -Path $WorkDir | Out-Null

# 3. Copy Files
Copy-Item "$PSScriptRoot\DecoSecurityAgent.exe" -Destination $ExePath -Force

# 4. Install Service using NSSM
# We assume nssm.exe is provided in the zip or downloaded.
if (Test-Path $NssmPath) {
    Copy-Item $NssmPath -Destination "$WorkDir\nssm.exe" -Force
    $ServiceNssm = "$WorkDir\nssm.exe"
    
    & $ServiceNssm stop DecoSecurityAgent
    & $ServiceNssm remove DecoSecurityAgent confirm
    & $ServiceNssm install DecoSecurityAgent "$ExePath"
    & $ServiceNssm set DecoSecurityAgent AppDirectory "$WorkDir"
    & $ServiceNssm set DecoSecurityAgent DisplayName "Deco Security Agent"
    & $ServiceNssm set DecoSecurityAgent Description "Deco-Security Universal Agent Service"
    & $ServiceNssm set DecoSecurityAgent Start SERVICE_AUTO_START
    
    # Redirect I/O to logs
    New-Item -ItemType Directory -Force -Path "C:\ProgramData\DecoSecurityAgent\logs" | Out-Null
    & $ServiceNssm set DecoSecurityAgent AppStdout "C:\ProgramData\DecoSecurityAgent\logs\service.log"
    & $ServiceNssm set DecoSecurityAgent AppStderr "C:\ProgramData\DecoSecurityAgent\logs\service.log"

    & $ServiceNssm start DecoSecurityAgent
    Write-Host "Service Installed and Started via NSSM."
} else {
    Write-Warning "nssm.exe not found. Please download NSSM and place it next to this script."
    Write-Host "Alternative: Using sc.exe (Less robust for Python scripts but works for compiled exe)"
    sc.exe create DecoSecurityAgent binPath= "$ExePath" start= auto DisplayName= "Deco Security Agent"
    sc.exe description DecoSecurityAgent "Deco-Security Universal Agent Service"
    sc.exe start DecoSecurityAgent
}
