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
from app.config import update_config, get_config
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
        # Configure logging FIRST before anything else
        import logging
        from pathlib import Path

        # Set up logging to file and console
        log_dir = Path(os.getenv('APPDATA', '.')) / 'EasyClaude'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / 'easyclaude.log'

        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )

        logger = logging.getLogger(__name__)
        logger.info(f"EasyClaude starting. Log file: {log_file}")

        # Load configuration
        self.config = get_config()
        logger.info(f"Configuration loaded. Hotkey: {self.config.hotkey}")

        # Initialize launcher first
        self.launcher = ClaudeLauncher()
        
        # Initialize GUI and pre-create it on the main thread
        # This prevents issues when showing from hotkey callback thread
        self.gui = LauncherGUI(self._on_launch)
        self.gui._ensure_initialized()  # Pre-initialize GUI
        logger.debug("GUI pre-initialized on main thread")
        
        # Initialize hotkey manager
        self.hotkey_manager = HotkeyManager(self.config.hotkey)
        
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
        logger.info("Application initialized successfully")

    def _on_launch(self, directory: str, command: str):
        """
        Handle launch request from GUI.

        Args:
            directory: Working directory
            command: Command to execute
        """
        import logging
        logger = logging.getLogger(__name__)

        # Save last used settings
        update_config(
            last_directory=directory,
            last_command=command,
        )
        self.config = get_config()
        logger.info(f"Launch requested: directory='{directory}', command='{command}'")

        # Launch Claude (always uses PowerShell)
        success = self.launcher.launch(
            directory=directory,
            command=command
        )

        if not success:
            logger.error(f"Failed to launch Claude in {directory}")

    def show_gui(self):
        """Show the launcher GUI with last used directory."""
        self.config = get_config()
        self.gui.show(
            initial_directory=self.config.last_directory,
        )

    def _show_config_info(self):
        """Show configuration information."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"EasyClaude Configuration:")
        logger.info(f"  Hotkey: {self.config.hotkey}")
        logger.info(f"  Last directory: {self.config.last_directory}")
        logger.info(f"  Last command: {self.config.last_command}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.shutdown()
        sys.exit(0)

    def run(self):
        """Start the application - pystray runs in background thread."""
        import logging
        logger = logging.getLogger(__name__)

        with self._lock:
            self._running = True

        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("EasyClaude is starting...")
        logger.info(f"Hotkey: {self.config.hotkey}")
        logger.info("Press Ctrl+C or use the tray menu to exit.")

        # Start pystray in a background thread so main thread can handle tkinter properly
        import threading
        tray_thread = threading.Thread(
            target=self._run_tray_in_thread,
            name="TrayIconThread",
            daemon=False  # Don't use daemon so tray can exit cleanly
        )
        tray_thread.start()

        # Keep main thread alive with a simple event loop
        # This allows tkinter operations to work properly
        # Also periodically update tkinter to process pending events
        try:
            while self._running:
                self.gui.update()  # Process tkinter events
                time.sleep(0.05)  # 20 FPS for event processing
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        finally:
            self.shutdown()

        # Wait for tray thread to finish
        tray_thread.join(timeout=2.0)

    def _run_tray_in_thread(self):
        """Run the tray icon in a background thread."""
        import logging
        logger = logging.getLogger(__name__)
        try:
            self.tray_manager.start(title="EasyClaude - Press Ctrl+Alt+C to launch")
        except Exception as e:
            logger.error(f"Tray icon error: {e}")
        finally:
            with self._lock:
                self._running = False

    def shutdown(self):
        """Shutdown the application gracefully."""
        import logging
        logger = logging.getLogger(__name__)

        with self._lock:
            if not self._running:
                return
            self._running = False

        logger.info("Shutting down EasyClaude...")

        # Unregister hotkey first
        self.hotkey_manager.unregister()

        # Stop tray icon (this will exit the tray thread)
        self.tray_manager.stop()

        # Destroy GUI
        self.gui.destroy()

        logger.info("EasyClaude has shut down.")


def main():
    """Main entry point for EasyClaude."""
    # Check if another instance is already running
    if not check_single_instance():
        sys.exit(1)

    app = EasyClaudeApp()
    app.run()


if __name__ == "__main__":
    main()
