# CLAUDE.md - EasyClaude Development Guide

> This document provides essential context for AI assistants (Claude, GPT, etc.) working on the EasyClaude codebase.

## Project Overview

EasyClaude is a **cross-platform system tray application** for launching Claude Code CLI from any directory via a global hotkey. It runs silently in the background and provides quick access to Claude through a GUI launcher.

### Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| GUI | tkinter (built-in) |
| System Tray | pystray |
| Global Hotkey | pynput |
| Configuration | pydantic (type-safe models) |
| Testing | pytest + pytest-cov |

### Platform Support

| Platform | Status | Features |
|----------|--------|----------|
| Windows | Full | Tray, Hotkey, Terminal (PowerShell/WT/CMD), Autostart |
| Linux | Full | Tray (AppIndicator), Hotkey (X11), Terminal (8+ emulators), Autostart (XDG) |
| macOS | Stub | Basic structure only - not yet implemented |

## Architecture

### Core Components

```
app/
  main.py              # Entry point - EasyClaudeApp orchestrates all components
  config.py            # Pydantic Config model + load/save/update functions
  gui.py               # LauncherGUI (tkinter) - directory picker & command buttons
  hotkey.py            # HotkeyManager (pynput) - global hotkey registration
  tray.py              # TrayManager (pystray) - system tray icon & menu
  launcher.py          # ClaudeLauncher - wraps platform terminal launcher
  single_instance.py   # Single-process enforcement via file lock
  autostart.py         # Windows autostart (Startup folder)
  autostart_linux.py   # Linux autostart (XDG autostart)
  platform/
    __init__.py        # Platform detection + TerminalLauncher base class
    windows.py         # WindowsTerminalLauncher (PowerShell/WT/CMD)
    linux.py           # LinuxTerminalLauncher (8+ terminals)
    macos.py           # MacOSTerminalLauncher (stub)
```

### Data Flow

```
User presses hotkey
    HotkeyManager detects -> callbacks to EasyClaudeApp.show_gui()
        LauncherGUI.show() appears
            User selects directory + clicks command
                GUI calls EasyClaudeApp._on_launch()
                    ClaudeLauncher.launch_claude()
                        Platform terminal launcher executes command
                            Claude opens in new terminal window
```

### Key Classes

- **EasyClaudeApp** (`main.py`): Main orchestrator - owns all managers
- **Config** (`config.py`): Pydantic model with validation
- **LauncherGUI** (`gui.py`): tkinter window with lazy initialization
- **HotkeyManager** (`hotkey.py`): pynput keyboard listener
- **TrayManager** (`tray.py`): pystray icon with menu
- **TerminalLauncher** (`platform/__init__.py`): Abstract base class
- **LinuxTerminalLauncher** (`platform/linux.py`): DE-aware terminal detection

## Code Style & Conventions

### Python Style

- **PEP 8 compliant**: 4-space indentation, snake_case naming
- **Type Hints**: Required for all function signatures
- **Docstrings**: Google-style with Args/Returns/Raises sections
- **Imports**: Grouped (stdlib, third-party, local) with blank lines between

### Threading Patterns

```python
# Use Lock/RLock for thread-safe operations
self._lock = threading.Lock()

# Double-check locking pattern for lazy init
def _ensure_initialized(self):
    if not self._initialized:
        with self._lock:
            if not self._initialized:
                # initialize...
                self._initialized = True

# Use queue.Queue for cross-thread communication
self._command_queue = queue.Queue()
```

### Logging

```python
logger = logging.getLogger(__name__)

# Levels: DEBUG (details), INFO (state changes), WARNING (issues), ERROR (failures)
logger.info("Starting application")
logger.debug(f"Config loaded: {config}")
logger.error(f"Failed to launch: {e}")
```

### Error Handling

- Never crash on user input errors - show messagebox instead
- Use try/except with logging for unexpected errors
- Graceful degradation: log and continue with fallback

### tkinter Patterns

- Lazy initialization via `_ensure_initialized()` with double-check locking
- Always-on-top: `root.attributes('-topmost', True)`
- Window centering: calculate x,y from screen dimensions
- Thread-safe updates via command queue with `root.after()` polling

## Configuration

**Location**: `~/.easyclaude/config.json`

```json
{
  "hotkey": "ctrl+alt+c",
  "last_directory": "/home/user/projects",
  "last_command": "claude",
  "always_use_powershell": false,
  "window_position": "center",
  "directory_history": [
    {"path": "/path/to/project", "last_used": "2024-01-15T10:30:00", "use_count": 5}
  ]
}
```

**Config Model** (`config.py`):
- Pydantic `Config` class with validators
- `validate_hotkey()`: Ensures valid hotkey format
- `validate_window_position()`: Ensures valid position value
- `validate_directory_history()`: Maintains max 10 entries

## Platform-Specific Details

### Windows (`platform/windows.py`)

- Terminals: PowerShell, CMD, Windows Terminal
- Detection: Check `os.environ` for WT_SESSION, fall back to PowerShell
- Autostart: Shortcut in `shell:startup` folder

### Linux (`platform/linux.py`)

**Terminal Detection**:
1. Detect desktop environment via `XDG_CURRENT_DESKTOP`
2. Get DE-specific terminal preferences
3. Check availability with `shutil.which()`
4. Fall back to xterm if nothing found

**Supported Terminals**:
- gnome-terminal, konsole, xfce4-terminal
- mate-terminal, lxterminal
- kitty, alacritty
- xterm (fallback)

**Shell Handling**:
- Auto-detect user shell from `$SHELL`
- Support bash, zsh, fish syntax
- Use `shlex.quote()` for safe command escaping

**Known Limitations**:
- Wayland: Global hotkeys may not work (security model)
- GNOME 40+: Requires AppIndicator extension for tray

## Testing

### Running Tests

```bash
# All tests with coverage
pytest tests/ -v

# Specific test file
pytest tests/test_config.py -v

# With coverage report
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Test Structure

```
tests/
  conftest.py              # Shared fixtures
  test_config.py           # Config load/save/validation
  test_gui.py              # GUI unit tests
  test_hotkey.py           # Hotkey manager tests
  test_launcher.py         # Launcher tests (mocked)
  test_launcher_real.py    # Real terminal launch tests
  test_tray.py             # Tray manager tests
  test_integration.py      # End-to-end tests
  test_directory_history.py # Directory history feature
  platform/
    test_linux.py          # Linux terminal launcher unit tests
    test_linux_desktop.py  # Desktop environment detection
    test_linux_integration.py # Integration tests
  linux/
    README.md              # Linux testing documentation
    run_local_tests.sh     # Local test runner
```

### Writing Tests

- Use pytest fixtures for common setup
- Mock external dependencies (subprocess, file I/O)
- Test both success and error paths
- Aim for >80% coverage on core modules

## Building

### Windows

```bash
pip install pyinstaller
pyinstaller easyclaude.spec
# Output: dist/EasyClaude.exe
```

### Linux

```bash
pip install pyinstaller
pyinstaller easyclaude_linux.spec
# Output: dist/EasyClaude
```

## Development Workflow

### Setup

```bash
git clone https://github.com/AhmadHanif12/EasyClaude.git
cd EasyClaude
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

pip install -e ".[dev]"    # Install with dev dependencies
pip install -e ".[linux]"  # Add Linux dependencies (Linux only)
```

### Debugging

- Logs written to `easyclaude_debug.log` in project root
- Console output visible when running from source
- Use `logging.getLogger(__name__).setLevel(logging.DEBUG)` for verbose output

### Common Tasks

**Add new terminal support** (Linux):
1. Add terminal name to `TERMINALS` list in `platform/linux.py`
2. Add to appropriate DE in `DE_TERMINAL_MAP`
3. Implement terminal-specific command array in `_get_terminal_command_array()`
4. Add tests in `tests/platform/test_linux.py`

**Add new configuration option**:
1. Add field to `Config` class in `config.py`
2. Add validator if needed
3. Update `load_config()` defaults
4. Add tests in `test_config.py`

**Add new GUI element**:
1. Add to `_build_layout()` in `gui.py`
2. Ensure thread-safe updates via command queue
3. Add tests in `test_gui.py`

## Important Notes

### Single Instance Enforcement

The app uses a file-based lock (`single_instance.py`) to prevent multiple instances. This is critical for:
- Preventing hotkey conflicts
- Avoiding duplicate tray icons
- Ensuring consistent configuration state

### Thread Safety

Multiple threads are used:
- **Main thread**: tkinter GUI
- **Background thread**: pynput hotkey listener
- **Background thread**: pystray tray icon

Always use locks/queues when sharing data between threads.

### Graceful Degradation

If a feature fails:
1. Log the error
2. Show user-friendly message (if GUI available)
3. Continue with fallback behavior
4. Never crash silently

## Recent Changes

### v0.2.0 - Linux Support Complete

- Full `LinuxTerminalLauncher` implementation
- Desktop environment detection (GNOME, KDE, XFCE, MATE, etc.)
- 8+ terminal emulators supported
- Shell-aware command formatting (bash/zsh/fish)
- Directory history feature with quick selection
- Comprehensive test suite for Linux platform
- Autostart support via XDG autostart

## Related Documentation

- `README.md` - User-facing documentation
- `docs/` - Additional documentation (if exists)
- `tests/linux/` - Linux testing strategy and guides
- `.serena/memories/` - Project memory files (PROJECT_OVERVIEW, STYLE_CONVENTIONS, etc.)
