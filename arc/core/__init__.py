"""
Arc Music Bot Core Module
Contains all core functionality for the bot

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

from arc.core.config import Config
from arc.core.logging import LOGGER, log
from arc.core.database import Database
from arc.core.bot import Bot
from arc.core.userbot import Userbot
from arc.core.youtube import YouTube
from arc.core.api import ArcAPI
from arc.core.calls import TgCall
from arc.core.telegram import Telegram
from arc.core.queue import Queue
from arc.core.lang import Language

# Initialize logger
logger = LOGGER(__name__)

# Initialize configuration
config = Config()

# Initialize database
db = Database()

# Initialize bot
app = Bot()

# Initialize userbot
userbot = Userbot()

# Initialize YouTube handler
yt = YouTube()

# Initialize API handler
api = ArcAPI()

# Initialize call handler
call = TgCall()

# Initialize Telegram media handler
tg = Telegram()

# Initialize queue manager
queue = Queue()

# Initialize language handler
lang = Language()

__all__ = [
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
]
