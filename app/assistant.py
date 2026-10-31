import time
import streamlit as st
import re

MODES = {
    "LLM Only": "llm_only",
    "General RAG": "general_rag",
    "Sport-aware RAG": "sport_aware_rag",
}

EXAMPLES = {
    "MMA": "What are the main fouls in professional MMA?",
    "Muay Thai": "What protective equipment is required in IFMA Muay Thai?",
    "K-1": "Are elbow strikes allowed in WAKO K-1?",
    "Compare": "How do knee strike rules differ between Muay Thai and K-1?",
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
    
    if status in (500, 502, 503, 504):
        return (
            "The Groq service is temporarily unavailable. "
            "Please try again later."
        )

    return f"Answer generation failed: {error}"


def get_cited_source_numbers(answer, sources):
    matches = re.findall(
        r"(?:\[(\d+)\]|【(\d+)】)",
        answer,
    )

    numbers = {
        int(a or b)
        for a, b in matches
    }

    return sorted(
        number for number in numbers
        if 1 <= number <= len(sources)
    )


def render_source_legend(answer, sources):
    """Show only sources explicitly cited by the model."""
    if not sources:
        return

    cited_numbers = get_cited_source_numbers(answer, sources)

    st.markdown("#### Sources")

    if not cited_numbers:
        st.caption("No valid inline citations in this answer.")
        return

    for number in cited_numbers:
        source = sources[number - 1]

        st.markdown(
            f"**[{number}]** "
            f"{source.get('source', source.get('filename', 'Unknown'))} "
            f"· PDF page {source.get('page', '?')} "
            f"· {source.get('sport', 'Unknown')}"
        )




def render_source_details(sources):
    """Show every passage supplied to the LLM."""
    if not sources:
        return

    with st.expander(f"All retrieved chunks ({len(sources)})"):
        for number, source in enumerate(sources, start=1):
            name = source.get(
                "source",
                source.get("filename", "Unknown"),
            )
            page = source.get("page", "?")
            sport = source.get("sport", "Unknown")

            st.markdown(
                f"**[{number}] {name}** "
                f"· PDF page {page} · {sport}"
            )

            text = source.get("text", "")
            if text:
                st.text(text[:800])

            if number < len(sources):
                st.divider()






def render_answer_block(answer, mode_label, elapsed, sources):
    with st.container(border=True):
        st.markdown("#### Answer")
        st.markdown(answer)
        st.caption(f"{mode_label} · {elapsed:.1f} seconds")

    if sources:
        with st.container(border=True):
            render_source_legend(answer, sources)
            render_source_details(sources)

    elif mode_label != "LLM Only":
        st.caption("No sources were returned.")



def render_assistant():
    with st.container(border=True):
        st.subheader("Rulebook Assistant")
        st.caption(
            "Ask questions about MMA, Muay Thai and K-1 rules using three AI answering modes."
        )

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        left, right = st.columns([3, 1])

        with left:
            mode_label = st.segmented_control(
                "Answering method",
                options=list(MODES),
                default="Sport-aware RAG",
                selection_mode="single",
                width="stretch",
            )

        with right:
            st.write("")
            st.write("")
            if st.button("Clear chat", width="stretch"):
                st.session_state.chat_history = []
                st.rerun()

        descriptions = {
            "LLM Only": "Answers using the model’s general knowledge.",
            "General RAG": "Retrieves relevant passages from all indexed rulebooks.",
            "Sport-aware RAG": "Detects the relevant sports first, then retrieves targeted passages.",
        }

        st.caption(descriptions[mode_label])

        st.markdown("**Explore the rulebooks**")
        st.caption("Start with a suggested topic.")

        example_cols = st.columns(4, gap="small")
        selected_example = None

        for col, (label, question) in zip(example_cols, EXAMPLES.items()):
            with col:
                with st.container(border=True):
                    if st.button(
                        label,
                        key=f"example_{label}",
                        width="stretch",
                    ):
                        selected_example = question

    # previous messages
    for item in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(item["question"])

        with st.chat_message("assistant"):
            render_answer_block(
                answer=item["answer"],
                mode_label=item["mode"],
                elapsed=item["elapsed"],
                sources=item["sources"],
            )

    prompt = st.chat_input("Ask about MMA, Muay Thai or K-1 rules...")
    question = selected_example or prompt

    if not question:
        return

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching rulebooks and generating answer..."):
            started = time.perf_counter()

            try:
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

        render_answer_block(
            answer=answer,
            mode_label=mode_label,
            elapsed=elapsed,
            sources=sources,
        )

    st.session_state.chat_history.append(
        {
            "question": question,
            "answer": answer,
            "mode": mode_label,
            "elapsed": elapsed,
            "sources": sources,
        }
    )