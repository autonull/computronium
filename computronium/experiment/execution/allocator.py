"""Allocation policy for experiment execution (WP4)."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from computronium.experiment.schema.coordinate import Coordinate

if TYPE_CHECKING:
    from computronium.experiment.execution.budget import Budget, CostModel
    from computronium.experiment.schema.coordinate import Schedule
    from computronium.experiment.schema.record import Record


logger = logging.getLogger(__name__)


@runtime_checkable
class AllocationPolicy(Protocol):
    """Protocol for allocation policies that decide which cells to execute next.

    Allocation policies implement evidence-driven successive promotion (R46-R51):
    they observe results from lower-fidelity runs and promote promising cells
    to higher-fidelity evaluation.
    """

    def propose(
        self,
        candidates: list[tuple[Coordinate, Schedule]],
        records: list[Record],
        budget: Budget,
        cost_model: CostModel,
    ) -> list[tuple[Coordinate, Schedule]]:
        """Propose next cells to evaluate.

        Args:
            candidates: Available (coordinate, schedule) pairs to choose from
            records: Previously completed records for evidence-driven decisions
            budget: Current budget state
            cost_model: Cost model for estimation

        Returns:
            List of proposed (coordinate, schedule) pairs to evaluate next.
        """
        ...

    def observe(self, record: Record) -> None:
        """Incorporate a completed record into the policy's evidence base.

        Args:
            record: Completed experiment record.
        """
        ...


@dataclass(frozen=True, slots=True)
class PromotionCandidate:
    """A cell candidate for promotion to higher fidelity."""

    cell_key: str
    coordinate: Coordinate
    current_fidelity: str
    current_seed: int
    best_score: float
    n_seeds_completed: int
    divergence_score: float = 0.0
    stagnation_score: float = 0.0


@dataclass(slots=True)
class AllocationState:
    """Internal state for evidence-driven allocation.

    Tracks promotion candidates, divergence/stagnation telemetry,
    and waste reporting data.
    """

    # Cell_key -> PromotionCandidate
    promotion_candidates: dict[str, PromotionCandidate] = field(default_factory=dict)

    # Cell_key -> list of (fidelity, seed, score) for telemetry
    fidelity_history: dict[str, list[tuple[str, int, float]]] = field(
        default_factory=dict
    )

    # Waste report data
    wasted_evaluations: int = 0
    promoted_cells: int = 0
    pruned_cells: int = 0

    # Telemetry
    divergence_score: float = 0.0
    stagnation_score: float = 0.0


class EvidenceDrivenAllocator:
    """Reference implementation of evidence-driven successive promotion (R46-R51).

    Observes results from lower-fidelity runs and promotes promising cells
    to higher-fidelity evaluation. Implements divergence and stagnation
    detection with waste reporting.
    """

    def __init__(
        self,
        *,
        promotion_threshold: float = 0.1,  # Minimum improvement to promote
        divergence_threshold: float = 2.0,  # Score multiplier for divergence
        stagnation_patience: int = 3,  # Seeds without improvement before stagnation
        max_fidelity: str = "L2",
        fidelities: tuple[str, ...] = ("L0", "L1", "L2"),
    ) -> None:
        self._state = AllocationState()
        self._promotion_threshold = promotion_threshold
        self._divergence_threshold = divergence_threshold
        self._stagnation_patience = stagnation_patience
        self._max_fidelity = max_fidelity
        self._fidelities = fidelities
        self._fidelity_order = {f: i for i, f in enumerate(fidelities)}

    def propose(
        self,
        candidates: list[tuple[Coordinate, Schedule]],
        records: list[Record],
        budget: Budget,
        cost_model: CostModel,
    ) -> list[tuple[Coordinate, Schedule]]:
        """Propose next cells using evidence-driven promotion."""
        # Update state with new records
        for record in records:
            self.observe(record)

        # Filter candidates by budget
        affordable = self._filter_affordable(candidates, budget, cost_model)
        if not affordable:
            return []

        # Separate new cells from promotion candidates
        new_cells, promotions = self._categorize_candidates(affordable)

        # Prioritize promotions first (evidence-driven)
        proposals = []
        proposals.extend(self._select_promotions(promotions, budget, cost_model))
        proposals.extend(
            self._select_new_cells(new_cells, budget, cost_model, len(proposals))
        )

        return proposals

    def observe(self, record: Record) -> None:
        """Incorporate a completed record into the evidence base."""
        cell_key = record.cell_key
        fidelity = record.schedule.fidelity
        seed = record.schedule.seed
        score = self._extract_score(record)

        # Update fidelity history
        if cell_key not in self._state.fidelity_history:
            self._state.fidelity_history[cell_key] = []
        self._state.fidelity_history[cell_key].append((fidelity, seed, score))

        # Check for divergence
        if self._is_divergent(cell_key, score):
            self._state.divergence_score = score
            logger.warning(
                "Cell %s diverged at %s seed %d: score=%f",
                cell_key,
                fidelity,
                seed,
                score,
            )
            self._state.wasted_evaluations += 1
            return

        # Check for stagnation
        if self._is_stagnant(cell_key):
            logger.info("Cell %s stagnated at %s", cell_key, fidelity)
            self._state.stagnation_score = score
            return

        # Update or create promotion candidate
        self._update_promotion_candidate(cell_key, record, score)

    def _extract_score(self, record: Record) -> float:
        """Extract primary score from record payload."""
        # Try common metric names in order of preference
        for key in ("val_acc", "test_acc", "accuracy", "score", "loss"):
            if key in record.payload:
                val = record.payload[key]
                if isinstance(val, (int, float)):
                    return float(val)
        return 0.0

    def _is_divergent(self, cell_key: str, current_score: float) -> bool:
        """Check if a cell has diverged (score exploded)."""
        history = self._state.fidelity_history.get(cell_key, [])
        if len(history) < 2:
            return False
        # Check if current score is much worse than best
        best = max(h[2] for h in history[:-1])
        return current_score > best * self._divergence_threshold if best > 0 else False

    def _is_stagnant(self, cell_key: str) -> bool:
        """Check if a cell has stagnated (no improvement across seeds)."""
        history = self._state.fidelity_history.get(cell_key, [])
        if len(history) < self._stagnation_patience:
            return False
        recent = history[-self._stagnation_patience :]
        scores = [h[2] for h in recent]
        return max(scores) - min(scores) < 1e-4  # No meaningful improvement

    def _update_promotion_candidate(
        self, cell_key: str, record: Record, score: float
    ) -> None:
        """Update or create a promotion candidate."""
        fidelity = record.schedule.fidelity
        current_idx = self._fidelity_order.get(fidelity, 0)

        if current_idx >= len(self._fidelities) - 1:
            return  # Already at max fidelity

        next_fidelity = self._fidelities[current_idx + 1]

        if cell_key in self._state.promotion_candidates:
            candidate = self._state.promotion_candidates[cell_key]
            if score > candidate.best_score + self._promotion_threshold:
                # Significant improvement - update and allow promotion
                self._state.promotion_candidates[cell_key] = PromotionCandidate(
                    cell_key=candidate.cell_key,
                    coordinate=candidate.coordinate,
                    current_fidelity=next_fidelity,
                    current_seed=record.schedule.seed,
                    best_score=score,
                    n_seeds_completed=candidate.n_seeds_completed + 1,
                    divergence_score=candidate.divergence_score,
                    stagnation_score=candidate.stagnation_score,
                )
        else:
            # New candidate at next fidelity
            self._state.promotion_candidates[cell_key] = PromotionCandidate(
                cell_key=cell_key,
                coordinate=Coordinate(
                    substrate=record.substrate,
                    geometry=record.geometry,
                    dynamics=record.dynamics,
                    plasticity=record.plasticity,
                    credit=record.credit,
                    update=record.update,
                    params=record.params,
                ),
                current_fidelity=next_fidelity,
                current_seed=record.schedule.seed,
                best_score=score,
                n_seeds_completed=1,
            )

    def _filter_affordable(
        self,
        candidates: list[tuple[Coordinate, Schedule]],
        budget: Budget,
        cost_model: CostModel,
    ) -> list[tuple[Coordinate, Schedule]]:
        """Filter candidates that fit within remaining budget."""
        affordable = []
        for coord, sched in candidates:
            cost = cost_model.estimate_cost(
                (
                    coord.substrate,
                    coord.geometry,
                    coord.dynamics,
                    coord.plasticity,
                    coord.credit,
                    coord.update,
                    coord.params,
                ),
                sched.to_dict(),
            )
            if (
                budget.target_cost is None
                or budget.cost_consumed + cost <= budget.target_cost
            ):
                affordable.append((coord, sched))
        return affordable

    def _categorize_candidates(
        self, candidates: list[tuple[Coordinate, Schedule]]
    ) -> tuple[list[tuple[Coordinate, Schedule]], list[tuple[Coordinate, Schedule]]]:
        """Separate new cells from promotion candidates."""
        new_cells = []
        promotions = []
        for coord, sched in candidates:
            cell_key = coord.cell_key()
            if cell_key in self._state.promotion_candidates:
                # Check if this schedule matches the promotion
                promo = self._state.promotion_candidates[cell_key]
                if sched.fidelity == promo.current_fidelity:
                    promotions.append((coord, sched))
                else:
                    new_cells.append((coord, sched))
            else:
                new_cells.append((coord, sched))
        return new_cells, promotions

    def _select_promotions(
        self,
        promotions: list[tuple[Coordinate, Schedule]],
        budget: Budget,
        cost_model: CostModel,
    ) -> list[tuple[Coordinate, Schedule]]:
        """Select promotion candidates, prioritized by score."""
        # Sort by best score descending
        sorted_promos = sorted(
            promotions,
            key=lambda cs: (
                self._state.promotion_candidates[cs[0].cell_key()].best_score
            ),
            reverse=True,
        )

        selected = []
        for coord, sched in sorted_promos:
            cost = cost_model.estimate_cost(
                (
                    coord.substrate,
                    coord.geometry,
                    coord.dynamics,
                    coord.plasticity,
                    coord.credit,
                    coord.update,
                    coord.params,
                ),
                sched.to_dict(),
            )
            if (
                budget.target_cost is None
                or budget.cost_consumed + cost <= budget.target_cost
            ):
                selected.append((coord, sched))
                self._state.promoted_cells += 1
            if len(selected) >= 10:  # Limit concurrent promotions
                break
        return selected

    def _select_new_cells(
        self,
        new_cells: list[tuple[Coordinate, Schedule]],
        budget: Budget,
        cost_model: CostModel,
        already_selected: int,
    ) -> list[tuple[Coordinate, Schedule]]:
        """Select new cells for exploration."""
        # Simple round-robin for now; could be stratified random
        selected = []
        remaining_budget = (
            budget.target_cost - budget.cost_consumed
            if budget.target_cost
            else float("inf")
        )

        for coord, sched in new_cells:
            if already_selected + len(selected) >= 50:  # Batch limit
                break
            cost = cost_model.estimate_cost(
                (
                    coord.substrate,
                    coord.geometry,
                    coord.dynamics,
                    coord.plasticity,
                    coord.credit,
                    coord.update,
                    coord.params,
                ),
                sched.to_dict(),
            )
            if cost <= remaining_budget:
                selected.append((coord, sched))
                remaining_budget -= cost
        return selected

    def get_waste_report(self) -> dict[str, float | int]:
        """Generate waste report (R51)."""
        return {
            "wasted_evaluations": self._state.wasted_evaluations,
            "promoted_cells": self._state.promoted_cells,
            "pruned_cells": self._state.pruned_cells,
            "total_candidates": len(self._state.promotion_candidates),
            "active_fidelity_tracks": len(self._state.fidelity_history),
        }

    def get_telemetry(self) -> dict[str, object]:
        """Get divergence/stagnation telemetry."""
        return {
            "divergence_candidates": sum(
                1
                for c in self._state.promotion_candidates.values()
                if c.divergence_score > 0
            ),
            "stagnation_candidates": sum(
                1
                for c in self._state.promotion_candidates.values()
                if c.stagnation_score > 0
            ),
            "fidelity_distribution": self._get_fidelity_distribution(),
        }

    def _get_fidelity_distribution(self) -> dict[str, int]:
        """Get distribution of cells across fidelities."""
        dist: dict[str, int] = {}
        for history in self._state.fidelity_history.values():
            for fidelity, _, _ in history:
                dist[fidelity] = dist.get(fidelity, 0) + 1
        return dist


@dataclass(frozen=True, slots=True)
class Promotion:
    """A promotion decision for a cell to higher fidelity."""

    cell_key: str
    coordinate: Coordinate
    from_fidelity: str
    to_fidelity: str
    rationale: str
    score: float


@dataclass(frozen=True, slots=True)
class Abandonment:
    """An abandonment decision for a cell."""

    cell_key: str
    coordinate: Coordinate
    fidelity: str
    rationale: str
    reason: str  # "divergence" | "stagnation" | "budget" | "legality"


__all__ = [
    "Abandonment",
    "AllocationPolicy",
    "AllocationState",
    "EvidenceDrivenAllocator",
    "Promotion",
    "PromotionCandidate",
]
