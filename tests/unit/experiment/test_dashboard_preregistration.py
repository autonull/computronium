"""A registration confirms the cell it names (TODO68).

The dashboard writes registrations for single cells: a quest for a cell
nobody measured, a confirmation for a cell that was. If a registration
counted for every run that claims the metric, one click on one cell would
make every run in the repository confirmatory — the same failure the
timestamp rule was written to stop, one level down.

So a registration that names a cell counts only for a run that measured that
cell, and one that names no cell — a protocol about the metric itself, the
kind written by hand — counts as it always did.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest

from computronium.experiment.surface.report import (
    coordinate_key,
    measured_cells,
    preregistered_metrics,
    registrations,
)

if TYPE_CHECKING:
    from collections.abc import Generator
    from datetime import datetime
    from pathlib import Path

GRADIENT = {
    "substrate": "digital",
    "geometry": "feedforward",
    "dynamics": "instantaneous",
    "plasticity": "null",
    "credit": "gradient",
    "update": "adam",
}
PEPITA = {**GRADIENT, "credit": "pepita"}


@pytest.fixture
def registry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[Path]:
    """A registry the report reads, and a clean cache around it."""
    from computronium.experiment.surface import report

    root = tmp_path / "preregistrations"
    root.mkdir()
    monkeypatch.setattr(report, "PREREGISTRATION_ROOT", root)
    report.registrations.cache_clear()
    yield root
    report.registrations.cache_clear()


def _write(registry: Path, name: str, payload: dict[str, Any]) -> None:
    (registry / name).write_text(json.dumps(payload), encoding="utf-8")


class TestTheCellDecides:
    """A registration speaks about a cell, or about the metric."""

    def test_a_registration_about_the_cell_confirms_the_run(
        self, registry: Path
    ) -> None:
        _write(
            registry,
            "quest.json",
            {
                "metric": "val_acc",
                "threshold": 0.2,
                "alpha": 0.05,
                "min_seeds": 63,
                "registered_at": "2026-01-01T09:00:00",
                "coordinate": GRADIENT,
            },
        )

        cells = frozenset({coordinate_key(GRADIENT)})

        assert "val_acc" in preregistered_metrics(None, cells)

    def test_a_registration_about_another_cell_does_not(self, registry: Path) -> None:
        _write(
            registry,
            "quest.json",
            {
                "metric": "val_acc",
                "threshold": 0.2,
                "alpha": 0.05,
                "min_seeds": 63,
                "registered_at": "2026-01-01T09:00:00",
                "coordinate": PEPITA,
            },
        )

        cells = frozenset({coordinate_key(GRADIENT)})

        assert "val_acc" not in preregistered_metrics(None, cells)

    def test_a_protocol_about_the_metric_counts_for_every_run(
        self, registry: Path
    ) -> None:
        """A registration written by hand names no cell, and speaks of all."""
        _write(
            registry,
            "eqprop.json",
            {
                "metric": "val_acc",
                "threshold": 0.8,
                "alpha": 0.05,
                "min_seeds": 5,
                "created": "2026-01-01",
            },
        )

        assert "val_acc" in preregistered_metrics(None, frozenset())

    def test_the_registry_reads_the_registration(self, registry: Path) -> None:
        _write(
            registry,
            "quest.json",
            {
                "metric": "val_acc",
                "threshold": 0.2,
                "registered_at": "2026-01-01T09:00:00",
                "coordinate": GRADIENT,
            },
        )

        entries = registrations(None)

        assert len(entries) == 1
        assert entries[0].metric == "val_acc"
        assert entries[0].threshold == pytest.approx(0.2)
        assert entries[0].cell == coordinate_key(GRADIENT)


class TestTheRunIsConfirmed:
    """The chip reads the rule, not a label."""

    def _status(
        self,
        cells: frozenset[tuple[tuple[str, str], ...]],
        started_at: datetime | None = None,
    ) -> str:
        from computronium.experiment.execution.dashboard.web import run_status

        status = run_status(
            None,
            "run-1",
            ("val_acc",),
            started_at,
            cells,
        )
        return str(status["mode"])

    def test_the_cell_the_run_measured_confirms_it(self, registry: Path) -> None:
        _write(
            registry,
            "quest.json",
            {
                "metric": "val_acc",
                "threshold": 0.2,
                "registered_at": "2026-01-01T09:00:00",
                "coordinate": GRADIENT,
            },
        )

        cells = frozenset({coordinate_key(GRADIENT)})

        assert self._status(cells) == "PREREGISTERED"

    def test_another_run_is_not_confirmed_by_it(self, registry: Path) -> None:
        _write(
            registry,
            "quest.json",
            {
                "metric": "val_acc",
                "threshold": 0.2,
                "registered_at": "2026-01-01T09:00:00",
                "coordinate": GRADIENT,
            },
        )

        cells = frozenset({coordinate_key(PEPITA)})

        assert self._status(cells) == "EXPLORATORY"


class TestTheCellsARunMeasured:
    """The cells a run measured are the ones its records name."""

    def test_the_records_name_the_cells(self) -> None:
        from computronium.experiment.schema.coordinate import (
            Coordinate,
            Provenance,
            Schedule,
        )
        from computronium.experiment.schema.record import (
            FailureCause,
            GateVerdict,
            Maturity,
            Record,
            ReproducibilityClass,
            Severity,
            Status,
        )

        record = Record.create(
            run_id="run-1",
            coordinate=Coordinate(**GRADIENT, params={}),
            schedule=Schedule(
                fidelity="L1",
                seed=0,
                n_seeds=1,
                epochs=1,
                batch_limit=0,
                budget_id="preregistration-test",
                task_id="digits",
                param_budget=0,
            ),
            provenance=Provenance(
                env={"python": "3.14", "platform": "linux"},
                dataset="digits",
                dataset_version="1.0",
                code_sha="preregistration-test",
                policy="preregistration-test",
                links={"run_id": "run-1"},
            ),
            status=Status(
                gate_verdict=GateVerdict.PASS_,
                defect="",
                cause=FailureCause.UNKNOWN,
                severity=Severity.LOW,
                quarantine=False,
                maturity=Maturity.L1,
                uncertainty={},
                reproducibility=ReproducibilityClass.REPLAYABLE,
                assessment_procedure_version="1.0",
                ceec_link=None,
            ),
            payload={"val_acc": 0.4},
        )

        cells = measured_cells([record])

        assert cells == frozenset({coordinate_key(GRADIENT)})
