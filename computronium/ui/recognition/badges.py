"""Badges — ledger-linked, verifiable recognition (M2.3).

8 badges per GAME.md §8.3. Each resolves to a CEEC/KB record with "see evidence" link.
No XP, no points, no streaks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass(frozen=True, slots=True)
class Badge:
    """A verifiable badge with evidence link."""

    id: str
    name: str
    description: str
    icon: str
    evidence_kind: str  # e.g., "ceec_experiment", "kb_cell", "defect_record"
    evidence_query: str  # How to find the evidence (CEEC query, KB key, etc.)
    register_explorer: str
    register_lab: str


# Badge specifications — single source of truth
BADGE_SPECS: tuple[Badge, ...] = (
    Badge(
        id="first_steps",
        name="First Steps",
        description="Completed your first measurement cell",
        icon="👣",
        evidence_kind="kb_cell",
        evidence_query="first completed cell",
        register_explorer="Ran your first experiment",
        register_lab="First cell completed",
    ),
    Badge(
        id="mapmaker",
        name="Mapmaker",
        description="Charted 10 distinct regions on the discovery map",
        icon="🗺️",
        evidence_kind="kb_coverage",
        evidence_query="regions_charted >= 10",
        register_explorer="Mapped 10 regions",
        register_lab="KB coverage: 10+ regions",
    ),
    Badge(
        id="double_checker",
        name="Double-Checker",
        description="Ran 3+ repeat measurements on the same coordinate",
        icon="🔍",
        evidence_kind="kb_cell",
        evidence_query="repeats >= 3 on same coordinate",
        register_explorer="Verified a result 3 times",
        register_lab="3+ repeats on identical coordinate",
    ),
    Badge(
        id="gold_standard",
        name="Gold Standard",
        description="Achieved a Pareto-optimal result on any objective pair",
        icon="🥇",
        evidence_kind="ceec_experiment",
        evidence_query="pareto_optimal == true",
        register_explorer="Found a best trade-off",
        register_lab="Pareto-optimal cell recorded",
    ),
    Badge(
        id="honest_broker",
        name="Honest Broker",
        description="Reported a structural void (gate rejection) — boundaries, not bugs",
        icon="⚖️",
        evidence_kind="structural_void",
        evidence_query="void recorded",
        register_explorer="Found a boundary, not a bug",
        register_lab="Structural void documented",
    ),
    Badge(
        id="repair_crew",
        name="Repair Crew",
        description="Fixed 5+ runtime defects via unquarantine",
        icon="🔧",
        evidence_kind="defect_record",
        evidence_query="resolved_defects >= 5",
        register_explorer="Fixed 5 crashed experiments",
        register_lab="5+ defects unquarantined",
    ),
    Badge(
        id="steady_hand",
        name="Steady Hand",
        description="Ran 50+ cells with zero NaN divergences",
        icon="🤲",
        evidence_kind="kb_cell",
        evidence_query="cells >= 50 AND nan_loss == 0",
        register_explorer="50 clean runs, no blowups",
        register_lab="50+ cells, zero NaN loss",
    ),
    Badge(
        id="cartographer",
        name="Cartographer",
        description="Charted 50% of planned regions in a campaign",
        icon="🧭",
        evidence_kind="kb_coverage",
        evidence_query="coverage_pct >= 50",
        register_explorer="Mapped half the territory",
        register_lab="KB coverage ≥ 50%",
    ),
    Badge(
        id="open_book",
        name="Open Book",
        description="Shared a complete experiment receipt (CEEC ledger chain)",
        icon="📖",
        evidence_kind="ceec_experiment",
        evidence_query="ledger_chain complete",
        register_explorer="Shared full proof",
        register_lab="CEEC chain: Experiment→Evidence→Belief→Gate→Decision",
    ),
)


def check_badge_conditions(event_kind: str, payload: dict) -> Iterable[Badge]:
    """Check if any badges should be awarded for this event.

    Pure function — no side effects. Returns newly-earned badges.
    """
    # This is a simplified version; real implementation would track
    # aggregate state across events. For now, return badges based on
    # single-event conditions.

    if event_kind == "cell_completed":
        # First Steps — would need aggregate tracking
        # For now, check if this is the first cell (would need state)
        pass

    elif event_kind == "defect_resolved":
        # Repair Crew — would need count
        pass

    elif event_kind == "pareto_front_expanded":
        # Gold Standard
        yield BADGE_SPECS[3]  # gold_standard

    elif event_kind == "campaign_complete":
        # Could award multiple based on final stats
        pass

    # Structural void reporting
    if event_kind == "measurement_recorded" and payload.get("is_void"):
        yield BADGE_SPECS[4]  # honest_broker


def get_badge_by_id(badge_id: str) -> Badge | None:
    """Look up a badge by ID."""
    for badge in BADGE_SPECS:
        if badge.id == badge_id:
            return badge
    return None


def get_all_badges() -> tuple[Badge, ...]:
    """Get all badge specifications."""
    return BADGE_SPECS
