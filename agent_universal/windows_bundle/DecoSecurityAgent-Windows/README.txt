Deco Security Agent - Windows Build Instructions
================================================

Este paquete contiene el código fuente actualizado del Agente Universal para ser compilado en Windows.

Instrucciones:
1. Descomprimir esta carpeta en C:\deco-agent\DecoSecurityAgent-Windows
2. Abrir PowerShell como Administrador.
3. Navegar a la carpeta:
   cd C:\deco-agent\DecoSecurityAgent-Windows\installers\windows
4. Ejecutar el script de construcción:
   .\build_windows.ps1

El ejecutable final se generará en:
C:\deco-agent\DecoSecurityAgent-Windows\installers\windows\dist\DecoSecurityAgent.exe

Notas:
- Asegúrese de tener Python instalado y en el PATH.
- El script instalará las dependencias necesarias (psutil, requests, pyinstaller, etc.).
- Si hay errores de permisos, ejecute PowerShell como Administrador.
