"""Generic hard-constraint validator interface (T20.2.3).

External projects plug in project-specific hard constraints (e.g.
coordinate validation, budget ceilings) that gate evidence promotion.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class ConstraintResult:
    """Outcome of one hard-constraint validation."""

    name: str
    passed: bool
    detail: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class ConstraintValidator(Protocol):
    """A hard constraint evaluated against a candidate record.

    ``candidate`` is the ledger object (artifact/evidence/belief/experiment)
    as a plain dict of public fields. Implementations must be pure.
    """

    def validate(self, candidate: dict[str, Any]) -> ConstraintResult: ...


def validate_all(
    validators: list[ConstraintValidator], candidate: dict[str, Any]
) -> list[ConstraintResult]:
    """Run every validator; return all results (hard constraints AND results)."""
    return [v.validate(candidate) for v in validators]


def all_passed(results: list[ConstraintResult]) -> bool:
    return all(r.passed for r in results)
