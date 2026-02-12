r"""
Windows terminal launcher implementation for EasyClaude.

This module provides Windows-specific terminal launching using PowerShell.
It supports both Windows Terminal and the legacy console window.

Example:
    launcher = WindowsTerminalLauncher()
    launcher.launch_claude(r"C:\Users\Projects", "claude --continue")
"""
import os
import re
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
        self._wt_exe: Optional[str] = None
        self._powershell_exe: Optional[str] = None
        self._detect_environment()

    def _detect_environment(self) -> None:
        """Detect the Windows environment and available terminals."""
        # First, try to find the actual Windows Terminal executable
        # The WindowsApps wt.exe is a 0-byte shim that doesn't work with subprocess
        import glob
        wt_actual = None
        
        # Check Program Files WindowsApps for the real executable
        program_files_apps = r'C:\Program Files\WindowsApps'
        try:
            pattern = os.path.join(program_files_apps, 'Microsoft.WindowsTerminal_*', 'wt.exe')
            matches = glob.glob(pattern)
            if matches:
                # Use the first (latest) match
                wt_actual = matches[0]
                logger.debug(f"Found Windows Terminal executable: {wt_actual}")
        except Exception:
            pass
        
        # Fallback to shutil.which which finds the WindowsApps shim
        if not wt_actual:
            wt_actual = shutil.which(self.WT_EXE)
        
        self._has_wt = wt_actual is not None
        if self._has_wt:
            # Store the actual path to wt.exe
            self._wt_exe = wt_actual
            logger.debug(f"Windows Terminal detected: {self._wt_exe}")
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

    # Strict whitelist for allowed command patterns to prevent injection
    # Only allows: claude followed by optional flags (e.g., --continue, --plan)
    _VALID_COMMAND_PATTERN = re.compile(r'^claude(?:\s+(?:--?[a-z-]+))*$')

    def _build_powershell_command(self, directory: str, command: str) -> str:
        """
        Build a PowerShell command string for execution.

        Uses strict validation and proper escaping to prevent command injection.
        Directory is validated for dangerous characters before being escaped.
        Command must match whitelist pattern before being accepted.

        Args:
            directory: The validated directory path
            command: The validated command string

        Returns:
            A safely escaped PowerShell command string

        Raises:
            LaunchFailedError: If command or directory contains dangerous content
        """
        # Validate command format strictly - whitelist approach
        if not self._VALID_COMMAND_PATTERN.match(command):
            raise LaunchFailedError(
                f"Invalid command format: {command}. "
                "Only 'claude' with optional flags (e.g., --continue) is allowed."
            )

        # Validate directory has no dangerous characters that could break out
        dangerous_chars = ['\n', '\r', '\x00', ';', '&', '|', '$', '`', '"', "'"]
        if any(c in directory for c in dangerous_chars):
            raise LaunchFailedError(
                f"Directory path contains invalid characters. "
                "Please use a standard path without special characters."
            )

        # Escape backticks for PowerShell (uses backtick as escape character)
        escaped_dir = directory.replace('`', '``')

        # Build command with Set-Location (safer than cd)
        # Using -LiteralPath prevents any interpretation of special characters in path
        ps_command = f"Set-Location -LiteralPath '{escaped_dir}'; {command}"

        return ps_command

    def launch_claude(self, directory: str, command: str) -> None:
        """Launch Claude Code in a Windows PowerShell terminal."""
        if not self.is_available():
            raise TerminalNotFoundError("PowerShell is not available on this system. Please install PowerShell to use EasyClaude.")
        try:
            use_wt = self.prefer_windows_terminal and self._has_wt and self._wt_exe
            terminal_type = "Windows Terminal" if use_wt else "PowerShell console"
            
            # Build the PowerShell command
            validated_dir = self._validate_directory(directory)
            validated_cmd = self._validate_command(command)
            ps_command = self._build_powershell_command(str(validated_dir), validated_cmd)
            
            if use_wt:
                # Windows Terminal requires special handling
                # Use the actual wt.exe path (not the WindowsApps shim)
                cmd = [
                    self._wt_exe,  # type: ignore
                    self._powershell_exe,
                    "-NoExit",
                    "-Command",
                    ps_command
                ]
            else:
                # Standard PowerShell console
                cmd = [
                    self._powershell_exe,  # type: ignore
                    "-NoExit",
                    "-Command",
                    ps_command
                ]
            
            logger.info(f"Launching Claude in {terminal_type}: {directory}")
            logger.debug(f"Command: {' '.join(cmd)}")
            
            # For wt.exe, use proper Windows Terminal syntax
            if use_wt:
                # Windows Terminal command line: wt.exe powershell.exe -NoExit -Command "..."
                subprocess.Popen(cmd, shell=False)
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
