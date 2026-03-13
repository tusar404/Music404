"""
Arc Music Bot - Telegram Voice Chat Music Player
Main Entry Point

Copyright (c) 2025 Team Arc
Developer: @tusar404
Support: @ArcUpdates

Based on AnonXMusic architecture
"""

import asyncio
import sys
import signal
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from arc.core import (
    config,
    logger,
    db,
    app,
    userbot,
    yt,
    call,
    api,
    tg_log,
)
from arc.utils.cleanup import CacheCleaner


async def startup():
    """Initialize all components."""
    logger.info("=" * 50)
    logger.info("Arc Music Bot Starting...")
    logger.info("=" * 50)

    # Validate configuration
    if not config.validate():
        logger.error("Configuration validation failed!")
        sys.exit(1)

    logger.info("Configuration validated")

    # Connect to database
    await db.connect()
    logger.info("Database connected")

    # Save cookies if URLs provided
    if config.COOKIE_URLS:
        await yt.save_cookies(config.COOKIE_URLS)
        logger.info("Cookies saved")

    # Start userbot assistants
    await userbot.start()
    logger.info(f"{userbot.count} Assistant(s) started")

    # Start PyTgCalls
    call.set_app(app)
    await call.boot()
    logger.info("PyTgCalls initialized")

    # Start bot
    await app.boot()
    logger.info("Bot started")

    # Setup Telegram logger
    tg_log.setup(app, config.LOGGER_ID, await db.is_logger())
    logger.info("Telegram logger initialized")

    # Start cache cleaner
    cleaner = CacheCleaner()
    asyncio.create_task(cleaner.start())

    logger.info("=" * 50)
    logger.info("Arc Music Bot is now running!")
    logger.info(f"Updates: {config.UPDATES_CHANNEL}")
    logger.info("=" * 50)
    logger.info("")
    logger.info("Copyright (c) 2025 Team Arc")
    logger.info("Developer: @tusar404")
    logger.info("=" * 50)


async def shutdown():
    """Gracefully shutdown all components."""
    logger.info("=" * 50)
    logger.info("Shutting down Arc Music Bot...")

    # Stop call handlers
    try:
        for client in call.clients:
            await client.stop()
        logger.info("PyTgCalls stopped")
    except Exception:
        pass

    # Stop userbot
    await userbot.stop()
    logger.info("Assistants stopped")

    # Stop bot
    await app.exit()
    logger.info("Bot stopped")

    # Close database
    await db.close()
    logger.info("Database closed")

    # Close API session
    await api.close()
    logger.info("API session closed")

    logger.info("=" * 50)
    logger.info("Arc Music Bot stopped. Goodbye!")
    logger.info("=" * 50)


def signal_handler(sig, frame):
    """Handle termination signals."""
    logger.info(f"Received signal {sig}")
    asyncio.get_event_loop().run_until_complete(shutdown())
    sys.exit(0)


async def main():
    """Main entry point."""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await startup()

        # Keep running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as ex:
        logger.error(f"Fatal error: {ex}")
    finally:
        await shutdown()


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 10):
        print("Python 3.10 or higher is required!")
        sys.exit(1)

    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
