# Release Notes — Computronium Platform Launch (TODO20)

Date: 2026-09-11. All packages are uv workspace members installed by
`uv sync --dev --all-extras`.

## Packages

| Package | Version | Status | Evidence status |
|---|---|---|---|
| ceec-core | 0.1.0 | validated | internal ledger provenance E-000001..E-000026; audit clean |
| psi-peft | 0.1.0 | validated | X-TPC-001..003, X-TAC-001; parity lock vs internal ridge |
| local-feedback | 0.1.0 | validated | X-ALI-001, X-ALI-002 (E-000027, adaptive wins all seeds); parity lock |
| stability | 0.1.0 | validated | PR-5 calibration; artifact lock `stability_guard_pr5.json`; X-STA-002 (E-000028) |
| computronium-lab | 0.1.0 | validated | wraps validated mechanisms; order-invariant compare pinned by test |

## What is new in this launch

- Five standalone packages extracted under the ONE-copy rule (Rule 6):
  `packages/` copies are the source of truth; `computronium` depends on
  them via uv workspace membership; legacy import paths are adapters.
- X-STA-002 executed and closed (E-000028): stable-transient coordinates
  give 4×–2600× transient retention over matched contractive controls at
  ρ=0.85 while noise divergence scales identically (retention gain, not
  SNR gain); all settle within budget. `stability.matrices` helper and the
  `stable_amplification` Lab recipe shipped on this evidence.
- Beliefs narrowed post-evidence: B-H3-STABLE-TRANSIENT-AMPLIFICATION and
  B-H1-ADAPTIVE-LOCAL-INVERSES both to [0.55, 0.85].
- External docs published: mechanism recipe book, neuromorphic edge
  blueprint (simulation-only), external summary, publication-draft outline,
  this file, and the release manifest.

## Known limitations (per package)

- **ceec-core:** depends on pydantic v2 (documented deviation from the
  stdlib-only plan); no concurrent-writer hardening of `_next_id`.
- **psi-peft:** buffered arm trades ~0.1 conflict-phase accuracy for ~2×
  speed; quick-budget CPU probes only; conflict required for forgetting.
- **local-feedback:** two-layer local-trainer scope; slow-blend
  (`feedback_lr=0.02`) is the validated setting; depth scaling (X-ALI-003)
  deferred.
- **stability:** energy-minimization + non-normal linear coordinates scope;
  guard probe costs 2–13× a step — deploy at the calibrated interval.
- **computronium-lab:** quick synthetic task only; eqprop needs ≥5 quick
  epochs; fa_mlp quick-tuned to lr=0.05.

## Explicit boundaries / deferred work

- **X-USU-002** (muon-on-forward defect hunt): deferred; the RoleSplit
  recipe boundary is the X-USU-001 result only.
- **X-RSE / X-RSE-002** (routing efficiency): release blocked — dense
  baseline not reliably above chance; boundary recorded, no routing recipe.
- ceec-core/psi-peft single-source migration (Rule 6 end-state): internal
  duplicates remain as documented transitional scaffolding; suggested
  migration order in `TODO20.md` §17.