# steam_api.py
import re
import time
import requests

STEAM_LINK_REGEX = re.compile(
    r"(?:https?://)?(?:store\.steampowered\.com|steamcommunity\.com|steam://)"
    r"/(?:(app|sub|bundle|run))/(\d+)",
    re.IGNORECASE,
)

# appid -> (name, expires_epoch)
_CACHE: dict[str, tuple[str, float]] = {}
_TTL_SECONDS = 24 * 60 * 60  # 24h


def extract_steam_ref(text: str) -> tuple[str, str] | None:
    m = STEAM_LINK_REGEX.search(text or "")
    if not m:
        return None
    kind = (m.group(1) or "").lower()
    steam_id = m.group(2)
    return (kind, steam_id)


def extract_appid(text: str) -> str | None:
    ref = extract_steam_ref(text)
    if not ref:
        return None
    kind, steam_id = ref
    if kind in ("app", "run"):
        return steam_id
    return None


def get_steam_game_name(appid: str) -> str | None:
    now = time.time()
    cached = _CACHE.get(appid)
    if cached and cached[1] > now:
        return cached[0]

    url = "https://store.steampowered.com/api/appdetails"
    params = {"appids": appid, "cc": "gb", "l": "en"}

    r = requests.get(url, params=params, timeout=10)
    if r.status_code != 200:
        return None

    data = r.json()
    app_data = data.get(appid)
    if not app_data or not app_data.get("success"):
        return None

    name = app_data.get("data", {}).get("name")
    if not name:
        return None

    _CACHE[appid] = (name, now + _TTL_SECONDS)
    return name
