"""Budget and cost model for experiment execution (WP4)."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from computronium.experiment.schema.record import Record


@runtime_checkable
class CostModel(Protocol):
    """Protocol for cost estimation models.

    Implementations estimate the computational cost of executing an
    experiment cell, enabling budget-aware allocation policies.
    """

    def estimate_cost(
        self,
        coordinate: tuple[str, str, str, str, str, str, dict],
        schedule: dict[str, int | str | float | None],
    ) -> float:
        """Estimate cost in abstract units (e.g., GPU-seconds).

        Args:
            coordinate: 6-axis coordinate (substrate, geometry, dynamics,
                plasticity, credit, update, params)
            schedule: Execution schedule (fidelity, seed, n_seeds, epochs,
                batch_limit, budget_id)

        Returns:
            Estimated cost in cost units.
        """
        ...

    def actual_cost(self, record: Record) -> float:
        """Compute actual cost from a completed record.

        Args:
            record: Completed experiment record.

        Returns:
            Actual cost incurred.
        """
        ...


@dataclass(frozen=True, slots=True)
class Budget:
    """Execution budget with time and cell limits.

    Frozen value object: ``advance``/``advance_by`` return fresh instances.
    ``target_cells`` is a hard cap on completed cells; ``soft_seconds`` stops
    *starting* new cells past the anchor; ``hard_seconds`` is the stricter
    between-cells ceiling for loop drivers.
    """

    started_at: float  # time.monotonic() anchor
    soft_seconds: float | None = None
    hard_seconds: float | None = None
    target_cells: int | None = None
    target_cost: float | None = None
    done: int = 0
    cost_consumed: float = 0.0

    @classmethod
    def from_duration(
        cls,
        duration: str,
        *,
        target_cells: int | None = None,
        target_cost: float | None = None,
        started_at: float | None = None,
    ) -> Budget:
        """Parse duration string into a Budget.

        Args:
            duration: Duration string like "5m", "90s", "1h", "3600"
            target_cells: Optional hard cap on completed cells
            target_cost: Optional hard cap on total cost
            started_at: Optional monotonic time anchor (default: now)

        Returns:
            Budget instance.
        """
        DURATION_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*([smh]?)\s*$", re.IGNORECASE)
        DURATION_SCALES: dict[str, float] = {"": 1.0, "s": 1.0, "m": 60.0, "h": 3600.0}

        match = DURATION_RE.match(duration)
        if match is None:
            raise ValueError(
                f"invalid budget {duration!r}: expected '<n><s|m|h>' (e.g. 5m, 90s, 1h)"
            )
        seconds = float(match.group(1)) * DURATION_SCALES[match.group(2).lower()]
        return cls(
            started_at=time.monotonic() if started_at is None else started_at,
            soft_seconds=seconds,
            hard_seconds=seconds,
            target_cells=target_cells,
            target_cost=target_cost,
        )

    def soft_expired(self, now: float | None = None) -> bool:
        """Check if soft time limit has expired."""
        now = time.monotonic() if now is None else now
        return (
            self.soft_seconds is not None and now - self.started_at >= self.soft_seconds
        )

    def hard_expired(self, now: float | None = None) -> bool:
        """Check if hard time limit has expired."""
        now = time.monotonic() if now is None else now
        return (
            self.hard_seconds is not None and now - self.started_at >= self.hard_seconds
        )

    def target_reached(self) -> bool:
        """Check if cell target has been reached."""
        return (self.target_cells is not None and self.done >= self.target_cells) or (
            self.target_cost is not None and self.cost_consumed >= self.target_cost
        )

    def expired(self, now: float | None = None) -> bool:
        """Check if budget is exhausted (hard limit or target reached)."""
        return self.hard_expired(now) or self.target_reached()

    def advance(self) -> Budget:
        """Return new Budget with done incremented by 1."""
        return self.advance_by(1)

    def advance_by(self, n: int) -> Budget:
        """Return new Budget with done incremented by n."""
        return replace(self, done=self.done + n)

    def add_cost(self, cost: float) -> Budget:
        """Return new Budget with cost_consumed increased."""
        return replace(self, cost_consumed=self.cost_consumed + cost)

    def elapsed_seconds(self, now: float | None = None) -> float:
        """Return elapsed time in seconds."""
        now = time.monotonic() if now is None else now
        return now - self.started_at

    def remaining_seconds(self, now: float | None = None) -> float | None:
        """Return remaining soft seconds, or None if unlimited."""
        if self.soft_seconds is None:
            return None
        remaining = self.soft_seconds - self.elapsed_seconds(now)
        return max(0.0, remaining)


@dataclass(frozen=True, slots=True)
class SimpleCostModel:
    """Simple cost model based on schedule parameters.

    Estimates cost proportional to epochs * n_seeds * batch_factor.
    """

    base_cost_per_epoch: float = 1.0
    seed_multiplier: float = 1.0
    fidelity_multipliers: dict[str, float] | None = None

    def __post_init__(self) -> None:
        if self.fidelity_multipliers is None:
            object.__setattr__(
                self,
                "fidelity_multipliers",
                {"L0": 0.1, "L1": 0.5, "L2": 1.0},
            )

    def estimate_cost(
        self,
        coordinate: tuple[str, str, str, str, str, str, dict],
        schedule: dict[str, int | str | float | None],
    ) -> float:
        """Estimate cost based on schedule parameters."""
        epochs = int(schedule.get("epochs", 1) or 1)
        n_seeds = int(schedule.get("n_seeds", 1) or 1)
        fidelity = str(schedule.get("fidelity", "L1") or "L1")

        base = self.base_cost_per_epoch * epochs
        seed_factor = n_seeds * self.seed_multiplier
        multipliers = self.fidelity_multipliers or {"L0": 0.1, "L1": 0.5, "L2": 1.0}
        fidelity_factor = multipliers.get(fidelity, 1.0)

        return base * seed_factor * fidelity_factor

    def actual_cost(self, record: Record) -> float:
        """Compute actual cost from record payload (walltime)."""
        # Try to get walltime from payload
        walltime = record.payload.get("walltime_s")
        if isinstance(walltime, (int, float)):
            return float(walltime)
        return self.estimate_cost(
            (
                record.substrate,
                record.geometry,
                record.dynamics,
                record.plasticity,
                record.credit,
                record.update,
                record.params,
            ),
            record.schedule.to_dict(),
        )


__all__ = [
    "Budget",
    "CostModel",
    "SimpleCostModel",
]
