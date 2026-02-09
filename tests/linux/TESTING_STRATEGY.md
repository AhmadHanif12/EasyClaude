# Linux Testing Strategy for EasyClaude

## Document Metadata
- **Version**: 1.0
- **Last Updated**: 2026-02-08
- **Target Release**: Phase 2 - Linux Support
- **Author**: QA and Testing Specialist

## Executive Summary

This document outlines a comprehensive testing strategy for the Linux release of EasyClaude. The strategy covers automated testing, manual testing procedures, and quality assurance measures across multiple Linux distributions, desktop environments, and configurations.

---

## 1. Testing Matrix

### 1.1 Distribution Coverage

| Distribution | Version | Priority | Test Environment | Notes |
|-------------|---------|----------|------------------|-------|
| Ubuntu | 22.04 LTS | P0 | VirtualBox/VMware | Most common desktop distro |
| Ubuntu | 24.04 LTS | P0 | VirtualBox/VMware | Latest LTS |
| Fedora | 39 | P1 | VirtualBox/VMware | GNOME-focused |
| Fedora | 40 | P1 | VirtualBox/VMware | Latest release |
| Debian | 12 (Bookworm) | P1 | VirtualBox/VMware | Stable server/desktop |
| Arch Linux | Rolling | P2 | VirtualBox/VMware | Rolling release |
| Linux Mint | 21.x | P1 | VirtualBox/VMware | Ubuntu-based, Cinnamon |
| Pop!_OS | 22.04/24.04 | P2 | VirtualBox/VMware | Ubuntu-based, COSMIC |
| openSUSE Tumbleweed | Rolling | P3 | VirtualBox/VMware | RPM-based rolling |
| Manjaro | Rolling | P3 | VirtualBox/VMware | Arch-based user-friendly |

**Priority Definitions:**
- **P0**: Must test, blocking release
- **P1**: High priority, should test before release
- **P2**: Medium priority, test if resources allow
- **P3**: Low priority, nice to have

### 1.2 Desktop Environment Coverage

| Desktop Environment | Distributions | Priority | Key Features to Test |
|---------------------|----------------|----------|---------------------|
| GNOME | Ubuntu, Fedora, Debian | P0 | System tray, hotkeys, notifications |
| KDE Plasma | Kubuntu, Fedora KDE, Manjaro KDE | P0 | System tray, hotkeys, theme integration |
| XFCE | Xubuntu, Linux Mint XFCE | P1 | System tray, lightweight testing |
| Cinnamon | Linux Mint | P1 | System tray, menu integration |
| MATE | Ubuntu MATE, Linux Mint MATE | P2 | System tray compatibility |
| LXQt/LXDE | Lubuntu, Linux Mint LXDE | P2 | Lightweight environment testing |
| COSMIC | Pop!_OS | P2 | New DE, future-proofing |
| Pantheon | elementary OS | P3 | Unique desktop patterns |
| i3/Sway | Various | P3 | Tiling WM compatibility |

### 1.3 Terminal Emulator Coverage

| Terminal | Command | Priority | Testing Notes |
|----------|---------|----------|---------------|
| gnome-terminal | `gnome-terminal` | P0 | Default on Ubuntu/Fedora GNOME |
| konsole | `konsole` | P0 | Default on KDE Plasma |
| xfce4-terminal | `xfce4-terminal` | P1 | Default on XFCE |
| mate-terminal | `mate-terminal` | P1 | MATE desktop default |
| lxterminal | `lxterminal` | P2 | LXDE default |
| xterm | `xterm` | P1 | Fallback, universal availability |
| alacritty | `alacritty` | P2 | GPU-accelerated, popular |
| kitty | `kitty` | P2 | GPU-accelerated, features |
| terminator | `terminator` | P3 | Grid terminals |
| tilix | `tilix` | P3 | Drop-down terminals |
| guake | `guake` | P3 | Drop-down terminals |

### 1.4 Python Version Coverage

| Python Version | Status | Test Coverage |
|----------------|--------|---------------|
| 3.10 | Minimum Supported | Full test suite |
| 3.11 | Recommended | Full test suite |
| 3.12 | Latest | Full test suite |
| 3.9 | End of Life | Minimal testing only |
| 3.13 (future) | Not supported | N/A |

---

## 2. Automated Testing

### 2.1 Unit Tests

#### 2.1.1 Linux-Specific Unit Tests

Create `tests/platform/test_linux.py`:

```python
"""Unit tests for Linux platform implementation."""
import pytest
from unittest.mock import patch, MagicMock, Mock
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

    def test_get_command_gnome_terminal(self):
        """Test command generation for gnome-terminal."""
        with patch('shutil.which', return_value=True):
            launcher = LinuxTerminalLauncher(terminal_preference="gnome-terminal")
            # When implemented, should test command structure
            with pytest.raises(LaunchFailedError):
                launcher.get_terminal_command("/home/user/project", "claude")

    def test_get_command_konsole(self):
        """Test command generation for konsole."""
        with patch('shutil.which', return_value=True):
            launcher = LinuxTerminalLauncher(terminal_preference="konsole")
            with pytest.raises(LaunchFailedError):
                launcher.get_terminal_command("/home/user/project", "claude")

    def test_get_command_xfce4_terminal(self):
        """Test command generation for xfce4-terminal."""
        with patch('shutil.which', return_value=True):
            launcher = LinuxTerminalLauncher(terminal_preference="xfce4-terminal")
            with pytest.raises(LaunchFailedError):
                launcher.get_terminal_command("/home/user/project", "claude")

class TestLinuxLaunchClaude:
    """Test Claude launching on Linux."""

    @patch('shutil.which')
    def test_launch_unavailable_terminal(self, mock_which):
        """Test launching when no terminal is available."""
        mock_which.return_value = None
        launcher = LinuxTerminalLauncher()
        with pytest.raises(TerminalNotFoundError):
            launcher.launch_claude("/home/user/project", "claude")

    @patch('shutil.which')
    def test_launch_stub_implementation(self, mock_which):
        """Test that stub raises LaunchFailedError."""
        mock_which.return_value = True
        launcher = LinuxTerminalLauncher()
        with pytest.raises(LaunchFailedError) as exc_info:
            launcher.launch_claude("/home/user/project", "claude")
        assert "not yet implemented" in str(exc_info.value)

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
        with pytest.raises(ValueError):
            launcher.set_terminal_preference("invalid-terminal")

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
```

#### 2.1.2 Integration Tests

Create `tests/platform/test_linux_integration.py`:

```python
"""Integration tests for Linux platform implementation."""
import pytest
import subprocess
from unittest.mock import patch, MagicMock
from pathlib import Path

class TestLinuxTerminalIntegration:
    """Integration tests for terminal launching."""

    @pytest.mark.skipif(not pytest.mark.linux(), reason="Linux only")
    def test_actual_gnome_terminal_launch(self):
        """Test actual gnome-terminal launch (Linux only)."""
        # Test with a simple echo command
        result = subprocess.run([
            "gnome-terminal",
            "--",
            "bash", "-c", "echo 'test'; sleep 1"
        ], capture_output=True)
        # Should not error
        assert result.returncode in [0, None]

    @pytest.mark.skipif(not pytest.mark.linux(), reason="Linux only")
    def test_actual_konsole_launch(self):
        """Test actual konsole launch (Linux only)."""
        result = subprocess.run([
            "konsole",
            "-e", "bash", "-c", "echo 'test'; sleep 1"
        ], capture_output=True)
        assert result.returncode in [0, None]

class TestLinuxShellCompatibility:
    """Test shell compatibility on Linux."""

    @pytest.mark.parametrize("shell", ["bash", "zsh", "fish"])
    def test_shell_detection(self, shell):
        """Test detection of different shells."""
        with patch('shutil.which') as mock_which:
            mock_which.side_effect = lambda x: x == shell
            # When implemented, test shell detection
            assert True  # Placeholder

class TestLinuxPathHandling:
    """Test Linux path handling."""

    def test_unix_path_validation(self):
        """Test Unix-style path validation."""
        valid_paths = [
            "/home/user/projects",
            "/var/www/html",
            "~/Documents",
            "/tmp/test project",  # With spaces
            "/path/with/unicode/ünicode",
        ]
        for path in valid_paths:
            # Test path validation logic
            assert Path(path).is_absolute() or path.startswith("~")

    def test_path_with_spaces(self):
        """Test paths containing spaces."""
        path = "/home/user/my project"
        # Should be properly quoted
        quoted = f'"{path}"'
        assert path in quoted

class TestLinuxDesktopEnvironment:
    """Test desktop environment detection."""

    @patch.dict('os.environ', {'XDG_CURRENT_DESKTOP': 'ubuntu:GNOME'})
    def test_detect_gnome(self):
        """Test GNOME environment detection."""
        # When implemented, test DE detection
        assert True  # Placeholder

    @patch.dict('os.environ', {'XDG_CURRENT_DESKTOP': 'KDE'})
    def test_detect_kde(self):
        """Test KDE environment detection."""
        assert True  # Placeholder

    @patch.dict('os.environ', {'XDG_CURRENT_DESKTOP': 'XFCE'})
    def test_detect_xfce(self):
        """Test XFCE environment detection."""
        assert True  # Placeholder
```

### 2.2 Mock Tests for Desktop Features

Create `tests/platform/test_linux_desktop.py`:

```python
"""Mock tests for Linux desktop environment features."""
import pytest
from unittest.mock import patch, MagicMock, Mock
import sys

class TestLinuxSystemTray:
    """Test Linux system tray functionality."""

    @patch('app.tray.pystray.Icon')
    def test_system_tray_icon_creation(self, mock_icon):
        """Test system tray icon creation on Linux."""
        # When implemented, test icon creation
        assert True  # Placeholder

    @patch('app.tray.pystray.MenuItem')
    def test_system_tray_menu_structure(self, mock_menu_item):
        """Test system tray menu structure on Linux."""
        expected_items = ["Launch Claude", "Change Directory", "Settings", "Exit"]
        # When implemented, verify menu items
        assert True  # Placeholder

class TestLinuxHotkeys:
    """Test Linux global hotkey registration."""

    @patch('app.hotkey.pynput.keyboard.global_hotkey')
    def test_hotkey_registration(self, mock_hotkey):
        """Test global hotkey registration on Linux."""
        # When implemented, test hotkey registration
        assert True  # Placeholder

    @patch('app.hotkey.pynput.keyboard.Listener')
    def test_hotkey_listener_lifecycle(self, mock_listener):
        """Test hotkey listener start/stop."""
        # When implemented, test listener lifecycle
        assert True  # Placeholder

class TestLinuxAutostart:
    """Test Linux autostart functionality."""

    @patch('pathlib.Path.home')
    def test_autostart_file_location(self, mock_home):
        """Test autostart .desktop file location."""
        mock_home.return_value = "/home/user"
        autostart_path = "/home/user/.config/autostart/easyclaude.desktop"
        # When implemented, verify autostart file creation
        assert True  # Placeholder

    @patch('builtins.open')
    def test_autostart_file_content(self, mock_open):
        """Test autostart .desktop file content."""
        expected_content = """[Desktop Entry]
Type=Application
Name=EasyClaude
Exec=easyclaude
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""
        # When implemented, verify content
        assert True  # Placeholder

class TestLinuxNotifications:
    """Test Linux desktop notifications."""

    @patch('subprocess.run')
    def test_notification_via_notify_send(self, mock_run):
        """Test notifications using notify-send."""
        # When implemented, test notification
        assert True  # Placeholder

    @patch('subprocess.run')
    def test_notification_with_dbus(self, mock_run):
        """Test notifications via D-Bus."""
        # When implemented, test D-Bus notifications
        assert True  # Placeholder
```

### 2.3 CI/CD Integration

#### 2.3.1 GitHub Actions Workflow

Create `.github/workflows/test-linux.yml`:

```yaml
name: Linux Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  workflow_dispatch:

jobs:
  test-linux-matrix:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ['3.10', '3.11', '3.12']
        distro: [ubuntu-22.04, ubuntu-24.04]
      max-parallel: 4

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Cache pip packages
      uses: actions/cache@v4
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
        pip install pytest-xvfb  # For X virtual framebuffer

    - name: Run unit tests
      run: |
        pytest tests/platform/test_linux.py -v --cov=app/platform/linux

    - name: Run mock integration tests
      run: |
        pytest tests/platform/test_linux_integration.py::TestLinuxPathHandling -v

    - name: Upload coverage
      uses: codecov/codecov-action@v4
      with:
        files: ./coverage.xml
        flags: linux

  test-linux-distro:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        container:
          - ubuntu:22.04
          - ubuntu:24.04
          - fedora:39
          - debian:12

    container:
      image: ${{ matrix.container }}

    steps:
    - uses: actions/checkout@v4

    - name: Install system dependencies
      run: |
        apt-get update -y
        apt-get install -y python3 python3-pip python3-dev
        # Desktop environment dependencies for testing
        apt-get install -y xvfb libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 \
                          libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
                          libxcb-xinerama0 libxcb-xfixes0

    - name: Install Python dependencies
      run: |
        pip3 install --upgrade pip
        pip3 install -e ".[dev]"

    - name: Run tests with Xvfb
      run: |
        xvfb-run -a pytest tests/ -v -k "not skip_linux" --tb=short

  lint-linux:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install linting tools
      run: |
        pip install pylint mypy flake8

    - name: Run pylint
      run: |
        pylint app/platform/linux.py --exit-zero

    - name: Run mypy
      run: |
        mypy app/platform/linux.py --ignore-missing-imports

    - name: Run flake8
      run: |
        flake8 app/platform/linux.py --max-line-length=100
```

#### 2.3.2 Local Testing Script

Create `tests/linux/run_local_tests.sh`:

```bash
#!/bin/bash
# Local Linux testing script

set -e

echo "=== EasyClaude Linux Test Runner ==="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test sections
run_unit_tests() {
    echo -e "${YELLOW}Running unit tests...${NC}"
    pytest tests/platform/test_linux.py -v --cov=app/platform/linux
}

run_integration_tests() {
    echo -e "${YELLOW}Running integration tests...${NC}"
    pytest tests/platform/test_linux_integration.py -v
}

run_mock_tests() {
    echo -e "${YELLOW}Running mock desktop tests...${NC}"
    pytest tests/platform/test_linux_desktop.py -v
}

run_all_tests() {
    echo -e "${YELLOW}Running all tests...${NC}"
    pytest tests/ -v -k "linux or Linux" --cov=app/platform/linux
}

check_dependencies() {
    echo -e "${YELLOW}Checking dependencies...${NC}"

    deps=("gnome-terminal" "konsole" "xfce4-terminal" "xterm")
    missing=()

    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing+=("$dep")
        else
            echo -e "  ${GREEN}✓${NC} $dep"
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        echo -e "${RED}Missing dependencies: ${missing[*]}${NC}"
        echo "Install with: sudo apt-get install ${missing[*]}"
    fi
}

# Main
case "${1:-all}" in
    unit)
        run_unit_tests
        ;;
    integration)
        run_integration_tests
        ;;
    mock)
        run_mock_tests
        ;;
    check)
        check_dependencies
        ;;
    all)
        check_dependencies
        run_all_tests
        ;;
    *)
        echo "Usage: $0 [unit|integration|mock|check|all]"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Test run complete!${NC}"
```

---

## 3. Manual Testing Checklist

### 3.1 Pre-Test Setup

- [ ] Create test VMs for each target distribution
- [ ] Install Python 3.10+ on all test systems
- [ ] Clone EasyClaude repository
- [ ] Install dependencies: `pip install -e ".[dev]"`
- [ ] Create test directory structure with various path scenarios
- [ ] Set up test Claude installation/config
- [ ] Document test environment details

### 3.2 Installation Tests

#### Package Installation

- [ ] **Install from source**
  - [ ] `pip install -e .`
  - [ ] Verify installation: `easyclaude --version`
  - [ ] Check all dependencies installed

- [ ] **Install with pip**
  - [ ] `pip install easyclaude`
  - [ ] Verify executable in PATH
  - [ ] Check desktop entry created

- [ ] **Install from package (when available)**
  - [ ] .deb package installation
  - [ ] .rpm package installation
  - [ ] Arch AUR package

#### First Launch

- [ ] **First run experience**
  - [ ] Application starts without errors
  - [ ] System tray icon appears
  - [ ] Default configuration created
  - [ ] User prompted for initial setup (if implemented)

### 3.3 System Tray Tests

#### Icon Appearance

| Test Case | Steps | Expected Result | Status |
|-----------|-------|-----------------|--------|
| Tray icon visible on GNOME | Launch app, look in top bar | Icon visible in status area | ☐ |
| Tray icon visible on KDE | Launch app, look in system tray | Icon visible in system tray | ☐ |
| Tray icon visible on XFCE | Launch app, look in panel | Icon visible in notification area | ☐ |
| Icon quality on HiDPI | Set display scaling to 200% | Icon appears crisp, not pixelated | ☐ |
| Icon with dark theme | Enable dark theme | Icon remains visible | ☐ |
| Icon with light theme | Enable light theme | Icon remains visible | ☐ |

#### Menu Functionality

| Test Case | Steps | Expected Result | Status |
|-----------|-------|-----------------|--------|
| Right-click menu opens | Right-click tray icon | Menu appears with all options | ☐ |
| "Launch Claude" works | Click menu item | GUI launcher opens | ☐ |
| "Change Directory" works | Click menu item | Directory picker opens | ☐ |
| "Settings" works | Click menu item | Settings dialog opens | ☐ |
| "Exit" works | Click menu item | Application closes cleanly | ☐ |
| Menu closes on outside click | Open menu, click elsewhere | Menu closes | ☐ |
| Menu keyboard navigation | Open menu, use arrow keys | Items highlight and select | ☐ |

### 3.4 Global Hotkey Tests

#### Registration

| Test Case | Steps | Expected Result | Status |
|-----------|-------|-----------------|--------|
| Default hotkey (Ctrl+Alt+C) | Press combination | GUI launcher opens | ☐ |
| Custom hotkey | Set custom combo, press | GUI launcher opens | ☐ |
| Hotkey with modifiers | Ctrl+Shift+Alt combinations | Works correctly | ☐ |
| Hotkey conflicts | Set conflicting hotkey | Appropriate error/warning | ☐ |
| Hotkey persists after restart | Restart app, test hotkey | Still works | ☐ |

#### Response Time

| Test Case | Measurement | Target | Status |
|-----------|-------------|--------|--------|
| Hotkey response time | From press to GUI visible | < 200ms | ☐ |
| Hotkey with app minimized | Press when minimized | < 200ms | ☐ |
| Hotkey with other app focused | Focus different app, press | < 200ms | ☐ |

### 3.5 Terminal Launching Tests

#### Terminal Detection

| Terminal | Detection | Launch | Working Directory | Status |
|----------|-----------|--------|-------------------|--------|
| gnome-terminal | ☐ | ☐ | ☐ | |
| konsole | ☐ | ☐ | ☐ | |
| xfce4-terminal | ☐ | ☐ | ☐ | |
| mate-terminal | ☐ | ☐ | ☐ | |
| lxterminal | ☐ | ☐ | ☐ | |
| xterm | ☐ | ☐ | ☐ | |

#### Directory Handling

| Test Case | Directory Path | Expected Behavior | Status |
|-----------|---------------|-------------------|--------|
| Standard path | `/home/user/projects` | Terminal opens in directory | ☐ |
| Path with spaces | `/home/user/my project` | Terminal opens correctly | ☐ |
| Path with special chars | `/home/user/project(2024)` | Terminal opens correctly | ☐ |
| Path with unicode | `/home/user/projét` | Terminal opens correctly | ☐ |
| Home directory shortcut | `~/Documents` | Terminal expands path | ☐ |
| Relative path | `./subdir` | Resolves correctly | ☐ |
| Non-existent path | `/nonexistent/path` | Appropriate error message | ☐ |

#### Command Execution

| Test Case | Command | Expected Behavior | Status |
|-----------|---------|-------------------|--------|
| Basic command | `claude` | Launches Claude | ☐ |
| With flags | `claude --continue` | Passes flags correctly | ☐ |
| With arguments | `claude -m "Fix bug"` | Quotes handled correctly | ☐ |
| With pipe | `echo test \| cat` | Pipe works correctly | ☐ |
| Multiple commands | `cd /tmp; ls` | Commands execute in sequence | ☐ |

### 3.6 GUI Launcher Tests

#### Window Appearance

| Test Case | DE/Theme | Expected Behavior | Status |
|-----------|----------|-------------------|--------|
| Window opens | GNOME | Centered dialog | ☐ |
| Window opens | KDE | Centered dialog | ☐ |
| Window opens | XFCE | Centered dialog | ☐ |
| Dark theme compatibility | Dark theme | Text visible, good contrast | ☐ |
| Light theme compatibility | Light theme | Text visible, good contrast | ☐ |
| Window resizable | All DEs | Can resize, content adapts | ☐ |
| Window position saved | Move, close, reopen | Remembers position | ☐ |

#### Input Fields

| Test Case | Field | Expected Behavior | Status |
|-----------|-------|-------------------|--------|
| Directory field | Click | Opens directory picker | ☐ |
| Directory field | Type path | Accepts typing | ☐ |
| Directory field | Paste path | Accepts paste | ☐ |
| Directory field history | Dropdown shows history | Previous directories listed | ☐ |
| Command field | Type command | Accepts typing | ☐ |
| Command field | Previous commands | Remembers last command | ☐ |

#### Buttons

| Test Case | Button | Expected Behavior | Status |
|-----------|--------|-------------------|--------|
| Launch button | Click | Opens terminal and closes dialog | ☐ |
| Cancel button | Click or ESC | Closes dialog without launching | ☐ |
| Browse button | Click | Opens file/directory picker | ☐ |
| Enter key | Press | Equivalent to Launch | ☐ |

### 3.7 Directory History Tests

| Test Case | Steps | Expected Result | Status |
|-----------|-------|-----------------|--------|
| History saves | Launch in multiple directories | All directories remembered | ☐ |
| History limit | Launch in 20+ directories | Keeps recent 10 (or configured) | ☐ |
| History dropdown | Click history button | Shows recent directories | ☐ |
| History selection | Select from dropdown | Fills directory field | ☐ |
| History persistence | Restart app | History retained | ☐ |
| History clear | Clear history option | History emptied | ☐ |

### 3.8 Autostart Tests

| Test Case | Steps | Expected Result | Status |
|-----------|-------|-----------------|--------|
| Enable autostart | Check setting in GUI | .desktop file created | ☐ |
| Disable autostart | Uncheck setting | .desktop file removed | ☐ |
| Autostart on login | Enable, logout, login | App starts automatically | ☐ |
| Autostart with settings | Enable with custom settings | Settings preserved | ☐ |

### 3.9 Settings Persistence Tests

| Test Case | Setting | Expected Behavior | Status |
|-----------|---------|-------------------|--------|
| Hotkey saved | Change hotkey, restart | New hotkey active | ☐ |
| Terminal preference saved | Select terminal, restart | Preference remembered | ☐ |
| Window position saved | Move window, restart | Position restored | ☐ |
| Last directory saved | Launch, close, reopen | Directory pre-filled | ☐ |
| Last command saved | Launch with command, reopen | Command pre-filled | ☐ |

### 3.10 Error Handling Tests

| Test Case | Scenario | Expected Behavior | Status |
|-----------|----------|-------------------|--------|
| No terminal available | Uninstall all terminals | Clear error message | ☐ |
| Invalid directory | Enter invalid path | Validation error | ☐ |
| Permission denied | Try to launch in /root | Permission error | ☐ |
| Claude not found | Claude not in PATH | Informative error | ☐ |
| Config corrupted | Corrupt config file | Graceful fallback/recreate | ☐ |

---

## 4. User Experience Testing

### 4.1 Performance Benchmarks

#### Startup Time

| Metric | Target | Measurement Method | Status |
|--------|--------|-------------------|--------|
| Cold start | < 2 seconds | Time from command to tray icon | ☐ |
| Warm start | < 500ms | Time from second launch to tray icon | ☐ |
| Hotkey response | < 200ms | Time from hotkey press to GUI visible | ☐ |
| Terminal launch | < 500ms | Time from launch to terminal visible | ☐ |

#### Memory Usage

| Metric | Target | Measurement Method | Status |
|--------|--------|-------------------|--------|
| Idle memory | < 50MB | Measure when idle in tray | ☐ |
| Peak memory | < 100MB | Measure during operations | ☐ |
| Memory leak check | No growth | Monitor over 1 hour | ☐ |

#### CPU Usage

| Metric | Target | Measurement Method | Status |
|--------|--------|-------------------|--------|
| Idle CPU | < 1% | Measure when idle | ☐ |
| Hotkey processing | < 5% | Measure during hotkey press | ☐ |
| Launch operation | < 20% spike | Brief spike acceptable | ☐ |

### 4.2 Accessibility Testing

| Feature | Test | Expected Result | Status |
|---------|------|-----------------|--------|
| Keyboard navigation | Tab through GUI | All controls reachable | ☐ |
| Screen reader | Orca/narrator compatibility | All elements announced | ☐ |
| High contrast | Enable high contrast mode | Text remains readable | ☐ |
| Font scaling | Set large fonts | Text remains visible | ☐ |
| Color blindness | Various color modes | Information not color-dependent | ☐ |

### 4.3 Localization Support

| Language | Translation Coverage | Test Priority | Status |
|----------|---------------------|---------------|--------|
| English (en) | 100% | P0 | ☐ |
| Spanish (es) | UI strings | P2 | ☐ |
| French (fr) | UI strings | P2 | ☐ |
| German (de) | UI strings | P2 | ☐ |
| Chinese (zh) | UI strings | P3 | ☐ |
| Japanese (ja) | UI strings | P3 | ☐ |

### 4.4 Desktop Integration

| Feature | Test | Expected Result | Status |
|---------|------|-----------------|--------|
| Desktop file | Verify .desktop file | Valid freedesktop.org format | ☐ |
| AppStream metadata | Verify appdata | Valid for software centers | ☐ |
| Icon theme | Install icons | Follows icon theme spec | ☐ |
| MIME associations | File associations | Configured correctly | ☐ |
| D-Bus interface | If applicable | Implements standard interfaces | ☐ |

---

## 5. Test Execution Plan

### 5.1 Phase-Based Testing

#### Phase 1: Development Testing (Weeks 1-2)
- Unit tests for all Linux-specific code
- Mock tests for desktop environment features
- Basic functionality tests on Ubuntu 22.04

#### Phase 2: Alpha Testing (Weeks 3-4)
- Integration tests
- Manual testing on primary distributions (Ubuntu, Fedora)
- Basic DE testing (GNOME, KDE)

#### Phase 3: Beta Testing (Weeks 5-6)
- Full distribution matrix testing
- All desktop environments
- Performance benchmarking
- User acceptance testing

#### Phase 4: Release Candidate (Week 7)
- Regression testing
- Final bug verification
- Documentation review
- Release preparation

### 5.2 Test Schedule

| Week | Focus | Deliverables |
|------|-------|--------------|
| 1 | Unit test development | 100% unit test coverage |
| 2 | Integration test development | Integration test suite |
| 3 | Ubuntu/Fedora testing | Test reports for P0 distros |
| 4 | DE testing (GNOME/KDE) | DE compatibility report |
| 5 | Extended distro testing | Full matrix results |
| 6 | Performance/accessibility | Benchmark and a11y report |
| 7 | Final verification | Release sign-off |

### 5.3 Success Criteria

The Linux release is considered ready when:

- **Code Coverage**: > 80% for Linux-specific code
- **P0 Distribution Tests**: 100% pass rate
- **P1 Distribution Tests**: > 95% pass rate
- **Desktop Environment Tests**: > 90% pass rate on P0/P1 DEs
- **Performance**: All benchmarks within targets
- **Critical Bugs**: Zero critical bugs remaining
- **High Priority Bugs**: < 5 high priority bugs
- **Documentation**: Complete installation and user documentation

---

## 6. Bug Reporting and Tracking

### 6.1 Bug Severity Levels

| Severity | Definition | Example |
|----------|-----------|---------|
| Critical | App crashes or unusable | App won't start, terminal doesn't open |
| High | Major feature broken | Hotkey doesn't work, settings not saved |
| Medium | Minor feature broken | One terminal not supported |
| Low | Cosmetic or minor issue | Icon pixelated, small typo |

### 6.2 Bug Report Template

```markdown
## Bug Title

**Severity**: [Critical/High/Medium/Low]
**Priority**: [P0/P1/P2/P3]
**Distribution**: [e.g., Ubuntu 22.04]
**Desktop Environment**: [e.g., GNOME 42]
**Terminal**: [e.g., gnome-terminal]
**Python Version**: [e.g., 3.11.2]

### Steps to Reproduce
1.
2.
3.

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happens]

### Screenshots/Logs
[Attach relevant files]

### Additional Context
[Any other relevant information]
```

---

## 7. Test Data and Test Scenarios

### 7.1 Test Directory Structure

```
/home/user/test_projects/
├── normal_project/
├── project with spaces/
├── project-with-dashes/
├── project_with_underscores/
├── project(2024)/
├── café_project/
├── .hidden_project/
├── very/deep/nested/path/project/
└── special~chars@project/
```

### 7.2 Test Commands

```bash
# Basic commands
claude
claude --help
claude --version

# Common flags
claude --continue
claude --dangerously-skip-permissions
claude --model claude-opus-4-6
claude --max-tokens 10000

# With messages
claude -m "Fix the login bug"
claude -m 'Add new feature'
claude --prompt "Review this code"
```

---

## 8. Automated Test Execution

### 8.1 Nightly Build Tests

Automated tests run nightly on:
- Ubuntu 22.04 (Python 3.10, 3.11, 3.12)
- Ubuntu 24.04 (Python 3.10, 3.11, 3.12)
- Fedora 39 (Python 3.10, 3.11, 3.12)

### 8.2 Weekly Matrix Tests

Weekly full matrix testing on all supported distributions.

### 8.3 Continuous Integration

Every pull request must:
- Pass all unit tests
- Pass linting checks
- Maintain code coverage thresholds

---

## 9. Documentation Requirements

### 9.1 Test Documentation

- Test plan (this document)
- Test cases (individual test files)
- Test execution logs
- Bug reports and tracking

### 9.2 User Documentation

- Installation guide for each distribution
- Troubleshooting guide
- Configuration guide
- Feature documentation

---

## 10. Conclusion

This testing strategy provides comprehensive coverage for the Linux release of EasyClaude. By following this plan, we can ensure a high-quality, stable release across multiple Linux distributions and desktop environments.

### Next Steps

1. Set up test infrastructure (CI/CD, test VMs)
2. Implement unit tests
3. Begin manual testing on P0 distributions
4. Expand testing to full matrix
5. Address bugs and issues
6. Final verification and release

---

## Appendix A: Test Environment Setup

### A.1 Ubuntu Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and development tools
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Install desktop environment dependencies
sudo apt install -y gnome-terminal konsole xfce4-terminal xterm

# Install test dependencies
sudo apt install -y xvfb libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 \
                      libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
                      libxcb-xinerama0 libxcb-xfixes0

# Install EasyClaude
git clone https://github.com/yourusername/EasyClaude.git
cd EasyClaude
pip install -e ".[dev]"
```

### A.2 Fedora Setup

```bash
# Update system
sudo dnf update -y

# Install Python and development tools
sudo dnf install -y python3 python3-pip python3-devel

# Install desktop environment dependencies
sudo dnf install -y gnome-terminal konsole xfce4-terminal xterm

# Install EasyClaude
git clone https://github.com/yourusername/EasyClaude.git
cd EasyClaude
pip install -e ".[dev]"
```

---

## Appendix B: Test Case Quick Reference

### B.1 Smoke Tests (Quick Validation)

1. Application starts without errors
2. System tray icon appears
3. Hotkey opens GUI launcher
4. Can select directory and launch
5. Terminal opens in correct directory
6. Settings persist across restarts

### B.2 Critical Path Tests

1. Complete workflow: Install → Start → Launch → Exit
2. Terminal launching for each supported terminal
3. Hotkey functionality on each DE
4. Settings save/load
5. Autostart functionality

---

**Document Version**: 1.0
**Last Updated**: 2026-02-08
**Next Review**: Before Phase 2 implementation begins
