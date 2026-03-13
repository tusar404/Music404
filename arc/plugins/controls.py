"""
Playback Controls Plugin for Arc Music Bot
Handles pause, resume, seek commands

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

from pyrogram import filters, types

from arc.core import app, db, call, lang


@app.on_message(filters.command(["pause", "puse"]) & filters.group)
async def pause_command(client, message: types.Message):
    """Handle /pause command."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_mention = message.from_user.mention
    _lang = await lang.get(chat_id)

    if not await db.get_call(chat_id):
        return await message.reply_text(
            _lang.get("error_no_call", "No active voice chat."),
            disable_web_page_preview=True
        )

    if await db.get_play_mode(chat_id):
        from arc.helpers.admins import is_admin
        if not await is_admin(chat_id, user_id):
            return await message.reply_text(
                _lang.get("error_not_admin", "You need to be an admin."),
                disable_web_page_preview=True
            )

    try:
        await call.pause(chat_id)
        await message.reply_text(
            _lang.get("paused", "Playback Paused\n\nBy: {0}").format(user_mention),
            disable_web_page_preview=True
        )
    except Exception as ex:
        await message.reply_text(
            _lang.get("error_generic", "Error: {0}").format(str(ex)),
            disable_web_page_preview=True
        )


@app.on_message(filters.command(["resume", "res"]) & filters.group)
async def resume_command(client, message: types.Message):
    """Handle /resume command."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_mention = message.from_user.mention
    _lang = await lang.get(chat_id)

    if not await db.get_call(chat_id):
        return await message.reply_text(
            _lang.get("error_no_call", "No active voice chat."),
            disable_web_page_preview=True
        )

    if await db.get_play_mode(chat_id):
        from arc.helpers.admins import is_admin
        if not await is_admin(chat_id, user_id):
            return await message.reply_text(
                _lang.get("error_not_admin", "You need to be an admin."),
                disable_web_page_preview=True
            )

    try:
        await call.resume(chat_id)
        await message.reply_text(
            _lang.get("resumed", "Playback Resumed\n\nBy: {0}").format(user_mention),
            disable_web_page_preview=True
        )
    except Exception as ex:
        await message.reply_text(
            _lang.get("error_generic", "Error: {0}").format(str(ex)),
            disable_web_page_preview=True
        )


@app.on_message(filters.command(["seek"]) & filters.group)
async def seek_command(client, message: types.Message):
    """Handle /seek command."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_mention = message.from_user.mention
    _lang = await lang.get(chat_id)

    if not await db.get_call(chat_id):
        return await message.reply_text(
            _lang.get("error_no_call", "No active voice chat."),
            disable_web_page_preview=True
        )

    if await db.get_play_mode(chat_id):
        from arc.helpers.admins import is_admin
        if not await is_admin(chat_id, user_id):
            return await message.reply_text(
                _lang.get("error_not_admin", "You need to be an admin."),
                disable_web_page_preview=True
            )

    # Parse seek time
    if len(message.command) < 2:
        return await message.reply_text(
            _lang.get("seek_usage", "Usage: /seek [time]\n\nExample: /seek 1:30 or /seek 90"),
            disable_web_page_preview=True
        )

    time_str = message.command[1]

    try:
        # Parse time (supports both "1:30" and "90" formats)
        if ":" in time_str:
            parts = time_str.split(":")
            if len(parts) == 2:
                minutes = int(parts[0])
                seconds = int(parts[1])
                seek_seconds = minutes * 60 + seconds
            elif len(parts) == 3:
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = int(parts[2])
                seek_seconds = hours * 3600 + minutes * 60 + seconds
            else:
                raise ValueError("Invalid time format")
        else:
            seek_seconds = int(time_str)

        # Seek
        await call.seek(chat_id, seek_seconds)
        await message.reply_text(
            _lang.get("seek_success", "Seeked to {0}\n\nBy: {1}").format(
                f"{seek_seconds // 60}:{seek_seconds % 60:02d}",
                user_mention
            ),
            disable_web_page_preview=True
        )
    except ValueError:
        await message.reply_text(
            _lang.get("seek_invalid", "Invalid seek time.\n\nFormat: 1:30 or 90"),
            disable_web_page_preview=True
        )
    except Exception as ex:
        await message.reply_text(
            _lang.get("error_generic", "Error: {0}").format(str(ex)),
            disable_web_page_preview=True
        )
