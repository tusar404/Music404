"""
Skip Command Plugin for Arc Music Bot
Handles skip and next commands

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

from pyrogram import filters, types

from arc.core import app, db, call, lang, queue


@app.on_message(filters.command(["skip", "next", "sk"]) & filters.group)
async def skip_command(client, message: types.Message):
    """Handle /skip command."""
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

    if not queue.has_next(chat_id):
        return await message.reply_text(
            _lang.get("queue_no_more", "No more tracks in queue."),
            disable_web_page_preview=True
        )

    try:
        await call.play_next(chat_id)
        await message.reply_text(
            _lang.get("skipped", "Skipped to next track.\n\nBy: {0}").format(user_mention),
            disable_web_page_preview=True
        )
    except Exception as ex:
        await message.reply_text(
            _lang.get("error_generic", "Error: {0}").format(str(ex)),
            disable_web_page_preview=True
        )


@app.on_message(filters.command(["end", "endskip"]) & filters.group)
async def end_skip_command(client, message: types.Message):
    """Handle /end command - skip to end of queue."""
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

    # Clear queue and stop
    queue.clear(chat_id)
    await call.stop(chat_id)
    await message.reply_text(
        _lang.get("stopped", "Playback stopped.\n\nBy: {0}").format(user_mention),
        disable_web_page_preview=True
    )
