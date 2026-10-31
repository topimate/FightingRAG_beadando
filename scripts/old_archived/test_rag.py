
from src.rag import generate_rag_answer


def main():
    question = (
        "What protective equipment is required "
        "for WAKO K-1 competitions?"
    )

    print(f"QUESTION: {question}\n")

    result = generate_rag_answer(question)

    print("=" * 60)
    print("RAG ANSWER")
    print("=" * 60)
    print(result["answer"])

    print("\n" + "=" * 60)
    print("RETRIEVED SOURCES")
    print("=" * 60)

    for index, source in enumerate(result["sources"], start=1):
        print(
            f"[SOURCE {index}] "
            f"{source['source']} | "
            f"Page {source['page']} | "
            f"Distance: {source['distance']:.4f}"
        )


if __name__ == "__main__":
    main()
