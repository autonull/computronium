# TODO25 — Boundary Certification and Instrument Debt

**Status:** EXECUTED 2026-09-14 — Phase A (4 debt items) + Phase B (parity boundary certified, H24.2 round 2 recorded); T25.B.3 deferred to a compute session.
**Builds on:** TODO24 (all 8 phases landed; extension points `register_problem_class` /
`register_objective` / `register_curriculum` shipped with zero-`Any` research layer).
**Explicit exclusion:** PyPI publishing remains out of scope.

---

## 0. The Next Synthesis

TODO24 shipped the corpus, benchmarks, and cookbook with one certified
promotion but left measured gaps: the surrogate is uncalibrated, ψ
adaptation underperformed at smoke budget, parity sits at chance without
a certified boundary, and four engineering-debt items were queued. TODO25
closes the debt and runs the cheapest campaigns that turn open
hypotheses into certified outcomes — promotion or boundary, never limbo.

Core rule unchanged: **evolution/campaigns produce evidence; gates
dispose; claims only at certified tier.**

---

## Phase A: Engineering Debt (no campaigns)

| Task | Deliverable | Depends On |
|---|---|---|
| **T25.A.1 `lab.train` loader injection** | `train_data` pass-through on `Lab.train`; `CampaignFitness`, corpus permuted control, continual arms, and `_control_accuracy` route through it (drops direct `train_with_certificates` calls outside `training.py`/`lab.py`) | — |
| **T25.A.2 Neuromorphic claim fix** | Catalog substrate claims narrowed to constructible paths (`backprop_mlp`: −neuromorphic; `ff_mlp`: −neuromorphic + provenance note); every catalog row now validates on every claimed substrate via `screen_config` | — |
| **T25.A.3 CEEC scoped `decide`** | `ceec.selection.decide(..., candidate_ids=...)` restricts the §22 pool; evolution kernel's `_scoped_decision` becomes a thin `decide` call (override + `StoreError` fallback to max-EV) | — |
| **T25.A.4 `ecosystem.py` pyright** | `check_external` dispatch via `StabilityGuard` cast; 0 pyright errors | — |

**Success criterion:** full lab + ceec suites green; ruff + pyright clean
on all touched files.

---

## Phase B: Certified Campaigns

| Task | Deliverable | Depends On |
|---|---|---|
| **T25.B.1 Parity boundary (H24-adjacent, cookbook #2)** | Lever sweep (lr ∈ {0.01, 0.1, 0.3} @ 20ep) + certified 120ep × 3 seeds on `ntm_classifier`; if all at chance: record belief + evidence (`defect_audit=pass`, `integrity_checks=pass`, `known_levers_exhausted=True`, rescue prob ≤ 0.05) → `declare_boundary` → second cookbook entry | A |
| **T25.B.2 Surrogate recalibration (H24.2/H24.6)** | Rank surrogate vs campaign at certified operating points (20ep flat × catalog rows); corpus-driven predictor refit; re-score H24.2 | A, B.1 compute slot |
| **T25.B.3 ψ quick-tier sweep (H24.3)** | Continual benchmark at quick tier (episode ladder × modes); re-score H24.3 | A, B.1 compute slot |

**Budget discipline:** certified parity = 120ep × 3 seeds + 3×20ep sweep
(~minutes on CPU, single-threaded tiers). Each campaign is pre-registered
before its outcome is scored. No gate weakening; blocked work gets a
`measurement_block`.

---

## 17. Progress Log

### Session 2026-09-14 — Phase A ✅
- [x] T25.A.1 `train_data` on `Lab.train` (+ test); corpus/campaign call sites deduped — 34+6 tests green
- [x] T25.A.2 Catalog claims narrowed; all-rows×all-claimed-substrates validation loop clean; provenance notes added
- [x] T25.A.3 `candidate_ids` on `ceec.selection.decide`; kernel shim → thin `decide` call; phase-2 evolution tests green
- [x] T25.A.4 ecosystem pyright 0 errors; test_ecosystem green

### Session 2026-09-14 — Phase B ✅ (T25.B.3 deferred)

- [x] T25.B.1 **Parity boundary certified** — probe (`scripts/probes/todo25_parity_boundary.py`): lr sweep {0.01, 0.1, 0.3} @ 20ep all within the chance band; certified 120ep × 3 seeds → accuracies [0.469, 0.539, 0.531], mean 0.513, verdict `abs(mean−0.5) ≤ 2·SE(n=3)`. Chance band set honestly at 2·binomial SE over the 32-episode val split (±0.177 per-seed; mean rule carries the decision). Recorder (`scripts/probes/todo25_parity_record.py`): belief `B-PARITY-CHANCE-001` + vector evidence (defect_audit=pass, integrity_checks=pass, known_levers_exhausted=True, seeds=3, matched_control) → **all §19 boundary gates passed → status `boundary`**. Cookbook entry #2 written (`docs/research/todo24/cookbook.md`, 1 promotion + 1 boundary); ledger audit clean.
- [x] T25.B.2 **Surrogate recalibrated (H24.2 round 2)** — probe (`scripts/probes/todo25_surrogate_recal.py`): 10 campaign-trainable rows at flat 20ep/seed 0; **Spearman ρ = 0.418** (smoke tier was 0/4 top-3). **Saturation censoring measured:** 6 rows at accuracy 1.0 (`epc_deep, ff_mlp, ntm_classifier, ntm_sequence, pepita_mlp, spatial_lattice_bp`) make top-3 agreement degenerate. H24.2 round 2 pre-registered as `X-H24-H242-T25V1` (certified/nightly, decision rule "ρ > 0.5 at a non-saturating operating point"), evidence recorded, **left OPEN** — never scored FOR on saturated data. Ledger audit clean.
- [ ] T25.B.3 ψ quick-tier sweep (H24.3) — **deferred**: a quick-tier episode ladder × 3 modes × 3 seeds is a separate compute session.

### Session 2026-09-14 — H24 re-scores

| ID | Round 1 (smoke) | Round 2 (this session) | Status |
|---|---|---|---|
| H24.2 | AGAINST (0/4, noise) | ρ=0.418, censored by saturation | OPEN (`X-H24-H242-T25V1`) |
| parity (H24.5-adjacent) | recorded limitation | **certified boundary belief** `B-PARITY-CHANCE-001` | CLOSED as boundary |

### 💡 Improvements discovered this session
1. **Saturation censoring as a first-class statistic.** Flat classification saturates ≥6 catalog rows at 20ep; any rank-based hypothesis test on it is degenerate. A non-saturating task class (larger dims, harder noise) is the highest-value corpus addition for hypothesis work.
2. **Per-seed chance bands must carry their binomial SE.** The first parity pass used a fixed ±0.03 band and got the wrong verdict; the honest band at n_eval=32 is ±0.177. Any future "at chance" screen should derive its band from the eval size.
3. **`temporal_psi_task_switcher` and `nca_predictor` are not campaign-trainable on flat specs** (readout/no-geometry builds). `CampaignFitness` skips them like the evolution kernel does; the catalog could carry a `trainable_on` field to make this explicit instead of exception-driven.

### 📝 Implementation notes
- Probes: `scripts/probes/todo25_parity_boundary.py` (campaign), `todo25_parity_record.py` (belief+gates), `todo25_surrogate_recal.py` (comparison), `todo25_recal_record.py` (evidence + pre-registration). Ledgers: `scratch/todo25_parity.sqlite3` (boundary), `scratch/todo24_h24.sqlite3` (H24 round 2) — both audit-clean, git-ignored.
- CEEC `Experiment` requires `created_at=now()`, `budget ∈ {quick, standard, nightly}`, `falsification_criterion`, `overturn_criterion`, `hard_gates`; belief `type_ ∈ {instrument, mechanism, generality, defect}` (boundary is a *status*, not a type); `GateResult` fields are `gate/passed/rationale`; `current_status` is beliefs-only (experiments read `.status` via `get_experiment`).
- `decide(candidate_ids=...)`: `StoreError` on an ineligible override target — the kernel catches it and falls back to max-EV-per-cost selection.
