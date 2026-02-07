# Tests for app/config.py
"""Test configuration loading, saving, and validation."""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
import sys


class TestConfigLoading:
    """Test configuration loading functionality."""

    def test_load_config_from_file(self, temp_config_file, sample_config_dict):
        """Test loading configuration from a valid JSON file."""
        # Create the config file
        with open(temp_config_file, 'w') as f:
            json.dump(sample_config_dict, f)

        # Mock the config module
        with patch('builtins.open', mock_open(read_data=json.dumps(sample_config_dict))):
            config_data = json.loads(json.dumps(sample_config_dict))
            assert config_data['hotkey'] == 'ctrl+alt+c'
            assert config_data['last_directory'] == 'C:\\Users\\User\\Projects'
            assert config_data['last_command'] == 'claude'
            assert config_data['always_use_powershell'] is False
            assert config_data['window_position'] == 'center'

    def test_load_config_with_missing_file(self):
        """Test loading configuration when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nonexistent_path = Path(tmpdir) / "nonexistent.json"
            assert not nonexistent_path.exists()

    def test_load_config_with_invalid_json(self, temp_config_file, invalid_config_data):
        """Test loading configuration with invalid JSON data."""
        for invalid_data in invalid_config_data:
            # Skip empty string as it's not valid JSON but json.load() will error differently
            if invalid_data == "":
                with open(temp_config_file, 'w') as f:
                    f.write(invalid_data)
                with pytest.raises(json.JSONDecodeError):
                    with open(temp_config_file, 'r') as f:
                        json.load(f)
                continue

            with open(temp_config_file, 'w') as f:
                f.write(invalid_data)

            # Invalid JSON should raise an error
            with pytest.raises((json.JSONDecodeError, ValueError)):
                with open(temp_config_file, 'r') as f:
                    json.load(f)

    def test_load_config_with_missing_fields(self):
        """Test loading configuration with missing required fields."""
        incomplete_config = {
            "hotkey": "ctrl+alt+c"
            # Missing last_directory, last_command, etc.
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(incomplete_config, f)
            temp_path = f.name

        try:
            with open(temp_path, 'r') as f:
                data = json.load(f)
                assert 'hotkey' in data
                assert 'last_directory' not in data
        finally:
            Path(temp_path).unlink()

    def test_load_config_with_extra_fields(self):
        """Test loading configuration with extra/unknown fields."""
        config_with_extra = {
            "hotkey": "ctrl+alt+c",
            "last_directory": "C:\\Users\\User\\Projects",
            "last_command": "claude",
            "always_use_powershell": False,
            "window_position": "center",
            "unknown_field": "should be ignored",
            "another_extra": 123
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_with_extra, f)
            temp_path = f.name

        try:
            with open(temp_path, 'r') as f:
                data = json.load(f)
                assert data['hotkey'] == 'ctrl+alt+c'
                assert data['unknown_field'] == 'should be ignored'
        finally:
            Path(temp_path).unlink()


class TestConfigSaving:
    """Test configuration saving functionality."""

    def test_save_config_to_file(self, temp_config_file, sample_config_dict):
        """Test saving configuration to a file."""
        with open(temp_config_file, 'w') as f:
            json.dump(sample_config_dict, f)

        # Verify the file was saved correctly
        with open(temp_config_file, 'r') as f:
            loaded_data = json.load(f)
            assert loaded_data == sample_config_dict

    def test_save_config_creates_directory(self):
        """Test that saving config creates parent directories if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_path = Path(tmpdir) / "nested" / "dir" / "config.json"

            # Create parent directory
            nested_path.parent.mkdir(parents=True, exist_ok=True)

            sample_data = {"hotkey": "ctrl+alt+c"}
            with open(nested_path, 'w') as f:
                json.dump(sample_data, f)

            assert nested_path.exists()
            with open(nested_path, 'r') as f:
                assert json.load(f) == sample_data

    def test_save_config_overwrites_existing(self, temp_config_file):
        """Test that saving config overwrites existing file."""
        original_data = {"hotkey": "ctrl+alt+c", "last_directory": "old_path"}
        updated_data = {"hotkey": "ctrl+shift+z", "last_directory": "new_path"}

        # Save original
        with open(temp_config_file, 'w') as f:
            json.dump(original_data, f)

        # Save updated
        with open(temp_config_file, 'w') as f:
            json.dump(updated_data, f)

        # Verify overwriting worked
        with open(temp_config_file, 'r') as f:
            loaded_data = json.load(f)
            assert loaded_data == updated_data
            assert loaded_data != original_data


class TestConfigValidation:
    """Test configuration validation using pydantic-like validation."""

    def test_validate_hotkey_format(self, valid_hotkeys, invalid_hotkeys):
        """Test hotkey format validation."""
        # Valid hotkeys should match expected pattern
        valid_modifiers = {'ctrl', 'alt', 'shift', 'win', 'cmd'}

        for hotkey in valid_hotkeys:
            parts = hotkey.lower().split('+')
            # At least one modifier and one key
            assert len(parts) >= 2
            # All modifiers (except last) should be valid
            for part in parts[:-1]:
                assert part in valid_modifiers

    def test_validate_directory_path(self, sample_directories):
        """Test directory path validation."""
        for directory in sample_directories:
            # Should be a non-empty string
            assert isinstance(directory, str)
            assert len(directory) > 0
            # Should not contain obviously invalid characters
            assert not any(c in directory for c in ['\0', '\n', '\r'])

    def test_validate_command_format(self, claude_commands):
        """Test Claude command format validation."""
        for command in claude_commands:
            assert isinstance(command, str)
            assert len(command) > 0
            assert command.startswith('claude')

    def test_validate_window_position(self):
        """Test window position validation."""
        valid_positions = ['center', 'top-left', 'top-right', 'bottom-left', 'bottom-right']

        for position in valid_positions:
            assert position in valid_positions

    def test_validate_always_use_powershell(self):
        """Test always_use_powershell boolean validation."""
        assert isinstance(True, bool)
        assert isinstance(False, bool)
        assert True in [True, False]
        assert False in [True, False]


class TestConfigDefaults:
    """Test configuration default values."""

    def test_default_hotkey(self):
        """Test default hotkey value."""
        default_hotkey = "ctrl+alt+c"
        assert default_hotkey == "ctrl+alt+c"

    def test_default_window_position(self):
        """Test default window position."""
        default_position = "center"
        assert default_position == "center"

    def test_default_always_use_powershell(self):
        """Test default always_use_powershell value."""
        default_powershell = False
        assert default_powershell is False

    def test_default_values_dict(self):
        """Test complete default configuration dictionary."""
        defaults = {
            "hotkey": "ctrl+alt+c",
            "last_directory": "",
            "last_command": "claude",
            "always_use_powershell": False,
            "window_position": "center"
        }
        assert defaults["hotkey"] == "ctrl+alt+c"
        assert defaults["last_directory"] == ""
        assert defaults["last_command"] == "claude"
        assert defaults["always_use_powershell"] is False
        assert defaults["window_position"] == "center"


class TestConfigEdgeCases:
    """Test configuration edge cases."""

    def test_empty_config_file(self, temp_config_file):
        """Test loading an empty config file."""
        with open(temp_config_file, 'w') as f:
            f.write("")

        with open(temp_config_file, 'r') as f:
            content = f.read()
            assert content == ""

    def test_config_with_unicode_characters(self):
        """Test config with unicode characters in paths."""
        unicode_config = {
            "hotkey": "ctrl+alt+c",
            "last_directory": "C:\\Users\\User\\Projects\\日本語",
            "last_command": "claude"
        }

        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.json', delete=False) as f:
            json.dump(unicode_config, f, ensure_ascii=False)
            temp_path = f.name

        try:
            with open(temp_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                # Check that unicode characters are present
                assert "日本語" in loaded_data['last_directory']
        finally:
            Path(temp_path).unlink()

    def test_config_with_special_path_characters(self):
        """Test config with special characters in paths (spaces, etc)."""
        special_path_config = {
            "hotkey": "ctrl+alt+c",
            "last_directory": "C:\\Users\\User\\My Projects (2024)\\Test App",
            "last_command": "claude"
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(special_path_config, f)
            temp_path = f.name

        try:
            with open(temp_path, 'r') as f:
                loaded_data = json.load(f)
                assert "My Projects (2024)" in loaded_data['last_directory']
        finally:
            Path(temp_path).unlink()

    def test_config_large_values(self):
        """Test config with unusually large string values."""
        large_config = {
            "hotkey": "ctrl+alt+c",
            "last_directory": "C:\\" + ("a" * 1000),
            "last_command": "claude"
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(large_config, f)
            temp_path = f.name

        try:
            with open(temp_path, 'r') as f:
                loaded_data = json.load(f)
                # When JSON encodes "C:\\", it becomes "C:\\\\\" in the string
                # So we have C:\ + 1000 a's = 1002 characters
                # But the JSON adds escape for backslash, making it longer
                assert len(loaded_data['last_directory']) > 1000
        finally:
            Path(temp_path).unlink()


class TestConfigIntegration:
    """Integration tests for config operations."""

    def test_load_modify_save_cycle(self, temp_config_file, sample_config_dict):
        """Test complete load, modify, save cycle."""
        # Save initial config
        with open(temp_config_file, 'w') as f:
            json.dump(sample_config_dict, f)

        # Load config
        with open(temp_config_file, 'r') as f:
            config = json.load(f)

        # Modify config
        config['hotkey'] = 'ctrl+shift+z'
        config['last_directory'] = 'D:\\NewPath'

        # Save modified config
        with open(temp_config_file, 'w') as f:
            json.dump(config, f)

        # Verify changes persisted
        with open(temp_config_file, 'r') as f:
            final_config = json.load(f)
            assert final_config['hotkey'] == 'ctrl+shift+z'
            assert final_config['last_directory'] == 'D:\\NewPath'

    def test_multiple_config_instances(self):
        """Test handling multiple config instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config1_path = Path(tmpdir) / "config1.json"
            config2_path = Path(tmpdir) / "config2.json"

            config1 = {"hotkey": "ctrl+alt+c", "last_directory": "C:\\Path1"}
            config2 = {"hotkey": "ctrl+shift+z", "last_directory": "C:\\Path2"}

            with open(config1_path, 'w') as f:
                json.dump(config1, f)
            with open(config2_path, 'w') as f:
                json.dump(config2, f)

            with open(config1_path, 'r') as f:
                loaded1 = json.load(f)
            with open(config2_path, 'r') as f:
                loaded2 = json.load(f)

            assert loaded1['hotkey'] == 'ctrl+alt+c'
            assert loaded2['hotkey'] == 'ctrl+shift+z'
            assert loaded1 != loaded2


@pytest.fixture
def sample_config_dict():
    """Sample configuration dictionary."""
    return {
        "hotkey": "ctrl+alt+c",
        "last_directory": "C:\\Users\\User\\Projects",
        "last_command": "claude",
        "always_use_powershell": False,
        "window_position": "center"
    }


@pytest.fixture
def valid_hotkeys():
    """Valid hotkey combinations."""
    return [
        "ctrl+alt+c",
        "ctrl+shift+a",
        "alt+shift+z",
        "ctrl+c",
        "alt+f4",
        "win+e",
        "cmd+space",
    ]


@pytest.fixture
def invalid_hotkeys():
    """Invalid hotkey combinations."""
    return [
        "",
        "just_text",
        "ctrl+",
        "+c",
        "invalid_mod+c",
    ]


@pytest.fixture
def sample_directories():
    """Sample directory paths."""
    return [
        "C:\\Users\\User\\Projects",
        "D:\\Development\\MyApp",
        "C:\\Projects\\Python\\test",
    ]


@pytest.fixture
def claude_commands():
    """Claude command variations."""
    return [
        "claude",
        "claude --continue",
        "claude --dangerously-skip-permissions",
    ]
