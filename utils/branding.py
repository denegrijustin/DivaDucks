"""
Branding helpers — all colors pulled from the Diva Ducks logo image.

Logo palette:
  Crimson  #B31B1B   shield, helmet, jersey red
  Forest   #1A5C1A   duck body, shield green patches
  Gold     #C9A84C   text outlines, helmet trim, jersey detail
  Dark     #111111   banner background
  Cream    #F2E8C8   DIVA DUCKS lettering
"""
import base64, os
from utils.constants import TEAM_COLORS, TEAM_NAME

C = TEAM_COLORS   # short alias

# ---------------------------------------------------------------------------
# Logo helpers
# ---------------------------------------------------------------------------
def _logo_b64() -> str:
    logo_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "assets", "diva_ducks_logo.png"
    )
    try:
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return ""

def logo_img_tag(height: int = 90) -> str:
    b64 = _logo_b64()
    if not b64:
        return "<span style='font-size:3rem;'>🦆</span>"
    return f'<img src="data:image/png;base64,{b64}" height="{height}" style="display:block;" alt="Diva Ducks Logo">'

# ---------------------------------------------------------------------------
# Global CSS — dark theme using logo palette
# ---------------------------------------------------------------------------
def get_css() -> str:
    return f"""
<style>
/* ── Background ─────────────────────────────────────────────── */
.stApp {{
    background-color: {C['bg_dark']};
    color: {C['cream']};
}}

/* ── Sidebar ─────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {C['dark']} 0%, {C['bg_card']} 100%);
    border-right: 3px solid {C['crimson']};
}}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label {{
    color: {C['cream']} !important;
}}

/* ── Headings ─────────────────────────────────────────────────── */
h1 {{ color: {C['cream']}   !important; }}
h2 {{ color: {C['gold']}    !important; }}
h3 {{ color: {C['cream']}   !important; }}
p, li {{ color: {C['off_white']}; }}

/* ── Metrics ──────────────────────────────────────────────────── */
[data-testid="stMetricValue"] {{
    color: {C['gold']} !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
}}
[data-testid="stMetricLabel"] {{
    color: {C['cream']} !important;
}}

/* ── Primary buttons ──────────────────────────────────────────── */
.stButton > button {{
    background: linear-gradient(135deg, {C['crimson']} 0%, {C['crimson_dark']} 100%);
    color: {C['cream']};
    border: 2px solid {C['gold']};
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.95rem;
    padding: 0.5rem 1.5rem;
    transition: all 0.2s ease;
}}
.stButton > button:hover {{
    background: linear-gradient(135deg, {C['crimson_light']} 0%, {C['crimson']} 100%);
    border-color: {C['cream']};
    color: {C['white']};
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(179,27,27,0.5);
}}

/* ── Tabs ─────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    background: {C['bg_card']};
    border-radius: 8px 8px 0 0;
    border-bottom: 2px solid {C['gold']};
    gap: 4px;
}}
.stTabs [data-baseweb="tab"] {{
    color: {C['cream']};
    font-weight: 600;
    padding: 0.6rem 1.2rem;
    border-radius: 6px 6px 0 0;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(180deg, {C['crimson']} 0%, {C['crimson_dark']} 100%) !important;
    color: {C['cream']} !important;
    border-bottom: 3px solid {C['gold']} !important;
}}

/* ── Expanders ────────────────────────────────────────────────── */
.streamlit-expanderHeader {{
    background: {C['bg_card']};
    border-left: 4px solid {C['gold']};
    color: {C['cream']} !important;
    font-weight: 600;
    border-radius: 4px;
}}

/* ── Data tables ──────────────────────────────────────────────── */
.stDataFrame {{
    border: 1px solid {C['gold']};
    border-radius: 8px;
}}
[data-testid="stTable"] th {{
    background: {C['crimson']} !important;
    color: {C['cream']} !important;
}}

/* ── Inputs & selects ─────────────────────────────────────────── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stNumberInput > div > div > input {{
    background: {C['bg_card']};
    color: {C['cream']};
    border: 1px solid {C['gold_dark']};
    border-radius: 6px;
}}
.stSlider > div > div > div > div {{
    background: {C['crimson']} !important;
}}

/* ── Alerts ───────────────────────────────────────────────────── */
.stAlert[data-baseweb="notification"] {{
    border-radius: 8px;
}}

/* ── Custom card classes ──────────────────────────────────────── */
.dd-card {{
    background: {C['bg_card']};
    border-left: 4px solid {C['crimson']};
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
}}
.dd-card-gold {{
    background: {C['bg_card']};
    border-left: 4px solid {C['gold']};
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
}}
.dd-card-green {{
    background: {C['bg_card']};
    border-left: 4px solid {C['forest']};
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
}}

/* ── Possession cards ─────────────────────────────────────────── */
.poss-card {{
    background: {C['bg_card']};
    border: 2px solid {C['gold']};
    border-radius: 12px;
    padding: 1.2rem;
    margin: 0.8rem 0;
}}
.poss-offense {{ border-color: {C['forest']}; }}
.poss-defense {{ border-color: {C['crimson']}; }}

.pos-row {{
    display: flex;
    justify-content: space-between;
    padding: 3px 0;
    border-bottom: 1px solid #2A2A2A;
}}
.pos-label {{
    color: {C['gold']};
    font-weight: 700;
    min-width: 90px;
    font-size: 0.9rem;
}}
.pos-name {{
    color: {C['cream']};
    font-size: 0.9rem;
}}
</style>
"""

# ---------------------------------------------------------------------------
# Page header HTML — logo left, title centre, badge right
# ---------------------------------------------------------------------------
def render_header(subtitle: str = "") -> str:
    logo_tag = logo_img_tag(height=80)
    sub_html = (
        f'<div style="color:{C["gold"]};font-size:0.85rem;letter-spacing:2px;'
        f'text-transform:uppercase;margin-top:2px;">🏈 {subtitle}</div>'
        if subtitle else ""
    )
    return (
        f'<div style="background:linear-gradient(135deg,{C["dark"]} 0%,{C["bg_card"]} 40%,{C["forest_dark"]} 100%);'
        f'border-bottom:4px solid {C["crimson"]};border-top:2px solid {C["gold"]};'
        f'padding:0.8rem 1.6rem;margin-bottom:1.2rem;border-radius:0 0 16px 16px;'
        f'display:flex;align-items:center;gap:1.2rem;">'

        f'<div style="flex-shrink:0;">{logo_tag}</div>'

        f'<div style="flex:1;">'
        f'<div style="font-size:1.9rem;font-weight:900;color:{C["cream"]};'
        f'text-shadow:2px 2px 6px {C["dark"]};letter-spacing:1px;line-height:1.1;">'
        f'{TEAM_NAME.upper()}</div>'
        f'<div style="color:{C["forest_light"]};font-size:0.75rem;letter-spacing:3px;font-weight:600;">'
        f'CYO FLAG FOOTBALL · COACHING COMMAND CENTER</div>'
        f'{sub_html}'
        f'</div>'

        f'<div style="background:linear-gradient(135deg,{C["crimson_dark"]} 0%,{C["crimson"]} 100%);'
        f'border:2px solid {C["gold"]};border-radius:10px;padding:0.5rem 1rem;'
        f'text-align:center;flex-shrink:0;">'
        f'<div style="color:{C["gold"]};font-weight:800;font-size:1.1rem;">DIVA</div>'
        f'<div style="color:{C["cream"]};font-size:0.7rem;letter-spacing:2px;">DUCKS</div>'
        f'</div>'

        f'</div>'
    )
