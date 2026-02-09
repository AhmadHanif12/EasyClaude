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


@pytest.fixture
def linux_directories():
    """Fixture providing Linux-style directory paths."""
    return [
        "/home/user/projects",
        "/home/user/my project",
        "/home/user/project(2024)",
        "/var/www/html",
        "/opt/application",
        "~/Documents",
        "~/projects",
        "/tmp/test project",
    ]


@pytest.fixture
def linux_terminals():
    """Fixture providing available Linux terminals."""
    return [
        "gnome-terminal",
        "konsole",
        "xfce4-terminal",
        "mate-terminal",
        "lxterminal",
        "x-terminal-emulator",
        "xterm",
    ]


@pytest.fixture
def linux_shells():
    """Fixture providing common Linux shells."""
    return ["bash", "zsh", "fish"]


@pytest.fixture
def mock_linux_environment():
    """Fixture that mocks Linux environment."""
    import platform
    original_platform = platform.system
    platform.system = lambda: "Linux"
    yield
    platform.system = original_platform


@pytest.fixture
def mock_shutil_which():
    """Mock shutil.which for terminal detection testing."""
    import shutil
    original_which = shutil.which

    def mock_which(cmd):
        # Simulate common terminals being available
        available = ["gnome-terminal", "xterm"]
        return cmd if cmd in available else None

    shutil.which = mock_which
    yield shutil.which
    shutil.which = original_which


@pytest.fixture
def linux_desktop_environments():
    """Fixture providing Linux desktop environment test data."""
    return {
        "GNOME": {
            "env_var": "XDG_CURRENT_DESKTOP",
            "env_value": "ubuntu:GNOME",
            "terminals": ["gnome-terminal"],
        },
        "KDE": {
            "env_var": "XDG_CURRENT_DESKTOP",
            "env_value": "KDE",
            "terminals": ["konsole"],
        },
        "XFCE": {
            "env_var": "XDG_CURRENT_DESKTOP",
            "env_value": "XFCE",
            "terminals": ["xfce4-terminal"],
        },
        "Cinnamon": {
            "env_var": "XDG_CURRENT_DESKTOP",
            "env_value": "X-Cinnamon",
            "terminals": ["gnome-terminal"],
        },
    }


@pytest.fixture
def sample_linux_config():
    """Sample Linux configuration dictionary."""
    return {
        "hotkey": "ctrl+alt+c",
        "last_directory": "/home/user/projects",
        "last_command": "claude",
        "terminal_preference": "gnome-terminal",
        "window_position": "center",
        "autostart_enabled": False,
    }


@pytest.fixture
def linux_xdg_paths():
    """Fixture providing XDG base directory paths."""
    import os
    from pathlib import Path

    home = Path.home()
    return {
        "config_home": Path(os.environ.get("XDG_CONFIG_HOME", home / ".config")),
        "data_home": Path(os.environ.get("XDG_DATA_HOME", home / ".local/share")),
        "cache_home": Path(os.environ.get("XDG_CACHE_HOME", home / ".cache")),
        "state_home": Path(os.environ.get("XDG_STATE_HOME", home / ".local/state")),
        "autostart": Path(os.environ.get("XDG_CONFIG_HOME", home / ".config")) / "autostart",
    }


@pytest.fixture
def linux_test_directories():
    """Fixture creating temporary test directory structure for Linux."""
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)

        # Create test directory structure
        test_dirs = [
            base / "normal_project",
            base / "project with spaces",
            base / "project-with-dashes",
            base / "project_with_underscores",
            base / "project(2024)",
            base / "café_project",
            base / ".hidden_project",
            base / "very" / "deep" / "nested" / "path" / "project",
        ]

        for directory in test_dirs:
            directory.mkdir(parents=True, exist_ok=True)

        yield base


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


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "linux: marks tests as Linux-specific")
    config.addinivalue_line("markers", "skip_linux: skip tests on Linux")
    config.addinivalue_line("markers", "gnome: marks tests for GNOME desktop")
    config.addinivalue_line("markers", "kde: marks tests for KDE desktop")
    config.addinivalue_line("markers", "xfce: marks tests for XFCE desktop")
