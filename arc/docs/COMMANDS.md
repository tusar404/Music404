# Arc Music Bot - Command Reference

## Music Commands

### /play [song/url]
Play audio from YouTube in the voice chat.

**Usage:**
- `/play never gonna give you up` - Search and play by name
- `/play https://youtube.com/watch?v=xxx` - Play from URL
- Reply to audio/video file with `/play` - Play Telegram media

**Aliases:** `/p`

---

### /vplay [video/url]
Play video from YouTube in the voice chat.

**Usage:**
- `/vplay music video` - Search and play video
- `/vplay https://youtube.com/watch?v=xxx` - Play video from URL

**Note:** Requires video chat enabled in the group.

---

### /pause
Pause the current playback.

**Usage:** `/pause`

**Aliases:** `/puse`

---

### /resume
Resume paused playback.

**Usage:** `/resume`

**Aliases:** `/res`

---

### /skip
Skip to the next track in the queue.

**Usage:** `/skip`

---

### /stop
Stop playback and leave the voice chat.

**Usage:** `/stop`

---

## Queue Commands

### /queue
View the current queue with pagination.

**Usage:** `/queue`

---

### /now
Show currently playing track.

**Usage:** `/now`

---

### /clear
Clear the entire queue.

**Usage:** `/clear`

---

### /shuffle
Shuffle the queue randomly.

**Usage:** `/shuffle`

---

## Admin Commands

### /auth [user]
Authorize a user to use admin-only commands.

**Usage:**
- `/auth` (reply to user's message)
- `/auth 123456789` (by user ID)

---

### /unauth [user]
Remove user authorization.

**Usage:**
- `/unauth` (reply to user's message)
- `/unauth 123456789` (by user ID)

**Aliases:** `/deauth`

---

### /adminmode
Toggle admin-only mode. When enabled, only admins can play music.

**Usage:** `/adminmode`

**Aliases:** `/adminonly`

---

### /autodelete
Toggle auto-deletion of commands after execution.

**Usage:** `/autodelete`

**Aliases:** `/autodel`

---

### /setlang
Set the bot language for the chat.

**Usage:** `/setlang` (shows inline buttons)

**Supported Languages:**
- English (en)
- Hindi (hi)
- Spanish (es)
- Arabic (ar)
- Indonesian (id)
- Burmese (my)

---

### /thumbnail
Toggle thumbnail display for now playing messages.

**Usage:** `/thumbnail`

---

## Utility Commands

### /ping
Check bot latency.

**Usage:** `/ping`

---

### /id
Get chat ID and user ID.

**Usage:** `/id`

---

### /info
Show bot information and statistics.

**Usage:** `/info`

**Aliases:** `/botinfo`

---

### /help
Show help message with commands.

**Usage:** `/help`

---

### /start
Start the bot (PM only).

**Usage:** `/start`

---

## Sudo/Owner Commands

### /sudo [user]
Add a sudo user (Owner only).

**Usage:**
- `/sudo` (reply to user)
- `/sudo 123456789` (by user ID)

**Aliases:** `/addsudo`

---

### /delsudo [user]
Remove a sudo user (Owner only).

**Usage:** `/delsudo 123456789`

**Aliases:** `/rmsudo`

---

### /blacklist [id]
Blacklist a chat or user (Owner only).

**Usage:** `/blacklist -1001234567890`

**Aliases:** `/bl`

---

### /unblacklist [id]
Remove from blacklist (Owner only).

**Usage:** `/unblacklist -1001234567890`

**Aliases:** `/unbl`

---

### /active
Show all active voice chats.

**Usage:** `/active`

**Aliases:** `/activecalls`, `/calls`

---

### /broadcast [message]
Broadcast a message to all chats.

**Usage:** `/broadcast Hello everyone!`

**Aliases:** `/gcast`

---

### /maintenance
Toggle maintenance mode.

**Usage:** `/maintenance`

---

### /logger
Toggle Telegram logging.

**Usage:** `/logger`

---

### /stats
Show bot statistics.

**Usage:** `/stats`

**Aliases:** `/botstats`

---

### /leave [chat_id]
Leave a specific chat.

**Usage:** `/leave -1001234567890`

---

### /cleanup
Clean cache and database.

**Usage:** `/cleanup`

**Aliases:** `/clean`

---

### /restart
Restart the bot.

**Usage:** `/restart`

**Aliases:** `/reboot`
