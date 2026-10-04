"""Decision types and round controller for the S1-S11 pipeline (WP16)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from computronium.experiment.execution.allocator import Abandonment, Promotion
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

    transition: StageTransition  # CONTINUE | COMPLETE | PAUSE | STOP
    new_proposals: list[Proposal] = field(default_factory=list)
    promotions: list[Promotion] = field(default_factory=list)
    abandonments: list[Abandonment] = field(default_factory=list)
    replications: list[Replication] = field(default_factory=list)
    rationale: str = ""
    budget_impact: float = 0.0


class RoundController:
    """Controls the S3-S10 round loop with Decision-based termination."""

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
    def decision(self) -> Decision | None:
        return self._decision

    def should_continue(self, decision: Decision) -> bool:
        """Determine if the round loop should continue."""
        from computronium.experiment.execution.stage import StageTransition

        self._decision = decision

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
                StageTransition.COMPLETE | StageTransition.PAUSE | StageTransition.STOP
            ):
                return False
            case _:
                return False


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


__all__ = [
    "Decision",
    "Replication",
    "RoundController",
    "complete_run",
    "continue_round",
    "create_decision",
    "pause_run",
    "stop_run",
]
