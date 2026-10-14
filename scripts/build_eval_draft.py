
from pathlib import Path

import pandas as pd


INPUT = Path("data/evaluation/questions.csv")
OUTPUT = Path("data/evaluation/questions_draft.csv")

# Answers directly verified against source documents.
VERIFIED = {
    "Q001": {
        "expected_answer": (
            "Professional MMA bouts may consist of 1 to 5 rounds. "
            "Each round lasts 5 minutes, with a 1-minute rest "
            "between rounds."
        ),
        "reference_sources": "mma_rules.pdf:p1",
    },
    "Q005": {
        "expected_answer": (
            "No. Elbow strikes are prohibited under "
            "the WAKO K-1 rules."
        ),
        "reference_sources": "k1_rules.pdf:p3",
    },
    "Q006": {
        "expected_answer": (
            "Under the K-1 amendment, legal target areas are "
            "the front and side of the head (including the "
            "forehead), the front and side of the torso, "
            "and the legs, including joints."
        ),
        "reference_sources": "k1_rules_updates.pdf:p1",
    },
}

df = pd.read_csv(INPUT, dtype=str, keep_default_na=False)

df["review_status"] = "needs_review"

for qid, answer in VERIFIED.items():
    mask = df["id"] == qid

    for field, value in answer.items():
        df.loc[mask, field] = value

    df.loc[mask, "answerable"] = "True"
    df.loc[mask, "review_status"] = "verified"

# Clarify the intended competition format.
df.loc[
    df["id"] == "Q004", "question"
] = "How are full-contact Muay Thai bouts scored under IFMA rules?"

df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")

print(f"Questions: {len(df)}")
print(f"Verified: {(df['review_status'] == 'verified').sum()}")
print(f"Needs review: {(df['review_status'] == 'needs_review').sum()}")
print(f"Saved to: {OUTPUT}")
