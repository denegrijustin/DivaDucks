import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any

COLORS = {
    "green": "#2E7D32",
    "light_green": "#4CAF50",
    "red": "#C62828",
    "gold": "#FFC107",
    "white": "#FFFFFF",
    "bg_dark": "#0D1117",
    "bg_card": "#1A1F2E",
}

def usage_bar_chart(usage: Dict[str, Any]) -> go.Figure:
    if not usage:
        return go.Figure()
    
    names = list(usage.keys())
    offense_pcts = [usage[n]["offense_pct"] for n in names]
    defense_pcts = [usage[n]["defense_pct"] for n in names]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Offense %", x=names, y=offense_pcts, marker_color=COLORS["light_green"]))
    fig.add_trace(go.Bar(name="Defense %", x=names, y=defense_pcts, marker_color=COLORS["red"]))
    
    fig.update_layout(
        barmode="group",
        title="Player Usage by Phase",
        paper_bgcolor=COLORS["bg_dark"],
        plot_bgcolor=COLORS["bg_card"],
        font_color=COLORS["white"],
        legend=dict(bgcolor=COLORS["bg_card"]),
        xaxis_tickangle=-30,
    )
    return fig

def lineup_rank_chart(game_plan: list) -> go.Figure:
    if not game_plan:
        return go.Figure()
    
    labels = [p["label"] for p in game_plan]
    ranks = [p["lineup_rank"] for p in game_plan]
    colors_list = [COLORS["light_green"] if p["type"] == "Offense" else COLORS["red"] for p in game_plan]
    
    fig = go.Figure(go.Bar(x=labels, y=ranks, marker_color=colors_list))
    fig.update_layout(
        title="Lineup Rank per Possession",
        paper_bgcolor=COLORS["bg_dark"],
        plot_bgcolor=COLORS["bg_card"],
        font_color=COLORS["white"],
        xaxis_tickangle=-30,
    )
    return fig

def player_ratings_radar(player: Dict) -> go.Figure:
    categories = ["Speed", "Hands", "Defense IQ", "Throwing", "Leadership", "Awareness"]
    keys = ["speed", "hands", "defense_iq", "throwing", "leadership", "awareness"]
    values = [player.get(k, 5) for k in keys]
    values.append(values[0])
    categories.append(categories[0])
    
    fig = go.Figure(go.Scatterpolar(
        r=values,
        theta=categories,
        fill="toself",
        name=player.get("name", "Player"),
        line_color=COLORS["light_green"],
        fillcolor=COLORS["light_green"],
        opacity=0.5,
    ))
    fig.update_layout(
        polar=dict(bgcolor=COLORS["bg_card"], radialaxis=dict(visible=True, range=[0, 10])),
        paper_bgcolor=COLORS["bg_dark"],
        font_color=COLORS["white"],
        title=f"{player.get('name', 'Player')} - Skills Radar",
    )
    return fig

def qb_usage_pie(qb_usage: Dict[str, int]) -> go.Figure:
    if not qb_usage:
        return go.Figure()
    names = list(qb_usage.keys())
    values = list(qb_usage.values())
    fig = go.Figure(go.Pie(labels=names, values=values, hole=0.4))
    fig.update_layout(
        title="QB Possession Share",
        paper_bgcolor=COLORS["bg_dark"],
        font_color=COLORS["white"],
    )
    return fig
