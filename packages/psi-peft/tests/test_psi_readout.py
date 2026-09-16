"""Unit tests for the temporal-ψ readout math."""

from __future__ import annotations

import pytest
import torch
from psi_peft.metrics import SyntheticTask
from psi_peft.readout import PsiReadout

FEATURE_DIM, NUM_CLASSES = 16, 3


def _gen(seed: int) -> torch.Generator:
    return torch.Generator().manual_seed(seed)


def test_fresh_readout_raises() -> None:
    readout = PsiReadout(FEATURE_DIM, NUM_CLASSES)
    with pytest.raises(RuntimeError, match="update"):
        readout.forward(torch.zeros(2, FEATURE_DIM))


def test_trace_decay_math_matches_manual() -> None:  # ruff: ignore[too-many-locals] mirrors the manual accumulation inline
    gen = _gen(0)
    task = SyntheticTask(gen, FEATURE_DIM, NUM_CLASSES)
    readout = PsiReadout(FEATURE_DIM, NUM_CLASSES, trace_decay=0.5)

    gram, cross = None, None
    for _ in range(3):
        h, y = task.batch(32)
        ones = torch.ones(h.shape[0], 1)
        h_aug = torch.cat((h, ones), dim=-1)
        onehot = torch.nn.functional.one_hot(y, NUM_CLASSES).float()
        g = h_aug.T @ h_aug
        c = h_aug.T @ (onehot - 0.5)
        gram = g if gram is None else g + 0.5 * gram
        cross = c if cross is None else c + 0.5 * cross
        readout.update(h, y)
    d = gram.shape[0]
    lam = 1e-3 * gram.diagonal().mean().clamp_min(1e-12)
    m_aug = torch.linalg.solve(gram + lam * torch.eye(d), cross)
    readout_m, readout_b = readout.readout  # type: ignore[misc]
    assert torch.allclose(readout_m, m_aug[:-1], atol=1e-5)
    assert torch.allclose(readout_b, m_aug[-1], atol=1e-5)


def test_rho_one_is_forget_free_limit() -> None:
    gen = _gen(1)
    task = SyntheticTask(gen, FEATURE_DIM, NUM_CLASSES)
    h, y = task.batch(64)
    readout = PsiReadout(FEATURE_DIM, NUM_CLASSES, trace_decay=1.0)
    readout.update(h, y)
    gram_1 = readout.gram.clone()
    readout.update(h, y)
    assert torch.allclose(readout.gram, 2 * gram_1, atol=1e-4)


def test_decaying_readout_tracks_current_task() -> None:
    """ρ<1 readout re-fits after a conflicting flip; ρ=1 blends toward chance."""
    gen = _gen(2)
    task = SyntheticTask(gen, FEATURE_DIM, NUM_CLASSES)
    decaying = PsiReadout(FEATURE_DIM, NUM_CLASSES, trace_decay=0.3)
    forget_free = PsiReadout(FEATURE_DIM, NUM_CLASSES, trace_decay=1.0)
    for _ in range(10):
        h, y = task.batch(64)
        decaying.update(h, y)
        forget_free.update(h, y)
    task.flip()
    for _ in range(10):
        h, y = task.batch(64)
        decaying.update(h, y)
        forget_free.update(h, y)
    h_probe, y_probe = task.batch(512)
    decaying_acc = (decaying.forward(h_probe).argmax(-1) == y_probe).float().mean()
    free_acc = (forget_free.forward(h_probe).argmax(-1) == y_probe).float().mean()
    assert decaying_acc > free_acc + 0.2


def test_reset_clears_trace() -> None:
    readout = PsiReadout(FEATURE_DIM, NUM_CLASSES)
    gen = _gen(3)
    task = SyntheticTask(gen, FEATURE_DIM, NUM_CLASSES)
    h, y = task.batch(32)
    readout.update(h, y)
    readout.reset()
    assert readout.trace_steps == 0
    assert not readout.has_readout
