"""T20.8.2 parity: standalone PsiReadout math == internal TemporalPsiPlasticity."""

from __future__ import annotations

import torch
from psi_peft.readout import PsiReadout

import computronium.core.plasticity.temporal_psi as internal

FEATURE_DIM, NUM_CLASSES = 12, 3


def test_ridge_solution_parity() -> None:
    gen = torch.Generator().manual_seed(0)
    h1 = torch.randn(64, FEATURE_DIM, generator=gen)
    y1 = torch.randint(0, NUM_CLASSES, (64,), generator=gen)
    h2 = torch.randn(64, FEATURE_DIM, generator=gen)
    y2 = torch.randint(0, NUM_CLASSES, (64,), generator=gen)

    standalone = PsiReadout(
        FEATURE_DIM, NUM_CLASSES, trace_decay=0.7, ridge_lambda=1e-3
    )
    standalone.update(h1, y1)
    standalone.update(h2, y2)
    assert standalone.readout is not None
    m_standalone, b_standalone = standalone.readout

    # Internal math: decayed accumulate + solve_trace_readout per episode.
    psi: dict[str, torch.Tensor] = {}
    for h, y in ((h1, y1), (h2, y2)):
        ones = torch.ones(h.shape[0], 1)
        h_aug = torch.cat((h, ones), dim=-1)
        onehot = torch.nn.functional.one_hot(y, NUM_CLASSES).float()
        gram, cross = internal.decayed(
            h_aug.T @ h_aug, h_aug.T @ (onehot - 0.5), psi, 0.7
        )
        psi = internal.solve_trace_readout(psi, gram, cross, 1e-3)

    assert torch.allclose(m_standalone, psi["readout_m"], atol=1e-5)
    assert torch.allclose(b_standalone, psi["readout_b"], atol=1e-5)


def test_conflict_adaptive_semantics_parity() -> None:
    """Adaptive arm's agreement gate mirrors ConflictAdaptivePsiPlasticity ρ rule."""
    from psi_peft.adaptive import AdaptivePsiReadout

    gen = torch.Generator().manual_seed(0)
    task_h = torch.randn(64, FEATURE_DIM, generator=gen)
    task_y = torch.randint(0, NUM_CLASSES, (64,), generator=gen)
    readout = AdaptivePsiReadout(FEATURE_DIM, NUM_CLASSES, conflict_threshold=0.6)
    readout.update(task_h, task_y)
    assert readout.last_rho == readout.forget_decay  # warm-up = conflict
