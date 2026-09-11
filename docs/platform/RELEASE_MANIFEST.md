# Release Manifest

Status vocabulary: `draft` (skeleton/demo exists) → `validated` (benchmark +
parity + scoped docs) → `released` (all release gates passed).

| Package | Version | Status | Evidence refs | Belief refs | Limitations | Gates passed |
|---|---|---|---|---|---|---|
| ceec-core | 0.1.0 | validated | E-000001..E-000026 (internal ledger provenance) | — | pydantic dependency (documented deviation); no concurrent-writer hardening (`_next_id`) | G-1, G-2, G-4, G-6 |
| psi-peft | 0.1.0 | validated | X-TPC-001, X-TPC-002, X-TPC-003, X-TAC-001 (E-000022..E-000026) | B-H2-TEMPORAL-PSI-CREDIT | quick-budget CPU probes only; conflict required for forgetting-on; buffered arm trades ~0.1 conflict-phase accuracy for ~2x speed (documented boundary); no optimality claim vs gradient readout retraining | G-1, G-2, G-3, G-6 |
| stability | 0.1.0 | validated | TODO11 R11.3.3 PR-5 calibration; registered artifact `docs/figures/registered/stability_guard_pr5.json` | — | energy-minimization + non-normal linear coordinates only (no transformer-collapse claim); `fast_proxy` calibration-only; probe cost 2–13× a step — deploy at the calibrated interval; simulation only, no hardware validation | G-1, G-2, G-3, G-4, G-6 (parity lock `tests/platform/test_stability_parity.py`) |
| local-feedback | 0.1.0 | validated | X-ALI-001 (E-000018), X-ALI-002 short-trajectory validation (E-000027, adaptive better on all 3 seeds at 10-step horizon) | B-H1-ADAPTIVE-LOCAL-INVERSES (narrowed to [0.55, 0.85] post X-ALI-002) | reduced two-layer local-trainer scope (not end-to-end vs internal EqProp systems); matched-norm required; slow-blend feedback_lr=0.02 is the validated setting (full re-projection lr=1.0 thrashes); depth scaling unvalidated (X-ALI-003) | G-1, G-2, G-3, G-6 (parity lock `tests/platform/test_local_feedback_parity.py`) |
| computronium-lab | 0.1.0 | validated | wraps validated mechanisms above (recipes carry X-TPC-*/X-ALI-*/X-USU-001/X-STA-001/002 refs); optional CEEC recording smoke-tested | — | quick synthetic task only (dataset wiring not exposed); eqprop needs ≥5 quick epochs; fa_mlp quick-tuned to lr=0.05 (internal default too weak for quick mode); markdown reports only; adds no new ontology semantics | G-1 (imports computronium by design), G-2, G-6 |

Phase 6 disposition (closed 2026-09-11):
- **X-STA-002 executed** (E-000028): stable-transient coordinates give
  4×–2600× transient retention over matched contractive controls at ρ=0.85
  while noise divergence scales identically (retention gain, **not** SNR
  gain); all settle within budget. `stability.matrices` + Lab
  `stable_amplification` recipe shipped on this evidence; belief
  B-H3-STABLE-TRANSIENT-AMPLIFICATION narrowed to [0.55, 0.85].
- **X-USU-002 deferred** (explicit boundary): RoleSplit recipe boundary is
  the X-USU-001 result only; no defect-hunt conclusion claimed.
- **X-RSE / X-RSE-002 blocked** (explicit boundary): dense baseline not
  reliably above chance; no routing recipe ships.