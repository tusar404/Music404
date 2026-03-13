# Arc Music Bot - Deployment Guide

## Prerequisites

- Python 3.11 or higher
- FFmpeg
- MongoDB database
- Telegram API credentials
- At least one session string

---

## VPS Deployment (Ubuntu/Debian)

### Step 1: System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install FFmpeg
sudo apt install ffmpeg -y

# Install Git
sudo apt install git -y
```

### Step 2: Clone and Setup

```bash
# Clone repository
git clone https://github.com/TeamArc/ArcMusicBot.git
cd ArcMusicBot

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configuration

```bash
# Copy example config
cp .env.example .env

# Edit configuration
nano .env
```

Add your credentials:
```bash
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
STRING1=your_session_string
MONGO_URL=mongodb+srv://...
OWNER_ID=your_telegram_id
LOGGER_ID=-100your_log_channel_id
```

### Step 4: Run the Bot

```bash
# Activate virtual environment
source venv/bin/activate

# Run
python3 -m arc
```

---

## Systemd Service (Auto-start on Boot)

### Create Service

```bash
sudo nano /etc/systemd/system/arcmusic.service
```

### Service Configuration

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

### Enable Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start
sudo systemctl enable arcmusic

# Start service
sudo systemctl start arcmusic

# Check status
sudo systemctl status arcmusic
```

### Service Management

```bash
# Stop service
sudo systemctl stop arcmusic

# Restart service
sudo systemctl restart arcmusic

# View logs
journalctl -u arcmusic -f
```

---

## Screen Alternative

```bash
# Install screen
sudo apt install screen -y

# Create session
screen -S arcmusic

# Run bot
source venv/bin/activate
python3 -m arc

# Detach: Press Ctrl+A+D
# Reattach: screen -r arcmusic
```

---

## Docker Deployment

### Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY arc/ ./arc/
COPY requirements.txt .

# Run
CMD ["python3", "-m", "arc"]
```

### Build and Run

```bash
# Build image
docker build -t arcmusic .

# Run container
docker run -d \
    --name arcmusic \
    --restart always \
    -v $(pwd)/.env:/app/.env \
    -v $(pwd)/downloads:/app/downloads \
    arcmusic

# View logs
docker logs -f arcmusic
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  arcmusic:
    build: .
    container_name: arcmusic
    restart: always
    volumes:
      - ./.env:/app/.env
      - ./downloads:/app/downloads
```

Run:
```bash
docker-compose up -d
```

---

## Updating the Bot

```bash
# Stop service
sudo systemctl stop arcmusic

# Navigate to directory
cd ArcMusicBot

# Pull updates
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt

# Start service
sudo systemctl start arcmusic
```

---

## Troubleshooting

### Bot won't start

1. Check logs: `journalctl -u arcmusic -f`
2. Verify `.env` configuration
3. Ensure MongoDB is accessible
4. Check API credentials

### FFmpeg not found

```bash
sudo apt install ffmpeg -y
```

### Permission denied

```bash
chmod +x venv/bin/python3
```

### MongoDB connection failed

1. Check connection string
2. Verify IP whitelist in MongoDB Atlas
3. Check network connectivity

### Session invalid

1. Generate new session string
2. Update `STRING1` in `.env`
3. Restart bot
