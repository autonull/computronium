"""Mechanism Cookbook v1 (TODO24 Phase 6): certified entries only.

An entry requires a promoted ``MechanismBelief`` (the ``promote_mechanism``
pipeline output) or a boundary belief id for a certified negative result.
Anything else is refused with a recorded reason — never an entry.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from computronium_lab.campaign import MechanismBelief

__all__ = [
    "CookbookEntry",
    "CookbookRefusal",
    "certify_entry",
    "render_cookbook",
]


@dataclass(frozen=True, slots=True)
class CookbookEntry:
    """One certified practitioner entry (TODO24 §6 format)."""

    mechanism: str
    problem_class: str
    constraints: str
    coordinate: dict[str, str]
    evidence: str
    certificates: str
    known_limitations: str
    deployment_notes: str

    def to_dict(self) -> dict[str, object]:
        return {
            "mechanism": self.mechanism,
            "problem_class": self.problem_class,
            "constraints": self.constraints,
            "coordinate": dict(self.coordinate),
            "evidence": self.evidence,
            "certificates": self.certificates,
            "known_limitations": self.known_limitations,
            "deployment_notes": self.deployment_notes,
        }


@dataclass(frozen=True, slots=True)
class CookbookRefusal:
    """Honest refusal: why no entry was certified."""

    mechanism: str
    problem_class: str
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "mechanism": self.mechanism,
            "problem_class": self.problem_class,
            "reason": self.reason,
        }


def certify_entry(
    belief: MechanismBelief | None,
    *,
    problem_class: str,
    constraints: str,
    coordinate: dict[str, str],
    known_limitations: str,
    deployment_notes: str,
    boundary_belief_id: str | None = None,
) -> CookbookEntry | CookbookRefusal:
    """Certify from a promoted belief or a boundary belief id.

    A certified negative result (boundary belief) yields an entry whose
    evidence states the boundary — the ledger distinguishes it from a
    promotion. Returns a ``CookbookRefusal`` otherwise.
    """
    mechanism = belief.mechanism if belief is not None else "unknown"
    if belief is not None and belief.promoted:
        campaigns = ", ".join(f"{c.mechanism}@{c.spec_key}" for c in belief.campaigns)
        return CookbookEntry(
            mechanism=belief.mechanism,
            problem_class=problem_class,
            constraints=constraints,
            coordinate=dict(coordinate),
            evidence=(
                f"belief {belief.belief_id}: campaigns [{campaigns}]; "
                f"controls {dict(belief.control_accuracies)}"
            ),
            certificates="promote_mechanism §18 gates; ledger-audited",
            known_limitations=known_limitations,
            deployment_notes=deployment_notes,
        )
    if boundary_belief_id is not None:
        return CookbookEntry(
            mechanism=mechanism,
            problem_class=problem_class,
            constraints=constraints,
            coordinate=dict(coordinate),
            evidence=(
                f"certified negative result: boundary belief {boundary_belief_id}"
            ),
            certificates="§19 boundary gates; ledger-audited",
            known_limitations=known_limitations,
            deployment_notes=deployment_notes,
        )
    if belief is None:
        reason = "no belief: promotion never attempted or ledger missing"
    else:
        reason = (
            f"belief {belief.belief_id} not promoted "
            f"(violations: {list(belief.violations)})"
        )
    return CookbookRefusal(
        mechanism=mechanism, problem_class=problem_class, reason=reason
    )


def render_cookbook(
    entries: list[CookbookEntry | CookbookRefusal],
) -> str:
    """Markdown cookbook with entries and recorded refusals."""
    lines = ["# Mechanism Cookbook v1", ""]
    certified = [e for e in entries if isinstance(e, CookbookEntry)]
    refused = [e for e in entries if isinstance(e, CookbookRefusal)]
    lines.append(f"Certified entries: {len(certified)}; refusals: {len(refused)}.")
    lines.append("")
    for entry in certified:
        lines.extend([
            f"## {entry.mechanism} — {entry.problem_class}",
            "",
            f"Mechanism: {entry.mechanism}",
            f"Problem class: {entry.problem_class}",
            f"Constraints: {entry.constraints}",
            f"Coordinate: {entry.coordinate}",
            f"Evidence: {entry.evidence}",
            f"Certificates: {entry.certificates}",
            f"Known limitations: {entry.known_limitations}",
            f"Deployment notes: {entry.deployment_notes}",
            "",
        ])
    if refused:
        lines.extend(["## Refusals (no entry without evidence)", ""])
        for refusal in refused:
            lines.append(
                f"- {refusal.mechanism} / {refusal.problem_class}: {refusal.reason}"
            )
        lines.append("")
    return "\n".join(lines)
