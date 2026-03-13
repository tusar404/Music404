# Arc Music Bot

A powerful Telegram Voice Chat Music Bot with YouTube support, queue management, and multi-language support.

## Features

- **Audio/Video Streaming** - Play from YouTube in voice chats
- **YouTube Support** - Download and stream from URLs
- **Search** - Search and play by song name
- **Queue Management** - Full queue with skip, shuffle
- **Custom Thumbnails** - Auto-generated thumbnails (toggleable)
- **Multi-Language** - English, Hindi, Spanish, Arabic, Indonesian, Burmese
- **Multi-Assistant** - Up to 5 assistant accounts
- **MongoDB Database** - Persistent storage
- **Auto-Leave** - Leaves after 2 hours of inactivity

## Quick Deploy

### VPS Deployment (Ubuntu/Debian)

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+ and pip
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install FFmpeg (required for audio processing)
sudo apt install ffmpeg -y

# Clone repository
git clone https://github.com/TeamArc/ArcMusicBot.git
cd ArcMusicBot

# Create and activate virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
nano .env
```

### Configuration (.env)

```bash
# Required Variables
API_ID=your_api_id                    # Get from my.telegram.org
API_HASH=your_api_hash                # Get from my.telegram.org
BOT_TOKEN=your_bot_token              # Get from @BotFather
STRING1=your_session_string           # Generate using session generator
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net
OWNER_ID=your_telegram_id
LOGGER_ID=-100your_log_channel_id

# Optional Variables
API_URL=https://api.deadlinetech.site
API_KEY=your_api_key
THUMBNAILS_ENABLED=True
AUTO_LEAVE=True
AUTO_LEAVE_TIME=7200
```

### Running the Bot

```bash
# Method 1: Direct run
source venv/bin/activate
python3 -m arc
```

### Using Systemd (Auto-start on boot)

```bash
# Create service file
sudo nano /etc/systemd/system/arcmusic.service
```

Add the following content:

```ini
[Unit]
Description=Arc Music Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/ArcMusicBot
ExecStart=/root/ArcMusicBot/venv/bin/python3 -m arc
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable arcmusic

# Start the bot
sudo systemctl start arcmusic

# Check status
sudo systemctl status arcmusic

# View live logs
journalctl -u arcmusic -f
```

### Using Screen (Alternative)

```bash
# Create new screen session
screen -S arcmusic

# Activate virtual environment and run
source venv/bin/activate
python3 -m arc

# Press Ctrl+A+D to detach
# Reattach with: screen -r arcmusic
```

## Docker Deployment

```bash
# Build image
docker build -t arcmusic .

# Run container
docker run -d --name arcmusic --restart always \
    -v $(pwd)/.env:/app/.env \
    -v $(pwd)/downloads:/app/downloads \
    arcmusic
```

## Getting Session String

Use the string generator: https://replit.com/@AnonX1025/StringGen

## Project Structure

```
arc/
├── __main__.py          # Entry point
├── core/                # Core modules (config, database, calls)
├── plugins/             # Command handlers
├── helpers/             # Utility helpers
├── languages/           # Language files
└── utils/               # Cleanup utilities
```

## Support

- **Updates:** @ArcUpdates
- **Support Chat:** @ArcUpdates

## Credits

Based on AnonXMusic architecture by [AnonymousX1025](https://github.com/AnonymousX1025)

---

**Copyright (c) 2025 Team Arc**

**Developer: [@tusar404](https://github.com/tusar404)**
