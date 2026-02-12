"""
Platform abstraction layer for EasyClaude.

This module provides a cross-platform interface for launching Claude Code
in platform-appropriate terminals. It implements the Strategy pattern to
allow different terminal launching behaviors per platform.

Usage:
    from app.platform import create_launcher, TerminalLauncher

    launcher = create_launcher()
    launcher.launch_claude(r"C:\\Projects", "claude --continue")
"""

import re
import logging
import platform
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

logger = logging.getLogger(__name__)


class TerminalLauncherError(Exception):
    """Base exception for terminal launcher errors."""
    pass


class TerminalNotFoundError(TerminalLauncherError):
    """Raised when the required terminal is not found on the system."""
    pass


class LaunchFailedError(TerminalLauncherError):
    """Raised when terminal launch fails for any reason."""
    pass


class TerminalLauncher(ABC):
    """
    Abstract base class for platform-specific terminal launchers.

    Each platform implementation must provide methods to:
    1. Launch Claude Code in a terminal at a specified directory
    2. Get the platform-specific command for launching
    3. Check if the terminal is available on the system

    Example:
        class MyTerminalLauncher(TerminalLauncher):
            def launch_claude(self, directory: str, command: str) -> None:
                cmd = self.get_terminal_command(directory, command)
                subprocess.Popen(cmd, ...)

            def get_terminal_command(self, directory: str, command: str) -> list[str]:
                return ["my-terminal", "-e", f"cd {directory} && {command}"]

            def is_available(self) -> bool:
                return shutil.which("my-terminal") is not None
    """

    # Strict whitelist for allowed command patterns to prevent command injection
    # Only allows: claude followed by optional flags (e.g., --continue, --plan, --dangerously-skip-permissions)
    _VALID_COMMAND_PATTERN = re.compile(r'^claude(?:\s+(?:--?[a-z-]+))*$', re.IGNORECASE)

    @abstractmethod
    def launch_claude(self, directory: str, command: str) -> None:
        """
        Launch Claude Code in a terminal at the specified directory.

        Args:
            directory: The working directory where Claude should start
            command: The Claude command to execute (e.g., "claude --continue")

        Raises:
            TerminalNotFoundError: If the terminal is not available
            LaunchFailedError: If the launch fails for any reason
            TerminalLauncherError: For other launcher-specific errors
        """
        pass

    @abstractmethod
    def get_terminal_command(self, directory: str, command: str) -> list[str]:
        """
        Get the platform-specific command list for launching Claude.

        This method returns the command as a list of strings suitable for
        use with subprocess.Popen or similar functions.

        Args:
            directory: The working directory where Claude should start
            command: The Claude command to execute

        Returns:
            A list of command arguments (e.g., ["powershell.exe", "-NoExit", ...])
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the terminal is available on this system.

        Returns:
            True if the terminal can be used, False otherwise
        """
        pass

    def _validate_directory(self, directory: str) -> Path:
        """
        Validate that the directory exists and is accessible.

        Args:
            directory: The directory path to validate

        Returns:
            A Path object for the directory

        Raises:
            LaunchFailedError: If the directory doesn't exist or isn't accessible
        """
        path = Path(directory).expanduser().resolve()

        if not path.exists():
            raise LaunchFailedError(f"Directory does not exist: {directory}")

        if not path.is_dir():
            raise LaunchFailedError(f"Path is not a directory: {directory}")

        return path

    def _validate_command(self, command: str) -> str:
        """
        Validate and sanitize the command string using strict whitelist validation.

        This method prevents command injection by only allowing commands that
        match a strict pattern: 'claude' followed by optional flags.

        Args:
            command: The command to validate

        Returns:
            The validated and normalized command string

        Raises:
            LaunchFailedError: If the command is invalid or potentially dangerous
        """
        if not command or not command.strip():
            raise LaunchFailedError("Command cannot be empty")

        # Strip whitespace and validate against whitelist pattern
        command = command.strip()

        # Use regex whitelist to prevent command injection
        # Only allows: claude [ --flag1 --flag2 ... ]
        # Rejects: claude; rm -rf /, claude | evil, claude && bad, etc.
        if not self._VALID_COMMAND_PATTERN.match(command):
            raise LaunchFailedError(
                f"Invalid command format: {command}. "
                "Only 'claude' with optional flags (e.g., --continue, --plan) is allowed."
            )

        return command


def create_launcher() -> TerminalLauncher:
    """
    Factory function to create the appropriate platform-specific launcher.

    This function detects the current platform and returns an instance
    of the appropriate TerminalLauncher implementation.

    Returns:
        A TerminalLauncher instance for the current platform

    Raises:
        NotImplementedError: If the current platform is not supported

    Example:
        launcher = create_launcher()
        launcher.launch_claude("/home/user/projects", "claude")
    """
    system = platform.system()

    if system == "Windows":
        from app.platform.windows import WindowsTerminalLauncher
        # Always use PowerShell console directly (not Windows Terminal)
        return WindowsTerminalLauncher(prefer_windows_terminal=False)
    elif system == "Linux":
        from app.platform.linux import LinuxTerminalLauncher
        return LinuxTerminalLauncher()
    elif system == "Darwin":  # macOS
        # Future implementation
        raise NotImplementedError("macOS support is planned for a future release")
    else:
        raise NotImplementedError(f"Platform '{system}' is not supported")


def get_platform_info() -> dict:
    """
    Get information about the current platform.

    Returns:
        A dictionary containing platform information:
        - system: OS name (Windows, Linux, Darwin)
        - release: OS release version
        - version: OS version string
        - python_version: Python version
        - supported: Whether this platform is supported
    """
    system = platform.system()
    supported = system in ("Windows", "Linux")

    return {
        "system": system,
        "release": platform.release(),
        "version": platform.version(),
        "python_version": platform.python_version(),
        "supported": supported,
    }


# Backward compatibility alias
get_platform_launcher = create_launcher

__all__ = [
    "TerminalLauncher",
    "TerminalLauncherError",
    "TerminalNotFoundError",
    "LaunchFailedError",
    "create_launcher",
    "get_platform_launcher",
    "get_platform_info",
]
