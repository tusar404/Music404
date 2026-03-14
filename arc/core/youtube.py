"""
YouTube Module for Arc Music Bot
Handles YouTube search, playlist parsing, and downloads using yt-dlp

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

import os
import re
import random
import asyncio
import aiohttp
from pathlib import Path
from typing import Optional

import yt_dlp
from py_yt import Playlist, VideosSearch

from arc.core.config import config
from arc.core.logging import LOGGER


# Timeouts
SEARCH_TIMEOUT = 10  # 10 seconds for YouTube search
DOWNLOAD_TIMEOUT = 80  # 80 seconds for downloads


def _get_to_seconds():
    """Lazy import to_seconds to avoid circular imports."""
    from arc.helpers.utils import to_seconds
    return to_seconds


class YouTube:
    """
    YouTube handler class for searching, downloading, and managing
    YouTube content for the music bot.
    """

    def __init__(self):
        self.base_url = "https://www.youtube.com/watch?v="
        self.cookies = []
        self.cookies_checked = False
        self.cookie_dir = "arc/cookies"
        self.warned_missing_cookies = False

        # YouTube URL regex pattern
        self.url_pattern = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )

    def get_cookie_file(self) -> Optional[str]:
        """
        Get a random cookie file for yt-dlp.
        Helps bypass YouTube restrictions.

        Returns:
            Path to cookie file or None if not available
        """
        if not self.cookies_checked:
            cookie_path = Path(self.cookie_dir)
            if cookie_path.exists():
                for file in cookie_path.iterdir():
                    if file.suffix == ".txt":
                        self.cookies.append(str(file))
            self.cookies_checked = True

        if not self.cookies:
            if not self.warned_missing_cookies:
                self.warned_missing_cookies = True
                LOGGER(__name__).warning("No cookie files found - downloads may fail!")
            return None

        return random.choice(self.cookies)

    async def save_cookies(self, urls: list) -> None:
        """
        Save cookie files from URL sources.

        Args:
            urls: List of URLs containing cookie data
        """
        logger = LOGGER(__name__)
        logger.info(f"Saving {len(urls)} cookie files...")

        cookie_dir = Path(self.cookie_dir)
        cookie_dir.mkdir(parents=True, exist_ok=True)

        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    name = url.split("/")[-1]
                    raw_url = f"https://batbin.me/raw/{name}"

                    async with session.get(raw_url) as resp:
                        resp.raise_for_status()
                        data = await resp.read()

                    def write_cookie():
                        with open(cookie_dir / f"{name}.txt", "wb") as f:
                            f.write(data)

                    await asyncio.to_thread(write_cookie)
                    logger.info(f"Saved cookie: {name}")

                except Exception as ex:
                    logger.error(f"Failed to save cookie from {url}: {ex}")

        # Reset cookies to rescan
        self.cookies = []
        self.cookies_checked = False
        logger.info("Cookie files saved successfully.")

    def is_valid_url(self, url: str) -> bool:
        """Check if URL is a valid YouTube URL."""
        return bool(re.match(self.url_pattern, url))

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL.

        Args:
            url: YouTube URL

        Returns:
            11-character video ID or None
        """
        try:
            if "v=" in url:
                return url.split("v=")[-1].split("&")[0]
            elif "youtu.be" in url:
                return url.split("/")[-1].split("?")[0]
            elif "shorts/" in url:
                return url.split("shorts/")[-1].split("?")[0]
        except Exception:
            pass
        return None

    def get_youtube_url(self, video_id: str) -> str:
        """Get full YouTube URL from video ID."""
        return f"https://www.youtube.com/watch?v={video_id}"

    async def search(
        self,
        query: str,
        message_id: int,
        video: bool = False
    ) -> Optional[dict]:
        """
        Search for a video on YouTube with timeout.

        Args:
            query: Search query
            message_id: Message ID for tracking
            video: Whether to return video result

        Returns:
            Track dict or None
        """
        to_seconds = _get_to_seconds()
        
        try:
            # Use asyncio.wait_for for timeout
            search = VideosSearch(query, limit=1, with_live=False)
            results = await asyncio.wait_for(
                search.next(),
                timeout=SEARCH_TIMEOUT
            )

            if results and results.get("result"):
                data = results["result"][0]
                video_id = data.get("id")
                return {
                    "id": video_id,
                    "channel_name": data.get("channel", {}).get("name", ""),
                    "duration": data.get("duration", "0:00"),
                    "duration_sec": to_seconds(data.get("duration", "0:00")),
                    "message_id": message_id,
                    "title": data.get("title", "Unknown")[:50],
                    "thumbnail": data.get("thumbnails", [{}])[-1].get("url", "").split("?")[0],
                    "url": self.get_youtube_url(video_id) if video_id else data.get("link", ""),
                    "view_count": data.get("viewCount", {}).get("short", ""),
                    "video": video,
                }

        except asyncio.TimeoutError:
            LOGGER(__name__).warning(f"YouTube search timed out for: {query}")
        except Exception as ex:
            LOGGER(__name__).error(f"YouTube search failed: {ex}")

        return None

    async def get_playlist(
        self,
        url: str,
        limit: int,
        user: str,
        video: bool = False
    ) -> list:
        """
        Parse a YouTube playlist.

        Args:
            url: Playlist URL
            limit: Maximum number of tracks
            user: User who requested
            video: Whether these are video tracks

        Returns:
            List of track dicts
        """
        to_seconds = _get_to_seconds()
        tracks = []

        try:
            playlist = await Playlist.get(url)

            for data in playlist.get("videos", [])[:limit]:
                video_id = data.get("id")
                tracks.append({
                    "id": video_id,
                    "channel_name": data.get("channel", {}).get("name", ""),
                    "duration": data.get("duration", "0:00"),
                    "duration_sec": to_seconds(data.get("duration", "0:00")),
                    "title": data.get("title", "Unknown")[:50],
                    "thumbnail": data.get("thumbnails", [{}])[-1].get("url", "").split("?")[0],
                    "url": self.get_youtube_url(video_id) if video_id else data.get("link", "").split("&list=")[0],
                    "user": user,
                    "view_count": "",
                    "video": video,
                })

            LOGGER(__name__).info(f"Parsed playlist with {len(tracks)} tracks")

        except Exception as ex:
            LOGGER(__name__).error(f"Playlist parsing failed: {ex}")

        return tracks

    async def download(
        self,
        video_id: str,
        video: bool = False
    ) -> Optional[str]:
        """
        Download a YouTube video/audio.
        Uses external API for faster downloads if configured.

        Args:
            video_id: YouTube video ID
            video: Whether to download video

        Returns:
            Path to downloaded file or None
        """
        url = self.base_url + video_id
        download_dir = Path("download")
        download_dir.mkdir(exist_ok=True)

        # Route audio to external API if configured
        if not video and config.API_URL and config.API_KEY:
            from arc.core.api import ArcAPI
            api = ArcAPI()
            file_path = await api.download_track(url, video=False)
            if file_path:
                return file_path

        # Local yt-dlp download
        ext = "mp4" if video else "webm"
        filename = download_dir / f"{video_id}.{ext}"

        # Check if already downloaded
        if filename.exists() and filename.stat().st_size > 0:
            return str(filename)

        cookie = self.get_cookie_file()

        # Base yt-dlp options
        base_opts = {
            "outtmpl": str(download_dir / "%(id)s.%(ext)s"),
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "no_warnings": True,
            "overwrites": True,
            "nocheckcertificate": True,
            "cookiefile": cookie,
            "postprocessor_args": {"ffmpeg": ["-nostdin", "-y"]},
            "source_address": "0.0.0.0",
        }

        # Format-specific options
        if video:
            ydl_opts = {
                **base_opts,
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio)",
                "merge_output_format": "mp4",
            }
        else:
            ydl_opts = {
                **base_opts,
                "format": "bestaudio[ext=webm][acodec=opus]",
            }

        def _download():
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                return str(filename)
            except yt_dlp.utils.DownloadError:
                if cookie and cookie in self.cookies:
                    self.cookies.remove(cookie)
                return None
            except Exception as ex:
                LOGGER(__name__).error(f"yt-dlp download failed: {ex}")
                return None

        return await asyncio.to_thread(_download)

    async def get_info(self, url: str) -> Optional[dict]:
        """
        Get video information without downloading.

        Args:
            url: YouTube URL

        Returns:
            Video info dict or None
        """
        cookie = self.get_cookie_file()

        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "cookiefile": cookie,
        }

        def _extract():
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    return ydl.extract_info(url, download=False)
            except Exception:
                return None

        return await asyncio.to_thread(_extract)
