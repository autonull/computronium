"""Graph geometry batched-input lock (TODO88 G9/R7).

A graph task hands the geometry a PyG ``Batch``: node features plus that
batch's ``edge_index`` and ``batch`` vector. Two paths ignored that contract.

1. ``forward_with_intermediates`` never entered the batched scope, so the act
   stack aggregated over the geometry's static edge list and the head saw
   node-sized acts instead of pooled logits.
2. ``_batched`` sized the degree vector from ``edge_index.max() + 1``. PyG
   appends trailing isolated nodes after the last edge, so the degrees were
   narrower than the activations (measured: 1134 vs 1201 rows).
3. The free-phase probe fed a batch's node matrix to ``forward`` with no
   ``edge_index``, i.e. node-mode geometry over a foreign edge list — an
   out-of-bounds gather on CUDA (sticky device assert, every later CUDA cell in
   the process dies) and a caught warning on CPU.

The lock contains the case the mechanism exists for: a node whose id exceeds
the edge maximum, and a probe call that has only node rows.

Locks:
1. degrees are sized by activation rows, so a trailing isolated node keeps its
   own features instead of raising a broadcast error;
2. ``forward_with_intermediates`` equals ``forward`` in graph mode, with the
   readout pooled to one row per graph;
3. node-mode ``forward`` rejects a batched node matrix with a ``ValueError``
   naming the missing kwargs, before any kernel launch;
4. the post-training probe returns no sample input for a PyG batch.
"""

from __future__ import annotations

import pytest
import torch
from torch_geometric.data import Batch, Data

from computronium.experiment.kernel._trainer_utils import _sample_inputs
from computronium.ontology.geometry import GeometryConfig, GraphGeometry
from computronium.ontology.substrate import DigitalSubstrate

INPUT_DIM, OUTPUT_DIM = 4, 2
STATIC_EDGE_INDEX = [[0], [2]]


def _geometry() -> GraphGeometry:
    return GraphGeometry(
        GeometryConfig.graph(
            input_dim=INPUT_DIM,
            output_dim=OUTPUT_DIM,
            edge_index=STATIC_EDGE_INDEX,
            hidden_dims=(INPUT_DIM,),
        )
    )


def _identity_geometry() -> GraphGeometry:
    geometry = _geometry()
    geometry._layer_weights["layer_0"].data = torch.eye(INPUT_DIM)
    geometry._layer_biases["layer_0"].data = torch.zeros(INPUT_DIM)
    return geometry


def test_trailing_isolated_node_is_sized_by_activation_rows() -> None:
    geometry = _identity_geometry()
    x = torch.zeros(5, INPUT_DIM)
    x[0, 0] = 1.0
    # Edges stop at node 2; nodes 3 and 4 are PyG's trailing isolated nodes.
    edge_index = torch.tensor([[0, 1], [1, 2]])
    batch = torch.tensor([0, 0, 0, 1, 1])
    try:
        h = geometry.settle_blocks(
            x, DigitalSubstrate(), edge_index=edge_index, batch=batch
        )[1]
    except RuntimeError as exc:  # pragma: no cover - pre-fix regression path
        raise AssertionError(f"degrees narrower than activations: {exc}") from exc
    assert h.shape == (5, INPUT_DIM), h.shape
    assert torch.allclose(h[0], torch.tensor([1.0, 0.0, 0.0, 0.0])), h[0]
    assert torch.allclose(h[3], x[3]), h[3]
    assert torch.allclose(h[4], x[4]), h[4]


def test_forward_with_intermediates_matches_forward_on_a_batch() -> None:
    geometry = GraphGeometry(
        GeometryConfig.graph(
            input_dim=INPUT_DIM,
            output_dim=OUTPUT_DIM,
            edge_index=STATIC_EDGE_INDEX,
            hidden_dims=(8, 8),
        )
    )
    generator = torch.Generator().manual_seed(0)
    x = torch.randn(6, INPUT_DIM, generator=generator)
    edge_index = torch.tensor([[0, 1, 2, 3, 4], [1, 2, 3, 4, 0]])
    batch = torch.tensor([0, 0, 0, 1, 1, 1])
    substrate = DigitalSubstrate()

    acts = geometry.forward_with_intermediates(
        x, substrate, edge_index=edge_index, batch=batch
    )
    logits = geometry.forward(x, substrate, edge_index=edge_index, batch=batch)
    assert len(acts) == len(geometry.config.hidden_dims) + 2, len(acts)
    assert acts[-1].shape == (2, OUTPUT_DIM), acts[-1].shape
    assert torch.allclose(acts[-1], logits, atol=1e-6)


def test_node_mode_forward_rejects_batched_rows() -> None:
    geometry = _geometry()
    with pytest.raises(ValueError, match="edge_index and batch"):
        geometry(torch.randn(6, INPUT_DIM))


def test_probe_skips_graph_batch_inputs() -> None:
    batch = Batch.from_data_list([
        Data(x=torch.randn(3, INPUT_DIM), edge_index=torch.tensor([[0, 1], [1, 2]])),
        Data(x=torch.randn(4, INPUT_DIM), edge_index=torch.tensor([[0, 1], [1, 2]])),
    ])

    class _GraphTask:
        def get_dataloader(self, split: str):
            return [batch]

    sample_x, sample_count = _sample_inputs(_GraphTask(), "cpu")
    assert sample_x is None
    assert sample_count == 2, sample_count


def test_probe_returns_flattened_rows_for_a_tensor_batch() -> None:
    batch = torch.randn(8, 1, 6, 6)

    class _VisionTask:
        def get_dataloader(self, split: str):
            return [batch]

    sample_x, sample_count = _sample_inputs(_VisionTask(), "cpu")
    assert sample_x is not None
    assert sample_x.shape == (8, 36), sample_x.shape
    assert sample_count == 8, sample_count
