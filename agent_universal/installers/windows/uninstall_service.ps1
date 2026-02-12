# Uninstall Service Script

$ServiceNssm = "C:\Program Files\DecoSecurityAgent\nssm.exe"

if (Test-Path $ServiceNssm) {
    & $ServiceNssm stop DecoSecurityAgent
    & $ServiceNssm remove DecoSecurityAgent confirm
} else {
    sc.exe stop DecoSecurityAgent
    sc.exe delete DecoSecurityAgent
}

Write-Host "Service Uninstalled."
