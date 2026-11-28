"""Lock: a near-chance row carries its ladder record (TODO97 S6b).

A measurement at the base box is not a verdict. The ladder decides whether
the row is one knob away from training, and its record carries the verdict,
the rungs, the cost and the replay hash. The predicates here are the audit's
``near_chance_without_ladder`` check, so the gate is executable in the suite
as well as in CI, and an unimplemented ladder stays a failing test.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from computronium.experiment.sec_ladder import (
    chance_of,
    ladder_rows,
    map_findings,
    near_chance_band,
    replay_hash,
)

MAP = Path("results/sec/map.json")
_RUNS = pytest.mark.skipif(
    not MAP.exists(), reason="no map artifact: the screen runs locally"
)
_PRIMITIVE = "primitive.credit_assignment.pc_alm"
_RUNGS = [
    {
        "factor": 0.1,
        "value": 0.05,
        "status": "measured",
        "val_acc": 0.11,
        "walltime_s": 1.0,
    },
    {
        "factor": 1.0,
        "value": 0.5,
        "status": "measured",
        "val_acc": 0.12,
        "walltime_s": 1.0,
    },
    {
        "factor": 10.0,
        "value": 5.0,
        "status": "measured",
        "val_acc": 0.13,
        "walltime_s": 1.0,
    },
]


def _record(verdict: str = "unimplemented") -> dict[str, Any]:
    """A complete record the schema accepts; a test tampers with one field."""
    rungs = [dict(rung) for rung in _RUNGS]
    record: dict[str, Any] = {
        "primitive": _PRIMITIVE,
        "axis": "credit",
        "task": "mnist",
        "knob": "credit.beta",
        "default": 0.5,
        "rungs": rungs,
        "confirm": dict(rungs[-1]),
        "best": dict(rungs[-1]),
        "verdict": verdict,
        "reason": "the ladder found no point clear of the near-chance band",
        "failing_test": (
            "tests/property/test_ladder_record_lock.py"
            f"::test_an_unimplemented_ladder_clears_its_band[{_PRIMITIVE}]"
        ),
        "close_condition": "the dual-variable settle is not composed",
        "runs": 4,
        "walltime_s": 4.0,
    }
    if verdict == "tuned":
        record["reason"] = None
        record["failing_test"] = None
        record["close_condition"] = None
    record["replay"] = replay_hash(record)
    return record


def _document(record: dict[str, Any] | None = None) -> dict[str, Any]:
    """One bound row at chance, with the record (or without it)."""
    document: dict[str, Any] = {
        "primitives": {
            _PRIMITIVE: {
                "binding": "bound",
                "box": {"credit": "pc_alm", "credit.beta": 0.5},
                "measurement": {"val_acc": 0.12},
                "ruler": "val_acc on mnist (primary validation_accuracy, chance 0.100)",
                "task": "mnist",
            }
        }
    }
    if record is not None:
        document["ladders"] = {_PRIMITIVE: record}
    return document


def test_a_complete_record_has_no_problems() -> None:
    assert map_findings(_document(_record())) == []


def test_a_row_without_a_record_is_a_finding() -> None:
    findings = map_findings(_document())

    assert findings
    assert "no ladder record" in findings[0]


def test_a_record_without_a_verdict_is_a_finding() -> None:
    record = _record()
    del record["verdict"]

    assert any("verdict" in finding for finding in map_findings(_document(record)))


def test_an_unimplemented_record_without_a_close_is_a_finding() -> None:
    record = _record()
    record["close_condition"] = None

    assert any(
        "close condition" in finding for finding in map_findings(_document(record))
    )


def test_a_changed_number_changes_the_replay_hash() -> None:
    record = _record()
    record["rungs"][0]["val_acc"] = 0.99

    assert any("replay hash" in finding for finding in map_findings(_document(record)))


def test_a_claimed_rung_that_did_not_run_is_a_finding() -> None:
    record = _record()
    record["rungs"] = []
    record["replay"] = replay_hash(record)

    assert any(
        "ladder carries" in finding for finding in map_findings(_document(record))
    )


def test_a_tuned_record_needs_a_best_point() -> None:
    record = _record("tuned")
    record["best"] = None
    record["replay"] = replay_hash(record)

    assert any("best point" in finding for finding in map_findings(_document(record)))


@_RUNS
def test_the_base_coordinate_is_the_control_not_a_ladder_candidate() -> None:
    """A row that swaps an axis back to the base value re-measures the control."""
    document = {
        "base": {"credit": "gradient"},
        "primitives": {
            "primitive.credit_assignment.gradient": {
                "binding": "bound",
                "axis": "credit",
                "box": {"credit": "gradient"},
                "measurement": {"val_acc": 0.11},
                "ruler": "val_acc on mnist (chance 0.100)",
            },
            "primitive.credit_assignment.local_contrastive": {
                "binding": "bound",
                "axis": "credit",
                "box": {"credit": "local_contrastive"},
                "measurement": {"val_acc": 0.11},
                "ruler": "val_acc on mnist (chance 0.100)",
            },
        },
    }

    rows = [spec_id for spec_id, _row, _chance in ladder_rows(document)]

    assert rows == ["primitive.credit_assignment.local_contrastive"]


def test_every_near_chance_row_in_the_map_carries_a_record() -> None:
    document = json.loads(MAP.read_text(encoding="utf-8"))

    assert map_findings(document) == []


def _ladder_params() -> list[object]:
    """The map's near-chance rows: every record's verdict is checked."""
    if not MAP.exists():
        return []
    document = json.loads(MAP.read_text(encoding="utf-8"))
    return [
        pytest.param(spec_id, id=spec_id)
        for spec_id, _row, _chance in ladder_rows(document)
    ]


@_RUNS
@pytest.mark.parametrize("spec_id", _ladder_params())
def test_a_ladder_record_matches_its_band(spec_id: str) -> None:
    """An unimplemented ladder stays in the band and names its closing primitive.

    A ``tuned`` record clears the band. The test asserts the verdict and the
    measured rungs agree, so a row that is re-tuned (or a claim that is
    rescued) fails here and forces the record to be updated.
    """
    document = json.loads(MAP.read_text(encoding="utf-8"))
    record = document["ladders"][spec_id]
    row = document["primitives"][spec_id]
    chance = chance_of(str(row["ruler"]))
    assert chance is not None

    values = [
        rung["val_acc"]
        for rung in record["rungs"]
        if rung["status"] == "measured" and rung["val_acc"] is not None
    ]
    confirm = record["confirm"]
    if confirm is not None and confirm["val_acc"] is not None:
        values.append(confirm["val_acc"])
    assert values, "the ladder recorded no measured point"

    band = near_chance_band(chance)
    if record["verdict"] == "unimplemented":
        assert max(values) <= band, (
            f"best {max(values):.3f} cleared the band {band:.3f} but the "
            "record says unimplemented — re-record the ladder"
        )
        assert record["close_condition"], (
            "an unimplemented ladder must name the primitive that closes it"
        )
    else:
        assert max(values) > band, (
            f"best {max(values):.3f} is inside the band {band:.3f}: "
            f"{record['close_condition']}"
        )


@pytest.mark.parametrize(
    ("spec_id", "axis"),
    [
        ("primitive.parameter_update.quantized_adam", "update"),
        ("primitive.plasticity.temporal_psi", "plasticity"),
        ("primitive.substrate.noisy", "substrate"),
    ],
)
def test_the_knob_table_names_the_axis_own_fields(spec_id: str, axis: str) -> None:
    """Every axis's declared ladder knob is a field the config actually has.

    Measured 2026-11-20: the update/plasticity/substrate rows named ``lr``,
    ``decay``, ``bit_width`` and ``energy_per_op``, none of which those configs
    declare, so their ladders recorded "no numeric knob" for a trainable row.
    """
    from computronium.experiment.sec_ladder import ladder_knob
    from computronium.experiment.sec_loop import _AXIS_DEFAULTS, _coordinate

    base = _coordinate(
        {**_AXIS_DEFAULTS, axis: spec_id.rsplit(".", 1)[-1]}, own_knobs=axis
    )
    knob = ladder_knob(spec_id, base, axis)
    assert knob is not None, f"{axis} declares no knob the config carries"
    assert knob[0].startswith(f"{axis}.")


def test_the_ladder_withdraws_a_knob_the_law_declares_unread() -> None:
    """Three identical numbers on an unwired knob are not a capability boundary.

    Measured 2026-11-20 (S9e probe): ``thermodynamic_contrast`` and
    ``local_goodness`` measured the same val_acc at 0.001/0.01/0.1 of
    ``feedback_scale``, and their pseudo-gradient norm is bit-identical at
    those scales. The ladder sweeps the knob the law declares it reads; a
    credit whose declared ff law reads none has no ladder point here.

    S9e follow-up: the two credits S9b also swept still laddered the
    withdrawn knob. ``target_inversion`` declares it reads ``feedback_scale``
    (the norm moves ×10), and ``zeroth_order`` declares it reads the SPSA
    pair budget and ``fd_step`` (the norm moves 76.8 / 79.4 / 115.9), so the
    ladder sweeps ``fd_step`` instead.
    """
    from computronium.experiment.sec_ladder import ladder_knob
    from computronium.experiment.sec_loop import _AXIS_DEFAULTS, _coordinate

    def knob(credit: str) -> tuple[str, float] | None:
        base = _coordinate({**_AXIS_DEFAULTS, "credit": credit}, own_knobs="credit")
        return ladder_knob(f"primitive.credit_assignment.{credit}", base, "credit")

    assert knob("thermodynamic_contrast") == ("credit.beta", 0.5)
    assert knob("local_goodness") is None
    assert knob("random_projections") == ("credit.feedback_scale", 0.01)
    assert knob("target_inversion") == ("credit.feedback_scale", 0.01)
    assert knob("zeroth_order") == ("credit.fd_step", 0.01)


@_RUNS
def test_a_row_box_rebuilds_its_own_coordinate() -> None:
    """The box is a fixed point of the screen's builder, params included.

    A row's box must rebuild the coordinate it measured, or a ladder and a
    claim run another number than the row (TODO97 S9b/S9c: three of six
    sampled rows did not reproduce at their rebuilt box). The builder adds the
    params the box carries and nothing else, so a box screened at another mode
    shows up as a diff.
    """
    from computronium.experiment.sec_ladder import spec_axis
    from computronium.experiment.sec_loop import (
        _box_summary,
        screen_coordinate,
    )
    from computronium.experiment.sec_pilot import base_schedule

    schedule = base_schedule("mnist", "cpu")
    assert schedule is not None
    document = json.loads(MAP.read_text(encoding="utf-8"))
    for spec_id, row in (document.get("primitives") or {}).items():
        box = row.get("box") or {}
        if (row.get("measurement") or {}).get("val_acc") is None:
            continue
        coord = screen_coordinate(box, spec_axis(spec_id), spec_id.rsplit(".", 1)[-1])
        rebuilt = json.loads(json.dumps(_box_summary(coord, schedule), default=str))
        assert rebuilt == json.loads(json.dumps(box, default=str)), spec_id


@pytest.mark.parametrize(
    "spec_id",
    ["primitive.state_dynamics.error_predictive_coding", "primitive.geometry.conv"],
)
def test_the_ladder_sweeps_the_primitive_own_axis(spec_id: str) -> None:
    """A dynamics or geometry row ladders its own knob, not a credit one.

    Measured 2026-11-20: the credit-only ladder placed ``conv`` on the credit
    axis, composed nothing, and recorded "no ladder point trained" for a row
    the screen had just measured.
    """
    from computronium.experiment.kernel.evaluate import CellEvaluation
    from computronium.experiment.sec_ladder import run_ladder
    from computronium.experiment.sec_pilot import base_schedule

    schedule = base_schedule("mnist")
    assert schedule is not None

    def fake(_coord: Any, run: Any) -> CellEvaluation:
        return CellEvaluation(
            metrics={"val_acc": 0.9, "loss": 0.1},
            params={},
            param_count=100,
            walltime_s=0.01,
            epochs_completed=1,
            task_id=run.task_id,
        )

    from computronium.experiment.sec_loop import (
        _AXIS_DEFAULTS,
        _box_summary,
        _coordinate,
    )

    kind = "dynamics" if spec_id.split(".")[1] == "state_dynamics" else "geometry"
    level = spec_id.rsplit(".", 1)[-1]
    axes = {**_AXIS_DEFAULTS, kind: level}
    if kind == "dynamics":
        axes["credit"] = "local_goodness"
    row = {
        "task": "mnist",
        "ruler": "val_acc on mnist (chance 0.100)",
        "box": _box_summary(_coordinate(axes, own_knobs=kind), schedule),
    }
    record = run_ladder(spec_id, row, 0.1, evaluate=fake, schedule=schedule)
    expected = kind
    assert record.axis == expected
    assert record.knob is not None and record.knob.startswith(f"{expected}.")
    assert record.runs == 4
    assert record.verdict == "tuned"


def test_a_ladder_point_the_declared_space_refuses_is_not_trained() -> None:
    """A point the planner would never propose is refused, never trained.

    Measured 2026-11-20: a refused box was trained by the ladder and published
    a false ``tuned`` coordinate; the S9 claim then refused the same box before
    its first cell. The fixture uses the live declared-space rule: a graph
    topology on a 4-feature table cannot read the task's input shape (the
    earlier ``nonlayered_instantaneous_gradient_credit`` row no longer exists).
    """
    from computronium.experiment.sec_ladder import run_ladder
    from computronium.experiment.sec_pilot import base_schedule

    schedule = base_schedule("iris")
    assert schedule is not None

    def boom(_coord: Any, _run: Any) -> None:
        raise AssertionError("the ladder trained a refused box")

    row = {
        "task": "iris",
        "ruler": "val_acc on iris (chance 0.333)",
        "box": {
            "substrate": "digital",
            "geometry": "graph",
            "dynamics": "instantaneous",
            "plasticity": "null",
            "credit": "gradient",
            "update": "euclidean",
            "credit.lr": 0.01,
        },
    }
    record = run_ladder(
        "primitive.geometry.graph", row, 1.0 / 3.0, evaluate=boom, schedule=schedule
    )
    assert record.rungs
    assert all(rung.status == "refused" for rung in record.rungs)
    assert all(
        rung.reason and "cannot read iris's input shape" in rung.reason
        for rung in record.rungs
    )
    assert record.verdict == "unimplemented"


def test_a_ladder_runs_at_its_rows_box() -> None:
    """The ladder's base is the screened row's box, not a compose default.

    Measured 2026-11-20 (S9b): the ladder rebuilt the coordinate from the six
    axes alone, so ``energy_minimization``'s factor-1.0 rung measured 0.2176
    against the row's 0.8709: the base's structural params were dropped, and
    the row's own knob value never entered the ladder.
    """
    from computronium.experiment.sec_ladder import _ladder_setup, ladder_knob
    from computronium.experiment.sec_loop import _params_for
    from computronium.experiment.sec_pilot import base_schedule

    schedule = base_schedule("mnist", "cpu")
    assert schedule is not None
    row = {
        "task": "mnist",
        "axis": "dynamics",
        "box": {
            "substrate": "digital",
            "geometry": "feedforward",
            "dynamics": "pc_alm",
            "plasticity": "null",
            "credit": "gradient",
            "update": "euclidean",
        },
    }
    _, _, base = _ladder_setup("primitive.state_dynamics.pc_alm", row, None, schedule)
    expected = _params_for(
        {
            "substrate": "digital",
            "geometry": "feedforward",
            "dynamics": "pc_alm",
            "plasticity": "null",
            "credit": "gradient",
            "update": "euclidean",
        },
        own_knobs="dynamics",
    )

    assert base.params == expected
    assert base.params["dynamics.step_size"] == 0.1
    assert ladder_knob("primitive.state_dynamics.pc_alm", base, "dynamics") == (
        "dynamics.step_size",
        0.1,
    )


def test_a_pc_alm_step_above_its_stability_bound_is_refused() -> None:
    """The settle's stability bound is declared, so the box is refused by name.

    Measured 2026-11-20 (S9b): ``pc_alm``'s ×10 rung (``dynamics.step_size``
    1.0 against the row's 0.1, rho 1.0) crashed at settle step 6 with
    "NaN/Inf detected in activations". The gain ``step_size * (1 + rho)`` is
    the explicit-Euler curvature of the primal-dual iterate, so the declared
    space refuses a gain at or above its bound instead of proposing a box that
    cannot settle (TODO97 S9d).
    """
    from dataclasses import replace

    from computronium.experiment.sec_loop import _is_legal, screen_coordinate
    from computronium.ontology.system import PC_ALM_GAIN_CEILING

    base = screen_coordinate(
        {
            "substrate": "digital",
            "geometry": "feedforward",
            "dynamics": "pc_alm",
            "plasticity": "null",
            "credit": "pc_alm",
            "update": "euclidean",
        },
        "dynamics",
        "pc_alm",
    )
    large = replace(base, params={**base.params, "dynamics.step_size": 1.0})
    legal, reason = _is_legal(large, "mnist")

    assert not legal
    assert reason is not None and "stability bound" in reason
    assert PC_ALM_GAIN_CEILING <= 1.0 * (1.0 + 1.0)
    assert _is_legal(base, "mnist")[0]


def test_an_unfiled_crash_names_no_borrowed_lock() -> None:
    """A defect no declared class owns names no lock, and the audit says so.

    The unimplemented lock is parameterized over near-chance rows only, so a
    defective row that pointed at it would name a test no run collects (D26).
    A defect class files its own lock when it is filed; an unfiled crash names
    none, and ``record_problems`` reports the missing lock.
    """
    from computronium.experiment.sec_ladder import record_problems, run_ladder
    from computronium.experiment.sec_pilot import base_schedule

    schedule = base_schedule("mnist", "cpu")
    assert schedule is not None

    def boom(_coord: Any, _run: Any) -> None:
        raise RuntimeError("NaN/Inf detected in activations at step 6")

    row = {
        "task": "mnist",
        "axis": "dynamics",
        "box": {
            "substrate": "digital",
            "geometry": "feedforward",
            "dynamics": "pc_alm",
            "plasticity": "null",
            "credit": "pc_alm",
            "update": "euclidean",
            "dynamics.step_size": 0.1,
        },
    }
    record = run_ladder(
        "primitive.state_dynamics.pc_alm", row, 0.1, evaluate=boom, schedule=schedule
    )

    assert record.verdict == "defective"
    assert record.failing_test is None
    assert "defective without a failing test" in record_problems(
        "primitive.state_dynamics.pc_alm", record.to_dict()
    )


def test_a_ladder_refuses_a_row_whose_box_cannot_be_rebuilt() -> None:
    """A row screened before the box carried its params is stale, not adjudicated.

    The box named six axes and a schedule, so its coordinate was rebuilt from
    the screen's defaults — another box (measured 2026-11-20, S9c: three of six
    sampled rows did not reproduce at their rebuilt box). The ladder refuses by
    name and the close is the screen's own repair.
    """
    from computronium.experiment.sec_ladder import run_ladder
    from computronium.experiment.sec_pilot import base_schedule

    schedule = base_schedule("mnist", "cpu")
    assert schedule is not None

    def boom(_coord: Any, _run: Any) -> None:
        raise AssertionError("a stale row trained a cell")

    row = {
        "task": "mnist",
        "axis": "credit",
        "box": {
            "substrate": "digital",
            "geometry": "feedforward",
            "dynamics": "instantaneous",
            "plasticity": "null",
            "credit": "local_contrastive",
            "update": "euclidean",
        },
    }
    record = run_ladder(
        "primitive.credit_assignment.local_contrastive",
        row,
        0.1,
        evaluate=boom,
        schedule=schedule,
    )

    assert record.verdict == "stale"
    assert record.runs == 0
    assert record.close_condition
    assert "structural params" in (record.reason or "")
    document = {
        "primitives": {
            "primitive.credit_assignment.local_contrastive": {
                "binding": "bound",
                "box": row["box"],
                "measurement": {"val_acc": 0.11},
                "ruler": "val_acc on mnist (chance 0.100)",
                "task": "mnist",
            }
        },
        "ladders": {"primitive.credit_assignment.local_contrastive": record.to_dict()},
    }
    assert any("stale" in finding for finding in map_findings(document))


def test_a_tie_goes_to_the_point_nearest_the_default() -> None:
    """A tie is not a change: the best of three equal rungs is the default.

    Measured 2026-11-20 (S9b): ``thermodynamic_contrast`` measured 0.7056 at
    every factor, and the smallest factor was published as a tuned point whose
    claim then had identical arms.
    """
    from computronium.experiment.sec_ladder import LadderRung, _best

    rungs = [
        LadderRung(factor, 0.01 * factor, "measured", 0.7056, 1.0, None)
        for factor in (0.1, 1.0, 10.0)
    ]

    best = _best(rungs)
    assert best is not None
    assert best.factor == 1.0
