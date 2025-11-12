"""
Test suite for configuration manager.
"""

import pytest
from pathlib import Path
import json
import tempfile
import shutil
import os
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config import ConfigManager


class TestConfigManager:
    """Tests for ConfigManager class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration data."""
        return {
            "version": "1.0.0",
            "target_channel": {
                "channel_id": "UC_TEST_CHANNEL_ID",
                "channel_url": "https://www.youtube.com/channel/UC_TEST_CHANNEL_ID"
            },
            "active_hours": {
                "start": "10:00",
                "end": "22:00"
            },
            "download": {
                "directory": "downloads",
                "format": "best"
            },
            "monitoring": {
                "check_interval_minutes": 10
            }
        }
    
    @pytest.fixture
    def config_manager(self, temp_dir, sample_config):
        """Create ConfigManager instance with temp config file."""
        config_path = Path(temp_dir) / "test_config.json"
        with open(config_path, 'w') as f:
            json.dump(sample_config, f)
        
        return ConfigManager(config_path=str(config_path))
    
    def test_load_config(self, config_manager, sample_config):
        """Test configuration loading."""
        assert config_manager.config is not None
        assert config_manager.config["version"] == sample_config["version"]
        assert "target_channel" in config_manager.config
    
    def test_get_value_simple(self, config_manager):
        """Test getting simple configuration value."""
        version = config_manager.get("version")
        assert version == "1.0.0"
    
    def test_get_value_nested(self, config_manager):
        """Test getting nested configuration value using dot notation."""
        channel_id = config_manager.get("target_channel.channel_id")
        assert channel_id == "UC_TEST_CHANNEL_ID"
        
        start_time = config_manager.get("active_hours.start")
        assert start_time == "10:00"
    
    def test_get_value_with_default(self, config_manager):
        """Test getting non-existent value with default."""
        value = config_manager.get("non.existent.key", "default_value")
        assert value == "default_value"
    
    def test_get_value_missing_no_default(self, config_manager):
        """Test getting non-existent value without default returns None."""
        value = config_manager.get("missing.key")
        assert value is None
    
    def test_set_value_simple(self, config_manager):
        """Test setting simple configuration value."""
        config_manager.set("new_key", "new_value")
        assert config_manager.get("new_key") == "new_value"
    
    def test_set_value_nested(self, config_manager):
        """Test setting nested configuration value."""
        config_manager.set("new_section.nested_key", "nested_value")
        assert config_manager.get("new_section.nested_key") == "nested_value"
    
    def test_set_value_update_existing(self, config_manager):
        """Test updating existing configuration value."""
        config_manager.set("version", "2.0.0")
        assert config_manager.get("version") == "2.0.0"
    
    def test_save_config(self, temp_dir, config_manager):
        """Test saving configuration to file."""
        config_manager.set("new_setting", "test_value")
        result = config_manager.save()
        
        assert result is True
        assert config_manager.config_path.exists()
        
        # Reload and verify
        with open(config_manager.config_path, 'r') as f:
            saved_config = json.load(f)
        assert saved_config["new_setting"] == "test_value"
    
    def test_validation_success(self, config_manager):
        """Test configuration validation with valid config."""
        is_valid, errors = config_manager.validate()
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validation_missing_required_field(self, temp_dir):
        """Test configuration validation with missing required field."""
        config_path = Path(temp_dir) / "invalid_config.json"
        invalid_config = {
            "version": "1.0.0"
            # Missing required fields
        }
        with open(config_path, 'w') as f:
            json.dump(invalid_config, f)
        
        cm = ConfigManager(config_path=str(config_path))
        is_valid, errors = cm.validate()
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("target_channel.channel_id" in error for error in errors)
    
    def test_validation_invalid_time_format(self, temp_dir):
        """Test configuration validation with invalid time format."""
        config_path = Path(temp_dir) / "invalid_time_config.json"
        invalid_config = {
            "target_channel": {"channel_id": "UC_TEST"},
            "active_hours": {
                "start": "25:00",  # Invalid hour
                "end": "22:00"
            },
            "download": {"directory": "downloads"}
        }
        with open(config_path, 'w') as f:
            json.dump(invalid_config, f)
        
        cm = ConfigManager(config_path=str(config_path))
        is_valid, errors = cm.validate()
        
        assert is_valid is False
        assert any("time format" in error.lower() for error in errors)
    
    def test_is_valid_time_format(self):
        """Test time format validation method."""
        assert ConfigManager._is_valid_time_format("10:00") is True
        assert ConfigManager._is_valid_time_format("23:59") is True
        assert ConfigManager._is_valid_time_format("00:00") is True
        assert ConfigManager._is_valid_time_format("9:30") is True
        
        assert ConfigManager._is_valid_time_format("24:00") is False
        assert ConfigManager._is_valid_time_format("10:60") is False
        assert ConfigManager._is_valid_time_format("invalid") is False
        assert ConfigManager._is_valid_time_format("10-30") is False
    
    def test_create_from_example(self, temp_dir, monkeypatch):
        """Test creating config from example when config doesn't exist."""
        # Change to temp directory
        monkeypatch.chdir(temp_dir)
        
        # Create example config
        example_path = Path(temp_dir) / "config.example.json"
        example_config = {"version": "1.0.0", "example": True}
        with open(example_path, 'w') as f:
            json.dump(example_config, f)
        
        # Mock the paths
        ConfigManager.DEFAULT_CONFIG_PATH = str(Path(temp_dir) / "config.json")
        ConfigManager.EXAMPLE_CONFIG_PATH = str(example_path)
        
        # Create ConfigManager - should create from example
        cm = ConfigManager()
        
        assert Path(cm.config_path).exists()
        assert cm.get("example") is True
    
    def test_get_env(self, config_manager, monkeypatch):
        """Test getting environment variable."""
        monkeypatch.setenv("TEST_ENV_VAR", "test_value")
        
        value = config_manager.get_env("TEST_ENV_VAR")
        assert value == "test_value"
        
        default_value = config_manager.get_env("NON_EXISTENT_VAR", "default")
        assert default_value == "default"
    
    def test_config_with_empty_file(self, temp_dir):
        """Test handling of empty configuration file."""
        config_path = Path(temp_dir) / "empty_config.json"
        config_path.write_text("")
        
        cm = ConfigManager(config_path=str(config_path))
        assert cm.config == {}
    
    def test_config_with_invalid_json(self, temp_dir):
        """Test handling of invalid JSON in config file."""
        config_path = Path(temp_dir) / "invalid_config.json"
        config_path.write_text("{ invalid json }")
        
        cm = ConfigManager(config_path=str(config_path))
        assert cm.config == {}
    
    def test_nested_dict_creation_on_set(self, config_manager):
        """Test that setting nested keys creates intermediate dicts."""
        config_manager.set("level1.level2.level3", "deep_value")
        
        assert config_manager.get("level1.level2.level3") == "deep_value"
        assert isinstance(config_manager.config["level1"], dict)
        assert isinstance(config_manager.config["level1"]["level2"], dict)
