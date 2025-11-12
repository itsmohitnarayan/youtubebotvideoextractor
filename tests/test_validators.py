"""
Test suite for validators.
"""

import pytest
from pathlib import Path
import tempfile
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.validators import (
    validate_youtube_url,
    validate_channel_id,
    validate_video_id,
    validate_time_format,
    validate_file_path,
    validate_directory_path,
    validate_integer_range,
    validate_privacy_status,
    validate_category_id
)


class TestValidators:
    """Tests for validation functions."""
    
    def test_validate_youtube_url_valid(self):
        """Test validating valid YouTube URLs."""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=test12345",  # Changed from http to https for security
            "https://youtu.be/dQw4w9WgXcQ"
        ]
        
        for url in valid_urls:
            is_valid, msg = validate_youtube_url(url)
            assert is_valid is True, f"Failed for: {url}"
            assert msg == ""
    
    def test_validate_youtube_url_invalid(self):
        """Test validating invalid YouTube URLs."""
        invalid_urls = [
            "",
            "not a url",
            "https://google.com",
            "https://vimeo.com/123456"
        ]
        
        for url in invalid_urls:
            is_valid, msg = validate_youtube_url(url)
            assert is_valid is False
            assert msg != ""
    
    def test_validate_channel_id_valid(self):
        """Test validating valid channel IDs."""
        valid_ids = [
            "UCuAXFkgsw1L7xaCfnd5JJOw",  # 24 chars starting with UC
            "UC1234567890123456789012",
        ]
        
        for channel_id in valid_ids:
            is_valid, msg = validate_channel_id(channel_id)
            assert is_valid is True
            assert msg == ""
    
    def test_validate_channel_id_invalid(self):
        """Test validating invalid channel IDs."""
        invalid_ids = [
            "",
            "ABC123",  # Too short
            "UC123",  # Too short
            "XX1234567890123456789012",  # Doesn't start with UC
            "UC12345678901234567890123"  # Too long
        ]
        
        for channel_id in invalid_ids:
            is_valid, msg = validate_channel_id(channel_id)
            assert is_valid is False
            assert msg != ""
    
    def test_validate_video_id_valid(self):
        """Test validating valid video IDs."""
        valid_ids = [
            "dQw4w9WgXcQ",
            "aBcDeFgHiJk",
            "12345678901"
        ]
        
        for video_id in valid_ids:
            is_valid, msg = validate_video_id(video_id)
            assert is_valid is True
            assert msg == ""
    
    def test_validate_video_id_invalid(self):
        """Test validating invalid video IDs."""
        invalid_ids = [
            "",
            "short",
            "toolongvideoid123",
            "invalid@char"
        ]
        
        for video_id in invalid_ids:
            is_valid, msg = validate_video_id(video_id)
            assert is_valid is False
            assert msg != ""
    
    def test_validate_time_format_valid(self):
        """Test validating valid time formats."""
        valid_times = [
            "00:00",
            "10:30",
            "23:59",
            "9:00",
            "12:45"
        ]
        
        for time_str in valid_times:
            is_valid, msg = validate_time_format(time_str)
            assert is_valid is True, f"Failed for: {time_str}"
            assert msg == ""
    
    def test_validate_time_format_invalid(self):
        """Test validating invalid time formats."""
        invalid_times = [
            "",
            "24:00",  # Hour out of range
            "10:60",  # Minute out of range
            "25:30",  # Hour out of range
            "10-30",  # Wrong separator
            "invalid",
            "10:5",  # Wrong format (should be 10:05)
        ]
        
        for time_str in invalid_times:
            is_valid, msg = validate_time_format(time_str)
            assert is_valid is False, f"Should fail for: {time_str}"
            assert msg != ""
    
    def test_validate_file_path_valid(self):
        """Test validating valid file paths."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            is_valid, msg = validate_file_path(tmp_path, must_exist=True)
            assert is_valid is True
            assert msg == ""
        finally:
            Path(tmp_path).unlink()
    
    def test_validate_file_path_nonexistent(self):
        """Test validating non-existent file path with must_exist=True."""
        is_valid, msg = validate_file_path("/nonexistent/file.txt", must_exist=True)
        assert is_valid is False
        assert "does not exist" in msg
    
    def test_validate_directory_path_valid(self):
        """Test validating valid directory path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            is_valid, msg = validate_directory_path(tmpdir)
            assert is_valid is True
            assert msg == ""
    
    def test_validate_directory_path_create(self):
        """Test creating directory during validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "new_directory"
            
            is_valid, msg = validate_directory_path(str(new_dir), create=True)
            assert is_valid is True
            assert new_dir.exists()
            assert new_dir.is_dir()
    
    def test_validate_integer_range_valid(self):
        """Test validating integers within range."""
        is_valid, msg = validate_integer_range(5, min_value=0, max_value=10)
        assert is_valid is True
        assert msg == ""
        
        is_valid, msg = validate_integer_range(0, min_value=0, max_value=10)
        assert is_valid is True
        
        is_valid, msg = validate_integer_range(10, min_value=0, max_value=10)
        assert is_valid is True
    
    def test_validate_integer_range_invalid(self):
        """Test validating integers outside range."""
        is_valid, msg = validate_integer_range(-1, min_value=0, max_value=10)
        assert is_valid is False
        assert "at least" in msg
        
        is_valid, msg = validate_integer_range(11, min_value=0, max_value=10)
        assert is_valid is False
        assert "at most" in msg
    
    def test_validate_integer_range_not_integer(self):
        """Test validating non-integer value."""
        is_valid, msg = validate_integer_range("not an int", min_value=0)
        assert is_valid is False
        assert "integer" in msg
    
    def test_validate_privacy_status_valid(self):
        """Test validating valid privacy statuses."""
        valid_statuses = ["public", "private", "unlisted", "PUBLIC", "PRIVATE"]
        
        for status in valid_statuses:
            is_valid, msg = validate_privacy_status(status)
            assert is_valid is True
            assert msg == ""
    
    def test_validate_privacy_status_invalid(self):
        """Test validating invalid privacy status."""
        is_valid, msg = validate_privacy_status("invalid")
        assert is_valid is False
        assert "Privacy must be one of" in msg
    
    def test_validate_category_id_valid(self):
        """Test validating valid category IDs."""
        valid_categories = ["1", "10", "20", "22", "28"]
        
        for cat_id in valid_categories:
            is_valid, msg = validate_category_id(cat_id)
            assert is_valid is True
            assert msg == ""
    
    def test_validate_category_id_invalid(self):
        """Test validating invalid category ID."""
        invalid_categories = ["0", "99", "invalid", ""]
        
        for cat_id in invalid_categories:
            is_valid, msg = validate_category_id(cat_id)
            assert is_valid is False
            assert "Invalid category ID" in msg
