"""Unit tests for Linux platform implementation."""
import pytest
from unittest.mock import patch, MagicMock
from app.platform.linux import LinuxTerminalLauncher
from app.platform import TerminalNotFoundError, LaunchFailedError


class TestLinuxTerminalLauncherInit:
    """Test Linux terminal launcher initialization."""

    def test_init_without_preference(self):
        """Test initialization without terminal preference."""
        with patch('shutil.which') as mock_which:
            mock_which.return_value = True
            launcher = LinuxTerminalLauncher()
            assert launcher.terminal_preference is None
            assert launcher._detected_terminal is not None

    def test_init_with_preference(self):
        """Test initialization with terminal preference."""
        with patch('shutil.which') as mock_which:
            mock_which.return_value = True
            launcher = LinuxTerminalLauncher(terminal_preference="gnome-terminal")
            assert launcher.terminal_preference == "gnome-terminal"
            assert launcher._detected_terminal == "gnome-terminal"

    def test_init_no_terminals_available(self):
        """Test initialization when no terminals are available."""
        with patch('shutil.which') as mock_which:
            mock_which.return_value = None
            launcher = LinuxTerminalLauncher()
            assert len(launcher._available_terminals) == 0


class TestLinuxEnvironmentDetection:
    """Test Linux environment detection."""

    @patch('shutil.which')
    def test_detect_gnome_terminal(self, mock_which):
        """Test detection of gnome-terminal."""
        mock_which.side_effect = lambda x: x == "gnome-terminal"
        launcher = LinuxTerminalLauncher()
        assert "gnome-terminal" in launcher._available_terminals

    @patch('shutil.which')
    def test_detect_konsole(self, mock_which):
        """Test detection of konsole."""
        mock_which.side_effect = lambda x: x == "konsole"
        launcher = LinuxTerminalLauncher()
        assert "konsole" in launcher._available_terminals

    @patch('shutil.which')
    def test_detect_multiple_terminals(self, mock_which):
        """Test detection of multiple terminals."""
        available = ["gnome-terminal", "konsole", "xterm"]
        mock_which.side_effect = lambda x: x in available
        launcher = LinuxTerminalLauncher()
        assert len(launcher._available_terminals) == 3


class TestLinuxAvailability:
    """Test Linux terminal availability checks."""

    @patch('shutil.which')
    def test_is_available_true(self, mock_which):
        """Test is_available returns True when terminals exist."""
        mock_which.return_value = True
        launcher = LinuxTerminalLauncher()
        assert launcher.is_available() is True

    @patch('shutil.which')
    def test_is_available_false(self, mock_which):
        """Test is_available returns False when no terminals."""
        mock_which.return_value = None
        launcher = LinuxTerminalLauncher()
        assert launcher.is_available() is False


class TestLinuxGetTerminalCommand:
    """Test Linux terminal command generation."""

    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.is_dir', return_value=True)
    @patch('shutil.which', return_value=True)
    def test_get_command_gnome_terminal(self, mock_which, mock_is_dir, mock_exists):
        """Test command generation for gnome-terminal."""
        launcher = LinuxTerminalLauncher(terminal_preference="gnome-terminal")
        cmd = launcher.get_terminal_command("/home/user/project", "claude")
        assert cmd[0] == "gnome-terminal"
        assert "--working-directory" in cmd
        assert "/home/user/project" in cmd

    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.is_dir', return_value=True)
    @patch('shutil.which', return_value=True)
    def test_get_command_konsole(self, mock_which, mock_is_dir, mock_exists):
        """Test command generation for konsole."""
        launcher = LinuxTerminalLauncher(terminal_preference="konsole")
        cmd = launcher.get_terminal_command("/home/user/project", "claude")
        assert cmd[0] == "konsole"
        assert "--workdir" in cmd or "-w" in cmd

    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.is_dir', return_value=True)
    @patch('shutil.which', return_value=True)
    def test_get_command_xfce4_terminal(self, mock_which, mock_is_dir, mock_exists):
        """Test command generation for xfce4-terminal."""
        launcher = LinuxTerminalLauncher(terminal_preference="xfce4-terminal")
        cmd = launcher.get_terminal_command("/home/user/project", "claude")
        assert cmd[0] == "xfce4-terminal"
        assert "--working-directory" in cmd

    @patch('shutil.which', return_value=True)
    def test_get_command_invalid_directory(self, mock_which):
        """Test command generation with invalid directory."""
        launcher = LinuxTerminalLauncher()
        # Should validate directory
        with pytest.raises(LaunchFailedError) as exc_info:
            launcher.get_terminal_command("", "claude")
        assert "Directory" in str(exc_info.value).lower() or "does not exist" in str(exc_info.value).lower()

    @patch('pathlib.Path.exists', return_value=False)
    @patch('shutil.which', return_value=True)
    def test_get_command_nonexistent_directory(self, mock_which, mock_exists):
        """Test command generation with nonexistent directory."""
        launcher = LinuxTerminalLauncher()
        with pytest.raises(LaunchFailedError) as exc_info:
            launcher.get_terminal_command("/nonexistent/path", "claude")
        assert "does not exist" in str(exc_info.value)


class TestLinuxLaunchClaude:
    """Test Claude launching on Linux."""

    @patch('shutil.which')
    def test_launch_unavailable_terminal(self, mock_which):
        """Test launching when no terminal is available."""
        mock_which.return_value = None
        launcher = LinuxTerminalLauncher()
        with pytest.raises(TerminalNotFoundError) as exc_info:
            launcher.launch_claude("/home/user/project", "claude")
        assert "No supported terminal" in str(exc_info.value)

    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.is_dir', return_value=True)
    @patch('subprocess.Popen')
    @patch('shutil.which', return_value=True)
    def test_launch_with_valid_directory(self, mock_which, mock_popen, mock_is_dir, mock_exists):
        """Test launching with a valid directory."""
        launcher = LinuxTerminalLauncher()
        launcher.launch_claude("/home/user/project", "claude")
        # Verify Popen was called to launch the terminal
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args
        assert call_args[1]['start_new_session'] is True

    @patch('shutil.which', return_value=True)
    def test_launch_with_invalid_directory(self, mock_which):
        """Test launching with an invalid directory."""
        launcher = LinuxTerminalLauncher()
        with pytest.raises(LaunchFailedError) as exc_info:
            launcher.launch_claude("/nonexistent/path", "claude")
        assert "does not exist" in str(exc_info.value).lower()


class TestLinuxTerminalPreferences:
    """Test terminal preference management."""

    @patch('shutil.which')
    def test_set_valid_preference(self, mock_which):
        """Test setting a valid terminal preference."""
        mock_which.return_value = True
        launcher = LinuxTerminalLauncher()
        launcher.set_terminal_preference("konsole")
        assert launcher.terminal_preference == "konsole"
        assert launcher._detected_terminal == "konsole"

    @patch('shutil.which')
    def test_set_invalid_preference(self, mock_which):
        """Test setting an invalid terminal preference."""
        mock_which.return_value = True
        launcher = LinuxTerminalLauncher()
        with pytest.raises(ValueError) as exc_info:
            launcher.set_terminal_preference("invalid-terminal")
        assert "Unsupported terminal" in str(exc_info.value)

    @patch('shutil.which')
    def test_get_available_terminals(self, mock_which):
        """Test getting available terminals info."""
        available = ["gnome-terminal", "xterm"]
        mock_which.side_effect = lambda x: x in available
        launcher = LinuxTerminalLauncher()
        info = launcher.get_available_terminals()
        assert info["available"] == available
        assert info["detected"] in available
        assert "gnome-terminal" in info["supported"]
        assert "konsole" in info["supported"]  # All supported terminals listed


class TestLinuxTerminalConstants:
    """Test Linux terminal configuration constants."""

    def test_supported_terminals_list(self):
        """Test that supported terminals list is comprehensive."""
        launcher = LinuxTerminalLauncher()
        expected_terminals = [
            "gnome-terminal",
            "konsole",
            "xfce4-terminal",
            "mate-terminal",
            "lxterminal",
            "x-terminal-emulator",
            "xterm",
        ]
        assert launcher.TERMINALS == expected_terminals

    def test_supported_shells_list(self):
        """Test that supported shells list includes common shells."""
        launcher = LinuxTerminalLauncher()
        expected_shells = ["bash", "zsh", "fish"]
        assert launcher.SHELLS == expected_shells


class TestLinuxPathValidation:
    """Test Linux path validation."""

    @patch('shutil.which', return_value=True)
    def test_validate_unix_absolute_path(self, mock_which):
        """Test validation of Unix absolute paths."""
        launcher = LinuxTerminalLauncher()
        # Should validate Unix-style paths
        test_path = "/home/user/projects"
        # Validation happens in get_terminal_command
        with pytest.raises(LaunchFailedError):
            launcher.get_terminal_command(test_path, "claude")

    @patch('shutil.which', return_value=True)
    def test_validate_home_expansion(self, mock_which):
        """Test validation of paths with ~ home shortcut."""
        launcher = LinuxTerminalLauncher()
        test_path = "~/Documents"
        with pytest.raises(LaunchFailedError):
            launcher.get_terminal_command(test_path, "claude")


class TestLinuxCommandValidation:
    """Test Linux command validation."""

    @patch('shutil.which', return_value=True)
    def test_validate_basic_command(self, mock_which):
        """Test validation of basic Claude command."""
        launcher = LinuxTerminalLauncher()
        with pytest.raises(LaunchFailedError):
            launcher.get_terminal_command("/home/user/project", "claude")

    @patch('shutil.which', return_value=True)
    def test_validate_command_with_flags(self, mock_which):
        """Test validation of command with flags."""
        launcher = LinuxTerminalLauncher()
        with pytest.raises(LaunchFailedError) as exc_info:
            launcher.get_terminal_command("/home/user/project", "claude --continue")
        assert "--continue" in str(exc_info.value)

    @patch('shutil.which', return_value=True)
    def test_validate_command_with_arguments(self, mock_which):
        """Test validation of command with arguments."""
        launcher = LinuxTerminalLauncher()
        with pytest.raises(LaunchFailedError) as exc_info:
            launcher.get_terminal_command("/home/user/project", "claude -m 'Fix bug'")
        assert "Fix bug" in str(exc_info.value)
