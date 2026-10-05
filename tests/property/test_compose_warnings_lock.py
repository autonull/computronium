"""Q5 — Compose warnings lock.

A legal cell's compose is silent. This lock composes every legal cell of the
campaign YAML under ``warnings.error`` and asserts none raised.
"""

import warnings
from pathlib import Path

import pytest

from computronium.experiment.execution.compose import compose_configs
from computronium.experiment.execution.evaluate import task_shape
from computronium.experiment.execution.search_space import (
    iter_candidates,
    search_space_from_spec,
)
from computronium.experiment.schema.run_spec import RunSpec
from computronium.experiment.schema.seed_registries import seed_all_registries

EXAMPLE = Path(__file__).resolve().parents[2] / "examples"
CAMPAIGN = EXAMPLE / "learning-rules-and-geometry-digits.yaml"


def test_campaign_compose_is_silent() -> None:
    """Every legal cell of the campaign YAML composes without warnings."""
    seed_all_registries()
    spec = RunSpec.load(CAMPAIGN)
    space = search_space_from_spec(spec, tasks=spec.task_names)

    # Collect all legal cells (no budget limit, no cost model)
    cells = list(
        iter_candidates(
            spec,
            space,
            shape=task_shape,
        )
    )
    assert cells, "campaign declares no legal cells"

    # Compose each cell with warnings as errors
    for coordinate, schedule in cells:
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            compose_configs(
                coordinate=coordinate,
                geometry={},
                input_shape=task_shape(schedule.task_id).input_shape,
                output_dim=task_shape(schedule.task_id).output_dim,
                param_budget=schedule.param_budget,
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
