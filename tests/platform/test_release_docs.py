"""Release-doc claim checks (G-RELEASE-4/5, TODO20 T20.8.5).

Each package README must carry validated-scope, limitations, and evidence
sections; external docs must not contain banned overclaim phrases outside
explicit negations.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SCOPE_HEADINGS = ("validated scope", "scope")
LIMIT_HEADINGS = ("known limitations", "limitations", "boundaries")
EVIDENCE_HEADINGS = ("evidence references", "evidence")

BANNED_PHRASES = (
    "solves catastrophic forgetting",
    "replaces backpropagation",
    "universally more efficient",
    "universally superior",
    "replaces backprop",
)

_NEGATION_PREFIXES = ("no claim", "not ", "nothing", "no ", "- no", "neither")


def _readings(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _has_section(text: str, headings: tuple[str, ...]) -> bool:
    return any(
        line.lstrip("# ").strip().lower().startswith(h)
        for line in text.splitlines()
        if line.startswith("#")
        for h in headings
    )


def test_every_package_readme_has_scope_limitations_evidence() -> None:
    for readme in sorted((REPO_ROOT / "packages").glob("*/README.md")):
        text = _readings(readme)
        assert _has_section(text, SCOPE_HEADINGS), f"{readme}: no validated scope"
        assert _has_section(text, LIMIT_HEADINGS), f"{readme}: no limitations"
        assert _has_section(text, EVIDENCE_HEADINGS), f"{readme}: no evidence refs"


def _asserted_lines(text: str) -> list[str]:
    return [
        line
        for line in text.lower().splitlines()
        if not any(line.lstrip("- ").startswith(p) for p in _NEGATION_PREFIXES)
    ]


def test_external_docs_free_of_overclaims() -> None:
    docs = sorted((REPO_ROOT / "docs" / "platform").glob("*.md")) + sorted(
        (REPO_ROOT / "packages").glob("*/README.md")
    )
    for doc in docs:
        asserted = _asserted_lines(_readings(doc))
        lowered = " ".join(asserted).lower()
        for phrase in BANNED_PHRASES:
            assert phrase not in lowered, f"{doc}: banned claim {phrase!r}"


def test_blueprints_state_simulation_only() -> None:
    text = _readings(
        REPO_ROOT / "docs" / "platform" / "NEUROMORPHIC_EDGE_BLUEPRINT.md"
    ).lower()
    assert "simulation only" in text or "no physical hardware validation" in text


def test_manuscript_structure_and_traceability() -> None:
    manuscript = REPO_ROOT / "docs" / "platform" / "MANUSCRIPT.md"
    repro = REPO_ROOT / "docs" / "platform" / "REPRODUCIBILITY.md"
    venue = REPO_ROOT / "docs" / "platform" / "PUBLICATION_VENUE.md"
    for path in (manuscript, repro, venue):
        assert path.exists(), f"missing publication artifact {path}"
    text = _readings(manuscript)
    lowered = text.lower()
    for heading in ("threats to validity", "non-claims", "reproducibility"):
        assert heading in lowered, f"MANUSCRIPT.md missing {heading!r}"
    assert "reproducibility.md" in lowered, (
        "MANUSCRIPT.md must point at REPRODUCIBILITY.md"
    )


def test_reproducibility_maps_numbers_to_evidence() -> None:
    text = _readings(REPO_ROOT / "docs" / "platform" / "REPRODUCIBILITY.md").lower()
    for token in ("e-000018", "e-000028", "uv run", "x-tpc", "x-ali", "x-sta"):
        assert token in text, f"REPRODUCIBILITY.md missing {token!r}"
