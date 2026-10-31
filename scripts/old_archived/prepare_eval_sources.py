
import json
from pathlib import Path

import pandas as pd

from src.retrieval import retrieve, retrieve_sport_aware


QUESTIONS_PATH = Path("data/evaluation/questions.csv")
OUTPUT_PATH = Path("data/evaluation/source_candidates.json")

TOP_K = 6


def main():
    questions = pd.read_csv(
        QUESTIONS_PATH,
        dtype=str,
        keep_default_na=False,
    )

    output = []

    for _, row in questions.iterrows():
        question = row["question"]

        # We gather candidates from both retrieval methods.
        general = retrieve(question, top_k=TOP_K)
        sport_aware = retrieve_sport_aware(
            question,
            top_k=TOP_K,
        )

        # Keep unique source passages.
        unique_sources = {}

        for source in general + sport_aware:
            key = (
                source["filename"],
                source["page"],
                source["text"],
            )
            unique_sources[key] = source

        candidates = []

        for source in unique_sources.values():
            candidates.append({
                "sport": source["sport"],
                "filename": source["filename"],
                "page": source["page"],
                "document_type": source["document_type"],
                "distance": round(source["distance"], 4),
                "text": source["text"],
            })

        output.append({
            "id": row["id"],
            "question": question,
            "sports": row["sports"].split("|"),
            "candidates": candidates,
        })

        print(
            f"{row['id']}: "
            f"{len(candidates)} candidate passages"
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(f"\nSaved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
