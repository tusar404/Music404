"""
Arc Music Bot Core Module
Contains all core functionality for the bot

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

# Import config first (no dependencies on other arc modules)
from arc.core.config import Config, config

# Import logging (no dependencies on other arc modules)
from arc.core.logging import LOGGER, log, tg_log

# Import queue and lang (no arc dependencies)
from arc.core.queue import Queue
from arc.core.lang import Language

# Import database (depends on config, logging)
from arc.core.database import Database

# Import bot and userbot (depend on config, logging)
from arc.core.bot import Bot
from arc.core.userbot import Userbot

# Import API and YouTube (depend on config, logging)
from arc.core.api import ArcAPI
from arc.core.youtube import YouTube

# Import calls (depends on logging, uses lazy imports for buttons)
from arc.core.calls import TgCall

# Import telegram (depends on config, logging)
from arc.core.telegram import Telegram

# Initialize logger
logger = LOGGER(__name__)

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
