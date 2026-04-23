import streamlit as st
from utils.branding import get_css, render_header
from utils.persistence import load_settings, save_settings
from components.validation_messages import show_success

st.set_page_config(page_title="Settings | Diva Ducks", page_icon="🦆", layout="wide")
st.markdown(get_css(), unsafe_allow_html=True)

if "settings" not in st.session_state:
    st.session_state.settings = load_settings()

settings = st.session_state.settings

st.markdown(render_header("Settings"), unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["⚙️ Game Rules", "⚖️ Weights", "🎨 Theme"])

with tab1:
    st.markdown("### Game Rules")
    with st.form("game_rules"):
        col1, col2 = st.columns(2)
        with col1:
            offense_size = st.number_input("Players on Offense", min_value=5, max_value=11, value=settings.get("offense_size", 7))
            defense_size = st.number_input("Players on Defense", min_value=5, max_value=11, value=settings.get("defense_size", 7))
        with col2:
            possessions = st.number_input("Possessions per Half", min_value=1, max_value=6, value=settings.get("possessions_per_half", 3))
            halves = st.number_input("Number of Halves", min_value=1, max_value=4, value=settings.get("halves", 2))
        
        planning_mode = st.selectbox(
            "Default Planning Mode",
            ["Fair Rotation", "Balanced", "Must-Win"],
            index=["Fair Rotation", "Balanced", "Must-Win"].index(settings.get("planning_mode", "Fair Rotation"))
        )
        
        if st.form_submit_button("💾 Save Game Rules", use_container_width=True):
            settings["offense_size"] = int(offense_size)
            settings["defense_size"] = int(defense_size)
            settings["possessions_per_half"] = int(possessions)
            settings["halves"] = int(halves)
            settings["planning_mode"] = planning_mode
            save_settings(settings)
            st.session_state.settings = settings
            show_success("Game rules saved!")

with tab2:
    st.markdown("### Rating Weights")
    st.info("Weights are automatically normalized. Higher values = more influence on ratings.")
    
    weight_groups = {
        "Offense Rating": "offense",
        "Defense Rating": "defense",
        "QB Rating": "qb",
    }
    
    for label, key in weight_groups.items():
        with st.expander(f"⚖️ {label}"):
            weights = settings.get("rating_weights", {}).get(key, {})
            for attr, val in weights.items():
                new_val = st.slider(
                    attr.replace("_", " ").title(),
                    min_value=0.0, max_value=1.0,
                    value=float(val), step=0.05,
                    key=f"weight_{key}_{attr}"
                )
                settings["rating_weights"][key][attr] = new_val
    
    if st.button("💾 Save Weights", use_container_width=True):
        save_settings(settings)
        st.session_state.settings = settings
        show_success("Weights saved!")

with tab3:
    st.markdown("### Fairness / Strength Balance")
    fairness = st.slider(
        "Fairness Weight (0=pure strength, 1=pure fairness)",
        0.0, 1.0,
        value=settings.get("fairness_weight", 0.5), step=0.1
    )
    settings["fairness_weight"] = fairness
    settings["strength_weight"] = round(1.0 - fairness, 2)
    
    st.markdown(f"**Fairness:** {fairness:.0%} | **Strength:** {settings['strength_weight']:.0%}")
    
    if st.button("💾 Save Balance", use_container_width=True):
        save_settings(settings)
        st.session_state.settings = settings
        show_success("Balance saved!")
