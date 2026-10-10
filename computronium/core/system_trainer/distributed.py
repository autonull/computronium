"""DistributedSystemTrainer: Native PyTorch DDP/FSDP support.

Extends SystemTrainer with distributed training capabilities using
PyTorch's native DistributedDataParallel and FullyShardedDataParallel.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel
from torch.utils.data import DataLoader
from torch.utils.data.distributed import DistributedSampler

from computronium.core.logging import get_logger
from computronium.core.system_trainer.trainer import SystemTrainer

if TYPE_CHECKING:
    from torch import Tensor

    from computronium.core.system_trainer._resume import TrainerSnapshot
    from computronium.core.system_trainer.config import SystemTrainerConfig
    from computronium.ontology import System

# Type for DDP or FSDP wrapped model
DDPModel = DistributedDataParallel | Any

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class DistributedState:
    """Runtime state for distributed training."""

    rank: int
    world_size: int
    local_rank: int
    is_distributed: bool
    process_group: Any | None = None


class DistributedSystemTrainer(SystemTrainer):
    """SystemTrainer with native DDP/FSDP support.

    Supports both DistributedDataParallel (replicate model on each GPU)
    and FullyShardedDataParallel (shard model across GPUs) modes.

    Usage:
        # Launch with torchrun:
        # torchrun --nproc_per_node=4 train.py

        config = SystemTrainerConfig(
            distributed_backend="ddp",  # or "fsdp"
            max_epochs=10,
            device="cuda",
        )
        trainer = DistributedSystemTrainer(
            system=system,
            config=config,
            train_data=train_loader,
            val_data=val_loader,
        )
        history = trainer.fit()
    """

    system: System
    config: SystemTrainerConfig
    train_data: Any
    val_data: Any | None = None

    # Distributed state
    _dist_state: DistributedState | None = None
    _ddp_model: DDPModel | None = None
    _original_model: Any = None

    def __post_init__(self) -> None:
        """Initialize distributed training if configured."""
        self._setup_distributed()
        super().__post_init__()

    def _setup_distributed(self) -> None:
        """Initialize distributed process group and wrap model."""
        if self.config.distributed_backend == "none":
            self._dist_state = DistributedState(
                rank=0,
                world_size=1,
                local_rank=0,
                is_distributed=False,
            )
            return

        # Get rank/world_size from environment (set by torchrun)
        rank = int(os.environ.get("RANK", "0"))
        world_size = int(os.environ.get("WORLD_SIZE", "1"))
        local_rank = int(os.environ.get("LOCAL_RANK", "0"))

        if not dist.is_initialized():  # type: ignore[attr-defined]
            dist.init_process_group(  # type: ignore[attr-defined]
                backend=self.config.ddp_backend,
                init_method="env://",
                world_size=world_size,
                rank=rank,
            )

        self._dist_state = DistributedState(
            rank=rank,
            world_size=world_size,
            local_rank=local_rank,
            is_distributed=True,
            process_group=dist.group.WORLD,  # type: ignore[attr-defined]
        )

        # Set device for this rank
        self.device = torch.device(f"cuda:{local_rank}")
        torch.cuda.set_device(self.device)

        logger.info(
            "Distributed training initialized: rank=%d, world_size=%d, local_rank=%d",
            rank,
            world_size,
            local_rank,
        )

        # Wrap model with DDP/FSDP
        self._wrap_model()

        # Wrap data loaders with distributed samplers
        self._wrap_data_loaders()

    def _wrap_model(self) -> None:
        """Wrap the system's geometry with DDP or FSDP."""
        if not self._dist_state or not self._dist_state.is_distributed:
            return

        # Move geometry to device first
        self.system.geometry.to(self.device)

        if self.config.distributed_backend == "ddp":
            self._wrap_ddp()
        elif self.config.distributed_backend == "fsdp":
            self._wrap_fsdp()

    def _wrap_ddp(self) -> None:
        """Wrap model with DistributedDataParallel."""
        # Store original model for checkpointing
        self._original_model = self.system.geometry

        # DDP requires the model to be on the correct device
        self._ddp_model = DistributedDataParallel(
            self.system.geometry,
            device_ids=[self._dist_state.local_rank],  # type: ignore[union-attr]
            output_device=self._dist_state.local_rank,  # type: ignore[union-attr]
            process_group=self._dist_state.process_group,  # type: ignore[union-attr]
            find_unused_parameters=False,
        )

        # Replace the geometry with DDP-wrapped version
        # We need to create a proxy that forwards to the DDP model
        self.system.geometry = _DDPGeometryProxy(self._ddp_model, self._original_model)

        logger.info("Model wrapped with DDP")

    def _wrap_fsdp(self) -> None:
        """Wrap model with FullyShardedDataParallel."""
        from torch.distributed.fsdp import FullyShardedDataParallel, MixedPrecision
        from torch.distributed.fsdp.wrap import size_based_auto_wrap_policy

        # Store original model
        self._original_model = self.system.geometry

        # Mixed precision policy
        mp_policy = None
        if self.config.fsdp_mixed_precision:
            mp_policy = MixedPrecision(
                param_dtype=torch.bfloat16,
                reduce_dtype=torch.bfloat16,
                buffer_dtype=torch.bfloat16,
            )

        # Auto wrap policy
        auto_wrap_policy = size_based_auto_wrap_policy(  # type: ignore[call-arg]
            min_num_params=self.config.fsdp_min_params,
        )

        # Sharding strategy
        sharding_strategy = getattr(
            torch.distributed.fsdp.ShardingStrategy,  # type: ignore[attr-defined]
            self.config.fsdp_sharding_strategy,
        )

        cpu_offload = None
        if self.config.fsdp_cpu_offload:
            from torch.distributed.fsdp import CPUOffload

            cpu_offload = CPUOffload(offload_params=True)

        self._ddp_model = FullyShardedDataParallel(  # type: ignore[assignment,call-arg]
            self.system.geometry,
            process_group=self._dist_state.process_group,  # type: ignore[union-attr]
            sharding_strategy=sharding_strategy,
            auto_wrap_policy=auto_wrap_policy,
            mixed_precision=mp_policy,
            cpu_offload=cpu_offload,
            device_id=self._dist_state.local_rank,  # type: ignore[union-attr]
        )

        # Replace geometry with FSDP-wrapped version
        self.system.geometry = _DDPGeometryProxy(self._ddp_model, self._original_model)

        logger.info("Model wrapped with FSDP")

    def _wrap_data_loaders(self) -> None:
        """Wrap data loaders with DistributedSampler."""
        if not self._dist_state or not self._dist_state.is_distributed:
            return

        # Wrap training data loader
        if isinstance(self.train_data, DataLoader):
            sampler = DistributedSampler(
                self.train_data.dataset,
                num_replicas=self._dist_state.world_size,
                rank=self._dist_state.rank,
                shuffle=True,
            )
            self.train_data = DataLoader(
                self.train_data.dataset,
                batch_size=self.config.batch_size,
                sampler=sampler,
                num_workers=self.train_data.num_workers,
                pin_memory=self.train_data.pin_memory,
                drop_last=self.train_data.drop_last,
            )

        # Wrap validation data loader
        if self.val_data is not None and isinstance(self.val_data, DataLoader):
            sampler = DistributedSampler(
                self.val_data.dataset,
                num_replicas=self._dist_state.world_size,
                rank=self._dist_state.rank,
                shuffle=False,
            )
            self.val_data = DataLoader(
                self.val_data.dataset,
                batch_size=self.config.val_batch_size or self.config.batch_size,
                sampler=sampler,
                num_workers=self.val_data.num_workers,
                pin_memory=self.val_data.pin_memory,
                drop_last=False,
            )

    def train_epoch(self) -> dict[str, float]:
        """Run one distributed training epoch."""
        if not self._dist_state or not self._dist_state.is_distributed:
            return super().train_epoch()

        # Set epoch for distributed sampler
        if isinstance(self.train_data, DataLoader) and isinstance(
            self.train_data.sampler, DistributedSampler
        ):
            self.train_data.sampler.set_epoch(self.current_epoch)

        return super().train_epoch()

    def validate(self) -> dict[str, float]:
        """Run validation epoch (only on rank 0 for logging)."""
        if not self._dist_state or not self._dist_state.is_distributed:
            return super().validate()

        # Only rank 0 computes validation metrics
        if self._dist_state.rank != 0:
            return {}

        return super().validate()

    def save_checkpoint(self, path: str | Path | None = None) -> Path:
        """Save checkpoint (only rank 0 saves)."""
        if self._dist_state and self._dist_state.is_distributed:
            if self._dist_state.rank != 0:
                return Path()  # No-op for non-rank-0

            # Save the original (unwrapped) model state
            if path is None:
                path = Path(f"checkpoint_epoch_{self.current_epoch}.pt")

            snapshot = self.snapshot()
            torch.save(
                {
                    "epoch": snapshot.epoch,
                    "global_step": snapshot.global_step,
                    "history": snapshot.history,
                    "theta": snapshot.theta,
                    "opt_state": snapshot.opt_state,
                    "credit_state": snapshot.credit_state,
                    "config": self.config,
                },
                path,
            )
            logger.info("Checkpoint saved to %s (rank 0)", path)
            return Path(path)

        return super().save_checkpoint(path)

    def snapshot(self) -> TrainerSnapshot:
        """Capture snapshot with original model state."""
        if self._original_model is not None:
            # Use original model parameters for checkpointing
            theta = {
                name: t.detach().clone()
                for name, t in self._original_model.params.items()
            }
        else:
            theta = {
                name: t.detach().clone()
                for name, t in self.system.geometry.params.items()
            }

        get_state = getattr(self.system.update, "get_state", None)
        buffers: dict[str, dict[str, Tensor]] = (
            get_state() if get_state is not None else {}
        )
        credit_state_fn = getattr(self.system.credit, "get_state", None)
        credit_state: dict[str, dict[str, Tensor]] = (
            credit_state_fn() if credit_state_fn is not None else {}
        )

        from computronium.core.system_trainer._resume import TrainerSnapshot

        return TrainerSnapshot(
            epoch=self.current_epoch,
            global_step=self.global_step,
            history=tuple(self.history),
            theta=theta,
            opt_state=buffers,
            credit_state=credit_state,
        )

    def close(self) -> None:
        """Clean up distributed resources."""
        super().close()
        if self._dist_state and self._dist_state.is_distributed:
            if dist.is_initialized():  # type: ignore[attr-defined]
                dist.destroy_process_group()  # type: ignore[attr-defined]
            logger.info("Distributed process group destroyed")


class _DDPGeometryProxy:
    """Proxy that forwards geometry operations to DDP/FSDP-wrapped model."""

    def __init__(self, ddp_model: DDPModel, original_model: Any):
        self._ddp_model = ddp_model
        self._original_model = original_model

    def __getattr__(self, name: str) -> Any:
        # Forward to DDP model for forward/train_step
        if name in {
            "forward",
            "train_step",
            "parameters",
            "named_parameters",
            "to",
            "train",
            "eval",
        }:
            return getattr(self._ddp_model, name)
        # Forward to original model for params, update_params, etc.
        return getattr(self._original_model, name)

    @property
    def params(self) -> dict[str, torch.Tensor]:
        return self._original_model.params

    def update_params(self, new_params: dict[str, torch.Tensor]) -> None:
        self._original_model.update_params(new_params)

    def state_dict(self) -> dict[str, torch.Tensor]:
        return self._original_model.state_dict()

    def load_state_dict(self, state_dict: dict[str, torch.Tensor]) -> None:
        self._original_model.load_state_dict(state_dict)


__all__ = [
    "DistributedState",
    "DistributedSystemTrainer",
]
