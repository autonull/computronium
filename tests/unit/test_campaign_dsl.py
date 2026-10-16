"""Unit tests for the campaign design DSL (``CampaignDSL``).

Locks the behaviour refactored out of ``to_campaign_yaml``: the recurrent
geometry filter, the axis-selection order, enum serialization, and the
adaptive-budget plan derived from design blocks. No store, no training.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from computronium.experiment.design.campaign_dsl import CampaignDSL

_AXES = ("substrate", "geometry", "dynamics", "plasticity", "credit", "update")


def _spec(**design_overrides: object) -> CampaignDSL:
    design: dict[str, object] = {
        "design_type": "full_factorial",
        "blocks": [{"task": "digits", "epochs": 3, "seeds": 2}],
        "factors": {
            "geometry": {"name": "geometry", "values": ["recurrent", "mlp"]},
            "dynamics": {"name": "dynamics", "values": ["instantaneous"]},
            "credit": {"name": "credit", "values": ["gradient"]},
        },
    }
    design.update(design_overrides)
    return CampaignDSL.model_validate({"meta": {"name": "t"}, "design": design})


def _geometry_primitives(spec: CampaignDSL) -> list[str]:
    run = spec._build_runs()[0]
    axes = run["overrides"]["axes"]
    return next(a["primitives"] for a in axes if a["axis"] == "geometry")


def test_recurrent_geometry_dropped_for_instantaneous_gradient() -> None:
    spec = _spec(
        factors={
            "geometry": {
                "name": "geometry",
                "values": ["recurrent", "recurrent_attractor", "mlp"],
            },
            "dynamics": {"name": "dynamics", "values": ["instantaneous"]},
            "credit": {"name": "credit", "values": ["gradient"]},
        }
    )
    assert _geometry_primitives(spec) == ["mlp"]


def test_recurrent_geometry_survives_temporal_dynamics() -> None:
    spec = _spec(
        factors={
            "geometry": {
                "name": "geometry",
                "values": ["recurrent", "recurrent_attractor", "mlp"],
            },
            "dynamics": {"name": "dynamics", "values": ["predictive_settling"]},
            "credit": {"name": "credit", "values": ["gradient"]},
        }
    )
    assert _geometry_primitives(spec) == ["recurrent", "recurrent_attractor", "mlp"]


def test_axis_selection_order_is_stable() -> None:
    axes = _spec()._build_runs()[0]["overrides"]["axes"]
    assert tuple(a["axis"] for a in axes) == _AXES


def test_enum_values_serialize_as_strings() -> None:
    dumped = _spec().model_dump(mode="json")
    assert dumped["design"]["design_type"] == "full_factorial"


def test_campaign_yaml_is_written() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = _spec().to_campaign_yaml(Path(tmp) / "nested" / "c.yaml")
        assert out.exists()
        assert "runs:" in out.read_text(encoding="utf-8")


def test_adaptive_budget_plan_reads_block_shape() -> None:
    plan = _spec().to_adaptive_budget_plan()
    assert plan.epochs == 3
    assert plan.n_seeds == 2
