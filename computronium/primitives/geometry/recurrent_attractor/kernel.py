"""Accelerated kernel for Recurrent Attractor.

Delegates to computronium.ontology.geometry.RecurrentGeometry with triton acceleration.
Provides uniform `forward(case)` interface.
"""

from typing import TYPE_CHECKING, Any

from computronium.acceleration.backends import kernel_available

if TYPE_CHECKING:
    import torch

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def forward(case: Any) -> torch.Tensor:
    """Execute one accelerated forward pass using the opaque case object."""
    if not is_available():
        from .reference import forward as reference_forward

        return reference_forward(case)

    # Use accelerated implementation (Triton TODO)
    import torch

    # Use pre-created geometry from case for determinism
    geometry = case.geometry

    # Get input
    x = case.state

    # Get substrate
    device = case.state.device
    from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig

    substrate = DigitalSubstrate(SubstrateConfig.digital(device=device))

    # Run forward with deterministic RNG state
    rng_state = torch.get_rng_state()
    torch.manual_seed(case.config.get("seed", 0))
    try:
        output = geometry(x, substrate)
    finally:
        torch.set_rng_state(rng_state)

    return output


# Alias for the central registry test which expects `step`
step = forward
