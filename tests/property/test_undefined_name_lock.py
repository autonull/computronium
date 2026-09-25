"""Undefined names are a blocking defect, and suppression is not a fix.

TODO34 §2.1 found 11 ``reportUndefinedVariable`` sites, two of them live
``NameError``s on GPU/CLI paths. All 11 carried a
``# ruff: ignore[undefined-name]`` directive, which is why ``ruff check``
stayed green: the F821 gate had been silenced at every site it flagged.

Two locks:

* ``ruff check --select F821`` over the whole tree must be clean.
* No source file may suppress ``undefined-name`` — the escape hatch that hid
  the defect is itself the thing being banned, so it cannot be reintroduced
  quietly alongside a new undefined name.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCANNED = ("computronium", "tests", "scripts", "packages")
SUPPRESSION = "undefined-name"


def _ruff_f821() -> str:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "--select",
            "F821",
            "--quiet",
            *SCANNED,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout


def test_no_undefined_names_in_tree() -> None:
    findings = _ruff_f821()
    assert findings == "", f"F821 findings must be fixed, not suppressed:\n{findings}"


def test_undefined_name_is_never_suppressed() -> None:
    roots = [REPO_ROOT / root for root in SCANNED]
    candidates = sorted(p for root in roots for p in root.rglob("*.py"))
    offenders = [
        f"{path.relative_to(REPO_ROOT)}:{line}"
        for path in candidates
        if path != Path(__file__)
        for line, text in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        )
        if SUPPRESSION in text
    ]
    assert offenders == [], (
        f"`{SUPPRESSION}` is suppressed at {offenders}; an undefined name is a "
        "crash, not a lint finding — import or define the name instead"
    )


@pytest.mark.parametrize("module", ["computronium", "tests", "scripts", "packages"])
def test_scanned_roots_exist(module: str) -> None:
    assert (REPO_ROOT / module).is_dir()
