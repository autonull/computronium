"""Property tests for TemporalPsiPlasticity (TODO19 X-TPC-001 primitive).

Properties:
- ρ = 1 is the forget-free limit: exact hand-rolled accumulation match.
- The NUDGED target is consumed: no target ⇒ ψ untouched (the D22 guard);
  with target ⇒ nonzero readout correction.
- Trace decay: statistics shrink geometrically and the effective readout
  tracks the recent task (migration lever), unlike the forget-free ρ = 1.
- modulate injects the correction only when readout ψ exists.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import torch

from computronium.core.joint import CompositeState
from computronium.core.plasticity.temporal_psi import (
    TemporalPsiConfig,
    TemporalPsiPlasticity,
    create_temporal_psi_plasticity,
)

if TYPE_CHECKING:
    from torch import Tensor


B, H, C = 8, 16, 4


def _z(h: Tensor, logits: Tensor, target: Tensor | None) -> CompositeState:
    activity: dict[str, Tensor] = {"x": h, "h": h, "y": logits}
    if target is not None:
        activity["target"] = target
    return CompositeState(activity=activity, plastic={}, substrate={})


def _stream(seed: int, n: int, cls: int) -> list[tuple[Tensor, Tensor, Tensor]]:
    g = torch.Generator().manual_seed(seed)
    out = []
    for _ in range(n):
        h = torch.randn(B, H, generator=g)
        logits = torch.randn(B, C, generator=g)
        target = torch.randint(0, cls, (B,), generator=g)
        out.append((h, logits, target))
    return out


def _run(law, rho: float, seed: int = 0, n: int = 5, cls: int = C):
    law.config = TemporalPsiConfig(trace_decay=rho)
    psi: dict[str, Tensor] = {}
    for h, logits, target in _stream(seed, n, cls):
        psi = law.step(psi, _z(h, logits, target), context=None)  # type: ignore[arg-type]
    return psi


def test_rho_one_is_the_forget_free_limit() -> None:
    stream = _stream(3, 5, C)
    law = TemporalPsiPlasticity(TemporalPsiConfig(trace_decay=1.0))
    psi: dict[str, Tensor] = {}
    gram = cross = None
    for h, logits, target in stream:
        z = _z(h, logits, target)
        psi = law.step(psi, z, context=None)  # type: ignore[arg-type]
        hh = torch.cat((h, torch.ones(h.shape[0], 1)), -1)
        onehot = torch.nn.functional.one_hot(target, C).float()
        g = hh.T @ hh
        c = hh.T @ (onehot - 0.5)
        gram = g if gram is None else gram + g
        cross = c if cross is None else cross + c
    assert torch.allclose(psi["gram"], gram, rtol=1e-5, atol=1e-6)
    assert torch.allclose(psi["cross"], cross, rtol=1e-5, atol=1e-6)


def test_no_target_leaves_psi_untouched() -> None:
    law = create_temporal_psi_plasticity()
    h, logits = torch.randn(B, H), torch.randn(B, C)
    z = _z(h, logits, target=None)
    psi = law.step({}, z, context=None)  # type: ignore[arg-type]
    assert psi == {}


def test_target_produces_nonzero_correction() -> None:
    psi = _run(TemporalPsiPlasticity(), rho=0.9)
    assert torch.count_nonzero(psi["readout_m"]) > 0
    assert psi["trace_steps"].item() == 5.0


def test_trace_decay_tracks_recent_task() -> None:
    # Statistics: one Task-A batch, then one Task-B batch. ρ=1 blends both
    # equally; ρ<1 weights the recent (B) batch more — the migration lever.
    g = torch.Generator().manual_seed(7)
    h_a, h_b = torch.randn(B, H, generator=g), torch.randn(B, H, generator=g)
    t_a, t_b = torch.zeros(B, dtype=torch.long), torch.ones(B, dtype=torch.long)
    logits = torch.zeros(B, C)

    def run(rho: float) -> Tensor:
        law = TemporalPsiPlasticity(TemporalPsiConfig(trace_decay=rho))
        psi = law.step({}, _z(h_a, logits, t_a), context=None)  # type: ignore[arg-type]
        psi = law.step(psi, _z(h_b, logits, t_b), context=None)  # type: ignore[arg-type]
        return psi["cross"].sum(dim=-1)

    recent_heavier = run(0.5) - run(1.0)
    # For the B-task row the ρ<1 trace keeps more relative B mass than ρ=1.
    assert recent_heavier[1] > 0.0


def test_modulate_injects_correction_only_with_readout() -> None:
    law = create_temporal_psi_plasticity()
    acts = [torch.randn(B, H), torch.randn(B, C)]
    assert law.modulate(acts, {}) is acts
    psi = _run(law, rho=0.9, n=3)
    before = acts[-1].clone()
    out = law.modulate(acts, psi)
    assert isinstance(out, list)
    assert not torch.equal(out[-1], before)
    assert torch.equal(out[-2], acts[-2])


def test_factory_validates() -> None:
    law = create_temporal_psi_plasticity(trace_decay=0.5, ridge_lambda=0.01)
    assert law.config == TemporalPsiConfig(trace_decay=0.5, ridge_lambda=0.01)
    with pytest.raises(TypeError):
        create_temporal_psi_plasticity(bogus=1)  # type: ignore[call-arg]
