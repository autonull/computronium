"""Lock: the deep dive carries one pre-registered claim (TODO95 S4).

The map's surprising bound row is laddered on its primary knob, then five
paired seeds at matched boxes decide a margin that was committed before the
first seed. This test fails if the registration is written after the seeds, if
the seed budget is not fixed-n, if a claim is decided at another box, or if an
inert knob is priced as if it were a result.
"""

from __future__ import annotations

import json
from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from computronium.experiment.sec_deep_dive import (
    CLAIM_SEEDS,
    LADDER_FACTORS,
    MARGIN,
    DeepDiveCandidate,
    LadderRung,
    best_rung,
    claim_registration,
    claim_verdict,
    ladder_points,
    load_registration,
    preregister,
    primary_knob,
    select_candidate,
)
from computronium.validation.preregistration import (
    PairedComparison,
    paired_comparison,
)

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.experiment.schema.coordinate import Schedule


def _schedule(**extra) -> Schedule:
    from computronium.experiment.sec_loop import base_schedule

    schedule = base_schedule("mnist", "cpu")
    assert schedule is not None
    return replace(schedule, **extra)


def _row_box(primitive: str) -> dict:
    """The box a screen writes for one row: axes, params and the schedule."""
    from computronium.experiment.sec_ladder import spec_axis
    from computronium.experiment.sec_loop import (
        _AXIS_DEFAULTS,
        _box_summary,
        screen_coordinate,
    )

    level = primitive.rsplit(".", 1)[-1]
    axis = spec_axis(primitive)
    coord = screen_coordinate({**_AXIS_DEFAULTS, axis: level}, axis, level)
    return _box_summary(coord, _schedule())


def _row(
    primitive: str,
    axis: str,
    val_acc: float,
    *,
    binding: str = "bound",
    swapped: bool = False,
    status: str = "measured",
) -> dict:
    return {
        "primitive": primitive,
        "axis": axis,
        "status": status,
        "binding": binding,
        "swapped": swapped,
        "measurement": {"val_acc": val_acc, "loss": 1.0},
        "resource": {"walltime_s": 1.0},
        "box": _row_box(primitive),
    }


def _map() -> dict:
    rows = {
        row["primitive"]: row
        for row in [
            _row(
                "primitive.credit_assignment.target_inversion",
                "credit_assignment",
                0.12,
            ),
            _row("primitive.credit_assignment.pc_alm", "credit_assignment", 0.30),
            _row(
                "primitive.credit_assignment.gradient",
                "credit_assignment",
                0.89,
                swapped=True,
            ),
            _row(
                "primitive.credit_assignment.homeostatic",
                "credit_assignment",
                0.13,
                binding="inert",
            ),
            _row("primitive.geometry.conv", "geometry", 0.121),
            _row("primitive.credit_assignment.diffusion", "state_dynamics", 0.105),
        ]
    }
    return {"version": "SEC-v3", "inventory": {"bar": 0.106}, "primitives": rows}


def test_the_deep_dive_is_the_surprising_bound_row() -> None:
    """Smallest margin over the bar, bound, non-swapped, with a declared knob."""
    candidate = select_candidate(_map())
    assert candidate is not None
    assert candidate.primitive == "primitive.credit_assignment.target_inversion"
    assert candidate.axis == "credit"
    assert candidate.knob == "credit.feedback_scale"
    assert candidate.default == pytest.approx(0.01)
    assert candidate.margin == pytest.approx(0.12 - 0.106)


def test_a_row_at_the_bar_or_without_a_knob_is_not_a_dive() -> None:
    """An inert axis, a swapped row and a knobless primitive never win."""
    assert select_candidate({"primitives": {}, "inventory": {"bar": 0.1}}) is None
    no_knob = _map()
    no_knob["primitives"] = {
        "primitive.geometry.conv": _row("primitive.geometry.conv", "geometry", 0.12)
    }
    assert select_candidate(no_knob) is None
    assert primary_knob("geometry", "conv") is None


def test_the_ladder_is_three_points_on_the_declared_default() -> None:
    candidate = select_candidate(_map())
    assert candidate is not None
    points = ladder_points(candidate)
    assert [factor for factor, _value in points] == list(LADDER_FACTORS)
    assert [value for _factor, value in points] == pytest.approx([
        candidate.default * factor for factor in LADDER_FACTORS
    ])


def _rung(factor: float, *, status: str = "measured", val_acc: float | None = 0.5):
    return LadderRung(
        factor=factor,
        value=factor,
        status=status,
        val_acc=val_acc,
        walltime_s=1.0,
        replay_hash=None,
        box={},
        reason=None,
    )


def test_the_best_rung_is_measured_and_nearest_on_a_tie() -> None:
    refused = _rung(0.1, status="refused", val_acc=None)
    tie = best_rung((refused, _rung(0.1, val_acc=0.4), _rung(1.0, val_acc=0.4)))
    assert tie is not None and tie.factor == 0.1
    high = _rung(10.0, val_acc=0.6)
    assert best_rung((refused, _rung(1.0, val_acc=0.4), high)) is high
    assert best_rung((refused,)) is None


def test_the_registration_is_written_before_the_first_seed(tmp_path: Path) -> None:
    """The margin, alpha, box and n_max exist before a cell is run."""
    from computronium.experiment.sec_deep_dive import candidate_box

    schedule = _schedule()
    candidate = select_candidate(_map())
    assert candidate is not None
    path = tmp_path / "sec_deep_dive.json"
    registration = preregister(_map(), schedule, path)
    assert registration.min_seeds == CLAIM_SEEDS == 5
    assert registration.threshold == pytest.approx(MARGIN)
    assert registration.box
    assert path.exists()
    assert load_registration(path, candidate_box(candidate, 1.0, schedule)) == (
        registration
    )
    # The schedule alone is another box: a registration that names the row
    # refuses a run that names only the base schedule (TODO97 S9c).
    assert load_registration(path, schedule) is None
    assert json.loads(path.read_text())["min_seeds"] == 5


def test_the_deep_dive_pair_runs_at_the_rows_box() -> None:
    """The arm and the registration rebuild the row, not the base axes.

    Measured 2026-11-20 (S9c follow-up): the arm rebuilt from the six axes
    alone and the registration committed the schedule alone, so the pair ran at
    another box than the registration named. The row's box is the builder.
    """
    from computronium.experiment.sec_deep_dive import candidate_box
    from computronium.experiment.sec_loop import _deep_dive_coordinate, box_params

    schedule = _schedule()
    candidate = select_candidate(_map())
    assert candidate is not None
    control = _deep_dive_coordinate(candidate, 1.0)
    assert candidate_box(candidate, 1.0, schedule) == candidate.box
    assert control.params[candidate.knob] == pytest.approx(candidate.default)
    assert box_params(candidate.box).keys() <= control.params.keys()


def test_a_row_without_box_params_has_no_dive(tmp_path: Path) -> None:
    """A row screened before its box carried params refuses the dive by name.

    The quiet refusal is executable, not prose: the setup returns ``None``
    and the close is the screen's own repair (TODO97 S9c).
    """
    from computronium.experiment.sec_loop import MAP_VERSION, _deep_dive_setup

    document = _map()
    document["version"] = MAP_VERSION
    document["base"] = {"task": "mnist"}
    for row in document["primitives"].values():
        row.pop("box")
    out = tmp_path / "sec"
    out.mkdir()
    (out / "map.json").write_text(json.dumps(document))
    assert _deep_dive_setup(out, "cpu", tmp_path / "absent.json") is None


def test_a_claim_refuses_a_missing_or_foreign_registration(tmp_path: Path) -> None:
    schedule = _schedule()
    assert load_registration(tmp_path / "absent.json", schedule) is None
    path = tmp_path / "sec_deep_dive.json"
    preregister(_map(), schedule, path)
    other = replace(schedule, batch_size=8)
    assert load_registration(path, other) is None


def test_five_paired_seeds_carry_the_interval() -> None:
    """Five index-matched seeds at a matched box: the interval is the claim."""
    control = [0.10, 0.11, 0.12, 0.13, 0.14]
    treatment = [value + 0.06 for value in control]
    paired = paired_comparison(treatment, control, n_boot=200, n_permutations=200)
    assert paired.n == 5
    assert paired.mean_diff == pytest.approx(0.06)
    assert paired.ci_lower <= paired.mean_diff <= paired.ci_upper
    with pytest.raises(ValueError):
        paired_comparison(treatment[:4], control[:4])


def test_the_claim_reads_the_registered_margin_and_box() -> None:
    from computronium.experiment.sec_deep_dive import candidate_box

    schedule = _schedule()
    candidate = DeepDiveCandidate(
        primitive="primitive.credit_assignment.target_inversion",
        axis="credit",
        level="target_inversion",
        val_acc=0.12,
        margin=0.014,
        knob="credit.feedback_scale",
        default=0.01,
        box=_row_box("primitive.credit_assignment.target_inversion"),
        walltime_s=1.0,
    )
    box = candidate_box(candidate, 1.0, schedule)
    registration = claim_registration(candidate, schedule)
    clear = PairedComparison(
        n=5, mean_diff=0.05, ci_lower=0.03, ci_upper=0.07, p_value=0.01, cohens_dz=1.0
    )
    assert claim_verdict(clear, registration, box) == "claim"
    inside = replace(clear, mean_diff=0.005, ci_lower=0.0, ci_upper=0.01)
    assert claim_verdict(inside, registration, box) == "coordinate"
    assert claim_verdict(None, registration, box) == "coordinate"
    assert claim_verdict(clear, registration, schedule) == "coordinate"
    elsewhere = replace(schedule, batch_size=8)
    assert claim_verdict(clear, registration, elsewhere) == "coordinate"
    reboxed = {**box, "credit.feedback_scale": 0.02}
    assert claim_verdict(clear, registration, reboxed) == "coordinate"


def test_an_inert_knob_is_a_capability_gap_not_a_claim() -> None:
    """A ladder that never moves is recorded, never priced as a result."""
    from computronium.experiment.sec_deep_dive import DeepDive

    flat = tuple(_rung(factor, val_acc=0.1195) for factor in LADDER_FACTORS)
    candidate = select_candidate(_map())
    assert candidate is not None
    dive = DeepDive(
        candidate=candidate,
        rungs=flat,
        best=flat[0],
        cells=(),
        paired=None,
        claim={},
        verdict="coordinate",
        stop_reason="the arms are identical at every seed",
        walltime_s=1.0,
        knob_binds=False,
        no_power=True,
    )
    record = dive.to_dict()
    assert record["knob_binds"] is False
    assert record["no_power"] is True
    assert record["effect"] is None
