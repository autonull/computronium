# TODO22 — Platform Maturation & Next Research Cycle

**Status:** PLANNED (2026-09-11). Supersedes TODO21 upon acceptance.
**Created:** 2026-09-11
**Supersedes:** TODO21 (IN PROGRESS — Phase 1 publication DONE, Phase 2 boundary-gated science DONE, Phase 3 hygiene DONE, Phase 3A dedupe DONE, Phase 4 deferred)

---

## 0. Charter

TODO21 shipped the manuscript (ICLR 2027 workshop), closed the hygiene debt (Register C + Phase 3A dedupes), and drew honest boundaries on B-H3, X-USU-002, X-RSE. The platform exists as five standalone packages with a unified ontology and a verified claim set.

TODO22 has three aims, in payout order:

1. **Publication follow-through** — shepherd the manuscript to acceptance; maintain the reproducibility artifact; respond to reviews without scope creep.
2. **Platform hardening** — make the five packages independently installable, versioned, and documented for external adoption; close the two documented deferrals (T21.3.2, T21.3.4).
3. **Next research cycle** — use the now-mature platform to run *one* focused campaign that extends the I(C,U) law to I(C,U,P) at depth-matched conditions (the w17_icu_fit degradation was a sampling artifact, not a ψ effect — TODO17 §5.1), and ship the result as a v0.2 platform release.

Operating rule (inherited, tightened):

> No new internal knowledge accumulation unless it directly supports the publication response, a release-blocking defect fix, or the single scoped research campaign.

Non-goals: new ontology axes, new ledger features, new packages, hardware purchases, large-scale benchmarking beyond the scoped campaign, universal claims.

---

## 1. Phase 1 — Publication Follow-Through (highest leverage)

### T22.1.1 Review response tooling
- **File:** `docs/platform/REVIEW_RESPONSE_TEMPLATE.md` — structured template mapping each reviewer comment to: (a) manuscript location, (b) evidence id / command, (c) action taken or justification for no action.
- **Gate:** every reviewer point must resolve to a traceable artifact or an explicit "out of scope for this submission" with rationale.

### T22.1.2 Reproducibility artifact maintenance
- Keep `docs/platform/REPRODUCIBILITY.md` current with the manuscript's final claim set.
- **Fresh-clone gate:** `uv sync --dev --all-extras` + quick-mode demos must reproduce every cited number in <30 min walltime on CPU. Add CI job `repro-smoke` that runs this weekly.

### T22.1.3 Claim-discipline audit (continuous)
- Extend `tests/platform/test_release_docs.py` to scan the *final submitted PDF* (via pdftotext) for banned phrases and untraceable numbers.
- Run pre-submission and on every revision.

### T22.1.4 Version pin for the paper commit
- Tag the exact commit used for the submission: `git tag paper/iclr2027-workshop-v1 <commit>`.
- All review responses must be on branches from this tag; no silent rewrites of the evidence chain.

**Acceptance:** manuscript under review; every claim traceable; fresh-clone gate green; review response template ready.

---

## 2. Phase 2 — Platform Hardening (external adoption readiness)

### T22.2.1 Per-package pyright configs (T21.3.2 closure)
- **Target:** `packages/ceec-core/pyrightconfig.json`, `packages/psi-peft/pyrightconfig.json`, `packages/local-feedback/pyrightconfig.json`, `packages/stability/pyrightconfig.json`, `packages/computronium-lab/pyrightconfig.json`.
- Each config must:
  - Enable `strict` for `src/` only.
  - Exclude `examples/`, `benchmarks/`, `tests/` (or use `--verifytypes` mode).
  - Declare `pythonVersion = "3.14"` and `venvPath/venv` for uv workspaces.
- **Gate:** `uv run pyright -p packages/<pkg>` passes on each package independently.

### T22.2.2 Lab trainer-metrics contract (T21.3.4 closure)
- **Problem:** `Lab.train` hardcodes history keys (`train_acc`, `val_acc`, `train_loss`); `ComparisonResult` has no per-epoch curve field.
- **Fix:** 
  1. `LabConfig.metrics_keys: tuple[str, ...] = ("train_acc", "val_acc", "train_loss")` — user-extensible.
  2. `ComparisonResult.history: dict[str, list[float]]` — per-arm, per-epoch curves.
  3. `Lab.train` returns `ComparisonResult` with populated history; `Lab.compare` aggregates.
- **Gate:** `packages/computronium-lab/tests/test_lab_train.py` asserts history shape matches `metrics_keys`.

### T22.2.3 Package versioning & release automation
- **Files:** each `packages/*/pyproject.toml` — `version = "0.1.0"` (initial), `[tool.uv.publish]` config.
- **Script:** `scripts/release_packages.py` — builds all 5 wheels, runs boundary/parity/determinism tests on the *installed* wheels (not editable), publishes to TestPyPI on tag `platform/v0.1.0`.
- **Gate:** `uv run python scripts/release_packages.py --dry-run` passes; actual publish is manual.

### T22.2.4 External documentation refresh
- Each package README must pass G-RELEASE-4 (scope, limitations, evidence refs, verification level) against the *published* evidence, not the internal ledger.
- `docs/platform/EXTERNAL_SUMMARY.md` updated to reflect v0.1 capabilities and boundaries.

### T22.2.5 Dependency audit & license compliance
- `uv run pip-audit` on each package wheel.
- `uv run pip-licenses --format=json` → `docs/platform/DEPENDENCY_LICENSES.json`.
- No GPL/AGPL in transitive closure.

**Acceptance:** all 5 packages independently installable from TestPyPI; pyright clean per-package; Lab history contract works; release automation tested; license audit clean.

---

## 3. Phase 3 — Scoped Research Campaign: I(C,U,P) at Depth-Matched Conditions

### T22.3.1 Campaign design (pre-registered)
- **Question:** Does ψ (plasticity) modulate the credit×update interaction surface *when depth is controlled*?
- **Hypothesis:** The w17_icu_fit degradation (0.944 → 0.722 held-out) was caused by depth-distribution mismatch in the training rows (d32 vs {1,2,100}), not by ψ. At depth-matched conditions, ψ is orthogonal to I(C,U) — the law generalizes.
- **Design:**
  - Fixed: `S=Digital, G=FeedforwardDAG (MLP), D=InstantaneousPass`
  - Varied: `C ∈ {bp, fa, pepita, lemma}`, `U ∈ {euclid, muon, ortho}`, `P ∈ {null, routing, fastweight}`, `depth ∈ {1, 2, 32, 50, 100}`
  - Seeds: 3 per cell
  - Budget: quick-mode (150 batches) for depth ≤ 50; 40 batches for depth 100
  - Total cells: 4 × 3 × 3 × 5 × 3 = 540 (subsettable to 180 by fixing U={muon, ortho} first)
- **Pre-registration:** `configs/ceec/experiments/icu_p_depth_matched.yaml`
- **Success criterion:** Held-out lattice accuracy ≥ 0.90 *with depth as a feature*; ψ coefficient not significant (p > 0.05) in the logistic fit.

### T22.3.2 Execution (background, ≤5 min/cell)
- **Script:** `scripts/probes/w18_icu_p_depth.py` — reuses `harvest_icu_table.py` parser, writes to `data/icu_measurements_v2.csv`.
- **Parallelism:** OMP=2, 3 concurrent shards by seed.
- **Walltime estimate:** 180 cells × ~2 min × 3 seeds / 3 parallel ≈ 6 hours background.

### T22.3.3 Analysis & report
- **Script:** `scripts/analysis/fit_icu_model_v2.py` — depth-stratified CV, ψ coefficient test, held-out geometry prediction (lattice, NCA, NTM).
- **Output:** `docs/reports/icu_p_depth_matched.html` — interaction surfaces per depth, coefficient table, prediction validation.
- **Claim lock:** `tests/integration/test_paper_claims.py` extended to validate the new report's numbers against the CSV.

### T22.3.4 Platform release v0.2
- **Tag:** `platform/v0.2.0` — includes the I(C,U,P) depth-matched result as a new recipe card entry.
- **Changelog:** `docs/platform/RELEASE_NOTES_v0.2.md` — what changed, what the new result means, updated boundaries.

**Acceptance:** campaign pre-registered; executed; held-out prediction ≥ 0.90; ψ orthogonality confirmed at 3 seeds; v0.2 released with updated recipe book.

---

## 4. Phase 4 — Conditional Science (boundary-gated, only if Phase 3 unblocks)

These run ONLY if Phase 3 produces a positive result that demands follow-up.

### T22.4.1 I(C,U,P) on retrieval-demanding tasks
- **Condition:** Phase 3 shows ψ *does* modulate I(C,U) on retrieval tasks (contrary to campaign 7.1).
- **Design:** Same C×U×P grid on NTM copy/recall + NCA growth tasks.
- **Gate:** pre-register first; budget ≤ 200 cells.

### T22.4.2 Stable-amplification noise probe (Phase 4 from TODO21)
- **Condition:** Reviewer asks for hardware-realistic validation of the stable-amplification recipe.
- **Design:** Quantized ψ readout (T21.4.1), noisy feedback blend (T21.4.2), substrate-noise replay (T21.4.3) — all simulation-only, quick-budget.
- **Gate:** each is pre-registered; falsification feeds the blueprint's "what is NOT claimed" section.

---

## 5. Release Gates (inherited + strengthened)

### G-RELEASE-7 — External installability
Each package must be installable via `pip install <pkg>==0.1.0 --index-url https://test.pypi.org/simple/` and pass its quickstart demo without the source tree.

### G-RELEASE-8 — Versioned API stability
No breaking changes to public APIs in `packages/*/src/<pkg>/` without a minor version bump and a migration note in the changelog.

### G-RELEASE-9 — Claim traceability in the wild
`tests/platform/test_release_docs.py` must verify that every number in `docs/platform/EXTERNAL_SUMMARY.md` and each package README resolves to a command + evidence id in the *released* artifact (not the dev tree).

---

## 6. Definition of Done

- [ ] Manuscript submitted; review response template ready; fresh-clone gate green (T22.1).
- [ ] All 5 packages have per-package pyright configs, pass independently (T22.2.1).
- [ ] Lab trainer-metrics contract implemented + tested (T22.2.2).
- [ ] Release automation tested on TestPyPI; packages installable externally (T22.2.3).
- [ ] External docs refreshed; license audit clean (T22.2.4, T22.2.5).
- [ ] I(C,U,P) depth-matched campaign pre-registered, executed, analyzed (T22.3.1–3).
- [ ] Platform v0.2 released with updated recipe book (T22.3.4).
- [ ] Conditional science items either executed or explicitly deferred with rationale (T22.4).

---

## 7. Minimal Viable TODO22

If constrained, the minimum acceptable TODO22 is:

1. T22.1.1–T22.1.3 (publication follow-through).
2. T22.2.1 (per-package pyright) + T22.2.2 (Lab history contract).
3. T22.3.1–T22.3.3 (scoped campaign — the single research deliverable).
4. T22.3.4 (v0.2 release).

Deferred in minimal mode:
- Release automation polish (T22.2.3 beyond dry-run).
- External doc refresh beyond what the campaign needs.
- Conditional science (T22.4).

---

## 8. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Reviewer demands new experiments | Pre-registered campaign (T22.3) is the *only* new experiment; other requests get "out of scope, future work" with boundary recorded. |
| Package pyright configs reveal deep typing debt | Strict mode on `src/` only; legacy findings in `examples/`/`tests/` excluded; debt stays in Register C. |
| Campaign execution exceeds budget | Subset to 180 cells (fix U={muon, ortho}); background with kill timeout; intermediate results logged every 50 cells. |
| ψ modulation found at depth-matched conditions | That *is* a result — report honestly; the law extends. If not found, orthogonality confirmed — also a result. |
| Platform adoption stalls without marketing | Non-goal. The measure is: can someone install, run, understand, trust, reuse? (TODO20 §13). |

---

## 9. Execution Order

### Step 1 — Publication readiness (immediate)
T22.1.1–T22.1.4. Do not launch packages or campaigns until the manuscript is submitted and the fresh-clone gate passes.

### Step 2 — Platform hardening (parallel with review wait)
T22.2.1–T22.2.5. These are pure engineering; no research risk.

### Step 3 — Scoped campaign (after submission, during review)
T22.3.1–T22.3.3. Pre-register → execute → analyze. This is the *only* new research.

### Step 4 — Release v0.2 (after campaign + review decision)
T22.3.4. Tag, changelog, publish.

### Step 5 — Conditional follow-ups (only if triggered)
T22.4.1–T22.4.2. Explicitly gated.

---

## 10. Success Metrics

TODO22 succeeds if:

1. The manuscript is accepted (or rejected with clean, traceable responses — no "we should have run X" regrets).
2. An external user can `pip install ceec-core psi-peft local-feedback stability computronium-lab --index-url https://test.pypi.org/simple/` and run each quickstart.
3. The I(C,U,P) depth-matched campaign produces a clean held-out prediction ≥ 0.90 and a citable ψ-orthogonality coefficient.
4. Platform v0.2 exists with updated recipe book and no breaking changes from v0.1.
5. Zero new untraceable claims in any external documentation.

---

## 11. Anti-Bureaucracy Clause (inherited)

```text
No new ledger features.
No new oracle features.
No new campaign infrastructure beyond the single scoped campaign.
No new probes unless tied to the campaign or a reviewer demand.
No new beliefs unless required for the campaign evidence.
No new schemas unless they become external recipes.
```

The measure of TODO22 is not how much we learned internally.

The measure is:
```text
Is the manuscript defensible? Are the packages independently usable? Does the one campaign produce a clean, traceable result?
```

---

## 12. Progress Log (to be filled during execution)

### Session YYYY-MM-DD — Phase 1: Publication follow-through
- [ ] T22.1.1 Review response template created
- [ ] T22.1.2 Reproducibility artifact maintained
- [ ] T22.1.3 Claim-discipline audit on final PDF
- [ ] T22.1.4 Paper commit tagged

### Session YYYY-MM-DD — Phase 2: Platform hardening
- [ ] T22.2.1 Per-package pyright configs
- [ ] T22.2.2 Lab trainer-metrics contract
- [ ] T22.2.3 Release automation dry-run
- [ ] T22.2.4 External docs refresh
- [ ] T22.2.5 Dependency/license audit

### Session YYYY-MM-DD — Phase 3: Campaign
- [ ] T22.3.1 Campaign pre-registered
- [ ] T22.3.2 Campaign executed
- [ ] T22.3.3 Analysis & report
- [ ] T22.3.4 Platform v0.2 released

### Session YYYY-MM-DD — Phase 4: Conditional (if any)
- [ ] T22.4.1 / T22.4.2 executed or deferred

---

## 13. Inherited Threads Audit (from TODO21 §12 open items)

| Item | Status in TODO22 |
|------|------------------|
| REPRODUCIBILITY fresh-clone gate | T22.1.2 — maintained continuously |
| T21.3A.9 sqlite-ledger | CLOSED in TODO21 — no action |
| Gallery lock staleness | Softened in TODO21 — no action; monitor only |
| Ruff zero findings | Maintained per-commit; repo-wide at round close |
| Ledger gate reform (bounded status) | Deferred — ledger feature work, non-goal |
| Phase 4 hardware probes | T22.4.2 — conditional on reviewer demand |
| T21.3.2 per-package pyright | T22.2.1 — **closure here** |
| T21.3.4 Lab trainer-metrics | T22.2.2 — **closure here** |

No un-owned work carries forward.