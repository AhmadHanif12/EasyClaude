# EasyClaude QA Validation Checklist

**Project:** EasyClaude - Claude Code Launcher
**QA Agent:** QA Agent
**Date:** 2026-02-07
**Version:** 0.1.0
**Status:** PENDING IMPLEMENTATION

---

## Executive Summary

The EasyClaude application is currently in early development with only project structure and documentation in place. Core modules (main.py, config.py, hotkey.py, tray.py, gui.py, launcher.py, platform abstraction) have not yet been implemented.

**Current Status:** Architecture design phase
**Ready for Testing:** No - awaiting implementation

---

## Test Environment Requirements

- [ ] Python 3.10+ installed
- [ ] Claude Code CLI accessible in PATH
- [ ] Windows 10/11 (primary target)
- [ ] Test directories with various permission levels
- [ ] Network connectivity (for Claude API calls)
- [ ] Administrative and non-administrative user accounts

---

## Module-by-Module Test Plan

### 1. Configuration Module (app/config.py)

**Functionality:** Configuration persistence with pydantic validation

#### Test Cases:
- [ ] **C-001**: Create default config on first run
  - Verify: `~/.easyclaude/config.json` created with defaults
  - Expected: Default hotkey "ctrl+alt+c", empty last_directory

- [ ] **C-002**: Load existing configuration
  - Verify: All settings loaded correctly from JSON
  - Expected: Pydantic validation passes, settings accessible

- [ ] **C-003**: Save configuration changes
  - Verify: Changes persisted to disk
  - Expected: JSON file updated, next load reflects changes

- [ ] **C-004**: Validate configuration on load
  - Verify: Invalid config rejected or corrected
  - Test: Corrupt JSON, invalid hotkey format, negative values
  - Expected: Graceful fallback to defaults or error message

- [ ] **C-005**: Configuration migration
  - Verify: Old config versions upgrade properly
  - Expected: No data loss, schema updates applied

#### Edge Cases:
- [ ] Config file is locked by another process
- [ ] Insufficient permissions to write config directory
- [ ] Disk full when saving config
- [ ] Config file contains future version schema
- [ ] Concurrent config read/write operations

---

### 2. Global Hotkey Module (app/hotkey.py)

**Functionality:** Global hotkey registration with pynput

#### Test Cases:
- [ ] **H-001**: Register default hotkey (Ctrl+Alt+C)
  - Verify: Hotkey triggers GUI when pressed
  - Expected: GUI appears centered and always-on-top

- [ ] **H-002**: Change hotkey configuration
  - Verify: New hotkey registered, old one released
  - Expected: Only new hotkey triggers GUI

- [ ] **H-003**: Hotkey with GUI already open
  - Verify: Pressing hotkey again brings GUI to focus
  - Expected: No duplicate windows, single instance

- [ ] **H-004**: Hotkey while command executing
  - Verify: Hotkey responsive during Claude execution
  - Expected: Can open new instance or show busy state

#### Edge Cases:
- [ ] Hotkey already registered by another application
- [ ] Invalid hotkey combination
- [ ] System key combinations (Win+L, Ctrl+Alt+Del)
- [ ] Hotkey during system sleep/hibernate
- [ ] Keyboard layout changes affecting hotkey
- [ ] Rapid hotkey presses (debounce needed?)
- [ ] Accessibility tools interfering with hotkey

---

### 3. GUI Module (app/gui.py)

**Functionality:** Launcher GUI with tkinter (always-on-top, centered)

#### Test Cases:
- [ ] **G-001**: Window positioning - centered on screen
  - Verify: Window appears centered on primary monitor
  - Expected: Calculates screen dimensions correctly

- [ ] **G-002**: Always-on-top behavior
  - Verify: Window stays above other applications
  - Test: Click other windows, verify GUI remains visible
  - Expected: GUI stays on top

- [ ] **G-003**: Directory picker functionality
  - Verify: Native folder selection dialog opens
  - Expected: Selected path populates directory field

- [ ] **G-004**: Command selection buttons
  - Verify: Buttons for claude, --continue, --dangerously-skip-permissions
  - Expected: Selection stored for execution

- [ ] **G-005**: Directory field persistence
  - Verify: Last used directory pre-populated
  - Expected: Value from config loaded on startup

- [ ] **G-006**: Execute button
  - Verify: Launches Claude with selected options
  - Expected: Command passed to launcher, GUI closes

- [ ] **G-007**: Cancel button
  - Verify: Closes GUI without executing
  - Expected: No command executed, GUI dismissed

- [ ] **G-008**: Multi-monitor support
  - Verify: Window centers on active monitor
  - Expected: Correct positioning for multi-monitor setups

#### Edge Cases:
- [ ] Very small screen resolutions (800x600, 1024x768)
- [ ] Ultra-wide monitors
- [ ] High DPI displays (150%, 200% scaling)
- [ ] Directory path longer than field width
- [ ] Network drive paths in directory picker
- [ ] Unicode characters in directory paths
- [ ] GUI opened when Claude is already running in terminal

---

### 4. System Tray Module (app/tray.py)

**Functionality:** System tray icon with pystray

#### Test Cases:
- [ ] **T-001**: Tray icon appears on startup
  - Verify: Icon visible in system tray
  - Expected: EasyClaude icon present

- [ ] **T-002**: Tray icon menu items
  - Verify: "Open", "Settings", "Exit" options available
  - Expected: All menu items functional

- [ ] **T-003**: "Open" shows GUI
  - Verify: Clicking opens the launcher GUI
  - Expected: Same behavior as hotkey

- [ ] **T-004**: "Exit" terminates application
  - Verify: Application closes, tray icon removed
  - Expected: Clean shutdown, no orphaned processes

- [ ] **T-005**: Double-click behavior
  - Verify: Double-clicking icon opens GUI
  - Expected: Consistent with menu "Open"

#### Edge Cases:
- [ ] System tray not visible (Windows tablet mode)
- [ ] Custom taskbar settings hiding tray icons
- [ ] Explorer restart (tray icon recreation)
- [ ] Multiple clicks on tray icon
- [ ] Tray icon tooltip text display

---

### 5. Launcher Module (app/launcher.py)

**Functionality:** Terminal execution of Claude commands

#### Test Cases:
- [ ] **L-001**: Standard claude launch
  - Verify: `claude` executes in selected directory
  - Expected: Terminal opens, Claude session starts

- [ ] **L-002**: Continue last session
  - Verify: `claude --continue` executes
  - Expected: Last session resumed in terminal

- [ ] **L-003**: Skip permissions
  - Verify: `claude --dangerously-skip-permissions` executes
  - Expected: Claude starts without permission prompts

- [ ] **L-004**: Invalid directory path
  - Verify: Error message shown to user
  - Expected: Graceful failure, no crash

- [ ] **L-005**: Directory without write permissions
  - Verify: Error handling for restricted directories
  - Expected: Clear error message

- [ ] **L-006**: Claude not in PATH
  - Verify: Appropriate error when Claude unavailable
  - Expected: User-friendly error with installation guidance

- [ ] **L-007**: PowerShell vs CMD selection
  - Verify: Respect always_use_powershell setting
  - Expected: Correct shell type used

#### Edge Cases:
- [ ] Network paths with authentication requirements
- [ ] Symbolic links and junctions in paths
- [ ] Paths with spaces and special characters
- [ ] Very long directory paths (MAX_PATH issues)
- [ ] Terminal window already open with Claude session
- [ ] System resource constraints (memory, CPU)
- [ ] Antivirus or security software interference

---

### 6. Platform Abstraction (app/platform/)

**Functionality:** Cross-platform terminal launching

#### Test Cases:
- [ ] **P-001**: Windows platform detection
  - Verify: Windows implementation selected
  - Expected: Correct platform module loaded

- [ ] **P-002**: Windows PowerShell launch
  - Verify: PowerShell opens with proper command
  - Expected: `powershell.exe -NoExit -Command "cd '<path>'; claude ..."`

- [ ] **P-003**: Linux stub (future)
  - Verify: NotImplementedError raised appropriately
  - Expected: Clear message about Linux support coming in Phase 2

#### Edge Cases:
- [ ] Windows editions (Home, Pro, Enterprise)
- [ ] Windows versions (10, 11, future versions)
- [ ] PowerShell Core vs Windows PowerShell
- [ ] Execution policy restrictions

---

### 7. Main Application (app/main.py)

**Functionality:** Entry point, component orchestration

#### Test Cases:
- [ ] **M-001**: Clean startup
  - Verify: All components initialized without errors
  - Expected: Tray icon appears, hotkey registered

- [ ] **M-002**: Graceful shutdown
  - Verify: All components cleaned up properly
  - Expected: No orphaned processes, config saved

- [ ] **M-003**: Crash recovery
  - Verify: Can restart after unexpected crash
  - Expected: No corruption, clean restart

- [ ] **M-004**: Multiple instance prevention
  - Verify: Only one instance running at a time
  - Expected: Second attempt shows existing instance or error

#### Edge Cases:
- [ ] Startup failure (missing dependencies)
- [ ] Config file corruption on startup
- [ ] Another instance already running
- [ ] System startup (autostart scenario)
- [ ] User logged in/out rapidly

---

## Integration Test Scenarios

### Scenario 1: First-Time User
1. Install EasyClaude
2. Launch application
3. Verify tray icon appears
4. Press hotkey (Ctrl+Alt+C)
5. Verify GUI appears centered
6. Select directory via picker
7. Click "Execute"
8. Verify terminal opens with Claude

### Scenario 2: Returning User
1. Launch application (config exists)
2. Press hotkey
3. Verify last directory pre-populated
4. Change directory
5. Execute command
6. Verify new directory saved to config

### Scenario 3: Error Handling
1. Press hotkey
2. Enter invalid directory path
3. Click "Execute"
4. Verify clear error message
5. GUI remains open for correction

### Scenario 4: Hotkey Conflict
1. Configure hotkey used by another app
2. Try to register hotkey
3. Verify conflict detection
4. Verify fallback or error message

### Scenario 5: Resource Constraints
1. Run with low memory
2. Execute multiple rapid commands
3. Verify no memory leaks
4. Verify stable performance

---

## UX Evaluation Criteria

### Responsiveness
- [ ] Hotkey triggers GUI within 100ms
- [ ] GUI renders without noticeable lag
- [ ] Directory picker opens instantly
- [ ] Command execution initiates promptly

### Visual Feedback
- [ ] Window positioning consistent
- [ ] Always-on-top behavior reliable
- [ ] Tray icon visible and identifiable
- [ ] Button states clear (hover, active, disabled)

### Error Messaging
- [ ] Errors use plain language
- [ ] Errors suggest resolution
- [ ] No raw stack traces to end users
- [ ] Error dialogs non-modal when appropriate

### Accessibility
- [ ] Keyboard navigation works
- [ ] High DPI scaling handled
- [ ] Screen reader compatibility (basic)
- [ ] Color contrast adequate

---

## Performance Benchmarks

- [ ] Cold start time: < 2 seconds
- [ ] Hotkey response: < 100ms
- [ ] GUI render: < 50ms
- [ ] Memory footprint: < 50MB idle
- [ ] CPU usage: < 1% idle

---

## Security Considerations

- [ ] No credential storage without encryption
- [ ] Command injection prevention in paths
- [ ] Safe handling of symbolic links
- [ ] Permission validation before execution
- [ ] No arbitrary code execution vulnerabilities

---

## Regression Testing

After any code changes, verify:
- [ ] All existing test cases still pass
- [ ] No new memory leaks introduced
- [ ] Performance hasn't degraded
- [ ] Configuration remains backward compatible

---

## Automated Testing Requirements

### Unit Tests
- [ ] Config model validation (pytest)
- [ ] Hotkey manager (mocked keyboard)
- [ ] Launcher command construction
- [ ] Platform abstraction interface

### Integration Tests
- [ ] Full workflow simulations
- [ ] Error scenario testing
- [ ] Configuration persistence
- [ ] Multi-instance handling

### UI Tests (Optional)
- [ ] Automated GUI interaction
- [ ] Screenshot-based validation
- [ ] Cross-version Windows testing

---

## Test Deliverables

- [ ] Test case execution report
- [ ] Bug reports with reproduction steps
- [ ] Performance profiling results
- [ ] UX improvement recommendations
- [ ] Test coverage metrics (>80%)

---

## Known Limitations (Phase 1)

- Linux support not implemented (Phase 2)
- macOS not tested
- Single monitor only (multi-monitor untested)
- English UI only (no i18n)

---

## Recommendations for Development

Based on architecture review:

1. **Priority Critical:**
   - Implement comprehensive error handling from the start
   - Add logging throughout for debugging
   - Create configuration backup/restore mechanism

2. **UX Improvements:**
   - Add keyboard shortcuts in GUI (Enter to execute, Esc to cancel)
   - Show recent directories for quick selection
   - Add option to keep GUI open after execution

3. **Error Handling:**
   - Validate Claude availability on startup
   - Test directory existence/permissions before execution
   - Handle terminal window creation failures

4. **Testing:**
   - Write tests alongside implementation (TDD)
   - Create mock Claude CLI for testing
   - Use fixtures for test directories

---

## Sign-Off

**QA Agent:** _________________
**Date:** _________________
**Status:** READY FOR TESTING / NOT READY

**Dev Agent Review:** _________________
**Date:** _________________

**Team Lead Approval:** _________________
**Date:** _________________

---

## Appendix: Test Data

### Sample Test Directories
- `C:\Users\Test\Projects` (standard path)
- `C:\Very\Long\Path\That\Goes\On\And\On\...` (long path)
- `\\Network\Share\Path` (network path)
- `C:\Test\Dir With Spaces` (spaces in name)
- `C:\Test\日本語\テスト` (Unicode characters)

### Sample Invalid Paths
- `C:\NonExistent\Directory\`
- `C:\Protected\System\` (permission denied)
- `INVALID:\PATH\FORMAT`
- `C:\Test\..\..\System32` (path traversal attempt)

### Sample Claude Commands
- `claude`
- `claude --continue`
- `claude --dangerously-skip-permissions`
- `claude model=claude-opus-4-6`

---

*Document Version: 1.0*
*Last Updated: 2026-02-07*
*Next Review: When implementation is ready for testing*
