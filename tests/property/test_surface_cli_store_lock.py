"""W64: the store-reading commands, locked on what they promise.

The surface CLI was 25% covered after the parser lock: the parser resolved a
documented invocation, but the handlers behind it never ran. These commands
are the read surface of the store, so each is asserted through ``main`` with a
real DuckDB file (D6 — a contract, not a copied output):

* **`status` names the run it was asked about**, in text and in JSON.
* **`--detailed` adds the economics the plain status omits.**
* **`report` writes the run it names**, and refuses the format it cannot
  render (a PDF without pandoc exits non-zero, it does not raise).
* **`export` then `import` round-trips the records into a second store.**
* **A dry run prints a plan and writes nothing** (TODO46 D22).
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

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
from computronium.experiment.surface import cli as surface_cli

_RECORDS = 3


def _record(
    run_id: str,
    seed: int,
    *,
    credit: str = "gradient",
    payload: dict[str, Any] | None = None,
) -> Record:
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
        payload=payload
        or {
            "val_acc": 0.8 + 0.02 * seed,
            "walltime_total": 12.0,
            "param_count": 1600,
            "train_acc": 0.9,
            "walltime_s": 12.0,
        },
    )


@pytest.fixture
def store_path(tmp_path: Path) -> tuple[Path, str]:
    path = tmp_path / "experiment.duckdb"
    with RecordStore(StoreConfig(path=path)) as store:
        run_id = store.create_run()
        for seed in range(_RECORDS):
            store.append(_record(run_id, seed))
        store.finish_run(run_id, "completed", budget_consumed_s=36.0)
    return path, run_id


def _main(*argv: str) -> int:
    return surface_cli.main(list(argv))


def test_status_names_the_run_it_was_asked_about(
    store_path: tuple[Path, str], capsys: pytest.CaptureFixture[str]
) -> None:
    path, run_id = store_path

    assert (
        _main("status", "--store", str(path), "--run-id", run_id, "--format", "json")
        == 0
    )
    payload = json.loads(capsys.readouterr().out)

    assert payload["run_id"] == run_id
    assert payload["record_count"] == _RECORDS


def test_status_detailed_adds_the_economics(
    store_path: tuple[Path, str], capsys: pytest.CaptureFixture[str]
) -> None:
    path, run_id = store_path

    assert _main("status", "--store", str(path), "--run-id", run_id, "--detailed") == 0
    text = capsys.readouterr().out

    assert f"Run: {run_id}" in text
    assert "Cost per Record" in text


def test_status_without_a_run_lists_every_run(
    store_path: tuple[Path, str], capsys: pytest.CaptureFixture[str]
) -> None:
    path, run_id = store_path

    assert _main("status", "--store", str(path), "--format", "json") == 0
    payload = json.loads(capsys.readouterr().out)

    assert [run["run_id"] for run in payload["runs"]] == [run_id]


def test_status_refuses_an_unknown_run_by_name(
    store_path: tuple[Path, str], capsys: pytest.CaptureFixture[str]
) -> None:
    path, _run_id = store_path

    assert _main("status", "--store", str(path), "--run-id", "absent") == 1
    assert "absent" in capsys.readouterr().err


def test_report_writes_the_run_it_names(
    store_path: tuple[Path, str], tmp_path: Path
) -> None:
    path, run_id = store_path
    output = tmp_path / "report.txt"

    assert (
        _main(
            "report", "--store", str(path), "--run-id", run_id, "--output", str(output)
        )
        == 0
    )
    text = output.read_text(encoding="utf-8")

    assert run_id in text
    assert f"Total Records: {_RECORDS}" in text


def test_report_axis_coverage_is_a_per_axis_table(
    store_path: tuple[Path, str], capsys: pytest.CaptureFixture[str]
) -> None:
    path, run_id = store_path

    assert (
        _main("report", "--store", str(path), "--run-id", run_id, "--axis-coverage")
        == 0
    )
    text = capsys.readouterr().out

    assert "Axis Coverage" in text
    assert "credit:" in text


def test_report_latex_is_a_document(
    store_path: tuple[Path, str], tmp_path: Path
) -> None:
    path, run_id = store_path
    output = tmp_path / "report.tex"

    assert (
        _main(
            "report",
            "--store",
            str(path),
            "--run-id",
            run_id,
            "--format",
            "latex",
            "--output",
            str(output),
        )
        == 0
    )

    assert output.read_text(encoding="utf-8").startswith(r"\documentclass")


def test_report_pdf_returns_refused_without_the_converter(
    store_path: tuple[Path, str], tmp_path: Path
) -> None:
    path, run_id = store_path

    assert (
        _main(
            "report",
            "--store",
            str(path),
            "--run-id",
            run_id,
            "--format",
            "pdf",
            "--output",
            str(tmp_path / "report.pdf"),
        )
        == 1
    )


def test_export_then_import_round_trips_the_records(
    store_path: tuple[Path, str], tmp_path: Path
) -> None:
    source, run_id = store_path
    bundle = tmp_path / "bundle.json"
    target = tmp_path / "imported.duckdb"

    assert (
        _main(
            "export",
            "--store",
            str(source),
            "--run-id",
            run_id,
            "--output",
            str(bundle),
        )
        == 0
    )
    assert (
        _main(
            "import", "--store", str(target), "--input", str(bundle), "--format", "json"
        )
        == 0
    )

    with RecordStore(StoreConfig(path=target, read_only=True)) as imported:
        records = imported.query_records(run_id=run_id)
    assert len(records) == _RECORDS


def test_import_refuses_a_missing_input_by_name(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = tmp_path / "imported.duckdb"

    assert (
        _main(
            "import", "--store", str(target), "--input", str(tmp_path / "absent.json")
        )
        == 1
    )
    assert "absent.json" in capsys.readouterr().err


def test_a_dry_run_prints_a_plan_and_writes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = tmp_path / "experiment.duckdb"

    assert (
        _main(
            "import",
            "--store",
            str(store),
            "--input",
            str(tmp_path / "bundle.json"),
            "--dry-run",
            "--format",
            "json",
        )
        == 0
    )
    plan: dict[str, Any] = json.loads(capsys.readouterr().out)

    assert plan["command"] == "import"
    assert not store.exists()


def _two_group_store(path: Path) -> str:
    with RecordStore(StoreConfig(path=path)) as store:
        run_id = store.create_run()
        for seed in range(3):
            store.append(
                _record(
                    run_id,
                    seed,
                    credit="gradient",
                    payload={"val_acc": 0.80 + 0.01 * seed, "walltime_s": 12.0},
                )
            )
            store.append(
                _record(
                    run_id,
                    seed,
                    credit="local_supervision",
                    payload={"val_acc": 0.70 + 0.01 * seed, "walltime_s": 10.0},
                )
            )
        store.finish_run(run_id, "completed", budget_consumed_s=60.0)
    return run_id


def test_stats_groups_by_axis_and_reports_every_aggregation(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "experiment.duckdb"
    run_id = _two_group_store(path)

    assert (
        _main(
            "stats",
            "--store",
            str(path),
            "--run-id",
            run_id,
            "--metrics",
            "val_acc",
            "--agg",
            "mean,std,min,max,median,ci95",
            "--group-by",
            "credit",
            "--format",
            "json",
        )
        == 0
    )
    rows = json.loads(capsys.readouterr().out)

    assert {row["credit"] for row in rows} == {"gradient", "local_supervision"}
    for row in rows:
        assert row["val_acc_count"] == 3
        assert row["val_acc_mean"] > 0
        assert row["val_acc_median"] > 0
        assert row["val_acc_ci95_low"] <= row["val_acc_mean"]
    assert any("_cohens_d_vs_" in key for row in rows for key in row)


def test_stats_table_and_csv_name_the_metrics(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "experiment.duckdb"
    run_id = _two_group_store(path)

    assert (
        _main(
            "stats",
            "--store",
            str(path),
            "--run-id",
            run_id,
            "--metrics",
            "val_acc",
            "--format",
            "csv",
        )
        == 0
    )
    csv_text = capsys.readouterr().out
    assert csv_text.splitlines()[0].startswith("count,")

    assert (
        _main(
            "stats",
            "--store",
            str(path),
            "--run-id",
            run_id,
            "--metrics",
            "val_acc",
            "--format",
            "table",
        )
        == 0
    )
    assert "val_acc_mean" in capsys.readouterr().out


def test_pareto_excludes_a_dominated_record(
    tmp_path: Path,
) -> None:
    path = tmp_path / "experiment.duckdb"
    with RecordStore(StoreConfig(path=path)) as store:
        run_id = store.create_run()
        for seed, (acc, wall) in enumerate([(0.90, 15.0), (0.80, 10.0), (0.70, 20.0)]):
            store.append(
                _record(
                    run_id,
                    seed,
                    payload={"val_acc": acc, "walltime_s": wall},
                )
            )
    output = tmp_path / "front.json"

    assert (
        _main(
            "pareto",
            "--store",
            str(path),
            "--run-id",
            run_id,
            "--objectives",
            "val_acc,walltime_s",
            "--maximize",
            "true,false",
            "--format",
            "json",
            "--output",
            str(output),
        )
        == 0
    )

    front = json.loads(output.read_text(encoding="utf-8"))
    assert len(front) == 2
    assert {round(point["val_acc"], 2) for point in front} == {0.9, 0.8}


def test_diff_names_both_runs_and_the_test_it_applied(
    tmp_path: Path,
) -> None:
    path = tmp_path / "experiment.duckdb"
    with RecordStore(StoreConfig(path=path)) as store:
        run_a = store.create_run()
        run_b = store.create_run()
        for seed in range(3):
            store.append(_record(run_a, seed, payload={"val_acc": 0.9}))
            store.append(_record(run_b, seed, payload={"val_acc": 0.7}))
    output = tmp_path / "diff.json"

    assert (
        _main(
            "diff",
            "--store",
            str(path),
            "--run-id-a",
            run_a,
            "--run-id-b",
            run_b,
            "--metrics",
            "val_acc",
            "--test",
            "mannwhitney",
            "--format",
            "json",
            "--output",
            str(output),
        )
        == 0
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["run_a"] == run_a
    assert payload["run_b"] == run_b
    comparison = payload["comparisons"]["val_acc"]
    assert comparison["test"] == "mannwhitney"
    assert comparison["mean_diff"] == pytest.approx(0.2)
