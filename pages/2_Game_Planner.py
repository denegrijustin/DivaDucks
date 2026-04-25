import streamlit as st
from utils.branding import get_css, render_header
from utils.persistence import load_players, load_settings, save_players, save_settings
from utils.rating_engine import enrich_players
from utils.lineup_engine import generate_game_plans, select_qbs, repair_game_plan
from utils.validation import (
    validate_game_plan_inputs,
    validate_full_sit_flow,
    validate_offense_to_defense_no_repeat_sits,
    validate_defense_to_next_offense_no_repeat_sits,
)
from utils.analytics_engine import (
    compute_usage, compute_qb_usage, check_no_sit_twice_violations
)
from components.lineup_display import render_possession_card
from components.summary_cards import render_summary_cards
from components.validation_messages import show_errors, show_warnings, show_success

st.set_page_config(page_title="Game Planner | Diva Ducks", page_icon="🦆", layout="wide")
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
if "rules_check_offense" not in st.session_state:
    st.session_state.rules_check_offense = None
if "rules_check_defense" not in st.session_state:
    st.session_state.rules_check_defense = None
if "repair_warnings_offense" not in st.session_state:
    st.session_state.repair_warnings_offense = []
if "repair_warnings_defense" not in st.session_state:
    st.session_state.repair_warnings_defense = []

players = st.session_state.players
settings = st.session_state.settings
enriched = enrich_players(players, settings)

st.markdown(render_header("Game Planner"), unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎮 Game Setup")

    planning_mode = st.selectbox(
        "Planning Mode",
        ["Fair Rotation", "Balanced", "Must-Win"],
        index=["Fair Rotation", "Balanced", "Must-Win"].index(
            settings.get("planning_mode", "Fair Rotation")
        ),
    )

    st.markdown("### 👥 Player Availability")
    qcols = st.columns(2)
    with qcols[0]:
        if st.button("✅ All Available", use_container_width=True):
            for p in players:
                if not p.get("injured") and not p.get("archived"):
                    p["available"] = True
            save_players(players)
            st.session_state.players = players
            st.rerun()
    with qcols[1]:
        if st.button("❌ Clear All", use_container_width=True):
            for p in players:
                p["available"] = False
            save_players(players)
            st.session_state.players = players
            st.rerun()

    active = [p for p in enriched if not p.get("archived") and not p.get("injured")]

    st.markdown("**Select Available Players:**")
    availability: dict = {}
    for p in active:
        availability[p["id"]] = st.checkbox(
            f"#{p.get('jersey_number', '?')} {p['name']}",
            value=p.get("available", True),
            key=f"avail_{p['id']}",
        )

    st.markdown("### 🏈 QB Selection")
    if st.button("⭐ Recommend Best 2 QBs"):
        qb_pool = sorted(
            [p for p in active if p.get("can_play_qb")],
            key=lambda x: -x.get("qb_rating", 0),
        )
        st.session_state["recommended_qb_ids"] = [p["id"] for p in qb_pool[:2]]

    if st.button("✖️ Clear QB Selections"):
        st.session_state["recommended_qb_ids"] = []

    recommended_ids = st.session_state.get("recommended_qb_ids", [])
    qb_eligible_map: dict = {}
    for p in active:
        default_qb = p.get("qb_eligible", False) or p["id"] in recommended_ids
        qb_eligible_map[p["id"]] = st.checkbox(
            f"QB: {p['name']}",
            value=default_qb,
            key=f"qb_{p['id']}",
        )

# Apply sidebar selections
for p in players:
    if p["id"] in availability:
        p["available"] = availability[p["id"]]
    if p["id"] in qb_eligible_map:
        p["qb_eligible"] = qb_eligible_map[p["id"]]

available_players = [
    p for p in enriched
    if availability.get(p["id"], p.get("available", True))
    and not p.get("archived")
    and not p.get("injured")
]
qb_eligible_ids = [pid for pid, eligible in qb_eligible_map.items() if eligible]

# ── Main layout ──────────────────────────────────────────────────────────────
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

    valid, errors = validate_game_plan_inputs(available_players, qb_eligible_ids, settings)
    if errors:
        show_errors(errors)

    if st.button("🚀 Generate Both Game Plans", use_container_width=True, disabled=not valid):
        qb1, qb2 = select_qbs(available_players, qb_eligible_ids)
        if qb1 and qb2:
            plans = generate_game_plans(
                available_players,
                qb1["id"],
                qb2["id"],
                settings,
                mode=planning_mode,
            )

            # Attempt repair for both plans
            repaired_off, warn_off = repair_game_plan(plans["offense_first"], available_players)
            repaired_def, warn_def = repair_game_plan(plans["defense_first"], available_players)

            st.session_state.game_plan_offense_first = repaired_off
            st.session_state.game_plan_defense_first = repaired_def
            st.session_state.repair_warnings_offense = warn_off
            st.session_state.repair_warnings_defense = warn_def
            # Default active plan = offense first
            st.session_state.game_plan = repaired_off
            st.session_state.current_possession_idx = 0

            # Run full rules check
            off_pass, off_viols = validate_full_sit_flow(repaired_off)
            def_pass, def_viols = validate_full_sit_flow(repaired_def)
            st.session_state.rules_check_offense = {"pass": off_pass, "violations": off_viols}
            st.session_state.rules_check_defense = {"pass": def_pass, "violations": def_viols}

            st.rerun()
        else:
            show_errors(["Could not determine QB assignments."])

    has_plans = bool(st.session_state.game_plan_offense_first)
    if has_plans:
        usage = compute_usage(st.session_state.game_plan, available_players)
        qb_usage = compute_qb_usage(st.session_state.game_plan)

        st.markdown("### 📊 QB Plan")
        for name, count in qb_usage.items():
            st.metric(f"QB: {name}", f"{count} possessions")

        render_summary_cards(st.session_state.game_plan, available_players)

        # ── Rules Check Section ───────────────────────────────────────────
        st.markdown("---")
        st.markdown("### �� Rules Check")

        def _render_rules_check(plan_label: str, rules_result: dict, repair_warnings: list):
            if rules_result is None:
                st.info(f"Rules check pending for {plan_label}.")
                return False

            off_d_viols = validate_offense_to_defense_no_repeat_sits(
                st.session_state.game_plan_offense_first
                if plan_label == "Offense-First"
                else st.session_state.game_plan_defense_first
            )
            def_o_viols = validate_defense_to_next_offense_no_repeat_sits(
                st.session_state.game_plan_offense_first
                if plan_label == "Offense-First"
                else st.session_state.game_plan_defense_first
            )
            full_pass = rules_result["pass"]
            all_viols = rules_result["violations"]

            off_d_pass = len(off_d_viols) == 0
            def_o_pass = len(def_o_viols) == 0

            st.markdown(f"**{plan_label}**")
            col1, col2, col3 = st.columns(3)
            with col1:
                if off_d_pass:
                    st.success("✔ Off→Def: Pass")
                else:
                    st.error("✘ Off→Def: Fail")
            with col2:
                if def_o_pass:
                    st.success("✔ Def→Off: Pass")
                else:
                    st.error("✘ Def→Off: Fail")
            with col3:
                if full_pass:
                    st.success("✔ Full Flow: Pass")
                else:
                    st.error("✘ Full Flow: Fail")

            if all_viols:
                with st.expander(f"⚠️ {len(all_viols)} violation(s) — click to expand"):
                    for v in all_viols:
                        st.warning(v)

            if repair_warnings:
                with st.expander(f"🔧 {len(repair_warnings)} repair note(s)"):
                    for w in repair_warnings:
                        st.info(w)

            return full_pass

        off_check = st.session_state.rules_check_offense
        def_check = st.session_state.rules_check_defense
        warn_off = st.session_state.repair_warnings_offense
        warn_def = st.session_state.repair_warnings_defense

        off_rules_pass = _render_rules_check("Offense-First", off_check, warn_off)
        st.markdown("")
        def_rules_pass = _render_rules_check("Defense-First", def_check, warn_def)

        all_rules_pass = off_rules_pass and def_rules_pass
        if not all_rules_pass and (off_check is not None or def_check is not None):
            st.error("🚫 One or more hard rules failed. Fix violations before exporting.")
        elif all_rules_pass:
            st.success("✅ All hard rules passed. Plans are valid for export.")

with col_preview:
    has_plans = bool(st.session_state.game_plan_offense_first)

    # Determine if rules passed (gating)
    off_check = st.session_state.rules_check_offense
    def_check = st.session_state.rules_check_defense
    rules_passed = (
        off_check is not None and off_check["pass"]
        and def_check is not None and def_check["pass"]
    )

    if has_plans:
        st.markdown("### 📋 Game Plan Preview")

        if not rules_passed and off_check is not None:
            st.warning("⚠️ Hard rules have violations. Lineup display is shown below but PDF export is blocked until all rules pass.")

        version_tabs = st.tabs(["🏈 Offense First", "🛡️ Defense First"])

        for v_idx, (v_tab, v_key, v_label) in enumerate(zip(
            version_tabs,
            ["game_plan_offense_first", "game_plan_defense_first"],
            ["Offense-First", "Defense-First"],
        )):
            with v_tab:
                plan = st.session_state[v_key]
                if st.button(
                    f"Set as Active Plan ({v_label})",
                    key=f"set_active_{v_idx}",
                    use_container_width=True,
                ):
                    st.session_state.game_plan = plan
                    st.session_state.current_possession_idx = 0
                    show_success(f"{v_label} set as active plan for Live View & Analytics.")
                    st.rerun()

                half_tabs = st.tabs(["1st Half", "2nd Half"])
                for half_idx, half_tab in enumerate(half_tabs):
                    with half_tab:
                        half_num = half_idx + 1
                        half_plan = [p for p in plan if p["half"] == half_num]
                        for poss in half_plan:
                            render_possession_card(poss, expanded=(half_idx == 0))
    else:
        st.info("👈 Configure your game plan and click Generate.")
        st.markdown("""
        **How to use:**
        1. Select available players in the sidebar
        2. Mark QB-eligible players
        3. Choose a planning mode
        4. Click **Generate Both Game Plans**
        5. Two versions are created: **Offense First** and **Defense First**
        6. Set one as active to use in the Live Game View
        """)
