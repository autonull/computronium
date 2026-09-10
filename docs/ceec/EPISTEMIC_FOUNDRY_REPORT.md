# Epistemic Foundry Report

**Round:** 4 (2026-09-10) — temporal-ψ mechanism built and X-TPC-001 executed under CEEC governance.

## Active beliefs

| ID | Statement (abridged) | Status | Interval |
|---|---|---|---|
| B-H1-ADAPTIVE-LOCAL-INVERSES | Slow feedback adaptation improves local credit descent | open | [0.45, 0.80] (was [0.20, 0.60]) |
| B-H2-TEMPORAL-PSI-CREDIT | Temporal ψ credit extends frozen-θ task horizon | open | [0.20, 0.40] (was [0.10, 0.45]) |
| B-H3-STABLE-TRANSIENT-AMPLIFICATION | Stable transient amplification improves robustness | open | [0.30, 0.70] (was [0.20, 0.55]) |
| B-H4-ROUTING-SPARSITY-EFFICIENCY | Routing yields measurable resource benefits | open | [0.05, 0.35] (was [0.25, 0.60]) |
| B-H5-UPDATE-RULE-SPECIALIZATION | Role-specific update rules improve learning/stability | open | [0.25, 0.60] (was [0.20, 0.55]) |

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

## Round 4 outcomes — X-TPC-001 (temporal-ψ mechanism build)

- **Mechanism build (G-HARD-9/G-HARD-8 satisfied):** new Plasticity
  primitive `TemporalPsiPlasticity` (`computronium/core/plasticity/
  temporal_psi.py`) — trace-decayed ridge readout residual stepped on the
  NUDGED settle (`psi_phase = "nudged"`), identity-carded, ρ=1 forget-free
  limit property-locked. Three pre-flight defects found and fixed BEFORE
  the governed run (recorded in the probe docstring): trace-accumulation
  sign defect (ρ applied to the incoming batch, trace never forgot),
  additive-residual channel inert under saturated frozen-net margins
  (9.5 vs 0.4/sample, zero argmax flips), and onehot−softmax residual
  target collapse (replaced by centered one-hot).
- **Execution:** `scripts/probes/x_tpc_001.py`, ~8.5 s CPU, 3 seeds,
  A→B→A' switch (parity → last-symbol → parity), θ bitwise frozen in the
  ψ phase (SHA-256 + FrozenThetaAudit).
- **P1 (acquisition) SUPPORTED:** temporal_090 beats the frozen-null
  floor by ≥ +0.10 on 2/3 seeds (B {0.754, 0.777, 0.766} vs null
  {0.645, 0.660, 0.707}).
- **P2 (temporal credit) FALSIFIED at quick scale:** the forget-free
  closed-form arm matches A' return (0.875–0.875 vs temporal
  0.863–0.949) — the parity/last-symbol h-fits don't conflict, so trace
  forgetting buys nothing here. A latent artifact reading (temporal >
  closed-form under the residual target) was identified as
  target-induced and discarded.
- **Belief update:** B-H2 narrowed [0.10, 0.45] → [0.20, 0.40]:
  supervised-ψ acquisition is real; the *temporal* (trace-decay)
  advantage needs conflicting task fits — an X-TPC-002 follow-up with
  deliberately conflicting A/B tasks is the boundary-condition test.
- **Gates:** only `probability_threshold` fails (one probe cannot
  promote). **Calibration:** CAL-000005 (acquisition_only, outcome
  boolean 0 vs the temporal-credit prediction). **Audit:** clean.

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
| X-TPC-001 | completed, P1 positive / P2 falsified, calibrated |
| X-STA-001 | completed, positive, calibrated |
| X-RSE-001 | completed, negative at operating point, calibrated |
| X-USU-001 | completed, positive, calibrated |

## Calibration summary

5 records (CAL-000001..CAL-000005). Outcomes: 3 success (ALI, STA, USU),
2 failure (RSE routing benefit, TPC temporal-credit advantage). Review
flags: none — prediction misses were honest interval misses, not
miscalibration drift.

## Migrated evidence

TODO18 claim records (vertical slice, mechanistic study, memory stability)
and the corrections log migrated as Artifact + Evidence + Derived — never as
beliefs (TODO19 §17).
