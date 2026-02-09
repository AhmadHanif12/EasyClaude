# Linux Terminal Launcher Research for EasyClaude

## Executive Summary

This document provides comprehensive research on Linux terminal emulators and their command-line interfaces for implementing `LinuxTerminalLauncher.launch_claude()` to match the quality of `WindowsTerminalLauncher`.

## Table of Contents
1. [Terminal Emulator Command-Line Interfaces](#terminal-emulator-command-line-interfaces)
2. [Shell Detection and Syntax](#shell-detection-and-syntax)
3. [Terminal Detection Best Practices](#terminal-detection-best-practices)
4. [Command Escaping and Security](#command-escaping-and-security)
5. [Implementation Examples](#implementation-examples)
6. [Recommended Implementation Strategy](#recommended-implementation-strategy)

---

## 1. Terminal Emulator Command-Line Interfaces

### 1.1 gnome-terminal (GNOME)
**Package:** `gnome-terminal`
**Desktop Environment:** GNOME
**Priority:** HIGH (most common on modern Linux)

**Command Syntax:**
```bash
# Basic usage
gnome-terminal --working-directory=/path/to/dir -- command

# With shell execution
gnome-terminal --working-directory=/path/to/dir -- bash -c "command; exec bash"

# Keep terminal open after command completes
gnome-terminal --working-directory=/path/to/dir -- bash -c "command; exec bash"
```

**Key Flags:**
- `--working-directory=PATH` or `-w PATH`: Set working directory
- `--` or `-e`: Execute command (deprecated, use `--` instead)
- `--title=TITLE`: Set window title
- `--command=CMD`: Execute command (newer versions)

**Example for EasyClaude:**
```python
cmd = [
    "gnome-terminal",
    "--working-directory", directory,
    "--",
    "bash", "-c", f"cd '{directory}' && {command}; exec bash"
]
```

**Notes:**
- The `--working-directory` flag is preferred over `cd` in the command
- Using `exec bash` at the end keeps the terminal open
- Modern versions (3.28+) prefer `--command` over `-e`

---

### 1.2 konsole (KDE)
**Package:** `konsole`
**Desktop Environment:** KDE Plasma
**Priority:** HIGH (second most common)

**Command Syntax:**
```bash
# Basic usage
konsole --workdir /path/to/dir -e bash -c "command; exec bash"

# With separate command
konsole --workdir /path/to/dir --noclose -e command

# Using --hold flag
konsole --workdir /path/to/dir -e bash -c "command" --hold
```

**Key Flags:**
- `--workdir DIR` or `-w DIR`: Set working directory
- `-e` or `--command`: Execute command
- `--hold` or `--noclose`: Keep window open after command exits
- `--profile`: Use specific profile
- `--title`: Set window title

**Example for EasyClaude:**
```python
cmd = [
    "konsole",
    "--workdir", directory,
    "--hold",
    "-e", "bash", "-c", f"cd '{directory}' && {command}; exec bash"
]
```

**Notes:**
- `--hold` keeps the window open after command completion
- KDE-specific: can use `--profile` for custom terminal settings
- Supports tabs with `--new-tab`

---

### 1.3 xfce4-terminal (XFCE)
**Package:** `xfce4-terminal`
**Desktop Environment:** XFCE
**Priority:** MEDIUM

**Command Syntax:**
```bash
# Basic usage
xfce4-terminal --working-directory=/path/to/dir -x bash -c "command; exec bash"

# With --hold option
xfce4-terminal --working-directory=/path/to-dir -x bash -c "command" --disable-server
```

**Key Flags:**
- `--working-directory=PATH`: Set working directory
- `-x` or `--execute`: Execute remaining arguments
- `-e` or `--command`: Execute command string
- `--title`: Set window title
- `--hold`: Keep window open after command exits (v0.8.10+)
- `--disable-server`: Disable D-Bus server

**Example for EasyClaude:**
```python
cmd = [
    "xfce4-terminal",
    "--working-directory", directory,
    "-x", "bash", "-c", f"cd '{directory}' && {command}; exec bash"
]
```

**Notes:**
- `-x` executes all following arguments as a command
- For older versions without `--hold`, use `exec bash` trick

---

### 1.4 mate-terminal (MATE)
**Package:** `mate-terminal`
**Desktop Environment:** MATE
**Priority:** MEDIUM

**Command Syntax:**
```bash
# Basic usage (similar to gnome-terminal)
mate-terminal --working-directory=/path/to/dir -- command

# With execution
mate-terminal --working-directory=/path/to/dir -x bash -c "command; exec bash"
```

**Key Flags:**
- `--working-directory=PATH`: Set working directory
- `-x` or `--execute`: Execute command
- `-t` or `--title`: Set window title
- `--profile`: Use specific profile

**Example for EasyClaude:**
```python
cmd = [
    "mate-terminal",
    "--working-directory", directory,
    "-x", "bash", "-c", f"cd '{directory}' && {command}; exec bash"
]
```

**Notes:**
- Forked from gnome-terminal 2.x, very similar syntax
- Inherits most gnome-terminal flags

---

### 1.5 lxterminal (LXDE/LXQt)
**Package:** `lxterminal`
**Desktop Environment:** LXDE/LXQt
**Priority:** LOW

**Command Syntax:**
```bash
# Basic usage
lxterminal --working-directory=/path/to/dir -e bash -c "command; exec bash"
```

**Key Flags:**
- `--working-directory=PATH`: Set working directory
- `-e` or `--command`: Execute command
- `--title`: Set window title
- `--geometry`: Set window geometry

**Example for EasyClaude:**
```python
cmd = [
    "lxterminal",
    "--working-directory", directory,
    "-e", "bash", "-c", f"cd '{directory}' && {command}; exec bash"
]
```

**Notes:**
- Lightweight terminal, fewer features
- No built-in `--hold` option

---

### 1.6 xterm (X11)
**Package:** xterm
**Desktop Environment:** Any X11
**Priority:** LOW (fallback)

**Command Syntax:**
```bash
# Basic usage
xterm -e bash -c "command; exec bash"

# With working directory
xterm -e "cd /path/to/dir && command; exec bash"
```

**Key Flags:**
- `-e`: Execute command
- `-T`: Set title
- `-geometry`: Set window geometry
- `-fn`: Set font
- `-bg`/`-fg`: Background/foreground colors

**Example for EasyClaude:**
```python
cmd = [
    "xterm",
    "-e", "bash", "-c", f"cd '{directory}' && {command}; exec bash"
]
```

**Notes:**
- Oldest terminal, most basic
- No native `--working-directory` flag
- Must use `cd` in command

---

### 1.7 kitty (Modern GPU-Accelerated)
**Package:** kitty
**Desktop Environment:** Any
**Priority:** GROWING (increasingly popular)

**Command Syntax:**
```bash
# Basic usage
kitty --directory=/path/to/dir bash -c "command; exec bash"

# With hold option
kitty --directory=/path/to/dir --hold bash -c "command"

# Using launch command
kitty +launch --directory=/path/to/dir -- bash -c "command; exec bash"
```

**Key Flags:**
- `--directory=PATH` or `-d PATH`: Set working directory
- `--hold`: Keep window open after command exits
- `--title`: Set window title
- `--instance-group`: Group windows
- `--listen-on`: Control via socket

**Example for EasyClaude:**
```python
cmd = [
    "kitty",
    "--directory", directory,
    "--hold",
    "bash", "-c", f"cd '{directory}' && {command}; exec bash"
]
```

**Notes:**
- Modern, feature-rich terminal
- GPU-accelerated rendering
- Highly configurable via `kitty.conf`

---

### 1.8 alacritty (Modern GPU-Accelerated)
**Package:** alacritty
**Desktop Environment:** Any
**Priority:** GROWING

**Command Syntax:**
```bash
# Basic usage (must use shell to change directory)
alacritty -e bash -c "cd /path/to/dir && command; exec bash"

# Using config file for working directory
alacritty --working-directory=/path/to/dir -e command

# With command in config
```

**Key Flags:**
- `-e` or `--command`: Execute command
- `--working-directory`: Set working directory (v0.13.0+)
- `-t` or `--title`: Set window title
- `--config-file`: Use custom config

**Example for EasyClaude:**
```python
cmd = [
    "alacritty",
    "--working-directory", directory,
    "-e", "bash", "-c", f"{command}; exec bash"
]
```

**Notes:**
- No native `--hold` option
- Must use `exec shell` trick
- Configuration via YAML file

---

## 2. Shell Detection and Syntax

### 2.1 Detecting User's Default Shell

**Method 1: Reading /etc/passwd**
```python
import pwd
import os

def get_user_shell() -> str:
    """Get the user's default shell from /etc/passwd."""
    return os.environ.get('SHELL', '/bin/bash')

# Example returns: '/bin/bash', '/bin/zsh', '/bin/fish'
```

**Method 2: Using environment variable**
```python
def get_user_shell() -> str:
    """Get shell from SHELL environment variable."""
    return os.environ.get('SHELL', '/bin/bash')
```

**Method 3: Platform detection with fallback**
```python
def get_user_shell() -> str:
    """Get the user's shell with intelligent fallback."""
    # Check SHELL environment variable
    shell = os.environ.get('SHELL')

    if shell and os.path.exists(shell):
        return shell

    # Fallback to common shells in order of preference
    for shell in ['/bin/zsh', '/bin/bash', '/bin/sh', '/usr/bin/zsh', '/usr/bin/bash']:
        if os.path.exists(shell):
            return shell

    # Last resort
    return '/bin/sh'
```

### 2.2 Shell-Specific Syntax Considerations

**Bash (/bin/bash)**
```bash
# Command chaining
cd /path/to/dir && command; exec bash

# Variable assignment (not needed for our use case)
VAR="value"

# Quoting: use double quotes for variable expansion, single for literals
cd "$HOME/claude && command"
```

**Zsh (/bin/zsh)**
```bash
# Similar to bash
cd /path/to/dir && command; exec zsh

# Zsh-specific: can use more advanced globbing
# For our purposes, bash-compatible syntax works fine
```

**Fish (/bin/fish)**
```bash
# DIFFERENT SYNTAX - not compatible with bash!
cd /path/to/dir; and command; exec fish

# Fish doesn't use ; for command chaining in the same way
# Uses 'and', 'or' instead of '&&', '||'
```

**Recommendation for EasyClaude:**
```python
def get_shell_command(shell_path: str, directory: str, command: str) -> str:
    """Get shell-specific command string."""
    shell_name = os.path.basename(shell_path)

    if shell_name == 'fish':
        # Fish-specific syntax
        return f'cd "{directory}"; and {command}; exec {shell_path}'
    else:
        # Bash/zsh compatible syntax
        return f'cd "{directory}" && {command}; exec {shell_path}'
```

---

## 3. Terminal Detection Best Practices

### 3.1 Desktop Environment Detection

```python
import os
import subprocess

def detect_desktop_environment() -> str:
    """Detect the current desktop environment."""
    # Check XDG_CURRENT_DESKTOP
    xdg_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()

    if 'gnome' in xdg_desktop:
        return 'gnome'
    elif 'kde' in xdg_desktop or 'plasma' in xdg_desktop:
        return 'kde'
    elif 'xfce' in xdg_desktop:
        return 'xfce'
    elif 'mate' in xdg_desktop:
        return 'mate'
    elif 'lxde' in xdg_desktop or 'lxqt' in xdg_desktop:
        return 'lxde'

    # Fallback: check for running processes
    try:
        result = subprocess.run(['ps', '-e'], capture_output=True, text=True)
        output = result.stdout.lower()

        if 'gnome-terminal' in output:
            return 'gnome'
        elif 'konsole' in output:
            return 'kde'
        elif 'xfce4-terminal' in output:
            return 'xfce'
    except Exception:
        pass

    return 'unknown'
```

### 3.2 Terminal Priority by Desktop Environment

```python
TERMINAL_PREFERENCES = {
    'gnome': ['gnome-terminal', 'kgx', 'xterm'],
    'kde': ['konsole', 'gnome-terminal', 'xterm'],
    'xfce': ['xfce4-terminal', 'gnome-terminal', 'xterm'],
    'mate': ['mate-terminal', 'gnome-terminal', 'xterm'],
    'lxde': ['lxterminal', 'gnome-terminal', 'xterm'],
    'unknown': ['gnome-terminal', 'konsole', 'xfce4-terminal',
                'mate-terminal', 'lxterminal', 'xterm', 'kitty', 'alacritty']
}

def get_preferred_terminals() -> list:
    """Get terminal preferences based on desktop environment."""
    de = detect_desktop_environment()
    return TERMINAL_PREFERENCES.get(de, TERMINAL_PREFERENCES['unknown'])
```

### 3.3 Terminal Detection with Caching

```python
import shutil
from functools import lru_cache
from typing import Optional

class TerminalDetector:
    """Detect and cache available terminals."""

    # Terminal list in order of preference
    TERMINALS = [
        'gnome-terminal',
        'konsole',
        'xfce4-terminal',
        'mate-terminal',
        'lxterminal',
        'kitty',
        'alacritty',
        'xterm',
    ]

    def __init__(self):
        self._detected_terminals: Optional[list] = None
        self._primary_terminal: Optional[str] = None

    def detect_terminals(self) -> list:
        """Detect all available terminals."""
        if self._detected_terminals is not None:
            return self._detected_terminals

        available = []
        de = detect_desktop_environment()
        preferences = get_preferred_terminals()

        # Sort terminals by preference
        sorted_terminals = sorted(
            self.TERMINALS,
            key=lambda t: preferences.index(t) if t in preferences else 999
        )

        for terminal in sorted_terminals:
            if shutil.which(terminal):
                available.append(terminal)

        self._detected_terminals = available
        self._primary_terminal = available[0] if available else None

        return available

    def get_primary_terminal(self) -> Optional[str]:
        """Get the primary (most preferred) terminal."""
        if self._primary_terminal is None:
            self.detect_terminals()
        return self._primary_terminal
```

---

## 4. Command Escaping and Security

### 4.1 Bash/Zsh Command Escaping

```python
import re

def escape_bash_command(command: str) -> str:
    """
    Escape a command string for safe execution in bash/zsh.

    Prevents command injection by properly escaping:
    - Single quotes: ' -> '\''
    - Double quotes: " -> \"
    - Backslashes: \ -> \\
    - Dollar signs: $ -> \$
    - Backticks: ` -> \`
    """
    # Remove any null bytes
    command = command.replace('\0', '')

    # Escape special characters
    # Use shlex.quote for proper shell escaping
    import shlex
    return shlex.quote(command)
```

### 4.2 Safe Command Building

```python
import shlex
from pathlib import Path

def build_safe_command(directory: str, command: str, shell: str) -> str:
    """
    Build a safe shell command for execution.

    Args:
        directory: The working directory
        command: The command to execute
        shell: Path to the shell (e.g., /bin/bash)

    Returns:
        A safely escaped command string
    """
    # Validate directory exists
    dir_path = Path(directory).expanduser().resolve()
    if not dir_path.exists() or not dir_path.is_dir():
        raise LaunchFailedError(f"Invalid directory: {directory}")

    # Escape directory path
    escaped_dir = shlex.quote(str(dir_path))

    # Validate and escape command
    if not command or not command.strip():
        raise LaunchFailedError("Command cannot be empty")

    # For the claude command, we can be more permissive
    # but should still validate it starts with "claude"
    command = command.strip()
    if not command.lower().startswith("claude"):
        raise LaunchFailedError(f"Invalid command: {command}")

    escaped_cmd = shlex.quote(command)

    # Build final command
    shell_name = Path(shell).name

    if shell_name == 'fish':
        # Fish syntax
        return f"cd {escaped_dir}; and {escaped_cmd}; exec {shlex.quote(shell)}"
    else:
        # Bash/zsh syntax
        return f"cd {escaped_dir} && {escaped_cmd}; exec {shlex.quote(shell)}"
```

### 4.3 Alternative: Using Shell Argument Array

```python
def get_terminal_command_array(terminal: str, directory: str,
                               command: str, shell: str) -> list:
    """
    Build command as an array to avoid shell escaping issues.

    This is safer than building a command string.
    """
    validated_dir = str(Path(directory).expanduser().resolve())

    # Build shell command string
    shell_name = Path(shell).name

    if shell_name == 'fish':
        cmd_str = f'cd "{validated_dir}"; and {command}; exec {shell}'
    else:
        cmd_str = f'cd "{validated_dir}" && {command}; exec {shell}'

    # Terminal-specific command arrays
    terminal_commands = {
        'gnome-terminal': [
            'gnome-terminal',
            '--working-directory', validated_dir,
            '--', shell, '-c', cmd_str
        ],
        'konsole': [
            'konsole',
            '--workdir', validated_dir,
            '--hold',
            '-e', shell, '-c', cmd_str
        ],
        'xfce4-terminal': [
            'xfce4-terminal',
            '--working-directory', validated_dir,
            '-x', shell, '-c', cmd_str
        ],
        'mate-terminal': [
            'mate-terminal',
            '--working-directory', validated_dir,
            '-x', shell, '-c', cmd_str
        ],
        'lxterminal': [
            'lxterminal',
            '--working-directory', validated_dir,
            '-e', shell, '-c', cmd_str
        ],
        'kitty': [
            'kitty',
            '--directory', validated_dir,
            '--hold',
            shell, '-c', cmd_str
        ],
        'alacritty': [
            'alacritty',
            '--working-directory', validated_dir,
            '-e', shell, '-c', cmd_str
        ],
        'xterm': [
            'xterm',
            '-e', shell, '-c', cmd_str
        ],
    }

    return terminal_commands.get(terminal, terminal_commands['xterm'])
```

---

## 5. Implementation Examples

### 5.1 Complete LinuxTerminalLauncher Implementation

```python
"""Linux terminal launcher implementation for EasyClaude."""

import os
import shutil
import logging
import subprocess
from typing import Optional, Dict, List
from pathlib import Path

from app.platform import TerminalLauncher, TerminalNotFoundError, LaunchFailedError

logger = logging.getLogger(__name__)


class LinuxTerminalLauncher(TerminalLauncher):
    """
    Linux-specific terminal launcher.

    Supports multiple terminal emulators with automatic detection
    and desktop environment awareness.
    """

    # Supported terminals in order of preference
    TERMINALS = [
        'gnome-terminal',
        'konsole',
        'xfce4-terminal',
        'mate-terminal',
        'lxterminal',
        'kitty',
        'alacritty',
        'xterm',
    ]

    # Desktop environment to terminal mapping
    DE_TERMINAL_MAP = {
        'gnome': ['gnome-terminal', 'kgx', 'xterm'],
        'kde': ['konsole', 'gnome-terminal', 'xterm'],
        'plasma': ['konsole', 'gnome-terminal', 'xterm'],
        'xfce': ['xfce4-terminal', 'gnome-terminal', 'xterm'],
        'mate': ['mate-terminal', 'gnome-terminal', 'xterm'],
        'lxde': ['lxterminal', 'gnome-terminal', 'xterm'],
        'lxqt': ['lxterminal', 'gnome-terminal', 'xterm'],
    }

    # Common shells in order of preference
    SHELLS = [
        '/bin/zsh',
        '/bin/bash',
        '/bin/sh',
        '/usr/bin/zsh',
        '/usr/bin/bash',
    ]

    def __init__(self, terminal_preference: Optional[str] = None,
                 shell_preference: Optional[str] = None):
        """
        Initialize the Linux terminal launcher.

        Args:
            terminal_preference: Preferred terminal emulator
            shell_preference: Preferred shell (path or name)
        """
        self.terminal_preference = terminal_preference
        self.shell_preference = shell_preference

        # Cached detection results
        self._available_terminals: Optional[List[str]] = None
        self._detected_terminal: Optional[str] = None
        self._user_shell: Optional[str] = None
        self._desktop_environment: Optional[str] = None

        self._detect_environment()

    def _detect_environment(self) -> None:
        """Detect the Linux environment: desktop, terminals, and shell."""
        self._detect_desktop_environment()
        self._detect_terminals()
        self._detect_shell()

    def _detect_desktop_environment(self) -> None:
        """Detect the current desktop environment."""
        # Check XDG_CURRENT_DESKTOP environment variable
        xdg_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()

        # XDG_CURRENT_DESKTOP can contain multiple DEs separated by :
        for de in xdg_desktop.split(':'):
            if de in self.DE_TERMINAL_MAP:
                self._desktop_environment = de
                logger.debug(f"Detected desktop environment: {de}")
                return

        # Fallback: check for running processes
        try:
            result = subprocess.run(
                ['ps', '-e'],
                capture_output=True,
                text=True,
                timeout=2
            )
            output = result.stdout.lower()

            if 'gnome-session' in output or 'gnome-shell' in output:
                self._desktop_environment = 'gnome'
            elif 'plasmashell' in output or 'kded' in output:
                self._desktop_environment = 'kde'
            elif 'xfce4-session' in output or 'xfce4-panel' in output:
                self._desktop_environment = 'xfce'
            elif 'mate-session' in output:
                self._desktop_environment = 'mate'
            elif 'lxsession' in output or 'lxqt-session' in output:
                self._desktop_environment = 'lxde'
            else:
                self._desktop_environment = 'unknown'
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.debug(f"Could not detect desktop environment: {e}")
            self._desktop_environment = 'unknown'

        logger.debug(f"Desktop environment: {self._desktop_environment}")

    def _detect_terminals(self) -> None:
        """Detect available terminal emulators."""
        self._available_terminals = []

        # Determine terminal preference order
        if self.terminal_preference:
            # User has a preference, try it first
            if shutil.which(self.terminal_preference):
                self._available_terminals.append(self.terminal_preference)
                logger.debug(f"Found preferred terminal: {self.terminal_preference}")
            else:
                logger.warning(
                    f"Preferred terminal '{self.terminal_preference}' not found"
                )

        # Get preferred terminals for current DE
        de_terminals = self.DE_TERMINAL_MAP.get(
            self._desktop_environment or 'unknown',
            self.TERMINALS
        )

        # Check for remaining terminals
        for terminal in de_terminals:
            if terminal not in self._available_terminals:
                if shutil.which(terminal):
                    self._available_terminals.append(terminal)
                    logger.debug(f"Found terminal: {terminal}")

        # Set detected terminal
        if self._available_terminals:
            self._detected_terminal = self._available_terminals[0]
            logger.debug(f"Primary terminal: {self._detected_terminal}")
        else:
            logger.warning("No supported terminal emulators found")

    def _detect_shell(self) -> None:
        """Detect the user's preferred shell."""
        if self.shell_preference:
            # User has a shell preference
            if os.path.exists(self.shell_preference):
                self._user_shell = self.shell_preference
                logger.debug(f"Using preferred shell: {self._user_shell}")
                return
            else:
                logger.warning(
                    f"Preferred shell '{self.shell_preference}' not found"
                )

        # Check SHELL environment variable
        env_shell = os.environ.get('SHELL')
        if env_shell and os.path.exists(env_shell):
            self._user_shell = env_shell
            logger.debug(f"Using shell from environment: {self._user_shell}")
            return

        # Fallback to common shells
        for shell in self.SHELLS:
            if os.path.exists(shell):
                self._user_shell = shell
                logger.debug(f"Using fallback shell: {self._user_shell}")
                return

        # Last resort
        self._user_shell = '/bin/sh'
        logger.warning("Using /bin/sh as fallback shell")

    def is_available(self) -> bool:
        """Check if any terminal is available on this system."""
        return bool(self._detected_terminal)

    def get_available_terminals(self) -> Dict[str, any]:
        """Get information about available terminals on this system."""
        return {
            'available': self._available_terminals or [],
            'detected': self._detected_terminal,
            'supported': self.TERMINALS,
            'desktop_environment': self._desktop_environment,
            'user_shell': self._user_shell,
        }

    def set_terminal_preference(self, terminal: str) -> None:
        """Set the preferred terminal emulator."""
        if not shutil.which(terminal):
            raise ValueError(
                f"Terminal '{terminal}' not found. "
                f"Available: {self._available_terminals}"
            )
        self.terminal_preference = terminal
        self._detect_terminals()  # Re-detect with new preference
        logger.debug(f"Terminal preference set to: {terminal}")

    def get_terminal_command(self, directory: str, command: str) -> List[str]:
        """
        Get the Linux-specific command list for launching Claude.

        Args:
            directory: The working directory
            command: The command to execute

        Returns:
            A list of command arguments suitable for subprocess.Popen
        """
        if not self.is_available():
            raise TerminalNotFoundError(
                "No supported terminal emulator found. "
                "Please install one of: " + ", ".join(self.TERMINALS)
            )

        validated_dir = self._validate_directory(directory)
        validated_cmd = self._validate_command(command)

        return self._build_terminal_command(
            str(validated_dir),
            validated_cmd,
            self._detected_terminal,  # type: ignore
            self._user_shell  # type: ignore
        )

    def _build_terminal_command(self, directory: str, command: str,
                                terminal: str, shell: str) -> List[str]:
        """
        Build the terminal-specific command array.

        Args:
            directory: The working directory
            command: The command to execute
            terminal: The terminal emulator to use
            shell: The shell to use

        Returns:
            A list of command arguments
        """
        # Build the shell command string
        shell_cmd = self._build_shell_command(directory, command, shell)

        # Terminal-specific command arrays
        terminal_commands = {
            'gnome-terminal': [
                'gnome-terminal',
                '--working-directory', directory,
                '--', shell, '-c', shell_cmd
            ],
            'konsole': [
                'konsole',
                '--workdir', directory,
                '--hold',
                '-e', shell, '-c', shell_cmd
            ],
            'xfce4-terminal': [
                'xfce4-terminal',
                '--working-directory', directory,
                '-x', shell, '-c', shell_cmd
            ],
            'mate-terminal': [
                'mate-terminal',
                '--working-directory', directory,
                '-x', shell, '-c', shell_cmd
            ],
            'lxterminal': [
                'lxterminal',
                '--working-directory', directory,
                '-e', shell, '-c', shell_cmd
            ],
            'kitty': [
                'kitty',
                '--directory', directory,
                '--hold',
                shell, '-c', shell_cmd
            ],
            'alacritty': [
                'alacritty',
                '--working-directory', directory,
                '-e', shell, '-c', shell_cmd
            ],
            'xterm': [
                'xterm',
                '-e', shell, '-c', shell_cmd
            ],
        }

        return terminal_commands.get(
            terminal,
            terminal_commands['xterm']
        )

    def _build_shell_command(self, directory: str, command: str,
                             shell: str) -> str:
        """
        Build the shell command string for execution.

        Args:
            directory: The working directory
            command: The command to execute
            shell: The shell to use

        Returns:
            A shell command string
        """
        shell_name = os.path.basename(shell)

        # Escape directory and command
        # We use shlex.quote for proper escaping
        import shlex
        escaped_dir = shlex.quote(directory)
        escaped_cmd = shlex.quote(command)
        escaped_shell = shlex.quote(shell)

        if shell_name == 'fish':
            # Fish-specific syntax
            return f'cd {escaped_dir}; and {escaped_cmd}; exec {escaped_shell}'
        else:
            # Bash/zsh compatible syntax
            return f'cd {escaped_dir} && {escaped_cmd}; exec {escaped_shell}'

    def launch_claude(self, directory: str, command: str) -> None:
        """
        Launch Claude Code in a Linux terminal.

        Args:
            directory: The working directory where Claude should start
            command: The Claude command to execute

        Raises:
            TerminalNotFoundError: If no terminal is available
            LaunchFailedError: If the launch fails for any reason
        """
        if not self.is_available():
            raise TerminalNotFoundError(
                "No supported terminal emulator found. "
                "Please install one of: " + ", ".join(self.TERMINALS)
            )

        try:
            validated_dir = self._validate_directory(directory)
            validated_cmd = self._validate_command(command)

            terminal = self._detected_terminal  # type: ignore
            shell = self._user_shell  # type: ignore

            # Build the command array
            cmd = self._build_terminal_command(
                str(validated_dir),
                validated_cmd,
                terminal,
                shell
            )

            logger.info(f"Launching Claude in {terminal}: {directory}")
            logger.debug(f"Command: {' '.join(cmd)}")

            # Launch the terminal
            # For Linux terminals, we don't need special flags
            subprocess.Popen(cmd, start_new_session=True)

            logger.info("Terminal launched successfully")

        except FileNotFoundError as e:
            raise TerminalNotFoundError(
                f"Failed to launch terminal: {e.filename} not found"
            ) from e
        except subprocess.SubprocessError as e:
            raise LaunchFailedError(
                f"Failed to launch terminal: {e}"
            ) from e
        except Exception as e:
            raise LaunchFailedError(
                f"Unexpected error launching terminal: {e}"
            ) from e


__all__ = ["LinuxTerminalLauncher"]
```

### 5.2 Terminal-Specific Helper Class

```python
"""Terminal-specific command builders for Linux."""

import shlex
from typing import List, Dict
from abc import ABC, abstractmethod


class TerminalCommandBuilder(ABC):
    """Abstract base class for terminal-specific command builders."""

    @abstractmethod
    def build_command(self, directory: str, shell_cmd: str) -> List[str]:
        """Build the command array for this terminal."""
        pass


class GnomeTerminalBuilder(TerminalCommandBuilder):
    """Command builder for gnome-terminal."""

    def build_command(self, directory: str, shell_cmd: str) -> List[str]:
        return [
            'gnome-terminal',
            '--working-directory', directory,
            '--', 'bash', '-c', shell_cmd
        ]


class KonsoleBuilder(TerminalCommandBuilder):
    """Command builder for KDE Konsole."""

    def build_command(self, directory: str, shell_cmd: str) -> List[str]:
        return [
            'konsole',
            '--workdir', directory,
            '--hold',
            '-e', 'bash', '-c', shell_cmd
        ]


class XfceTerminalBuilder(TerminalCommandBuilder):
    """Command builder for XFCE Terminal."""

    def build_command(self, directory: str, shell_cmd: str) -> List[str]:
        return [
            'xfce4-terminal',
            '--working-directory', directory,
            '-x', 'bash', '-c', shell_cmd
        ]


class KittyBuilder(TerminalCommandBuilder):
    """Command builder for kitty terminal."""

    def build_command(self, directory: str, shell_cmd: str) -> List[str]:
        return [
            'kitty',
            '--directory', directory,
            '--hold',
            'bash', '-c', shell_cmd
        ]


class XtermBuilder(TerminalCommandBuilder):
    """Command builder for xterm (fallback)."""

    def build_command(self, directory: str, shell_cmd: str) -> List[str]:
        return [
            'xterm',
            '-e', 'bash', '-c', shell_cmd
        ]


# Registry of terminal builders
TERMINAL_BUILDERS: Dict[str, TerminalCommandBuilder] = {
    'gnome-terminal': GnomeTerminalBuilder(),
    'konsole': KonsoleBuilder(),
    'xfce4-terminal': XfceTerminalBuilder(),
    'mate-terminal': GnomeTerminalBuilder(),  # Same as gnome
    'lxterminal': GnomeTerminalBuilder(),     # Similar to gnome
    'kitty': KittyBuilder(),
    'alacritty': KittyBuilder(),              # Similar to kitty
    'xterm': XtermBuilder(),
}


def get_terminal_builder(terminal: str) -> TerminalCommandBuilder:
    """Get the command builder for a terminal."""
    return TERMINAL_BUILDERS.get(
        terminal,
        TERMINAL_BUILDERS['xterm']  # Fallback
    )
```

---

## 6. Recommended Implementation Strategy

### 6.1 Phase 1: Core Implementation
1. Implement basic terminal detection
2. Support gnome-terminal, konsole, xfce4-terminal
3. Add bash/zsh shell support
4. Implement proper command escaping

### 6.2 Phase 2: Enhanced Support
1. Add fish shell support
2. Add kitty and alacritty support
3. Desktop environment detection
4. Terminal preference storage

### 6.3 Phase 3: Advanced Features
1. Terminal profile support
2. Custom terminal configurations
3. Multi-terminal launch (tabs)
4. Terminal history integration

### 6.4 Testing Strategy

```python
"""Test cases for Linux terminal launcher."""

import pytest
from unittest.mock import patch, MagicMock
from app.platform.linux import LinuxTerminalLauncher


class TestLinuxTerminalLauncher:
    """Test suite for Linux terminal launcher."""

    def test_detect_desktop_environment_gnome(self):
        """Test detection of GNOME desktop environment."""
        with patch.dict('os.environ', {'XDG_CURRENT_DESKTOP': 'GNOME'}):
            launcher = LinuxTerminalLauncher()
            assert launcher._desktop_environment == 'gnome'

    def test_detect_desktop_environment_kde(self):
        """Test detection of KDE desktop environment."""
        with patch.dict('os.environ', {'XDG_CURRENT_DESKTOP': 'KDE'}):
            launcher = LinuxTerminalLauncher()
            assert launcher._desktop_environment in ['kde', 'plasma']

    def test_detect_terminals(self):
        """Test terminal detection."""
        with patch('shutil.which') as mock_which:
            # Mock available terminals
            mock_which.side_effect = lambda x: x in ['gnome-terminal', 'xterm']

            launcher = LinuxTerminalLauncher()
            assert 'gnome-terminal' in launcher._available_terminals
            assert 'xterm' in launcher._available_terminals

    def test_detect_shell(self):
        """Test shell detection."""
        with patch.dict('os.environ', {'SHELL': '/bin/bash'}):
            launcher = LinuxTerminalLauncher()
            assert launcher._user_shell == '/bin/bash'

    def test_build_shell_command_bash(self):
        """Test shell command building for bash."""
        launcher = LinuxTerminalLauncher()
        cmd = launcher._build_shell_command(
            '/home/user/project',
            'claude --continue',
            '/bin/bash'
        )
        assert 'cd' in cmd
        assert 'claude' in cmd
        assert 'exec' in cmd

    def test_build_shell_command_fish(self):
        """Test shell command building for fish shell."""
        launcher = LinuxTerminalLauncher()
        cmd = launcher._build_shell_command(
            '/home/user/project',
            'claude --continue',
            '/usr/bin/fish'
        )
        assert 'cd' in cmd
        assert '; and' in cmd  # Fish-specific syntax
        assert 'claude' in cmd

    def test_build_terminal_command_gnome(self):
        """Test command building for gnome-terminal."""
        launcher = LinuxTerminalLauncher()
        cmd = launcher._build_terminal_command(
            '/home/user/project',
            'claude --continue',
            'gnome-terminal',
            '/bin/bash'
        )
        assert cmd[0] == 'gnome-terminal'
        assert '--working-directory' in cmd

    def test_build_terminal_command_konsole(self):
        """Test command building for konsole."""
        launcher = LinuxTerminalLauncher()
        cmd = launcher._build_terminal_command(
            '/home/user/project',
            'claude --continue',
            'konsole',
            '/bin/bash'
        )
        assert cmd[0] == 'konsole'
        assert '--hold' in cmd

    def test_is_available(self):
        """Test availability check."""
        with patch('shutil.which') as mock_which:
            mock_which.return_value = '/usr/bin/gnome-terminal'
            launcher = LinuxTerminalLauncher()
            assert launcher.is_available()

    def test_is_available_no_terminal(self):
        """Test availability check with no terminals."""
        with patch('shutil.which') as mock_which:
            mock_which.return_value = None
            launcher = LinuxTerminalLauncher()
            assert not launcher.is_available()

    def test_get_terminal_command(self):
        """Test getting terminal command."""
        with patch('shutil.which') as mock_which:
            mock_which.return_value = '/usr/bin/gnome-terminal'
            launcher = LinuxTerminalLauncher()

            cmd = launcher.get_terminal_command(
                '/home/user/project',
                'claude --continue'
            )
            assert isinstance(cmd, list)
            assert len(cmd) > 0

    @patch('subprocess.Popen')
    def test_launch_claude(self, mock_popen):
        """Test launching Claude."""
        with patch('shutil.which') as mock_which:
            mock_which.return_value = '/usr/bin/gnome-terminal'
            launcher = LinuxTerminalLauncher()

            launcher.launch_claude('/home/user/project', 'claude --continue')

            assert mock_popen.called

    def test_set_terminal_preference(self):
        """Test setting terminal preference."""
        with patch('shutil.which') as mock_which:
            mock_which.return_value = '/usr/bin/konsole'
            launcher = LinuxTerminalLauncher()

            launcher.set_terminal_preference('konsole')

            assert launcher.terminal_preference == 'konsole'
            assert launcher._detected_terminal == 'konsole'

    def test_set_terminal_preference_not_found(self):
        """Test setting non-existent terminal preference."""
        with patch('shutil.which') as mock_which:
            mock_which.return_value = None
            launcher = LinuxTerminalLauncher()

            with pytest.raises(ValueError):
                launcher.set_terminal_preference('nonexistent-terminal')
```

---

## Summary of Key Findings

1. **Terminal Diversity**: Linux has many terminal emulators with different CLI syntax
2. **Desktop Environment Matters**: Terminal choice should be influenced by DE
3. **Shell Compatibility**: Fish shell requires different syntax than bash/zsh
4. **Security**: Use `shlex.quote()` for proper command escaping
5. **Hold Mechanism**: Different terminals use different flags to stay open
6. **Working Directory**: Most modern terminals support `--working-directory`

## Recommended Implementation

The recommended implementation above provides:
- Automatic terminal detection with DE awareness
- Shell detection with fish support
- Secure command escaping
- Comprehensive terminal support
- Fallback mechanisms
- Clean, maintainable code structure matching Windows implementation quality

## Testing Recommendations

1. Test on multiple Linux distributions (Ubuntu, Fedora, Arch, etc.)
2. Test with different desktop environments
3. Test with different shells (bash, zsh, fish)
4. Test command escaping with special characters
5. Test with various directory paths (spaces, special chars, etc.)
