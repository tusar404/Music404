"""
Configuration Module for Arc Music Bot

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class for all environment variables."""

    def __init__(self):
        # Telegram API
        self.API_ID: int = int(os.getenv("API_ID", "0"))
        self.API_HASH: str = os.getenv("API_HASH", "")

        # Bot Token
        self.BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

        # Userbot Sessions (at least 1 required)
        self.STRING1: str = os.getenv("STRING1", "")
        self.STRING2: str = os.getenv("STRING2", "")
        self.STRING3: str = os.getenv("STRING3", "")
        self.STRING4: str = os.getenv("STRING4", "")
        self.STRING5: str = os.getenv("STRING5", "")

        # MongoDB
        self.MONGO_URL: str = os.getenv("MONGO_URL", "")
        self.DB_NAME: str = os.getenv("DB_NAME", "ArcMusic")
        self.DB_URI: str = os.getenv("DB_URI", "")  # Secondary database for media

        # Owner & Logger
        self.OWNER_ID: int = int(os.getenv("OWNER_ID", "0"))
        self.LOGGER_ID: int = int(os.getenv("LOGGER_ID", "0"))

        # External API (deadlinetech.site)
        self.API_URL: str = os.getenv("API_URL", "")
        self.API_KEY: str = os.getenv("API_KEY", "")

        # Media Channel
        self.MEDIA_CHANNEL_ID: str = os.getenv("MEDIA_CHANNEL_ID", "")

        # Bot Settings
        self.DURATION_LIMIT: int = int(os.getenv("DURATION_LIMIT", "5400"))  # 90 minutes
        self.QUEUE_LIMIT: int = int(os.getenv("QUEUE_LIMIT", "50"))  # Max tracks in queue
        self.LANG_CODE: str = os.getenv("LANG_CODE", "en")

        # Support Info
        self.SUPPORT_CHAT: str = os.getenv("SUPPORT_CHAT", "@ArcUpdates")
        self.UPDATES_CHANNEL: str = os.getenv("UPDATES_CHANNEL", "@ArcUpdates")
        self.SOURCE_CODE: str = os.getenv("SOURCE_CODE", "https://github.com/TeamArc/ArcMusicBot")

        # Feature Toggles (Developer Settings)
        self.THUMBNAILS_ENABLED: bool = os.getenv("THUMBNAILS_ENABLED", "True").lower() == "true"
        self.AUTO_LEAVE: bool = os.getenv("AUTO_LEAVE", "True").lower() == "true"
        self.AUTO_LEAVE_TIME: int = int(os.getenv("AUTO_LEAVE_TIME", "7200"))  # 2 hours

        # Paths
        self.DEFAULT_THUMB: str = "arc/assets/default_thumb.jpg"

        # Spotify (optional)
        self.SPOTIFY_CLIENT_ID: str = os.getenv("SPOTIFY_CLIENT_ID", "")
        self.SPOTIFY_CLIENT_SECRET: str = os.getenv("SPOTIFY_CLIENT_SECRET", "")

        # Cookies
        self.COOKIE_URLS: list = []
        if os.getenv("COOKIE_URLS", ""):
            self.COOKIE_URLS = [u.strip() for u in os.getenv("COOKIE_URLS").split(",")]

        # Maintenance Mode
        self.MAINTENANCE_MODE: bool = False

    def validate(self) -> bool:
        """Validate required configuration."""
        required = [
            ("API_ID", self.API_ID),
            ("API_HASH", self.API_HASH),
            ("BOT_TOKEN", self.BOT_TOKEN),
            ("MONGO_URL", self.MONGO_URL),
            ("OWNER_ID", self.OWNER_ID),
            ("LOGGER_ID", self.LOGGER_ID),
        ]

        missing = [n for n, v in required if not v]
        if missing:
            for n in missing:
                print(f"ERROR: {n} not set!")
            return False

        sessions = [self.STRING1, self.STRING2, self.STRING3, self.STRING4, self.STRING5]
        if not any(sessions):
            print("ERROR: At least one STRING session required!")
            return False

        return True

    @property
    def session_strings(self) -> list:
        """Get list of session strings."""
        return [s for s in [self.STRING1, self.STRING2, self.STRING3, self.STRING4, self.STRING5] if s]

    @property
    def assistant_count(self) -> int:
        """Get number of assistants."""
        return len(self.session_strings)

    def set_maintenance(self, status: bool):
        """Set maintenance mode status."""
        self.MAINTENANCE_MODE = status


# Create config instance at module level
# This allows other modules to import config directly
config = Config()
