# Tests for app/tray.py
"""Test system tray functionality with mocked pystray."""

import pytest
from unittest.mock import MagicMock, patch, Mock, call
import threading
import time
from PIL import Image


class TestTrayIconCreation:
    """Test tray icon creation and initialization."""

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Image')
    @patch('app.tray.ImageDraw')
    def test_tray_manager_initialization(self, mock_draw, mock_image, mock_icon):
        """Test TrayManager initialization."""
        # Mock the PIL Image and ImageDraw
        mock_img_instance = MagicMock()
        mock_image.new.return_value = mock_img_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        from app.tray import TrayManager

        manager = TrayManager()

        # Verify initialization
        assert manager._icon is None
        assert manager._running is False
        assert manager._launch_callback is None
        assert manager._config_callback is None
        assert manager._icon_image is not None

    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_create_icon_default_size(self, mock_draw, mock_image_new):
        """Test icon creation with default size."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance

        manager = TrayManager()

        # Verify Image.new was called with default size 64x64
        mock_image_new.assert_called_once_with("RGBA", (64, 64), (0, 0, 0, 0))

    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_create_icon_custom_size(self, mock_draw, mock_image_new):
        """Test icon creation with custom size."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance

        manager = TrayManager()
        custom_size = 128
        manager._create_icon(size=custom_size)

        # Verify Image.new was called with custom size
        mock_image_new.assert_called_with("RGBA", (custom_size, custom_size), (0, 0, 0, 0))

    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_icon_has_transparent_background(self, mock_draw, mock_image_new):
        """Test that icon has transparent background."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        manager = TrayManager()

        # Verify transparent background (alpha = 0)
        mock_image_new.assert_called_once()
        call_args = mock_image_new.call_args
        assert call_args[0][0] == "RGBA"  # RGBA mode for transparency
        assert call_args[0][2] == (0, 0, 0, 0)  # Transparent black

    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_icon_draws_ellipse(self, mock_draw, mock_image_new):
        """Test that icon draws an ellipse (circle)."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        manager = TrayManager()

        # Verify ellipse was drawn
        mock_draw_instance.ellipse.assert_called_once()

    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_icon_draws_opening(self, mock_draw, mock_image_new):
        """Test that icon draws the 'C' opening."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        manager = TrayManager()

        # Verify rectangle was drawn for opening
        mock_draw_instance.rectangle.assert_called_once()


class TestTrayMenuItems:
    """Test tray menu items and their functionality."""

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Menu')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_menu_creation(self, mock_draw, mock_image_new, mock_menu, mock_icon):
        """Test tray menu creation with all menu items."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        mock_menu_instance = MagicMock()
        mock_menu.return_value = mock_menu_instance

        manager = TrayManager()
        manager.start()

        # Verify Menu was created
        mock_menu.assert_called_once()

        # Verify menu items were passed to Menu
        call_args = mock_menu.call_args
        assert len(call_args[0]) == 3  # Three menu items

    @patch('app.tray.MenuItem')
    def test_launch_menu_item(self, mock_menu_item):
        """Test Launch menu item."""
        from app.tray import TrayManager

        manager = TrayManager()
        launch_callback = MagicMock()
        manager.set_callbacks(launch_callback=launch_callback)

        # Trigger launch callback
        manager._on_launch()

        # Verify callback was called
        launch_callback.assert_called_once()

    @patch('app.tray.MenuItem')
    def test_config_menu_item(self, mock_menu_item):
        """Test Configure menu item."""
        from app.tray import TrayManager

        manager = TrayManager()
        config_callback = MagicMock()
        manager.set_callbacks(config_callback=config_callback)

        # Trigger config callback
        manager._on_config()

        # Verify callback was called
        config_callback.assert_called_once()

    @patch('app.tray.MenuItem')
    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_exit_menu_item(self, mock_draw, mock_image_new, mock_icon, mock_menu_item):
        """Test Exit menu item."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        mock_icon_instance = MagicMock()
        mock_icon.return_value = mock_icon_instance

        manager = TrayManager()
        manager.start()

        # Trigger exit callback
        manager._on_exit()

        # Verify stop was called
        assert manager._running is False
        mock_icon_instance.stop.assert_called_once()


class TestTrayCallbacks:
    """Test tray callback functionality."""

    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_set_launch_callback(self, mock_draw, mock_image_new):
        """Test setting launch callback."""
        from app.tray import TrayManager

        manager = TrayManager()
        callback = MagicMock()
        manager.set_callbacks(launch_callback=callback)

        assert manager._launch_callback == callback

    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_set_config_callback(self, mock_draw, mock_image_new):
        """Test setting config callback."""
        from app.tray import TrayManager

        manager = TrayManager()
        callback = MagicMock()
        manager.set_callbacks(config_callback=callback)

        assert manager._config_callback == callback

    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_set_both_callbacks(self, mock_draw, mock_image_new):
        """Test setting both callbacks at once."""
        from app.tray import TrayManager

        manager = TrayManager()
        launch_cb = MagicMock()
        config_cb = MagicMock()

        manager.set_callbacks(
            launch_callback=launch_cb,
            config_callback=config_cb
        )

        assert manager._launch_callback == launch_cb
        assert manager._config_callback == config_cb

    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_callback_not_set_initially(self, mock_draw, mock_image_new):
        """Test that callbacks are None initially."""
        from app.tray import TrayManager

        manager = TrayManager()

        assert manager._launch_callback is None
        assert manager._config_callback is None

    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_launch_callback_without_set(self, mock_draw, mock_image_new):
        """Test calling launch when no callback is set."""
        from app.tray import TrayManager

        manager = TrayManager()

        # Should not raise exception
        manager._on_launch()

    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_config_callback_without_set(self, mock_draw, mock_image_new):
        """Test calling config when no callback is set."""
        from app.tray import TrayManager

        manager = TrayManager()

        # Should not raise exception
        manager._on_config()


class TestTrayLifecycle:
    """Test tray icon lifecycle management."""

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Menu')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_start_tray_icon(self, mock_draw, mock_image_new, mock_menu, mock_icon):
        """Test starting the tray icon."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        mock_icon_instance = MagicMock()
        mock_icon.return_value = mock_icon_instance
        mock_menu_instance = MagicMock()
        mock_menu.return_value = mock_menu_instance

        manager = TrayManager()
        result = manager.start(title="EasyClaude")

        # Verify icon was created with correct parameters
        mock_icon.assert_called_once()
        call_kwargs = mock_icon.call_args[1]
        assert call_kwargs['name'] == 'easyclaude'
        assert call_kwargs['title'] == 'EasyClaude'
        assert call_kwargs['icon'] == manager._icon_image
        assert call_kwargs['menu'] == mock_menu_instance

        # Verify run was called
        mock_icon_instance.run.assert_called_once()

        # Verify running state
        assert manager._running is True
        assert result is True

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Menu')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_start_already_running(self, mock_draw, mock_image_new, mock_menu, mock_icon):
        """Test starting when already running returns False."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        mock_icon_instance = MagicMock()
        mock_icon.return_value = mock_icon_instance
        mock_menu_instance = MagicMock()
        mock_menu.return_value = mock_menu_instance

        manager = TrayManager()
        manager._running = True

        result = manager.start()

        # Should return False without creating new icon
        assert result is False
        mock_icon.assert_not_called()

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Menu')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_stop_tray_icon(self, mock_draw, mock_image_new, mock_menu, mock_icon):
        """Test stopping the tray icon."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        mock_icon_instance = MagicMock()
        mock_icon.return_value = mock_icon_instance
        mock_menu_instance = MagicMock()
        mock_menu.return_value = mock_menu_instance

        manager = TrayManager()
        manager.start()
        manager.stop()

        # Verify stop was called
        mock_icon_instance.stop.assert_called_once()
        assert manager._running is False

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Menu')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_stop_without_start(self, mock_draw, mock_image_new, mock_menu, mock_icon):
        """Test stopping without starting should be safe."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        manager = TrayManager()

        # Should not raise exception
        manager.stop()

        assert manager._running is False

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Menu')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_is_running_state(self, mock_draw, mock_image_new, mock_menu, mock_icon):
        """Test is_running method."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        manager = TrayManager()

        # Initially not running
        assert manager.is_running() is False

        # Simulate running state
        manager._running = True
        assert manager.is_running() is True


class TestTrayUpdates:
    """Test tray icon and title updates."""

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Menu')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_update_title(self, mock_draw, mock_image_new, mock_menu, mock_icon):
        """Test updating tray icon title."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        mock_icon_instance = MagicMock()
        mock_icon.return_value = mock_icon_instance
        mock_menu_instance = MagicMock()
        mock_menu.return_value = mock_menu_instance

        manager = TrayManager()
        manager.start()

        new_title = "EasyClaude - Active"
        manager.update_title(new_title)

        # Verify title was updated
        assert manager._icon.title == new_title

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Menu')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_update_title_without_start(self, mock_draw, mock_image_new, mock_menu, mock_icon):
        """Test updating title without starting should be safe."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        manager = TrayManager()

        # Should not raise exception
        manager.update_title("New Title")

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Menu')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_update_icon(self, mock_draw, mock_image_new, mock_menu, mock_icon):
        """Test updating tray icon image."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        mock_icon_instance = MagicMock()
        mock_icon.return_value = mock_icon_instance
        mock_menu_instance = MagicMock()
        mock_menu.return_value = mock_menu_instance

        manager = TrayManager()
        manager.start()

        # Create a new icon image
        new_image = MagicMock()
        manager.update_icon(new_image)

        # Verify icon was updated
        assert manager._icon.icon == new_image

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Menu')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_update_icon_without_start(self, mock_draw, mock_image_new, mock_menu, mock_icon):
        """Test updating icon without starting should be safe."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        manager = TrayManager()

        # Should not raise exception
        new_image = MagicMock()
        manager.update_icon(new_image)


class TestTrayCleanup:
    """Test tray icon cleanup and resource management."""

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Menu')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_del_calls_stop(self, mock_draw, mock_image_new, mock_menu, mock_icon):
        """Test that __del__ calls stop for cleanup."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        mock_icon_instance = MagicMock()
        mock_icon.return_value = mock_icon_instance
        mock_menu_instance = MagicMock()
        mock_menu.return_value = mock_menu_instance

        manager = TrayManager()
        manager.start()

        # Delete the manager
        del manager

        # Verify stop was called
        mock_icon_instance.stop.assert_called_once()

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Menu')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_del_without_start(self, mock_draw, mock_image_new, mock_menu, mock_icon):
        """Test __del__ without start is safe."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        manager = TrayManager()

        # Should not raise exception
        del manager


class TestTrayThreadSafety:
    """Test thread-safe tray operations."""

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Menu')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_stop_from_different_thread(self, mock_draw, mock_image_new, mock_menu, mock_icon):
        """Test stopping tray icon from a different thread."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        mock_icon_instance = MagicMock()
        mock_icon.return_value = mock_icon_instance
        mock_menu_instance = MagicMock()
        mock_menu.return_value = mock_menu_instance

        manager = TrayManager()
        manager.start()

        # Simulate stop from another thread
        def stop_in_thread():
            manager.stop()

        thread = threading.Thread(target=stop_in_thread)
        thread.start()
        thread.join(timeout=1.0)

        # Verify stop was called (pystray's stop is thread-safe)
        mock_icon_instance.stop.assert_called_once()
        assert manager._running is False

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Menu')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_concurrent_callback_invocations(self, mock_draw, mock_image_new, mock_menu, mock_icon):
        """Test multiple concurrent callback invocations."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        mock_icon_instance = MagicMock()
        mock_icon.return_value = mock_icon_instance
        mock_menu_instance = MagicMock()
        mock_menu.return_value = mock_menu_instance

        manager = TrayManager()

        call_count = []

        def callback():
            call_count.append(1)

        manager.set_callbacks(launch_callback=callback)

        # Simulate concurrent calls
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=manager._on_launch)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join(timeout=1.0)

        # All callbacks should have been called
        assert len(call_count) == 10


class TestTrayIntegrationScenarios:
    """Integration test scenarios for tray functionality."""

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Menu')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_full_lifecycle(self, mock_draw, mock_image_new, mock_menu, mock_icon):
        """Test complete tray lifecycle: init -> start -> update -> stop."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        mock_icon_instance = MagicMock()
        mock_icon.return_value = mock_icon_instance
        mock_menu_instance = MagicMock()
        mock_menu.return_value = mock_menu_instance

        # Initialize
        manager = TrayManager()

        # Set callbacks
        launch_cb = MagicMock()
        config_cb = MagicMock()
        manager.set_callbacks(
            launch_callback=launch_cb,
            config_callback=config_cb
        )

        # Start
        manager.start(title="EasyClaude")
        assert manager.is_running()

        # Update title
        manager.update_title("EasyClaude - Running")

        # Trigger callbacks
        manager._on_launch()
        manager._on_config()

        # Stop
        manager.stop()
        assert not manager.is_running()

        # Verify everything was called
        launch_cb.assert_called_once()
        config_cb.assert_called_once()

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Menu')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_tray_with_hotkey_integration(self, mock_draw, mock_image_new, mock_menu, mock_icon):
        """Test tray integration with hotkey trigger."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        mock_icon_instance = MagicMock()
        mock_icon.return_value = mock_icon_instance
        mock_menu_instance = MagicMock()
        mock_menu.return_value = mock_menu_instance

        manager = TrayManager()

        gui_shown = []

        def show_gui():
            gui_shown.append(True)

        manager.set_callbacks(launch_callback=show_gui)
        manager.start()

        # Simulate hotkey trigger via launch menu
        manager._on_launch()

        assert len(gui_shown) == 1


class TestTrayEdgeCases:
    """Test edge cases and error handling."""

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Menu')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_callback_exception_handling(self, mock_draw, mock_image_new, mock_menu, mock_icon):
        """Test that exceptions in callbacks don't crash tray."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        mock_icon_instance = MagicMock()
        mock_icon.return_value = mock_icon_instance
        mock_menu_instance = MagicMock()
        mock_menu.return_value = mock_menu_instance

        manager = TrayManager()
        manager.start()

        def failing_callback():
            raise RuntimeError("Callback error")

        manager.set_callbacks(launch_callback=failing_callback)

        # Should not raise exception (exception propagates to caller)
        with pytest.raises(RuntimeError):
            manager._on_launch()

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Menu')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_update_callback_after_start(self, mock_draw, mock_image_new, mock_menu, mock_icon):
        """Test updating callbacks after tray has started."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        mock_icon_instance = MagicMock()
        mock_icon.return_value = mock_icon_instance
        mock_menu_instance = MagicMock()
        mock_menu.return_value = mock_menu_instance

        manager = TrayManager()
        manager.start()

        # Update callbacks after start
        new_callback = MagicMock()
        manager.set_callbacks(launch_callback=new_callback)

        manager._on_launch()

        # Verify new callback was called
        new_callback.assert_called_once()

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Menu')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_none_callback_handling(self, mock_draw, mock_image_new, mock_menu, mock_icon):
        """Test handling None callbacks gracefully."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        mock_icon_instance = MagicMock()
        mock_icon.return_value = mock_icon_instance
        mock_menu_instance = MagicMock()
        mock_menu.return_value = mock_menu_instance

        manager = TrayManager()
        manager.start()

        # Set callback to None explicitly
        manager.set_callbacks(launch_callback=None)

        # Should not raise exception
        manager._on_launch()


class TestSingleInstanceEnforcement:
    """Test single instance enforcement functionality."""

    @patch('ctypes.windll.kernel32.CreateMutexW')
    @patch('ctypes.windll.kernel32.GetLastError')
    def test_single_instance_first_instance(self, mock_get_last_error, mock_create_mutex):
        """Test single instance check for first instance."""
        from app.single_instance import SingleInstance

        # Simulate first instance (mutex doesn't exist)
        mock_mutex = MagicMock()
        mock_create_mutex.return_value = mock_mutex
        mock_get_last_error.return_value = 0  # No error

        instance = SingleInstance()
        is_running = instance.is_already_running()

        # Verify mutex was created
        mock_create_mutex.assert_called_once()
        assert is_running is False

    @patch('ctypes.windll.kernel32.CreateMutexW')
    @patch('ctypes.windll.kernel32.GetLastError')
    def test_single_instance_second_instance(self, mock_get_last_error, mock_create_mutex):
        """Test single instance check for second instance."""
        from app.single_instance import SingleInstance

        # Simulate second instance (mutex already exists)
        mock_mutex = MagicMock()
        mock_create_mutex.return_value = mock_mutex
        mock_get_last_error.return_value = 183  # ERROR_ALREADY_EXISTS

        instance = SingleInstance()
        is_running = instance.is_already_running()

        # Should detect existing instance
        assert is_running is True

    @patch('ctypes.windll.kernel32.CreateMutexW')
    @patch('ctypes.windll.kernel32.ReleaseMutex')
    @patch('ctypes.windll.kernel32.CloseHandle')
    def test_single_instance_release(self, mock_close_handle, mock_release_mutex, mock_create_mutex):
        """Test releasing single instance mutex."""
        from app.single_instance import SingleInstance

        mock_mutex = MagicMock()
        mock_create_mutex.return_value = mock_mutex

        instance = SingleInstance()
        instance.is_already_running()

        # Release the mutex
        instance.release()

        # Verify release and close were called
        mock_release_mutex.assert_called_once_with(mock_mutex)
        mock_close_handle.assert_called_once_with(mock_mutex)
        assert instance._mutex is None

    @patch('ctypes.windll.kernel32.CreateMutexW')
    @patch('ctypes.windll.kernel32.GetLastError')
    def test_single_instance_context_manager(self, mock_get_last_error, mock_create_mutex):
        """Test single instance as context manager."""
        from app.single_instance import SingleInstance

        mock_mutex = MagicMock()
        mock_create_mutex.return_value = mock_mutex
        mock_get_last_error.return_value = 0

        with SingleInstance() as instance:
            assert instance._mutex is not None

    @patch('ctypes.windll.kernel32.CreateMutexW')
    @patch('ctypes.windll.kernel32.GetLastError')
    def test_custom_mutex_name(self, mock_get_last_error, mock_create_mutex):
        """Test single instance with custom mutex name."""
        from app.single_instance import SingleInstance

        custom_name = "MyCustomApp_Mutex"
        mock_mutex = MagicMock()
        mock_create_mutex.return_value = mock_mutex
        mock_get_last_error.return_value = 0

        instance = SingleInstance(mutex_name=custom_name)
        instance.is_already_running()

        # Verify custom name was used
        call_args = mock_create_mutex.call_args
        assert call_args[0][2] == custom_name

    @patch('ctypes.windll.kernel32.CreateMutexW')
    def test_single_instance_failure_handling(self, mock_create_mutex):
        """Test single instance handles mutex creation failure."""
        from app.single_instance import SingleInstance

        # Simulate mutex creation failure
        mock_create_mutex.return_value = None

        instance = SingleInstance()
        is_running = instance.is_already_running()

        # Should return False (allow instance to run)
        assert is_running is False

    @patch('ctypes.windll.kernel32.CreateMutexW')
    @patch('ctypes.windll.kernel32.GetLastError')
    @patch('builtins.print')
    def test_check_single_instance_function(self, mock_print, mock_get_last_error, mock_create_mutex):
        """Test check_single_instance convenience function."""
        from app.single_instance import check_single_instance

        mock_mutex = MagicMock()
        mock_create_mutex.return_value = mock_mutex
        mock_get_last_error.return_value = 0

        result = check_single_instance()

        # Should return True for first instance
        assert result is True

    @patch('ctypes.windll.kernel32.CreateMutexW')
    @patch('ctypes.windll.kernel32.GetLastError')
    @patch('builtins.print')
    def test_check_single_instance_already_running(self, mock_print, mock_get_last_error, mock_create_mutex):
        """Test check_single_instance when already running."""
        from app.single_instance import check_single_instance

        mock_mutex = MagicMock()
        mock_create_mutex.return_value = mock_mutex
        mock_get_last_error.return_value = 183  # ERROR_ALREADY_EXISTS

        result = check_single_instance()

        # Should return False and print message
        assert result is False
        assert mock_print.call_count >= 2  # Two print statements


class TestTrayHotkeyIntegration:
    """Test integration between tray and hotkey functionality."""

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Menu')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    @patch('app.hotkey.HotkeyManager')
    def test_hotkey_triggers_tray_launch_callback(self, mock_hotkey_mgr, mock_draw, mock_image_new, mock_menu, mock_icon):
        """Test that hotkey trigger invokes tray launch callback."""
        from app.tray import TrayManager
        from app.hotkey import HotkeyManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        mock_icon_instance = MagicMock()
        mock_icon.return_value = mock_icon_instance
        mock_menu_instance = MagicMock()
        mock_menu.return_value = mock_menu_instance

        tray_manager = TrayManager()

        # Track if callback was invoked
        gui_shown = []

        def show_gui():
            gui_shown.append(True)

        tray_manager.set_callbacks(launch_callback=show_gui)

        # Simulate hotkey triggering the callback
        tray_manager._on_launch()

        assert len(gui_shown) == 1


class TestCleanShutdown:
    """Test clean shutdown scenarios."""

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Menu')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    @patch('app.hotkey.HotkeyManager')
    def test_shutdown_sequence(self, mock_hotkey_mgr, mock_draw, mock_image_new, mock_menu, mock_icon):
        """Test proper shutdown sequence."""
        from app.tray import TrayManager
        from app.hotkey import HotkeyManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        mock_icon_instance = MagicMock()
        mock_icon.return_value = mock_icon_instance
        mock_menu_instance = MagicMock()
        mock_menu.return_value = mock_menu_instance

        mock_hotkey_instance = MagicMock()
        mock_hotkey_mgr.return_value = mock_hotkey_instance

        # Initialize components
        tray_manager = TrayManager()
        tray_manager.start()

        hotkey_manager = HotkeyManager("ctrl+alt+c")
        hotkey_manager.register(MagicMock())

        # Shutdown sequence
        tray_manager.stop()
        hotkey_manager.unregister()

        # Verify clean shutdown
        assert not tray_manager.is_running()
        assert not hotkey_manager.is_active()

    @patch('app.tray.pystray.Icon')
    @patch('app.tray.Menu')
    @patch('app.tray.Image.new')
    @patch('app.tray.ImageDraw.Draw')
    def test_exit_menu_triggers_shutdown(self, mock_draw, mock_image_new, mock_menu, mock_icon):
        """Test that Exit menu item triggers proper shutdown."""
        from app.tray import TrayManager

        mock_image_instance = MagicMock()
        mock_image_new.return_value = mock_image_instance
        mock_draw_instance = MagicMock()
        mock_draw.Draw.return_value = mock_draw_instance

        mock_icon_instance = MagicMock()
        mock_icon.return_value = mock_icon_instance
        mock_menu_instance = MagicMock()
        mock_menu.return_value = mock_menu_instance

        manager = TrayManager()
        manager.start()

        # Simulate clicking Exit menu
        manager._on_exit()

        # Verify shutdown
        assert manager._running is False
        mock_icon_instance.stop.assert_called_once()
