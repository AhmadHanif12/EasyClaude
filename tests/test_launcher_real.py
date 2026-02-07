# Tests for app/launcher.py and app/platform/windows.py
"""Test actual Windows launcher implementation with real classes."""

import pytest
from unittest.mock import MagicMock, patch, Mock, call, mock_open
from pathlib import Path
import subprocess
import sys
import os

# Import the actual classes being tested
from app.launcher import ClaudeLauncher
from app.platform.windows import WindowsTerminalLauncher
from app.platform import TerminalNotFoundError, LaunchFailedError, TerminalLauncherError


@pytest.fixture
def temp_directory(tmp_path):
    """Create a temporary directory for testing."""
    return str(tmp_path)


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file for testing invalid directory paths."""
    file_path = tmp_path / "test_file.txt"
    file_path.touch()
    return str(file_path)


class TestWindowsTerminalLauncherInit:
    """Test WindowsTerminalLauncher initialization and environment detection."""

    @patch('shutil.which')
    @patch('glob.glob')
    def test_init_with_default_preferences(self, mock_glob, mock_which):
        """Test initialization with default Windows Terminal preference."""
        # Mock PowerShell found, but no Windows Terminal
        # Need to mock which to return None for wt.exe but value for powershell.exe
        def which_side_effect(cmd):
            if cmd == 'wt.exe':
                return None
            elif cmd == 'powershell.exe':
                return 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'
            elif cmd == 'pwsh.exe':
                return None
            return None

        mock_which.side_effect = which_side_effect
        mock_glob.return_value = []  # No Windows Terminal in glob

        launcher = WindowsTerminalLauncher()

        assert launcher.prefer_windows_terminal is True
        assert launcher._has_wt is False
        assert launcher._wt_exe is None
        assert launcher._powershell_exe == 'powershell.exe'

    @patch('shutil.which')
    @patch('glob.glob')
    def test_init_with_windows_terminal_disabled(self, mock_glob, mock_which):
        """Test initialization preferring legacy console."""
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'
        mock_glob.return_value = []

        launcher = WindowsTerminalLauncher(prefer_windows_terminal=False)

        assert launcher.prefer_windows_terminal is False

    @patch('shutil.which')
    @patch('glob.glob')
    def test_detect_environment_with_windows_terminal(self, mock_glob, mock_which):
        """Test environment detection when Windows Terminal is present."""
        # Mock Windows Terminal found
        wt_path = 'C:\\Program Files\\WindowsApps\\Microsoft.WindowsTerminal_1.15.0.0\\wt.exe'
        mock_glob.return_value = [wt_path]
        mock_which.side_effect = lambda x: 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe' if x == 'powershell.exe' else None

        launcher = WindowsTerminalLauncher()

        assert launcher._has_wt is True
        assert launcher._wt_exe == wt_path

    @patch('shutil.which')
    @patch('glob.glob')
    def test_detect_environment_without_windows_terminal(self, mock_glob, mock_which):
        """Test environment detection when Windows Terminal is absent."""
        mock_glob.return_value = []
        mock_which.side_effect = lambda x: 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe' if x == 'powershell.exe' else None

        launcher = WindowsTerminalLauncher()

        assert launcher._has_wt is False
        assert launcher._wt_exe is None

    @patch('shutil.which')
    @patch('glob.glob')
    def test_detect_environment_powershell_fallback_to_pwsh(self, mock_glob, mock_which):
        """Test fallback to PowerShell Core when PowerShell not found."""
        mock_glob.return_value = []
        # PowerShell not found, but pwsh is
        mock_which.side_effect = lambda x: 'C:\\Program Files\\PowerShell\\7\\pwsh.exe' if x == 'pwsh.exe' else None

        launcher = WindowsTerminalLauncher()

        assert launcher._powershell_exe == 'pwsh.exe'


class TestWindowsTerminalLauncherAvailability:
    """Test WindowsTerminalLauncher availability checks."""

    @patch('shutil.which')
    @patch('glob.glob')
    def test_is_available_with_powershell(self, mock_glob, mock_which):
        """Test is_available returns True when PowerShell detected."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

        launcher = WindowsTerminalLauncher()

        assert launcher.is_available() is True

    @patch('shutil.which')
    @patch('glob.glob')
    def test_is_available_without_powershell(self, mock_glob, mock_which):
        """Test is_available returns False when PowerShell absent."""
        mock_glob.return_value = []
        mock_which.return_value = None

        launcher = WindowsTerminalLauncher()

        assert launcher.is_available() is False

    @patch('shutil.which')
    @patch('glob.glob')
    def test_get_available_terminals(self, mock_glob, mock_which):
        """Test get_available_terminals returns correct dict."""
        wt_path = 'C:\\Program Files\\WindowsApps\\Microsoft.WindowsTerminal_1.15.0.0\\wt.exe'
        ps_path = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

        def which_side_effect(cmd):
            if cmd == 'wt.exe':
                return wt_path
            elif cmd == 'powershell.exe':
                return ps_path
            elif cmd == 'pwsh.exe':
                return None
            return None

        mock_which.side_effect = which_side_effect
        mock_glob.return_value = [wt_path]

        launcher = WindowsTerminalLauncher()

        result = launcher.get_available_terminals()

        # _has_wt is a boolean, not the path
        assert result['windows_terminal'] is True
        assert result['powershell'] == ps_path
        assert 'powershell_core' in result

    @patch('shutil.which')
    @patch('glob.glob')
    def test_set_prefer_windows_terminal(self, mock_glob, mock_which):
        """Test set_prefer_windows_terminal changes preference."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

        launcher = WindowsTerminalLauncher()

        launcher.set_prefer_windows_terminal(False)
        assert launcher.prefer_windows_terminal is False

        launcher.set_prefer_windows_terminal(True)
        assert launcher.prefer_windows_terminal is True


class TestWindowsTerminalLauncherValidation:
    """Test WindowsTerminalLauncher validation methods."""

    @patch('shutil.which')
    @patch('glob.glob')
    def test_validate_directory_exists(self, mock_glob, mock_which, temp_directory):
        """Test _validate_directory with valid directory."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

        launcher = WindowsTerminalLauncher()

        result = launcher._validate_directory(temp_directory)

        assert isinstance(result, Path)
        assert str(result) == str(Path(temp_directory).resolve())

    @patch('shutil.which')
    @patch('glob.glob')
    def test_validate_directory_not_exists(self, mock_glob, mock_which):
        """Test _validate_directory raises LaunchFailedError for missing dir."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

        launcher = WindowsTerminalLauncher()

        with pytest.raises(LaunchFailedError) as exc_info:
            launcher._validate_directory("C:\\Nonexistent\\Directory\\Path")

        assert "Directory does not exist" in str(exc_info.value)

    @patch('shutil.which')
    @patch('glob.glob')
    def test_validate_directory_is_file(self, mock_glob, mock_which, temp_file):
        """Test _validate_directory raises LaunchFailedError for file path."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

        launcher = WindowsTerminalLauncher()

        with pytest.raises(LaunchFailedError) as exc_info:
            launcher._validate_directory(temp_file)

        assert "Path is not a directory" in str(exc_info.value)

    @patch('shutil.which')
    @patch('glob.glob')
    def test_validate_command_valid(self, mock_glob, mock_which):
        """Test _validate_command with valid claude command."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

        launcher = WindowsTerminalLauncher()

        result = launcher._validate_command("claude")
        assert result == "claude"

        result = launcher._validate_command("  claude --continue  ")
        assert result == "claude --continue"

    @patch('shutil.which')
    @patch('glob.glob')
    def test_validate_command_empty(self, mock_glob, mock_which):
        """Test _validate_command raises LaunchFailedError for empty command."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

        launcher = WindowsTerminalLauncher()

        with pytest.raises(LaunchFailedError) as exc_info:
            launcher._validate_command("")

        assert "Command cannot be empty" in str(exc_info.value)

        with pytest.raises(LaunchFailedError) as exc_info:
            launcher._validate_command("   ")

        assert "Command cannot be empty" in str(exc_info.value)

    @patch('shutil.which')
    @patch('glob.glob')
    def test_validate_command_not_claude(self, mock_glob, mock_which):
        """Test _validate_command raises for non-claude command."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

        launcher = WindowsTerminalLauncher()

        with pytest.raises(LaunchFailedError) as exc_info:
            launcher._validate_command("git status")

        assert "Invalid command" in str(exc_info.value)


class TestWindowsTerminalLauncherCommandBuilding:
    """Test WindowsTerminalLauncher command building methods."""

    @patch('shutil.which')
    @patch('glob.glob')
    def test_build_powershell_command_basic(self, mock_glob, mock_which):
        """Test _build_powershell_command with basic inputs."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

        launcher = WindowsTerminalLauncher()

        result = launcher._build_powershell_command("C:\\Users\\Test", "claude")

        assert "Set-Location -LiteralPath" in result
        assert "C:\\Users\\Test" in result
        assert "claude" in result
        assert result.endswith("claude")

    @patch('shutil.which')
    @patch('glob.glob')
    def test_build_powershell_command_with_backtick(self, mock_glob, mock_which):
        """Test backtick escaping in directory path."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

        launcher = WindowsTerminalLauncher()

        result = launcher._build_powershell_command("C:\\Test`Dir", "claude")

        # Backtick should be escaped to double backtick
        assert "``" in result

    @patch('shutil.which')
    @patch('glob.glob')
    def test_build_powershell_command_with_quotes(self, mock_glob, mock_which):
        """Test quote escaping in directory path."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

        launcher = WindowsTerminalLauncher()

        result = launcher._build_powershell_command('C:\\Test"Dir', "claude")

        # Quote should be escaped
        assert "`\"" in result

    @patch('shutil.which')
    @patch('glob.glob')
    def test_get_terminal_command_with_windows_terminal(self, mock_glob, mock_which, temp_directory):
        """Test get_terminal_command returns wt.exe command when WT preferred."""
        wt_path = 'C:\\Program Files\\WindowsApps\\Microsoft.WindowsTerminal_1.15.0.0\\wt.exe'
        mock_glob.return_value = [wt_path]
        mock_which.side_effect = lambda x: 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe' if x == 'powershell.exe' else wt_path

        launcher = WindowsTerminalLauncher(prefer_windows_terminal=True)

        result = launcher.get_terminal_command(temp_directory, "claude")

        assert result[0] == 'wt.exe'
        assert 'powershell.exe' in result
        assert '-NoExit' in result
        assert '-Command' in result

    @patch('shutil.which')
    @patch('glob.glob')
    def test_get_terminal_command_without_windows_terminal(self, mock_glob, mock_which, temp_directory):
        """Test get_terminal_command returns powershell.exe when WT not preferred."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

        launcher = WindowsTerminalLauncher(prefer_windows_terminal=False)

        result = launcher.get_terminal_command(temp_directory, "claude")

        assert result[0] == 'powershell.exe'
        assert '-NoExit' in result
        assert '-Command' in result

    @patch('shutil.which')
    @patch('glob.glob')
    def test_get_terminal_command_without_wt_installed(self, mock_glob, mock_which, temp_directory):
        """Test get_terminal_command returns powershell.exe when WT not installed."""
        def which_side_effect(cmd):
            if cmd == 'wt.exe':
                return None  # WT not installed
            elif cmd == 'powershell.exe':
                return 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'
            elif cmd == 'pwsh.exe':
                return None
            return None

        mock_which.side_effect = which_side_effect
        mock_glob.return_value = []  # No WT in glob either

        launcher = WindowsTerminalLauncher(prefer_windows_terminal=True)

        result = launcher.get_terminal_command(temp_directory, "claude")

        # Should fall back to PowerShell since WT is not available
        assert result[0] == 'powershell.exe'


class TestWindowsTerminalLauncherLaunch:
    """Test WindowsTerminalLauncher.launch_claude method."""

    @patch('subprocess.Popen')
    @patch('shutil.which')
    @patch('glob.glob')
    def test_launch_claude_with_windows_terminal(self, mock_glob, mock_which, mock_popen, temp_directory):
        """Test launch_claude uses Windows Terminal when available."""
        wt_path = 'C:\\Program Files\\WindowsApps\\Microsoft.WindowsTerminal_1.15.0.0\\wt.exe'
        mock_glob.return_value = [wt_path]
        mock_which.side_effect = lambda x: 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe' if x == 'powershell.exe' else wt_path
        mock_popen.return_value = MagicMock()

        launcher = WindowsTerminalLauncher(prefer_windows_terminal=True)

        launcher.launch_claude(temp_directory, "claude")

        # Verify Popen was called
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args

        # Check that wt.exe is in the command
        cmd = call_args[0][0]
        assert cmd[0] == wt_path
        assert 'powershell.exe' in cmd
        assert shell_not_used(call_args)

    @patch('subprocess.Popen')
    @patch('shutil.which')
    @patch('glob.glob')
    def test_launch_claude_without_windows_terminal(self, mock_glob, mock_which, mock_popen, temp_directory):
        """Test launch_claude uses PowerShell when WT not available."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'
        mock_popen.return_value = MagicMock()

        launcher = WindowsTerminalLauncher(prefer_windows_terminal=False)

        launcher.launch_claude(temp_directory, "claude")

        # Verify Popen was called
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args

        # Check command structure
        cmd = call_args[0][0]
        assert cmd[0] == 'powershell.exe'
        assert '-NoExit' in cmd
        assert '-Command' in cmd

    @patch('subprocess.Popen')
    @patch('shutil.which')
    @patch('glob.glob')
    def test_launch_claude_creates_new_process_group(self, mock_glob, mock_which, mock_popen, temp_directory):
        """Test launch_claude sets CREATE_NEW_PROCESS_GROUP flag."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'
        mock_popen.return_value = MagicMock()

        launcher = WindowsTerminalLauncher(prefer_windows_terminal=False)

        launcher.launch_claude(temp_directory, "claude")

        # Verify Popen was called with creationflags
        call_args = mock_popen.call_args
        assert 'creationflags' in call_args[1]
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        assert call_args[1]['creationflags'] == CREATE_NEW_PROCESS_GROUP

    @patch('subprocess.Popen')
    @patch('shutil.which')
    @patch('glob.glob')
    def test_launch_claude_shell_false_for_security(self, mock_glob, mock_which, mock_popen, temp_directory):
        """Test launch_claude uses shell=False for security."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'
        mock_popen.return_value = MagicMock()

        launcher = WindowsTerminalLauncher(prefer_windows_terminal=False)

        launcher.launch_claude(temp_directory, "claude")

        # Verify shell=False (security best practice)
        call_args = mock_popen.call_args
        assert shell_not_used(call_args)

    @patch('subprocess.Popen', side_effect=FileNotFoundError("powershell.exe not found"))
    @patch('shutil.which')
    @patch('glob.glob')
    def test_launch_claude_powershell_not_found(self, mock_glob, mock_which, mock_popen, temp_directory):
        """Test launch_claude raises TerminalNotFoundError for missing PowerShell."""
        # This test simulates the edge case where PowerShell was detected during
        # initialization but disappears before launch
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

        launcher = WindowsTerminalLauncher()

        with pytest.raises(TerminalNotFoundError) as exc_info:
            launcher.launch_claude(temp_directory, "claude")

        assert "Failed to launch terminal" in str(exc_info.value)

    @patch('shutil.which')
    @patch('glob.glob')
    def test_launch_claude_when_not_available(self, mock_glob, mock_which, temp_directory):
        """Test launch_claude raises when is_available is False."""
        mock_glob.return_value = []
        mock_which.return_value = None  # No PowerShell

        launcher = WindowsTerminalLauncher()

        with pytest.raises(TerminalNotFoundError) as exc_info:
            launcher.launch_claude(temp_directory, "claude")

        assert "PowerShell is not available" in str(exc_info.value)

    @patch('subprocess.Popen')
    @patch('shutil.which')
    @patch('glob.glob')
    def test_launch_claude_invalid_directory(self, mock_glob, mock_which, mock_popen):
        """Test launch_claude handles invalid directory."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

        launcher = WindowsTerminalLauncher()

        with pytest.raises(LaunchFailedError) as exc_info:
            launcher.launch_claude("C:\\Nonexistent\\Directory", "claude")

        assert "Directory does not exist" in str(exc_info.value)

    @patch('subprocess.Popen')
    @patch('shutil.which')
    @patch('glob.glob')
    def test_launch_claude_invalid_command(self, mock_glob, mock_which, mock_popen, temp_directory):
        """Test launch_claude handles invalid command."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

        launcher = WindowsTerminalLauncher()

        with pytest.raises(LaunchFailedError) as exc_info:
            launcher.launch_claude(temp_directory, "git status")

        assert "Invalid command" in str(exc_info.value)

    @patch('subprocess.Popen')
    @patch('shutil.which')
    @patch('glob.glob')
    def test_launch_claude_with_command_arguments(self, mock_glob, mock_which, mock_popen, temp_directory):
        """Test launch_claude passes command arguments correctly."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'
        mock_popen.return_value = MagicMock()

        launcher = WindowsTerminalLauncher()

        launcher.launch_claude(temp_directory, "claude --continue --max-tokens 10000")

        # Verify Popen was called
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args

        # Check that command arguments are in the PowerShell command
        cmd = call_args[0][0]
        ps_command = cmd[cmd.index('-Command') + 1]
        assert '--continue' in ps_command
        assert '--max-tokens' in ps_command
        assert '10000' in ps_command

    @patch('subprocess.Popen', side_effect=subprocess.SubprocessError("Launch failed"))
    @patch('shutil.which')
    @patch('glob.glob')
    def test_launch_claude_subprocess_error(self, mock_glob, mock_which, mock_popen, temp_directory):
        """Test launch_claude raises LaunchFailedError for subprocess errors."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

        launcher = WindowsTerminalLauncher()

        with pytest.raises(LaunchFailedError) as exc_info:
            launcher.launch_claude(temp_directory, "claude")

        assert "Failed to launch terminal" in str(exc_info.value)


class TestClaudeLauncher:
    """Test high-level ClaudeLauncher interface."""

    def test_init(self):
        """Test ClaudeLauncher initialization."""
        launcher = ClaudeLauncher()

        assert launcher._platform_launcher is not None
        assert hasattr(launcher._platform_launcher, 'launch_claude')
        assert hasattr(launcher._platform_launcher, 'is_available')

    @patch('app.platform.windows.WindowsTerminalLauncher.launch_claude')
    @patch('shutil.which')
    @patch('glob.glob')
    def test_launch_success(self, mock_glob, mock_which, mock_launch, temp_directory):
        """Test launch returns True on success."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'
        mock_launch.return_value = None

        launcher = ClaudeLauncher()

        result = launcher.launch(temp_directory, "claude")

        assert result is True
        mock_launch.assert_called_once_with(directory=temp_directory, command="claude")

    @patch('app.platform.windows.WindowsTerminalLauncher.launch_claude')
    @patch('shutil.which')
    @patch('glob.glob')
    def test_launch_with_custom_command(self, mock_glob, mock_which, mock_launch, temp_directory):
        """Test launch passes custom command to platform launcher."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'
        mock_launch.return_value = None

        launcher = ClaudeLauncher()

        result = launcher.launch(temp_directory, "claude --continue")

        assert result is True
        mock_launch.assert_called_once_with(directory=temp_directory, command="claude --continue")

    @patch('app.platform.windows.WindowsTerminalLauncher.launch_claude',
           side_effect=TerminalNotFoundError("PowerShell not found"))
    @patch('shutil.which')
    @patch('glob.glob')
    def test_launch_terminal_not_found(self, mock_glob, mock_which, mock_launch):
        """Test launch returns False for TerminalNotFoundError."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

        launcher = ClaudeLauncher()

        result = launcher.launch("C:\\Some\\Dir", "claude")

        assert result is False

    @patch('app.platform.windows.WindowsTerminalLauncher.launch_claude',
           side_effect=LaunchFailedError("Directory not found"))
    @patch('shutil.which')
    @patch('glob.glob')
    def test_launch_failed_error(self, mock_glob, mock_which, mock_launch):
        """Test launch returns False for LaunchFailedError."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

        launcher = ClaudeLauncher()

        result = launcher.launch("C:\\Some\\Dir", "claude")

        assert result is False

    @patch('app.platform.windows.WindowsTerminalLauncher.launch_claude',
           side_effect=Exception("Unexpected error"))
    @patch('shutil.which')
    @patch('glob.glob')
    def test_launch_unexpected_error(self, mock_glob, mock_which, mock_launch):
        """Test launch returns False for unexpected exceptions."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

        launcher = ClaudeLauncher()

        result = launcher.launch("C:\\Some\\Dir", "claude")

        assert result is False

    @patch('shutil.which')
    @patch('glob.glob')
    def test_launch_no_directory(self, mock_glob, mock_which):
        """Test launch returns False when directory is None/empty."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

        launcher = ClaudeLauncher()

        assert launcher.launch("", "claude") is False
        assert launcher.launch(None, "claude") is False

    @patch('app.platform.windows.WindowsTerminalLauncher.is_available')
    @patch('shutil.which')
    @patch('glob.glob')
    def test_is_available(self, mock_glob, mock_which, mock_available):
        """Test is_available delegates to platform launcher."""
        mock_glob.return_value = []
        mock_which.return_value = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'
        mock_available.return_value = True

        launcher = ClaudeLauncher()

        result = launcher.is_available()

        assert result is True
        mock_available.assert_called_once()


# Helper functions

def shell_not_used(call_args):
    """Check that shell=False was used in subprocess.Popen call."""
    kwargs = call_args[1] if len(call_args) > 1 else {}
    shell_value = kwargs.get('shell', None)
    # If shell is not specified, it defaults to False
    return shell_value is False or shell_value is None
