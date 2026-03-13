"""
Telegram Media Module for Arc Music Bot
Handles downloading and processing Telegram media files

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

import asyncio
import os
import time
from typing import Optional

from pyrogram import types

from arc.core.config import config
from arc.core.logging import LOGGER


class Telegram:
    """
    Handler for Telegram media downloads and processing.
    Supports audio, video, voice, and document files.
    """

    def __init__(self):
        self.active_downloads = []
        self.download_events = {}
        self.last_edit_time = {}
        self.edit_interval = 5

    def has_media(self, message: types.Message) -> bool:
        """Check if message contains playable media."""
        return any([
            message.video,
            message.audio,
            message.document,
            message.voice
        ])

    def get_media_type(self, message: types.Message) -> str:
        """Get the type of media in message."""
        if message.video:
            return "video"
        elif message.audio:
            return "audio"
        elif message.voice:
            return "voice"
        elif message.document:
            mime = getattr(message.document, "mime_type", "")
            if mime and mime.startswith("video/"):
                return "video"
            return "document"
        return "unknown"

    async def cancel_download(self, query: types.CallbackQuery):
        """Cancel an active download."""
        msg_id = query.message.id
        event = self.download_events.get(msg_id)

        if event:
            event.set()

        if event:
            await query.edit_message_text(
                f"Download cancelled by {query.from_user.mention}"
            )
        else:
            await query.answer("No active download found.", show_alert=True)

    async def download(
        self,
        message: types.Message,
        status_message: types.Message,
        _lang: dict = None
    ) -> Optional[dict]:
        """Download media from a Telegram message."""
        if _lang is None:
            _lang = {}

        msg_id = status_message.id
        event = asyncio.Event()
        self.download_events[msg_id] = event
        self.last_edit_time[msg_id] = 0
        start_time = time.time()

        # Get media attributes
        media = message.audio or message.voice or message.video or message.document
        file_id = getattr(media, "file_unique_id", None)
        file_name = getattr(media, "file_name", f"telegram_{file_id}")
        file_ext = file_name.split(".")[-1] if "." in file_name else "mp3"
        file_size = getattr(media, "file_size", 0)
        file_title = getattr(media, "title", None) or file_name
        duration = getattr(media, "duration", 0)

        # Determine if video
        mime_type = getattr(media, "mime_type", "")
        is_video = mime_type.startswith("video/") or bool(message.video)

        # Check duration limit
        if duration > config.DURATION_LIMIT:
            await status_message.edit_text(
                _lang.get("play_duration_limit", "Duration limit exceeded. Maximum: {0} minutes").format(config.DURATION_LIMIT // 60)
            )
            return None

        # Check file size limit (200MB)
        if file_size > 200 * 1024 * 1024:
            await status_message.edit_text(
                _lang.get("dl_limit", "File size exceeds 200MB limit.")
            )
            return None

        # Progress callback
        async def progress_callback(current: int, total: int):
            if event.is_set():
                return

            now = time.time()
            if now - self.last_edit_time[msg_id] < self.edit_interval:
                return

            self.last_edit_time[msg_id] = now
            percent = current * 100 / total
            speed = current / (now - start_time or 1e-6)

            from arc.helpers.utils import format_size, format_eta
            text = _lang.get("dl_progress", (
                "Downloading...\n\n"
                "Progress: {0} / {1}\n"
                "Percentage: {2}%\n"
                "Speed: {3}/s\n"
                "ETA: {4}"
            )).format(
                format_size(current),
                format_size(total),
                round(percent, 1),
                format_size(speed),
                format_eta(int((total - current) / speed))
            )

            try:
                await status_message.edit_text(text)
            except Exception:
                pass

        try:
            download_dir = "download"
            os.makedirs(download_dir, exist_ok=True)
            file_path = f"{download_dir}/{file_id}.{file_ext}"

            # Check if already downloaded
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                return {
                    "id": file_id,
                    "duration": time.strftime("%M:%S", time.gmtime(duration)),
                    "duration_sec": duration,
                    "file_path": file_path,
                    "message_id": status_message.id,
                    "url": message.link,
                    "title": file_title[:50],
                    "video": is_video,
                }

            # Check for duplicate downloads
            if file_id in self.active_downloads:
                await status_message.edit_text(
                    _lang.get("dl_active", "This file is already being downloaded...")
                )
                return None

            # Start download
            self.active_downloads.append(file_id)

            try:
                from arc.core import app
                await message.download(
                    file_name=file_path,
                    progress=progress_callback
                )

                elapsed = round(time.time() - start_time, 2)
                await status_message.edit_text(
                    _lang.get("dl_complete", "Download complete in {0}s").format(elapsed)
                )

            finally:
                if file_id in self.active_downloads:
                    self.active_downloads.remove(file_id)

            return {
                "id": file_id,
                "duration": time.strftime("%M:%S", time.gmtime(duration)),
                "duration_sec": duration,
                "file_path": file_path,
                "message_id": status_message.id,
                "url": message.link,
                "title": file_title[:50],
                "video": is_video,
            }

        except asyncio.CancelledError:
            return None

        except Exception as ex:
            LOGGER(__name__).error(f"Download error: {ex}")
            await status_message.edit_text(
                _lang.get("dl_error", "Download failed: {0}").format(str(ex))
            )
            return None

        finally:
            self.download_events.pop(msg_id, None)
            self.last_edit_time.pop(msg_id, None)
