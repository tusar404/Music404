"""
Language/i18n Module for Arc Music Bot
Multi-language support for bot messages

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

import json
from pathlib import Path
from typing import Optional


class Language:
    """
    Language handler for internationalization support.
    Loads language files and provides translations.
    """

    def __init__(self):
        self.lang_dir = Path("arc/languages")
        self.lang_dir.mkdir(parents=True, exist_ok=True)

        self._cache: dict = {}
        self._default_lang = "en"

        # Default English translations
        self._default_strings = {
            # Now Playing
            "now_playing": "<b>Now Playing</b>\n\nTitle: <a href='{0}'>{1}</a>\nDuration: {2}\nRequested by: {3}",

            # Play commands
            "play_next": "<i>Playing next track...</i>",
            "play_again": "<i>Replaying current track...</i>",
            "play_added": "<b>Added to queue</b>\n\nTitle: {0}\nPosition: {1}",
            "play_searching": "<i>Searching for:</i> <code>{0}</code>",
            "play_downloading": "<i>Downloading...</i>",
            "play_no_results": "No results found for: <code>{0}</code>",

            # Queue commands
            "queue_empty": "<b>Queue is empty</b>",
            "queue_title": "<b>Current Queue</b> ({0} tracks)",
            "queue_item": "{0}. {1} [{2}]",
            "queue_current": ">> {0}. {1} [{2}] <i>(Now Playing)</i>",

            # Status messages
            "paused": "<b>Playback Paused</b>",
            "resumed": "<b>Playback Resumed</b>",
            "skipped": "<b>Skipped</b> to next track",
            "stopped": "<b>Playback Stopped</b>\nLeft the voice chat.",
            "shuffled": "<b>Queue Shuffled</b>",

            # Error messages
            "error_no_call": "<b>No active voice chat found.</b>\nPlease start a voice chat first!",
            "error_no_file": "<b>File not found.</b>\nContact {0} for support.",
            "error_no_audio": "<b>Could not extract audio from file.</b>",
            "error_tg_server": "<b>Telegram server error.</b>\nTry again later.",
            "error_rtmp": "<b>RTMP streaming is not supported.</b>",
            "error_generic": "<b>Error:</b> {0}",
            "error_not_admin": "<b>You need to be an admin to use this command.</b>",
            "error_auth": "<b>You are not authorized to use this command.</b>",
            "error_blacklisted": "<b>This chat/user is blacklisted.</b>",
            "error_maintenance": "<b>Bot is under maintenance.</b>\nPlease try again later.",
            "error_anonymous": "<b>You appear to be anonymous!</b>\n\nTo use this bot, please disable anonymous mode:\n"
                "1. Click on your profile picture in the chat\n"
                "2. Select 'Show Profile' or disable 'Remain Anonymous'\n"
                "3. Then use the command again",
            "error_bot_permissions": "<b>Bot lacks required permissions!</b>\n\n"
                "The bot needs the following permissions:\n"
                "- Manage Voice Chats\n"
                "- Invite Users via Link\n"
                "- Delete Messages\n\n"
                "Please grant these permissions to continue.",

            # Download messages
            "dl_progress": "<b>Downloading...</b>\n\nProgress: {0} / {1}\nPercentage: {2}%\nSpeed: {3}/s\nETA: {4}",
            "dl_complete": "<b>Download complete</b> in {0}s",
            "dl_cancel": "<b>Download cancelled</b> by {0}",
            "dl_limit": "<b>File size exceeds 200MB limit.</b>",
            "dl_active": "<i>This file is already being downloaded...</i>",
            "dl_not_found": "No active download found.",
            "dl_error": "<b>Download failed:</b> {0}",

            # Duration limit
            "play_duration_limit": "<b>Duration limit exceeded.</b>\nMaximum: {0} minutes",

            # Admin commands
            "admin_auth_added": "<b>User authorized:</b> {0}",
            "admin_auth_removed": "<b>User unauthorized:</b> {0}",
            "admin_mode_on": "<b>Admin-only mode enabled.</b>\nOnly admins can play music.",
            "admin_mode_off": "<b>Admin-only mode disabled.</b>\nEveryone can play music.",
            "admin_cmd_delete_on": "<b>Auto-delete commands enabled.</b>",
            "admin_cmd_delete_off": "<b>Auto-delete commands disabled.</b>",

            # Thumbnail toggle
            "thumbnail_on": "<b>Thumbnails enabled.</b>",
            "thumbnail_off": "<b>Thumbnails disabled.</b>",

            # Sudo commands
            "sudo_added": "<b>Sudo user added:</b> {0}",
            "sudo_removed": "<b>Sudo user removed:</b> {0}",
            "blacklist_added": "<b>Blacklisted:</b> {0}",
            "blacklist_removed": "<b>Unblacklisted:</b> {0}",
            "maintenance_on": "<b>Maintenance mode enabled.</b>\nBot will only respond to sudo users.",
            "maintenance_off": "<b>Maintenance mode disabled.</b>\nBot is now available to everyone.",

            # Active calls
            "active_calls_title": "<b>Active Voice Chats</b> ({0})",
            "active_calls_item": "{0}. {1} (ID: <code>{2}</code>)",

            # Playlist
            "playlist_added": "<b>Playlist added:</b> {0} tracks",
            "playlist_limit": "<b>Playlist limited to {0} tracks.</b>",

            # Misc
            "ping": "<b>Pong!</b>\nPing: {0}ms",
            "lang_set": "<b>Language set to:</b> {0}",
            "cancel": "Cancel",

            # Start and Help
            "start_pm": (
                "<b>Welcome to {0}!</b>\n\n"
                "I can play music and videos in your Telegram voice chats.\n\n"
                "<b>Features:</b>\n"
                "- Play audio from YouTube\n"
                "- Play video from YouTube\n"
                "- Support for Telegram media files\n"
                "- Queue management\n"
                "- Playlist support\n\n"
                "<b>Add me to a group and use</b> <code>/play</code> <b>to start!</b>"
            ),
            "help_text": (
                "<b>Arc Music Bot - Commands</b>\n\n"
                "<b>Music Commands:</b>\n"
                "/play [song/url] - Play audio\n"
                "/vplay [video/url] - Play video\n"
                "/pause - Pause playback\n"
                "/resume - Resume playback\n"
                "/skip - Skip current track\n"
                "/stop - Stop and leave VC\n\n"
                "<b>Queue Commands:</b>\n"
                "/queue - View queue\n"
                "/now - Now playing\n"
                "/clear - Clear queue\n\n"
                "<b>Settings:</b>\n"
                "/auth [user] - Authorize user\n"
                "/adminmode - Toggle admin-only\n"
                "/thumbnail - Toggle thumbnails"
            ),
        }

        # Create default language file if not exists
        self._create_default_lang_file()

    def _create_default_lang_file(self):
        """Create the default English language file."""
        lang_file = self.lang_dir / "en.json"
        if not lang_file.exists():
            with open(lang_file, "w", encoding="utf-8") as f:
                json.dump(self._default_strings, f, indent=2, ensure_ascii=False)

    def load(self, lang_code: str) -> dict:
        """Load a language file."""
        if lang_code in self._cache:
            return self._cache[lang_code]

        lang_file = self.lang_dir / f"{lang_code}.json"

        if lang_file.exists():
            try:
                with open(lang_file, "r", encoding="utf-8") as f:
                    strings = json.load(f)
                merged = {**self._default_strings, **strings}
                self._cache[lang_code] = merged
                return merged
            except Exception:
                pass

        return self._default_strings

    async def get(self, chat_id: int) -> dict:
        """Get language strings for a chat."""
        from arc.core import db
        lang_code = await db.get_lang(chat_id)
        return self.load(lang_code)

    def get_string(self, lang_code: str, key: str, *args) -> str:
        """Get a translated string with formatting."""
        strings = self.load(lang_code)
        template = strings.get(key, self._default_strings.get(key, key))

        if args:
            try:
                return template.format(*args)
            except (IndexError, KeyError):
                return template

        return template

    async def set_chat_lang(self, chat_id: int, lang_code: str) -> bool:
        """Set language for a chat."""
        from arc.core import db
        lang_file = self.lang_dir / f"{lang_code}.json"
        if not lang_file.exists():
            return False

        await db.set_lang(chat_id, lang_code)
        return True

    def list_languages(self) -> list:
        """Get list of available language codes."""
        languages = []
        for file in self.lang_dir.glob("*.json"):
            languages.append(file.stem)
        return sorted(languages)
