"""
Bot Client Module for Arc Music Bot
Main Pyrogram bot client for handling commands and messages

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

import pyrogram
from pyrogram import enums, types, filters

from arc.core.config import config
from arc.core.logging import LOGGER


class Bot(pyrogram.Client):
    """
    Main Bot Client class extending Pyrogram Client.
    Handles bot initialization, startup, and shutdown procedures.
    """

    def __init__(self):
        super().__init__(
            name="ArcBot",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            parse_mode=enums.ParseMode.HTML,
            max_concurrent_transmissions=7,
            workdir=".",
            plugins=dict(root="arc.plugins"),
        )

        # Bot attributes
        self.owner = config.OWNER_ID
        self.logger_group = config.LOGGER_ID

        # Filter sets
        self.sudoers = pyrogram.filters.user(self.owner)
        self.bl_users = pyrogram.filters.user()

        # Track active chats
        self.active_chats: set = set()

        # Track last activity for auto-leave
        self.last_activity: dict = {}

    async def boot(self):
        """
        Start the bot and perform initial setup.
        Verifies access to logger group and admin status.

        Raises:
            SystemExit: If bot fails to access logger group or isn't admin.
        """
        await super().start()

        # Set bot attributes
        self.id = self.me.id
        self.name = self.me.first_name
        self.username = self.me.username
        self.mention = self.me.mention

        logger = LOGGER(__name__)
        logger.info(f"Bot starting as @{self.username} (ID: {self.id})")

        # Verify logger group access
        try:
            await self.send_message(
                self.logger_group,
                f"<b>Arc Music Bot Started</b>\n\n"
                f"Bot: {self.mention}\n"
                f"ID: <code>{self.id}</code>\n"
                f"Owner: <code>{self.owner}</code>"
            )
            member = await self.get_chat_member(self.logger_group, self.id)
        except Exception as ex:
            raise SystemExit(
                f"Bot failed to access logger group: {self.logger_group}\n"
                f"Reason: {ex}"
            )

        # Verify admin status in logger group
        if member.status != enums.ChatMemberStatus.ADMINISTRATOR:
            raise SystemExit(
                "Bot must be an administrator in the logger group!\n"
                "Please promote the bot and try again."
            )

        logger.info(f"Bot successfully started as @{self.username}")

    async def exit(self):
        """Gracefully stop the bot."""
        try:
            await self.send_message(
                self.logger_group,
                "<b>Arc Music Bot Stopped</b>"
            )
        except Exception:
            pass

        await super().stop()
        LOGGER(__name__).info("Bot stopped.")

    async def is_sudo(self, user_id: int) -> bool:
        """Check if user is a sudo user."""
        if user_id == self.owner:
            return True
        from arc.core import db
        sudoers = await db.get_sudoers()
        return user_id in sudoers

    async def is_blacklisted(self, user_id: int) -> bool:
        """Check if user is blacklisted."""
        from arc.core import db
        return user_id in await db.get_blacklisted()

    async def add_active_chat(self, chat_id: int):
        """Add chat to active chats set."""
        self.active_chats.add(chat_id)

    async def remove_active_chat(self, chat_id: int):
        """Remove chat from active chats set."""
        self.active_chats.discard(chat_id)

    async def is_active_chat(self, chat_id: int) -> bool:
        """Check if chat is active."""
        return chat_id in self.active_chats

    def update_activity(self, chat_id: int):
        """Update last activity timestamp for a chat."""
        import time
        self.last_activity[chat_id] = time.time()

    def get_last_activity(self, chat_id: int) -> float:
        """Get last activity timestamp for a chat."""
        return self.last_activity.get(chat_id, 0)
