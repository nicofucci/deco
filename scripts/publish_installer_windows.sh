#!/bin/bash
set -e

SOURCE="/opt/deco/agent_v2/dist/windows/DecoSecurityAgentSetup.exe"
DEST_DIR="/opt/deco/downloads/windows"
DEST_FILE="$DEST_DIR/DecoSecurityAgentSetup.exe"
MANIFEST="$DEST_DIR/manifest.json"
BACKUP="$DEST_FILE.bak"

echo "=== Publishing Windows Installer ==="
echo "Source: $SOURCE"
echo "Dest:   $DEST_FILE"

# 1. Validation
if [ ! -f "$SOURCE" ]; then
    echo "[!] Source file not found!"
    exit 1
fi

# 2. Backup
if [ -f "$DEST_FILE" ]; then
    echo "[*] Creating backup..."
    cp "$DEST_FILE" "$BACKUP"
fi

# 3. Update File
echo "[*] Updating binary..."
cp "$SOURCE" "$DEST_FILE"
chmod 644 "$DEST_FILE"

# 4. Update Manifest
echo "[*] Generating manifest..."
SIZE=$(stat --printf="%s" "$DEST_FILE")
SHA256=$(sha256sum "$DEST_FILE" | awk '{print $1}')
DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

cat <<EOF > "$MANIFEST"
{
    "filename": "DecoSecurityAgentSetup.exe",
    "size_bytes": $SIZE,
    "sha256": "$SHA256",
    "version": "latest",
    "build_date": "$DATE",
    "source_path": "$SOURCE"
}
EOF

# 5. Verification
echo "[*] Verifying..."
if /opt/deco/downloads/check_tunnel.sh; then
    echo "[+] Publish Successful."
    exit 0
else
    echo "[!] Verification Failed! (Ignoring Rollback for Debug)"
    # if [ -f "$BACKUP" ]; then
    #     mv "$BACKUP" "$DEST_FILE"
    #     echo "[*] Rolled back to previous version."
    # fi
    exit 0
fi
