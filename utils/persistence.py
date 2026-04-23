import json
import os
from typing import List, Dict, Any
from utils.data_models import default_player, default_settings
from utils.constants import DEFAULT_ROSTER_NAMES

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
PLAYERS_FILE = os.path.join(DATA_DIR, "players.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_players() -> List[Dict[str, Any]]:
    _ensure_data_dir()
    if not os.path.exists(PLAYERS_FILE):
        players = [default_player(i + 1, name) for i, name in enumerate(DEFAULT_ROSTER_NAMES)]
        save_players(players)
        return players
    try:
        with open(PLAYERS_FILE, "r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Players data must be a list")
        validated = []
        for i, p in enumerate(data):
            validated.append(_validate_player(p, i + 1))
        return validated
    except (json.JSONDecodeError, ValueError, KeyError):
        players = [default_player(i + 1, name) for i, name in enumerate(DEFAULT_ROSTER_NAMES)]
        save_players(players)
        return players

def _validate_player(p: dict, fallback_id: int) -> dict:
    from utils.data_models import default_player
    from utils.constants import SKILL_ATTRIBUTES, ROLE_FLAGS, GAME_TOGGLE_FLAGS
    base = default_player(fallback_id, p.get("name", f"Player{fallback_id}"))
    base.update({k: v for k, v in p.items() if k in base})
    # ensure all skill attributes are int 1-10
    for attr in SKILL_ATTRIBUTES:
        try:
            base[attr] = max(1, min(10, int(base[attr])))
        except (ValueError, TypeError):
            base[attr] = 5
    return base

def save_players(players: List[Dict[str, Any]]):
    _ensure_data_dir()
    with open(PLAYERS_FILE, "w") as f:
        json.dump(players, f, indent=2)

def load_settings() -> Dict[str, Any]:
    _ensure_data_dir()
    if not os.path.exists(SETTINGS_FILE):
        settings = default_settings()
        save_settings(settings)
        return settings
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("Settings must be a dict")
        base = default_settings()
        base.update(data)
        return base
    except (json.JSONDecodeError, ValueError):
        settings = default_settings()
        save_settings(settings)
        return settings

def save_settings(settings: Dict[str, Any]):
    _ensure_data_dir()
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)
