"""
Arc Music Bot Helpers Module
Uses lazy imports to avoid circular dependencies

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

# Import ONLY from utils at module level - NO imports from buttons or admins
# This prevents circular imports when core modules import from helpers
from arc.helpers.utils import (
    format_size,
    format_eta,
    format_duration,
    seconds_to_time,
    time_to_seconds,
    to_seconds,
    truncate_text,
    is_url,
    extract_url,
    get_url,
    with_timeout,
    run_with_timeout,
    run_in_thread,
    gather_with_timeout,
    retry_async,
    CircuitBreaker,
    RateLimiter,
)

__all__ = [
    # Buttons - use lazy import via __getattr__
    "start_keyboard",
    "help_main_keyboard",
    "help_back_keyboard",
    "controls_keyboard",
    "paused_keyboard",
    "queue_keyboard",
    "close_keyboard",
    "language_keyboard",
    # Admins - use lazy import via __getattr__
    "is_admin",
    "get_admins",
    "reload_admins",
    "bot_can_manage_voice_chats",
    "bot_can_invite_users",
    "bot_can_delete_messages",
    "get_bot_permissions",
    "check_bot_permissions",
    # Utils
    "format_size",
    "format_eta",
    "format_duration",
    "seconds_to_time",
    "time_to_seconds",
    "to_seconds",
    "truncate_text",
    "is_url",
    "extract_url",
    "get_url",
    "with_timeout",
    "run_with_timeout",
    "run_in_thread",
    "gather_with_timeout",
    "retry_async",
    "CircuitBreaker",
    "RateLimiter",
]


def __getattr__(name):
    """
    Lazy import for buttons and admin functions to avoid circular imports.
    Only imports when the attribute is actually accessed.
    """
    # Button functions
    if name in ("start_keyboard", "help_main_keyboard", "help_back_keyboard",
                "controls_keyboard", "paused_keyboard", "queue_keyboard",
                "close_keyboard", "language_keyboard", "confirm_keyboard"):
        from arc.helpers import buttons
        return getattr(buttons, name)
    
    # Admin functions
    if name in ("is_admin", "get_admins", "reload_admins", 
                "bot_can_manage_voice_chats", "bot_can_invite_users",
                "bot_can_delete_messages", "get_bot_permissions",
                "check_bot_permissions"):
        from arc.helpers import admins
        return getattr(admins, name)
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
