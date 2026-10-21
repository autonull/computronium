"""The cell's own dynamics, measured for the dashboard (TODO69).

The stage's last family is about the *system* being measured rather than the
bookkeeping around it. These tests pin the rules that make those pictures
worth reading: the map is the cell's own relaxation and not the identity,
a cell without a state says so rather than drawing a picture of nothing,
and the payload names the cell it measured and the axes it swapped to find
one with a state.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest
from fastapi.testclient import TestClient

from computronium.experiment.execution.dashboard.dynamics import (
    candidate_cells,
    measure_cell,
)
from computronium.experiment.execution.dashboard.web import (
    DashboardConfig,
    WebDashboard,
)
from tests.unit.experiment.dashboard_store import demo_record as _record
from tests.unit.experiment.dashboard_store import demo_spec as _spec

if TYPE_CHECKING:
    from pathlib import Path

# The demo's own cell: feedforward with an instantaneous pass, and so no
# state that moves.
RUN_CELL = {
    "substrate": "digital",
    "geometry": "feedforward",
    "dynamics": "instantaneous",
    "plasticity": "null",
    "credit": "gradient",
    "update": "adam",
}

# A cell that does have a state: a recurrent geometry with a dynamics that
# relaxes.
STATEFUL_CELL = {
    "substrate": "digital",
    "geometry": "recurrent",
    "dynamics": "predictive_settling",
    "plasticity": "null",
    "credit": "thermodynamic_contrast",
    "update": "adam",
}


@pytest.fixture(autouse=True)
def _registries() -> None:
    """The registries the dashboard reads through."""
    from computronium.experiment.schema.seed_registries import seed_all_registries

    seed_all_registries()


@pytest.fixture(scope="module")
def measured() -> dict[str, Any]:
    """One cell's own dynamics, measured once."""
    return measure_cell(STATEFUL_CELL, "digits")


class TestTheTransition:
    """The map is the cell's own, and not the identity."""

    def test_a_cell_with_a_state_moves(self) -> None:
        """The first transition measured the identity; a spectrum of zeros."""
        from computronium.domains.factory import create_task
        from computronium.experiment.analysis.transition import build_transition
        from computronium.experiment.kernel.compose import compose_cell_system
        from computronium.experiment.kernel.evaluate import task_shape
        from computronium.experiment.schema.coordinate import Coordinate

        device = "cpu"
        task = create_task("digits", device=device, quick_mode=True, num_workers=0)
        task.setup()
        shape = task_shape("digits", device)
        cell = compose_cell_system(
            coordinate=Coordinate(**STATEFUL_CELL, params={}),
            geometry={},
            input_shape=shape.input_shape,
            output_dim=shape.output_dim,
            param_budget=10_000,
        )
        system = cell.system.to(device)
        sample_x, _ = next(iter(task.get_dataloader("train")))
        flat = sample_x.reshape(sample_x.shape[0], -1)

        transition = build_transition(system, flat)
        assert transition.stateful

        state = transition.initial
        moved = False
        for _ in range(10):
            nxt = transition.step(state, None)
            if not torch_allclose(nxt.activity["x"], state.activity["x"]):
                moved = True
                break
            state = nxt
        assert moved, "the cell's own relaxation left the state where it was"

    def test_a_cell_without_a_state_says_so(self) -> None:
        """An instantaneous pass has nothing to relax, and says so."""
        payload = measure_cell(RUN_CELL, "digits")
        assert payload["stateful"] is False
        assert "no state that moves" in payload["reason"]
        assert payload["verdict"]


def torch_allclose(left: Any, right: Any) -> bool:
    """Whether two tensors are the same, to the last bit."""
    import torch

    return bool(torch.allclose(left, right, atol=0.0, rtol=0.0))


class TestTheRepair:
    """The nearest cell with a state, and the axes that were swapped."""

    def test_the_runs_own_cell_is_tried_first(self) -> None:
        candidates = candidate_cells(RUN_CELL)
        assert candidates[0][0] == RUN_CELL
        assert candidates[0][1] == []

    def test_a_repair_names_the_axes_it_swapped(self) -> None:
        candidates = candidate_cells(RUN_CELL)
        repaired = [(values, repairs) for values, repairs in candidates if repairs]
        assert repaired
        for values, repairs in repaired:
            assert set(repairs) <= {"geometry", "dynamics", "credit"}
            assert values["dynamics"] != RUN_CELL["dynamics"]
            for axis in repairs:
                assert values[axis] != RUN_CELL[axis]


class TestTheMeasurement:
    """What the server measured, and what it says about it."""

    def test_the_cell_is_named(self, measured: dict[str, Any]) -> None:
        assert measured["cell"]["coordinate"] == STATEFUL_CELL
        assert measured["cell"]["params"] > 0

    def test_the_weights_are_said_to_be_untrained(
        self, measured: dict[str, Any]
    ) -> None:
        """The store does not carry the trained cell, and the picture says so."""
        assert measured["trained"] is False

    def test_the_trajectory_is_a_path(self, measured: dict[str, Any]) -> None:
        trajectory = measured["trajectory"]
        assert len(trajectory["path"]) == trajectory["steps"]
        assert len(trajectory["error"]) == trajectory["steps"]
        assert len(trajectory["norm"]) == trajectory["steps"]

    def test_the_spectrum_is_the_stability_estimate(
        self, measured: dict[str, Any]
    ) -> None:
        """The exponents of the cell's own map, not of the identity."""
        spectrum = measured["spectrum"]
        assert spectrum
        assert any(value != 0.0 for value in spectrum)

    def test_the_basin_is_measured_at_several_radii(
        self, measured: dict[str, Any]
    ) -> None:
        basin = measured["basin"]
        assert len(basin["radii"]) == len(basin["stability"])
        assert basin["paths"]

    def test_the_landscape_is_a_grid(self, measured: dict[str, Any]) -> None:
        landscape = measured["landscape"]
        assert len(landscape["grid"]) == len(landscape["x"])
        row = landscape["grid"][0]
        assert len(row) == len(landscape["y"])

    def test_the_verdict_is_a_sentence(self, measured: dict[str, Any]) -> None:
        verdict = measured["verdict"]
        assert verdict.endswith(".")
        assert len(verdict.split()) > 4

    def test_no_number_is_a_nan(self, measured: dict[str, Any]) -> None:
        """JSON has no NaN, and the browser cannot read one."""
        assert "NaN" not in json.dumps(measured)


class TestTheEndpoint:
    """The dashboard serves the cell's own dynamics."""

    def test_the_run_endpoint_measures_the_runs_cell(self, tmp_path: Path) -> None:
        from computronium.experiment.evidence.store import RecordStore, StoreConfig

        path = tmp_path / "run.duckdb"
        with RecordStore(StoreConfig(path=path)) as store:
            run_id = store.create_run(spec=_spec())
            store.append(_record(run_id, 0.40, 0))

        dashboard = WebDashboard(DashboardConfig(store_path=str(path)))
        with TestClient(dashboard.app) as client:
            response = client.get(f"/api/runs/{run_id}/dynamics")

        assert response.status_code == 200
        payload = response.json()
        assert payload["run_id"] == run_id
        assert payload["stateful"] is True
        assert payload["cell"]["measured_by_run"] is False
        assert payload["cell"]["repairs"]

    def test_the_cell_endpoint_answers_for_a_cell(self, tmp_path: Path) -> None:
        dashboard = WebDashboard(DashboardConfig(store_path=str(tmp_path / "x.duckdb")))
        with TestClient(dashboard.app) as client:
            response = client.get("/api/cells/dynamics", params=STATEFUL_CELL)

        assert response.status_code == 200
        payload = response.json()
        assert payload["stateful"] is True
        assert payload["cell"]["coordinate"] == STATEFUL_CELL
