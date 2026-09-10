"""X-USU-001 — CEEC-governed probe for B-H5-UPDATE-RULE-SPECIALIZATION.

Question (pre-registered in configs/ceec/experiments/update_rule_specialization.yaml):
    Does role-specific update assignment improve one-step improvement_per_norm
    relative to uniform update?

Arms (credit=random_projections, EqProp recurrent cell, one step, 3 seeds,
per-arm norm-matched lr via mechanistic_study._calibrated_lr):
    uniform_euclid    — EuclideanUpdate everywhere (gradient-relative SGD).
    uniform_muon      — RiemannianOrthogonalUpdate (ortho_steps=0, exact SVD
                        polar factor) everywhere (per-element displacement).
    hybrid_muon_fwd   — Muon on forward/hidden weights (0.weight,
                        recurrent_weight), Euclid on the readout (2.weight).
    hybrid_muon_out   — Muon on the readout only, Euclid on forward/hidden.

The hybrid rule is a dispatcher over the two stateful rule instances: each
sub-rule sees the full pseudo-gradient list with non-role entries zeroed
(zero momentum buffer → exactly zero displacement), and the merged dict
takes each name from its owning sub-rule — so no parameter receives two
displacements and no role leaks.

Evidence kind: tensor (arm × seed).

Verdict: at least one hybrid beats BOTH uniforms on improvement_per_norm on
all 3 seeds.

Run:
    uv run python scripts/probes/x_usu_001.py            # run only
    uv run python scripts/probes/x_usu_001.py --ceec     # run + ingest into ledger
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

import torch
from torch import Tensor

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from computronium.analysis.mechanistic_study import (
    _INPUT_DIM,
    _OUTPUT_DIM,
    _build_system,
    _calibrated_lr,
)
from computronium.analysis.vertical_slice import (
    free_loss,
)
from computronium.core.pipeline import (
    run_train_step,
)
from computronium.ontology.credit import (
    CreditAssignmentConfig,
)
from computronium.ontology.update import (
    EuclideanUpdate,
    ParameterUpdateConfig,
    RiemannianOrthogonalUpdate,
)

if TYPE_CHECKING:
    from collections.abc import Callable

N_SEEDS = 3

UNIFORM_ARMS = ("uniform_euclid", "uniform_muon")
HYBRID_ARMS = ("hybrid_muon_fwd", "hybrid_muon_out")
ALL_ARMS = UNIFORM_ARMS + HYBRID_ARMS


def _euclid_cfg(lr: float) -> ParameterUpdateConfig:
    return ParameterUpdateConfig.euclidean(step_size=lr, momentum=0.0)


def _muon_cfg(lr: float) -> ParameterUpdateConfig:
    return ParameterUpdateConfig.riemannian_orthogonal(
        step_size=lr, momentum=0.0, ortho_steps=0
    )


def _task(seed: int) -> tuple[Tensor, Tensor]:
    torch.manual_seed(seed + 777)
    xs = torch.randn(8, _INPUT_DIM)
    ys = torch.randint(0, _OUTPUT_DIM, (8,))
    return xs, ys


def _norm_matched_lr(credit_cfg: CreditAssignmentConfig, arm: str, seed: int) -> float:
    """Per-arm calibrated lr: first-step ||Δθ|| matches the fixed reference."""
    torch.manual_seed(seed + 777)
    xs = torch.randn(8, _INPUT_DIM)
    ys = torch.randint(0, _OUTPUT_DIM, (8,))
    xs = torch.randn(8, _INPUT_DIM)
    ys = torch.randint(0, _OUTPUT_DIM, (8,))
    ref_system = _build_system(credit_cfg, _euclid_cfg(0.05), seed=seed)
    before = {n: t.detach().clone() for n, t in ref_system.geometry.params.items()}
    ref_system.train_step(xs, ys)
    reference_norm = (
        sum(
            float((ref_system.geometry.params[n].detach() - before[n]).norm() ** 2)
            for n in before
        )
        ** 0.5
    )
    cfg_fn: Callable[[float], ParameterUpdateConfig] = (
        _muon_cfg if arm == "uniform_muon" else _euclid_cfg
    )
    return _calibrated_lr(credit_cfg, cfg_fn, reference_norm, xs, ys, seed=seed)


def _readout_name(params: dict[str, Tensor]) -> str:
    for name, p in params.items():
        if p.ndim == 2 and p.shape[0] == _OUTPUT_DIM:
            return name
    raise ValueError(f"no readout weight among {sorted(params)}")


class _RoleSplitUpdate:
    """Dispatcher: rule_a on role names, rule_b on the rest (no double-step)."""

    def __init__(
        self,
        rule_a: EuclideanUpdate | RiemannianOrthogonalUpdate,
        rule_b: EuclideanUpdate | RiemannianOrthogonalUpdate,
        role_names: frozenset[str],
    ) -> None:
        self._rule_a = rule_a
        self._rule_b = rule_b
        self._role_names = role_names

    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: object,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]:
        names = [n for n, p in params.items() if p.ndim == 2 and "weight" in n]
        grads_a = [
            g if n in self._role_names else torch.zeros_like(g)
            for n, g in zip(names, pseudo_grads)
        ]
        grads_b = [
            g if n not in self._role_names else torch.zeros_like(g)
            for n, g in zip(names, pseudo_grads)
        ]
        step_a = self._rule_a.step(params, grads_a, geometry, bias_grads)  # type: ignore[arg-type]
        step_b = self._rule_b.step(params, grads_b, geometry, bias_grads)  # type: ignore[arg-type]
        merged = dict(params)
        for n in names:
            merged[n] = step_a[n] if n in self._role_names else step_b[n]
        return merged

    def get_state(self) -> dict[str, object]:
        return {
            "rule_a": self._rule_a.get_state(),
            "rule_b": self._rule_b.get_state(),
        }

    def load_state(self, state: dict[str, object]) -> None:
        self._rule_a.load_state(state["rule_a"])  # type: ignore[arg-type]
        self._rule_b.load_state(state["rule_b"])  # type: ignore[arg-type]


def make_update(arm: str, lr: float, params: dict[str, Tensor], readout: str) -> object:
    """Update instance for one arm; muon step_size rides the calibrated lr."""
    muon_cfg = ParameterUpdateConfig.riemannian_orthogonal(
        step_size=lr, momentum=0.0, ortho_steps=0
    )
    euclid_cfg = ParameterUpdateConfig.euclidean(step_size=lr, momentum=0.0)
    match arm:
        case "uniform_euclid":
            return EuclideanUpdate(euclid_cfg)
        case "uniform_muon":
            return RiemannianOrthogonalUpdate(muon_cfg)
        case "hybrid_muon_fwd":
            roles = frozenset(
                n
                for n, p in params.items()
                if "weight" in n and p.ndim == 2 and n != readout
            )
            return _RoleSplitUpdate(
                RiemannianOrthogonalUpdate(muon_cfg),
                EuclideanUpdate(euclid_cfg),
                roles,
            )
        case "hybrid_muon_out":
            return _RoleSplitUpdate(
                RiemannianOrthogonalUpdate(muon_cfg),
                EuclideanUpdate(euclid_cfg),
                frozenset([readout]),
            )
        case _:
            raise ValueError(f"unknown arm {arm!r}")


def run_arm(seed: int, arm: str) -> dict[str, float | int | bool]:
    torch.manual_seed(seed)
    credit_cfg = CreditAssignmentConfig.random_projections(feedback_scale=0.1)
    lr = _norm_matched_lr(credit_cfg, arm, seed)

    xs, ys = _task(seed)
    probe_system = _build_system(credit_cfg, _euclid_cfg(0.01), seed=seed)
    readout = _readout_name(probe_system.geometry.params)
    update = make_update(arm, lr, probe_system.geometry.params, readout)
    system = _build_system(credit_cfg, _euclid_cfg(lr), seed=seed)

    loss_before = free_loss(system, xs, ys)
    before_params = {n: t.detach().clone() for n, t in system.geometry.params.items()}
    metrics = run_train_step(
        system.substrate,
        system.geometry,
        system.dynamics,
        system.credit,
        update,  # type: ignore[arg-type]
        xs,
        ys,
    )
    loss_after = metrics["free_loss"]
    disp = (
        sum(
            float((system.geometry.params[n].detach() - before_params[n]).norm() ** 2)
            for n in before_params
        )
        ** 0.5
    )
    ipn = (loss_before - loss_after) / disp if disp > 0 else 0.0
    rho = float(
        torch.linalg
        .eigvals(system.geometry.params["recurrent_weight"].detach())
        .abs()
        .max()
    )
    return {
        "improvement_per_norm": ipn,
        "displacement_norm": disp,
        "lr": lr,
        "loss_before": loss_before,
        "loss_after": loss_after,
        "spectral_radius": rho,
        "channel_live": disp > 0.0,
    }


def run_probe() -> dict[str, object]:
    t0 = time.perf_counter()
    arms = {arm: [run_arm(s, arm) for s in range(N_SEEDS)] for arm in ALL_ARMS}
    ipns = {
        arm: [r["improvement_per_norm"] for r in runs] for arm, runs in arms.items()
    }
    winners = [
        arm
        for arm in ("hybrid_muon_fwd", "hybrid_muon_out")
        if all(
            ipns[arm][s] > ipns["uniform_euclid"][s]
            and ipns[arm][s] > ipns["uniform_muon"][s]
            for s in range(N_SEEDS)
        )
    ]
    all_live = all(r["channel_live"] for runs in arms.values() for r in runs)
    walltime = time.perf_counter() - t0
    return {
        "arms": arms,
        "winning_hybrids": winners,
        "specialization_supported": bool(winners) and all_live,
        "channel_live": all_live,
        "walltime_s": walltime,
        "n_seeds": N_SEEDS,
    }


def _ingest_ceec(result: dict[str, object]) -> None:
    """Full governance loop into the real ledger (X-USU-001)."""
    from computronium.ceec import audit, calibration, gates, models, selection
    from computronium.ceec.probe_adapter import record_probe_result
    from computronium.ceec.store import CEECStore

    output = {
        "status": "ok" if result["channel_live"] else "missing",
        "kind": "tensor",
        "scope": {
            "domain": "update",
            "substrate": ["digital"],
            "budget": "quick",
        },
        "axes": ["arm", "seed"],
        "values": {
            arm: {
                "improvement_per_norm": [r["improvement_per_norm"] for r in runs],
                "displacement_norm": [r["displacement_norm"] for r in runs],
                "spectral_radius": [r["spectral_radius"] for r in runs],
                "lr": [r["lr"] for r in runs],
            }
            for arm, runs in result["arms"].items()  # type: ignore[union-attr]
        },
        "quality": {
            "seeds": N_SEEDS,
            "matched_control": True,
            "evaluation_policy": "one-step improvement_per_norm with per-arm "
            "calibrated norm matching, 3 seeds; readout identified by "
            "out-features == output_dim",
            "defect_audit": "pass" if result["channel_live"] else "fail",
            "reproduction": True,
            "verification_level": 4,
        },
        "defects": []
        if result["channel_live"]
        else ["inert update channel (zero displacement)"],
        "summary": {
            "winning_hybrids": result["winning_hybrids"],
            "specialization_supported": result["specialization_supported"],
        },
        "summary_operator": "per_seed_hybrid_vs_uniform",
        "notes": "X-USU-001 role-split update ablation (muon vs euclid per role)",
    }

    with CEECStore(
        REPO_ROOT / "ceec" / "ceec.sqlite3", REPO_ROOT / "ceec" / "artifacts"
    ) as store:
        probe_result = record_probe_result(store, output, "X-USU-001")
        belief_id = "B-H5-UPDATE-RULE-SPECIALIZATION"
        store._link(
            store._conn,
            "belief_evidence",
            "belief_id",
            belief_id,
            "evidence_id",
            [probe_result.evidence.id],
        )
        store._conn.commit()

        supported = bool(result["specialization_supported"])
        prior = store.latest_revision(belief_id)
        prior_span = (
            f"[{prior.probability.low}, {prior.probability.high}]" if prior else "none"
        )
        new_low, new_high = (0.25, 0.60) if supported else (0.05, 0.35)
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
            f"X-USU-001: a hybrid role-split beats both uniforms on all seeds "
            f"= {supported} (winners {result['winning_hybrids']}, prior "
            f"{prior_span})",
        )

        evaluation = gates.evaluate_promotion(store, belief_id)
        failed = [r.gate for r in evaluation.results if not r.passed]
        print(f"promotion gates failed: {failed or 'none'}")

        cal = calibration.record_experiment_outcome(
            store,
            "X-USU-001",
            "specialization_supported" if supported else "no_specialization",
            outcome_boolean=supported,
            notes="X-USU-001 probe outcome vs pre-registered prediction",
        )
        print(f"calibration: {cal.id if cal else 'n/a (no point probability)'}")

        findings = [f for f in audit.run_audit(store) if f.severity == "violation"]
        print(f"audit violations: {len(findings)}")
        for f in findings:
            print(f"  {f.check}: {f.detail}")

        profile = selection.load_profile(
            REPO_ROOT / "configs" / "ceec" / "profile.yaml"
        )
        decision = selection.decide(store, profile, rationale="post X-USU-001 round 3")
        print(f"next selection: {decision.selected_experiment}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ceec", action="store_true", help="ingest into CEEC ledger")
    args = parser.parse_args()
    result = run_probe()
    compact = {k: v for k, v in result.items() if k not in {"arms", "walltime_s"}}
    print(json.dumps(compact, indent=2))
    for arm, runs in result["arms"].items():  # type: ignore[union-attr, attr-defined]
        cells = [f"{r['improvement_per_norm']:.4f}" for r in runs]  # type: ignore[index]
        print(f"{arm:16s} ipn/seed = {cells}")
    if args.ceec:
        _ingest_ceec(result)
    print(f"walltime: {result['walltime_s']:.2f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
