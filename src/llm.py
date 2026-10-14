
from groq import Groq

from src.config import GROQ_API_KEY, GROQ_MODEL


SYSTEM_PROMPT = """
You are a knowledgeable assistant specializing in combat sports rules.

Your task is to answer questions about:
- Mixed Martial Arts (MMA)
- Muay Thai
- Kickboxing, specifically K-1 Style

Rules may differ by governing organization, competition type,
and athlete category.

Instructions:
1. Answer the user's question accurately and clearly.
2. When comparing sports, explain the relevant differences.
3. Do not assume that all organizations use identical rules.
4. If you are uncertain, clearly acknowledge uncertainty.
5. Never invent official rule references or citations.
6. Respond in the same language as the user's question.
"""


client = Groq(
    api_key=GROQ_API_KEY,
    timeout=30.0,
    max_retries=0,
)


def generate_answer(
    question: str,
    system_prompt: str = SYSTEM_PROMPT,
    context: str | None = None,
) -> str:
    """
    Generate an answer using the Groq API.

    Args:
        question: The user's question.
        system_prompt: Instructions for the LLM.
        context: Optional retrieved document context.

    Returns:
        The generated answer as a string.
    """

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        }
    ]

    if context is None:
        user_message = question
    else:
        user_message = (
            "Answer the following question using only the "
            "provided document context.\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{question}"
        )

    messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0,
        max_completion_tokens=1200,
    )
    finish_reason = response.choices[0].finish_reason

    if finish_reason != "stop":
        print(f"WARNING: LLM finish reason: {finish_reason}")
        
    answer = response.choices[0].message.content

    if not answer:
        raise RuntimeError("The LLM returned an empty answer.")

    return answer
