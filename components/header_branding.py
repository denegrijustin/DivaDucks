import streamlit as st
from utils.branding import get_css, render_header

def show_header(subtitle: str = ""):
    st.markdown(get_css(), unsafe_allow_html=True)
    st.markdown(render_header(subtitle), unsafe_allow_html=True)
