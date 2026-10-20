
from src.llm import generate_answer
from src.retrieval import retrieve, retrieve_sport_aware
from src.config import TOP_K

RAG_SYSTEM_PROMPT = """
You are a combat sports rules assistant.

Answer questions about MMA, IFMA Muay Thai and WAKO K-1 Style.

Use only the supplied document context.
If the context is insufficient, say so.

When comparing sports, clearly explain the differences
and support each sport's claims with its own sources.

Never invent rules, citations or source numbers.
Do not mix rules from different sports or organizations.

WAKO K-1 amendments may replace older rules.
If conflicting passages appear and precedence is uncertain,
explain the conflict rather than guessing.

For WAKO K-1 questions, treat the base rules and the
amendment document as one combined rulebook.

The amendment document supplements the base rules.
If an amendment explicitly contradicts an older rule,
follow the amendment.

If the documents do not provide enough information,
acknowledge the uncertainty.

Use short, clear answers.
Prefer bullet points over large tables unless a table is truly helpful.

CITATION RULES:
- Every factual claim about a combat sport rule must have
  at least one inline citation.
- Place citations immediately after the claim they support.
- Use citation numbers in the format [1], [2], [3].
- Cite only sources that directly support the specific claim.
- Never invent citation numbers or cite unrelated passages.
- For comparisons, cite each sport's rules separately.
- Do not put all citations at the end of the answer.
- If the retrieved documents do not support a claim,
  do not present it as a verified fact.
- If the answer is based on missing information,
  explain the limitation instead of inventing a citation.


Respond in the user's language.
"""


def generate_rag_answer(
    question: str,
    mode: str = "general",
    top_k: int = TOP_K,
) -> dict:
    """Generate an answer using one of the RAG strategies."""

    if mode == "general":
        passages = retrieve(question, top_k=top_k)

    elif mode == "sport_aware":
        passages = retrieve_sport_aware(question, top_k=top_k)

    else:
        raise ValueError(f"Unknown RAG mode: {mode}")

    context_parts = []

    for index, passage in enumerate(passages, start=1):
        context_parts.append(
            f"[{index}]\n"
            f"Sport: {passage['sport']}\n"
            f"Document: {passage['source']}\n"
            f"Document type: {passage['document_type']}\n"
            f"PDF page: {passage['page']}\n"
            f"Text:\n{passage['text']}"
        )

    context = "\n\n".join(context_parts)

    answer = generate_answer(
        question=question,
        system_prompt=RAG_SYSTEM_PROMPT,
        context=context,
    )

    return {
        "question": question,
        "mode": mode,
        "answer": answer,
        "sources": passages,
    }
