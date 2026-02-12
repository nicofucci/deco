# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# Collect all submodules for agent to ensure everything is included
agent_hidden_imports = collect_submodules('agent')
# Explicitly collect utils if it were a sub-package, but collect_submodules('agent') covers it.
# We add standard hidden imports explicitly requested.

hidden_imports = [
    'win32timezone',
    'win32service',
    'win32serviceutil',
    'win32event',
    'servicemanager',
    'pywintypes', # Important for win32
    'requests',
    'psutil',
    'ipaddress',
    'socket',
    'logging.handlers',
    'concurrent.futures'
] + agent_hidden_imports

a = Analysis(
    ['win_service.py'], # Changed to root entry point
    pathex=['.'], # Root dir is path
    binaries=[],
    datas=[('agent', 'agent')], # Include entire agent package as data/source
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
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
    name='DecoSecurityAgent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # Service = No Console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
    version='version_info.txt',
    icon=None
)
