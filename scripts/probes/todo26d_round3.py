"""TODO26d Round 3 — confirmation + the last probe round before escalation.

R3-Probe 1 (escalation gate): ≥3-seed repeat of residual+μPC+LocalAdam on
the sign-of-mean depth sweep, plus an MNIST depth-scaling check
(residual+mupc vs default-init, ePC credit + LocalAdam). GREEN if
depth-20 holds across seeds on sign-of-mean AND MNIST shows the mupc
lift where default fails.

R3-Probe 2 (error-bus rung): TargetInversionCredit (transpose-propagated
per-layer prediction targets — the zoo's explicit error channel) vs
residual-only ePC at depth 20, and depth 30 (beyond R2's frontier) on
sign-of-mean. GREEN if the bus matches/beats residuals or enables depth
where residuals fail. Caveat stated up front: transpose feedback is
weight-transport-adjacent — the bus is *channel* redesign, not perfectly
local; recorded as such.

R3-Probe 3 (flagship gate): supervised-ψ at scale — TemporalPsi
(ρ=0.9, replace_readout) vs closed-form (ρ=1) at 600 episodes on the
L3.5 switch, θ frozen + SHA-256 audited, trajectory logged every 100
episodes. GREEN if Task B ≥ 0.95.

Run: uv run python scripts/probes/todo26d_round3.py (~34 s CPU)
Walltime printed, never recorded.

VERDICTS (2026-09-14):

- R3-Probe 1 — RED (re-diagnose; the gate did its job). Depth-20
  residual+mupc across seeds: 0.849 / 0.633 / 0.854 — seed 1 collapses;
  the R2-P1 green is FRAGILE, not robust. The MNIST mupc lift does NOT
  reproduce at this operating point either (mupc 0.453 vs default 0.727
  at depth 8, 100 batches) — but three axes differ from the recorded
  mupc_residual_regime positive (LocalAdam 3e-3 vs Euclid 0.2, ePC 5
  steps vs sPC 60, 100 vs 600 batches), so this is a non-replication at
  a different operating point, not a falsification. Per TODO26d's RED
  clause: re-diagnose (seed sensitivity + operating point) BEFORE
  spending campaign compute. No escalation.
- R3-Probe 2 — RED (residuals are the minimal sufficient channel).
  TargetInversionCredit (transpose-propagated per-layer targets — the
  zoo's explicit error channel) sits at chance at depth 20 AND 30 in
  every geometry (residual+mupc 0.491/0.498; bare 0.499/0.496) while
  residual+mupc+epc trains both (0.865/0.821). Note depth 30 ePC holds
  (0.821) — the residual+μPC regime extends past R2's frontier. The
  transpose-target bus adds nothing here; caveat stands (transpose
  feedback is weight-transport-adjacent) and the lr was not re-tuned
  for the bus's gradient scale — record RED-at-operating-point.
- R3-Probe 3 — RED (P-axis ceiling below the flagship bar). At 600
  episodes both ψ arms plateau at B ~0.70-0.73 (temporal_090 0.699,
  closed_form 0.709; trajectories oscillate 0.68-0.74 from episode 100
  on — no trend toward 0.95). θ bitwise-invariant in both. The
  supervised-ψ readout regression has a ceiling ~0.73 on this switch —
  far below the flagship bar. Re-scope: the P-axis claim is "frozen-θ
  readout adaptation to ~0.73", not "solves the switch". Z3 escalation
  NOT warranted at this mechanism.
- Round verdict: R3-P1 RED (fragile seed), R3-P2 RED (bus adds
  nothing), R3-P3 RED (ceiling). Per the escalation rule: NO campaign
  compute yet. The honest state: the pivot is real but single-seed
  fragile at depth 20; residuals are the minimal channel; ψ plateaus.
"""

from __future__ import annotations

import hashlib
import time
from itertools import islice

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
    TargetInversionCredit,
    ThermodynamicContrast,
    compose_system,
    create_task,
)
from computronium.core.pipeline import forward_pass, run_train_step
from computronium.core.plasticity.temporal_psi import (
    TemporalPsiConfig,
    TemporalPsiPlasticity,
)
from computronium.experiments.joint.tasks import create_switching_task
from computronium.ontology.geometry import (
    InitScheme,  # ruff: ignore[typing-only-first-party-import]
)
from computronium.state import CompositeState

INPUT_DIM = 16
WIDTH = 32
BATCH = 64
BETA = 0.5
DEVICE = "cpu"
SEEDS = (0, 1, 2)


def _theta_sha256(system) -> str:
    raw = b"".join(
        p.detach().cpu().contiguous().view(-1).view(torch.uint8).numpy().tobytes()
        for p in system.geometry.params.values()
    )
    return hashlib.sha256(raw).hexdigest()


def _build(
    depth: int,
    *,
    residual: bool,
    scheme: InitScheme,
    credit: str,
    step_size: float,
    input_dim: int,
    width: int = WIDTH,
):
    if credit == "epc":
        dynamics = ErrorPredictiveCodingDynamics(
            StateDynamicsConfig.error_predictive_coding(
                max_steps=5, step_size=0.5, beta=BETA
            )
        )
        credit_obj = ThermodynamicContrast(
            CreditAssignmentConfig.thermodynamic_contrast(beta=BETA)
        )
    elif credit == "target_inv":
        dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
        credit_obj = TargetInversionCredit(CreditAssignmentConfig.target_inversion())
    else:
        dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
        credit_obj = BackpropCredit(CreditAssignmentConfig.gradient())
    return compose_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device=DEVICE)),
        geometry=FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=input_dim,
                output_dim=2,
                hidden_dims=(width,) * depth,
                residual=residual,
                init_scheme=scheme,
            )
        ),
        dynamics=dynamics,
        credit=credit_obj,
        update=LocalAdamUpdate(
            ParameterUpdateConfig.local_adam(step_size=step_size, momentum=0.9)
        ),
    )


def r3_probe_1_confirmation() -> None:
    print("== R3-Probe 1: Depth-Arm Confirmation (3 seeds) ==", flush=True)
    data = [create_switching_task(BATCH, 4, INPUT_DIM, phase="A") for _ in range(60)]
    for depth in (4, 20):
        for seed in SEEDS:
            torch.manual_seed(seed)
            system = _build(
                depth,
                residual=True,
                scheme="mupc",
                credit="epc",
                step_size=3e-3,
                input_dim=4 * INPUT_DIM,
            )
            acc = SystemTrainer(
                system=system,
                config=SystemTrainerConfig(max_epochs=1, device=DEVICE, seed=seed),
                train_data=data,
            ).fit()[-1]["train_acc"]
            print(
                f"depth {depth:>2} residual+mupc seed {seed}: acc {acc:.3f}", flush=True
            )
    print("-- MNIST depth-scaling check (residual, ePC+LocalAdam) --", flush=True)
    task = create_task("mnist", device=DEVICE, quick_mode=True, num_workers=0)
    task.setup()
    torch.manual_seed(0)
    train = [
        (x.view(x.size(0), -1), y)
        for x, y in islice(task.get_dataloader("train"), 100)  # type: ignore[attr-defined]
    ]
    for scheme in ("mupc", "default"):
        torch.manual_seed(0)
        system = compose_system(
            substrate=DigitalSubstrate(SubstrateConfig.digital(device=DEVICE)),
            geometry=FeedforwardGeometry(
                GeometryConfig.feedforward(
                    input_dim=784,
                    output_dim=10,
                    hidden_dims=(128,) * 8,
                    residual=True,
                    init_scheme=scheme,
                )
            ),
            dynamics=ErrorPredictiveCodingDynamics(
                StateDynamicsConfig.error_predictive_coding(
                    max_steps=5, step_size=0.5, beta=BETA
                )
            ),
            credit=ThermodynamicContrast(
                CreditAssignmentConfig.thermodynamic_contrast(beta=BETA)
            ),
            update=LocalAdamUpdate(
                ParameterUpdateConfig.local_adam(step_size=3e-3, momentum=0.9)
            ),
        )
        acc = SystemTrainer(
            system=system,
            config=SystemTrainerConfig(max_epochs=1, device=DEVICE, seed=42),
            train_data=train,
        ).fit()[-1]["train_acc"]
        print(f"MNIST depth 8 residual {scheme}+local_adam: acc {acc:.3f}", flush=True)


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


def r3_probe_2_error_bus() -> None:
    print("== R3-Probe 2: Error-Bus Rung (transpose targets) ==", flush=True)
    data = [create_switching_task(BATCH, 4, INPUT_DIM, phase="A") for _ in range(60)]
    arms: tuple[tuple[str, bool, InitScheme, str], ...] = (
        ("residual+mupc+epc", True, "mupc", "epc"),
        ("residual+mupc+targetinv", True, "mupc", "target_inv"),
        ("none+default+targetinv", False, "default", "target_inv"),
    )
    for depth in (20, 30):
        for label, residual, scheme, credit in arms:
            torch.manual_seed(0)
            system = _build(
                depth,
                residual=residual,
                scheme=scheme,
                credit=credit,
                step_size=3e-3,
                input_dim=4 * INPUT_DIM,
            )
            try:
                acc = SystemTrainer(
                    system=system,
                    config=SystemTrainerConfig(max_epochs=1, device=DEVICE, seed=42),
                    train_data=data,
                ).fit()[-1]["train_acc"]
                print(f"depth {depth:>2} {label}: acc {acc:.3f}", flush=True)
            except RuntimeError as e:
                print(
                    f"depth {depth:>2} {label}: CRASH {type(e).__name__}: "
                    f"{str(e)[:120]}",
                    flush=True,
                )


class _Ctx:
    """Minimal SystemContext stand-in: temporal ψ reads .theta/.device."""

    def __init__(self, theta):
        self.theta = theta
        self.device = torch.device(DEVICE)


def _train_phase(system, task: str, episodes: int) -> None:
    for _ in range(episodes):
        x, y = create_switching_task(BATCH, 4, INPUT_DIM, phase=task)
        run_train_step(
            system.substrate,
            system.geometry,
            system.dynamics,
            system.credit,
            system.update,
            x.reshape(BATCH, -1),
            y,
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


def _psi_arm(label: str, trace_decay: float, episodes: int) -> None:
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
    _train_phase(system, "A", 300)
    a_mastery = _probe(system, "A")
    b_null = _probe(system, "B")
    for p in system.geometry.params.values():
        p.requires_grad_(False)
    sha_before = _theta_sha256(system)

    plasticity = TemporalPsiPlasticity(
        TemporalPsiConfig(trace_decay=trace_decay, replace_readout=True)
    )
    psi: dict[str, Tensor] = {}
    context = _Ctx(system.geometry.params)
    marks: list[str] = []
    for ep in range(1, episodes + 1):
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
            z = CompositeState(
                activity={"h": acts[-2], "target": y, "y": acts[-1]},
                plastic=psi,
                substrate={},
            )
            psi = plasticity.step(psi, z, context)  # type: ignore[arg-type]
        if ep % 100 == 0 or ep == episodes:
            b_now = _probe_psi(system, plasticity, psi, "B")
            marks.append(f"{ep}:{b_now:.3f}")
    b_final = _probe_psi(system, plasticity, psi, "B")
    a_retained = _probe_psi(system, plasticity, psi, "A")
    theta_invariant = sha_before == _theta_sha256(system)
    print(
        f"{label}: A {a_mastery:.3f}  null {b_null:.3f}  traj "
        f"[{' '.join(marks)}]  final B {b_final:.3f}  A ret {a_retained:.3f}  "
        f"θ inv {theta_invariant}",
        flush=True,
    )


def r3_probe_3_psi_bar() -> None:
    print("== R3-Probe 3: ψ at the 0.95 Bar (600 episodes) ==", flush=True)
    _psi_arm("temporal_090", 0.9, 600)
    _psi_arm("closed_form_100", 1.0, 600)


def main() -> None:
    t0 = time.perf_counter()
    r3_probe_1_confirmation()
    r3_probe_2_error_bus()
    r3_probe_3_psi_bar()
    print(f"total walltime {time.perf_counter() - t0:.1f}s")


if __name__ == "__main__":
    main()
