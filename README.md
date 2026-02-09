# EasyClaude

> A cross-platform system tray application for launching Claude Code from any directory via global hotkey.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

## Overview

EasyClaude runs silently in your system tray, ready to launch Claude Code in any directory with a single global hotkey press. No more navigating through terminal windows or searching for the right directory.

## Features

- **Global Hotkey**: Press `Ctrl+Alt+C` to instantly open the launcher
- **Cross-Platform**: Support for Windows and Linux
- **Directory Selection**: Native folder picker or manual path entry
- **Quick Commands**: One-click access to common Claude commands
- **Configuration Persistence**: Remembers your last directory and preferences
- **Always-On-Top**: Launcher GUI appears above other windows
- **System Tray**: Minimal presence with easy access to all features
- **Terminal Detection**: Automatically detects and uses your preferred terminal

## Quick Start

### Prerequisites

1. **Python 3.10 or higher** installed
2. **Claude Code CLI** installed and in your PATH:

```bash
npm install -g @anthropic-ai/claude-code
```

Verify installation: `claude --version`

### Installation

#### Windows

**Option 1: Executable (Recommended)**

Download `EasyClaude.exe` from the [Releases](https://github.com/AhmadHanif12/EasyClaude/releases) page and run it.

**Option 2: From Source**

```powershell
git clone https://github.com/AhmadHanif12/EasyClaude.git
cd EasyClaude
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

#### Linux

**Option 1: From PyPI (Recommended)**

```bash
pip install easyclaude[linux]
easyclaude
```

**Option 2: From Source**

```bash
git clone https://github.com/AhmadHanif12/EasyClaude.git
cd EasyClaude
python -m venv venv
source venv/bin/activate
pip install -e ".[linux]"
python -m app.main
```

**Linux Dependencies**

EasyClaude requires the following system packages on Linux:

- Debian/Ubuntu: `sudo apt install python3-cairo python3-xlib libgirepository1.0-dev`
- Fedora: `sudo dnf install python3-cairo python3-xlib gobject-introspection-devel`
- Arch: `sudo pacman -S python-cairo python-xlib gobject-introspection`

For system tray integration on GNOME, install the [AppIndicator Extension](https://extensions.gnome.org/extension/615/appindicator-kstatusnotifier-item/).

### First Run

1. Launch EasyClaude - it will appear in your system tray
2. Press `Ctrl+Alt+C` to open the launcher
3. Select your project directory
4. Click a command button to launch Claude

### Usage

#### Launching Claude

1. Press `Ctrl+Alt+C` (or your configured hotkey)
2. The launcher GUI appears centered on your screen
3. Choose a directory:
   - Click "Browse..." to use the folder picker
   - Type or paste a path directly
4. Click a command:
   - **claude** - Standard launch
   - **claude --continue** - Continue last session
   - **claude --dangerously-skip-permissions** - Skip permission prompts
5. Claude opens in a new terminal window

#### Tray Menu

Right-click the tray icon for:
- **Launch Claude** - Open the launcher GUI
- **Configure** - View current configuration
- **Exit** - Close EasyClaude

## Configuration

Configuration is stored at:
- **Windows**: `C:\Users\YourName\.easyclaude\config.json`
- **Linux**: `~/.easyclaude/config.json`

```json
{
  "hotkey": "ctrl+alt+c",
  "last_directory": "/home/user/projects",
  "last_command": "claude",
  "always_use_powershell": false,
  "window_position": "center"
}
```

### Changing the Hotkey

Edit the `hotkey` field in `config.json`. Supported formats:

- `ctrl+alt+c` - Ctrl + Alt + C
- `ctrl+shift+z` - Ctrl + Shift + Z
- `win+e` - Windows/Super Key + E
- `alt+f4` - Alt + F4

Modifiers: `ctrl`, `alt`, `shift`, `win`, `cmd`

## Platform-Specific Information

### Windows

- **Terminals**: PowerShell, CMD, Windows Terminal
- **Autostart**: Add shortcut to `shell:startup` folder
- **Tray Icon**: Native Windows system tray

### Linux

**Supported Desktop Environments:**
- GNOME (with AppIndicator extension)
- KDE Plasma
- XFCE
- MATE
- LXDE/LXQt
- Cinnamon

**Supported Terminals:**
- gnome-terminal
- konsole
- xfce4-terminal
- mate-terminal
- lxterminal
- kitty
- alacritty
- xterm (fallback)

**Autostart on Linux:**

To enable autostart, copy the desktop file:

```bash
mkdir -p ~/.config/autostart
cp assets/easyclaude-autostart.desktop ~/.config/autostart/
```

Or enable it through your desktop environment's autostart settings.

**Known Limitations:**

- **Wayland**: Global hotkeys may not work due to Wayland's security model. Consider using X11 or a DBus-based hotkey daemon.
- **GNOME 40+**: The system tray is hidden by default. Install the AppIndicator extension to see the tray icon.

## Building from Source

### Windows

```bash
pip install pyinstaller
pyinstaller easyclaude.spec
```

The executable will be in `dist/EasyClaude.exe`.

### Linux

```bash
pip install pyinstaller
pyinstaller easyclaude_linux.spec
```

The executable will be in `dist/EasyClaude`.

## Development

### Project Structure

```
EasyClaude/
├── app/
│   ├── __init__.py
│   ├── main.py           # Entry point
│   ├── config.py         # Configuration management
│   ├── hotkey.py         # Global hotkey (pynput)
│   ├── tray.py           # System tray (pystray)
│   ├── gui.py            # Launcher GUI (tkinter)
│   ├── launcher.py       # Claude execution wrapper
│   ├── single_instance.py # Single-process enforcement
│   └── platform/         # Platform abstraction
│       ├── __init__.py
│       ├── windows.py    # Windows implementation
│       ├── linux.py      # Linux implementation
│       └── macos.py      # macOS stub (future)
├── tests/
│   ├── test_config.py
│   ├── test_hotkey.py
│   └── test_launcher.py
├── assets/
│   ├── icon.ico          # Windows icon
│   ├── icon.png          # Linux icon
│   ├── easyclaude.desktop        # Linux app launcher
│   └── easyclaude-autostart.desktop  # Linux autostart
├── easyclaude.spec       # Windows PyInstaller spec
├── easyclaude_linux.spec # Linux PyInstaller spec
├── README.md
├── requirements.txt
└── pyproject.toml
```

### Running Tests

```bash
pytest tests/ -v
```

### Running with Coverage

```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

## Troubleshooting

### Hotkey Not Working

- Check if another application is using the same hotkey
- Verify `config.json` has a valid hotkey format
- Restart EasyClaude after changing configuration
- **Linux/Wayland**: Global hotkeys may not work; consider using X11

### Claude Not Found

- Ensure Claude Code is installed: `claude --version`
- Check that Claude is in your system PATH
- Try launching Claude manually first to verify installation

### Terminal Window Closes Immediately

- Check Claude's error output for issues
- Verify directory path is valid
- Ensure directory has proper permissions

### Linux: Tray Icon Not Visible

- **GNOME**: Install the AppIndicator extension
- Check that pycairo and python-xlib are installed
- Verify EasyClaude is running: `ps aux | grep easyclaude`

### Linux: Hotkey Not Working on Wayland

- Wayland's security model prevents global hotkey listening
- Consider using X11 session instead
- Or use a DBus-based hotkey daemon

## Roadmap

### Phase 1: Core Features (Current)
- [x] Windows system tray integration
- [x] Windows global hotkey support
- [x] Linux terminal launcher
- [x] Linux desktop integration
- [x] GUI launcher
- [x] Configuration persistence

### Phase 2: Enhanced Features
- [ ] Cross-platform autostart management
- [ ] Settings GUI
- [ ] Recent directories quick-list
- [ ] Custom command templates
- [ ] Multiple Claude sessions

### Phase 3: Future Platforms
- [ ] macOS Terminal.app support
- [ ] AppImage/Flatpak distributions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
git clone https://github.com/AhmadHanif12/EasyClaude.git
cd EasyClaude
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e ".[dev]"
pre-commit install
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [pystray](https://github.com/moses-palmer/pystray) for system tray functionality
- [pynput](https://github.com/moses-palmer/pynput) for global hotkey support
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) by Anthropic

## Support

- **Issues**: [GitHub Issues](https://github.com/AhmadHanif12/EasyClaude/issues)
- **Discussions**: [GitHub Discussions](https://github.com/AhmadHanif12/EasyClaude/discussions)

---

Made with ❤️ for the developer community
