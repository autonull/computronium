"""G8: the findings page cannot outlive the documents that support them.

Each row names a document, a headline number and a lock. The number is quoted —
never recomputed — so this asserts it still appears in the document (minus signs
normalised) and that ``docs/FINDINGS.md`` names the document at all. Retracting
a result means editing its document and the page in the same commit. The README
must link the page, so a findings section cannot disappear from the front door.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
README = (REPO / "README.md").read_text(encoding="utf-8")
FINDINGS_PAGE = (REPO / "docs" / "FINDINGS.md").read_text(encoding="utf-8")

# (document, headline number or token, checkable lock)
FINDINGS = (
    ("docs/eqprop_deep_limitation.md", "1.19", "G2"),
    ("docs/eqprop_deep_limitation.md", "9.2", "G2"),
    ("docs/phantom_knob_audit.md", "phantom_knobs", "validate_all_rule_spaces"),
    ("docs/CORRECTIONS.md", "10.025", "test_jacobian_amplification"),
)


def _normalise(text: str) -> str:
    return text.replace("\u2212", "-")


def test_the_readme_links_the_findings_page() -> None:
    assert "docs/FINDINGS.md" in README


@pytest.mark.parametrize(("document", "number", "lock"), FINDINGS)
def test_a_finding_quotes_its_document(document: str, number: str, lock: str) -> None:
    path = REPO / document
    assert path.exists(), f"the findings page names a document that is gone: {document}"
    assert document in FINDINGS_PAGE, f"the findings page does not name {document}"
    body = _normalise(path.read_text(encoding="utf-8"))
    assert _normalise(number) in body, (
        f"{document} no longer contains its headline {number!r}; "
        "the findings page quote is stale"
    )
    assert lock in body or lock in FINDINGS_PAGE
