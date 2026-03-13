"""
Cache Cleaner Utility for Arc Music Bot
Cleans disk cache and downloads every 12 hours
"""

import os
import asyncio
import time
from pathlib import Path

from arc.core.logging import LOGGER


class CacheCleaner:
    """
    Automatic cache and download cleaner.
    Runs every 12 hours to clean old files.
    """

    def __init__(self):
        self.interval = 12 * 60 * 60  # 12 hours
        self.max_age = 24 * 60 * 60  # 24 hours
        self.cache_dir = Path("cache")
        self.download_dir = Path("download")

    async def start(self):
        """Start the periodic cleanup task."""
        logger = LOGGER(__name__)
        logger.info("Cache cleaner started")

        while True:
            await asyncio.sleep(self.interval)
            await self.cleanup()

    async def cleanup(self):
        """Clean up old files in cache and download directories."""
        logger = LOGGER(__name__)
        logger.info("Starting cache cleanup...")

        cleaned = {
            "cache": 0,
            "downloads": 0,
            "total_size": 0
        }

        current_time = time.time()

        # Clean cache directory
        if self.cache_dir.exists():
            for file in self.cache_dir.iterdir():
                if file.is_file():
                    file_age = current_time - file.stat().st_mtime
                    if file_age > self.max_age:
                        try:
                            size = file.stat().st_size
                            file.unlink()
                            cleaned["cache"] += 1
                            cleaned["total_size"] += size
                        except Exception as ex:
                            logger.error(f"Failed to delete {file}: {ex}")

        # Clean download directory
        if self.download_dir.exists():
            for file in self.download_dir.iterdir():
                if file.is_file():
                    file_age = current_time - file.stat().st_mtime
                    if file_age > self.max_age:
                        try:
                            size = file.stat().st_size
                            file.unlink()
                            cleaned["downloads"] += 1
                            cleaned["total_size"] += size
                        except Exception as ex:
                            logger.error(f"Failed to delete {file}: {ex}")

        # Log cleanup results
        size_mb = cleaned["total_size"] / (1024 * 1024)
        logger.info(
            f"Cache cleanup complete. "
            f"Cache files: {cleaned['cache']}, "
            f"Downloads: {cleaned['downloads']}, "
            f"Freed: {size_mb:.2f} MB"
        )

        return cleaned

    async def force_cleanup(self):
        """Force immediate cleanup."""
        return await self.cleanup()

    def get_disk_usage(self) -> dict:
        """Get disk usage of cache directories."""
        usage = {
            "cache": {"files": 0, "size": 0},
            "downloads": {"files": 0, "size": 0}
        }

        for name, directory in [("cache", self.cache_dir), ("downloads", self.download_dir)]:
            if directory.exists():
                for file in directory.iterdir():
                    if file.is_file():
                        usage[name]["files"] += 1
                        usage[name]["size"] += file.stat().st_size

        # Convert to MB
        usage["cache"]["size_mb"] = usage["cache"]["size"] / (1024 * 1024)
        usage["downloads"]["size_mb"] = usage["downloads"]["size"] / (1024 * 1024)

        return usage
