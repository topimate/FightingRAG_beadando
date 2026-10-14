
from collections import Counter
from pathlib import Path
import json


input_path = Path("data/processed/pages.jsonl")

with input_path.open(encoding="utf-8") as file:
    records = [
        json.loads(line)
        for line in file
        if line.strip()
    ]

print(f"Total records: {len(records)}")

print("\nRecords by sport:")
for sport, count in Counter(
    record["sport"] for record in records
).items():
    print(f"  {sport}: {count}")

print("\nRecords by document:")
for filename, count in Counter(
    record["filename"] for record in records
).items():
    print(f"  {filename}: {count}")

print("\nAmendment records:")
updates = [
    record
    for record in records
    if record["document_type"] == "amendment"
]

for record in updates:
    print(
        f"  {record['id']} | "
        f"{len(record['text'])} characters"
    )

print("\nUnique IDs:", len({
    record["id"] for record in records
}) == len(records))

print("Empty texts:", sum(
    not record["text"].strip()
    for record in records
))
