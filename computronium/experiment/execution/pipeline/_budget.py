"""Deadline, cell cap and zero-yield enforcement."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ._base import _PipelineBase
from ._types import ZeroYieldError

if TYPE_CHECKING:
    from computronium.experiment.execution.deadline import (
        DeadlineEnforcer,
        SignalHandler,
    )
    from computronium.experiment.schema.record import Record

logger = logging.getLogger(__name__)


class _BudgetMixin(_PipelineBase):
    def _should_stop_round_loop(
        self,
        deadline_enforcer: DeadlineEnforcer | None,
        signal_handler: SignalHandler | None,
    ) -> bool:
        """Check if round loop should stop. Returns True if should stop.

        ONLY stops on: shutdown signal, hard deadline expired, soft deadline reached.
        """
        if signal_handler and signal_handler.shutdown_requested:
            logger.info("Shutdown requested, stopping round loop")
            self._shutdown = True
            return True

        if deadline_enforcer and deadline_enforcer.deadline.expired():
            logger.info("Hard deadline expired, stopping round loop")
            self._shutdown = True
            return True

        if deadline_enforcer and not deadline_enforcer.check_before_cell():
            logger.info("Soft deadline reached, stopping before new round")
            self._shutdown = True
            return True

        return bool(self._shutdown)

    def _stream_is_spent(self, records_before_round: int, records_now: int) -> bool:
        """Whether a finite space is fully measured and the loop should stop.

        A stream with nothing left to hand out is a finite space, not a
        timeout: every cell a round could schedule is one the store already
        holds. Stopping keeps the loop bounded. The production space is
        astronomically larger than any budget and never reaches this state, so
        this fires only for the small spaces the mechanism locks declare.
        """
        stream = self._state.cell_stream
        return (
            stream is not None
            and stream.is_exhausted
            and not self._state.pending_proposals
            and records_now == records_before_round
        )

    def _check_post_round_deadline(
        self, deadline_enforcer: DeadlineEnforcer | None
    ) -> None:
        """Check deadline after round completes."""
        if deadline_enforcer and not deadline_enforcer.check_after_cell():
            logger.info("Soft deadline reached after round, stopping")
            self._shutdown = True

    def _check_zero_yield(self) -> None:
        """Check for consecutive zero-yield batches with uniform failure cause.

        If K>=3 consecutive batches produce zero successes with a single shared
        failure cause, raise ZeroYieldError — a reviewable failure, not a silent stop.
        """
        # Analyze the last round's rejections to find the dominant failure cause
        if not self._state.rejections:
            return

        # Get rejections from the last round (approximate by looking at recent)
        recent_rejections = self._state.rejections[-10:]  # Last 10 rejections
        if not recent_rejections:
            return

        # Count causes
        cause_counts: dict[str, int] = {}
        for r in recent_rejections:
            cause = r.get("cause", "UNKNOWN")
            cause_counts[cause] = cause_counts.get(cause, 0) + 1

        # Find dominant cause
        if cause_counts:
            dominant_cause, count = max(cause_counts.items(), key=lambda x: x[1])
            if count >= 3:  # At least 3 failures with same cause in recent rejections
                if self._state.last_zero_yield_cause == dominant_cause:
                    self._state.zero_yield_count += 1
                else:
                    self._state.zero_yield_count = 1
                    self._state.last_zero_yield_cause = dominant_cause

                if self._state.zero_yield_count >= 3:
                    raise ZeroYieldError(
                        cause=dominant_cause,
                        count=self._state.zero_yield_count,
                        message=f"Uniform failure cause '{dominant_cause}' across {self._state.zero_yield_count} batches",
                    )

    async def _apply_ceiling(self, max_workers: int | None) -> None:
        """Move the backend's ceiling when the plane asks for another.

        The ceiling is a cap, not a target: lowering it leaves the cells in
        flight alone and stops the next admission.
        """
        if max_workers is None or max_workers == self._ceiling:
            return
        backend = self._config.backend
        if backend is None:
            return
        await backend.set_max_workers(max_workers)
        self._ceiling = max_workers
        logger.info("The control plane set the ceiling to %d cell(s)", max_workers)

    def _charge_budget(self, records: list[Record]) -> None:
        """Update cell timing with actual walltime from completed records.

        In the deadline system, we track measured walltime per cell for
        online learning, not predicted cost.
        """
        if not records:
            return
        cell_timing = self._state.cell_timing
        if cell_timing is None:
            return
        # Try to get walltime from record payload
        for record in records:
            walltime = record.payload.get("walltime_s")
            if isinstance(walltime, (int, float)):
                cell_timing.cell_times.append(float(walltime))
                cell_timing.total_walltime_s += float(walltime)
                cell_timing.cell_count += 1
