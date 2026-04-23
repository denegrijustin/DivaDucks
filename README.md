# 🦆 Diva Ducks — CYO Flag Football Coaching App

A modular Streamlit coaching app for 3rd/4th grade girls CYO flag football.

## Features
- Player profile management with skill ratings
- Game-day availability tracking
- QB assignment with half-based rotation
- Offensive and defensive lineup generation (3 modes)
- Live game possession navigator
- Analytics: usage, rankings, role fit, leaderboards
- 3-page PDF game plan export with Diva Ducks branding
- Persistent JSON storage

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure

```
app.py                    # Main entry point
pages/
  1_Player_Management.py  # Edit roster, ratings, availability
  2_Game_Planner.py       # Generate game plan
  3_Live_Game_View.py     # Sideline navigator
  4_Analytics.py          # Charts and stats
  5_Settings.py           # Game rules and weights
  6_Export_PDF.py         # PDF export
components/               # Shared UI components
utils/                    # Business logic and data
data/                     # JSON persistence
assets/                   # Logo and static files
```

## Team
**Diva Ducks** — Green (#2E7D32), Black (#000000), Red (#C62828)

## Default Roster
Katrina, Sophia, Olivia, Francie, Eva, Quinn, Isla, Timber, Adriana, Felicity