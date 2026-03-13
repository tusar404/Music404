"""
Thumbnail Generator Module for Arc Music Bot
Creates custom thumbnails for playing messages
"""

import os
import asyncio
import aiohttp
from PIL import (
    Image,
    ImageDraw,
    ImageEnhance,
    ImageFilter,
    ImageFont,
    ImageOps
)
from typing import Optional

from arc.core.config import config
from arc.core.logging import LOGGER


class Thumbnail:
    """
    Thumbnail generator for creating custom playing message images.
    Uses PIL to create branded thumbnails with track information.
    """

    def __init__(self):
        self.canvas_size = (1280, 720)
        self.album_art_rect = (914, 514)
        self.fill_color = (255, 255, 255, 255)

        # Font paths
        self.font_bold_path = "arc/assets/Raleway-Bold.ttf"
        self.font_light_path = "arc/assets/Inter-Light.ttf"
        self.font_size_title = 30
        self.font_size_info = 26

        # Cache for loaded fonts
        self._font_bold = None
        self._font_light = None

    def _load_fonts(self):
        """Load fonts, falling back to default if not available."""
        if self._font_bold is None:
            try:
                self._font_bold = ImageFont.truetype(
                    self.font_bold_path,
                    self.font_size_title
                )
            except (FileNotFoundError, OSError):
                self._font_bold = ImageFont.load_default()

        if self._font_light is None:
            try:
                self._font_light = ImageFont.truetype(
                    self.font_light_path,
                    self.font_size_info
                )
            except (FileNotFoundError, OSError):
                self._font_light = ImageFont.load_default()

        return self._font_bold, self._font_light

    async def _download_thumbnail(self, url: str, output_path: str) -> bool:
        """Download thumbnail from URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.read()

                        def write_file():
                            with open(output_path, "wb") as f:
                                f.write(data)

                        await asyncio.to_thread(write_file)
                        return True
        except Exception:
            pass
        return False

    async def generate(self, track: dict, size: tuple = (1280, 720)) -> Optional[str]:
        """Generate a custom thumbnail for a track."""
        try:
            cache_dir = "cache"
            os.makedirs(cache_dir, exist_ok=True)

            track_id = track.get("id", "unknown")
            temp_path = f"{cache_dir}/temp_{track_id}.jpg"
            output_path = f"{cache_dir}/{track_id}.png"

            # Check if already generated
            if os.path.exists(output_path):
                return output_path

            # Download thumbnail
            thumbnail_url = track.get("thumbnail", "")
            if not thumbnail_url:
                return config.DEFAULT_THUMB

            downloaded = await self._download_thumbnail(thumbnail_url, temp_path)
            if not downloaded:
                return config.DEFAULT_THUMB

            # Load fonts
            font_bold, font_light = self._load_fonts()

            def _process():
                # Open and resize base image
                base = Image.open(temp_path).convert("RGBA")
                base = base.resize(size, Image.Resampling.LANCZOS)

                # Apply blur and darken
                blurred = base.filter(ImageFilter.GaussianBlur(25))
                darkened = ImageEnhance.Brightness(blurred).enhance(0.4)

                # Create rounded album art
                album_size = self.album_art_rect
                album = ImageOps.fit(
                    base,
                    album_size,
                    method=Image.Resampling.LANCZOS,
                    centering=(0.5, 0.5)
                )

                # Create rounded mask
                mask = Image.new("L", album_size, 0)
                draw_mask = ImageDraw.Draw(mask)
                draw_mask.rounded_rectangle(
                    (0, 0, album_size[0], album_size[1]),
                    radius=15,
                    fill=255
                )
                album.putalpha(mask)

                # Paste album art onto background
                darkened.paste(album, (183, 30), album)

                # Draw text elements
                draw = ImageDraw.Draw(darkened)

                # Channel name and view count
                channel_text = track.get("channel_name", "Unknown")[:30]
                view_count = track.get("view_count", "")
                if view_count:
                    channel_text += f" | {view_count}"
                draw.text(
                    (50, 560),
                    channel_text,
                    font=font_light,
                    fill=self.fill_color[:3]
                )

                # Track title
                title = track.get("title", "Unknown")[:60]
                draw.text(
                    (50, 600),
                    title,
                    font=font_bold,
                    fill=self.fill_color[:3]
                )

                # Duration bar
                draw.text((40, 650), "0:01", font=font_bold, fill=self.fill_color[:3])
                draw.line(
                    [(140, 670), (1160, 670)],
                    fill=self.fill_color[:3],
                    width=5
                )

                # Total duration
                duration = track.get("duration", "0:00")
                draw.text(
                    (1185, 650),
                    duration,
                    font=font_bold,
                    fill=self.fill_color[:3]
                )

                # Save output
                darkened = darkened.convert("RGB")
                darkened.save(output_path, "PNG")

                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)

                return output_path

            return await asyncio.to_thread(_process)

        except Exception as ex:
            LOGGER(__name__).error(f"Thumbnail generation failed: {ex}")
            return config.DEFAULT_THUMB

    def cleanup_cache(self, max_age_hours: int = 24):
        """Clean up old cached thumbnails."""
        cache_dir = Path("cache")
        if not cache_dir.exists():
            return

        import time
        max_age_seconds = max_age_hours * 3600
        current_time = time.time()

        for file in cache_dir.iterdir():
            if file.is_file():
                file_age = current_time - file.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        file.unlink()
                    except Exception:
                        pass
