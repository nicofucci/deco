@echo off
setlocal enabledelayedexpansion
set LOGFILE=build_windows.log

echo === DecoSecurityAgent - Build Windows === > %LOGFILE%

REM 1) venv
if not exist venv (
    echo Creando entorno virtual... >> %LOGFILE%
    python -m venv venv >> %LOGFILE% 2>&1
)

REM 2) Dependencias
echo Instalando dependencias... >> %LOGFILE%
call venv\Scripts\python -m pip install --upgrade pip wheel setuptools >> %LOGFILE% 2>&1
call venv\Scripts\python -m pip install -r requirements.txt pyinstaller >> %LOGFILE% 2>&1

REM 3) PyInstaller
if not exist dist_release mkdir dist_release
if not exist build_win mkdir build_win

echo Ejecutando PyInstaller... >> %LOGFILE%
call venv\Scripts\pyinstaller --onefile --noconsole --name DecoSecurityAgent --workpath build_win --distpath dist_release agent_main.py >> %LOGFILE% 2>&1

echo Build finalizado. Ejecutable en dist_release\DecoSecurityAgent.exe >> %LOGFILE%
endlocal
echo Build completado. Revisa %LOGFILE% para detalles.
