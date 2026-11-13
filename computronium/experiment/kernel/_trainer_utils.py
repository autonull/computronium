"""Trainer configuration and checkpointing utilities extracted from evaluate.py."""

from __future__ import annotations

import tempfile
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Any

import torch

from computronium.core.system_trainer import SystemTrainer, SystemTrainerConfig
from computronium.core.system_trainer._resume import TrainerSnapshot

if TYPE_CHECKING:
    from computronium.experiment.schema.coordinate import Schedule


def _resolve_device(device: str) -> str:
    """Resolve 'auto' to 'cuda' if available, otherwise 'cpu'."""
    if device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return device


def _create_trainer_config(
    schedule: Schedule,
    resolved_device: str,
    params: Mapping[str, Any] | None,
) -> SystemTrainerConfig:
    """Create SystemTrainerConfig from schedule and params."""
    limit = schedule.batch_limit or None

    # Extract deadline check callback from params (for WS2.7 deadline enforcement)
    deadline_check = params.get("deadline_check") if params else None
    deadline_check_every_n_steps = (
        params.get("deadline_check_every_n_steps", 0) if params else 0
    )
    log_every_n_steps = params.get("log_every_n_steps", 0) if params else 0

    return SystemTrainerConfig(
        max_epochs=schedule.epochs,
        device=resolved_device,
        seed=schedule.seed,
        limit_train_batches=limit,
        limit_val_batches=limit,
        track_flops=True,
        track_memory=True,
        log_every_n_steps=int(log_every_n_steps),
        deterministic=schedule.deterministic,
        precision=schedule.precision if hasattr(schedule, "precision") else "fp32",
        checkpoint_every_n=schedule.checkpoint_every_n,
        # Early stopping (WS2.4)
        early_stopping_patience=getattr(schedule, "early_stopping_patience", 0),
        # Deadline enforcement (WS2.7)
        deadline_check=deadline_check,
        deadline_check_every_n_steps=deadline_check_every_n_steps,
        # Distributed training (Phase E1)
        distributed_backend=schedule.distributed_backend,
        ddp_backend=schedule.ddp_backend,
        fsdp_sharding_strategy=schedule.fsdp_sharding_strategy,
        fsdp_min_params=schedule.fsdp_min_params,
        fsdp_cpu_offload=schedule.fsdp_cpu_offload,
        fsdp_mixed_precision=schedule.fsdp_mixed_precision,
    )


def _setup_checkpointing(
    schedule: Schedule,
    checkpoint_dir: str | None,
    config: SystemTrainerConfig,
) -> tuple[tempfile.TemporaryDirectory | None, list[str | None], Callable | None]:
    """Set up checkpoint directory and callback if enabled.

    Returns:
        Tuple of (temp_dir, checkpoint_path_ref, checkpoint_callback).
        temp_dir is a TemporaryDirectory that must be cleaned up.
        checkpoint_path_ref is a mutable reference (list) to capture the path.
        checkpoint_callback is the callback function or None.
    """
    temp_dir: tempfile.TemporaryDirectory | None = None
    checkpoint_path_ref: list[str | None] = [None]

    if schedule.checkpoint_every_n <= 0:
        return None, checkpoint_path_ref, None

    if checkpoint_dir is not None:
        ckpt_dir = Path(checkpoint_dir)
        ckpt_dir.mkdir(parents=True, exist_ok=True)
    else:
        temp_dir = tempfile.TemporaryDirectory(prefix="ckpt_")
        ckpt_dir = Path(temp_dir.name)

    def _checkpoint_callback(snapshot: TrainerSnapshot) -> None:
        ckpt_file = ckpt_dir / f"checkpoint_epoch_{snapshot.epoch}.pt"
        torch.save(
            {
                "epoch": snapshot.epoch,
                "global_step": snapshot.global_step,
                "history": snapshot.history,
                "theta": snapshot.theta,
                "opt_state": snapshot.opt_state,
                "credit_state": snapshot.credit_state,
                "config": config,
            },
            ckpt_file,
        )
        checkpoint_path_ref[0] = str(ckpt_file)

    return temp_dir, checkpoint_path_ref, _checkpoint_callback


def _create_trainer(
    trainer_class: type[SystemTrainer],
    cell: Any,
    task: Any,
    config: SystemTrainerConfig,
    resume_checkpoint_path: str | None,
    checkpoint_callback: Callable | None,
) -> SystemTrainer:
    """Create trainer, optionally resuming from checkpoint."""
    from pathlib import Path

    # Specialized trainers (RL, Graph) use the task directly as train_data
    # because they have custom training loops that don't use standard data providers.
    from computronium.core.system_trainer import GraphSystemTrainer, RLSystemTrainer

    if trainer_class in {RLSystemTrainer, GraphSystemTrainer}:
        train_data = task
        val_data = task  # Use same task for validation (different masks/splits)
    else:
        batch_size = config.limit_train_batches or 32  # fallback
        train_data = _create_data_provider(
            task, "train", batch_size, config.limit_train_batches
        )
        val_data = _create_data_provider(
            task, "val", batch_size, config.limit_val_batches
        )

    if resume_checkpoint_path and Path(resume_checkpoint_path).exists():
        # Resume from checkpoint
        trainer = trainer_class.from_checkpoint(
            resume_checkpoint_path,
            system=cell.system,
            train_data=train_data,
            val_data=val_data,
            max_epochs=config.max_epochs,
        )
        if checkpoint_callback is not None:
            trainer.checkpoint_callback = checkpoint_callback
    else:
        trainer = trainer_class(
            cell.system,
            config,
            train_data,
            val_data=val_data,
            checkpoint_callback=checkpoint_callback,
        )
    return trainer


def _run_training(
    trainer_class: type[SystemTrainer],
    cell: Any,
    task: Any,
    config: SystemTrainerConfig,
    resume_checkpoint_path: str | None,
    checkpoint_callback: Callable | None,
) -> tuple[SystemTrainer, list[dict[str, float]]]:
    """Run training, optionally resuming from checkpoint.

    Returns:
        Tuple of (trainer, history).
    """
    from computronium.experiment.kernel.evaluate import EvaluationError

    trainer = _create_trainer(
        trainer_class, cell, task, config, resume_checkpoint_path, checkpoint_callback
    )
    try:
        history = trainer.fit()
    except EvaluationError:
        raise
    except Exception as exc:
        msg = f"Training failed: {exc}"
        raise EvaluationError("runtime_error", msg) from exc

    return trainer, history


def _collect_trainer_metrics(trainer: SystemTrainer) -> dict[str, float]:
    """Extract resource metrics from trainer's last epoch."""
    metrics: dict[str, float] = {}
    if not trainer.epoch_resources:
        return metrics

    last_epoch = trainer.epoch_resources[-1]
    if last_epoch.forward_flops is not None and last_epoch.steps > 0:
        flops_per_step = last_epoch.forward_flops / last_epoch.steps
        metrics["flops"] = float(flops_per_step)
        metrics["macs_per_step"] = float(flops_per_step / 2)  # 1 MAC = 2 FLOPs
    if last_epoch.peak_memory_mb is not None:
        metrics["memory_usage"] = last_epoch.peak_memory_mb
    if last_epoch.steps > 0:
        metrics["latency_ms"] = (last_epoch.epoch_time_s / last_epoch.steps) * 1000.0
    if last_epoch.energy_joules is not None and last_epoch.steps > 0:
        metrics["energy_per_step"] = last_epoch.energy_joules / last_epoch.steps
    return metrics


class _Reiterable:
    """A data provider that starts a fresh pass on every iteration.

    The trainer iterates the provider once per epoch. A single-pass
    iterator (``islice`` over a loader, a bare generator) leaves every
    epoch after the first with no batches at all — the cell then reports
    its last, empty epoch's zeroed metrics as its result.
    """

    def __init__(self, factory: Callable[[], Any]) -> None:
        self._factory = factory

    def __iter__(self) -> Any:
        return self._factory()


def _bounded_batches(source: Any, limit: int) -> Any:
    """At most ``limit`` batches per pass over a data provider."""
    from itertools import islice

    return _Reiterable(lambda: islice(iter(source), limit))


def _val_batches(task: Any, limit: int | None) -> Any | None:
    """The task's validation split, bounded, or ``None`` when it declares none."""
    from computronium.domains.base import TaskSplit

    try:
        loader = task.get_dataloader(TaskSplit.VAL)
        if loader is not None:
            return _bounded_batches(loader, limit) if limit else loader
    except (LookupError, ValueError, NotImplementedError, AttributeError) as exc:
        from computronium.core.logging import get_logger

        logger = get_logger(__name__)
        logger.info("task %s declares no validation DataLoader: %s", task.name, exc)

    # Try get_batch for tasks without DataLoaders
    try:
        batch_size = 32  # default, will be overridden by _create_trainer
        return _create_data_provider(task, "val", batch_size, limit)
    except NotImplementedError, AttributeError:
        return None


def _sample_inputs(task: Any, device: str) -> tuple[torch.Tensor | None, int]:
    """One flattened training batch, on ``device``, and its sample count.

    Returns ``(None, n)`` for a PyG batch: its node matrix is not a batch-free
    input — the readout is pooled and aggregation needs that batch's edges — so
    a caller that only has the rows must skip the free-phase probes instead of
    running node-mode geometry over a foreign edge index.
    """
    try:
        batch = next(iter(task.get_dataloader("train")))
    except TypeError, StopIteration:
        # Task doesn't use DataLoader (e.g., graph, RL); use get_batch
        batch = task.get_batch("train", batch_size=32)

    # Handle different batch structures. The trainer's provider contract is an
    # ``(x, y)`` pair, and a ``DataLoader`` over a pair dataset collates it to
    # a two-element list — not a tuple. Stacking that list turned one
    # sequence batch into ``[2, B, T]`` and the settle probe then compared
    # ``B*T`` logits against a ``T``-wide positional table.
    if isinstance(batch, list | tuple):
        items = list(batch)
        if len(items) == 2 or isinstance(batch, tuple):
            sample_x = items[0]
        elif items and all(b.shape == items[0].shape for b in items):
            sample_x = torch.stack(items)
        else:
            sample_x = items[0]
    else:
        sample_x = batch

    # Handle graph tasks: sample_x is a PyG Data/Batch object
    if hasattr(sample_x, "x") and hasattr(sample_x, "edge_index"):
        return None, int(getattr(sample_x, "num_graphs", 1))
    flat = sample_x.to(device).reshape(sample_x.shape[0], -1)
    return flat, flat.shape[0]


def _create_data_provider(task: Any, split: str, batch_size: int, limit: int | None):
    """Create an iterable data provider for a task.

    Handles both standard DataLoader tasks and get_batch-based tasks
    (graph, RL, etc.). The provider is re-iterable: the trainer walks
    it once per epoch.
    """
    # Try DataLoader first
    try:
        loader = task.get_dataloader(split)
        if loader is not None:
            return _bounded_batches(loader, limit) if limit else loader
    except TypeError, StopIteration, NotImplementedError, AttributeError:
        pass

    # Fall back to get_batch for tasks without DataLoaders
    def batch_generator():
        batches_yielded = 0
        max_batches = limit if limit is not None else 10**9
        while batches_yielded < max_batches:
            try:
                x, y = task.get_batch(split, batch_size)
                # For graph tasks: get_batch returns (Data, labels); extract node features
                if hasattr(x, "x") and hasattr(x, "edge_index"):
                    # PyG Data object: use node features as input
                    x = x.x
                yield x, y
                batches_yielded += 1
            except StopIteration, NotImplementedError:
                break

    return _Reiterable(batch_generator)
