import streamlit as st
from utils.branding import get_css, render_header
from utils.persistence import load_players, load_settings, save_settings
from utils.rating_engine import enrich_players
from utils.lineup_engine import generate_game_plan, select_qbs
from utils.validation import validate_game_plan_inputs
from utils.analytics_engine import compute_usage, compute_qb_usage
from components.lineup_display import render_possession_card
from components.summary_cards import render_summary_cards
from components.validation_messages import show_errors, show_warnings, show_success

st.set_page_config(page_title="Game Planner | Diva Ducks", page_icon="🦆", layout="wide")
st.markdown(get_css(), unsafe_allow_html=True)

if "players" not in st.session_state:
    st.session_state.players = load_players()
if "settings" not in st.session_state:
    st.session_state.settings = load_settings()
if "game_plan" not in st.session_state:
    st.session_state.game_plan = []

players = st.session_state.players
settings = st.session_state.settings
enriched = enrich_players(players, settings)

st.markdown(render_header("Game Planner"), unsafe_allow_html=True)

# Sidebar controls
with st.sidebar:
    st.markdown("### 🎮 Game Setup")
    
    planning_mode = st.selectbox(
        "Planning Mode",
        ["Fair Rotation", "Balanced", "Must-Win"],
        index=["Fair Rotation", "Balanced", "Must-Win"].index(settings.get("planning_mode", "Fair Rotation"))
    )
    
    st.markdown("### 👥 Player Availability")
    
    qcols = st.columns(2)
    with qcols[0]:
        if st.button("✅ All Available", use_container_width=True):
            for p in players:
                if not p.get("injured") and not p.get("archived"):
                    p["available"] = True
            from utils.persistence import save_players
            save_players(players)
            st.session_state.players = players
            st.rerun()
    with qcols[1]:
        if st.button("❌ Clear All", use_container_width=True):
            for p in players:
                p["available"] = False
            from utils.persistence import save_players
            save_players(players)
            st.session_state.players = players
            st.rerun()
    
    active = [p for p in enriched if not p.get("archived") and not p.get("injured")]
    
    st.markdown("**Select Available Players:**")
    availability = {}
    for p in active:
        availability[p["id"]] = st.checkbox(
            f"#{p.get('jersey_number', '?')} {p['name']}",
            value=p.get("available", True),
            key=f"avail_{p['id']}"
        )
    
    st.markdown("### 🏈 QB Selection")
    
    qb_hint_cols = st.columns(1)
    recommend_clicked = st.button("⭐ Recommend Best 2 QBs")
    
    qb_eligible_map = {}
    qb_pool = sorted([p for p in active if p.get("can_play_qb")], key=lambda x: -x.get("qb_rating", 0))
    
    if recommend_clicked:
        recommended_ids = [p["id"] for p in qb_pool[:2]]
        st.session_state["recommended_qb_ids"] = recommended_ids
    
    recommended_ids = st.session_state.get("recommended_qb_ids", [])
    
    for p in active:
        default_qb = p.get("qb_eligible", False) or p["id"] in recommended_ids
        qb_eligible_map[p["id"]] = st.checkbox(
            f"QB: {p['name']}",
            value=default_qb,
            key=f"qb_{p['id']}"
        )

# Apply availability from sidebar
for p in players:
    if p["id"] in availability:
        p["available"] = availability[p["id"]]
    if p["id"] in qb_eligible_map:
        p["qb_eligible"] = qb_eligible_map[p["id"]]

available_players = [p for p in enriched if availability.get(p["id"], p.get("available", True)) and not p.get("archived") and not p.get("injured")]
qb_eligible_ids = [pid for pid, eligible in qb_eligible_map.items() if eligible]

# Main content
col_plan, col_preview = st.columns([1, 2])

with col_plan:
    st.markdown("### 📋 Plan Settings")
    
    quick_cols = st.columns(2)
    with quick_cols[0]:
        if st.button("⚡ Quick Fair Plan", use_container_width=True):
            planning_mode = "Fair Rotation"
    with quick_cols[1]:
        if st.button("🔥 Quick Must-Win", use_container_width=True):
            planning_mode = "Must-Win"
    
    st.markdown(f"**Mode:** {planning_mode}")
    st.markdown(f"**Available Players:** {len(available_players)}")
    st.markdown(f"**QB Eligible:** {len(qb_eligible_ids)}")
    
    # Validate
    valid, errors = validate_game_plan_inputs(available_players, qb_eligible_ids, settings)
    if errors:
        show_errors(errors)
    
    if st.button("🚀 Generate Game Plan", use_container_width=True, disabled=not valid):
        qb1, qb2 = select_qbs(available_players, qb_eligible_ids)
        if qb1 and qb2:
            game_plan = generate_game_plan(
                available_players,
                qb1["id"],
                qb2["id"],
                settings,
                mode=planning_mode
            )
            st.session_state.game_plan = game_plan
            st.session_state.current_possession_idx = 0
            show_success(f"Game plan generated! {len(game_plan)} possessions.")
            st.rerun()
    
    if st.session_state.game_plan:
        usage = compute_usage(st.session_state.game_plan, available_players)
        qb_usage = compute_qb_usage(st.session_state.game_plan)
        
        st.markdown("### 📊 QB Plan")
        for name, count in qb_usage.items():
            st.metric(f"QB: {name}", f"{count} possessions")
        
        render_summary_cards(st.session_state.game_plan, available_players)

with col_preview:
    if st.session_state.game_plan:
        st.markdown("### 📋 Game Plan Preview")
        
        half_tabs = st.tabs(["1st Half", "2nd Half"])
        
        for half_idx, half_tab in enumerate(half_tabs):
            with half_tab:
                half_num = half_idx + 1
                half_plan = [p for p in st.session_state.game_plan if p["half"] == half_num]
                for poss in half_plan:
                    render_possession_card(poss, expanded=(half_idx == 0))
    else:
        st.info("👈 Configure your game plan and click Generate.")
        st.markdown("""
        **How to use:**
        1. Select available players in the sidebar
        2. Mark QB-eligible players
        3. Choose a planning mode
        4. Click Generate Game Plan
        """)
