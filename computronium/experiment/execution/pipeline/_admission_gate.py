"""Admission gate utilities for pipeline.

Provides the reusable last-mile admission gate (compose validation)
that can be used by pipeline stages and other components.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.experiment.kernel.compose import ProposalComposeError
from computronium.experiment.kernel.evaluate import task_shape
from computronium.experiment.schema.registries import PARAM_BUDGET_TOLERANCE

if TYPE_CHECKING:
    from computronium.experiment.schema.coordinate import Coordinate, Schedule


class AdmissionGateError(ValueError):
    """Raised when a cell fails the admission gate."""

    def __init__(self, cause: str, message: str) -> None:
        self.cause = cause
        super().__init__(message)


def check_compose_gate(
    coordinate: Coordinate,
    schedule: Schedule,
    task_id: str | None = None,
) -> tuple[bool, str | None]:
    """Check SystemConfig.validate via compose_configs (last-mile legality).

    Args:
        coordinate: The experiment coordinate to check.
        schedule: The execution schedule.
        task_id: Optional task ID; inferred from schedule if not provided.

    Returns:
        Tuple of (passed, rejection_message_or_none).
    """
    from computronium.experiment.kernel.compose import (
        compose_configs,
        geometry_param_count,
    )

    try:
        task_name = task_id or schedule.task_id or "unknown"
        task_shape_info = task_shape(task_name)
        config = compose_configs(
            coordinate=coordinate,
            geometry={},
            input_shape=task_shape_info.input_shape,
            output_dim=task_shape_info.output_dim,
            param_budget=schedule.param_budget,
        )
        # Param budget check (R25 fairness rule)
        if schedule.param_budget > 0 and geometry_param_count(
            config.geometry
        ) > schedule.param_budget * (1 + PARAM_BUDGET_TOLERANCE):
            raise ValueError(
                f"Param budget exceeded: {geometry_param_count(config.geometry)} > {schedule.param_budget}"
            )
    except (ValueError, TypeError, KeyError, ProposalComposeError) as e:
        return False, str(e)
    return True, None


def passes_admission_gate(
    coordinate: Coordinate,
    schedule: Schedule,
    task_id: str | None = None,
) -> tuple[bool, str | None]:
    """Run the last-mile compose/validate gate.

    ``iter_candidates`` is the only legality filter upstream; this gate is the
    last mile that proves the selected cell composes for its task shape.

    Args:
        coordinate: The experiment coordinate to check.
        schedule: The execution schedule.
        task_id: Optional task ID; inferred from schedule if not provided.

    Returns:
        Tuple of (passed, rejection_message_or_none).
    """
    return check_compose_gate(coordinate, schedule, task_id)


__all__ = [
    "AdmissionGateError",
    "check_compose_gate",
    "passes_admission_gate",
]
