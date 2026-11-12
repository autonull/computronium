"""Lock: the coverage command and the breadth probe count one corpus one way.

``comp coverage report --corpus`` and ``scripts/probes/t3_credit_breadth.py``
are two surfaces over ``evidence.corpus.scan_corpus``. This lock builds a small
corpus — two readable stores, a FAIL record, and a store that cannot be read —
and asserts both surfaces report the same total, per-geometry error-aware
credits, per-task counts, and the unreadable store. A CLI that ignored
``--corpus`` (or a probe that skipped an unreadable file) fails here.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.schema import (
    Coordinate,
    DataOrigin,
    FailureCause,
    GateVerdict,
    Maturity,
    Provenance,
    Record,
    ReproducibilityClass,
    Schedule,
    Severity,
    Status,
    seed_all_registries,
)
from computronium.experiment.surface import cli

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.timeout(120)


def _record(
    run_id: str,
    *,
    geometry: str,
    credit: str,
    task: str,
    seed: int,
    passed: bool = True,
) -> Record:
    return Record.create(
        run_id=run_id,
        coordinate=Coordinate(
            substrate="digital",
            geometry=geometry,
            dynamics="energy_minimization",
            plasticity="fast_weights",
            credit=credit,
            update="euclidean",
            params={},
        ),
        schedule=Schedule(
            fidelity="L0",
            seed=seed,
            n_seeds=2,
            epochs=1,
            batch_limit=1,
            budget_id="corpus-lock",
            task_id=task,
            param_budget=10_000,
        ),
        provenance=Provenance(
            env={"lock": "corpus"},
            dataset=task,
            dataset_version="1.0",
            code_sha="lock",
            policy="lock",
            links={"run_id": run_id},
            data_origin=DataOrigin.EXPLORATION,
        ),
        status=Status(
            gate_verdict=GateVerdict.PASS_ if passed else GateVerdict.FAIL,
            defect="" if passed else "lock fixture",
            cause=FailureCause.UNKNOWN if passed else FailureCause.RUNTIME_ERROR,
            severity=Severity.LOW,
            quarantine=not passed,
            maturity=Maturity.L0,
            uncertainty={},
            reproducibility=ReproducibilityClass.REPLAYABLE,
            assessment_procedure_version="1.0",
            ceec_link=None,
        ),
        payload={"val_acc": 0.5} if passed else {"status": "failed"},
    )


@pytest.fixture()
def corpus_root(tmp_path: Path) -> Path:
    """Two readable stores (one FAIL record) and one unreadable store."""
    seed_all_registries()
    experiments = tmp_path / "experiments"
    experiments.mkdir()

    first = experiments / "a.duckdb"
    with RecordStore(StoreConfig(path=first)) as store:
        run_id = store.create_run()
        store.append(
            _record(
                run_id, geometry="feedforward", credit="gradient", task="digits", seed=0
            )
        )
        store.append(
            _record(
                run_id, geometry="feedforward", credit="gradient", task="digits", seed=1
            )
        )
        store.append(
            _record(
                run_id,
                geometry="feedforward",
                credit="homeostatic",
                task="digits",
                seed=0,
            )
        )
        store.append(
            _record(
                run_id,
                geometry="feedforward",
                credit="gradient",
                task="digits",
                seed=2,
                passed=False,
            )
        )

    second = experiments / "b.duckdb"
    with RecordStore(StoreConfig(path=second)) as store:
        run_id = store.create_run()
        store.append(
            _record(run_id, geometry="conv", credit="gradient", task="mnist", seed=0)
        )
        store.append(
            _record(
                run_id, geometry="graph", credit="target_inversion", task="cora", seed=0
            )
        )

    (experiments / "broken.duckdb").write_bytes(b"not a duckdb file")
    return tmp_path


def _command_numbers(
    monkeypatch: pytest.MonkeyPatch, root: Path, capsys: pytest.CaptureFixture[str]
) -> dict:
    monkeypatch.chdir(root)
    assert cli.main(["coverage", "report", "--corpus", "--format", "json"]) == 0
    return json.loads(capsys.readouterr().out)


def _probe_numbers(root: Path, capsys: pytest.CaptureFixture[str]) -> dict:
    from scripts.probes.t3_credit_breadth import main

    assert main(["--root", str(root)]) == 0
    return json.loads(capsys.readouterr().out)


def test_the_command_and_the_probe_count_the_same_corpus(
    corpus_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    command = _command_numbers(monkeypatch, corpus_root, capsys)
    probe = _probe_numbers(corpus_root, capsys)

    assert command["pass_cells"] == probe["pass_cells"] == 5
    assert command["geometries"] == probe["geometries"]
    assert command["tasks"] == probe["tasks"] == {"cora": 1, "digits": 3, "mnist": 1}
    assert command["untouched_tasks"] == probe["untouched_tasks"]
    assert "kmnist" in command["untouched_tasks"]

    feedforward = command["geometries"]["feedforward"]
    assert feedforward["error_aware"] == ["gradient"]
    assert feedforward["error_blind"] == ["homeostatic"]
    assert feedforward["pass_cells"] == 3  # the FAIL record is not counted


def test_an_unreadable_store_is_reported_by_both_surfaces(
    corpus_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    command = _command_numbers(monkeypatch, corpus_root, capsys)
    probe = _probe_numbers(corpus_root, capsys)

    broken = "experiments/broken.duckdb"
    assert broken in command["unreadable"]
    assert broken in probe["unreadable"]
    assert len(command["source"]) == 2  # the broken store is not a source
