"""Deterministic test cases for Spatial Lattice 3D Geometry.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

from dataclasses import dataclass
from typing import Any

import torch

from computronium.ontology.geometry import GeometryConfig, SpatialLattice3DGeometry


@dataclass(frozen=True, slots=True)
class Case:
    state: torch.Tensor
    config: dict[str, Any]
    geometry: SpatialLattice3DGeometry


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
) -> Case:
    generator = torch.Generator(device=device).manual_seed(seed)

    # Input batch of 2, feature dim 16
    input_dim = 16
    state = torch.randn(2, input_dim, device=device, dtype=dtype, generator=generator)

    # Create a fixed geometry for deterministic testing
    # Save/restore RNG state to ensure deterministic geometry creation
    rng_state = torch.get_rng_state()
    torch.manual_seed(seed)
    try:
        geometry = SpatialLattice3DGeometry(
            GeometryConfig.spatial_lattice(
                input_dim=input_dim,
                output_dim=8,
                lattice_dims=(4, 4, 4),
                hidden_dims=(16, 16),
                connectivity_radius=1,
                init_scale=0.1,
            )
        )
    finally:
        torch.set_rng_state(rng_state)

    config = {
        "input_dim": input_dim,
        "output_dim": 8,
        "lattice_dims": (4, 4, 4),
        "hidden_dims": (16, 16),
        "connectivity_radius": 1,
        "init_scale": 0.1,
        "seed": seed,
    }

    return Case(
        state=state,
        config=config,
        geometry=geometry,
    )
