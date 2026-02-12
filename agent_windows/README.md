# Deco-Security Windows Agent (v2.1.0)

Agente profesional de ciberseguridad para Windows, diseñado para ejecutarse como servicio, detectar amenazas y reportar a la Deco-Security Global Grid.

## 📋 Características

- **Servicio Windows Nativo**: Se ejecuta en background, auto-inicio.
- **Detección de Red**: Identifica IP real (ignora VPNs/VMs), escanea LAN y puertos locales.
- **Heartbeat Seguro**: Reporta estado cada 30s a `api.deco-security.com`.
- **Auto-Update**: Capacidad de actualizarse a sí mismo desde el Orchestrator.
- **Instalador Profesional**: Wizard gráfico para configuración inicial (URL + API Key).

## 🛠️ Requisitos de Compilación

Necesitas una máquina Windows con:
1. **Python 3.10+**
2. **Inno Setup 6+**

### Dependencias Python
```bash
pip install pyinstaller pywin32 requests psutil
```

## 🚀 Instrucciones de Compilación

1. **Clonar el repositorio** (o copiar la carpeta `agent_windows`).
2. **Generar el Ejecutable**:
   Abrir terminal en la carpeta del proyecto y ejecutar:
   ```bash
   pyinstaller DecoSecurityAgent.spec
   ```
   Esto generará `dist/DecoSecurityAgent.exe`.

3. **Crear el Instalador**:
   - Abrir `setup.iss` con Inno Setup Compiler.
   - Compilar el script.
   - El instalador final estará en la carpeta `Output` (ej. `DecoSecurityAgentInstaller.exe`).

## 📦 Instalación y Uso

1. Ejecutar `DecoSecurityAgentInstaller.exe` como Administrador.
2. Seguir el wizard:
   - Ingresar URL del Orchestrator (default: `https://api.deco-security.com`).
   - Ingresar **Client API Key**.
3. El servicio se iniciará automáticamente.

## 🔍 Logs y Debugging

Los logs se encuentran en:
`C:\ProgramData\DecoSecurity\logs\agent.log`

Para reiniciar el servicio manualmente:
```cmd
net stop DecoSecurityAgent
net start DecoSecurityAgent
```
