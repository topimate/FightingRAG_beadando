import streamlit as st

from app.assistant import render_assistant
from app.insights import render_insights
from app.theme import apply_theme

st.set_page_config(
    page_title="FightRAG",
    page_icon="🥊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_theme()

left_pad, main_col, right_pad = st.columns([0.8, 8.8, 0.8])

with main_col:
    with st.container(border=True):
        left, right = st.columns([4, 1.2])

        with left:
            st.caption("AI RULEBOOK ASSISTANT")
            st.title("FightRAG")
            st.caption("Combat sports intelligence, simplified.")

        with right:
            st.metric("Sports", "3")
            st.caption("MMA · MUAY THAI · K-1")

    st.write("")

    assistant_tab, insights_tab = st.tabs([
        "Rulebook Assistant",
        "Model Insights",
    ])

    with assistant_tab:
        render_assistant()

    with insights_tab:
        render_insights()