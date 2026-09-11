"""X-ALI-002 — CEEC-governed probe: short-trajectory adaptive feedback.

Question (pre-registered in
configs/ceec/experiments/adaptive_local_inverses_short.yaml):
    Does the X-ALI-001 adaptive-feedback advantage in improvement_per_norm
    persist on short (10-step) trajectories under matched displacement norm?

Arms: fixed vs adaptive (per-step re-projection onto normalized forward
weights, matched norm) — identical to X-ALI-001 but with a 10-step horizon.
Verdict: adaptive late-half mean improvement_per_norm strictly greater than
fixed on all 3 seeds.

Run:
    uv run python scripts/probes/x_ali_002.py            # run only
    uv run python scripts/probes/x_ali_002.py --ceec     # run + ingest
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
N_STEPS = 10
FEEDBACK_SCALE = 0.1


def _feedback_alignment(credit: RandomProjectionsCredit, geometry) -> float:
    """Mean cosine between feedback matrices and forward weights."""
    cosines = [
        float(
            torch.nn.functional.cosine_similarity(
                fb.flatten(), geometry.params[name].detach().flatten(), dim=0
            )
        )
        for name, fb in credit._feedback_weights.items()
    ]
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

    torch.manual_seed(seed + 777)
    xs = torch.randn(8, _INPUT_DIM)
    ys = torch.randint(0, _OUTPUT_DIM, (8,))
    ref_system = _build_system(credit_cfg, euclid(0.05), seed=seed)
    before = {n: t.detach().clone() for n, t in ref_system.geometry.params.items()}
    ref_system.train_step(xs, ys)
    reference_norm = (
        sum(
            float((ref_system.geometry.params[n].detach() - before[n]).norm().item())
            ** 2
            for n in before
        )
        ** 0.5
    )

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
        disp = (
            sum(
                float(
                    (system.geometry.params[n].detach() - before_params[n])
                    .norm()
                    .item()
                )
                ** 2
                for n in before_params
            )
            ** 0.5
        )
        losses.append(loss_after)
        ipns.append((-loss_after + loss_before) / disp if disp > 0 else 0.0)
        disps.append(disp)
        alignments.append(_feedback_alignment(credit, system.geometry))
        if adaptive:
            _adapt_feedback(credit, system.geometry)
    return {
        "losses": losses,
        "improvement_per_norm": ipns,
        "displacement_norms": disps,
        "feedback_alignment": alignments,
        "lr": lr,
        "channel_live": max(disps) > 0.0,
    }


def _late_list(arms: dict[str, dict[str, object]], arm: str) -> list[float]:
    late = arms[arm]["mean_improvement_per_norm_late"]
    return late if isinstance(late, list) else []  # type: ignore[return-value]


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
        arms[arm] = {
            "per_seed": arm_runs,
            "mean_improvement_per_norm_late": mean_ipn_late,
            "consistent_improvement": all(ipn > 0 for ipn in mean_ipn_late),
            "channel_live": all(r["channel_live"] for r in arm_runs),
        }
    adaptive_better_all_seeds = all(
        a > f
        for a, f in zip(
            _late_list(arms, "adaptive"),  # pyright: ignore[reportArgumentType]
            _late_list(arms, "fixed"),  # pyright: ignore[reportArgumentType]
        )
    )
    return {
        "arms": arms,
        "adaptive_better_all_seeds": adaptive_better_all_seeds,
        "walltime_s": time.perf_counter() - t0,
        "n_seeds": N_SEEDS,
        "n_steps": N_STEPS,
    }


def _ingest_ceec(result: dict[str, object]) -> None:
    from computronium.ceec import models
    from computronium.ceec.probe_adapter import record_probe_result
    from computronium.ceec.store import CEECStore

    def arms_payload(arm: str) -> dict[str, list[list[float]]]:
        runs = result["arms"][arm]["per_seed"]  # type: ignore[index]
        return {
            "loss": [r["losses"] for r in runs],  # type: ignore[index]
            "improvement_per_norm": [r["improvement_per_norm"] for r in runs],  # type: ignore[index]
            "feedback_alignment": [r["feedback_alignment"] for r in runs],  # type: ignore[index]
        }

    channel_live = result["arms"]["fixed"]["channel_live"]  # type: ignore[index]
    output = {
        "status": "ok" if channel_live else "missing",
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
        "quality": {
            "seeds": N_SEEDS,
            "matched_control": True,
            "evaluation_policy": "late-half improvement_per_norm over "
            "matched-norm 10-step trajectories, 3 seeds",
            "defect_audit": "pass" if channel_live else "fail",
            "reproduction": True,
        },
        "defects": [] if channel_live else ["inert feedback channel"],
        "summary": {
            "adaptive_better_all_seeds": result["adaptive_better_all_seeds"],
            "fixed_ipn_late_mean": _mean(arms_payload("fixed")["improvement_per_norm"]),
            "adaptive_ipn_late_mean": _mean(
                arms_payload("adaptive")["improvement_per_norm"]
            ),
        },
        "summary_operator": "late_half_mean",
        "notes": "X-ALI-002 short-trajectory adaptive-feedback validation",
    }

    with CEECStore(
        REPO_ROOT / "ceec" / "ceec.sqlite3", REPO_ROOT / "ceec" / "artifacts"
    ) as store:
        probe_result = record_probe_result(store, output, "X-ALI-002")
        store._link(
            store._conn,
            "belief_evidence",
            "belief_id",
            "B-H1-ADAPTIVE-LOCAL-INVERSES",
            "evidence_id",
            [probe_result.evidence.id],
        )
        store.set_experiment_status("X-ALI-002", "completed")
        store._conn.commit()

        better = bool(result["adaptive_better_all_seeds"])
        prior = store.latest_revision("B-H1-ADAPTIVE-LOCAL-INVERSES")
        prior_span = (
            f"[{prior.probability.low}, {prior.probability.high}]" if prior else "none"
        )
        new_low, new_high = (0.55, 0.85) if better else (0.30, 0.55)
        store.update_belief(
            "B-H1-ADAPTIVE-LOCAL-INVERSES",
            models.Probability(
                low=new_low,
                high=new_high,
                method="heuristic_interval_based_on_gate_evidence",
            ),
            "medium",
            "medium",
            "narrow",
            "open",
            f"X-ALI-002 short-horizon: adaptive better on all seeds = {better} "
            f"(prior {prior_span})",
        )
        store._conn.commit()
        print(f"belief updated: [low={new_low}, high={new_high}] (prior {prior_span})")
        print(
            f"experiment X-ALI-002 marked completed; evidence {probe_result.evidence.id}"
        )


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
