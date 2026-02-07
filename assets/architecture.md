# EasyClaude Architecture

## System Overview

EasyClaude is a Windows-first, cross-platform Python system tray application that provides instant access to Claude Code via a global hotkey (Ctrl+Alt+C). The architecture follows a modular design with clear separation of concerns, enabling maintainability and future platform expansion.

```
+-----------------------------------------------------------------------+
|                          EasyClaude Application                       |
+-----------------------------------------------------------------------+
                                                                       |
+---------------------------+    +-------------------+    +-----------+
|      System Tray          |    |   Global Hotkey   |    |    GUI    |
|      (pystray)            |<-->|   (pynput)        |<-->| (tkinter) |
+---------------------------+    +-------------------+    +-----------+
            |                           |                        |
            +---------------------------+------------------------+
                                        |
                                        v
                              +-------------------+
                              |   Main Orchestrator|
                              +-------------------+
                                        |
          +-----------------------------+-----------------------------+
          |                             |                             |
          v                             v                             v
+------------------+          +------------------+        +------------------+
|  Config Manager  |          |  Launcher        |        |  Platform Layer  |
|  (pydantic)      |          |                  |        |  (Abstract)      |
+------------------+          +------------------+        +------------------+
          |                             |                             |
          |                             v                             v
          |                    +------------------+          +------------------+
          |                    |  Claude Command  |          |  Terminal        |
          +--------------------->  Execution       |          |  Launchers       |
                               +------------------+          +------------------+
                                                                   |
                                                 +----------------+----------------+
                                                 |                                 |
                                                 v                                 v
                                    +------------------+               +------------------+
                                    |  Windows         |               |  Linux           |
                                    |  (PowerShell)    |               |  (Phase 2)       |
                                    +------------------+               +------------------+
```

## Component Architecture

### 1. Main Orchestrator (`app/main.py`)

**Responsibility:** Application lifecycle and component coordination

**Key Functions:**
- Initialize all subsystems (tray, hotkey, config, launcher)
- Coordinate component startup/shutdown
- Handle application-level events and errors
- Manage graceful shutdown

**Dependencies:**
- All other components (composition root)

**Interfaces:**
```python
class Application:
    def __init__(self)
    def start() -> None
    def stop() -> None
    def run() -> None
```

### 2. System Tray Component (`app/tray.py`)

**Responsibility:** System tray icon and menu management

**Key Functions:**
- Display icon in system tray
- Provide context menu (Launch, Settings, Quit)
- Handle tray icon clicks
- Update icon state (active/inactive)

**Dependencies:**
- `pystray`
- GUI component (for menu actions)

**Interfaces:**
```python
class TrayIcon:
    def __init__(self, on_launch_callback, on_settings_callback, on_quit_callback)
    def show() -> None
    def hide() -> None
    def update_tooltip(message: str) -> None
```

### 3. Global Hotkey Component (`app/hotkey.py`)

**Responsibility:** Global hotkey registration and handling

**Key Functions:**
- Register system-wide hotkey (default: Ctrl+Alt+C)
- Detect hotkey press
- Trigger GUI display on activation
- Support hotkey reconfiguration

**Dependencies:**
- `pynput`
- GUI component
- Config (for hotkey settings)

**Interfaces:**
```python
class GlobalHotkey:
    def __init__(self, hotkey_combination: str, on_press_callback)
    def start() -> None
    def stop() -> None
    def update_hotkey(hotkey_combination: str) -> None
```

### 4. GUI Component (`app/gui.py`)

**Responsibility:** User interface for directory and command selection

**Key Functions:**
- Display centered, always-on-top window
- Directory selection (browse + text entry)
- Command selection buttons
- Launch/Cancel actions
- Remember last position

**Dependencies:**
- `tkinter`
- Config (for persistence)
- Launcher (for execution)

**Interfaces:**
```python
class LauncherGUI:
    def __init__(self, config, on_launch_callback)
    def show() -> None
    def hide() -> None
    def get_selection() -> tuple[str, str]  # (directory, command)
```

### 5. Configuration Manager (`app/config.py`)

**Responsibility:** Configuration persistence and validation

**Key Functions:**
- Load configuration from file
- Save configuration changes
- Validate configuration values
- Provide typed configuration access

**Dependencies:**
- `pydantic`
- Platform-specific config directory

**Interfaces:**
```python
class AppConfig(BaseModel):
    hotkey: str = "ctrl+alt+c"
    last_directory: str
    last_command: str = "claude"
    always_use_powershell: bool = False
    window_position: str = "center"

class ConfigManager:
    def load() -> AppConfig
    def save(config: AppConfig) -> None
    def get_config_dir() -> Path
```

### 6. Launcher Component (`app/launcher.py`)

**Responsibility:** Claude command execution coordination

**Key Functions:**
- Construct Claude command strings
- Delegate to platform-specific launcher
- Handle execution errors
- Report launch status

**Dependencies:**
- Platform layer (TerminalLauncher)
- Config (for settings)

**Interfaces:**
```python
class ClaudeLauncher:
    def __init__(self, platform_launcher: TerminalLauncher)
    def launch(directory: str, command: str) -> bool
    def get_available_commands() -> list[str]
```

### 7. Platform Abstraction Layer (`app/platform/`)

**Responsibility:** Platform-specific terminal launching

**Design Pattern:** Strategy Pattern with Abstract Base Class

**Base Interface:**
```python
from abc import ABC, abstractmethod
from pathlib import Path

class TerminalLauncher(ABC):
    """Abstract base for platform-specific terminal launchers."""

    @abstractmethod
    def launch_claude(self, directory: str, command: str) -> None:
        """Launch Claude Code in a terminal at the specified directory."""
        pass

    @abstractmethod
    def get_terminal_command(self, directory: str, command: str) -> list[str]:
        """Get the platform-specific command list for launching."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the terminal is available on this system."""
        pass
```

**Platform Factory:**
```python
def create_launcher() -> TerminalLauncher:
    """Factory function to create platform-appropriate launcher."""
    import platform
    if platform.system() == "Windows":
        return WindowsTerminalLauncher()
    elif platform.system() == "Linux":
        return LinuxTerminalLauncher()
    else:
        raise NotImplementedError(f"Platform {platform.system()} not supported")
```

## Data Flow

### Launch Flow

```
User presses Ctrl+Alt+C
        |
        v
[GlobalHotkey] detects hotkey
        |
        v
[Main] receives hotkey event
        |
        v
[GUI] shows launcher window (centered, always-on-top)
        |
        v
User selects directory and command
        |
        v
[GUI] returns selection to [Main]
        |
        v
[Config] saves last directory/command
        |
        v
[Launcher] constructs full command
        |
        v
[Platform] executes in terminal
        |
        v
Terminal opens with Claude Code running
```

### Configuration Flow

```
Application Startup
        |
        v
[Config] loads from ~/.easyclaude/config.json
        |
        v
Validation (pydantic)
        |
        v
Components initialized with config
        |
        v
... application runs ...
        |
        v
User changes settings
        |
        v
[Config] validates and saves
        |
        v
Persists to disk
```

### Error Handling Flow

```
Any component encounters error
        |
        v
Error logged to logs/easyclaude.log
        |
        v
User notified (if actionable)
        |
        v
Application continues (graceful degradation)
        |
        v
Critical error -> [Main] initiates shutdown
```

## Cross-Platform Support Strategy

### Phase 1: Windows (Current)

**Implementation:** `app/platform/windows.py`

**Terminal:** PowerShell

**Command Construction:**
```powershell
powershell.exe -NoExit -Command "cd '<directory>'; <command>"
```

**Special Handling:**
- Path escaping for Windows
- PowerShell profile detection
- Windows Terminal vs legacy console detection

### Phase 2: Linux (Future)

**Implementation:** `app/platform/linux.py`

**Terminal Strategy:**
1. Detect available terminal emulators (gnome-terminal, konsole, xterm, etc.)
2. Use user's preferred terminal if configured
3. Fall back to detected terminals in priority order

**Command Construction:**
```bash
terminal -- bash -c "cd '<directory>'; <command>; exec bash"
```

**Special Handling:**
- Shell detection (bash, zsh, fish)
- XDG config directories
- Desktop entry for autostart

### Platform Detection

```python
import platform

def get_platform_info() -> dict:
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "python_version": platform.python_version(),
    }
```

## Configuration Storage

### Location

- **Windows:** `C:\Users\<User>\AppData\Roaming\.easyclaude\config.json`
- **Linux:** `~/.config/easyclaude/config.json`

### Schema

```json
{
  "$schema": "./config.schema.json",
  "hotkey": "ctrl+alt+c",
  "last_directory": "C:\\Users\\User\\Projects",
  "last_command": "claude",
  "always_use_powershell": false,
  "window_position": "center",
  "terminal_preference": "auto"
}
```

## Thread Safety

### Threading Model

```
Main Thread:
  - GUI event loop (tkinter)
  - System tray (pystray)

Hotkey Thread:
  - Global hotkey listener (pynput)
  - Communication via queue/callback

Worker Threads (async):
  - Terminal subprocess launching
  - Configuration I/O
```

### Synchronization

- `threading.Lock` for config access
- `queue.Queue` for thread-safe communication
- Callbacks must be thread-safe when called from hotkey thread

## Error Handling Strategy

### Exception Categories

1. **Configuration Errors**
   - Invalid config file -> Recreate with defaults
   - Invalid values -> Validation error, use default

2. **Platform Errors**
   - Terminal not found -> Error dialog, graceful degradation
   - Command execution failure -> Error message to user

3. **Runtime Errors**
   - Hotkey registration -> Log warning, continue without hotkey
   - GUI display -> Log error, attempt restart

### Logging

```python
import logging

logger = logging.getLogger("easyclaude")
logger.setLevel(logging.DEBUG)

# File handler
file_handler = logging.FileHandler("logs/easyclaude.log")
file_handler.setLevel(logging.DEBUG)

# Console handler (development)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
```

## Security Considerations

1. **Command Injection Prevention**
   - Validate directory paths
   - Escape shell arguments properly
   - Avoid direct string interpolation

2. **Permission Handling**
   - Respect file system permissions
   - Warn if running without necessary privileges

3. **Credential Safety**
   - No credential storage in config
   - Respect Claude's own authentication

## Build and Distribution

### PyInstaller Configuration

**Spec File:** `build/build.spec`

**Key Settings:**
- One-file or one-dir mode
- Include data files (icon, config)
- Console window hidden (pythonw.exe)
- UPX compression (optional)

**Build Command:**
```bash
pyinstaller build/build.spec
```

### Autostart Integration

**Windows:**
- Registry key: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- Shortcut in Startup folder

**Linux (Future):**
- `.desktop` file in `~/.config/autostart/`

## Testing Strategy

### Unit Tests (`tests/`)

```
test_config.py       - Configuration loading, validation, persistence
test_launcher.py     - Command construction, platform launcher calls
test_gui.py          - GUI component interactions
test_hotkey.py       - Hotkey registration and callbacks
test_platform.py     - Platform-specific launcher tests
```

### Integration Tests

- Full launch flow with mocked terminal
- Configuration persistence across restarts
- Hotkey to GUI to launch sequence

### Platform Testing

- Windows: PowerShell versions, Windows Terminal
- Linux: Multiple terminal emulators (Phase 2)

## Dependencies

### Runtime Dependencies

```
pystray>=0.19.5      # System tray
pynput>=1.7.6        # Global hotkey
pydantic>=2.0.0      # Configuration validation
```

### Development Dependencies

```
pytest>=7.0.0        # Testing
pytest-asyncio       # Async test support
pytest-cov           # Coverage reporting
```

### Build Dependencies

```
pyinstaller>=5.0.0   # Windows executable
```

## Extension Points

### Adding New Commands

Add to `app/launcher.py`:
```python
AVAILABLE_COMMANDS = [
    "claude",
    "claude --continue",
    "claude --dangerously-skip-permissions",
    # Add new commands here
]
```

### Adding New Platforms

1. Create `app/platform/<platform>.py`
2. Implement `TerminalLauncher` interface
3. Update factory in `app/platform/__init__.py`

### Custom Terminal Preference

Extend config:
```python
terminal_preference: str = "auto"  # auto, powershell, cmd, gnome-terminal, etc.
```

## Performance Considerations

1. **Startup Time:** Minimize imports, lazy-load non-critical components
2. **Memory Usage:** Clean up resources when GUI is hidden
3. **Hotkey Latency:** Keep hotkey handler lightweight
4. **Terminal Launch:** Async execution to avoid blocking

## Future Enhancements

### Phase 2 Features

- Linux support
- Multiple terminal profiles
- Command history
- Recent directories quick access
- Custom command templates

### Phase 3 Features

- macOS support
- Plugin system for custom commands
- Cloud config sync
- Advanced hotkey configuration
- Terminal session management
