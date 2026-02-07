"""
EasyClaude - Main entry point.

A Windows system tray application for launching Claude Code
from any directory via global hotkey.
"""

import sys
import os
import signal
from app.config import load_config, update_config, get_config
from app.hotkey import HotkeyManager
from app.tray import TrayManager
from app.gui import LauncherGUI
from app.launcher import ClaudeLauncher


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
        self.tray_manager = TrayManager()
        self.gui = LauncherGUI(self._on_launch)

        # Set up tray callbacks
        self.tray_manager.set_callbacks(
            launch_callback=self.show_gui,
            config_callback=self._show_config_info
        )

        # Register hotkey
        self.hotkey_manager.register(self.show_gui)

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

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
        """Show configuration information (placeholder)."""
        print(f"EasyClaude Configuration:")
        print(f"  Hotkey: {self.config.hotkey}")
        print(f"  Last directory: {self.config.last_directory}")
        print(f"  Last command: {self.config.last_command}")

    def _signal_handler(self, signum, frame):
        """
        Handle shutdown signals for graceful exit.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        self.shutdown()
        sys.exit(0)

    def run(self):
        """Start the application main loop."""
        # Start tray icon
        self.tray_manager.start(title="EasyClaude - Press Ctrl+Alt+C to launch")

        print("EasyClaude is running in the system tray.")
        print(f"Press {self.config.hotkey} to open the launcher, or use the tray menu.")
        print("Press Ctrl+C to exit.")

        # Keep the main thread alive
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        """Shutdown the application gracefully."""
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
    app = EasyClaudeApp()
    app.run()


if __name__ == "__main__":
    main()
