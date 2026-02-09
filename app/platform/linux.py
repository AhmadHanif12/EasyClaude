"""Linux terminal launcher implementation for EasyClaude.

This module provides Linux-specific terminal launching with support for
multiple terminal emulators and desktop environments.

Supported terminals:
    - gnome-terminal (GNOME, Ubuntu, Fedora default)
    - konsole (KDE Plasma default)
    - xfce4-terminal (XFCE default)
    - mate-terminal (MATE default)
    - lxterminal (LXDE default)
    - kitty (modern GPU-accelerated terminal)
    - alacritty (modern GPU-accelerated terminal)
    - xterm (universal fallback)

Example:
    launcher = LinuxTerminalLauncher()
    launcher.launch_claude("/home/user/projects", "claude --continue")
"""

import os
import shlex
import shutil
import subprocess
import logging
from typing import Optional, List, Dict, Any

from app.platform import (
    TerminalLauncher,
    TerminalNotFoundError,
    LaunchFailedError,
)

logger = logging.getLogger(__name__)

# Desktop environment to terminal mapping
# Each DE lists terminals in order of preference
DE_TERMINAL_MAP: Dict[str, List[str]] = {
    'gnome': ['gnome-terminal', 'kgx', 'kitty', 'xterm'],
    'kde': ['konsole', 'gnome-terminal', 'kitty', 'xterm'],
    'xfce': ['xfce4-terminal', 'gnome-terminal', 'kitty', 'xterm'],
    'mate': ['mate-terminal', 'gnome-terminal', 'kitty', 'xterm'],
    'lxde': ['lxterminal', 'gnome-terminal', 'kitty', 'xterm'],
    'cinnamon': ['gnome-terminal', 'mate-terminal', 'kitty', 'xterm'],
    'pantheon': ['gnome-terminal', 'kitty', 'xterm'],
    'budgie': ['gnome-terminal', 'kitty', 'xterm'],
    'deepin': ['gnome-terminal', 'kitty', 'xterm'],
}

# All supported terminals
TERMINALS = [
    "gnome-terminal",
    "konsole",
    "xfce4-terminal",
    "mate-terminal",
    "lxterminal",
    "kitty",
    "alacritty",
    "x-terminal-emulator",
    "xterm",
]

# Supported shells for command execution
SHELLS = ["bash", "zsh", "fish"]


class LinuxTerminalLauncher(TerminalLauncher):
    """Linux-specific terminal launcher with DE and shell detection.

    This launcher automatically detects the desktop environment and
    selects an appropriate terminal emulator. It also detects the
    user's default shell and properly escapes commands.

    Attributes:
        terminal_preference: User-specified terminal to use
        _available_terminals: List of installed terminal emulators
        _detected_terminal: Auto-selected or preferred terminal
        _desktop_environment: Detected desktop environment
        _user_shell: Detected user shell
    """

    def __init__(self, terminal_preference: Optional[str] = None):
        """Initialize the Linux terminal launcher.

        Args:
            terminal_preference: Optional terminal name to force use.
                If None, auto-detects based on desktop environment.

        Raises:
            ValueError: If terminal_preference is not a supported terminal.
        """
        self.terminal_preference = terminal_preference
        self._available_terminals: Optional[List[str]] = None
        self._detected_terminal: Optional[str] = None
        self._desktop_environment: Optional[str] = None
        self._user_shell: Optional[str] = None

        # Validate preference if provided
        if terminal_preference and terminal_preference not in TERMINALS:
            raise ValueError(
                f"Unsupported terminal: {terminal_preference}. "
                f"Supported: {', '.join(TERMINALS)}"
            )

        self._detect_environment()
        self._detect_shell()

    def _detect_environment(self) -> None:
        """Detect the Linux environment and available terminals.

        This method:
        1. Detects the desktop environment from XDG_CURRENT_DESKTOP
        2. Scans for available terminal emulators
        3. Selects the best terminal based on DE preference or availability
        """
        # Detect desktop environment
        xdg_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        desktop_session = os.environ.get('DESKTOP_SESSION', '').lower()

        # Parse XDG_CURRENT_DESKTOP (can be colon-separated list)
        de_candidates = xdg_desktop.split(':') if xdg_desktop else []
        if desktop_session and desktop_session not in de_candidates:
            de_candidates.append(desktop_session)

        # Find matching desktop environment
        self._desktop_environment = None
        for candidate in de_candidates:
            candidate = candidate.strip()
            for de_key in DE_TERMINAL_MAP:
                if de_key in candidate or candidate in de_key:
                    self._desktop_environment = de_key
                    logger.debug(f"Detected desktop environment: {de_key}")
                    break
            if self._desktop_environment:
                break

        if not self._desktop_environment:
            logger.debug("Could not detect desktop environment, using defaults")

        # Scan for available terminals
        self._available_terminals = []
        for terminal in TERMINALS:
            if shutil.which(terminal):
                self._available_terminals.append(terminal)
                logger.debug(f"Found terminal: {terminal}")

        # Select terminal based on preference or DE
        if self.terminal_preference:
            self._detected_terminal = self.terminal_preference
            logger.debug(f"Using preferred terminal: {self._detected_terminal}")
        elif self._available_terminals:
            # Use DE-specific preference if available
            if self._desktop_environment:
                preferred_terminals = DE_TERMINAL_MAP.get(
                    self._desktop_environment, []
                )
                for terminal in preferred_terminals:
                    if terminal in self._available_terminals:
                        self._detected_terminal = terminal
                        break

            # Fallback to first available
            if not self._detected_terminal:
                self._detected_terminal = self._available_terminals[0]

            logger.debug(f"Auto-detected terminal: {self._detected_terminal}")
        else:
            logger.warning("No supported terminal emulators found")

    def _detect_shell(self) -> None:
        """Detect the user's default shell.

        Checks SHELL environment variable and validates against supported shells.
        Falls back to bash if SHELL is not a supported shell.
        """
        shell_path = os.environ.get('SHELL', '')
        if shell_path:
            shell_name = os.path.basename(shell_path)
            if shell_name in SHELLS:
                self._user_shell = shell_name
                logger.debug(f"Detected user shell: {shell_name}")
                return

        # Default to bash
        self._user_shell = 'bash'
        logger.debug("Defaulting to bash shell")

    def is_available(self) -> bool:
        """Check if any terminal is available on this system.

        Returns:
            True if at least one supported terminal is installed.
        """
        return len(self._available_terminals) > 0 if self._available_terminals else False

    def _get_terminal_command_array(self, directory: str, command: str) -> List[str]:
        """Get the terminal-specific command array.

        Args:
            directory: The validated directory path
            command: The validated command string

        Returns:
            A list of command arguments suitable for subprocess.Popen.

        Raises:
            LaunchFailedError: If the terminal is not supported.
        """
        terminal = self._detected_terminal
        if not terminal:
            raise LaunchFailedError("No terminal emulator detected")

        # Build the shell command that keeps terminal open
        shell_cmd = self._build_shell_command(directory, command)

        # Terminal-specific command arrays
        terminal_commands: Dict[str, List[str]] = {
            'gnome-terminal': [
                'gnome-terminal',
                '--working-directory', directory,
                '--',
                'bash', '-c', shell_cmd
            ],
            'kgx': [  # GNOME console (Ubuntu's new terminal)
                'kgx',
                '--working-directory', directory,
                '--',
                'bash', '-c', shell_cmd
            ],
            'konsole': [
                'konsole',
                '--workdir', directory,
                '-e', 'bash', '-c', shell_cmd
            ],
            'xfce4-terminal': [
                'xfce4-terminal',
                '--working-directory', directory,
                '-x', 'bash', '-c', shell_cmd
            ],
            'mate-terminal': [
                'mate-terminal',
                '--working-directory', directory,
                '-x', 'bash', '-c', shell_cmd
            ],
            'lxterminal': [
                'lxterminal',
                '--working-directory', directory,
                '-e', f'bash -c {shlex.quote(shell_cmd)}'
            ],
            'kitty': [
                'kitty',
                '--directory', directory,
                'bash', '-c', shell_cmd
            ],
            'alacritty': [
                'alacritty',
                '--working-directory', directory,
                '-e', 'bash', '-c', shell_cmd
            ],
            'x-terminal-emulator': [  # Debian's x-terminal-emulator wrapper
                'x-terminal-emulator',
                '-e', 'bash', '-c', shell_cmd
            ],
            'xterm': [
                'xterm',
                '-e', 'bash', '-c', shell_cmd
            ],
        }

        if terminal not in terminal_commands:
            raise LaunchFailedError(
                f"Terminal '{terminal}' command array not implemented"
            )

        return terminal_commands[terminal]

    def _build_shell_command(self, directory: str, command: str) -> str:
        """Build a shell command that keeps the terminal open.

        Args:
            directory: The validated directory path
            command: The validated command string

        Returns:
            A shell command string that executes the command and keeps
            the terminal open using exec $SHELL.
        """
        # Escape the directory and command for shell safety
        escaped_dir = shlex.quote(directory)
        escaped_cmd = shlex.quote(command)

        # Build command: cd to directory, run command, then exec shell
        # Using exec replaces the shell process, keeping terminal open
        shell = self._user_shell or 'bash'

        if shell == 'fish':
            # Fish shell uses different syntax for keeping terminal open
            return f'cd {escaped_dir}; {escaped_cmd}; exec fish'
        else:
            # bash and zsh use similar syntax
            return f'cd {escaped_dir}; {escaped_cmd}; exec {shell}'

    def get_terminal_command(self, directory: str, command: str) -> List[str]:
        """
        Get the Linux-specific command list for launching Claude.

        Different terminals have different command-line syntax for executing
        commands in a new terminal window. This method handles the differences.

        Args:
            directory: The working directory where Claude should start
            command: The Claude command to execute

        Returns:
            A list of command arguments suitable for subprocess.Popen

        Raises:
            LaunchFailedError: If terminal is not available or paths are invalid
        """
        validated_dir = self._validate_directory(directory)
        validated_cmd = self._validate_command(command)

        terminal = self._detected_terminal
        if not terminal:
            raise LaunchFailedError("No terminal detected. Please install a supported terminal.")

        return self._get_terminal_command_array(str(validated_dir), validated_cmd)

    def launch_claude(self, directory: str, command: str) -> None:
        """
        Launch Claude Code in a Linux terminal.

        Detects the available terminal emulator and launches it with the
        appropriate command to run Claude in the specified directory.

        Args:
            directory: The working directory where Claude should start
            command: The Claude command to execute

        Raises:
            TerminalNotFoundError: If no supported terminal is available
            LaunchFailedError: If the launch fails for any reason
        """
        if not self.is_available():
            raise TerminalNotFoundError(
                "No supported terminal emulator found. "
                "Please install one of: " + ", ".join(TERMINALS)
            )

        try:
            validated_dir = self._validate_directory(directory)
            validated_cmd = self._validate_command(command)

            terminal = self._detected_terminal
            if not terminal:
                raise LaunchFailedError("No terminal detected")

            cmd = self.get_terminal_command(directory, command)

            logger.info(f"Launching Claude in {terminal}: {directory}")
            logger.debug(f"Command: {' '.join(cmd)}")

            # Use Popen to launch without blocking
            # start_new_session=True makes the process independent of the parent
            subprocess.Popen(cmd, start_new_session=True)

            logger.info("Terminal launched successfully")

        except FileNotFoundError as e:
            raise TerminalNotFoundError(
                f"Terminal executable not found: {e.filename}"
            ) from e
        except subprocess.SubprocessError as e:
            raise LaunchFailedError(f"Failed to launch terminal: {e}") from e
        except Exception as e:
            raise LaunchFailedError(f"Unexpected error launching terminal: {e}") from e

    def get_available_terminals(self) -> Dict[str, Any]:
        """Get information about available terminals on this system.

        Returns:
            A dictionary containing:
                - available: List of installed terminal names
                - detected: The auto-selected terminal name
                - supported: List of all supported terminal names
                - desktop_environment: Detected desktop environment
                - user_shell: Detected user shell
        """
        return {
            "available": self._available_terminals or [],
            "detected": self._detected_terminal,
            "supported": TERMINALS,
            "desktop_environment": self._desktop_environment,
            "user_shell": self._user_shell,
        }

    def set_terminal_preference(self, terminal: str) -> None:
        """Set the preferred terminal emulator.

        Args:
            terminal: The terminal name to use

        Raises:
            ValueError: If the terminal is not supported
        """
        if terminal not in TERMINALS:
            raise ValueError(
                f"Unsupported terminal: {terminal}. "
                f"Supported: {', '.join(TERMINALS)}"
            )
        self.terminal_preference = terminal
        self._detected_terminal = terminal
        logger.debug(f"Terminal preference set to: {terminal}")


__all__ = ["LinuxTerminalLauncher", "DE_TERMINAL_MAP", "TERMINALS", "SHELLS"]
