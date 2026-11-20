"""The defect classes the family screens found, each with its lock (TODO97 S5h).

A row states a defect only when a test names the mechanism. The three classes
the declared space now refuses read the space's own rules (a reversal here
re-admits a cell that dies at train time). The two runtime classes are strict
xfail: they fail today with the traceback the screen recorded and flip green
only when the mechanism is fixed, which is when the marker is deleted.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from computronium.experiment import sec_loop
from computronium.experiment.kernel.evaluate import (
    EvaluationError,
    TaskShape,
    evaluate_cell,
)
from computronium.experiment.kernel.search_space import (
    _is_batch_layout_compatible,
    _is_geometry_task_compatible,
)
from computronium.experiment.sec_pilot import base_schedule


def _coordinate(task_id: str, axis: str, primitive: str):
    axes = sec_loop._base_axes(task_id)
    axes[axis] = primitive
    return sec_loop._coordinate(axes)


def _cpu_schedule(task_id: str):
    schedule = base_schedule(task_id)
    assert schedule is not None
    return replace(schedule, device="cpu")


@pytest.mark.parametrize(
    "primitive",
    ["eligibility_prop", "rtrl_reference", "unbiased_rtrl"],
)
def test_a_time_major_credit_is_refused_on_a_flat_task(primitive: str) -> None:
    """D18: the credit reads a time axis the flat task's loader never emits."""
    legal, reason = sec_loop._is_legal(
        _coordinate("cartpole", "credit", primitive), "cartpole"
    )

    assert legal is False
    assert "batch-layout disagreement" in (reason or "")
    # The same credit composes when the loader does emit a time axis.
    assert _is_batch_layout_compatible("credit", primitive, "time_major") is True


def test_nca_refuses_a_flat_feature_task() -> None:
    """D16: a cell grid needs the task's H and W; 21 features have neither."""
    legal, reason = sec_loop._is_legal(
        _coordinate("copy_task", "geometry", "nca"), "copy_task"
    )

    assert legal is False
    assert "input shape (21,)" in (reason or "")
    # A vision task supplies the grid, so the row stays measurable there.
    assert (
        _is_geometry_task_compatible(
            "nca", TaskShape(input_shape=(1, 28, 28), output_dim=10), "mnist"
        )
        is True
    )


def test_a_causal_transformer_refuses_a_flat_classifier_task() -> None:
    """Its token mode shifts per-token labels a flat classifier does not have."""
    for task_id in ("copy_task", "cartpole"):
        legal, reason = sec_loop._is_legal(
            _coordinate(task_id, "geometry", "causal_transformer"), task_id
        )
        assert legal is False, task_id
        assert "cannot read" in (reason or ""), task_id


@pytest.mark.timeout(300)
@pytest.mark.xfail(
    strict=True,
    reason=(
        "ntm threads its recurrent state across time steps and calls backward "
        "on the same graph twice; close: detach the state between steps"
    ),
)
def test_ntm_detaches_its_recurrent_state() -> None:
    schedule = _cpu_schedule("cartpole")

    evaluate_cell(_coordinate("cartpole", "geometry", "ntm"), schedule)


@pytest.mark.timeout(300)
@pytest.mark.xfail(
    strict=True,
    reason=(
        "a language task's token-id input (int64) and per-token target are not "
        "carried into the geometry/credit contract, so 22 rows on "
        "tiny_shakespeare raise a dtype or shape error; close: declare the "
        "token lane and refuse or adapt a cell that cannot read it"
    ),
)
def test_a_language_task_declares_its_token_lane() -> None:
    """The declared space refuses a cell that cannot read tokens, or it trains."""
    for task_id, geometry in (
        ("tiny_shakespeare", "feedforward"),
        ("char_ngram", "causal_transformer"),
    ):
        coordinate = _coordinate(task_id, "geometry", geometry)
        legal, _reason = sec_loop._is_legal(coordinate, task_id)
        if not legal:
            continue
        schedule = _cpu_schedule(task_id)
        try:
            evaluate_cell(coordinate, schedule)
        except EvaluationError as exc:
            pytest.fail(f"the token lane is undeclared on {task_id}: {exc}")
