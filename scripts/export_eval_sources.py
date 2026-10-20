
import json
from pathlib import Path

INPUT_PATH = Path("data/evaluation/source_candidates.json")
OUTPUT_PATH = Path("data/evaluation/source_review.md")


def main():
    records = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    lines = ["# FightRAG – Candidate source review", ""]

    for item in records:
        lines.extend([
            f"## {item['id']} – {item['question']}",
            "",
        ])

        for index, source in enumerate(item["candidates"], start=1):
            lines.extend([
                f"### Candidate {index}",
                f"- Sport: {source['sport']}",
                f"- PDF: {source['filename']}",
                f"- Page: {source['page']}",
                f"- Distance: {source['distance']}",
                "",
                source["text"],
                "",
                "---",
                "",
            ])

    OUTPUT_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print(f"Questions: {len(records)}")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
