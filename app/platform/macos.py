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
            # Use osascript to run AppleScript
            script = f'''
            tell application "Terminal"
                activate
                do script "cd '{validated_dir}' && {validated_cmd}"
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
        script = f'''
        tell application "Terminal"
            activate
            do script "cd '{directory}' && {command}"
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
