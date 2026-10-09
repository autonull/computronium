"""SystemTrainer class for training 5-D composable systems."""

from __future__ import annotations

import dataclasses
from collections.abc import Callable, Mapping
from dataclasses import field
from pathlib import Path
from typing import TYPE_CHECKING

import torch

from computronium.core.logging import get_logger
from computronium.core.losses import perplexity
from computronium.core.system_trainer._resources import EpochResource, EpochResources
from computronium.core.system_trainer._resume import (
    DOMAIN_EPOCH,
    TrainerSnapshot,
    fold_in,
)

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import TracebackType
    from typing import Any

    from torch import Tensor

    from computronium.core.system_trainer.config import (
        SystemTrainerConfig,
        _DataProvider,
    )
    from computronium.ontology import System

type StepCallback = Callable[[Mapping[str, float]], None]
type CheckpointCallback = Callable[[TrainerSnapshot], None]

logger = get_logger()


def _autocast_context(device: torch.device, precision: str):
    """Return appropriate autocast context manager for the device and precision."""
    if device.type == "cuda" and precision != "fp32":
        if precision == "fp16":
            return torch.autocast("cuda", dtype=torch.float16)
        if precision == "bf16":
            return torch.autocast("cuda", dtype=torch.bfloat16)
    # Return a no-op context manager for CPU or fp32
    return torch.autocast("cpu", enabled=False)  # type: ignore[return-value]


@dataclasses.dataclass
class SystemTrainer:
    """Trainer for 5-D composable systems.

    Orchestrates the pipeline:
        Substrate.forward_op → Geometry.route → StateDynamics.settle
        → CreditAssignment.compute_pseudo_gradient → ParameterUpdate.step

    The trainer accepts a pre-composed System and data providers,
    enabling clean separation of model architecture from training loop.
    """

    system: System
    config: SystemTrainerConfig
    train_data: _DataProvider
    val_data: _DataProvider | None = None
    # Optional per-batch telemetry sink. Default no-op: a bare
    # `None` check on the hot path, never blocks or errors training.
    step_callback: StepCallback | None = None
    # Optional checkpoint persistence callback. Called with TrainerSnapshot
    # when a checkpoint is saved (every config.checkpoint_every_n epochs).
    checkpoint_callback: CheckpointCallback | None = None

    # Training state
    current_epoch: int = field(default=0, init=False)
    global_step: int = field(default=0, init=False)
    history: list[dict[str, float]] = field(default_factory=list, init=False)
    # Per-epoch cost, kept out of ``history`` on purpose: history is a claim
    # about the model and must be bit-for-bit reproducible from a seed, and
    # wall time and peak memory are not.
    epoch_resources: list[EpochResource] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self._setup_device()
        self._set_seed()
        # Move system components to device
        if hasattr(self.system.geometry, "to"):
            self.system.geometry.to(self.device)  # type: ignore[attr-defined]
        self._ema: dict[str, Tensor] = {}
        self._best_theta: dict[str, Tensor] | None = None
        self._best_score = -float("inf")
        self._resources = EpochResources(
            system=self.system,
            device=self.device,
            track_flops=self.config.track_flops,
            track_memory=self.config.track_memory,
            max_epoch_time=self.config.max_epoch_time,
        )
        # Autocast context for mixed precision
        self._autocast = _autocast_context(self.device, self.config.precision)

    def _harvest_enabled(self) -> bool:
        return self.config.harvest_mode is not None

    def _harvest_init(self) -> None:
        if self.config.harvest_mode == "ema":
            self._ema = {
                name: t.detach().clone()
                for name, t in self.system.geometry.params.items()
            }

    def _harvest_step(self) -> None:
        """Update harvest state after one training batch."""
        if not self._harvest_enabled():
            return
        if self.config.harvest_mode == "ema":
            decay = self.config.harvest_decay
            with torch.no_grad():
                for name, t in self.system.geometry.params.items():
                    self._ema[name].mul_(decay).add_(t.detach(), alpha=1 - decay)
            return
        if (
            self.global_step % self.config.harvest_every_n == 0
            and self.val_data is not None
        ):
            score = self.validate()["val_acc"]
            if score >= self._best_score:
                self._best_score = score
                self._best_theta = {
                    name: t.detach().clone()
                    for name, t in self.system.geometry.params.items()
                }

    def _harvest_snapshot_epoch(self) -> None:
        """best_snapshot fallback: epoch-end scoring when no per-batch val."""
        if self.config.harvest_mode != "best_snapshot" or self.val_data is not None:
            return
        score = self.history[-1].get("train_acc", 0.0) if self.history else 0.0
        if score >= self._best_score:
            self._best_score = score
            self._best_theta = {
                name: t.detach().clone()
                for name, t in self.system.geometry.params.items()
            }

    def _harvest_finalize(self) -> None:
        """Restore harvested weights into the geometry (in place)."""
        if not self._harvest_enabled():
            return
        theta = self._ema if self.config.harvest_mode == "ema" else self._best_theta
        if theta is None:
            logger.warning(
                "harvest_mode=%s produced no weights", self.config.harvest_mode
            )
            return
        self.system.geometry.update_params(dict(theta))
        logger.info(
            "Harvest restored (%s): score=%.4f",
            self.config.harvest_mode,
            self._best_score,
        )

    def _begin_epoch(self) -> None:
        """Seed the stream the epoch's shuffle permutation draws from."""
        if not self.config.resumable:
            return
        torch.manual_seed(
            fold_in(self.config.seed, self.current_epoch, 0, domain=DOMAIN_EPOCH)
        )

    def _load_batch(
        self, train_iter: Iterator[Any], load_stream: torch.cuda.Stream
    ) -> tuple[torch.Tensor, torch.Tensor] | None:
        """Fetch the next batch onto the device on the load stream.

        Returns ``None`` once the iterator is exhausted, which is the async
        path's break condition — the loop cannot rely on ``StopIteration``
        escaping from a prefetch.
        """
        batch = next(train_iter, None)
        if batch is None:
            return None
        with torch.cuda.stream(load_stream):
            return (
                batch[0].to(self.device, non_blocking=True),
                batch[1].to(self.device, non_blocking=True),
            )

    def _setup_device(self) -> None:
        if self.config.device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(self.config.device)
        logger.debug("SystemTrainer using device: %s", self.device)

    def _set_seed(self) -> None:
        torch.manual_seed(self.config.seed)
        if self.config.deterministic:
            import os

            os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
            torch.use_deterministic_algorithms(True)

    def train_epoch(self) -> dict[str, float]:  # ruff: ignore[complex-structure, too-many-statements, too-many-branches, too-many-locals]
        """Run one training epoch.

        When ``config.async_dataloading`` is True and CUDA is available,
        overlaps host->device data transfer with the previous batch's
        forward/backward using CUDA streams (double-buffering).
        """
        self.system.geometry.train()
        self._begin_epoch()

        epoch_loss = 0.0
        epoch_acc = 0.0
        epoch_energy = 0.0
        num_samples = 0
        budget = self.config.max_epoch_time
        self._resources.start()

        # Async data loading setup (CUDA streams double-buffering)
        use_async = (
            self.config.async_dataloading
            and self.device.type == "cuda"
            and torch.cuda.is_available()
        )

        # Create iterator from train_data (handles both iterables and iterators)
        train_iter = iter(self.train_data)

        limit = self.config.limit_train_batches
        max_batches = limit if limit is not None else 10**9

        if use_async:
            compute_stream = torch.cuda.Stream()
            load_stream = torch.cuda.Stream()
            pending = self._load_batch(train_iter, load_stream)

        for batch_idx in range(max_batches):
            if use_async:
                if pending is None:
                    break
                current = torch.cuda.current_stream()
                current.wait_stream(load_stream)
                current.wait_stream(compute_stream)
                x, y = pending
                x.record_stream(compute_stream)
                y.record_stream(compute_stream)
                pending = self._load_batch(train_iter, load_stream)
            else:
                try:
                    x, y = next(train_iter)
                except StopIteration:
                    break

            if self.config.resumable:
                torch.manual_seed(
                    fold_in(self.config.seed, self.current_epoch, batch_idx)
                )

            # For async path, x/y are already on device from load stream
            if not use_async:
                x = x.to(self.device)  # ruff: ignore[redefined-loop-name]
                y = y.to(self.device)  # ruff: ignore[redefined-loop-name]

            # Canonical flat input: systems compose against a flat
            # input_dim (e.g. vision (B, C, H, W) -> (B, C*H*W)); the
            # 4-D raw tensor crashed credit/view reshapes downstream.
            if x.dim() > 2:
                x = x.reshape(x.size(0), -1)  # ruff: ignore[redefined-loop-name]

            # Run train_step with mixed precision
            def _train_step():
                with self._autocast:
                    return self.system.train_step(x, y)

            # Run train_step on compute stream for async path
            if use_async:
                with torch.cuda.stream(compute_stream):
                    metrics = _train_step()
                # Sync to get metrics for logging/accumulation
                torch.cuda.current_stream().wait_stream(compute_stream)
            else:
                metrics = _train_step()

            batch = x.size(0)
            self._resources.note_step(batch)
            epoch_loss += metrics.get("loss", 0.0) * batch
            epoch_acc += (
                metrics.get("free_accuracy", metrics.get("nudged_fit_accuracy", 0.0))
                * batch
            )
            epoch_energy += metrics.get("energy", 0.0) * batch
            num_samples += batch
            self.global_step += 1
            self._harvest_step()

            if self.step_callback is not None:
                self.step_callback(metrics)

            if self.global_step % self.config.log_every_n_steps == 0:
                logger.info(
                    "Step %d: loss=%.4f, free_acc=%.4f, energy=%.4f",
                    self.global_step,
                    metrics.get("loss", 0.0),
                    metrics.get(
                        "free_accuracy", metrics.get("nudged_fit_accuracy", 0.0)
                    ),
                    metrics.get("energy", 0.0),
                )
            if budget and self._resources.over_budget:
                logger.info(
                    "Epoch %d stopped after batch %d: max_epoch_time=%.1fs",
                    self.current_epoch,
                    batch_idx,
                    budget,
                )
                break

        # Final sync for async path
        if use_async:
            torch.cuda.current_stream().wait_stream(compute_stream)

        self._resources.stop()
        denom = max(num_samples, 1)
        avg_loss = epoch_loss / denom
        avg_acc = epoch_acc / denom
        avg_energy = epoch_energy / denom

        self.epoch_resources.append(self._resources.record(self.current_epoch))

        epoch_record: dict[str, float] = {
            "epoch": self.current_epoch,
            "train_loss": avg_loss,
            "train_acc": avg_acc,
            "train_energy": avg_energy,
            "global_step": self.global_step,
        }

        if self.val_data is not None:
            epoch_record.update(self.validate())

        self.history.append(epoch_record)
        self._harvest_snapshot_epoch()
        self.current_epoch += 1

        logger.info(
            "Epoch %d: train_loss=%.4f, train_acc=%.4f, train_energy=%.4f",
            self.current_epoch,
            avg_loss,
            avg_acc,
            avg_energy,
        )

        # Checkpoint if configured
        if (
            self.config.checkpoint_every_n > 0
            and self.current_epoch % self.config.checkpoint_every_n == 0
        ):
            self.save_checkpoint()
            if self.checkpoint_callback is not None:
                self.checkpoint_callback(self.snapshot())

        return epoch_record

    def validate(self) -> dict[str, float]:
        """Run validation epoch."""
        if self.val_data is None:
            return {}

        self.system.geometry.eval()
        val_ce_sum = 0.0
        val_correct = 0
        num_samples = 0

        with torch.no_grad(), self._autocast:
            for x, y in self.val_data:
                x = x.to(self.device)  # ruff: ignore[redefined-loop-name]
                y = y.to(self.device)  # ruff: ignore[redefined-loop-name]
                if x.dim() > 2:
                    x = x.reshape(x.size(0), -1)  # ruff: ignore[redefined-loop-name]

                logits = self.system.forward(x)
                ce = torch.nn.functional.cross_entropy(logits, y, reduction="sum")
                val_ce_sum += ce.item()
                val_correct += (logits.argmax(-1) == y).sum().item()
                num_samples += y.size(0)

        denom = max(num_samples, 1)
        val_loss = val_ce_sum / denom
        return {
            "val_loss": val_loss,
            "val_acc": val_correct / denom,
            "val_ppl": perplexity(val_loss),
        }

    def save_checkpoint(self, path: str | Path | None = None) -> Path:
        """Save a training checkpoint to disk.

        Args:
            path: Optional path to save checkpoint. If None, uses a default
                path based on the store location.

        Returns:
            Path to the saved checkpoint file.
        """
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
        logger.info("Checkpoint saved to %s", path)
        return Path(path)

    @classmethod
    def from_checkpoint(
        cls,
        checkpoint_path: str | Path,
        *,
        system: System,
        train_data: _DataProvider,
        val_data: _DataProvider | None = None,
    ) -> SystemTrainer:
        """Load a trainer from a checkpoint file.

        Args:
            checkpoint_path: Path to the checkpoint file.
            system: The system to load state into.
            train_data: Training data provider.
            val_data: Optional validation data provider.

        Returns:
            A new SystemTrainer instance restored from the checkpoint.
        """
        checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
        config = checkpoint["config"]
        trainer = cls(
            system=system, config=config, train_data=train_data, val_data=val_data
        )
        snapshot = TrainerSnapshot(
            epoch=checkpoint["epoch"],
            global_step=checkpoint["global_step"],
            history=checkpoint["history"],
            theta=checkpoint["theta"],
            opt_state=checkpoint["opt_state"],
            credit_state=checkpoint["credit_state"],
        )
        trainer._restore(snapshot)
        logger.info("Restored from checkpoint: %s", checkpoint_path)
        return trainer

    def snapshot(self) -> TrainerSnapshot:
        """Capture the full resume state (theta, optimizer state, counters)."""
        theta = {
            name: t.detach().clone() for name, t in self.system.geometry.params.items()
        }
        get_state = getattr(self.system.update, "get_state", None)
        buffers: dict[str, dict[str, Tensor]] = (
            get_state() if get_state is not None else {}
        )
        credit_state_fn = getattr(self.system.credit, "get_state", None)
        credit_state: dict[str, dict[str, Tensor]] = (
            credit_state_fn() if credit_state_fn is not None else {}
        )
        return TrainerSnapshot(
            epoch=self.current_epoch,
            global_step=self.global_step,
            history=tuple(self.history),
            theta=theta,
            opt_state=buffers,
            credit_state=credit_state,
        )

    @classmethod
    def from_snapshot(
        cls,
        *,
        system: System,
        config: SystemTrainerConfig,
        train_data: _DataProvider,
        snapshot: TrainerSnapshot,
        val_data: _DataProvider | None = None,
    ) -> SystemTrainer:
        """Build a trainer that resumes ``snapshot`` at ``snapshot.epoch``.

        With ``config.resumable`` enabled and the same ``seed`` / data
        stream, continuing training is bitwise identical to never having
        stopped (R11.2.24). ``max_epochs`` counts total epochs.
        """
        trainer = cls(
            system=system, config=config, train_data=train_data, val_data=val_data
        )
        trainer._restore(snapshot)
        return trainer

    def _restore(self, snap: TrainerSnapshot) -> None:
        self.system.geometry.update_params({
            name: t.to(self.device) for name, t in snap.theta.items()
        })
        if snap.opt_state:
            load = getattr(self.system.update, "load_state", None)
            if load is None:
                raise TypeError(
                    f"{type(self.system.update).__name__} carries no "
                    "optimizer state to restore into"
                )
            load(snap.opt_state)
        if snap.credit_state:
            credit_load = getattr(self.system.credit, "load_state", None)
            if credit_load is None:
                msg = (
                    f"{type(self.system.credit).__name__} carries no "
                    "credit state to restore into"
                )
                raise TypeError(msg)
            credit_load(snap.credit_state)
        self.current_epoch = snap.epoch
        self.global_step = snap.global_step
        self.history = list(snap.history)
        logger.info(
            "Resumed from snapshot: epoch %d, global_step %d",
            snap.epoch,
            snap.global_step,
        )

    def fit(self) -> list[dict[str, float]]:
        """Run the training loop to ``config.max_epochs`` total epochs."""
        logger.debug(
            "Starting training for %d epochs (from epoch %d)",
            self.config.max_epochs,
            self.current_epoch,
        )

        self._harvest_init()
        while self.current_epoch < self.config.max_epochs:
            self.train_epoch()

        self._harvest_finalize()
        logger.debug("Training complete")
        return self.history

    def close(self) -> None:
        """Clean up resources (e.g., move model to CPU, clear CUDA cache)."""
        if hasattr(self, "system") and self.system is not None:  # ruff: ignore[collapsible-if]
            if hasattr(self.system.geometry, "cpu"):
                self.system.geometry.cpu()
        if hasattr(self, "device") and self.device.type == "cuda":
            torch.cuda.empty_cache()
        logger.debug("SystemTrainer resources cleaned up")

    def __enter__(self) -> SystemTrainer:  # ruff: ignore[non-self-return-type]
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        self.close()
        return False


__all__ = ["SystemTrainer"]
