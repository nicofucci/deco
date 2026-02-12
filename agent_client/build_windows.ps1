$ErrorActionPreference = "Stop"

# Inicia transcript de build
$logFile = "build_windows.log"
if (Test-Path $logFile) { Remove-Item $logFile -Force }
Start-Transcript -Path $logFile -Append

try {
    Write-Host "=== DecoSecurityAgent - Build Windows ==="

    # 1) venv
    if (-not (Test-Path ".\venv")) {
        Write-Host "Creando entorno virtual..."
        python -m venv venv
    }

    # 2) Activar venv y actualizar herramientas
    Write-Host "Instalando dependencias..."
    .\venv\Scripts\python -m pip install --upgrade pip wheel setuptools
    .\venv\Scripts\python -m pip install -r requirements.txt pyinstaller

    # 3) Ejecutar PyInstaller
    Write-Host "Ejecutando PyInstaller..."
    $distDir = "dist_release"
    $workDir = "build_win"
    if (-not (Test-Path $distDir)) { New-Item -ItemType Directory -Path $distDir | Out-Null }
    if (-not (Test-Path $workDir)) { New-Item -ItemType Directory -Path $workDir | Out-Null }

    .\venv\Scripts\pyinstaller --onefile --noconsole --name DecoSecurityAgent `
        --workpath $workDir `
        --distpath $distDir `
        agent_main.py

    Write-Host "Build finalizado. Ejecutable en $distDir\DecoSecurityAgent.exe"
}
catch {
    Write-Host "Error durante el build: $($_.Exception.Message)" -ForegroundColor Red
    throw
}
finally {
    Stop-Transcript | Out-Null
}
