
from time import perf_counter

from groq import GroqError

from src.llm import generate_answer


questions = [
    "Is ground fighting allowed in Muay Thai?",
    "What is the difference between MMA and K-1?",
    "Milyen védőfelszerelés szükséges K-1 versenyeken?",
]


def main():
    for index, question in enumerate(questions, start=1):
        print(f"\n{'=' * 60}", flush=True)
        print(f"QUESTION {index}: {question}", flush=True)
        print("=" * 60, flush=True)

        start = perf_counter()

        try:
            answer = generate_answer(question)
            elapsed = perf_counter() - start

            print(answer)
            print(f"\nResponse time: {elapsed:.2f}s", flush=True)

        except GroqError as error:
            print(
                f"Groq API error: {type(error).__name__}: {error}",
                flush=True,
            )

        except Exception as error:
            print(
                f"Unexpected error: {type(error).__name__}: {error}",
                flush=True,
            )


if __name__ == "__main__":
    main()
