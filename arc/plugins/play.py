"""
Play Command Plugin for Arc Music Bot
Handles play, vplay commands for YouTube and Telegram media

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

import asyncio
from pyrogram import filters, types
from pyrogram.errors import UserNotParticipant, ChannelPrivate

from arc.core import app, config, db, call, yt, tg, queue, lang, tg_log
from arc.helpers.utils import is_url, extract_url
from arc.helpers.admins import is_admin, bot_can_manage_voice_chats, bot_can_invite_users

# Timeouts
SEARCH_TIMEOUT = 10  # 10 seconds for searching
DOWNLOAD_TIMEOUT = 80  # 80 seconds for API downloads


async def check_permissions(chat_id: int, user_id: int, _lang: dict) -> tuple:
    """Check if user can use play command."""
    if chat_id in await db.get_blacklisted(True):
        return False, _lang.get("error_blacklisted", "This chat is blacklisted.")

    if config.MAINTENANCE_MODE:
        if not await app.is_sudo(user_id):
            return False, _lang.get("error_maintenance", "Bot is under maintenance.")

    if await db.get_play_mode(chat_id):
        if not await is_admin(chat_id, user_id):
            return False, _lang.get("error_not_admin", "You need to be an admin.")

    return True, None


async def check_bot_permissions(chat_id: int, _lang: dict) -> tuple:
    """Check if bot has required permissions."""
    issues = []

    if not await bot_can_manage_voice_chats(chat_id):
        issues.append("Manage Voice Chats")

    if not await bot_can_invite_users(chat_id):
        issues.append("Invite Users via Link")

    if issues:
        return False, _lang.get("error_bot_permissions", "Bot lacks permissions.") + "\n\nMissing: " + ", ".join(issues)

    return True, None


async def check_assistant(chat_id: int, _lang: dict) -> tuple:
    """Check if assistant is in chat."""
    status = await call.check_assistant_status(chat_id)

    if status.get("banned"):
        assistant_name = status.get("assistant_name", "Assistant")
        assistant_id = status.get("assistant_id", "Unknown")
        return False, (
            f"<b>Assistant is banned in this chat!</b>\n\n"
            f"Assistant: {assistant_name}\n"
            f"ID: <code>{assistant_id}</code>\n\n"
            f"Please unban the assistant to continue."
        )

    if not status.get("valid"):
        await db.set_assistant(chat_id)
        return True, None

    return True, None


async def start_playback(chat_id: int, status: types.Message, track: dict):
    """Start playback - download only when ready to play."""
    _lang = await lang.get(chat_id)

    await status.edit_text(_lang.get("play_downloading", "Downloading..."), disable_web_page_preview=True)

    try:
        # Download with timeout
        file_path = await asyncio.wait_for(
            yt.download(track.get("id"), video=track.get("video", False)),
            timeout=DOWNLOAD_TIMEOUT
        )
    except asyncio.TimeoutError:
        await status.edit_text(
            _lang.get("error_download_timeout", "Download timed out. Please try again."),
            disable_web_page_preview=True
        )
        queue.remove(chat_id, queue.position(chat_id))
        return

    if not file_path:
        await status.edit_text(
            _lang.get("error_no_file", "Download failed. Contact {0}").format(config.SUPPORT_CHAT),
            disable_web_page_preview=True
        )
        queue.remove(chat_id, queue.position(chat_id))
        return

    track["file_path"] = file_path
    queue.set_current(chat_id, track)

    await call.play_media(chat_id, status, track)


@app.on_message(filters.command(["play", "p", "vplay", "vp"]) & filters.group)
async def play_command(client, message: types.Message):
    """Handle /play and /vplay commands."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_mention = message.from_user.mention

    # Check anonymous
    if not user_id:
        _lang = await lang.get(chat_id)
        return await message.reply_text(
            _lang.get("error_anonymous", "You appear to be anonymous!"),
            disable_web_page_preview=True
        )

    _lang = await lang.get(chat_id)

    # Check permissions
    can_play, error = await check_permissions(chat_id, user_id, _lang)
    if not can_play:
        return await message.reply_text(error, disable_web_page_preview=True)

    # Check bot permissions
    has_perms, perm_error = await check_bot_permissions(chat_id, _lang)
    if not has_perms:
        await tg_log.log_permission_issue(chat_id, message.chat.title, perm_error)
        return await message.reply_text(perm_error, disable_web_page_preview=True)

    # Check assistant
    assistant_ok, assistant_error = await check_assistant(chat_id, _lang)
    if not assistant_ok:
        if "banned" in assistant_error.lower():
            await tg_log.log_assistant_banned(
                call.clients[0].me.id if call.clients else 0,
                "Assistant",
                chat_id,
                message.chat.title
            )
        return await message.reply_text(assistant_error, disable_web_page_preview=True)

    is_video = message.command[0] in ["vplay", "vp"]

    # Register
    await db.add_chat(chat_id, message.chat.title)
    await db.add_user(user_id)

    # Handle reply to Telegram media
    if message.reply_to_message:
        reply = message.reply_to_message

        if tg.has_media(reply):
            status = await message.reply_text(
                _lang.get("play_downloading", "Downloading..."),
                disable_web_page_preview=True
            )
            media = await tg.download(reply, status, _lang)

            if media:
                media["user"] = user_mention
                media["video"] = is_video or media.get("video", False)

                position = queue.add(chat_id, media)

                if not await db.get_call(chat_id):
                    await start_playback(chat_id, status, media)
                else:
                    video_id = media.get("id", "")
                    track_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else ""
                    await status.edit_text(
                        _lang.get("play_added", "Added to queue\n\nTitle: {0}\nPosition: {1}").format(
                            f"<a href='{track_url}'>{media.get('title', 'Unknown')}</a>",
                            position
                        ),
                        disable_web_page_preview=True
                    )
            return

    # Get query
    query = " ".join(message.command[1:])

    if not query:
        return await message.reply_text(
            _lang.get("play_usage", "Usage: /{0} [song name or URL]").format(message.command[0]),
            disable_web_page_preview=True
        )

    status = await message.reply_text(
        _lang.get("play_searching", "Searching for: {0}").format(query),
        disable_web_page_preview=True
    )

    url = extract_url(query) if is_url(query) else None

    if url and yt.is_valid_url(url):
        # Playlist
        if "playlist" in url:
            limit = min(config.DURATION_LIMIT, 50)
            tracks = await yt.get_playlist(url, limit, user_mention, is_video)

            if tracks:
                for track in tracks:
                    queue.add(chat_id, track)

                await status.edit_text(
                    _lang.get("playlist_added", "Playlist added: {0} tracks").format(len(tracks)),
                    disable_web_page_preview=True
                )

                if not await db.get_call(chat_id) and tracks:
                    first = queue.get(chat_id, 1)
                    await start_playback(chat_id, status, first)
            else:
                await status.edit_text(
                    _lang.get("play_no_results", "No results for: {0}").format(query),
                    disable_web_page_preview=True
                )
        else:
            # Single video - search with timeout
            try:
                video_id = yt.extract_video_id(url)
                if video_id:
                    track = await asyncio.wait_for(
                        yt.search(url, status.id, is_video),
                        timeout=SEARCH_TIMEOUT
                    )
                    if track:
                        track["user"] = user_mention
                        position = queue.add(chat_id, track)

                        if not await db.get_call(chat_id):
                            await start_playback(chat_id, status, track)
                        else:
                            track_url = f"https://www.youtube.com/watch?v={track.get('id', '')}"
                            await status.edit_text(
                                _lang.get("play_added", "Added to queue\n\nTitle: {0}\nPosition: {1}").format(
                                    f"<a href='{track_url}'>{track.get('title', 'Unknown')}</a>",
                                    position
                                ),
                                disable_web_page_preview=True
                            )
                    else:
                        await status.edit_text(
                            _lang.get("play_no_results", "No results for: {0}").format(query),
                            disable_web_page_preview=True
                        )
                else:
                    await status.edit_text("Invalid YouTube URL.", disable_web_page_preview=True)
            except asyncio.TimeoutError:
                await status.edit_text(
                    _lang.get("play_timeout", "Search timed out. Please try again."),
                    disable_web_page_preview=True
                )
    else:
        # Search with timeout
        try:
            track = await asyncio.wait_for(
                yt.search(query, status.id, is_video),
                timeout=SEARCH_TIMEOUT
            )

            if track:
                track["user"] = user_mention
                position = queue.add(chat_id, track)

                if not await db.get_call(chat_id):
                    await start_playback(chat_id, status, track)
                else:
                    track_url = f"https://www.youtube.com/watch?v={track.get('id', '')}"
                    await status.edit_text(
                        _lang.get("play_added", "Added to queue\n\nTitle: {0}\nPosition: {1}").format(
                            f"<a href='{track_url}'>{track.get('title', 'Unknown')}</a>",
                            position
                        ),
                        disable_web_page_preview=True
                    )
            else:
                await status.edit_text(
                    _lang.get("play_no_results", "No results for: {0}").format(query),
                    disable_web_page_preview=True
                )
        except asyncio.TimeoutError:
            await status.edit_text(
                _lang.get("play_timeout", "Search timed out. Please try again."),
                disable_web_page_preview=True
            )


# Callbacks
@app.on_callback_query(filters.regex(r"^pause_(\d+)"))
async def cb_pause(client, query: types.CallbackQuery):
    """Handle pause callback."""
    chat_id = int(query.matches[0].group(1))
    _lang = await lang.get(chat_id)

    try:
        await call.pause(chat_id)
        from arc.helpers.buttons import paused_keyboard
        await query.edit_message_reply_markup(reply_markup=paused_keyboard(chat_id))
        await query.answer(_lang.get("paused", "Paused by {0}").format(query.from_user.mention))
    except Exception as ex:
        await query.answer(f"Error: {ex}", show_alert=True)


@app.on_callback_query(filters.regex(r"^resume_(\d+)"))
async def cb_resume(client, query: types.CallbackQuery):
    """Handle resume callback."""
    chat_id = int(query.matches[0].group(1))
    _lang = await lang.get(chat_id)

    try:
        await call.resume(chat_id)
        from arc.helpers.buttons import controls_keyboard
        await query.edit_message_reply_markup(reply_markup=controls_keyboard(chat_id))
        await query.answer(_lang.get("resumed", "Resumed by {0}").format(query.from_user.mention))
    except Exception as ex:
        await query.answer(f"Error: {ex}", show_alert=True)


@app.on_callback_query(filters.regex(r"^skip_(\d+)"))
async def cb_skip(client, query: types.CallbackQuery):
    """Handle skip callback."""
    chat_id = int(query.matches[0].group(1))

    try:
        await call.play_next(chat_id)
        await query.answer(f"Skipped by {query.from_user.mention}!")
    except Exception as ex:
        await query.answer(f"Error: {ex}", show_alert=True)


@app.on_callback_query(filters.regex(r"^stop_(\d+)"))
async def cb_stop(client, query: types.CallbackQuery):
    """Handle stop callback."""
    chat_id = int(query.matches[0].group(1))
    _lang = await lang.get(chat_id)

    try:
        await call.stop(chat_id)
        await query.edit_message_text(
            _lang.get("stopped", "Playback stopped.\n\nBy: {0}").format(query.from_user.mention),
            disable_web_page_preview=True
        )
    except Exception as ex:
        await query.answer(f"Error: {ex}", show_alert=True)


@app.on_callback_query(filters.regex(r"^queue_(\d+)(?:_(\d+))?"))
async def cb_queue(client, query: types.CallbackQuery):
    """Handle queue pagination callback."""
    chat_id = int(query.matches[0].group(1))
    page = int(query.matches[0].group(2) or 1)
    _lang = await lang.get(chat_id)

    items, current_page, total_pages = await queue.get_queue_page(chat_id, page)

    if not items:
        return await query.edit_message_text(
            _lang.get("queue_empty", "Queue is empty."),
            disable_web_page_preview=True
        )

    text = _lang.get("queue_title", "Current Queue ({0} tracks)").format(queue.length(chat_id)) + "\n\n"

    for idx, media in enumerate(items, start=(page - 1) * 10 + 1):
        current = "▶️ " if idx == queue.position(chat_id) else f"{idx}. "
        text += f"{current}{media.get('title', 'Unknown')[:35]} [{media.get('duration', '0:00')}]\n"

    if queue.length(chat_id) > 10:
        text += f"\n... and {queue.length(chat_id) - 10} more"

    from arc.helpers.buttons import queue_keyboard
    await query.edit_message_text(
        text,
        reply_markup=queue_keyboard(chat_id, current_page, total_pages),
        disable_web_page_preview=True
    )


@app.on_callback_query(filters.regex(r"^close_(\d+)"))
async def cb_close(client, query: types.CallbackQuery):
    """Handle close callback."""
    try:
        await query.message.delete()
    except Exception:
        pass


@app.on_callback_query(filters.regex(r"^shuffle_(\d+)"))
async def cb_shuffle(client, query: types.CallbackQuery):
    """Handle shuffle callback."""
    chat_id = int(query.matches[0].group(1))
    queue.shuffle(chat_id)
    await query.answer(f"Queue shuffled by {query.from_user.mention}!")
