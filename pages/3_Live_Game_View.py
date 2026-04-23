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
if "game_plan_offense_first" not in st.session_state:
    st.session_state.game_plan_offense_first = []
if "game_plan_defense_first" not in st.session_state:
    st.session_state.game_plan_defense_first = []
if "game_plan" not in st.session_state:
    st.session_state.game_plan = []
if "current_possession_idx" not in st.session_state:
    st.session_state.current_possession_idx = 0

st.markdown(render_header("Live Game View"), unsafe_allow_html=True)

# ── Version selector ──────────────────────────────────────────────────────────
has_offense = bool(st.session_state.game_plan_offense_first)
has_defense = bool(st.session_state.game_plan_defense_first)

if not has_offense and not has_defense:
    st.warning("⚠️ No game plan generated. Go to **Game Planner** to create one.")
    st.stop()

C = TEAM_COLORS
version_options = []
if has_offense:
    version_options.append("🏈 Offense First")
if has_defense:
    version_options.append("🛡️ Defense First")

col_ver, col_reset = st.columns([3, 1])
with col_ver:
    selected_version = st.radio(
        "Game-Flow Version",
        version_options,
        horizontal=True,
        label_visibility="collapsed",
    )
with col_reset:
    if st.button("⏮ Reset to Start", use_container_width=True):
        st.session_state.current_possession_idx = 0
        st.rerun()

if "Offense" in selected_version:
    game_plan = st.session_state.game_plan_offense_first
    version_label = "Offense-First"
else:
    game_plan = st.session_state.game_plan_defense_first
    version_label = "Defense-First"

# Keep session game_plan in sync with selected version
st.session_state.game_plan = game_plan

total = len(game_plan)
idx = min(st.session_state.current_possession_idx, total - 1)

# ── Navigation ────────────────────────────────────────────────────────────────
st.markdown("### 🎮 Possession Navigator")

nav_cols = st.columns([1, 4, 1])
with nav_cols[0]:
    if st.button("⬅️ Previous", use_container_width=True, disabled=(idx == 0)):
        st.session_state.current_possession_idx = max(0, idx - 1)
        st.rerun()

with nav_cols[1]:
    progress_text = f"**{version_label}  —  Possession {idx + 1} of {total}**"
    st.markdown(
        f"<div style='text-align:center; color:{C['gold']}; font-size:1.1rem;'>{progress_text}</div>",
        unsafe_allow_html=True,
    )
    st.progress((idx + 1) / total)

with nav_cols[2]:
    if st.button("Next ➡️", use_container_width=True, disabled=(idx == total - 1)):
        st.session_state.current_possession_idx = min(total - 1, idx + 1)
        st.rerun()

# Jump selector
jump = st.selectbox(
    "Jump to Possession",
    options=list(range(total)),
    format_func=lambda i: game_plan[i]["label"],
    index=idx,
)
if jump != idx:
    st.session_state.current_possession_idx = jump
    st.rerun()

st.markdown("---")

# ── Current possession card ───────────────────────────────────────────────────
current = game_plan[idx]
render_possession_card(current, expanded=True)

# ── Up-next preview ───────────────────────────────────────────────────────────
if idx + 1 < total:
    st.markdown("### 👀 Up Next")
    render_possession_card(game_plan[idx + 1], expanded=False)

# ── All-possessions strip ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📋 Full Game Sequence")

cols = st.columns(4)
for i, poss in enumerate(game_plan):
    is_current = (i == idx)
    icon = "🏈" if poss["type"] == "Offense" else "🛡️"
    rank_label = poss.get("rank_label", "")
    btn_label = f"{icon} {poss['label']}\n{rank_label} ({poss['lineup_rank']:.1f})"

    with cols[i % 4]:
        if st.button(
            btn_label,
            key=f"nav_{i}",
            use_container_width=True,
            type="primary" if is_current else "secondary",
        ):
            st.session_state.current_possession_idx = i
            st.rerun()

