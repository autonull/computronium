"""Conflict-adaptive ψ plasticity: self-switching trace decay (TODO19 R7).

Like TemporalPsiPlasticity the law accumulates trace-decayed ridge
sufficient statistics on the NUDGED-phase settle, but ρ is NOT configured
per task phase — the law detects fit conflict from its own readout:

    a_t = mean(argmax(h_t @ M_{t−1} + b_{t−1}) == y_t)
    ρ_t = forget_decay if a_t < conflict_threshold else 1.0
    G_t = ρ_t·G_{t−1} + HᵀH,  C_t = ρ_t·C_{t−1} + Hᵀ(onehot(y) − ½)

While the current readout agrees with the incoming targets (a_t high) the
trace accumulates forget-free (ρ = 1, full data weight). The moment the
targets disagree (label-geometry flip, new mapping on the same frozen h)
agreement collapses below the threshold and ρ drops to ``forget_decay`` —
the law forgets on its own, then stops forgetting once re-acquired. No
task boundaries are handed in; ψ keys add ``agreement``/``rho_used`` for
inspection.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

import torch
from torch import Tensor

from computronium.core.identity_card import AlgorithmIdentityCard
from computronium.core.plasticity.temporal_psi import (
    TemporalPsiPlasticity,
    apply_readout,
    decayed,
    solve_trace_readout,
)

if TYPE_CHECKING:
    from computronium.core.joint.transition import PlasticityConfig
    from computronium.state import CompositeState, SystemContext


@dataclass(frozen=True, slots=True)
class ConflictAdaptivePsiConfig:
    """Agreement-driven trace decay.

    ``conflict_threshold``: mean readout agreement below this marks the
    incoming stream as conflicting → fast forgetting. ``forget_decay``: the
    ρ used while conflicting (acquisition is also conflicting — no readout
    yet — so it runs at this ρ too).
    """

    conflict_threshold: float = 0.65
    forget_decay: float = 0.5
    ridge_lambda: float = 1e-3
    replace_readout: bool = True


class ConflictAdaptivePsiPlasticity(TemporalPsiPlasticity):
    """ψ = ridge readout whose trace decay is driven by detected conflict.

    Subclasses TemporalPsiPlasticity for ``_stats``/``modulate``; ``step``
    chooses ρ_t from the current batch's readout agreement before the
    trace update. ψ keys: temporal keys plus ``agreement``/``rho_used``.
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="ConflictAdaptivePsiPlasticity",
        reference_equations=(
            "a_t = mean(argmax(h@M_{t−1} + b_{t−1}) == y); "
            "ρ_t = forget_decay if a_t < threshold else 1.0; "
            "G_t = ρ_tG_{t−1} + HᵀH; C_t = ρ_tC_{t−1} + Hᵀ(onehot(y) − ½); "
            "M_t = (G_t + λ·mean(diag G_t)·I)⁻¹C_t; o' = M-corrected readout"
        ),
        deviations_from_literature=(
            "conflict detected from readout agreement, not task boundaries — "
            "no oracle switch signal is handed in",
            "warm-up episodes (no readout yet) count as conflicting: "
            "acquisition always runs at forget_decay",
            "single-pass exponentially-decayed ridge — no optimality claim",
        ),
        objective_function="agreement-gated trace-weighted ridge fit of "
        "centered one-hot targets from settled h",
        pseudo_gradient_def="none — no gradient path; ψ is a deterministic "
        "function of (ψ_{t−1}, activity, target)",
        symmetry_requirements=(
            "G symmetric PSD by construction; solve is exact (torch.linalg.solve)",
        ),
        approximation_parameters=(
            "conflict_threshold=0.65",
            "forget_decay=0.5",
            "ridge_lambda=1e-3",
            "replace_readout=True",
        ),
        validated_limits=(
            "quick-budget CPU probes (3 seeds, MNIST frozen-backbone "
            "alternating-task streams); binary readout tasks",
        ),
    )

    config: ConflictAdaptivePsiConfig

    def __init__(self, config: ConflictAdaptivePsiConfig | None = None):
        self.config = config or ConflictAdaptivePsiConfig()

    def step(
        self,
        psi: dict[str, Tensor],
        z: CompositeState,
        context: SystemContext,
    ) -> dict[str, Tensor]:
        h = z.activity.get("h")
        target = z.activity.get("target")
        if not (isinstance(h, Tensor) and isinstance(target, Tensor)):
            return psi
        m = psi.get("readout_m")
        if m is None:
            agreement = 0.0
        else:
            logits = h.detach().float() @ m.detach().float()
            if (bias := psi.get("readout_b")) is not None:
                logits += bias.detach().float()
            agreement = (logits.argmax(-1) == target).float().mean().item()
        rho = (
            self.config.forget_decay
            if agreement < self.config.conflict_threshold
            else 1.0
        )
        stats = self._stats(z)
        if stats is None:
            return psi
        out = solve_trace_readout(
            psi, *decayed(*stats, psi, rho), self.config.ridge_lambda
        )
        out["agreement"] = torch.tensor(agreement)
        out["rho_used"] = torch.tensor(rho)
        return out

    def modulate(
        self, activations: list[Tensor] | Tensor, psi: dict[str, Tensor]
    ) -> list[Tensor] | Tensor:
        return apply_readout(activations, psi, self.config.replace_readout)


def create_conflict_adaptive_psi_plasticity(
    conflict_threshold: float = 0.65,
    forget_decay: float = 0.5,
    ridge_lambda: float = 1e-3,
    replace_readout: bool = True,
) -> ConflictAdaptivePsiPlasticity:
    return ConflictAdaptivePsiPlasticity(
        ConflictAdaptivePsiConfig(
            conflict_threshold=conflict_threshold,
            forget_decay=forget_decay,
            ridge_lambda=ridge_lambda,
            replace_readout=replace_readout,
        )
    )


def conflict_adaptive_from_config(
    config: PlasticityConfig,
) -> ConflictAdaptivePsiPlasticity:
    """Instantiate from a ``PlasticityConfig`` (plasticity_type="conflict_adaptive")."""
    if config.plasticity_type != "conflict_adaptive":
        raise ValueError(
            f"Expected conflict_adaptive config, got {config.plasticity_type}"
        )
    raw = config.consolidation_config or {}
    return ConflictAdaptivePsiPlasticity(
        ConflictAdaptivePsiConfig(
            conflict_threshold=cast("float", raw.get("conflict_threshold", 0.65)),
            forget_decay=cast("float", raw.get("forget_decay", 0.5)),
            ridge_lambda=cast("float", raw.get("ridge_lambda", 1e-3)),
            replace_readout=cast("bool", raw.get("replace_readout", True)),
        )
    )
