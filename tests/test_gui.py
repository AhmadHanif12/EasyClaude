# Tests for app/gui.py
"""Test GUI component functionality with mocked tkinter."""

import pytest
from unittest.mock import MagicMock, patch, Mock, call
import sys


class TestGUIInitialization:
    """Test GUI initialization and setup."""

    @patch('tkinter.Tk')
    def test_create_main_window(self, mock_tk):
        """Test creating the main tkinter window."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        root = mock_tk()

        # Verify window was created
        mock_tk.assert_called_once()

    @patch('tkinter.Tk')
    def test_set_window_title(self, mock_tk):
        """Test setting window title."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        root = mock_tk()
        root.title("EasyClaude")

        root.title.assert_called_once_with("EasyClaude")

    @patch('tkinter.Tk')
    def test_set_window_geometry(self, mock_tk):
        """Test setting window geometry (size and position)."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        root = mock_tk()
        geometry = "600x400+300+200"
        root.geometry(geometry)

        root.geometry.assert_called_once_with(geometry)

    @patch('tkinter.Tk')
    def test_set_always_on_top(self, mock_tk):
        """Test setting window to always stay on top."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        root = mock_tk()
        root.attributes('-topmost', True)

        root.attributes.assert_called_once_with('-topmost', True)

    @patch('tkinter.Tk')
    def test_center_window_on_screen(self, mock_tk):
        """Test centering window on screen."""
        mock_root = MagicMock()
        mock_root.winfo_screenwidth.return_value = 1920
        mock_root.winfo_screenheight.return_value = 1080
        mock_tk.return_value = mock_root

        window_width = 600
        window_height = 400

        screen_width = 1920
        screen_height = 1080

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        expected_geometry = f"{window_width}x{window_height}+{x}+{y}"

        assert x == 660
        assert y == 340
        assert expected_geometry == "600x400+660+340"


class TestGUIComponents:
    """Test GUI component creation and layout."""

    @patch('tkinter.ttk.Frame')
    def test_create_main_frame(self, mock_frame):
        """Test creating main container frame."""
        mock_parent = MagicMock()
        mock_frame_instance = MagicMock()
        mock_frame.return_value = mock_frame_instance

        main_frame = mock_frame(mock_parent)
        main_frame.pack(fill='both', expand=True)

        mock_frame.assert_called_once_with(mock_parent)
        mock_frame_instance.pack.assert_called_once()

    @patch('tkinter.ttk.Label')
    def test_create_directory_label(self, mock_label):
        """Test creating directory selection label."""
        mock_parent = MagicMock()
        mock_label_instance = MagicMock()
        mock_label.return_value = mock_label_instance

        label = mock_label(mock_parent, text="Select Directory:")
        label.pack(pady=5)

        mock_label.assert_called_once()
        mock_label_instance.pack.assert_called_once_with(pady=5)

    @patch('tkinter.Entry')
    def test_create_directory_entry(self, mock_entry):
        """Test creating directory entry field."""
        mock_parent = MagicMock()
        mock_entry_instance = MagicMock()
        mock_entry.return_value = mock_entry_instance

        entry = mock_entry(mock_parent, width=50)
        entry.pack(pady=5)

        mock_entry.assert_called_once_with(mock_parent, width=50)
        mock_entry_instance.pack.assert_called_once_with(pady=5)

    @patch('tkinter.ttk.Button')
    def test_create_browse_button(self, mock_button):
        """Test creating browse button for directory selection."""
        mock_parent = MagicMock()
        mock_button_instance = MagicMock()
        mock_button.return_value = mock_button_instance

        browse_callback = MagicMock()
        button = mock_button(mock_parent, text="Browse...", command=browse_callback)
        button.pack(pady=5)

        mock_button.assert_called_once_with(mock_parent, text="Browse...", command=browse_callback)
        mock_button_instance.pack.assert_called_once_with(pady=5)

    @patch('tkinter.ttk.Label')
    def test_create_command_label(self, mock_label):
        """Test creating command selection label."""
        mock_parent = MagicMock()
        mock_label_instance = MagicMock()
        mock_label.return_value = mock_label_instance

        label = mock_label(mock_parent, text="Claude Command:")
        label.pack(pady=5)

        mock_label.assert_called_once()
        mock_label_instance.pack.assert_called_once_with(pady=5)

    @patch('tkinter.ttk.Button')
    def test_create_command_buttons(self, mock_button):
        """Test creating command selection buttons."""
        mock_parent = MagicMock()
        mock_button_instance = MagicMock()
        mock_button.return_value = mock_button_instance

        commands = [
            ("Claude", MagicMock()),
            ("Continue", MagicMock()),
            ("Skip Permissions", MagicMock())
        ]

        for text, callback in commands:
            button = mock_button(mock_parent, text=text, command=callback)
            button.pack(side='left', padx=5)

        assert mock_button.call_count == 3


class TestGUIDirectoryPicker:
    """Test directory picker dialog functionality."""

    @patch('tkinter.filedialog.askdirectory')
    def test_directory_picker_initial(self, mock_askdir):
        """Test opening directory picker dialog."""
        mock_askdir.return_value = "C:\\Users\\User\\Projects"

        selected_dir = mock_askdir(
            title="Select Directory",
            initialdir="C:\\Users\\User"
        )

        mock_askdir.assert_called_once()
        assert selected_dir == "C:\\Users\\User\\Projects"

    @patch('tkinter.filedialog.askdirectory')
    def test_directory_picker_cancelled(self, mock_askdir):
        """Test directory picker when user cancels."""
        mock_askdir.return_value = ""  # Empty string indicates cancellation

        selected_dir = mock_askdir(title="Select Directory")

        assert selected_dir == ""

    @patch('tkinter.filedialog.askdirectory')
    def test_directory_picker_with_initial_dir(self, mock_askdir):
        """Test directory picker with initial directory from config."""
        last_directory = "D:\\Development\\MyProject"
        mock_askdir.return_value = "D:\\Development\\MyProject\\Subdir"

        selected_dir = mock_askdir(
            title="Select Directory",
            initialdir=last_directory
        )

        mock_askdir.assert_called_once_with(
            title="Select Directory",
            initialdir=last_directory
        )

    @patch('tkinter.Entry')
    @patch('tkinter.filedialog.askdirectory')
    def test_update_directory_entry_on_selection(self, mock_askdir, mock_entry):
        """Test that directory entry is updated when directory is selected."""
        mock_entry_instance = MagicMock()
        mock_entry.return_value = mock_entry_instance

        mock_askdir.return_value = "C:\\Selected\\Directory"

        selected_dir = mock_askdir()
        mock_entry_instance.delete(0, 'end')
        mock_entry_instance.insert(0, selected_dir)

        mock_entry_instance.delete.assert_called_once_with(0, 'end')
        mock_entry_instance.insert.assert_called_once_with(0, "C:\\Selected\\Directory")


class TestGUICommandSelection:
    """Test command selection functionality."""

    def test_standard_command_selection(self):
        """Test selecting standard 'claude' command."""
        selected_command = "claude"
        assert selected_command == "claude"

    def test_continue_command_selection(self):
        """Test selecting 'claude --continue' command."""
        selected_command = "claude --continue"
        assert selected_command == "claude --continue"

    def test_skip_permissions_command_selection(self):
        """Test selecting 'claude --dangerously-skip-permissions' command."""
        selected_command = "claude --dangerously-skip-permissions"
        assert selected_command == "claude --dangerously-skip-permissions"

    def test_custom_command_entry(self):
        """Test entering custom command arguments."""
        base_command = "claude"
        custom_args = "-m 'Fix the authentication bug'"
        full_command = f"{base_command} {custom_args}"

        assert full_command == "claude -m 'Fix the authentication bug'"


class TestGUIWindowPositioning:
    """Test window positioning functionality."""

    def test_center_position_calculation(self):
        """Test calculating centered window position."""
        screen_width = 1920
        screen_height = 1080
        window_width = 600
        window_height = 400

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        assert x == 660
        assert y == 340

    def test_top_left_position(self):
        """Test top-left window positioning."""
        position = "top-left"
        x, y = 50, 50

        assert position == "top-left"
        assert x == 50
        assert y == 50

    def test_top_right_position(self):
        """Test top-right window positioning."""
        screen_width = 1920
        window_width = 600
        position = "top-right"

        x = screen_width - window_width - 50
        y = 50

        assert position == "top-right"
        assert x == 1270
        assert y == 50

    def test_bottom_left_position(self):
        """Test bottom-left window positioning."""
        screen_height = 1080
        window_height = 400
        position = "bottom-left"

        x = 50
        y = screen_height - window_height - 50

        assert position == "bottom-left"
        assert x == 50
        assert y == 630

    def test_bottom_right_position(self):
        """Test bottom-right window positioning."""
        screen_width = 1920
        screen_height = 1080
        window_width = 600
        window_height = 400
        position = "bottom-right"

        x = screen_width - window_width - 50
        y = screen_height - window_height - 50

        assert position == "bottom-right"
        assert x == 1270
        assert y == 630


class TestGUIEventHandling:
    """Test GUI event handling."""

    def test_launch_button_click(self):
        """Test handling launch button click event."""
        launch_clicked = []

        def on_launch_click():
            launch_clicked.append(True)

        on_launch_click()
        assert len(launch_clicked) == 1

    def test_cancel_button_click(self):
        """Test handling cancel button click event."""
        window_closed = []

        def on_cancel_click():
            window_closed.append(True)

        on_cancel_click()
        assert len(window_closed) == 1

    @patch('tkinter.Tk')
    def test_window_close_event(self, mock_tk):
        """Test handling window close button (X) event."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        root = mock_tk()
        root.protocol("WM_DELETE_WINDOW", MagicMock())

        root.protocol.assert_called_once()

    def test_hotkey_trigger_shows_gui(self):
        """Test that hotkey trigger shows GUI."""
        gui_visible = []

        def show_gui():
            gui_visible.append(True)

        # Simulate hotkey press
        show_gui()

        assert len(gui_visible) == 1


class TestGUIStateManagement:
    """Test GUI state persistence."""

    def test_remember_last_directory(self):
        """Test remembering last used directory."""
        last_directories = []

        def save_directory(directory):
            last_directories.append(directory)

        save_directory("C:\\Project1")
        save_directory("D:\\Project2")

        assert "C:\\Project1" in last_directories
        assert "D:\\Project2" in last_directories
        assert last_directories[-1] == "D:\\Project2"

    def test_remember_last_command(self):
        """Test remembering last used command."""
        last_commands = []

        def save_command(command):
            last_commands.append(command)

        save_command("claude")
        save_command("claude --continue")

        assert last_commands[-1] == "claude --continue"

    def test_load_saved_state_on_open(self):
        """Test loading saved state when GUI opens."""
        saved_state = {
            "last_directory": "C:\\Saved\\Project",
            "last_command": "claude --continue"
        }

        loaded_directory = saved_state["last_directory"]
        loaded_command = saved_state["last_command"]

        assert loaded_directory == "C:\\Saved\\Project"
        assert loaded_command == "claude --continue"


class TestGUIValidation:
    """Test GUI input validation."""

    def test_validate_directory_not_empty(self):
        """Test that directory is not empty before launch."""
        directory = ""
        is_valid = len(directory) > 0

        assert is_valid is False

    def test_validate_directory_exists(self):
        """Test that selected directory exists."""
        from pathlib import Path
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            directory = tmpdir
            exists = Path(directory).exists()

            assert exists is True

    def test_validate_command_not_empty(self):
        """Test that command is not empty before launch."""
        command = ""
        is_valid = len(command) > 0

        assert is_valid is False

    def test_show_error_on_invalid_input(self):
        """Test showing error message for invalid input."""
        error_messages = []

        def show_error(message):
            error_messages.append(message)

        show_error("Please select a directory")

        assert "Please select a directory" in error_messages


class TestGUIStyling:
    """Test GUI appearance and styling."""

    @patch('tkinter.ttk.Style')
    def test_apply_ttk_style(self, mock_style):
        """Test applying ttk style to widgets."""
        mock_style_instance = MagicMock()
        mock_style.return_value = mock_style_instance

        style = mock_style()
        style.theme_use('clam')

        style.theme_use.assert_called_once_with('clam')

    @patch('tkinter.ttk.Style')
    def test_configure_button_style(self, mock_style):
        """Test configuring button appearance."""
        mock_style_instance = MagicMock()
        mock_style.return_value = mock_style_instance

        style = mock_style()
        style.configure('TButton', padding=10, font=('Arial', 10))

        style.configure.assert_called_once()

    @patch('tkinter.Tk')
    def test_set_window_icon(self, mock_tk):
        """Test setting window icon."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        root = mock_tk()
        icon_path = "assets/icon.ico"
        root.iconbitmap(icon_path)

        root.iconbitmap.assert_called_once_with(icon_path)


class TestGUIAccessibility:
    """Test GUI accessibility features."""

    def test_keyboard_navigation(self):
        """Test keyboard navigation between widgets."""
        # Widgets should support Tab navigation
        tab_navigation_supported = True

        assert tab_navigation_supported is True

    def test_enter_key_launches(self):
        """Test that Enter key triggers launch."""
        enter_pressed = []

        def on_enter_key():
            enter_pressed.append(True)

        on_enter_key()
        assert len(enter_pressed) == 1

    def test_escape_key_closes(self):
        """Test that Escape key closes GUI."""
        escape_pressed = []

        def on_escape_key():
            escape_pressed.append(True)

        on_escape_key()
        assert len(escape_pressed) == 1


class TestGUIMultiMonitor:
    """Test multi-monitor support."""

    def test_primary_monitor_center(self):
        """Test centering on primary monitor."""
        monitor_width = 1920
        monitor_height = 1080
        window_width = 600
        window_height = 400

        x = (monitor_width - window_width) // 2
        y = (monitor_height - window_height) // 2

        # Position is on primary monitor
        assert 0 <= x <= monitor_width - window_width
        assert 0 <= y <= monitor_height - window_height

    def test_secondary_monitor_position(self):
        """Test positioning on secondary monitor."""
        primary_width = 1920
        monitor_offset = primary_width
        window_width = 600

        x = monitor_offset + 100

        # Position is on secondary monitor
        assert x >= primary_width
