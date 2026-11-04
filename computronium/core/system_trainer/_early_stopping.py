"""Early stopping utilities for training loops.

Provides reusable early stopping logic that can be used by SystemTrainer
and other training components.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping


@dataclass(frozen=True, slots=True)
class EarlyStoppingConfig:
    """Configuration for early stopping.

    Attributes:
        patience: Number of epochs to wait for improvement before stopping.
        min_delta: Minimum change in the monitored metric to qualify as improvement.
        metric: The metric name to monitor (e.g., "val_acc", "val_loss").
        mode: "max" for metrics where higher is better, "min" for lower is better.
    """

    patience: int = 3
    min_delta: float = 0.01
    metric: str = "val_acc"
    mode: str = "max"  # "max" or "min"

    def __post_init__(self) -> None:
        if self.patience < 0:
            raise ValueError("patience must be non-negative")
        if self.min_delta < 0:
            raise ValueError("min_delta must be non-negative")
        if self.mode not in {"max", "min"}:
            raise ValueError(f"mode must be 'max' or 'min', got {self.mode!r}")


@dataclass(frozen=True, slots=True)
class EarlyStoppingState:
    """Mutable state for early stopping tracking.

    This is intentionally not frozen so it can be updated during training.
    """

    best_metric: float = -float("inf")
    patience_counter: int = 0
    stopped: bool = False
    stop_reason: str = ""

    def reset(self) -> None:
        """Reset state for a new training run."""
        object.__setattr__(self, "best_metric", -float("inf"))
        object.__setattr__(self, "patience_counter", 0)
        object.__setattr__(self, "stopped", False)
        object.__setattr__(self, "stop_reason", "")


def check_early_stopping(
    state: EarlyStoppingState,
    config: EarlyStoppingConfig,
    current_metrics: Mapping[str, float],
) -> tuple[bool, str | None]:
    """Check if early stopping should trigger.

    Args:
        state: Current early stopping state (will be mutated).
        config: Early stopping configuration.
        current_metrics: Metrics from the latest epoch.

    Returns:
        Tuple of (should_stop, stop_reason). stop_reason is None if not stopping.
    """
    if config.patience <= 0:
        return False, None

    current_metric = current_metrics.get(config.metric)
    if current_metric is None:
        return False, None

    improved = False
    if config.mode == "max":
        improved = current_metric > state.best_metric + config.min_delta
    else:
        improved = current_metric < state.best_metric - config.min_delta

    if improved:
        object.__setattr__(state, "best_metric", current_metric)
        object.__setattr__(state, "patience_counter", 0)
        return False, None
    else:
        object.__setattr__(state, "patience_counter", state.patience_counter + 1)
        if state.patience_counter >= config.patience:
            object.__setattr__(state, "stopped", True)
            reason = (
                f"Early stopping triggered: {config.metric}={current_metric:.4f} "
                f"did not improve >{config.min_delta:.4f} for {config.patience} epochs "
                f"(best={state.best_metric:.4f})"
            )
            object.__setattr__(state, "stop_reason", reason)
            return True, reason
        return False, None


def create_early_stopping_config_from_schedule(schedule) -> EarlyStoppingConfig:
    """Create EarlyStoppingConfig from a Schedule object.

    Args:
        schedule: Schedule object with early_stopping_patience attribute.

    Returns:
        EarlyStoppingConfig with values from schedule.
    """
    patience = getattr(schedule, "early_stopping_patience", 0)
    if patience <= 0:
        return EarlyStoppingConfig(patience=0)  # Disabled

    return EarlyStoppingConfig(
        patience=patience,
        min_delta=0.01,  # 1% minimum improvement
        metric="val_acc",
        mode="max",
    )


__all__ = [
    "EarlyStoppingConfig",
    "EarlyStoppingState",
    "check_early_stopping",
    "create_early_stopping_config_from_schedule",
]
