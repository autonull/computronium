"""The promotion history's replay field names what happened (TODO107 W35).

A cell the L1 statistical gates reject never reaches replay or confirmation.
The history used to call that ``replay=fail``, which blamed in-process state
for a gate decision; the field now says ``not_attempted``. Both directions are
locked: a rejected cell is not a replay failure, and a confirmed cell is a
replay pass.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.experiment.evidence import RecordStore, StoreConfig
from computronium.experiment.execution.statistical_promotion import (
    GateThresholds,
    promote_with_stats,
)
from computronium.experiment.schema import (
    Coordinate,
    FailureCause,
    GateVerdict,
    Maturity,
    Provenance,
    Record,
    ReproducibilityClass,
    RunSpec,
    Schedule,
    Severity,
    Status,
)

if TYPE_CHECKING:
    from pathlib import Path


def _record(run_id: str, seed: int, payload: dict[str, float]) -> Record:
    coordinate = Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="null",
        credit="gradient",
        update="euclidean",
        params={},
    )
    schedule = Schedule(
        fidelity="L0",
        seed=seed,
        n_seeds=2,
        epochs=1,
        batch_limit=1,
        budget_id="w35",
        task_id="digits",
    )
    record = Record.create(
        run_id=run_id,
        coordinate=coordinate,
        schedule=schedule,
        provenance=Provenance(
            env={"test": "w35"},
            dataset="digits",
            dataset_version="1.0",
            code_sha="w35",
            policy="w35",
            links={},
        ),
        status=Status(
            gate_verdict=GateVerdict.PASS_,
            defect="",
            cause=FailureCause.UNKNOWN,
            severity=Severity.LOW,
            quarantine=False,
            maturity=Maturity.L0,
            uncertainty={},
            reproducibility=ReproducibilityClass.REPLAYABLE,
            assessment_procedure_version="1.0",
            ceec_link=None,
        ),
        payload=payload,
    )
    object.__setattr__(record, "cell_key", "cell_w35")
    return record


def _spec() -> RunSpec:
    return RunSpec(profile="w35", task="digits", n_seeds=2, epochs=1)


def _history(
    tmp_path: Path,
    payloads: list[dict[str, float]],
    *,
    confirmation: bool = False,
) -> list[dict[str, object]]:
    with RecordStore(StoreConfig(path=tmp_path / "w35.duckdb")) as store:
        run_id = store.create_run(spec=_spec())
        for seed, payload in enumerate(payloads, start=1):
            store.append(_record(run_id, seed, payload))

        def confirmation_evaluator(_group, seeds):
            return [_record(run_id, seed, payloads[0]) for seed in seeds]

        return promote_with_stats(
            store,
            run_id,
            _spec(),
            tolerance=1e-6,
            thresholds=GateThresholds(min_seeds_for_stats=2, ci_width_threshold=0.1),
            confirmation_evaluator=confirmation_evaluator if confirmation else None,
        )


def test_a_gate_rejected_cell_was_never_replayed(tmp_path: Path) -> None:
    # No train_acc: the train/val gate has insufficient data and rejects the
    # cell, so L2 is never attempted.
    history = _history(tmp_path, [{"val_acc": 0.9}, {"val_acc": 0.9}])
    assert len(history) == 1
    assert history[0]["replay"] == "not_attempted"
    assert history[0]["maturity"] == Maturity.L1.value


def test_a_confirmed_cell_reports_a_replay_pass(tmp_path: Path) -> None:
    payload = {"val_acc": 0.9, "train_acc": 0.9, "spectral_radius": 0.5}
    history = _history(tmp_path, [payload, payload], confirmation=True)
    assert len(history) == 1
    assert history[0]["replay"] == "pass"
    assert history[0]["maturity"] == Maturity.L2.value
