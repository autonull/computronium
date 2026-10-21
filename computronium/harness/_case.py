"""The deterministic payloads primitive and algorithm harnesses exchange.

Every primitive and algorithm ships a ``cases`` module that builds a small
deterministic payload and a ``reference``/``kernel`` pair that consumes it.
The construction rules are the same everywhere — a seeded generator, a seeded
geometry, a config that names the seed — so they are written once here and
each harness contributes only what is specific to it.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import torch

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Mapping

    from computronium.ontology.geometry import Geometry

__all__ = [
    "AlgorithmCase",
    "DynamicsCase",
    "UpdateCase",
    "case_generator",
    "make_algorithm_case",
    "make_dynamics_case",
    "make_update_case",
    "seeded_rng",
]


@dataclass(frozen=True, slots=True)
class AlgorithmCase:
    """The payload an algorithm reference or kernel step receives.

    Attributes:
        state: Input batch of shape ``(batch, width)``.
        target: Class index each row of ``state`` is scored against.
        config: Algorithm hyperparameters, including the seed.
        geometry: The fixed geometry the step runs against.
    """

    state: torch.Tensor
    target: torch.Tensor | None
    config: dict[str, Any]
    geometry: Geometry


@dataclass(frozen=True, slots=True)
class DynamicsCase:
    """The payload a state-dynamics reference or kernel step receives.

    Attributes:
        state: The current state the dynamics settle.
        prediction: The readout the dynamics are asked to match.
        multiplier: The per-example weight of the readout in the objective.
        config: Dynamics hyperparameters, including the seed.
        geometry: The fixed geometry the step runs against.
    """

    state: torch.Tensor
    prediction: torch.Tensor
    multiplier: torch.Tensor
    config: dict[str, Any]
    geometry: Geometry


@dataclass(frozen=True, slots=True)
class UpdateCase:
    """The payload a parameter-update reference or kernel step receives.

    Attributes:
        state: The forward pass the update follows.
        prediction: The readout the update acts on.
        multiplier: The per-example weight of the readout in the objective.
        config: Update hyperparameters, including the seed.
    """

    state: torch.Tensor
    prediction: torch.Tensor
    multiplier: torch.Tensor
    config: dict[str, Any]


@contextmanager
def seeded_rng(seed: int) -> Generator[None]:
    """Seed the global RNG for the block, then restore the caller's state.

    Args:
        seed: The seed the global RNG is set to for the duration of the block.

    Yields:
        Nothing; the block runs with a deterministic global RNG.
    """
    state = torch.get_rng_state()
    torch.manual_seed(seed)
    try:
        yield
    finally:
        torch.set_rng_state(state)


def case_generator(device: str, seed: int) -> torch.Generator:
    """A generator seeded for reproducible case construction.

    Args:
        device: The device the generator draws on.
        seed: The seed to draw from.

    Returns:
        A seeded ``torch.Generator``.
    """
    return torch.Generator(device=device).manual_seed(seed)


def make_algorithm_case(
    *,
    geometry_factory: Callable[[], Geometry],
    config: Mapping[str, Any],
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
    batch: int = 2,
    width: int = 4,
) -> AlgorithmCase:
    """Build the deterministic case an algorithm harness consumes.

    Args:
        geometry_factory: Builds the fixed geometry. It is called under
            ``seeded_rng`` so the geometry is identical for a given seed.
        config: The algorithm's own hyperparameters.
        device: The device the tensors are drawn on.
        dtype: The floating dtype of the drawn tensors.
        seed: The seed for the generator, the geometry, and the config.
        batch: The number of rows in the input batch.
        width: The width of the input batch and of the target range.

    Returns:
        The case, with the geometry built and the config completed.
    """
    generator = case_generator(device, seed)
    state = torch.randn(batch, width, device=device, dtype=dtype, generator=generator)
    target = torch.randint(0, width, (batch,), device=device, generator=generator)
    with seeded_rng(seed):
        geometry = geometry_factory()
    return AlgorithmCase(
        state=state,
        target=target,
        config={**config, "output_dim": width, "seed": seed},
        geometry=geometry,
    )


def make_dynamics_case(
    *,
    geometry_factory: Callable[[], Geometry],
    config: Mapping[str, Any],
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
    batch: int = 2,
    width: int = 4,
) -> DynamicsCase:
    """Build the deterministic case a state-dynamics harness consumes.

    Args:
        geometry_factory: Builds the fixed geometry. It is called under
            ``seeded_rng`` so the geometry is identical for a given seed.
        config: The dynamics' own hyperparameters.
        device: The device the tensors are drawn on.
        dtype: The floating dtype of the drawn tensors.
        seed: The seed for the generator, the geometry, and the config.
        batch: The number of rows in the batch.
        width: The width of the drawn tensors.

    Returns:
        The case, with the geometry built and the config completed.
    """
    generator = case_generator(device, seed)
    state = torch.randn(batch, width, device=device, dtype=dtype, generator=generator)
    prediction = torch.randn(
        batch, width, device=device, dtype=dtype, generator=generator
    )
    multiplier = torch.randn(
        batch, width, device=device, dtype=dtype, generator=generator
    )
    with seeded_rng(seed):
        geometry = geometry_factory()
    return DynamicsCase(
        state=state,
        prediction=prediction,
        multiplier=multiplier,
        config={**config, "seed": seed},
        geometry=geometry,
    )


def make_update_case(
    *,
    config: Mapping[str, Any],
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
    batch: int = 2,
    width: int = 4,
) -> UpdateCase:
    """Build the deterministic case a parameter-update harness consumes.

    Args:
        config: The update's own hyperparameters.
        device: The device the tensors are drawn on.
        dtype: The floating dtype of the drawn tensors.
        seed: The seed for the generator and the config.
        batch: The number of rows in the batch.
        width: The width of the drawn tensors.

    Returns:
        The case, with the config completed.
    """
    generator = case_generator(device, seed)
    state = torch.randn(batch, width, device=device, dtype=dtype, generator=generator)
    prediction = torch.randn(
        batch, width, device=device, dtype=dtype, generator=generator
    )
    multiplier = torch.randn(
        batch, width, device=device, dtype=dtype, generator=generator
    )
    return UpdateCase(
        state=state,
        prediction=prediction,
        multiplier=multiplier,
        config={**config, "seed": seed},
    )
