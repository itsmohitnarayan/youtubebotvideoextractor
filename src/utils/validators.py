"""
Input Validators
Functions to validate user inputs and configuration values.
"""

import re
from pathlib import Path
from typing import Tuple


def validate_youtube_url(url: str) -> Tuple[bool, str]:
    """
    Validate YouTube URL format.
    
    Args:
        url: URL to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL cannot be empty"
    
    youtube_patterns = [
        r'^https?://(www\.)?youtube\.com/',
        r'^https?://youtu\.be/',
    ]
    
    for pattern in youtube_patterns:
        if re.match(pattern, url):
            return True, ""
    
    return False, "Invalid YouTube URL format"


def validate_channel_id(channel_id: str) -> Tuple[bool, str]:
    """
    Validate YouTube channel ID format.
    
    Args:
        channel_id: Channel ID to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not channel_id:
        return False, "Channel ID cannot be empty"
    
    # YouTube channel IDs start with UC and are 24 characters total
    if re.match(r'^UC[a-zA-Z0-9_-]{22}$', channel_id):
        return True, ""
    
    return False, "Invalid channel ID format (should start with UC and be 24 characters)"


def validate_video_id(video_id: str) -> Tuple[bool, str]:
    """
    Validate YouTube video ID format.
    
    Args:
        video_id: Video ID to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not video_id:
        return False, "Video ID cannot be empty"
    
    # YouTube video IDs are 11 characters
    if re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
        return True, ""
    
    return False, "Invalid video ID format (should be 11 characters)"


def validate_time_format(time_str: str) -> Tuple[bool, str]:
    """
    Validate time format (HH:MM).
    
    Args:
        time_str: Time string to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not time_str:
        return False, "Time cannot be empty"
    
    if not re.match(r'^\d{1,2}:\d{2}$', time_str):
        return False, "Invalid time format (use HH:MM)"
    
    try:
        parts = time_str.split(':')
        hour, minute = int(parts[0]), int(parts[1])
        
        if not (0 <= hour <= 23):
            return False, "Hour must be between 0 and 23"
        
        if not (0 <= minute <= 59):
            return False, "Minute must be between 0 and 59"
        
        return True, ""
    except (ValueError, IndexError):
        return False, "Invalid time format"


def validate_file_path(file_path: str, must_exist: bool = False) -> Tuple[bool, str]:
    """
    Validate file path.
    
    Args:
        file_path: File path to validate
        must_exist: Whether file must already exist
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path:
        return False, "File path cannot be empty"
    
    try:
        path = Path(file_path)
        
        if must_exist and not path.exists():
            return False, f"File does not exist: {file_path}"
        
        # Check if parent directory exists (or can be created)
        if not path.parent.exists():
            return False, f"Parent directory does not exist: {path.parent}"
        
        return True, ""
    except (OSError, ValueError) as e:
        return False, f"Invalid file path: {str(e)}"


def validate_directory_path(dir_path: str, create: bool = False) -> Tuple[bool, str]:
    """
    Validate directory path.
    
    Args:
        dir_path: Directory path to validate
        create: Whether to create directory if it doesn't exist
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not dir_path:
        return False, "Directory path cannot be empty"
    
    try:
        path = Path(dir_path)
        
        if create:
            path.mkdir(parents=True, exist_ok=True)
        
        if not path.exists():
            return False, f"Directory does not exist: {dir_path}"
        
        if not path.is_dir():
            return False, f"Path is not a directory: {dir_path}"
        
        return True, ""
    except (OSError, ValueError) as e:
        return False, f"Invalid directory path: {str(e)}"


def validate_integer_range(
    value: int,
    min_value: int = None,
    max_value: int = None
) -> Tuple[bool, str]:
    """
    Validate integer is within range.
    
    Args:
        value: Value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, int):
        return False, "Value must be an integer"
    
    if min_value is not None and value < min_value:
        return False, f"Value must be at least {min_value}"
    
    if max_value is not None and value > max_value:
        return False, f"Value must be at most {max_value}"
    
    return True, ""


def validate_privacy_status(privacy: str) -> Tuple[bool, str]:
    """
    Validate YouTube privacy status.
    
    Args:
        privacy: Privacy status to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_statuses = ['public', 'private', 'unlisted']
    
    if privacy.lower() not in valid_statuses:
        return False, f"Privacy must be one of: {', '.join(valid_statuses)}"
    
    return True, ""


def validate_category_id(category_id: str) -> Tuple[bool, str]:
    """
    Validate YouTube category ID.
    
    Args:
        category_id: Category ID to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # YouTube category IDs are numeric strings
    valid_categories = [
        "1", "2", "10", "15", "17", "19", "20",
        "22", "23", "24", "25", "26", "27", "28"
    ]
    
    if category_id not in valid_categories:
        return False, f"Invalid category ID: {category_id}"
    
    return True, ""
