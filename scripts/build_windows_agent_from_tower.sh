#!/usr/bin/env bash
set -euo pipefail

LOG_PREFIX="[build-win-installer]"
say() { echo "${LOG_PREFIX} $*" >&2; }
fail() { echo "${LOG_PREFIX} ERROR: $*" >&2; exit 1; }

# Configuration
WINEPREFIX="${HOME}/.wine-deco-agent"
WINEARCH=win64
export WINEPREFIX WINEARCH

ROOT="/opt/deco"
INSTALLER_DIR="${ROOT}/agent_windows/installer"
# Output path for Onefile build is directly under dist/
DIST_EXE="${INSTALLER_DIR}/dist/agent_installer.exe"

command -v file >/dev/null || fail "'file' command required"
command -v wine >/dev/null || fail "'wine' command required"

verify_wine_python() {
  say "Verifying Python in Wine..."
  if ! wine python --version >/dev/null 2>&1; then
    fail "Python not found in ${WINEPREFIX}. Please run Step 2 of the setup."
  fi
}

build_installer() {
  say "Building agent_installer.exe with PyInstaller (Onefile)..."
  cd "${INSTALLER_DIR}"
  
  # Clean previous builds
  rm -rf build dist
  
  # Run PyInstaller via Wine
  # Note: running python module pyinstaller explicitly
  wine python -m PyInstaller --clean --noconfirm agent_installer.spec
}

verify_output() {
  if [[ ! -f "${DIST_EXE}" ]]; then
    fail "agent_installer.exe not found at ${DIST_EXE}"
  fi
  
  say "Output file: ${DIST_EXE}"
  
  # Check file size (approx > 5MB)
  local size
  size=$(stat -c%s "${DIST_EXE}")
  say "Size: $((size/1024/1024)) MB ($size bytes)"
  
  if [[ "$size" -lt 5242880 ]]; then # 5MB
    fail "Executable is suspiciously small (<5MB). Build might have failed or is incomplete."
  fi
  
  file "${DIST_EXE}" | sed "s/^/${LOG_PREFIX} /"
  
  say "Build verified successfully."
}

test_run() {
  say "Testing execution (expecting Code 3 or Interactive Prompt if visible)..."
  # Use timeout to prevent hanging if it prompts and we can't see it (though we expect code fix to block)
  # But since this is automated, we want to know if it runs.
  # We will just run it and expect it to NOT crash immediately with python errors.
  # Code 0 = Success (unlikely without input), Code 3 = Missing Key (if prompt fails), Code 1 = Error
  
  set +e
  output=$(timeout 5s wine "${DIST_EXE}" 2>&1)
  ret=$?
  set -e
  
  say "Exit Code: $ret"
  # say "Output: $output"
  
  # If we see "ImportError" or similar, it failed.
  if echo "$output" | grep -i "ImportError"; then
    fail "Python Import Error detected in output."
  fi
  if echo "$output" | grep -i "ModuleNotFoundError"; then
    fail "Module Not Found detected in output."
  fi
}

main() {
  verify_wine_python
  build_installer
  verify_output
  # test_run # Optional: enable if we want to auto-verify execution behavior
  say "DONE. Artifact available at: ${DIST_EXE}"
}

main "$@"

