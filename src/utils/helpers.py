"""
Helper Functions
Utility functions used throughout the application.
"""

import re
from pathlib import Path
from datetime import datetime, time
from typing import Optional


def format_file_size(size_bytes: int) -> str:
    """
    Convert bytes to human-readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted string (e.g., "10.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def format_duration(seconds: int) -> str:
    """
    Convert seconds to HH:MM:SS format.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted string (e.g., "01:23:45")
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """
    Remove invalid characters from filename.
    
    Args:
        filename: Original filename
        max_length: Maximum filename length
    
    Returns:
        Sanitized filename
    """
    # Remove invalid characters for Windows filenames
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized or "untitled"


def is_within_active_hours(
    start_time_str: str,
    end_time_str: str,
    current_time: Optional[datetime] = None
) -> bool:
    """
    Check if current time is within active hours.
    
    Args:
        start_time_str: Start time in HH:MM format
        end_time_str: End time in HH:MM format
        current_time: Time to check (default: now)
    
    Returns:
        True if within active hours, False otherwise
    """
    if current_time is None:
        current_time = datetime.now()
    
    try:
        start_hour, start_min = map(int, start_time_str.split(':'))
        end_hour, end_min = map(int, end_time_str.split(':'))
        
        start = time(start_hour, start_min)
        end = time(end_hour, end_min)
        current = current_time.time()
        
        if start <= end:
            # Normal case: 10:00 - 22:00
            return start <= current <= end
        else:
            # Crosses midnight: 22:00 - 06:00
            return current >= start or current <= end
    except (ValueError, AttributeError):
        return True  # Default to always active if invalid format


def extract_video_id_from_url(url: str) -> Optional[str]:
    """
    Extract video ID from YouTube URL.
    
    Args:
        url: YouTube video URL
    
    Returns:
        Video ID or None if not found
    """
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # If no pattern matches, check if it's already a video ID
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url
    
    return None


def extract_channel_id_from_url(url: str) -> Optional[str]:
    """
    Extract channel ID from YouTube URL.
    
    Args:
        url: YouTube channel URL
    
    Returns:
        Channel ID or None if not found
    """
    patterns = [
        r'youtube\.com/channel/([a-zA-Z0-9_-]+)',
        r'youtube\.com/c/([a-zA-Z0-9_-]+)',
        r'youtube\.com/@([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # If no pattern matches, check if it's already a channel ID
    if re.match(r'^UC[a-zA-Z0-9_-]{22}$', url):
        return url
    
    return None


def calculate_eta(
    downloaded: int,
    total: int,
    elapsed_seconds: float
) -> str:
    """
    Calculate estimated time of arrival for download/upload.
    
    Args:
        downloaded: Bytes downloaded/uploaded so far
        total: Total bytes
        elapsed_seconds: Time elapsed so far
    
    Returns:
        Formatted ETA string (e.g., "5m 30s")
    """
    if downloaded == 0 or elapsed_seconds == 0:
        return "calculating..."
    
    remaining = total - downloaded
    speed = downloaded / elapsed_seconds
    
    if speed == 0:
        return "unknown"
    
    eta_seconds = int(remaining / speed)
    
    if eta_seconds < 60:
        return f"{eta_seconds}s"
    elif eta_seconds < 3600:
        minutes = eta_seconds // 60
        seconds = eta_seconds % 60
        return f"{minutes}m {seconds}s"
    else:
        hours = eta_seconds // 3600
        minutes = (eta_seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def ensure_directory(path: str) -> Path:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        path: Directory path
    
    Returns:
        Path object
    """
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
    
    Returns:
        File size in bytes, 0 if file doesn't exist
    """
    try:
        return Path(file_path).stat().st_size
    except (FileNotFoundError, OSError):
        return 0


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.
    
    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
