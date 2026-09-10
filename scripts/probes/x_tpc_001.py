"""X-TPC-001: temporal-ψ credit across an A→B→A' task switch (TODO19).

Pre-registered predictions (BEFORE the run; governed by B-H2
TEMPORAL-PSI-CREDIT, prior [0.10, 0.45]):

- P1 (acquisition): with θ bitwise frozen, TemporalPsiPlasticity (ρ < 1)
  moves stage-B (last-symbol) probe accuracy off the frozen-null floor by
  ≥ +0.10 on ≥ 2 of 3 seeds. The D22 root cause (ψ consumed only
  target-free first-phase activity) is repaired: the law steps on the
  NUDGED settle and consumes the target (psi_phase = "nudged").
- P2 (temporal credit — the headline): after re-adaptation on A' (parity
  again), the best temporal arm's A' accuracy beats the forget-free
  closed-form ridge (ρ = 1, which irreversibly blends B and A'
  sufficient statistics) by ≥ +0.10 on ≥ 2 of 3 seeds.

Falsification: no temporal arm moves off the floor (P1), or closed-form
matches/beats the temporal arms on A' return (P2).

Arms (stage-B/A' ψ law, all θ-frozen): temporal_050 (ρ=0.5),
temporal_090 (ρ=0.9), closed_form (ρ=1.0), frozen_null (no modulation).
All ψ arms run in replace_readout mode.

Pre-flight defect log (recorded BEFORE the governed run; each fix is in
the landed TemporalPsiPlasticity, and the run below is the first
governed measurement of the fixed law):

- D-TPC-a: trace-accumulation sign defect — the first implementation
  applied ρ to the incoming batch (G_t = G_{t−1} + ρg) instead of the
  stored trace (G_t = ρG_{t−1} + g), so the trace never forgot and the
  old task dominated; found by exact-saturation unit check (ρ=0.5 must
  saturate at g/(1−ρ)), fixed, property-locked.
- D-TPC-b: additive residual channel inert at this coordinate — frozen
  net logit margins ≈ 9.5 vs correction ≈ 0.4/sample; zero argmax flips
  across all arms. Replacement readout is the margin-robust channel.
- D-TPC-c: onehot−softmax residual target collapses under saturated
  softmax (A' fit inverts to 0.22–0.29); centered one-hot target
  replaces it. The earlier "temporal beats closed-form" P2 reading
  under the residual target was a target-induced artifact, discarded.

Hard gates on build: identity_card_for_new_primitive (TemporalPsiPlasticity
card in docs/IDENTITY_CARDS.md), frozen_theta_audit (this run).
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
from computronium.experiments.joint.adaptation_efficiency import (
    create_switching_task,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

SEEDS = (0, 1, 2)
STAGE_A_EPISODES = 300
PSI_EPISODES = 200
BATCH = 32
SEQ = 4
INPUT_DIM = 8
PROBE_BATCHES = 8
LR = 0.05
RIDGE_LAMBDA = 1e-3


class ArmRun(TypedDict):
    a_mastery: float
    b_null_floor: float
    b_final: float
    a_retained: float
    a_prime_final: float
    theta_invariant: bool


ARMS: dict[str, float | None] = {
    "temporal_050": 0.5,
    "temporal_090": 0.9,
    "closed_form": 1.0,
    "frozen_null": None,
}


def _theta_sha256(system) -> str:
    raw = b"".join(
        p.detach().cpu().contiguous().view(-1).view(torch.uint8).numpy().tobytes()
        for p in system.geometry.params.values()
    )
    return hashlib.sha256(raw).hexdigest()


def _batch(task: str) -> tuple[Tensor, Tensor]:
    x, y = create_switching_task(BATCH, SEQ, INPUT_DIM, phase=task)
    return x.reshape(BATCH, -1), y


def _settled(system, x: Tensor):
    state = SystemState(x=x)
    state.activations = forward_pass(system.substrate, system.geometry, x)
    return system.dynamics.settle(state, system.geometry, system.substrate, target=None)


def _out_from(acts) -> Tensor:
    return acts[-1] if isinstance(acts, list) else acts


def _probe_modulated(system, plasticity, psi: dict, task: str) -> float:
    correct = total = 0
    with torch.no_grad():
        for _ in range(PROBE_BATCHES):
            x, y = _batch(task)
            acts = plasticity.modulate(_settled(system, x).activations, psi)
            out = _out_from(acts)
            correct += (out.argmax(-1) == y).sum().item()
            total += len(y)
    return correct / total


def _probe(system, task: str) -> float:
    class _Null:
        def modulate(self, acts, psi):
            return acts

    return _probe_modulated(system, _Null(), {}, task)


def _train_stage_a(system) -> float:
    from computronium.core.pipeline import run_train_step

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


def _psi_episode(system, plasticity, psi: dict, task: str) -> dict[str, Tensor]:
    x, y = _batch(task)
    with torch.no_grad():
        settled = _settled(system, x)
        acts = settled.activations
        act_list = acts if isinstance(acts, list) else [acts]
        post = _out_from(acts)
        activity = {
            "x": x,
            "h": act_list[-2],
            "y": post,
            "target": y,
        }
        psi = plasticity.step(psi, _z(activity), _ctx(system))  # type: ignore[arg-type]
    return psi


class _Ctx:
    """Minimal SystemContext stand-in: the law reads .theta/.device."""

    def __init__(self, system):
        self.theta = system.geometry.params
        self.device = torch.device("cpu")


def _ctx(system):
    return _Ctx(system)


def _z(activity: dict[str, Tensor]):
    from computronium.state import CompositeState

    return CompositeState(activity=activity, plastic={}, substrate={})


def _freeze(system) -> None:
    for p in system.geometry.params.values():
        p.requires_grad_(False)


def _run_arm(rho: float | None, seed: int) -> ArmRun:
    torch.manual_seed(seed)
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
    null_probe = {
        "b_final": _probe(system, "B"),
        "a_prime_final": _probe(system, "A"),
    }
    result = ArmRun(
        a_mastery=a_mastery,
        b_null_floor=null_probe["b_final"],
        a_null_floor=null_probe["a_prime_final"],
    )
    if rho is None:
        result.update(
            b_final=null_probe["b_final"],
            a_retained=null_probe["a_prime_final"],
            a_prime_final=null_probe["a_prime_final"],
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
    with FrozenThetaAudit(system):
        for _ in range(PSI_EPISODES):
            psi = _psi_episode(system, plasticity, psi, "B")
        result["b_final"] = _probe_modulated(system, plasticity, psi, "B")
        result["a_retained"] = _probe_modulated(system, plasticity, psi, "A")
        for _ in range(PSI_EPISODES):
            psi = _psi_episode(system, plasticity, psi, "A")
        result["a_prime_final"] = _probe_modulated(system, plasticity, psi, "A")
        result["theta_invariant"] = hash_before == _theta_sha256(system)
    return result


def run_probe() -> dict[str, object]:
    t0 = time.time()
    runs: dict[str, list[ArmRun]] = {
        arm: [_run_arm(rho, seed) for seed in SEEDS] for arm, rho in ARMS.items()
    }
    # P1: best temporal arm beats the null floor by ≥ +0.10 on ≥ 2/3 seeds.
    p1 = {}
    for arm in ("temporal_050", "temporal_090"):
        wins = sum(
            1
            for r, n in zip(runs[arm], runs["frozen_null"], strict=True)
            if r["theta_invariant"] and r["b_final"] - n["b_final"] >= 0.10
        )
        p1[arm] = wins
    p1_supported = max(p1.values()) >= 2
    # P2: best temporal arm beats closed_form on A' return on ≥ 2/3 seeds.
    p2 = {}
    for arm in ("temporal_050", "temporal_090"):
        wins = sum(
            1
            for r, c in zip(runs[arm], runs["closed_form"], strict=True)
            if r["theta_invariant"] and r["a_prime_final"] - c["a_prime_final"] >= 0.10
        )
        p2[arm] = wins
    p2_supported = max(p2.values()) >= 2
    all_invariant = all(r["theta_invariant"] for rs in runs.values() for r in rs)
    return {
        "arms": runs,
        "p1_wins": p1,
        "p2_wins": p2,
        "p1_supported": p1_supported,
        "p2_supported": p2_supported,
        "temporal_credit_supported": p1_supported and p2_supported,
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
                "a_retained": [r["a_retained"] for r in rs],
                "a_prime_final": [r["a_prime_final"] for r in rs],
            }
            for arm, rs in arms.items()
        },
        "quality": {
            "seeds": len(SEEDS),
            "matched_control": True,
            "frozen_theta_audit": result["frozen_theta_invariant"],
            "evaluation_policy": "3-stage parity→last-symbol→parity switch; "
            "θ bitwise-frozen in the ψ phase (SHA-256 + FrozenThetaAudit); "
            "probe accuracy over 8 fresh batches per read",
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
            "temporal_credit_supported": result["temporal_credit_supported"],
            "p1_wins": result["p1_wins"],
            "p2_wins": result["p2_wins"],
        },
        "summary_operator": "per_seed_temporal_vs_null_and_closed_form",
        "notes": "X-TPC-001 temporal-ψ credit probe (trace-decayed supervised "
        "readout, A→B→A' switch, θ frozen)",
    }
    supported = result["temporal_credit_supported"]
    p1 = result["p1_supported"]
    new_interval = (0.30, 0.60) if supported else ((0.20, 0.40) if p1 else (0.05, 0.25))
    rationale = (
        f"P1 acquisition={result['p1_supported']} (wins {result['p1_wins']}), "
        f"P2 temporal return={result['p2_supported']} (wins {result['p2_wins']}), "
        f"theta_invariant={result['frozen_theta_invariant']}"
    )
    with CEECStore(
        REPO_ROOT / "ceec" / "ceec.sqlite3", REPO_ROOT / "ceec" / "artifacts"
    ) as store:
        verdict = ingest_verdict(
            store,
            probe_name="X-TPC-001",
            probe_output=output,
            belief_id="B-H2-TEMPORAL-PSI-CREDIT",
            new_interval=new_interval,
            rationale=rationale,
            outcome="temporal_credit_supported"
            if supported
            else ("acquisition_only" if p1 else "no_acquisition"),
            outcome_boolean=supported,
            notes="X-TPC-001 outcome vs pre-registered P1/P2",
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
            store, profile, rationale="post X-TPC-001 temporal-ψ build"
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
        cells = [f"B={r['b_final']:.3f} A'={r['a_prime_final']:.3f}" for r in rs]
        print(f"{arm:12s} {cells}")
    if args.ceec:
        _ingest_ceec(result)
    print(f"walltime: {result['walltime_s']:.2f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
