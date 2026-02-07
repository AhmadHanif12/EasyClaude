# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for EasyClaude
Build with: pyinstaller build/build.spec
"""

import os
import sys

block_cipher = None

# Get the project root directory (parent of build/ directory)
project_root = os.path.dirname(SPECPATH)

# Collect all app modules
app_dir = os.path.join(project_root, 'app')
assets_dir = os.path.join(project_root, 'assets')

a = Analysis(
    [os.path.join(app_dir, 'main.py')],
    pathex=[project_root],
    binaries=[],
    datas=[
        (assets_dir, 'assets'),  # Include assets folder
    ],
    hiddenimports=[
        'pystray',
        'pynput',
        'pynput.keyboard',
        'pydantic',
        'tkinter',
        'PIL',
        'win32com',
        'win32com.shell',
        'app.single_instance',
    ],
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
    name='EasyClaude',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(assets_dir, 'icon.ico') if os.path.exists(os.path.join(assets_dir, 'icon.ico')) else None,
)
