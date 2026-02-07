"""
Windows autostart setup for EasyClaude.

Creates/Removes startup shortcut in Windows Startup folder.
"""

import os
import sys
from pathlib import Path


def get_startup_folder() -> Path:
    """
    Get the Windows Startup folder path.

    Returns:
        Path: Startup folder path
    """
    # Get APPDATA environment variable
    appdata = os.environ.get('APPDATA', '')
    if not appdata:
        # Fallback to user home
        appdata = Path.home() / "AppData" / "Roaming"
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def get_exe_path() -> Path:
    """
    Get the path to the EasyClaude executable.

    Returns:
        Path: Path to EasyClaude.exe or main.py
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        return Path(sys.executable)
    else:
        # Running in development mode - use python with main.py
        return Path(sys.executable)


def get_shortcut_path() -> Path:
    """
    Get the path for the EasyClaude shortcut in Startup folder.

    Returns:
        Path: Shortcut path
    """
    startup_folder = get_startup_folder()
    return startup_folder / "EasyClaude.lnk"


def enable_autostart() -> bool:
    """
    Create a shortcut in the Windows Startup folder.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        import pythoncom
        from win32com.shell import shell, shellcon

        exe_path = get_exe_path()
        shortcut_path = get_shortcut_path()

        # Ensure startup folder exists
        shortcut_path.parent.mkdir(parents=True, exist_ok=True)

        # Create shortcut
        shortcut = pythoncom.CoCreateInstance(
            shell.CLSID_ShellLink,
            None,
            pythoncom.CLSCTX_INPROC_SERVER,
            shell.IID_IShellLink
        )

        shortcut.SetPath(str(exe_path))
        shortcut.SetDescription("Launch Claude Code from any directory")
        shortcut.SetIconLocation(str(exe_path), 0)

        # Save shortcut
        persist_file = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
        persist_file.Save(str(shortcut_path), 0)

        print(f"Autostart shortcut created: {shortcut_path}")
        return True

    except ImportError:
        print("Error: pywin32 not installed. Install with: pip install pywin32")
        return False
    except Exception as e:
        print(f"Error creating autostart shortcut: {e}")
        return False


def disable_autostart() -> bool:
    """
    Remove the shortcut from the Windows Startup folder.

    Returns:
        bool: True if successful or doesn't exist, False on error
    """
    try:
        shortcut_path = get_shortcut_path()

        if shortcut_path.exists():
            shortcut_path.unlink()
            print(f"Autostart shortcut removed: {shortcut_path}")
        else:
            print("No autostart shortcut found.")

        return True

    except Exception as e:
        print(f"Error removing autostart shortcut: {e}")
        return False


def is_autostart_enabled() -> bool:
    """
    Check if EasyClaude is set to autostart.

    Returns:
        bool: True if autostart is enabled
    """
    return get_shortcut_path().exists()


def main():
    """Command-line interface for autostart management."""
    if len(sys.argv) < 2:
        print("Usage: python autostart.py <enable|disable|status>")
        print(f"Current status: {'Enabled' if is_autostart_enabled() else 'Disabled'}")
        return

    command = sys.argv[1].lower()

    if command == "enable":
        if enable_autostart():
            print("Autostart enabled successfully.")
        else:
            print("Failed to enable autostart.")
            sys.exit(1)

    elif command == "disable":
        if disable_autostart():
            print("Autostart disabled successfully.")
        else:
            print("Failed to disable autostart.")
            sys.exit(1)

    elif command == "status":
        if is_autostart_enabled():
            print("Autostart is ENABLED")
        else:
            print("Autostart is DISABLED")

    else:
        print(f"Unknown command: {command}")
        print("Available commands: enable, disable, status")
        sys.exit(1)


if __name__ == "__main__":
    main()
