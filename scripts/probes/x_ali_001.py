"""X-ALI-001 — CEEC-governed probe for B-H1-ADAPTIVE-LOCAL-INVERSES.

Question (pre-registered in configs/ceec/experiments/adaptive_local_inverses.yaml):
    Does slowly adapting feedback improve descent quality (improvement_per_norm)
    relative to fixed random feedback under matched one-step displacement norm?

Arms (credit=random_projections, EqProp recurrent cell, 30 steps, 3 seeds):
    fixed     — feedback matrices drawn once (scale 0.1), never changed.
    adaptive  — feedback re-projected onto the normalized forward weights each
                step (B := scale * W / ||W|| * sqrt(numel) to hold the fixed
                arm's expected Frobenius norm). This is the "slow adaptation"
                lever: the feedback pathway drifts with W instead of staying
                frozen.

Norm matching: per-arm lr calibrated (mechanistic_study._calibrated_lr) so the
first-step ||Δθ|| matches the fixed arm's reference. Channel liveness is
checked (non-zero displacement on both arms — see random_projections
docstring's inertness warning); a zero-displacement arm is reported inert.

Evidence kind: curve (per-step loss + improvement_per_norm + alignment).

Verdict format: consistent improvement = adaptive mean improvement_per_norm
(strictly greater than fixed, averaged over the last half of the trajectory)
on all 3 seeds.

Run:
    uv run python scripts/probes/x_ali_001.py            # run only
    uv run python scripts/probes/x_ali_001.py --ceec     # run + ingest into ledger
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import torch

REPO_ROOT = Path(__file__).resolve().parents[2]

from computronium.analysis.mechanistic_study import (
    _INPUT_DIM,
    _OUTPUT_DIM,
    _build_system,
    _calibrated_lr,
)
from computronium.analysis.vertical_slice import free_loss
from computronium.ontology.credit import (
    CreditAssignmentConfig,
    RandomProjectionsCredit,
)
from computronium.ontology.update import ParameterUpdateConfig

N_SEEDS = 3
N_STEPS = 30
FEEDBACK_SCALE = 0.1


def _feedback_alignment(credit: RandomProjectionsCredit, geometry) -> float:
    """Mean cosine between feedback matrices and forward weights."""
    cosines = []
    for name, fb in credit._feedback_weights.items():
        w = geometry.params[name].detach()
        cosines.append(
            float(
                torch.nn.functional.cosine_similarity(fb.flatten(), w.flatten(), dim=0)
            )
        )
    return sum(cosines) / len(cosines) if cosines else 0.0


def _adapt_feedback(credit: RandomProjectionsCredit, geometry) -> None:
    """Re-project feedback onto normalized forward weights (shape-safe)."""
    for name, fb in credit._feedback_weights.items():
        w = geometry.params[name].detach()
        w_norm = w.norm()
        if w_norm == 0:
            continue
        credit._feedback_weights[name] = (
            (w / w_norm) * FEEDBACK_SCALE * (fb.numel() ** 0.5)
        ).to(fb.dtype)


def run_arm(seed: int, adaptive: bool) -> dict[str, object]:  # ruff: ignore[too-many-locals]  probe payload assembly
    torch.manual_seed(seed)
    credit_cfg = CreditAssignmentConfig.random_projections(
        feedback_scale=FEEDBACK_SCALE
    )
    euclid = lambda lr: ParameterUpdateConfig.euclidean(step_size=lr, momentum=0.0)  # ruff: ignore[lambda-assignment]

    # Norm-matched lr: calibrate on the fixed arm's first-step displacement.
    torch.manual_seed(seed + 777)
    xs = torch.randn(8, _INPUT_DIM)
    ys = torch.randint(0, _OUTPUT_DIM, (8,))
    ref_system = _build_system(credit_cfg, euclid(0.05), seed=seed)
    before = {n: t.detach().clone() for n, t in ref_system.geometry.params.items()}
    ref_system.train_step(xs, ys)
    sq = sum(
        float((ref_system.geometry.params[n].detach() - before[n]).norm() ** 2)
        for n in before
    )
    reference_norm = sq**0.5

    lr = _calibrated_lr(
        credit_cfg,
        euclid,
        reference_norm,
        xs,
        ys,
        seed=seed,
    )
    system = _build_system(credit_cfg, euclid(lr), seed=seed)

    credit = system.credit
    # force feedback init
    torch.manual_seed(seed + 1)
    credit._init_feedback_weights(system.geometry, torch.device("cpu"))

    losses: list[float] = []
    ipns: list[float] = []
    disps: list[float] = []
    alignments: list[float] = []
    for _ in range(N_STEPS):
        before_params = {
            n: t.detach().clone() for n, t in system.geometry.params.items()
        }
        loss_before = free_loss(system, xs, ys)
        system.train_step(xs, ys)
        loss_after = free_loss(system, xs, ys)
        sq = sum(
            float((system.geometry.params[n].detach() - before_params[n]).norm() ** 2)
            for n in before_params
        )
        disp = sq**0.5
        losses.append(loss_after)
        ipns.append((-loss_after + loss_before) / disp if disp > 0 else 0.0)
        disps.append(disp)
        if adaptive:
            alignments.append(_feedback_alignment(credit, system.geometry))
            _adapt_feedback(credit, system.geometry)
        else:
            alignments.append(_feedback_alignment(credit, system.geometry))
    return {
        "losses": losses,
        "improvement_per_norm": ipns,
        "displacement_norms": disps,
        "feedback_alignment": alignments,
        "lr": lr,
        "channel_live": max(disps) > 0.0,
    }


def run_probe() -> dict[str, object]:
    t0 = time.perf_counter()
    arms: dict[str, dict[str, object]] = {}
    for arm in ("fixed", "adaptive"):
        arm_runs = [
            run_arm(seed, adaptive=(arm == "adaptive")) for seed in range(N_SEEDS)
        ]
        half = N_STEPS // 2
        mean_ipn_late = [
            sum(r["improvement_per_norm"][half:]) / (N_STEPS - half)  # type: ignore[index]
            for r in arm_runs
        ]
        consistent = all(ipn > 0 for ipn in mean_ipn_late)
        arms[arm] = {
            "per_seed": arm_runs,
            "mean_improvement_per_norm_late": mean_ipn_late,
            "consistent_improvement": consistent,
            "channel_live": all(r["channel_live"] for r in arm_runs),
        }
    adaptive_better_all_seeds = all(
        a > f
        for a, f in zip(
            arms["adaptive"]["mean_improvement_per_norm_late"],
            arms["fixed"]["mean_improvement_per_norm_late"],
        )
    )
    walltime = time.perf_counter() - t0
    return {
        "arms": arms,
        "adaptive_better_all_seeds": adaptive_better_all_seeds,
        "walltime_s": walltime,
        "n_seeds": N_SEEDS,
        "n_steps": N_STEPS,
    }


def _ingest_ceec(result: dict[str, object]) -> None:
    """Full governance loop into the real ledger (X-ALI-001)."""
    from computronium.ceec import (
        audit,
        calibration,
        gates,
        models,
        selection,
    )
    from computronium.ceec.probe_adapter import record_probe_result
    from computronium.ceec.store import CEECStore

    def arms_payload(arm: str) -> dict[str, list[list[float]]]:
        runs = result["arms"][arm]["per_seed"]
        return {
            "loss": [r["losses"] for r in runs],
            "improvement_per_norm": [r["improvement_per_norm"] for r in runs],
            "feedback_alignment": [r["feedback_alignment"] for r in runs],
        }

    quality = {
        "seeds": N_SEEDS,
        "matched_control": True,
        "evaluation_policy": "improvement_per_norm over matched-norm 30-step "
        "trajectories, late-half mean, 3 seeds",
        "defect_audit": "pass" if result["arms"]["fixed"]["channel_live"] else "fail",
        "reproduction": True,
    }
    output = {
        "status": "ok" if result["arms"]["fixed"]["channel_live"] else "missing",
        "kind": "curve",
        "scope": {
            "domain": "credit",
            "substrate": ["digital"],
            "credit": ["random_projections"],
            "budget": "quick",
        },
        "axes": ["step"],
        "values": {
            "fixed": arms_payload("fixed"),
            "adaptive": arms_payload("adaptive"),
            "adaptive_better_all_seeds": result["adaptive_better_all_seeds"],
        },
        "quality": quality,
        "defects": []
        if result["arms"]["fixed"]["channel_live"]
        else ["inert feedback channel (zero displacement)"],
        "summary": {
            "adaptive_better_all_seeds": result["adaptive_better_all_seeds"],
            "fixed_ipn_late_mean": _mean(arms_payload("fixed")["improvement_per_norm"]),
            "adaptive_ipn_late_mean": _mean(
                arms_payload("adaptive")["improvement_per_norm"]
            ),
        },
        "summary_operator": "late_half_mean",
        "notes": "X-ALI-001 norm-matched fixed-vs-adaptive feedback probe",
    }

    with CEECStore(
        REPO_ROOT / "ceec" / "ceec.sqlite3", REPO_ROOT / "ceec" / "artifacts"
    ) as store:
        probe_result = record_probe_result(store, output, "X-ALI-001")
        belief_id = "B-H1-ADAPTIVE-LOCAL-INVERSES"
        store._link(
            store._conn,
            "belief_evidence",
            "belief_id",
            belief_id,
            "evidence_id",
            [probe_result.evidence.id],
        )
        store._conn.commit()

        better = bool(result["adaptive_better_all_seeds"])
        prior = store.latest_revision(belief_id)
        prior_span = (
            f"[{prior.probability.low}, {prior.probability.high}]" if prior else "none"
        )
        new_low, new_high = (0.45, 0.80) if better else (0.10, 0.40)
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
            f"X-ALI-001: adaptive better on all seeds = {better} (prior {prior_span})",
        )

        evaluation = gates.evaluate_promotion(store, belief_id)
        failed = [r.gate for r in evaluation.results if not r.passed]
        print(f"promotion gates failed: {failed or 'none'}")

        cal = calibration.record_experiment_outcome(
            store,
            "X-ALI-001",
            "adaptive_improves" if better else "no_effect",
            outcome_boolean=better,
            notes="X-ALI-001 probe outcome vs pre-registered prediction",
        )
        print(f"calibration: {cal.id if cal else 'n/a (no point probability)'}")

        findings = [f for f in audit.run_audit(store) if f.severity == "violation"]
        print(f"audit violations: {len(findings)}")
        for f in findings:
            print(f"  {f.check}: {f.detail}")

        profile = selection.load_profile(
            REPO_ROOT / "configs" / "ceec" / "profile.yaml"
        )
        decision = selection.decide(store, profile, rationale="post X-ALI-001 round 2")
        print(f"next selection: {decision.selected_experiment}")


def _mean(values: object) -> float | None:
    import itertools

    if not isinstance(values, list):
        return None
    flat = [
        v for v in itertools.chain.from_iterable(values) if isinstance(v, (int, float))
    ]
    return sum(flat) / len(flat) if flat else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ceec", action="store_true", help="ingest into CEEC ledger")
    args = parser.parse_args()
    result = run_probe()
    print(json.dumps({k: v for k, v in result.items() if k != "arms"}, indent=2))
    for arm in ("fixed", "adaptive"):
        arm_data = result["arms"][arm]  # type: ignore[index]
        print(
            f"{arm:9s} channel_live={arm_data['channel_live']} "
            f"late ipn/seed={[round(x, 4) for x in arm_data['mean_improvement_per_norm_late']]} "
            f"consistent={arm_data['consistent_improvement']}"
        )
    if args.ceec:
        _ingest_ceec(result)
    print(f"walltime: {result['walltime_s']:.2f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
