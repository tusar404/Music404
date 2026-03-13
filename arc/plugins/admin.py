"""
Admin Commands Plugin for Arc Music Bot
Handles authorization and settings commands

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

from pyrogram import filters, types

from arc.core import app, db, lang
from arc.helpers.admins import is_admin
from arc.helpers.buttons import language_keyboard, close_keyboard


@app.on_message(filters.command(["auth", "authorize"]) & filters.group)
async def auth_command(client, message: types.Message):
    """Handle /auth command."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_mention = message.from_user.mention
    _lang = await lang.get(chat_id)

    if not await is_admin(chat_id, user_id):
        return await message.reply_text(
            _lang.get("error_not_admin", "You need to be an admin."),
            disable_web_page_preview=True
        )

    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        target_name = message.reply_to_message.from_user.mention
    elif len(message.command) > 1:
        try:
            target_id = int(message.command[1])
            target_name = f"<code>{target_id}</code>"
        except ValueError:
            return await message.reply_text(
                "Invalid user ID.",
                disable_web_page_preview=True
            )
    else:
        return await message.reply_text(
            "Usage: <code>/auth [user_id]</code> or reply to a user.",
            disable_web_page_preview=True
        )

    await db.add_auth(chat_id, target_id)
    await message.reply_text(
        _lang.get("admin_auth_added", "User authorized: {0}").format(target_name),
        disable_web_page_preview=True
    )


@app.on_message(filters.command(["unauth", "deauth", "unauthorize"]) & filters.group)
async def unauth_command(client, message: types.Message):
    """Handle /unauth command."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_mention = message.from_user.mention
    _lang = await lang.get(chat_id)

    if not await is_admin(chat_id, user_id):
        return await message.reply_text(
            _lang.get("error_not_admin", "You need to be an admin."),
            disable_web_page_preview=True
        )

    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        target_name = message.reply_to_message.from_user.mention
    elif len(message.command) > 1:
        try:
            target_id = int(message.command[1])
            target_name = f"<code>{target_id}</code>"
        except ValueError:
            return await message.reply_text(
                "Invalid user ID.",
                disable_web_page_preview=True
            )
    else:
        return await message.reply_text(
            "Usage: <code>/unauth [user_id]</code>",
            disable_web_page_preview=True
        )

    await db.remove_auth(chat_id, target_id)
    await message.reply_text(
        _lang.get("admin_auth_removed", "User unauthorized: {0}").format(target_name),
        disable_web_page_preview=True
    )


@app.on_message(filters.command(["adminmode", "adminonly"]) & filters.group)
async def admin_mode_command(client, message: types.Message):
    """Handle /adminmode command."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_mention = message.from_user.mention
    _lang = await lang.get(chat_id)

    if not await is_admin(chat_id, user_id):
        return await message.reply_text(
            _lang.get("error_not_admin", "You need to be an admin."),
            disable_web_page_preview=True
        )

    current_mode = await db.get_play_mode(chat_id)
    new_mode = not current_mode

    await db.set_play_mode(chat_id, new_mode)

    if new_mode:
        await message.reply_text(
            _lang.get("admin_mode_on", "Admin-only mode enabled.\n\nOnly admins can play music.\n\nBy: {0}").format(user_mention),
            disable_web_page_preview=True
        )
    else:
        await message.reply_text(
            _lang.get("admin_mode_off", "Admin-only mode disabled.\n\nEveryone can play music.\n\nBy: {0}").format(user_mention),
            disable_web_page_preview=True
        )


@app.on_message(filters.command(["setlang", "lang"]) & filters.group)
async def set_language_command(client, message: types.Message):
    """Handle /setlang command with inline buttons."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_mention = message.from_user.mention
    _lang = await lang.get(chat_id)

    if not await is_admin(chat_id, user_id):
        return await message.reply_text(
            _lang.get("error_not_admin", "You need to be an admin."),
            disable_web_page_preview=True
        )

    # Show inline buttons for language selection
    current_lang = await db.get_lang(chat_id)
    await message.reply_text(
        f"<b>Choose Language / भाषा चुनें</b>\n\n"
        f"Current: <code>{current_lang.upper() if current_lang else 'EN'}</code>",
        reply_markup=language_keyboard(),
        disable_web_page_preview=True
    )


@app.on_callback_query(filters.regex("^lang_"))
async def language_callback(client, query: types.CallbackQuery):
    """Handle language selection callback."""
    chat_id = query.message.chat.id
    user_id = query.from_user.id
    user_mention = query.from_user.mention

    if not await is_admin(chat_id, user_id):
        return await query.answer("You need to be an admin!", show_alert=True)

    lang_code = query.data.split("_")[1]

    if await lang.set_chat_lang(chat_id, lang_code):
        _lang = await lang.get(chat_id)
        await query.edit_message_text(
            _lang.get("lang_set", "Language set to: {0}").format(lang_code.upper()),
            reply_markup=close_keyboard(),
            disable_web_page_preview=True
        )
    else:
        await query.answer(f"Language '{lang_code}' not found!", show_alert=True)


@app.on_message(filters.command(["thumbnail", "thumb"]) & filters.group)
async def thumbnail_command(client, message: types.Message):
    """Handle /thumbnail command."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_mention = message.from_user.mention
    _lang = await lang.get(chat_id)

    if not await is_admin(chat_id, user_id):
        return await message.reply_text(
            _lang.get("error_not_admin", "You need to be an admin."),
            disable_web_page_preview=True
        )

    current = await db.is_thumbnail_enabled(chat_id)
    new_value = not current
    await db.set_thumbnail(chat_id, new_value)

    if new_value:
        await message.reply_text(
            _lang.get("thumbnail_on", "Thumbnails enabled.\n\nBy: {0}").format(user_mention),
            disable_web_page_preview=True
        )
    else:
        await message.reply_text(
            _lang.get("thumbnail_off", "Thumbnails disabled.\n\nBy: {0}").format(user_mention),
            disable_web_page_preview=True
        )
