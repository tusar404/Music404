"""
Sudo Commands Plugin for Arc Music Bot
Handles owner and sudo user commands

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

from pyrogram import filters, types

from arc.core import app, config, db, call, lang, queue, tg_log
from arc.core.logging import LOGGER


async def is_sudo_user(user_id: int) -> bool:
    """Check if user is owner or sudo."""
    if user_id == config.OWNER_ID:
        return True
    sudoers = await db.get_sudoers()
    return user_id in sudoers


@app.on_message(filters.command(["sudo", "addsudo"]) & filters.private)
async def add_sudo_command(client, message: types.Message):
    """Add sudo user (owner only)."""
    user_id = message.from_user.id
    user_mention = message.from_user.mention

    if user_id != config.OWNER_ID:
        return

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
            "Usage: <code>/sudo [user_id]</code>",
            disable_web_page_preview=True
        )

    await db.add_sudo(target_id)
    LOGGER(__name__).info(f"Sudo added: {target_id}")
    await message.reply_text(
        f"<b>Sudo user added:</b> {target_name}\n\nBy: {user_mention}",
        disable_web_page_preview=True
    )


@app.on_message(filters.command(["delsudo", "rmsudo"]) & filters.private)
async def remove_sudo_command(client, message: types.Message):
    """Remove sudo user (owner only)."""
    user_id = message.from_user.id
    user_mention = message.from_user.mention

    if user_id != config.OWNER_ID:
        return

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
            "Usage: <code>/delsudo [user_id]</code>",
            disable_web_page_preview=True
        )

    await db.remove_sudo(target_id)
    await message.reply_text(
        f"<b>Sudo user removed:</b> {target_name}\n\nBy: {user_mention}",
        disable_web_page_preview=True
    )


@app.on_message(filters.command(["blacklist", "bl"]) & filters.private)
async def blacklist_command(client, message: types.Message):
    """Blacklist chat/user (owner only)."""
    user_id = message.from_user.id
    user_mention = message.from_user.mention

    if user_id != config.OWNER_ID:
        return

    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        target_name = message.reply_to_message.from_user.mention
    elif len(message.command) > 1:
        try:
            target_id = int(message.command[1])
            target_name = f"<code>{target_id}</code>"
        except ValueError:
            return await message.reply_text(
                "Invalid ID.",
                disable_web_page_preview=True
            )
    else:
        return await message.reply_text(
            "Usage: <code>/blacklist [chat_id/user_id]</code>",
            disable_web_page_preview=True
        )

    await db.add_blacklist(target_id)
    LOGGER(__name__).info(f"Blacklisted: {target_id}")
    await message.reply_text(
        f"<b>Blacklisted:</b> {target_name}\n\nBy: {user_mention}",
        disable_web_page_preview=True
    )


@app.on_message(filters.command(["unblacklist", "unbl"]) & filters.private)
async def unblacklist_command(client, message: types.Message):
    """Unblacklist chat/user (owner only)."""
    user_id = message.from_user.id
    user_mention = message.from_user.mention

    if user_id != config.OWNER_ID:
        return

    if len(message.command) < 2:
        return await message.reply_text(
            "Usage: <code>/unblacklist [id]</code>",
            disable_web_page_preview=True
        )

    try:
        target_id = int(message.command[1])
    except ValueError:
        return await message.reply_text(
            "Invalid ID.",
            disable_web_page_preview=True
        )

    await db.remove_blacklist(target_id)
    await message.reply_text(
        f"<b>Unblacklisted:</b> <code>{target_id}</code>\n\nBy: {user_mention}",
        disable_web_page_preview=True
    )


@app.on_message(filters.command(["stats", "botstats"]) & filters.private)
async def stats_command(client, message: types.Message):
    """Show bot statistics."""
    user_id = message.from_user.id

    if not await is_sudo_user(user_id):
        return

    users = await db.get_users()
    chats = await db.get_chats()
    active_calls = await db.get_active_calls()

    text = (
        f"<b>Bot Statistics</b>\n\n"
        f"Users: {len(users)}\n"
        f"Chats: {len(chats)}\n"
        f"Active Calls: {len(active_calls)}\n"
        f"Assistants: {len(call.clients)}\n\n"
        f"Copyright (c) 2025 Team Arc\n"
        f"Developer: @tusar404"
    )

    await message.reply_text(text, disable_web_page_preview=True)


@app.on_message(filters.command(["active", "activecalls", "calls"]) & filters.private)
async def active_calls_command(client, message: types.Message):
    """Show active voice chats."""
    user_id = message.from_user.id

    if not await is_sudo_user(user_id):
        return

    active_calls = await db.get_active_calls()

    if not active_calls:
        return await message.reply_text(
            "No active voice chats.",
            disable_web_page_preview=True
        )

    text = f"<b>Active Voice Chats</b> ({len(active_calls)})\n\n"

    for idx, chat_id in enumerate(active_calls.keys(), start=1):
        try:
            chat = await app.get_chat(chat_id)
            text += f"{idx}. {chat.title} (ID: <code>{chat_id}</code>)\n"
        except Exception:
            text += f"{idx}. Unknown (ID: <code>{chat_id}</code>)\n"

    await message.reply_text(text, disable_web_page_preview=True)


@app.on_message(filters.command(["broadcast", "gcast"]) & filters.private)
async def broadcast_command(client, message: types.Message):
    """Broadcast message to all chats."""
    user_id = message.from_user.id
    user_mention = message.from_user.mention

    if not await is_sudo_user(user_id):
        return

    if len(message.command) < 2:
        return await message.reply_text(
            "Usage: <code>/broadcast [message]</code>",
            disable_web_page_preview=True
        )

    broadcast_text = " ".join(message.command[1:])
    chats = await db.get_chats()

    success = 0
    failed = 0

    status = await message.reply_text(
        f"<b>Broadcasting to {len(chats)} chats...</b>",
        disable_web_page_preview=True
    )

    for chat_id in chats:
        try:
            # Broadcast with preview enabled (only place where preview is enabled)
            await app.send_message(chat_id, broadcast_text, disable_web_page_preview=False)
            success += 1
        except Exception:
            failed += 1

    await status.edit_text(
        f"<b>Broadcast Complete</b>\n\n"
        f"Success: {success}\n"
        f"Failed: {failed}\n\n"
        f"By: {user_mention}",
        disable_web_page_preview=True
    )


@app.on_message(filters.command(["maintenance", "maintain"]) & filters.private)
async def maintenance_command(client, message: types.Message):
    """Toggle maintenance mode."""
    user_id = message.from_user.id
    user_mention = message.from_user.mention

    if not await is_sudo_user(user_id):
        return

    current = config.MAINTENANCE_MODE
    new_value = not current

    config.set_maintenance(new_value)

    await tg_log.log_maintenance(new_value, message.from_user)

    if new_value:
        await message.reply_text(
            f"<b>Maintenance mode enabled.</b>\n\nBot will only respond to sudo users.\n\nBy: {user_mention}",
            disable_web_page_preview=True
        )
    else:
        await message.reply_text(
            f"<b>Maintenance mode disabled.</b>\n\nBot is now available.\n\nBy: {user_mention}",
            disable_web_page_preview=True
        )


@app.on_message(filters.command(["logger", "logs"]) & filters.private)
async def logger_command(client, message: types.Message):
    """Toggle Telegram logging."""
    user_id = message.from_user.id
    user_mention = message.from_user.mention

    if not await is_sudo_user(user_id):
        return

    current = await db.is_logger()
    new_value = not current

    await db.set_logger(new_value)
    tg_log.enabled = new_value

    status = "Enabled" if new_value else "Disabled"
    await message.reply_text(
        f"<b>Telegram Logger:</b> {status}\n\nBy: {user_mention}",
        disable_web_page_preview=True
    )


@app.on_message(filters.command(["leave", "leavechat"]) & filters.private)
async def leave_chat_command(client, message: types.Message):
    """Leave a chat."""
    user_id = message.from_user.id
    user_mention = message.from_user.mention

    if not await is_sudo_user(user_id):
        return

    if len(message.command) < 2:
        return await message.reply_text(
            "Usage: <code>/leave [chat_id]</code>",
            disable_web_page_preview=True
        )

    try:
        chat_id = int(message.command[1])
    except ValueError:
        return await message.reply_text(
            "Invalid chat ID.",
            disable_web_page_preview=True
        )

    try:
        await app.leave_chat(chat_id)
        await db.remove_chat(chat_id)
        await message.reply_text(
            f"<b>Left chat:</b> <code>{chat_id}</code>\n\nBy: {user_mention}",
            disable_web_page_preview=True
        )
    except Exception as ex:
        await message.reply_text(
            f"<b>Failed to leave chat:</b> {ex}",
            disable_web_page_preview=True
        )


@app.on_message(filters.command(["restart", "reboot"]) & filters.private)
async def restart_command(client, message: types.Message):
    """Restart the bot."""
    user_id = message.from_user.id
    user_mention = message.from_user.mention

    if not await is_sudo_user(user_id):
        return

    await message.reply_text(
        f"<b>Restarting bot...</b>\n\nBy: {user_mention}",
        disable_web_page_preview=True
    )

    import os
    import sys
    os.execv(sys.executable, [sys.executable] + sys.argv)


@app.on_message(filters.command(["cleanup", "clean"]) & filters.private)
async def cleanup_command(client, message: types.Message):
    """Clean cache and database."""
    user_id = message.from_user.id
    user_mention = message.from_user.mention

    if not await is_sudo_user(user_id):
        return

    from arc.utils.cleanup import CacheCleaner
    cleaner = CacheCleaner()
    disk_result = await cleaner.force_cleanup()

    db_result = await db.cleanup_database()

    await message.reply_text(
        f"<b>Cleanup Complete</b>\n\n"
        f"<b>Disk:</b>\n"
        f"- Cache: {disk_result['cache']}\n"
        f"- Downloads: {disk_result['downloads']}\n"
        f"- Freed: {disk_result['total_size'] / (1024*1024):.2f} MB\n\n"
        f"<b>Database:</b>\n"
        f"- Chats removed: {db_result['chats']}\n\n"
        f"By: {user_mention}",
        disable_web_page_preview=True
    )
