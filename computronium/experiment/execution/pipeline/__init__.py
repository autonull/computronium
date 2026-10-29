"""S1-S11 pipeline runner with wrapper obligations (WP9/15/16 + WP19).

The public surface is unchanged from the former single-module
``computronium.experiment.execution.pipeline``: lifecycle, stage execution,
checkpointing and budget enforcement live in separate concern modules, and
:class:`PipelineRunner` composes them.
"""

from __future__ import annotations

from computronium.experiment.execution.pipeline._runner import PipelineRunner
from computronium.experiment.execution.pipeline._types import (
    PipelineConfig,
    PipelineState,
    ZeroYieldError,
    _provenance_for,
    _resolve_tasks,
)

__all__ = [
    "PipelineConfig",
    "PipelineRunner",
    "PipelineState",
    "ZeroYieldError",
    "_provenance_for",
    "_resolve_tasks",
]
