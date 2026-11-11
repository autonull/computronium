"""Graph geometry self-connection lock (TODO88 G4).

``GraphGeometry`` aggregated with a bare neighbour mean, i.e. without the
self connection that GCN's ``(A + I)`` normalisation supplies. Two symptoms
followed: a node reachable only through outgoing edges had its own features
replaced by zero, and MUTAG training accuracy plateaued below the majority
class instead of fitting 150 graphs.

The lock contains the case the mechanism exists for: a source-only node whose
post-aggregation features must equal its own transformed features.

1. aggregation follows PyG edge order and averages ``neighbours + self``;
2. a source-only node keeps its own features and an isolated node keeps its
   own features (both are zeroed by a bare neighbour mean);
3. the graph-classification split is deterministic and label-stratified, so
   seeds vary initialization rather than which held-out graphs are scored.
"""

from __future__ import annotations

import torch

from computronium.domains.factory import _stratified_split
from computronium.ontology.geometry import GeometryConfig, GraphGeometry
from computronium.ontology.substrate import DigitalSubstrate

INPUT_DIM, OUTPUT_DIM = 4, 2
# PyG edge order: 0 -> 2. Node 0 sends, receives nothing; node 2 receives.
EDGE_INDEX = [[0], [2]]


def _geometry() -> GraphGeometry:
    geometry = GraphGeometry(
        GeometryConfig.graph(
            input_dim=INPUT_DIM,
            output_dim=OUTPUT_DIM,
            edge_index=EDGE_INDEX,
            hidden_dims=(INPUT_DIM,),
        )
    )
    geometry._layer_weights["layer_0"].data = torch.eye(INPUT_DIM)
    geometry._layer_biases["layer_0"].data = torch.zeros(INPUT_DIM)
    return geometry


def test_source_only_node_keeps_own_features() -> None:
    geometry = _geometry()
    x = torch.zeros(3, INPUT_DIM)
    x[0, 0] = 1.0
    x[1, 1] = 1.0
    h = geometry._stack(x, lambda a, w: a @ w.T)
    # Node 0 receives nothing: self connection only.
    assert torch.allclose(h[0], torch.tensor([1.0, 0.0, 0.0, 0.0])), h[0]
    # Node 1 is isolated from the edge list: self connection only.
    assert torch.allclose(h[1], torch.tensor([0.0, 1.0, 0.0, 0.0])), h[1]
    # Node 2 receives node 0 and keeps itself: mean of the two.
    assert torch.allclose(h[2], torch.tensor([0.5, 0.0, 0.0, 0.0])), h[2]


def test_settle_blocks_matches_forward() -> None:
    """The settle path must apply aggregation between layers, like forward.

    ``settle_blocks`` appended the aggregated act but kept routing the
    *pre-aggregation* relu output into the next layer, so the pipeline's
    multi-layer graph forward aggregated only the final layer. The credits
    read the act stack, so the harness trained a different (weaker) model
    than ``GraphGeometry.forward``.
    """
    geometry = GraphGeometry(
        GeometryConfig.graph(
            input_dim=INPUT_DIM,
            output_dim=OUTPUT_DIM,
            edge_index=EDGE_INDEX,
            hidden_dims=(8, 8),
        )
    )
    generator = torch.Generator().manual_seed(0)
    x = torch.randn(6, INPUT_DIM, generator=generator)
    edge_index = torch.tensor([[0, 1, 2, 3, 4, 5], [1, 2, 3, 4, 5, 0]])
    batch = torch.tensor([0, 0, 1, 1, 2, 2])
    substrate = DigitalSubstrate()
    acts = geometry.settle_blocks(x, substrate, edge_index=edge_index, batch=batch)
    logits = geometry.forward(x, edge_index=edge_index, batch=batch)
    assert torch.allclose(acts[-1], logits, atol=1e-6)
    op = substrate.get_forward_operator()
    with geometry._batched(x, edge_index, batch):
        hidden = geometry._stack(x, op)
    assert torch.allclose(acts[-2], hidden, atol=1e-6)


def test_graph_split_is_deterministic_and_stratified() -> None:
    labels = torch.tensor([0] * 20 + [1] * 60)
    train_a, val_a = _stratified_split(labels)
    train_b, val_b = _stratified_split(labels)
    assert torch.equal(train_a, train_b) and torch.equal(val_a, val_b)
    assert len(train_a) + len(val_a) == labels.numel()
    assert not set(train_a.tolist()) & set(val_a.tolist())
    val_class_zero = int((labels[val_a] == 0).sum())
    assert val_class_zero == 4, val_class_zero  # 20% of each class, not of the pool
