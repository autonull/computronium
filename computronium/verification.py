"""Verification Taxonomy: the five levels of evidential strength (TODO18 2.3).

1. ANALYTICAL — derivation in docs; hand-checked math.
2. MACHINE_CHECKED — Lean/Coq/Rocq artifact.
3. CERTIFIED_NUMERICAL — interval arithmetic / enclosures.
4. SAMPLED_NUMERICAL — hypothesis/pytest sampling.
5. EMPIRICAL — task-performance measurement.

The CI gate relies primarily on Level 4 and Level 5. Test docstrings must
label their strongest claim with the level it actually meets; the word
"proof" is reserved for Levels 1-2, "certified" for Level 3.
"""

from __future__ import annotations

from enum import StrEnum

__all__ = ["BANNED_PHRASES", "VerificationLevel", "render_taxonomy_markdown"]


class VerificationLevel(StrEnum):
    """Evidence tier of a claim, weakest to strongest."""

    ANALYTICAL = "1"
    MACHINE_CHECKED = "2"
    CERTIFIED_NUMERICAL = "3"
    SAMPLED_NUMERICAL = "4"
    EMPIRICAL = "5"

    @property
    def description(self) -> str:
        return _DESCRIPTIONS[self]


_DESCRIPTIONS: dict[VerificationLevel, str] = {
    VerificationLevel.ANALYTICAL: "Analytical result (derivation in docs)",
    VerificationLevel.MACHINE_CHECKED: "Machine-checked theorem (Lean/Coq artifact)",
    VerificationLevel.CERTIFIED_NUMERICAL: "Certified numerical bound (interval arithmetic/enclosures)",
    VerificationLevel.SAMPLED_NUMERICAL: "Sampled numerical test (hypothesis/pytest)",
    VerificationLevel.EMPIRICAL: "Empirical result (task performance)",
}


def render_taxonomy_markdown() -> str:
    """Render the taxonomy as a Markdown numbered list (docs/README use)."""
    return (
        "\n".join(f"{lvl.value}. {lvl.description}" for lvl in VerificationLevel) + "\n"
    )


# Phrases banned from pytest/test docstrings unless the claim meets Level 2/3.
BANNED_PHRASES: tuple[str, ...] = (
    "formal proof",
    "formally proven",
    "machine-checked theorem",
    "mathematically certified",
    "no weight transport",
    "upper bound via power iteration",
)
