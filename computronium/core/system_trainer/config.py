"""Configuration for SystemTrainer.

This module contains only the SystemTrainerConfig dataclass.
Protocols are in protocol.py, serialization utilities are in spec.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Protocol

if TYPE_CHECKING:
    from collections.abc import Iterator

    from torch import Tensor


@dataclass(slots=True)
class SystemTrainerConfig:
    """Configuration for SystemTrainer.

    Attributes:
        max_epochs: Number of training epochs
        batch_size: Training batch size
        val_batch_size: Validation batch size (defaults to batch_size)
        device: Target device ("auto", "cpu", "cuda", "mps")
        grad_clip: Gradient clipping norm (applied in ParameterUpdate if supported)
        track_energy: Track energy metrics during training
        track_flops: Track FLOPs during training
        track_memory: Track memory usage
        log_every_n_steps: Logging frequency
        seed: Random seed
        deterministic: Use deterministic algorithms
        resumable: Reseed the global RNG per batch via ``fold_in`` so an
        interrupted run resumes bitwise identical to an uninterrupted
        one (R11.2.24); required for ``from_snapshot`` parity claims.
        harvest_mode: End-of-run weight harvest instrument. ``None`` (default)
            trains exactly as before. ``"ema"`` keeps a streaming exponential
            moving average of geometry parameters (decay ``harvest_decay`` per
            batch) and restores the EMA weights when ``fit`` completes.
            ``"best_snapshot"`` tracks the best validation accuracy (train
            accuracy when no val data) every ``harvest_every_n`` batches and
            restores the best checkpoint at the end.
        harvest_decay: Per-batch EMA decay for ``harvest_mode="ema"``.
        harvest_every_n: Evaluation cadence (batches) for
            ``harvest_mode="best_snapshot"``.
        max_epoch_time: Per-epoch wall-clock budget in seconds; ``0`` is
            unlimited. An epoch that overruns it stops early and is flagged
            ``epoch_time_budget_stopped``, so a consumer of that epoch's
            resource metrics knows they describe a partial epoch.
        async_dataloading: Enable CUDA stream double-buffering to overlap
            host->device data transfer with forward/backward computation.
            Only effective on CUDA devices. Default: False.
        precision: Numerical precision ("fp32", "fp16", "bf16").
            Uses ``torch.autocast`` for mixed precision on CUDA.
        checkpoint_every_n: Save checkpoint every N epochs (0 = disabled).
        # Distributed training (Phase E1)
        distributed_backend: Literal["none", "ddp", "fsdp"] = "none"
        ddp_backend: str = "nccl"  # nccl, gloo, mpi
        fsdp_sharding_strategy: str = "FULL_SHARD"  # FULL_SHARD, SHARD_GRAD_OP, NO_SHARD
        fsdp_min_params: int = 1_000_000  # Minimum params to shard
        fsdp_cpu_offload: bool = False
        fsdp_mixed_precision: bool = True
    """

    max_epochs: int = 10
    batch_size: int = 64
    val_batch_size: int | None = None
    device: str = "auto"
    grad_clip: float | None = 1.0
    track_energy: bool = True
    track_flops: bool = True
    track_memory: bool = True
    log_every_n_steps: int = 10
    seed: int = 42
    deterministic: bool = False
    resumable: bool = False
    limit_train_batches: int | None = None
    limit_val_batches: int | None = None
    harvest_mode: Literal["ema", "best_snapshot"] | None = None
    harvest_decay: float = 0.99
    harvest_every_n: int = 10
    max_epoch_time: float = 0.0
    async_dataloading: bool = False
    precision: Literal["fp32", "fp16", "bf16"] = "fp32"
    checkpoint_every_n: int = 0
    # Distributed training (Phase E1)
    distributed_backend: Literal["none", "ddp", "fsdp"] = "none"
    ddp_backend: str = "nccl"
    fsdp_sharding_strategy: str = "FULL_SHARD"
    fsdp_min_params: int = 1_000_000
    fsdp_cpu_offload: bool = False
    fsdp_mixed_precision: bool = True


class _DataProvider(Protocol):
    """Protocol for data providers (DataLoader, Task, etc.)."""

    def __iter__(self) -> Iterator[tuple[Tensor, Tensor]]: ...
    def __len__(self) -> int: ...


__all__ = [
    "SystemTrainerConfig",
    "_DataProvider",
]
