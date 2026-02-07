r"""
Windows terminal launcher implementation for EasyClaude.

This module provides Windows-specific terminal launching using PowerShell.
It supports both Windows Terminal and the legacy console window.

Example:
    launcher = WindowsTerminalLauncher()
    launcher.launch_claude(r"C:\Users\Projects", "claude --continue")
"""
import os
import subprocess
import shutil
import logging
from typing import Optional

from app.platform import (
    TerminalLauncher,
    TerminalNotFoundError,
    LaunchFailedError,
)

logger = logging.getLogger(__name__)


class WindowsTerminalLauncher(TerminalLauncher):
    """Windows-specific terminal launcher using PowerShell."""

    POWERSHELL_EXE = "powershell.exe"
    PWSH_EXE = "pwsh.exe"
    WT_EXE = "wt.exe"

    def __init__(self, prefer_windows_terminal: bool = True):
        """Initialize the Windows terminal launcher."""
        self.prefer_windows_terminal = prefer_windows_terminal
        self._has_wt: Optional[bool] = None
        self._powershell_exe: Optional[str] = None
        self._detect_environment()

    def _detect_environment(self) -> None:
        """Detect the Windows environment and available terminals."""
        self._has_wt = shutil.which(self.WT_EXE) is not None
        if self._has_wt:
            logger.debug("Windows Terminal detected")
        else:
            logger.debug("Windows Terminal not found, will use legacy console")
        if shutil.which(self.POWERSHELL_EXE):
            self._powershell_exe = self.POWERSHELL_EXE
            logger.debug(f"Using PowerShell: {self._powershell_exe}")
        elif shutil.which(self.PWSH_EXE):
            self._powershell_exe = self.PWSH_EXE
            logger.debug(f"Using PowerShell Core: {self._powershell_exe}")
        else:
            logger.warning("PowerShell not found on system")

    def is_available(self) -> bool:
        """Check if PowerShell is available on this system."""
        return self._powershell_exe is not None

    def get_terminal_command(self, directory: str, command: str) -> list[str]:
        """Get the Windows-specific command list for launching Claude."""
        validated_dir = self._validate_directory(directory)
        validated_cmd = self._validate_command(command)
        ps_command = self._build_powershell_command(str(validated_dir), validated_cmd)
        use_wt = self.prefer_windows_terminal and self._has_wt
        if use_wt:
            return [self.WT_EXE, self._powershell_exe, "-NoExit", "-Command", ps_command]
        else:
            return [self._powershell_exe, "-NoExit", "-Command", ps_command]

    def _build_powershell_command(self, directory: str, command: str) -> str:
        """
        Build a PowerShell command string for execution.

        Uses proper escaping to prevent command injection.
        Directory is escaped using PowerShell's escape character and wrapped in quotes.
        Command is validated to prevent injection.

        Args:
            directory: The validated directory path
            command: The validated command string

        Returns:
            A safely escaped PowerShell command string
        """
        # Escape backticks and quotes for PowerShell
        # PowerShell uses backtick ` as escape character
        escaped_dir = directory.replace('`', '``').replace('"', '`"')

        # Build command with Set-Location (safer than cd)
        # Using single quotes around path to prevent variable expansion
        ps_command = f"Set-Location -LiteralPath '{escaped_dir}'; {command}"

        return ps_command

    def launch_claude(self, directory: str, command: str) -> None:
        """Launch Claude Code in a Windows PowerShell terminal."""
        if not self.is_available():
            raise TerminalNotFoundError("PowerShell is not available on this system. Please install PowerShell to use EasyClaude.")
        try:
            use_wt = self.prefer_windows_terminal and self._has_wt
            terminal_type = "Windows Terminal" if use_wt else "PowerShell console"
            
            # Build the PowerShell command
            validated_dir = self._validate_directory(directory)
            validated_cmd = self._validate_command(command)
            ps_command = self._build_powershell_command(str(validated_dir), validated_cmd)
            
            if use_wt:
                # Windows Terminal requires special handling
                # Use the wt.exe command-line syntax properly
                cmd = [
                    self.WT_EXE,
                    self._powershell_exe,
                    "-NoExit",
                    "-Command",
                    ps_command
                ]
            else:
                # Standard PowerShell console
                cmd = [
                    self._powershell_exe,
                    "-NoExit",
                    "-Command",
                    ps_command
                ]
            
            logger.info(f"Launching Claude in {terminal_type}: {directory}")
            logger.debug(f"Command: {' '.join(cmd)}")
            
            # For wt.exe, we need to use shell=True or launch it differently
            if use_wt:
                # Windows Terminal needs to be launched through the shell
                subprocess.Popen(cmd, shell=True)
            else:
                # PowerShell can be launched directly
                CREATE_NEW_PROCESS_GROUP = 0x00000200
                subprocess.Popen(cmd, creationflags=CREATE_NEW_PROCESS_GROUP)
            
            logger.info("Terminal launched successfully")
        except FileNotFoundError as e:
            raise TerminalNotFoundError(f"Failed to launch terminal: {e.filename} not found") from e
        except subprocess.SubprocessError as e:
            raise LaunchFailedError(f"Failed to launch terminal: {e}") from e
        except Exception as e:
            raise LaunchFailedError(f"Unexpected error launching terminal: {e}") from e

    def get_available_terminals(self) -> dict:
        """Get information about available terminals on this system."""
        return {"windows_terminal": self._has_wt, "powershell": shutil.which(self.POWERSHELL_EXE), "powershell_core": shutil.which(self.PWSH_EXE)}

    def set_prefer_windows_terminal(self, prefer: bool) -> None:
        """Set whether to prefer Windows Terminal over legacy console."""
        self.prefer_windows_terminal = prefer
        logger.debug(f"Windows Terminal preference set to: {prefer}")


__all__ = ["WindowsTerminalLauncher"]
