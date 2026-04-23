import streamlit as st
from utils.constants import TEAM_COLORS

def render_possession_card(possession: dict, expanded: bool = True):
    colors = TEAM_COLORS
    is_offense = possession["type"] == "Offense"
    border_color = colors["green"] if is_offense else colors["red"]
    icon = "🏈" if is_offense else "🛡️"
    
    with st.expander(f"{icon} {possession['label']} | Rank: {possession['lineup_rank']:.1f}", expanded=expanded):
        assignment = possession.get("assignment", {})
        
        col1, col2 = st.columns(2)
        items = list(assignment.items())
        half = (len(items) + 1) // 2
        
        with col1:
            for pos, name in items[:half]:
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid #2A2F3E;">
                    <span style="color:#FFC107; font-weight:bold; min-width:80px;">{pos}</span>
                    <span style="color:#FFFFFF;">{name}</span>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            for pos, name in items[half:]:
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid #2A2F3E;">
                    <span style="color:#FFC107; font-weight:bold; min-width:80px;">{pos}</span>
                    <span style="color:#FFFFFF;">{name}</span>
                </div>
                """, unsafe_allow_html=True)
        
        if possession.get("players_out"):
            st.markdown(f"**Players Out:** {', '.join(possession['players_out'])}")
        if possession.get("notes"):
            st.info(possession["notes"])
