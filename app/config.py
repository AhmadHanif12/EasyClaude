"""
Configuration management for EasyClaude.

Uses pydantic for type-safe configuration persistence.
Config is stored at ~/.easyclaude/config.json
"""

import json
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, Field, validator
import platform

logger = logging.getLogger(__name__)


# Default configuration values
DEFAULT_HOTKEY = "ctrl+alt+c"
DEFAULT_COMMAND = "claude"
DEFAULT_WINDOW_POSITION = "center"
DEFAULT_MAX_HISTORY_ENTRIES = 15


class DirectoryEntry(BaseModel):
    """
    Represents a single directory entry in the history.

    Attributes:
        path: Directory path
        last_used: ISO format timestamp of last usage
        usage_count: Number of times this directory was used
    """

    path: str = Field(..., description="Directory path")
    last_used: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO format timestamp of last usage"
    )
    usage_count: int = Field(default=1, description="Number of times used", ge=1)

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: str,
        }


class Config(BaseModel):
    """
    Application configuration model.

    Attributes:
        hotkey: Global hotkey combination (e.g., "ctrl+alt+c")
        last_directory: Last used working directory
        last_command: Last executed command
        window_position: Window position ("center" or "x,y")
        directory_history: List of directory entries with metadata (max 15)
        recent_directories: Legacy field - migrated to directory_history
    """

    hotkey: str = Field(default=DEFAULT_HOTKEY, description="Global hotkey combination")
    last_directory: str = Field(default="", description="Last used working directory")
    last_command: str = Field(default=DEFAULT_COMMAND, description="Last executed command")
    window_position: str = Field(
        default=DEFAULT_WINDOW_POSITION, description="Window position"
    )
    directory_history: List[DirectoryEntry] = Field(
        default_factory=list,
        description="Directory history with metadata (path, timestamp, usage count)"
    )
    recent_directories: list[str] = Field(
        default_factory=list, description="Legacy: Recently used directories (use directory_history)"
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

    @validator("directory_history", pre=True)
    def validate_directory_history(cls, v):
        """Validate and clean directory history list.

        Ensures:
        - All items are valid DirectoryEntry objects
        - Paths are unique (duplicates removed, first occurrence kept)
        - Max 15 entries
        - Handles migration from legacy recent_directories format
        """
        if v is None:
            return []
        if not isinstance(v, list):
            return []

        # Handle migration from legacy string list format
        if v and isinstance(v[0], str):
            # Migrate from old format: list of strings
            # Keep original order (most recent first)
            migrated = []
            for path in v:
                if isinstance(path, str) and path and path not in {e.path for e in migrated}:
                    migrated.append(DirectoryEntry(path=path))
                if len(migrated) >= DEFAULT_MAX_HISTORY_ENTRIES:
                    break
            return migrated

        # Process DirectoryEntry objects or dicts (from JSON)
        # Keep order, removing duplicates (first occurrence wins)
        seen_paths = set()
        result = []
        for entry in v:
            # Handle both DirectoryEntry objects and dicts
            if isinstance(entry, dict):
                path = entry.get("path", "")
                last_used = entry.get("last_used", datetime.now().isoformat())
                usage_count = entry.get("usage_count", 1)
            elif isinstance(entry, DirectoryEntry):
                path = entry.path
                last_used = entry.last_used
                usage_count = entry.usage_count
            else:
                continue

            if not path or not isinstance(path, str):
                continue

            # Skip duplicates, keeping first occurrence
            if path in seen_paths:
                continue

            seen_paths.add(path)
            result.append(DirectoryEntry(
                path=path,
                last_used=last_used,
                usage_count=usage_count
            ))

            if len(result) >= DEFAULT_MAX_HISTORY_ENTRIES:
                break

        return result

    @validator("recent_directories", pre=True)
    def validate_recent_directories(cls, v):
        """Validate and clean recent directories list."""
        if v is None:
            return []
        if not isinstance(v, list):
            return []
        # Ensure all items are strings and unique, keep max 15
        seen = set()
        cleaned = []
        for item in reversed(v):
            if isinstance(item, str) and item and item not in seen:
                seen.add(item)
                cleaned.insert(0, item)
                if len(cleaned) >= 15:
                    break
        return cleaned

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
            json.dump(config.model_dump(), f, indent=2)

        logger.debug(f"Configuration saved to {config_path}")
        return True
    except (OSError, IOError) as e:
        logger.error(f"Failed to save config: {e}")
        return False


# Global config instance (lazy-loaded)
_config_cache: Optional[Config] = None
# Re-entrant lock avoids deadlocks when update paths call get_config() while
# already holding the config lock.
_config_lock = threading.RLock()


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
            if key in config.model_fields:
                update_data[key] = value

        if update_data:
            # Create new config with updated values
            _config_cache = Config(**{**config.model_dump(), **update_data})
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


def add_directory_to_history(directory: str) -> bool:
    """
    Add a directory to the history, moving existing entries to the top.

    If the directory already exists in history, its timestamp and usage count
    are updated, and it's moved to the top of the list.

    Args:
        directory: Directory path to add to history

    Returns:
        bool: True if successful, False otherwise
    """
    global _config_cache
    with _config_lock:
        config = get_config()

        # Find existing entry or create new one
        existing_index = -1
        for i, entry in enumerate(config.directory_history):
            if entry.path == directory:
                existing_index = i
                break

        if existing_index >= 0:
            # Update existing entry
            existing_entry = config.directory_history[existing_index]
            updated_entry = DirectoryEntry(
                path=directory,
                last_used=datetime.now().isoformat(),
                usage_count=existing_entry.usage_count + 1
            )
            # Remove from current position
            new_history = [e for e in config.directory_history if e.path != directory]
            # Insert at top
            new_history.insert(0, updated_entry)
        else:
            # Add new entry at top
            new_entry = DirectoryEntry(path=directory)
            new_history = [new_entry] + list(config.directory_history)

        # Trim to max entries
        new_history = new_history[:DEFAULT_MAX_HISTORY_ENTRIES]

        # Update config
        _config_cache = Config(**{**config.model_dump(), "directory_history": new_history})
        result = save_config(_config_cache)
        if result:
            logger.debug(f"Added directory to history: {directory}")
        return result


def get_directory_history(limit: Optional[int] = None) -> List[str]:
    """
    Get directory history as a list of paths, sorted by most recently used.

    Args:
        limit: Maximum number of entries to return (None for all)

    Returns:
        List[str]: List of directory paths, most recent first
    """
    config = get_config()
    history = [entry.path for entry in config.directory_history]
    if limit is not None:
        return history[:limit]
    return history


def remove_from_history(directory: str) -> bool:
    """
    Remove a directory from history.

    Args:
        directory: Directory path to remove

    Returns:
        bool: True if found and removed, False otherwise
    """
    global _config_cache
    with _config_lock:
        config = get_config()

        # Filter out the directory
        new_history = [e for e in config.directory_history if e.path != directory]

        if len(new_history) == len(config.directory_history):
            # Directory not found
            return False

        # Update config
        _config_cache = Config(**{**config.model_dump(), "directory_history": new_history})
        result = save_config(_config_cache)
        if result:
            logger.debug(f"Removed directory from history: {directory}")
        return result


def clear_history() -> bool:
    """
    Clear all directory history.

    Returns:
        bool: True if successful, False otherwise
    """
    global _config_cache
    with _config_lock:
        config = get_config()

        # Update config with empty history
        _config_cache = Config(**{**config.model_dump(), "directory_history": []})
        result = save_config(_config_cache)
        if result:
            logger.info("Directory history cleared")
        return result
