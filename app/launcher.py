"""
Claude launcher module.

Wraps the platform-specific terminal launcher for EasyClaude.
"""

from typing import Optional
import logging
from app.platform import get_platform_launcher, LaunchFailedError, TerminalNotFoundError

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
        use_powershell: Optional[bool] = None,
    ) -> bool:
        """
        Launch Claude in a new terminal window.

        Args:
            directory: Working directory for Claude
            command: Command to execute (default: "claude")
            use_powershell: Force PowerShell on Windows (ignored - platform default)

        Returns:
            bool: True if launch was successful, False otherwise
        """
        if not directory:
            logger.error("No directory specified")
            return False

        try:
            # Platform launcher uses its own terminal defaults
            self._platform_launcher.launch_claude(
                directory=directory,
                command=command
            )
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
