from utils.constants import TEAM_COLORS, TEAM_NAME

def get_css() -> str:
    colors = TEAM_COLORS
    return f"""
<style>
    /* Main app background */
    .stApp {{
        background-color: {colors['bg_dark']};
        color: {colors['white']};
    }}
    
    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {{
        background-color: {colors['bg_card']};
    }}
    
    /* Metric cards */
    [data-testid="stMetricValue"] {{
        color: {colors['light_green']} !important;
        font-size: 2rem !important;
    }}
    
    /* Headers */
    h1, h2, h3 {{
        color: {colors['white']} !important;
    }}
    
    /* Buttons */
    .stButton > button {{
        background-color: {colors['green']};
        color: {colors['white']};
        border: none;
        border-radius: 8px;
        font-weight: bold;
        font-size: 1rem;
        padding: 0.5rem 1.5rem;
    }}
    
    .stButton > button:hover {{
        background-color: {colors['light_green']};
        color: {colors['black']};
    }}
    
    /* Cards */
    .duck-card {{
        background-color: {colors['bg_card']};
        border-left: 4px solid {colors['green']};
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }}
    
    /* Danger cards */
    .duck-card-danger {{
        background-color: {colors['bg_card']};
        border-left: 4px solid {colors['red']};
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }}
    
    /* Success */
    .duck-success {{
        color: {colors['light_green']};
        font-weight: bold;
    }}
    
    /* Warning */
    .duck-warning {{
        color: {colors['gold']};
        font-weight: bold;
    }}
    
    /* Tables */
    .stDataFrame {{
        border-radius: 8px;
    }}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab"] {{
        color: {colors['white']};
        font-weight: bold;
    }}
    
    .stTabs [aria-selected="true"] {{
        border-bottom-color: {colors['green']} !important;
        color: {colors['light_green']} !important;
    }}
    
    /* Possession cards */
    .possession-card {{
        background: linear-gradient(135deg, {colors['bg_card']} 0%, #1E2A3A 100%);
        border: 2px solid {colors['green']};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }}
    
    .possession-header {{
        color: {colors['light_green']};
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }}
    
    .player-position {{
        display: flex;
        justify-content: space-between;
        padding: 0.25rem 0;
        border-bottom: 1px solid #2A2F3E;
    }}
    
    .pos-label {{
        color: {colors['gold']};
        font-weight: bold;
        min-width: 80px;
    }}
    
    .player-name {{
        color: {colors['white']};
    }}
</style>
"""

def render_header(subtitle: str = "") -> str:
    colors = TEAM_COLORS
    duck_emoji = "🦆"
    return f"""
<div style="
    background: linear-gradient(135deg, {colors['dark_green']} 0%, {colors['bg_card']} 50%, {colors['black']} 100%);
    border-bottom: 3px solid {colors['green']};
    padding: 1rem 2rem;
    margin-bottom: 1.5rem;
    border-radius: 0 0 12px 12px;
">
    <div style="display: flex; align-items: center; gap: 1rem;">
        <div style="font-size: 3rem;">{duck_emoji}</div>
        <div>
            <h1 style="color: {colors['white']}; margin: 0; font-size: 2rem; text-shadow: 2px 2px 4px {colors['black']};">
                {TEAM_NAME}
            </h1>
            <div style="color: {colors['light_green']}; font-size: 0.9rem; letter-spacing: 2px;">
                🏈 COACHING COMMAND CENTER {('— ' + subtitle) if subtitle else ''}
            </div>
        </div>
    </div>
</div>
"""
