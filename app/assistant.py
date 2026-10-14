
import streamlit as st

from src.pipeline import answer_question


MODES = {
    "LLM Only": "llm_only",
    "General RAG": "general_rag",
    "Sport-aware RAG": "sport_aware_rag",
}


def render_assistant():
    st.subheader("Rulebook Assistant")

    st.write(
        "Ask questions about MMA, Muay Thai and K-1 rules. "
        "Choose how FightRAG should generate its answer."
    )

    mode = st.radio(
        "Answering method",
        options=list(MODES.keys()),
        horizontal=True,
    )

    question = st.text_area(
        "Your question",
        placeholder="How do knee strikes differ between Muay Thai and K-1?",
        height=110,
    )

    if st.button("Ask FightRAG", type="primary"):
        if not question.strip():
            st.warning("Please enter a question.")
            return

        with st.spinner("Generating answer..."):
            try:
                result = answer_question(
                    question=question.strip(),
                    mode=MODES[mode],
                )

            except Exception as error:
                status_code = getattr(error, "status_code", None)

                if status_code == 429 or "rate_limit" in str(error).lower():
                    st.warning(
                        "Groq rate limit reached. "
                        "Please wait a little and try again."
                    )
                else:
                    st.error(f"Failed to generate answer: {error}")
                return

        st.markdown("### Answer")
        st.markdown(result["answer"])

        sources = result.get("sources") or []

        if sources:
            with st.expander(
                f"Retrieved sources ({len(sources)})"
            ):
                for index, source in enumerate(sources, start=1):
                    st.markdown(
                        f"**{index}. {source.get('filename', 'Unknown')}** "
                        f"— PDF page {source.get('page', '?')} "
                        f"— {source.get('sport', 'Unknown')}"
                    )
        elif MODES[mode] != "llm_only":
            st.caption("No sources were returned.")
