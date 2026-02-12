#!/bin/bash
# build_windows_agent_inno_final.sh
# Automates the build and verification of the Deco Security Windows Agent (Inno Setup)

set -e

# --- Configuration ---
WINEPREFIX=~/.wine-deco-agent
SOURCE_DIR="/opt/deco/agent_windows"
BUILD_DIR="/opt/deco/agent_win_builder"
DIST_DIR="$BUILD_DIR/dist"
LOG_DIR="$BUILD_DIR/logs"
WINE_PYTHON="$WINEPREFIX/drive_c/Program Files/Python311/python.exe"
WINE_PIP="$WINEPREFIX/drive_c/Program Files/Python311/Scripts/pip.exe"
WINE_PYINSTALLER="$WINEPREFIX/drive_c/Program Files/Python311/Scripts/pyinstaller.exe"
INNO_COMPILER="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

mkdir -p "$DIST_DIR"
mkdir -p "$LOG_DIR"

echo "=================================================="
echo "   DECO SECURITY - WINDOWS AGENT BUILD (FINAL)    "
echo "=================================================="
echo "Start Time: $(date)"

# 1. Clean Build Environment
echo "[1/6] Cleaning build environment..."
rm -rf "$SOURCE_DIR/build" "$SOURCE_DIR/dist"
rm -rf "$BUILD_DIR/dist/*"

# 2. Prepare Source
echo "[2/6] Preparing source..."
if [ -f "$SOURCE_DIR/requirements.txt" ]; then
    echo "Installing/Verifying requirements..."
    wine "$WINE_PIP" install -r "$SOURCE_DIR/requirements.txt" > "$LOG_DIR/pip_install.log" 2>&1
else
    echo "requirements.txt not found. Skipping pip install (assuming env ready)..."
fi

# 3. Build Payload (PyInstaller)
echo "[3/6] Building Agent Payload (PyInstaller)..."
cd "$SOURCE_DIR"
wine "$WINE_PYTHON" -m PyInstaller --clean --noconfirm "$SOURCE_DIR/DecoSecurityAgent.spec"

if [ ! -f "$SOURCE_DIR/dist/DecoSecurityAgent.exe" ]; then
    echo "ERROR: PyInstaller failed. Check log: $LOG_DIR/pyinstaller_build.log"
    exit 1
fi

PAYLOAD_SIZE=$(ls -lh "$SOURCE_DIR/dist/DecoSecurityAgent.exe" | awk '{print $5}')
echo "Payload Built: $SOURCE_DIR/dist/DecoSecurityAgent.exe ($PAYLOAD_SIZE)"
echo "Payload SHA256: $(sha256sum "$SOURCE_DIR/dist/DecoSecurityAgent.exe" | awk '{print $1}')"

# 4. Build Installer (Inno Setup)
echo "[4/6] Building Installer (Inno Setup)..."
# Convert path to Windows format for Inno Setup
ISS_FILE_WIN=$(winepath -w "$SOURCE_DIR/setup.iss")
echo "Compiling: $ISS_FILE_WIN"

wine "$INNO_COMPILER" "$ISS_FILE_WIN"

# Move artifact to builder dist
# Inno Setup output defaults to "Output" dir relative to script if not specified absolute.
# setup.iss defines OutputBaseFilename, and default OutputDir is "Output" subfolder of script.
# So it should be in $SOURCE_DIR/Output/
mv "$SOURCE_DIR/Output/DecoSecurityAgentInstaller.exe" "$DIST_DIR/DecoSecurityAgent-Setup-FINAL.exe"

if [ ! -f "$DIST_DIR/DecoSecurityAgent-Setup-FINAL.exe" ]; then
    echo "ERROR: Inno Setup failed. Check log: $LOG_DIR/iscc_build.log"
    exit 1
fi

FINAL_SIZE=$(ls -lh "$DIST_DIR/DecoSecurityAgent-Setup-FINAL.exe" | awk '{print $5}')
echo "Installer Built: $DIST_DIR/DecoSecurityAgent-Setup-FINAL.exe ($FINAL_SIZE)"
echo "Installer SHA256: $(sha256sum "$DIST_DIR/DecoSecurityAgent-Setup-FINAL.exe" | awk '{print $1}')"

# 5. Verification (Wine Smoke Test)
echo "[5/6] Verifying Installer (Wine Smoke Test)..."
export WINEPREFIX=~/.wine-deco-agent

# Test A: Interactive/Visible (Simulated by not suppressing windows, but automated inputs?)
# Inno Setup supports command line parameters for automation even without silent
# But user wants "Interactive" test essentially to verify it runs.
# We will do a SILENT install for logic verification first.

TEST_LOG="C:\\windows\\temp\\deco_install.log"
wine "$DIST_DIR/DecoSecurityAgent-Setup-FINAL.exe" /VERYSILENT /SUPPRESSMSGBOXES /LOG="$TEST_LOG"
# Note: install might fail if service installation requires Real Admin or specific win args, 
# but we check if files are put in place.

echo "Waiting for installation..."
sleep 5

# Check Files
INSTALLED_EXE="$WINEPREFIX/drive_c/Program Files/Deco Security Agent/DecoSecurityAgent.exe"
CONFIG_FILE="$WINEPREFIX/drive_c/ProgramData/DecoSecurity/config.json"
INSTALL_LOG="$WINEPREFIX/drive_c/windows/temp/deco_install.log"

if [ -f "$INSTALLED_EXE" ]; then
    echo "SUCCESS: Executable installed at $INSTALLED_EXE"
else
    echo "FAILURE: Executable not found after install."
    echo "Install Log Tail:"
    tail -n 20 "$INSTALL_LOG"
    exit 1
fi

# 6. Runtime Verification (Imports)
echo "[6/6] Verifying Runtime (Import Check)..."
# We try to run the agent with --version or just run it and check for immediate crash
# Service executables often can't run directly in console mode easily if they expect Service Manager
# BUT our code has: if len(sys.argv) == 1: ... StartServiceCtrlDispatcher
# So running it without args might hang or fail.
# We can try to run it with a flag if we had one, or just check simple run.
# However, the user issue was "No module named utils" which happens AT IMPORT time, before service start.
# So just running it and seeing if it outputs specific error or gets to service start is enough.

# Run for 5 seconds then kill, capture output
timeout 5s wine "$INSTALLED_EXE" > "$LOG_DIR/runtime_test.log" 2>&1 || true

if grep -q "No module named" "$LOG_DIR/runtime_test.log"; then
    echo "CRITICAL FAILURE: 'No module named' found in runtime log!"
    cat "$LOG_DIR/runtime_test.log"
    exit 1
else
    echo "SUCCESS: No import errors detected in runtime."
fi

echo "=================================================="
echo "             BUILD COMPLETE - SUCCESS             "
echo "=================================================="
echo "Artifact: $DIST_DIR/DecoSecurityAgent-Setup-FINAL.exe"
sha256sum "$DIST_DIR/DecoSecurityAgent-Setup-FINAL.exe"
ls -lh "$DIST_DIR/DecoSecurityAgent-Setup-FINAL.exe"
