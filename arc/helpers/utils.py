"""
Utility Functions for Arc Music Bot
Helper functions for formatting and URL handling

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

import re
import time
from typing import Optional, Tuple
from urllib.parse import urlparse


def format_size(size: int) -> str:
    """Format file size to human readable format."""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"


def format_eta(seconds: int) -> str:
    """Format ETA to human readable format."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def format_duration(seconds: int) -> str:
    """Format duration in seconds to MM:SS or HH:MM:SS."""
    if seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:02d}"


def to_seconds(duration: str) -> int:
    """Convert duration string to seconds."""
    if not duration:
        return 0

    try:
        parts = duration.split(":")
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        else:
            return int(duration)
    except (ValueError, IndexError):
        return 0


def is_url(text: str) -> bool:
    """Check if text contains a URL."""
    url_pattern = re.compile(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        re.IGNORECASE
    )
    return bool(url_pattern.search(text))


def extract_url(text: str) -> Optional[str]:
    """Extract first URL from text."""
    url_pattern = re.compile(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        re.IGNORECASE
    )
    match = url_pattern.search(text)
    return match.group(0) if match else None


def is_youtube_url(url: str) -> bool:
    """Check if URL is a YouTube URL."""
    youtube_pattern = re.compile(
        r"(https?://)?(www\.|m\.|music\.)?"
        r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
        r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)",
        re.IGNORECASE
    )
    return bool(youtube_pattern.match(url))


def extract_youtube_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from URL."""
    patterns = [
        r"v=([A-Za-z0-9_-]{11})",
        r"youtu\.be/([A-Za-z0-9_-]{11})",
        r"shorts/([A-Za-z0-9_-]{11})",
        r"embed/([A-Za-z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def get_progress_bar(current: int, total: int, length: int = 10) -> str:
    """Generate a progress bar string."""
    if total == 0:
        return "▱" * length

    filled = int(length * current / total)
    empty = length - filled

    return "▰" * filled + "▱" * empty


def get_readable_time(seconds: int) -> str:
    """Convert seconds to readable time format."""
    if seconds < 60:
        return f"{seconds} sec"
    elif seconds < 3600:
        minutes = seconds // 60
        seconds %= 60
        return f"{minutes} min {seconds} sec"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours} hr {minutes} min"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days} day {hours} hr"


def mention_user(user_id: int, name: str) -> str:
    """Create a user mention."""
    return f'<a href="tg://user?id={user_id}">{name}</a>'


def get_time_ago(timestamp: float) -> str:
    """Get human-readable time ago from timestamp."""
    diff = time.time() - timestamp

    if diff < 60:
        return "just now"
    elif diff < 3600:
        return f"{int(diff / 60)} min ago"
    elif diff < 86400:
        return f"{int(diff / 3600)} hr ago"
    elif diff < 604800:
        return f"{int(diff / 86400)} days ago"
    else:
        return f"{int(diff / 604800)} weeks ago"


def seconds_to_time(seconds: int) -> str:
    """Convert seconds to HH:MM:SS or MM:SS format."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def time_to_seconds(time_str: str) -> int:
    """Convert time string (HH:MM:SS or MM:SS) to seconds."""
    try:
        parts = time_str.split(":")

        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        else:
            return int(time_str)
    except (ValueError, IndexError):
        return 0


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to max length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

