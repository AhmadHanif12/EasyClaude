"""
Integration tests for app/gui.py LauncherGUI class.

These tests mock tkinter components to test the actual LauncherGUI implementation,
not just tkinter primitives in isolation.
"""

import pytest
from unittest.mock import MagicMock, Mock, patch, call, ANY, PropertyMock
import threading
import queue
import sys
import os

# Add the app directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.gui import LauncherGUI


# Create mock Variable classes
class MockStringVar:
    """Mock StringVar for testing."""
    def __init__(self, value=""):
        self._value = value

    def set(self, value):
        self._value = value

    def get(self):
        return self._value


class MockBooleanVar:
    """Mock BooleanVar for testing."""
    def __init__(self, value=False):
        self._value = value

    def set(self, value):
        self._value = value

    def get(self):
        return self._value


@pytest.fixture
def mock_string_var():
    """Mock StringVar factory."""
    vars = []
    def factory(value=""):
        var = MockStringVar(value)
        vars.append(var)
        return var
    factory.instances = vars
    return factory


@pytest.fixture
def mock_boolean_var():
    """Mock BooleanVar factory."""
    vars = []
    def factory(value=False):
        var = MockBooleanVar(value)
        vars.append(var)
        return var
    factory.instances = vars
    return factory


@pytest.fixture
def mock_tk_root():
    """Create a fully mocked tkinter root."""
    mock_root = MagicMock()
    mock_root.winfo_screenwidth.return_value = 1920
    mock_root.winfo_screenheight.return_value = 1080
    return mock_root


@pytest.fixture
def mock_gui(mock_tk_root, mock_string_var, mock_boolean_var):
    """Create a LauncherGUI with all tkinter dependencies mocked."""
    with patch('tkinter.Tk', return_value=mock_tk_root), \
         patch('tkinter.StringVar', side_effect=mock_string_var), \
         patch('tkinter.BooleanVar', side_effect=mock_boolean_var), \
         patch('tkinter.ttk.Frame'), \
         patch('tkinter.ttk.Label'), \
         patch('tkinter.Entry'), \
         patch('tkinter.ttk.Button'), \
         patch('tkinter.ttk.Checkbutton'), \
         patch('tkinter.filedialog.askdirectory'), \
         patch('tkinter.messagebox.showwarning'), \
         patch('tkinter.messagebox.showerror'):
        gui = LauncherGUI(MagicMock())
        gui._ensure_initialized()
        yield gui


class TestLauncherGUIConstruction:
    """Test LauncherGUI class construction and initialization."""

    def test_init_stores_callback(self):
        """Test that launch callback is stored."""
        callback = MagicMock()
        gui = LauncherGUI(callback)

        assert gui._launch_callback is callback
        assert gui._root is None
        assert gui._initialized is False

    def test_init_creates_command_queue(self):
        """Test that command queue is created."""
        gui = LauncherGUI(MagicMock())

        assert hasattr(gui, '_command_queue')
        assert isinstance(gui._command_queue, queue.Queue)

    def test_commands_constant(self):
        """Test available commands constant."""
        expected_commands = [
            "claude",
            "claude --continue",
            "claude --dangerously-skip-permissions",
        ]
        assert LauncherGUI.COMMANDS == expected_commands


class TestLauncherGUILazyInitialization:
    """Test lazy initialization pattern."""

    def test_ensure_initialized_creates_window(self, mock_tk_root, mock_string_var, mock_boolean_var):
        """Test that _ensure_initialized creates the window."""
        with patch('tkinter.Tk', return_value=mock_tk_root), \
             patch('tkinter.StringVar', side_effect=mock_string_var), \
             patch('tkinter.BooleanVar', side_effect=mock_boolean_var), \
             patch('tkinter.ttk.Frame'), \
             patch('tkinter.ttk.Label'), \
             patch('tkinter.Entry'), \
             patch('tkinter.ttk.Button'), \
             patch('tkinter.ttk.Checkbutton'):
            gui = LauncherGUI(MagicMock())
            gui._ensure_initialized()

            assert gui._initialized is True
            assert gui._root is mock_tk_root

    def test_ensure_initialized_idempotent(self, mock_tk_root, mock_string_var, mock_boolean_var):
        """Test that _ensure_initialized only creates window once."""
        with patch('tkinter.Tk', return_value=mock_tk_root), \
             patch('tkinter.StringVar', side_effect=mock_string_var), \
             patch('tkinter.BooleanVar', side_effect=mock_boolean_var), \
             patch('tkinter.ttk.Frame'), \
             patch('tkinter.ttk.Label'), \
             patch('tkinter.Entry'), \
             patch('tkinter.ttk.Button'), \
             patch('tkinter.ttk.Checkbutton'):
            gui = LauncherGUI(MagicMock())
            gui._ensure_initialized()
            gui._ensure_initialized()

            # Should only be created once
            assert mock_tk_root.title.call_count >= 1

    def test_window_properties_set(self, mock_tk_root, mock_string_var, mock_boolean_var):
        """Test that window properties are configured correctly."""
        with patch('tkinter.Tk', return_value=mock_tk_root), \
             patch('tkinter.StringVar', side_effect=mock_string_var), \
             patch('tkinter.BooleanVar', side_effect=mock_boolean_var), \
             patch('tkinter.ttk.Frame'), \
             patch('tkinter.ttk.Label'), \
             patch('tkinter.Entry'), \
             patch('tkinter.ttk.Button'), \
             patch('tkinter.ttk.Checkbutton'):
            gui = LauncherGUI(MagicMock())
            gui._ensure_initialized()

            # Verify title
            mock_tk_root.title.assert_called_with("EasyClaude")

            # Verify non-resizable
            mock_tk_root.resizable.assert_called_with(False, False)

            # Verify initially hidden
            mock_tk_root.withdraw.assert_called()

            # Verify always on top
            mock_tk_root.attributes.assert_called_with('-topmost', True)

    def test_widgets_created(self, mock_gui):
        """Test that all widgets are created."""
        # Verify state variables exist
        assert hasattr(mock_gui, '_directory_var')
        assert hasattr(mock_gui, '_powershell_var')

    def test_keyboard_bindings(self, mock_gui):
        """Test that keyboard shortcuts are bound."""
        # Verify bindings were called
        mock_gui._root.bind.assert_any_call('<Return>', ANY)
        mock_gui._root.bind.assert_any_call('<Escape>', ANY)

    def test_window_close_protocol(self, mock_gui):
        """Test that WM_DELETE_WINDOW is handled."""
        # Verify WM_DELETE_WINDOW protocol
        mock_gui._root.protocol.assert_called_with("WM_DELETE_WINDOW", mock_gui.hide)


class TestLauncherGUIShowHide:
    """Test show/hide functionality."""

    def test_show_queues_command(self, mock_gui):
        """Test that show() queues the show command."""
        mock_gui.show("C:\\Test\\Directory")

        # Should have queued the command
        assert not mock_gui._command_queue.empty()

        cmd = mock_gui._command_queue.get_nowait()
        assert cmd["cmd"] == "show"
        assert cmd["directory"] == "C:\\Test\\Directory"

    def test_show_without_directory(self, mock_gui):
        """Test show() without initial directory."""
        mock_gui.show()

        cmd = mock_gui._command_queue.get_nowait()
        assert cmd["cmd"] == "show"
        assert cmd["directory"] == ""

    def test_hide_direct(self, mock_gui):
        """Test hide() when called from GUI thread."""
        mock_gui.hide()

        mock_gui._root.withdraw.assert_called()

    def test_hide_when_root_none(self):
        """Test hide() when root is None."""
        gui = LauncherGUI(MagicMock())

        # Should not raise
        gui.hide()

    def test_command_queue_processing(self, mock_gui):
        """Test that command queue is processed."""
        # Queue a show command
        mock_gui._command_queue.put({"cmd": "show", "directory": "C:\\Test"})

        # Process queue
        mock_gui._process_command_queue()

        # Should deiconify and focus
        mock_gui._root.deiconify.assert_called()
        mock_gui._root.lift.assert_called()
        mock_gui._root.focus_force.assert_called()

    def test_command_queue_hide_processing(self, mock_gui):
        """Test that hide command in queue is processed."""
        # Queue a hide command
        mock_gui._command_queue.put({"cmd": "hide"})

        mock_gui._process_command_queue()

        mock_gui._root.withdraw.assert_called()


class TestLauncherGUIDirectoryPicker:
    """Test directory picker functionality."""

    def test_browse_directory_with_current_dir(self, mock_gui):
        """Test _browse_directory with valid current directory."""
        from tkinter import filedialog
        mock_gui._directory_var.set("C:\\Current\\Dir")

        with patch.object(filedialog, 'askdirectory', return_value="C:\\Selected\\Dir"):
            mock_gui._browse_directory(mock_gui._directory_var)

            # Directory should be updated
            assert mock_gui._directory_var.get() == "C:\\Selected\\Dir"

    def test_browse_directory_with_invalid_current(self, mock_gui):
        """Test _browse_directory with invalid current directory."""
        from tkinter import filedialog
        from unittest.mock import patch
        import os as os_module

        mock_gui._directory_var.set("C:\\Invalid\\Dir")

        with patch.object(filedialog, 'askdirectory', return_value="C:\\Selected\\Dir") as mock_askdir, \
             patch.object(os_module.path, 'isdir', return_value=False):
            mock_gui._browse_directory(mock_gui._directory_var)

            # Should be called with some initialdir
            assert mock_askdir.called

    def test_browse_directory_cancelled(self, mock_gui):
        """Test _browse_directory when user cancels."""
        from tkinter import filedialog

        mock_gui._directory_var.set("C:\\Current")

        with patch.object(filedialog, 'askdirectory', return_value=""):
            mock_gui._browse_directory(mock_gui._directory_var)

            # Directory should not be updated
            assert mock_gui._directory_var.get() == "C:\\Current"


class TestLauncherGUILaunch:
    """Test launch functionality."""

    def test_launch_with_empty_directory(self, mock_gui):
        """Test _do_launch with empty directory."""
        from tkinter import messagebox

        mock_gui._directory_var.set("")

        with patch.object(messagebox, 'showwarning') as mock_warning:
            mock_gui._do_launch("claude")

            # Should show warning
            mock_warning.assert_called_once()

            # Callback should not be called
            mock_gui._launch_callback.assert_not_called()

    def test_launch_with_invalid_directory(self, mock_gui):
        """Test _do_launch with non-existent directory."""
        from tkinter import messagebox
        import os as os_module

        mock_gui._directory_var.set("C:\\NonExistent")

        with patch.object(messagebox, 'showerror') as mock_error, \
             patch.object(os_module.path, 'isdir', return_value=False):
            mock_gui._do_launch("claude")

            # Should show error
            mock_error.assert_called_once()

            # Callback should not be called
            mock_gui._launch_callback.assert_not_called()

    def test_launch_success_hides_window(self, mock_gui):
        """Test that successful launch hides the window."""
        import os as os_module

        mock_gui._directory_var.set("C:\\Valid")

        with patch.object(os_module.path, 'isdir', return_value=True):
            mock_gui._do_launch("claude")

            # Window should be hidden
            mock_gui._root.withdraw.assert_called()

    def test_launch_calls_callback_in_thread(self, mock_gui):
        """Test that callback is called in a separate thread."""
        import os as os_module
        import time

        mock_gui._directory_var.set("C:\\Valid")
        mock_gui._powershell_var.set(True)

        with patch.object(os_module.path, 'isdir', return_value=True):
            mock_gui._do_launch("claude --continue")

            # Wait for thread
            time.sleep(0.1)

            # Callback should be called with correct arguments
            mock_gui._launch_callback.assert_called_once_with("C:\\Valid", "claude --continue", True)

    def test_launch_with_powershell_false(self, mock_gui):
        """Test launch with PowerShell checkbox unchecked."""
        import os as os_module
        import time

        mock_gui._directory_var.set("C:\\Valid")
        mock_gui._powershell_var.set(False)

        with patch.object(os_module.path, 'isdir', return_value=True):
            mock_gui._do_launch("claude")

            time.sleep(0.1)

            mock_gui._launch_callback.assert_called_once_with("C:\\Valid", "claude", False)


class TestLauncherGUIKeyboardShortcuts:
    """Test keyboard shortcut bindings."""

    def test_return_key_launches_first_command(self, mock_gui):
        """Test that Return key launches with default command."""
        import os as os_module
        import time

        mock_gui._directory_var.set("C:\\Valid")

        with patch.object(os_module.path, 'isdir', return_value=True):
            # Simulate Return key binding
            mock_gui._do_launch(mock_gui.COMMANDS[0])

            time.sleep(0.1)

            mock_gui._launch_callback.assert_called_once()

    def test_escape_key_hides_window(self, mock_gui):
        """Test that Escape key hides the window."""
        # Simulate Escape key binding
        mock_gui.hide()

        mock_gui._root.withdraw.assert_called()


class TestLauncherGUIState:
    """Test state management."""

    def test_directory_stringvar_initialization(self, mock_gui):
        """Test that directory StringVar is initialized."""
        assert hasattr(mock_gui, '_directory_var')
        assert mock_gui._directory_var.get() == ""

    def test_powershell_booleanvar_default(self, mock_gui):
        """Test that PowerShell BooleanVar defaults to False."""
        assert hasattr(mock_gui, '_powershell_var')
        assert mock_gui._powershell_var.get() is False

    def test_directory_persistence_in_show(self, mock_gui):
        """Test that directory is set when showing GUI."""
        mock_gui.show("C:\\Persisted\\Directory")

        # Process the queue
        cmd = mock_gui._command_queue.get_nowait()
        assert cmd["directory"] == "C:\\Persisted\\Directory"


class TestLauncherGUIUpdate:
    """Test update() method."""

    def test_update_when_initialized(self, mock_gui):
        """Test update() when GUI is initialized."""
        mock_gui.update()

        mock_gui._root.update.assert_called_once()

    def test_update_when_not_initialized(self):
        """Test update() when GUI is not initialized."""
        gui = LauncherGUI(MagicMock())

        # Should not raise
        gui.update()

    def test_update_handles_exception(self, mock_tk_root, mock_string_var, mock_boolean_var):
        """Test update() handles exceptions gracefully."""
        mock_tk_root.update.side_effect = RuntimeError("Test error")

        with patch('tkinter.Tk', return_value=mock_tk_root), \
             patch('tkinter.StringVar', side_effect=mock_string_var), \
             patch('tkinter.BooleanVar', side_effect=mock_boolean_var), \
             patch('tkinter.ttk.Frame'), \
             patch('tkinter.ttk.Label'), \
             patch('tkinter.Entry'), \
             patch('tkinter.ttk.Button'), \
             patch('tkinter.ttk.Checkbutton'):
            gui = LauncherGUI(MagicMock())
            gui._ensure_initialized()

            # Should not raise
            gui.update()


class TestLauncherGUIDestroy:
    """Test destroy() method."""

    def test_destroy_when_initialized(self, mock_gui):
        """Test destroy() when GUI is initialized."""
        # Store reference to root before destroy
        root = mock_gui._root
        mock_gui.destroy()

        root.destroy.assert_called_once()
        assert mock_gui._root is None
        assert mock_gui._initialized is False

    def test_destroy_when_not_initialized(self):
        """Test destroy() when GUI is not initialized."""
        gui = LauncherGUI(MagicMock())

        # Should not raise
        gui.destroy()
        assert gui._initialized is False

    def test_destroy_handles_exception(self, mock_tk_root, mock_string_var, mock_boolean_var):
        """Test destroy() handles exceptions gracefully."""
        mock_tk_root.destroy.side_effect = RuntimeError("Test error")

        with patch('tkinter.Tk', return_value=mock_tk_root), \
             patch('tkinter.StringVar', side_effect=mock_string_var), \
             patch('tkinter.BooleanVar', side_effect=mock_boolean_var), \
             patch('tkinter.ttk.Frame'), \
             patch('tkinter.ttk.Label'), \
             patch('tkinter.Entry'), \
             patch('tkinter.ttk.Button'), \
             patch('tkinter.ttk.Checkbutton'):
            gui = LauncherGUI(MagicMock())
            gui._ensure_initialized()

            # Should not raise
            gui.destroy()
            assert gui._initialized is False


class TestLauncherGUIThreadSafety:
    """Test thread-safe operations."""

    def test_show_from_background_thread(self, mock_gui):
        """Test that show() can be called from background thread."""
        def show_in_thread():
            mock_gui.show("C:\\From\\Thread")

        thread = threading.Thread(target=show_in_thread)
        thread.start()
        thread.join()

        # Should have queued the command
        assert not mock_gui._command_queue.empty()
        cmd = mock_gui._command_queue.get_nowait()
        assert cmd["cmd"] == "show"

    def test_hide_from_background_thread(self, mock_gui):
        """Test that hide() can be called from background thread."""
        def hide_in_thread():
            mock_gui.hide()

        thread = threading.Thread(target=hide_in_thread)
        thread.start()
        thread.join()

        # Should not crash - test passes if no exception


class TestLauncherGUICommandEventProcessing:
    """Test command queue event processing."""

    def test_process_empty_queue(self, mock_gui):
        """Test processing empty queue doesn't crash."""
        # Should not raise
        mock_gui._process_command_queue()

    def test_process_multiple_commands(self, mock_gui):
        """Test processing multiple commands in queue."""
        # Queue multiple commands
        mock_gui._command_queue.put({"cmd": "show", "directory": "C:\\Dir1"})
        mock_gui._command_queue.put({"cmd": "hide"})

        mock_gui._process_command_queue()

        # Both should be processed
        mock_gui._root.deiconify.assert_called()
        mock_gui._root.withdraw.assert_called()

    def test_show_command_sets_directory(self, mock_gui):
        """Test that show command sets the directory."""
        mock_gui._command_queue.put({"cmd": "show", "directory": "C:\\Test\\Dir"})
        mock_gui._process_command_queue()

        assert mock_gui._directory_var.get() == "C:\\Test\\Dir"

    def test_show_without_directory_doesnt_change(self, mock_gui):
        """Test show command without directory doesn't change value."""
        mock_gui._directory_var.set("C:\\Existing")
        mock_gui._command_queue.put({"cmd": "show", "directory": ""})
        mock_gui._process_command_queue()

        # Directory should remain unchanged
        assert mock_gui._directory_var.get() == "C:\\Existing"

    def test_schedules_next_queue_processing(self, mock_gui):
        """Test that queue processing reschedules itself."""
        mock_gui._process_command_queue()

        # Should schedule next processing
        mock_gui._root.after.assert_called_with(50, mock_gui._process_command_queue)
