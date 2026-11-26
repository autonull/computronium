"""Lock: the capability rung reads the row's screened box, not a default.

S5j's defect: ``_base_coordinate`` built a box from ``_AXIS_DEFAULTS``, so an
update row ran euclidean while its map row named a different update, and a
graph row crashed in the standard trainer. The rung now rebuilds the measured
row's box with the screen's own builder, asks the declared space before it
trains, and names a row it cannot run (TODO97 S5j).
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from computronium.experiment.sec_claims import map_rows
from computronium.primitives.registry import list_primitives
from tests.primitives.test_primitive_capability import _rung_for

if TYPE_CHECKING:
    from pathlib import Path


def _spec(primitive: str):
    return next(spec for spec in list_primitives() if spec.id == primitive)


def _graph_box() -> dict:
    return {
        "substrate": "digital",
        "geometry": "graph",
        "dynamics": "instantaneous",
        "plasticity": "null",
        "credit": "gradient",
        "update": "euclidean",
        "task": "cora",
        "batch_size": 1,
        "seed": 7,
        "geometry.hidden_dim": 128,
        "geometry.depth": 2,
        "geometry.edge_index": [[0, 1], [1, 0]],
    }


def test_map_rows_keys_each_row_by_its_task(tmp_path: Path) -> None:
    document = {
        "primitives": {
            "primitive.geometry.graph": {
                "status": "measured",
                "box": {"task": "cora"},
            },
            "primitive.geometry.ntm": {
                "status": "refused",
                "box": {"task": "char_ngram"},
            },
        }
    }
    path = tmp_path / "map.json"
    path.write_text(json.dumps(document))
    rows = map_rows([path])
    assert rows["primitive.geometry.graph", "cora"]["status"] == "measured"
    assert rows["primitive.geometry.ntm", "char_ngram"]["status"] == "refused"


def test_a_measured_row_runs_at_its_box_not_the_compose_default() -> None:
    row = {"status": "measured", "box": _graph_box()}
    rung = _rung_for(
        _spec("primitive.geometry.graph"),
        "graph",
        {("primitive.geometry.graph", "cora"): row},
    )
    assert rung.reason is None
    assert rung.coordinate is not None
    assert rung.task_id == "cora"
    assert rung.batch_size == 1
    assert rung.seed == 7
    assert rung.coordinate.geometry == "graph"
    assert rung.coordinate.params["geometry.hidden_dim"] == 128


def test_a_refused_row_is_refused_by_name_before_it_trains() -> None:
    row = {"status": "refused", "trigger": "the declared shape refuses it"}
    rung = _rung_for(
        _spec("primitive.geometry.graph"),
        "sequence",
        {("primitive.geometry.graph", "char_ngram"): row},
    )
    assert rung.coordinate is None
    assert rung.reason is not None
    assert rung.reason.startswith("refused by name: ")
    assert "geometry=graph" in rung.reason
    assert "cannot read" in rung.reason


def test_a_measured_box_the_declared_space_refuses_is_not_trained() -> None:
    box = {
        "substrate": "digital",
        "geometry": "causal_transformer",
        "dynamics": "instantaneous",
        "plasticity": "null",
        "credit": "gradient",
        "update": "euclidean",
        "task": "char_ngram",
        "batch_size": 32,
        "credit.lr": 0.01,
        "update.step_size": 0.01,
        "geometry.hidden_dim": 128,
        "geometry.depth": 2,
    }
    rung = _rung_for(
        _spec("primitive.geometry.causal_transformer"),
        "sequence",
        {
            ("primitive.geometry.causal_transformer", "char_ngram"): {
                "status": "measured",
                "box": box,
            }
        },
    )
    assert rung.coordinate is None
    assert rung.reason is not None
    assert "refused by name" in rung.reason


def test_a_row_without_params_asks_for_a_re_screen() -> None:
    row = {"status": "measured", "box": {"geometry": "graph"}}
    rung = _rung_for(
        _spec("primitive.geometry.graph"),
        "graph",
        {("primitive.geometry.graph", "cora"): row},
    )
    assert rung.coordinate is None
    assert rung.reason is not None
    assert "no structural params" in rung.reason


def test_the_graph_lane_runs_at_the_priced_epochs() -> None:
    box = _graph_box()
    box["epochs"] = 200
    box["batch_limit"] = 1
    rung = _rung_for(
        _spec("primitive.geometry.graph"),
        "graph",
        {("primitive.geometry.graph", "cora"): {"status": "measured", "box": box}},
    )
    assert rung.epochs == 200
    assert rung.batch_limit == 1


def test_a_missing_family_row_falls_back_to_the_declared_base() -> None:
    rung = _rung_for(_spec("primitive.geometry.graph"), "graph", {})
    assert rung.reason is None
    assert rung.coordinate is not None
    assert rung.coordinate.geometry == "graph"
    assert rung.epochs == 1
    assert rung.batch_limit == 64


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
