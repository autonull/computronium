"""Decision types and round controller for the S1-S11 pipeline (WP16).

Extended with deadline-aware termination and QUARANTINE state for
hard deadline enforcement (TODO55 Phase E).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from computronium.experiment.execution.allocator import Abandonment, Promotion
    from computronium.experiment.execution.deadline import Deadline
    from computronium.experiment.execution.stage import Proposal, StageTransition
    from computronium.experiment.schema.coordinate import Coordinate, Schedule


@dataclass(frozen=True, slots=True)
class Replication:
    """A request for additional replication seeds."""

    coordinate: Coordinate
    base_schedule: Schedule
    additional_seeds: int
    rationale: str


@dataclass(frozen=True, slots=True)
class Decision:
    """Decision from S10 Decide stage."""

    transition: StageTransition  # CONTINUE | COMPLETE | PAUSE | STOP | QUARANTINE
    new_proposals: list[Proposal] = field(default_factory=list)
    promotions: list[Promotion] = field(default_factory=list)
    abandonments: list[Abandonment] = field(default_factory=list)
    replications: list[Replication] = field(default_factory=list)
    rationale: str = ""
    budget_impact: float = 0.0
    # Deadline-aware fields
    deadline_expired: bool = False
    deadline_reason: str = ""


class RoundController:
    """Controls the S3-S10 round loop with Decision-based termination.

    Extended with deadline-aware termination for hard deadline enforcement.
    """

    def __init__(
        self,
        max_rounds: int | None = None,
        min_rounds: int = 1,
    ) -> None:
        self._max_rounds = max_rounds
        self._min_rounds = min_rounds
        self._current_round = 0
        self._decision: Decision | None = None

    @property
    def current_round(self) -> int:
        return self._current_round

    @property
    def max_rounds(self) -> int | None:
        return self._max_rounds

    @property
    def min_rounds(self) -> int:
        return self._min_rounds

    @property
    def decision(self) -> Decision | None:
        return self._decision

    def should_continue(
        self, decision: Decision, deadline: Deadline | None = None
    ) -> bool:
        """Determine if the round loop should continue.

        Args:
            decision: The decision from S10 Decide stage
            deadline: Optional hard deadline. If provided and expired,
                     forces STOP regardless of decision.
        """
        from computronium.experiment.execution.stage import StageTransition

        self._decision = decision

        # Hard deadline takes precedence over everything
        if deadline is not None and deadline.expired():
            return False

        # Check if we've already completed the minimum required rounds
        if self._current_round < self._min_rounds:
            self._current_round += 1
            return True

        # Check max rounds
        if self._max_rounds is not None and self._current_round >= self._max_rounds:
            return False

        # Check decision transition
        match decision.transition:
            case StageTransition.CONTINUE:
                self._current_round += 1
                return True
            case (
                StageTransition.COMPLETE
                | StageTransition.PAUSE
                | StageTransition.STOP
                | StageTransition.QUARANTINE
            ):
                return False
            case _:
                return False

    def should_continue_simple(self, decision: Decision) -> bool:
        """Backward-compatible version without deadline check.

        For use in contexts where deadline is managed externally.
        """
        return self.should_continue(decision, deadline=None)


def create_decision(
    transition: StageTransition,
    *,
    new_proposals: list[Proposal] | None = None,
    promotions: list[Promotion] | None = None,
    abandonments: list[Abandonment] | None = None,
    replications: list[Replication] | None = None,
    rationale: str = "",
    budget_impact: float = 0.0,
) -> Decision:
    """Factory for creating Decision objects."""
    return Decision(
        transition=transition,
        new_proposals=new_proposals or [],
        promotions=promotions or [],
        abandonments=abandonments or [],
        replications=replications or [],
        rationale=rationale,
        budget_impact=budget_impact,
    )


# Convenience factories
def continue_round(
    new_proposals: list[Proposal] | None = None,
    promotions: list[Promotion] | None = None,
    abandonments: list[Abandonment] | None = None,
    replications: list[Replication] | None = None,
    rationale: str = "",
    budget_impact: float = 0.0,
) -> Decision:
    from computronium.experiment.execution.stage import StageTransition

    return create_decision(
        StageTransition.CONTINUE,
        new_proposals=new_proposals,
        promotions=promotions,
        abandonments=abandonments,
        replications=replications,
        rationale=rationale,
        budget_impact=budget_impact,
    )


def complete_run(
    rationale: str = "",
    budget_impact: float = 0.0,
) -> Decision:
    from computronium.experiment.execution.stage import StageTransition

    return create_decision(
        StageTransition.COMPLETE,
        rationale=rationale,
        budget_impact=budget_impact,
    )


def pause_run(
    rationale: str = "",
) -> Decision:
    from computronium.experiment.execution.stage import StageTransition

    return create_decision(
        StageTransition.PAUSE,
        rationale=rationale,
    )


def stop_run(
    rationale: str = "",
) -> Decision:
    from computronium.experiment.execution.stage import StageTransition

    return create_decision(
        StageTransition.STOP,
        rationale=rationale,
    )


def quarantine_run(
    rationale: str = "Hard deadline exceeded",
) -> Decision:
    """Create a QUARANTINE decision (hard deadline exceeded mid-cell).

    Cells interrupted by deadline are marked QUARANTINE for later analysis.
    """
    from computronium.experiment.execution.stage import StageTransition

    return create_decision(
        StageTransition.QUARANTINE,
        rationale=rationale,
    )


def deadline_expired(
    rationale: str = "Hard deadline expired",
) -> Decision:
    """Create a COMPLETE decision due to deadline expiration.

    Used when the deadline expires cleanly between cells.
    """
    from computronium.experiment.execution.stage import StageTransition

    return create_decision(
        StageTransition.COMPLETE,
        rationale=rationale,
        budget_impact=0.0,
    )


def continue_round_deadline(
    deadline: Deadline,
    new_proposals: list[Proposal] | None = None,
    promotions: list[Promotion] | None = None,
    abandonments: list[Abandonment] | None = None,
    replications: list[Replication] | None = None,
    rationale: str = "",
    budget_impact: float = 0.0,
) -> Decision:
    """Create a CONTINUE decision with deadline awareness.

    Includes deadline status in the decision for traceability.
    """
    from computronium.experiment.execution.stage import StageTransition

    remaining = deadline.remaining_soft_seconds()
    deadline_reason = (
        f"Remaining: {remaining:.1f}s" if remaining > 0 else "Deadline exceeded"
    )

    decision = create_decision(
        StageTransition.CONTINUE,
        new_proposals=new_proposals,
        promotions=promotions,
        abandonments=abandonments,
        replications=replications,
        rationale=rationale,
        budget_impact=budget_impact,
    )
    # Note: deadline_expired and deadline_reason are not in create_decision signature
    # but Decision dataclass has them as optional fields
    return Decision(
        transition=decision.transition,
        new_proposals=decision.new_proposals,
        promotions=decision.promotions,
        abandonments=decision.abandonments,
        replications=decision.replications,
        rationale=decision.rationale,
        budget_impact=decision.budget_impact,
        deadline_expired=deadline.expired(),
        deadline_reason=deadline_reason,
    )


__all__ = [
    "Decision",
    "Replication",
    "RoundController",
    "complete_run",
    "continue_round",
    "continue_round_deadline",
    "create_decision",
    "deadline_expired",
    "pause_run",
    "quarantine_run",
    "stop_run",
]
