import streamlit as st
from utils.constants import SKILL_ATTRIBUTES, ROLE_FLAGS, GAME_TOGGLE_FLAGS

ATTR_LABELS = {
    "speed": "🏃 Speed", "agility": "↕ Agility", "stamina": "💪 Stamina", "toughness": "🛡 Toughness",
    "hands": "🙌 Hands", "route_running": "🔀 Route Running", "offensive_iq": "🧠 Offensive IQ", "throwing": "🏈 Throwing",
    "flag_pulling": "🚩 Flag Pulling", "defense_iq": "🛡 Defense IQ",
    "awareness": "👁 Awareness", "leadership": "⭐ Leadership"
}

ROLE_LABELS = {
    "can_play_qb": "QB", "can_play_rb": "RB", "can_play_center": "Center",
    "can_play_wr": "WR", "can_play_slot": "Slot",
    "can_play_olb": "OLB", "can_play_mlb": "MLB", "can_play_cb": "CB",
    "can_play_safety": "Safety", "can_play_blitzer": "Blitzer", "can_play_utility": "Utility"
}

def render_player_editor(player: dict, key_prefix: str = "") -> dict:
    updated = dict(player)
    
    col1, col2 = st.columns(2)
    with col1:
        updated["name"] = st.text_input("Name", value=player.get("name", ""), key=f"{key_prefix}_name")
        updated["jersey_number"] = st.text_input("Jersey #", value=player.get("jersey_number", ""), key=f"{key_prefix}_jersey")
    with col2:
        updated["notes"] = st.text_area("Notes", value=player.get("notes", ""), height=80, key=f"{key_prefix}_notes")
    
    st.markdown("**Game Toggles**")
    toggle_cols = st.columns(3)
    toggle_items = [f for f in GAME_TOGGLE_FLAGS if f != "injured"]
    for i, flag in enumerate(GAME_TOGGLE_FLAGS):
        label = flag.replace("_", " ").title()
        with toggle_cols[i % 3]:
            updated[flag] = st.checkbox(label, value=player.get(flag, False), key=f"{key_prefix}_{flag}")
    
    st.markdown("**Skill Ratings** (1-10)")
    
    # Group attributes
    groups = {
        "Athleticism": ["speed", "agility", "stamina", "toughness"],
        "Offense": ["hands", "route_running", "offensive_iq", "throwing"],
        "Defense": ["flag_pulling", "defense_iq"],
        "Mental": ["awareness", "leadership"]
    }
    
    for group, attrs in groups.items():
        with st.expander(f"📊 {group}", expanded=True):
            gcols = st.columns(2)
            for i, attr in enumerate(attrs):
                with gcols[i % 2]:
                    label = ATTR_LABELS.get(attr, attr)
                    updated[attr] = st.slider(
                        label, min_value=1, max_value=10,
                        value=int(player.get(attr, 5)),
                        key=f"{key_prefix}_{attr}"
                    )
    
    st.markdown("**Positions** (check all that apply)")
    role_cols = st.columns(4)
    for i, role in enumerate(ROLE_FLAGS):
        with role_cols[i % 4]:
            label = ROLE_LABELS.get(role, role)
            updated[role] = st.checkbox(label, value=player.get(role, True), key=f"{key_prefix}_{role}")
    
    return updated
