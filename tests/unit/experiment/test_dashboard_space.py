"""The declared legal space, and the cells the system refuses (TODO68).

The discovery map can only show a gap if it knows the space the gap sits in.
These tests pin that space: the run's own evidence is never hidden by the
grid, the held axes say where their value came from, the void cells are the
ones the system's own rules refuse — and the verbs refuse them too, so the
mark on the picture and the behaviour of the dashboard agree.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient

from computronium.experiment.execution.dashboard.space import (
    SOURCE_MEASURED,
    declared_space,
    grid_values,
    held_axes,
    void_reason,
)
from computronium.experiment.execution.dashboard.web import (
    DashboardConfig,
    WebDashboard,
)
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.seed_registries import seed_all_registries
from tests.unit.experiment.dashboard_store import (
    COORDINATE,
    VOID_COORDINATE,
)
from tests.unit.experiment.dashboard_store import (
    demo_record as _record,
)
from tests.unit.experiment.dashboard_store import (
    demo_spec as _spec,
)

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture(autouse=True)
def _registries() -> None:
    """The registries the space is read through."""
    seed_all_registries()


@pytest.fixture
def store_with_run(tmp_path: Path) -> tuple[Path, str]:
    """A store holding one run with five measured seeds of one cell."""
    from computronium.experiment.evidence.store import RecordStore, StoreConfig

    path = tmp_path / "run.duckdb"
    with RecordStore(StoreConfig(path=path)) as store:
        run_id = store.create_run(spec=_spec())
        for seed in range(5):
            store.append(_record(run_id, 0.40 + 0.02 * seed, seed))
    return path, run_id


class TestDeclaredSpace:
    """The space the grid shows, and where it comes from."""

    def test_the_evidence_is_never_hidden_by_the_grid(self) -> None:
        """A grid that hid the run's own cells would show a false picture."""
        spec = _spec()

        values = grid_values(StructuralAxis.CREDIT, spec, [])

        assert "gradient" in values
        assert "pepita" in values

    def test_the_held_axes_carry_the_runs_own_value(self) -> None:
        spec = _spec()

        held, sources = held_axes(
            spec,
            [],
            [StructuralAxis.CREDIT, StructuralAxis.GEOMETRY, StructuralAxis.DYNAMICS],
        )

        assert held["substrate"] == "digital"
        assert held["plasticity"] == "null"
        assert held["update"] == "adam"
        assert set(sources.values()) == {"declared"}

    def test_a_measured_axis_is_held_at_what_the_run_measured(self) -> None:

        spec = _spec()
        record = _record("run-1", 0.4, 0)

        held, sources = held_axes(
            spec,
            [record],
            [StructuralAxis.CREDIT, StructuralAxis.GEOMETRY, StructuralAxis.DYNAMICS],
        )

        assert held["substrate"] == "digital"
        assert sources["substrate"] == SOURCE_MEASURED

    def test_a_legal_cell_is_legal_and_a_void_one_is_not(self) -> None:
        spec = _spec()

        space = declared_space(
            spec,
            [],
            [StructuralAxis.CREDIT, StructuralAxis.GEOMETRY, StructuralAxis.DYNAMICS],
            task="digits",
        )

        statuses = {cell["status"] for cell in space["cells"]}
        assert "legal" in statuses
        assert "void" in statuses

    def test_the_void_cells_name_the_rule_that_refuses_them(self) -> None:
        spec = _spec()

        space = declared_space(
            spec,
            [],
            [StructuralAxis.CREDIT, StructuralAxis.GEOMETRY, StructuralAxis.DYNAMICS],
            task="digits",
        )

        voids = [cell for cell in space["cells"] if cell["status"] == "void"]
        assert voids
        assert all(cell["reason"] for cell in voids)
        assert space["void_rules"]
        assert sum(space["void_rules"].values()) == len(voids)

    def test_every_cell_names_all_six_axes(self) -> None:
        spec = _spec()

        space = declared_space(
            spec,
            [],
            [StructuralAxis.CREDIT, StructuralAxis.GEOMETRY, StructuralAxis.DYNAMICS],
            task="digits",
        )

        for cell in space["cells"]:
            assert set(cell["coordinate"]) == {
                "credit",
                "geometry",
                "dynamics",
                "substrate",
                "plasticity",
                "update",
            }
            assert all(cell["coordinate"].values())

    def test_the_counts_match_the_cells(self) -> None:
        spec = _spec()

        space = declared_space(
            spec,
            [],
            [StructuralAxis.CREDIT, StructuralAxis.GEOMETRY, StructuralAxis.DYNAMICS],
            task="digits",
        )

        assert space["counts"]["legal"] + space["counts"]["void"] == len(space["cells"])

    def test_the_runs_own_declaration_is_reported(self) -> None:
        spec = _spec()

        space = declared_space(
            spec,
            [],
            [StructuralAxis.CREDIT, StructuralAxis.GEOMETRY, StructuralAxis.DYNAMICS],
            task="digits",
        )

        assert space["declared"]["credit"] == [
            "gradient",
            "random_projections",
            "pepita",
            "local_goodness",
        ]
        assert space["declared"]["geometry"] == ["feedforward"]

    def test_a_cell_inside_the_declaration_says_so(self) -> None:
        spec = _spec()

        space = declared_space(
            spec,
            [],
            [StructuralAxis.CREDIT, StructuralAxis.GEOMETRY, StructuralAxis.DYNAMICS],
            task="digits",
        )

        inside = [
            cell
            for cell in space["cells"]
            if cell["coordinate"]["credit"] == "gradient"
            and cell["coordinate"]["geometry"] == "feedforward"
            and cell["coordinate"]["dynamics"] == "instantaneous"
        ]
        assert inside and inside[0]["in_declaration"] is True


class TestVoidRefusal:
    """The system refuses a cell: the verbs refuse it too."""

    def test_the_reason_names_the_rule(self) -> None:
        reason = void_reason(VOID_COORDINATE, "digits")

        assert reason is not None
        assert "predictive_settling_credit" in reason

    def test_a_legal_cell_is_not_refused(self) -> None:
        assert void_reason(COORDINATE, "digits") is None

    def test_a_quest_about_a_void_cell_is_refused(
        self, store_with_run: tuple[Path, str], tmp_path: Path
    ) -> None:
        path, run_id = store_with_run
        dashboard = WebDashboard(
            DashboardConfig(
                store_path=str(path),
                registration_dir=tmp_path / "regs",
                enable_websockets=False,
            )
        )

        with TestClient(dashboard.app) as client:
            response = client.post(
                f"/api/cells/{run_id}/quest",
                json={"coordinate": VOID_COORDINATE},
            )

        assert response.status_code == 409
        assert "refuses this cell" in response.json()["error"]

    def test_a_replication_of_a_void_cell_is_refused(
        self, store_with_run: tuple[Path, str]
    ) -> None:
        from computronium.experiment.execution.campaign_queue import CampaignQueue

        path, run_id = store_with_run
        dashboard = WebDashboard(
            DashboardConfig(
                store_path=str(path),
                campaign_queue=CampaignQueue(max_concurrent=0),
                enable_websockets=False,
            )
        )

        with TestClient(dashboard.app) as client:
            response = client.post(
                f"/api/cells/{run_id}/replicate",
                json={"coordinate": VOID_COORDINATE},
            )

        assert response.status_code == 409
        assert "refuses this cell" in response.json()["error"]

    def test_queueing_a_gap_measures_the_seeds_the_gate_asks_for(
        self, store_with_run: tuple[Path, str]
    ) -> None:
        """A cell nobody measured owes the whole gate, not the gate and the run's plan.

        The run's own seed plan covers the seeds it measured; a cell it never
        measured owes the gate's count and no more.
        """
        from computronium.experiment.execution.campaign_queue import CampaignQueue

        path, run_id = store_with_run
        dashboard = WebDashboard(
            DashboardConfig(
                store_path=str(path),
                campaign_queue=CampaignQueue(max_concurrent=0),
                enable_websockets=False,
            )
        )

        gap = {**COORDINATE, "credit": "pepita"}
        with TestClient(dashboard.app) as client:
            response = client.post(
                f"/api/cells/{run_id}/replicate",
                json={"coordinate": gap},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["plan"] == 63
        assert body["measurements"] == 63


class TestSpaceEndpoint:
    """The space, as the grid asks for it."""

    def _dashboard(self, store_path: Path) -> WebDashboard:
        return WebDashboard(
            DashboardConfig(
                store_path=str(store_path),
                enable_websockets=False,
            )
        )

    def test_the_endpoint_returns_the_slice(
        self, store_with_run: tuple[Path, str]
    ) -> None:
        path, run_id = store_with_run
        dashboard = self._dashboard(path)

        with TestClient(dashboard.app) as client:
            response = client.post(
                f"/api/cells/{run_id}/space",
                json={"axes": ["credit", "geometry", "dynamics"]},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["run_id"] == run_id
        assert body["axes"] == ["credit", "geometry", "dynamics"]
        assert body["held"]["substrate"] == "digital"
        assert body["cells"]
        assert body["counts"]["legal"] + body["counts"]["void"] == len(body["cells"])

    def test_an_unknown_axis_is_refused(self, store_with_run: tuple[Path, str]) -> None:
        path, run_id = store_with_run
        dashboard = self._dashboard(path)

        with TestClient(dashboard.app) as client:
            response = client.post(
                f"/api/cells/{run_id}/space",
                json={"axes": ["credit", "geometry", "nonsense"]},
            )

        assert response.status_code == 409
        assert "unknown axis" in response.json()["error"]

    def test_an_unknown_run_is_refused(self, tmp_path: Path) -> None:
        from computronium.experiment.evidence.store import RecordStore, StoreConfig

        path = tmp_path / "empty.duckdb"
        with RecordStore(StoreConfig(path=path)):
            pass
        dashboard = self._dashboard(path)

        with TestClient(dashboard.app) as client:
            response = client.post(
                "/api/cells/nope/space",
                json={"axes": ["credit", "geometry", "dynamics"]},
            )

        assert response.status_code == 409
        assert "not in the store" in response.json()["error"]

    def test_the_same_axis_twice_is_refused(
        self, store_with_run: tuple[Path, str]
    ) -> None:
        path, run_id = store_with_run
        dashboard = self._dashboard(path)

        with TestClient(dashboard.app) as client:
            response = client.post(
                f"/api/cells/{run_id}/space",
                json={"axes": ["credit", "credit", "dynamics"]},
            )

        assert response.status_code == 409
        assert "three different axes" in response.json()["error"]
