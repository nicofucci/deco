# -*- mode: python -*-
import os
from pathlib import Path

block_cipher = None

base_dir = Path(os.getcwd())
project_root = (base_dir / ".." / "..").resolve()

a = Analysis(
    ['installer_main.py'],
    pathex=[str(base_dir)],
    binaries=[],
    datas=[
        (str(project_root / 'agent_universal'), 'agent_universal'),
        (str(project_root / 'agent_windows' / 'src'), 'agent_windows_src'),
    ],
    hiddenimports=['win32timezone', 'win32service', 'win32event', 'servicemanager'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='agent_installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

