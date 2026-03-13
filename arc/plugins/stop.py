"""
Stop Command Plugin for Arc Music Bot
Handles stop and clear commands

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

from pyrogram import filters, types

from arc.core import app, db, call, lang, queue


@app.on_message(filters.command(["stop", "leave", "endvc"]) & filters.group)
async def stop_command(client, message: types.Message):
    """Handle /stop command."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_mention = message.from_user.mention
    _lang = await lang.get(chat_id)

    if not await db.get_call(chat_id):
        return await message.reply_text(
            _lang.get("error_no_call", "No active voice chat."),
            disable_web_page_preview=True
        )

    from arc.helpers.admins import is_admin
    if not await is_admin(chat_id, user_id):
        return await message.reply_text(
            _lang.get("error_not_admin", "You need to be an admin."),
            disable_web_page_preview=True
        )

    try:
        await call.stop(chat_id)
        await message.reply_text(
            _lang.get("stopped", "<b>Playback Stopped</b>\n\nLeft the voice chat.\n\nBy: {0}").format(user_mention),
            disable_web_page_preview=True
        )
    except Exception as ex:
        await message.reply_text(
            _lang.get("error_generic", "Error: {0}").format(str(ex)),
            disable_web_page_preview=True
        )


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


@app.on_message(filters.command(["shuffle"]) & filters.group)
async def shuffle_command(client, message: types.Message):
    """Handle /shuffle command."""
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

    if queue.is_empty(chat_id):
        return await message.reply_text(
            _lang.get("queue_empty", "Queue is empty."),
            disable_web_page_preview=True
        )

    queue.shuffle(chat_id)
    await message.reply_text(
        _lang.get("shuffled", "<b>Queue Shuffled</b>\n\nBy: {0}").format(user_mention),
        disable_web_page_preview=True
    )
