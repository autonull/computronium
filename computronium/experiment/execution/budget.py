"""Legacy budget and cost model classes for backward compatibility.

This module provides the Budget, CostModel, and SimpleCostModel classes
that were previously in the execution package. They are kept for
backward compatibility with tests and legacy code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Budget:
    """Legacy budget configuration (replaced by Deadline system)."""

    soft_seconds: float | None = None
    hard_seconds: float | None = None
    max_cells: int | None = None

    @classmethod
    def from_duration(cls, duration: str) -> Budget:
        """Create budget from duration string like '60s' or '5m'."""
        duration = duration.strip().lower()
        if duration.endswith("s"):
            seconds = float(duration[:-1])
        elif duration.endswith("m"):
            seconds = float(duration[:-1]) * 60
        elif duration.endswith("h"):
            seconds = float(duration[:-1]) * 3600
        else:
            seconds = float(duration)
        return cls(soft_seconds=seconds, hard_seconds=seconds)


class CostModel:
    """Abstract base class for cost models."""

    def estimate(self, cell: Any) -> float:
        """Estimate cost of running a cell."""
        raise NotImplementedError


class SimpleCostModel(CostModel):
    """Simple cost model with fixed per-cell cost."""

    def __init__(self, cost_per_cell: float = 1.0) -> None:
        self.cost_per_cell = cost_per_cell

    def estimate(self, cell: Any) -> float:
        return self.cost_per_cell


__all__ = ["Budget", "CostModel", "SimpleCostModel"]
