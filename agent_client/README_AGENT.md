# 🕵️ Deco-Security Agent (v1.0.0)

El Agente Oficial de Deco-Security Global Grid. Diseñado para ser silencioso, seguro y auto-actualizable.

## 📁 Estructura

```
agent_client/
├── agent_main.py       # Punto de entrada y lógica del servicio
├── config.py           # Configuración y rutas
├── updater.py          # Sistema de auto-actualización
├── modules/            # Módulos de funcionalidad (Heartbeat, Discovery, Ports)
├── installer/
│   ├── windows/        # Scripts para generar instalador .exe
│   └── linux/          # Scripts install.sh / uninstall.sh
└── bin/                # Binarios externos (nmap)
```

## 🪟 Windows (Generación del .exe)

### Requisitos
- Python 3.11
- PyInstaller (`pip install pyinstaller`)
- Inno Setup (para crear el instalador final)

### 1. Compilar el Agente
Ejecuta el siguiente comando en la carpeta `agent_client`:

```bash
pyinstaller --onefile --noconsole --name "DecoSecurityAgent" --icon=installer/windows/deco_agent.ico agent_main.py
```

Esto generará `dist/DecoSecurityAgent.exe`.

### 2. Crear el Instalador
1. Abre `installer/windows/deco_installer.iss` con Inno Setup Compiler.
2. Compila el script.
3. Obtendrás `Output/DecoAgentInstaller.exe`.

### 3. Instalación Silenciosa
El instalador soporta instalación desatendida y paso de API Key:

```cmd
DecoAgentInstaller.exe /VERYSILENT /SUPPRESSMSGBOXES /APIKEY="tu_api_key_cliente"
```

Esto instalará el agente en `%ProgramFiles%\DecoSecurity`, registrará el servicio `DecoSecurityAgent` y lo iniciará automáticamente.

## 🐧 Linux (Instalación)

### Requisitos
- Python 3
- Systemd (Ubuntu, Debian, CentOS, etc.)
- Permisos de root

### Instalación
```bash
cd installer/linux
sudo chmod +x install.sh
sudo ./install.sh "tu_api_key_cliente"
```

Esto:
1. Copiará los archivos a `/opt/deco-agent`.
2. Instalará dependencias.
3. Creará y activará el servicio `/etc/systemd/system/deco-agent.service`.

### Desinstalación
```bash
cd installer/linux
sudo ./uninstall.sh
```

## ⚙️ Configuración

La configuración se almacena de forma segura en:
- **Windows:** `%PROGRAMDATA%\DecoSecurity\config.json`
- **Linux:** `/etc/deco-security/agent_config.json` (o `~/.deco-security/` si no es root)

## 🔄 Auto-Actualización

El agente consulta periódicamente `/api/agents/version`. Si detecta una nueva versión:
1. Descarga el paquete.
2. Verifica la integridad.
3. Reemplaza el binario.
4. Reinicia el servicio.

## 🛠️ Desarrollo y Pruebas

Para probar el agente localmente sin instalar el servicio:

```bash
./test_agent_local.sh
```
