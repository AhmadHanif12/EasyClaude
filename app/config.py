"""
Configuration management for EasyClaude.

Uses pydantic for type-safe configuration persistence.
Config is stored at ~/.easyclaude/config.json
"""

import json
import logging
import threading
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, validator
import platform

logger = logging.getLogger(__name__)


# Default configuration values
DEFAULT_HOTKEY = "ctrl+alt+c"
DEFAULT_COMMAND = "claude"
DEFAULT_WINDOW_POSITION = "center"
DEFAULT_ALWAYS_USE_POWERSHELL = False


class Config(BaseModel):
    """
    Application configuration model.

    Attributes:
        hotkey: Global hotkey combination (e.g., "ctrl+alt+c")
        last_directory: Last used working directory
        last_command: Last executed command
        always_use_powershell: Whether to always use PowerShell
        window_position: Window position ("center" or "x,y")
    """

    hotkey: str = Field(default=DEFAULT_HOTKEY, description="Global hotkey combination")
    last_directory: str = Field(default="", description="Last used working directory")
    last_command: str = Field(default=DEFAULT_COMMAND, description="Last executed command")
    always_use_powershell: bool = Field(
        default=DEFAULT_ALWAYS_USE_POWERSHELL, description="Always use PowerShell"
    )
    window_position: str = Field(
        default=DEFAULT_WINDOW_POSITION, description="Window position"
    )

    @validator("hotkey")
    def validate_hotkey(cls, v: str) -> str:
        """Validate hotkey format."""
        if not v or not v.strip():
            return DEFAULT_HOTKEY
        # Normalize to lowercase
        return v.strip().lower()

    @validator("window_position")
    def validate_window_position(cls, v: str) -> str:
        """Validate window position format."""
        if not v or not v.strip():
            return DEFAULT_WINDOW_POSITION
        v = v.strip().lower()
        if v == "center":
            return v
        # Validate x,y format
        try:
            parts = v.split(",")
            if len(parts) == 2:
                x, y = int(parts[0].strip()), int(parts[1].strip())
                if x >= 0 and y >= 0:
                    return f"{x},{y}"
        except (ValueError, AttributeError):
            pass
        return DEFAULT_WINDOW_POSITION

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            Path: str,
        }


def get_config_dir() -> Path:
    """
    Get the platform-specific config directory.

    Returns:
        Path: Configuration directory path
    """
    system = platform.system()
    home = Path.home()

    if system == "Windows":
        config_dir = home / ".easyclaude"
    elif system == "Darwin":  # macOS
        config_dir = home / "Library" / "Application Support" / "EasyClaude"
    else:  # Linux and others
        # Follow XDG Base Directory Specification
        config_dir = home / ".config" / "easyclaude"

    return config_dir


def get_config_path() -> Path:
    """
    Get the full path to the config file.

    Returns:
        Path: Config file path
    """
    config_dir = get_config_dir()
    return config_dir / "config.json"


def load_config() -> Config:
    """
    Load configuration from file, creating default if doesn't exist.

    Returns:
        Config: Configuration object
    """
    config_path = get_config_path()

    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return Config(**data)
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            # If config is corrupted, log and return default
            logger.warning(f"Failed to load config: {e}. Using defaults.")
            return Config()
    else:
        # Create default config
        config = Config()
        save_config(config)
        logger.info(f"Created default configuration at {config_path}")
        return config


def save_config(config: Config) -> bool:
    """
    Save configuration to file.

    Args:
        config: Configuration object to save

    Returns:
        bool: True if successful, False otherwise
    """
    config_path = get_config_path()
    config_dir = config_path.parent

    try:
        # Ensure config directory exists
        config_dir.mkdir(parents=True, exist_ok=True)

        # Save config
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config.dict(), f, indent=2)

        logger.debug(f"Configuration saved to {config_path}")
        return True
    except (OSError, IOError) as e:
        logger.error(f"Failed to save config: {e}")
        return False


# Global config instance (lazy-loaded)
_config_cache: Optional[Config] = None
_config_lock = threading.Lock()


def get_config() -> Config:
    """
    Get the global configuration instance (cached).

    Thread-safe singleton pattern with lazy loading.

    Returns:
        Config: Configuration object
    """
    global _config_cache
    if _config_cache is None:
        with _config_lock:
            # Double-check pattern
            if _config_cache is None:
                _config_cache = load_config()
                logger.debug("Configuration loaded and cached")
    return _config_cache


def update_config(**kwargs) -> bool:
    """
    Update configuration with new values and save.

    Thread-safe update with lock.

    Args:
        **kwargs: Configuration fields to update

    Returns:
        bool: True if successful, False otherwise
    """
    global _config_cache
    with _config_lock:
        config = get_config()

        # Update only valid fields
        update_data = {}
        for key, value in kwargs.items():
            if key in config.__fields__:
                update_data[key] = value

        if update_data:
            # Create new config with updated values
            _config_cache = Config(**{**config.dict(), **update_data})
            result = save_config(_config_cache)
            if result:
                logger.debug(f"Configuration updated: {list(update_data.keys())}")
            return result

        return False


def reset_config() -> bool:
    """
    Reset configuration to defaults and save.

    Thread-safe reset with lock.

    Returns:
        bool: True if successful, False otherwise
    """
    global _config_cache
    with _config_lock:
        _config_cache = Config()
        result = save_config(_config_cache)
        if result:
            logger.info("Configuration reset to defaults")
        return result


def invalidate_cache() -> None:
    """
    Invalidate the configuration cache.

    Forces reload on next get_config() call. Useful for testing.
    """
    global _config_cache
    with _config_lock:
        _config_cache = None
        logger.debug("Configuration cache invalidated")
