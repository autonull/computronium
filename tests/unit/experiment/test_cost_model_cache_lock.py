"""Cost-model cache lock (TODO88 G7).

``experiments/.timing.json`` prices waves and dry-run estimates per
``device/fidelity``. A run that measured one task rewrote the whole
``per_task`` map, so a 1.8 s/cell MUTAG run at ``cuda/L1`` deleted the
247 s/cell MNIST price for the same key — a 138x under-price that surfaces as
a dry-run saying ``~1.8s/cell`` for a run that costs four minutes a cell.

The lock contains the case: two runs of *different* tasks, same key, in
sequence, must both keep a price.
"""

from __future__ import annotations

import json

import pytest

from computronium.experiment.wave import CostModel, _save_cost_model


@pytest.fixture()
def cache(tmp_path, monkeypatch):
    from computronium.experiment import wave

    path = tmp_path / "timing.json"
    monkeypatch.setattr(wave, "TIMING_CACHE", path)
    return path


def _keys(path) -> dict:
    return json.loads(path.read_text())["cuda/L1"]


def test_a_second_task_keeps_the_first_tasks_price(cache) -> None:
    _save_cost_model(
        "cuda",
        "L1",
        CostModel(
            cost_per_cell_s=247.157,
            startup_s=0.0,
            measured=True,
            per_task={"mnist": 247.157},
        ),
    )
    _save_cost_model(
        "cuda",
        "L1",
        CostModel(
            cost_per_cell_s=1.786,
            startup_s=0.0,
            measured=True,
            per_task={"graph_classification": 1.786},
        ),
    )
    per_task = _keys(cache)["per_task"]
    assert per_task["mnist"] == pytest.approx(247.157)
    assert per_task["graph_classification"] == pytest.approx(1.786)


def test_cost_for_prefers_the_tasks_own_price() -> None:
    model = CostModel(
        cost_per_cell_s=1.786,
        startup_s=0.0,
        measured=True,
        per_task={"mnist": 247.157, "graph_classification": 1.786},
    )
    assert model.cost_for("mnist") == pytest.approx(247.157)
    assert model.cost_for("graph_classification") == pytest.approx(1.786)
    # An unmeasured single task falls back to the aggregate.
    assert model.cost_for(None) == pytest.approx(1.786)


def test_cost_for_a_multi_task_run_means_the_selected_tasks() -> None:
    model = CostModel(
        cost_per_cell_s=1.786,
        startup_s=0.0,
        measured=True,
        per_task={"mnist": 247.157, "graph_classification": 1.786},
    )
    assert model.cost_for_tasks(["mnist"]) == pytest.approx(247.157)
    assert model.cost_for_tasks(["mnist", "graph_classification"]) == pytest.approx(
        (247.157 + 1.786) / 2
    )
    assert model.cost_for_tasks(["unmeasured"]) == pytest.approx(1.786)
