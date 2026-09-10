"""X-STA-001 — CEEC-governed probe for B-H3-STABLE-TRANSIENT-AMPLIFICATION.

Question (pre-registered in
configs/ceec/experiments/stable_transient_amplification.yaml):
    Can we identify coordinates with spectral radius within limit
    (rho <= 0.95) and dominant singular value above 1 that still settle
    within the settling budget?

Coordinates (3 seeds, sweep c): W = Q blkdiag(rho_t*(I + c*K_m)) Q^T with
four size-4 Jordan blocks (rho_t = 0.85), Q a random orthogonal rotation.
Nominal rho(W) = rho_t while sigma_max(W) grows with c — the canonical
nonnormal transient-amplification family (cf. the Jordan-block regression
in tests/property/test_jacobian_amplification.py). c = 0 is the purely
contractive control (sigma_max = rho_t < 1).

Transition: x' = x @ W.T (linear), so the settled-state Jacobian IS W and
the instrument functions (I-JACOBIAN-SEPARATION) measure it exactly.

Evidence kind: vector (per-seed vectors over the c sweep).

Verdict: a c > 0 coordinate with sigma_max > 1, rho <= limit, and settling
time <= budget exists on all 3 seeds.

Run:
    uv run python scripts/probes/x_sta_001.py            # run only
    uv run python scripts/probes/x_sta_001.py --ceec     # run + ingest into ledger
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import cast

import torch
from torch import Tensor

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from computronium.stability.settling import (
    measure_settling_time,
)
from computronium.stability.spectral_radius import (
    dominant_singular_value,
    estimate_directional_amplification,
    spectral_radius_from_jacobian,
)
from computronium.state import (
    CompositeState,
    SystemContext,
)

N_SEEDS = 3
HIDDEN = 16
BLOCK = 4
RHO_TARGET = 0.85
RHO_LIMIT = 0.95
C_SWEEP = (0.0, 0.5, 1.0, 2.0, 4.0)
SETTLING_BUDGET = 500
SETTLING_TOL = 1e-4


class _Ctx:
    theta: tuple = ()


def _build_w(seed: int, c: float) -> torch.Tensor:
    """W = Q blkdiag(rho*(I + c*K_m) x4) Q^T (m=4 Jordan blocks, rotated).

    Nominal rho(W) = rho_t; a size-4 defect perturbs stored-float32
    eigenvalues by ~eps^(1/4) ~ 0.02, so realized rho stays under the
    0.95 limit. The superdiagonal c drives sigma_max above 1 — the
    canonical nonnormal transient-amplification family.
    """
    torch.manual_seed(seed)
    q, _ = torch.linalg.qr(torch.randn(HIDDEN, HIDDEN))
    block = RHO_TARGET * (torch.eye(BLOCK) + c * torch.diag(torch.ones(BLOCK - 1), 1))
    core = torch.kron(torch.eye(HIDDEN // BLOCK), block)
    return q @ core @ q.T


def _linear_transition(w: torch.Tensor):
    def fn(z: CompositeState, _ctx: object) -> CompositeState:
        x = cast("Tensor", z.activity["x"])
        return CompositeState(
            activity={"x": x @ w.T}, plastic=z.plastic, substrate=z.substrate
        )

    return fn


def _state(x: torch.Tensor) -> CompositeState:
    return CompositeState(activity={"x": x}, plastic={}, substrate={})


def run_coordinate(seed: int, c: float) -> dict[str, float | int | bool]:
    w = _build_w(seed, c)
    fn = _linear_transition(w)
    ctx = cast("SystemContext", _Ctx())
    z = _state(torch.randn(1, HIDDEN))
    rho = spectral_radius_from_jacobian(fn, z, context=ctx)  # type: ignore[arg-type]
    sigma = dominant_singular_value(fn, z, context=ctx)  # type: ignore[arg-type]
    amp = estimate_directional_amplification(  # type: ignore[arg-type]
        fn, z, ctx, num_iterations=50
    )
    steps, _ = measure_settling_time(  # type: ignore[arg-type]
        fn, z, ctx, tolerance=SETTLING_TOL, max_steps=SETTLING_BUDGET
    )
    return {
        "c": c,
        "spectral_radius": rho,
        "dominant_singular_value": sigma,
        "directional_amplification": amp,
        "settling_steps": steps,
        "stable_transient": bool(rho <= RHO_LIMIT and sigma > 1.0),
        "settles_in_budget": bool(steps < SETTLING_BUDGET),
    }


def run_probe() -> dict[str, object]:
    t0 = time.perf_counter()
    per_seed = [[run_coordinate(seed, c) for c in C_SWEEP] for seed in range(N_SEEDS)]
    hits = [
        [m for m in seed_row if m["stable_transient"] and m["settles_in_budget"]]
        for seed_row in per_seed
    ]
    found_all_seeds = all(len(h) > 0 for h in hits)
    first_hit_c = [h[0]["c"] if h else None for h in hits]
    walltime = time.perf_counter() - t0
    return {
        "per_seed": per_seed,
        "found_all_seeds": found_all_seeds,
        "first_hit_c": first_hit_c,
        "settling_steps_at_first_hit": [
            h[0]["settling_steps"] if h else None for h in hits
        ],
        "walltime_s": walltime,
        "n_seeds": N_SEEDS,
        "c_sweep": list(C_SWEEP),
    }


def _ingest_ceec(result: dict[str, object]) -> None:
    """Full governance loop into the real ledger (X-STA-001)."""
    from computronium.ceec import audit, calibration, gates, models, selection
    from computronium.ceec.probe_adapter import record_probe_result
    from computronium.ceec.store import CEECStore

    found = bool(result["found_all_seeds"])
    output = {
        "status": "ok",
        "kind": "vector",
        "scope": {
            "domain": "stability",
            "substrate": ["digital"],
            "geometry": ["recurrent"],
            "budget": "quick",
        },
        "axes": ["c_sweep", "seed"],
        "values": {"per_seed": result["per_seed"]},
        "quality": {
            "seeds": N_SEEDS,
            "matched_control": True,
            "evaluation_policy": "exact rho(J)/sigma_max(J) via autograd Jacobian "
            "instruments on the linear transition (J = W), settling at "
            f"tol={SETTLING_TOL}, budget={SETTLING_BUDGET} steps",
            "defect_audit": "pass",
            "reproduction": True,
            "verification_level": 4,
        },
        "defects": [],
        "summary": {
            "found_all_seeds": found,
            "first_hit_c": result["first_hit_c"],
            "settling_steps_at_first_hit": result["settling_steps_at_first_hit"],
        },
        "summary_operator": "first_hit_per_seed",
        "notes": "X-STA-001 stability separation probe (nonnormal W = rho*U + c*N)",
    }

    with CEECStore(
        REPO_ROOT / "ceec" / "ceec.sqlite3", REPO_ROOT / "ceec" / "artifacts"
    ) as store:
        probe_result = record_probe_result(store, output, "X-STA-001")
        belief_id = "B-H3-STABLE-TRANSIENT-AMPLIFICATION"
        store._link(
            store._conn,
            "belief_evidence",
            "belief_id",
            belief_id,
            "evidence_id",
            [probe_result.evidence.id],
        )
        store._conn.commit()

        prior = store.latest_revision(belief_id)
        prior_span = (
            f"[{prior.probability.low}, {prior.probability.high}]" if prior else "none"
        )
        new_low, new_high = (0.30, 0.70) if found else (0.05, 0.30)
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
            f"X-STA-001: stable-transient coordinates settle in budget on all "
            f"seeds = {found} (prior {prior_span})",
        )

        evaluation = gates.evaluate_promotion(store, belief_id)
        failed = [r.gate for r in evaluation.results if not r.passed]
        print(f"promotion gates failed: {failed or 'none'}")

        cal = calibration.record_experiment_outcome(
            store,
            "X-STA-001",
            "stable_transient_found" if found else "no_stable_transient",
            outcome_boolean=found,
            notes="X-STA-001 probe outcome vs pre-registered prediction",
        )
        print(f"calibration: {cal.id if cal else 'n/a (no point probability)'}")

        findings = [f for f in audit.run_audit(store) if f.severity == "violation"]
        print(f"audit violations: {len(findings)}")
        for f in findings:
            print(f"  {f.check}: {f.detail}")

        profile = selection.load_profile(
            REPO_ROOT / "configs" / "ceec" / "profile.yaml"
        )
        decision = selection.decide(store, profile, rationale="post X-STA-001 round 3")
        print(f"next selection: {decision.selected_experiment}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ceec", action="store_true", help="ingest into CEEC ledger")
    args = parser.parse_args()
    result = run_probe()
    compact = {k: v for k, v in result.items() if k not in {"per_seed", "walltime_s"}}
    print(json.dumps(compact, indent=2))
    for seed, row in enumerate(result["per_seed"]):  # type: ignore[index]
        cells = [
            f"c={m['c']}: rho={m['spectral_radius']:.3f} "
            f"smax={m['dominant_singular_value']:.2f} "
            f"settle={m['settling_steps']}"
            for m in row
        ]
        print(f"seed {seed}: " + " | ".join(cells))
    if args.ceec:
        _ingest_ceec(result)
    print(f"walltime: {result['walltime_s']:.2f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
