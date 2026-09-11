"""Shared temporal-ψ ridge math — the single implementation copy (Rule 6).

Used by ``psi_peft.readout`` (standalone surface) and by Computronium's
internal ``TemporalPsiPlasticity`` (ontology surface). Parity is
structural, not tested: both call sites import these functions.
"""

from __future__ import annotations

import torch
from torch import Tensor


def decayed(
    gram: Tensor, cross: Tensor, prev: dict[str, Tensor], rho: float
) -> tuple[Tensor, Tensor]:
    """Apply trace decay ρ to the previous sufficient statistics.

    ρ=1 is the forget-free limit: plain accumulation without decay.
    """
    if (prev_gram := prev.get("gram")) is not None:
        gram = gram + prev_gram if rho == 1.0 else gram + rho * prev_gram
    if (prev_cross := prev.get("cross")) is not None:
        cross = cross + prev_cross if rho == 1.0 else cross + rho * prev_cross
    return gram, cross


def solve_trace_readout(
    psi: dict[str, Tensor], gram: Tensor, cross: Tensor, ridge_lambda: float
) -> dict[str, Tensor]:
    """Solve the ridge readout from (already accumulated) statistics."""
    d = gram.shape[0]
    lam = ridge_lambda * gram.diagonal().mean().clamp_min(1e-12)
    m_aug = torch.linalg.solve(gram + lam * torch.eye(d, device=gram.device), cross)
    return {
        "gram": gram,
        "cross": cross,
        "readout_m": m_aug[:-1],
        "readout_b": m_aug[-1],
        "trace_steps": torch.tensor(
            psi.get("trace_steps", torch.zeros(())).item() + 1.0
        ),
    }
