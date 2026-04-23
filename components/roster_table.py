import streamlit as st
import pandas as pd
from utils.constants import DERIVED_RATINGS

def render_roster_table(players: list, show_ratings: bool = True):
    if not players:
        st.warning("No players to display.")
        return
    
    display_cols = ["name", "jersey_number", "available", "qb_eligible", "injured"]
    if show_ratings:
        display_cols += ["offense_rating", "defense_rating", "composite_rating"]
    
    df_data = []
    for p in players:
        row = {
            "Name": p.get("name", ""),
            "Jersey": p.get("jersey_number", ""),
            "Available": "✅" if p.get("available") else "❌",
            "QB": "✅" if p.get("qb_eligible") else "—",
            "Injured": "🚑" if p.get("injured") else "—",
        }
        if show_ratings:
            row["Off ⭐"] = f"{p.get('offense_rating', 5.0):.1f}"
            row["Def ⭐"] = f"{p.get('defense_rating', 5.0):.1f}"
            row["Composite"] = f"{p.get('composite_rating', 5.0):.1f}"
        df_data.append(row)
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
