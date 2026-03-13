"""
PyTgCalls Module for Arc Music Bot
"""

import asyncio
from typing import Optional

from ntgcalls import (
    ConnectionNotFound,
    TelegramServerError,
    RTMPStreamingUnsupported,
    ConnectionError as TgConnectionError
)
from pyrogram import types
from pyrogram.errors import (
    ChatSendMediaForbidden,
    ChatSendPhotosForbidden,
    MessageIdInvalid,
    UserNotParticipant,
    ChannelPrivate,
)
from pytgcalls import PyTgCalls, exceptions
from pytgcalls.pytgcalls_session import PyTgCallsSession

from arc.core import config, db, lang, queue, userbot
from arc.core.logging import LOGGER, tg_log
from arc.helpers.buttons import controls_keyboard, paused_keyboard


class TgCall:
    """PyTgCalls handler for voice chat streaming."""

    def __init__(self):
        self.clients = []
        self._app = None

    def set_app(self, app):
        self._app = app

    async def pause(self, chat_id: int) -> bool:
        client = await db.get_assistant(chat_id)
        await db.playing(chat_id, paused=True)
        return await client.pause(chat_id)

    async def resume(self, chat_id: int) -> bool:
        client = await db.get_assistant(chat_id)
        await db.playing(chat_id, paused=False)
        return await client.resume(chat_id)

    async def stop(self, chat_id: int):
        client = await db.get_assistant(chat_id)
        queue.clear(chat_id)
        await db.remove_call(chat_id)
        try:
            await client.leave_call(chat_id, close=False)
        except Exception:
            pass

    async def play_media(self, chat_id: int, message: types.Message, track: dict):
        """Play media in voice chat with buttons."""
        client = await db.get_assistant(chat_id)
        _lang = await lang.get(chat_id)

        # Check global thumbnail setting (dev toggle)
        thumb_path = None
        if config.THUMBNAILS_ENABLED:
            # Check per-chat setting
            if await db.is_thumbnail_enabled(chat_id):
                if track.get("thumbnail"):
                    from arc.core.thumbnails import Thumbnail
                    thumb = Thumbnail()
                    thumb_path = await thumb.generate(track)
                elif config.DEFAULT_THUMB:
                    thumb_path = config.DEFAULT_THUMB

        if not track.get("file_path"):
            await message.edit_text(
                _lang.get("error_no_file", "File not found. Contact {0}").format(config.SUPPORT_CHAT),
                disable_web_page_preview=True
            )
            return await self.play_next(chat_id)

        stream = types.MediaStream(
            media_path=track["file_path"],
            audio_parameters=types.AudioQuality.HIGH,
            video_parameters=types.VideoQuality.HD_720p,
            audio_flags=types.MediaStream.Flags.REQUIRED,
            video_flags=(
                types.MediaStream.Flags.AUTO_DETECT
                if track.get("video")
                else types.MediaStream.Flags.IGNORE
            ),
        )

        try:
            await client.play(
                chat_id=chat_id,
                stream=stream,
                config=types.GroupCallConfig(auto_start=False),
            )

            await db.add_call(chat_id)

            if self._app:
                self._app.update_activity(chat_id)

            # Build YouTube URL
            video_id = track.get("id", "")
            track_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else (track.get("url", ""))

            # Format now playing message
            text = _lang.get("now_playing", 
                "<b>Now Playing</b>\n\nTitle: <a href='{0}'>{1}</a>\nDuration: {2}\nRequested by: {3}"
            ).format(
                track_url,
                track.get("title", "Unknown")[:50],
                track.get("duration", "0:00"),
                track.get("user", "Unknown")
            )

            keyboard = controls_keyboard(chat_id)

            # Send/update with thumbnail
            try:
                if thumb_path:
                    await message.edit_media(
                        media=types.InputMediaPhoto(
                            media=thumb_path,
                            caption=text,
                        ),
                        reply_markup=keyboard,
                    )
                else:
                    await message.edit_text(text, reply_markup=keyboard, disable_web_page_preview=True)
            except (ChatSendMediaForbidden, ChatSendPhotosForbidden, MessageIdInvalid):
                if thumb_path:
                    sent = await self._app.send_photo(
                        chat_id=chat_id,
                        photo=thumb_path,
                        caption=text,
                        reply_markup=keyboard,
                    )
                else:
                    sent = await self._app.send_message(
                        chat_id=chat_id,
                        text=text,
                        reply_markup=keyboard,
                        disable_web_page_preview=True,
                    )
                track["message_id"] = sent.id

            # Log play
            try:
                chat = await self._app.get_chat(chat_id)
                await tg_log.log_play(
                    chat_id,
                    chat.title if chat else str(chat_id),
                    track.get("user", "Unknown"),
                    track.get("title", "Unknown"),
                    track_url
                )
            except Exception:
                pass

        except exceptions.NoActiveGroupCall:
            await self.stop(chat_id)
            await message.edit_text(
                _lang.get("error_no_call", "No active voice chat. Start one first."),
                disable_web_page_preview=True
            )

        except exceptions.NoAudioSourceFound:
            await message.edit_text(
                _lang.get("error_no_audio", "Could not extract audio."),
                disable_web_page_preview=True
            )
            await self.play_next(chat_id)

        except (TgConnectionError, ConnectionNotFound, TelegramServerError):
            await self.stop(chat_id)
            await message.edit_text(
                _lang.get("error_tg_server", "Telegram server error. Try again later."),
                disable_web_page_preview=True
            )

        except RTMPStreamingUnsupported:
            await self.stop(chat_id)
            await message.edit_text(
                _lang.get("error_rtmp", "RTMP streaming not supported."),
                disable_web_page_preview=True
            )

        except Exception as ex:
            LOGGER(__name__).error(f"Play error: {ex}")
            await self.stop(chat_id)
            await message.edit_text(
                _lang.get("error_generic", "Error: {0}").format(str(ex)),
                disable_web_page_preview=True
            )

    async def play_next(self, chat_id: int):
        """Play next track (don't delete command)."""
        media = queue.get_next(chat_id)

        # Delete previous playing message only
        if media and media.get("message_id"):
            try:
                await self._app.delete_messages(chat_id, media["message_id"])
            except Exception:
                pass

        if not media:
            return await self.stop(chat_id)

        _lang = await lang.get(chat_id)
        msg = await self._app.send_message(
            chat_id=chat_id,
            text=_lang.get("play_next", "Playing next track..."),
            disable_web_page_preview=True
        )

        if not media.get("file_path"):
            from arc.core import yt
            media["file_path"] = await yt.download(media.get("id"), video=media.get("video"))
            if not media["file_path"]:
                await self.stop(chat_id)
                return await msg.edit_text(
                    _lang.get("error_no_file", "Download failed.").format(config.SUPPORT_CHAT),
                    disable_web_page_preview=True
                )

        media["message_id"] = msg.id
        await self.play_media(chat_id, msg, media)

    async def ping(self) -> float:
        if not self.clients:
            return 0.0
        pings = [c.ping for c in self.clients]
        return round(sum(pings) / len(pings), 2)

    async def setup_decorators(self, client: PyTgCalls):
        @client.on_update()
        async def update_handler(_, update: types.Update):
            if isinstance(update, types.StreamEnded):
                if update.stream_type == types.StreamEnded.Type.AUDIO:
                    await self.play_next(update.chat_id)
            elif isinstance(update, types.ChatUpdate):
                if update.status in [
                    types.ChatUpdate.Status.KICKED,
                    types.ChatUpdate.Status.LEFT_GROUP,
                    types.ChatUpdate.Status.CLOSED_VOICE_CHAT,
                ]:
                    await self.stop(update.chat_id)

    async def boot(self):
        PyTgCallsSession.notice_displayed = True
        logger = LOGGER(__name__)

        for idx, ub_client in enumerate(userbot.clients, start=1):
            try:
                client = PyTgCalls(ub_client, cache_duration=100)
                await client.start()
                self.clients.append(client)
                await self.setup_decorators(client)
                logger.info(f"PyTgCalls client {idx} started")
            except Exception as ex:
                logger.error(f"Failed to start PyTgCalls client {idx}: {ex}")
                raise

        logger.info(f"All {len(self.clients)} PyTgCalls client(s) started")

    async def check_assistant_status(self, chat_id: int) -> dict:
        result = {"valid": True, "banned": False, "error": None}

        try:
            client = await db.get_assistant(chat_id)
            assistant_info = userbot.get_assistant_info(db.assistant.get(chat_id, 1))

            try:
                member = await client.get_chat_member(chat_id, client.me.id)
                if member.status in ["kicked", "left"]:
                    result["valid"] = False
                    result["banned"] = member.status == "kicked"
                    result["assistant_id"] = client.me.id
                    result["assistant_name"] = assistant_info.get("mention", f"Assistant {db.assistant.get(chat_id, 1)}")
            except UserNotParticipant:
                result["valid"] = False
                result["error"] = "Assistant not in chat"
            except ChannelPrivate:
                result["valid"] = False
                result["banned"] = True
                result["assistant_id"] = client.me.id
                result["assistant_name"] = assistant_info.get("mention", f"Assistant {db.assistant.get(chat_id, 1)}")

        except Exception as ex:
            result["valid"] = False
            result["error"] = str(ex)

        return result
