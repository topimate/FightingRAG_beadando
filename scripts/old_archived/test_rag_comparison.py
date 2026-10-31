
from src.rag import generate_rag_answer
from src.sport_detector import detect_sports


def main():
    question = (
        "What are the differences between MMA and "
        "K-1 protective equipment?"
    )

    print(f"QUESTION: {question}")
    print(f"DETECTED SPORTS: {detect_sports(question)}")

    for mode in ("general", "sport_aware"):
        print(f"\n{'=' * 65}")
        print(f"MODE: {mode.upper()}")
        print("=" * 65)

        result = generate_rag_answer(
            question=question,
            mode=mode,
            top_k=6,
        )

        print("\nANSWER:")
        print(result["answer"])

        print("\nSOURCES:")
        for index, source in enumerate(result["sources"], start=1):
            print(
                f"[{index}] {source['sport']} | "
                f"{source['source']} | "
                f"Page {source['page']} | "
                f"Distance {source['distance']:.4f}"
            )


if __name__ == "__main__":
    main()
