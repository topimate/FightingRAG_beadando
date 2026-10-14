
import streamlit as st

from app.assistant import render_assistant
from app.insights import render_insights


st.set_page_config(
    page_title="FightRAG",
    page_icon="🥊",
    layout="wide",
)

st.title(" FightRAG")
st.caption("AI-powered Combat Sports Rulebook Assistant")

assistant_tab, insights_tab = st.tabs([
    " Rulebook Assistant",
    " Model Insights",
])

with assistant_tab:
    render_assistant()

with insights_tab:
    render_insights()
