import json
import os
from name_utils import normalise_game_name

def load_games(path: str) -> set[str]:
    if not os.path.exists(path):
        return set()

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    return {normalise_game_name(name) for name in raw}

def save_games(path: str, games: set[str]) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(sorted(games), f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

def add_game(games: set[str], game_name: str) -> bool:
    key = normalise_game_name(game_name)
    if key in games:
        return False
    games.add(key)
    return True