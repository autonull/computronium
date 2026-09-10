# Epistemic Foundry Report

**Round:** 2 (2026-09-10) — X-ALI-001 executed under CEEC governance; X-TPC-001 lever analysis recorded.

## Active beliefs

| ID | Statement (abridged) | Status | Interval |
|---|---|---|---|
| B-H1-ADAPTIVE-LOCAL-INVERSES | Slow feedback adaptation improves local credit descent | open | [0.45, 0.80] (was [0.20, 0.60]) |
| B-H2-TEMPORAL-PSI-CREDIT | Temporal ψ credit extends frozen-θ task horizon | open | [0.10, 0.45] (was [0.15, 0.55]) |
| B-H3-STABLE-TRANSIENT-AMPLIFICATION | Stable transient amplification improves robustness | open | [0.20, 0.55] |
| B-H4-ROUTING-SPARSITY-EFFICIENCY | Routing yields measurable resource benefits | open | [0.25, 0.60] |
| B-H5-UPDATE-RULE-SPECIALIZATION | Role-specific update rules improve learning/stability | open | [0.20, 0.55] |

## Round 2 outcomes

### X-ALI-001 — executed (2.2 s CPU, 3 seeds × 30 steps × 2 arms)

- **Result:** adaptive feedback (B ∝ W/‖W‖ re-projection) beats fixed random
  feedback on late-half mean improvement_per_norm on **all 3 seeds** at
  matched ‖Δθ‖ (adaptive {0.863, 0.853, 0.694} vs fixed {0.490, 0.459, 0.517}).
- **Evidence:** curve, axes `[step]`, quality `{seeds: 3, matched_control:
  true, defect_audit: pass, reproduction: true}`; both channels live
  (non-zero displacement).
- **Belief update:** B-H1 narrowed upward [0.20, 0.60] → [0.45, 0.80].
- **Gate evaluation:** promotion evaluated; only `probability_threshold`
  fails ([0.45, 0.80] < 0.95) — correct: one probe cannot promote.
- **Calibration:** CAL-000001 (predicted [0.30, 0.60], outcome success,
  Brier 0.25 at midpoint 0.5).
- **Audit:** clean.

### X-TPC-001 — lever analysis recorded, execution deferred

D22 (2026-09-06) falsified **instantaneous** ψ-only adaptation (root cause:
the ψ-step contract consumes target-free first-phase activity; no plasticity
law takes a loss term). The temporal ψ credit X-TPC-001 names is not yet an
implemented mechanism; building it is a new Plasticity primitive requiring
G-HARD-9 (identity card) and G-HARD-8 (FrozenThetaAudit). B-H2 narrowed
[0.15, 0.55] → [0.10, 0.45]; `lever_analysis` derived object records
exhausted (instantaneous) vs untested (temporal, supervised-ψ-term,
metaplasticity) levers. **No boundary declared** — the temporal lever is the
untested mechanism the belief names; X-TPC-001 remains pre-registered.

## Promoted claims

None yet. Promotion requires `probability_low >= 0.95` plus the full gate
set (multi-seed, matched control, defect audit, reproduction, …).

## Boundaries

None. Boundary requires rescue `<= 0.05` plus defect hunt and lever
exhaustion.

## Quarantines

None. Audit reports clean.

## Reopened beliefs

None.

## Experiment outcomes

| Experiment | Status |
|---|---|
| X-ALI-001 | completed, positive, calibrated |
| X-TPC-001 | pre-registered, awaiting temporal-ψ mechanism build |
| X-STA-001 | pre-registered (oracle's next pick after round-2 decide) |
| X-RSE-001 | pre-registered |
| X-USU-001 | pre-registered |

## Calibration summary

1 record. Predicted [0.30, 0.60] (midpoint 0.5), observed success → Brier
0.25. Review flags: none.

## Migrated evidence

TODO18 claim records (vertical slice, mechanistic study, memory stability)
and the corrections log migrated as Artifact + Evidence + Derived — never as
beliefs (TODO19 §17).
