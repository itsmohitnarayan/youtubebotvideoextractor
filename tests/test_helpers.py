"""
Test suite for helper functions.
"""

import pytest
from pathlib import Path
import sys
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.helpers import (
    format_file_size,
    format_duration,
    sanitize_filename,
    is_within_active_hours,
    extract_video_id_from_url,
    extract_channel_id_from_url,
    calculate_eta,
    ensure_directory,
    get_file_size,
    truncate_string
)
from datetime import datetime


class TestHelpers:
    """Tests for helper functions."""
    
    def test_format_file_size(self):
        """Test file size formatting."""
        assert format_file_size(0) == "0.0 B"
        assert format_file_size(500) == "500.0 B"
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"
        assert format_file_size(1536) == "1.5 KB"
        assert format_file_size(50 * 1024 * 1024) == "50.0 MB"
    
    def test_format_duration(self):
        """Test duration formatting."""
        assert format_duration(0) == "00:00"
        assert format_duration(30) == "00:30"
        assert format_duration(60) == "01:00"
        assert format_duration(90) == "01:30"
        assert format_duration(3600) == "01:00:00"
        assert format_duration(3665) == "01:01:05"
        assert format_duration(7200) == "02:00:00"
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert sanitize_filename("normal_file.txt") == "normal_file.txt"
        assert sanitize_filename("file with spaces.txt") == "file with spaces.txt"
        
        # Invalid characters
        assert "/" not in sanitize_filename("file/with/slashes.txt")
        assert "\\" not in sanitize_filename("file\\with\\backslashes.txt")
        assert ":" not in sanitize_filename("file:with:colons.txt")
        assert "*" not in sanitize_filename("file*with*stars.txt")
        assert "?" not in sanitize_filename("file?with?question.txt")
        
        # Leading/trailing spaces and dots
        assert sanitize_filename("  file.txt  ") == "file.txt"
        assert sanitize_filename("..file.txt..") == "file.txt"
        
        # Empty or invalid becomes "untitled"
        assert sanitize_filename("") == "untitled"
        assert sanitize_filename("...") == "untitled"
    
    def test_sanitize_filename_max_length(self):
        """Test filename truncation."""
        long_name = "a" * 250
        result = sanitize_filename(long_name, max_length=200)
        assert len(result) == 200
    
    def test_is_within_active_hours(self):
        """Test active hours checking."""
        # Test normal range (10:00 - 22:00)
        test_time_morning = datetime(2025, 11, 10, 9, 30)
        assert is_within_active_hours("10:00", "22:00", test_time_morning) is False
        
        test_time_active = datetime(2025, 11, 10, 15, 30)
        assert is_within_active_hours("10:00", "22:00", test_time_active) is True
        
        test_time_night = datetime(2025, 11, 10, 23, 30)
        assert is_within_active_hours("10:00", "22:00", test_time_night) is False
        
        # Test boundary
        test_time_start = datetime(2025, 11, 10, 10, 0)
        assert is_within_active_hours("10:00", "22:00", test_time_start) is True
        
        test_time_end = datetime(2025, 11, 10, 22, 0)
        assert is_within_active_hours("10:00", "22:00", test_time_end) is True
    
    def test_extract_video_id_from_url(self):
        """Test extracting video ID from URLs."""
        urls_and_ids = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/v/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),  # Already an ID
        ]
        
        for url, expected_id in urls_and_ids:
            result = extract_video_id_from_url(url)
            assert result == expected_id, f"Failed for: {url}"
        
        # Invalid URL
        assert extract_video_id_from_url("https://google.com") is None
        assert extract_video_id_from_url("invalid") is None
    
    def test_extract_channel_id_from_url(self):
        """Test extracting channel ID from URLs."""
        urls_and_ids = [
            ("https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw", "UCuAXFkgsw1L7xaCfnd5JJOw"),
            ("https://youtube.com/c/ChannelName", "ChannelName"),
            ("https://www.youtube.com/@username", "username"),
            ("UCuAXFkgsw1L7xaCfnd5JJOw", "UCuAXFkgsw1L7xaCfnd5JJOw"),  # Already an ID
        ]
        
        for url, expected_id in urls_and_ids:
            result = extract_channel_id_from_url(url)
            assert result == expected_id, f"Failed for: {url}"
        
        # Invalid URL
        assert extract_channel_id_from_url("https://google.com") is None
    
    def test_calculate_eta(self):
        """Test ETA calculation."""
        # 50% downloaded in 10 seconds = 10 more seconds
        eta = calculate_eta(50, 100, 10)
        assert "10s" in eta or "0m" in eta
        
        # Nothing downloaded yet
        eta = calculate_eta(0, 100, 0)
        assert "calculating" in eta
        
        # Very slow (would take hours)
        eta = calculate_eta(1, 10000, 100)
        assert "h" in eta  # Should show hours
    
    def test_ensure_directory(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "test" / "nested" / "directory"
            result = ensure_directory(str(new_dir))
            
            assert result.exists()
            assert result.is_dir()
            assert result == new_dir
    
    def test_get_file_size(self):
        """Test getting file size."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"Hello, World!")
            tmp_path = tmp.name
        
        try:
            size = get_file_size(tmp_path)
            assert size == 13  # "Hello, World!" is 13 bytes
        finally:
            Path(tmp_path).unlink()
        
        # Non-existent file
        size = get_file_size("/nonexistent/file.txt")
        assert size == 0
    
    def test_truncate_string(self):
        """Test string truncation."""
        short = "Short string"
        assert truncate_string(short, 50) == short
        
        long = "This is a very long string that needs to be truncated"
        truncated = truncate_string(long, 20)
        assert len(truncated) <= 20
        assert truncated.endswith("...")
        
        # Custom suffix
        truncated = truncate_string(long, 20, suffix="[...]")
        assert truncated.endswith("[...]")
