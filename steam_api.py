import re
import time
import requests

_HTTP_STEAM_REGEX = re.compile(
    r"(?:https?://)?(?:store\.steampowered\.com|steamcommunity\.com)"
    r"/(?:(app|sub|bundle))/(\d+)",
    re.IGNORECASE,
)

_STEAM_RUN_REGEX = re.compile(
    r"steam://run/(\d+)",
    re.IGNORECASE,
)

_CACHE: dict[str, tuple[str, float]] = {}
_TTL_SECONDS = 24 * 60 * 60  # 24h


def extract_appid(text: str) -> str | None:
    text = text or ""

    m = _STEAM_RUN_REGEX.search(text)
    if m:
        return m.group(1)

    m = _HTTP_STEAM_REGEX.search(text)
    if not m:
        return None

    kind = (m.group(1) or "").lower()
    steam_id = m.group(2)

    if kind == "app":
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
