"""
External API Module for Arc Music Bot
Handles communication with external download APIs

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

import asyncio
import os
import re
import time
import uuid
import urllib.parse
from pathlib import Path
from typing import Optional, Any

import aiohttp
import aiofiles

from arc.core.config import config
from arc.core.logging import LOGGER


# Polling Configuration
JOB_POLL_ATTEMPTS = 15
JOB_POLL_INTERVAL = 2.0
JOB_POLL_BACKOFF = 1.2
HARD_TIMEOUT = 80

# Download Configuration
V2_DOWNLOAD_CYCLES = 8
NO_CANDIDATE_WAIT = 4
CDN_RETRIES = 5
CDN_RETRY_DELAY = 2
CHUNK_SIZE = 1024 * 1024

# Flood Control
TG_FLOOD_COOLDOWN = 0.0


class ArcAPI:
    """
    External API handler for YouTube downloads.
    Supports polling-based async downloads and CDN retrieval.
    Get your API key from: deadlinetech.site
    """

    def __init__(self):
        self.api_url = config.API_URL.rstrip("/") if config.API_URL else ""
        self.api_key = config.API_KEY
        self.download_dir = Path("download")
        self.download_dir.mkdir(parents=True, exist_ok=True)

        self._session: Optional[aiohttp.ClientSession] = None
        self._session_lock = asyncio.Lock()

    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session and not self._session.closed:
            return self._session

        async with self._session_lock:
            if self._session and not self._session.closed:
                return self._session

            timeout = aiohttp.ClientTimeout(
                total=HARD_TIMEOUT,
                sock_connect=10,
                sock_read=30
            )
            connector = aiohttp.TCPConnector(
                limit=100,
                ttl_dns_cache=300,
                enable_cleanup_closed=True
            )
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector
            )
            return self._session

    def _looks_like_status_text(self, text: Optional[str]) -> bool:
        """Check if response looks like a status message."""
        if not text:
            return False
        low = text.lower()
        return any(x in low for x in (
            "download started", "background", "jobstatus",
            "job_id", "processing", "queued"
        ))

    def _extract_candidate(self, obj: Any) -> Optional[str]:
        """Extract download URL from API response."""
        if obj is None:
            return None

        if isinstance(obj, str):
            s = obj.strip()
            return s if s else None

        if isinstance(obj, list) and obj:
            return self._extract_candidate(obj[0])

        if isinstance(obj, dict):
            # Check nested job result
            job = obj.get("job")
            if isinstance(job, dict):
                res = job.get("result")
                if isinstance(res, dict):
                    for k in ("public_url", "cdnurl", "download_url", "url"):
                        v = res.get(k)
                        if isinstance(v, str) and v.strip():
                            return v.strip()

            # Check direct keys
            for k in ("public_url", "cdnurl", "download_url", "url", "tg_link"):
                v = obj.get(k)
                if isinstance(v, str) and v.strip():
                    return v.strip()

            # Check nested structures
            for wrap in ("result", "results", "data", "items"):
                v = obj.get(wrap)
                if v:
                    return self._extract_candidate(v)

        return None

    def _normalize_url(self, candidate: str) -> Optional[str]:
        """Normalize URL to absolute path."""
        if not self.api_url or not candidate:
            return None

        c = candidate.strip()
        if c.startswith(("http://", "https://")):
            return c

        if c.startswith("/"):
            if c.startswith(("/root", "/home")):
                return None
            return f"{self.api_url}{c}"

        return f"{self.api_url}/{c.lstrip('/')}"

    def extract_video_id(self, link: str) -> Optional[str]:
        """Extract YouTube video ID from URL."""
        try:
            if "v=" in link:
                vid = link.split("v=")[-1].split("&")[0]
            elif "youtu.be" in link:
                vid = link.split("/")[-1].split("?")[0]
            elif "shorts/" in link:
                vid = link.split("shorts/")[-1].split("?")[0]
            else:
                return None

            if re.match(r"^[a-zA-Z0-9_-]{11}$", vid):
                return vid
        except Exception:
            pass
        return None

    async def _download_from_cdn(self, url: str, out_path: str) -> bool:
        """Download file from CDN URL."""
        logger = LOGGER(__name__)

        # HTTP CDN download
        for attempt in range(1, CDN_RETRIES + 1):
            try:
                session = await self.get_session()
                async with session.get(url, timeout=HARD_TIMEOUT) as resp:
                    if resp.status != 200:
                        if attempt < CDN_RETRIES:
                            await asyncio.sleep(CDN_RETRY_DELAY)
                            continue
                        return False

                    async with aiofiles.open(out_path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(CHUNK_SIZE):
                            if not chunk:
                                break
                            await f.write(chunk)

                if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                    return True

            except asyncio.TimeoutError:
                if attempt < CDN_RETRIES:
                    await asyncio.sleep(CDN_RETRY_DELAY)
            except Exception as ex:
                if attempt == CDN_RETRIES:
                    logger.error(f"CDN download failed: {ex}")
                await asyncio.sleep(CDN_RETRY_DELAY)

        return False

    async def download_track(
        self,
        link: str,
        video: bool = False
    ) -> Optional[str]:
        """
        Download a YouTube track using the external API.

        Args:
            link: YouTube URL or video ID
            video: Whether to download video

        Returns:
            Path to downloaded file or None
        """
        logger = LOGGER(__name__)
        vid = self.extract_video_id(link) or link
        file_id = self.extract_video_id(link) or uuid.uuid4().hex[:10]

        # Check existing files with various extensions
        possible_exts = ["mp4", "mkv"] if video else ["mp3", "m4a", "webm"]
        for ext in possible_exts:
            check_path = self.download_dir / f"{file_id}.{ext}"
            if check_path.exists() and check_path.stat().st_size > 0:
                return str(check_path)

        # Poll external API
        if not self.api_url or not self.api_key:
            logger.error("API credentials not configured")
            return None

        for cycle in range(1, V2_DOWNLOAD_CYCLES + 1):
            try:
                session = await self.get_session()
                url = f"{self.api_url}/youtube/v2/download"
                params = {
                    "query": vid,
                    "isVideo": str(video).lower(),
                    "api_key": self.api_key
                }

                async with session.get(url, params=params) as resp:
                    if resp.status != 200:
                        if cycle < V2_DOWNLOAD_CYCLES:
                            await asyncio.sleep(1)
                            continue
                        return None
                    data = await resp.json()

                # Extract download URL
                candidate = self._extract_candidate(data)
                if candidate and self._looks_like_status_text(candidate):
                    candidate = None

                # Handle job-based polling
                job_id = data.get("job_id")
                if isinstance(data.get("job"), dict):
                    job_id = data.get("job").get("id")

                if job_id and not candidate:
                    interval = JOB_POLL_INTERVAL

                    for _ in range(JOB_POLL_ATTEMPTS):
                        await asyncio.sleep(interval)
                        status_url = f"{self.api_url}/youtube/jobStatus"

                        try:
                            async with session.get(
                                status_url,
                                params={"job_id": job_id}
                            ) as s_resp:
                                if s_resp.status == 200:
                                    s_data = await s_resp.json()
                                    candidate = self._extract_candidate(s_data)

                                    if candidate and not self._looks_like_status_text(candidate):
                                        break

                                    job_data = s_data.get("job", {})
                                    if job_data.get("status") == "error":
                                        logger.error(f"Job error: {job_data.get('error')}")
                                        break
                        except Exception:
                            pass

                        interval *= JOB_POLL_BACKOFF

                if not candidate:
                    if cycle < V2_DOWNLOAD_CYCLES:
                        await asyncio.sleep(NO_CANDIDATE_WAIT)
                        continue
                    return None

                final_url = self._normalize_url(candidate)
                if not final_url:
                    if cycle < V2_DOWNLOAD_CYCLES:
                        await asyncio.sleep(NO_CANDIDATE_WAIT)
                        continue
                    return None

                # Determine extension from URL
                parsed_path = urllib.parse.urlparse(final_url).path
                dynamic_ext = os.path.splitext(parsed_path)[1].lstrip('.').lower()

                if not dynamic_ext or dynamic_ext not in ["mp3", "m4a", "webm", "mp4", "mkv"]:
                    dynamic_ext = "mp4" if video else "mp3"

                out_path = str(self.download_dir / f"{file_id}.{dynamic_ext}")

                if await self._download_from_cdn(final_url, out_path):
                    return out_path

            except Exception as ex:
                logger.error(f"API cycle {cycle} error: {ex}")
                if cycle < V2_DOWNLOAD_CYCLES:
                    await asyncio.sleep(1)

        return None

    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
