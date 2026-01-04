import os
import sys
import asyncio
import discord
import config
import logging
import signal
from logging_setup import setup_logging
from games_store import load_games
from live_tracker import LiveTracker
from steam_api import extract_appid, get_steam_game_name
from name_utils import normalise_game_name

setup_logging()
log = logging.getLogger("ghostiebot")

DISCORD_CHANNEL_ID = config.DISCORD_CHANNEL_ID
TWITCH_CHANNEL = config.TWITCH_CHANNEL
LIVE_CHECK_SECONDS = config.LIVE_CHECK_SECONDS
GAMES_FILE = f"games_data/{TWITCH_CHANNEL}_games.json"

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

if not DISCORD_TOKEN:
    sys.exit("Missing DISCORD_TOKEN")
if not TWITCH_CLIENT_ID:
    sys.exit("Missing TWITCH_CLIENT_ID")
if not TWITCH_CLIENT_SECRET:
    sys.exit("Missing TWITCH_CLIENT_SECRET")

os.makedirs("games_data", exist_ok=True)


def is_game_known(game_name: str) -> bool:
    games = load_games(GAMES_FILE)
    return normalise_game_name(game_name) in games


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)

tracker = LiveTracker(
    TWITCH_CLIENT_ID,
    TWITCH_CLIENT_SECRET,
    TWITCH_CHANNEL,
    GAMES_FILE,
)


@client.event
async def on_ready():
    log.info(f"Logged in as {client.user} (id={client.user.id})")
    log.info(f"Watching forum channel id: {DISCORD_CHANNEL_ID}")

    # immediate check, then background polling
    await tracker.check_once_async()
    tracker.start_loop(LIVE_CHECK_SECONDS)


@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if not isinstance(message.channel, discord.Thread):
        return
    if message.channel.parent_id != DISCORD_CHANNEL_ID:
        return
    if message.id != message.channel.id:
        return

    appid = extract_appid(message.content)
    if not appid:
        await message.reply("No Steam store link detected.")
        return

    game_name = await asyncio.to_thread(get_steam_game_name, appid)
    if not game_name:
        await message.reply(
            f"Steam app detected (appid: {appid}) but failed to resolve game name."
        )
        return

    user = message.author.display_name
    forum_name = message.channel.parent.name
    log.info(f"{user} posted '{game_name}' in {forum_name}")

    if is_game_known(game_name):
        await message.reply(f"{TWITCH_CHANNEL} has played **{game_name}**.")
    else:
        await message.reply(f"No record of {TWITCH_CHANNEL} playing **{game_name}**.")


async def shutdown(sig: str):
    log.info(f"Shutdown requested ({sig})")

    # stop background polling
    tracker.stop_loop()

    # close discord connection
    await client.close()

async def main():
    loop = asyncio.get_running_loop()

    # Handle Docker stop (SIGTERM) + Ctrl+C (SIGINT)
    for s in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(s, lambda sig=s: asyncio.create_task(shutdown(sig.name)))
        except NotImplementedError:
            # fallback (rare in containers, but safe)
            signal.signal(s, lambda *_: asyncio.create_task(shutdown(s.name)))

    await client.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
