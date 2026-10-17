
import streamlit as st

from app.assistant import render_assistant
from app.insights import render_insights



st.set_page_config(
    page_title="FightRAG",
    page_icon="🥊",
    layout="centered",
    initial_sidebar_state="collapsed",
)


st.title("FightRAG")
st.caption("Your AI guide to combat sports rules.")

assistant_tab, insights_tab = st.tabs([
    " Rulebook Assistant",
    " Model Insights",
])

with assistant_tab:
    render_assistant()

with insights_tab:
    render_insights()
