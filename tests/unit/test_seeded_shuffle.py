"""Lock: a cell's shuffle order comes from its seed, not the process RNG.

``DataLoader(shuffle=True)`` draws its permutation from the process RNG, so
concurrent cells walk each other's batches (TODO107 W32). The clone must own a
generator seeded by the cell, and must not mutate the shared task loader.
"""

from __future__ import annotations

from typing import Any

import torch
from torch.utils.data import DataLoader, RandomSampler, TensorDataset

from computronium.experiment.kernel._trainer_utils import _seeded_shuffle


def _loader() -> DataLoader:
    dataset = TensorDataset(torch.arange(64).float().unsqueeze(1), torch.arange(64))
    return DataLoader(dataset, batch_size=4, shuffle=True)


def _order(loader: Any) -> list[list[int]]:
    return [batch[1].tolist() for batch in loader]


def test_same_seed_same_order() -> None:
    loader = _loader()
    first = _order(_seeded_shuffle(loader, 7))
    torch.manual_seed(999)
    second = _order(_seeded_shuffle(loader, 7))
    assert first == second


def test_different_seed_different_order() -> None:
    loader = _loader()
    assert _order(_seeded_shuffle(loader, 7)) != _order(_seeded_shuffle(loader, 8))


def test_shared_loader_is_not_mutated() -> None:
    loader = _loader()
    sampler = loader.sampler
    assert isinstance(sampler, RandomSampler)
    generator = sampler.generator
    _seeded_shuffle(loader, 7)
    assert isinstance(loader.sampler, RandomSampler)
    assert loader.sampler.generator is generator


def test_a_non_dataloader_is_not_cloned() -> None:
    """A sequence loader has no ``dataset``; the clone may not assume one.

    Falsifiable by dropping the ``DataLoader`` check: ``_seeded_shuffle`` then
    reads ``loader.dataset`` off a time-major batch stream and the sequence
    cell fails to train at all (TODO107 W36).
    """

    class _Batches:
        sampler = RandomSampler(range(4))

    loader = _Batches()
    assert _seeded_shuffle(loader, 7) is loader
