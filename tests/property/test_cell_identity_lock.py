"""Lock: a cell's replay hash identifies its measurement, seed included (R5a).

The kernel used to assemble the per-cell hash from a hand-written field list
that omitted ``schedule.seed``, so seeds 42/43/44 of one coordinate shared a
hash while their val_acc differed. The hash is now the measurement key (which
carries seed, task, device and determinism) plus code/dataset provenance.
"""

from __future__ import annotations

from computronium.experiment.evidence import LimitationKind, derive_limitations
from computronium.experiment.kernel.evaluate import _cell_replay_hash
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


def _coordinate() -> Coordinate:
    return Coordinate(
        substrate="digital",
        geometry="graph",
        dynamics="instantaneous",
        plasticity="null",
        credit="gradient",
        update="adam",
        params={},
    )


def _schedule(**overrides) -> Schedule:
    base = {
        "fidelity": "L1",
        "seed": 42,
        "n_seeds": 3,
        "epochs": 200,
        "batch_limit": 0,
        "budget_id": "gate",
        "task_id": "graph_classification",
    }
    return Schedule(**{**base, **overrides})


def _provenance() -> Provenance:
    return Provenance(
        env={},
        dataset="graph_classification",
        dataset_version="1.0",
        code_sha="test",
        policy="test",
        links={"run_id": "gate"},
    )


def test_replay_hash_ignores_nothing_but_the_seed_changes_it() -> None:
    provenance = _provenance()
    coordinate = _coordinate()
    same = _cell_replay_hash(provenance, coordinate, _schedule())
    assert _cell_replay_hash(provenance, coordinate, _schedule()) == same
    assert _cell_replay_hash(provenance, coordinate, _schedule(seed=43)) != same


def test_replay_hash_splits_task_device_and_determinism() -> None:
    provenance = _provenance()
    coordinate = _coordinate()
    base = _cell_replay_hash(provenance, coordinate, _schedule())
    assert _cell_replay_hash(provenance, coordinate, _schedule(task_id="cora")) != base
    assert _cell_replay_hash(provenance, coordinate, _schedule(device="cuda")) != base
    assert _cell_replay_hash(
        provenance, coordinate, _schedule(device="cuda", deterministic=True)
    ) != _cell_replay_hash(provenance, coordinate, _schedule(device="cuda"))


def _record(device: str, deterministic: bool = False) -> Record:
    return Record.create(
        run_id="r5",
        coordinate=_coordinate(),
        schedule=_schedule(device=device, deterministic=deterministic),
        provenance=_provenance(),
        status=Status(
            gate_verdict=GateVerdict.PASS_,
            defect="",
            cause=FailureCause.UNKNOWN,
            severity=Severity.LOW,
            quarantine=False,
            maturity=Maturity.L1,
            uncertainty={},
            reproducibility=ReproducibilityClass.REPLAYABLE,
            assessment_procedure_version="test",
            ceec_link=None,
        ),
        payload={},
    )


def _accumulation_limitations(records: list[Record]):
    return [
        limitation
        for limitation in derive_limitations(records)
        if limitation.kind is LimitationKind.NONDETERMINISTIC_ACCUMULATION
    ]


def test_cuda_graph_cells_state_the_scatter_tolerance() -> None:
    line = _accumulation_limitations([_record(device="cuda")])
    assert len(line) == 1
    assert line[0].count == 1
    assert "one graph" in line[0].detail


def test_cpu_and_deterministic_cells_do_not_state_the_tolerance() -> None:
    assert _accumulation_limitations([_record(device="cpu")]) == []
    assert _accumulation_limitations([_record(device="cuda", deterministic=True)]) == []
