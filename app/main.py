"""
EasyClaude - Main entry point.

A Windows system tray application for launching Claude Code
from any directory via global hotkey.
"""

import sys
import os
import signal
import threading
import time
from app.config import load_config, update_config, get_config
from app.hotkey import HotkeyManager
from app.tray import TrayManager
from app.gui import LauncherGUI
from app.launcher import ClaudeLauncher
from app.single_instance import check_single_instance


class EasyClaudeApp:
    """
    Main application class for EasyClaude.

    Coordinates tray icon, hotkey, GUI, and launcher.
    """

    def __init__(self):
        """Initialize the application."""
        # Load configuration
        self.config = load_config()

        # Initialize components
        self.launcher = ClaudeLauncher()
        self.hotkey_manager = HotkeyManager(self.config.hotkey)
        self.gui = LauncherGUI(self._on_launch)
        self._running = False
        self._lock = threading.Lock()

        # Create tray icon (but don't start yet)
        self.tray_manager = TrayManager()

        # Set up tray callbacks
        self.tray_manager.set_callbacks(
            launch_callback=self.show_gui,
            config_callback=self._show_config_info
        )

        # Register hotkey
        self.hotkey_manager.register(self.show_gui)

    def _on_launch(self, directory: str, command: str, use_powershell: bool):
        """
        Handle launch request from GUI.

        Args:
            directory: Working directory
            command: Command to execute
            use_powershell: Whether to use PowerShell
        """
        # Save last used settings
        update_config(
            last_directory=directory,
            last_command=command,
        )

        # Launch Claude
        success = self.launcher.launch(
            directory=directory,
            command=command,
            use_powershell=use_powershell
        )

        if not success:
            print(f"Failed to launch Claude in {directory}")

    def show_gui(self):
        """Show the launcher GUI with last used directory."""
        self.gui.show(initial_directory=self.config.last_directory)

    def _show_config_info(self):
        """Show configuration information."""
        print(f"EasyClaude Configuration:")
        print(f"  Hotkey: {self.config.hotkey}")
        print(f"  Last directory: {self.config.last_directory}")
        print(f"  Last command: {self.config.last_command}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.shutdown()
        sys.exit(0)

    def run(self):
        """Start the application - pystray runs in main thread."""
        with self._lock:
            self._running = True

        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        print("EasyClaude is starting...")
        print(f"Hotkey: {self.config.hotkey}")
        print("Press Ctrl+C or use the tray menu to exit.")

        # Start the tray icon - this blocks in the main thread
        # pystray will handle the event loop
        self.tray_manager.start(title="EasyClaude - Press Ctrl+Alt+C to launch")

        # After tray stops, mark as not running
        with self._lock:
            self._running = False

    def shutdown(self):
        """Shutdown the application gracefully."""
        with self._lock:
            if not self._running:
                return
            self._running = False

        print("Shutting down EasyClaude...")

        # Unregister hotkey
        self.hotkey_manager.unregister()

        # Stop tray icon
        self.tray_manager.stop()

        # Destroy GUI
        self.gui.destroy()

        print("EasyClaude has shut down.")


def main():
    """Main entry point for EasyClaude."""
    # Check if another instance is already running
    if not check_single_instance():
        sys.exit(1)

    app = EasyClaudeApp()
    app.run()


if __name__ == "__main__":
    main()
