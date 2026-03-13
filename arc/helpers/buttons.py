"""
Inline Buttons for Arc Music Bot

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from arc.core import config


def start_keyboard(bot_username: str = None) -> InlineKeyboardMarkup:
    """Start message keyboard with bot username."""
    username = bot_username or "ArcMusicBot"
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Help", callback_data="help_main"),
            InlineKeyboardButton("Add to Group", url=f"https://t.me/{username}?startgroup=true&admin=post_messages+edit_messages+delete_messages+invite_users+manage_video_chats"),
        ],
        [
            InlineKeyboardButton("Support", url=f"https://t.me/{config.SUPPORT_CHAT.replace('@', '')}"),
            InlineKeyboardButton("Updates", url=f"https://t.me/{config.UPDATES_CHANNEL.replace('@', '')}"),
        ],
        [
            InlineKeyboardButton("Source Code", url=config.SOURCE_CODE),
        ],
    ])


def help_main_keyboard() -> InlineKeyboardMarkup:
    """Main help menu with category buttons."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Play", callback_data="help_play"),
            InlineKeyboardButton("Queue", callback_data="help_queue"),
        ],
        [
            InlineKeyboardButton("Controls", callback_data="help_controls"),
            InlineKeyboardButton("Admin", callback_data="help_admin"),
        ],
        [
            InlineKeyboardButton("Settings", callback_data="help_settings"),
            InlineKeyboardButton("Sudo", callback_data="help_sudo"),
        ],
        [
            InlineKeyboardButton("Tools", callback_data="help_tools"),
            InlineKeyboardButton("Close", callback_data="close"),
        ],
    ])


def help_back_keyboard() -> InlineKeyboardMarkup:
    """Back button for help sub-menus."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Back", callback_data="help_main"),
            InlineKeyboardButton("Close", callback_data="close"),
        ],
    ])


def controls_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    """Playback control keyboard."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Pause", callback_data=f"pause_{chat_id}"),
            InlineKeyboardButton("Skip", callback_data=f"skip_{chat_id}"),
        ],
        [
            InlineKeyboardButton("Stop", callback_data=f"stop_{chat_id}"),
            InlineKeyboardButton("Queue", callback_data=f"queue_{chat_id}_1"),
        ],
    ])


def paused_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    """Paused state keyboard."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Resume", callback_data=f"resume_{chat_id}"),
            InlineKeyboardButton("Skip", callback_data=f"skip_{chat_id}"),
        ],
        [
            InlineKeyboardButton("Stop", callback_data=f"stop_{chat_id}"),
            InlineKeyboardButton("Queue", callback_data=f"queue_{chat_id}_1"),
        ],
    ])


def queue_keyboard(chat_id: int, page: int = 1, total_pages: int = 1) -> InlineKeyboardMarkup:
    """Queue navigation keyboard."""
    buttons = []

    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("<<", callback_data=f"queue_{chat_id}_{page - 1}"))
    nav_row.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="queue_page"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton(">>", callback_data=f"queue_{chat_id}_{page + 1}"))
    buttons.append(nav_row)

    buttons.append([
        InlineKeyboardButton("Shuffle", callback_data=f"shuffle_{chat_id}"),
        InlineKeyboardButton("Close", callback_data=f"close_{chat_id}"),
    ])

    return InlineKeyboardMarkup(buttons)


def close_keyboard() -> InlineKeyboardMarkup:
    """Simple close button."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Close", callback_data="close")]
    ])


def language_keyboard() -> InlineKeyboardMarkup:
    """Language selection keyboard."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("English", callback_data="lang_en"),
            InlineKeyboardButton("हिंदी", callback_data="lang_hi"),
        ],
        [
            InlineKeyboardButton("Español", callback_data="lang_es"),
            InlineKeyboardButton("العربية", callback_data="lang_ar"),
        ],
        [
            InlineKeyboardButton("Indonesia", callback_data="lang_id"),
            InlineKeyboardButton("မြန်မာ", callback_data="lang_my"),
        ],
    ])


def confirm_keyboard(action: str, chat_id: int) -> InlineKeyboardMarkup:
    """Confirmation keyboard for actions."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Yes", callback_data=f"confirm_{action}_{chat_id}"),
            InlineKeyboardButton("No", callback_data=f"cancel_{action}_{chat_id}"),
        ],
    ])
