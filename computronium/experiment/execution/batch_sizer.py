"""BatchSizer: turns measured cell time + remaining soft time into batch size k.

Determines how many cells to propose in each round based on the remaining
budget and observed cell execution times.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from computronium.experiment.execution.deadline import CellTiming, Deadline

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class BatchSizer:
    """Budget-aware batch sizer for experiment execution.

    Computes the number of cells to propose in each round based on:
    - Remaining soft deadline time
    - Median cell walltime observed so far (online learning)
    - Safety margin to avoid overshoot
    - Report reserve time

    Args:
        deadline: Hard deadline for the run.
        timing: CellTiming tracker with observed cell times.
        min_k: Minimum cells per batch (default 4).
        max_k: Maximum cells per batch (default 64).
        safety: Safety multiplier for time estimation (default 1.5).
        report_reserve_s: Seconds reserved for final report generation (default 60).
    """

    deadline: Deadline
    timing: CellTiming
    min_k: int = 4
    max_k: int = 64
    safety: float = 1.5
    report_reserve_s: float = 60.0

    def n_propose(self) -> int:
        """Calculate the number of cells to propose in the next batch.

        Returns:
            Clamped batch size between min_k and max_k.
        """
        remaining_soft = self.deadline.remaining_soft_seconds()
        if remaining_soft <= 0:
            return 0

        median = self.timing.median_cell_time()
        if median is None:
            # Cold start: no measurements yet, use max_k to explore quickly
            logger.debug("Cold start: no median cell time, using max_k=%d", self.max_k)
            return self.max_k

        # Calculate how many cells fit in remaining time with safety margin
        estimated_k = remaining_soft / (self.safety * median)
        k = int(max(self.min_k, min(self.max_k, estimated_k)))

        logger.debug(
            "BatchSizer: remaining_soft=%.1fs, median=%.1fs, safety=%.1f, "
            "estimated_k=%.1f -> k=%d (min=%d, max=%d)",
            remaining_soft,
            median,
            self.safety,
            estimated_k,
            k,
            self.min_k,
            self.max_k,
        )
        return k

    def can_start(self, k: int) -> bool:
        """Check if there's enough time to safely start a batch of k cells.

        Args:
            k: Number of cells to propose.

        Returns:
            True if the batch can start, False if deadline is too close.
        """
        remaining_soft = self.deadline.remaining_soft_seconds()
        if remaining_soft <= 0:
            return False

        median = self.timing.median_cell_time()
        if median is None:
            # Cold start: assume we can start if we have at least report_reserve + min_k * estimated
            # Use a conservative estimate based on max_k
            estimated_batch_time = self.safety * self.max_k * 10.0  # 10s fallback
        else:
            estimated_batch_time = self.safety * k * median

        required = self.report_reserve_s + estimated_batch_time
        can = remaining_soft > required

        logger.debug(
            "BatchSizer.can_start: remaining_soft=%.1fs, required=%.1fs "
            "(reserve=%.1f + batch=%.1f) -> %s",
            remaining_soft,
            required,
            self.report_reserve_s,
            estimated_batch_time,
            can,
        )
        return can

    @property
    def remaining_soft(self) -> float:
        """Seconds until soft deadline."""
        return self.deadline.remaining_soft_seconds()

    @property
    def budget_utilization(self) -> float:
        """Fraction of budget elapsed (elapsed / total_budget)."""
        elapsed = self.deadline.elapsed_seconds()
        total = self.deadline.remaining_soft_seconds() + elapsed
        if total <= 0:
            return 0.0
        return elapsed / total


__all__ = ["BatchSizer"]
