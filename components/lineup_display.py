import streamlit as st
from utils.constants import TEAM_COLORS

C = TEAM_COLORS

def render_possession_card(possession: dict, expanded: bool = True):
    is_offense = possession["type"] == "Offense"
    border_color = C["forest"] if is_offense else C["crimson"]
    header_bg    = C["forest_dark"] if is_offense else C["crimson_dark"]
    phase_label  = "OFFENSE" if is_offense else "DEFENSE"
    icon         = "🏈" if is_offense else "🛡️"
    rank         = possession["lineup_rank"]

    label = f"{icon} {possession['label']}  |  Rank: {rank:.1f}  |  {phase_label}"

    with st.expander(label, expanded=expanded):
        assignment = possession.get("assignment", {})
        items = list(assignment.items())
        half  = (len(items) + 1) // 2

        col1, col2 = st.columns(2)

        def _row(pos, name):
            return (
                f'<div style="display:flex;justify-content:space-between;'
                f'padding:5px 8px;border-bottom:1px solid #2A2A2A;border-radius:3px;">'
                f'<span style="color:{C["gold"]};font-weight:700;min-width:80px;">{pos}</span>'
                f'<span style="color:{C["cream"]};">{name}</span>'
                f'</div>'
            )

        with col1:
            html = "".join(_row(p, n) for p, n in items[:half])
            st.markdown(
                f'<div style="background:{C["bg_card"]};border-left:3px solid {border_color};'
                f'border-radius:6px;padding:4px;">{html}</div>',
                unsafe_allow_html=True
            )

        with col2:
            html = "".join(_row(p, n) for p, n in items[half:])
            if html:
                st.markdown(
                    f'<div style="background:{C["bg_card"]};border-left:3px solid {border_color};'
                    f'border-radius:6px;padding:4px;">{html}</div>',
                    unsafe_allow_html=True
                )

        if possession.get("players_out"):
            st.markdown(
                f'<div style="color:{C["gold_dark"]};font-size:0.82rem;margin-top:6px;">'
                f'<b>Out:</b> {", ".join(possession["players_out"])}</div>',
                unsafe_allow_html=True
            )
        if possession.get("notes"):
            st.info(possession["notes"])

