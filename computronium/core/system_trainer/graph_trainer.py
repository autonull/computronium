"""GraphSystemTrainer for graph tasks with 5-D composable systems.

Handles both:
- Node classification (Planetoid-style): single graph with train/val/test masks
- Graph classification (TUDataset-style): batched graphs from DataLoader
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable, Mapping
from dataclasses import field
from pathlib import Path
from typing import TYPE_CHECKING, Any

import torch
from torch import optim

from computronium.core.logging import get_logger
from computronium.core.system_trainer._early_stopping import (
    EarlyStoppingConfig,
    EarlyStoppingState,
    check_early_stopping,
)
from computronium.core.system_trainer._progress import log_epoch
from computronium.core.system_trainer._resume import (
    DOMAIN_EPOCH,
    TrainerSnapshot,
    fold_in,
)
from computronium.core.system_trainer.config import SystemTrainerConfig

if TYPE_CHECKING:
    from types import TracebackType

    from torch import Tensor

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
    return torch.autocast("cpu", enabled=False)  # type: ignore[return-value]


@dataclasses.dataclass
class GraphSystemTrainer:
    """Trainer for graph tasks with 5-D composable systems.

    Supports two modes:
    1. Node classification: single graph with train/val/test masks (Planetoid)
    2. Graph classification: batched graphs from DataLoader (TUDataset)
    """

    system: System
    config: SystemTrainerConfig
    train_data: Any  # GraphTask or GraphClassificationTask instance
    val_data: Any | None = None
    step_callback: StepCallback | None = None
    checkpoint_callback: CheckpointCallback | None = None

    # Training state
    current_epoch: int = field(default=0, init=False)
    global_step: int = field(default=0, init=False)
    history: list[dict[str, float]] = field(default_factory=list, init=False)
    epoch_resources: list[Any] = field(default_factory=list, init=False)

    # Internal: set in __post_init__
    _data: Any = field(default=None, init=False, repr=False)
    _is_graph_classification: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        self._setup_device()
        self._set_seed()

        # Move system to device
        mover = getattr(self.system, "to", None)
        if callable(mover):
            mover(self.device)
        elif hasattr(self.system.geometry, "to"):
            self.system.geometry.to(self.device)

        # Get graph data from train_data
        if not self.train_data._setup_done:
            self.train_data.setup()

        # Detect task type: node classification (has _data) vs graph classification (has _train_loader only)
        if hasattr(self.train_data, "_data") and self.train_data._data is not None:
            # Node classification mode (Planetoid-style)
            self._is_graph_classification = False
            self._data = self.train_data._data.to(self.device)
        else:
            # Graph classification mode (TUDataset-style) - uses DataLoader
            self._is_graph_classification = True
            self._data = None  # Not used in this mode

        # Optimizer
        lr = self.config.extra.get("lr", 1e-2) if self.config.extra else 1e-2
        self.optimizer = optim.Adam(self.system.geometry.params.values(), lr=lr)

        self._ema: dict[str, Tensor] = {}
        self._best_theta: dict[str, Tensor] | None = None
        self._best_score = -float("inf")
        self._autocast = _autocast_context(self.device, self.config.precision)

        logger.debug("GraphSystemTrainer mode: %s", "graph_classification" if self._is_graph_classification else "node_classification")

    def _setup_device(self) -> None:
        if self.config.device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(self.config.device)
        logger.debug("GraphSystemTrainer using device: %s", self.device)

    def _set_seed(self) -> None:
        torch.manual_seed(self.config.seed)
        if self.config.deterministic:
            import os

            os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
            torch.use_deterministic_algorithms(True)

    def _begin_epoch(self) -> None:
        """Seed the stream for this epoch's shuffle permutation."""
        if not self.config.resumable:
            return
        torch.manual_seed(
            fold_in(self.config.seed, self.current_epoch, 0, domain=DOMAIN_EPOCH)
        )

    def train_epoch(self) -> dict[str, float]:
        """Run one training epoch."""
        self.system.geometry.train()
        self._begin_epoch()

        if self._is_graph_classification:
            return self._train_epoch_graph_classification()
        else:
            return self._train_epoch_node_classification()

    def _train_epoch_node_classification(self) -> dict[str, float]:
        """Run one training epoch for node classification (single graph with masks)."""
        # Forward pass on full graph
        with self._autocast:
            out = self.system.forward(self._data.x)

        # Training mask
        train_mask = self._data.train_mask
        if train_mask is None:
            raise ValueError("Graph data missing train_mask")

        # Compute loss on training nodes
        train_out = out[train_mask]
        train_y = self._data.y[train_mask]
        loss = torch.nn.functional.cross_entropy(train_out, train_y)

        # Backward and optimize
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.system.geometry.params.values(), 1.0)
        self.optimizer.step()

        # Metrics
        pred = train_out.argmax(dim=1)
        train_acc = (pred == train_y).float().mean().item()
        train_loss = loss.item()

        metrics = {
            "epoch": self.current_epoch,
            "train_loss": train_loss,
            "train_acc": train_acc,
            "loss": train_loss,
            "global_step": self.global_step,
        }

        self.global_step += 1

        # Validation
        if self.val_data is not None:
            val_metrics = self.validate()
            metrics.update(val_metrics)

        self.history.append(metrics)
        self.current_epoch += 1

        log_epoch(
            self.config,
            epoch=self.current_epoch,
            loss=train_loss,
            metric_name="val_acc",
            metric_value=metrics.get("val_acc"),
        )

        # Checkpoint if configured
        if (
            self.config.checkpoint_every_n > 0
            and self.current_epoch % self.config.checkpoint_every_n == 0
        ):
            self.save_checkpoint()
            if self.checkpoint_callback is not None:
                self.checkpoint_callback(self.snapshot())

        return metrics

    def _train_epoch_graph_classification(self) -> dict[str, float]:
        """Run one training epoch for graph classification (batched graphs)."""
        loader = self.train_data.get_dataloader("train")

        total_loss = 0.0
        total_correct = 0
        total_samples = 0

        for data_batch in loader:
            data_batch = data_batch.to(self.device)

            with self._autocast:
                # Graph classification: model(x, edge_index, batch) -> graph-level logits
                out = self.system.forward(data_batch.x, data_batch.edge_index, data_batch.batch)

            loss = torch.nn.functional.cross_entropy(out, data_batch.y)

            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.system.geometry.params.values(), 1.0)
            self.optimizer.step()

            pred = out.argmax(dim=1)
            total_loss += loss.item() * data_batch.num_graphs
            total_correct += (pred == data_batch.y).sum().item()
            total_samples += data_batch.num_graphs

        avg_loss = total_loss / total_samples if total_samples > 0 else 0.0
        train_acc = total_correct / total_samples if total_samples > 0 else 0.0

        metrics = {
            "epoch": self.current_epoch,
            "train_loss": avg_loss,
            "train_acc": train_acc,
            "loss": avg_loss,
            "global_step": self.global_step,
        }

        self.global_step += 1

        # Validation
        if self.val_data is not None:
            val_metrics = self.validate()
            metrics.update(val_metrics)

        self.history.append(metrics)
        self.current_epoch += 1

        log_epoch(
            self.config,
            epoch=self.current_epoch,
            loss=avg_loss,
            metric_name="val_acc",
            metric_value=metrics.get("val_acc"),
        )

        # Checkpoint if configured
        if (
            self.config.checkpoint_every_n > 0
            and self.current_epoch % self.config.checkpoint_every_n == 0
        ):
            self.save_checkpoint()
            if self.checkpoint_callback is not None:
                self.checkpoint_callback(self.snapshot())

        return metrics

    def validate(self) -> dict[str, float]:
        """Run validation."""
        self.system.geometry.eval()

        if self._is_graph_classification:
            return self._validate_graph_classification()
        else:
            return self._validate_node_classification()

    def _validate_node_classification(self) -> dict[str, float]:
        """Validate on node classification (mask-based)."""
        # Use val_data if provided, else use train_data with val_mask
        data = self._data
        if self.val_data is not None and hasattr(self.val_data, "_data"):
            data = self.val_data._data.to(self.device)

        val_mask = data.val_mask
        if val_mask is None:
            logger.warning("No val_mask found, using test_mask")
            val_mask = data.test_mask
        if val_mask is None:
            raise ValueError("Graph data missing val_mask and test_mask")

        with torch.no_grad(), self._autocast:
            out = self.system.forward(data.x)
            val_out = out[val_mask]
            val_y = data.y[val_mask]

            loss = torch.nn.functional.cross_entropy(val_out, val_y).item()
            pred = val_out.argmax(dim=1)
            acc = (pred == val_y).float().mean().item()

        return {
            "val_loss": loss,
            "val_acc": acc,
        }

    def _validate_graph_classification(self) -> dict[str, float]:
        """Validate on graph classification (DataLoader-based)."""
        loader = self.train_data.get_dataloader("val")

        total_loss = 0.0
        total_correct = 0
        total_samples = 0

        with torch.no_grad(), self._autocast:
            for data_batch in loader:
                data_batch = data_batch.to(self.device)
                out = self.system.forward(data_batch.x, data_batch.edge_index, data_batch.batch)
                loss = torch.nn.functional.cross_entropy(out, data_batch.y)

                pred = out.argmax(dim=1)
                total_loss += loss.item() * data_batch.num_graphs
                total_correct += (pred == data_batch.y).sum().item()
                total_samples += data_batch.num_graphs

        avg_loss = total_loss / total_samples if total_samples > 0 else 0.0
        acc = total_correct / total_samples if total_samples > 0 else 0.0

        return {
            "val_loss": avg_loss,
            "val_acc": acc,
        }

    def save_checkpoint(self, path: str | Path | None = None) -> Path:
        """Save a training checkpoint to disk."""
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
        train_data: Any,
        val_data: Any | None = None,
        max_epochs: int | None = None,
    ) -> GraphSystemTrainer:
        """Load a trainer from a checkpoint file."""
        checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
        config = checkpoint["config"]
        if max_epochs is not None:
            import dataclasses

            config = dataclasses.replace(config, max_epochs=max_epochs)
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
            "Starting Graph training for %d epochs (from epoch %d)",
            self.config.max_epochs,
            self.current_epoch,
        )

        early_stopping_config = EarlyStoppingConfig(
            patience=self.config.early_stopping_patience,
            min_delta=self.config.early_stopping_min_delta,
            metric=self.config.early_stopping_metric,
            mode="max",  # val_acc is maximized
        )
        early_stopping_state = EarlyStoppingState()
        early_stopping_enabled = (
            early_stopping_config.patience > 0 and self.val_data is not None
        )

        while self.current_epoch < self.config.max_epochs:
            self.train_epoch()

            if early_stopping_enabled and self.history:
                last_epoch = self.history[-1]
                should_stop, reason = check_early_stopping(
                    early_stopping_state, early_stopping_config, last_epoch
                )
                if should_stop:
                    logger.info(reason)
                    break

        logger.debug("Graph Training complete")
        return self.history

    def close(self) -> None:
        """Clean up resources."""
        if hasattr(self, "system") and self.system is not None:
            if hasattr(self.system.geometry, "cpu"):
                self.system.geometry.cpu()
        if hasattr(self, "device") and self.device.type == "cuda":
            torch.cuda.empty_cache()
        logger.debug("GraphSystemTrainer resources cleaned up")

    def __enter__(self) -> GraphSystemTrainer:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        self.close()
        return False


__all__ = ["GraphSystemTrainer"]