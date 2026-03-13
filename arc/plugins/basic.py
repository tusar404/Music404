"""
Basic Commands Plugin for Arc Music Bot
Handles start, help, ping, and utility commands

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

from pyrogram import filters, types
from pyrogram.errors import MessageNotModified

from arc.core import app, config, call, db, lang
from arc.helpers.buttons import (
    start_keyboard, help_main_keyboard, help_back_keyboard, close_keyboard
)


@app.on_message(filters.command(["start"]) & filters.private)
async def start_command(client, message: types.Message):
    """Handle /start command with animation effect."""
    user = message.from_user
    await db.add_user(user.id)

    from arc.core import tg_log
    await tg_log.log_user_start(user)

    _lang = await lang.get(user.id)

    # Send animated starting message
    animation_frames = [
        "⏳ <i>Initializing...</i>",
        "⏳ <i>Loading components...</i>",
        "⏳ <i>Connecting to server...</i>",
        "✅ <i>Ready!</i>",
    ]

    status = await message.reply_text(animation_frames[0], disable_web_page_preview=True)

    # Animate through frames
    for frame in animation_frames[1:]:
        try:
            await status.edit_text(frame, disable_web_page_preview=True)
        except MessageNotModified:
            pass

    # Final welcome message
    text = _lang.get("start_pm",
        "<b>Welcome to {0}!</b>\n\n"
        "I can play music and videos in your Telegram voice chats.\n\n"
        "<b>Features:</b>\n"
        "• Play audio from YouTube\n"
        "• Play video from YouTube\n"
        "• Support for Telegram media files\n"
        "• Queue management\n"
        "• Playlist support\n\n"
        "<b>Add me to a group and use</b> <code>/play</code> <b>to start!</b>"
    ).format(app.name)

    await status.edit_text(
        text,
        reply_markup=start_keyboard(app.username),
        disable_web_page_preview=True
    )


@app.on_message(filters.command(["help"]) & filters.group)
async def help_group_command(client, message: types.Message):
    """Handle /help in groups with inline buttons."""
    _lang = await lang.get(message.chat.id)

    text = _lang.get("help_main",
        "<b>Arc Music Bot - Help Center</b>\n\n"
        "Select a category below to view commands:"
    )

    await message.reply_text(
        text,
        reply_markup=help_main_keyboard(),
        disable_web_page_preview=True
    )


@app.on_message(filters.command(["help"]) & filters.private)
async def help_pm_command(client, message: types.Message):
    """Handle /help in private with inline buttons."""
    _lang = await lang.get(message.from_user.id)

    text = _lang.get("help_main",
        "<b>Arc Music Bot - Help Center</b>\n\n"
        "Select a category below to view commands:"
    )

    await message.reply_text(
        text,
        reply_markup=help_main_keyboard(),
        disable_web_page_preview=True
    )


@app.on_callback_query(filters.regex("^help_main$"))
async def help_main_callback(client, query: types.CallbackQuery):
    """Handle main help menu callback."""
    _lang = await lang.get(query.message.chat.id)

    text = _lang.get("help_main",
        "<b>Arc Music Bot - Help Center</b>\n\n"
        "Select a category below to view commands:"
    )

    await query.edit_message_text(
        text,
        reply_markup=help_main_keyboard(),
        disable_web_page_preview=True
    )


@app.on_callback_query(filters.regex("^help_"))
async def help_category_callback(client, query: types.CallbackQuery):
    """Handle help category callbacks."""
    category = query.data.split("_")[1]
    _lang = await lang.get(query.message.chat.id)

    help_texts = {
        "play": _lang.get("help_play",
            "<b>🎵 Play Commands</b>\n\n"
            "<code>/play [song]</code> - Play audio from YouTube\n"
            "<code>/play [url]</code> - Play from YouTube URL\n"
            "<code>/vplay [video]</code> - Play video in VC\n"
            "<code>/play</code> (reply) - Play replied media\n\n"
            "<i>Supports: YouTube, SoundCloud, Spotify links</i>"
        ),
        "queue": _lang.get("help_queue",
            "<b>📋 Queue Commands</b>\n\n"
            "<code>/queue</code> - View current queue\n"
            "<code>/now</code> - Show now playing\n"
            "<code>/clear</code> - Clear the queue\n"
            "<code>/shuffle</code> - Shuffle queue\n\n"
            "<i>Queue supports pagination for large lists</i>"
        ),
        "controls": _lang.get("help_controls",
            "<b>🎛️ Playback Controls</b>\n\n"
            "<code>/pause</code> - Pause playback\n"
            "<code>/resume</code> - Resume playback\n"
            "<code>/skip</code> - Skip current track\n"
            "<code>/stop</code> - Stop and leave VC\n"
            "<code>/seek [time]</code> - Seek to position\n\n"
            "<i>Example: /seek 1:30</i>"
        ),
        "admin": _lang.get("help_admin",
            "<b>👨‍💼 Admin Commands</b>\n\n"
            "<code>/auth [user]</code> - Authorize user\n"
            "<code>/unauth [user]</code> - Remove authorization\n"
            "<code>/adminmode</code> - Toggle admin-only mode\n"
            "<code>/setlang</code> - Set language\n"
            "<code>/thumbnail</code> - Toggle thumbnails"
        ),
        "settings": _lang.get("help_settings",
            "<b>⚙️ Settings</b>\n\n"
            "<code>/setlang</code> - Change bot language\n"
            "<code>/thumbnail</code> - Toggle thumbnail display\n"
            "<code>/adminmode</code> - Restrict to admins only\n\n"
            "<i>Languages: English, Hindi, Spanish, Arabic, Indonesian, Burmese</i>"
        ),
        "sudo": _lang.get("help_sudo",
            "<b>🔐 Sudo Commands</b>\n\n"
            "<code>/sudo [user]</code> - Add sudo user\n"
            "<code>/delsudo [user]</code> - Remove sudo\n"
            "<code>/blacklist [id]</code> - Blacklist chat/user\n"
            "<code>/broadcast [msg]</code> - Broadcast message\n"
            "<code>/maintenance</code> - Maintenance mode\n"
            "<code>/active</code> - Show active calls\n"
            "<code>/stats</code> - Bot statistics\n"
            "<code>/restart</code> - Restart bot"
        ),
        "tools": _lang.get("help_tools",
            "<b>🔧 Utility Commands</b>\n\n"
            "<code>/ping</code> - Check bot latency\n"
            "<code>/id</code> - Get chat/user IDs\n"
            "<code>/info</code> - Bot information\n"
            "<code>/speed</code> - Speed test\n\n"
            "<i>These commands work in all chats</i>"
        ),
    }

    text = help_texts.get(category, "Unknown category.")
    await query.edit_message_text(
        text,
        reply_markup=help_back_keyboard(),
        disable_web_page_preview=True
    )


@app.on_message(filters.command(["ping", "pong"]))
async def ping_command(client, message: types.Message):
    """Handle /ping command."""
    import time

    _lang = await lang.get(message.chat.id)

    start = time.time()
    msg = await message.reply_text("🏓 Pong!", disable_web_page_preview=True)
    end = time.time()

    ping_ms = round((end - start) * 1000, 2)
    pytgcalls_ping = await call.ping() if call.clients else 0

    text = _lang.get("ping", "<b>Pong!</b>\n\nAPI: {0}ms | VC: {1}ms").format(ping_ms, pytgcalls_ping)

    await msg.edit_text(text, disable_web_page_preview=True)


@app.on_message(filters.command(["id"]))
async def id_command(client, message: types.Message):
    """Handle /id command."""
    text = ""

    if message.chat.type != "private":
        text += f"Chat ID: <code>{message.chat.id}</code>\n"

    text += f"User ID: <code>{message.from_user.id}</code>"

    if message.reply_to_message:
        text += f"\nReplied User ID: <code>{message.reply_to_message.from_user.id}</code>"

    await message.reply_text(text, disable_web_page_preview=True)


@app.on_message(filters.command(["info", "botinfo"]))
async def info_command(client, message: types.Message):
    """Handle /info command."""
    users = len(await db.get_users())
    chats = len(await db.get_chats())

    text = (
        f"<b>{app.name}</b>\n\n"
        f"ID: <code>{app.id}</code>\n"
        f"Username: @{app.username}\n\n"
        f"Users: {users}\n"
        f"Chats: {chats}\n"
        f"Active Calls: {len(db.active_calls)}\n"
        f"Assistants: {len(call.clients)}\n\n"
        f"Copyright (c) 2025 Team Arc\n"
        f"Developer: @tusar404"
    )

    await message.reply_text(text, disable_web_page_preview=True)


@app.on_callback_query(filters.regex("^add_me$"))
async def add_me_callback(client, query: types.CallbackQuery):
    """Handle add me callback."""
    await query.answer("Add me to your group and promote as admin!", show_alert=True)


@app.on_callback_query(filters.regex("^close$"))
async def close_callback(client, query: types.CallbackQuery):
    """Handle close callback."""
    try:
        await query.message.delete()
    except Exception:
        pass
