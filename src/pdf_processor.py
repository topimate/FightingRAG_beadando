
from pathlib import Path
import json
import re

import pymupdf


PDF_CONFIG = [
    {
        "filename": "mma_rules.pdf",
        "sport": "mma",
        "document_type": "base",
        "source": "ABC Unified Rules of MMA",
    },
    {
        "filename": "muay_thai_rules.pdf",
        "sport": "muay_thai",
        "document_type": "base",
        "source": "IFMA Muaythai Rules and Regulations",
    },
    {
        "filename": "k1_rules.pdf",
        "sport": "kickboxing",
        "document_type": "base",
        "source": "WAKO K-1 Rules V18",
    },
    {
        "filename": "k1_rules_updates.pdf",
        "sport": "kickboxing",
        "document_type": "amendment",
        "source": "WAKO K-1 Rules Changes",
    },
]


def clean_text(text: str) -> str:
    """Remove unnecessary whitespace without losing paragraphs."""
    text = text.replace("\u00a0", " ")

    # Normalize spaces inside lines.
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_document(
    pdf_path: Path,
    metadata: dict,
) -> list[dict]:
    """Extract pages and preserve document metadata."""
    records = []

    with pymupdf.open(pdf_path) as doc:
        for page_index, page in enumerate(doc):
            text = clean_text(page.get_text("text"))

            if not text:
                continue

            records.append(
                {
                    "id": (
                        f"{pdf_path.stem}_"
                        f"page_{page_index + 1:03d}"
                    ),
                    "sport": metadata["sport"],
                    "document_type": metadata["document_type"],
                    "source": metadata["source"],
                    "filename": metadata["filename"],
                    "page": page_index + 1,
                    "text": text,
                }
            )

    return records


def process_all_pdfs(
    input_dir: Path = Path("data/raw"),
    output_path: Path = Path("data/processed/pages.jsonl"),
) -> None:
    """Extract all configured PDF documents into JSONL."""
    all_records = []

    for metadata in PDF_CONFIG:
        pdf_path = input_dir / metadata["filename"]

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"Missing PDF: {pdf_path}"
            )

        records = extract_document(pdf_path, metadata)
        all_records.extend(records)

        print(
            f"{metadata['source']}: "
            f"{len(records)} pages extracted"
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        for record in all_records:
            file.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )

    print(f"\nTotal records: {len(all_records)}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    process_all_pdfs()
