"""Deterministic test cases for Fabric PC Geometry.

These cases are intentionally small. They are used for parity tests,
smoke tests, and microbenchmarks. They are not scientific benchmarks.
"""

from dataclasses import dataclass
from typing import Any

import torch

from computronium.ontology.geometry import GeometryConfig, GraphGeometry


@dataclass(frozen=True, slots=True)
class Case:
    state: torch.Tensor
    config: dict[str, Any]
    geometry: GraphGeometry


def make_case(
    *,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    seed: int = 0,
) -> Case:
    generator = torch.Generator(device=device).manual_seed(seed)

    # Graph with 5 nodes, feature dim 8
    input_dim = 8
    output_dim = 4
    num_nodes = 5
    state = torch.randn(
        num_nodes, input_dim, device=device, dtype=dtype, generator=generator
    )

    # Create a fixed graph geometry for deterministic testing
    # Simple chain graph: 0->1->2->3->4
    edge_index = [[0, 1, 2, 3], [1, 2, 3, 4]]  # 4 edges connecting 5 nodes
    rng_state = torch.get_rng_state()
    torch.manual_seed(seed)
    try:
        geometry = GraphGeometry(
            GeometryConfig.graph(
                input_dim=input_dim,
                output_dim=output_dim,
                edge_index=edge_index,
                hidden_dims=(8, 8, 8),
                init_scale=0.1,
            )
        )
    finally:
        torch.set_rng_state(rng_state)

    config = {
        "input_dim": input_dim,
        "output_dim": output_dim,
        "edge_index": edge_index,
        "hidden_dims": (8, 8, 8),
        "init_scale": 0.1,
        "seed": seed,
    }

    return Case(
        state=state,
        config=config,
        geometry=geometry,
    )
