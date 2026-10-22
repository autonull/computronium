"""Shared utilities for primitive implementations.

Provides common Case dataclass, case construction utilities, and reference
wrappers to eliminate boilerplate across primitives.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import torch

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Mapping

    from computronium.ontology.geometry import Geometry


@dataclass(frozen=True, slots=True)
class PrimitiveCase:
    """Base case for primitive test harness.

    Attributes:
        weights: List of weight tensors (one per learnable layer).
        free_activations: Activations from the free phase.
        nudged_activations: Activations from the nudged phase.
        config: Primitive-specific configuration dict.
        geometry: The geometry the case runs against.
    """

    weights: list[torch.Tensor]
    free_activations: list[torch.Tensor]
    nudged_activations: list[torch.Tensor]
    config: dict[str, Any]
    geometry: Geometry


@dataclass(frozen=True, slots=True)
class ActivationPrimitiveCase:
    """Case for primitives using state/activations/nudged_activations structure.

    Attributes:
        state: Input state tensor.
        activations: Free phase activations.
        nudged_activations: Nudged phase activations.
        config: Primitive-specific configuration dict.
        geometry: The geometry the case runs against.
    """

    state: torch.Tensor
    activations: list[torch.Tensor]
    nudged_activations: list[torch.Tensor]
    config: dict[str, Any]
    geometry: Geometry


def case_generator(device: str, seed: int) -> torch.Generator:
    """A generator seeded for reproducible case construction."""
    return torch.Generator(device=device).manual_seed(seed)


@contextmanager
def seeded_rng(seed: int) -> Generator[None]:
    """Seed the global RNG for the block, then restore the caller's state."""
    state = torch.get_rng_state()
    torch.manual_seed(seed)
    try:
        yield
    finally:
        torch.set_rng_state(state)


def make_primitive_case(
    *,
    geometry_factory: Callable[[], Geometry],
    config: Mapping[str, Any],
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
    batch: int = 2,
    width: int = 4,
    requires_grad: bool = False,
) -> PrimitiveCase:
    """Build a deterministic primitive case with weights/free/nudged structure.

    Args:
        geometry_factory: Builds the fixed geometry. Called under ``seeded_rng``
            so the geometry is identical for a given seed.
        config: The primitive's own hyperparameters.
        device: The device the tensors are drawn on.
        dtype: The floating dtype of the drawn tensors.
        seed: The seed for the generator, the geometry, and the config.
        batch: The number of rows in the input batch.
        width: The width of the input batch.
        requires_grad: Whether free/nudged inputs should require grad (for
            credit rules that use autograd through the settle graph).

    Returns:
        The case, with the geometry built and the config completed.
    """
    generator = case_generator(device, seed)

    with seeded_rng(seed):
        geometry = geometry_factory()

    # Extract weights for reference (only Linear layers)
    weights = [
        layer.weight.data.clone()
        for layer in geometry._layers  # type: ignore[attr-defined]
        if isinstance(layer, torch.nn.Linear)
    ]

    # Run forward pass for free activations
    free_input = torch.randn(
        batch,
        width,
        device=device,
        dtype=dtype,
        generator=generator,
        requires_grad=requires_grad,
    )
    free_activations = [free_input]
    x = free_input
    for layer in geometry._layers:  # type: ignore[attr-defined]
        x = layer(x)
        free_activations.append(x)

    # Run forward pass for nudged activations
    nudged_gen = torch.Generator(device=device).manual_seed(seed + 1)
    nudged_input = torch.randn(
        batch,
        width,
        device=device,
        dtype=dtype,
        generator=nudged_gen,
        requires_grad=requires_grad,
    )
    nudged_activations = [nudged_input]
    x_n = nudged_input
    for layer in geometry._layers:  # type: ignore[attr-defined]
        x_n = layer(x_n)
        nudged_activations.append(x_n)

    full_config = {**config, "seed": seed}

    return PrimitiveCase(
        weights=weights,
        free_activations=free_activations,
        nudged_activations=nudged_activations,
        config=full_config,
        geometry=geometry,
    )


def make_activation_primitive_case(
    *,
    geometry_factory: Callable[[], Geometry],
    config: Mapping[str, Any],
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
    batch: int = 2,
    width: int = 4,
    requires_grad: bool = True,
) -> ActivationPrimitiveCase:
    """Build a deterministic primitive case with state/activations/nudged structure.

    Args:
        geometry_factory: Builds the fixed geometry. Called under ``seeded_rng``
            so the geometry is identical for a given seed.
        config: The primitive's own hyperparameters.
        device: The device the tensors are drawn on.
        dtype: The floating dtype of the drawn tensors.
        seed: The seed for the generator, the geometry, and the config.
        batch: The number of rows in the input batch.
        width: The width of the input batch.
        requires_grad: Whether activations should require grad.

    Returns:
        The case, with the geometry built and the config completed.
    """
    generator = case_generator(device, seed)

    with seeded_rng(seed):
        geometry = geometry_factory()

    # Create state and activations with requires_grad for autograd path
    state = torch.randn(batch, width, device=device, dtype=dtype, generator=generator)
    activations = [state]
    x = state
    for layer in geometry._layers:  # type: ignore[attr-defined]
        x = layer(x)
        activations.append(x)

    # Nudged activations also need requires_grad
    _ = torch.Generator(device=device).manual_seed(seed + 1)
    nudged_activations = [state]
    x_n = state
    for layer in geometry._layers:  # type: ignore[attr-defined]
        x_n = layer(x_n)
        nudged_activations.append(x_n)

    full_config = {**config, "seed": seed}

    return ActivationPrimitiveCase(
        state=state,
        activations=activations,
        nudged_activations=nudged_activations,
        config=full_config,
        geometry=geometry,
    )


def case_to_states(case: PrimitiveCase) -> dict[str, Any]:
    """Convert a PrimitiveCase to free/nudged SystemState dict.

    Returns:
        Dict with Phase.FREE and Phase.NUDGED keys mapping to SystemState objects.
    """
    from computronium.ontology.credit import Phase
    from computronium.ontology.system import SystemState

    free_state = SystemState(
        activations=case.free_activations,
        x=case.free_activations[0],
        y=case.config.get("target"),
    )
    nudged_state = SystemState(
        activations=case.nudged_activations,
        x=case.nudged_activations[0],
        y=case.config.get("target"),
    )
    return {
        Phase.FREE: free_state,
        Phase.NUDGED: nudged_state,
    }


def activation_case_to_composite_states(
    case: ActivationPrimitiveCase,
) -> dict[str, Any]:
    """Convert an ActivationPrimitiveCase to free/nudged CompositeState dict."""
    from computronium.state import CompositeState

    free_state = CompositeState(
        activity={
            "x": case.state,
            "activations": case.activations,
        },
        plastic={},
        substrate={},
    )
    nudged_state = CompositeState(
        activity={
            "x": case.state,
            "activations": case.nudged_activations,
        },
        plastic={},
        substrate={},
    )
    return {
        "free": free_state,
        "nudged": nudged_state,
    }


def case_to_geometry(case: PrimitiveCase) -> Geometry:
    """Reconstruct a geometry from the case's weights."""
    from torch import nn

    from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig

    weight_shapes = [w.shape for w in case.weights]
    dims = (weight_shapes[0][1], *[s[0] for s in weight_shapes])
    layers = []
    for i in range(len(weight_shapes)):
        layer = nn.Linear(dims[i], dims[i + 1], bias=False)
        layer.weight.data = case.weights[i].clone()
        layers.append(layer)

    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=dims[0],
            output_dim=dims[-1],
            hidden_dims=dims[1:-1],
        ),
        layers=layers,
    )
    return geometry


def make_reference_step(
    credit_cls: type,
    config_factory: Callable[[dict[str, Any]], Any],
    *,
    case_to_states_fn: Callable[[Any], dict[str, Any]] = case_to_states,
    case_to_geometry_fn: Callable[[Any], Geometry] = case_to_geometry,
) -> Callable[[Any], list[torch.Tensor]]:
    """Create a reference step function for a credit assignment primitive.

    Args:
        credit_cls: The credit assignment class (e.g., ThermodynamicContrast).
        config_factory: Function that takes case.config and returns the
            CreditAssignmentConfig instance.
        case_to_states_fn: Function to convert case to states dict.
            Defaults to case_to_states for PrimitiveCase.
        case_to_geometry_fn: Function to convert case to geometry.
            Defaults to case_to_geometry for PrimitiveCase.

    Returns:
        A step(case) function suitable for use as a reference implementation.
    """
    from computronium.harness import seeded_rng

    def step(case: Any) -> list[torch.Tensor]:
        config = config_factory(case.config)
        credit = credit_cls(config)

        states = case_to_states_fn(case)
        geometry = case_to_geometry_fn(case)

        with seeded_rng(case.config.get("seed", 0)):
            grads = credit.compute_pseudo_gradient(states, None, geometry)

        return grads

    return step


def make_reference_step_with_loss(
    credit_cls: type,
    config_factory: Callable[[dict[str, Any]], Any],
    *,
    case_to_states_fn: Callable[[Any], dict[str, Any]],
    loss_fn: Callable[[Any], torch.Tensor],
    case_to_geometry_fn: Callable[[Any], Geometry] = lambda c: c.geometry,
) -> Callable[[Any], list[torch.Tensor]]:
    """Create a reference step function that computes loss from the case.

    Args:
        credit_cls: The credit assignment class.
        config_factory: Function that takes case.config and returns the config.
        case_to_states_fn: Function to convert case to states dict.
        loss_fn: Function that takes case and returns loss tensor.
        case_to_geometry_fn: Function to get geometry from case.

    Returns:
        A step(case) function.
    """
    from computronium.harness import seeded_rng

    def step(case: Any) -> list[torch.Tensor]:
        config = config_factory(case.config)
        credit = credit_cls(config)

        states = case_to_states_fn(case)
        geometry = case_to_geometry_fn(case)
        loss = loss_fn(case)

        with seeded_rng(case.config.get("seed", 0)):
            grads = credit.compute_pseudo_gradient(states, loss, geometry)

        return grads

    return step


def kernel_availability(family: str) -> Callable[[], bool]:
    """Create an is_available function for a kernel module.

    Args:
        family: The availability family name (e.g., "fa", "pc", "ff").

    Returns:
        An is_available() function that checks if the Triton rung compiles.
    """
    from computronium.acceleration.availability import triton_rung_available

    def is_available() -> bool:
        return triton_rung_available(family)

    return is_available
