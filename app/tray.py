"""
System tray management for EasyClaude.

Uses pystray library for cross-platform system tray icon and menu.
"""

from typing import Callable, Optional
from PIL import Image, ImageDraw
import pystray
from pystray import Menu, MenuItem


class TrayManager:
    """
    Manages system tray icon and menu for EasyClaude.

    Provides menu items for launching, configuring, and exiting the app.
    """

    def __init__(self):
        """Initialize the tray manager."""
        self._icon: Optional[pystray.Icon] = None
        self._running = False
        self._launch_callback: Optional[Callable[[], None]] = None
        self._config_callback: Optional[Callable[[], None]] = None

        # Create icon
        self._icon_image = self._create_icon()

    def _create_icon(self, size: int = 64) -> Image.Image:
        """
        Create a simple icon for the system tray.

        Args:
            size: Icon size in pixels

        Returns:
            PIL.Image: Icon image
        """
        # Create a square image with transparent background
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw a simple "C" for Claude
        padding = size // 8
        draw.ellipse(
            [padding, padding, size - padding, size - padding],
            fill=(100, 150, 255, 255),  # Light blue
            outline=(50, 100, 200, 255),  # Darker blue outline
            width=max(1, size // 16)
        )

        # Draw the "C" opening
        opening_width = size // 4
        draw.rectangle(
            [size // 2 - opening_width // 2, padding,
             size // 2 + opening_width // 2, size - padding],
            fill=(0, 0, 0, 0)  # Transparent (clear)
        )

        return image

    def _on_launch(self) -> None:
        """Handle launch menu item click."""
        if self._launch_callback:
            self._launch_callback()

    def _on_config(self) -> None:
        """Handle configuration menu item click."""
        if self._config_callback:
            self._config_callback()

    def _on_exit(self) -> None:
        """Handle exit menu item click."""
        self.stop()

    def set_callbacks(
        self,
        launch_callback: Optional[Callable[[], None]] = None,
        config_callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Set callbacks for menu item actions.

        Args:
            launch_callback: Called when "Launch" is clicked
            config_callback: Called when "Configure" is clicked
        """
        if launch_callback:
            self._launch_callback = launch_callback
        if config_callback:
            self._config_callback = config_callback

    def start(self, title: str = "EasyClaude") -> bool:
        """
        Start the system tray icon (blocking - runs in main thread).

        Args:
            title: Tooltip/title for the tray icon

        Returns:
            bool: True if started successfully
        """
        if self._running:
            return False

        # Create menu
        menu = Menu(
            MenuItem("Launch Claude", self._on_launch),
            MenuItem("Configure", self._on_config),
            MenuItem("Exit", self._on_exit),
        )

        # Create icon
        self._icon = pystray.Icon(
            name="easyclaude",
            icon=self._icon_image,
            title=title,
            menu=menu
        )

        # Run the icon (this blocks in the main thread)
        self._running = True
        self._icon.run()

        return True

    def stop(self) -> None:
        """Stop the system tray icon."""
        if self._icon and self._running:
            self._icon.stop()
            self._running = False

    def is_running(self) -> bool:
        """
        Check if tray icon is running.

        Returns:
            bool: True if running
        """
        return self._running

    def update_title(self, title: str) -> None:
        """
        Update the tray icon tooltip/title.

        Args:
            title: New title
        """
        if self._icon:
            self._icon.title = title

    def update_icon(self, image: Image.Image) -> None:
        """
        Update the tray icon image.

        Args:
            image: New icon image
        """
        if self._icon:
            self._icon.icon = image

    def __del__(self):
        """Cleanup when object is destroyed."""
        self.stop()
