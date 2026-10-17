
import time

import streamlit as st


MODES = {
    "LLM Only": "llm_only",
    "General RAG": "general_rag",
    "Sport-aware RAG": "sport_aware_rag",
}

EXAMPLES = {
    "MMA": "What are the main fouls in professional MMA?",
    "Muay Thai": "What protective equipment is required in IFMA Muay Thai?",
    "K-1": "Are elbow strikes allowed in WAKO K-1?",
    "Compare": "How do knee strike rules differ between MMA and K-1?",
}


def get_error_message(error):
    message = str(error).lower()
    status = getattr(error, "status_code", None)

    if (
        status == 429
        or "rate_limit" in message
        or "rate limit" in message
        or "tokens per minute" in message
    ):
        return (
            "Groq API rate limit reached. "
            "Please wait a little before trying again."
        )

    if "api_key" in message or "authentication" in message:
        return "Groq authentication failed. Check your API key."

    return f"Answer generation failed: {error}"


def display_sources(sources):
    if not sources:
        return

    with st.expander(f"📚 Retrieved sources ({len(sources)})"):
        for index, source in enumerate(sources, start=1):
            sport = source.get("sport", "Unknown")
            filename = source.get("filename", "Unknown")
            page = source.get("page", "?")

            st.markdown(
                f"**{index}. {sport}** — "
                f"`{filename}` · PDF page {page}"
            )


def render_assistant():
    st.subheader("Rulebook Assistant")
    st.caption(
        "Explore combat sports regulations with three AI approaches."
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Settings
    left, right = st.columns([3, 1])

    with left:
        mode_label = st.radio(
            "Answering method",
            options=list(MODES),
            horizontal=True,
            index=2,
        )

    with right:
        st.write("")
        if st.button(
            "Clear chat",
            icon=":material/delete_outline:",
            use_container_width=True,
        ):
            st.session_state.chat_history = []
            st.rerun()

    # Brief explanation
    descriptions = {
        "LLM Only": "Answers using general model knowledge.",
        "General RAG": "Retrieves passages from all indexed rulebooks.",
        "Sport-aware RAG": (
            "Detects the relevant sports and retrieves "
            "passages from their rulebooks."
        ),
    }

    st.caption(descriptions[mode_label])

    st.divider()

    # Example questions
    st.markdown("**Try an example**")

    example_cols = st.columns(4)

    selected_example = None

    for col, (label, question) in zip(
        example_cols, EXAMPLES.items()
    ):
        with col:
            if st.button(label, use_container_width=True):
                selected_example = question

    # Conversation history
    for item in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(item["question"])

        with st.chat_message("assistant"):
            st.markdown(item["answer"])

            st.caption(
                f"{item['mode']} · "
                f"{item['elapsed']:.1f} seconds"
            )

            display_sources(item["sources"])

    # Input
    prompt = st.chat_input(
        "Ask about MMA, Muay Thai or K-1 rules..."
    )

    question = selected_example or prompt

    if not question:
        return

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching rulebooks and generating answer..."):
            started = time.perf_counter()

            try:
                # Import only when an answer is requested.
                from src.pipeline import answer_question

                result = answer_question(
                    question=question,
                    mode=MODES[mode_label],
                )

                elapsed = time.perf_counter() - started
                answer = result.get("answer") or "No answer returned."
                sources = result.get("sources") or []

            except Exception as error:
                st.error(get_error_message(error))
                return

        st.markdown(answer)

        st.caption(
            f"{mode_label} · {elapsed:.1f} seconds"
        )

        display_sources(sources)

    st.session_state.chat_history.append(
        {
            "question": question,
            "answer": answer,
            "mode": mode_label,
            "elapsed": elapsed,
            "sources": sources,
        }
    )
