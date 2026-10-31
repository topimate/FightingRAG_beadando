
from pathlib import Path

import pymupdf as fitz

DATA_DIR = Path("data/raw")

PDF_FILES = {
    "MMA": "mma_rules.pdf",
    "Muay Thai": "muay_thai_rules.pdf",
    "K-1 (Base Rules)": "k1_rules.pdf",
    "K-1 (Rule Updates)": "k1_rules_updates.pdf",
}


def inspect_pdf(sport: str, filename: str) -> None:
    pdf_path = DATA_DIR / filename

    print(f"\n{'=' * 60}")
    print(f"SPORT: {sport}")
    print(f"FILE: {pdf_path}")
    print("=" * 60)

    if not pdf_path.exists():
        print("ERROR: PDF file not found.")
        return

    with fitz.open(pdf_path) as doc:
        page_lengths = [
            len(page.get_text("text").strip())
            for page in doc
        ]

        empty_pages = [
            index + 1
            for index, length in enumerate(page_lengths)
            if length < 100
        ]

        print(f"Pages: {len(doc)}")
        print(f"Total characters: {sum(page_lengths):,}")
        print(
            "Average characters per page: "
            f"{sum(page_lengths) / max(len(doc), 1):.0f}"
        )
        print(f"Pages with little text: {empty_pages}")

        sample_page = next(
            (
                index
                for index, length in enumerate(page_lengths)
                if length > 500
            ),
            None,
        )

        if sample_page is not None:
            text = doc[sample_page].get_text("text")

            print(f"\nSample from page {sample_page + 1}:")
            print("-" * 60)
            print(text[:1000])
        else:
            print("WARNING: No page with substantial text found.")


def main() -> None:
    for sport, filename in PDF_FILES.items():
        inspect_pdf(sport, filename)


if __name__ == "__main__":
    main()
