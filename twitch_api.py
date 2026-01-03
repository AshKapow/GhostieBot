import requests

class TwitchAuthError(Exception):
    pass

def get_app_token(client_id: str, client_secret: str) -> str:
    r = requests.post(
        "https://id.twitch.tv/oauth2/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        },
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["access_token"]

def get_live_game_name(client_id: str, token: str, channel_login: str) -> str | None:
    r = requests.get(
        "https://api.twitch.tv/helix/streams",
        headers={"Client-ID": client_id, "Authorization": f"Bearer {token}"},
        params={"user_login": channel_login},
        timeout=15,
    )

    if r.status_code in (401, 403):
        raise TwitchAuthError(f"Twitch auth failed ({r.status_code})")

    r.raise_for_status()

    data = r.json().get("data", [])
    if not data:
        return None
    return (data[0].get("game_name") or "").strip() or None
