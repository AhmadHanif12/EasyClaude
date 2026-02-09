# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for EasyClaude on Linux.
A system tray launcher for Claude Code.
"""

import os
import sys

block_cipher = None

# Get the base directory
base_dir = os.path.dirname(os.path.abspath(SPEC))


def _existing(entry):
    """Return tuple entry only if its source path exists."""
    src, dst = entry
    return entry if src and os.path.exists(src) else None


# Linux-specific binaries and data files
extra_binaries = []

extra_datas = [
    _existing((os.path.join(base_dir, 'assets', 'icon.png'), 'assets')),
    _existing((os.path.join(base_dir, 'assets', 'easyclaude.desktop'), 'assets')),
    _existing((os.path.join(base_dir, 'assets', 'easyclaude-autostart.desktop'), 'assets')),
]
extra_datas = [x for x in extra_datas if x is not None]

a = Analysis(
    [os.path.join(base_dir, 'app', 'main.py')],
    pathex=[base_dir],
    binaries=extra_binaries,
    datas=extra_datas,
    hiddenimports=[
        # pystray dependencies (Linux)
        'pystray._util.gtk',
        'pystray._util.gtk_dbus',
        # pynput dependencies (Linux)
        'pynput.keyboard._xorg',
        'pynput.mouse._xorg',
        # pydantic
        'pydantic',
        'pydantic.deprecated',
        'pydantic.deprecated.decorator',
        # cairo/glib (for Linux tray support)
        'cairo',
        'gi',
        'gi.repository',
        'gi.repository.Gtk',
        'gi.repository.Gdk',
        'gi.repository.Gio',
        # tkinter (for GUI)
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        # App modules
        'app.platform.linux',
        'app.platform.windows',
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
        # Exclude Windows-specific packages
        'win32api',
        'win32con',
        'win32gui',
        'win32process',
        'pywin32',
        'pystray._win32',
        'pynput.keyboard._win32',
        'pynput.mouse._win32',
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
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window - this is a GUI/tray app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(base_dir, 'assets', 'icon.png'),
    version=None,
)
