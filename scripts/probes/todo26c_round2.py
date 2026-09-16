"""TODO26c Engine Check Round 2 — the three live levers.

R2-Probe 1 (headline — tests the pivot): residual co-design depth arm.
D14-faithful composition on the tiny parity harness: residual
feedforward geometry (skip paths give credit a shortcut to layer 1) +
μPC depth-scaled init + LocalAdam, depth sweep 4/8/12/20. GREEN if
depth-20 parity learns (>chance).

R2-Probe 2 (tractable P-axis fix): supervised ψ term. TemporalPsi
Plasticity (X-TPC-001's law: trace-decayed ridge readout stepped on the
NUDGED settle, consuming the target) on the L3.5 switch, θ frozen
(SHA-256 audited), ψ-only 50 steps on Task B. TODO26c GREEN bar: Task B
>95% with θ bitwise-invariant.

R2-Probe 3 (diagnostic — decides the next lever): directional credit
SNR on the depth-20 settle path, credit_norm none vs rms. Split-half
design: per-layer error eps_l = (free − nudged)/β computed on two
independent batch halves; per-layer SNR proxy = cosine between the two
half-mean credit vectors. Trapped ≈ zero norm (signal never arrives);
noisy = nonzero norm, low cosine; usable = high cosine.

Context: X-TPC-001/002 already SUPPORTED supervised-ψ acquisition on
the governed harness (B 0.754-0.777 vs null 0.645-0.707, θ frozen);
R2-P2 re-measures that law on this round's exact switch/bar.

Run: uv run python scripts/probes/todo26c_round2.py (~19 s CPU)
Walltime printed, never recorded.

VERDICTS (2026-09-14):

- R2-Probe 1 — GREEN (the headline). Depth-20 sign-of-mean 2x2
  ablation: residual+mupc 0.865 vs residual+default 0.536,
  mupc-only 0.489, neither 0.496 — ONLY the joint composition trains
  at depth 20 (at depth 4 every arm learns, 0.80-0.89). The ePC depth
  wall is broken by architecture co-design: residual skip paths give
  the credit a route to layer 1 AND muPC's depth-scaled init keeps the
  channel conditioned; neither alone suffices. And it runs on
  LocalAdam — a cheap substrate-native local optimizer, no Muon
  (the TODO26b P2 "optimizer crutch" was compensating for geometry,
  not credit direction). Parity harness lesson: 16-bit parity at this
  budget exceeds even exact backprop (residual+mupc+BP control chance
  at depth 4 with 4x budget) — the parity arm cannot certify the
  accuracy axis for ANY arm; fair tests need a BP-learnable task.
- R2-Probe 2 — GREEN on mechanism, bar unmet. TemporalPsiPlasticity
  (the supervised ψ law X-TPC-001 built) on this exact switch:
  B 0.676 -> 0.734 (+0.058) in 50 steps with θ SHA-256 bitwise
  invariant, A retained 0.844. TODO26c's >95% bar is NOT met at quick
  budget — consistent with X-TPC-001's governed measurement (B
  0.754-0.777 at 600 episodes; acquisition real, saturates below 0.95).
  The D22 missing-supervised-term diagnosis is confirmed as the
  tractable part: supervised ψ adapts; the 0.95 bar needs more
  episodes/capacity, not a mechanism change.
- R2-Probe 3 — TRAPPED (decisively). Split-half cosine of the
  per-weight contrastive credit: layers 19-21 cosine 1.000 (clean
  shared signal), layer 10 cosine 0.97, layers 1-2 cosine 0.000 with
  |mean_credit| ~1e-9. credit_norm=rms lifts the layer-1 noise floor
  1e-9 -> 1.6e-1 with cosine STILL 0.000 — normalization amplifies
  noise, not signal. The denoising/averaging lever is closed; the
  architecture co-design lever (R2-P1, now GREEN) is mandatory.
  (Method note: the first draft measured raw settle eps with reversed
  layer indexing and showed an illusory "0.404 cosine at layer 1";
  the corrected per-weight-credit measurement with true layer indexing
  shows the trap.)
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
from computronium.core.plasticity.temporal_psi import (
    TemporalPsiConfig,
    TemporalPsiPlasticity,
)
from computronium.experiments.joint.tasks import create_switching_task
from computronium.ontology.credit import CreditNormMode, Phase
from computronium.ontology.geometry import InitScheme  # ruff: ignore[typing-only-first-party-import]
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


def _epc_system(
    depth: int,
    *,
    residual: bool = False,
    init_scheme: InitScheme = "default",  # noqa: TC001
    credit_norm: CreditNormMode = "none",
    step_size: float = 3e-3,
    input_dim: int | None = None,
):
    return compose_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device=DEVICE)),
        geometry=FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=input_dim if input_dim is not None else INPUT_DIM,
                output_dim=2,
                hidden_dims=(WIDTH,) * depth,
                residual=residual,
                init_scheme=init_scheme,
            )
        ),
        dynamics=ErrorPredictiveCodingDynamics(
            StateDynamicsConfig.error_predictive_coding(
                max_steps=5, step_size=0.5, beta=BETA
            )
        ),
        credit=ThermodynamicContrast(
            CreditAssignmentConfig.thermodynamic_contrast(
                beta=BETA, credit_norm=credit_norm
            )
        ),
        update=LocalAdamUpdate(
            ParameterUpdateConfig.local_adam(step_size=step_size, momentum=0.9)
        ),
    )


def r2_probe_1_residual_depth() -> None:
    print("== R2-Probe 1: Residual Co-Design Depth Arm ==", flush=True)
    # Parity harness note: 16-bit parity at this budget exceeds even exact
    # backprop (residual+mupc+BP control: chance at depth 4 with 4x budget)
    # — the parity arm cannot certify the accuracy axis for ANY arm.
    bp_data = _parity_batches(240)
    torch.manual_seed(0)
    bp_system = _bp_switch_system(residual=True, input_dim=INPUT_DIM)
    bp_acc = SystemTrainer(
        system=bp_system,
        config=SystemTrainerConfig(max_epochs=4, device=DEVICE, seed=42),
        train_data=bp_data,
    ).fit()[-1]["train_acc"]
    print(
        f"parity BP control (residual+mupc, 240 batches): acc {bp_acc:.3f}", flush=True
    )

    # Fair test: the BP-learnable sign-of-mean task (BP reaches 0.979),
    # residual x init ablation at depths 4 and 20, lr 3e-3, 60 batches.
    data = [create_switching_task(BATCH, 4, INPUT_DIM, phase="A") for _ in range(60)]
    for depth in (4, 20):
        arms: tuple[tuple[bool, InitScheme], ...] = (
            (True, "mupc"),
            (True, "default"),
            (False, "mupc"),
            (False, "default"),
        )
        for residual, scheme in arms:
            torch.manual_seed(0)
            system = _epc_system(
                depth,
                residual=residual,
                init_scheme=scheme,
                step_size=3e-3,
                input_dim=4 * INPUT_DIM,
            )
            acc = SystemTrainer(
                system=system,
                config=SystemTrainerConfig(max_epochs=1, device=DEVICE, seed=42),
                train_data=data,
            ).fit()[-1]["train_acc"]
            print(
                f"depth {depth:>2} residual={residual!s:<5} {scheme:<7}: "
                f"ePC+local_adam sign-of-mean acc {acc:.3f}",
                flush=True,
            )


def _bp_switch_system(*, residual: bool, input_dim: int):
    from computronium import BackpropCredit

    return compose_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device=DEVICE)),
        geometry=FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=input_dim,
                output_dim=2,
                hidden_dims=(WIDTH,) * 4,
                residual=residual,
                init_scheme="mupc",
            )
        ),
        dynamics=InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
        credit=BackpropCredit(CreditAssignmentConfig.gradient()),
        update=EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=0.05)),
    )


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


def _switch_system():
    return compose_system(
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


def r2_probe_2_supervised_psi() -> None:
    print("== R2-Probe 2: Supervised ψ (TemporalPsiPlasticity) ==", flush=True)
    torch.manual_seed(0)
    system = _switch_system()
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

    plasticity = TemporalPsiPlasticity(
        TemporalPsiConfig(trace_decay=0.9, replace_readout=True)
    )
    psi: dict[str, Tensor] = {}
    context = _Ctx(system.geometry.params)
    for _ in range(50):
        x, y = create_switching_task(BATCH, 4, INPUT_DIM, phase="B")
        with torch.no_grad():
            x_flat = x.reshape(BATCH, -1)
            state = SystemState(x=x_flat, y=y)
            state.activations = forward_pass(system.substrate, system.geometry, x_flat)
            settled = system.dynamics.settle(
                state,  # type: ignore[arg-type]
                system.geometry,
                system.substrate,
                target=None,
            )
            acts = settled.activations
            assert isinstance(acts, list)
            # The supervised ψ contract: h = pre-readout hidden stream,
            # target = y, y = post-settle logits (psi_phase = "nudged").
            z = CompositeState(
                activity={"h": acts[-2], "target": y, "y": acts[-1]},
                plastic=psi,
                substrate={},
            )
            psi = plasticity.step(psi, z, context)  # type: ignore[arg-type]

    b_final = _probe_psi(system, plasticity, psi, "B")
    a_retained = _probe_psi(system, plasticity, psi, "A")
    theta_invariant = sha_before == _theta_sha256(system)
    print(
        f"A mastery {a_mastery:.3f}  B frozen-null {b_null:.3f}  "
        f"B after ψ(50) {b_final:.3f}  A retained {a_retained:.3f}  "
        f"θ bitwise invariant {theta_invariant}",
        flush=True,
    )


def _probe_psi(system, plasticity, psi, task: str) -> float:
    correct = total = 0
    with torch.no_grad():
        for _ in range(8):
            x, y = create_switching_task(BATCH, 4, INPUT_DIM, phase=task)
            x_flat = x.reshape(BATCH, -1)
            state = SystemState(x=x_flat)
            state.activations = forward_pass(system.substrate, system.geometry, x_flat)
            settled = system.dynamics.settle(
                state, system.geometry, system.substrate, target=None
            )
            acts = settled.activations
            assert acts is not None
            modulated = plasticity.modulate(acts, psi)
            out = modulated[-1] if isinstance(modulated, list) else modulated
            correct += (out.argmax(-1) == y).sum().item()
            total += len(y)
    return correct / total


class _Ctx:
    """Minimal SystemContext stand-in: temporal ψ reads only .device/theta."""

    def __init__(self, theta):
        self.theta = theta
        self.device = torch.device(DEVICE)


def _cosine(a: Tensor, b: Tensor) -> float:
    a, b = a.detach().flatten(), b.detach().flatten()
    denom = a.norm() * b.norm()
    if denom == 0:
        return float("nan")
    return float((a @ b) / denom)


def _credit_grads(system, x: Tensor, y: Tensor) -> list[Tensor]:
    """Per-weight contrastive credit (the channel credit_norm acts on)."""
    free = system.dynamics.settle(
        SystemState(x=x), system.geometry, system.substrate, target=None
    )
    nudged = system.dynamics.settle(
        SystemState(x=x), system.geometry, system.substrate, target=y
    )
    return system.credit.compute_pseudo_gradient(
        {Phase.FREE: free, Phase.NUDGED: nudged}, None, system.geometry
    )


def r2_probe_3_credit_snr() -> None:
    print("== R2-Probe 3: Credit SNR (trapped vs noisy) ==", flush=True)
    data = _parity_batches(n_batches=8)
    depth = 20
    for norm in ("none", "rms"):
        torch.manual_seed(0)
        system = _epc_system(depth, residual=False, credit_norm=norm)
        half = BATCH // 2
        per_layer: list[tuple[list[Tensor], list[Tensor]]] = []
        for x, y in data[:4]:
            for h, (xh, yh) in enumerate((
                (x[:half], y[:half]),
                (x[half:], y[half:]),
            )):
                grads = _credit_grads(system, xh, yh)
                for l, g in enumerate(grads):
                    if l == len(per_layer):
                        per_layer.append(([], []))
                    per_layer[l][h].append(g)
        print(f"credit_norm={norm}:", flush=True)
        for l in range(len(per_layer)):
            m1 = torch.stack(per_layer[l][0]).mean(0)
            m2 = torch.stack(per_layer[l][1]).mean(0)
            n1, n2 = m1.norm().item(), m2.norm().item()
            snr = _cosine(m1, m2) if n1 > 0 and n2 > 0 else float("nan")
            layer_idx = l + 1  # transition 1 = input -> hidden1
            if layer_idx in {1, 2, 10, 19, 20, 21}:
                print(
                    f"  layer {layer_idx:>2}: |mean_credit| "
                    f"{n1:.2e}/{n2:.2e}  split-half cosine {snr:+.3f}",
                    flush=True,
                )


def main() -> None:
    t0 = time.perf_counter()
    r2_probe_1_residual_depth()
    r2_probe_2_supervised_psi()
    r2_probe_3_credit_snr()
    print(f"total walltime {time.perf_counter() - t0:.1f}s")


if __name__ == "__main__":
    main()
