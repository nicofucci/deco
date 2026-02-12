# Build Script for Windows
# Run this on a Windows machine with Python and PyInstaller installed.

$VERSION = "1.0.0"
$DIST_DIR = "dist"
$BUILD_DIR = "build"
$SRC_DIR = "../../src"

Write-Host "Building Deco-Security Agent v$VERSION for Windows..."

# 1. Clean
if (Test-Path $DIST_DIR) { Remove-Item -Recurse -Force $DIST_DIR }
if (Test-Path $BUILD_DIR) { Remove-Item -Recurse -Force $BUILD_DIR }

# 2. PyInstaller Build
# Assumes requirements are installed: pip install pyinstaller requests pywin32
pyinstaller --clean DecoSecurityAgent.spec

# 3. Create ZIP Package
$ZipPath = "DecoSecurityAgent-Windows.zip"
Write-Host "Creating ZIP package..."
Compress-Archive -Path "$DIST_DIR\DecoSecurityAgent.exe", "install_service.ps1", "uninstall_service.ps1" -DestinationPath $ZipPath -Force

Write-Host "Build Complete: $ZipPath"
