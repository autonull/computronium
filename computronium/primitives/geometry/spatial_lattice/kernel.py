"""Accelerated kernel for Spatial Lattice 3D Geometry.

Delegates to computronium.ontology.geometry.SpatialLattice3DGeometry with triton acceleration.
Provides uniform `forward(case)` interface.
"""

from computronium.acceleration.backends import kernel_available
from computronium.harness import seeded_rng
from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def forward(case):
    """Execute accelerated forward pass using the opaque case object."""
    if not is_available():
        from .reference import forward as reference_forward

        return reference_forward(case)

    # Use pre-created geometry from case for determinism
    geometry = case.geometry

    # Get input
    x = case.state

    # Get substrate
    device = case.state.device
    substrate = DigitalSubstrate(SubstrateConfig.digital(device=device))

    # Run forward with deterministic RNG state
    with seeded_rng(case.config.get("seed", 0)):
        output = geometry(x, substrate)

    return output


# Alias for the central registry test which expects `step`
step = forward
