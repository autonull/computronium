"""Checkpoint capture, restore and resume for the pipeline runner."""

from __future__ import annotations

import contextlib
import logging
from typing import TYPE_CHECKING, Any

from computronium.experiment.execution.deadline import (
    CellTiming,
    _create_checkpoint_data,
    _PipelineStateSnapshot,
)
from computronium.experiment.execution.stage import Proposal

from ._base import _PipelineBase

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.schema.coordinate import Coordinate, Schedule

    from ._runner import PipelineRunner
    from ._types import PipelineConfig

logger = logging.getLogger(__name__)


class _CheckpointMixin(_PipelineBase):
    @classmethod
    def from_checkpoint(
        cls,
        run_id: str,
        config: PipelineConfig,
        store: RecordStore,
    ) -> PipelineRunner:
        """Create PipelineRunner and resume from checkpoint.

        Args:
            run_id: The run identifier to resume
            config: Pipeline configuration (deadline, policy, backend, etc.)
            store: RecordStore with existing run data

        Returns:
            PipelineRunner with state restored from checkpoint
        """

        from ._runner import PipelineRunner

        runner = PipelineRunner(config, store)

        # Load checkpoint from store
        if store.is_open:
            checkpoint_data = store.load_checkpoint(run_id)
            if checkpoint_data:
                runner._restore_from_checkpoint(checkpoint_data)
                logger.info(
                    "Resumed run %s from checkpoint (round %d)",
                    run_id,
                    runner._state.current_round,
                )

        return runner

    def _restore_from_checkpoint(self, checkpoint_data: dict[str, Any]) -> None:
        """Restore pipeline state from checkpoint data."""
        from computronium.experiment.execution.deadline import CellTiming

        # Restore completed keys
        self._state.completed_measurement_keys = set(
            checkpoint_data.get("completed_measurement_keys", [])
        )

        # Restore pending proposals (deserialize)
        pending_data = checkpoint_data.get("pending_proposals", [])
        self._state.pending_proposals = [
            self._deserialize_proposal(p) for p in pending_data
        ]

        # Restore in-progress
        in_progress_data = checkpoint_data.get("in_progress", [])
        self._state.in_progress = [
            self._deserialize_in_progress(ip) for ip in in_progress_data
        ]

        # Restore round state
        self._state.current_round = checkpoint_data.get("current_round", 0)
        if self._state.round_controller:
            rc_state = checkpoint_data.get("round_controller_state", {})
            # Access private attribute since property has no setter
            self._state.round_controller._current_round = rc_state.get(
                "current_round", 0
            )

        # Restore policy state
        if self._config.policy:
            policy_state = checkpoint_data.get("policy_state", {})
            get_state = getattr(self._config.policy, "set_state", None)
            if callable(get_state):
                get_state(policy_state)

        # Restore allocator state
        if self._config.allocator:
            allocator_state = checkpoint_data.get("allocator_state")
            if allocator_state:
                get_state = getattr(self._config.allocator, "set_state", None)
                if callable(get_state):
                    get_state(allocator_state)

        # Restore cell timing
        ct_data = checkpoint_data.get("cell_timing", {})
        self._state.cell_timing = CellTiming(
            cell_count=ct_data.get("cell_count", 0),
            total_walltime_s=ct_data.get("total_walltime_s", 0.0),
            cell_times=ct_data.get("cell_times", []),
        )

        # Restore CellStream state
        cell_stream_state_data = checkpoint_data.get("cell_stream_state")
        if cell_stream_state_data is not None:
            from computronium.experiment.execution.stream import CellStreamState

            self._state.cell_stream_state = CellStreamState.from_dict(
                cell_stream_state_data
            )

        logger.info(
            "Restored checkpoint: %d completed, %d pending, round %d",
            len(self._state.completed_measurement_keys),
            len(self._state.pending_proposals),
            self._state.current_round,
        )

    def _deserialize_proposal(self, data: dict[str, Any]) -> Proposal:
        """Deserialize a Proposal from checkpoint data."""
        from computronium.experiment.schema.coordinate import Coordinate, Schedule

        coord_data = data.get("coordinate", {})
        coord = Coordinate(
            substrate=coord_data.get("substrate", ""),
            geometry=coord_data.get("geometry", ""),
            dynamics=coord_data.get("dynamics", ""),
            plasticity=coord_data.get("plasticity", ""),
            credit=coord_data.get("credit", ""),
            update=coord_data.get("update", ""),
            params=coord_data.get("params", {}),
        )
        sched_data = data.get("schedule", {})
        sched = (
            Schedule.from_dict(sched_data)
            if sched_data
            else Schedule(
                fidelity="L1",
                seed=0,
                n_seeds=1,
                epochs=1,
                batch_limit=0,
                budget_id="initial",
            )
        )
        return Proposal(
            coordinate=coord,
            schedule=sched,
            rationale=data.get("rationale", ""),
            metadata=data.get("metadata", {}),
        )

    def _deserialize_in_progress(
        self, data: dict[str, Any]
    ) -> tuple[Coordinate, Schedule]:
        """Deserialize an in-progress cell from checkpoint data."""
        from computronium.experiment.schema.coordinate import Coordinate, Schedule

        coord_data = data.get("coordinate", {})
        coord = Coordinate(
            substrate=coord_data.get("substrate", ""),
            geometry=coord_data.get("geometry", ""),
            dynamics=coord_data.get("dynamics", ""),
            plasticity=coord_data.get("plasticity", ""),
            credit=coord_data.get("credit", ""),
            update=coord_data.get("update", ""),
            params=coord_data.get("params", {}),
        )
        sched_data = data.get("schedule", {})
        sched = (
            Schedule.from_dict(sched_data)
            if sched_data
            else Schedule(
                fidelity="L1",
                seed=0,
                n_seeds=1,
                epochs=1,
                batch_limit=0,
                budget_id="initial",
            )
        )
        return (coord, sched)

    def _collect_checkpoint_state(self) -> _PipelineStateSnapshot | None:
        """Collect all state needed for checkpoint. Returns None if store not open."""
        if not self._store.is_open:
            return None

        policy_state = self._get_policy_state()
        allocator_state = self._get_allocator_state()
        system_context_snapshot = self._get_system_context_snapshot()
        round_controller_state = self._get_round_controller_state()
        cell_timing = self._get_or_create_cell_timing()

        # Save CellStream state for resume
        cell_stream_state = None
        if self._state.cell_stream is not None:
            cell_stream_state = self._state.cell_stream.get_state().to_dict()

        return _PipelineStateSnapshot(
            run_id=self._config.run_id,
            completed_keys=frozenset(self._state.completed_measurement_keys),
            pending_proposals=self._state.pending_proposals,
            in_progress=self._state.in_progress,
            current_round=self._state.current_round,
            round_controller_state=round_controller_state,
            policy_state=policy_state,
            allocator_state=allocator_state,
            system_context_snapshot=system_context_snapshot,
            cell_timing=cell_timing,
            cell_stream_state=cell_stream_state,
        )

    def _get_policy_state(self) -> dict[str, Any]:
        """Extract state from policy if supported."""
        policy_state: dict[str, Any] = {}
        if self._config.policy:
            with contextlib.suppress(Exception):
                get_state = getattr(self._config.policy, "get_state", None)
                if callable(get_state):
                    state = get_state()
                    if isinstance(state, dict):
                        policy_state = state
        return policy_state

    def _get_allocator_state(self) -> dict[str, Any] | None:
        """Extract state from allocator if supported."""
        allocator_state: dict[str, Any] | None = None
        if self._config.allocator:
            with contextlib.suppress(Exception):
                get_state = getattr(self._config.allocator, "get_state", None)
                if callable(get_state):
                    state = get_state()
                    if isinstance(state, dict):
                        allocator_state = state
        return allocator_state

    def _get_system_context_snapshot(self) -> dict[str, Any] | None:
        """Extract environment snapshot from system context."""
        system_context_snapshot = None
        if self._state.system_context:
            with contextlib.suppress(Exception):
                system_context_snapshot = (
                    self._state.system_context.environment.to_provenance_dict()
                )
        return system_context_snapshot

    def _get_round_controller_state(self) -> dict[str, Any]:
        """Extract state from round controller."""
        round_controller_state = {}
        if self._state.round_controller:
            round_controller_state = {
                "current_round": self._state.round_controller.current_round,
                "max_rounds": self._state.round_controller.max_rounds,
                "min_rounds": self._state.round_controller.min_rounds,
            }
            if self._state.round_controller.decision:
                round_controller_state["decision"] = {
                    "transition": self._state.round_controller.decision.transition.value,
                    "rationale": self._state.round_controller.decision.rationale,
                }
        return round_controller_state

    def _get_or_create_cell_timing(self) -> CellTiming:
        """Get cell timing or create new if None."""
        cell_timing = self._state.cell_timing
        if cell_timing is None:
            from computronium.experiment.execution.deadline import CellTiming

            cell_timing = CellTiming()
        return cell_timing

    def _checkpoint(self) -> None:
        """Save checkpoint to store for SIGTERM-aware resume.

        Captures current pipeline state including completed measurements,
        pending proposals, round state, policy state, and cell timing.
        """
        try:
            snapshot = self._collect_checkpoint_state()
            if snapshot is None:
                return
            checkpoint_data = _create_checkpoint_data(snapshot)

            # Save to store (convert CheckpointData to dict)
            if self._store.is_open:
                self._store.save_checkpoint(
                    self._config.run_id, checkpoint_data.to_dict()
                )
                logger.info(
                    "Checkpoint saved for run %s (round %d, %d completed)",
                    self._config.run_id,
                    self._state.current_round,
                    len(self._state.completed_measurement_keys),
                )

        except Exception:
            logger.exception("Failed to save checkpoint")
