# Linux Testing Quick Reference

## Quick Test Commands

### Run All Linux Tests
```bash
./tests/linux/run_local_tests.sh all
```

### Run Specific Test Categories
```bash
# Unit tests only
./tests/linux/run_local_tests.sh unit

# Integration tests only
./tests/linux/run_local_tests.sh integration

# Mock tests only
./tests/linux/run_local_tests.sh mock

# All Linux-specific tests
./tests/linux/run_local_tests.sh linux
```

### Check Dependencies
```bash
./tests/linux/run_local_tests.sh check
```

### Run with Virtual Display
```bash
./tests/linux/run_local_tests.sh xvfb
```

### Generate Coverage Report
```bash
./tests/linux/run_local_tests.sh coverage
```

---

## Smoke Tests (5-Minute Validation)

1. **Application starts**
   ```bash
   easyclaude
   ```
   Expected: System tray icon appears

2. **Hotkey works**
   Press: Ctrl+Alt+C
   Expected: GUI launcher opens

3. **Can launch terminal**
   - Select directory
   - Click Launch
   Expected: Terminal opens in selected directory

4. **Settings persist**
   - Change a setting
   - Restart app
   Expected: Setting remembered

---

## Critical Path Tests (15-Minute Validation)

1. **Install → Start → Launch → Exit**
   ```bash
   pip install -e .
   easyclaude
   # Press hotkey, select directory, launch
   # Exit from tray menu
   ```

2. **Terminal compatibility**
   - Test with gnome-terminal
   - Test with konsole
   - Test with xterm

3. **Desktop environment**
   - Test on GNOME
   - Test on KDE
   - Test on XFCE (if available)

4. **Path handling**
   - Standard path: `/home/user/project`
   - With spaces: `/home/user/my project`
   - Special chars: `/home/user/project(2024)`

---

## Bug Report Template

```markdown
## [Title]

**Severity**: Critical/High/Medium/Low
**Distribution**: [e.g., Ubuntu 22.04]
**Desktop Environment**: [e.g., GNOME 42]
**Terminal**: [e.g., gnome-terminal]
**Python Version**: [e.g., 3.11.2]

### Steps to Reproduce
1.
2.
3.

### Expected Behavior

### Actual Behavior

### Logs/Screenshots

### Additional Context
```

---

## Test Environment Setup

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-dev
sudo apt install -y gnome-terminal konsole xfce4-terminal xterm
pip3 install -e ".[dev]"
```

### Fedora
```bash
sudo dnf update
sudo dnf install -y python3 python3-pip python3-devel
sudo dnf install -y gnome-terminal konsole xfce4-terminal xterm
pip3 install -e ".[dev]"
```

### Arch
```bash
sudo pacman -Syu
sudo pacman -S python python-pip
sudo pacman -S gnome-terminal konsole xfce4-terminal xterm
pip install -e ".[dev]"
```

---

## Distribution Priority Matrix

| Priority | Distributions |
|----------|---------------|
| P0 (Must Test) | Ubuntu 22.04, Ubuntu 24.04 |
| P1 (Should Test) | Fedora 39, Fedora 40, Debian 12, Linux Mint |
| P2 (Nice to Have) | Arch Linux, Pop!_OS |
| P3 (If Time) | openSUSE, Manjaro |

---

## Desktop Environment Priority

| Priority | Desktop Environments |
|----------|---------------------|
| P0 | GNOME, KDE Plasma |
| P1 | XFCE, Cinnamon |
| P2 | MATE, LXQt |
| P3 | COSMIC, Pantheon, i3/Sway |

---

## Terminal Testing Priority

| Priority | Terminals |
|----------|-----------|
| P0 | gnome-terminal, konsole, xterm |
| P1 | xfce4-terminal, mate-terminal |
| P2 | alacritty, kitty |
| P3 | terminator, tilix, guake |

---

## Performance Benchmarks

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Cold start | < 2s | `time easyclaude` |
| Warm start | < 500ms | Start, exit, `time easyclaude` |
| Hotkey response | < 200ms | Manual test with stopwatch |
| Terminal launch | < 500ms | Manual test |
| Idle memory | < 50MB | `ps aux | grep easyclaude` |
| Idle CPU | < 1% | `top` or `htop` |

---

## Success Criteria

**Release is ready when:**
- [ ] All P0 distribution tests pass
- [ ] > 95% P1 tests pass
- [ ] > 90% DE tests pass (P0/P1 DEs)
- [ ] All performance benchmarks met
- [ ] Zero critical bugs
- [ ] < 5 high priority bugs
- [ ] Code coverage > 80%

---

## Common Issues and Solutions

### Issue: System tray icon not appearing
**Possible causes:**
- DE not supporting StatusNotifierItem
- Missing dependencies
**Solution:**
```bash
# For GNOME, may need extension
sudo apt install gnome-shell-extension-appindicator

# Check dependencies
./tests/linux/run_local_tests.sh check
```

### Issue: Hotkey not working
**Possible causes:**
- Another app using the hotkey
- Accessibility permissions
**Solution:**
- Change hotkey in settings
- Check system hotkey settings

### Issue: Terminal not opening
**Possible causes:**
- Terminal not installed
- Wrong terminal command
**Solution:**
```bash
# Check terminal availability
which gnome-terminal konsole xterm

# Install if missing
sudo apt install gnome-terminal
```

---

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/test-linux.yml`) runs:
- Unit tests on Python 3.10, 3.11, 3.12
- Integration tests
- Lint checks (pylint, mypy, flake8)
- Security scans (bandit, safety)
- Multi-distro tests (Ubuntu 22.04/24.04, Debian 12)

---

## Test Files Structure

```
tests/
├── platform/
│   ├── test_linux.py              # Unit tests
│   ├── test_linux_integration.py  # Integration tests
│   └── test_linux_desktop.py      # Desktop mock tests
├── linux/
│   ├── TESTING_STRATEGY.md        # Full test strategy
│   ├── TEST_TRACKING.md           # Test tracking template
│   ├── QUICK_REFERENCE.md         # This file
│   └── run_local_tests.sh         # Test runner script
└── conftest.py                    # Shared fixtures
```

---

## Getting Help

- **Full testing strategy**: See `TESTING_STRATEGY.md`
- **Test tracking**: Use `TEST_TRACKING.md` template
- **Run tests**: Use `run_local_tests.sh`
- **CI issues**: Check GitHub Actions tab

---

## Quick Test Scenarios

### Scenario 1: Basic Workflow (2 minutes)
1. Start EasyClaude
2. Press Ctrl+Alt+C
3. Select ~/Documents
4. Click Launch
5. Verify terminal opens in ~/Documents

### Scenario 2: Settings (2 minutes)
1. Open EasyClaude
2. Change hotkey to Ctrl+Alt+D
3. Change terminal to konsole
4. Restart EasyClaude
5. Verify settings persist

### Scenario 3: Edge Cases (3 minutes)
1. Try launching in `/root` (expect error)
2. Try path with spaces: `/tmp/test dir`
3. Try non-existent path
4. Verify appropriate error messages

---

**Last Updated**: 2026-02-08
**Version**: 1.0
