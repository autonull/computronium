"""S1-S11 pipeline runner with reconciliation (WP4)."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from computronium.experiment.schema.coordinate import Coordinate, Provenance, Schedule

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.execution.backends import ExecutionBackend
    from computronium.experiment.execution.budget import Budget, CostModel
    from computronium.experiment.execution.policy import Policy
    from computronium.experiment.execution.stage import StageId, StageSpec
    from computronium.experiment.schema.record import Record

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    """Configuration for the pipeline runner."""

    run_id: str
    run_spec: dict[str, Any]
    stages: list[StageId] = field(default_factory=list)
    budget: Budget | None = None
    cost_model: CostModel | None = None
    policy: Policy | None = None
    backend: ExecutionBackend | None = None
    checkpoint_dir: Path | None = None
    checkpoint_interval_seconds: float = 60.0
    max_concurrent_evaluations: int = 10
    seed: int | None = None


@dataclass(slots=True)
class PipelineState:
    """Mutable state for pipeline execution."""

    run_id: str
    current_stage_idx: int = 0
    completed_measurement_keys: set[str] = field(default_factory=set)
    pending_candidates: list[tuple[Coordinate, Schedule]] = field(default_factory=list)
    in_progress: list[tuple[Coordinate, Schedule]] = field(default_factory=list)
    budget: Budget | None = None
    allocator_state: dict[str, Any] | None = None
    last_checkpoint_time: float = 0.0


class PipelineRunner:
    """S1-S11 pipeline runner with atomic append + reconciliation.

    Coordinates the full experiment lifecycle:
    - Stage progression (S1-S11)
    - Budget management
    - Policy-driven candidate selection
    - Backend execution
    - Record persistence with reconciliation
    - Checkpointing and resume
    """

    def __init__(
        self,
        config: PipelineConfig,
        store: RecordStore,
    ) -> None:
        self._config = config
        self._store = store
        self._state = PipelineState(
            run_id=config.run_id,
            budget=config.budget,
        )
        self._stages = config.stages or [s.stage_id for s in STAGE_SPECS]
        self._stage_specs = [get_stage_spec(s) for s in self._stages]
        self._shutdown = False

    async def run(self) -> list[Record]:
        """Run the full pipeline to completion.

        Returns:
            All records produced during the run.
        """
        logger.info(
            "Starting pipeline run %s with stages: %s",
            self._config.run_id,
            self._stages,
        )

        all_records: list[Record] = []

        for stage_idx, stage_spec in enumerate(self._stage_specs):
            if self._shutdown:
                break

            self._state.current_stage_idx = stage_idx
            logger.info("Entering stage %s (%s)", stage_spec.stage_id, stage_spec.name)

            stage_records = await self._run_stage(stage_spec)
            all_records.extend(stage_records)

            # Check gate verdict
            if not self._check_gate(stage_records, stage_spec):
                logger.warning(
                    "Gate failed for stage %s, stopping pipeline", stage_spec.stage_id
                )
                break

            # Checkpoint after each stage
            if self._config.checkpoint_dir:
                await self._create_checkpoint()

        logger.info(
            "Pipeline run %s completed: %d records",
            self._config.run_id,
            len(all_records),
        )
        return all_records

    async def _run_stage(self, stage_spec: StageSpec) -> list[Record]:
        """Execute a single pipeline stage."""
        # Generate candidates for this stage
        candidates = await self._generate_candidates(stage_spec)

        if not candidates:
            logger.info("No candidates for stage %s, skipping", stage_spec.stage_id)
            return []

        # Filter by budget
        if self._state.budget and self._state.budget.expired():
            logger.info("Budget exhausted, stopping stage %s", stage_spec.stage_id)
            return []

        # Execute candidates
        records = await self._execute_candidates(candidates, stage_spec)

        # Update state
        for record in records:
            self._state.completed_measurement_keys.add(record.measurement_key)

        return records

    async def _generate_candidates(
        self, stage_spec: StageSpec
    ) -> list[tuple[Coordinate, Schedule]]:
        """Generate candidate (coordinate, schedule) pairs for a stage."""
        # If we have pending candidates from previous stage, use those
        if self._state.pending_candidates:
            candidates = self._state.pending_candidates
            self._state.pending_candidates = []
            return candidates

        # Otherwise, generate from policy
        if self._config.policy and self._state.budget and self._config.cost_model:
            # Get recent records for evidence-driven policies
            recent_records = self._store.query_records(
                run_id=self._config.run_id, limit=1000
            )

            proposals = self._config.policy.propose(
                candidates=[],  # Will be populated from search space
                records=recent_records,
                budget=self._state.budget,
                cost_model=self._config.cost_model,
            )
            return proposals

        # Fallback: generate from search space (placeholder)
        return []

    async def _execute_candidates(
        self,
        candidates: list[tuple[Coordinate, Schedule]],
        stage_spec: StageSpec,
    ) -> list[Record]:
        """Execute a batch of candidates using the backend."""
        if not self._config.backend:
            logger.warning("No backend configured, skipping execution")
            return []

        # Prepare provenance
        provenance = Provenance(
            env={"python": "3.14", "platform": "linux"},
            dataset=self._config.run_spec.get("dataset", "unknown"),
            dataset_version=self._config.run_spec.get("dataset_version", "1.0"),
            code_sha=self._config.run_spec.get("code_sha", "unknown"),
            policy=self._config.policy.get_name() if self._config.policy else "unknown",
            links={"run_id": self._config.run_id},
        )

        # Execute in batches
        batch_size = self._config.max_concurrent_evaluations
        all_records = []

        for i in range(0, len(candidates), batch_size):
            batch = candidates[i : i + batch_size]
            logger.debug(
                "Executing batch %d/%d (%d candidates)",
                i // batch_size + 1,
                (len(candidates) + batch_size - 1) // batch_size,
                len(batch),
            )

            batch_records = await self._config.backend.submit_batch(
                [(coord, sched, provenance, coord.params) for coord, sched in batch],
                self._store,
            )

            # Append each record to store (with reconciliation)
            for record in batch_records:
                try:
                    stored_record = self._store.append(record)
                    all_records.append(stored_record)
                    logger.debug(
                        "Stored record %s (seq=%d)",
                        stored_record.record_id[:16],
                        stored_record.seq,
                    )
                except Exception:
                    logger.exception("Failed to store record")
                    raise

            # Update budget
            if self._state.budget:
                for record in batch_records:
                    cost = (
                        self._config.cost_model.actual_cost(record)
                        if self._config.cost_model
                        else 1.0
                    )
                    self._state.budget = self._state.budget.add_cost(cost).advance()

            # Periodic checkpoint
            if (
                self._config.checkpoint_dir
                and time.time() - self._state.last_checkpoint_time
                > self._config.checkpoint_interval_seconds
            ):
                await self._create_checkpoint()

        return all_records

    def _check_gate(self, records: list[Record], stage_spec: StageSpec) -> bool:
        """Check if stage gate passes."""
        if stage_spec.gate == "skip":
            return True

        if not records:
            return stage_spec.gate != "pass"

        # For claim gate, require claim_eligible records
        if stage_spec.gate == "claim":
            eligible = [r for r in records if self._is_claim_eligible(r)]
            return len(eligible) > 0

        # For pass gate, require at least one non-quarantine PASS
        if stage_spec.gate == "pass":
            passing = [
                r
                for r in records
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

        from computronium.experiment.execution.replay import (
            create_checkpoint,
        )

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
            pending=self._state.pending_candidates,
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


# Import STAGE_SPECS and get_stage_spec from stage module
from computronium.experiment.execution.stage import (  # noqa: E402
    STAGE_SPECS,
    get_stage_spec,
)

__all__ = [
    "PipelineConfig",
    "PipelineRunner",
    "PipelineState",
]
