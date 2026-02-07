# EasyClaude Test Configuration
"""Shared pytest fixtures for EasyClaude tests."""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import MagicMock, Mock
import sys


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for config files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_config_file(temp_config_dir):
    """Create a temporary config file path."""
    config_path = Path(temp_config_dir) / "config.json"
    return str(config_path)


@pytest.fixture
def mock_subprocess():
    """Mock subprocess module."""
    from unittest.mock import MagicMock
    mock = MagicMock()
    sys.modules['subprocess'] = mock
    yield mock
    if 'subprocess' in sys.modules:
        del sys.modules['subprocess']


@pytest.fixture
def mock_pynput():
    """Mock pynput module."""
    from unittest.mock import MagicMock
    mock = MagicMock()
    sys.modules['pynput'] = mock
    sys.modules['pynput.keyboard'] = MagicMock()
    sys.modules['pynput.keyboard'].global_hotkey = MagicMock()
    sys.modules['pynput.keyboard'].key = MagicMock()
    sys.modules['pynput.keyboard'].KeyCode = MagicMock()
    yield mock
    for mod in ['pynput', 'pynput.keyboard']:
        if mod in sys.modules:
            del sys.modules[mod]


@pytest.fixture
def mock_tkinter():
    """Mock tkinter module."""
    from unittest.mock import MagicMock
    mock = MagicMock()
    sys.modules['tkinter'] = mock
    sys.modules['tkinter.ttk'] = MagicMock()
    sys.modules['tkinter.filedialog'] = MagicMock()
    yield mock
    for mod in ['tkinter', 'tkinter.ttk', 'tkinter.filedialog']:
        if mod in sys.modules:
            del sys.modules[mod]


@pytest.fixture
def mock_pystray():
    """Mock pystray module."""
    from unittest.mock import MagicMock
    mock = MagicMock()
    sys.modules['pystray'] = mock
    sys.modules['pystray'].Icon = MagicMock()
    sys.modules['pystray'].Menu = MagicMock()
    sys.modules['pystray'].MenuItem = MagicMock()
    yield mock
    if 'pystray' in sys.modules:
        del sys.modules['pystray']


@pytest.fixture
def mock_platform_module():
    """Mock platform module for OS detection."""
    from unittest.mock import MagicMock
    mock = MagicMock()
    sys.modules['platform'] = mock
    mock.system.return_value = 'Windows'
    yield mock
    if 'platform' in sys.modules:
        del sys.modules['platform']


@pytest.fixture
def sample_config_dict():
    """Sample configuration dictionary."""
    return {
        "hotkey": "ctrl+alt+c",
        "last_directory": "C:\\Users\\User\\Projects",
        "last_command": "claude",
        "always_use_powershell": False,
        "window_position": "center"
    }


@pytest.fixture
def sample_config_json():
    """Sample configuration JSON string."""
    return '''{
  "hotkey": "ctrl+alt+c",
  "last_directory": "C:\\\\Users\\\\User\\\\Projects",
  "last_command": "claude",
  "always_use_powershell": false,
  "window_position": "center"
}'''


@pytest.fixture
def mock_logger():
    """Mock logger fixture."""
    from unittest.mock import MagicMock
    mock_logger = MagicMock()
    mock_logger.info = MagicMock()
    mock_logger.debug = MagicMock()
    mock_logger.warning = MagicMock()
    mock_logger.error = MagicMock()
    mock_logger.exception = MagicMock()
    return mock_logger


@pytest.fixture
def mock_terminal_launcher():
    """Mock TerminalLauncher for testing."""
    from unittest.mock import MagicMock
    mock = MagicMock()
    mock.launch_claude = MagicMock()
    return mock


@pytest.fixture
def invalid_config_paths():
    """Fixture providing invalid config path scenarios."""
    return [
        "",  # Empty string
        None,  # None value
        "/nonexistent/path/config.json",  # Non-existent file
        "/root/no-permission/config.json",  # No permission path
    ]


@pytest.fixture
def invalid_config_data():
    """Fixture providing invalid JSON config data (truly invalid JSON syntax)."""
    return [
        "",  # Empty string
        "{",  # Incomplete JSON
        "not json at all",  # Not JSON
        "{invalid json}",  # Invalid JSON syntax
        '{"hotkey": "test", missing_close',  # Incomplete JSON object
    ]


@pytest.fixture
def valid_hotkeys():
    """Fixture providing valid hotkey combinations."""
    return [
        "ctrl+alt+c",
        "ctrl+shift+a",
        "alt+shift+z",
        "ctrl+c",
        "alt+f4",
        "win+e",
        "cmd+space",
        "ctrl+alt+shift+d",
    ]


@pytest.fixture
def invalid_hotkeys():
    """Fixture providing invalid hotkey combinations."""
    return [
        "",  # Empty
        "just_text",  # No modifiers
        "ctrl+",  # Trailing modifier
        "+c",  # Leading modifier
        "invalid_mod+c",  # Invalid modifier
        "ctrl+invalid_key+",  # Invalid key
        "ctrl++",  # Double modifier
    ]


@pytest.fixture
def sample_directories():
    """Fixture providing sample directory paths."""
    return [
        "C:\\Users\\User\\Projects",
        "D:\\Development\\MyApp",
        "C:\\Projects\\Python\\test",
        "/home/user/projects",  # Linux style
        "~/Documents",
    ]


@pytest.fixture
def claude_commands():
    """Fixture providing Claude command variations."""
    return [
        "claude",
        "claude --continue",
        "claude --dangerously-skip-permissions",
        "claude --help",
        "claude --version",
        "claude -m 'Fix bug in main.py'",
    ]


@pytest.fixture(autouse=True)
def reset_sys_modules():
    """Reset sys.modules after each test to clean up mocks."""
    yield
    # Clean up any mocked modules
    modules_to_remove = [
        'pynput', 'pynput.keyboard',
        'tkinter', 'tkinter.ttk', 'tkinter.filedialog',
        'pystray', 'platform', 'subprocess'
    ]
    for mod in modules_to_remove:
        if mod in sys.modules and hasattr(sys.modules[mod], '_is_mock'):
            del sys.modules[mod]
