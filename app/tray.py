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
        Load the icon for the system tray.

        Args:
            size: Icon size in pixels (used for fallback only)

        Returns:
            PIL.Image: Icon image
        """
        import sys
        import os
        
        # Try to find the icon file
        icon_paths = [
            # When running from source
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icon.png"),
            # When running from PyInstaller bundle
            os.path.join(getattr(sys, '_MEIPASS', ''), "assets", "icon.png"),
            # Relative to current directory
            os.path.join("assets", "icon.png"),
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                try:
                    # Open and immediately load+copy the image to release file handle
                    with Image.open(icon_path) as img:
                        # Load the image data into memory
                        img.load()
                        # Create a copy that doesn't hold a file reference
                        image = img.copy()
                    # Resize to appropriate size for system tray
                    image = image.resize((size, size), Image.Resampling.LANCZOS)
                    return image.convert("RGBA")
                except Exception:
                    pass
        
        # Fallback: Create a simple icon if file not found
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        padding = size // 8
        draw.ellipse(
            [padding, padding, size - padding, size - padding],
            fill=(255, 100, 50, 255),  # Orange to match new icon
            outline=(200, 80, 40, 255),
            width=max(1, size // 16)
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
        """Stop the system tray icon - thread-safe."""
        if self._icon and self._running:
            self._running = False
            # Use pystray's stop method which is thread-safe
            # It sends a message to the icon's message loop
            self._icon.stop()

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
