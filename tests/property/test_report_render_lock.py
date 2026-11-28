"""W64: the report renders what the store holds, and refuses what it cannot.

The report is the product's answer to "what did this run do", and its two
renderers disagreed about a run with no records: the HTML path refused by
name, and the markdown path raised ``KeyError: 'param_count'`` from
``optimizes`` — the objective registry is seeded as a side effect of appending
records, so a store opened read-only (the dashboard, the CLI) reported with an
empty registry. Every other surface entry point seeds it; the report did not.

These tests hold the render surface to the store: the run it names, the
records it counts, the axes it stratified, the export it round-trips, and the
front's directions — which are read from the registry, seeded on demand.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from computronium.experiment.evidence import RecordStore, StoreConfig
from computronium.experiment.schema import (
    Coordinate,
    FailureCause,
    GateVerdict,
    Maturity,
    Provenance,
    Record,
    ReproducibilityClass,
    Schedule,
    Severity,
    Status,
)
from computronium.experiment.surface.report import (
    _maximizes,
    export_to_json,
    generate_html_report,
    generate_run_report,
    load_export_bundle,
    narrative_handoff_summary,
)

_RECORDS = 5


def _record(run_id: str, seed: int, credit: str) -> Record:
    return Record.create(
        run_id=run_id,
        coordinate=Coordinate(
            substrate="digital",
            geometry="feedforward",
            dynamics="instantaneous",
            plasticity="null",
            credit=credit,
            update="euclidean",
            params={"hidden_dims": 16},
        ),
        schedule=Schedule(
            fidelity="L1",
            seed=seed,
            n_seeds=1,
            epochs=1,
            batch_limit=2,
            budget_id="b",
            task_id="digits",
        ),
        provenance=Provenance(
            env={"python": "3.14", "platform": "test"},
            dataset="digits",
            dataset_version="1.0",
            code_sha="test",
            policy="test",
            links={"run_id": run_id},
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
        payload={
            "val_acc": 0.8 + 0.02 * seed,
            "walltime_total": 12.0,
            "param_count": 1600,
            "train_acc": 0.9,
        },
    )


@pytest.fixture
def store() -> Any:
    with RecordStore(StoreConfig(path=Path(":memory:"))) as opened:
        yield opened


def _run(store: RecordStore) -> str:
    run_id = store.create_run()
    for seed in range(_RECORDS - 2):
        store.append(_record(run_id, seed, "gradient"))
    for seed in range(2):
        store.append(_record(run_id, seed, "local_supervision"))
    return run_id


def test_a_report_names_the_run_and_counts_its_records(store: RecordStore) -> None:
    run_id = _run(store)
    text = generate_run_report(store, run_id)

    assert run_id in text
    assert f"Total Records: {_RECORDS}" in text
    assert "gradient" in text
    assert "local_supervision" in text


def test_a_report_makes_no_claim_a_run_cannot_support(store: RecordStore) -> None:
    """One record per cell is no replication: the report says so, not 'no effect'."""
    run_id = _run(store)
    text = generate_run_report(store, run_id)

    assert "no claim-eligible" in text
    assert "INSUFFICIENT" in text


def test_a_report_for_a_run_with_no_records_renders(store: RecordStore) -> None:
    """The dashboard polls a run before its first cell lands."""
    run_id = store.create_run()

    text = generate_run_report(store, run_id)

    assert run_id in text
    assert "Total Records: 0" in text


def test_an_export_round_trips_the_runs_records(
    store: RecordStore, tmp_path: Path
) -> None:
    run_id = _run(store)

    path = export_to_json(store, tmp_path / "bundle.json", run_id)
    bundle = load_export_bundle(path)

    assert len(bundle.records) == _RECORDS
    assert {r["record_id"] for r in bundle.records} == {
        r.record_id for r in store.query_records(run_id=run_id)
    }
    assert bundle.metadata["record_count"] == _RECORDS


def test_an_export_without_a_run_carries_every_run(
    store: RecordStore, tmp_path: Path
) -> None:
    first = _run(store)
    second = _run(store)

    path = export_to_json(store, tmp_path / "bundle.json")
    bundle = load_export_bundle(path)

    assert len(bundle.records) == 2 * _RECORDS
    assert {r["run_id"] for r in bundle.records} == {first, second}


def test_the_html_report_writes_the_run_it_renders(
    store: RecordStore, tmp_path: Path
) -> None:
    run_id = _run(store)

    path = generate_html_report(store, run_id, tmp_path / "report.html")
    page = path.read_text(encoding="utf-8")

    assert page.lower().startswith("<!doctype html>")
    assert "plotly-graph-div" in page
    assert run_id in page


def test_the_html_report_refuses_a_run_with_no_records(
    store: RecordStore, tmp_path: Path
) -> None:
    run_id = store.create_run()

    with pytest.raises(ValueError, match=run_id):
        generate_html_report(store, run_id, tmp_path / "report.html")


def test_the_narrative_names_the_run_it_hands_off(store: RecordStore) -> None:
    run_id = _run(store)
    narrative = narrative_handoff_summary(store, run_id)

    assert run_id in narrative
    assert f"{_RECORDS} total" in narrative


def test_a_front_reads_each_objectives_declared_direction() -> None:
    """Accuracy is maximized, cost is minimized — from the seeded registry."""
    assert _maximizes("val_acc") is True
    assert _maximizes("walltime_total") is False
    assert _maximizes("param_count") is False
    assert _maximizes("an_unclaimed_key") is False
