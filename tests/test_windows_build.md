# Validación de Build Windows

## Pasos de Verificación

1. **Descarga**:
   - Acceder a `https://download.deco-security.com`.
   - Descargar `DecoSecurityAgent-Windows.zip`.
   - Verificar SHA256 con `Get-FileHash`.

2. **Instalación**:
   - Descomprimir ZIP.
   - Ejecutar PowerShell como Administrador.
   - Correr `.\install_service.ps1`.
   - Verificar salida: "Service Installed and Started".

3. **Verificación de Servicio**:
   ```powershell
   Get-Service DecoSecurityAgent
   # Status debe ser Running
   ```

4. **Verificación de Procesos**:
   ```powershell
   Get-Process DecoSecurityAgent
   ```

5. **Verificación de Logs**:
   - Revisar `C:\ProgramData\DecoSecurityAgent\logs\agent.log`.
   - Buscar "Heartbeat sent".

6. **Verificación en Orchestrator**:
   - Ir a la Consola de Cliente.
   - Verificar que el agente aparece "Online".
   - Verificar que `primary_cidr` está poblado.
