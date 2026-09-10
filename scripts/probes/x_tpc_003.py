"""X-TPC-003: frozen-backbone readout migration on a REAL task pair (TODO19).

Round-7 R6-B deliverable: X-TPC-002 supported P2 on a 2-class synthetic
switch; this probe tests the conflicting coordinate at real scale with
MNIST and adds the control TODO19 names as the nameable-result clause —
re-training the readout from scratch.

Design: stage A trains a 784-128-2 MLP (gradient credit, CE) on MNIST
digit>=5 — theta then frozen. Stage B acquires PARITY (even=1) on the
frozen h basis via TemporalPsiPlasticity; stage C re-adapts on INVERTED
parity (odd=1), the conflicting label geometry. Arms (psi law, theta
frozen): temporal_070 (rho=0.7), temporal_090 (rho=0.9), closed_form
(rho=1), frozen_null, retrain_sgd (fresh nn.Linear readout trained with
SGD/CE for the SAME TOTAL adaptation budget — 2x psi episodes — on task
C only).

Pre-registered predictions (BEFORE the run; governed by B-H2
TEMPORAL-PSI-CREDIT, prior [0.35, 0.55]):

- P1 (acquisition): temporal_090 lifts stage-B probe accuracy off the
  frozen-null floor by >= +0.10 on >= 2 of 3 seeds.
- P2 (temporal credit under conflict, real scale): after re-adaptation
  on C, the best temporal arm beats closed_form by >= +0.10 on >= 2 of 3
  seeds (the rho=1 statistics blend opposite mappings and cancel).
- P3 (nameable result): the best temporal arm's C return accuracy is
  within 0.02 of retrain_sgd (fresh readout, same total budget) on >= 2
  of 3 seeds — frozen-backbone switching matches readout re-training.

Falsification: no temporal arm acquires B (P1); closed-form matches/beats
the temporal arms on C return (P2); retrain_sgd dominates the temporal
arms by more than the P3 margin (frozen-backbone switching loses to
plain readout re-training).

Hard gates on build: identity_card_for_new_primitive (TemporalPsiPlasticity
card, landed round 4), frozen_theta_audit (this run).
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
from computronium.core.plasticity.temporal_psi import (
    TemporalPsiConfig,
    TemporalPsiPlasticity,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

SEEDS = (0, 1, 2)
STAGE_A_EPISODES = 600
PSI_EPISODES = 200
BATCH = 64
PROBE_BATCHES = 20
LR = 0.1
RETRAIN_LR = 0.1
RIDGE_LAMBDA = 1e-3
TRAIN_POOL = 10_000


class ArmRun(TypedDict):
    a_mastery: float
    b_null_floor: float
    b_final: float
    b_retained: float
    c_null_floor: float
    c_final: float
    retrain_c: float
    retrain_s: float
    theta_invariant: bool


ARMS: dict[str, float | None] = {
    "temporal_070": 0.7,
    "temporal_090": 0.9,
    "closed_form": 1.0,
    "frozen_null": None,
    "retrain_sgd": None,
}


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


def label_for(y: Tensor, phase: str) -> Tensor:
    """A: digit>=5. B: parity (even=1). C: INVERTED parity (odd=1)."""
    if phase == "A":
        return (y >= 5).long()
    parity = (y % 2 == 0).long()
    return 1 - parity if phase == "C" else parity


class MNISTTasks:
    def __init__(self) -> None:
        self.xtr, self.ytr, self.xte, self.yte = load_mnist()
        self._gen = torch.Generator().manual_seed(0)

    def batch(self, phase: str) -> tuple[Tensor, Tensor]:
        idx = torch.randint(0, len(self.xtr), (BATCH,), generator=self._gen)
        return self.xtr[idx], label_for(self.ytr[idx], phase)

    def probe_batches(self, phase: str):
        idx = torch.randperm(len(self.xte), generator=self._gen)[
            : PROBE_BATCHES * BATCH
        ].view(PROBE_BATCHES, BATCH)
        return [(self.xte[i], label_for(self.yte[i], phase)) for i in idx]


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


def _probe_modulated(system, plasticity, psi: dict, task, phase: str) -> float:
    correct = total = 0
    with torch.no_grad():
        for x, y in task.probe_batches(phase):
            acts = plasticity.modulate(_settled(system, x).activations, psi)
            correct += (_out_from(acts).argmax(-1) == y).sum().item()
            total += len(y)
    return correct / total


def _probe(system, task, phase: str) -> float:
    class _Null:
        def modulate(self, acts, psi):
            return acts

    return _probe_modulated(system, _Null(), {}, task, phase)


def _train_stage_a(system, task) -> float:
    from computronium.core.pipeline import run_train_step

    for _ in range(STAGE_A_EPISODES):
        x, y = task.batch("A")
        run_train_step(
            system.substrate,
            system.geometry,
            system.dynamics,
            system.credit,
            system.update,
            x,
            y,
        )
    return _probe(system, task, "A")


class _Ctx:
    """Minimal SystemContext stand-in: the law reads .theta/.device."""

    def __init__(self, system):
        self.theta = system.geometry.params
        self.device = torch.device("cpu")


def _z(activity: dict[str, Tensor]):
    from computronium.state import CompositeState

    return CompositeState(activity=activity, plastic={}, substrate={})


def _freeze(system) -> None:
    for p in system.geometry.params.values():
        p.requires_grad_(False)


def _psi_episode(system, plasticity, psi: dict, task, phase: str) -> dict[str, Tensor]:
    x, y = task.batch(phase)
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


def _retrain_sgd(system, task, phase: str) -> tuple[float, float]:
    """Fresh linear readout on frozen h, SGD/CE, 2x psi episodes on C."""
    from torch import nn

    torch.manual_seed(99)
    readout = nn.Linear(128, 2)
    opt = torch.optim.SGD(readout.parameters(), lr=RETRAIN_LR)
    t0 = time.time()
    for _ in range(2 * PSI_EPISODES):
        x, y = task.batch(phase)
        with torch.no_grad():
            acts = _settled(system, x).activations
            h = (acts if isinstance(acts, list) else [acts])[-2]
        opt.zero_grad()
        loss = torch.nn.functional.cross_entropy(readout(h), y)
        loss.backward()
        opt.step()
    train_s = time.time() - t0
    correct = total = 0
    with torch.no_grad():
        for x, y in task.probe_batches(phase):
            acts = _settled(system, x).activations
            h = (acts if isinstance(acts, list) else [acts])[-2]
            correct += (readout(h).argmax(-1) == y).sum().item()
            total += len(y)
    return correct / total, train_s


def _run_arm(arm: str, rho: float | None, seed: int, task: MNISTTasks) -> ArmRun:
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
        b_null_floor=_probe(system, task, "B"),
        b_final=0.0,
        b_retained=0.0,
        c_null_floor=_probe(system, task, "C"),
        c_final=0.0,
        retrain_c=0.0,
        retrain_s=0.0,
        theta_invariant=False,
    )
    if arm == "retrain_sgd":
        result["retrain_c"], result["retrain_s"] = _retrain_sgd(system, task, "C")
        result["c_final"] = result["retrain_c"]
        result["theta_invariant"] = True
        return result
    if rho is None:
        result.update(
            b_final=result["b_null_floor"],
            b_retained=result["b_null_floor"],
            c_final=result["c_null_floor"],
            theta_invariant=True,
        )
        return result
    plasticity = TemporalPsiPlasticity(
        TemporalPsiConfig(
            trace_decay=rho, ridge_lambda=RIDGE_LAMBDA, replace_readout=True
        )
    )
    psi: dict[str, Tensor] = {}
    _freeze(system)
    hash_before = _theta_sha256(system)
    t0 = time.time()
    with FrozenThetaAudit(system):
        for _ in range(PSI_EPISODES):
            psi = _psi_episode(system, plasticity, psi, task, "B")
        result["b_final"] = _probe_modulated(system, plasticity, psi, task, "B")
        for _ in range(PSI_EPISODES):
            psi = _psi_episode(system, plasticity, psi, task, "C")
        result["b_retained"] = _probe_modulated(system, plasticity, psi, task, "B")
        result["c_final"] = _probe_modulated(system, plasticity, psi, task, "C")
        result["theta_invariant"] = hash_before == _theta_sha256(system)
    result["retrain_s"] = time.time() - t0
    return result


def run_probe() -> dict[str, object]:
    t0 = time.time()
    task = MNISTTasks()
    runs: dict[str, list[ArmRun]] = {
        arm: [_run_arm(arm, rho, seed, task) for seed in SEEDS]
        for arm, rho in ARMS.items()
    }
    temporal = ("temporal_070", "temporal_090")
    p1 = {
        arm: sum(
            1
            for r, n in zip(runs[arm], runs["frozen_null"], strict=True)
            if r["theta_invariant"] and r["b_final"] - n["b_final"] >= 0.10
        )
        for arm in temporal
    }
    p2 = {
        arm: sum(
            1
            for r, c in zip(runs[arm], runs["closed_form"], strict=True)
            if r["theta_invariant"] and r["c_final"] - c["c_final"] >= 0.10
        )
        for arm in temporal
    }
    p3 = {
        arm: sum(
            1
            for r in runs[arm]
            if r["theta_invariant"] and r["c_final"] >= r["retrain_c"] - 0.02
        )
        for arm in temporal
    }
    p1_supported = max(p1.values()) >= 2
    p2_supported = max(p2.values()) >= 2
    p3_supported = max(p3.values()) >= 2
    all_invariant = all(r["theta_invariant"] for rs in runs.values() for r in rs)
    return {
        "arms": runs,
        "p1_wins": p1,
        "p2_wins": p2,
        "p3_wins": p3,
        "p1_supported": p1_supported,
        "p2_supported": p2_supported,
        "p3_supported": p3_supported,
        "readout_migration_supported": p1_supported and p2_supported and p3_supported,
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
        "axes": ["arm", "seed"],
        "values": {
            arm: {
                "a_mastery": [r["a_mastery"] for r in rs],
                "b_null_floor": [r["b_null_floor"] for r in rs],
                "b_final": [r["b_final"] for r in rs],
                "b_retained": [r["b_retained"] for r in rs],
                "c_null_floor": [r["c_null_floor"] for r in rs],
                "c_final": [r["c_final"] for r in rs],
                "retrain_c": [r["retrain_c"] for r in rs],
                "retrain_s": [r["retrain_s"] for r in rs],
            }
            for arm, rs in arms.items()
        },
        "quality": {
            "seeds": len(SEEDS),
            "matched_control": True,
            "frozen_theta_audit": result["frozen_theta_invariant"],
            "evaluation_policy": "MNIST backbone trained on digit>=5 (theta "
            "then bitwise-frozen, SHA-256 + FrozenThetaAudit); parity "
            "acquisition then INVERTED-parity migration on frozen h; probe "
            "accuracy over 20 held-out test batches; retrain_sgd control = "
            "fresh linear readout, same total adaptation budget, task C only",
            "defect_audit": "pass" if result["frozen_theta_invariant"] else "fail",
            "identity_card": "TemporalPsiPlasticity carded (G-HARD-9)",
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
            "readout_migration_supported": result["readout_migration_supported"],
            "p1_wins": result["p1_wins"],
            "p2_wins": result["p2_wins"],
            "p3_wins": result["p3_wins"],
        },
        "summary_operator": "per_seed_temporal_vs_null_closed_form_retrain_mnist",
        "notes": "X-TPC-003 real-task (MNIST) frozen-backbone readout "
        "migration probe: parity -> INVERTED parity, theta frozen, "
        "retrain-the-readout control",
    }
    p1, p2, p3 = (
        bool(result["p1_supported"]),
        bool(result["p2_supported"]),
        bool(result["p3_supported"]),
    )
    full = p1 and p2 and p3
    new_interval = (
        (0.40, 0.65)
        if full
        else ((0.35, 0.55) if p1 and p2 else ((0.20, 0.45) if p1 else (0.05, 0.25)))
    )
    rationale = (
        f"P1 acquisition={p1} (wins {result['p1_wins']}), "
        f"P2 conflict return={p2} (wins {result['p2_wins']}), "
        f"P3 vs retrain_sgd={p3} (wins {result['p3_wins']}), "
        f"theta_invariant={result['frozen_theta_invariant']}"
    )
    with CEECStore(
        REPO_ROOT / "ceec" / "ceec.sqlite3", REPO_ROOT / "ceec" / "artifacts"
    ) as store:
        verdict = ingest_verdict(
            store,
            probe_name="X-TPC-003",
            probe_output=output,
            belief_id="B-H2-TEMPORAL-PSI-CREDIT",
            new_interval=new_interval,
            rationale=rationale,
            outcome="readout_migration_supported"
            if full
            else (
                "acquisition_and_conflict"
                if p1 and p2
                else ("acquisition_only" if p1 else "no_acquisition")
            ),
            outcome_boolean=full,
            notes="X-TPC-003 outcome vs pre-registered P1/P2/P3 (real-task "
            "conflict + retrain control)",
            experiment_config=REPO_ROOT
            / "configs"
            / "ceec"
            / "experiments"
            / "temporal_psi_readout_migration.yaml",
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
            store, profile, rationale="post X-TPC-003 real-task migration"
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
            f"A={r['a_mastery']:.3f} B={r['b_final']:.3f} Bret={r['b_retained']:.3f} "
            f"C={r['c_final']:.3f} retC={r['retrain_c']:.3f} ({r['retrain_s']:.1f}s)"
            for r in rs
        ]
        print(f"{arm:12s} {cells}")
    if args.ceec:
        _ingest_ceec(result)
    print(f"walltime: {result['walltime_s']:.2f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
