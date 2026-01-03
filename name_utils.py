import re

_TM_RX = re.compile(r"[™®]")
_WS_RX = re.compile(r"\s+")
_PUNCT_RX = re.compile(r"[^\w\s]")

def normalise_game_name(name: str) -> str:
    if not name:
        return ""
    s = name.casefold()
    s = _TM_RX.sub("", s)
    s = _PUNCT_RX.sub(" ", s)
    s = _WS_RX.sub(" ", s).strip()
    return s
