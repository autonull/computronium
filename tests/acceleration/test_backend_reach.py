"""Every coordinate with an arm must *train the system it is attached to* (TODO38 §4.0).

Wiring the ``backend`` argument to a real attach (TODO38 §4 commit 0) turned the
kernel rung from decoration into a running path, and the first thing that path
did was fail. The failures were not one bug but one *class*: nine copies of a
``_extract_layers`` that looked for ``nn.Linear`` submodules the ontology's
geometries do not have, found nothing, and let each backend train a private copy
of the network — plausible metrics, weights the system never read.

:class:`computronium.acceleration.kernel_backend.linear_views` is the one
replacement, and this file is the lock that says which arms may stand. A
coordinate whose rung cannot move the composed system's parameters has **no
arm**: it runs the reference rung, says so, and the reason is recorded in
TODO38.md. An arm that trains nothing is the worst outcome available — it
reports the kernel rung's speed for the reference rung's learning.
"""

import importlib
from typing import TYPE_CHECKING

import pytest
import torch

from computronium.acceleration.coordinate import (
    DISPATCH_AXES,
    DispatchKey,
    key_of,
    select_backend_class,
)
from computronium.algorithms import _ALGORITHMS

if TYPE_CHECKING:
    from collections.abc import Callable

    from computronium.ontology import System

BATCH = 6
IN_FEATURES = 8
HIDDEN = 16
CLASSES = 4

#: Every algorithm the ontology ships a public factory for.
FACTORIES: dict[str, Callable[..., System]] = {
    name: next(
        value
        for key, value in vars(
            importlib.import_module(f"computronium.algorithms.{name}.factory")
        ).items()
        if key.startswith("create_") and key.endswith("_mlp")
    )
    for name in sorted(_ALGORITHMS)
}


def build(name: str, backend: str = "reference") -> System:
    """One algorithm's system, small enough to step in a unit test."""
    return FACTORIES[name](
        input_dim=IN_FEATURES,
        hidden_dims=(HIDDEN,),
        output_dim=CLASSES,
        backend=backend,
    )


def coordinates() -> dict[DispatchKey, str]:
    """The dispatch coordinate of every shipped algorithm, deduplicated."""
    seen: dict[DispatchKey, str] = {}
    for name in FACTORIES:
        key = key_of(build(name))
        seen.setdefault(key, name)
    return seen


def test_every_algorithm_composes_a_readable_coordinate() -> None:
    """No algorithm may name an axis the key cannot read.

    A coordinate with an empty slot is a coordinate that dispatched on a guess,
    which is what the family vocabulary was.
    """
    for key, name in coordinates().items():
        assert "" not in key, f"{name} composes an unnamed axis: {key}"


def test_no_two_distinct_coordinates_reach_one_backend() -> None:
    """A backend serves one algorithm; two coordinates reaching it is a collision.

    The decidable form of the test TODO37 could not state: two coordinates that
    the five axes cannot separate *must* share a backend, so any pair that does
    not share one has to differ in the axes its backend reads.
    """
    by_backend: dict[type, list[DispatchKey]] = {}
    for key in coordinates():
        backend = select_backend_class(key)
        if backend is not None:
            by_backend.setdefault(backend, []).append(key)
    for backend, keys in by_backend.items():
        assert len(keys) == 1, (
            f"{backend.__name__} serves {len(keys)} coordinates: "
            f"{[dict(zip(DISPATCH_AXES, k, strict=True)) for k in keys]}"
        )


@pytest.mark.parametrize("name", sorted(FACTORIES))
def test_an_arm_trains_the_system_it_is_bound_to(name: str) -> None:
    """An attached kernel rung must move the system's own parameters.

    Not "must not raise" — a rung that runs and updates a private copy of the
    network passes every test except this one.
    """
    system = build(name, backend="auto")
    backend = getattr(system, "_kernel_backend", None)
    if backend is None:
        pytest.skip(f"{name} has no attachable rung for its coordinate")

    before = {key: value.clone() for key, value in system.geometry.params.items()}
    metrics = system.train_step(
        torch.randn(BATCH, IN_FEATURES), torch.randint(0, CLASSES, (BATCH,))
    )

    moved = [
        key
        for key, value in system.geometry.params.items()
        if not torch.equal(value, before[key])
    ]
    assert moved, (
        f"{name} attached {type(backend).__name__}, which reported "
        f"{metrics} without changing any of {sorted(before)}"
    )
    assert metrics.get("loss", 0.0) > 0.0, f"{name} reported a zero loss"
