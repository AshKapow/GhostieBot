import asyncio
import logging
from discord.ext import tasks
from games_store import load_games, save_games, add_game
from twitch_api import get_app_token, get_live_game_name, TwitchAuthError

log = logging.getLogger("ghostiebot")

class LiveTracker:
    def __init__(self, client_id: str, client_secret: str, channel: str, games_file: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.channel = channel
        self.games_file = games_file

        self.token: str | None = None
        self.online: bool | None = None
        self._loop = None

    def _refresh_token(self) -> None:
        self.token = get_app_token(self.client_id, self.client_secret)

    def check_once(self) -> None:
        try:
            if not self.token:
                self._refresh_token()

            try:
                game = get_live_game_name(
                    self.client_id,
                    self.token,
                    self.channel,
                )
            except TwitchAuthError:
                log.warning("Token expired or invalid, refreshing…")
                self._refresh_token()
                game = get_live_game_name(
                    self.client_id,
                    self.token,
                    self.channel,
                )

            if game:
                if self.online is not True:
                    log.info(f"{self.channel} is now ONLINE")
                self.online = True

                games = load_games(self.games_file)
                is_new = add_game(games, game)
                save_games(self.games_file, games)

                log.info(
                    f"{'NEW' if is_new else 'KNOWN'} "
                    f"'{game}' for {self.channel}"
                )
            else:
                if self.online is not False:
                    log.info(f"{self.channel} is now OFFLINE")
                self.online = False

        except Exception as e:
            log.error(f"Poll error: {type(e).__name__}: {e}")

    async def check_once_async(self) -> None:
        try:
            await asyncio.to_thread(self.check_once)
        except Exception as e:
            log.error(f"Async poll error: {type(e).__name__}: {e}")

    def start_loop(self, interval_seconds: int) -> None:
        @tasks.loop(seconds=interval_seconds)
        async def _poll():
            await self.check_once_async()

        self._loop = _poll
        _poll.start()

    def stop_loop(self) -> None:
        if self._loop and self._loop.is_running():
            self._loop.cancel()
