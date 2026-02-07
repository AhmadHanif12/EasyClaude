"""Linux terminal launcher implementation for EasyClaude (Phase 2 stub)."""

import shutil
import logging
from typing import Optional, List

from app.platform import TerminalLauncher, TerminalNotFoundError, LaunchFailedError

logger = logging.getLogger(__name__)


class LinuxTerminalLauncher(TerminalLauncher):
    """Linux-specific terminal launcher (Phase 2 - Stub Implementation)."""

    TERMINALS = [
        "gnome-terminal",
        "konsole",
        "xfce4-terminal",
        "mate-terminal",
        "lxterminal",
        "x-terminal-emulator",
        "xterm",
    ]

    SHELLS = ["bash", "zsh", "fish"]

    def __init__(self, terminal_preference: Optional[str] = None):
        """Initialize the Linux terminal launcher."""
        self.terminal_preference = terminal_preference
        self._available_terminals: Optional[List[str]] = None
        self._detected_terminal: Optional[str] = None
        self._detect_environment()

    def _detect_environment(self) -> None:
        """Detect the Linux environment and available terminals."""
        self._available_terminals = []
        for terminal in self.TERMINALS:
            if shutil.which(terminal):
                self._available_terminals.append(terminal)
                logger.debug(f"Found terminal: {terminal}")
        if self.terminal_preference is None and self._available_terminals:
            self._detected_terminal = self._available_terminals[0]
            logger.debug(f"Auto-detected terminal: {self._detected_terminal}")
        elif self.terminal_preference:
            self._detected_terminal = self.terminal_preference
            logger.debug(f"Using preferred terminal: {self._detected_terminal}")

    def is_available(self) -> bool:
        """Check if any terminal is available on this system."""
        return len(self._available_terminals) > 0 if self._available_terminals else False

    def get_terminal_command(self, directory: str, command: str) -> List[str]:
        """Get the Linux-specific command list for launching Claude."""
        validated_dir = self._validate_directory(directory)
        validated_cmd = self._validate_command(command)
        raise LaunchFailedError(
            "Linux terminal launcher is not yet implemented. "
            "This feature is planned for Phase 2. "
            f"Would launch in {validated_dir} with command: {validated_cmd}"
        )

    def launch_claude(self, directory: str, command: str) -> None:
        """Launch Claude Code in a Linux terminal."""
        if not self.is_available():
            raise TerminalNotFoundError(
                "No supported terminal emulator found. "
                "Please install one of: " + ", ".join(self.TERMINALS)
            )
        raise LaunchFailedError(
            "Linux terminal launcher is not yet implemented. "
            "This feature is planned for Phase 2. "
            f"Would launch in {directory} with command: {command}"
        )

    def get_available_terminals(self) -> dict:
        """Get information about available terminals on this system."""
        return {
            "available": self._available_terminals or [],
            "detected": self._detected_terminal,
            "supported": self.TERMINALS,
        }

    def set_terminal_preference(self, terminal: str) -> None:
        """Set the preferred terminal emulator."""
        if terminal not in self.TERMINALS:
            raise ValueError(f"Unsupported terminal: {terminal}. Supported: {self.TERMINALS}")
        self.terminal_preference = terminal
        self._detected_terminal = terminal
        logger.debug(f"Terminal preference set to: {terminal}")


__all__ = ["LinuxTerminalLauncher"]
