# Guía de Build para Windows (Deco-Security Agent)

## Requisitos
- Windows 10/11 o Server.
- Python 3.9+ instalado y en PATH.
- Git (opcional).
- PowerShell.

## Pasos para Generar el Ejecutable

1. **Preparar Entorno**:
   ```powershell
   # Instalar dependencias
   pip install pyinstaller requests pywin32
   ```

2. **Obtener Código**:
   - Copiar la carpeta `/opt/deco/agent_universal` a tu máquina Windows (ej: `C:\deco\agent_universal`).

3. **Ejecutar Build**:
   - Abrir PowerShell en `C:\deco\agent_universal\installers\windows`.
   - Ejecutar:
     ```powershell
     .\build_windows.ps1
     ```

4. **Resultado**:
   - Se generará `DecoSecurityAgent-Windows.zip` en la misma carpeta.
   - Este ZIP contiene:
     - `DecoSecurityAgent.exe`
     - `install_service.ps1`
     - `uninstall_service.ps1`

## Instalación en Cliente

1. Descomprimir el ZIP en el cliente.
2. (Opcional) Descargar `nssm.exe` y ponerlo en la misma carpeta para mayor robustez.
3. Ejecutar `install_service.ps1` como Administrador.
4. Editar `C:\ProgramData\DecoSecurityAgent\config.json` y poner la API Key.
5. Reiniciar el servicio: `Restart-Service DecoSecurityAgent`.
