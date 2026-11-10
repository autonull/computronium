"""One line per epoch, so a long cell is never silent.

A cell at L2 runs 20 epochs and can take minutes. Without an epoch line the
only signal between "cell started" and "cell finished" is a idle process, which
reads as a hang. Per-step chat stays opt-in (``log_every_n_steps``); this is the
coarse heartbeat every trainer emits by default.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config import SystemTrainerConfig

logger = logging.getLogger(__name__)


def log_epoch(
    config: SystemTrainerConfig,
    *,
    epoch: int,
    loss: float,
    metric_name: str | None = None,
    metric_value: float | None = None,
    epoch_time_s: float | None = None,
) -> None:
    """Emit one progress line when ``epoch`` matches the configured cadence."""
    every = config.log_every_n_epochs
    if every <= 0 or epoch % every:
        return

    metric = (
        f", {metric_name}={metric_value:.4f}"
        if metric_name is not None and metric_value is not None
        else ""
    )
    timing = f", {epoch_time_s:.1f}s/epoch" if epoch_time_s else ""
    remaining = max(0, config.max_epochs - epoch)
    eta = (
        f", ~{remaining * epoch_time_s:.0f}s left" if epoch_time_s and remaining else ""
    )
    logger.info(
        "  epoch %d/%d: loss=%.4f%s%s%s",
        epoch,
        config.max_epochs,
        loss,
        metric,
        timing,
        eta,
    )


__all__ = ["log_epoch"]
