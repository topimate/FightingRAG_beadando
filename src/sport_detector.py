
import re


SPORT_PATTERNS = {
    "mma": [
        r"\bmma\b",
        r"\bmixed martial arts\b",
    ],
    "muay_thai": [
        r"\bmuay[\s-]*thai\b",
        r"\bmuaythai\b",
        r"\bthai[\s-]*boxing\b",
    ],
    "kickboxing": [
        r"\bk[\s-]*1\b",
        r"\bkick[\s-]*box(?:ing)?\b",
        r"\bkickbox\b",
        r"\bwako\b",
    ],
}


def detect_sports(question: str) -> list[str]:
    """Identify sports explicitly mentioned in a question."""
    detected = []

    for sport, patterns in SPORT_PATTERNS.items():
        if any(
            re.search(pattern, question, re.IGNORECASE)
            for pattern in patterns
        ):
            detected.append(sport)

    return detected
