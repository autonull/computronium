"""Lock: a structural constraint reaches the forward path (N3/G18).

``sparsity`` is the sparse substrate's defining constraint. Its forward operator
was a dense matmul behind a weight clamp, so the sparse substrate and the
digital substrate produced the same loss curve seed for seed: a substrate axis
that named no difference. The lock fixes both ends — the mask zeroes the
declared fraction, and the sparse forward differs from the digital one.

Falsified by removing ``prune_weights`` from the forward: the two operators
agree again and the second test fails.
"""

from __future__ import annotations

import torch

from computronium.ontology.substrate._substrate import (
    DigitalSubstrate,
    SparseSubstrate,
    SubstrateConfig,
)


def _weights(out_features: int = 8, in_features: int = 8) -> torch.Tensor:
    generator = torch.Generator().manual_seed(7)
    return torch.randn(out_features, in_features, generator=generator)


def test_the_declared_fraction_is_zeroed() -> None:
    substrate = SparseSubstrate(SubstrateConfig.sparse(sparsity=0.5))
    weights = _weights()

    pruned = substrate.prune_weights(weights)

    assert torch.count_nonzero(pruned) == weights.numel() // 2
    assert torch.equal(pruned != 0, torch.abs(pruned) > 0)


def test_the_sparse_forward_differs_from_the_digital_one() -> None:
    weights = _weights()
    x = torch.ones(2, weights.shape[1])

    sparse_out = SparseSubstrate(
        SubstrateConfig.sparse(sparsity=0.5)
    ).get_forward_operator()(x, weights)
    digital_out = DigitalSubstrate(SubstrateConfig.digital()).get_forward_operator()(
        x, weights
    )

    assert not torch.allclose(sparse_out, digital_out)


def test_no_declared_sparsity_leaves_the_weights_alone() -> None:
    substrate = SparseSubstrate(SubstrateConfig.sparse(sparsity=0.0))
    weights = _weights()

    assert torch.equal(substrate.prune_weights(weights), weights)
