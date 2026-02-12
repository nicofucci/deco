# Deco-Security Agent – Guía de Build/Prueba en Windows

## Requisitos
- Windows 10/11 x64.
- Python 3.11 x64 instalado (en PATH).
- PowerShell (ejecución de scripts permitida: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` si es necesario).

## Pasos de compilación
1. Copia la carpeta completa `agent_client` a tu PC Windows (por ejemplo `C:\deco-agent`).
2. Abre PowerShell en esa carpeta.
3. Ejecuta:
   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned   # (si el sistema lo requiere)
   .\build_windows.ps1
   ```
4. El ejecutable final queda en `.\dist_release\DecoSecurityAgent.exe`.  
   El log de compilación se guarda en `build_windows.log`.

> Alternativa CMD: ejecuta `build_windows.bat` (hace lo mismo que el script de PowerShell).

## Cómo probar el agente compilado
1. Crea/edita el config en `C:\ProgramData\DecoSecurity\config.json` con la API key de cliente y, opcionalmente, la URL:
   ```json
   {
     "client_api_key": "TU_API_KEY",
     "orchestrator_url": "https://api.deco-security.com"
   }
   ```
2. Ejecuta un ciclo de prueba en consola:
   ```powershell
   .\dist_release\DecoSecurityAgent.exe --once --config C:\ProgramData\DecoSecurity\config.json
   ```
   Esto hace un heartbeat + lectura/ejecución de jobs y sale.
3. Revisa logs:
   - Normal: `C:\ProgramData\DecoSecurity\logs\agent.log`
   - Fatales (traceback si algo peta): `C:\ProgramData\DecoSecurity\logs\agent_fatal.log`

## Despliegue/servicio
- Si ya tenías el servicio “DecoSecurityAgent”, basta con reemplazar el `.exe` en la carpeta de instalación y reiniciar el servicio.
- Si lo usas como tarea programada/servicio propio, apunta al nuevo `DecoSecurityAgent.exe`.

## Notas
- El agente soporta:
  - `--once`: un ciclo y termina (útil para pruebas).
  - `--config <ruta>`: usar un config distinto al predeterminado.
  - Registro rápido: `--api-key <key> --url <orchestrator>` para guardar la config y salir.
- Si ocurre un error no controlado, se escribe el traceback en `agent_fatal.log` en lugar de mostrar únicamente “Failed to execute script”.
