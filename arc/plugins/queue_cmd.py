"""
Queue Command Plugin for Arc Music Bot
Handles queue, now, clear commands

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

from pyrogram import filters, types

from arc.core import app, queue, lang
from arc.helpers.buttons import queue_keyboard


@app.on_message(filters.command(["queue", "q", "playlist", "pl"]) & filters.group)
async def queue_command(client, message: types.Message):
    """Handle /queue command."""
    chat_id = message.chat.id
    _lang = await lang.get(chat_id)

    items = queue.get_all(chat_id)

    if not items:
        return await message.reply_text(
            _lang.get("queue_empty", "Queue is empty"),
            disable_web_page_preview=True
        )

    text = _lang.get("queue_title", "Current Queue ({0} tracks)").format(len(items)) + "\n\n"

    for idx, media in enumerate(items[:10], start=1):
        current = "▶️ " if idx == queue.position(chat_id) else f"{idx}. "
        title = media.get("title", "Unknown")[:35]
        duration = media.get("duration", "0:00")
        text += f"{current}{title} [{duration}]\n"

    if len(items) > 10:
        text += f"\n... and {len(items) - 10} more"

    if len(items) > 10:
        total_pages = (len(items) + 9) // 10
        await message.reply_text(
            text,
            reply_markup=queue_keyboard(chat_id, 1, total_pages),
            disable_web_page_preview=True
        )
    else:
        await message.reply_text(text, disable_web_page_preview=True)


@app.on_message(filters.command(["now", "np", "current"]) & filters.group)
async def now_playing_command(client, message: types.Message):
    """Handle /now command."""
    chat_id = message.chat.id
    _lang = await lang.get(chat_id)

    current = queue.get_current(chat_id)

    if not current:
        return await message.reply_text(
            _lang.get("queue_empty", "Nothing is playing"),
            disable_web_page_preview=True
        )

    video_id = current.get("id", "")
    track_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else ""

    text = _lang.get("now_playing",
        "<b>🎵 Now Playing</b>\n\n"
        "Title: <a href='{0}'>{1}</a>\n"
        "Duration: {2}\n"
        "Requested by: {3}"
    ).format(
        track_url,
        current.get("title", "Unknown"),
        current.get("duration", "0:00"),
        current.get("user", "Unknown")
    )

    await message.reply_text(text, disable_web_page_preview=True)


@app.on_message(filters.command(["clear", "clearqueue"]) & filters.group)
async def clear_queue_command(client, message: types.Message):
    """Handle /clear command."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_mention = message.from_user.mention
    _lang = await lang.get(chat_id)

    from arc.helpers.admins import is_admin
    if not await is_admin(chat_id, user_id):
        return await message.reply_text(
            _lang.get("error_not_admin", "You need to be an admin."),
            disable_web_page_preview=True
        )

    queue.clear(chat_id)
    await message.reply_text(
        _lang.get("queue_cleared", "<b>Queue Cleared</b>\n\nBy: {0}").format(user_mention),
        disable_web_page_preview=True
    )
