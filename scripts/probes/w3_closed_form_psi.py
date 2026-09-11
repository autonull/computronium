"""W3 probe: closed-form ψ adaptation — "LoRA without gradients" (TODO13b W3).

D22 mapped the ψ boundary exactly: no landed ψ law consumes a loss term
(the pipeline fed ψ the FREE-phase, target-free settle) — ψ-only could
never acquire Task B. This probe closes that gap with the landed
contract change + primitive:

- Pipeline: ``run_train_step`` steps ψ on the NUDGED settle when the
  primitive declares ``psi_phase = "nudged"``; z then carries the target
  and the pre-readout stream ``h``.
- Primitive: ``ClosedFormRidgePlasticity`` — ridge sufficient statistics
  G = Σ HᵀH, C = Σ Hᵀ(onehot(y) − softmax(post)) accumulated per episode;
  ψ = M = (G + λI)⁻¹C solved exactly. No gradients anywhere. θ's only
  protection is a zero step_size (bitwise — SHA-asserted).

Stage A → Task B switch, d22 skeleton reused verbatim (parity →
last-symbol, Z3 task helpers, 300 A episodes, probe batches 8).

Pre-registered predictions (written BEFORE any measurement):

- P1 (acquisition): ψ-only moves stage-B probe accuracy OFF the frozen-
  null floor (d22: 0.656; stage-A transfer floor 0.644) with ‖Δθ‖ = 0
  bitwise (SHA-256 identical before/after stage B).
- P2 (speed): ψ reaches the fine-tune accuracy bar (d22's 0.984) in
  FEWER stage-B episodes than lr-matched θ fine-tuning (d22 lesson:
  matched lr = lr/2). Falsified → ψ adaptation slower than fine-tune —
  honest boundary.
- P3 (retention): Task-A accuracy under the final Task-B ψ ≈ the
  frozen-null retention (d22: 0.973) and ≫ fine-tune's 0.660 — zero
  catastrophic forgetting by construction (θ untouched). Falsified →
  the ψ readout residual corrupts off-task behavior; measure the cost.

Leak controls: probes never see training batches (fresh draws, seeded
generator); the null arm re-measures the floor in THIS run; the ψ arm's
modulation is the only stage-B intervention.

Walltime printed, never recorded.

VERDICT (2026-09-07, probe run ~2.6 s CPU; the closed-form boundary is
now EXACTLY mapped):

- Arms: stage A 0.977; frozen-null B 0.6445 / A 0.9727; ψ-only
  B 0.6445 → 0.6992 (ceiling, reached immediately — the ridge solve IS
  the linear probe on frozen features), A 0.9727; fine-tune
  B 0.9922 @ 112 episodes, A 0.6602.
- P1 FALSIFIED in its strong form: ψ moves Task B off the floor
  (+0.055) with θ bitwise frozen (SHA-verified, step_size=0 through the
  real pipeline), but acquires only 0.699 — the linear-probe ceiling of
  the stage-A representation. Closed-form ψ = the optimal linear readout
  on frozen features; it cannot synthesize features. The A→B switch
  needs feature reorganization, which requires θ change.
- P2 FALSIFIED: ψ never reaches the fine-tune bar (0.984); fine-tune
  hits 0.9922 in 112 episodes. Speed comparison void — ψ is instant but
  bounded, fine-tune is slow but unbounded.
- P3 ✅ DECISIVELY: A-retention 0.9727 ≈ null (0.9727) ≫ fine-tune
  (0.6602) — zero forgetting by construction, exactly as predicted.
- THE FINDING (promotable, bounded): "a closed-form ridge ψ set from
  settled activity is an instant, forget-free readout adaptation that
  recovers exactly the frozen-feature linear-probe ceiling — no more.
  It composes with, and cannot substitute for, θ plasticity."
  Improvement lever (untested): ψ laws that modulate HIDDEN layers
  (per-layer closed-form corrections) — the readout-only law cannot
  reorganize features; a hidden-layer ψ might. Queued, not claimed.
- Instrument notes: (a) stage-B ψ arm runs the REAL pipeline
  (``run_train_step``) with a zero-step EuclideanUpdate — bitwise θ
  invariance asserted via SHA-256, exercising the new ``psi_phase``
  contract end-to-end; (b) ``run_train_step`` now writes ψ back into
  the caller's dict (without the in-place sync the P-axis silently
  reset every call — latent defect fixed en route); (c) the ridge is
  bias-augmented (constant column) — measured no effect here (balanced
  task), kept for generality.
"""

from __future__ import annotations

import hashlib
import time

import torch
from torch import Tensor

from computronium import (
    BackpropCredit,
    ClosedFormRidgePlasticity,
    CreditAssignmentConfig,
    EuclideanUpdate,
    GeometryConfig,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemState,
    compose_system_from_configs,
)
from computronium.core.pipeline import forward_pass, run_train_step
from computronium.experiments.joint.tasks import (
    create_switching_task,
)

SEED = 0
STAGE_A_EPISODES = 300
STAGE_B_EPISODES = 200
CRITERION = 0.984
BATCH = 32
SEQ = 4
INPUT_DIM = 8
PROBE_BATCHES = 8
LR = 0.05


def _theta_sha256(system) -> str:
    raw = b"".join(
        p.detach().cpu().contiguous().view(-1).view(torch.uint8).numpy().tobytes()
        for p in system.geometry.params.values()
    )
    return hashlib.sha256(raw).hexdigest()


def _batch(task: str) -> tuple[Tensor, Tensor]:
    x, y = create_switching_task(BATCH, SEQ, INPUT_DIM, phase=task)
    return x.reshape(BATCH, -1), y


def _settled_acts(system, x: Tensor) -> list[Tensor]:
    state = SystemState(x=x)
    state.activations = forward_pass(system.substrate, system.geometry, x)
    settled = system.dynamics.settle(
        state, system.geometry, system.substrate, target=None
    )
    acts = settled.activations
    return list(acts) if isinstance(acts, list) else [acts]


def _probe(system, task: str, plasticity=None, psi=None) -> float:
    correct = total = 0
    with torch.no_grad():
        for _ in range(PROBE_BATCHES):
            x, y = _batch(task)
            acts = _settled_acts(system, x)
            if plasticity is not None and psi:
                acts = plasticity.modulate(acts, psi)
            correct += (acts[-1].argmax(-1) == y).sum().item()
            total += len(y)
    return correct / total


def _train_stage_a(system) -> float:
    for _ in range(STAGE_A_EPISODES):
        x, y = _batch("A")
        run_train_step(
            system.substrate,
            system.geometry,
            system.dynamics,
            system.credit,
            system.update,
            x,
            y,
        )
    return _probe(system, "A")


class _Context:
    """Minimal SystemContext stand-in: plasticity.step reads .theta/.device."""

    def __init__(self, theta):
        self.theta = theta
        self.device = torch.device("cpu")


def _stage_b_psi(system) -> dict[str, float | bool | int]:
    plasticity = ClosedFormRidgePlasticity()
    psi: dict[str, Tensor] = plasticity.initial_psi(None, BATCH)
    context = _Context(system.geometry.params)  # type: ignore[arg-type]
    hash_before = _theta_sha256(system)
    b_start = _probe(system, "B")
    frozen_update = EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=0.0))
    episodes = acc = 0
    for episodes in range(1, STAGE_B_EPISODES + 1):
        x, y = _batch("B")
        run_train_step(
            system.substrate,
            system.geometry,
            system.dynamics,
            system.credit,
            frozen_update,
            x,
            y,
            plasticity=plasticity,
            psi=psi,
            context=context,
        )
        acc = _probe(system, "B", plasticity, psi)
        if acc >= CRITERION:
            break
    return {
        "b_start": b_start,
        "b_final": acc,
        "episodes_to_criterion": episodes,
        "a_retained": _probe(system, "A", plasticity, psi),
        "theta_invariant": hash_before == _theta_sha256(system),
        "psi_norm": float(psi["readout_m"].norm()) if "readout_m" in psi else 0.0,
    }


def _stage_b_null(system) -> dict[str, float | bool]:
    return {
        "b_final": _probe(system, "B"),
        "a_retained": _probe(system, "A"),
    }


def _stage_b_finetune(system) -> dict[str, float | bool | int]:
    b_start = _probe(system, "B")
    credit = BackpropCredit(CreditAssignmentConfig.gradient())
    euclid = EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=LR / 2))
    episodes = acc = 0
    for episodes in range(1, STAGE_B_EPISODES + 1):
        x, y = _batch("B")
        run_train_step(
            system.substrate,
            system.geometry,
            system.dynamics,
            credit,
            euclid,
            x,
            y,
        )
        acc = _probe(system, "B")
        if acc >= CRITERION:
            break
    return {
        "b_start": b_start,
        "b_final": acc,
        "episodes_to_criterion": episodes,
        "a_retained": _probe(system, "A"),
    }


def main() -> int:
    torch.manual_seed(SEED)
    t0 = time.time()
    stage_a: list[float] = []
    results: dict[str, dict[str, float | bool | int]] = {}
    builders = {
        "psi_only": _stage_b_psi,
        "null": _stage_b_null,
        "finetune": _stage_b_finetune,
    }
    for arm, stage_b in builders.items():
        torch.manual_seed(SEED)
        system = compose_system_from_configs(
            SubstrateConfig.digital(),
            GeometryConfig.feedforward(
                input_dim=SEQ * INPUT_DIM, output_dim=2, hidden_dims=(32,)
            ),
            StateDynamicsConfig.instantaneous(),
            CreditAssignmentConfig.gradient(),
            ParameterUpdateConfig.euclidean(step_size=LR),
        )
        a_mastery = _train_stage_a(system)
        stage_a.append(a_mastery)
        results[arm] = stage_b(system)
        print(f"{arm}: stage A {a_mastery:.3f}  {results[arm]}", flush=True)

    print(f"\nwalltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
