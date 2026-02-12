# Guía de Instalación para Windows

## Requisitos
- Python 3.9+ instalado (o usar versión empaquetada con PyInstaller).
- Permisos de Administrador.

## Pasos Manuales (Desarrollo)

1. **Copiar Archivos**:
   Copiar la carpeta `src` a `C:\Program Files\DecoSecurityAgent\src`.

2. **Configuración**:
   Crear carpeta `C:\ProgramData\DecoSecurityAgent`.
   (Opcional) Crear `config.json` con la API Key.

3. **Instalar Servicio (NSSM)**:
   Usar NSSM (Non-Sucking Service Manager) es la forma más robusta.
   
   ```powershell
   nssm.exe install DecoSecurityAgent "C:\Python39\python.exe" "C:\Program Files\DecoSecurityAgent\src\main.py"
   nssm.exe set DecoSecurityAgent AppDirectory "C:\Program Files\DecoSecurityAgent\src"
   nssm.exe set DecoSecurityAgent Description "Deco-Security Universal Agent"
   nssm.exe start DecoSecurityAgent
   ```

## Empaquetado (Producción)

Para crear un `DecoSecurityAgent-Setup-Windows.exe`:

1. Usar **PyInstaller** para generar un EXE único:
   ```bash
   pyinstaller --onefile --noconsole --name DecoSecurityAgent src/main.py
   ```
2. Usar **Inno Setup** para crear el instalador que:
   - Copie el EXE.
   - Ejecute el comando de registro de servicio (sc create o nssm).
   - Pida la API Key durante la instalación (Wizard) y la escriba en `%PROGRAMDATA%\DecoSecurityAgent\config.json`.
