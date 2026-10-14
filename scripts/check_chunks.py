
import json
from collections import Counter
from pathlib import Path


INPUT_PATH = Path("data/processed/chunks.jsonl")


def main() -> None:
    with INPUT_PATH.open(encoding="utf-8") as file:
        chunks = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    lengths = [len(chunk["text"]) for chunk in chunks]

    print(f"Total chunks: {len(chunks)}")
    print(f"Average length: {sum(lengths) / len(lengths):.0f}")
    print(f"Shortest chunk: {min(lengths)}")
    print(f"Longest chunk: {max(lengths)}")

    print("\nChunks by sport:")
    for sport, count in Counter(
        chunk["sport"] for chunk in chunks
    ).items():
        print(f"  {sport}: {count}")

    print("\nChunks by document:")
    for document, count in Counter(
        chunk["filename"] for chunk in chunks
    ).items():
        print(f"  {document}: {count}")

    print("\nValidation:")
    print(
        "Unique IDs:",
        len({chunk["id"] for chunk in chunks}) == len(chunks),
    )
    print(
        "Empty chunks:",
        sum(not chunk["text"].strip() for chunk in chunks),
    )
    print(
        "Oversized chunks:",
        sum(len(chunk["text"]) > 2200 for chunk in chunks),
    )

    print("\nSample chunks:")
    for filename in (
        "mma_rules.pdf",
        "muay_thai_rules.pdf",
        "k1_rules.pdf",
        "k1_rules_updates.pdf",
    ):
        sample = next(
            (c for c in chunks if c["filename"] == filename),
            None,
        )

        if sample:
            print(f"\n--- {filename}, page {sample['page']} ---")
            print(sample["text"][:600])


if __name__ == "__main__":
    main()
