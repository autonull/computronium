"""Readability Lint (UX-L4) — check Explorer strings Flesch-Kincaid grade level.

Self-contained FK grade calculation (no third-party NLP dependency):
FK = 0.39 * (words/sentences) + 11.8 * (syllables/word) - 15.59.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

_VOWELS = "aeiouy"
_SENTENCE_SPLIT = re.compile(r"[.!?]+")
_WORD_SPLIT = re.compile(r"[^a-z']+")


def count_syllables(word: str) -> int:
    """Estimate syllable count via vowel-group heuristic (min 1 per word)."""
    word = word.lower().strip("'")
    if not word:
        return 0
    groups = re.findall(rf"[{_VOWELS}]+", word)
    count = len(groups)
    if word.endswith("e") and not word.endswith(("le", "ee", "ye")) and count > 1:
        count -= 1
    if word.endswith("ed") and not word.endswith(("ted", "ded")) and count > 1:
        count -= 1
    return max(1, count)


def flesch_kincaid_grade(text: str) -> float:
    """Compute Flesch-Kincaid grade level for a text sample."""
    sentences = [s for s in _SENTENCE_SPLIT.split(text) if s.strip()] or [text]
    words = [w for w in _WORD_SPLIT.split(text.lower()) if w]
    if not words:
        return 0.0
    syllables = sum(count_syllables(w) for w in words)
    return (
        0.39 * (len(words) / len(sentences)) + 11.8 * (syllables / len(words)) - 15.59
    )


def check_readability(
    glossary_path: Path, max_grade: float = 8.0
) -> list[dict[str, Any]]:
    """Return Explorer strings exceeding the FK grade threshold."""
    glossary = json.loads(glossary_path.read_text(encoding="utf-8"))
    terms = glossary.get("terms", {})

    issues = []
    for key, registers in terms.items():
        if "explorer" not in registers:
            continue
        text = registers["explorer"]
        if not text or text.isspace():
            continue
        grade = flesch_kincaid_grade(text)
        if grade > max_grade:
            issues.append({
                "key": key,
                "text": text,
                "grade": round(grade, 1),
                "max_grade": max_grade,
            })

    return sorted(issues, key=lambda x: x["grade"], reverse=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="comp lint-readability",
        description="Check Flesch-Kincaid readability of Explorer strings",
    )
    parser.add_argument(
        "--glossary",
        type=Path,
        default=Path("computronium/ui/glossary.json"),
        help="Path to glossary.json",
    )
    parser.add_argument(
        "--max-grade",
        type=float,
        default=8.0,
        help="Maximum Flesch-Kincaid grade level (default: 8.0)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/readability_audit.json"),
        help="Output audit report",
    )
    args = parser.parse_args()

    print(f"Glossary: {args.glossary}")
    print(f"Max grade: {args.max_grade}")

    issues = check_readability(args.glossary, args.max_grade)

    if issues:
        print(f"\n❌ READABILITY ISSUES ({len(issues)}):")
        for issue in issues[:20]:
            print(f"  [{issue['grade']:.1f}] {issue['key']}: {issue['text'][:80]}")
    else:
        print("\n✅ All Explorer strings pass readability check (≤ FK grade 8)")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps({"max_grade": args.max_grade, "issues": issues}, indent=2)
    )
    print(f"\nFull audit report: {args.output}")

    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
