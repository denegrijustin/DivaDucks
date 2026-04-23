import streamlit as st
from typing import List

def show_errors(errors: List[str]):
    for err in errors:
        st.error(f"🚫 {err}")

def show_warnings(warnings: List[str]):
    for warn in warnings:
        st.warning(f"⚠️ {warn}")

def show_success(msg: str):
    st.success(f"✅ {msg}")
