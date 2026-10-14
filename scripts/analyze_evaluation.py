
from pathlib import Path

import pandas as pd


DATA_DIR = Path("data/evaluation")

df = pd.read_csv(DATA_DIR / "answer_review_scored.csv")

# Csak a független tesztkérdéseket vizsgáljuk
test = df[df["split"] == "evaluation"].copy()

if len(test) != 66 or test["correctness"].isna().any():
    raise ValueError("Expected 66 scored evaluation responses.")

test["correctness"] = pd.to_numeric(test["correctness"])

# Modell-összehasonlítás
summary = (
    test.groupby("mode")
    .agg(
        questions=("id", "count"),
        total_score=("correctness", "sum"),
        average_score=("correctness", "mean"),
        fully_correct=("correctness", lambda x: (x == 2).sum()),
    )
    .reset_index()
)

summary["normalized_score_pct"] = (
    summary["total_score"]
    / (summary["questions"] * 2)
    * 100
).round(1)

# Kérdéstípus szerinti összehasonlítás
by_category = (
    test.groupby(["category", "mode"])
    .agg(
        questions=("id", "count"),
        average_score=("correctness", "mean"),
    )
    .reset_index()
)

by_category["normalized_score_pct"] = (
    by_category["average_score"] / 2 * 100
).round(1)

summary.to_csv(
    DATA_DIR / "evaluation_summary.csv",
    index=False,
)

by_category.to_csv(
    DATA_DIR / "evaluation_by_category.csv",
    index=False,
)

print("\n=== PIPELINE COMPARISON ===")
print(summary.to_string(index=False))

print("\n=== PERFORMANCE BY QUESTION TYPE ===")
print(by_category.to_string(index=False))

print("\nSaved:")
print("- data/evaluation/evaluation_summary.csv")
print("- data/evaluation/evaluation_by_category.csv")
