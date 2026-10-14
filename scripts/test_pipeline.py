
from src.pipeline import answer_question


QUESTION = "Is ground fighting allowed in Muay Thai?"

MODES = [
    "llm_only",
    "general_rag",
    "sport_aware_rag",
]


def main():
    for mode in MODES:
        print(f"\n{'=' * 60}")
        print(f"MODE: {mode}")
        print("=" * 60)

        result = answer_question(
            question=QUESTION,
            mode=mode,
        )

        print("\nANSWER:")
        print(result["answer"])

        print("\nSOURCES:")
        if not result["sources"]:
            print("No retrieved documents.")
        else:
            for source in result["sources"]:
                print(
                    f"{source['sport']} | "
                    f"{source['source']} | "
                    f"Page {source['page']}"
                )


if __name__ == "__main__":
    main()
