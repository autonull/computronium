"""Run lifecycle: construction, phase/round drives, control and reporting."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import sys
import time
from typing import TYPE_CHECKING, Any

from computronium.experiment.execution.control import ControlPlane, RunStatus
from computronium.experiment.execution.deadline import (
    CellTiming,
    DeadlineEnforcer,
    SignalHandler,
)
from computronium.experiment.execution.decision import RoundController
from computronium.experiment.execution.stage import StageId, get_stage_spec
from computronium.experiment.execution.stream import CellStream
from computronium.experiment.execution.sysctx import (
    SystemContext,
    capture_environment_snapshot,
    resolve_code_sha,
)

from ._base import _PipelineBase
from ._types import (
    PipelineConfig,
    PipelineState,
    _resolve_tasks,
)

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.schema.coordinate import Coordinate, Schedule
    from computronium.experiment.schema.record import Record

logger = logging.getLogger(__name__)

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None  # type: ignore[assignment]


class _LifecycleMixin(_PipelineBase):
    def __init__(
        self,
        config: PipelineConfig,
        store: RecordStore,
    ) -> None:
        self._config = config
        self._store = store

        # Resolved once: the code SHA and dataset the records will carry. A spec
        # that leaves them unset would persist values the store refuses, so the
        # engine infers them here instead of per stage (TODO65 turn-key path).
        self._dataset = (
            config.run_spec.dataset
            if config.run_spec.dataset not in {"", "unknown"}
            else _resolve_tasks(config)[0]
        )
        self._code_sha = resolve_code_sha(config.run_spec.code_sha)

        # Capture environment snapshot once per run (WP19)
        env_snapshot = capture_environment_snapshot(
            dtype=config.dtype,
            worker_config=config.worker_config,
            code_sha=config.code_sha,
        )

        # Create system context with environment snapshot (R75/K10)
        system_context = SystemContext(
            run_id=config.run_id,
            environment=env_snapshot,
        )

        self._state = PipelineState(
            run_id=config.run_id,
            deadline=config.deadline,
            deadline_enforcer=DeadlineEnforcer(config.deadline)
            if config.deadline
            else None,
            cell_timing=CellTiming(),
            signal_handler=SignalHandler(
                checkpoint_callback=self._checkpoint,
                shutdown_callback=self.shutdown,
            ),
            round_controller=RoundController(
                max_rounds=config.max_rounds,
                min_rounds=config.min_rounds,
            ),
            system_context=system_context,
        )
        # Create BatchSizer for budget-aware n_propose (only if deadline is set)
        if config.deadline is not None:
            from computronium.experiment.execution.batch_sizer import BatchSizer

            self._state.batch_sizer = BatchSizer(
                deadline=config.deadline,
                timing=self._state.cell_timing,
            )
        self._stages = config.stages or [
            StageId(n) for n in config.run_spec.stage_names
        ]
        self._shutdown = False
        self._control = (
            ControlPlane(config.control_plane) if config.control_plane else None
        )
        self._steps_taken = 0
        self._ceiling: int | None = None

        # Install signal handler for graceful shutdown
        if self._state.signal_handler:
            self._state.signal_handler.install()

        self._resume_completed_measurements()

    def _resume_completed_measurements(self) -> None:
        """Seed completed measurement keys from the store for this run_id.

        Without this a resumed run re-measures every cell it already holds: the
        batch dedup only saw one round, so the duplicate reached the store and
        came back as a PERSISTENCE_ERROR rejection instead of a skip.
        """
        if not self._store.is_open:
            return
        keys = {
            record.measurement_key
            for record in self._store.query_records(run_id=self._config.run_id)
        }
        if keys:
            self._state.completed_measurement_keys.update(keys)
            # The policy's stream is filtered by this same history
            # (`ProposalContext.cells`), so a relaunched run continues for every
            # policy rather than for the ones that kept a cursor.
            logger.info(
                "Resuming run %s: %d measurement(s) already stored",
                self._config.run_id,
                len(keys),
            )

    def _is_measured(self, key: str) -> bool:
        """Whether the store already holds this cell, or the gate rejected it.

        The stream is the only producer, so freshness lives here: a cell the
        store has measured, or the admission gate has refused, is never handed
        out again. Handing it out is a round spent re-measuring nothing.
        """
        return (
            key in self._state.completed_measurement_keys
            or key in self._state.rejected_keys
        )

    @property
    def allocator_promotions(self) -> list[tuple[Coordinate, Schedule]]:
        """The allocator's promotions from the last completed round (S10).

        Empty when no allocator is configured, the deadline is unset, or the
        allocations after measuring proposed nothing. This is the observable
        evidence that successive-halving allocation ran (TODO65 §3.W2).
        """
        return self._state.allocator_promotions

    @property
    def replay_hash(self) -> str | None:
        """The run-level replay hash, once the run has finished measuring."""
        return self._state.replay_hash

    def _record_replay_hash(self) -> None:
        """Write the run's replay hash when it finishes, not on demand.

        A hash computed on demand describes whatever the store happens to hold
        later; only the one written at completion describes the run.
        """
        from computronium.experiment.execution.replay import compute_run_replay_hash

        digest = compute_run_replay_hash(
            self._config.run_spec, self._state.completed_measurement_keys
        )
        self._state.replay_hash = digest
        if self._store.is_open:
            self._store.set_replay_hash(self._config.run_id, digest)
        logger.info("Run %s replay hash: %s", self._config.run_id, digest[:16])

    @property
    def rejections(self) -> tuple[dict[str, Any], ...]:
        """Every rejected cell this run classified, in order."""
        return tuple(self._state.rejections)

    def _publish_status(self) -> None:
        """Tell the dashboard what the run is doing now."""
        plane = self._control
        if plane is None:
            return
        backend = self._config.backend
        ceiling = self._ceiling
        if ceiling is None and backend is not None:
            ceiling = backend.max_workers
        plane.write_status(
            RunStatus(
                run_id=self._config.run_id,
                stage=self._state.current_stage,
                in_flight=backend.in_flight if backend is not None else 0,
                cells_done=len(self._state.completed_measurement_keys),
                ceiling=ceiling or 0,
                at=time.time(),
            )
        )

    def _create_round_progress_bar(self, round_controller: RoundController):
        """Create progress bar for rounds."""
        if tqdm is None:
            return None
        return tqdm(
            total=round_controller.max_rounds or 0,
            desc="Rounds",
            unit="round",
            disable=tqdm is None or not sys.stdout.isatty(),
        )

    async def run(self) -> list[Record]:
        """Run the full pipeline to completion with round loop.

        Returns:
            All records produced during the run.
        """
        logger.info(
            "Starting pipeline run %s with stages: %s",
            self._config.run_id,
            self._stages,
        )

        # Start heartbeat task
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        # Load already-measured keys for resume support
        self._resume_completed_measurements()

        # Build SearchSpace from RunSpec
        self._state.search_space = self._build_search_space()

        # Create CellStream for unbounded candidate generation
        if self._config.deadline is not None and self._state.search_space is not None:
            from computronium.experiment.kernel.evaluate import task_shape

            self._state.cell_stream = CellStream(
                spec=self._config.run_spec,
                space=self._state.search_space,
                shape=task_shape,
                deadline=self._config.deadline,
                is_measured=self._is_measured,
            )
            # Set exploit policy if available
            if self._config.policy:
                self._state.cell_stream.set_exploit_policy(self._config.policy)
            # Restore cell stream state from checkpoint if available
            if self._state.cell_stream_state is not None:
                self._state.cell_stream.set_state(self._state.cell_stream_state)

        all_records: list[Record] = []

        # The run holds here if the dashboard asked it to pause before the
        # first cell: a run that starts paused never starts.
        await self._await_control(consumes_step=False)

        # S1-S2: Run once at start
        await self._run_initial_phases(all_records)

        # S3-S10: Round loop
        await self._run_round_loop(all_records)

        # S11 Report
        if StageId.S11_REPORT in self._stages:
            fragment = await self._dispatch_stage(
                StageId.S11_REPORT, get_stage_spec(StageId.S11_REPORT)
            )
            self._merge_coverage(fragment.coverage)

        self._record_replay_hash()

        # Stop heartbeat
        self._heartbeat_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._heartbeat_task

        logger.info(
            "Pipeline run %s completed: %d records, %d rounds",
            self._config.run_id,
            len(all_records),
            self._state.current_round,
        )
        return all_records

    async def _heartbeat_loop(self) -> None:
        """Update run heartbeat every 30 seconds."""
        while not self._shutdown:
            await asyncio.sleep(30)
            if self._shutdown:
                break
            try:
                if self._store.is_open:
                    self._store.update_heartbeat(self._config.run_id)
                    logger.debug("Heartbeat updated for run %s", self._config.run_id)
            except Exception as e:
                logger.warning("Failed to update heartbeat: %s", e)

    async def _run_initial_phases(self, all_records: list[Record]) -> None:
        """Run S1-S2 phases once at start."""
        for stage_id in [StageId.S1_FRAME, StageId.S2_SPACE]:
            if self._shutdown:
                break
            if stage_id not in self._stages:
                continue

            stage_spec = get_stage_spec(stage_id)
            fragment = await self._dispatch_stage(stage_id, stage_spec)

            # Collect records and proposals
            all_records.extend(fragment.records)
            self._state.pending_proposals.extend(fragment.proposals)

            # Update coverage
            self._merge_coverage(fragment.coverage)

            # Check gate
            if not self._check_gate(fragment, stage_spec):
                logger.warning("Gate failed for stage %s, stopping pipeline", stage_id)
                self._shutdown = True
                break

    async def _run_round_loop(self, all_records: list[Record]) -> None:
        """Run S3-S10 round loop — stops ONLY on deadline or shutdown.

        The only legal terminations are:
        (a) deadline (soft or hard)
        (b) SIGINT/SIGTERM (shutdown_requested)

        Any other termination — empty stream, "fruitless" rounds, all-seen batch,
        single-round cap, 80% sub-budget — is a DEFECT.
        """
        round_controller = self._state.round_controller
        if round_controller is None:
            round_controller = RoundController(
                max_rounds=self._config.max_rounds,
                min_rounds=self._config.min_rounds,
            )
            self._state.round_controller = round_controller

        pbar_rounds = self._create_round_progress_bar(round_controller)
        deadline_enforcer = self._state.deadline_enforcer
        signal_handler = self._state.signal_handler

        while round_controller.should_continue(self._get_decision_from_fragments()):
            if self._should_stop_round_loop(deadline_enforcer, signal_handler):
                break

            await self._await_control(consumes_step=False)

            before = len(all_records)
            await self._execute_round(all_records)

            self._check_post_round_deadline(deadline_enforcer)

            if self._stream_is_spent(before, len(all_records)):
                logger.info(
                    "Cell stream exhausted and round %d produced nothing; stopping",
                    self._state.current_round,
                )
                self._shutdown = True

            if pbar_rounds:
                pbar_rounds.update(1)

            # Track zero-yield batches for ZeroYieldError
            if len(all_records) > before:
                # Successful batch - reset zero-yield counter
                self._state.zero_yield_count = 0
                self._state.last_zero_yield_cause = None
            else:
                # Zero-yield batch - check for uniform failure cause
                self._check_zero_yield()

            # Periodic checkpointing (gated by checkpoint_every_n in RunSpec)
            checkpoint_every_n = self._config.run_spec.checkpoint_every_n
            if (
                checkpoint_every_n > 0
                and self._state.current_round % checkpoint_every_n == 0
            ):
                self._checkpoint()

        if pbar_rounds:
            pbar_rounds.close()

    async def _await_control(self, *, consumes_step: bool) -> None:
        """Hold at a boundary until the plane releases the run.

        A pause is a boundary, not a kill: the cell in flight finishes and is
        recorded, and the run waits here for the next release. A step releases
        exactly one batch, so a boundary that is not a batch boundary lets the
        run proceed to the batch that will consume it.

        Args:
            consumes_step: Whether this boundary is the one that spends a
                step.
        """
        plane = self._control
        if plane is None:
            return
        while not self._shutdown:
            state = await plane.wait_for_release(steps_taken=self._steps_taken)
            if state.cancel:
                logger.info("The control plane asked the run to stop")
                self._shutdown = True
                return
            await self._apply_ceiling(state.max_workers)
            if not state.paused:
                return
            if consumes_step:
                self._steps_taken += 1
                logger.info("Stepping: releasing one batch")
            return

    def shutdown(self) -> None:
        """Shutdown the pipeline runner."""
        self._shutdown = True
        if self._config.backend:
            self._config.backend.shutdown()

    @property
    def shutdown_requested(self) -> bool:
        """Whether a signal asked the run to stop.

        A run stops for several reasons — a signal, a spent budget, a spent
        space, a gate refusing a cell — and only the first one means the run
        was interrupted and can be resumed. The others are the run finishing
        what it set out to do, and the caller is told which it was.
        """
        handler = self._state.signal_handler
        return handler.shutdown_requested if handler is not None else False

    def get_coverage_report(self) -> dict[str, Any]:
        """Get coverage report (R18)."""
        return self._state.coverage

    def get_rejection_report(self) -> list[dict[str, Any]]:
        """Get rejection classification report (R19)."""
        return self._state.rejections

    def get_proposal_provenance(self) -> list[dict[str, Any]]:
        """Get proposal provenance (R20)."""
        return self._state.proposal_provenance
