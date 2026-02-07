# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for EasyClaude.
A Windows system tray launcher for Claude Code.
"""

import os
import sys

block_cipher = None

# Get the base directory
base_dir = os.path.dirname(os.path.abspath(SPEC))

# Resolve tkinter package and binary explicitly. This is needed when building
# from Microsoft Store Python, where PyInstaller may fail to auto-collect it.
try:
    import tkinter  # type: ignore
    import _tkinter  # type: ignore

    tkinter_pkg_dir = os.path.dirname(tkinter.__file__)
    tkinter_pyd = _tkinter.__file__
except Exception:
    tkinter_pkg_dir = None
    tkinter_pyd = None


def _existing(entry):
    """Return tuple entry only if its source path exists."""
    src, dst = entry
    return entry if src and os.path.exists(src) else None


extra_binaries = [
    _existing((os.path.join(base_dir, 'assets', 'tcl86t.dll'), '.')),
    _existing((os.path.join(base_dir, 'assets', 'tk86t.dll'), '.')),
    _existing((tkinter_pyd, '.')),
]
extra_binaries = [x for x in extra_binaries if x is not None]

extra_datas = [
    _existing((os.path.join(base_dir, 'assets', 'icon.ico'), 'assets')),
    _existing((tkinter_pkg_dir, 'tkinter')),
]
extra_datas = [x for x in extra_datas if x is not None]

a = Analysis(
    [os.path.join(base_dir, 'app', 'main.py')],
    pathex=[base_dir],
    binaries=extra_binaries,
    datas=extra_datas,
    hiddenimports=[
        # pystray dependencies
        'pystray._win32',
        'PIL._tkinter_finder',
        # pynput dependencies
        'pynput.keyboard._win32',
        'pynput.mouse._win32',
        # pydantic
        'pydantic',
        'pydantic.deprecated',
        'pydantic.deprecated.decorator',
        # pywin32
        'win32api',
        'win32con',
        'win32gui',
        'win32process',
        # tkinter (for GUI)
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        # App modules - explicit imports to avoid detection issues
        'app.platform.windows',
        'app.platform.linux',
        'app.platform.macos',
        'app.single_instance',
        # Standard library
        'json',
        'pathlib',
        'threading',
        'subprocess',
        'logging',
        'queue',
        'glob',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude testing and dev packages
        'pytest',
        'pytest_mock',
        'pytest_cov',
        '_pytest',
        'unittest',
        'doctest',
        'test',
        'tests',
        # Other unneeded packages
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'jupyter',
    ],
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
    upx=False,  # Disabled to avoid hanging during compression
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window - this is a GUI/tray app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(base_dir, 'assets', 'icon.ico'),
    version=None,
    uac_admin=False,
)
