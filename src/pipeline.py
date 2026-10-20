
from src.llm import generate_answer
from src.rag import generate_rag_answer


VALID_MODES = (
    "llm_only",
    "general_rag",
    "sport_aware_rag",
)


def answer_question(
    question: str,
    mode: str = "general_rag",
) -> dict:
    """Answer a question using the selected pipeline."""

    question = question.strip()

    if not question:
        raise ValueError("Question cannot be empty.")

    if mode not in VALID_MODES:
        raise ValueError(f"Invalid pipeline mode: {mode}")

    if mode == "llm_only":
        return {
            "question": question,
            "mode": mode,
            "answer": generate_answer(question),
            "sources": [],
        }

    rag_mode = (
        "general"
        if mode == "general_rag"
        else "sport_aware"
    )

    result = generate_rag_answer(
        question=question,
        mode=rag_mode,
    )

    return {
        "question": question,
        "mode": mode,
        "answer": result["answer"],
        "sources": result["sources"],
    }
