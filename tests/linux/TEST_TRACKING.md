# Linux Test Tracking Template

## Test Execution Tracking

### Distribution Testing Status

| Distribution | Version | DE | Terminal | Python | Status | Date Tested | Tester | Notes |
|--------------|---------|----|----|--------|--------|-------------|--------|-------|
| Ubuntu | 22.04 | GNOME | gnome-terminal | 3.11 | ☐ | | | |
| Ubuntu | 22.04 | GNOME | konsole | 3.11 | ☐ | | | |
| Ubuntu | 24.04 | GNOME | gnome-terminal | 3.12 | ☐ | | | |
| Fedora | 39 | GNOME | gnome-terminal | 3.11 | ☐ | | | |
| Fedora | 40 | KDE | konsole | 3.12 | ☐ | | | |
| Debian | 12 | GNOME | gnome-terminal | 3.11 | ☐ | | | |
| Linux Mint | 21 | Cinnamon | gnome-terminal | 3.11 | ☐ | | | |

### Feature Testing Checklist

#### Installation

| Test Case | Ubuntu 22.04 | Ubuntu 24.04 | Fedora 39 | Debian 12 | Mint 21 |
|-----------|--------------|--------------|-----------|-----------|---------|
| pip install from source | ☐ | ☐ | ☐ | ☐ | ☐ |
| pip install from package | ☐ | ☐ | ☐ | ☐ | ☐ |
| First launch works | ☐ | ☐ | ☐ | ☐ | ☐ |
| Config created correctly | ☐ | ☐ | ☐ | ☐ | ☐ |

#### System Tray

| Test Case | GNOME | KDE | XFCE | Cinnamon |
|-----------|-------|-----|------|----------|
| Icon appears | ☐ | ☐ | ☐ | ☐ |
| Icon visible dark theme | ☐ | ☐ | ☐ | ☐ |
| Icon visible light theme | ☐ | ☐ | ☐ | ☐ |
| Right-click menu works | ☐ | ☐ | ☐ | ☐ |
| All menu items present | ☐ | ☐ | ☐ | ☐ |
| Menu items functional | ☐ | ☐ | ☐ | ☐ |

#### Hotkeys

| Test Case | Result | Notes |
|-----------|--------|-------|
| Default hotkey (Ctrl+Alt+C) | ☐ | |
| Custom hotkey set | ☐ | |
| Hotkey with app minimized | ☐ | |
| Hotkey with other app focused | ☐ | |
| Hotkey response time < 200ms | ☐ | |

#### Terminal Launching

| Terminal | Detects | Launches | Working Dir | Special Chars |
|----------|---------|----------|-------------|---------------|
| gnome-terminal | ☐ | ☐ | ☐ | ☐ |
| konsole | ☐ | ☐ | ☐ | ☐ |
| xfce4-terminal | ☐ | ☐ | ☐ | ☐ |
| mate-terminal | ☐ | ☐ | ☐ | ☐ |
| lxterminal | ☐ | ☐ | ☐ | ☐ |
| xterm | ☐ | ☐ | ☐ | ☐ |

#### GUI Launcher

| Test Case | GNOME | KDE | XFCE | Cinnamon |
|-----------|-------|-----|------|----------|
| Window opens centered | ☐ | ☐ | ☐ | ☐ |
| Dark theme compatible | ☐ | ☐ | ☐ | ☐ |
| Light theme compatible | ☐ | ☐ | ☐ | ☐ |
| Directory picker works | ☐ | ☐ | ☐ | ☐ |
| History dropdown works | ☐ | ☐ | ☐ | ☐ |
| Launch button works | ☐ | ☐ | ☐ | ☐ |
| Cancel/ESC works | ☐ | ☐ | ☐ | ☐ |

#### Directory Handling

| Path Type | Result | Notes |
|-----------|--------|-------|
| Standard (/home/user) | ☐ | |
| With spaces | ☐ | |
| With special chars ()[]) | ☐ | |
| Unicode characters | ☐ | |
| Home shortcut (~) | ☐ | |
| Relative paths | ☐ | |
| Deep nesting | ☐ | |

#### Settings Persistence

| Setting | Persists | Notes |
|---------|----------|-------|
| Hotkey preference | ☐ | |
| Terminal preference | ☐ | |
| Window position | ☐ | |
| Last directory | ☐ | |
| Last command | ☐ | |
| Autostart enabled | ☐ | |

#### Error Handling

| Scenario | Handled Gracefully | Notes |
|----------|-------------------|-------|
| No terminal available | ☐ | |
| Invalid directory | ☐ | |
| Permission denied | ☐ | |
| Claude not in PATH | ☐ | |
| Corrupted config | ☐ | |

#### Performance

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Cold start time | < 2s | | ☐ |
| Warm start time | < 500ms | | ☐ |
| Hotkey response | < 200ms | | ☐ |
| Terminal launch | < 500ms | | ☐ |
| Idle memory | < 50MB | | ☐ |
| Idle CPU | < 1% | | ☐ |

#### Accessibility

| Feature | Works | Notes |
|---------|-------|-------|
| Keyboard navigation | ☐ | |
| Screen reader compatible | ☐ | |
| High contrast mode | ☐ | |
| Font scaling | ☐ | |
| Color blindness | ☐ | |

---

## Bug Tracking

| ID | Severity | Summary | Distribution | DE | Status | Assigned |
|----|----------|---------|--------------|----|----|----------|
| L-001 | | | | | | |
| L-002 | | | | | | |

---

## Test Results Summary

### Coverage

- **Unit Tests**: ☐ Pass / Fail
- **Integration Tests**: ☐ Pass / Fail
- **Mock Tests**: ☐ Pass / Fail
- **Manual Tests**: ☐ Pass / Fail

### Code Coverage

- **Linux Platform Code**: __%
- **Overall Coverage**: __%

### Release Criteria

- [ ] All P0 tests passing
- [ ] > 95% P1 tests passing
- [ ] > 90% DE tests passing
- [ ] Zero critical bugs
- [ ] < 5 high priority bugs
- [ ] All performance benchmarks met

### Sign-off

- [ ] QA Approved
- [ ] Documentation Complete
- [ ] Release Notes Prepared

---

**Instructions**:
1. Copy this template for each test session
2. Check off completed tests with ☑ or x
3. Fill in actual values for performance metrics
4. Document any bugs or issues found
5. Update summary at end of session
