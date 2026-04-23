import streamlit as st
from utils.branding import get_css, render_header
from utils.persistence import load_players, load_settings
from components.lineup_display import render_possession_card
from utils.constants import TEAM_COLORS

st.set_page_config(page_title="Live Game View | Diva Ducks", page_icon="🦆", layout="wide")
st.markdown(get_css(), unsafe_allow_html=True)

if "players" not in st.session_state:
    st.session_state.players = load_players()
if "settings" not in st.session_state:
    st.session_state.settings = load_settings()
if "game_plan" not in st.session_state:
    st.session_state.game_plan = []
if "current_possession_idx" not in st.session_state:
    st.session_state.current_possession_idx = 0

st.markdown(render_header("Live Game View"), unsafe_allow_html=True)

game_plan = st.session_state.game_plan

if not game_plan:
    st.warning("No game plan generated. Go to Game Planner to create one.")
    st.stop()

total = len(game_plan)
idx = st.session_state.current_possession_idx

# Navigation
st.markdown("### 🎮 Possession Navigator")

nav_cols = st.columns([1, 3, 1])
with nav_cols[0]:
    if st.button("⬅️ Previous", use_container_width=True, disabled=(idx == 0)):
        st.session_state.current_possession_idx = max(0, idx - 1)
        st.rerun()

with nav_cols[1]:
    progress_text = f"Possession {idx + 1} of {total}"
    st.markdown(f"<h3 style='text-align:center; color:#4CAF50;'>{progress_text}</h3>", unsafe_allow_html=True)
    st.progress((idx + 1) / total)

with nav_cols[2]:
    if st.button("Next ➡️", use_container_width=True, disabled=(idx == total - 1)):
        st.session_state.current_possession_idx = min(total - 1, idx + 1)
        st.rerun()

# Jump to possession
jump = st.selectbox(
    "Jump to Possession",
    options=list(range(total)),
    format_func=lambda i: game_plan[i]["label"],
    index=idx
)
if jump != idx:
    st.session_state.current_possession_idx = jump
    st.rerun()

st.markdown("---")

# Current possession
current = game_plan[idx]
render_possession_card(current, expanded=True)

# Show next possession preview
if idx + 1 < total:
    st.markdown("### 👀 Up Next")
    render_possession_card(game_plan[idx + 1], expanded=False)

# Quick overview strip
st.markdown("---")
st.markdown("### 📋 All Possessions")

cols = st.columns(3)
for i, poss in enumerate(game_plan):
    is_current = (i == idx)
    border = "3px solid #4CAF50" if is_current else "1px solid #2A2F3E"
    icon = "🏈" if poss["type"] == "Offense" else "🛡️"
    
    with cols[i % 3]:
        if st.button(
            f"{icon} {poss['label']}\nRank: {poss['lineup_rank']:.1f}",
            key=f"nav_{i}",
            use_container_width=True,
        ):
            st.session_state.current_possession_idx = i
            st.rerun()
