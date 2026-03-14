"""
Arc Music Bot Core Module
Contains all core functionality for the bot

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

# ============== FIRST: Import config and logging (no arc dependencies) ==============
from arc.core.config import Config, config
from arc.core.logging import LOGGER, log, tg_log

# ============== SECOND: Import modules with no arc dependencies ==============
from arc.core.queue import Queue
from arc.core.lang import Language

# ============== THIRD: Import modules that only depend on config/logging ==============
from arc.core.database import Database
from arc.core.bot import Bot
from arc.core.userbot import Userbot
from arc.core.api import ArcAPI

# ============== FOURTH: Import modules with lazy imports or helpers dependencies ==============
# These use lazy imports internally to avoid circular dependencies
from arc.core.youtube import YouTube
from arc.core.calls import TgCall
from arc.core.telegram import Telegram

# ============== Initialize logger ==============
logger = LOGGER(__name__)

# ============== Initialize instances ==============
db = Database()
app = Bot()
userbot = Userbot()
yt = YouTube()
api = ArcAPI()
call = TgCall()
tg = Telegram()
queue = Queue()
lang = Language()

__all__ = [
    "Config",
    "config",
    "db",
    "app",
    "userbot",
    "yt",
    "api",
    "call",
    "tg",
    "queue",
    "lang",
    "logger",
    "LOGGER",
    "log",
    "tg_log",
]
