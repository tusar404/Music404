"""
Userbot Module for Arc Music Bot
Manages multiple userbot assistants for voice chat functionality

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

from pyrogram import Client
from arc.core.config import config
from arc.core.logging import LOGGER


# Global lists for tracking assistants
assistants = []
assistant_ids = []
assistant_details = {}


class Userbot:
    """
    Userbot class managing multiple Pyrogram userbot instances.
    Each instance acts as an assistant for voice chat streaming.
    """

    def __init__(self):
        """Initialize userbot clients with session strings."""
        self.clients = []
        self._setup_clients()

    def _setup_clients(self):
        """Setup client instances from session strings."""
        sessions = config.session_strings

        for idx, session in enumerate(sessions, start=1):
            client = Client(
                name=f"ArcAssist{idx}",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=session,
                no_updates=True,
            )
            self.clients.append(client)

    async def start(self):
        """
        Start all configured userbot assistants.
        Each assistant joins required chats and logs startup to logger group.

        Raises:
            SystemExit: If any assistant fails to access logger group.
        """
        logger = LOGGER(__name__)
        logger.info(f"Starting {len(self.clients)} assistant(s)...")

        for idx, client in enumerate(self.clients, start=1):
            try:
                await client.start()

                # Set client attributes
                client.id = client.me.id
                client.name = client.me.first_name
                client.username = client.me.username
                client.mention = client.me.mention
                client.index = idx

                # Track assistant
                assistants.append(idx)
                assistant_ids.append(client.id)
                assistant_details[idx] = {
                    "id": client.id,
                    "name": client.name,
                    "username": client.username,
                    "mention": client.mention,
                }

                # Join support chat
                try:
                    await client.join_chat("ArcUpdates")
                except Exception:
                    pass

                # Log to logger group
                try:
                    await client.send_message(
                        config.LOGGER_ID,
                        f"<b>Assistant {idx} Started</b>\n"
                        f"Name: {client.mention}\n"
                        f"ID: <code>{client.id}</code>"
                    )
                except Exception as ex:
                    logger.error(
                        f"Assistant {idx} failed to access logger group: {ex}"
                    )
                    raise SystemExit(
                        f"Assistant {idx} cannot access logger group.\n"
                        "Make sure the assistant is added and promoted as admin!"
                    )

                logger.info(f"Assistant {idx} started as @{client.username}")

            except Exception as ex:
                logger.error(f"Failed to start assistant {idx}: {ex}")
                raise

    async def stop(self):
        """Stop all userbot assistants gracefully."""
        logger = LOGGER(__name__)
        logger.info("Stopping all assistants...")

        for idx, client in enumerate(self.clients, start=1):
            try:
                await client.stop()
                logger.info(f"Assistant {idx} stopped.")
            except Exception:
                pass

    def get_client(self, index: int) -> Client:
        """
        Get a specific client by index (1-based).

        Args:
            index: The 1-based index of the client

        Returns:
            The Pyrogram Client instance

        Raises:
            IndexError: If index is out of range
        """
        if 1 <= index <= len(self.clients):
            return self.clients[index - 1]
        raise IndexError(f"Assistant index {index} out of range")

    def get_random_client(self) -> Client:
        """Get a random assistant client."""
        import random
        return random.choice(self.clients)

    def get_client_by_id(self, user_id: int) -> Client:
        """Get client by user ID."""
        for idx, uid in enumerate(assistant_ids):
            if uid == user_id:
                return self.clients[idx]
        return None

    @property
    def count(self) -> int:
        """Return the number of active assistants."""
        return len(self.clients)

    def get_assistant_info(self, index: int) -> dict:
        """Get assistant info by index."""
        return assistant_details.get(index, {})
