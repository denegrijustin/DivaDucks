# Team and app constants

TEAM_NAME = "Diva Ducks"
TEAM_COLORS = {
    "green": "#2E7D32",
    "black": "#000000", 
    "red": "#C62828",
    "light_green": "#4CAF50",
    "dark_green": "#1B5E20",
    "gold": "#FFC107",
    "white": "#FFFFFF",
    "bg_dark": "#0D1117",
    "bg_card": "#1A1F2E",
}

OFFENSE_POSITIONS = ["QB", "RB", "Center", "WR1", "WR2", "Slot1", "Slot2"]
DEFENSE_POSITIONS = ["OLB1", "OLB2", "MLB", "CB1", "CB2", "Safety", "Blitzer"]

OFFENSE_SIZE = 7
DEFENSE_SIZE = 7
DEFAULT_POSSESSIONS_PER_HALF = 3
DEFAULT_HALVES = 2

SKILL_ATTRIBUTES = [
    "speed", "agility", "stamina", "toughness",
    "hands", "route_running", "offensive_iq", "throwing",
    "flag_pulling", "defense_iq",
    "awareness", "leadership"
]

ROLE_FLAGS = [
    "can_play_qb", "can_play_rb", "can_play_center",
    "can_play_wr", "can_play_slot",
    "can_play_olb", "can_play_mlb", "can_play_cb",
    "can_play_safety", "can_play_blitzer", "can_play_utility"
]

GAME_TOGGLE_FLAGS = [
    "available", "qb_eligible", "injured",
    "must_play_more", "offense_only", "defense_only"
]

DERIVED_RATINGS = [
    "offense_rating", "defense_rating", "qb_rating",
    "rb_rating", "wr_rating", "slot_rating", "center_rating",
    "olb_rating", "mlb_rating", "cb_rating", "safety_rating",
    "blitzer_rating", "versatility_rating", "composite_rating"
]

PLANNING_MODES = ["Fair Rotation", "Balanced", "Must-Win"]

DEFAULT_ROSTER_NAMES = [
    "Katrina", "Sophia", "Olivia", "Francie", "Eva",
    "Quinn", "Isla", "Timber", "Adriana", "Felicity"
]
