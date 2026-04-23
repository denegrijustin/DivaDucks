import streamlit as st
from utils.branding import get_css, render_header
from utils.persistence import load_players, save_players
from utils.rating_engine import enrich_players
from utils.validation import validate_players
from utils.data_models import default_player
from utils.constants import DEFAULT_ROSTER_NAMES
from components.header_branding import show_header
from components.player_editor import render_player_editor
from components.roster_table import render_roster_table
from components.validation_messages import show_warnings, show_errors, show_success

st.set_page_config(page_title="Player Management | Diva Ducks", page_icon="🦆", layout="wide")
st.markdown(get_css(), unsafe_allow_html=True)

# Load state
if "players" not in st.session_state:
    st.session_state.players = load_players()
if "settings" not in st.session_state:
    from utils.persistence import load_settings
    st.session_state.settings = load_settings()

players = st.session_state.players
settings = st.session_state.settings

st.markdown(render_header("Player Management"), unsafe_allow_html=True)

# Warnings
enriched = enrich_players(players, settings)
warnings = validate_players(enriched)
if warnings:
    show_warnings(warnings)

# Quick actions
st.markdown("### ⚡ Quick Actions")
qcols = st.columns(4)
with qcols[0]:
    if st.button("✅ Set All Available", use_container_width=True):
        for p in players:
            if not p.get("injured") and not p.get("archived"):
                p["available"] = True
        save_players(players)
        st.session_state.players = players
        show_success("All players set as available.")
        st.rerun()

with qcols[1]:
    if st.button("❌ Clear All Available", use_container_width=True):
        for p in players:
            p["available"] = False
        save_players(players)
        st.session_state.players = players
        show_success("All availability cleared.")
        st.rerun()

with qcols[2]:
    if st.button("🏈 Clear QB Selections", use_container_width=True):
        for p in players:
            p["qb_eligible"] = False
        save_players(players)
        st.session_state.players = players
        show_success("All QB selections cleared.")
        st.rerun()

with qcols[3]:
    if st.button("🔄 Reset Roster", use_container_width=True):
        if st.session_state.get("confirm_reset"):
            new_players = [default_player(i + 1, name) for i, name in enumerate(DEFAULT_ROSTER_NAMES)]
            save_players(new_players)
            st.session_state.players = new_players
            st.session_state.confirm_reset = False
            show_success("Roster reset to defaults.")
            st.rerun()
        else:
            st.session_state.confirm_reset = True
            st.warning("Click again to confirm reset.")

st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 Roster Overview", "✏️ Edit Players", "➕ Add Player"])

with tab1:
    active_players = [p for p in enriched if not p.get("archived")]
    st.markdown(f"**{len(active_players)} active players**")
    render_roster_table(active_players, show_ratings=True)

with tab2:
    active_players = [p for p in players if not p.get("archived")]
    if not active_players:
        st.info("No active players.")
    else:
        player_names = [p["name"] for p in active_players]
        selected_name = st.selectbox("Select Player to Edit", player_names)
        selected = next((p for p in active_players if p["name"] == selected_name), None)
        
        if selected:
            with st.form(f"edit_player_{selected['id']}"):
                updated = render_player_editor(selected, key_prefix=f"edit_{selected['id']}")
                
                col_save, col_archive = st.columns(2)
                with col_save:
                    if st.form_submit_button("💾 Save Changes", use_container_width=True):
                        idx = next(i for i, p in enumerate(players) if p["id"] == selected["id"])
                        players[idx].update(updated)
                        save_players(players)
                        st.session_state.players = players
                        show_success(f"Saved changes for {updated['name']}")
                        st.rerun()
                with col_archive:
                    if st.form_submit_button("📦 Archive Player", use_container_width=True):
                        idx = next(i for i, p in enumerate(players) if p["id"] == selected["id"])
                        players[idx]["archived"] = True
                        save_players(players)
                        st.session_state.players = players
                        show_success(f"Archived {selected['name']}")
                        st.rerun()

with tab3:
    st.markdown("**Add a New Player**")
    with st.form("add_player"):
        new_name = st.text_input("Player Name")
        new_jersey = st.text_input("Jersey Number")
        if st.form_submit_button("➕ Add Player", use_container_width=True):
            if new_name.strip():
                new_id = max((p["id"] for p in players), default=0) + 1
                new_player = default_player(new_id, new_name.strip())
                new_player["jersey_number"] = new_jersey.strip()
                players.append(new_player)
                save_players(players)
                st.session_state.players = players
                show_success(f"Added {new_name}")
                st.rerun()
            else:
                st.error("Player name is required.")
    
    # Show archived
    archived = [p for p in players if p.get("archived")]
    if archived:
        st.markdown("**Archived Players**")
        for p in archived:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(p["name"])
            with col2:
                if st.button("Restore", key=f"restore_{p['id']}"):
                    idx = next(i for i, pl in enumerate(players) if pl["id"] == p["id"])
                    players[idx]["archived"] = False
                    save_players(players)
                    st.session_state.players = players
                    st.rerun()
