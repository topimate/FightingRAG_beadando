from dotenv import load_dotenv
from groq import Groq

load_dotenv()

from groq import Groq

from src.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    MAX_COMPLETION_TOKENS,
    TEMPERATURE,
    REASONING_EFFORT,
)

if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY in .env")

client = Groq(
    api_key=GROQ_API_KEY,
    timeout=30.0,
    max_retries=0,
)

SYSTEM_PROMPT = """
You are an assistant specializing in combat sports rules.

Answer questions about MMA, Muay Thai, and WAKO K-1 Style.

Rules can differ between governing organizations and
competition categories.

Answer accurately, acknowledge uncertainty, and
never invent official rule references.

Respond in the language of the user's question.
"""


def generate_answer(
    question: str,
    system_prompt: str = SYSTEM_PROMPT,
    context: str | None = None,
) -> str:
    """Generate an LLM answer, optionally using retrieved context."""

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if context is None:
        user_message = question
    else:
        user_message = (
            "Answer using only the supplied document context. "
            "If the information is insufficient, say so.\n\n"
            f"DOCUMENT CONTEXT:\n{context}\n\n"
            f"QUESTION:\n{question}"
        )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=TEMPERATURE,
        max_completion_tokens=MAX_COMPLETION_TOKENS,
        reasoning_effort=REASONING_EFFORT,
    )

    choice = response.choices[0]

    if choice.finish_reason != "stop":
        print(f"WARNING: LLM finish reason: {choice.finish_reason}")

    answer = choice.message.content

    if not answer:
        raise RuntimeError("LLM returned an empty answer.")

    return answer
