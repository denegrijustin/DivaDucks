import streamlit as st
from utils.branding import get_css, render_header
from utils.persistence import load_players, load_settings
from utils.rating_engine import enrich_players

st.set_page_config(
    page_title="Diva Ducks Coaching App",
    page_icon="🦆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply branding CSS
st.markdown(get_css(), unsafe_allow_html=True)

# Load data into session state
if "players" not in st.session_state:
    st.session_state.players = load_players()
if "settings" not in st.session_state:
    st.session_state.settings = load_settings()
if "game_plan" not in st.session_state:
    st.session_state.game_plan = []
if "game_plan_offense_first" not in st.session_state:
    st.session_state.game_plan_offense_first = []
if "game_plan_defense_first" not in st.session_state:
    st.session_state.game_plan_defense_first = []
if "current_possession_idx" not in st.session_state:
    st.session_state.current_possession_idx = 0

# Enrich players with computed ratings
players = enrich_players(st.session_state.players, st.session_state.settings)
st.session_state.enriched_players = players

# Header
st.markdown(render_header("Dashboard"), unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding: 1rem;">
    <h2 style="color: #C9A84C;">🏈 Welcome, Coach!</h2>
    <p style="color: #F2E8C8; font-size: 1.1rem;">
        Your Diva Ducks coaching command center is ready.<br>
        Use the sidebar to navigate between pages.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    active = [p for p in players if not p.get("archived") and not p.get("injured")]
    st.metric("Active Players", len(active))
    available = [p for p in active if p.get("available")]
    st.metric("Available Today", len(available))

with col2:
    qb_eligible = [p for p in active if p.get("qb_eligible")]
    st.metric("QB Eligible", len(qb_eligible))
    has_plan = bool(st.session_state.get("game_plan_offense_first"))
    st.metric("Plan Generated", "Yes ✅" if has_plan else "No ❌")

with col3:
    game_plan = st.session_state.get("game_plan", [])
    if game_plan:
        offense_poss = [p for p in game_plan if p["type"] == "Offense"]
        avg_rank = sum(p["lineup_rank"] for p in offense_poss) / max(len(offense_poss), 1)
        st.metric("Avg Offense Rank", f"{avg_rank:.1f}")
        defense_poss = [p for p in game_plan if p["type"] == "Defense"]
        avg_def = sum(p["lineup_rank"] for p in defense_poss) / max(len(defense_poss), 1)
        st.metric("Avg Defense Rank", f"{avg_def:.1f}")
    else:
        st.info("Generate a game plan to see rankings.")

st.markdown("---")
st.markdown("""
### Quick Links
- 👥 **Player Management** — Edit roster, skills, availability
- 📋 **Game Planner** — Generate both Offense-First and Defense-First plans
- 🎮 **Live Game View** — Sideline possession navigator (toggle between versions)
- 📊 **Analytics** — Usage charts, bench patterns, sit-twice analysis
- ⚙️ **Settings** — Adjust game rules and weights
- 📄 **Export PDF** — Print your 3-page game plan (per version)
""")
