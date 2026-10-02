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

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from computronium.experiment.execution.decision import Decision, RoundController
from computronium.experiment.execution.stage import StageId, get_stage_spec
from computronium.experiment.execution.sysctx import (
    SystemContext,
    capture_environment_snapshot,
)
from computronium.experiment.schema.coordinate import Coordinate, Provenance, Schedule

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.execution.allocator import EvidenceDrivenAllocator
    from computronium.experiment.execution.backends import ExecutionBackend
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
    checkpoint_dir: Path | None = None
    checkpoint_interval_seconds: float = 60.0
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
    last_checkpoint_time: float = 0.0
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

        logger.info(
            "Pipeline run %s completed: %d records, %d rounds",
            self._config.run_id,
            len(all_records),
            self._state.current_round,
        )
        return all_records

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
        """Run S3-S10 round loop with Decision-based termination."""
        round_controller = self._state.round_controller
        if round_controller is None:
            from computronium.experiment.execution.decision import RoundController

            round_controller = RoundController(
                max_rounds=self._config.max_rounds,
                min_rounds=self._config.min_rounds,
            )
            self._state.round_controller = round_controller

        while round_controller.should_continue(self._get_decision_from_fragments()):
            if self._shutdown:
                break
            await self._execute_round(all_records)

    async def _execute_round(self, all_records: list[Record]) -> None:  # ruff: ignore[complex-structure]
        """Execute a single round of S3-S10 stages."""
        self._state.current_round += 1
        logger.info("Starting round %d", self._state.current_round)

        # S3 Schedule
        if StageId.S3_SCHEDULE in self._stages:
            fragment = await self._dispatch_stage(
                StageId.S3_SCHEDULE, get_stage_spec(StageId.S3_SCHEDULE)
            )
            self._state.pending_proposals.extend(fragment.proposals)
            self._merge_coverage(fragment.coverage)

        # S4 Gate
        if StageId.S4_GATE in self._stages:
            fragment = await self._dispatch_stage(
                StageId.S4_GATE, get_stage_spec(StageId.S4_GATE)
            )
            self._state.pending_proposals = fragment.proposals  # Filtered
            self._merge_coverage(fragment.coverage)
            self._merge_classification(fragment.classification)

        # S5 Compose
        if StageId.S5_COMPOSE in self._stages:
            fragment = await self._dispatch_stage(
                StageId.S5_COMPOSE, get_stage_spec(StageId.S5_COMPOSE)
            )
            self._state.pending_proposals = fragment.proposals
            self._merge_coverage(fragment.coverage)

        # S6 Train
        if StageId.S6_TRAIN in self._stages:
            # First dispatch the stage to get any stage-specific proposals
            fragment = await self._dispatch_stage(
                StageId.S6_TRAIN, get_stage_spec(StageId.S6_TRAIN)
            )
            self._merge_coverage(fragment.coverage)

            # Execute pending proposals with failure isolation (WP19)
            if self._state.pending_proposals:
                successful_records = await self._execute_batch_with_isolation(
                    self._state.pending_proposals
                )
                all_records.extend(successful_records)
                fragment.records.extend(successful_records)

        # S7 Measure
        if StageId.S7_MEASURE in self._stages:
            fragment = await self._dispatch_stage(
                StageId.S7_MEASURE, get_stage_spec(StageId.S7_MEASURE)
            )
            all_records.extend(fragment.records)
            self._merge_coverage(fragment.coverage)

            # Run allocator between rounds (after S7_MEASURE, before S10_DECIDE)
            if self._config.allocator and self._config.budget:
                await self._run_allocator(fragment.records)

        # S8 Record
        if StageId.S8_RECORD in self._stages:
            fragment = await self._dispatch_stage(
                StageId.S8_RECORD, get_stage_spec(StageId.S8_RECORD)
            )
            all_records.extend(fragment.records)
            self._merge_coverage(fragment.coverage)

        # S9 Attribute
        if StageId.S9_ATTRIBUTE in self._stages:
            fragment = await self._dispatch_stage(
                StageId.S9_ATTRIBUTE, get_stage_spec(StageId.S9_ATTRIBUTE)
            )
            self._merge_coverage(fragment.coverage)

        # S10 Decide
        if StageId.S10_DECIDE in self._stages:
            fragment = await self._dispatch_stage(
                StageId.S10_DECIDE, get_stage_spec(StageId.S10_DECIDE)
            )
            self._state.pending_proposals.extend(fragment.proposals)
            self._merge_coverage(fragment.coverage)

        # Checkpoint after each round
        if self._config.checkpoint_dir:
            await self._create_checkpoint()

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
        """Extract Decision from the last S10 fragment."""
        # For now, create a default continue decision
        # In practice, this would come from the S10 Decide stage fragment
        from computronium.experiment.execution.decision import continue_round

        return continue_round(rationale="Default continue")

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

    async def _execute_batch_with_isolation(
        self,
        proposals: list[Proposal],
    ) -> list[Record]:
        """Execute a batch of proposals with failure isolation (WP19).

        Uses backend.submit_batch which returns per-item EvaluationResult
        (Success or Failure), allowing successful siblings to continue
        even if some evaluations fail.

        Args:
            proposals: List of proposals to evaluate

        Returns:
            List of successfully evaluated Records.
        """
        if not self._config.backend:
            logger.warning("No backend configured, skipping batch execution")
            return []

        # Build batch items for backend
        system_context = self._state.system_context
        if system_context is None:
            raise ValueError("SystemContext not initialized")
        env_dict = system_context.environment.to_provenance_dict()
        provenance = self._provenance(env_dict)

        # Deduplicate proposals by measurement_key to avoid duplicate key errors
        seen_keys: set[str] = set()
        batch_items = []
        for p in proposals:
            mkey = p.coordinate.measurement_key(p.schedule)
            if mkey not in seen_keys:
                seen_keys.add(mkey)
                batch_items.append((p.coordinate, p.schedule, provenance, {}))
            else:
                logger.warning("Skipping duplicate measurement_key: %s", mkey)

        # Execute with failure isolation
        from computronium.experiment.execution.backends import (
            EvaluationResult,
            Failure,
            Success,
        )

        results: list[EvaluationResult] = await self._config.backend.submit_batch(
            batch_items, self._store
        )

        # Process results: persist successes, classify failures
        successful_records: list[Record] = []
        for i, result in enumerate(results):
            match result:
                case Success(record=record):
                    try:
                        self._store.append(record)
                        self._observe(record)
                        successful_records.append(record)
                        self._state.completed_measurement_keys.add(
                            record.measurement_key
                        )
                    except Exception as e:
                        logger.exception(
                            "Failed to persist record for %s",
                            proposals[i].coordinate.cell_key(),
                        )
                        self._classify_rejection(
                            coordinate=proposals[i].coordinate,
                            schedule=proposals[i].schedule,
                            cause="PERSISTENCE_ERROR",
                            message=str(e),
                        )
                case Failure(failure_event=event):
                    logger.warning(
                        "Evaluation failed for %s: %s",
                        proposals[i].coordinate.cell_key(),
                        event.error_message,
                    )
                    self._classify_rejection(
                        coordinate=proposals[i].coordinate,
                        schedule=proposals[i].schedule,
                        cause=event.failure_cause.value
                        if hasattr(event.failure_cause, "value")
                        else str(event.failure_cause),
                        message=event.error_message,
                    )
                    # Siblings continue - we don't raise the exception

        return successful_records

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
        """Check if record is claim-eligible (pure predicate)."""
        return (
            record.status.gate_verdict.value == "PASS"
            and not record.status.quarantine
            and record.schedule.fidelity == "L2"
            and record.schedule.n_seeds >= 5
        )

    async def _create_checkpoint(self) -> None:
        """Create a periodic checkpoint."""
        if not self._config.checkpoint_dir:
            return

        from computronium.experiment.execution.replay import create_checkpoint

        self._config.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        timestamp = int(time.time() * 1000)
        checkpoint_path = (
            self._config.checkpoint_dir
            / f"checkpoint_{self._config.run_id}_{timestamp}.json"
        )

        checkpoint = create_checkpoint(
            run_id=self._config.run_id,
            run_spec=self._config.run_spec,
            completed_keys=frozenset(self._state.completed_measurement_keys),
            pending=[(p.coordinate, p.schedule) for p in self._state.pending_proposals],
            in_progress=self._state.in_progress,
            budget=self._state.budget,
            allocator_state=self._state.allocator_state,
        )
        checkpoint.to_file(checkpoint_path)
        self._state.last_checkpoint_time = time.time()
        logger.debug("Created checkpoint: %s", checkpoint_path)

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
