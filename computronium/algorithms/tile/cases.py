"""Deterministic test cases for TileNet algorithm.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

import torch

from computronium.harness import AlgorithmCase, make_algorithm_case
from computronium.ontology.geometry import GeometryConfig, TileGeometry

Case = AlgorithmCase


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
) -> AlgorithmCase:
    """Build the deterministic case this algorithm's steps consume."""

    def _geometry() -> TileGeometry:
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
        return TileGeometry(
            tile_cfg,
            neurons_per_tile=4,
            tiles_per_layer=2,
        )

    return make_algorithm_case(
        geometry_factory=_geometry,
        config={
            "lr": 1e-3,
            "neurons_per_tile": 4,
            "tiles_per_layer": 2,
        },
        device=device,
        dtype=dtype,
        seed=seed,
    )
