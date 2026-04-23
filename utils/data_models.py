from utils.constants import SKILL_ATTRIBUTES, ROLE_FLAGS, GAME_TOGGLE_FLAGS

def default_player(player_id: int, name: str) -> dict:
    player = {
        "id": player_id,
        "name": name,
        "jersey_number": str(player_id),
        "notes": "",
        "archived": False,
    }
    for flag in GAME_TOGGLE_FLAGS:
        player[flag] = (flag == "available")
    for attr in SKILL_ATTRIBUTES:
        player[attr] = 5
    for role in ROLE_FLAGS:
        player[role] = True
    return player

def default_settings() -> dict:
    return {
        "offense_size": 7,
        "defense_size": 7,
        "possessions_per_half": 3,
        "halves": 2,
        "planning_mode": "Fair Rotation",
        "fairness_weight": 0.5,
        "strength_weight": 0.5,
        "theme": "dark",
        "rating_weights": {
            "offense": {
                "speed": 0.20, "hands": 0.20, "route_running": 0.15,
                "offensive_iq": 0.20, "stamina": 0.10, "awareness": 0.15
            },
            "defense": {
                "speed": 0.15, "agility": 0.15, "flag_pulling": 0.20,
                "defense_iq": 0.20, "stamina": 0.10, "awareness": 0.10, "toughness": 0.10
            },
            "qb": {
                "throwing": 0.30, "offensive_iq": 0.25, "leadership": 0.20,
                "awareness": 0.15, "stamina": 0.10
            },
            "rb": {"speed": 0.35, "agility": 0.30, "offensive_iq": 0.20, "stamina": 0.15},
            "wr": {"speed": 0.30, "hands": 0.30, "route_running": 0.25, "offensive_iq": 0.15},
            "slot": {"hands": 0.30, "route_running": 0.25, "awareness": 0.25, "offensive_iq": 0.20},
            "center": {
                "awareness": 0.25, "leadership": 0.25, "hands": 0.20,
                "toughness": 0.15, "offensive_iq": 0.15
            },
            "olb": {"defense_iq": 0.30, "flag_pulling": 0.30, "awareness": 0.20, "toughness": 0.20},
            "mlb": {"defense_iq": 0.30, "leadership": 0.25, "awareness": 0.25, "toughness": 0.20},
            "cb": {"speed": 0.30, "agility": 0.30, "defense_iq": 0.20, "awareness": 0.20},
            "safety": {"speed": 0.30, "awareness": 0.30, "defense_iq": 0.25, "leadership": 0.15},
            "blitzer": {"speed": 0.30, "agility": 0.25, "toughness": 0.25, "flag_pulling": 0.20},
        }
    }
