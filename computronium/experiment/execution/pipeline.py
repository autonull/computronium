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
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Final

from computronium.experiment.execution.backends import Failure, Success
from computronium.experiment.execution.decision import Decision, RoundController
from computronium.experiment.execution.stage import StageId, get_stage_spec
from computronium.experiment.execution.sysctx import (
    SystemContext,
    capture_environment_snapshot,
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
    from computronium.experiment.execution.budget import Budget, CostModel
    from computronium.experiment.execution.policy import Policy
    from computronium.experiment.execution.search_space import SearchSpace
    from computronium.experiment.execution.stage import (
        Fragment,
        Proposal,
        StageContext,
    )
    from computronium.experiment.schema.record import Record
    from computronium.experiment.schema.run_spec import RunSpec

logger = logging.getLogger(__name__)

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None  # type: ignore[assignment]

# Rounds that may measure nothing while still proposing fresh cells before the
# run concludes they cannot measure anything.
_MAX_FRUITLESS_ROUNDS: Final = 3

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


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    """Configuration for the pipeline runner."""

    run_id: str
    run_spec: RunSpec
    stages: list[StageId] = field(default_factory=list)
    budget: Budget | None = None
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
    budget: Budget | None = None
    allocator_state: dict[str, Any] | None = None
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
    # Whether the last batch contained a cell this run had never proposed, and
    # how many rounds in a row have measured nothing while fresh cells existed
    # (a failing cell must not spin the loop forever).
    last_batch_was_all_seen: bool = False
    fruitless_rounds: int = 0
    # System context with environment snapshot (WP19/R75/K10)
    system_context: SystemContext | None = None


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
            budget=config.budget,
            round_controller=RoundController(
                max_rounds=config.max_rounds,
                min_rounds=config.min_rounds,
            ),
            system_context=system_context,
        )
        self._stages = config.stages or [
            StageId(n) for n in config.run_spec.stage_names
        ]
        self._shutdown = False
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
        try:
            await self._heartbeat_task
        except asyncio.CancelledError:
            pass

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
        """Run S3-S10 round loop with Decision-based termination.

        A round that stores nothing new ends the run: the policy has exhausted
        the space the spec declares (or the budget can no longer afford a cell),
        and S10's decision is a constant CONTINUE, so nothing else would ever
        say so. An undeclared run limit would instead hide the exhaustion
        behind a truncation.
        """
        round_controller = self._state.round_controller
        if round_controller is None:
            from computronium.experiment.execution.decision import RoundController

            round_controller = RoundController(
                max_rounds=self._config.max_rounds,
                min_rounds=self._config.min_rounds,
            )
            self._state.round_controller = round_controller

        # Progress bar for rounds
        pbar_rounds = (
            tqdm(
                total=round_controller.max_rounds or 0,
                desc="Rounds",
                unit="round",
                disable=tqdm is None,
            )
            if tqdm
            else None
        )

        while round_controller.should_continue(self._get_decision_from_fragments()):
            if self._shutdown:
                break
            before = len(all_records)
            await self._execute_round(all_records)
            if pbar_rounds:
                pbar_rounds.update(1)
            if len(all_records) > before:
                self._state.fruitless_rounds = 0
                continue
            # Nothing was stored. If the round proposed nothing the run had not
            # already measured, the policy has no fresh cell left and the space
            # it can reach is exhausted; if it did propose fresh cells and they
            # all failed, the loop retries a bounded number of times rather
            # than spinning forever on a cell that cannot be measured.
            if self._state.last_batch_was_all_seen:
                logger.info(
                    "Round %d re-proposed only measured cells; the space this "
                    "policy reaches is exhausted",
                    round_controller.current_round,
                )
                break
            self._state.fruitless_rounds += 1
            if self._state.fruitless_rounds >= _MAX_FRUITLESS_ROUNDS:
                logger.info(
                    "%d rounds measured nothing despite fresh cells; stopping",
                    self._state.fruitless_rounds,
                )
                break

        if pbar_rounds:
            pbar_rounds.close()

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

        # Progress bar for proposals in this round
        pbar_proposals = (
            tqdm(
                total=len(self._state.pending_proposals),
                desc=f"Round {self._state.current_round} cells",
                unit="cell",
                leave=False,
                disable=tqdm is None,
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

    async def _attribute_allocation(self, records: list[Record]) -> None:
        """Re-allocate after measuring, before S10 decides (R19 allocator)."""
        if self._config.allocator and self._config.budget:
            await self._run_allocator(records)

    def _build_search_space(self) -> SearchSpace:
        """Build the run's active space from its spec (TODO46 §3.3)."""
        from computronium.experiment.execution.search_space import (
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
        return fragment

    def _create_stage_context(self, stage_id: StageId, stage_spec) -> StageContext:
        """Create StageContext for a stage."""
        from computronium.experiment.execution.stage import StageContext

        # Ensure required components are available
        budget = self._state.budget
        cost_model = self._config.cost_model
        policy = self._config.policy
        backend = self._config.backend
        search_space = self._state.search_space

        if (
            budget is None
            or cost_model is None
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
            budget=budget,
            cost_model=cost_model,
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
        )

    def _provenance(self, env_dict: dict[str, Any]) -> Provenance:
        """The run's provenance: environment plus the spec's own declarations."""
        spec = self._config.run_spec
        return Provenance(
            env=env_dict,
            dataset=spec.dataset,
            dataset_version=spec.dataset_version,
            code_sha=spec.code_sha,
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
        """Charge the run's budget for what it actually stored.

        A budget nobody charges cannot expire: ``target_cells`` and
        ``target_cost`` were unreachable, every cell looked affordable, and
        S10's "budget exhausted" could only ever be read off the clock. A
        campaign declares a budget as its stopping condition, so the charge is
        the difference between a declared limit and a comment — and because the
        store keeps what it stored, an exhausted budget is also the resume
        point (``comp run --run-id``).
        """
        budget = self._state.budget
        cost_model = self._config.cost_model
        if budget is None or not records:
            return
        cost = (
            sum(cost_model.actual_cost(record) for record in records)
            if cost_model is not None
            else 0.0
        )
        self._state.budget = budget.advance_by(len(records)).add_cost(cost)

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

    async def _run_allocator(self, records: list[Record]) -> None:
        """Run EvidenceDrivenAllocator between rounds (R46-R51)."""
        if not self._config.allocator:
            return

        logger.debug("Running allocator for run %s", self._config.run_id)

        # Convert pending proposals to candidates
        candidates = [(p.coordinate, p.schedule) for p in self._state.pending_proposals]

        # Get proposals from allocator
        budget = self._state.budget
        cost_model = self._config.cost_model
        if budget is None or cost_model is None:
            return

        proposals = self._config.allocator.propose(
            candidates=candidates,
            records=records,
            budget=budget,
            cost_model=cost_model,
        )

        # Convert to Proposal objects
        from computronium.experiment.execution.stage import Proposal

        for coord, sched in proposals:
            self._state.pending_proposals.append(
                Proposal(
                    coordinate=coord,
                    schedule=sched,
                    rationale="allocator_promotion",
                )
            )

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
        """
        seen: set[str] = set(self._state.completed_measurement_keys)
        skipped = 0
        items: list[tuple[Coordinate, Schedule, Provenance, dict[str, Any]]] = []
        for proposal in proposals:
            item_provenance = _provenance_for(provenance, proposal)
            for schedule in proposal.schedule.seed_plan:
                key = proposal.coordinate.measurement_key(schedule)
                if key in seen:
                    skipped += 1
                    continue
                seen.add(key)
                items.append((proposal.coordinate, schedule, item_provenance, {}))
        self._state.last_batch_was_all_seen = not items
        if skipped:
            logger.info("Skipped %d already-measured seed(s)", skipped)
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

        Args:
            proposals: List of proposals to evaluate
            progress_bar: Optional tqdm progress bar to update

        Returns:
            List of successfully evaluated Records.
        """
        if not self._config.backend:
            logger.warning("No backend configured, skipping batch execution")
            return []

        system_context = self._state.system_context
        if system_context is None:
            raise ValueError("SystemContext not initialized")
        provenance = self._provenance(system_context.environment.to_provenance_dict())

        batch_items = self._fresh_batch_items(proposals, provenance)
        if not batch_items:
            return []

        results = await self._config.backend.submit_batch(batch_items, self._store)
        stored = self._persist_results(batch_items, results)
        for record in stored:
            self._observe(record)
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
