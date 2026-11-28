"""Lock: the flattened input contract, both directions (TODO108 W48).

A task may report its input as a width or a spatial shape. ``flat_input_dim``
is the one reduction every MLP geometry is sized by, and ``resolve_task`` must
report the same number ``math.prod`` gives, so a spatial task and a flat task
cannot size the same geometry differently.
"""

from __future__ import annotations

import math

import pytest

from computronium.domains.base import flat_input_dim
from computronium.domains.factory import create_task
from computronium.domains.registry import resolve_task

_TASK_FAMILIES = (
    "digits",  # vision, flat 8x8
    "optical_mnist_sim",  # photonic vision, 784
    "diabetes",  # tabular regression
    "char_ngram",  # language tokens
    "copy_task",  # memory/sequence
    "lorenz_state",  # scientific ODE
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (784, 784),  # already flat
        ((3, 28, 28), 2352),  # channels-first image
        ((28, 28), 784),  # bare image
        ([4, 4], 16),  # list form
    ],
)
def test_flat_input_dim_reduces_width_and_shape(value, expected: int) -> None:
    assert flat_input_dim(value, "task") == expected


@pytest.mark.parametrize("value", [None, ("a", 4), 3.5])
def test_flat_input_dim_refuses_what_it_cannot_size(value) -> None:
    with pytest.raises(ValueError):
        flat_input_dim(value, "task")


def test_resolved_width_is_the_flattened_shape() -> None:
    """``resolve_task`` and ``flat_input_dim`` agree on every task family."""
    for name in _TASK_FAMILIES:
        task = create_task(name, device="cpu", quick_mode=True)
        task.setup()
        spec = resolve_task(name)
        assert spec.input_dim == flat_input_dim(task.input_dim, task.name), name
        assert spec.input_dim == math.prod(
            task.input_dim if isinstance(task.input_dim, tuple) else (task.input_dim,)
        ), name
