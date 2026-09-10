"""Probe (TODO18 round 14): WHY lemma cells are inert on the settle coordinate.

The 5.1 mechanistic study headline: lemma credit cells show ~zero descent
quality at matched norms on the vertical-slice coordinate (recurrent
geometry + EnergyMinimization settle). Hypothesis under test — the
inertness is a COORDINATE mismatch, not a wiring defect: LEMMA's closed
form routes the output differential e₁ through fixed random inverse
projections under the assumption of a one-pass layer-local computation;
on a settle coordinate the phases/geometry it assumes do not hold, so the
pseudo-gradient should be nearly orthogonal to the true free-loss descent
direction. Control: the same credits on a feedforward + Instantaneous
coordinate, where layer-local closed forms are in-regime.

Pre-registered predictions (written before measurement):
- P1: lemma per-layer cos(pseudo-grad, ∇ free loss) ≈ 0 on the settle
  coordinate at every layer (TODO15 §12: cos ≈ 0 including readout).
- P2: bp (GradientCredit) cos ≈ 1 on both coordinates (sanity anchor).
- P3: on the feedforward/instantaneous control, lemma cos is materially
  above 0 (>> settle-coordinate cos) — if it is ALSO ≈ 0 there, the
  defect is in the lemma path itself, not the coordinate.

Verdict (2026-09-10): P1 confirmed, P3 FALSIFIED — the coordinate-mismatch
hypothesis is dead. Mean per-layer cos(pseudo-grad, ∇ free loss) over 3
seeds:
- lemma: +0.003/+0.086/+0.000 on recurrent/energy_min; −0.010/+0.107 on
  feedforward/instantaneous — ≈ 0 on BOTH coordinates.
- ff: +0.43..0.47 (settle) and +0.44..0.53 (instant) — healthy everywhere.
- bp: +1.000 everywhere (sanity anchor P2 holds).
- eqprop: +0.70/+0.55 on its own settle coordinate; ≈0 on the first layer
  of the instantaneous control (FREE == NUDGED there, so the contrastive
  difference collapses — expected, not a defect).

Conclusion: the 5.1 lemma-cell inertness is the LEMMA closed form's own
directional quality (fixed random inverse projections produce a
pseudo-gradient orthogonal to the true descent direction), NOT a settle-
coordinate mismatch and NOT a wiring defect. Consistent with TODO15 §12
(cos ≈ 0 at every layer) and with the 5.1 record's near-zero
improvement_per_norm. The lemma-on-settle direction stays closed until
the projection structure itself changes (e.g. learned-B — already
measured worse, 0.107 vs 0.306 on the Muon boundary record).

Usage: uv run python scripts/probes/lemma_settle_inertness.py
"""

from __future__ import annotations

import torch
from torch import Tensor

from computronium.core.pipeline import forward_pass, task_loss
from computronium.core.system_trainer.factory import compose_system_from_configs
from computronium.ontology import Phase, SystemState
from computronium.ontology.credit import CreditAssignmentConfig
from computronium.ontology.dynamics import StateDynamicsConfig
from computronium.ontology.geometry import GeometryConfig
from computronium.ontology.substrate import SubstrateConfig

_INPUT_DIM, _HIDDEN_DIM, _OUTPUT_DIM, _BATCH = 16, 24, 4, 16


def _system(credit_cfg, *, settle: bool, seed: int):
    from computronium.ontology import ParameterUpdateConfig

    torch.manual_seed(seed)
    return compose_system_from_configs(
        substrate=SubstrateConfig(
            precision="float32",
            noise_level=0.0,
            weight_bounds=None,
            sparsity=0.0,
            device="cpu",
        ),
        geometry=(
            GeometryConfig.recurrent(
                input_dim=_INPUT_DIM,
                output_dim=_OUTPUT_DIM,
                hidden_dims=(_HIDDEN_DIM,),
                init_scale=0.1,
            )
            if settle
            else GeometryConfig.feedforward(
                input_dim=_INPUT_DIM,
                output_dim=_OUTPUT_DIM,
                hidden_dims=(_HIDDEN_DIM,),
                init_scale=0.1,
            )
        ),
        dynamics=(
            StateDynamicsConfig.energy_minimization(
                max_steps=10,
                convergence_threshold=1e-4,
                convergence_start=5,
                step_size=0.1,
                beta=0.5,
                track_free_energy_per_iter=False,
            )
            if settle
            else StateDynamicsConfig.instantaneous()
        ),
        credit=credit_cfg,
        update=ParameterUpdateConfig.euclidean(step_size=0.05),
    )


def _true_grad(system, x: Tensor, y: Tensor) -> list[Tensor]:
    """Autograd ∇ of task loss at the settled output w.r.t. geometry params."""
    state = SystemState(x=x, y=y)
    state.activations = forward_pass(system.substrate, system.geometry, x)
    settled = system.dynamics.settle(state, system.geometry, system.substrate)
    loss = task_loss(settled, y)
    names = list(system.geometry.params)
    grads = torch.autograd.grad(loss, [system.geometry.params[n] for n in names])
    # credits emit weight-matrix pseudo-gradients only (H2: bias deltas 0.0);
    # compare against the matrix entries of the true gradient.
    return [g for n, g in zip(names, grads, strict=True) if g.dim() == 2]


def _phased_pseudo_grad(system, x: Tensor, y: Tensor) -> list[Tensor]:
    credit = system.credit
    initial = forward_pass(system.substrate, system.geometry, x)
    states = {}
    for phase in credit.phases:
        state = SystemState(x=x, y=y)
        state.activations = initial
        target = y if phase is Phase.NUDGED else None
        settled = system.dynamics.settle(
            state, system.geometry, system.substrate, target=target
        )
        if phase is Phase.NUDGED:
            settled.loss = task_loss(settled, y)
        settled.energy = system.dynamics.compute_energy(settled, system.geometry)
        states[phase] = settled
    return credit.compute_pseudo_gradient(states, y, system.geometry)


def _cosines(a: list[Tensor], b: list[Tensor]) -> list[float]:
    # pair by shape (some credits emit a subset of the weight matrices,
    # e.g. eqprop skips the recurrent matrix)
    by_shape = {}
    for t in b:
        by_shape.setdefault(tuple(t.shape), t)
    out = []
    for g in a:
        t = by_shape.get(tuple(g.shape))
        if t is None:
            out.append(float("nan"))
            continue
        gn, tn = g.detach().norm(), t.detach().norm()
        out.append(
            float("nan") if gn == 0 or tn == 0 else float((g * t).sum() / (gn * tn))
        )
    return out


def main() -> None:
    coords = (
        ("recurrent/energy_min", True),
        ("feedforward/instantaneous", False),
    )
    credit_cfgs = {
        "bp": CreditAssignmentConfig.gradient,
        "lemma": lambda: CreditAssignmentConfig.local_goodness(local_objective="lemma"),
        "ff": lambda: CreditAssignmentConfig.local_goodness(local_objective="ff"),
        "eqprop": CreditAssignmentConfig.thermodynamic_contrast,
    }
    for coord, settle in coords:
        for name, cfg in credit_cfgs.items():
            seed_cos = []
            for seed in (0, 1, 2):
                system = _system(cfg(), settle=settle, seed=seed)
                g = torch.Generator().manual_seed(seed * 77 + 1)
                x = torch.randn(_BATCH, _INPUT_DIM, generator=g)
                y = torch.randint(0, _OUTPUT_DIM, (_BATCH,), generator=g)
                pg = (
                    _true_grad(system, x, y)
                    if name == "bp"
                    else _phased_pseudo_grad(system, x, y)
                )
                tg = _true_grad(system, x, y)
                seed_cos.append(_cosines(pg, tg))
            n_layers = max(len(c) for c in seed_cos)
            means = [
                sum(c[i] for c in seed_cos if i < len(c) and c[i] == c[i])
                / max(1, sum(1 for c in seed_cos if i < len(c) and c[i] == c[i]))
                for i in range(n_layers)
            ]
            print(
                f"{coord} x {name}: mean cos per layer (3 seeds) = {[f'{c:+.3f}' for c in means]}"
            )


if __name__ == "__main__":
    main()
