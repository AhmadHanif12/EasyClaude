# EasyClaude

> A Windows system tray application for launching Claude Code from any directory via global hotkey.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

## Overview

EasyClaude runs silently in your system tray, ready to launch Claude Code in any directory with a single global hotkey press. No more navigating through terminal windows or searching for the right directory.

## Features

- **Global Hotkey**: Press `Ctrl+Alt+C` to instantly open the launcher
- **Directory Selection**: Native folder picker or manual path entry
- **Quick Commands**: One-click access to common Claude commands
- **PowerShell Support**: Optional PowerShell for Claude execution
- **Configuration Persistence**: Remembers your last directory and preferences
- **Always-On-Top**: Launcher GUI appears above other windows
- **System Tray**: Minimal presence with easy access to all features

## Quick Start

### Installation

#### Option 1: From Source

```bash
git clone https://github.com/AhmadHanif12/EasyClaude.git
cd EasyClaude
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

#### Option 2: Executable

Download `EasyClaude.exe` from the [Releases](https://github.com/AhmadHanif12/EasyClaude/releases) page and run it.

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
5. Optionally check "Always use PowerShell"
6. Claude opens in a new terminal window

#### Tray Menu

Right-click the tray icon for:
- **Launch Claude** - Open the launcher GUI
- **Configure** - View current configuration
- **Exit** - Close EasyClaude

## Configuration

Configuration is stored at `~/.easyclaude/config.json`:

```json
{
  "hotkey": "ctrl+alt+c",
  "last_directory": "C:\Users\YourName\Projects",
  "last_command": "claude",
  "always_use_powershell": false,
  "window_position": "center"
}
```

### Changing the Hotkey

Edit the `hotkey` field in `config.json`. Supported formats:

- `ctrl+alt+c` - Ctrl + Alt + C
- `ctrl+shift+z` - Ctrl + Shift + Z
- `win+e` - Windows Key + E
- `alt+f4` - Alt + F4

Modifiers: `ctrl`, `alt`, `shift`, `win`, `cmd`

## Requirements

- Python 3.10 or higher
- Windows 10/11 (primary target)
- Claude Code CLI installed and in PATH

### Installing Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

See [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code) for details.

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
│   └── platform/         # Platform abstraction
│       ├── __init__.py
│       ├── windows.py    # Windows implementation
│       ├── linux.py      # Linux stub (Phase 2)
│       └── macos.py      # macOS stub (Phase 2)
├── tests/
│   ├── test_config.py
│   ├── test_hotkey.py
│   └── test_launcher.py
├── assets/
│   └── icon.ico
├── build/
│   └── build.spec        # PyInstaller spec
├── CLAUDE.md
├── README.md
├── requirements.txt
└── pyproject.toml
```

### Running Tests

```bash
pytest tests/ -v
```

### Building Executable

```bash
pyinstaller build/build.spec
```

The executable will be in `dist/EasyClaude.exe`.

### Creating an Autostart Shortcut

To start EasyClaude automatically on Windows login:

1. Press `Win + R`, type `shell:startup`, and press Enter
2. Create a shortcut to `EasyClaude.exe` in the Startup folder
3. EasyClaude will now start automatically when you log in

## Troubleshooting

### Hotkey Not Working

- Check if another application is using the same hotkey
- Verify `config.json` has a valid hotkey format
- Restart EasyClaude after changing configuration

### Claude Not Found

- Ensure Claude Code is installed: `claude --version`
- Check that Claude is in your system PATH
- Try launching Claude manually first to verify installation

### PowerShell Issues

- Ensure PowerShell is available: `powershell.exe -Version`
- Check execution policy: `Get-ExecutionPolicy`
- If restricted, consider using CMD instead

### Terminal Window Closes Immediately

- Check Claude's error output for issues
- Verify directory path is valid
- Ensure directory has proper permissions

## Roadmap

### Phase 1: Windows (Current)
- [x] System tray integration
- [x] Global hotkey support
- [x] GUI launcher
- [x] Configuration persistence
- [x] PowerShell support
- [ ] Windows autostart installer
- [ ] Settings GUI

### Phase 2: Cross-Platform
- [ ] Linux terminal support
- [ ] macOS Terminal.app support
- [ ] Platform-specific packaging

### Phase 3: Enhanced Features
- [ ] Recent directories quick-list
- [ ] Custom command templates
- [ ] Multiple Claude sessions
- [ ] Integration with Claude's project management

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [pystray](https://github.com/moses-palmer/pystray) for system tray functionality
- [pynput](https://github.com/moses-palmer/pynput) for global hotkey support
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) by Anthropic

## Support

- **Issues**: [GitHub Issues](https://github.com/AhmadHanif12/EasyClaude/issues)
- **Discussions**: [GitHub Discussions](https://github.com/AhmadHanif12/EasyClaude/discussions)

---

Made with ❤️ for the developer community
