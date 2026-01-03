# GhostieBot

<p align="center">
  <a href="https://github.com/AshKapow/GhostieBot">
    <img src="https://img.shields.io/github/stars/AshKapow/GhostieBot?style=flat&logo=github" alt="GitHub stars">
  </a>
  <a href="https://github.com/AshKapow/GhostieBot/issues">
    <img src="https://img.shields.io/github/issues/AshKapow/GhostieBot" alt="GitHub issues">
  </a>
  <a href="https://github.com/AshKapow/GhostieBot/commits/main">
    <img src="https://img.shields.io/github/last-commit/AshKapow/GhostieBot" alt="Last commit">
  </a>
  <img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/docker-ready-blue.svg" alt="Docker">
  <img src="https://img.shields.io/badge/discord-bot-5865F2.svg" alt="Discord">
  <img src="https://img.shields.io/badge/twitch-helix-9146FF.svg" alt="Twitch Helix">
  <img src="https://img.shields.io/github/license/AshKapow/GhostieBot" alt="License">
</p>



<p align="center">
<strong>GhostieBot</strong> is a lightweight Discord bot for tracking whether a Twitch streamer has played a suggested Steam game before.
</p>

<p align="center">
Built and maintained by <strong>AshKapow</strong>
</p>

---

> A simple Discord bot that watches Steam game suggestions and tells your community whether the streamer has already played the game based only on what happens while the bot is running.

---

## Why this exists

Viewers often suggest games by pasting Steam links into Discord.  
Manually remembering what has or hasn’t been played quickly becomes unreliable.

GhostieBot was created to answer one question automatically:

> **“Has the streamer played this game before?”**

Important design decisions:
- No scraping
- No VOD history
- No third‑party tracking sites

If the bot didn’t see it happen, it doesn’t count.

---

## What GhostieBot does

### Discord (Steam suggestions)
- Watches a **specific Discord forum channel**
- Only processes the **first post of each forum thread**
- Finds Steam links even if there is text before or after them
- Supports common Steam URL formats (`/app`, `steam://run`, community links)
- Resolves the game name via the Steam API
- Replies in the thread:
  - Played before on stream
  - Not played before on stream

### Twitch (game tracking)
- Polls the Twitch Helix API every `LIVE_CHECK_SECONDS`
- Detects streamer **ONLINE / OFFLINE** state
- When the streamer is live:
  - Reads the current Twitch category/game
  - Stores it once (no duplicates)
- Logs only meaningful state changes (no spam)

“Played before” means:
> The game name exists in the locally stored list.

---

## Data & persistence

Tracked games are stored locally in:

```
games_data/<twitch_channel>_games.json
```

Example:
```json
[
  "phasmophobia",
  "project zomboid"
]
```

- Names are normalised to avoid Steam/Twitch naming differences
- The `games_data/` directory should be mounted as a Docker volume

---

## Requirements

- Discord bot token
- Twitch app credentials (Client ID + Client Secret)
- Docker + Docker Compose (recommended)

---

## How to use

### 1) Discord setup
1. Create a Discord application and bot
2. Enable **Message Content Intent**
3. Invite the bot with permission to:
   - View channels
   - Read message history
   - Send messages
   - Reply in threads

### 2) Forum channel
- Enable Developer Mode in Discord
- Right‑click the forum channel → **Copy Channel ID**
- Set it in `config.py` as `DISCORD_CHANNEL_ID`

### 3) Twitch app
- Create a Twitch application
- Copy:
  - Client ID → `TWITCH_CLIENT_ID`
  - Client Secret → `TWITCH_CLIENT_SECRET`
- Set `TWITCH_CHANNEL` in `config.py` to the streamer login name

### 4) Configure `config.py`
```py
DISCORD_CHANNEL_ID = 123456789012345678
TWITCH_CHANNEL = "streamer_channel"
LIVE_CHECK_SECONDS = 300
```

### 5) Environment variables
Secrets are read **only** from environment variables:
- `DISCORD_TOKEN`
- `TWITCH_CLIENT_ID`
- `TWITCH_CLIENT_SECRET`

### 6) Run with Docker
```yaml
services:
  ghostiebot:
    image: ashkapow/ghostiebot:latest
    container_name: ghostiebot
    restart: unless-stopped
    environment:
      DISCORD_TOKEN: ${DISCORD_TOKEN}
      TWITCH_CLIENT_ID: ${TWITCH_CLIENT_ID}
      TWITCH_CLIENT_SECRET: ${TWITCH_CLIENT_SECRET}
      LOG_LEVEL: INFO
    volumes:
      - ./config.py:/app/config.py:ro
      - ./games_data:/app/games_data
```

---

## Behaviour notes

- Only the first post of a forum thread is processed
- Replies inside the thread are ignored
- Tracking starts from the moment the bot is running

---

## Contributing

Issues and improvements are welcome via GitHub Issues or PRs.  
Please keep changes aligned with the original design goals (simple, local, non‑scraping).

---

## License & attribution

Created by **AshKapow**.

If you fork this project:
- Keep attribution
- Clearly document any behavioural changes