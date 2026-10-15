# TODO64: Finish the Autonomous Scientific Loop — Remaining Work from TODO63

**Status:** Phase A complete (F0, F0c done). Phase B in progress (exploit-axis selection, S1, S2).
**Predecessor:** TODO63.md (full rationale). This doc keeps only what is *not yet done*.
**Goal:** close the gap between "the loop runs" and "the loop produces a first empirical verdict."
That means scientific validation (From-Scratch Test, First Governed Claim), cross-domain coverage,
statistical rigor, and the hygiene/instrumentation that makes it trustworthy at scale.

> Line numbers are deliberately omitted — they rot. References are module/function names.

---

## 1. Done (so "remaining" is unambiguous)

| Workstream | State |
|---|---|
| A/G/H/N — engine-driven `loop` CLI; no shell drivers | ✅ |
| B — statistical promotion ladder (payload-key bug fixed) | ✅ caller + gate |
| C — online baselines (store lookup + `check_or_run` discovery) | ✅ |
| D — multi-objective Pareto (`multi_objective.compute_pareto_frontier`) | ✅ |
| E — multi-objective proposer + ICU-guided search | ✅ core |
| F — `task_registry` (26 tasks / 6 domains) + `coverage` command | ✅ registry |
| I — defect→constraint (`defect_registry` → `LegalityEngine` S4 gate; `defect list/cluster/revoke`) | ✅ core |
| J — evidence auto-population + `ModelRegistry` on PASS path | ✅ core |
| K — narrow effect lock | ✅ narrow |
| O — provenance, deterministic seeds, checkpoint, store migration | ✅ run-level |
| Phase 5 — hypotheses attached to cycles; ICU fed | ✅ core |
| Cleanup — `execution/budget.py`, `cost_tracking.py`, `promotion.promote_run` deleted | ✅ partial |
| **F0 — Per-domain objective emission (perplexity, f1_score, bleu_score, mean_reward)** | ✅ **Phase A complete** |
| **F0c — Baseline metric-name mismatch fix** | ✅ **Phase A complete** |

---

## 2. Scientific payoff (highest priority — the reason the loop exists)

### S1 — From-Scratch Test (DoD §6.12)
Loop rediscovers the known Pareto-optimal region (`tile_mesh` + local credit) on cheap tasks
without seeded priors.
- Scaffolded in `tests/acceptance/test_todo63_scientific_validation.py::TestFromScratchTest`; **not
  verified green**.
- `test_pareto_frontier_includes_local_credit` only `print`s — **make it a hard assertion** or it is
  a comment (a lock whose fixture cannot fail is a comment).
- Blocked by weak exploit-axis selection (§6).

### S2 — First Governed Claim (DoD §6.13)
One preregistered cross-domain hypothesis with a definitive verdict, exported at the CEEC boundary.
Candidate `H1_credit_efficiency`.
- Scaffolded in `...::TestFirstGovernedClaim`; **not verified green**.
- **Risk:** per-cycle single-task evaluation starves cross-domain hypotheses — accumulate records
  across cycles before testing.
- **Boundary:** the loop exports a `ceec_link`/`StatisticalResult`; it must *not* render the verdict
  (CEEC owns the decision).

---

## 3. Cross-domain coverage gap (DoD §6.1 — currently 4/6 domains)

### F0 — Per-domain objective emission (**[BUILD]** — highest leverage) ✅ **DONE**
`MEASURED_OBJECTIVES` now measures `val_acc`/`val_loss`/`val_ppl`/`test_acc`/`test_loss`/`f1_score`/`perplexity`/`bleu_score`/`mean_reward`.
- Root cause fixed: `HISTORY_METRICS` now includes `val_ppl`; `Task.evaluate()` is now called by
  `evaluate_cell` and its metrics are merged into the payload.
- Deliverable: emit `perplexity`, `f1_score`, `bleu_score`, RL `mean_reward`; registered in `MEASURED_OBJECTIVES`.
- **Lock:** a coverage cell may not be populated unless the corresponding domain objective is
  measured.

### F0b — Normalization before Pareto
Normalize per task against that task's online baseline (ruler-relative) via
`task_registry.normalize_per_task_baseline` + `ObjectiveSpec.normalizer`. Until a task has a
baseline, the frontier is within-task only and the report must say so.

### F0c — Baseline metric-name mismatch (real bug) ✅ **DONE**
`BaselineRegistry._aggregate_metrics` and `compute_ruler_metrics` now use payload keys (e.g., `val_acc`, `val_ppl`)
consistent with `MEASURED_OBJECTIVES`. Fixed classification so task metrics no longer land in `cost_metrics`.

### Coverage-driven scheduling (small)
Un-measured `(task × primitive)` pairs get priority; cheap tasks get more cycles; expensive ones
budgeted from measured walltime. `TaskRegistry.measured_objectives()`/`unmeasured_objectives_report()`
already exist.

---

## 4. Statistical rigor (B) — anti-winner's-curse

- Derive gate thresholds + seed counts from a **power analysis over measured seed variance**
  (`analysis/seed_variability.py`), not fixed `2·SE`.
- **Discovery-seed vs confirmation-seed separation** (or multiplicity control): promote only on
  fresh seeds. **The infrastructure already exists** — `registry/seed.py::SeedContext` exposes
  `discovery_seeds`/`confirmation_seeds`, but `loop.py` only calls `cycle_seed`. Wiring it is the
  deliverable.
- **L2 hardening:** require *every* confirmation seed to beat the baseline at the replay rung, not
  just the mean.
- Populate `power_achieved` in `loop._test_hypothesis` (currently unset).

---

## 5. C12 — Ruler geometry fallback

The backprop ruler cannot run on `tile_mesh` (D1 shape mismatch is handled by a *rejection* in
`ontology/system.py`, not a fix). Define an equivalent-capacity fallback geometry, record the
substitution, and have the evidence state the limitation rather than imply a matched-geometry claim.

---

## 6. Registry / checkpoint hardening

1. **Single long-lived `ExperimentRegistry`.** The loop opens a fresh registry (new `run_id`) per
   cycle, so checkpoint commits don't span the loop; loop-level resume is still `checkpoint.json`.
   `create_registry` is unused. One registry across cycles (or a loop-cycle store row).
2. **Exact seed enumeration.** `ExperimentRegistry._collect_all_seeds` estimates (`n_seeds * 10`),
   so provenance `seed_list` is approximate. Enumerate the real `CellSeedPlan.all_seeds()`.
3. **`get_task_objective_set` unused** by the driver (it reads `TaskRegistry.measured_objectives()`).
   Route through it or mark superseded.
4. **Exploit-axis selection is weak.** With few cells all are non-dominated, so "exploit" ≈ full
   space. Add crowding / top-*k* front selection — this gates S1.

---

## 7. Instrumentation (K) + allocator

- **Repo-wide effect lock:** every declared hyperparameter must change the output or be explicitly
  declared inert for that primitive (generalize the one narrow lock).
- **Silent-drop detector:** any swept value dropped by composition records a defect.
- **Per-stage timing:** instrument the pipeline stages (only cell-level `CellTiming` exists today);
  a stage over threshold becomes a defect.
- **Allocator:** `EvidenceDrivenAllocator` is effectively unwired — `_run_allocator` is a no-op and
  S10 calls `propose(candidates, [], ...)` with empty records, so `S10_DECIDE.promotions` is always
  `[]`. Either feed it real records or delete it and its S10 branch.
- **De-duplicate stability math:** `analysis/nonnormality.py`, `analysis/energy_landscape.py`, and
  `kernel/evaluate.py` re-derive ρ/σ_max/Jacobian/attractors that `packages/stability` already
  exposes (`spectral_radius`, `lyapunov`, `settling`, `basin`). Call the package.

---

## 8. Self-validation (M) — beyond the shipped M-lite

- **Gate-calibration feedback:** flag non-discriminative rungs (>90% too loose, <5% too strict) and
  suggest a threshold change (counts are already in the loop report).
- **Drift detection:** re-run top configs; a shift beyond the seed band on unchanged hardware raises
  an environment-drift defect.
- **Metric-coverage warnings:** report any primitive lacking stability/energy/parity metrics (the
  M-lite report lists unmeasured *objectives*; this adds per-primitive metric gaps).
- **`capabilities` command:** a truthful "what it can / cannot validate." None exists today
  (`comp conformance --list-only` is unrelated).

---

## 9. Regression checks for the systemic risks found this session

1. **Gate/measurement:** assert `gate_values` is non-empty on a known-good cell (the payload-key bug
   made L2 unreachable).
2. **Baseline hyperparameter names:** audit `STANDARD_BASELINES` against
   `seed_registries._accepted_params` (axis-prefixed names required).
3. **CLI reachability:** CI check that every surface command appears in `cli/__main__._SUBCOMMANDS`
   (`loop`/`baseline`/`coverage`/`defect` were once untypeable).
4. **Baseline ruler discovery:** keep a test that the gate runs when the store lacks a ruler (do not
   regress to a silent pass).

### Defect-loop (I) follow-ups
- **Compatibility matrix for policy-aware sampling** (defect consumer #3 from TODO63 §4 I): constraints
  should also feed a compatibility matrix the proposer can sample against, not only the S4 gate.
- **`defect revoke` confirmation:** revoking a constraint should re-run the affected proposal to
  confirm the region is safe again (today revoke only removes the row).

---

## 10. Orphaned / duplicated modules (found by re-audit — additional work)

Complete-but-uncalled code is the repo's recurring failure mode. For each: **wire it or delete it.**

| Item | What / where | Action |
|---|---|---|
| Reproducer machinery | `evidence/failure.py::save_reproducer`, `FixLinkageStore`, `Reproducer`; `analyze_store_failures` reached only via uncalled `DefectRegistry.get_digest` + a dead CLI import | Wire under `defect`/`report`, or delete |
| Analysis orphans | `analysis/gradient_stats.py`, `analysis/weight_evolution.py` — no caller anywhere; many exported symbols unused; **no test imports the analysis package** | Delete/wire; add a report-section lock |
| HTML report dup | `surface/report.py::generate_html_report` orphaned vs live `reporters/html.py::generate_html_report`; private Pareto impls duplicated across `reporters/*`, `optimization/multi_objective.py`, `analysis/pareto_analysis.py` | Keep one |
| Status/procedures | `evidence/status.py`, `evidence/procedures.py` — fully orphaned (register but nothing reads) | Wire or delete + prune lazy exports |
| Surface ops/service | `surface/operations.py`, `surface/service.py` — `RunController`/`ServiceLoop` only tests; no CLI `service`/`steer` | Wire or delete |
| Codegen | `surface/codegen.py` only run by `test_codegen_drift_lock`; `surface/evidence.py::evidence_for` dead without it | Wire into pre-commit/CLI, or delete |
| Conformance dup | `surface/conformance.py::check_conformance` unused; CLI reimplements via `_check_capability` | Point CLI at the harness |
| Reporter dead exports | `reporters/{html,json}.*_from_db`, `surface/report.load_export_bundle`, `surface/profiles.question_first` — no prod caller | Remove or wire |
| SurrogatePolicy | `learning/surrogate.py` — interface mismatch (`propose(n, dict)` vs `Policy.propose(ProposalContext)`); `create_surrogate_policy`/`create_tpe_policy` zero callers; `predict_with_grad` returns zeros | Implement the Policy protocol, or delete; keep `ModelBasedPolicy` |
| Third hypothesis notion | `learning/reasoning.py` — orphaned; `SystemContext.reasoning_store` never set | Delete or wire |
| Campaign DSL | `design/campaign_dsl.py` — orphaned; overlaps `execution/campaign.py::CampaignSpec`; duplicates power analysis | Delete or route into CLI |
| Dead CLI + runners | `computronium/experiment/cli/` package and `scripts/comp.py` are the only callers of `runners/{ablation,scaling,comparison,replay}.py` (zero tests); `comparison`/`replay` duplicate `statistical_promotion`/`replay_survives` | Delete the dead CLI + runners, or port onto `promote_with_stats` |
| Legality stubs | `legality/engine.py::is_cell_suppressed` returns `False` (unimplemented); `legality/classify.py::DEFECT_REGISTRY` duplicates the inline checks in `ontology/system.py::SystemConfig.validate` | Implement / single-source the void table |
| Power analysis ×4 | `HypothesisSpec.required_sample_size`, `DesignSpec.required_sample_size`, `statistical_promotion.compute_required_seeds_power`, and byte-identical `power_for_two_sample` in `core/statistics.py` + `validation/statistics.py` | Unify |
| Placeholder quality | `quality/gates.py::_check_accessibility` always emits info; `legality/dsl.py::eval_eventually` ignores step context | Fix or mark |
| Placeholder locks | `test_legality_boundary_lock` (4 tests vacuous until DECLARED constraints land); `test_u3_multi_round_with_allocator` asserts nothing about the allocator; `test_wp10_learning_integration_lock::test_closed_loop_mechanics` "just verifies it runs" | Strengthen or delete |

Also still open from TODO63's register: `EvidenceDrivenAllocator`, `MultiprocessBackend`/`DDPBackend`,
two round loops, triplicated hardware-fingerprint logic, two `EnvironmentSnapshot` classes,
`schema/primitives.py`, `schema/builder.py`.

---

## 11. Deferred / anti-goals (do not start without a concrete need)

- **L — Terminal TUI.** Web dashboard accessors are private async FastAPI methods; needs a
  data-layer refactor. Revisit only if demoing.
- **`campaign_queue` as the loop driver.** Simpler `PipelineRunner`-per-cycle is correct; adopt only
  for multi-campaign resource sharing.
- **Ray/SLURM/`DDPBackend`.** Local/Multiprocess suffice for cheap tasks.
- **`SystemConfig.validate` codegen from defects.** The `LegalityEngine` mask gives the signal;
  auto-patching is a separate pass.

---

## 12. Assumptions to verify before `--budget 24h`

| Assumption | Risk | Check |
|---|---|---|
| `n_seeds=1` works with statistical gates | gates silently fail | `comp loop --cycles 1 --profile quick-verify --n-seeds 2` |
| Exploit axes = frontier union at n≈20 | no exploitation signal | frontier size vs. search space |
| Baseline discovery after the pipeline | added latency | time the gate |
| Dry-run ≈ real execution | misses OOM/shape errors | one real `--cycles 1` |
| Per-cycle registry is correct | provenance seed_list approximate | §6.2 |
| Per-cycle single-task hypothesis eval | cross-domain hypotheses starve | §2 S2 |
| DuckDB WAL concurrency | lock conflicts | run CLI + pytest together |

**Cost-model contamination (critical):** objectives *are* `energy_per_step`/`walltime_total`/`flops`.
Checkpoint I/O must not bias them — checkpoint only when `--checkpoint-every-n-cycles > 0` and cycle
time ≫ interval; for `quick-verify` **never** checkpoint.

---

## 13. Definition of Done — status

| # | Criterion | Status |
|---|---|---|
| 1 | All 6 domains swept | 🔄 4/6 — §3 |
| 2 | Online baselines; Δ per promotion | ✅ |
| 3 | Ladder + statistical gates | ✅ |
| 4 | Auto-promote gate-passers | ✅ |
| 5 | Declared objective set (≥3) | ✅ |
| 6 | Learns from defects; digest | 🔄 verify e2e |
| 7 | Terminal TUI | ⏸ deferred |
| 8 | Evidence per run w/ limitations | 🔄 verify via S1/S2 |
| 9 | Self-report (calibration, drift, gaps) | 🔄 M-lite done; §8 |
| 10 | CLI-only; zero `run_*.sh` | ✅ |
| 11 | No `KNOWN_GOOD`/`FIX_HINTS` | ✅ |
| 12 | **From-Scratch Test** | ❌ §2 S1 |
| 13 | **First Governed Claim** + CEEC export | ❌ §2 S2 |
| 14 | Provenance; crash resume; replay | ✅ run-level; §6.1 loop-level |
| 15 | **Per-domain objectives emitted (perplexity, f1_score, bleu_score, mean_reward)** | ✅ §3 F0 |
| 16 | **Baseline metric-name mismatch fixed** | ✅ §3 F0c |

---

## 14. Execution schedule

Phases are ordered by dependency. Each ends in a dry-run or one short run; no full-suite during
development. Item IDs reference the sections above.

| Phase | Work | Depends on | Exit criterion |
|---|---|---|---|
| **A. Honest measurement** | F0, F0b, F0c, R1, R2 | — | ✅ **COMPLETE** — `coverage` shows language/RL/graph with their own metrics; baseline Δ computes for language task; gate_values regression passes |
| **B. Scientific acceptance** | §6.4 (exploit selection), B2 (discovery/confirmation seeds), S1, S2 | A | both acceptance tests green; hypothesis gets CONFIRMED/REJECTED; CEEC export consumed |
| **C. Rigor & self-awareness** | B1 (power/multiplicity), M1, M2, M3, R3 | B | noisy cell not promoted; `capabilities` truthful; CLI-reachability CI green |
| **D. Instrumentation & integrity** | K1, K2, K3, allocator (wire/delete), stability dedup | A | per-stage timings queryable; allocator either promotes or is gone |
| **E. Hygiene / consolidation** | §10 table + remaining §1-register items; lock hygiene | — (round close) | orphans gone; ruff/pyright clean on changed; shard runs green |
| **F. Scale** | §12 assumptions | A–D | one `--cycles 2 --n-seeds 2` clean; then `--budget 24h` |

**Suggested order if serialized:** A → B → (C ∥ D) → E → F. E is independent and can ride any round
close.

---

## 15. Next action

1. **Phase B** — exploit-axis selection (§6.4), then S1 (From-Scratch Test), then S2 (First Governed Claim).
2. **Phase C** — power/multiplicity analysis (B1), gate-calibration feedback (M1), drift detection (M2).
3. Fold §10 deletions into the next round-close hygiene commit.
4. Scale to `--budget 24h` only after S1/S2 pass on cheap tasks.
