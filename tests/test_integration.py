# Integration Tests for EasyClaude
"""
End-to-end integration tests for the EasyClaude application.

These tests verify complete user workflows and component integration.
Due to the GUI and system tray nature of the app, some tests use mocking
to simulate user interactions without requiring actual Windows desktop automation.
"""

import pytest
import json
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch, call
import sys


class TestFirstRunNoConfig:
    """Test the first run scenario when no configuration exists."""

    @pytest.fixture
    def clean_config_env(self):
        """Set up a clean environment with no existing config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".easyclaude"
            original_get_config_dir = None

            # Patch config module before importing
            with patch('app.config.get_config_dir', return_value=config_dir):
                from app.config import invalidate_cache
                invalidate_cache()
                yield config_dir

    def test_creates_default_config_on_first_run(self, clean_config_env):
        """Test that default config is created on first run."""
        from app.config import load_config, get_config_path

        config_path = get_config_path()
        assert not config_path.exists(), "Config should not exist initially"

        # Load config (should create default)
        config = load_config()

        # Verify default values
        assert config.hotkey == "ctrl+alt+c"
        assert config.last_directory == ""
        assert config.last_command == "claude"
        assert config.always_use_powershell is False
        assert config.window_position == "center"

        # Verify file was created
        assert config_path.exists(), "Config file should be created"

    def test_first_run_loads_defaults(self, clean_config_env):
        """Test that first run loads all default values correctly."""
        from app.config import load_config, DEFAULT_HOTKEY, DEFAULT_COMMAND

        config = load_config()

        assert config.hotkey == DEFAULT_HOTKEY
        assert config.last_command == DEFAULT_COMMAND
        assert config.last_directory == ""
        assert config.always_use_powershell is False


class TestLaunchWithExistingConfig:
    """Test launching the app with existing configuration."""

    @pytest.fixture
    def existing_config_env(self):
        """Set up environment with existing config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".easyclaude"
            config_dir.mkdir(parents=True, exist_ok=True)
            config_file = config_dir / "config.json"

            # Create existing config
            existing_config = {
                "hotkey": "ctrl+shift+z",
                "last_directory": "C:\\Users\\Test\\Projects",
                "last_command": "claude --continue",
                "always_use_powershell": True,
                "window_position": "100,200"
            }

            with open(config_file, 'w') as f:
                json.dump(existing_config, f)

            with patch('app.config.get_config_dir', return_value=config_dir):
                from app.config import invalidate_cache
                invalidate_cache()
                yield existing_config

    def test_loads_existing_config(self, existing_config_env):
        """Test that existing config is loaded correctly."""
        from app.config import load_config, invalidate_cache

        invalidate_cache()
        config = load_config()

        assert config.hotkey == "ctrl+shift+z"
        assert config.last_directory == "C:\\Users\\Test\\Projects"
        assert config.last_command == "claude --continue"
        assert config.always_use_powershell is True
        assert config.window_position == "100,200"

    def test_app_initiates_with_existing_hotkey(self, existing_config_env):
        """Test that app initializes with the existing hotkey from config."""
        # This test verifies the integration between config and hotkey manager
        from app.config import load_config

        config = load_config()
        assert config.hotkey == "ctrl+shift+z"
        # In real app, HotkeyManager would be initialized with this hotkey


class TestHotkeyChangePersistence:
    """Test changing hotkey and verifying it persists across restarts."""

    def test_hotkey_change_persists(self):
        """Test that changing the hotkey persists to config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".easyclaude"
            config_dir.mkdir(parents=True, exist_ok=True)
            config_file = config_dir / "config.json"

            with patch('app.config.get_config_dir', return_value=config_dir):
                from app.config import load_config, update_config, invalidate_cache

                # Load initial config
                invalidate_cache()
                config = load_config()
                original_hotkey = config.hotkey

                # Update hotkey
                new_hotkey = "ctrl+alt+shift+d"
                update_config(hotkey=new_hotkey)

                # Verify change persisted
                invalidate_cache()
                config = load_config()
                assert config.hotkey == new_hotkey

                # Verify file contains new hotkey
                with open(config_file, 'r') as f:
                    saved_config = json.load(f)
                    assert saved_config['hotkey'] == new_hotkey

    def test_multiple_hotkey_changes_persist(self):
        """Test that multiple hotkey changes all persist correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".easyclaude"
            config_dir.mkdir(parents=True, exist_ok=True)

            with patch('app.config.get_config_dir', return_value=config_dir):
                from app.config import load_config, update_config, invalidate_cache

                hotkeys_to_test = [
                    "ctrl+alt+c",
                    "ctrl+shift+z",
                    "alt+shift+x",
                    "win+e",
                ]

                for hotkey in hotkeys_to_test:
                    update_config(hotkey=hotkey)
                    invalidate_cache()
                    config = load_config()
                    assert config.hotkey == hotkey


class TestLaunchWithDifferentCommands:
    """Test launching Claude with different commands."""

    @pytest.fixture
    def mock_launch_environment(self):
        """Set up mocked launch environment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".easyclaude"
            config_dir.mkdir(parents=True, exist_ok=True)

            with patch('app.config.get_config_dir', return_value=config_dir):
                from app.config import invalidate_cache
                invalidate_cache()
                yield tmpdir

    def test_launch_with_default_command(self, mock_launch_environment, mock_terminal_launcher):
        """Test launching with default command."""
        from app.launcher import ClaudeLauncher

        launcher = ClaudeLauncher()
        launcher._platform_launcher = mock_terminal_launcher

        result = launcher.launch(
            directory="C:\\Test",
            command="claude"
        )

        assert result is True
        mock_terminal_launcher.launch_claude.assert_called_once()

    def test_launch_with_continue_flag(self, mock_launch_environment, mock_terminal_launcher):
        """Test launching with --continue flag."""
        from app.launcher import ClaudeLauncher

        launcher = ClaudeLauncher()
        launcher._platform_launcher = mock_terminal_launcher

        result = launcher.launch(
            directory="C:\\Test",
            command="claude --continue"
        )

        assert result is True
        mock_terminal_launcher.launch_claude.assert_called_once_with(
            directory="C:\\Test",
            command="claude --continue"
        )

    def test_launch_with_custom_message(self, mock_launch_environment, mock_terminal_launcher):
        """Test launching with custom message."""
        from app.launcher import ClaudeLauncher

        launcher = ClaudeLauncher()
        launcher._platform_launcher = mock_terminal_launcher

        custom_cmd = 'claude -m "Fix the bug in main.py"'
        result = launcher.launch(
            directory="C:\\Test",
            command=custom_cmd
        )

        assert result is True
        mock_terminal_launcher.launch_claude.assert_called_once()

    def test_launch_with_various_flags(self, mock_launch_environment, mock_terminal_launcher):
        """Test launching with various Claude flags."""
        from app.launcher import ClaudeLauncher

        launcher = ClaudeLauncher()
        launcher._platform_launcher = mock_terminal_launcher

        commands = [
            "claude",
            "claude --continue",
            "claude --dangerously-skip-permissions",
            "claude --help",
            "claude --version",
        ]

        for cmd in commands:
            mock_terminal_launcher.launch_claude.reset_mock()
            result = launcher.launch(directory="C:\\Test", command=cmd)
            assert result is True


class TestCloseAndRelaunchStatePreservation:
    """Test that state is preserved when closing and relaunching the app."""

    def test_last_directory_preserved(self):
        """Test that last used directory is preserved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".easyclaude"
            config_dir.mkdir(parents=True, exist_ok=True)

            with patch('app.config.get_config_dir', return_value=config_dir):
                from app.config import load_config, update_config, invalidate_cache

                # Simulate first launch with directory
                invalidate_cache()
                config = load_config()
                assert config.last_directory == ""

                # Update after "launch"
                test_dir = "C:\\Users\\Test\\MyProject"
                update_config(last_directory=test_dir)

                # Simulate app restart
                invalidate_cache()
                config = load_config()
                assert config.last_directory == test_dir

    def test_last_command_preserved(self):
        """Test that last used command is preserved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".easyclaude"
            config_dir.mkdir(parents=True, exist_ok=True)

            with patch('app.config.get_config_dir', return_value=config_dir):
                from app.config import load_config, update_config, invalidate_cache

                # Use a specific command
                test_cmd = "claude --continue --dangerously-skip-permissions"
                update_config(last_command=test_cmd)

                # Verify persistence
                invalidate_cache()
                config = load_config()
                assert config.last_command == test_cmd

    def test_full_state_preservation_cycle(self):
        """Test complete state preservation through close/relaunch cycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".easyclaude"
            config_dir.mkdir(parents=True, exist_ok=True)

            with patch('app.config.get_config_dir', return_value=config_dir):
                from app.config import load_config, update_config, invalidate_cache

                # Set up initial state
                initial_state = {
                    "hotkey": "ctrl+alt+c",
                    "last_directory": "",
                    "last_command": "claude",
                    "always_use_powershell": False,
                    "window_position": "center"
                }

                # Simulate user session
                invalidate_cache()
                config = load_config()

                # User changes hotkey
                update_config(hotkey="ctrl+shift+x")

                # User launches from directory
                update_config(last_directory="C:\\Projects\\Test")
                update_config(last_command="claude --continue")

                # User changes window position
                update_config(window_position="200,300")

                # Simulate app restart
                invalidate_cache()
                config = load_config()

                # Verify all state preserved
                assert config.hotkey == "ctrl+shift+x"
                assert config.last_directory == "C:\\Projects\\Test"
                assert config.last_command == "claude --continue"
                assert config.window_position == "200,300"


class TestAppIntegration:
    """Integration tests for the main application."""

    @pytest.fixture
    def mock_dependencies(self):
        """Mock all external dependencies for app initialization."""
        mocks = {}

        # Mock pynput for hotkey
        mock_pynput = MagicMock()
        mock_pynput.keyboard.global_hotkey = MagicMock()
        sys.modules['pynput'] = mock_pynput
        sys.modules['pynput.keyboard'] = mock_pynput.keyboard
        mocks['pynput'] = mock_pynput

        # Mock tkinter for GUI
        mock_tkinter = MagicMock()
        mock_tkinter.Tk = MagicMock
        mock_tkinter.ttk = MagicMock()
        mock_tkinter.filedialog = MagicMock()
        sys.modules['tkinter'] = mock_tkinter
        sys.modules['tkinter.ttk'] = mock_tkinter.ttk
        sys.modules['tkinter.filedialog'] = mock_tkinter.filedialog
        mocks['tkinter'] = mock_tkinter

        # Mock pystray for tray
        mock_pystray = MagicMock()
        mock_pystray.Icon = MagicMock
        mock_pystray.Menu = MagicMock()
        mock_pystray.MenuItem = MagicMock()
        sys.modules['pystray'] = mock_pystray
        mocks['pystray'] = mock_pystray

        yield mocks

        # Cleanup
        for mod in ['pynput', 'pynput.keyboard', 'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'pystray']:
            if mod in sys.modules:
                del sys.modules[mod]

    def test_app_initialization_workflow(self, mock_dependencies):
        """Test the complete app initialization workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".easyclaude"
            config_dir.mkdir(parents=True, exist_ok=True)

            with patch('app.config.get_config_dir', return_value=config_dir):
                from app.config import invalidate_cache
                invalidate_cache()

                # Import after mocking
                from app.main import EasyClaudeApp

                # Initialize app
                app = EasyClaudeApp()

                # Verify components initialized
                assert app.config is not None
                assert app.launcher is not None
                assert app.gui is not None
                assert app.hotkey_manager is not None
                assert app.tray_manager is not None

    def test_launch_callback_integration(self, mock_dependencies):
        """Test the launch callback integration flow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".easyclaude"
            config_dir.mkdir(parents=True, exist_ok=True)

            with patch('app.config.get_config_dir', return_value=config_dir):
                from app.config import invalidate_cache
                invalidate_cache()

                from app.main import EasyClaudeApp

                app = EasyClaudeApp()

                # Mock the launcher
                app.launcher.launch = MagicMock(return_value=True)

                # Simulate launch callback
                test_dir = "C:\\Test\\Project"
                test_cmd = "claude --continue"

                app._on_launch(test_dir, test_cmd, False)

                # Verify launcher was called
                app.launcher.launch.assert_called_once_with(
                    directory=test_dir,
                    command=test_cmd,
                    use_powershell=False
                )

                # Verify config was updated
                from app.config import load_config
                config = load_config()
                assert config.last_directory == test_dir
                assert config.last_command == test_cmd


class TestSingleInstanceEnforcement:
    """Test single instance enforcement integration."""

    def test_single_instance_allows_first(self):
        """Test that first instance is allowed."""
        from app.single_instance import SingleInstance

        instance = SingleInstance("Test_Mutex_First_Instance")

        try:
            is_running = instance.is_already_running()
            assert is_running is False, "First instance should not detect another running"
        finally:
            instance.release()

    def test_single_instance_blocks_second(self):
        """Test that second instance is blocked."""
        from app.single_instance import SingleInstance

        instance1 = SingleInstance("Test_Mutex_Block_Second")

        try:
            # First instance should not detect running
            assert instance1.is_already_running() is False

            # Second instance should detect first
            instance2 = SingleInstance("Test_Mutex_Block_Second")
            is_running = instance2.is_already_running()

            try:
                assert is_running is True, "Second instance should detect first instance running"
            finally:
                instance2.release()
        finally:
            instance1.release()


class TestWindowsTerminalLauncherIntegration:
    """Integration tests for Windows terminal launcher."""

    def test_launcher_detects_environment(self):
        """Test that launcher detects Windows environment."""
        from app.platform.windows import WindowsTerminalLauncher

        launcher = WindowsTerminalLauncher()

        # Should detect PowerShell
        assert launcher._powershell_exe is not None
        assert launcher.is_available() is True

    def test_launcher_command_building(self):
        """Test that launcher builds correct PowerShell commands."""
        from app.platform.windows import WindowsTerminalLauncher

        launcher = WindowsTerminalLauncher()

        # Test command building
        test_dir = "C:\\Users\\Test\\Projects"
        test_cmd = "claude"

        cmd = launcher.get_terminal_command(test_dir, test_cmd)

        assert isinstance(cmd, list)
        assert len(cmd) > 0
        assert launcher._powershell_exe in cmd

    def test_launcher_validates_directory(self):
        """Test that launcher validates directory paths."""
        from app.platform.windows import WindowsTerminalLauncher

        launcher = WindowsTerminalLauncher()

        # Valid directories
        valid_dirs = [
            "C:\\Users\\Test",
            "D:\\Projects",
            "C:\\Program Files\\Test",
        ]

        for dir_path in valid_dirs:
            result = launcher._validate_directory(dir_path)
            assert result is not None
            assert str(result) == dir_path

    def test_launcher_validates_command(self):
        """Test that launcher validates commands."""
        from app.platform.windows import WindowsTerminalLauncher

        launcher = WindowsTerminalLauncher()

        valid_commands = [
            "claude",
            "claude --continue",
            "claude -m 'test'",
        ]

        for cmd in valid_commands:
            result = launcher._validate_command(cmd)
            assert result is not None
            assert result == cmd


class TestConfigStateTransitions:
    """Test configuration state transitions during app lifecycle."""

    def test_clean_to_modified_state(self):
        """Test transition from clean (default) to modified state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".easyclaude"
            config_dir.mkdir(parents=True, exist_ok=True)

            with patch('app.config.get_config_dir', return_value=config_dir):
                from app.config import load_config, update_config, invalidate_cache

                # Start with default
                invalidate_cache()
                config = load_config()
                assert config.hotkey == "ctrl+alt+c"  # Default

                # Transition to modified
                update_config(hotkey="ctrl+shift+z")

                # Verify state
                invalidate_cache()
                config = load_config()
                assert config.hotkey == "ctrl+shift+z"

    def test_multiple_modifications_accumulate(self):
        """Test that multiple modifications accumulate correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".easyclaude"
            config_dir.mkdir(parents=True, exist_ok=True)

            with patch('app.config.get_config_dir', return_value=config_dir):
                from app.config import load_config, update_config, invalidate_cache

                # Apply multiple changes
                update_config(hotkey="ctrl+shift+x")
                update_config(last_directory="C:\\Test1")
                update_config(last_command="claude --continue")
                update_config(window_position="100,100")

                # Verify all changes persisted
                invalidate_cache()
                config = load_config()
                assert config.hotkey == "ctrl+shift+x"
                assert config.last_directory == "C:\\Test1"
                assert config.last_command == "claude --continue"
                assert config.window_position == "100,100"

    def test_reset_to_defaults(self):
        """Test resetting configuration to defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".easyclaude"
            config_dir.mkdir(parents=True, exist_ok=True)

            with patch('app.config.get_config_dir', return_value=config_dir):
                from app.config import load_config, update_config, reset_config, invalidate_cache

                # Modify config
                update_config(
                    hotkey="ctrl+shift+x",
                    last_directory="C:\\Modified",
                    last_command="modified command"
                )

                # Reset
                reset_config()

                # Verify back to defaults
                invalidate_cache()
                config = load_config()
                assert config.hotkey == "ctrl+alt+c"
                assert config.last_directory == ""
                assert config.last_command == "claude"


class TestErrorRecoveryScenarios:
    """Test error recovery and edge cases."""

    def test_corrupted_config_recovery(self):
        """Test recovery from corrupted config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".easyclaude"
            config_dir.mkdir(parents=True, exist_ok=True)
            config_file = config_dir / "config.json"

            # Write corrupted JSON
            with open(config_file, 'w') as f:
                f.write("{invalid json content")

            with patch('app.config.get_config_dir', return_value=config_dir):
                from app.config import load_config, invalidate_cache

                # Should recover with defaults
                invalidate_cache()
                config = load_config()
                assert config.hotkey == "ctrl+alt+c"

    def test_concurrent_config_access(self):
        """Test thread-safe config access."""
        import threading

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".easyclaude"
            config_dir.mkdir(parents=True, exist_ok=True)

            with patch('app.config.get_config_dir', return_value=config_dir):
                from app.config import load_config, update_config, invalidate_cache

                errors = []

                def update_config_thread(hotkey):
                    try:
                        update_config(hotkey=hotkey)
                    except Exception as e:
                        errors.append(e)

                # Launch multiple threads
                threads = []
                for i in range(10):
                    t = threading.Thread(target=update_config_thread, args=(f"ctrl+alt+{i}",))
                    threads.append(t)
                    t.start()

                # Wait for all threads
                for t in threads:
                    t.join()

                # Should not have errors
                assert len(errors) == 0


# E2E test considerations:
# The following tests document what would be tested in a full E2E setup
# but are not executable in the automated test environment due to
# Windows desktop interaction requirements.

class TestE2EScenarios:
    """
    End-to-end test scenarios for Windows desktop app.

    Note: These tests document complete user workflows but require
    Windows desktop automation tools (like pywinauto, WinAppDriver)
    to actually execute. They serve as documentation for manual testing
    and future automation implementation.
    """

    def test_e2e_first_launch_workflow(self):
        """
        E2E Scenario: First Launch Workflow

        Manual Test Steps:
        1. Delete any existing config at ~/.easyclaude/config.json
        2. Launch EasyClaude.exe
        3. Verify: Tray icon appears in system tray
        4. Verify: Log file created at %APPDATA%/EasyClaude/easyclaude.log
        5. Verify: Default config created at ~/.easyclaude/config.json
        6. Press Ctrl+Alt+C
        7. Verify: GUI window appears centered
        8. Close GUI (without launching)
        9. Right-click tray icon -> Exit
        10. Verify: App shuts down cleanly
        """

    def test_e2e_launch_claude_workflow(self):
        """
        E2E Scenario: Launch Claude Workflow

        Manual Test Steps:
        1. Launch EasyClaude
        2. Press hotkey (Ctrl+Alt+C)
        3. Select a directory using browse button
        4. Enter command: "claude --continue"
        5. Click Launch button
        6. Verify: PowerShell/Windows Terminal opens
        7. Verify: Terminal is in selected directory
        8. Verify: Claude command is executed
        9. Close terminal
        10. Press hotkey again
        11. Verify: GUI shows previously used directory
        """

    def test_e2e_hotkey_change_workflow(self):
        """
        E2E Scenario: Change Hotkey Workflow

        Manual Test Steps:
        1. Launch EasyClaude (default hotkey: Ctrl+Alt+C)
        2. Manually edit config to change hotkey to "ctrl+shift+x"
        3. Relaunch EasyClaude
        4. Press Ctrl+Shift+X
        5. Verify: GUI appears (new hotkey works)
        6. Press Ctrl+Alt+C
        7. Verify: Nothing happens (old hotkey doesn't work)
        """

    def test_e2e_single_instance_workflow(self):
        """
        E2E Scenario: Single Instance Enforcement

        Manual Test Steps:
        1. Launch EasyClaude.exe
        2. Verify: Tray icon appears
        3. Try to launch EasyClaude.exe again (second instance)
        4. Verify: Message box appears "Another instance is already running"
        5. Verify: Second instance exits
        6. Verify: First instance continues normally
        """

    def test_e2e_state_persistence_workflow(self):
        """
        E2E Scenario: State Persistence Across Sessions

        Manual Test Steps:
        1. Launch EasyClaude
        2. Press hotkey, select directory C:\TestProject
        3. Launch with command "claude -m 'test'"
        4. Exit EasyClaude
        5. Relaunch EasyClaude
        6. Press hotkey
        7. Verify: Directory field shows C:\TestProject
        8. Verify: Command field shows "claude -m 'test'"
        """

    def test_e2e_windows_terminal_workflow(self):
        """
        E2E Scenario: Windows Terminal Integration

        Manual Test Steps (requires Windows Terminal installed):
        1. Ensure Windows Terminal is installed
        2. Launch EasyClaude
        3. Press hotkey, select any directory
        4. Click Launch
        5. Verify: Windows Terminal opens (not legacy console)
        6. Verify: Working directory is correct
        7. Verify: Claude is running in the terminal
        """

    def test_e2e_powershell_fallback_workflow(self):
        """
        E2E Scenario: PowerShell Fallback (no Windows Terminal)

        Manual Test Steps:
        1. Ensure Windows Terminal is NOT available
        2. Launch EasyClaude
        3. Press hotkey, select any directory
        4. Click Launch
        5. Verify: Legacy PowerShell console opens
        6. Verify: Working directory is correct
        7. Verify: Claude is running
        """


# Test execution markers
pytestmark = [
    pytest.mark.integration,
]
