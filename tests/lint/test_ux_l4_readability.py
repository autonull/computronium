"""UX-L4: readability lint — Explorer strings ≤ FK grade 8 (CI lint gate)."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.lint_readability import (
    check_readability,
    count_syllables,
    flesch_kincaid_grade,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
GLOSSARY = REPO_ROOT / "computronium" / "ui" / "glossary.json"


def test_count_syllables_basic() -> None:
    assert count_syllables("cat") == 1
    assert count_syllables("water") == 2
    assert count_syllables("the") == 1
    assert count_syllables("") == 0


def test_flesch_kincaid_grade_simple_vs_complex() -> None:
    simple = "The cat sat on the mat."
    complex_text = (
        "The electroencephalographically characterized multidimensional "
        "representation demonstrates incomprehensibly pathological "
        "institutionalization tendencies."
    )
    assert flesch_kincaid_grade(simple) < flesch_kincaid_grade(complex_text)


def test_flesch_kincaid_grade_empty_is_zero() -> None:
    assert flesch_kincaid_grade("") == 0.0
    assert flesch_kincaid_grade("   ") == 0.0


def test_glossary_file_exists_and_parses() -> None:
    assert GLOSSARY.exists()
    data = json.loads(GLOSSARY.read_text(encoding="utf-8"))
    assert "terms" in data


def test_check_readability_returns_sorted_issues(tmp_path: Path) -> None:
    glossary = {
        "terms": {
            "easy": {
                "explorer": "The cat sat on the mat. It was fat.",
                "lab": "feline_resting_posture",
            },
            "hard": {
                "explorer": (
                    "The electroencephalographically characterized "
                    "multidimensional representation demonstrates "
                    "incomprehensibly pathological institutionalization."
                ),
                "lab": "hard_term",
            },
            "lab_only": {"lab": "no_explorer_string"},
        }
    }
    path = tmp_path / "glossary.json"
    path.write_text(json.dumps(glossary), encoding="utf-8")

    issues = check_readability(path, max_grade=8.0)
    keys = [i["key"] for i in issues]
    assert "hard" in keys
    assert "easy" not in keys
    assert "lab_only" not in keys
    # Sorted descending by grade
    grades = [i["grade"] for i in issues]
    assert grades == sorted(grades, reverse=True)


def test_script_main_runs_on_repo_glossary(tmp_path: Path) -> None:
    """Smoke: lint script executes end-to-end against the real glossary."""
    import subprocess  # ruff: ignore[suspicious-subprocess-import]
    import sys

    out = tmp_path / "audit.json"
    result = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "lint_readability.py"),
            "--glossary",
            str(GLOSSARY),
            "--output",
            str(out),
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO_ROOT,
        check=False,
    )
    assert result.returncode in {0, 1}, result.stderr
    assert out.exists()
    report = json.loads(out.read_text(encoding="utf-8"))
    assert "issues" in report
