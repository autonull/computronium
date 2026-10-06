"""
Training utilities for the TaskProtocol interface.
"""

from typing import Protocol, cast, runtime_checkable

import torch
from torch import nn

from computronium.core.logging import get_logger
from computronium.domains.base import DomainType

__all__ = [
    "TaskProtocol",
    "_TaskTrainer",
    "_resolve_task_loss",
]

logger = get_logger()


class _TrackerProtocol(Protocol):
    """Protocol for experiment trackers."""

    def log_metrics(self, metrics: dict[str, float]) -> None: ...


@runtime_checkable
class TaskProtocol(Protocol):
    """Structural interface for experiment tasks.

    All task classes should satisfy this protocol.  Type annotations should
    use ``TaskProtocol`` instead of ``BaseTask`` to allow duck-typed task
    implementations.
    """

    name: str
    quick_mode: bool

    @property
    def device(self) -> str | torch.device:
        """Where batches live. Read-only here: ``DomainTask`` widens it to
        ``str | torch.device``, and a mutable attribute in a Protocol makes
        the protocol invariant, which no concrete task then satisfies."""
        ...

    @property
    def input_dim(self) -> int | None: ...

    @property
    def output_dim(self) -> int: ...

    @property
    def task_type(self) -> str: ...

    def setup(self) -> None: ...

    def get_batch(
        self, split: str = "train", batch_size: int = 32
    ) -> tuple[torch.Tensor, torch.Tensor]: ...

    def create_trainer(self, model: nn.Module, **kwargs) -> object: ...

    def compute_metrics(
        self, logits: torch.Tensor, y: torch.Tensor, loss: float
    ) -> dict[str, float]: ...


def _resolve_task_loss(task: TaskProtocol) -> nn.Module:
    """Pick a torch loss module matching the task's output geometry.

    Regression tasks (``task_type == "tabular"`` with ``output_dim == 1``
    — e.g. California Housing) emit float ``[B, 1]`` targets and must use
    MSELoss; everything else (vision/lm/discrete-tabular) treats the
    target as a class index and uses CrossEntropyLoss.
    """
    if task.task_type == DomainType.TABULAR and task.output_dim == 1:
        return nn.MSELoss()
    return nn.CrossEntropyLoss()


def _compute_task_loss(task: TaskProtocol, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
    """Compute loss using task's custom logic if available, otherwise use resolved loss.

    LM tasks need special handling: they output (B, T, V) and target is (B, T),
    requiring reshape before cross_entropy.
    """
    if hasattr(task, "compute_loss"):
        return task.compute_loss(logits, targets)
    loss_fn = _resolve_task_loss(task)
    return loss_fn(logits, targets)


def _accuracy(logits: torch.Tensor, y: torch.Tensor) -> float:
    """Classification accuracy; 0.0 for non-index targets (regression)."""
    if y.dtype not in (torch.long, torch.int, torch.int32, torch.int64):  # ruff: ignore[literal-membership]
        return 0.0
    preds = logits[:, -1, :] if logits.dim() == 3 else logits
    return (preds.argmax(-1) == y).float().mean().item()


class _SafetyConfig:
    """Minimal safety config for task training (replaces deleted execution._guards)."""

    def __init__(
        self,
        max_grad_norm: float = 1.0,
        max_loss: float = 1e6,
        check_finite: bool = True,
    ):
        self.max_grad_norm = max_grad_norm
        self.max_loss = max_loss
        self.check_finite = check_finite


class _SafetyWrapper:
    """Minimal safety wrapper for task training (replaces deleted execution._guards)."""

    def __init__(self, config: _SafetyConfig):
        self.config = config

    def check_loss(self, loss: torch.Tensor) -> torch.Tensor:
        if self.config.check_finite and not torch.isfinite(loss):
            raise RuntimeError(f"Non-finite loss: {loss}")
        if loss > self.config.max_loss:
            raise RuntimeError(f"Loss exceeds maximum: {loss} > {self.config.max_loss}")
        return loss

    def clip_grad_norm(self, parameters, max_norm: float | None = None) -> torch.Tensor:
        max_norm = max_norm or self.config.max_grad_norm
        return nn.utils.clip_grad_norm_(parameters, max_norm)


class _TaskTrainer:
    """Lightweight task-protocol trainer for plain ``nn.Module`` models.

    Runs the canonical forward/loss/backward/step loop over task batches with
    inline validation, preserving the ``train_*``-prefixed metric shape.
    """

    def __init__(
        self,
        model: nn.Module,
        task: TaskProtocol,
        device: str | torch.device = "cpu",
        epochs: int = 10,
        batches_per_epoch: int = 100,
        batch_size: int = 32,
        eval_batches: int | None = None,
        optimizer: torch.optim.Optimizer | None = None,
        lr: float = 1e-3,
        grad_clip: float = 1.0,
        track_energy: bool = False,
        ablation_tags: dict | None = None,
        output_dir: str | None = None,
        use_compile: bool = False,
        scheduler_type: str | None = None,
        scheduler_kwargs: dict | None = None,
        safety_config: _SafetyConfig | None = None,
        **kwargs,
    ):
        self.model: nn.Module = cast("nn.Module", model)
        self.task = task
        self.device = device
        self.epochs = epochs
        self.batches_per_epoch = int(kwargs.pop("steps", batches_per_epoch))
        self.episodes_per_epoch = self.batches_per_epoch
        self.batch_size = int(kwargs.pop("batch_size", 32))
        self.eval_batches = eval_batches
        self.grad_clip = grad_clip
        self.track_energy = track_energy
        self.ablation_tags = ablation_tags or {}
        self.output_dir = output_dir
        self._loss = _resolve_task_loss(task)
        self.tracker: _TrackerProtocol | None = None
        self.safety_config = safety_config or _SafetyConfig()
        self.safety_wrapper = _SafetyWrapper(self.safety_config)
        if use_compile:
            self.model = cast("nn.Module", torch.compile(self.model))
        lr = float(kwargs.pop("lr", 1e-3))
        self.optimizer = optimizer or torch.optim.Adam(self.model.parameters(), lr=lr)

        # Learning rate scheduler
        self.scheduler: torch.optim.lr_scheduler.LRScheduler | None = None
        if scheduler_type:
            self._create_scheduler(scheduler_type, scheduler_kwargs or {})

    def _create_scheduler(self, scheduler_type: str, scheduler_kwargs: dict) -> None:
        """Create learning rate scheduler from type and kwargs."""
        scheduler_type_lower = scheduler_type.lower()
        if scheduler_type_lower == "cosine":
            t_max = scheduler_kwargs.get("t_max", self.epochs)
            self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer,
                T_max=t_max,
                **{k: v for k, v in scheduler_kwargs.items() if k != "t_max"},
            )
        elif scheduler_type_lower == "step":
            step_size = scheduler_kwargs.get("step_size", 10)
            gamma = scheduler_kwargs.get("gamma", 0.1)
            self.scheduler = torch.optim.lr_scheduler.StepLR(
                self.optimizer, step_size=step_size, gamma=gamma
            )
        elif scheduler_type_lower == "linear":
            start_factor = scheduler_kwargs.get("start_factor", 1.0)
            end_factor = scheduler_kwargs.get("end_factor", 0.01)
            total_iters = scheduler_kwargs.get("total_iters", self.epochs)
            self.scheduler = torch.optim.lr_scheduler.LinearLR(
                self.optimizer,
                start_factor=start_factor,
                end_factor=end_factor,
                total_iters=total_iters,
            )

    def train(self) -> list[dict[str, float]]:
        """Run training loop and return per-epoch metrics."""
        self.task.setup()
        history: list[dict[str, float]] = []

        for epoch in range(self.epochs):
            self.model.train()
            epoch_metrics: dict[str, float] = {}

            for _ in range(self.batches_per_epoch):
                x, y = self.task.get_batch("train", self.batch_size)
                x, y = x.to(self.device), y.to(self.device)

                self.optimizer.zero_grad()
                logits = self.model(x)
                loss = _compute_task_loss(self.task, logits, y)
                loss = self.safety_wrapper.check_loss(loss)
                loss.backward()
                self.safety_wrapper.clip_grad_norm(
                    self.model.parameters(), self.grad_clip
                )
                self.optimizer.step()

                # Accumulate metrics
                epoch_metrics.setdefault("train_loss", 0.0)
                epoch_metrics["train_loss"] += loss.item()

            # Average training metrics
            for k in list(epoch_metrics):
                if k.startswith("train_"):
                    epoch_metrics[k] /= self.batches_per_epoch

            # Validation
            if self.eval_batches is not None:
                val_metrics = self._validate()
                epoch_metrics.update(val_metrics)

            if self.scheduler:
                self.scheduler.step()

            if self.tracker:
                self.tracker.log_metrics(epoch_metrics)

            history.append(epoch_metrics)

        return history

    def train_epoch(self) -> dict[str, float]:
        """Run a single training epoch and return metrics."""
        self.task.setup()
        self.model.train()
        epoch_metrics: dict[str, float] = {}

        for _ in range(self.batches_per_epoch):
            x, y = self.task.get_batch("train", self.batch_size)
            x, y = x.to(self.device), y.to(self.device)

            self.optimizer.zero_grad()
            logits = self.model(x)
            loss = _compute_task_loss(self.task, logits, y)
            loss = self.safety_wrapper.check_loss(loss)
            loss.backward()
            self.safety_wrapper.clip_grad_norm(
                self.model.parameters(), self.grad_clip
            )
            self.optimizer.step()

            # Accumulate metrics
            epoch_metrics.setdefault("train_loss", 0.0)
            epoch_metrics["train_loss"] += loss.item()

        # Average training metrics
        for k in list(epoch_metrics):
            if k.startswith("train_"):
                epoch_metrics[k] /= self.batches_per_epoch

        # Compatibility: also expose as "loss" for tests expecting that key
        if "train_loss" in epoch_metrics:
            epoch_metrics["loss"] = epoch_metrics["train_loss"]

        if self.scheduler:
            self.scheduler.step()

        if self.tracker:
            self.tracker.log_metrics(epoch_metrics)

        return epoch_metrics

    def _validate(self) -> dict[str, float]:
        """Run validation batches."""
        self.model.eval()
        metrics: dict[str, float] = {}
        total_loss = 0.0
        eval_batches = self.eval_batches
        assert eval_batches is not None

        with torch.no_grad():
            for _ in range(eval_batches):
                x, y = self.task.get_batch("val", self.batch_size)
                x, y = x.to(self.device), y.to(self.device)
                logits = self.model(x)
                loss = _compute_task_loss(self.task, logits, y)
                total_loss += loss.item()
                metrics.setdefault("val_acc", 0.0)
                metrics["val_acc"] += _accuracy(logits, y)

        metrics["val_loss"] = total_loss / eval_batches
        metrics["val_acc"] /= eval_batches
        return metrics
