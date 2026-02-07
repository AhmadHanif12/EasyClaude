# Tests for directory history feature
"""Test directory history model, management functions, and GUI integration."""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from app.config import (
    Config,
    DirectoryEntry,
    add_directory_to_history,
    get_directory_history,
    remove_from_history,
    clear_history,
    invalidate_cache,
    DEFAULT_MAX_HISTORY_ENTRIES,
)
import app.config as config_module


class TestDirectoryEntryModel:
    """Test DirectoryEntry Pydantic model."""

    def test_create_directory_entry_with_path_only(self):
        """Test creating a DirectoryEntry with just a path."""
        entry = DirectoryEntry(path="C:\\Users\\Test")
        assert entry.path == "C:\\Users\\Test"
        assert isinstance(entry.last_used, str)
        assert entry.usage_count == 1

    def test_create_directory_entry_with_all_fields(self):
        """Test creating a DirectoryEntry with all fields."""
        timestamp = "2024-01-15T10:30:00"
        entry = DirectoryEntry(
            path="/home/user/projects",
            last_used=timestamp,
            usage_count=5
        )
        assert entry.path == "/home/user/projects"
        assert entry.last_used == timestamp
        assert entry.usage_count == 5

    def test_directory_entry_usage_count_validation(self):
        """Test that usage_count must be >= 1."""
        with pytest.raises(ValueError):
            DirectoryEntry(path="C:\\Test", usage_count=0)

    def test_directory_entry_serialization(self):
        """Test DirectoryEntry can be serialized to dict."""
        entry = DirectoryEntry(path="D:\\Projects", usage_count=3)
        data = entry.dict()
        assert data["path"] == "D:\\Projects"
        assert "last_used" in data
        assert data["usage_count"] == 3


class TestConfigDirectoryHistoryField:
    """Test Config model with directory_history field."""

    def test_config_with_empty_history(self):
        """Test creating a Config with empty directory history."""
        cfg = Config()
        assert cfg.directory_history == []
        assert cfg.recent_directories == []

    def test_config_with_directory_history_entries(self):
        """Test Config with DirectoryEntry objects."""
        entries = [
            DirectoryEntry(path="C:\\Projects\\A"),
            DirectoryEntry(path="D:\\Projects\\B", usage_count=2),
        ]
        cfg = Config(directory_history=entries)
        assert len(cfg.directory_history) == 2
        assert cfg.directory_history[0].path == "C:\\Projects\\A"
        assert cfg.directory_history[1].usage_count == 2

    def test_config_migration_from_legacy_string_list(self):
        """Test migration from legacy recent_directories string list."""
        legacy_data = {
            "hotkey": "ctrl+alt+c",
            "directory_history": [
                "C:\\Projects\\A",
                "D:\\Projects\\B",
                "E:\\Projects\\C"
            ]
        }
        cfg = Config(**legacy_data)
        # Should create DirectoryEntry objects
        assert len(cfg.directory_history) == 3
        assert all(isinstance(e, DirectoryEntry) for e in cfg.directory_history)
        assert cfg.directory_history[0].path == "C:\\Projects\\A"
        assert cfg.directory_history[0].usage_count == 1

    def test_config_history_validation_deduplicates(self):
        """Test that duplicate paths are removed during validation."""
        data = {
            "directory_history": [
                {"path": "C:\\Test", "last_used": "2024-01-01T10:00:00"},
                {"path": "D:\\Other", "last_used": "2024-01-02T10:00:00"},
                {"path": "C:\\Test", "last_used": "2024-01-03T10:00:00"},
            ]
        }
        cfg = Config(**data)
        # Should keep only first occurrence (most recent based on input order)
        paths = [e.path for e in cfg.directory_history]
        assert paths.count("C:\\Test") == 1

    def test_config_history_enforces_max_entries(self):
        """Test that history is limited to DEFAULT_MAX_HISTORY_ENTRIES."""
        entries = [
            DirectoryEntry(path=f"C:\\Project{i}") for i in range(20)
        ]
        cfg = Config(directory_history=entries)
        assert len(cfg.directory_history) <= DEFAULT_MAX_HISTORY_ENTRIES


class TestAddDirectoryToHistory:
    """Test add_directory_to_history function."""

    def setup_method(self):
        """Reset config cache before each test."""
        invalidate_cache()

    def test_add_new_directory_to_empty_history(self):
        """Test adding a directory to empty history."""
        with patch('app.config.save_config', return_value=True) as mock_save:
            result = add_directory_to_history("C:\\NewProject")
            assert result is True
            mock_save.assert_called_once()

    def test_add_directory_moves_existing_to_top(self):
        """Test that existing directory is moved to top with updated timestamp."""
        # Create initial history
        entries = [
            DirectoryEntry(path="C:\\Old1"),
            DirectoryEntry(path="C:\\Current", usage_count=2),
            DirectoryEntry(path="C:\\Old2"),
        ]

        with patch('app.config.get_config', return_value=Config(directory_history=entries)):
            with patch('app.config.save_config', return_value=True) as mock_save:
                add_directory_to_history("C:\\Current")

                # Get the call arguments
                call_args = mock_save.call_args[0][0]
                assert call_args.directory_history[0].path == "C:\\Current"
                assert call_args.directory_history[0].usage_count == 3

    def test_add_directory_enforces_max_limit(self):
        """Test that adding beyond max entries removes oldest."""
        # Create full history
        entries = [
            DirectoryEntry(path=f"C:\\Project{i}", usage_count=i+1)
            for i in range(DEFAULT_MAX_HISTORY_ENTRIES)
        ]

        with patch('app.config.get_config', return_value=Config(directory_history=entries)):
            with patch('app.config.save_config', return_value=True) as mock_save:
                add_directory_to_history("C:\\NewProject")

                call_args = mock_save.call_args[0][0]
                # Should be at max limit
                assert len(call_args.directory_history) == DEFAULT_MAX_HISTORY_ENTRIES
                # New entry should be at top
                assert call_args.directory_history[0].path == "C:\\NewProject"


class TestGetDirectoryHistory:
    """Test get_directory_history function."""

    def setup_method(self):
        """Reset config cache before each test."""
        invalidate_cache()

    def test_get_history_from_empty_config(self):
        """Test getting history when empty."""
        with patch('app.config.get_config', return_value=Config()):
            history = get_directory_history()
            assert history == []

    def test_get_history_returns_paths_only(self):
        """Test that history returns list of path strings."""
        entries = [
            DirectoryEntry(path="C:\\A", usage_count=1),
            DirectoryEntry(path="D:\\B", usage_count=5),
        ]
        with patch('app.config.get_config', return_value=Config(directory_history=entries)):
            history = get_directory_history()
            assert history == ["C:\\A", "D:\\B"]
            assert all(isinstance(p, str) for p in history)

    def test_get_history_with_limit(self):
        """Test getting history with a limit."""
        entries = [DirectoryEntry(path=f"C:\\Project{i}") for i in range(10)]
        with patch('app.config.get_config', return_value=Config(directory_history=entries)):
            history = get_directory_history(limit=3)
            assert len(history) == 3
            assert history == ["C:\\Project0", "C:\\Project1", "C:\\Project2"]


class TestRemoveFromHistory:
    """Test remove_from_history function."""

    def setup_method(self):
        """Reset config cache before each test."""
        invalidate_cache()

    def test_remove_existing_directory(self):
        """Test removing an existing directory from history."""
        entries = [
            DirectoryEntry(path="C:\\Keep"),
            DirectoryEntry(path="C:\\RemoveMe"),
            DirectoryEntry(path="D:\\AlsoKeep"),
        ]
        with patch('app.config.get_config', return_value=Config(directory_history=entries)):
            with patch('app.config.save_config', return_value=True) as mock_save:
                result = remove_from_history("C:\\RemoveMe")
                assert result is True

                call_args = mock_save.call_args[0][0]
                paths = [e.path for e in call_args.directory_history]
                assert "C:\\RemoveMe" not in paths
                assert len(call_args.directory_history) == 2

    def test_remove_nonexistent_directory(self):
        """Test removing a directory that doesn't exist in history."""
        entries = [DirectoryEntry(path="C:\\OnlyOne")]
        with patch('app.config.get_config', return_value=Config(directory_history=entries)):
            with patch('app.config.save_config', return_value=True) as mock_save:
                result = remove_from_history("C:\\NotInHistory")
                assert result is False
                mock_save.assert_not_called()


class TestClearHistory:
    """Test clear_history function."""

    def setup_method(self):
        """Reset config cache before each test."""
        invalidate_cache()

    def test_clear_history_with_entries(self):
        """Test clearing all entries from history."""
        entries = [DirectoryEntry(path=f"C:\\Project{i}") for i in range(5)]
        with patch('app.config.get_config', return_value=Config(directory_history=entries)):
            with patch('app.config.save_config', return_value=True) as mock_save:
                result = clear_history()
                assert result is True

                call_args = mock_save.call_args[0][0]
                assert call_args.directory_history == []

    def test_clear_already_empty_history(self):
        """Test clearing history when already empty."""
        with patch('app.config.get_config', return_value=Config()):
            with patch('app.config.save_config', return_value=True) as mock_save:
                result = clear_history()
                assert result is True


class TestHistoryPersistence:
    """Test that history persists across config loads."""

    def test_history_saved_and_loaded(self):
        """Test that history is properly saved and can be loaded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"

            # Create and save config with history
            entries = [
                DirectoryEntry(path="C:\\Test1", usage_count=1),
                DirectoryEntry(path="D:\\Test2", usage_count=3),
            ]
            cfg = Config(directory_history=entries)

            with patch('app.config.get_config_path', return_value=config_path):
                from app.config import save_config, load_config
                save_config(cfg)

                # Load it back
                loaded_cfg = load_config()
                assert len(loaded_cfg.directory_history) == 2
                assert loaded_cfg.directory_history[0].path == "C:\\Test1"
                assert loaded_cfg.directory_history[1].usage_count == 3


class TestHistoryThreadSafety:
    """Test thread safety of history operations."""

    def test_concurrent_add_operations(self):
        """Test that concurrent adds don't corrupt history."""
        import threading

        with patch('app.config.save_config', return_value=True):
            results = []

            def add_dir(path):
                try:
                    results.append(add_directory_to_history(path))
                except Exception as e:
                    results.append(e)

            threads = [
                threading.Thread(target=add_dir, args=(f"C:\\Project{i}",))
                for i in range(10)
            ]

            for t in threads:
                t.start()
            for t in threads:
                t.join()

            # All operations should complete without exception
            assert len(results) == 10
            assert all(r is True or isinstance(r, bool) for r in results)


# Test fixtures
@pytest.fixture
def sample_directories():
    """Sample directory paths for testing."""
    return [
        "C:\\Users\\User\\Projects",
        "D:\\Development\\MyApp",
        "C:\\Projects\\Python\\test",
        "/home/user/projects",
        "~/Documents",
    ]


@pytest.fixture
def sample_history_entries():
    """Sample DirectoryEntry objects for testing."""
    return [
        DirectoryEntry(
            path="C:\\ProjectA",
            last_used="2024-01-01T10:00:00",
            usage_count=1
        ),
        DirectoryEntry(
            path="D:\\ProjectB",
            last_used="2024-01-02T11:30:00",
            usage_count=3
        ),
        DirectoryEntry(
            path="E:\\ProjectC",
            last_used="2024-01-03T14:15:00",
            usage_count=1
        ),
    ]
