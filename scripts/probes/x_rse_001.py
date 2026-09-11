"""X-RSE-001 — CEEC-governed probe for B-H4-ROUTING-SPARSITY-EFFICIENCY.

Question (pre-registered in configs/ceec/experiments/routing_sparsity_efficiency.yaml):
    Does routing reduce effective operations relative to the dense baseline
    on a sparse task?

Arms (backprop credit, instant dynamics, MLP 16→(24,24)→4, 30 steps, 3 seeds):
    dense   — NullPlasticity (6-D coordinate with M=Null, Zero-Extension slice).
    routed  — RoutingPlasticity (gate_dim=16): per-sample per-unit soft mask
              sigmoid(gate_logits @ U_ℓ) modulates every layer's activations.

Task: synthetic sparse classification — only 3 of 16 input features carry
class signal; the other 13 are pure noise. Exploitable sparsity is built in.

Effective ops: dense per-step FLOPs (I-FLOPS-ESTIMATOR,
estimate_train_step_flops) scaled by the realized active-unit fraction
(mean over samples/units of sigmoid(mask) > 0.5 — the hard-selection
criterion RoutingPlasticity.modulate implements at eval). Gate collapse is
checked via compute_gate_entropy (I-RESOURCE-PROFILER).

Evidence kind: tensor (arm × seed metric vectors).

Verdict: effective_ops_reduction >= 10% AND accuracy_loss <= 1 point AND
gates not collapsed.

Run:
    uv run python scripts/probes/x_rse_001.py            # run only
    uv run python scripts/probes/x_rse_001.py --ceec     # run + ingest into ledger
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import NamedTuple, cast

import numpy as np
import torch
from torch import Tensor

REPO_ROOT = Path(__file__).resolve().parents[2]

from computronium.analysis.training_dynamics import compute_gate_entropy
from computronium.core.joint.transition import NullPlasticity
from computronium.core.pipeline import run_train_step
from computronium.core.plasticity import RoutingPlasticity
from computronium.core.presets import (
    _default_credit,
    _default_substrate,
    _mlp_geometry,
)
from computronium.core.profiling import estimate_train_step_flops
from computronium.core.system_trainer import compose_joint_system
from computronium.ontology import (
    EuclideanUpdate,
    InstantaneousDynamics,
    ParameterUpdateConfig,
    StateDynamicsConfig,
)

N_SEEDS = 3
N_STEPS = 30
INPUT_DIM = 16
HIDDEN_DIMS = (24, 24)
OUTPUT_DIM = 4
INFORMATIVE = 3
BATCH = 64
GATE_DIM = 16
LR = 0.005


def make_task(seed: int) -> tuple[Tensor, Tensor]:
    torch.manual_seed(seed + 123)
    xs = torch.randn(BATCH, INPUT_DIM)
    ys = torch.randint(0, OUTPUT_DIM, (BATCH,))
    xs[torch.arange(BATCH), ys % INFORMATIVE] += 2.0 * (ys.float() - 1.5)
    return xs, ys


class _ArmBuild(NamedTuple):
    """The six composed components plus the joint system for one arm."""

    substrate: object
    geometry: object
    dynamics: object
    credit: object
    update: object
    plasticity: object
    joint: object


def _build_arm(seed: int, routed: bool) -> _ArmBuild:
    torch.manual_seed(seed)
    substrate = _default_substrate()
    geometry = _mlp_geometry(INPUT_DIM, HIDDEN_DIMS, OUTPUT_DIM)
    dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    credit = _default_credit()
    update = EuclideanUpdate(
        ParameterUpdateConfig.euclidean(step_size=LR, momentum=0.0)
    )
    plasticity: object = (
        RoutingPlasticity(gate_dim=GATE_DIM, temperature=1.0, decay=0.99)
        if routed
        else NullPlasticity()
    )
    joint = compose_joint_system(
        substrate,
        geometry,
        dynamics,
        plasticity,
        credit,
        update,  # type: ignore[arg-type]
    )
    return _ArmBuild(substrate, geometry, dynamics, credit, update, plasticity, joint)


def _routing_metrics(
    psi: dict[str, Tensor], entropies: list[float], dense_flops: float
) -> tuple[float, float, bool]:
    """Realized active-unit fraction, effective FLOPs, collapse flag."""
    logits = psi.get("gate_logits")
    if logits is None:
        return 1.0, dense_flops, False
    active_fraction = float((torch.sigmoid(logits.detach()) > 0.5).float().mean())
    effective_flops = dense_flops * active_fraction
    collapsed = bool(entropies and entropies[-1] < 0.1 * np.log(GATE_DIM))
    return active_fraction, effective_flops, collapsed


def _train_loop(
    seed: int, routed: bool
) -> tuple[list[float], list[float], list[float], dict[str, Tensor], float]:
    """Run one arm; return (losses, accuracies, entropies, psi, dense_flops)."""
    arm = _build_arm(seed, routed)
    xs, ys = make_task(seed)
    context = arm.joint.context  # type: ignore[attr-defined]
    psi = arm.plasticity.initial_psi(context, batch_size=BATCH)  # type: ignore[union-attr]
    losses: list[float] = []
    accuracies: list[float] = []
    entropies: list[float] = []
    for _ in range(N_STEPS):
        metrics = run_train_step(
            arm.substrate,  # type: ignore[arg-type]
            arm.geometry,  # type: ignore[arg-type]
            arm.dynamics,  # type: ignore[arg-type]
            arm.credit,  # type: ignore[arg-type]
            arm.update,  # type: ignore[arg-type]
            xs,
            ys,
            plasticity=arm.plasticity,
            psi=psi,
            context=context,
        )
        losses.append(metrics["free_loss"])
        accuracies.append(metrics["free_accuracy"])
        logits = psi.get("gate_logits")
        if logits is not None:
            entropies.append(compute_gate_entropy(logits.detach().cpu().numpy()))
    dense_flops = float(estimate_train_step_flops(arm.joint, BATCH))  # type: ignore[arg-type]
    return losses, accuracies, entropies, psi, dense_flops


def run_arm(seed: int, routed: bool) -> dict[str, object]:
    losses, accuracies, entropies, psi, dense_flops = _train_loop(seed, routed)
    active_fraction, effective_flops, collapsed = _routing_metrics(
        psi, entropies, dense_flops
    )
    return {
        "losses": losses,
        "accuracies": accuracies,
        "final_accuracy": accuracies[-1],
        "final_loss": losses[-1],
        "gate_entropy": entropies,
        "active_fraction": active_fraction,
        "dense_flops": dense_flops,
        "effective_flops": effective_flops,
        "gates_collapsed": collapsed,
    }


def run_probe() -> dict[str, object]:
    t0 = time.perf_counter()
    arms = {
        arm: [run_arm(seed, routed=(arm == "routed")) for seed in range(N_SEEDS)]
        for arm in ("dense", "routed")
    }
    reductions = [
        1.0 - r["effective_flops"] / d["effective_flops"]  # type: ignore[operator]
        for d, r in zip(arms["dense"], arms["routed"])
    ]
    accuracy_losses = [
        d["final_accuracy"] - r["final_accuracy"]  # type: ignore[operator]
        for d, r in zip(arms["dense"], arms["routed"])
    ]
    no_collapse = not any(a["gates_collapsed"] for a in arms["routed"])
    verdict = (
        all(red >= 0.10 for red in reductions)
        and all(loss <= 0.01 for loss in accuracy_losses)
        and no_collapse
    )
    walltime = time.perf_counter() - t0
    return {
        "arms": arms,
        "effective_ops_reductions": reductions,
        "accuracy_losses": accuracy_losses,
        "no_gate_collapse": no_collapse,
        "routing_benefits": verdict,
        "walltime_s": walltime,
        "n_seeds": N_SEEDS,
        "n_steps": N_STEPS,
    }


def _probe_output(result: dict[str, object]) -> dict[str, object]:
    """E.1 probe contract for X-RSE-001."""
    arms = cast("dict[str, list[dict[str, object]]]", result["arms"])
    live = all(
        cast("float", a["final_accuracy"]) > 0.25 for arm in arms.values() for a in arm
    )
    return {
        "status": "ok" if live else "inert",
        "kind": "tensor",
        "scope": {
            "domain": "resources",
            "substrate": ["digital", "sparse"],
            "budget": "quick",
        },
        "axes": ["arm", "seed"],
        "values": {
            arm: {
                "accuracies": [a["accuracies"] for a in runs],
                "gate_entropy": [a["gate_entropy"] for a in runs],
                "active_fraction": [a["active_fraction"] for a in runs],
                "effective_flops": [a["effective_flops"] for a in runs],
                "dense_flops": [a["dense_flops"] for a in runs],
            }
            for arm, runs in arms.items()
        },
        "quality": {
            "seeds": N_SEEDS,
            "matched_control": True,
            "evaluation_policy": "final free_accuracy and realized active-unit "
            "fraction over 30 steps, 3 seeds, identical structure/seed",
            "defect_audit": "pass" if live else "fail",
            "reproduction": True,
            "verification_level": 4,
        },
        "defects": [] if live else ["channel inert (all arms at chance)"],
        "summary": {
            "routing_benefits": result["routing_benefits"],
            "effective_ops_reductions": result["effective_ops_reductions"],
            "accuracy_losses": result["accuracy_losses"],
            "no_gate_collapse": result["no_gate_collapse"],
        },
        "summary_operator": "per_seed_reduction_and_loss",
        "notes": "X-RSE-001 routed-vs-dense effective-ops probe on a "
        "3-informative-feature sparse task",
    }


def _ingest_ceec(result: dict[str, object]) -> None:
    """Full governance loop into the real ledger (X-RSE-001)."""
    from computronium.ceec import audit, calibration, gates, models, selection
    from computronium.ceec.probe_adapter import record_probe_result
    from computronium.ceec.store import CEECStore

    output = _probe_output(result)

    with CEECStore(
        REPO_ROOT / "ceec" / "ceec.sqlite3", REPO_ROOT / "ceec" / "artifacts"
    ) as store:
        probe_result = record_probe_result(store, output, "X-RSE-001")
        belief_id = "B-H4-ROUTING-SPARSITY-EFFICIENCY"
        store._link(
            store._conn,
            "belief_evidence",
            "belief_id",
            belief_id,
            "evidence_id",
            [probe_result.evidence.id],
        )
        store._conn.commit()

        benefits = bool(result["routing_benefits"])
        prior = store.latest_revision(belief_id)
        prior_span = (
            f"[{prior.probability.low}, {prior.probability.high}]" if prior else "none"
        )
        new_low, new_high = (0.20, 0.55) if benefits else (0.05, 0.35)
        store.update_belief(
            belief_id,
            models.Probability(
                low=new_low,
                high=new_high,
                method="heuristic_interval_based_on_gate_evidence",
            ),
            "medium",
            "medium",
            "narrow",
            "open",
            f"X-RSE-001: routing benefits (>=10% ops reduction, <=1pt accuracy "
            f"loss, no collapse) = {benefits} (prior {prior_span})",
        )

        evaluation = gates.evaluate_promotion(store, belief_id)
        failed = [r.gate for r in evaluation.results if not r.passed]
        print(f"promotion gates failed: {failed or 'none'}")

        cal = calibration.record_experiment_outcome(
            store,
            "X-RSE-001",
            "routing_benefits" if benefits else "no_routing_benefit",
            outcome_boolean=benefits,
            notes="X-RSE-001 probe outcome vs pre-registered prediction",
        )
        print(f"calibration: {cal.id if cal else 'n/a (no point probability)'}")

        findings = [f for f in audit.run_audit(store) if f.severity == "violation"]
        print(f"audit violations: {len(findings)}")
        for f in findings:
            print(f"  {f.check}: {f.detail}")

        profile = selection.load_profile(
            REPO_ROOT / "configs" / "ceec" / "profile.yaml"
        )
        decision = selection.decide(store, profile, rationale="post X-RSE-001 round 3")
        print(f"next selection: {decision.selected_experiment}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ceec", action="store_true", help="ingest into CEEC ledger")
    args = parser.parse_args()
    result = run_probe()
    compact = {k: v for k, v in result.items() if k not in {"arms", "walltime_s"}}
    print(json.dumps(compact, indent=2))
    for arm, runs in result["arms"].items():  # type: ignore[union-attr, attr-defined]
        for seed, r in enumerate(runs):  # type: ignore[index]
            print(
                f"{arm:6s} seed {seed}: final_acc={r['final_accuracy']:.3f} "
                f"active_frac={r['active_fraction']:.3f} "
                f"eff_flops={r['effective_flops']:.0f} "
                f"collapsed={r['gates_collapsed']}"
            )
    if args.ceec:
        _ingest_ceec(result)
    print(f"walltime: {result['walltime_s']:.2f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
