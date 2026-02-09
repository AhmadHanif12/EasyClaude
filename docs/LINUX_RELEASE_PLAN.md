# EasyClaude Linux Release Plan

## Executive Summary

This plan outlines the comprehensive strategy for releasing EasyClaude on Linux, ensuring feature parity with the Windows version and a smooth user experience across all major Linux distributions and desktop environments.

## Table of Contents

1. [Current Status](#current-status)
2. [Feature Compatibility Matrix](#feature-compatibility-matrix)
3. [Implementation Plan](#implementation-plan)
4. [Packaging Strategy](#packaging-strategy)
5. [Desktop Environment Integration](#desktop-environment-integration)
6. [Testing Strategy](#testing-strategy)
7. [Release Roadmap](#release-roadmap)
8. [Post-Release Maintenance](#post-release-maintenance)

---

## Current Status

### What Works (Windows)
- System tray icon with menu (pystray)
- Global hotkey registration (pynput)
- Terminal launching (PowerShell/Windows Terminal)
- Autostart via Windows Startup folder
- GUI launcher dialog (tkinter)

### What Needs Implementation (Linux)
- Complete `LinuxTerminalLauncher` class (currently a stub)
- Desktop entry file for application launcher
- Autostart `.desktop` file for `$XDG_CONFIG_HOME/autostart`
- Verify pystray/pynput Linux compatibility
- Add Linux-specific dependencies

---

## Feature Compatibility Matrix

| Windows Feature | Linux Equivalent | Implementation Notes |
|----------------|------------------|---------------------|
| System Tray | AppIndicator/libappindicator | pystray has Linux support via pycairo |
| Global Hotkey | pynput keyboard.Listener | Works on Linux with X11/Wayland considerations |
| PowerShell Launcher | Terminal emulator | Support gnome-terminal, konsole, xfce4-terminal, etc. |
| Windows Terminal | Native terminal | Auto-detect DE and use appropriate terminal |
| Startup Folder | XDG autostart | `.desktop` file in `~/.config/autostart/` |
| GUI | tkinter | Fully compatible on Linux |

---

## Implementation Plan

### Phase 1: Core Linux Terminal Launcher (Week 1)

**File: `app/platform/linux.py`**

Replace the stub implementation with full functionality.

**Key Implementation Details:**
1. Desktop environment detection via `XDG_CURRENT_DESKTOP`
2. Terminal auto-detection with `shutil.which()`
3. Shell detection (bash/zsh/fish) with proper syntax
4. Secure command escaping with `shlex.quote()`
5. Terminal-specific command arrays

### Phase 2: Desktop Integration (Week 1-2)

**Create: `assets/easyclaude.desktop`**

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=EasyClaude
Comment=Launch Claude Code from any directory
Exec=easyclaude
Icon=easyclaude
Terminal=false
Categories=Development;Utility;
Keywords=Claude;AI;Terminal;
StartupNotify=true
```

**Create: `assets/easyclaude-autostart.desktop`**

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=EasyClaude
Comment=System tray launcher for Claude Code
Exec=easyclaude --hidden
X-GNOME-Autostart-enabled=true
X-KDE-autostart-after=panel
X-MATE-Autostart-enabled=true
```

**Create: `app/autostart_linux.py`**

```python
"""Linux autostart setup for EasyClaude."""

import os
from pathlib import Path
from xdg import xdg_config_home

AUTOSTART_DIR = xdg_config_home() / "autostart"
AUTOSTART_FILE = AUTOSTART_DIR / "easyclaude-autostart.desktop"

def enable_autostart() -> bool:
    """Create autostart entry in XDG autostart directory."""
    pass

def disable_autostart() -> bool:
    """Remove autostart entry."""
    pass

def is_autostart_enabled() -> bool:
    """Check if autostart is enabled."""
    return AUTOSTART_FILE.exists()
```

### Phase 3: Dependencies & Configuration (Week 2)

**Update: `pyproject.toml`**

```toml
[project]
name = "easyclaude"
version = "0.2.0"
description = "System tray launcher for Claude Code (Windows & Linux)"

classifiers = [
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX :: Linux",
    "Operating System :: MacOS",
]

dependencies = [
    "pystray>=0.19.5",
    "pynput>=1.7.6",
    "pydantic>=2.5.0",
    "pycairo>=1.23.0",      # Linux: for pystray
    "python-xlib>=0.33",    # Linux: for pystray/pynput
]

[project.optional-dependencies]
linux = [
    "pycairo>=1.23.0",
    "python-xlib>=0.33",
    "pygobject>=3.44.0",  # For AppIndicator
]
windows = [
    "pywin32>=305",
]
```

---

## Packaging Strategy

### Phase 1: AppImage (Week 2-3)

**Why AppImage First?**
- Universal distribution format
- No approval process
- Easy testing and feedback collection
- Good for early adopters

**Create: `AppImageBuilder.yml`**

```yaml
version: 1
AppDir:
  path: /AppDir
  app_info:
    id: com.easyclaude.app
    name: EasyClaude
    icon: easyclaude
    version: 0.2.0
    exec: usr/bin/python3 -m app.main
    exec_args: $@
  files:
    include:
    - app/
    - assets/
    exclude:
    - __pycache__
    - "*.pyc"
    - tests/
  runtime:
    env:
      PYTHONPATH: ${APPDIR}/usr/lib/python${PY_VERSION}/site-packages:${APPDIR}
```

**GitHub Actions Workflow: `.github/workflows/build-appimage.yml`**

```yaml
name: Build AppImage

on: [push, pull_request]

jobs:
  appimage:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v3
      - name: Build AppImage
        run: |
          sudo apt install appimage-builder
          appimage-builder --recipe AppImageBuilder.yml
      - name: Upload Artifact
        uses: actions/upload-artifact@v3
        with:
          name: EasyClaude-x86_64.AppImage
          path: "*.AppImage"
```

### Phase 2: Flatpak (Week 4-6)

**Why Flatpak?**
- Flathub provides massive distribution
- Automatic updates
- Better desktop integration
- Proper permissions handling

**Create: `com.easyclaude.app.yml`**

```yaml
app-id: com.easyclaude.app
runtime: org.freedesktop.Platform
runtime-version: "23.08"
sdk: org.freedesktop.Sdk
command: easyclaude

finish-args:
  - --share=ipc
  - --socket=x11
  - --socket=fallback-x11
  - --socket=wayland
  - --device=dri
  - --filesystem=host
  - --talk-name=org.freedesktop.Notifications

modules:
  - name: python3-pynput
    buildsystem: simple
    build-commands:
      - pip3 install --prefix=/app pynput

  - name: easyclaude
    buildsystem: simple
    build-commands:
      - pip3 install --prefix=/app .
      - install -Dm644 assets/easyclaude.desktop /app/share/applications/com.easyclaude.app.desktop
      - install -Dm644 assets/easyclaude.png /app/share/icons/hicolor/256x256/apps/com.easyclaude.app.png
    sources:
      - type: dir
        path: .
```

### Phase 3: PyPI (Week 4)

**Why PyPI?**
- Easy installation: `pip install easyclaude`
- Works with virtual environments
- Complements native packages

### Phase 4: Community Packages (Week 5+)

- **AUR**: Create PKGBUILD template, let community maintain
- **Debian/Ubuntu**: Document packaging process
- **Fedora**: Community contributions welcome

---

## Desktop Environment Integration

### System Tray / AppIndicator

**Current Dependencies:**
- `pystray` - Has Linux support via `pycairo` and `python-xlib`
- Works with X11 and most Wayland compositors

**Potential Issues:**
- GNOME 40+ removed legacy tray support
- Requires AppIndicator extension for GNOME

**Recommendations:**
1. Document AppIndicator requirement for GNOME users
2. Consider adding AppIndicator detection
3. Provide fallback instructions for unsupported DEs

### Global Hotkeys

**Current Dependencies:**
- `pynput` - Works on Linux with X11
- Wayland support is limited due to security model

**Recommendations:**
1. For Wayland: Document that global hotkeys may not work
2. Consider adding DBus-based hotkey registration for Wayland
3. Fallback to manual launcher for Wayland users

### Autostart

**Implementation:**
- Create `.desktop` file in `~/.config/autostart/`
- Follow XDG autostart specification
- Support enabling/disabling via tray menu

---

## Testing Strategy

### Testing Matrix

| Distribution | Version | DE | Terminal | Python |
|--------------|---------|-------|----------|---------|
| Ubuntu | 22.04, 24.04 | GNOME | gnome-terminal | 3.10, 3.11, 3.12 |
| Fedora | 39, 40 | GNOME/KDE | gnome-terminal/konsole | 3.12 |
| Arch | Rolling | KDE/XFCE | konsole/xfce4-terminal | 3.12 |
| Debian | 12 | GNOME/MATE | gnome-terminal/mate-terminal | 3.11 |
| Linux Mint | 21 | Cinnamon | gnome-terminal | 3.10 |

### Test Cases

**Core Functionality:**
1. [ ] System tray icon appears
2. [ ] Tray menu items work (Launch, Configure, Exit)
3. [ ] Global hotkey registers and triggers
4. [ ] Terminal launches in correct directory
5. [ ] Terminal stays open after command
6. [ ] Autostart works after reboot
7. [ ] GUI dialog opens and closes properly

**Terminal-Specific:**
1. [ ] gnome-terminal launches correctly
2. [ ] konsole launches correctly
3. [ ] xfce4-terminal launches correctly
4. [ ] xterm fallback works

**Shell Compatibility:**
1. [ ] bash commands execute correctly
2. [ ] zsh commands execute correctly
3. [ ] fish syntax is handled (if implemented)

**Error Handling:**
1. [ ] Graceful handling when no terminal found
2. [ ] Proper error messages for invalid directories
3. [ ] App doesn't crash on missing dependencies

---

## Release Roadmap

### Week 1-2: Core Implementation
- [ ] Complete `LinuxTerminalLauncher` implementation
- [ ] Create desktop entry files
- [ ] Implement Linux autostart
- [ ] Update dependencies in `pyproject.toml`
- [ ] Manual testing on Ubuntu 22.04

### Week 3-4: AppImage Build
- [ ] Create AppImageBuilder configuration
- [ ] Set up GitHub Actions workflow
- [ ] Test AppImage on multiple distributions
- [ ] Create GitHub Release with AppImage
- [ ] Add Linux documentation to README

### Week 5-6: Flatpak & PyPI
- [ ] Create Flatpak manifest
- [ ] Test Flatpak build locally
- [ ] Submit to Flathub
- [ ] Publish to PyPI
- [ ] Update installation documentation

### Week 7-8: Testing & Polish
- [ ] Test on all major distributions
- [ ] Fix reported bugs
- [ ] Performance optimization
- [ ] Final documentation updates

### Week 9: Public Release
- [ ] Announce on GitHub
- [ ] Post on Reddit (r/linux, r/python)
- [ ] Submit to listing sites (AlternativeTo, etc.)
- [ ] Monitor for issues and feedback

---

## Post-Release Maintenance

### Ongoing Tasks
1. Monitor GitHub issues for Linux-specific bugs
2. Update dependencies as needed
3. Add support for new terminal emulators
4. Address Wayland compatibility improvements
5. Respond to user feedback

### Metrics to Track
1. Download counts (AppImage, Flatpak, PyPI)
2. Bug reports by distribution/DE
3. User feature requests
4. Community contributions

---

## File Structure Changes

```
EasyClaude/
├── app/
│   ├── platform/
│   │   ├── __init__.py         # Platform detection
│   │   ├── windows.py          # Windows (existing)
│   │   ├── linux.py            # Linux (to be completed)
│   │   └── macos.py            # macOS (stub, future)
│   ├── autostart.py            # Windows autostart (existing)
│   └── autostart_linux.py      # Linux autostart (new)
├── assets/
│   ├── easyclaude.desktop      # App launcher (new)
│   ├── easyclaude-autostart.desktop  # Autostart (new)
│   └── icon.png                # App icon (needed)
├── .github/
│   └── workflows/
│       ├── build-appimage.yml  # AppImage build (new)
│       └── build-flatpak.yml   # Flatpak build (new)
├── AppImageBuilder.yml         # AppImage config (new)
├── com.easyclaude.app.yml      # Flatpak manifest (new)
└── pyproject.toml              # Updated for Linux (modify)
```

---

## Dependencies Summary

### New Linux-Specific Dependencies
```
pycairo>=1.23.0         # For pystray Linux support
python-xlib>=0.33       # For X11 integration
pygobject>=3.44.0       # For AppIndicator (optional but recommended)
```

### Cross-Platform (Existing)
```
pystray>=0.19.5         # Works on Linux with additional deps
pynput>=1.7.6           # Works on Linux with X11
pydantic>=2.5.0         # Fully cross-platform
```

---

## Success Criteria

The Linux release will be considered successful when:

1. **Feature Parity**: All Windows features work on Linux
2. **Distribution Support**: AppImage works on at least 3 major distros
3. **Performance**: Hotkey response < 100ms, startup < 1s
4. **Stability**: No crashes in normal usage
5. **Documentation**: Clear installation and usage instructions
6. **Feedback**: Positive user feedback and low bug rate

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Wayland hotkey issues | High | Medium | Document limitations, explore DBus alternative |
| GNOME tray removal | High | Low | Recommend AppIndicator extension |
| Terminal fragmentation | Medium | Medium | Support top 5 terminals + fallback |
| Flatpak rejection | Low | Medium | Follow guidelines closely, iterate |
| Maintenance burden | Medium | High | Community packaging, clear contribution guide |

---

## Terminal Emulator Reference

### Supported Terminals

| Terminal | Command | Working Directory | Hold Open |
|----------|---------|-------------------|-----------|
| gnome-terminal | `--working-directory DIR -- shell -c "cmd; exec shell"` | `--working-directory` | `exec shell` |
| konsole | `--workdir DIR --hold -e shell -c "cmd"` | `--workdir` | `--hold` |
| xfce4-terminal | `--working-directory DIR -x shell -c "cmd; exec shell"` | `--working-directory` | `exec shell` |
| mate-terminal | `--working-directory DIR -x shell -c "cmd; exec shell"` | `--working-directory` | `exec shell` |
| kitty | `--directory DIR --hold shell -c "cmd; exec shell"` | `--directory` | `--hold` |
| alacritty | `--working-directory DIR -e shell -c "cmd; exec shell"` | `--working-directory` | `exec shell` |
| xterm | `-e shell -c "cd DIR && cmd; exec shell"` | use `cd` | `exec shell` |

### Shell Syntax

| Shell | Command Chaining | Example |
|-------|------------------|---------|
| bash | `&&` and `;` | `cd /path && cmd; exec bash` |
| zsh | `&&` and `;` | `cd /path && cmd; exec zsh` |
| fish | `; and` | `cd /path; and cmd; exec fish` |

---

*Document Version: 1.0*
*Last Updated: 2025-02-08*
