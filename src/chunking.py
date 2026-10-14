
import json
import re
from pathlib import Path


INPUT_PATH = Path("data/processed/pages.jsonl")
OUTPUT_PATH = Path("data/processed/chunks.jsonl")

MAX_CHARS = 2200
OVERLAP_CHARS = 200


def remove_noise(text: str, filename: str) -> str:
    """Remove known headers and footers, preserving actual rules."""

    if filename == "muay_thai_rules.pdf":
        # Repeated IFMA document header.
        text = re.sub(
            r"IFMA MUAYTHAI RULES & REGULATIONS\s+"
            r"INCLUDING WAI KRU, MAI MUAY, FULL CONTACT "
            r"AND SEMI CONTACT COMPETITIONS",
            "",
            text,
        )

        # Standalone IFMA footer / page number.
        text = re.sub(
            r"(?m)^\s*Page \d+ of 93\s*$",
            "",
            text,
        )

        # Website-only final page.
        if text.strip() == "www.muaythai.sport":
            return ""

    elif filename == "k1_rules.pdf":
        # Repeated old WAKO page header/footer.
        text = re.sub(
            r"WAKO Rules Ring Sports K-1\s+"
            r"Ring Sports K1 Rules V18\s+"
            r"Page\d+ to 10",
            "",
            text,
        )

        text = re.sub(
            r"Ring Sports K1 Rules V18\s+Page\d+ to 10",
            "",
            text,
        )

    # Standalone figure captions that have little retrieval value.
    text = re.sub(
        r"(?m)^\s*Figure \d+[^\n]*$",
        "",
        text,
    )

    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_long_text(text: str) -> list[str]:
    """Split oversized paragraphs on word boundaries."""
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + MAX_CHARS, len(text))

        if end < len(text):
            boundary = text.rfind(" ", start, end)
            if boundary > start + MAX_CHARS // 2:
                end = boundary

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        # Keep some overlapping context.
        next_start = max(0, end - OVERLAP_CHARS)

        # Avoid starting the next chunk inside a word.
        if next_start > 0 and not text[next_start - 1].isspace():
            match = re.search(r"\s", text[next_start:end])
            if match:
                next_start += match.end()

        start = max(start + 1, next_start)

    return chunks


def split_page(text: str) -> list[str]:
    """Keep paragraphs together where possible."""
    paragraphs = [
        p.strip()
        for p in re.split(r"\n\s*\n", text)
        if p.strip()
    ]

    chunks = []
    current = ""

    for paragraph in paragraphs:
        if len(paragraph) > MAX_CHARS:
            if current:
                chunks.append(current)
                current = ""

            chunks.extend(split_long_text(paragraph))
            continue

        candidate = (
            f"{current}\n\n{paragraph}"
            if current
            else paragraph
        )

        if len(candidate) <= MAX_CHARS:
            current = candidate
        else:
            chunks.append(current)
            current = paragraph

    if current:
        chunks.append(current)

    # Merge short trailing chunks when there is space.
    if len(chunks) >= 2 and len(chunks[-1]) < 150:
        merged = chunks[-2] + "\n\n" + chunks[-1]

        if len(merged) <= MAX_CHARS:
            chunks[-2] = merged
            chunks.pop()

    return chunks


def create_chunks(pages: list[dict]) -> list[dict]:
    all_chunks = []

    for page in pages:
        cleaned_text = remove_noise(
            page["text"],
            page["filename"],
        )

        if not cleaned_text:
            continue

        text_chunks = split_page(cleaned_text)

        for index, text in enumerate(text_chunks, start=1):
            all_chunks.append({
                "id": f"{page['id']}_chunk_{index:03d}",
                "sport": page["sport"],
                "document_type": page["document_type"],
                "source": page["source"],
                "filename": page["filename"],
                "page": page["page"],
                "chunk_index": index,
                "text": text,
            })

    return all_chunks


def main() -> None:
    with INPUT_PATH.open(encoding="utf-8") as file:
        pages = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    chunks = create_chunks(pages)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        for chunk in chunks:
            file.write(
                json.dumps(chunk, ensure_ascii=False) + "\n"
            )

    print(f"Input pages: {len(pages)}")
    print(f"Generated chunks: {len(chunks)}")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
