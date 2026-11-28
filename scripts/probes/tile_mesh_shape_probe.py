"""Tile-mesh block widths for the distributed-trainer output contract."""

import torch

from computronium.ontology import GeometryConfig, TileGeometry

g = TileGeometry(
    GeometryConfig(
        input_dim=16,
        output_dim=10,
        num_layers=3,
        topology_type="tile_mesh",
        hidden_dims=(),
        connectivity=None,
        recurrent_weight=None,
    ),
    neurons_per_tile=8,
    tiles_per_layer=2,
)
print("layer_ids:", g._graph.layer_ids)
for tid, t in g._graph.tiles.items():
    print(
        tid,
        "neurons",
        t.neurons,
        "input",
        t.is_input,
        "output",
        t.is_output,
        "fwd",
        t.fwd_neighbors,
    )
print("output_projection:", g._output_projection)
print("forward:", g.forward(torch.randn(4, 16)).shape)
