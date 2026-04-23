# Team and app constants

TEAM_NAME = "Diva Ducks"

# Palette extracted directly from the Diva Ducks logo image:
# Crimson Red  → shield, helmet, jersey  (#B31B1B)
# Forest Green → duck body, shield patch (#1A5C1A)
# Gold/Tan     → trim, text outlines     (#C9A84C)
# Near Black   → banner background       (#111111)
# Cream        → team-name lettering     (#F2E8C8)
TEAM_COLORS = {
    # Primary brand colors (from logo)
    "crimson":       "#B31B1B",   # dominant shield / helmet red
    "forest":        "#1A5C1A",   # duck body / shield green
    "gold":          "#C9A84C",   # trim, text outlines
    "dark":          "#111111",   # banner / near-black
    "cream":         "#F2E8C8",   # team-name lettering

    # Derived / utility shades
    "crimson_light": "#D94040",   # hover states
    "crimson_dark":  "#7B1010",   # pressed / deep shadow
    "forest_light":  "#2E8B2E",   # hover states
    "forest_dark":   "#0D3B0D",   # deep shadow
    "gold_dark":     "#9A7A2A",   # muted gold
    "white":         "#FFFFFF",
    "off_white":     "#F5F0E8",   # warm white for text

    # App background shades (keep dark-theme feel, tinted toward brand)
    "bg_dark":  "#0E1210",        # near-black with forest tint
    "bg_card":  "#1A1E1A",        # card surface, very dark green-tinted
    "bg_card2": "#1F1008",        # alternate card with crimson tint
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
