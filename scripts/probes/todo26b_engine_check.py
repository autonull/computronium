"""TODO26b 10-Minute Engine Check — three foundational smoke probes.

Probe 1 (Depth Wall): ePC + per-layer credit_norm=rms, depths 4/8/12/20
on synthetic parity. GREEN if layer-1 credit survives to depth 20 and
accuracy > chance; RED if the wall persists under normalization.

Probe 2 (Width Wall): PEPITA + LocalAdamUpdate (no orthogonalizer),
widths 32/64/128, depth 4, synthetic parity. GREEN if w=128 trains
without Muon; RED if it collapses (credit direction, not magnitude).

Probe 3 (P-Axis): sign-of-mean (Task A) → last-symbol (Task B) switch,
θ frozen (SHA-256 verified), ψ-only adaptation for 50 steps. GREEN if
Task B > 95% with bitwise-invariant θ.

Run: uv run python scripts/probes/todo26b_engine_check.py (~15 s CPU)
Walltime printed, never recorded.

VERDICTS (2026-09-14; all three RED / mixed per the TODO26b matrix):

- Probe 1 — SPLIT, resolves RED. credit_norm=rms lifts the DEEP HIDDEN
  layers' credit (depth-20 hidden norms 2.1e-1..3.2e+1 vs
  3.5e-10..5.6e-4 unnormalized), but the layer-1 (input-weight) credit
  stays EXACTLY 0.00 even under rms — the 5-step settle never reaches
  layer 1 through 20 layers, and _apply_credit_norm leaves zeros
  untouched (no fabricated signal), so min-hidden stays 0.00 at depth
  20. Accuracy NEVER leaves chance (0.50) at any depth under either
  mode, and even the depth-4 baseline sits at chance with 4x budget
  (0.505), so the parity harness cannot certify the accuracy arm; the
  MNIST evidence (A3: unit_rms walls at depth 8+, 0.206@2) closes it:
  normalized credit carries NO usable contrastive signal —
  normalization lifts the noise floor along with the signal, and the
  input-weight layer's signal is exactly zero. Pivot per matrix:
  learned feedback projections / the D14 faithful-regime composition.
- Probe 2 — RED. PEPITA-family (LEMMA per-layer fixed-B,
  feedback_scale 0.05) + LocalAdam sits at chance (0.489-0.507) at
  EVERY width including 32 (parity chance 0.5). Consistent with P4-A0
  (local_adam exploded on LM pepita; LEMMA fixed-B boundary 0.306
  MNIST):   the failure is directional, not magnitudinal. (Note: the
  published PEPITA second-pass algorithm is CreditAssignmentConfig
  .pepita() with local_objective="ff" — a different rule, TODO15 §11;
  the per-layer fixed-B family probed here is the one with the
  boundary records: 0.306 fixed-B w32, 0.214 fixed-B depth-8, 0.107
  learned-B, all × Muon — LemmaCredit IDENTITY_CARD.) Pivot: learned
  feedback alignment is also closed (0.107), so the whole fixed-B
  family is boundary-locked.
- Probe 3 — RED. ψ-only adaptation 50 steps: B 0.676 -> 0.686 (within
  probe noise), θ bitwise invariant (SHA-256), ‖ψ‖ inflates to 18.3
  with no behavioral gain — replicates D22's falsification at 1/12 the
  episode budget. The ψ-step contract consumes no supervised term;
  P-axis remains a weight-preprocessor until a loss-bearing ψ rule
  lands (B5-adjacent supervised ψ / metaplasticity D2).
- Matrix row: 🔴🔴🔴 (with P1's magnitude sub-result green) —
  "Fundamental Mismatch" branch: local credit rules as currently
  framed are a dead end; the validated path is the architecture
  co-design already measured positive (D14 faithful regime, mupc
  residual regime train depth 20+).
"""

from __future__ import annotations

import hashlib
import time

import torch
from torch import Tensor

from computronium import (
    BackpropCredit,
    CreditAssignmentConfig,
    DigitalSubstrate,
    ErrorPredictiveCodingDynamics,
    EuclideanUpdate,
    FeedforwardGeometry,
    GeometryConfig,
    InstantaneousDynamics,
    LocalAdamUpdate,
    LocalGoodnessCredit,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemState,
    SystemTrainer,
    SystemTrainerConfig,
    ThermodynamicContrast,
    compose_system,
)
from computronium.core.pipeline import forward_pass, run_train_step
from computronium.core.plasticity.routing import RoutingPlasticity
from computronium.experiments.joint.tasks import create_switching_task
from computronium.ontology.credit import Phase
from computronium.state import CompositeState

INPUT_DIM = 16
WIDTH = 32
BATCH = 64
N_BATCHES = 60
BETA = 0.5
DEVICE = "cpu"


def _parity_batches(n_batches: int = N_BATCHES) -> list[tuple[Tensor, Tensor]]:
    rng = torch.Generator().manual_seed(0)
    out = []
    for _ in range(n_batches):
        x = (torch.rand(BATCH, INPUT_DIM, generator=rng) < 0.5).float() * 2 - 1
        y = (x > 0).sum(-1) % 2
        out.append((x, y))
    return out


def _credit_norms(system, x: Tensor, y: Tensor) -> list[float]:
    free = system.dynamics.settle(
        SystemState(x=x), system.geometry, system.substrate, target=None
    )
    nudged = system.dynamics.settle(
        SystemState(x=x), system.geometry, system.substrate, target=y
    )
    grads = system.credit.compute_pseudo_gradient(
        {Phase.FREE: free, Phase.NUDGED: nudged}, None, system.geometry
    )
    return [g.norm().item() for g in grads]


def probe_1_depth() -> None:
    print("== Probe 1: Depth Wall (ePC credit_norm) ==", flush=True)
    data = _parity_batches()
    x, y = data[0]
    for depth in (4, 8, 12, 20):
        for norm in ("none", "rms"):
            torch.manual_seed(0)
            system = compose_system(
                substrate=DigitalSubstrate(SubstrateConfig.digital(device=DEVICE)),
                geometry=FeedforwardGeometry(
                    GeometryConfig.feedforward(
                        input_dim=INPUT_DIM,
                        output_dim=2,
                        hidden_dims=(WIDTH,) * depth,
                    )
                ),
                dynamics=ErrorPredictiveCodingDynamics(
                    StateDynamicsConfig.error_predictive_coding(
                        max_steps=5, step_size=0.5, beta=BETA
                    )
                ),
                credit=ThermodynamicContrast(
                    CreditAssignmentConfig.thermodynamic_contrast(
                        beta=BETA, credit_norm=norm
                    )
                ),
                update=EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=0.2)),
            )
            acc = SystemTrainer(
                system=system,
                config=SystemTrainerConfig(max_epochs=1, device=DEVICE, seed=42),
                train_data=data,
            ).fit()[-1]["train_acc"]
            norms = _credit_norms(system, x, y)
            hidden = norms[:-1]
            print(
                f"depth {depth:>2} norm={norm:<4} acc {acc:.3f} "
                f"credit norms {[f'{n:.2e}' for n in norms]} "
                f"min-hidden {min(hidden):.2e}",
                flush=True,
            )


def probe_2_width() -> None:
    print("== Probe 2: Width Wall (PEPITA + LocalAdam) ==", flush=True)
    data = _parity_batches()
    for width in (32, 64, 128):
        best = (0.0, 0.0)
        for lr in (1e-3, 3e-3):
            torch.manual_seed(0)
            system = compose_system(
                substrate=DigitalSubstrate(SubstrateConfig.digital(device=DEVICE)),
                geometry=FeedforwardGeometry(
                    GeometryConfig.feedforward(
                        input_dim=INPUT_DIM,
                        output_dim=2,
                        hidden_dims=(width,) * 4,
                    )
                ),
                dynamics=InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
                # LEMMA per-layer fixed-B mode — the in-repo PEPITA-family
                # realization (CreditAssignmentConfig.pepita() is the
                # published second-pass algorithm, local_objective="ff",
                # a different rule — TODO15 §11).
                credit=LocalGoodnessCredit(
                    CreditAssignmentConfig.local_goodness(
                        local_objective="lemma", feedback_scale=0.05
                    )
                ),
                update=LocalAdamUpdate(
                    ParameterUpdateConfig.local_adam(step_size=lr, momentum=0.9)
                ),
            )
            acc = SystemTrainer(
                system=system,
                config=SystemTrainerConfig(max_epochs=1, device=DEVICE, seed=42),
                train_data=data,
            ).fit()[-1]["train_acc"]
            if acc > best[0]:
                best = (acc, lr)
            print(f"width {width:>3} lr {lr:g}: acc {acc:.3f}", flush=True)
        print(f"width {width:>3} BEST acc {best[0]:.3f} @ lr {best[1]:g}", flush=True)


def _theta_sha256(system) -> str:
    raw = b"".join(
        p.detach().cpu().contiguous().view(-1).view(torch.uint8).numpy().tobytes()
        for p in system.geometry.params.values()
    )
    return hashlib.sha256(raw).hexdigest()


def _settled_out(system, x: Tensor) -> Tensor:
    state = SystemState(x=x)
    state.activations = forward_pass(system.substrate, system.geometry, x)
    settled = system.dynamics.settle(
        state, system.geometry, system.substrate, target=None
    )
    acts = settled.activations
    return acts[-1] if isinstance(acts, list) else acts


def _probe(system, task: str, n_batches: int = 8) -> float:
    correct = total = 0
    with torch.no_grad():
        for _ in range(n_batches):
            x, y = create_switching_task(BATCH, 4, INPUT_DIM, phase=task)
            correct += (_settled_out(system, x).argmax(-1) == y).sum().item()
            total += len(y)
    return correct / total


def probe_3_p_axis() -> None:
    print("== Probe 3: P-Axis (frozen-θ ψ adaptation) ==", flush=True)
    torch.manual_seed(0)
    system = compose_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device=DEVICE)),
        geometry=FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=4 * INPUT_DIM, output_dim=2, hidden_dims=(64, 64)
            )
        ),
        dynamics=InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
        credit=BackpropCredit(CreditAssignmentConfig.gradient()),
        update=EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=0.05)),
    )
    for _ in range(300):
        x, y = create_switching_task(BATCH, 4, INPUT_DIM, phase="A")
        run_train_step(
            system.substrate,
            system.geometry,
            system.dynamics,
            system.credit,
            system.update,
            x.reshape(BATCH, -1),
            y,
        )
    a_mastery = _probe(system, "A")
    b_null = _probe(system, "B")

    for p in system.geometry.params.values():
        p.requires_grad_(False)
    sha_before = _theta_sha256(system)

    plasticity = RoutingPlasticity(gate_dim=64, learning_rate=0.05)
    psi = plasticity.initial_psi(None, 1)
    context = _Context(system.geometry.params)  # type: ignore[assignment]
    for _ in range(50):
        x, y = create_switching_task(BATCH, 4, INPUT_DIM, phase="B")
        with torch.no_grad():
            state = SystemState(x=x.reshape(BATCH, -1), y=y)
            state.activations = forward_pass(
                system.substrate, system.geometry, x.reshape(BATCH, -1)
            )
            settled = system.dynamics.settle(
                state,  # type: ignore[arg-type]
                system.geometry,
                system.substrate,
                target=None,
            )
            acts = settled.activations
            assert acts is not None
            z = CompositeState(
                activity={"x": x.reshape(BATCH, -1), "y": acts[-1]},
                plastic=psi,
                substrate={},
            )
            psi = plasticity.step(psi, z, context)  # type: ignore[arg-type]
            settled.activations = plasticity.modulate(acts, psi)

    b_final = _probe_modulated(system, plasticity, psi, "B")
    a_retained = _probe_modulated(system, plasticity, psi, "A")
    theta_invariant = sha_before == _theta_sha256(system)
    print(
        f"A mastery {a_mastery:.3f}  B frozen-null {b_null:.3f}  "
        f"B after ψ(50) {b_final:.3f}  A retained {a_retained:.3f}  "
        f"θ bitwise invariant {theta_invariant}  ‖ψ‖ "
        f"{float(psi['gate_logits'].norm()):.3f}",
        flush=True,
    )


def _probe_modulated(system, plasticity, psi, task: str) -> float:
    correct = total = 0
    with torch.no_grad():
        for _ in range(8):
            x, y = create_switching_task(BATCH, 4, INPUT_DIM, phase=task)
            acts = plasticity.modulate(_settled_out(system, x), psi)
            out = acts[-1] if isinstance(acts, list) else acts
            correct += (out.argmax(-1) == y).sum().item()
            total += len(y)
    return correct / total


class _Context:
    """Minimal SystemContext stand-in: plasticity.step reads .theta/.device."""

    def __init__(self, theta):
        self.theta = theta
        self.device = torch.device(DEVICE)


def main() -> None:
    t0 = time.perf_counter()
    probe_1_depth()
    probe_2_width()
    probe_3_p_axis()
    print(f"total walltime {time.perf_counter() - t0:.1f}s")


if __name__ == "__main__":
    main()
