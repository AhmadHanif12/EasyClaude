"""
Claude launcher module.

Wraps the platform-specific terminal launcher for EasyClaude.
"""

from typing import Optional
import logging
from pathlib import Path
from app.platform import get_platform_launcher, LaunchFailedError, TerminalNotFoundError
from app.config import add_directory_to_history

logger = logging.getLogger(__name__)


class ClaudeLauncher:
    """
    High-level interface for launching Claude Code.

    Uses the platform-specific launcher to open terminals with Claude.
    """

    def __init__(self):
        """Initialize the launcher with platform-specific implementation."""
        self._platform_launcher = get_platform_launcher()

    def launch(
        self,
        directory: str,
        command: str = "claude",
    ) -> bool:
        """
        Launch Claude in a new terminal window using PowerShell.

        Args:
            directory: Working directory for Claude
            command: Command to execute (default: "claude")

        Returns:
            bool: True if launch was successful, False otherwise
        """
        if not directory:
            logger.error("No directory specified")
            return False

        # Validate directory exists before launching
        dir_path = Path(directory)
        if not dir_path.exists():
            logger.error(f"Directory does not exist: {directory}")
            return False

        if not dir_path.is_dir():
            logger.error(f"Path is not a directory: {directory}")
            return False

        try:
            self._platform_launcher.launch_claude(
                directory=directory,
                command=command
            )

            # Add to history after successful launch
            # Thread-safe: add_directory_to_history handles its own locking
            add_directory_to_history(directory)

            return True
        except (TerminalNotFoundError, LaunchFailedError) as e:
            logger.error(f"Failed to launch Claude: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error launching Claude: {e}")
            return False

    def is_available(self) -> bool:
        """
        Check if the platform launcher is available.

        Returns:
            bool: True if available
        """
        return self._platform_launcher.is_available()


__all__ = [
    "ClaudeLauncher",
]
