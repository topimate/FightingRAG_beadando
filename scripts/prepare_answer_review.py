
import json
from pathlib import Path

import pandas as pd


DATA_DIR = Path("data/evaluation")

questions = pd.read_csv(
    DATA_DIR / "questions_verified_30.csv",
    dtype=str,
    keep_default_na=False,
)

with (DATA_DIR / "evaluation_results.jsonl").open(
    encoding="utf-8"
) as file:
    results = [
        json.loads(line)
        for line in file
        if line.strip()
    ]

rows = []

for result in results:
    reference = questions.loc[
        questions["id"] == result["id"]
    ]

    if reference.empty:
        raise ValueError(f"Unknown question: {result['id']}")

    q = reference.iloc[0]

    rows.append({
        "id": result["id"],
        "split": result["split"],
        "category": result["category"],
        "mode": result["mode"],
        "question": result["question"],
        "expected_answer": q["expected_answer"],
        "reference_sources": q["reference_sources"],
        "answer": result["answer"],
        "retrieved_sources": "; ".join(
            f"{s['filename']}:p{s['page']}"
            for s in result["sources"]
        ),
        "correctness": "",
        "source_support": "",
        "error_notes": "",
    })

df = pd.DataFrame(rows)

df.to_csv(
    DATA_DIR / "answer_review.csv",
    index=False,
    encoding="utf-8-sig",
)

print(f"Prepared {len(df)} answers for review.")
print("Saved: data/evaluation/answer_review.csv")
