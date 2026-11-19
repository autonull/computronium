"""The one capability-gap table (TODO95 D1/D9).

A gap is a primitive the inventory knows about that cannot run: a spec with no
composable axis coordinate, or an axis row whose mechanism is a no-op. It is
recorded here — with the reason and the reopen trigger — and nowhere else. The
census, the surface inventory and the README project this table; the axis
registry derives an unavailable row from it.

An empty table is the healthy state. A new gap gets exactly one row, keyed by
the primitive id every projection already uses; a row without a trigger is
prose, not a gap.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Mapping

#: The reason a spec row with no runtime coordinate cannot be screened. The
#: config classmethod the axis composes through is what is missing; a code path
#: may still exist behind a factory (see ``surface.inventory``).
GAP_REASON: Final[str] = "no config classmethod — a capability gap"


@dataclass(frozen=True, slots=True)
class GapEntry:
    """Why a primitive cannot run, and what reopens it."""

    reason: str
    trigger: str


#: Keyed by primitive id (``primitive.<axis>.<name>``) — the same id the spec
#: registry, the census and the map carry. A gap has a reason and the trigger
#: that reopens it; an empty table is the healthy state.
GAPS: Final[Mapping[str, GapEntry]] = MappingProxyType({
    "primitive.plasticity.rule_state": GapEntry(
        reason=(
            "RuleStatePlasticity has no modulate(): the standard train step "
            "evolves psi but never applies the selected operator, so the "
            "post-step geometry is bit-identical to null (TODO92 §3.9, "
            "one-step parameter fingerprint)."
        ),
        trigger=(
            "a trainer applies apply_operator in the standard step, or a "
            "measured reason to retire the primitive from the inventory"
        ),
    ),
    "primitive.plasticity.substrate_coupled": GapEntry(
        reason=(
            "SubstrateCoupledPlasticity is a no-op at the plasticity protocol "
            "level (psi = sigma; the substrate owns state evolution), so the "
            "standard step is bit-identical to null (TODO92 §3.9, one-step "
            "parameter fingerprint)."
        ),
        trigger=(
            "a substrate carries a separate state through the joint "
            "transition and the standard step reads it, or a measured reason "
            "to retire the primitive from the inventory"
        ),
    ),
})


def gap_for(primitive_id: str) -> GapEntry | None:
    """The declared gap for a primitive id, or ``None`` when it can run."""
    return GAPS.get(primitive_id)


__all__ = ["GAPS", "GapEntry", "gap_for"]
