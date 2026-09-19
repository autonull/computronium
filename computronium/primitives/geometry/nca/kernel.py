"""Accelerated kernel for NCA Geometry.

Delegates to computronium.ontology.geometry.NcaGeometry with triton
acceleration. Provides uniform `forward(case)` interface.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def forward(case: Any) -> Any:
    """Execute one accelerated forward pass using the opaque case object."""
    if not is_available():
        from .reference import forward as reference_forward

        return reference_forward(case)

    # Use accelerated implementation
    import torch

    from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig

    # Use pre-created geometry from case for determinism
    geometry = case.geometry

    # Get input
    x = case.state

    # Get substrate
    substrate = DigitalSubstrate(SubstrateConfig.digital(device=x.device))

    # Run with deterministic RNG state
    rng_state = torch.get_rng_state()
    torch.manual_seed(case.config.get("seed", 0))
    try:
        output = geometry(x, substrate)
    finally:
        torch.set_rng_state(rng_state)

    return output


# Alias for the central registry test which expects `step`
step = forward
