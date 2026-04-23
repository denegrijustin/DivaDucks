import streamlit as st
from utils.branding import get_css, render_header
from utils.persistence import load_players, load_settings
from utils.rating_engine import enrich_players
from utils.analytics_engine import compute_usage, compute_qb_usage
from utils.pdf_export import build_pdf
from components.validation_messages import show_errors, show_warnings, show_success

st.set_page_config(page_title="Export PDF | Diva Ducks", page_icon="🦆", layout="wide")
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
game_plan = st.session_state.game_plan

st.markdown(render_header("Export PDF"), unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding:1rem; background:#1A1F2E; border-radius:12px; border:2px solid #2E7D32; margin-bottom:1rem;">
    <h2 style="color:#4CAF50;">📄 Game Plan PDF Export</h2>
    <p style="color:#CCCCCC;">Generate a polished 3-page printable game plan for sideline use.</p>
    <ul style="text-align:left; color:#CCCCCC; display:inline-block;">
        <li>Page 1: 1st Half Game Plan</li>
        <li>Page 2: 2nd Half Game Plan</li>
        <li>Page 3: Analytics, QB Plan, Strongest/Weakest Units</li>
    </ul>
</div>
""", unsafe_allow_html=True)

if not game_plan:
    st.warning("⚠️ No game plan has been generated yet. Please go to the Game Planner page first.")
    st.stop()

available = [p for p in enriched if not p.get("archived")]
usage = compute_usage(game_plan, available)
qb_usage = compute_qb_usage(game_plan)

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("### 📋 Plan Summary")
    offense_poss = [p for p in game_plan if p["type"] == "Offense"]
    defense_poss = [p for p in game_plan if p["type"] == "Defense"]
    
    scols = st.columns(3)
    with scols[0]:
        st.metric("Total Possessions", len(game_plan) // 2)
    with scols[1]:
        avg_off = sum(p["lineup_rank"] for p in offense_poss) / max(len(offense_poss), 1)
        st.metric("Avg Offense Rank", f"{avg_off:.1f}")
    with scols[2]:
        avg_def = sum(p["lineup_rank"] for p in defense_poss) / max(len(defense_poss), 1)
        st.metric("Avg Defense Rank", f"{avg_def:.1f}")

with col2:
    st.markdown("### 📥 Export")
    if st.button("🖨️ Generate PDF", use_container_width=True, type="primary"):
        try:
            pdf_bytes = build_pdf(game_plan, enriched, settings, qb_usage, usage)
            show_success("PDF generated successfully!")
            st.download_button(
                label="⬇️ Download Game Plan PDF",
                data=pdf_bytes,
                file_name="diva_ducks_game_plan.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            show_errors([f"PDF generation failed: {str(e)}"])
            st.exception(e)
