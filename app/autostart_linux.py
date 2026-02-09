"""Linux autostart setup for EasyClaude.

Creates/Removes autostart desktop entry in ~/.config/autostart/.
"""

import logging
import shutil
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Autostart directory following XDG Base Directory Specification
AUTOSTART_DIR = Path.home() / ".config" / "autostart"

# Desktop entry filenames
AUTOSTART_FILENAME = "easyclaude-autostart.desktop"


def get_autostart_path() -> Path:
    """
    Get the path for the EasyClaude autostart desktop entry.

    Returns:
        Path: Autostart desktop entry path
    """
    return AUTOSTART_DIR / AUTOSTART_FILENAME


def get_source_desktop_file() -> Optional[Path]:
    """
    Get the path to the source desktop entry file in assets.

    Returns:
        Optional[Path]: Path to the source desktop file if found, None otherwise
    """
    # Try to find the desktop file relative to the module location
    module_dir = Path(__file__).parent.parent
    desktop_file = module_dir / "assets" / AUTOSTART_FILENAME

    if desktop_file.exists():
        return desktop_file

    # Fallback for development/frozen environments
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        bundle_dir = Path(sys.executable).parent
        desktop_file = bundle_dir / "share" / "applications" / AUTOSTART_FILENAME
        if desktop_file.exists():
            return desktop_file

    logger.warning(f"Could not find source desktop file: {AUTOSTART_FILENAME}")
    return None


def _create_autostart_desktop_entry() -> str:
    """
    Create the content for the autostart desktop entry.

    Returns:
        str: The desktop entry content
    """
    return """[Desktop Entry]
Version=1.0
Type=Application
Name=EasyClaude
Comment=Launch Claude Code from any directory
Exec=easyclaude --hidden
Icon=easyclaude
Terminal=false
Categories=Development;Utility;
Keywords=Claude;AI;Terminal;
X-GNOME-Autostart-enabled=true
X-KDE-autostart-after=panel
"""


def enable_autostart() -> bool:
    """
    Create a desktop entry in the XDG autostart directory.

    Creates ~/.config/autostart/easyclaude-autostart.desktop to enable
    automatic startup when the user logs in.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        autostart_path = get_autostart_path()

        # Ensure autostart directory exists
        AUTOSTART_DIR.mkdir(parents=True, exist_ok=True)

        # Try to copy from source desktop file
        source_file = get_source_desktop_file()
        if source_file:
            shutil.copy2(source_file, autostart_path)
            logger.info(f"Autostart desktop entry created from source: {autostart_path}")
        else:
            # Create the desktop entry content directly
            content = _create_autostart_desktop_entry()
            autostart_path.write_text(content)
            logger.info(f"Autostart desktop entry created: {autostart_path}")

        # Make the file executable (required for desktop entries)
        autostart_path.chmod(0o755)

        return True

    except PermissionError as e:
        logger.error(f"Permission denied creating autostart entry: {e}")
        return False
    except OSError as e:
        logger.error(f"Error creating autostart entry: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error enabling autostart: {e}")
        return False


def disable_autostart() -> bool:
    """
    Remove the desktop entry from the XDG autostart directory.

    Returns:
        bool: True if successful or doesn't exist, False on error
    """
    try:
        autostart_path = get_autostart_path()

        if autostart_path.exists():
            autostart_path.unlink()
            logger.info(f"Autostart desktop entry removed: {autostart_path}")
        else:
            logger.info("No autostart desktop entry found.")

        return True

    except PermissionError as e:
        logger.error(f"Permission denied removing autostart entry: {e}")
        return False
    except OSError as e:
        logger.error(f"Error removing autostart entry: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error disabling autostart: {e}")
        return False


def is_autostart_enabled() -> bool:
    """
    Check if EasyClaude is set to autostart.

    Returns:
        bool: True if autostart is enabled
    """
    return get_autostart_path().exists()


def main():
    """Command-line interface for autostart management."""
    if len(sys.argv) < 2:
        print("Usage: python autostart_linux.py <enable|disable|status>")
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
            print(f"Entry location: {get_autostart_path()}")
        else:
            print("Autostart is DISABLED")

    else:
        print(f"Unknown command: {command}")
        print("Available commands: enable, disable, status")
        sys.exit(1)


__all__ = [
    "enable_autostart",
    "disable_autostart",
    "is_autostart_enabled",
    "get_autostart_path",
]
