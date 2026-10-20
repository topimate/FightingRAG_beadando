
import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from src.config import GROQ_MODEL, TOP_K
from src.pipeline import answer_question


QUESTIONS_PATH = Path("data/evaluation/questions_verified_30.csv")
RESULTS_PATH = Path("data/evaluation/evaluation_results.jsonl")

MODES = ("llm_only", "general_rag", "sport_aware_rag")


def load_completed():
    """Find successfully completed question/mode pairs."""
    completed = set()

    if not RESULTS_PATH.exists():
        return completed

    with RESULTS_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            record = json.loads(line)

            if record.get("status") == "success":
                completed.add((record["id"], record["mode"]))

    return completed


def save_result(record):
    """Append one result immediately after generation."""
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with RESULTS_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")

def run_with_retry(question, mode, max_retries=3):
    """Retry temporary Groq rate limit errors."""

    for attempt in range(max_retries + 1):
        try:
            return answer_question(question=question, mode=mode)

        except Exception as error:
            if getattr(error, "status_code", None) != 429:
                raise

            if attempt == max_retries:
                raise

            wait_seconds = 20 * (attempt + 1)

            print(
                f"Rate limit reached. "
                f"Retrying in {wait_seconds}s..."
            )

            time.sleep(wait_seconds)

def run(limit=None, split="all", delay=5):
    with QUESTIONS_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        questions = list(csv.DictReader(file))

    if split != "all":
        questions = [
            q for q in questions if q["split"] == split
        ]

    if limit is not None:
        questions = questions[:limit]

    completed = load_completed()
    total = len(questions) * len(MODES)

    print(f"Questions: {len(questions)}")
    print(f"Total tasks: {total}")
    print(f"Existing completed tasks: {len(completed)}")

    for question in questions:
        for mode in MODES:
            key = (question["id"], mode)

            if key in completed:
                print(f"SKIP {question['id']} | {mode}")
                continue

            print(f"\nRUN {question['id']} | {mode}")

            start = time.perf_counter()

            try:
                result = run_with_retry(
                    question=question["question"],
                    mode=mode,
                )

                duration = round(
                    time.perf_counter() - start, 2
                )

                record = {
                    "id": question["id"],
                    "split": question["split"],
                    "category": question["category"],
                    "sports": question["sports"],
                    "question": question["question"],
                    "mode": mode,
                    "model": GROQ_MODEL,
                    "top_k": 0 if mode == "llm_only" else TOP_K,
                    "answer": result["answer"],
                    "sources": [
                        {
                            "sport": s["sport"],
                            "source": s["source"],
                            "filename": s["filename"],
                            "page": s["page"],
                            "document_type": s["document_type"],
                            "distance": s["distance"],
                        }
                        for s in result["sources"]
                    ],
                    "duration_seconds": duration,
                    "timestamp": datetime.now(
                        timezone.utc
                    ).isoformat(),
                    "status": "success",
                }

                save_result(record)
                completed.add(key)

                print(f"OK | {duration}s | saved")

            except Exception as error:
                status_code = getattr(error, "status_code", None)

                print(
                    f"ERROR {question['id']} | {mode}: {error}"
                )

                if status_code == 429:
                    print(
                        "Groq rate limit reached. "
                        "Results are saved. Resume later."
                    )
                else:
                    print(
                        "Evaluation stopped. "
                        "Fix the error, then resume."
                    )

                return

            time.sleep(delay)

    print("\nEvaluation finished successfully!")
    print(f"Results: {RESULTS_PATH}")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Number of questions to process",
    )

    parser.add_argument(
        "--split",
        choices=("all", "development", "evaluation"),
        default="all",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=5,
        help="Seconds between successful API calls",
    )

    args = parser.parse_args()

    run(
        limit=args.limit,
        split=args.split,
        delay=args.delay,
    )


if __name__ == "__main__":
    main()
