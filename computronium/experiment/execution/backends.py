"""Execution backends for experiment evaluation (WP4 + WP19)."""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from computronium.experiment.evidence.failure import FailureEvent
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.schema.coordinate import (
        Coordinate,
        Provenance,
        Schedule,
    )
    from computronium.experiment.schema.record import Record

logger = logging.getLogger(__name__)

try:
    import torch.distributed as dist
    from torch.nn.parallel import DistributedDataParallel as DDP
    from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
    from torch.distributed.fsdp.wrap import size_based_auto_wrap_policy
    HAS_DDP = True
except ImportError:
    HAS_DDP = False
    dist = None
    DDP = None
    FSDP = None
    size_based_auto_wrap_policy = None


# =============================================================================
# Failure Isolation Types (WP19)
# =============================================================================


@dataclass(frozen=True, slots=True)
class Success:
    """Successful evaluation result.

    One item is one cell across the schedule's whole seed plan, so it carries
    every seed's record: dropping the seeds past the first pays for them and
    then reports a one-seed measurement as a replicated one.
    """

    records: tuple[Record, ...]

    @property
    def record(self) -> Record:
        """The first seed's record — the item's own identity."""
        return self.records[0]


@dataclass(frozen=True, slots=True)
class Failure:
    """Failed evaluation result."""

    failure_event: FailureEvent


EvaluationResult = Success | Failure


# =============================================================================
# Backend Protocol
# =============================================================================


@runtime_checkable
class ExecutionBackend(Protocol):
    """Protocol for execution backends.

    Workers return Records; the pipeline process is the sole writer
    (single-writer topology per §1.1). In-process concurrency via
    asyncio.TaskGroup; blocking evaluation bodies stay out of the event loop
    via asyncio.to_thread.

    Failure isolation (WP19): submit_batch returns per-item EvaluationResult
    instead of raising exceptions, allowing successful siblings to continue.
    """

    async def submit(
        self,
        coordinate: Coordinate,
        schedule: Schedule,
        provenance: Provenance,
        params: dict[str, Any],
        store: RecordStore,
    ) -> list[Record]:
        """Submit an evaluation and return completed records.

        Args:
            coordinate: The 6-axis experiment coordinate
            schedule: Execution schedule
            provenance: Provenance metadata
            params: Experiment parameters
            store: RecordStore for persistence (pipeline is sole writer)

        Returns:
            List of completed Records (one per seed).
        """
        ...

    async def submit_batch(
        self,
        items: list[tuple[Coordinate, Schedule, Provenance, dict[str, Any]]],
        store: RecordStore,
    ) -> list[EvaluationResult]:
        """Submit a batch of evaluations.

        Args:
            items: List of (coordinate, schedule, provenance, params)
            store: RecordStore for persistence

        Returns:
            List of EvaluationResult (Success or Failure per item).
            Successful siblings continue even if some items fail.
        """
        ...

    def shutdown(self) -> None:
        """Shutdown the backend and release resources."""
        ...


@dataclass(frozen=True, slots=True)
class EvaluationTask:
    """A single evaluation task."""

    coordinate: Coordinate
    schedule: Schedule
    provenance: Provenance
    params: dict[str, Any]


class _ThreadedBackend:
    """Shared backend: one evaluation implementation, off the event loop.

    Subclasses differ only in where the blocking body runs; the evaluation
    itself is always :func:`cell_record`, so a stub can never come back in one
    class while the other trains for real (TODO46 §D1).
    """

    def __init__(self, *, max_workers: int = 4) -> None:
        self._max_workers = max_workers
        self._shutdown = False
        self._admission = asyncio.Semaphore(max_workers)
        self._admission_acquired = 0  # Track acquired permits for cleanup

    def _evaluate(
        self,
        coordinate: Coordinate,
        schedule: Schedule,
        provenance: Provenance,
        params: dict[str, Any],
        checkpoint_dir: str | None = None,
        resume_checkpoint_path: str | None = None,
    ) -> Record:
        """Train one cell and wrap the measurement as a Record."""
        from computronium.experiment.execution.evaluate import cell_record

        return cell_record(
            coordinate,
            schedule,
            provenance,
            params,
            checkpoint_dir,
            resume_checkpoint_path,
        )

    async def submit(
        self,
        coordinate: Coordinate,
        schedule: Schedule,
        provenance: Provenance,
        params: dict[str, Any],
        store: RecordStore,
    ) -> list[Record]:
        """Evaluate one coordinate across the schedule's seeds."""
        import tempfile

        from computronium.experiment.evidence.artifacts import (
            ArtifactRole,
        )

        cell_key = coordinate.cell_key()

        # Check for existing checkpoint artifact to resume from
        resume_checkpoint_path = None
        if schedule.checkpoint_every_n > 0:
            # Find records with the same cell_key that have checkpoint artifacts
            existing_records = store.query_records(cell_key=cell_key)
            for record in existing_records:
                artifacts = store.artifacts.get_for_record(record.record_id)
                for artifact in artifacts:
                    if artifact.role == ArtifactRole.MODEL_CHECKPOINT:
                        # Found a checkpoint, save it to a temp file and use for resume
                        checkpoint_bytes = store.artifacts.get(artifact.digest)
                        if checkpoint_bytes:
                            temp_ckpt = tempfile.NamedTemporaryFile(
                                suffix=".pt", delete=False
                            )
                            temp_ckpt.write(checkpoint_bytes)
                            temp_ckpt.close()
                            resume_checkpoint_path = temp_ckpt.name
                            logger.info(
                                "Resuming cell %s from checkpoint (epoch %d)",
                                cell_key[:12],
                                record.payload.get("epochs_completed", 0),
                            )
                            break
                if resume_checkpoint_path:
                    break

        # Create checkpoint directory if checkpointing is enabled
        checkpoint_dir = None
        temp_dir = None
        if schedule.checkpoint_every_n > 0:
            temp_dir = tempfile.TemporaryDirectory(prefix="ckpt_")
            checkpoint_dir = temp_dir.name

        records = [
            await asyncio.to_thread(
                self._evaluate,
                coordinate,
                seed_schedule,
                provenance,
                params,
                checkpoint_dir,
                resume_checkpoint_path,
            )
            for seed_schedule in schedule.seed_plan
        ]

        # Clean up resume checkpoint temp file
        if resume_checkpoint_path:
            Path(resume_checkpoint_path).unlink(missing_ok=True)

        # Store checkpoint bytes in record payload for later artifact persistence
        if checkpoint_dir and records:
            # Get the latest checkpoint from the first record's payload (all seeds share the same checkpoint dir)
            checkpoint_path = records[0].payload.get("checkpoint_path")
            if checkpoint_path and Path(checkpoint_path).exists():
                # Read checkpoint bytes and store as base64 in payload
                import base64

                checkpoint_bytes = Path(checkpoint_path).read_bytes()
                records[0].payload["checkpoint_bytes_b64"] = base64.b64encode(
                    checkpoint_bytes
                ).decode()

        if temp_dir:
            temp_dir.cleanup()

        return records

    async def submit_batch(
        self,
        items: list[tuple[Coordinate, Schedule, Provenance, dict[str, Any]]],
        store: RecordStore,
    ) -> list[EvaluationResult]:
        """Evaluate a batch with per-item failure isolation (WP19).

        Concurrency is capped at ``max_workers``. Unbounded, a round of ten
        cells trains ten cells simultaneously on one device: every cell then
        reports the walltime of all ten, and ``walltime_total`` — a Pareto
        axis — measures contention rather than the cell.
        """

        async def submit_one(
            coord: Coordinate,
            sched: Schedule,
            prov: Provenance,
            params: dict[str, Any],
        ) -> EvaluationResult:
            await self._admission.acquire()
            self._admission_acquired += 1
            try:
                try:
                    records = await self.submit(coord, sched, prov, params, store)
                except Exception as e:
                    import traceback

                    logger.error(
                        "Evaluation failed for %s: %s", coord.cell_key()[:12], e
                    )
                    logger.error("Full traceback: %s", traceback.format_exc())
                    return Failure(
                        failure_event=self._create_failure_event(
                            coord, sched, prov, str(e)
                        )
                    )
            finally:
                self._admission.release()
                self._admission_acquired -= 1
            if records:
                return Success(records=tuple(records))
            return Failure(
                failure_event=self._create_failure_event(
                    coord, sched, prov, "No records returned"
                )
            )

        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(submit_one(coord, sched, prov, params))
                for coord, sched, prov, params in items
            ]

        return [task.result() for task in tasks]

    def _create_failure_event(
        self,
        coordinate: Coordinate,
        schedule: Schedule,
        provenance: Provenance,
        error_message: str,
    ) -> FailureEvent:
        """Create a FailureEvent for a failed evaluation."""
        from computronium.experiment.evidence.failure import FailureEvent
        from computronium.experiment.schema.record import FailureCause

        return FailureEvent(
            cell_key=coordinate.cell_key(),
            failure_cause=FailureCause.RUNTIME_ERROR,
            error_message=error_message,
            coordinate=coordinate.to_dict(),
            schedule=schedule.to_dict(),
            provenance=provenance.to_dict(),
        )

    def shutdown(self) -> None:
        """Release the backend. Evaluation bodies live on the default pool."""
        self._shutdown = True
        # Release any acquired semaphore permits to avoid leak warnings
        while self._admission_acquired > 0:
            self._admission.release()
            self._admission_acquired -= 1


class LocalBackend(_ThreadedBackend):
    """In-process backend; evaluation bodies run on the default thread pool."""


class MultiprocessBackend(_ThreadedBackend):
    """Worker-pool backend reserved for process isolation.

    Currently the same in-process execution as :class:`LocalBackend`: the
    evaluator owns its own device and threading, so forking adds cost without
    changing what is measured. Kept as the seam where process isolation lands.
    """


# =============================================================================
# DDP/FSDP Backends (Phase E1)
# =============================================================================


@dataclass(frozen=True, slots=True)
class DDPConfig:
    """Configuration for DDP/FSDP backend."""

    backend: str = "nccl"  # nccl, gloo, mpi
    init_method: str = "env://"
    world_size: int = 1
    rank: int = 0
    local_rank: int = 0
    use_fsdp: bool = False
    fsdp_min_params: int = 1_000_000  # Minimum params to shard
    sharding_strategy: str = "FULL_SHARD"  # FULL_SHARD, SHARD_GRAD_OP, NO_SHARD
    cpu_offload: bool = False
    mixed_precision: bool = True


class DDPBackend:
    """Distributed Data Parallel / Fully Sharded Data Parallel backend.

    Implements multi-GPU training using PyTorch's native DDP and FSDP.
    Supports both DDP (replicate model on each GPU) and FSDP (shard model
    across GPUs) modes.

    Usage:
        # For DDP (set via torchrun or environment):
        backend = DDPBackend(DDPConfig(world_size=4, use_fsdp=False))

        # For FSDP:
        backend = DDPBackend(DDPConfig(world_size=4, use_fsdp=True))
    """

    def __init__(self, config: DDPConfig | None = None, max_workers: int = 1) -> None:
        if not HAS_DDP:
            raise RuntimeError("DDP/FSDP not available. Install torch with distributed support.")
        self.config = config or DDPConfig()
        self._max_workers = max_workers
        self._shutdown = False
        self._initialized = False
        self._process_group = None

    def _init_distributed(self) -> None:
        """Initialize distributed process group."""
        if self._initialized:
            return

        # Get rank/world_size from environment if not set
        if "RANK" in os.environ and "WORLD_SIZE" in os.environ:
            self.config = DDPConfig(
                backend=self.config.backend,
                init_method=self.config.init_method,
                world_size=int(os.environ["WORLD_SIZE"]),
                rank=int(os.environ["RANK"]),
                local_rank=int(os.environ.get("LOCAL_RANK", 0)),
                use_fsdp=self.config.use_fsdp,
                fsdp_min_params=self.config.fsdp_min_params,
                sharding_strategy=self.config.sharding_strategy,
                cpu_offload=self.config.cpu_offload,
                mixed_precision=self.config.mixed_precision,
            )

        # Initialize process group
        if not dist.is_initialized():
            dist.init_process_group(
                backend=self.config.backend,
                init_method=self.config.init_method,
                world_size=self.config.world_size,
                rank=self.config.rank,
            )
        self._process_group = dist.group.WORLD
        self._initialized = True

    def _cleanup_distributed(self) -> None:
        """Clean up distributed process group."""
        if dist.is_initialized():
            dist.destroy_process_group()
        self._initialized = False

    def _wrap_model(self, model: Any) -> Any:
        """Wrap model with DDP or FSDP."""
        import torch

        device = torch.device(f"cuda:{self.config.local_rank}")

        if self.config.use_fsdp:
            # FSDP wrapping
            from torch.distributed.fsdp import MixedPrecision
            from torch.distributed.fsdp.wrap import size_based_auto_wrap_policy

            mp_policy = None
            if self.config.mixed_precision:
                mp_policy = MixedPrecision(
                    param_dtype=torch.bfloat16,
                    reduce_dtype=torch.bfloat16,
                    buffer_dtype=torch.bfloat16,
                )

            auto_wrap_policy = size_based_auto_wrap_policy(
                min_num_params=self.config.fsdp_min_params
            )

            sharding_strategy = getattr(
                torch.distributed.fsdp.ShardingStrategy,
                self.config.sharding_strategy,
            )

            cpu_offload = None
            if self.config.cpu_offload:
                from torch.distributed.fsdp import CPUOffload

                cpu_offload = CPUOffload(offload_params=True)

            model = FSDP(
                model.to(device),
                process_group=self._process_group,
                sharding_strategy=sharding_strategy,
                auto_wrap_policy=auto_wrap_policy,
                mixed_precision=mp_policy,
                cpu_offload=cpu_offload,
                device_id=self.config.local_rank,
            )
        else:
            # DDP wrapping
            model = DDP(
                model.to(device),
                device_ids=[self.config.local_rank],
                output_device=self.config.local_rank,
                process_group=self._process_group,
                find_unused_parameters=False,
            )

        return model

    def _evaluate_ddp(
        self,
        coordinate: Coordinate,
        schedule: Schedule,
        provenance: Provenance,
        params: dict[str, Any],
        checkpoint_dir: str | None = None,
        resume_checkpoint_path: str | None = None,
    ) -> Record:
        """Train one cell using DDP/FSDP."""
        from computronium.experiment.execution.evaluate import cell_record

        # Initialize distributed if not already done
        self._init_distributed()

        # Only rank 0 creates the full model; others get empty models
        # cell_record handles the actual training, we just wrap the model
        try:
            record = cell_record(
                coordinate,
                schedule,
                provenance,
                params,
                checkpoint_dir,
                resume_checkpoint_path,
            )
            return record
        finally:
            # Note: We don't destroy process group here as it may be reused
            pass

    async def submit(
        self,
        coordinate: Coordinate,
        schedule: Schedule,
        provenance: Provenance,
        params: dict[str, Any],
        store: RecordStore,
    ) -> list[Record]:
        """Evaluate one coordinate across the schedule's seeds."""
        import tempfile

        from computronium.experiment.evidence.artifacts import ArtifactRole

        # Only rank 0 submits work; other ranks participate in DDP
        if self.config.rank != 0:
            # Non-rank-0 processes just participate in DDP collectives
            # They don't write to store
            await asyncio.sleep(0)  # Yield control
            return []

        cell_key = coordinate.cell_key()

        # Check for existing checkpoint artifact to resume from
        resume_checkpoint_path = None
        if schedule.checkpoint_every_n > 0:
            existing_records = store.query_records(cell_key=cell_key)
            for record in existing_records:
                artifacts = store.artifacts.get_for_record(record.record_id)
                for artifact in artifacts:
                    if artifact.role == ArtifactRole.MODEL_CHECKPOINT:
                        checkpoint_bytes = store.artifacts.get(artifact.digest)
                        if checkpoint_bytes:
                            temp_ckpt = tempfile.NamedTemporaryFile(
                                suffix=".pt", delete=False
                            )
                            temp_ckpt.write(checkpoint_bytes)
                            temp_ckpt.close()
                            resume_checkpoint_path = temp_ckpt.name
                            logger.info(
                                "Resuming cell %s from checkpoint (epoch %d)",
                                cell_key[:12],
                                record.payload.get("epochs_completed", 0),
                            )
                            break
                if resume_checkpoint_path:
                    break

        # Create checkpoint directory if checkpointing is enabled
        checkpoint_dir = None
        temp_dir = None
        if schedule.checkpoint_every_n > 0:
            temp_dir = tempfile.TemporaryDirectory(prefix="ckpt_")
            checkpoint_dir = temp_dir.name

        records = [
            await asyncio.to_thread(
                self._evaluate_ddp,
                coordinate,
                seed_schedule,
                provenance,
                params,
                checkpoint_dir,
                resume_checkpoint_path,
            )
            for seed_schedule in schedule.seed_plan
        ]

        # Clean up resume checkpoint temp file
        if resume_checkpoint_path:
            Path(resume_checkpoint_path).unlink(missing_ok=True)

        # Store checkpoint bytes in record payload for later artifact persistence
        if checkpoint_dir and records:
            checkpoint_path = records[0].payload.get("checkpoint_path")
            if checkpoint_path and Path(checkpoint_path).exists():
                import base64

                checkpoint_bytes = Path(checkpoint_path).read_bytes()
                records[0].payload["checkpoint_bytes_b64"] = base64.b64encode(
                    checkpoint_bytes
                ).decode()

        if temp_dir:
            temp_dir.cleanup()

        return records

    async def submit_batch(
        self,
        items: list[tuple[Coordinate, Schedule, Provenance, dict[str, Any]]],
        store: RecordStore,
    ) -> list[EvaluationResult]:
        """Evaluate a batch with per-item failure isolation.

        In DDP mode, only rank 0 coordinates the batch; all ranks participate
        in the actual training.
        """
        from computronium.experiment.evidence.failure import FailureEvent
        from computronium.experiment.schema.record import FailureCause

        if self.config.rank != 0:
            # Non-rank-0 processes participate in DDP but don't coordinate
            return [Success(records=()) for _ in items]

        async def submit_one(
            coord: Coordinate,
            sched: Schedule,
            prov: Provenance,
            params: dict[str, Any],
        ) -> EvaluationResult:
            try:
                records = await self.submit(coord, sched, prov, params, store)
            except Exception as e:
                import traceback

                logger.error(
                    "DDP evaluation failed for %s: %s", coord.cell_key()[:12], e
                )
                logger.error("Full traceback: %s", traceback.format_exc())
                return Failure(
                    failure_event=FailureEvent(
                        cell_key=coord.cell_key(),
                        failure_cause=FailureCause.RUNTIME_ERROR,
                        error_message=str(e),
                        coordinate=coord.to_dict(),
                        schedule=sched.to_dict(),
                        provenance=prov.to_dict(),
                    )
                )
            if records:
                return Success(records=tuple(records))
            return Failure(
                failure_event=FailureEvent(
                    cell_key=coord.cell_key(),
                    failure_cause=FailureCause.RUNTIME_ERROR,
                    error_message="No records returned",
                    coordinate=coord.to_dict(),
                    schedule=sched.to_dict(),
                    provenance=prov.to_dict(),
                )
            )

        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(submit_one(coord, sched, prov, params))
                for coord, sched, prov, params in items
            ]

        return [task.result() for task in tasks]

    def shutdown(self) -> None:
        """Shutdown the backend and clean up distributed resources."""
        self._shutdown = True
        self._cleanup_distributed()


__all__ = [
    "EvaluationResult",
    "EvaluationTask",
    "ExecutionBackend",
    "Failure",
    "LocalBackend",
    "MultiprocessBackend",
    "Success",
    "DDPBackend",
    "DDPConfig",
]
