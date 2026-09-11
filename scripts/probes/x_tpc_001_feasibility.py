"""Record X-TPC-001 feasibility on B-H2-TEMPORAL-PSI-CREDIT.

D22 (scripts/probes/d22_psi_only.py) falsified instantaneous ψ-only
adaptation: the ψ-step contract feeds first-phase (target-free) settled
activity; no landed plasticity law consumes a loss/target term. The temporal
ψ credit that X-TPC-001 pre-registers does not exist as an implemented
mechanism — building it is a new Plasticity primitive requiring an
AlgorithmIdentityCard (G-HARD-9) and FrozenThetaAudit (G-HARD-8).

This script records the governed state: lever analysis as a derived object,
a belief revision narrowing B-H2, and leaves X-TPC-001 pre-registered
(awaiting mechanism build). No boundary is declared — the temporal lever is
the untested mechanism B-H2 names; boundary would be premature.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

from computronium.ceec import CEECStore, audit, models

BELIEF = "B-H2-TEMPORAL-PSI-CREDIT"


def main() -> int:
    with CEECStore(
        REPO_ROOT / "ceec" / "ceec.sqlite3", REPO_ROOT / "ceec" / "artifacts"
    ) as store:
        prior = store.latest_revision(BELIEF)
        prior_span = (
            f"[{prior.probability.low}, {prior.probability.high}]" if prior else "none"
        )
        d22_note = store.record_instrument_note(
            BELIEF,
            "D22 (2026-09-06) falsified instantaneous psi-only adaptation: "
            "psi-step contract consumes first-phase target-free settled "
            "activity; no landed plasticity law takes a loss/target term. "
            "Instantaneous-psi lever exhausted; temporal trace is the named "
            "untested lever (TODO12 Open Questions resolved NO for "
            "instantaneous).",
            kind="observation",
        )
        derived = store.record_derived(
            type_="lever_analysis",
            operator="consolidate",
            inputs={"instrument_notes": [d22_note.id]},
            scope=models.Scope(domain="plasticity", extra={"belief": BELIEF}),
            value={
                "exhausted_levers": ["instantaneous_psi_update"],
                "untested_levers": [
                    "temporal_psi_credit",
                    "supervised_psi_term",
                    "metaplasticity",
                ],
                "mechanism_build_required": True,
                "hard_gates_on_build": [
                    "identity_card_for_new_primitive",
                    "frozen_theta_audit",
                ],
            },
            checks=["root-cause citation: D22 verdict block"],
        )
        store._link(
            store._conn,
            "belief_derived",
            "belief_id",
            BELIEF,
            "derived_id",
            [derived.id],
        )
        store._conn.commit()
        store.update_belief(
            BELIEF,
            models.Probability(
                low=0.10,
                high=0.45,
                method="heuristic_interval_based_on_gate_evidence",
            ),
            "high",
            "low",
            "narrow",
            "open",
            f"D22 lever analysis: instantaneous psi falsified; temporal "
            f"credit untested pending mechanism build "
            f"(prior {prior_span}). X-TPC-001 remains pre-registered.",
        )
        print(f"B-H2 narrowed; derived {derived.id}; note {d22_note.id}")
        violations = [f for f in audit.run_audit(store) if f.severity == "violation"]
        print(f"audit violations: {len(violations)}")
        for f in violations:
            print(f"  {f.check}: {f.detail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
