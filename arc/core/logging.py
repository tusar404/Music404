"""
Logging Module for Arc Music Bot
Provides colored console logging with file support and Telegram logger

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


class ColorFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""

    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[41m",
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        record.msg = f"{color}{record.msg}{self.RESET}"
        return super().format(record)


def LOGGER(name: str) -> logging.Logger:
    """
    Create and configure a logger instance.

    Args:
        name: The name for the logger (usually __name__)

    Returns:
        A configured Logger instance
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Console Handler with Color
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = ColorFormatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File Handler for error logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    file_handler = logging.FileHandler(
        log_dir / f"arc_music_{datetime.now().strftime('%Y%m%d')}.log",
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    return logger


class TelegramLogger:
    """
    Sends logs to Telegram logger group.
    """

    def __init__(self):
        self.app = None
        self.logger_id = None
        self.enabled = False

    def setup(self, app, logger_id: int, enabled: bool = True):
        """Setup the Telegram logger."""
        self.app = app
        self.logger_id = logger_id
        self.enabled = enabled

    async def log(self, text: str, parse_mode: str = "html"):
        """Send a log message to the logger group."""
        if not self.enabled or not self.app or not self.logger_id:
            return

        try:
            await self.app.send_message(
                self.logger_id,
                text,
                parse_mode=parse_mode,
                disable_web_page_preview=True
            )
        except Exception:
            pass

    async def log_user_start(self, user):
        """Log when a new user starts the bot in PM."""
        text = (
            f"#NewUser\n\n"
            f"User: {user.mention}\n"
            f"ID: <code>{user.id}</code>\n"
            f"Username: @{user.username if user.username else 'None'}"
        )
        await self.log(text)

    async def log_bot_added(self, chat):
        """Log when bot is added to a new group."""
        text = (
            f"#NewChat\n\n"
            f"Chat: {chat.title}\n"
            f"ID: <code>{chat.id}</code>\n"
            f"Type: {chat.type}\n"
            f"Members: {chat.members_count if hasattr(chat, 'members_count') else 'Unknown'}"
        )
        await self.log(text)

    async def log_play(self, chat_id: int, chat_title: str, user, track_title: str, track_url: str):
        """Log when a track is played."""
        text = (
            f"#Play\n\n"
            f"Chat: {chat_title}\n"
            f"Chat ID: <code>{chat_id}</code>\n"
            f"User: {user.mention if hasattr(user, 'mention') else user}\n"
            f"Track: <a href='{track_url}'>{track_title}</a>"
        )
        await self.log(text)

    async def log_bot_left(self, chat_id: int, chat_title: str, reason: str):
        """Log when bot leaves a chat."""
        text = (
            f"#BotLeft\n\n"
            f"Chat: {chat_title}\n"
            f"Chat ID: <code>{chat_id}</code>\n"
            f"Reason: {reason}"
        )
        await self.log(text)

    async def log_assistant_banned(self, assistant_id: int, assistant_name: str, chat_id: int, chat_title: str):
        """Log when assistant is banned in a chat."""
        text = (
            f"#AssistantBanned\n\n"
            f"Assistant: {assistant_name}\n"
            f"Assistant ID: <code>{assistant_id}</code>\n"
            f"Chat: {chat_title}\n"
            f"Chat ID: <code>{chat_id}</code>"
        )
        await self.log(text)

    async def log_permission_issue(self, chat_id: int, chat_title: str, issue: str):
        """Log permission issues."""
        text = (
            f"#PermissionIssue\n\n"
            f"Chat: {chat_title}\n"
            f"Chat ID: <code>{chat_id}</code>\n"
            f"Issue: {issue}"
        )
        await self.log(text)

    async def log_maintenance(self, enabled: bool, by_user):
        """Log maintenance mode toggle."""
        status = "Enabled" if enabled else "Disabled"
        text = (
            f"#Maintenance\n\n"
            f"Status: {status}\n"
            f"By: {by_user.mention if hasattr(by_user, 'mention') else by_user}"
        )
        await self.log(text)


# Global instances
log = LOGGER("ArcMusic")
tg_log = TelegramLogger()
