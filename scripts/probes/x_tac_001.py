"""X-TAC-001: conflict-adaptive psi — self-switching trace decay (TODO19 R7).

Round-8 R7 deliverable: the temporal-psi experiments so far (X-TPC-001/002/
003) required an ORACLE to hand in task boundaries and pick rho. This probe
tests ConflictAdaptivePsiPlasticity, which detects fit conflict from its
OWN readout agreement and switches trace decay on/off — the difference
between "we told it to forget" and "it forgets when it should".

Design: MNIST backbone (784-128-2, gradient credit) trained on digit>=5,
theta then bitwise-frozen (SHA-256 + FrozenThetaAudit). Unlabeled stream
of four alternating phases on the frozen h: parity, INVERTED parity,
parity, INVERTED parity (150 episodes each). Arms: adaptive,
temporal_090 (fixed rho), closed_form (rho=1), frozen_null. The adaptive
arm's (agreement, rho_used) trajectory is recorded per episode.

Pre-registered predictions (BEFORE the run; governed by B-H2
TEMPORAL-PSI-CREDIT, prior [0.40, 0.65]):

- P1 (acquisition): adaptive's end-of-phase accuracy is off the
  frozen-null floor by >= +0.10 on EVERY phase, on >= 2 of 3 seeds.
- P2 (self-switching matches hand-tuning): adaptive's mean end-of-phase
  accuracy across the four phases is within 0.02 of temporal_090 on
  >= 2 of 3 seeds.
- P3 (detection): after each of the three label flips, adaptive switches
  rho to forget_decay within <= 2 episodes on >= 2 of 3 seeds, with a
  false-conflict rate <= 20% of steady-phase episodes (excluding the
  first 5 episodes after each flip).

Falsification: adaptive fails to acquire (P1); temporal_090 dominates
beyond the P2 margin; detection is untimely or unstable (P3).

Hard gates on build: identity_card_for_new_primitive
(ConflictAdaptivePsiPlasticity card), frozen_theta_audit (this run).
Walltime: printed, never recorded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from typing import TypedDict
from pathlib import Path

import torch
from torch import Tensor

from computronium import (
    CreditAssignmentConfig,
    FrozenThetaAudit,
    GeometryConfig,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemState,
    compose_system_from_configs,
)
from computronium.core.pipeline import forward_pass
from computronium.core.plasticity.adaptive_psi import (
    ConflictAdaptivePsiConfig,
    ConflictAdaptivePsiPlasticity,
)
from computronium.core.plasticity.temporal_psi import (
    TemporalPsiConfig,
    TemporalPsiPlasticity,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

SEEDS = (0, 1, 2)
STAGE_A_EPISODES = 600
PHASES = (0, 1, 0, 1)  # parity, inverted, parity, inverted — no boundaries in
PHASE_EPISODES = 150
BATCH = 64
PROBE_BATCHES = 20
LR = 0.1
RIDGE_LAMBDA = 1e-3
TRAIN_POOL = 10_000
SWITCH_LAG_LIMIT = 2
FALSE_CONFLICT_LIMIT = 0.20


class ArmRun(TypedDict):
    a_mastery: float
    null_floors: list[float]
    phase_accs: list[float]
    rho_used: list[float]
    agreements: list[float]
    switch_lags: list[int | None]
    false_conflict_rate: float
    theta_invariant: bool


ARMS = ("adaptive", "temporal_090", "closed_form", "frozen_null")


def load_mnist() -> tuple[Tensor, Tensor, Tensor, Tensor]:
    from torchvision import transforms
    from torchvision.datasets import MNIST

    def _stack(train: bool) -> tuple[Tensor, Tensor]:
        ds = MNIST(
            str(REPO_ROOT / "data"),
            train=train,
            download=False,
            transform=transforms.ToTensor(),
        )
        xs = torch.stack([ds[i][0] for i in range(len(ds))]).float()
        ys = torch.tensor([int(ds[i][1]) for i in range(len(ds))])
        return xs.view(len(ds), -1), ys

    xtr, ytr = _stack(True)
    xte, yte = _stack(False)
    gen = torch.Generator().manual_seed(1234)
    pool = torch.randperm(len(xtr), generator=gen)[:TRAIN_POOL]
    return xtr[pool], ytr[pool], xte, yte


def label_for(y: Tensor, parity_flip: int) -> Tensor:
    """parity (even=1), XOR parity_flip inverts the mapping."""
    return (y % 2 == 0).long() ^ parity_flip


class MNISTTasks:
    def __init__(self) -> None:
        self.xtr, self.ytr, self.xte, self.yte = load_mnist()
        self._gen = torch.Generator().manual_seed(0)

    def batch(self, parity_flip: int) -> tuple[Tensor, Tensor]:
        idx = torch.randint(0, len(self.xtr), (BATCH,), generator=self._gen)
        return self.xtr[idx], label_for(self.ytr[idx], parity_flip)

    def probe_batches(self, parity_flip: int):
        idx = torch.randperm(len(self.xte), generator=self._gen)[
            : PROBE_BATCHES * BATCH
        ].view(PROBE_BATCHES, BATCH)
        return [(self.xte[i], label_for(self.yte[i], parity_flip)) for i in idx]

    def digit_ge5_batches(self):
        idx = torch.randint(0, len(self.xtr), (BATCH,), generator=self._gen)
        return self.xtr[idx], (self.ytr[idx] >= 5).long()

    def digit_ge5_probe_batches(self):
        idx = torch.randperm(len(self.xte), generator=self._gen)[:1024]
        return [(self.xte[i], (self.yte[i] >= 5).long()) for i in idx.view(-1, BATCH)]


def _theta_sha256(system) -> str:
    raw = b"".join(
        p.detach().cpu().contiguous().view(-1).view(torch.uint8).numpy().tobytes()
        for p in system.geometry.params.values()
    )
    return hashlib.sha256(raw).hexdigest()


def _settled(system, x: Tensor):
    state = SystemState(x=x)
    state.activations = forward_pass(system.substrate, system.geometry, x)
    return system.dynamics.settle(state, system.geometry, system.substrate, target=None)


def _out_from(acts) -> Tensor:
    return acts[-1] if isinstance(acts, list) else acts


def _probe_modulated(system, plasticity, psi: dict, task, flip: int) -> float:
    correct = total = 0
    with torch.no_grad():
        for x, y in task.probe_batches(flip):
            acts = plasticity.modulate(_settled(system, x).activations, psi)
            correct += (_out_from(acts).argmax(-1) == y).sum().item()
            total += len(y)
    return correct / total


def _probe(system, task, flip: int) -> float:
    class _Null:
        def modulate(self, acts, psi):
            return acts

    return _probe_modulated(system, _Null(), {}, task, flip)


def _train_stage_a(system, task) -> float:
    from computronium.core.pipeline import run_train_step

    for _ in range(STAGE_A_EPISODES):
        x, y = task.digit_ge5_batches()
        run_train_step(
            system.substrate,
            system.geometry,
            system.dynamics,
            system.credit,
            system.update,
            x,
            y,
        )
    return _probe_digit_ge5(system, task)


def _probe_digit_ge5(system, task) -> float:
    correct = total = 0
    with torch.no_grad():
        for x, y in task.digit_ge5_probe_batches():
            acts = _settled(system, x).activations
            correct += (_out_from(acts).argmax(-1) == y).sum().item()
            total += len(y)
    return correct / total


class _Ctx:
    def __init__(self, system):
        self.theta = system.geometry.params
        self.device = torch.device("cpu")


def _z(activity: dict[str, Tensor]):
    from computronium.state import CompositeState

    return CompositeState(activity=activity, plastic={}, substrate={})


def _psi_episode(system, plasticity, psi: dict, task, flip: int) -> dict[str, Tensor]:
    x, y = task.batch(flip)
    with torch.no_grad():
        acts = _settled(system, x).activations
        act_list = acts if isinstance(acts, list) else [acts]
        activity = {
            "x": x,
            "h": act_list[-2],
            "y": _out_from(acts),
            "target": y,
        }
        psi = plasticity.step(psi, _z(activity), _Ctx(system))  # type: ignore[arg-type]
    return psi


def _make_plasticity(arm: str):
    if arm == "adaptive":
        return ConflictAdaptivePsiPlasticity(
            ConflictAdaptivePsiConfig(ridge_lambda=RIDGE_LAMBDA)
        )
    if arm == "temporal_090":
        return TemporalPsiPlasticity(
            TemporalPsiConfig(
                trace_decay=0.9, ridge_lambda=RIDGE_LAMBDA, replace_readout=True
            )
        )
    return TemporalPsiPlasticity(
        TemporalPsiConfig(
            trace_decay=1.0, ridge_lambda=RIDGE_LAMBDA, replace_readout=True
        )
    )


def _run_arm(arm: str, seed: int, task: MNISTTasks) -> ArmRun:
    torch.manual_seed(seed)
    task._gen.manual_seed(seed)
    system = compose_system_from_configs(
        SubstrateConfig.digital(),
        GeometryConfig.feedforward(input_dim=784, output_dim=2, hidden_dims=(128,)),
        StateDynamicsConfig.instantaneous(),
        CreditAssignmentConfig.gradient(),
        ParameterUpdateConfig.euclidean(step_size=LR),
    )
    a_mastery = _train_stage_a(system, task)
    result = ArmRun(
        a_mastery=a_mastery,
        null_floors=[],
        phase_accs=[],
        rho_used=[],
        agreements=[],
        switch_lags=[],
        false_conflict_rate=0.0,
        theta_invariant=False,
    )
    if arm == "frozen_null":
        result["null_floors"] = [_probe(system, task, f) for f in (0, 1)]
        result["phase_accs"] = [result["null_floors"][f] for f in PHASES]
        result["theta_invariant"] = True
        return result
    plasticity = _make_plasticity(arm)
    adaptive = arm == "adaptive"
    psi: dict[str, Tensor] = {}
    _freeze(system)
    hash_before = _theta_sha256(system)
    with FrozenThetaAudit(system):
        for p_i, flip in enumerate(PHASES):
            if p_i == 0:
                result["null_floors"] = [
                    _probe(system, task, 0),
                    _probe(system, task, 1),
                ]
            for i in range(PHASE_EPISODES):
                psi = _psi_episode(system, plasticity, psi, task, flip)
                if adaptive:
                    result["rho_used"].append(psi["rho_used"].item())
                    result["agreements"].append(psi["agreement"].item())
            result["phase_accs"].append(
                _probe_modulated(system, plasticity, psi, task, flip)
            )
        result["theta_invariant"] = hash_before == _theta_sha256(system)
    return result


def _freeze(system) -> None:
    for p in system.geometry.params.values():
        p.requires_grad_(False)


def _switch_metrics(rho_used: list[float], phases, phase_len: int):
    """Switch lag after each flip + steady-phase false-conflict rate."""
    lags: list[int | None] = []
    steady_conflicts = steady_total = 0
    for p, flip in enumerate(phases):
        start = p * phase_len
        phase_rho = rho_used[start : start + phase_len]
        if p > 0:
            lag = next((k for k, r in enumerate(phase_rho, 1) if r < 0.99), None)
            lags.append(lag)
        for k, r in enumerate(phase_rho, 1):
            if k > 5:  # exclude the post-flip detection window
                steady_total += 1
                steady_conflicts += r < 0.99
    rate = steady_conflicts / steady_total if steady_total else 0.0
    return lags, rate


def run_probe() -> dict[str, object]:
    t0 = time.time()
    task = MNISTTasks()
    runs: dict[str, list[ArmRun]] = {
        arm: [_run_arm(arm, seed, task) for seed in SEEDS] for arm in ARMS
    }
    adaptive = runs["adaptive"]
    for r in adaptive:
        r["switch_lags"], r["false_conflict_rate"] = _switch_metrics(
            r["rho_used"], PHASES, PHASE_EPISODES
        )
    temporal = runs["temporal_090"]
    p1 = {
        seed: all(
            r["phase_accs"][p] - r["null_floors"][PHASES[p]] >= 0.10
            for p in range(len(PHASES))
        )
        for seed, r in enumerate(adaptive)
    }
    p2 = {
        seed: (
            sum(r["phase_accs"]) / len(PHASES)
            >= sum(t["phase_accs"]) / len(PHASES) - 0.02
        )
        for seed, (r, t) in enumerate(zip(adaptive, temporal, strict=True))
        if r["theta_invariant"]
    }
    p3 = {
        seed: all(
            lag is not None and lag <= SWITCH_LAG_LIMIT for lag in r["switch_lags"]
        )
        and r["false_conflict_rate"] <= FALSE_CONFLICT_LIMIT
        for seed, r in enumerate(adaptive)
        if r["theta_invariant"]
    }
    p1_supported = sum(p1.values()) >= 2
    p2_supported = sum(p2.values()) >= 2
    p3_supported = sum(p3.values()) >= 2
    all_invariant = all(r["theta_invariant"] for rs in runs.values() for r in rs)
    return {
        "arms": runs,
        "p1_wins": p1,
        "p2_wins": p2,
        "p3_wins": p3,
        "p1_supported": p1_supported,
        "p2_supported": p2_supported,
        "p3_supported": p3_supported,
        "self_switching_supported": p1_supported and p2_supported and p3_supported,
        "frozen_theta_invariant": all_invariant,
        "n_seeds": len(SEEDS),
        "walltime_s": time.time() - t0,
    }


def _ingest_ceec(result: dict[str, object]) -> None:
    from computronium.ceec import selection
    from computronium.ceec.probe_adapter import ingest_verdict
    from computronium.ceec.store import CEECStore

    arms: dict[str, list[ArmRun]] = result["arms"]  # type: ignore[assignment]
    output = {
        "status": "ok" if result["frozen_theta_invariant"] else "missing",
        "kind": "tensor",
        "scope": {
            "domain": "plasticity",
            "substrate": ["digital"],
            "budget": "quick",
        },
        "axes": ["arm", "seed", "phase"],
        "values": {
            arm: {
                "a_mastery": [r["a_mastery"] for r in rs],
                "null_floors": [r["null_floors"] for r in rs],
                "phase_accs": [r["phase_accs"] for r in rs],
                "switch_lags": [r["switch_lags"] for r in rs],
                "false_conflict_rate": [r["false_conflict_rate"] for r in rs],
            }
            for arm, rs in arms.items()
        },
        "quality": {
            "seeds": len(SEEDS),
            "matched_control": True,
            "frozen_theta_audit": result["frozen_theta_invariant"],
            "evaluation_policy": "MNIST backbone trained on digit>=5 (theta then "
            "bitwise-frozen, SHA-256 + FrozenThetaAudit); UNLABELED four-phase "
            "alternating parity stream (150 episodes each); probe accuracy on "
            "20 held-out test batches per phase; controls = fixed temporal_090, "
            "closed_form rho=1, frozen_null; adaptive arm's rho trajectory "
            "recorded per episode",
            "defect_audit": "pass" if result["frozen_theta_invariant"] else "fail",
            "identity_card": "ConflictAdaptivePsiPlasticity carded (G-HARD-9)",
            "reproduction": True,
            "verification_level": 4,
        },
        "defects": []
        if result["frozen_theta_invariant"]
        else ["theta invariance failed"],
        "summary": {
            "p1_supported": result["p1_supported"],
            "p2_supported": result["p2_supported"],
            "p3_supported": result["p3_supported"],
            "self_switching_supported": result["self_switching_supported"],
            "p1_wins": result["p1_wins"],
            "p2_wins": result["p2_wins"],
            "p3_wins": result["p3_wins"],
        },
        "summary_operator": "per_seed_adaptive_vs_fixed_temporal_alternating",
        "notes": "X-TAC-001 conflict-adaptive psi probe: self-switching trace "
        "decay on an unlabeled alternating parity stream, theta frozen",
    }
    p1, p2, p3 = (
        bool(result["p1_supported"]),
        bool(result["p2_supported"]),
        bool(result["p3_supported"]),
    )
    full = p1 and p2 and p3
    new_interval = (
        (0.45, 0.70)
        if full
        else ((0.40, 0.60) if p1 and p2 else ((0.20, 0.45) if p1 else (0.05, 0.25)))
    )
    rationale = (
        f"P1 acquisition={p1} (wins {result['p1_wins']}), "
        f"P2 matches temporal_090={p2} (wins {result['p2_wins']}), "
        f"P3 detection={p3} (wins {result['p3_wins']}), "
        f"theta_invariant={result['frozen_theta_invariant']}"
    )
    with CEECStore(
        REPO_ROOT / "ceec" / "ceec.sqlite3", REPO_ROOT / "ceec" / "artifacts"
    ) as store:
        verdict = ingest_verdict(
            store,
            probe_name="X-TAC-001",
            probe_output=output,
            belief_id="B-H2-TEMPORAL-PSI-CREDIT",
            new_interval=new_interval,
            rationale=rationale,
            outcome="self_switching_supported"
            if full
            else (
                "acquisition_and_matching"
                if p1 and p2
                else ("acquisition_only" if p1 else "no_acquisition")
            ),
            outcome_boolean=full,
            notes="X-TAC-001 outcome vs pre-registered P1/P2/P3 (self-switching "
            "trace decay, unlabeled stream)",
            experiment_config=REPO_ROOT
            / "configs"
            / "ceec"
            / "experiments"
            / "conflict_adaptive_psi.yaml",
        )
        failed = [r.gate for r in verdict.evaluation.results if not r.passed]
        print(f"promotion gates failed: {failed or 'none'}")
        print(
            f"calibration: {verdict.calibration.id if verdict.calibration else 'n/a'}"
        )
        print(f"audit violations: {len(verdict.violations)}")
        for f in verdict.violations:
            print(f"  {f.check}: {f.detail}")
        profile = selection.load_profile(
            REPO_ROOT / "configs" / "ceec" / "profile.yaml"
        )
        decision = selection.decide(
            store, profile, rationale="post X-TAC-001 adaptive-psi component"
        )
        print(f"next selection: {decision.selected_experiment}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ceec", action="store_true", help="ingest into CEEC ledger")
    args = parser.parse_args()
    result = run_probe()
    compact = {k: v for k, v in result.items() if k != "arms"}
    print(json.dumps(compact, indent=2, default=str))
    arms: dict[str, list[ArmRun]] = result["arms"]  # type: ignore[assignment]
    for arm, rs in arms.items():
        cells = [
            f"A={r['a_mastery']:.3f} phases={[round(a, 3) for a in r['phase_accs']]}"
            for r in rs
        ]
        print(f"{arm:12s} {cells}")
    adaptive = arms["adaptive"]
    for seed, r in enumerate(adaptive):
        rho = r["rho_used"]
        switches = [i for i in range(1, len(rho)) if abs(rho[i] - rho[i - 1]) > 0.25]
        print(
            f"adaptive seed {seed}: rho switch episodes {switches[:12]}, "
            f"lags={r['switch_lags']}, false_conflict={r['false_conflict_rate']:.3f}"
        )
    if args.ceec:
        _ingest_ceec(result)
    print(f"walltime: {result['walltime_s']:.2f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
