"""Verification-label enforcement (TODO18 2.3 / C.4 claim-record linting).

Level 4 sampled numerical test of the repo's own claim hygiene:
- scans every test module under tests/ for banned overclaim phrases;
- scans every docstring under ``computronium/`` for the same;
- scans README.md and docs/*.md (archives exempted — historical record);
- requires that any test mentioning "theorem" labels its level. CI fails
  on violation.
"""

import ast
from pathlib import Path

from computronium.verification import (
    BANNED_PHRASES,
    VerificationLevel,
    render_taxonomy_markdown,
)

_TESTS_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT = _TESTS_ROOT.parent
_SCAN_DIRS = (_TESTS_ROOT / "property", _TESTS_ROOT / "integration")
_PACKAGE_ROOT = _REPO_ROOT / "computronium"
_MD_FILES = (
    _REPO_ROOT / "README.md",
    *(p for p in (_REPO_ROOT / "docs").rglob("*.md") if "archive" not in p.parts),
)


def _iter_test_files():
    for directory in _SCAN_DIRS:
        yield from sorted(directory.rglob("test_*.py"))


def _docstrings(path: Path):
    """Yield (lineno, text) for module/class/function docstrings."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            doc = ast.get_docstring(node)
            if doc:
                yield (
                1 if isinstance(node, ast.Module) else node.lineno
            ), doc.lower()


def _collect_violations(scanned):
    """scanned: iterable of (display_path, texts) — texts iterable of (line, str)."""
    violations = []
    for display, lines in scanned:
        for lineno, text in lines:
            for phrase in BANNED_PHRASES:
                if phrase in text.lower():
                    violations.append(f"{display}:{lineno}: {phrase!r}")
    return violations


def test_no_banned_overclaim_phrases():
    """No test docstring/comment may assert Level 2-3 strength without proof."""
    violations = _collect_violations(
        (
            f"tests/{path.relative_to(_TESTS_ROOT)}",
            enumerate(path.read_text(encoding="utf-8").splitlines(), 1),
        )
        for path in _iter_test_files()
    )
    assert not violations, "banned claim phrases found:\n" + "\n".join(violations)


def test_no_banned_phrases_in_package_docstrings():
    """C.4: computronium/ docstrings carry no banned overclaim phrases."""
    violations = _collect_violations(
        (f"computronium/{path.relative_to(_PACKAGE_ROOT)}", _docstrings(path))
        for path in sorted(_PACKAGE_ROOT.rglob("*.py"))
    )
    assert not violations, "banned claim phrases in docstrings:\n" + "\n".join(
        violations
    )


def test_no_banned_phrases_in_markdown_docs():
    """C.4: README + non-archive docs carry no banned overclaim phrases."""
    violations = _collect_violations(
        (
            str(path.relative_to(_REPO_ROOT)),
            enumerate(path.read_text(encoding="utf-8").splitlines(), 1),
        )
        for path in _MD_FILES
        if path.exists()
    )
    assert not violations, "banned claim phrases found:\n" + "\n".join(violations)


def test_theorem_claims_are_labeled():
    """Any test claiming a theorem must carry an explicit verification level."""
    violations = []
    for path in _iter_test_files():
        text = path.read_text(encoding="utf-8")
        if "theorem" not in text.lower():
            continue
        has_level = any(
            f"Level {lvl.value}" in text or lvl.name in text
            for lvl in VerificationLevel
        )
        if not has_level:
            violations.append(
                f"{path.relative_to(_TESTS_ROOT)}: theorem claim without verification level"
            )
    assert not violations, "unlabeled theorem claims:\n" + "\n".join(violations)


def test_taxonomy_rendering():
    md = render_taxonomy_markdown()
    assert "1. Analytical result" in md
    assert "5. Empirical result" in md
    assert VerificationLevel.SAMPLED_NUMERICAL.description.startswith(
        "Sampled numerical"
    )
