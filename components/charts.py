import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any

# Logo-matched palette
COLORS = {
    "crimson":       "#B31B1B",
    "crimson_light": "#D94040",
    "forest":        "#1A5C1A",
    "forest_light":  "#2E8B2E",
    "gold":          "#C9A84C",
    "dark":          "#111111",
    "cream":         "#F2E8C8",
    "white":         "#FFFFFF",
    "bg_dark":       "#0E1210",
    "bg_card":       "#1A1E1A",
}

def _base_layout(**extra) -> dict:
    return dict(
        paper_bgcolor=COLORS["bg_dark"],
        plot_bgcolor=COLORS["bg_card"],
        font=dict(color=COLORS["cream"], size=12),
        legend=dict(bgcolor=COLORS["bg_card"], font=dict(color=COLORS["cream"])),
        xaxis=dict(gridcolor="#2A2A2A", tickfont=dict(color=COLORS["cream"])),
        yaxis=dict(gridcolor="#2A2A2A", tickfont=dict(color=COLORS["cream"])),
        **extra,
    )

def usage_bar_chart(usage: Dict[str, Any]) -> go.Figure:
    if not usage:
        return go.Figure()

    names = list(usage.keys())
    offense_pcts = [usage[n]["offense_pct"] for n in names]
    defense_pcts = [usage[n]["defense_pct"] for n in names]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Offense %", x=names, y=offense_pcts,
                         marker_color=COLORS["forest_light"],
                         marker_line_color=COLORS["gold"], marker_line_width=0.8))
    fig.add_trace(go.Bar(name="Defense %", x=names, y=defense_pcts,
                         marker_color=COLORS["crimson"],
                         marker_line_color=COLORS["gold"], marker_line_width=0.8))

    fig.update_layout(
        barmode="group",
        title=dict(text="Player Usage by Phase", font=dict(color=COLORS["cream"], size=15)),
        xaxis_tickangle=-30,
        **_base_layout(),
    )
    return fig

def lineup_rank_chart(game_plan: list) -> go.Figure:
    if not game_plan:
        return go.Figure()

    labels = [p["label"] for p in game_plan]
    ranks = [p["lineup_rank"] for p in game_plan]
    colors_list = [COLORS["forest_light"] if p["type"] == "Offense" else COLORS["crimson"]
                   for p in game_plan]

    fig = go.Figure(go.Bar(x=labels, y=ranks, marker_color=colors_list,
                           marker_line_color=COLORS["gold"], marker_line_width=1))
    fig.update_layout(
        title=dict(text="Lineup Rank per Possession", font=dict(color=COLORS["cream"], size=15)),
        xaxis_tickangle=-45,
        **_base_layout(),
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
        line_color=COLORS["gold"],
        fillcolor=COLORS["crimson"],
        opacity=0.55,
    ))
    fig.update_layout(
        polar=dict(
            bgcolor=COLORS["bg_card"],
            radialaxis=dict(visible=True, range=[0, 10], color=COLORS["gold"],
                            gridcolor="#3A3A3A"),
            angularaxis=dict(color=COLORS["cream"]),
        ),
        paper_bgcolor=COLORS["bg_dark"],
        font=dict(color=COLORS["cream"]),
        title=dict(text=f"{player.get('name', 'Player')} — Skills Radar",
                   font=dict(color=COLORS["cream"], size=14)),
    )
    return fig

def qb_usage_pie(qb_usage: Dict[str, int]) -> go.Figure:
    if not qb_usage:
        return go.Figure()
    names = list(qb_usage.keys())
    values = list(qb_usage.values())
    pie_colors = [COLORS["crimson"], COLORS["forest_light"], COLORS["gold"],
                  COLORS["crimson_light"], COLORS["forest"]]
    fig = go.Figure(go.Pie(
        labels=names, values=values, hole=0.45,
        marker=dict(colors=pie_colors[:len(names)],
                    line=dict(color=COLORS["gold"], width=2)),
        textfont=dict(color=COLORS["cream"]),
    ))
    fig.update_layout(
        title=dict(text="QB Possession Share", font=dict(color=COLORS["cream"], size=15)),
        paper_bgcolor=COLORS["bg_dark"],
        font=dict(color=COLORS["cream"]),
        legend=dict(font=dict(color=COLORS["cream"])),
    )
    return fig

def bench_pattern_chart(bench_patterns: Dict[str, Any]) -> go.Figure:
    """
    Stacked bar chart showing total bench count and violation count per player.
    """
    if not bench_patterns:
        return go.Figure()

    names = sorted(bench_patterns.keys(),
                   key=lambda n: bench_patterns[n]["total_bench"], reverse=True)
    total_bench = [bench_patterns[n]["total_bench"] for n in names]
    violations = [bench_patterns[n]["consecutive_violations"] for n in names]
    bench_pct = [bench_patterns[n]["bench_pct"] for n in names]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Times Benched", x=names, y=total_bench,
        marker_color=COLORS["forest_light"],
        marker_line_color=COLORS["gold"], marker_line_width=0.8,
        text=[f"{p:.0f}%" for p in bench_pct],
        textposition="outside",
        textfont=dict(color=COLORS["cream"]),
    ))
    fig.add_trace(go.Bar(
        name="Consecutive-Sit Violations", x=names, y=violations,
        marker_color=COLORS["crimson"],
        marker_line_color=COLORS["gold"], marker_line_width=0.8,
    ))

    fig.update_layout(
        barmode="group",
        title=dict(text="Bench Load & Violation Count per Player",
                   font=dict(color=COLORS["cream"], size=15)),
        xaxis_tickangle=-30,
        **_base_layout(),
    )
    return fig

def sit_streak_chart(bench_patterns: Dict[str, Any]) -> go.Figure:
    """Bar chart of max consecutive bench streak per player."""
    if not bench_patterns:
        return go.Figure()

    names = sorted(bench_patterns.keys(),
                   key=lambda n: bench_patterns[n]["max_consecutive_bench"], reverse=True)
    max_streaks = [bench_patterns[n]["max_consecutive_bench"] for n in names]
    bar_colors = [
        COLORS["crimson"] if s >= 2 else COLORS["forest_light"]
        for s in max_streaks
    ]

    fig = go.Figure(go.Bar(
        x=names, y=max_streaks, marker_color=bar_colors,
        marker_line_color=COLORS["gold"], marker_line_width=0.8,
        text=max_streaks, textposition="outside",
        textfont=dict(color=COLORS["cream"]),
    ))
    fig.add_hline(y=1.5, line_dash="dash", line_color=COLORS["gold"],
                  annotation_text="Violation threshold",
                  annotation_font_color=COLORS["gold"])
    fig.update_layout(
        title=dict(text="Max Consecutive Bench Streak per Player",
                   font=dict(color=COLORS["cream"], size=15)),
        xaxis_tickangle=-30,
        **_base_layout(),
    )
    return fig
