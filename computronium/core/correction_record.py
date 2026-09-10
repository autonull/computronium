"""CorrectionRecord: schema for tracking superseded measurements (TODO18 1.1).

Every time an audit invalidates a previously published measurement, the
correction is recorded here — original claim, the procedure that audited it,
what it affected, and the replacement metric — so the evidence chain stays
transparent. Published log: ``docs/CORRECTIONS.md``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

__all__ = ["CorrectionRecord", "CorrectionStatus"]

type CorrectionStatus = Literal["corrected", "requires_rerun", "deprecated"]


@dataclass(frozen=True, slots=True)
class CorrectionRecord:
    """One superseded measurement, audited and replaced.

    Attributes:
        original_claim: The claim as previously published.
        original_metric: Metric the claim was based on.
        audited_procedure: Where/how the audit was performed (test, probe, PR).
        affected_conclusions: Downstream conclusions invalidated by the audit.
        replacement_metric: Metric that now backs the corrected claim.
        status: Lifecycle of the correction.
        commit_hash: Commit introducing the correction.
    """

    original_claim: str
    original_metric: str
    audited_procedure: str
    affected_conclusions: tuple[str, ...] = field(default_factory=tuple)
    replacement_metric: str = ""
    status: CorrectionStatus = "corrected"
    commit_hash: str = ""

    def to_row(self) -> dict[str, str | tuple[str, ...]]:
        """Flat dict for rendering into ``docs/CORRECTIONS.md`` tables."""
        return {
            "original_claim": self.original_claim,
            "original_metric": self.original_metric,
            "audited_procedure": self.audited_procedure,
            "affected_conclusions": self.affected_conclusions,
            "replacement_metric": self.replacement_metric,
            "status": self.status,
            "commit_hash": self.commit_hash,
        }
