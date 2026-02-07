"""
EasyClaude - Claude Code Launcher

A Windows-first, cross-platform Python system tray application
for launching Claude Code via GUI + global hotkey.
"""

__version__ = "0.1.0"
__author__ = "EasyClaude Team"
__description__ = "Claude Code Launcher with global hotkey"

from app.config import Config, get_config, save_config
from app.launcher import ClaudeLauncher
from app.hotkey import HotkeyManager
from app.tray import TrayManager
from app.gui import LauncherGUI

__all__ = [
    "Config",
    "get_config",
    "save_config",
    "ClaudeLauncher",
    "HotkeyManager",
    "TrayManager",
    "LauncherGUI",
    "__version__",
]
