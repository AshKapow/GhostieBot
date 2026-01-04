from name_utils import normalise_game_name
from steam_api import extract_appid

def test_normalise_game_name_basic():
    assert normalise_game_name("Phasmophobia™") == "phasmophobia"
    assert normalise_game_name("Project Zomboid") == "project zomboid"

def test_extract_appid_common_formats():
    assert extract_appid("https://store.steampowered.com/app/108600/") == "108600"
    assert extract_appid("steam://run/108600") == "108600"
    assert extract_appid("https://steamcommunity.com/app/108600") == "108600"
