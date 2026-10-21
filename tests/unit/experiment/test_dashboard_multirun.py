"""Several runs' evidence in one space (TODO69).

A store holds more than one run, and where each of them reached is a
question about the space rather than about one run. These tests pin that
answer: the runs are named with what they measured, the union of their
slices carries every run's values, the cells they have in common are
counted as cells they met in, and the sentence says which of those it was.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient

from computronium.experiment.execution.dashboard.multirun import (
    SpaceReader,
    agreement,
    cell_key,
    measured_cells,
    multirun_payload,
    summary,
    union_values,
)
from computronium.experiment.execution.dashboard.web import (
    DashboardConfig,
    WebDashboard,
)
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.seed_registries import seed_all_registries
from tests.unit.experiment.dashboard_store import demo_record as _record
from tests.unit.experiment.dashboard_store import demo_spec as _spec

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.experiment.schema.run_spec import RunSpec

AXES = [StructuralAxis.CREDIT, StructuralAxis.GEOMETRY, StructuralAxis.DYNAMICS]


@pytest.fixture(autouse=True)
def _registries() -> None:
    """The registries the space is read through."""
    seed_all_registries()


def _other_spec() -> RunSpec:
    """A second run's declaration: another credit arm, the same rest."""
    spec = _spec()
    axes = tuple(
        selection.model_copy(update={"primitives": ("homeostatic",)})
        if selection.axis is StructuralAxis.CREDIT
        else selection
        for selection in spec.axes
    )
    return spec.model_copy(update={"profile": "demo-second", "axes": axes})


@pytest.fixture
def store_with_two_runs(tmp_path: Path) -> Path:
    """A store holding two runs that reached different cells."""
    from computronium.experiment.evidence.store import RecordStore, StoreConfig

    path = tmp_path / "runs.duckdb"
    with RecordStore(StoreConfig(path=path)) as store:
        first = store.create_run(spec=_spec())
        for seed in range(3):
            store.append(_record(first, 0.40 + 0.02 * seed, seed))
        second = store.create_run(spec=_other_spec())
        for seed in range(2):
            store.append(_record(second, 0.20, seed, credit="homeostatic"))
    return path


class TestTheRunsEvidence:
    """What each run measured, and where it measured it."""

    def test_a_cell_is_named_by_the_axes_the_picture_shows(self) -> None:
        record = _record("run-1", 0.4, 0)

        cells = measured_cells([record], AXES)

        assert list(cells) == [cell_key(["gradient", "feedforward", "instantaneous"])]

    def test_a_cell_carries_its_mean_its_seeds_and_its_arm(self) -> None:
        records = [_record("run-1", 0.40, 0), _record("run-1", 0.50, 1)]

        cell = measured_cells(records, AXES)[
            cell_key(["gradient", "feedforward", "instantaneous"])
        ]

        assert cell["accuracy"] == pytest.approx(0.45)
        assert cell["seeds"] == 2
        assert cell["arm"] == "gradient"

    def test_a_record_without_the_metric_measures_nothing(self) -> None:
        record = _record("run-1", 0.4, 0)
        record.payload.pop("val_acc")

        assert measured_cells([record], AXES) == {}


class TestTheUnion:
    """The runs' slices, taken together."""

    def test_the_union_carries_the_values_of_both_runs(
        self, store_with_two_runs: Path
    ) -> None:
        from computronium.experiment.evidence.store import RecordStore, StoreConfig

        with RecordStore(
            StoreConfig(path=store_with_two_runs, read_only=True)
        ) as store:
            reader = SpaceReader()
            runs = [reader.slice(store, run_id, AXES) for run_id in reader.runs(store)]
            values = union_values([run for run in runs if run], AXES)

        assert "gradient" in values["credit"]
        assert "homeostatic" in values["credit"]

    def test_the_values_keep_the_registrys_order(
        self, store_with_two_runs: Path
    ) -> None:
        from computronium.experiment.evidence.store import RecordStore, StoreConfig

        with RecordStore(
            StoreConfig(path=store_with_two_runs, read_only=True)
        ) as store:
            reader = SpaceReader()
            runs = [reader.slice(store, run_id, AXES) for run_id in reader.runs(store)]
            values = union_values([run for run in runs if run], AXES)

        credit = values["credit"]
        assert credit == sorted(credit, key=credit.index)

    def test_a_slice_is_read_once_and_kept(self, store_with_two_runs: Path) -> None:
        from computronium.experiment.evidence.store import RecordStore, StoreConfig

        with RecordStore(
            StoreConfig(path=store_with_two_runs, read_only=True)
        ) as store:
            reader = SpaceReader()
            run_id = reader.runs(store)[0]
            first = reader.slice(store, run_id, AXES)
            second = reader.slice(store, run_id, AXES)

        assert first is second


class TestTheAgreement:
    """What the runs did between them."""

    def test_a_cell_measured_twice_is_one_cell_they_met_in(self) -> None:
        runs = [
            {"measured": {"a": {}, "b": {}}},
            {"measured": {"b": {}, "c": {}}},
        ]

        measured, shared = agreement(runs)

        assert measured == 3
        assert shared == 1

    def test_runs_that_met_in_nothing_say_so(self) -> None:
        runs = [{"measured": {"a": {}}}, {"measured": {"b": {}}}]

        assert "met in none" in summary(runs)

    def test_runs_that_met_say_where(self) -> None:
        runs = [{"measured": {"a": {}}}, {"measured": {"a": {}}}]

        assert "met in 1" in summary(runs)

    def test_one_run_is_one_run(self) -> None:
        assert "One run measured" in summary([{"measured": {"a": {}}}])

    def test_no_run_says_so(self) -> None:
        assert "No run" in summary([])


class TestTheSpacesEndpoint:
    """The runs' evidence, as the browser asks for it."""

    def _dashboard(self, store_path: Path) -> WebDashboard:
        return WebDashboard(
            DashboardConfig(store_path=str(store_path), enable_websockets=False)
        )

    def test_the_endpoint_holds_every_run_that_measured(
        self, store_with_two_runs: Path
    ) -> None:
        dashboard = self._dashboard(store_with_two_runs)

        with TestClient(dashboard.app) as client:
            response = client.post(
                "/api/spaces",
                json={"axes": ["credit", "geometry", "dynamics"]},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["counts"]["runs"] == 2
        assert body["axes"] == ["credit", "geometry", "dynamics"]
        assert body["summary"]

    def test_every_run_carries_the_cells_it_measured(
        self, store_with_two_runs: Path
    ) -> None:
        dashboard = self._dashboard(store_with_two_runs)

        with TestClient(dashboard.app) as client:
            body = client.post(
                "/api/spaces",
                json={"axes": ["credit", "geometry", "dynamics"]},
            ).json()

        measured = {key for run in body["runs"] for key in run["measured"]}
        assert "gradient|feedforward|instantaneous" in measured
        assert "homeostatic|feedforward|instantaneous" in measured

    def test_the_refused_cells_are_named(self, store_with_two_runs: Path) -> None:
        dashboard = self._dashboard(store_with_two_runs)

        with TestClient(dashboard.app) as client:
            body = client.post(
                "/api/spaces",
                json={"axes": ["credit", "geometry", "dynamics"]},
            ).json()

        assert all(run["refused"] for run in body["runs"])

    def test_an_unknown_axis_is_refused(self, store_with_two_runs: Path) -> None:
        dashboard = self._dashboard(store_with_two_runs)

        with TestClient(dashboard.app) as client:
            response = client.post(
                "/api/spaces",
                json={"axes": ["credit", "geometry", "nonsense"]},
            )

        assert "unknown axis" in response.json()["error"]

    def test_the_same_axis_twice_is_refused(self, store_with_two_runs: Path) -> None:
        dashboard = self._dashboard(store_with_two_runs)

        with TestClient(dashboard.app) as client:
            response = client.post(
                "/api/spaces",
                json={"axes": ["credit", "credit", "dynamics"]},
            )

        assert "three different axes" in response.json()["error"]

    def test_a_run_that_measured_nothing_is_not_in_the_picture(
        self, tmp_path: Path
    ) -> None:
        from computronium.experiment.evidence.store import RecordStore, StoreConfig

        path = tmp_path / "empty.duckdb"
        with RecordStore(StoreConfig(path=path)) as store:
            store.create_run(spec=_spec())
        dashboard = self._dashboard(path)

        with TestClient(dashboard.app) as client:
            body = client.post(
                "/api/spaces",
                json={"axes": ["credit", "geometry", "dynamics"]},
            ).json()

        assert body["counts"]["runs"] == 0
        assert "No run" in body["summary"]


class TestThePayloadItself:
    """The payload the browser draws."""

    def test_the_payload_names_the_runs_and_their_cells(
        self, store_with_two_runs: Path
    ) -> None:
        from computronium.experiment.evidence.store import RecordStore, StoreConfig

        with RecordStore(
            StoreConfig(path=store_with_two_runs, read_only=True)
        ) as store:
            payload = multirun_payload(SpaceReader(), store, AXES)

        assert payload["counts"]["runs"] == 2
        assert payload["counts"]["measured"] == 2
        assert payload["counts"]["shared"] == 0
        for run in payload["runs"]:
            assert run["run_id"]
            assert run["records"] > 0
            assert run["values"]
            assert run["measured"]
