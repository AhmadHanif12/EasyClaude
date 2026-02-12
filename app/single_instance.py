"""
Single instance enforcement for EasyClaude.

Uses a named mutex on Windows to ensure only one instance runs at a time.
"""

import sys
import ctypes
import logging
from ctypes import wintypes

logger = logging.getLogger(__name__)


class SingleInstance:
    """
    Ensures only one instance of the application is running.

    Uses Windows named mutex for cross-process synchronization.
    """

    def __init__(self, mutex_name: str = "EasyClaude_SingleInstance_Mutex"):
        """
        Initialize the single instance checker.

        Args:
            mutex_name: Unique name for the mutex
        """
        self.mutex_name = mutex_name
        self._mutex = None

    def is_already_running(self) -> bool:
        """
        Check if another instance is already running.

        Returns:
            bool: True if another instance is running
        """
        # Try to create or open the mutex
        # ERROR_ALREADY_EXISTS = 183
        ERROR_ALREADY_EXISTS = 183

        try:
            self._mutex = ctypes.windll.kernel32.CreateMutexW(
                None,
                True,  # Initial owner
                self.mutex_name
            )

            if self._mutex is None:
                # Failed to create mutex, assume not running
                # (or we don't have permissions, but let it proceed)
                logger.warning("Failed to create mutex - allowing instance to run")
                return False

            # Check if mutex already existed
            error_code = ctypes.windll.kernel32.GetLastError()
            return error_code == ERROR_ALREADY_EXISTS

        except Exception as e:
            # If anything goes wrong, log and allow the instance to run
            logger.warning(f"Failed to check mutex: {e} - allowing instance to run")
            return False

    def release(self) -> None:
        """Release the mutex."""
        if self._mutex:
            try:
                ctypes.windll.kernel32.ReleaseMutex(self._mutex)
                ctypes.windll.kernel32.CloseHandle(self._mutex)
            except Exception as e:
                logger.debug(f"Failed to release mutex: {e}")
            self._mutex = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()


def check_single_instance() -> bool:
    """
    Check if this is the only instance of EasyClaude.

    Returns:
        bool: True if this is the first instance, False if another is running
    """
    instance = SingleInstance()
    if instance.is_already_running():
        # GUI builds do not show stdout/stderr, so surface this as a dialog.
        try:
            MB_OK = 0x00000000
            MB_ICONWARNING = 0x00000030
            MB_TOPMOST = 0x00040000
            ctypes.windll.user32.MessageBoxW(
                None,
                "EasyClaude is already running in your system tray.\n\nClose the existing instance before starting a new one.",
                "EasyClaude",
                MB_OK | MB_ICONWARNING | MB_TOPMOST,
            )
        except Exception as e:
            # Fallback in case user32 is unavailable.
            logger.warning(f"Failed to show message box: {e}")
            print("Another instance of EasyClaude is already running.")
            print("Only one instance is allowed at a time.")
        return False

    # Store the instance so it gets released on exit
    # We don't want to release it while the app is running
    sys._easyclaude_mutex = instance
    return True


__all__ = ["SingleInstance", "check_single_instance"]
