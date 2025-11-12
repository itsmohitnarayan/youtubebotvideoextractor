"""
Configuration Manager
Handles loading, saving, and validating application configuration.
"""

import json
import os
from pathlib import Path
from typing import Any, Optional
from dotenv import load_dotenv

# Import file security utility for automatic permission hardening
try:
    from src.utils.file_security import secure_sensitive_files
    _SECURITY_AVAILABLE = True
except ImportError:
    _SECURITY_AVAILABLE = False


class ConfigManager:
    """Manages application configuration from JSON file and environment variables."""
    
    DEFAULT_CONFIG_PATH = "config.json"
    EXAMPLE_CONFIG_PATH = "config.example.json"
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file. If None, uses default.
        """
        self.config_path = Path(config_path or self.DEFAULT_CONFIG_PATH)
        self.config: dict[str, Any] = {}
        
        # Load environment variables
        load_dotenv()
        
        # Load configuration
        self._load_config()
        
        # Secure sensitive files and directories (Windows permissions hardening)
        if _SECURITY_AVAILABLE:
            try:
                secure_sensitive_files()
            except Exception as e:
                # Non-critical: just log the warning
                print(f"⚠️  Could not secure file permissions: {e}")
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        if not self.config_path.exists():
            print(f"Config file not found: {self.config_path}")
            print(f"Creating from example: {self.EXAMPLE_CONFIG_PATH}")
            self._create_from_example()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print(f"Configuration loaded from {self.config_path}")
        except json.JSONDecodeError as e:
            print(f"Error parsing config file: {e}")
            self.config = {}
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = {}
    
    def _create_from_example(self) -> None:
        """Create config.json from config.example.json."""
        example_path = Path(self.EXAMPLE_CONFIG_PATH)
        if example_path.exists():
            with open(example_path, 'r', encoding='utf-8') as f:
                example_config = json.load(f)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(example_config, f, indent=2)
            
            print(f"Created {self.config_path} from example")
        else:
            print(f"Example config not found: {example_path}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'monitoring.check_interval_minutes')
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by dot-notation key.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the final key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def save(self) -> bool:
        """
        Save configuration to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            print(f"Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration.
        
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        # Check required fields
        required_fields = [
            'target_channel.channel_id',
            'active_hours.start',
            'active_hours.end',
            'download.directory',
        ]
        
        for field in required_fields:
            if not self.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate active hours format
        start = self.get('active_hours.start', '')
        end = self.get('active_hours.end', '')
        
        if start and not self._is_valid_time_format(start):
            errors.append(f"Invalid time format for active_hours.start: {start}")
        
        if end and not self._is_valid_time_format(end):
            errors.append(f"Invalid time format for active_hours.end: {end}")
        
        return (len(errors) == 0, errors)
    
    @staticmethod
    def _is_valid_time_format(time_str: str) -> bool:
        """
        Validate time format (HH:MM).
        
        Args:
            time_str: Time string to validate
        
        Returns:
            True if valid, False otherwise
        """
        try:
            parts = time_str.split(':')
            if len(parts) != 2:
                return False
            
            hour, minute = int(parts[0]), int(parts[1])
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except (ValueError, AttributeError):
            return False
    
    def get_env(self, key: str, default: Any = None) -> Any:
        """
        Get environment variable.
        
        Args:
            key: Environment variable name
            default: Default value if not found
        
        Returns:
            Environment variable value or default
        """
        return os.getenv(key, default)
