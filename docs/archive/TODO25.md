# TODO25 — Boundary Certification and Instrument Debt

**Status:** EXECUTED 2026-09-14 — Phase A (4 debt items) + Phase B (parity boundary certified; H24.2 certified AGAINST in round 3; H24.3 resolved instrument-blocked — see T25.B.3) + Phase C (CEEC builders/audit/runner/report/drift cadence) + Phase D (trainable_on, flat_classification_hard + certified H24.2 round-3 verdict, research one-shot, probe promotion, CEEC guide) + post-Phase-D continuation (improvement #6: vacuous single-candidate overrides unrecorded). Remaining work (improvement #7 composed backbone+ψ, #10 process items) → **TODO26.md**. PyPI publishing remains out of scope.
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
`measurement_block`. — B.3 executed under a minutes-only budget and
returned a measurement block (instrument boundary), the honest
`measurement_block` path the discipline prescribes.

---

## Phase C: CEEC Robustness — Experiments, Decisions, Reporting

Friction measured while landing B.1/B.2: required-field discovery by
failure (`created_at`, budget literal, falsification/overturn gates,
quality-flag spellings), evidence assembled by hand, no ledger-level
report, no post-hoc decision audit. Phase C turns each into an
instrument.

| Task | Deliverable | Depends On |
|---|---|---|
| **T25.C.1 Experiment/belief builders** | `ceec.builders`: `experiment(...)` (auto `created_at`, defaults for gates/criteria, budget-mapping from `BudgetTier`), `gate_evidence(...)` (assembles the §19/§18 quality dict with exact flag spellings, validates against the gate readers), `chance_verdict(accuracies, n_eval)` (2·binomial-SE band + across-seed mean rule — the B.1 statistics as a reusable, tested helper) | — |
| **T25.C.2 Decision quality audit** | `ceec.audit.audit_decisions(store)`: for each Decision — did the selected experiment complete or fail? override justifications present? candidate set overlap with later `measurement_block`s? feeds a `decision_quality` Derived | A.3 |
| **T25.C.3 Ledger report renderer** | `research.reports.render_ledger(store)`: markdown/JSON rollup — experiments by status, calibration (Brier/log + §24 drift flags), beliefs by status, decisions + audit findings; `lab.research_report()` one-shot writing it beside the corpus report | C.2 |
| **T25.C.4 Closed-loop runner** | `ceec.run.run_experiment(store, experiment_id, probe)`: pre-register → execute probe callable → ingest artifact/evidence → `record_experiment_outcome` → optional boundary/promotion evaluation. Makes "every certified measurement is pre-registered with a recorded Decision" structural, not procedural | C.1 |
| **T25.C.5 §24 drift review cadence** | `review_flags` wired into `render_ledger` + a lock test: any belief whose Brier drifts > τ across rounds flags for review; reviewed state recorded as StatusChange | C.3 |

**Success criterion:** TODO25's own probes rewritten on the builders
(`chance_verdict` reproduces B.1 exactly); a fresh ledger built end-to-end
through `ceec.run` passes `run_ledger_audit` with zero hand-assembled
payloads; ledger report renders for both TODO24/25 ledgers.

---

## Phase D: Architectural Integration + Usability

Measured integration gaps: catalog rows that cannot train on a spec fail
by exception; saturation hides hypothesis signal; research entry points
span 3 modules with no quickstart one-liner; probe scripts duplicate
logic that belongs in the library.

| Task | Deliverable | Depends On |
|---|---|---|
| **T25.D.1 `trainable_on` catalog field** | `MechanismCandidate.trainable_on: frozenset[str]` (task classes the construction path actually trains on); `CampaignFitness`/`remeasure_catalog` consult it *before* building (replaces exception-driven skipping measured in B.2); mismatch → structured `measurement_block`, never a traceback | — |
| **T25.D.2 Non-saturating corpus variant** | `flat_classification_hard` problem class (higher dims / stronger noise so 20ep does not saturate — B.2's finding); H24.2's decision statistic re-runs on it, closing the round-2 experiment | D.1 |
| **T25.D.3 Research one-shot API** | `lab.research_report(spec_key, tier)` → single dict: synthesis, evolution plan, corpus arms, ledger summary; docs quickstart updated to one call per practitioner question | C.3 |
| **T25.D.4 Probe → library promotion** | `scripts/probes` statistics (spearman, chance verdict) and record-flow helpers move into `computronium_lab.research` / `ceec.builders`; probes shrink to thin invocations (probe conventions: measured-regime numbers + citing demo stay) | C.1 |
| **T25.D.5 CEEC practitioner guide** | `docs/research/todo24/ceec_guide.md`: pre-register → run → decide → boundary/promote → calibrate walkthrough using the Phase C builders, with the TODO25 ledgers as worked examples | C.5 |

**Success criterion:** a newcomer reproduces the parity boundary
end-to-end from `ceec_guide.md` alone in one session; `flat_classification_hard`
produces an uncensored H24.2 verdict (FOR/AGAINST, no "censored" escape
hatch); `ruff` + strict pyright stay clean.

---

## 17. Progress Log

### Session 2026-09-14 — Phase A ✅
- [x] T25.A.1 `train_data` on `Lab.train` (+ test); corpus/campaign call sites deduped — 34+6 tests green
- [x] T25.A.2 Catalog claims narrowed; all-rows×all-claimed-substrates validation loop clean; provenance notes added
- [x] T25.A.3 `candidate_ids` on `ceec.selection.decide`; kernel shim → thin `decide` call; phase-2 evolution tests green
- [x] T25.A.4 ecosystem pyright 0 errors; test_ecosystem green

### Session 2026-09-14 — Phase B ✅

- [x] T25.B.1 **Parity boundary certified** — probe (`scripts/probes/todo25_parity_boundary.py`): lr sweep {0.01, 0.1, 0.3} @ 20ep all within the chance band; certified 120ep × 3 seeds → accuracies [0.469, 0.539, 0.531], mean 0.513, verdict `abs(mean−0.5) ≤ 2·SE(n=3)`. Chance band set honestly at 2·binomial SE over the 32-episode val split (±0.177 per-seed; mean rule carries the decision). Recorder (`scripts/probes/todo25_parity_record.py`): belief `B-PARITY-CHANCE-001` + vector evidence (defect_audit=pass, integrity_checks=pass, known_levers_exhausted=True, seeds=3, matched_control) → **all §19 boundary gates passed → status `boundary`**. Cookbook entry #2 written (`docs/research/todo24/cookbook.md`, 1 promotion + 1 boundary); ledger audit clean.
- [x] T25.B.2 **Surrogate recalibrated (H24.2 round 2)** — probe (`scripts/probes/todo25_surrogate_recal.py`): 10 campaign-trainable rows at flat 20ep/seed 0; **Spearman ρ = 0.418** (smoke tier was 0/4 top-3). **Saturation censoring measured:** 6 rows at accuracy 1.0 (`epc_deep, ff_mlp, ntm_classifier, ntm_sequence, pepita_mlp, spatial_lattice_bp`) make top-3 agreement degenerate. H24.2 round 2 pre-registered as `X-H24-H242-T25V1` (certified/nightly, decision rule "ρ > 0.5 at a non-saturating operating point"), evidence recorded, **left OPEN** — never scored FOR on saturated data. Ledger audit clean.
- [x] T25.B.3 ψ quick-tier sweep (H24.3) — **resolved as instrument-blocked, not compute-deferred**: the timing probe showed the registered continual benchmark cannot run `temporal_psi_task_switcher` at any budget — `AdaptivePsiReadout` is a bare closed-form readout (no `nn.Module` θ, no `.geometry`), so task-A `lab.train`, `theta_digest`, and the θ-finetune control all crash; Phase 4 tests only ever passed `backprop_mlp`. Recorded as `X-H24-H243-T25V1` (pre-registered → `failed` with an instrument-boundary measurement block and a `outcome_boolean=None` calibration — never scored); round 1's "ψ underperformed" provenance is flagged as not reproducible through this instrument. Ledger audit clean.

### Session 2026-09-14 — Phase C/D planned

Scope added from this session's CEEC friction: builders for
experiment/evidence/chance-verdict payloads (C.1), decision quality audit
(C.2), ledger report renderer (C.3), closed-loop `ceec.run` (C.4), §24
drift cadence (C.5); architectural — `trainable_on` catalog field (D.1),
non-saturating `flat_classification_hard` corpus variant (D.2),
`lab.research_report` one-shot (D.3), probe→library promotion (D.4),
CEEC practitioner guide (D.5). Status: **EXECUTED — see the Phase C and
Phase D session entries above.**

### Session 2026-09-14 — H24 re-scores

| ID | Round 1 (smoke) | Round 2 (certified flat) | Round 3 (certified hard) | Status |
|---|---|---|---|---|
| H24.2 | AGAINST (0/4, noise) | ρ=0.418, censored by saturation | **ρ=0.494 ≤ 0.5 at a non-saturating point → AGAINST** (`X-H24-H242-T25V3`) | CLOSED as certified AGAINST |
| parity (H24.5-adjacent) | recorded limitation | **certified boundary belief** `B-PARITY-CHANCE-001` | — | CLOSED as boundary |
| H24.3 (ψ task-switch) | "underperformed" (smoke; harness ≠ registered benchmark) | — | **instrument-blocked** (`X-H24-H243-T25V1`, measurement block) | BLOCKED — composed backbone+ψ instrument is the unblocker (TODO26) |

Round 3 rode the closed loop (`ceec.run.run_experiment`): pre-register →
§22 decision → 10-row hard-task campaign → evidence → calibration scored
AGAINST under the recorded rule. Round 2 (`X-H24-H242-T25V1`) closed as
`censored_superseded` (calibration line with `outcome_boolean=None` —
never scored FOR on saturated data); the failed first attempt
(`X-H24-H242-T25V2`) remains in the ledger as the record of the
fixed-dim build-path defect D.2 exposed and fixed.

### Session 2026-09-14 — Phase C ✅

- [x] T25.C.1 `ceec.builders` — `experiment(...)` (auto `created_at`, §22 design defaults, tier→budget map), `gate_evidence`/`quality_flags` (exact §18/§19 flag spellings, validated against the gate readers), `chance_verdict` (2·binomial-SE band + across-seed mean rule; reproduces B.1 exactly — tested). Tests: `packages/ceec-core/tests/test_ceec_builders.py`
- [x] T25.C.2 `ceec.audit.audit_decisions(store)` — selected-experiment resolution, override justification, candidate-vs-later-measurement-block overlap; `record=True` appends a `decision_quality` Derived (audits stay read-only by default)
- [x] T25.C.3 `render_ledger(store)` → (markdown, data) rollup: experiments/beliefs by status, calibration + `review_flags` + Brier drift, decisions + audit findings; `Lab.research_report(..., path=...)` writes `ledger_report.md`/`.json`; both TODO24/25 ledgers render + audit clean
- [x] T25.C.4 `ceec.run.run_experiment(store, experiment, probe, evaluate=...)` — pre-register (builder draft or pre_registered id) → §22 single-candidate decision → probe (outcome generated strictly after pre-registration) → artifact/evidence → calibration → optional boundary/promotion. Probe exceptions record `failed` + `missing` evidence, never raise. `_ALLOWED_ARTIFACT_TYPES` extended (`experiment_payload`, `experiment_failure`)
- [x] T25.C.5 §24 drift cadence — `calibration.belief_drift(store, tau=0.15)` + `review_belief` (`acknowledge`→instrument note; `reopen`/`quarantine`→gated `StatusChange`); `review_flags` wired into `render_ledger`; lock-tested

### Session 2026-09-14 — Phase D ✅

- [x] T25.D.1 `MechanismCandidate.trainable_on: frozenset[str]` — every row declares its trainable problem classes; `CampaignFitness.evaluate` raises structured `NotTrainableError`; `ResearchConstitution` rejects at plan admission; `MeasurementRunner` files blocks *before* building (no exception-driven skips). Two latent fixed-dim build defects surfaced and fixed instead of excluded: `role_split_muon_readout` and `spatial_lattice_bp` catalog rows now pass `input_dim`/`output_dim` recipe kwargs (hard-spec matmul-shape crashes)
- [x] T25.D.2 `flat_classification_hard` corpus class (64×8 dims; `HARD_TASK_PARAMS` pinned by `scripts/probes/todo25_hard_task.py`: same scale/noise as flat, hardness via dims/classes — top row 0.984, zero rows ≥ 0.995, weak rules at the collapse ceiling); H24.2's decision statistic re-ran on it (round 3, above) — uncensored AGAINST
- [x] T25.D.3 `Lab.research_report(spec | spec_key, tier, path)` one-shot: synthesis + evolution plan (dry run) + corpus arm plan (trainable vs expected blocks) + ledger rollup; spec `key()` round-trip
- [x] T25.D.4 probe→library promotion — `spearman_rho` (average-rank ties, scipy-consistent) in `computronium.validation.statistics`; `chance_verdict`/`gate_evidence` in `ceec.builders`; parity/recal probes rewritten as thin invocations (B.1 verdict now derives its band from `n_eval`, never a fixed ±0.03)
- [x] T25.D.5 `docs/research/todo24/ceec_guide.md` — pre-register → run → decide → boundary/promote → calibrate walkthrough on the Phase C builders, TODO25 ledgers as worked examples, instrument checklist

**Phase C/D success criteria met:** fresh ledger end-to-end through
`ceec.run` audits clean with zero hand-assembled payloads (tested +
T25V3 run); ledger report renders for both TODO24/25 ledgers
(`scratch/reports/`); `chance_verdict` reproduces B.1 exactly;
`flat_classification_hard` produced an uncensored FOR/AGAINST verdict;
ruff + strict pyright clean on all touched modules; demo gate + gallery
lock + research suites green (80 + 26 tests).

### Session 2026-09-14 — Continuation ✅

- [x] Improvement #6 landed — `ceec.selection.decide` treats a
  `select_experiment` override on a single-eligible-candidate pool as
  **vacuous**: still validated (ineligible target raises `StoreError`)
  but not recorded, so §24 `override_rate` keeps signal for real
  selections-with-alternatives. Closes the by-construction
  `override_rate_high` firing observed at 2/2 closed-loop decisions in
  `scratch/todo24_h24.sqlite3`. `run_experiment` and the evolution
  kernel's `_scoped_decision` keep passing the explicit selection intent
  and inherit the fix unchanged. Policy note in
  `docs/ceec/CALIBRATION_POLICY.md`; guide note in
  `docs/research/todo24/ceec_guide.md`. Tests:
  `test_vacuous_single_candidate_override_unrecorded`,
  `test_closed_loop_override_rate_stays_clean` — ceec (37) + evolution
  phase-3 suites green, ruff + strict pyright clean on touched files.
- [x] **CEEC reference consolidated** — root [`CEEC.md`](CEEC.md) is the
  canonical system reference (chain, object model, gates/thresholds, §22
  selection incl. the vacuous-override rule, §24 calibration, closed
  loop, CLI, ledgers-in-repo map, honest assessment); README's CEEC
  section rewritten to the canonical package (`packages/ceec-core`, not
  the `computronium/ceec` shim) with the complete module table and CLI;
  shim-stale CLI/location pointers fixed in
  `docs/ceec/{CEEC_CORE,LEDGER_POLICY,CALIBRATION_POLICY,INSTRUMENT_BELIEFS}.md`.

### 💡 Improvements discovered this session
1. **Saturation censoring as a first-class statistic.** Flat classification saturates ≥6 catalog rows at 20ep; any rank-based hypothesis test on it is degenerate. A non-saturating task class (larger dims, harder noise) is the highest-value corpus addition for hypothesis work. — *landed as `flat_classification_hard` (D.2)*
2. **Per-seed chance bands must carry their binomial SE.** The first parity pass used a fixed ±0.03 band and got the wrong verdict; the honest band at n_eval=32 is ±0.177. Any future "at chance" screen should derive its band from the eval size. — *landed as `ceec.builders.chance_verdict` (D.4)*
3. **`temporal_psi_task_switcher` and `nca_predictor` are not campaign-trainable on flat specs** (readout/no-geometry builds). `CampaignFitness` skips them like the evolution kernel does; the catalog could carry a `trainable_on` field to make this explicit instead of exception-driven. — *landed as `trainable_on` (D.1)*
4. **Fixed-dim construction paths masquerade as spec-generic.** `role_split_muon_readout` and `spatial_lattice_bp` built 32-dim geometries for any spec (crash on 64-dim input). When a row fails a *buildable-looking* spec, diff the recipe kwargs before concluding "not trainable" — parameterize the path, don't blocklist the row. — *fixed in D.1*
5. **Calibration probes must sweep what the campaign actually measures.** The first hard-task sweep varied (scale, noise) around `CampaignFitness`, whose hard path pinned the very constants under test — four "different" candidates gave byte-identical accuracies. Calibration sweeps must go through the raw generator + trainer; the pinned constant is chosen once, after the sweep.
6. **Single-candidate closed-loop decisions fire the §24 override-rate flag by construction** (`override_rate_high` at 2/2 decisions in `scratch/todo24_h24.sqlite3`). `decide()` could treat a one-element candidate pool as a non-override selection so the flag keeps signal for real overrides. — *landed post-Phase-D: vacuous single-candidate overrides are validated but unrecorded*
7. **T25.B.3 (H24.3) is instrument-blocked, not compute-blocked.** The continual corpus path requires a geometry-backed system; the flagship ψ mechanism is a bare ridge readout. The unblocking work is a **composed backbone+ψ system** (trainable feature-extractor θ + ψ ridge on top): ψ arm = frozen θ with per-episode ridge re-solve, θ-finetune control = SGD on the same backbone at matched compute, frozen_no_psi = frozen θ + linear probe. — *scoped as TODO26 Phase S (T26.S.1–S.4)*; round 1's ψ-underperformance result should carry an "instrument ≠ registered benchmark" caveat wherever cited.
8. **Pre-fix ledgers overcount `override_rate`.** Decisions recorded in `scratch/todo24_h24.sqlite3` / `scratch/todo25_parity.sqlite3` predate the vacuous-override semantics; their stored calibration rows keep the inflated rate (append-only — no rewrite). TODO26 calibration reviews citing those ledgers should read pre-continuation single-candidate decisions as non-overrides when reading trends.
9. **TODO26's ψ campaign inherits a clean override budget.** The composed backbone+ψ closed loop (item 7) runs through `run_experiment`; its single-candidate decisions are now non-overrides by construction, so the `override_rate` flag stays free for the campaign's real surrogate-ranked focus selections.
10. **CEEC process improvements (from the CEEC.md review).** (a) Ledger ownership: no machine-readable statement of which ledger owns what — record a role at `init` and let `run_audit` enforce scope (campaign ledgers can't gate against main-ledger instruments). (b) `policy_version` stamp on Decisions/CalibrationRecords — the vacuous-override semantic change left pre-fix ledgers indistinguishable in-data. (c) One-command round close (`ceec close-round`: render + audit + review-flags, non-zero exit on triggers) to make the §24 cadence mechanical. Details in `CEEC.md` § "Honest assessment".

### 📝 Implementation notes
- Probes: `scripts/probes/todo25_parity_boundary.py` (campaign; verdict via `chance_verdict`), `todo25_parity_record.py` (belief+gates via `builders.gate_evidence`), `todo25_surrogate_recal.py` (task-parameterized comparator; library `spearman_rho`), `todo25_recal_record.py` (round-3 closed loop via `ceec.run`), `todo25_hard_task.py` (hard-task calibration sweep). Ledgers: `scratch/todo25_parity.sqlite3` (boundary), `scratch/todo24_h24.sqlite3` (H24 rounds 1-3) — both audit-clean, git-ignored; ledger reports in `scratch/reports/`.
- New instrument modules: `ceec/builders.py` (experiment/gate_evidence/quality_flags/chance_verdict), `ceec/run.py` (run_experiment/ProbeResult/ExperimentRun), `ceec.audit.audit_decisions`, `ceec.calibration.belief_drift/review_belief`, `computronium_lab.research.reports.render_ledger`, `Lab.research_report`/`_spec_from_key`. Tests: `packages/ceec-core/tests/test_ceec_builders.py`, `test_ceec_run.py`, `packages/computronium-lab/tests/test_research_todo25.py`.
- `render_ledger` is read-only; `audit_decisions(..., record=True)` opts into the append-only `decision_quality` Derived. `spearman_rho` returns 0.0 (not NaN) under zero rank variance — saturation degenerates to "no measured association".
- `ceec.experiment` budget mapping: tier strings {smoke→quick, quick→standard, certified→nightly} with direct ceec literals passing through; ceec stays Computronium-free (lab callers pass `BudgetTier.<X>.value`).
- CEEC `Experiment` requires `created_at=now()`, `budget ∈ {quick, standard, nightly}`, `falsification_criterion`, `overturn_criterion`, `hard_gates`; belief `type_ ∈ {instrument, mechanism, generality, defect}` (boundary is a *status*, not a type); `GateResult` fields are `gate/passed/rationale`; `current_status` is beliefs-only (experiments read `.status` via `get_experiment`) — all now hidden behind the builders.
- `decide(candidate_ids=...)`: `StoreError` on an ineligible override target — the kernel catches it and falls back to max-EV-per-cost selection; `run_experiment` pre-checks hard constraints and raises before the decision instead.
