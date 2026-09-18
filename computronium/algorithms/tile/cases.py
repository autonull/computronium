"""Deterministic test cases for TileNet algorithm.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

from dataclasses import dataclass
from typing import Any

import torch

from computronium.ontology.geometry import GeometryConfig, TileGeometry


@dataclass(frozen=True, slots=True)
class Case:
    state: torch.Tensor
    target: torch.Tensor | None
    config: dict[str, Any]
    geometry: TileGeometry


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
) -> Case:
    generator = torch.Generator(device=device).manual_seed(seed)

    # Input batch of 2, feature dim 4
    state = torch.randn(2, 4, device=device, dtype=dtype, generator=generator)
    target = torch.randint(0, 4, (2,), device=device, generator=generator)

    # Create a fixed geometry for deterministic testing
    rng_state = torch.get_rng_state()
    torch.manual_seed(seed)
    try:
        tile_cfg = GeometryConfig(
            input_dim=4,
            output_dim=4,
            hidden_dims=(8,),
            num_layers=2,
            topology_type="tile_mesh",
            connectivity=None,
            recurrent_weight=None,
            init_scale=0.1,
            neurons_per_tile=4,
            tiles_per_layer=2,
        )
        geometry = TileGeometry(
            tile_cfg,
            neurons_per_tile=4,
            tiles_per_layer=2,
        )
    finally:
        torch.set_rng_state(rng_state)

    config = {
        "lr": 1e-3,
        "neurons_per_tile": 4,
        "tiles_per_layer": 2,
        "output_dim": 4,
        "seed": seed,
    }

    return Case(
        state=state,
        target=target,
        config=config,
        geometry=geometry,
    )
