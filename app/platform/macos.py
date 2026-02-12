"""
macOS terminal launcher implementation (Phase 2).

Uses AppleScript to launch Terminal.app with specific command.
"""

import subprocess
import shutil
from app.platform import TerminalLauncher, LaunchFailedError


class MacOSTerminalLauncher(TerminalLauncher):
    """
    macOS-specific terminal launcher.

    Uses AppleScript to launch Terminal.app with specific command.
    """

    def _escape_applescript_string(self, s: str) -> str:
        """
        Escape a string for safe use in AppleScript.

        AppleScript uses single quotes for string literals, so we escape
        them by doubling. This prevents breaking out of the string context.

        Args:
            s: The string to escape

        Returns:
            The escaped string safe for AppleScript
        """
        return s.replace("'", "'\\''")

    def launch_claude(
        self,
        directory: str,
        command: str = "claude",
        use_powershell: bool = False,  # Ignored on macOS
    ) -> None:
        """
        Launch Claude in Terminal.app on macOS.

        Args:
            directory: Working directory path
            command: Command to execute
            use_powershell: Ignored on macOS

        Raises:
            LaunchFailedError: If launch fails
        """
        # Validate inputs using base class methods
        validated_dir = self._validate_directory(directory)
        validated_cmd = self._validate_command(command)

        if not self.is_available():
            raise LaunchFailedError("Terminal.app not found on this system")

        try:
            # Escape strings to prevent AppleScript injection
            escaped_dir = self._escape_applescript_string(str(validated_dir))
            escaped_cmd = self._escape_applescript_string(validated_cmd)

            # Use osascript to run AppleScript with properly escaped strings
            script = f'''
            tell application "Terminal"
                activate
                do script "cd '{escaped_dir}' && {escaped_cmd}"
            end tell
            '''

            subprocess.run(["osascript", "-e", script], check=True)
        except subprocess.CalledProcessError as e:
            raise LaunchFailedError(f"Failed to execute AppleScript: {e}") from e
        except Exception as e:
            raise LaunchFailedError(f"Failed to launch Terminal.app: {e}") from e

    def get_terminal_command(self, directory: str, command: str) -> list[str]:
        """
        Get the macOS-specific command list for launching Claude.

        Args:
            directory: The working directory where Claude should start
            command: The Claude command to execute

        Returns:
            A list of command arguments for subprocess
        """
        # Escape strings to prevent AppleScript injection
        escaped_dir = self._escape_applescript_string(directory)
        escaped_cmd = self._escape_applescript_string(command)

        script = f'''
        tell application "Terminal"
            activate
            do script "cd '{escaped_dir}' && {escaped_cmd}"
        end tell
        '''
        return ["osascript", "-e", script]

    def is_available(self) -> bool:
        """
        Check if this launcher is available on macOS.

        Returns:
            bool: True if on macOS and Terminal.app is available
        """
        import platform
        if platform.system() != "Darwin":
            return False

        # Check if osascript is available
        return shutil.which("osascript") is not None
