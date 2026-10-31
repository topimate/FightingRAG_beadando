import streamlit as st

from app.assistant import render_assistant
from app.insights import render_insights
from app.theme import apply_theme


def main() -> None:
    """Render the FightRAG Streamlit application."""
    st.set_page_config(
        page_title="FightRAG",
        page_icon="🥊",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    apply_theme()

    _, main_col, _ = st.columns([0.8, 8.8, 0.8])

    with main_col:
        with st.container(border=True, key="fight_hero"):
            hero_left, hero_right = st.columns(
                [4, 1.2], vertical_alignment="center"
            )

            with hero_left:
                st.caption("AI RULEBOOK ASSISTANT")
                st.title("FightRAG")
                st.caption("Combat sports intelligence, simplified.")

            with hero_right:
                st.metric("Sports", "3")
                st.caption("MMA · MUAY THAI · K-1")

        st.space("small")

        assistant_tab, insights_tab = st.tabs(
            ["Rulebook Assistant", "Model Insights"]
        )

        with assistant_tab:
            render_assistant()

        with insights_tab:
            render_insights()


if __name__ == "__main__":
    main()
