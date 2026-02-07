"""
Single instance enforcement for EasyClaude.

Uses a named mutex on Windows to ensure only one instance runs at a time.
"""

import sys
import ctypes
from ctypes import wintypes


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
                return False

            # Check if mutex already existed
            error_code = ctypes.windll.kernel32.GetLastError()
            return error_code == ERROR_ALREADY_EXISTS

        except Exception:
            # If anything goes wrong, allow the instance to run
            return False

    def release(self) -> None:
        """Release the mutex."""
        if self._mutex:
            try:
                ctypes.windll.kernel32.ReleaseMutex(self._mutex)
                ctypes.windll.kernel32.CloseHandle(self._mutex)
            except Exception:
                pass
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
        print("Another instance of EasyClaude is already running.")
        print("Only one instance is allowed at a time.")
        return False

    # Store the instance so it gets released on exit
    # We don't want to release it while the app is running
    sys._easyclaude_mutex = instance
    return True


__all__ = ["SingleInstance", "check_single_instance"]
