import streamlit as st
import pandas as pd
from utils.branding import get_css, render_header
from utils.persistence import load_players, load_settings
from utils.rating_engine import enrich_players
from utils.analytics_engine import (
    compute_usage, compute_qb_usage, find_strongest_weakest,
    player_role_fit, compute_bench_patterns, check_no_sit_twice_violations,
)
from components.charts import (
    usage_bar_chart, lineup_rank_chart, player_ratings_radar,
    qb_usage_pie, bench_pattern_chart, sit_streak_chart,
)

st.set_page_config(page_title="Analytics | Diva Ducks", page_icon="🦆", layout="wide")
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

st.markdown(render_header("Analytics"), unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Usage", "🏆 Rankings", "👤 Player Profiles", "🔍 Role Fit", "🪑 Bench Patterns"]
)

with tab1:
    if not game_plan:
        st.info("Generate a game plan to see usage analytics.")
    else:
        available = [p for p in enriched if not p.get("archived")]
        usage = compute_usage(game_plan, available)
        qb_usage = compute_qb_usage(game_plan)

        offense_poss = [p for p in game_plan if p["type"] == "Offense"]
        defense_poss = [p for p in game_plan if p["type"] == "Defense"]

        st.markdown("### Summary")
        scols = st.columns(4)
        with scols[0]:
            st.metric("Total Possessions", len(game_plan) // 2)
        with scols[1]:
            st.metric("Offense Possessions", len(offense_poss))
        with scols[2]:
            st.metric("Defense Possessions", len(defense_poss))
        with scols[3]:
            st.metric("QBs Used", len(qb_usage))

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(usage_bar_chart(usage), use_container_width=True)
        with col2:
            st.plotly_chart(qb_usage_pie(qb_usage), use_container_width=True)

        st.markdown("### Player Usage Detail")
        usage_rows = []
        for name, stats in usage.items():
            usage_rows.append({
                "Player": name,
                "Offense %": f"{stats['offense_pct']:.0f}%",
                "Defense %": f"{stats['defense_pct']:.0f}%",
                "Total %": f"{stats['total_pct']:.0f}%",
                "Off Possessions": stats["offense_possessions"],
                "Def Possessions": stats["defense_possessions"],
            })
        st.dataframe(pd.DataFrame(usage_rows), use_container_width=True, hide_index=True)

with tab2:
    if not game_plan:
        st.info("Generate a game plan to see lineup rankings.")
    else:
        st.plotly_chart(lineup_rank_chart(game_plan), use_container_width=True)

        strongest, weakest = find_strongest_weakest(game_plan)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 💪 Strongest Unit")
            if strongest:
                st.success(f"**{strongest['label']}**")
                st.metric("Rank", f"{strongest['lineup_rank']:.1f}  —  {strongest.get('rank_label', '')}")
                for pos, name in strongest["assignment"].items():
                    st.write(f"**{pos}:** {name}")
        with col2:
            st.markdown("### 🔧 Weakest Unit")
            if weakest:
                st.warning(f"**{weakest['label']}**")
                st.metric("Rank", f"{weakest['lineup_rank']:.1f}  —  {weakest.get('rank_label', '')}")
                for pos, name in weakest["assignment"].items():
                    st.write(f"**{pos}:** {name}")

        st.markdown("### 🏆 Player Leaderboard")
        leaderboard = sorted(enriched, key=lambda x: -x.get("composite_rating", 5))
        lb_data = [{
            "Rank": i + 1,
            "Player": p["name"],
            "Composite": f"{p.get('composite_rating', 5):.1f}",
            "Offense": f"{p.get('offense_rating', 5):.1f}",
            "Defense": f"{p.get('defense_rating', 5):.1f}",
            "QB": f"{p.get('qb_rating', 0):.1f}",
        } for i, p in enumerate(leaderboard) if not p.get("archived")]
        st.dataframe(pd.DataFrame(lb_data), use_container_width=True, hide_index=True)

with tab3:
    st.markdown("### 👤 Individual Player Profile")
    active = [p for p in enriched if not p.get("archived")]
    if not active:
        st.info("No active players.")
    else:
        names = [p["name"] for p in active]
        sel_name = st.selectbox("Select Player", names)
        sel_player = next((p for p in active if p["name"] == sel_name), None)

        if sel_player:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Composite Rating", f"{sel_player.get('composite_rating', 5):.1f}")
                st.metric("Offense Rating", f"{sel_player.get('offense_rating', 5):.1f}")
                st.metric("Defense Rating", f"{sel_player.get('defense_rating', 5):.1f}")
                st.metric("QB Rating", f"{sel_player.get('qb_rating', 0):.1f}")
                st.metric("Role Fit", player_role_fit(sel_player))

                if game_plan:
                    available = [p for p in enriched if not p.get("archived")]
                    usage = compute_usage(game_plan, available)
                    if sel_name in usage:
                        u = usage[sel_name]
                        st.metric("Game Usage", f"{u['total_pct']:.0f}%")
                        st.metric("Offense %", f"{u['offense_pct']:.0f}%")
                        st.metric("Defense %", f"{u['defense_pct']:.0f}%")
            with col2:
                st.plotly_chart(player_ratings_radar(sel_player), use_container_width=True)

with tab4:
    st.markdown("### 🔍 Role Fit Analysis")
    active = [p for p in enriched if not p.get("archived")]

    role_data = []
    for p in active:
        best_pos = max(
            ["qb", "rb", "wr", "slot", "center", "olb", "mlb", "cb", "safety", "blitzer"],
            key=lambda pos: p.get(f"{pos}_rating", 0),
        ).upper()
        role_data.append({
            "Player": p["name"],
            "Role Fit": player_role_fit(p),
            "Best Position": best_pos,
            "Composite": f"{p.get('composite_rating', 5):.1f}",
            "Off Rating": f"{p.get('offense_rating', 5):.1f}",
            "Def Rating": f"{p.get('defense_rating', 5):.1f}",
        })

    st.dataframe(pd.DataFrame(role_data), use_container_width=True, hide_index=True)

with tab5:
    st.markdown("### 🪑 Bench Patterns & Sit-Twice Analysis")
    if not game_plan:
        st.info("Generate a game plan to see bench pattern analytics.")
    else:
        available = [p for p in enriched if not p.get("archived")]
        bench_patterns = compute_bench_patterns(game_plan, available)
        violations = check_no_sit_twice_violations(game_plan, available)

        if violations:
            st.error("⚠️ **Sit-Twice Violations Detected!**")
            for v in violations:
                st.warning(f"• {v}")
        else:
            st.success("✅ No sit-twice violations — the no-sit-twice rule is satisfied for all players.")

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(bench_pattern_chart(bench_patterns), use_container_width=True)
        with col2:
            st.plotly_chart(sit_streak_chart(bench_patterns), use_container_width=True)

        st.markdown("### Bench Detail Table")
        bench_rows = []
        for name, data in sorted(bench_patterns.items(),
                                  key=lambda x: -x[1]["total_bench"]):
            bench_rows.append({
                "Player": name,
                "Times Benched": data["total_bench"],
                "Bench %": f"{data['bench_pct']:.0f}%",
                "Max Sit Streak": data["max_consecutive_bench"],
                "Violations": data["consecutive_violations"],
            })
        st.dataframe(pd.DataFrame(bench_rows), use_container_width=True, hide_index=True)

