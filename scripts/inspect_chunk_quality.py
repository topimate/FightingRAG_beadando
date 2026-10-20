
import json
from collections import Counter
from pathlib import Path

INPUT_PATH = Path("data/processed/chunks.jsonl")

with INPUT_PATH.open(encoding="utf-8") as f:
    chunks = [json.loads(line) for line in f if line.strip()]

print("=" * 60)
print("SHORT CHUNKS (< 150 characters)")
print("=" * 60)

short_chunks = [
    chunk for chunk in chunks
    if len(chunk["text"]) < 150
]

print(f"Count: {len(short_chunks)}")

for chunk in short_chunks:
    print(f"\nID: {chunk['id']}")
    print(f"Source: {chunk['filename']}, page {chunk['page']}")
    print(f"Length: {len(chunk['text'])}")
    print(f"Text: {chunk['text']!r}")

print("\n" + "=" * 60)
print("FIRST PAGE CHUNKS BY DOCUMENT")
print("=" * 60)

for filename in sorted({c["filename"] for c in chunks}):
    first_page = min(
        c["page"] for c in chunks
        if c["filename"] == filename
    )

    page_chunks = [
        c for c in chunks
        if c["filename"] == filename
        and c["page"] == first_page
    ]

    print(f"\n{filename} | page {first_page}")
    print(f"Chunks: {len(page_chunks)}")

    for chunk in page_chunks:
        print(
            f"- {chunk['id']}: "
            f"{len(chunk['text'])} chars"
        )
        print(chunk["text"][:250].replace("\n", " "))
        print()

print("\n" + "=" * 60)
print("SHORT CHUNKS BY DOCUMENT")
print("=" * 60)

for filename, count in Counter(
    c["filename"] for c in short_chunks
).items():
    print(f"{filename}: {count}")
