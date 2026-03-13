"""
Database Module for Arc Music Bot
MongoDB handler for persistent storage

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

from random import randint
from time import time
from pymongo import AsyncMongoClient

from arc.core.config import config
from arc.core.logging import LOGGER


class Database:
    """MongoDB handler for persistent storage."""

    def __init__(self):
        # Primary Database
        self.mongo = AsyncMongoClient(config.MONGO_URL, serverSelectionTimeoutMS=15000)
        self.db = self.mongo[config.DB_NAME]

        # Secondary Media Database
        self.media_mongo = None
        self.mediadb = None
        if config.DB_URI:
            self.media_mongo = AsyncMongoClient(config.DB_URI, serverSelectionTimeoutMS=15000)
            self.mediadb = self.media_mongo["arcapi"]["medias"]

        # Collections
        self.cache = self.db.cache
        self.assistantdb = self.db.assistant
        self.authdb = self.db.auth
        self.chatsdb = self.db.chats
        self.langdb = self.db.lang
        self.usersdb = self.db.users
        self.queuedb = self.db.queue
        self.settingsdb = self.db.settings

        # In-memory caches
        self.admin_list = {}
        self.active_calls = {}
        self.admin_play = []
        self.blacklisted = []
        self.cmd_delete = []
        self.loop = {}
        self.notified = []
        self.auth = {}
        self.assistant = {}
        self.chats = []
        self.lang = {}
        self.users = []

    async def connect(self):
        """Connect to MongoDB."""
        logger = LOGGER(__name__)
        try:
            start = time()
            await self.mongo.admin.command("ping")
            logger.info(f"Primary Database connected ({time() - start:.2f}s)")

            if self.media_mongo:
                start_media = time()
                await self.media_mongo.admin.command("ping")
                logger.info(f"Media Database connected ({time() - start_media:.2f}s)")

            await self.load_cache()

        except Exception as ex:
            raise SystemExit(f"Database connection failed: {type(ex).__name__}") from ex

    async def close(self):
        """Close database connections."""
        await self.mongo.close()
        if self.media_mongo:
            await self.media_mongo.close()
        LOGGER(__name__).info("Database connections closed.")

    async def load_cache(self):
        """Load cached data into memory."""
        await self.get_chats()
        await self.get_users()
        await self.get_blacklisted(True)
        await self.get_logger_status()
        LOGGER(__name__).info("Database cache loaded.")

    # Media Cache
    async def get_media_id(self, track_id: str, is_video: bool = False) -> int:
        if not self.mediadb:
            return None
        doc = await self.mediadb.find_one({"track_id": track_id, "isVideo": is_video}, {"message_id": 1})
        if not doc:
            return None
        try:
            return int(doc.get("message_id"))
        except (ValueError, TypeError):
            return None

    # Call Management
    async def get_call(self, chat_id: int) -> bool:
        return chat_id in self.active_calls

    async def add_call(self, chat_id: int):
        self.active_calls[chat_id] = 1

    async def remove_call(self, chat_id: int):
        self.active_calls.pop(chat_id, None)

    async def playing(self, chat_id: int, paused: bool = None) -> bool:
        if paused is not None:
            self.active_calls[chat_id] = int(not paused)
        return bool(self.active_calls.get(chat_id, 0))

    async def get_active_calls(self) -> dict:
        return self.active_calls.copy()

    # Admin Management
    async def get_admins(self, chat_id: int, reload: bool = False) -> list:
        from arc.helpers.admins import reload_admins
        if chat_id not in self.admin_list or reload:
            self.admin_list[chat_id] = await reload_admins(chat_id)
        return self.admin_list[chat_id]

    # Loop Settings
    async def get_loop(self, chat_id: int) -> int:
        return self.loop.get(chat_id, 0)

    async def set_loop(self, chat_id: int, count: int):
        self.loop[chat_id] = count

    # Auth System
    async def _get_auth(self, chat_id: int) -> set:
        if chat_id not in self.auth:
            doc = await self.authdb.find_one({"_id": chat_id}) or {}
            self.auth[chat_id] = set(doc.get("user_ids", []))
        return self.auth[chat_id]

    async def is_auth(self, chat_id: int, user_id: int) -> bool:
        return user_id in await self._get_auth(chat_id)

    async def add_auth(self, chat_id: int, user_id: int):
        users = await self._get_auth(chat_id)
        if user_id not in users:
            users.add(user_id)
            await self.authdb.update_one(
                {"_id": chat_id},
                {"$addToSet": {"user_ids": user_id}},
                upsert=True
            )

    async def remove_auth(self, chat_id: int, user_id: int):
        users = await self._get_auth(chat_id)
        if user_id in users:
            users.discard(user_id)
            await self.authdb.update_one(
                {"_id": chat_id},
                {"$pull": {"user_ids": user_id}}
            )

    # Assistant Assignment
    async def set_assistant(self, chat_id: int) -> int:
        from arc.core import userbot
        num = randint(1, userbot.count)
        await self.assistantdb.update_one(
            {"_id": chat_id},
            {"$set": {"num": num}},
            upsert=True
        )
        self.assistant[chat_id] = num
        return num

    async def get_assistant(self, chat_id: int):
        from arc.core import call
        if chat_id not in self.assistant:
            doc = await self.assistantdb.find_one({"_id": chat_id})
            num = doc["num"] if doc else await self.set_assistant(chat_id)
            self.assistant[chat_id] = num
        return call.clients[self.assistant[chat_id] - 1]

    # Blacklist Management
    async def add_blacklist(self, chat_id: int):
        if str(chat_id).startswith("-"):
            self.blacklisted.append(chat_id)
            await self.cache.update_one(
                {"_id": "bl_chats"},
                {"$addToSet": {"chat_ids": chat_id}},
                upsert=True
            )
        else:
            await self.cache.update_one(
                {"_id": "bl_users"},
                {"$addToSet": {"user_ids": chat_id}},
                upsert=True
            )

    async def remove_blacklist(self, chat_id: int):
        if str(chat_id).startswith("-"):
            self.blacklisted.discard(chat_id)
            await self.cache.update_one(
                {"_id": "bl_chats"},
                {"$pull": {"chat_ids": chat_id}}
            )
        else:
            await self.cache.update_one(
                {"_id": "bl_users"},
                {"$pull": {"user_ids": chat_id}}
            )

    async def get_blacklisted(self, chat: bool = False) -> list:
        if chat:
            if not self.blacklisted:
                doc = await self.cache.find_one({"_id": "bl_chats"})
                self.blacklisted.extend(doc.get("chat_ids", []) if doc else [])
            return self.blacklisted

        doc = await self.cache.find_one({"_id": "bl_users"})
        return doc.get("user_ids", []) if doc else []

    # Chat Management
    async def is_chat(self, chat_id: int) -> bool:
        return chat_id in self.chats

    async def add_chat(self, chat_id: int, title: str = ""):
        if not await self.is_chat(chat_id):
            self.chats.append(chat_id)
            await self.chatsdb.insert_one({
                "_id": chat_id,
                "title": title,
                "added_at": time()
            })

    async def remove_chat(self, chat_id: int):
        if await self.is_chat(chat_id):
            self.chats.remove(chat_id)
            await self.chatsdb.delete_one({"_id": chat_id})
            await self.authdb.delete_one({"_id": chat_id})
            await self.assistantdb.delete_one({"_id": chat_id})
            await self.langdb.delete_one({"_id": chat_id})
            await self.queuedb.delete_one({"_id": chat_id})
            await self.settingsdb.delete_one({"_id": chat_id})

    async def get_chats(self) -> list:
        if not self.chats:
            self.chats.extend([chat["_id"] async for chat in self.chatsdb.find()])
        return self.chats

    async def update_chat_title(self, chat_id: int, title: str):
        await self.chatsdb.update_one(
            {"_id": chat_id},
            {"$set": {"title": title}},
            upsert=True
        )

    # Language Settings
    async def set_lang(self, chat_id: int, lang_code: str):
        await self.langdb.update_one(
            {"_id": chat_id},
            {"$set": {"lang": lang_code}},
            upsert=True
        )
        self.lang[chat_id] = lang_code

    async def get_lang(self, chat_id: int) -> str:
        if chat_id not in self.lang:
            doc = await self.langdb.find_one({"_id": chat_id})
            self.lang[chat_id] = doc["lang"] if doc else config.LANG_CODE
        return self.lang[chat_id]

    # Play Mode
    async def get_play_mode(self, chat_id: int) -> bool:
        if chat_id not in self.admin_play:
            doc = await self.chatsdb.find_one({"_id": chat_id})
            if doc and doc.get("admin_play"):
                self.admin_play.append(chat_id)
        return chat_id in self.admin_play

    async def set_play_mode(self, chat_id: int, enabled: bool):
        if enabled:
            self.admin_play.append(chat_id)
        elif chat_id in self.admin_play:
            self.admin_play.remove(chat_id)

        await self.chatsdb.update_one(
            {"_id": chat_id},
            {"$set": {"admin_play": enabled}},
            upsert=True
        )

    # Command Delete
    async def get_cmd_delete(self, chat_id: int) -> bool:
        if chat_id not in self.cmd_delete:
            doc = await self.chatsdb.find_one({"_id": chat_id})
            if doc and doc.get("cmd_delete"):
                self.cmd_delete.append(chat_id)
        return chat_id in self.cmd_delete

    async def set_cmd_delete(self, chat_id: int, enabled: bool):
        if enabled:
            self.cmd_delete.append(chat_id)
        elif chat_id in self.cmd_delete:
            self.cmd_delete.remove(chat_id)

        await self.chatsdb.update_one(
            {"_id": chat_id},
            {"$set": {"cmd_delete": enabled}},
            upsert=True
        )

    # Logger Status
    async def is_logger(self) -> bool:
        return await self.get_logger_status()

    async def get_logger_status(self) -> bool:
        doc = await self.cache.find_one({"_id": "logger"})
        if doc:
            return doc.get("status", False)
        return False

    async def set_logger(self, status: bool):
        await self.cache.update_one(
            {"_id": "logger"},
            {"$set": {"status": status}},
            upsert=True
        )

    # Sudo Management
    async def add_sudo(self, user_id: int):
        await self.cache.update_one(
            {"_id": "sudoers"},
            {"$addToSet": {"user_ids": user_id}},
            upsert=True
        )

    async def remove_sudo(self, user_id: int):
        await self.cache.update_one(
            {"_id": "sudoers"},
            {"$pull": {"user_ids": user_id}}
        )

    async def get_sudoers(self) -> list:
        doc = await self.cache.find_one({"_id": "sudoers"})
        return doc.get("user_ids", []) if doc else []

    # User Management
    async def is_user(self, user_id: int) -> bool:
        return user_id in self.users

    async def add_user(self, user_id: int):
        if not await self.is_user(user_id):
            self.users.append(user_id)
            await self.usersdb.insert_one({
                "_id": user_id,
                "added_at": time()
            })

    async def remove_user(self, user_id: int):
        if await self.is_user(user_id):
            self.users.remove(user_id)
            await self.usersdb.delete_one({"_id": user_id})

    async def get_users(self) -> list:
        if not self.users:
            self.users.extend([user["_id"] async for user in self.usersdb.find()])
        return self.users

    # Queue Operations
    async def save_queue(self, chat_id: int, queue_list: list):
        await self.queuedb.update_one(
            {"_id": chat_id},
            {"$set": {"queue": queue_list}},
            upsert=True
        )

    async def load_queue(self, chat_id: int) -> list:
        doc = await self.queuedb.find_one({"_id": chat_id})
        return doc.get("queue", []) if doc else []

    async def clear_queue_db(self, chat_id: int):
        await self.queuedb.delete_one({"_id": chat_id})

    # Database Cleanup
    async def cleanup_database(self):
        """Clean up inactive chats and users."""
        logger = LOGGER(__name__)
        logger.info("Starting database cleanup...")

        from arc.core import app
        cleaned_chats = 0
        cleaned_users = 0

        chats = await self.get_chats()
        for chat_id in chats[:]:
            try:
                member = await app.get_chat_member(chat_id, app.id)
                if member.status in ["left", "kicked"]:
                    await self.remove_chat(chat_id)
                    cleaned_chats += 1
            except Exception:
                await self.remove_chat(chat_id)
                cleaned_chats += 1

        logger.info(f"Database cleanup complete. Removed {cleaned_chats} chats, {cleaned_users} users")
        return {"chats": cleaned_chats, "users": cleaned_users}
