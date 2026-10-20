"""The console dashboard shows the space (TODO68).

The browser draws the declared space: the cells the run measured, the gaps
nobody has measured, and the cells the system refuses. The console dashboard
has to show the same picture — a gap a researcher cannot see is a gap they
cannot act on — and it reads it through the same rules, so the two cannot
disagree.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from rich.text import Text

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.dashboard.console import (
    FREE_AXES,
    MARK_LEGAL,
    MARK_MEASURED,
    MARK_VOID,
    ConsoleDashboard,
    ConsoleDashboardConfig,
    measured_keys,
    space_grid,
)
from computronium.experiment.schema.seed_registries import seed_all_registries
from tests.unit.experiment.dashboard_store import demo_record, demo_spec

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture(autouse=True)
def _registries() -> None:
    """The registries the space is read through."""
    seed_all_registries()


@pytest.fixture
def store_path(tmp_path: Path) -> Path:
    """A store holding one run with five measured seeds of one cell."""
    path = tmp_path / "run.duckdb"
    with RecordStore(StoreConfig(path=path)) as store:
        run_id = store.create_run(spec=demo_spec())
        for seed in range(5):
            store.append(demo_record(run_id, 0.40 + 0.02 * seed, seed))
    return path


class TestTheSpaceGrid:
    """The space, drawn."""

    def test_the_grid_marks_measured_legal_and_void(self) -> None:
        space = {
            "axes": ["credit", "geometry", "dynamics"],
            "values": {
                "credit": ["gradient", "pepita"],
                "geometry": ["feedforward"],
                "dynamics": ["instantaneous"],
            },
            "cells": [
                {
                    "coordinate": {
                        "credit": "gradient",
                        "geometry": "feedforward",
                        "dynamics": "instantaneous",
                    },
                    "status": "legal",
                },
                {
                    "coordinate": {
                        "credit": "pepita",
                        "geometry": "feedforward",
                        "dynamics": "instantaneous",
                    },
                    "status": "void",
                },
            ],
        }

        drawn = space_grid(space, {"gradient|feedforward|instantaneous"}).plain

        assert MARK_MEASURED in drawn
        assert MARK_LEGAL not in drawn
        assert MARK_VOID in drawn
        assert "gradient" in drawn
        assert "pepita" in drawn

    def test_the_grid_names_the_axis_it_holds(self) -> None:
        space = {
            "axes": ["credit", "geometry", "dynamics"],
            "values": {
                "credit": ["gradient"],
                "geometry": ["feedforward"],
                "dynamics": ["instantaneous"],
            },
            "cells": [],
        }

        assert "dynamics=instantaneous" in space_grid(space).plain


class TestTheConsoleSpace:
    """The console dashboard's picture of the space."""

    def _dashboard(self, store_path: Path) -> ConsoleDashboard:
        return ConsoleDashboard(ConsoleDashboardConfig(store_path=str(store_path)))

    def test_the_dashboard_reads_the_declared_space(self, store_path: Path) -> None:
        dashboard = self._dashboard(store_path)

        with RecordStore(StoreConfig(path=store_path, read_only=True)) as store:
            run = store.query_runs()[0]
            records = list(store.query_records(run_id=run.run_id))
            space = dashboard._declared_space(run, records)

        assert space is not None
        assert space["counts"]["legal"] > 0
        assert space["counts"]["void"] > 0
        assert space["held"]["substrate"] == "digital"

    def test_the_panel_says_what_the_space_holds(self, store_path: Path) -> None:
        dashboard = self._dashboard(store_path)

        with RecordStore(StoreConfig(path=store_path, read_only=True)) as store:
            run = store.query_runs()[0]
            records = list(store.query_records(run_id=run.run_id))
            dashboard._latest_space = dashboard._declared_space(run, records)
            dashboard._latest_measured = measured_keys(
                records, [axis.value for axis in FREE_AXES]
            )

        panel = dashboard._render_space()

        assert panel is not None
        assert "Declared Space" in str(panel.title)
        content = panel.renderable
        assert isinstance(content, Text)
        assert "gaps" in content.plain
        assert MARK_MEASURED in content.plain

    def test_the_panel_says_when_there_is_no_space(self, store_path: Path) -> None:
        dashboard = self._dashboard(store_path)

        panel = dashboard._render_space()

        content = panel.renderable
        assert isinstance(content, Text)
        assert "No declared space yet" in content.plain


class TestTheSnapshot:
    """One frame of the console dashboard, as text (TODO69).

    The live dashboard draws into a terminal. A snapshot draws the same frame
    into a string, so a document — or an agent — can show the console
    dashboard without a terminal.
    """

    def _dashboard(self, store_path: Path) -> ConsoleDashboard:
        return ConsoleDashboard(ConsoleDashboardConfig(store_path=str(store_path)))

    def test_the_snapshot_is_a_frame_of_the_dashboard(self, store_path: Path) -> None:
        dashboard = self._dashboard(store_path)

        frame = dashboard.snapshot(width=120, height=30)

        assert "Computronium Console Dashboard" in frame
        assert "Declared Space" in frame

    def test_the_snapshot_reads_the_store_first(self, store_path: Path) -> None:
        """A snapshot of stale numbers is a lie."""
        dashboard = self._dashboard(store_path)

        frame = dashboard.snapshot(width=160, height=40)

        assert "gradient" in frame
        assert "records" in frame
