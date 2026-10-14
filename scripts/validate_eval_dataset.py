"""Validate the FightRAG 30-question evaluation dataset.

Run from the FightRAG repository root:
    python -m scripts.validate_eval_dataset
"""

import csv
import re
from collections import Counter
from pathlib import Path

DATASET = Path('data/evaluation/questions_verified_30.csv')
RAW_DIR = Path('data/raw')
EXPECTED_COUNTS = {
    'single': 10,
    'comparison': 10,
    'triple_comparison': 5,
    'unanswerable': 5,
}
PDF_PAGES = {
    'mma_rules.pdf': 9,
    'muay_thai_rules.pdf': 94,
    'k1_rules.pdf': 10,
    'k1_rules_updates.pdf': 3,
}
REQUIRED_FIELDS = (
    'id', 'category', 'sports', 'question', 'expected_answer',
    'reference_sources', 'answerable', 'split',
)


def main():
    errors = []
    with DATASET.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if any(c not in reader.fieldnames for c in REQUIRED_FIELDS):
            raise ValueError('Missing required CSV column(s).')
        rows = list(reader)

    ids = [r['id'] for r in rows]
    questions = [r['question'].strip().casefold() for r in rows]
    if len(rows) != 30 or len(set(ids)) != 30:
        errors.append('Expected exactly 30 rows with unique IDs.')
    if len(set(questions)) != len(questions):
        errors.append('Duplicate questions found.')

    counts = Counter(r['category'] for r in rows)
    if dict(counts) != EXPECTED_COUNTS:
        errors.append(f'Unexpected category counts: {dict(counts)}')

    splits = Counter(r['split'] for r in rows)
    if splits != {'development': 8, 'evaluation': 22}:
        errors.append(f'Unexpected split sizes: {dict(splits)}')

    for r in rows:
        qid = r['id']
        if not r['question'].strip() or not r['expected_answer'].strip():
            errors.append(f'{qid}: blank question/reference answer')
        sports = r['sports'].split('|')
        if not set(sports) <= {'mma', 'muay_thai', 'kickboxing'}:
            errors.append(f'{qid}: unknown sport in {sports}')
        if r['answerable'] not in ('True', 'False'):
            errors.append(f'{qid}: invalid answerable flag')
        if r['answerable'] == 'True' and not r['reference_sources']:
            errors.append(f'{qid}: no source for answerable question')
        if r['answerable'] == 'False' and r['reference_sources']:
            errors.append(f'{qid}: unanswerable question has source reference')

        for ref in filter(None, r['reference_sources'].split('|')):
            match = re.fullmatch(r'([^:]+):p(\d+)(?:-(\d+))?', ref)
            if not match:
                errors.append(f'{qid}: invalid source format: {ref}')
                continue
            name, start, end = match.group(1), int(match.group(2)), int(match.group(3) or match.group(2))
            if name not in PDF_PAGES or start < 1 or end > PDF_PAGES.get(name, 0) or start > end:
                errors.append(f'{qid}: invalid PDF page range: {ref}')
            if not (RAW_DIR / name).exists():
                errors.append(f'{qid}: missing PDF in data/raw/: {name}')

    print(f'Total questions: {len(rows)}')
    print('Category counts:', dict(counts))
    print('Dataset splits:', dict(splits))
    print(f'Answerable: {sum(r["answerable"] == "True" for r in rows)}')
    print(f'Unanswerable: {sum(r["answerable"] == "False" for r in rows)}')

    if errors:
        print('\nVALIDATION FAILED:')
        for err in errors:
            print('-', err)
        raise SystemExit(1)

    print('\nVALIDATION OK: the dataset is structurally consistent.')


if __name__ == '__main__':
    main()
