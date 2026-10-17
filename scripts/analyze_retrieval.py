
import csv
import json
from pathlib import Path


INPUT = Path("data/evaluation/evaluation_results.jsonl")
OUTPUT = Path("data/evaluation/retrieval_metrics.csv")


def main():
    records = []

    with INPUT.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    results = []

    for record in records:
        if record["mode"] == "llm_only":
            continue

        expected = set(record["sports"].split("|"))
        sources = record["sources"]
        retrieved = {s["sport"] for s in sources}

        matched = expected & retrieved

        coverage = len(matched) / len(expected)

        irrelevant = sum(
            s["sport"] not in expected for s in sources
        )

        results.append({
            "id": record["id"],
            "split": record["split"],
            "mode": record["mode"],
            "sport_coverage": coverage,
            "all_sports_found": int(expected <= retrieved),
            "irrelevant_sources": irrelevant,
            "irrelevant_source_rate": (
                irrelevant / len(sources) if sources else 0
            ),
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys()),
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"Analyzed {len(results)} RAG results\n")

    for mode in ("general_rag", "sport_aware_rag"):
        subset = [r for r in results if r["mode"] == mode]

        if not subset:
            continue

        n = len(subset)

        coverage = sum(r["sport_coverage"] for r in subset) / n
        all_found = sum(r["all_sports_found"] for r in subset)
        irrelevant = sum(r["irrelevant_sources"] for r in subset)
        source_count = 6 * n

        print(f"{mode}:")
        print(f"  Complete sport coverage: {all_found}/{n}")
        print(f"  Average sport coverage: {coverage:.1%}")
        print(f"  Irrelevant sources: {irrelevant}/{source_count}")
        print()

    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()
