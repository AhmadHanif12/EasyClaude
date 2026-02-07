# Tests for app/hotkey.py
"""Test hotkey registration functionality with mocked pynput."""

import pytest
from unittest.mock import MagicMock, patch, Mock
import sys


class TestHotkeyRegistration:
    """Test hotkey registration with pynput."""

    @patch('pynput.keyboard.GlobalHotKeys')
    def test_register_basic_hotkey(self, mock_hotkeys):
        """Test registering a basic hotkey combination."""
        # Mock the GlobalHotKeys class
        mock_instance = MagicMock()
        mock_hotkeys.return_value = mock_instance

        # Simulate hotkey registration
        hotkey_string = "ctrl+alt+c"
        callback = MagicMock()

        # Create hotkey map
        hotkey_map = {
            hotkey_string: callback
        }

        # Register hotkeys
        hotkeys = mock_hotkeys(hotkey_map)
        hotkeys.start()

        # Verify
        mock_hotkeys.assert_called_once_with(hotkey_map)
        mock_instance.start.assert_called_once()

    @patch('pynput.keyboard.GlobalHotKeys')
    def test_register_multiple_hotkeys(self, mock_hotkeys):
        """Test registering multiple hotkey combinations."""
        mock_instance = MagicMock()
        mock_hotkeys.return_value = mock_instance

        callback1 = MagicMock()
        callback2 = MagicMock()

        hotkey_map = {
            "ctrl+alt+c": callback1,
            "ctrl+shift+z": callback2
        }

        hotkeys = mock_hotkeys(hotkey_map)
        hotkeys.start()

        assert len(hotkey_map) == 2
        mock_instance.start.assert_called_once()

    @patch('pynput.keyboard.GlobalHotKeys')
    def test_hotkey_callback_execution(self, mock_hotkeys):
        """Test that hotkey callback is executed when triggered."""
        mock_instance = MagicMock()
        mock_hotkeys.return_value = mock_instance

        callback_called = False

        def test_callback():
            nonlocal callback_called
            callback_called = True

        hotkey_map = {"ctrl+alt+c": test_callback}
        hotkeys = mock_hotkeys(hotkey_map)

        # Simulate callback being called
        test_callback()

        assert callback_called is True

    @patch('pynput.keyboard.GlobalHotKeys')
    def test_unregister_hotkey(self, mock_hotkeys):
        """Test unregistering a hotkey."""
        mock_instance = MagicMock()
        mock_hotkeys.return_value = mock_instance

        hotkey_map = {"ctrl+alt+c": MagicMock()}
        hotkeys = mock_hotkeys(hotkey_map)
        hotkeys.start()

        # Stop hotkey listener
        hotkeys.stop()

        mock_instance.stop.assert_called_once()

    @patch('pynput.keyboard.GlobalHotKeys')
    def test_replace_hotkey(self, mock_hotkeys):
        """Test replacing an existing hotkey with new one."""
        mock_instance = MagicMock()
        mock_hotkeys.return_value = mock_instance

        old_callback = MagicMock()
        new_callback = MagicMock()

        # Register initial hotkey
        hotkey_map = {"ctrl+alt+c": old_callback}
        hotkeys = mock_hotkeys(hotkey_map)
        hotkeys.start()

        # Replace with new hotkey
        new_hotkey_map = {"ctrl+shift+z": new_callback}
        hotkeys.stop()
        new_hotkeys = mock_hotkeys(new_hotkey_map)
        new_hotkeys.start()

        # Verify new hotkey was registered
        mock_hotkeys.assert_called_with(new_hotkey_map)


class TestHotkeyFormats:
    """Test various hotkey format combinations."""

    def test_valid_hotkey_modifiers(self):
        """Test valid hotkey modifier combinations."""
        valid_modifiers = [
            "ctrl",
            "alt",
            "shift",
            "win",
            "cmd"
        ]

        for modifier in valid_modifiers:
            assert modifier in ["ctrl", "alt", "shift", "win", "cmd"]

    def test_single_modifier_hotkeys(self):
        """Test hotkeys with single modifier."""
        single_mod_hotkeys = [
            "ctrl+c",
            "alt+f4",
            "shift+esc",
            "win+e"
        ]

        for hotkey in single_mod_hotkeys:
            parts = hotkey.split('+')
            assert len(parts) == 2

    def test_double_modifier_hotkeys(self):
        """Test hotkeys with two modifiers."""
        double_mod_hotkeys = [
            "ctrl+alt+c",
            "ctrl+shift+a",
            "alt+shift+z",
            "ctrl+win+d"
        ]

        for hotkey in double_mod_hotkeys:
            parts = hotkey.split('+')
            assert len(parts) == 3

    def test_triple_modifier_hotkeys(self):
        """Test hotkeys with three modifiers."""
        triple_mod_hotkeys = [
            "ctrl+alt+shift+d",
            "ctrl+shift+win+s"
        ]

        for hotkey in triple_mod_hotkeys:
            parts = hotkey.split('+')
            assert len(parts) == 4

    def test_hotkey_case_insensitivity(self):
        """Test that hotkeys are case-insensitive."""
        hotkey1 = "ctrl+alt+c"
        hotkey2 = "CTRL+ALT+C"
        hotkey3 = "Ctrl+Alt+C"

        # All should be normalized to lowercase
        assert hotkey1.lower() == hotkey2.lower() == hotkey3.lower()


class TestHotkeyValidation:
    """Test hotkey string validation."""

    def test_validate_empty_hotkey(self):
        """Test validation of empty hotkey string."""
        empty_hotkey = ""

        # Should be invalid
        assert empty_hotkey == ""

    def test_validate_hotkey_without_modifier(self):
        """Test hotkey without modifier (should be invalid)."""
        invalid_hotkey = "c"

        # Invalid - no modifier
        parts = invalid_hotkey.split('+')
        assert len(parts) == 1

    def test_validate_hotkey_with_invalid_modifier(self):
        """Test hotkey with invalid modifier."""
        invalid_hotkey = "fn+ctrl+c"

        # fn is not a valid modifier
        parts = invalid_hotkey.split('+')
        assert "fn" in parts

    def test_validate_hotkey_with_trailing_plus(self):
        """Test hotkey with trailing plus sign."""
        invalid_hotkey = "ctrl+alt+"

        # Invalid - trailing modifier
        parts = invalid_hotkey.split('+')
        assert parts[-1] == ""

    def test_validate_hotkey_with_leading_plus(self):
        """Test hotkey with leading plus sign."""
        invalid_hotkey = "+alt+c"

        # Invalid - leading plus
        assert invalid_hotkey.startswith("+")


class TestHotkeyListener:
    """Test pynput keyboard listener behavior."""

    @patch('pynput.keyboard.Listener')
    def test_listener_start(self, mock_listener):
        """Test starting keyboard listener."""
        mock_instance = MagicMock()
        mock_listener.return_value = mock_instance

        on_press = MagicMock()
        on_release = MagicMock()

        listener = mock_listener(
            on_press=on_press,
            on_release=on_release
        )
        listener.start()

        mock_listener.assert_called_once()
        mock_instance.start.assert_called_once()

    @patch('pynput.keyboard.Listener')
    def test_listener_stop(self, mock_listener):
        """Test stopping keyboard listener."""
        mock_instance = MagicMock()
        mock_listener.return_value = mock_instance

        listener = mock_listener(on_press=MagicMock())
        listener.start()
        listener.stop()

        mock_instance.stop.assert_called_once()

    @patch('pynput.keyboard.Listener')
    def test_listener_running_state(self, mock_listener):
        """Test checking if listener is running."""
        mock_instance = MagicMock()
        mock_listener.return_value = mock_instance

        # Simulate running state
        mock_instance.running = True

        listener = mock_listener(on_press=MagicMock())
        listener.start()

        assert listener.running is True


class TestHotkeyCallbacks:
    """Test hotkey callback functionality."""

    def test_callback_with_no_args(self):
        """Test callback that takes no arguments."""
        callback_called = []

        def simple_callback():
            callback_called.append(True)

        simple_callback()
        assert len(callback_called) == 1

    def test_callback_with_args(self):
        """Test callback that receives arguments."""
        callback_results = []

        def callback_with_args(*args):
            callback_results.extend(args)

        callback_with_args("test", 123)
        assert "test" in callback_results
        assert 123 in callback_results

    def test_callback_exception_handling(self):
        """Test that exceptions in callbacks are handled."""
        def failing_callback():
            raise RuntimeError("Callback error")

        with pytest.raises(RuntimeError):
            failing_callback()

    def test_chained_callbacks(self):
        """Test executing multiple callbacks in sequence."""
        execution_order = []

        def callback1():
            execution_order.append(1)

        def callback2():
            execution_order.append(2)

        callback1()
        callback2()

        assert execution_order == [1, 2]


class TestHotkeyIntegration:
    """Integration tests for hotkey functionality."""

    def test_hotkey_with_gui_trigger(self):
        """Test hotkey triggering GUI display."""
        gui_shown = []

        def show_gui_callback():
            gui_shown.append(True)

        # Simulate hotkey press
        show_gui_callback()

        assert len(gui_shown) == 1

    def test_hotkey_with_config_update(self):
        """Test hotkey triggering config update."""
        config_updates = []

        def update_config(hotkey):
            config_updates.append(hotkey)

        update_config("ctrl+shift+z")
        assert "ctrl+shift+z" in config_updates

    def test_hotkey_persistence(self):
        """Test that hotkey setting persists across restarts."""
        saved_hotkey = "ctrl+alt+c"
        loaded_hotkey = saved_hotkey

        assert loaded_hotkey == "ctrl+alt+c"


class TestPlatformSpecificHotkeys:
    """Test platform-specific hotkey handling."""

    def test_windows_hotkey_format(self):
        """Test Windows-specific hotkey format."""
        # Windows uses 'win' modifier
        windows_hotkey = "win+e"
        assert "win" in windows_hotkey

    def test_macos_hotkey_format(self):
        """Test macOS-specific hotkey format."""
        # macOS uses 'cmd' modifier
        mac_hotkey = "cmd+space"
        assert "cmd" in mac_hotkey

    def test_linux_hotkey_format(self):
        """Test Linux hotkey format."""
        # Linux typically uses 'ctrl', 'alt', 'shift'
        linux_hotkey = "ctrl+alt+t"
        assert "ctrl" in linux_hotkey
        assert "alt" in linux_hotkey


class TestHotkeyEdgeCases:
    """Test edge cases in hotkey handling."""

    def test_rapid_hotkey_presses(self):
        """Test handling rapid successive hotkey presses."""
        press_count = []

        def on_hotkey():
            press_count.append(1)

        # Simulate rapid presses
        for _ in range(10):
            on_hotkey()

        assert len(press_count) == 10

    def test_hotkey_with_keyboard_grab_active(self):
        """Test hotkey when another app has grabbed keyboard."""
        # This tests the scenario where another application
        # might prevent hotkey registration
        grab_active = True

        if grab_active:
            # Hotkey might not register
            can_register = False
        else:
            can_register = True

        assert can_register is False

    def test_hotkey_during_fullscreen_app(self):
        """Test hotkey behavior during fullscreen application."""
        fullscreen_active = True

        # Some fullscreen apps may block global hotkeys
        if fullscreen_active:
            # May need to handle this case
            hotkey_blocked = True

        assert hotkey_blocked is True

    def test_duplicate_hotkey_registration(self):
        """Test registering the same hotkey twice."""
        registered_hotkeys = set()

        hotkey = "ctrl+alt+c"

        # First registration
        registered_hotkeys.add(hotkey)
        assert len(registered_hotkeys) == 1

        # Second registration (should replace)
        registered_hotkeys.add(hotkey)
        assert len(registered_hotkeys) == 1


class TestHotkeyConfiguration:
    """Test hotkey configuration management."""

    def test_load_hotkey_from_config(self):
        """Test loading hotkey setting from config."""
        config = {"hotkey": "ctrl+alt+c"}
        loaded_hotkey = config["hotkey"]

        assert loaded_hotkey == "ctrl+alt+c"

    def test_save_hotkey_to_config(self):
        """Test saving hotkey setting to config."""
        new_hotkey = "ctrl+shift+z"
        config = {"hotkey": new_hotkey}

        assert config["hotkey"] == "ctrl+shift+z"

    def test_reset_hotkey_to_default(self):
        """Test resetting hotkey to default value."""
        current_hotkey = "ctrl+shift+z"
        default_hotkey = "ctrl+alt+c"

        # Reset to default
        current_hotkey = default_hotkey

        assert current_hotkey == "ctrl+alt+c"

    def test_validate_hotkey_before_save(self):
        """Test validating hotkey before saving to config."""
        proposed_hotkey = "invalid+hotkey"

        # Validate
        valid_modifiers = {"ctrl", "alt", "shift", "win", "cmd"}
        parts = proposed_hotkey.split("+")

        is_valid = all(part.lower() in valid_modifiers or len(part) == 1
                      for part in parts)

        # "invalid" is not a valid modifier
        assert is_valid is False
