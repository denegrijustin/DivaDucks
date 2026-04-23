import streamlit as st
from utils.branding import get_css, render_header
from utils.persistence import load_players, load_settings
from utils.rating_engine import enrich_players
from utils.analytics_engine import (
    compute_usage, compute_qb_usage, compute_bench_patterns
)
from utils.pdf_export import build_pdf
from components.validation_messages import show_errors, show_success

st.set_page_config(page_title="Export PDF | Diva Ducks", page_icon="🦆", layout="wide")
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

players = st.session_state.players
settings = st.session_state.settings
enriched = enrich_players(players, settings)

st.markdown(render_header("Export PDF"), unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding:1rem; background:#1A1F2E; border-radius:12px;
            border:2px solid #1A5C1A; margin-bottom:1rem;">
    <h2 style="color:#C9A84C;">📄 Game Plan PDF Export</h2>
    <p style="color:#F2E8C8;">Generate a polished 3-page printable game plan for sideline use.</p>
    <ul style="text-align:left; color:#F2E8C8; display:inline-block;">
        <li><b>Page 1:</b> 1st Half Game Plan</li>
        <li><b>Page 2:</b> 2nd Half Game Plan</li>
        <li><b>Page 3:</b> Analytics, QB Plan, Player Usage Charts</li>
    </ul>
</div>
""", unsafe_allow_html=True)

has_offense = bool(st.session_state.game_plan_offense_first)
has_defense = bool(st.session_state.game_plan_defense_first)

if not has_offense and not has_defense:
    st.warning("⚠️ No game plan has been generated yet. Please go to the **Game Planner** page first.")
    st.stop()

available = [p for p in enriched if not p.get("archived")]

# ── Version selector + export ─────────────────────────────────────────────────
version_options = {}
if has_offense:
    version_options["🏈 Offense First"] = ("offense_first", st.session_state.game_plan_offense_first)
if has_defense:
    version_options["🛡️ Defense First"] = ("defense_first", st.session_state.game_plan_defense_first)

def _export_button(label: str, plan: list, version_key: str, enriched: list, settings: dict):
    """Render a generate + download block for one version."""
    usage = compute_usage(plan, available)
    qb_usage = compute_qb_usage(plan)
    bench_patterns = compute_bench_patterns(plan, available)

    offense_poss = [p for p in plan if p["type"] == "Offense"]
    defense_poss = [p for p in plan if p["type"] == "Defense"]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Possessions", len(plan) // 2)
    with c2:
        avg_off = sum(p["lineup_rank"] for p in offense_poss) / max(len(offense_poss), 1)
        st.metric("Avg Offense Rank", f"{avg_off:.1f}")
    with c3:
        avg_def = sum(p["lineup_rank"] for p in defense_poss) / max(len(defense_poss), 1)
        st.metric("Avg Defense Rank", f"{avg_def:.1f}")

    btn_key = f"gen_pdf_{version_key}"
    if st.button(f"🖨️ Generate PDF — {label}", use_container_width=True, type="primary", key=btn_key):
        try:
            pdf_bytes = build_pdf(
                plan, enriched, settings, qb_usage, usage,
                bench_patterns=bench_patterns,
                version_label=label,
            )
            show_success(f"PDF generated successfully — {label}!")
            st.download_button(
                label=f"⬇️ Download {label} PDF",
                data=pdf_bytes,
                file_name=f"diva_ducks_game_plan_{version_key}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key=f"dl_{version_key}",
            )
        except Exception as e:
            show_errors([f"PDF generation failed: {str(e)}"])
            st.exception(e)


for display_label, (v_key, plan) in version_options.items():
    with st.expander(f"📄 {display_label} Game Plan", expanded=True):
        _export_button(display_label, plan, v_key, enriched, settings)

# ── Bundle export (both) ──────────────────────────────────────────────────────
if has_offense and has_defense:
    st.markdown("---")
    st.markdown("### 📦 Export Both Versions as Separate PDFs")
    col1, col2 = st.columns(2)

    for col, (display_label, (v_key, plan)) in zip([col1, col2], version_options.items()):
        with col:
            usage = compute_usage(plan, available)
            qb_usage = compute_qb_usage(plan)
            bench_patterns = compute_bench_patterns(plan, available)
            if st.button(f"⬇️ {display_label}", use_container_width=True, key=f"quick_{v_key}"):
                try:
                    pdf_bytes = build_pdf(
                        plan, enriched, settings, qb_usage, usage,
                        bench_patterns=bench_patterns,
                        version_label=display_label,
                    )
                    st.download_button(
                        label=f"Save {display_label} PDF",
                        data=pdf_bytes,
                        file_name=f"diva_ducks_{v_key}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key=f"save_{v_key}",
                    )
                except Exception as e:
                    show_errors([f"PDF failed: {str(e)}"])

