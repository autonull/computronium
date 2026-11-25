"""SEC run infrastructure locks (TODO104 A1, A3, A4, A6, A7, A9).

Each test fails if the mechanism it locks is removed:
concurrent cells on one device, a thread-kill timeout, a dead knob in the box,
a sub-floor claim seed budget, a zero-value optimum, or a lost part.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from computronium.experiment.evidence.claims import DEFAULT_MIN_SEEDS
from computronium.experiment.meta_sec import (
    CLAIM_SEED_CHOICES,
    _resolve_best,
    analyze_cells_jsonl,
)
from computronium.experiment.sec_all_axes import (
    LadderRung,
    _build_axis_box,
    _declared_reads,
    _get_primary_knob,
    comparison_boxes,
    ladder_verdict,
    pair_schedule,
    preferred_task_family,
    resolve_semaphore,
)
from computronium.experiment.sec_loop import deadline_params
from computronium.experiment.sec_parts import reduce_parts, write_part
from computronium.experiment.schema.coordinate import Schedule


def test_one_device_runs_one_cell() -> None:
    """A single GPU refuses parallel cells: the semaphore is clamped to 1."""
    assert resolve_semaphore(8, devices=1) == 1
    assert resolve_semaphore(2, devices=0) == 1
    assert resolve_semaphore(4, devices=2) == 2
    assert resolve_semaphore(1, devices=4) == 1


def test_deadline_is_cooperative() -> None:
    """A spent budget stops the cell; no budget installs no deadline."""
    assert deadline_params(None) == {}
    params = deadline_params(0.01)
    check = params["deadline_check"]
    assert params["deadline_check_every_n_steps"] == 1
    assert check() is True
    time.sleep(0.02)
    assert check() is False


def _source(relative: str) -> str:
    root = Path(__file__).resolve().parents[2]
    return (root / relative).read_text(encoding="utf-8")


def test_driver_kills_no_thread() -> None:
    """The driver waits on a cell record, never on a cancelled thread."""
    assert "asyncio.wait_for" not in _source("scripts/run_full_sec_competitive.py")


def test_the_mechanisms_are_wired() -> None:
    """A helper that no call site uses locks nothing."""
    driver = _source("scripts/run_full_sec_competitive.py")
    assert "resolve_semaphore(" in driver
    assert "write_part(RESULTS_DIR" in driver
    assert "reduce_parts(RESULTS_DIR" in driver
    assert "RUNG2_ENABLED" in driver

    axes = _source("computronium/experiment/sec_all_axes.py")
    assert "pair_schedule(schedule, seed)" in axes
    assert "measure_declared_default(" in axes
    assert "measure_declared_default(" in driver

    loop = _source("computronium/experiment/sec_loop.py")
    assert "params = deadline_params(budget_s)" in loop


def test_each_pair_runs_its_own_seed() -> None:
    """A paired comparison is n index-matched seeds, not one cell n times."""
    base = Schedule(
        fidelity="L2",
        seed=0,
        n_seeds=5,
        epochs=20,
        batch_limit=0,
        budget_id="rung2-mnist",
        task_id="mnist",
    )
    paired = [pair_schedule(base, seed) for seed in range(5)]
    assert [p.seed for p in paired] == list(range(5))
    assert all(p.n_seeds == 1 for p in paired)
    assert (base.seed, base.n_seeds) == (0, 5)


def test_parts_survive_and_reduce(tmp_path: Path) -> None:
    """Every primitive's outcome is on disk before the axis is reduced."""
    measured = {
        "primitive": "lion",
        "rung1_verdict": "viable",
        "rung2_verdict": "claim",
    }
    write_part(tmp_path, "update", "lion", "measured", measured)
    write_part(tmp_path, "update", "muon", "skipped", {})
    write_part(tmp_path, "update", "adam", "error", {"primitive": "adam"})

    reduced = reduce_parts(tmp_path, "update")

    assert reduced["results"] == [measured]
    assert reduced["skipped"] == ["muon"]
    assert reduced["summary"]["completed"] == 1
    assert reduced["summary"]["viable"] == 1
    assert reduced["summary"]["claims"] == 1
    assert reduced["summary"]["errors"] == 1
    assert reduced["summary"]["skipped"] == 1


@pytest.mark.parametrize("primitive", ["lion", "muon", "local_adam"])
def test_box_varies_only_accepted_knobs(primitive: str) -> None:
    """A box must not ship a knob its primitive cannot read (A4)."""
    from computronium.experiment.schema.axis import StructuralAxis, get_axis_spec
    from computronium.experiment.schema.seed_registries import seed_all_registries

    seed_all_registries()
    spec = get_axis_spec(StructuralAxis.UPDATE, primitive)
    assert spec is not None
    box = _build_axis_box("update", primitive, "mnist")
    dead = [
        key
        for key in box
        if key.startswith("update.")
        and key.split(".", 1)[1] not in spec.accepted_params
    ]
    assert not dead, dead

    knob = _get_primary_knob("update", primitive, task_id="mnist")
    if knob is not None:
        assert knob[0].split(".", 1)[1] in spec.accepted_params


def test_claim_seed_space_respects_the_floor() -> None:
    """A seed budget below the pre-registration floor is not a legal point."""
    assert CLAIM_SEED_CHOICES
    assert all(seeds >= DEFAULT_MIN_SEEDS for seeds in CLAIM_SEED_CHOICES)


def test_zero_objective_is_an_invalid_study() -> None:
    """A best_value that cannot beat 0 falls back to declared defaults."""
    best, valid, reason = _resolve_best(0.0, {"claim_seeds": 3}, {"claim_seeds": 5})
    assert (best, valid) == ({"claim_seeds": 5}, False)
    assert reason is not None

    best, valid, reason = _resolve_best(1.5, {"claim_seeds": 7}, {"claim_seeds": 5})
    assert (best, valid, reason) == ({"claim_seeds": 7}, True, None)


def test_proxy_reads_the_measured_payload(tmp_path: Path) -> None:
    """The cost model reads the record's payload, not an empty top level (A7)."""
    cells = tmp_path / "cells.jsonl"
    rows = [
        {
            "screen": {
                "primitive": "primitive.update_rule.lion",
                "status": "MEASURED",
                "box": {"task_id": "mnist", "fidelity": "L0"},
            },
            "record": {"payload": {"walltime_s": 12.5, "val_acc": 0.91}},
        },
        {
            "screen": {
                "primitive": "primitive.update_rule.muon",
                "status": "MEASURED",
                "box": {"task_id": "mnist"},
            },
            "record": {"payload": {"walltime_s": 7.5, "val_acc": 0.5}},
        },
    ]
    cells.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8"
    )

    stats = analyze_cells_jsonl(cells)

    assert stats["avg_walltime_s"] == pytest.approx(10.0)
    assert stats["claims"] == 2
    assert stats["measured"] == 2


def test_gradient_declares_no_credit_knob() -> None:
    """Exact backprop reads no credit field: an empty set, not an omission."""
    from computronium.experiment.schema.seed_registries import seed_all_registries

    seed_all_registries()
    assert _declared_reads("credit", "gradient") == frozenset()
    assert _get_primary_knob("credit", "gradient", task_id="mnist") is None


def test_the_ladder_sweeps_a_declared_field() -> None:
    """A swept knob is one the rule declares it reads (never an inert field)."""
    from computronium.experiment.schema.seed_registries import seed_all_registries

    seed_all_registries()
    checked = 0
    for primitive in (
        "gradient",
        "local_goodness",
        "target_inversion",
        "zeroth_order",
        "thermodynamic_contrast",
        "random_projections",
    ):
        reads = _declared_reads("credit", primitive)
        if reads is None:
            continue
        checked += 1
        knob = _get_primary_knob("credit", primitive, task_id="mnist")
        if not reads:
            assert knob is None, primitive
        elif knob is not None:
            assert knob[0].split(".", 1)[1] in reads, primitive
    assert checked >= 4


def test_reads_steers_the_measured_knob() -> None:
    """The declared field wins over the table's first positive candidate."""
    from computronium.experiment.schema.seed_registries import seed_all_registries

    seed_all_registries()
    # feedback_scale comes first in the candidate table; zeroth_order reads
    # fd_step, and thermodynamic_contrast reads beta.
    assert _get_primary_knob("credit", "zeroth_order", task_id="mnist")[0] == (
        "credit.fd_step"
    )
    assert _get_primary_knob("credit", "thermodynamic_contrast", task_id="mnist")[
        0
    ] == ("credit.beta")


def _rung(val_acc: float | None, status: str = "measured") -> LadderRung:
    return LadderRung(
        factor=1.0,
        value=0.0,
        status=status,
        val_acc=val_acc,
        walltime_s=1.0,
        replay_hash=None,
        box={},
    )


def test_error_blind_credit_is_not_a_bar_verdict() -> None:
    """Chance accuracy is an error-blind credit's contract, not a failure."""
    from computronium.experiment.schema.seed_registries import seed_all_registries

    seed_all_registries()
    assert ladder_verdict("credit", "homeostatic", "mnist", _rung(0.0646)) == (
        "error_blind"
    )
    assert ladder_verdict("credit", "temporal_trace", "mnist", _rung(0.1028)) == (
        "error_blind"
    )
    assert ladder_verdict("credit", "random_projections", "mnist", _rung(0.0646)) == (
        "below_bar"
    )
    assert ladder_verdict("credit", "random_projections", "mnist", _rung(0.9)) == (
        "viable"
    )
    assert ladder_verdict("credit", "random_projections", "mnist", _rung(None)) == (
        "measured"
    )


def test_the_map_measures_the_common_family() -> None:
    """A declared family is availability; the map compares on one box (A17)."""
    assert preferred_task_family(["continual", "vision"]) == "vision"
    assert preferred_task_family(["continual"]) == "continual"
    assert preferred_task_family(["rl", "tabular"]) == "rl"
    assert preferred_task_family([]) is None


def test_a_pair_is_one_primitive_two_knobs() -> None:
    """A knob claim is decided on its own primitive, not another mechanism.

    The first claim run compared conv against feedforward and reported
    d=-61.27 — a different question than "tuning num_layers on conv"
    (TODO104 A21).
    """
    from computronium.experiment.schema.seed_registries import seed_all_registries

    seed_all_registries()
    knob_key, default_value = _get_primary_knob("geometry", "conv", task_id="mnist")
    treatment, control = comparison_boxes(
        "geometry", "conv", "mnist", default_value * 4, default_value
    )
    assert treatment["geometry"] == control["geometry"] == "conv"
    difference = {key for key in treatment if treatment[key] != control.get(key)}
    assert difference == {knob_key}
    # An integer knob is rounded; the control is the declared default either way.
    assert control[knob_key] in {default_value, round(default_value)}
