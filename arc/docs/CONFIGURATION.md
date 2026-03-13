# Arc Music Bot - Configuration Guide

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `API_ID` | Telegram API ID | `12345678` |
| `API_HASH` | Telegram API Hash | `abcdef123456...` |
| `BOT_TOKEN` | Bot token from @BotFather | `123456:ABC-DEF...` |
| `STRING1` | Session string for assistant | `BVtsxyz...` |
| `MONGO_URL` | MongoDB connection URL | `mongodb+srv://...` |
| `OWNER_ID` | Telegram ID of the owner | `123456789` |
| `LOGGER_ID` | Log channel ID | `-1001234567890` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `STRING2` to `STRING5` | Additional assistant sessions | None |
| `DB_NAME` | Database name | `ArcMusic` |
| `API_URL` | External API URL | None |
| `API_KEY` | External API key | None |
| `MEDIA_CHANNEL_ID` | Media channel for downloads | None |
| `DURATION_LIMIT` | Max track duration (seconds) | `5400` (90 min) |
| `LANG_CODE` | Default language code | `en` |
| `SUPPORT_CHAT` | Support chat username | `@ArcUpdates` |
| `UPDATES_CHANNEL` | Updates channel username | `@ArcUpdates` |

### Feature Toggles

| Variable | Description | Default |
|----------|-------------|---------|
| `THUMBNAILS_ENABLED` | Enable/disable thumbnails globally | `True` |
| `AUTO_LEAVE` | Auto-leave inactive chats | `True` |
| `AUTO_LEAVE_TIME` | Time before auto-leave (seconds) | `7200` (2 hours) |

### Spotify (Optional)

| Variable | Description |
|----------|-------------|
| `SPOTIFY_CLIENT_ID` | Spotify API client ID |
| `SPOTIFY_CLIENT_SECRET` | Spotify API secret |

### Cookies (Optional)

| Variable | Description |
|----------|-------------|
| `COOKIE_URLS` | Comma-separated cookie URLs |

---

## Getting Credentials

### Telegram API (API_ID, API_HASH)

1. Go to https://my.telegram.org/apps
2. Log in with your phone number
3. Create a new application
4. Copy `api_id` and `api_hash`

### Bot Token (BOT_TOKEN)

1. Open @BotFather on Telegram
2. Send `/newbot`
3. Follow the instructions
4. Copy the bot token

### Session String (STRING1)

Use the string generator:
- https://replit.com/@AnonX1025/StringGen

Or generate manually:

```python
from pyrogram import Client

app = Client("session", api_id=API_ID, api_hash=API_HASH)
app.run()
# Check console for the session string
```

### MongoDB (MONGO_URL)

1. Go to https://mongodb.com/cloud/atlas
2. Create a free cluster
3. Create a database user
4. Get connection string
5. Replace `<password>` with your password

### Logger Channel (LOGGER_ID)

1. Create a private channel/group
2. Add your bot as admin
3. Forward a message from the channel to @userinfobot
4. Use the ID (starts with -100)

---

## Example .env File

```bash
# Telegram API
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890

# Bot Token
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Assistant Sessions
STRING1=BVts1aJqMb...
STRING2=BVts2bKrNc...

# MongoDB
MONGO_URL=mongodb+srv://user:password@cluster.mongodb.net
DB_NAME=ArcMusic

# Owner & Logger
OWNER_ID=123456789
LOGGER_ID=-1001234567890

# External API (optional)
API_URL=https://api.deadlinetech.site
API_KEY=your_api_key

# Features
THUMBNAILS_ENABLED=True
AUTO_LEAVE=True
AUTO_LEAVE_TIME=7200
DURATION_LIMIT=5400

# Support
SUPPORT_CHAT=@ArcUpdates
UPDATES_CHANNEL=@ArcUpdates
```

---

## Running Multiple Assistants

You can run up to 5 assistant accounts by providing additional session strings:

```bash
STRING1=first_assistant_session
STRING2=second_assistant_session
STRING3=third_assistant_session
STRING4=fourth_assistant_session
STRING5=fifth_assistant_session
```

More assistants = better load distribution for large groups.
