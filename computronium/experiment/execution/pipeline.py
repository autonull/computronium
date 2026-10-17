"""S1-S11 pipeline runner with wrapper obligations (WP9/15/16 + WP19).

Wrapper obligations (R18/R19/R20/R29/R12):
- Coverage reporting (R18)
- Identical rejection classification for every policy (R19)
- Proposal provenance stamping (R20)
- Failure isolation (R29) - per-item Success/Failure via EvaluationResult
- Single-writer atomic appends (R12)
- Budget accounting (R21)
- EvidenceDrivenAllocator integration between rounds
- Replay hash computation and re-check (R26/R27)
- Resume via measurement_key dedup
- RegistryCostModel learns estimate-vs-actual (R23/R24)

Architecture:
- Stage dispatch via Stage.run(ctx) -> Fragment protocol (WP15)
- Round loop with S3-S10 repeating via Decision (WP16)
- SearchSpace/ProposalContext/Proposal canonical types (WP14)
- EnvironmentSnapshot captured once per run (WP19)
- SystemContext for run-scoped kernel cache and learning state (R75/K10)
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import sys
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Final

from computronium.experiment.execution.backends import Failure, Success
from computronium.experiment.execution.deadline import (
    CellTiming,
    Deadline,
    DeadlineEnforcer,
    SignalHandler,
    _create_checkpoint_data,
    _PipelineStateSnapshot,
)
from computronium.experiment.execution.decision import Decision, RoundController
from computronium.experiment.execution.stage import Proposal, StageId, get_stage_spec
from computronium.experiment.execution.stream import CellStream, CellStreamState
from computronium.experiment.execution.sysctx import (
    SystemContext,
    capture_environment_snapshot,
    resolve_code_sha,
)
from computronium.experiment.schema.coordinate import (
    Coordinate,
    DataOrigin,
    Provenance,
    Schedule,
)

if TYPE_CHECKING:
    from tqdm.std import tqdm

    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.execution.allocator import EvidenceDrivenAllocator
    from computronium.experiment.execution.backends import (
        EvaluationResult,
        ExecutionBackend,
    )
    from computronium.experiment.execution.policy import Policy
    from computronium.experiment.execution.stage import (
        Fragment,
        StageContext,
    )
    from computronium.experiment.kernel.resources import CostModel
    from computronium.experiment.kernel.search_space import SearchSpace
    from computronium.experiment.schema.record import Record
    from computronium.experiment.schema.run_spec import RunSpec

logger = logging.getLogger(__name__)

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None  # type: ignore[assignment]

# The stages one round walks, in order. The order is the pipeline's meaning —
# schedule, gate, compose, train, measure, record, attribute, decide — and a
# stage the run does not declare is skipped rather than reordered.
_ROUND_STAGE_ORDER: Final = (
    StageId.S3_SCHEDULE,
    StageId.S4_GATE,
    StageId.S5_COMPOSE,
    StageId.S6_TRAIN,
    StageId.S7_MEASURE,
    StageId.S8_RECORD,
    StageId.S9_ATTRIBUTE,
    StageId.S10_DECIDE,
)


class ZeroYieldError(RuntimeError):
    """Raised when K>=3 consecutive batches produce zero successes with a
    single shared failure cause. This is a reviewable failure, not a silent stop.
    """

    def __init__(self, cause: str, count: int, message: str):
        super().__init__(
            f"ZeroYieldError: {count} consecutive batches failed with cause '{cause}': {message}"
        )
        self.cause = cause
        self.count = count


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    """Configuration for the pipeline runner."""

    run_id: str
    run_spec: RunSpec
    stages: list[StageId] = field(default_factory=list)
    deadline: Deadline | None = None  # Hard deadline (replaces budget)
    budget: Any = (
        None  # Backward compatibility: accepts legacy Budget, converts to deadline
    )
    # Cells this launch may measure before stopping. Read from the legacy
    # Budget's ``target_cells``; a per-launch cap, so a resume continues.
    session_cell_limit: int | None = None
    cost_model: CostModel | None = None
    policy: Policy | None = None
    allocator: EvidenceDrivenAllocator | None = None
    backend: ExecutionBackend | None = None
    max_concurrent_evaluations: int = 10
    seed: int | None = None
    # Task IDs for multi-task runs (L17)
    task_ids: list[str] = field(default_factory=list)
    # Round controller config
    max_rounds: int | None = None
    min_rounds: int = 1
    # Runtime provenance (WP19)
    dtype: str = "float32"
    worker_config: dict[str, Any] = field(default_factory=dict)
    code_sha: str = "unknown"

    def __post_init__(self) -> None:
        # Convert legacy Budget to Deadline if provided, and carry its
        # per-launch cell cap. ``dataclasses.replace`` re-runs this even when a
        # deadline is already present, so the cap cannot depend on conversion.
        if self.budget is not None:
            from computronium.experiment.execution.deadline import Deadline
            from computronium.experiment.kernel.resources import Budget as LegacyBudget

            if isinstance(self.budget, LegacyBudget):
                object.__setattr__(self, "session_cell_limit", self.budget.target_cells)
                if self.deadline is None:
                    object.__setattr__(
                        self,
                        "deadline",
                        Deadline.from_seconds(self.budget.soft_seconds or 3600),
                    )


def _resolve_tasks(config: PipelineConfig) -> tuple[str, ...]:
    """The run's task names: the spec's, unless the config overrides them.

    ``RunSpec`` already refused an unresolvable task, so an empty result means
    the run measured nothing and the override must be checked here.
    """
    names = tuple(config.task_ids) or config.run_spec.task_names
    if not names:
        msg = f"run {config.run_id} names no task"
        raise ValueError(msg)
    from computronium.domains.registry import SUPPORTED_TASKS

    unknown = [n for n in names if n not in SUPPORTED_TASKS]
    if unknown:
        msg = f"unknown task(s) {unknown}; available: {sorted(SUPPORTED_TASKS)}"
        raise ValueError(msg)
    return names


_CONTRAST_LINK_KEYS: Final = ("contrast_id", "matched_group", "factor_assignments")


def _provenance_for(provenance: Provenance, proposal: Proposal) -> Provenance:
    """The run's provenance as this proposal's own record will carry it.

    ``data_origin`` is the schema's own field for the S1 allocation and the
    contrast design's group; the design's identifiers ride in ``links`` beside
    ``run_id``. Identity is untouched — the schedule is unchanged, so the same
    cell under two origins is still the same measurement key.
    """
    from dataclasses import replace

    metadata = proposal.metadata
    links = dict(provenance.links)
    for key in _CONTRAST_LINK_KEYS:
        if key in metadata:
            links[key] = str(metadata[key])
    if not links.keys() - {"run_id"} and provenance.data_origin == metadata.get(
        "data_origin", provenance.data_origin
    ):
        return provenance
    return replace(
        provenance,
        data_origin=DataOrigin(metadata.get("data_origin", provenance.data_origin)),
        links=links,
    )


@dataclass(slots=True)
class PipelineState:
    """Mutable state for pipeline execution."""

    run_id: str
    current_stage_idx: int = 0
    current_round: int = 0
    completed_measurement_keys: set[str] = field(default_factory=set)
    pending_proposals: list[Proposal] = field(default_factory=list)
    in_progress: list[tuple[Coordinate, Schedule]] = field(default_factory=list)
    deadline: Deadline | None = None
    deadline_enforcer: DeadlineEnforcer | None = None
    cell_timing: CellTiming = field(default_factory=CellTiming)
    signal_handler: SignalHandler | None = None
    allocator_state: dict[str, Any] | None = None
    allocator_promotions: list[tuple[Coordinate, Schedule]] = field(
        default_factory=list
    )
    last_decision: Decision | None = None
    # Coverage tracking (R18)
    coverage: dict[str, Any] = field(default_factory=dict)
    # Rejection classification (R19)
    rejections: list[dict[str, Any]] = field(default_factory=list)
    # Proposal provenance (R20)
    proposal_provenance: list[dict[str, Any]] = field(default_factory=list)
    # Replay hash tracking (R26/R27)
    replay_hash: str | None = None
    # Round controller
    round_controller: RoundController | None = None
    # Search space
    search_space: SearchSpace | None = None
    # Admission gate: durable set of rejected keys (never re-proposed)
    rejected_keys: set[str] = field(default_factory=set)
    # Batch sizer for budget-aware n_propose
    batch_sizer: Any = None  # BatchSizer, imported locally to avoid cycle
    # Cell stream for unbounded candidate generation
    cell_stream: CellStream | None = None
    cell_stream_state: CellStreamState | None = None
    # Consecutive zero-yield batches for ZeroYieldError
    zero_yield_count: int = 0
    last_zero_yield_cause: str | None = None
    # System context with environment snapshot (WP19/R75/K10)
    system_context: SystemContext | None = None
    # Last measured duration per stage, stamped into every record payload
    stage_timings: dict[str, float] = field(default_factory=dict)


class PipelineRunner:
    """S1-S11 pipeline runner with atomic append + reconciliation + wrapper obligations.

    Coordinates the full experiment lifecycle:
    - Stage progression (S1-S11) via Stage.run(ctx) -> Fragment dispatch
    - Round loop (S3-S10 repeat) with Decision-based termination
    - Budget management
    - Policy-driven candidate selection via SearchSpace
    - Backend execution with failure isolation (WP19)
    - Record persistence with reconciliation
    - Checkpointing and resume
    - Wrapper obligations: coverage, classification, traceability, failure isolation
    - EvidenceDrivenAllocator integration
    - Replay hash verification
    """

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
        runner = cls(config, store)

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

    def _get_all_stage_specs(self):
        from computronium.experiment.execution.stage import STAGE_SPECS

        return STAGE_SPECS

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
            from computronium.experiment.execution.decision import RoundController

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

            before = len(all_records)
            try:
                await self._execute_round(all_records)
            except ZeroYieldError:
                # Re-raise to stop the run with a diagnostic
                raise

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

    async def _execute_round(self, all_records: list[Record]) -> None:
        """Execute a single round of S3-S10 stages."""
        self._state.current_round += 1
        logger.info("Starting round %d", self._state.current_round)

        for stage_id in _ROUND_STAGE_ORDER:
            if stage_id not in self._stages:
                continue
            fragment = await self._dispatch_stage(stage_id, get_stage_spec(stage_id))
            self._merge_coverage(fragment.coverage)
            await self._apply_round_stage(stage_id, fragment, all_records)

    async def _apply_round_stage(
        self, stage_id: StageId, fragment: Fragment, all_records: list[Record]
    ) -> None:
        """Fold one round stage's fragment into the run: proposals, records, side work.

        Every round stage dispatches and merges coverage identically; what differs
        is what the stage's fragment *means* downstream, so that is the only
        thing this names.
        """
        match stage_id:
            case StageId.S3_SCHEDULE:
                self._state.pending_proposals = fragment.proposals
            case StageId.S10_DECIDE:
                self._state.pending_proposals = fragment.proposals
                if fragment.decisions:
                    self._state.last_decision = fragment.decisions[-1]
            case StageId.S4_GATE:
                # The gate filters: its proposals replace the queued ones.
                self._state.pending_proposals = fragment.proposals
                self._merge_classification(fragment.classification)
            case StageId.S5_COMPOSE:
                self._state.pending_proposals = fragment.proposals
            case StageId.S6_TRAIN:
                await self._train_pending(fragment, all_records)
            case StageId.S7_MEASURE | StageId.S8_RECORD:
                all_records.extend(fragment.records)
                if stage_id is StageId.S7_MEASURE:
                    await self._attribute_allocation(fragment.records)
            case _:
                # S9 attributes axes and names nothing downstream.
                ...

    async def _train_pending(
        self, fragment: Fragment, all_records: list[Record]
    ) -> None:
        """Execute the round's queued cells, with failure isolation (WP19)."""
        if not self._state.pending_proposals:
            return

        limit = self._config.session_cell_limit
        if limit is not None:
            remaining = limit - len(all_records)
            if remaining <= 0:
                self._state.pending_proposals.clear()
                self._shutdown = True
                return
            self._state.pending_proposals = self._state.pending_proposals[:remaining]

        # Progress bar for proposals in this round
        pbar_proposals = (
            tqdm(
                total=len(self._state.pending_proposals),
                desc=f"Round {self._state.current_round} cells",
                unit="cell",
                leave=False,
                disable=tqdm is None or not sys.stdout.isatty(),
            )
            if tqdm
            else None
        )

        successful = await self._execute_batch_with_isolation(
            self._state.pending_proposals,
            progress_bar=pbar_proposals,
        )
        all_records.extend(successful)
        fragment.records.extend(successful)
        # Executed is not pending: leaving them queued makes S3 skip the policy
        # next round, so a run re-proposes the same cells and stops after one
        # round of a space it never entered.
        self._state.pending_proposals.clear()

        if pbar_proposals:
            pbar_proposals.close()

        if limit is not None and len(all_records) >= limit:
            self._shutdown = True

    async def _attribute_allocation(self, records: list[Record]) -> None:
        """Re-allocate after measuring, before S10 decides (R19 allocator)."""
        if self._config.allocator and self._state.deadline:
            promotions = await self._run_allocator(records)
            # Store promotions in state for S10 Decide stage
            self._state.allocator_promotions = promotions

    def _build_search_space(self) -> SearchSpace:
        """Build the run's active space from its spec (TODO46 §3.3)."""
        from computronium.experiment.kernel.search_space import (
            search_space_from_spec,
        )

        return search_space_from_spec(
            self._config.run_spec, tasks=_resolve_tasks(self._config)
        )

    async def _dispatch_stage(self, stage_id: StageId, stage_spec) -> Fragment:
        """Dispatch to the concrete stage implementation."""
        from computronium.experiment.execution.stages_impl import (
            get_stage_implementation,
        )

        impl_class = get_stage_implementation(stage_id)
        if impl_class is None:
            logger.warning("No implementation for stage %s, using no-op", stage_id)
            from computronium.experiment.execution.stage import Fragment

            return Fragment(stage_id=stage_id)

        # Create stage context
        ctx = self._create_stage_context(stage_id, stage_spec)

        # Run the stage
        stage_impl = impl_class()
        started = time.perf_counter()
        try:
            fragment = await stage_impl.run(ctx)
        except Exception as e:
            logger.exception("Stage %s failed", stage_id)
            # Return fragment with error info
            from computronium.experiment.execution.stage import Fragment

            fragment = Fragment(
                stage_id=stage_id,
                metadata={"error": str(e)},
                coverage={"stage": stage_id.value, "error": True},
            )
        finally:
            self._state.stage_timings[stage_id.value] = time.perf_counter() - started
        return fragment

    def _create_stage_context(self, stage_id: StageId, stage_spec) -> StageContext:
        """Create StageContext for a stage."""
        from computronium.experiment.execution.stage import StageContext

        # Ensure required components are available
        deadline = self._state.deadline
        policy = self._config.policy
        backend = self._config.backend
        search_space = self._state.search_space

        if (
            deadline is None
            or policy is None
            or backend is None
            or search_space is None
        ):
            raise ValueError("Missing required pipeline components for stage context")

        # Use environment snapshot from system context (WP19)
        system_context = self._state.system_context
        if system_context is None:
            raise ValueError("SystemContext not initialized")
        env_dict = system_context.environment.to_provenance_dict()

        return StageContext(
            run_id=self._config.run_id,
            run_spec=self._config.run_spec,
            stage_id=stage_id,
            store=self._store,
            deadline=deadline,
            deadline_enforcer=self._state.deadline_enforcer,
            policy=policy,
            allocator=self._config.allocator,
            backend=backend,
            search_space=search_space,
            completed_keys=self._state.completed_measurement_keys,
            pending_proposals=self._state.pending_proposals,
            in_progress=self._state.in_progress,
            stage_params=stage_spec.params,
            provenance=self._provenance(env_dict),
            system_context=system_context,
            batch_sizer=self._state.batch_sizer,
            cell_stream=self._state.cell_stream,
            allocator_promotions=self._state.allocator_promotions,
        )

    def _provenance(self, env_dict: dict[str, Any]) -> Provenance:
        """The run's provenance: environment plus the spec's own declarations.

        The dataset and code SHA were resolved once in ``__init__`` from the
        spec (or the task/repo), so every stage's records carry the same
        contract-satisfying values.
        """
        spec = self._config.run_spec
        return Provenance(
            env=env_dict,
            dataset=self._dataset,
            dataset_version=spec.dataset_version,
            code_sha=self._code_sha,
            policy=self._config.policy.get_name() if self._config.policy else "unknown",
            links={"run_id": self._config.run_id},
        )

    def _merge_coverage(self, coverage: dict[str, Any]) -> None:
        """Merge coverage from fragment into state."""
        # Store per-stage coverage using stage key
        stage_key = coverage.get("stage", "unknown")
        self._state.coverage[stage_key] = coverage

    def _merge_classification(self, classification: dict[str, Any]) -> None:
        """Merge classification from fragment into state."""
        self._state.rejections.append(classification)

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

    def _classify_rejection(
        self,
        coordinate: Coordinate,
        schedule: Schedule,
        cause: str,
        message: str,
    ) -> None:
        """Classify a rejection identically for every policy (R19).

        Args:
            coordinate: The experiment coordinate that was rejected
            schedule: The execution schedule
            cause: Failure cause classification
            message: Human-readable error message
        """
        classification = {
            "stage": "train",
            "cell_key": coordinate.cell_key(),
            "coordinate": coordinate.to_dict(),
            "schedule": schedule.to_dict(),
            "cause": cause,
            "message": message,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }
        self._state.rejections.append(classification)

    def _get_decision_from_fragments(self) -> Decision:
        """The decision S10 last reached, or continue while it has said nothing.

        S10 states a real termination ("budget exhausted", a promotion gate that
        closed) and this read it back as a constant CONTINUE, so the run's only
        stopping condition was the round limit and the exhaustion heuristic —
        every reason a stage gave for stopping was a comment in a fragment.
        """
        from computronium.experiment.execution.decision import continue_round

        decision = self._state.last_decision
        return (
            decision
            if decision is not None
            else continue_round(rationale="No stage has decided yet")
        )

    async def _run_allocator(
        self, records: list[Record]
    ) -> list[tuple[Coordinate, Schedule]]:
        """Run EvidenceDrivenAllocator between rounds (R46-R51).

        In the deadline system, allocator uses online cell timing for
        cost estimation instead of predicted cost models.

        Returns:
            List of promoted (coordinate, schedule) pairs for the next round.
        """
        if not self._config.allocator:
            return []

        logger.debug("Running allocator for run %s", self._config.run_id)

        # Use deadline enforcer and cell timing for online cost estimation
        deadline_enforcer = self._state.deadline_enforcer
        cell_timing = self._state.cell_timing
        if deadline_enforcer is None or cell_timing is None:
            return []

        # Check if we have time for more cells
        if not deadline_enforcer.check_before_cell():
            logger.info("Deadline reached, skipping allocator proposals")
            return []

        # Get candidates from search space for promotion consideration
        search_space = self._state.search_space
        if search_space is None:
            return []

        # Build candidates from search space (structural coordinates at next fidelity)
        candidates = self._build_allocator_candidates(search_space)
        if not candidates:
            return []

        # Observe records to update allocator's evidence base
        for record in records:
            self._config.allocator.observe(record)

        # Get promotion proposals from allocator
        promotions = self._config.allocator.propose(
            candidates,
            records,
            deadline=self._state.deadline,
            cost_model=None,
        )

        logger.info("Allocator proposed %d promotions", len(promotions))
        return promotions

    def _build_allocator_candidates(
        self, search_space: SearchSpace
    ) -> list[tuple[Coordinate, Schedule]]:
        """Build candidate coordinates for allocator to consider for promotion.

        Generates structural coordinates at the next fidelity level for cells
        that have shown promise at lower fidelity.
        """
        from computronium.experiment.kernel.evaluate import task_shape
        from computronium.experiment.kernel.search_space import iter_candidates

        candidates = []
        # Use the first task for shape resolution
        task = (
            self._config.run_spec.task_names[0]
            if self._config.run_spec.task_names
            else "xor"
        )

        # Generate candidates at explore fidelity (L0/L1) for promotion to exploit fidelity
        spec = self._config.run_spec
        # Temporarily adjust fidelity for candidate generation
        explore_fidelity = "L0"
        original_fidelity = spec.fidelity

        # We need to generate candidates without modifying the original spec
        # Create a temporary spec-like object or use iter_candidates directly
        for coord, sched in iter_candidates(
            spec,
            search_space,
            deadline=self._state.deadline,
            shape=task_shape,
            max_scan=1000,  # Limit scan for allocator candidates
            check_composable=False,  # Skip composability for speed at allocation time
        ):
            # Only consider cells at explore fidelity for promotion
            if sched.fidelity in ("L0", "L1"):
                # Create a new schedule at the next fidelity
                next_fidelity = "L1" if sched.fidelity == "L0" else "L2"
                from computronium.experiment.schema.coordinate import Schedule

                promo_sched = Schedule(
                    fidelity=next_fidelity,
                    seed=sched.seed,
                    n_seeds=sched.n_seeds,
                    epochs=sched.epochs * 2,  # More epochs at higher fidelity
                    batch_limit=sched.batch_limit,
                    budget_id="promotion",
                    task_id=sched.task_id,
                    param_budget=sched.param_budget,
                    device=sched.device,
                    deterministic=sched.deterministic,
                    num_workers=sched.num_workers,
                    precision=sched.precision,
                    checkpoint_every_n=sched.checkpoint_every_n,
                )
                candidates.append((coord, promo_sched))

                if len(candidates) >= 50:  # Limit candidates
                    break

        return candidates

    def _fresh_batch_items(
        self, proposals: list[Proposal], provenance: Provenance
    ) -> list[tuple[Coordinate, Schedule, Provenance, dict[str, Any]]]:
        """The still-unmeasured seeds of every proposal, as single-seed items.

        Identity is the store's: a record is keyed by its own ``n_seeds=1``
        schedule, so a proposal whose seeds were measured in an earlier round —
        or in an earlier launch of this ``run_id`` — is skipped seed by seed
        rather than as a whole cell. Skipping the whole cell would drop the
        seeds it has never run; re-measuring all of them spends the store's
        patience, not the run's.

        Each item carries the proposal's *own* provenance, so the data origin
        and contrast assignment S1 stamped on it reach the record. The run's
        provenance carries neither: a design that vanishes before persistence
        is a design the store cannot re-derive, and the contrast split was
        exactly that.

        Admission gate: every candidate passes through SystemConfig.validate
        (via compose_configs) at the batch boundary. Invalid cells are added
        to rejected_keys and never reach the trainer.
        """
        from computronium.experiment.kernel.compose import compose_configs
        from computronium.experiment.kernel.evaluate import task_shape

        seen: set[str] = set(self._state.completed_measurement_keys)
        rejected: set[str] = set(self._state.rejected_keys)
        skipped = 0
        rejected_this_batch = 0
        items: list[tuple[Coordinate, Schedule, Provenance, dict[str, Any]]] = []
        for proposal in proposals:
            item_provenance = _provenance_for(provenance, proposal)
            for schedule in proposal.schedule.seed_plan:
                key = proposal.coordinate.measurement_key(schedule)
                if key in seen:
                    skipped += 1
                    continue
                if key in rejected:
                    rejected_this_batch += 1
                    continue

                # ADMISSION GATE: last-mile SystemConfig.validate check
                # This is the single source of truth for legality
                try:
                    task_id = schedule.task_id or (
                        self._config.run_spec.task_names[0]
                        if self._config.run_spec.task_names
                        else "unknown"
                    )
                    task_shape_info = task_shape(task_id)
                    config = compose_configs(
                        coordinate=proposal.coordinate,
                        geometry={},
                        input_shape=task_shape_info.input_shape,
                        output_dim=task_shape_info.output_dim,
                        param_budget=schedule.param_budget,
                    )
                    # Param budget check (R25 fairness rule)
                    from computronium.experiment.kernel.compose import (
                        geometry_param_count,
                    )
                    from computronium.experiment.schema.registries import (
                        PARAM_BUDGET_TOLERANCE,
                    )

                    if schedule.param_budget > 0:
                        if geometry_param_count(
                            config.geometry
                        ) > schedule.param_budget * (1 + PARAM_BUDGET_TOLERANCE):
                            raise ValueError(
                                f"Param budget exceeded: {geometry_param_count(config.geometry)} > {schedule.param_budget}"
                            )
                except (ValueError, TypeError, KeyError) as e:
                    # Reject this cell - add to durable rejected set
                    self._state.rejected_keys.add(key)
                    rejected_this_batch += 1
                    self._classify_rejection(
                        coordinate=proposal.coordinate,
                        schedule=schedule,
                        cause="ADMISSION_REJECTED",
                        message=str(e),
                    )
                    continue

                seen.add(key)
                items.append((proposal.coordinate, schedule, item_provenance, {}))

        if skipped:
            logger.info("Skipped %d already-measured seed(s)", skipped)
        if rejected_this_batch:
            logger.info(
                "Admission gate rejected %d invalid cell(s)", rejected_this_batch
            )
        return items

    async def _execute_batch_with_isolation(
        self,
        proposals: list[Proposal],
        progress_bar: tqdm | None = None,  # type: ignore[reportInvalidTypeForm]
    ) -> list[Record]:
        """Execute a batch of proposals with failure isolation (WP19).

        Uses backend.submit_batch which returns per-item EvaluationResult
        (Success or Failure), allowing successful siblings to continue
        even if some evaluations fail.

        Deadline enforcement:
        - Check soft deadline before starting batch
        - Track cell timing for online learning
        - Mark QUARANTINE cells if hard deadline breached mid-execution
        """
        if not self._config.backend:
            logger.warning("No backend configured, skipping batch execution")
            return []

        # Check deadline before starting batch
        deadline_enforcer = self._state.deadline_enforcer
        if deadline_enforcer and not deadline_enforcer.check_before_cell():
            logger.info("Soft deadline reached, stopping before new batch")
            self._shutdown = True
            return []

        system_context = self._state.system_context
        if system_context is None:
            raise ValueError("SystemContext not initialized")
        provenance = self._provenance(system_context.environment.to_provenance_dict())

        batch_items = self._fresh_batch_items(proposals, provenance)
        if not batch_items:
            return []

        # Start cell timing for this batch
        cell_timing = self._state.cell_timing
        if cell_timing:
            cell_timing.start_cell()

        try:
            results = await self._config.backend.submit_batch(batch_items, self._store)
        finally:
            # End cell timing
            if cell_timing:
                cell_timing.end_cell()

        stored = self._persist_results(batch_items, results)
        for record in stored:
            self._observe(record)

        # Check deadline after batch
        if deadline_enforcer and not deadline_enforcer.check_after_cell():
            logger.info("Soft deadline reached after batch, stopping")
            self._shutdown = True

        if progress_bar:
            progress_bar.update(len(stored))
        return stored

    def _persist_results(
        self,
        batch_items: list[tuple[Coordinate, Schedule, Provenance, dict[str, Any]]],
        results: list[EvaluationResult],
    ) -> list[Record]:
        """Persist successes and classify every non-success; a sibling never aborts the batch."""
        successful: list[Record] = []
        for (coord, sched, _prov, _params), result in zip(batch_items, results):
            match result:
                case Success(records=records):
                    stored_here: list[Record] = []
                    for record in records:
                        record.payload.setdefault(
                            "stage_timings", dict(self._state.stage_timings)
                        )
                        # Check for checkpoint artifact
                        artifacts = []
                        if "checkpoint_bytes_b64" in record.payload:
                            import base64

                            from computronium.experiment.evidence.artifacts import (
                                ArtifactInput,
                                ArtifactRole,
                            )

                            checkpoint_bytes = base64.b64decode(
                                record.payload["checkpoint_bytes_b64"]
                            )
                            artifacts.append(
                                ArtifactInput(
                                    bytes=checkpoint_bytes,
                                    role=ArtifactRole.MODEL_CHECKPOINT,
                                )
                            )
                            # Remove from payload to avoid duplication
                            del record.payload["checkpoint_bytes_b64"]

                        try:
                            if artifacts:
                                self._store.append_with_artifacts(record, artifacts)
                            else:
                                self._store.append(record)
                        except Exception as e:
                            logger.exception(
                                "Failed to persist record %s", coord.cell_key()
                            )
                            self._classify_rejection(
                                coordinate=coord,
                                schedule=sched,
                                cause="PERSISTENCE_ERROR",
                                message=str(e),
                            )
                            continue
                        stored_here.append(record)
                        self._state.completed_measurement_keys.add(
                            record.measurement_key
                        )
                    self._charge_budget(stored_here)
                    successful.extend(stored_here)
                case Failure(failure_event=event):
                    logger.warning(
                        "Evaluation failed for %s: %s",
                        coord.cell_key(),
                        event.error_message,
                    )
                    self._classify_rejection(
                        coordinate=coord,
                        schedule=sched,
                        cause=getattr(event.failure_cause, "value", None)
                        or str(event.failure_cause),
                        message=event.error_message,
                    )
        return successful

    def _observe(self, record: Record) -> None:
        """Hand a stored measurement to the policy.

        The policy is where a learning policy learns, and until this call
        existed `observe` had zero call sites outside its own module: the study
        was asked, never told (TODO46 §D3).
        """
        policy = self._config.policy
        if policy is None:
            return
        try:
            policy.observe(record)
        except Exception:
            logger.exception(
                "Policy %s failed to observe %s",
                policy.get_name(),
                record.measurement_key[:12],
            )

    def _check_gate(self, fragment: Fragment, stage_spec) -> bool:
        """Check if stage gate passes."""
        if stage_spec.gate == "skip":
            return True

        if not fragment.records and not fragment.proposals:
            return stage_spec.gate != "pass"

        # For claim gate, require claim_eligible records
        if stage_spec.gate == "claim":
            eligible = [r for r in fragment.records if self._is_claim_eligible(r)]
            return len(eligible) > 0

        # For pass gate, require at least one non-quarantine PASS
        if stage_spec.gate == "pass":
            passing = [
                r
                for r in fragment.records
                if r.status.gate_verdict.value == "PASS" and not r.status.quarantine
            ]
            return len(passing) > 0

        return True

    def _is_claim_eligible(self, record: Record) -> bool:
        """Check if record is claim-eligible (the one predicate, not a copy)."""
        from computronium.experiment.evidence.claims import claim_eligible

        return claim_eligible(record)

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

    def shutdown(self) -> None:
        """Shutdown the pipeline runner."""
        self._shutdown = True
        if self._config.backend:
            self._config.backend.shutdown()

    def get_coverage_report(self) -> dict[str, Any]:
        """Get coverage report (R18)."""
        return self._state.coverage

    def get_rejection_report(self) -> list[dict[str, Any]]:
        """Get rejection classification report (R19)."""
        return self._state.rejections

    def get_proposal_provenance(self) -> list[dict[str, Any]]:
        """Get proposal provenance (R20)."""
        return self._state.proposal_provenance


__all__ = [
    "PipelineConfig",
    "PipelineRunner",
    "PipelineState",
]
