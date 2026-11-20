"""The defect classes the family screens found, each with its lock (TODO97 S5h).

A row states a defect only when a test names the mechanism. The three classes
the declared space refuses read the space's own rules (a reversal here
re-admits a cell that dies at train time). The two runtime classes are now
fixed: the token lane is declared on the task and enforced by the space, and
the NTM detaches the state it carries between steps.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from computronium.experiment import sec_loop
from computronium.experiment.kernel.evaluate import (
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
        assert "token-lane disagreement" in (reason or ""), task_id


@pytest.mark.timeout(300)
def test_ntm_detaches_its_recurrent_state() -> None:
    """The zero-history local recipe: state crosses steps, its graph does not."""
    schedule = _cpu_schedule("cartpole")

    evaluate_cell(_coordinate("cartpole", "geometry", "ntm"), schedule)


def test_a_language_task_declares_its_token_lane() -> None:
    """The declared space refuses a cell that cannot read tokens, or it trains.

    An LM task declares token ids in and one label per token; a token geometry
    reads that lane and every other geometry is refused by name. A per-row
    language task (char_ngram) meets the same rule from the other direction:
    its targets do not fold per token, so the token geometry is refused.
    """
    for task_id, geometry in (
        ("tiny_shakespeare", "causal_transformer"),
        ("tiny_shakespeare", "feedforward"),
        ("char_ngram", "causal_transformer"),
        ("char_ngram", "attention"),
    ):
        coordinate = _coordinate(task_id, "geometry", geometry)
        legal, reason = sec_loop._is_legal(coordinate, task_id)
        lane_matches = (geometry == "causal_transformer") == (
            task_id == "tiny_shakespeare"
        )
        assert legal is lane_matches, (task_id, geometry, reason)
        if not legal:
            assert "token-lane disagreement" in (reason or "")
