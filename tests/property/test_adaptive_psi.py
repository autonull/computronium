"""Property tests for ConflictAdaptivePsiPlasticity (TODO19 R7 primitive).

Properties:
- Consistent stream: once the readout agrees with targets, ρ_t = 1 (the
  trace accumulates forget-free — nothing is forgotten that shouldn't be).
- Conflict flip: agreement collapses and ρ_t drops to forget_decay
  WITHOUT any task boundary being handed in.
- Warm-up: the first episodes (no readout yet) run at forget_decay.
- After a flip the law re-acquires and returns to ρ_t = 1.
- modulate/replace semantics match TemporalPsiPlasticity.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import torch

from computronium.core.joint import CompositeState
from computronium.core.plasticity.adaptive_psi import (
    ConflictAdaptivePsiConfig,
    ConflictAdaptivePsiPlasticity,
    create_conflict_adaptive_psi_plasticity,
)

if TYPE_CHECKING:
    from torch import Tensor


B, H, C = 32, 16, 2


def _z(h: Tensor, logits: Tensor, target: Tensor | None) -> CompositeState:
    activity: dict[str, Tensor] = {"x": h, "h": h, "y": logits}
    if target is not None:
        activity["target"] = target
    return CompositeState(activity=activity, plastic={}, substrate={})


def _consistent_batch(seed: int, invert: bool = False) -> CompositeState:
    """Fixed linear mapping h→label (labels = sign of first coord, or inv)."""
    g = torch.Generator().manual_seed(seed)
    h = torch.randn(B, H, generator=g)
    y = (h[:, 0] > 0).long()
    if invert:
        y = 1 - y
    return _z(h, torch.zeros(B, C), y)


def _run_phases(law, phases: list[tuple[int, bool]]) -> dict[str, Tensor]:
    psi: dict[str, Tensor] = {}
    for seed, invert in phases:
        psi = law.step(psi, _consistent_batch(seed, invert), context=None)  # type: ignore[arg-type]
    return psi


def test_warmup_runs_at_forget_decay() -> None:
    law = create_conflict_adaptive_psi_plasticity(
        forget_decay=0.5, conflict_threshold=0.55
    )
    psi = law.step({}, _consistent_batch(0), context=None)  # type: ignore[arg-type]
    assert psi["rho_used"].item() == 0.5  # no readout yet → conflicting
    assert psi["agreement"].item() == 0.0


def test_consistent_stream_returns_to_rho_one() -> None:
    law = create_conflict_adaptive_psi_plasticity(
        forget_decay=0.5, conflict_threshold=0.55
    )
    psi = _run_phases(law, [(0, False), (1, False), (2, False)])
    assert psi["rho_used"].item() == 1.0
    assert psi["agreement"].item() > law.config.conflict_threshold


def test_conflict_flip_switches_decay_without_boundaries() -> None:
    law = create_conflict_adaptive_psi_plasticity(
        forget_decay=0.5, conflict_threshold=0.55
    )
    psi = _run_phases(law, [(0, False), (1, False)])
    assert psi["rho_used"].item() == 1.0
    psi = law.step(psi, _consistent_batch(2, invert=True), context=None)  # type: ignore[arg-type]
    assert psi["agreement"].item() < law.config.conflict_threshold
    assert psi["rho_used"].item() == 0.5
    # ...and re-acquires: agreement recovers, forgetting switches off.
    psi = _run_phases(law, [(3, True), (4, True), (5, True)])
    assert psi["rho_used"].item() == 1.0
    assert psi["agreement"].item() > law.config.conflict_threshold


def test_conflict_trace_tracks_recent_task_beyond_forget_free() -> None:
    """Two all-y=1 batches then two all-y=0 batches: the adaptive trace
    carries strictly more post-flip label mass than the forget-free law —
    the forgetting lever fires exactly at the detected conflict."""

    def uniform_z(seed: int, label: int) -> CompositeState:
        g = torch.Generator().manual_seed(seed)
        h = torch.randn(B, H, generator=g)
        y = torch.full((B,), label, dtype=torch.long)
        return _z(h, torch.zeros(B, C), y)

    phases = [(0, 1), (1, 1), (2, 0), (3, 0)]
    adaptive = ConflictAdaptivePsiPlasticity(
        ConflictAdaptivePsiConfig(forget_decay=0.5, conflict_threshold=0.55)
    )
    forget_free = ConflictAdaptivePsiPlasticity(
        ConflictAdaptivePsiConfig(forget_decay=1.0, conflict_threshold=0.55)
    )

    def bias_row(law) -> float:
        psi: dict[str, Tensor] = {}
        for seed, label in phases:
            psi = law.step(psi, uniform_z(seed, label), context=None)  # type: ignore[arg-type]
        row = psi["cross"][-1]
        return (row[0] - row[1]).item()

    assert bias_row(adaptive) > bias_row(forget_free)


def test_modulate_matches_temporal_semantics() -> None:
    law = create_conflict_adaptive_psi_plasticity()
    acts = [torch.randn(B, H), torch.randn(B, C)]
    assert law.modulate(acts, {}) is acts
    psi = _run_phases(law, [(0, False), (1, False)])
    before = acts[-1].clone()
    out = law.modulate(acts, psi)
    assert isinstance(out, list)
    assert not torch.equal(out[-1], before)
    assert torch.equal(out[-2], acts[-2])
    with pytest.raises(TypeError):
        create_conflict_adaptive_psi_plasticity(bogus=1)  # type: ignore[call-arg]
    assert law.config == ConflictAdaptivePsiConfig()
