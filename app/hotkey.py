"""
Global hotkey management for EasyClaude.

Uses pynput library for cross-platform global hotkey registration.
"""

import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Optional
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

logger = logging.getLogger(__name__)


class HotkeyValidationError(Exception):
    """Raised when hotkey string is invalid."""
    pass


class HotkeyManager:
    """
    Manages global hotkey registration and callback handling.

    Provides thread-safe hotkey registration with proper cleanup.
    """

    def __init__(self, hotkey_string: str = "ctrl+alt+c"):
        """
        Initialize the hotkey manager.

        Args:
            hotkey_string: Hotkey combination (e.g., "ctrl+alt+c")

        Raises:
            HotkeyValidationError: If hotkey string is invalid
        """
        self._hotkey_string = hotkey_string
        self._callback: Optional[Callable[[], None]] = None
        self._listener: Optional[keyboard.Listener] = None
        self._hotkey_combination: Optional[tuple] = None
        self._pressed_keys = set()
        self._lock = threading.Lock()
        self._active = False
        self._executor: Optional[ThreadPoolExecutor] = None

        # Parse the hotkey string
        self._parse_hotkey()

    def _parse_hotkey(self) -> None:
        """
        Parse hotkey string into pynput-compatible format.

        Supports format: "ctrl+alt+c", "shift+cmd+a", etc.

        Raises:
            HotkeyValidationError: If hotkey string is invalid or cannot be parsed
        """
        if not self._hotkey_string or not self._hotkey_string.strip():
            raise HotkeyValidationError("Hotkey string cannot be empty")

        parts = self._hotkey_string.lower().replace(" ", "").split("+")
        combination = []
        invalid_keys = []

        for part in parts:
            if part in ("ctrl", "control"):
                combination.append(Key.ctrl_l)
            elif part in ("alt",):
                combination.append(Key.alt_l)
            elif part in ("shift",):
                combination.append(Key.shift_l)
            elif part in ("cmd", "win", "meta", "command"):
                combination.append(Key.cmd)
            elif part in ("cmd_r", "win_r", "meta_r"):
                combination.append(Key.cmd_r)
            elif part in ("ctrl_r", "control_r"):
                combination.append(Key.ctrl_r)
            elif part in ("alt_r",):
                combination.append(Key.alt_r)
            elif part in ("shift_r",):
                combination.append(Key.shift_r)
            elif len(part) == 1:
                # Single character key
                try:
                    combination.append(KeyCode.from_char(part))
                except KeyError:
                    invalid_keys.append(part)
            else:
                # Try to parse as special key name
                try:
                    key = getattr(Key, part.lower())
                    combination.append(key)
                except AttributeError:
                    invalid_keys.append(part)

        if invalid_keys:
            raise HotkeyValidationError(
                f"Unknown key(s) in hotkey: {', '.join(invalid_keys)}. "
                f"Valid formats: modifier+key (e.g., ctrl+alt+c)"
            )

        if not combination:
            raise HotkeyValidationError(
                f"Could not parse hotkey '{self._hotkey_string}'. "
                "Format: modifier+key (e.g., ctrl+alt+c)"
            )

        self._hotkey_combination = tuple(combination)
        logger.debug(f"Parsed hotkey '{self._hotkey_string}' successfully")

    def _on_press(self, key) -> None:
        """
        Handle key press events.

        Args:
            key: The key that was pressed
        """
        with self._lock:
            self._pressed_keys.add(key)

            # Check if hotkey combination is pressed
            if self._hotkey_combination and self._callback:
                if self._is_hotkey_pressed():
                    # Call callback in a separate thread to avoid blocking
                    # Use executor with max_workers=1 to prevent unbounded thread creation
                    if self._executor is None:
                        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="hotkey_callback")

                    def safe_callback():
                        try:
                            self._callback()
                        except Exception as e:
                            logger.error(f"Error in hotkey callback: {e}", exc_info=True)

                    self._executor.submit(safe_callback)

    def _on_release(self, key) -> None:
        """
        Handle key release events.

        Args:
            key: The key that was released
        """
        with self._lock:
            self._pressed_keys.discard(key)

    def _is_hotkey_pressed(self) -> bool:
        """
        Check if the hotkey combination is currently pressed.

        Returns:
            bool: True if hotkey is pressed
        """
        if not self._hotkey_combination:
            return False

        # Check if all keys in combination are pressed
        for key in self._hotkey_combination:
            if key not in self._pressed_keys:
                return False

        return True

    def register(self, callback: Callable[[], None]) -> bool:
        """
        Register a callback to be invoked when hotkey is pressed.

        Args:
            callback: Function to call when hotkey is pressed

        Returns:
            bool: True if registration successful
        """
        with self._lock:
            if self._active:
                return False

            self._callback = callback

            # Start the keyboard listener
            self._listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self._listener.start()
            self._active = True

            return True

    def unregister(self) -> None:
        """
        Unregister the hotkey and stop listening.
        """
        with self._lock:
            if self._listener:
                self._listener.stop()
                self._listener = None
            if self._executor:
                self._executor.shutdown(wait=False)
                self._executor = None
            self._callback = None
            self._active = False
            logger.debug("Hotkey unregistered")

    def set_hotkey(self, hotkey_string: str) -> bool:
        """
        Change the hotkey combination.

        Args:
            hotkey_string: New hotkey combination

        Returns:
            bool: True if hotkey was changed successfully

        Raises:
            HotkeyValidationError: If hotkey string is invalid
        """
        was_active = self._active

        # Unregister if active
        if was_active:
            self.unregister()

        # Parse new hotkey
        old_hotkey = self._hotkey_string
        self._hotkey_string = hotkey_string

        try:
            self._parse_hotkey()
        except HotkeyValidationError as e:
            # Restore old hotkey on failure
            self._hotkey_string = old_hotkey
            try:
                self._parse_hotkey()
            except HotkeyValidationError:
                pass
            raise

        # Re-register if was active
        if was_active and self._callback:
            return self.register(self._callback)

        logger.info(f"Hotkey changed to '{hotkey_string}'")
        return True

    def is_active(self) -> bool:
        """
        Check if hotkey listener is active.

        Returns:
            bool: True if active
        """
        return self._active

    def get_hotkey(self) -> str:
        """
        Get current hotkey string.

        Returns:
            str: Current hotkey combination
        """
        return self._hotkey_string

    def __del__(self):
        """Cleanup when object is destroyed."""
        self.unregister()
