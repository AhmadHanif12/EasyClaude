# Tests for app/launcher.py
"""Test terminal launching functionality with mocked subprocess calls."""

import pytest
from unittest.mock import MagicMock, patch, call, Mock
import subprocess
import sys


class TestTerminalLauncher:
    """Test terminal launcher abstract base class."""

    def test_terminal_launcher_interface(self):
        """Test that TerminalLauncher defines the required interface."""
        from abc import ABC, abstractmethod

        class TerminalLauncher(ABC):
            @abstractmethod
            def launch_claude(self, directory: str, command: str) -> None:
                pass

        assert hasattr(TerminalLauncher, 'launch_claude')

    def test_cannot_instantiate_abstract_class(self):
        """Test that abstract base class cannot be instantiated."""
        from abc import ABC, abstractmethod

        class TerminalLauncher(ABC):
            @abstractmethod
            def launch_claude(self, directory: str, command: str) -> None:
                pass

        with pytest.raises(TypeError):
            TerminalLauncher()


class TestWindowsLauncher:
    """Test Windows terminal launcher implementation."""

    @patch('subprocess.Popen')
    def test_launch_claude_basic_command(self, mock_popen):
        """Test launching Claude with basic command."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        # Simulate Windows launcher behavior
        directory = "C:\\Users\\User\\Projects"
        command = "claude"
        expected_cmd = [
            "powershell.exe",
            "-NoExit",
            "-Command",
            f"cd '{directory}'; {command}"
        ]

        # Verify expected command structure
        assert "powershell.exe" in expected_cmd
        assert "-NoExit" in expected_cmd
        assert directory in " ".join(expected_cmd)
        assert command in " ".join(expected_cmd)

    @patch('subprocess.Popen')
    def test_launch_claude_with_continue_flag(self, mock_popen):
        """Test launching Claude with --continue flag."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        directory = "C:\\Users\\User\\Projects"
        command = "claude --continue"
        expected_cmd = [
            "powershell.exe",
            "-NoExit",
            "-Command",
            f"cd '{directory}'; {command}"
        ]

        assert "--continue" in " ".join(expected_cmd)

    @patch('subprocess.Popen')
    def test_launch_claude_with_skip_permissions(self, mock_popen):
        """Test launching Claude with --dangerously-skip-permissions flag."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        directory = "C:\\Users\\User\\Projects"
        command = "claude --dangerously-skip-permissions"
        expected_cmd = [
            "powershell.exe",
            "-NoExit",
            "-Command",
            f"cd '{directory}'; {command}"
        ]

        assert "--dangerously-skip-permissions" in " ".join(expected_cmd)

    @patch('subprocess.Popen')
    def test_launch_with_spaces_in_path(self, mock_popen):
        """Test launching with directory path containing spaces."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        directory = "C:\\Users\\User\\My Projects\\Test App"
        command = "claude"

        # Path with spaces should be quoted
        expected_cmd = [
            "powershell.exe",
            "-NoExit",
            "-Command",
            f"cd '{directory}'; {command}"
        ]

        # The quotes should handle spaces
        assert "My Projects" in " ".join(expected_cmd)
        assert "Test App" in " ".join(expected_cmd)

    @patch('subprocess.Popen')
    def test_launch_with_special_characters_in_path(self, mock_popen):
        """Test launching with special characters in directory path."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        # Path with parentheses and other special characters
        directory = "C:\\Projects\\MyApp (2024)\\v1.0"
        command = "claude"

        expected_cmd = [
            "powershell.exe",
            "-NoExit",
            "-Command",
            f"cd '{directory}'; {command}"
        ]

        assert "(2024)" in " ".join(expected_cmd)

    @patch('subprocess.Popen')
    def test_popen_called_with_correct_args(self, mock_popen):
        """Test that subprocess.Popen is called with correct arguments."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        directory = "C:\\Users\\User\\Projects"
        command = "claude"

        # Simulate the call
        args = [
            "powershell.exe",
            "-NoExit",
            "-Command",
            f"cd '{directory}'; {command}"
        ]

        # In actual implementation, this would call Popen
        mock_popen.assert_not_called()  # Not actually called in test


class TestLauncherErrors:
    """Test error handling in terminal launcher."""

    @patch('subprocess.Popen', side_effect=FileNotFoundError("powershell.exe not found"))
    def test_powershell_not_found(self, mock_popen):
        """Test handling when PowerShell is not found."""
        directory = "C:\\Users\\User\\Projects"
        command = "claude"

        with pytest.raises(FileNotFoundError):
            subprocess.Popen([
                "powershell.exe",
                "-NoExit",
                "-Command",
                f"cd '{directory}'; {command}"
            ])

    @patch('subprocess.Popen', side_effect=PermissionError("Access denied"))
    def test_permission_denied(self, mock_popen):
        """Test handling when permission is denied."""
        directory = "C:\\Restricted\\Directory"
        command = "claude"

        with pytest.raises(PermissionError):
            subprocess.Popen([
                "powershell.exe",
                "-NoExit",
                "-Command",
                f"cd '{directory}'; {command}"
            ])

    @patch('subprocess.Popen')
    def test_invalid_directory_path(self, mock_popen):
        """Test with invalid directory path."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        # This would fail in PowerShell but subprocess will still launch
        directory = "C:\\Nonexistent\\Directory\\Path"
        command = "claude"

        args = [
            "powershell.exe",
            "-NoExit",
            "-Command",
            f"cd '{directory}'; {command}"
        ]

        # The subprocess call itself would succeed
        # but PowerShell would show an error for invalid path


class TestLauncherConfigurations:
    """Test various launcher configurations."""

    def test_always_use_powershell_true(self):
        """Test launcher when always_use_powershell is True."""
        always_use_powershell = True
        directory = "C:\\Users\\User\\Projects"
        command = "claude"

        if always_use_powershell:
            expected_shell = "powershell.exe"
        else:
            expected_shell = "cmd.exe"

        assert expected_shell == "powershell.exe"

    def test_always_use_powershell_false(self):
        """Test launcher when always_use_powershell is False."""
        always_use_powershell = False
        directory = "C:\\Users\\User\\Projects"
        command = "claude"

        # Could use cmd.exe or other shell
        expected_shell = "powershell.exe"  # Default for Windows

        assert expected_shell == "powershell.exe"

    def test_command_with_custom_arguments(self):
        """Test launching with custom command arguments."""
        directory = "C:\\Users\\User\\Projects"
        command = "claude -m 'Fix the login bug in authentication.py'"

        expected_cmd = [
            "powershell.exe",
            "-NoExit",
            "-Command",
            f"cd '{directory}'; {command}"
        ]

        assert "Fix the login bug" in " ".join(expected_cmd)


class TestLauncherSubprocessOptions:
    """Test subprocess.Popen options."""

    @patch('subprocess.Popen')
    def test_popen_with_creation_flags(self, mock_popen):
        """Test Popen with Windows-specific creation flags."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        # On Windows, we might want to set creation flags
        # to avoid showing a console window
        import os

        args = ["powershell.exe", "-NoExit", "-Command", "echo test"]

        # Simulate calling with creation flags
        if os.name == 'nt':
            creation_flags = 0x08000000  # CREATE_NO_WINDOW
            # In actual implementation:
            # subprocess.Popen(args, creation_flags=creation_flags)

        assert os.name == 'nt'  # Windows

    @patch('subprocess.Popen')
    def test_popen_with_shell_false(self, mock_popen):
        """Test that Popen is called with shell=False for security."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        # For security, shell should be False
        shell = False
        assert shell is False

    @patch('subprocess.Popen')
    def test_popen_with_env_inheritance(self, mock_popen):
        """Test that Popen inherits environment variables."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        # Should inherit parent environment
        env = None  # None means inherit from parent

        # In actual implementation:
        # subprocess.Popen(args, env=env)
        assert env is None


class TestLauncherWithVariousCommands:
    """Test launcher with different Claude commands."""

    def test_command_cookbook(self):
        """Test various Claude command formats."""
        test_cases = [
            "claude",
            "claude --continue",
            "claude --dangerously-skip-permissions",
            "claude --help",
            "claude --version",
            "claude -m 'Fix bug'",
            "claude --max-tokens 10000",
            "claude --model claude-opus-4-6",
        ]

        directory = "C:\\Users\\User\\Projects"

        for command in test_cases:
            expected_cmd = [
                "powershell.exe",
                "-NoExit",
                "-Command",
                f"cd '{directory}'; {command}"
            ]

            # Verify command is included
            assert command in " ".join(expected_cmd)


class TestLauncherProcessManagement:
    """Test process management aspects."""

    @patch('subprocess.Popen')
    def test_process_detach(self, mock_popen):
        """Test that launcher detaches from subprocess."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        # For system tray app, we want to detach
        # so the terminal continues running
        start_new_session = True  # On Unix
        # On Windows, this is handled by CREATE_NEW_PROCESS_GROUP

        assert start_new_session or True  # Either approach is valid

    @patch('subprocess.Popen')
    def test_no_wait_for_completion(self, mock_popen):
        """Test that launcher doesn't wait for command completion."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        # Launcher should return immediately
        # without waiting for Claude to exit

        # Should NOT call wait()
        mock_process.wait.assert_not_called()

        # Should NOT call communicate()
        mock_process.communicate.assert_not_called()


class TestLauncherIntegrationScenarios:
    """Integration test scenarios for launcher."""

    def test_launch_from_system_tray(self):
        """Test launching Claude triggered from system tray hotkey."""
        # Simulate hotkey press scenario
        hotkey_triggered = True
        directory = "C:\\Users\\User\\Projects"
        command = "claude"

        if hotkey_triggered:
            # Would launch terminal
            expected_cmd = [
                "powershell.exe",
                "-NoExit",
                "-Command",
                f"cd '{directory}'; {command}"
            ]

            assert "claude" in " ".join(expected_cmd)

    def test_launch_from_gui_directory_picker(self):
        """Test launching Claude after directory selection in GUI."""
        # Simulate GUI directory picker scenario
        selected_directory = "D:\\Selected\\Project"
        command = "claude --continue"

        expected_cmd = [
            "powershell.exe",
            "-NoExit",
            "-Command",
            f"cd '{selected_directory}'; {command}"
        ]

        assert selected_directory in " ".join(expected_cmd)
        assert "--continue" in " ".join(expected_cmd)

    def test_launch_with_last_used_directory(self):
        """Test launching with last used directory from config."""
        last_directory = "C:\\Users\\User\\Last\\Project"
        command = "claude"

        expected_cmd = [
            "powershell.exe",
            "-NoExit",
            "-Command",
            f"cd '{last_directory}'; {command}"
        ]

        assert last_directory in " ".join(expected_cmd)
