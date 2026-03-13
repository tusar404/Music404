"""
Queue Management Module for Arc Music Bot
Manages playback queues for each chat

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict
import asyncio
import time


class Queue:
    """
    Queue management system for handling playback queues.
    Supports multiple chats with independent queues.
    """

    def __init__(self):
        self._queues: dict = defaultdict(list)
        self._current: dict = {}
        self._positions: dict = defaultdict(int)
        self._locks: dict = defaultdict(asyncio.Lock)

    def _get_lock(self, chat_id: int) -> asyncio.Lock:
        """Get or create lock for chat queue."""
        if chat_id not in self._locks:
            self._locks[chat_id] = asyncio.Lock()
        return self._locks[chat_id]

    def add(self, chat_id: int, media: dict, position: int = None) -> int:
        """Add media to queue."""
        if position is not None and 0 <= position < len(self._queues[chat_id]):
            self._queues[chat_id].insert(position, media)
            return position + 1
        else:
            self._queues[chat_id].append(media)
            return len(self._queues[chat_id])

    def get(self, chat_id: int, position: int) -> Optional[dict]:
        """Get media at specific position."""
        if 1 <= position <= len(self._queues[chat_id]):
            return self._queues[chat_id][position - 1]
        return None

    def get_all(self, chat_id: int) -> list:
        """Get all items in queue."""
        return self._queues[chat_id].copy()

    def get_current(self, chat_id: int) -> Optional[dict]:
        """Get currently playing media."""
        return self._current.get(chat_id)

    def set_current(self, chat_id: int, media: dict):
        """Set currently playing media."""
        self._current[chat_id] = media

    def get_next(self, chat_id: int) -> Optional[dict]:
        """Get next media in queue and advance position."""
        queue = self._queues[chat_id]
        pos = self._positions[chat_id]

        if pos >= len(queue):
            return None

        media = queue[pos]
        self._current[chat_id] = media
        self._positions[chat_id] += 1

        return media

    def get_previous(self, chat_id: int) -> Optional[dict]:
        """Get previous media in queue."""
        pos = self._positions[chat_id]
        if pos <= 1:
            return None

        self._positions[chat_id] -= 1
        return self._queues[chat_id][pos - 2]

    def skip(self, chat_id: int, count: int = 1) -> Optional[dict]:
        """Skip specified number of tracks."""
        self._positions[chat_id] += count - 1
        return self.get_next(chat_id)

    def remove(self, chat_id: int, position: int) -> Optional[dict]:
        """Remove media from queue at position."""
        if 1 <= position <= len(self._queues[chat_id]):
            removed = self._queues[chat_id].pop(position - 1)
            current_pos = self._positions[chat_id]
            if position < current_pos:
                self._positions[chat_id] -= 1
            return removed
        return None

    def clear(self, chat_id: int):
        """Clear the entire queue for a chat."""
        self._queues[chat_id] = []
        self._positions[chat_id] = 0
        self._current.pop(chat_id, None)

    def shuffle(self, chat_id: int):
        """Shuffle the queue for a chat."""
        import random
        random.shuffle(self._queues[chat_id])

    def length(self, chat_id: int) -> int:
        """Get queue length."""
        return len(self._queues[chat_id])

    def position(self, chat_id: int) -> int:
        """Get current position in queue."""
        return self._positions[chat_id]

    def remaining(self, chat_id: int) -> int:
        """Get number of remaining tracks."""
        return len(self._queues[chat_id]) - self._positions[chat_id]

    def is_empty(self, chat_id: int) -> bool:
        """Check if queue is empty."""
        return len(self._queues[chat_id]) == 0

    def has_next(self, chat_id: int) -> bool:
        """Check if there are more tracks after current."""
        return self._positions[chat_id] < len(self._queues[chat_id])

    async def get_queue_page(
        self,
        chat_id: int,
        page: int = 1,
        per_page: int = 10
    ) -> tuple:
        """Get a page of queue items."""
        queue = self._queues[chat_id]
        total = len(queue)

        if total == 0:
            return [], 1, 1

        total_pages = (total + per_page - 1) // per_page
        page = max(1, min(page, total_pages))

        start = (page - 1) * per_page
        end = start + per_page

        return queue[start:end], page, total_pages

    def get_queue_list(self, chat_id: int) -> list:
        """Get queue as list of dicts for display."""
        result = []
        current_pos = self._positions[chat_id]

        for idx, media in enumerate(self._queues[chat_id], start=1):
            result.append({
                "position": idx,
                "title": media.get("title", "Unknown"),
                "duration": media.get("duration", "0:00"),
                "user": media.get("user", "Unknown"),
                "is_current": idx == current_pos,
                "id": media.get("id", ""),
            })

        return result
