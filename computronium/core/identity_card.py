"""AlgorithmIdentityCard: per-primitive provenance schema (TODO18 1.2).

One card per Credit / Update / Plasticity primitive, attached as a class
attribute. The card pins the primitive to its reference equations, states
deviations from the literature, and names the exact pseudo-gradient — so
comparisons across the ontology axes are made against stated math, not
marketing labels.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["AlgorithmIdentityCard"]


@dataclass(frozen=True, slots=True)
class AlgorithmIdentityCard:
    """Provenance record for one learning-mechanism primitive.

    Attributes:
        name: Primitive name as registered in the ontology.
        reference_equations: Link to paper/arXiv/equations the math follows.
        deviations_from_literature: Stated departures from the reference.
        objective_function: Objective optimized, if the primitive has one.
        pseudo_gradient_def: Exact definition of the pseudo-gradient signal.
        symmetry_requirements: Symmetry/reciprocity the primitive requires.
        approximation_parameters: Sampling/approximation knobs and their bias.
        validated_limits: Regimes where behavior is actually validated.
    """

    name: str
    reference_equations: str
    deviations_from_literature: tuple[str, ...] = field(default_factory=tuple)
    objective_function: str | None = None
    pseudo_gradient_def: str = ""
    symmetry_requirements: tuple[str, ...] = field(default_factory=tuple)
    approximation_parameters: tuple[str, ...] = field(default_factory=tuple)
    validated_limits: tuple[str, ...] = field(default_factory=tuple)

    def to_markdown_row(self) -> str:
        """One ``|``-delimited table row for docs/README tables."""
        return (
            f"| {self.name} | {self.reference_equations} | "
            f"{'; '.join(self.deviations_from_literature) or '—'} | "
            f"{self.objective_function or '—'} | {self.pseudo_gradient_def} | "
            f"{'; '.join(self.symmetry_requirements) or '—'} |"
        )


IDENTITY_CARD_HEADER = (
    "| Name | Reference | Deviations | Objective | Pseudo-gradient | Symmetry |\n"
    "|---|---|---|---|---|---|\n"
)


def render_identity_card_table(
    cards: list[AlgorithmIdentityCard],
) -> str:
    """Render cards as a Markdown table for docs/README generation."""
    return IDENTITY_CARD_HEADER + "\n".join(c.to_markdown_row() for c in cards) + "\n"
