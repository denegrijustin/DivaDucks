import streamlit as st

def render_summary_cards(game_plan: list, players: list):
    if not game_plan:
        return
    
    offense_poss = [p for p in game_plan if p["type"] == "Offense"]
    defense_poss = [p for p in game_plan if p["type"] == "Defense"]
    
    avg_off_rank = sum(p["lineup_rank"] for p in offense_poss) / max(len(offense_poss), 1)
    avg_def_rank = sum(p["lineup_rank"] for p in defense_poss) / max(len(defense_poss), 1)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Possessions", len(game_plan) // 2)
    with col2:
        st.metric("Avg Offense Rank", f"{avg_off_rank:.1f}")
    with col3:
        st.metric("Avg Defense Rank", f"{avg_def_rank:.1f}")
    with col4:
        active = [p for p in players if p.get("available") and not p.get("injured")]
        st.metric("Active Players", len(active))
