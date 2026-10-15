# TODO65 — Turn-Key Discovery Engine (v1.0)

**Status:** Terminal plan. There is no TODO66.
**Predecessor:** TODO64 (S1 From-Scratch ✅, S2 First Governed Claim ✅ — loop mechanics proven).
**Thesis:** The engine is built. It needs its built-but-unwired pieces connected, its architecture made
self-consistent, and its documentation made truthful — then an investor can point it at a configuration
and get governed results. This is a **wiring + repair** list, not a rebuild.

**Priorities (binding):** usability · purpose · architectural consistency · **preserve invested work**.
Counts are *not* a concern — they fluctuate by design (see §4: make them generated, not chased).

> `README.md` is generated from `docs/readme/*.md` + `<!-- gen:... -->` blocks
> (`docs/readme/build_readme.py`), locked by `tests/property/test_readme_build_lock.py`.
> **Never edit `README.md` directly.** It *can* be repaired: edit the snippet, regenerate, the lock passes.

---

## 0. What "turn-key" means

> **One configurable entry point: point the engine at a configuration (domains, search policy, budget,
> fidelity, objectives, hypothesis, device), and it explores the space intelligently, produces
> governed claims, exports them at the CEEC boundary, and writes a reproducible report.**

**Intelligible search, not brute force.** The engine covers the possibility space by *making decisions*
— proposal policies, DoE, a learnability metamodel, successive-halving allocation, Pareto exploitation —
not by running every (task × primitive) pair. "Support all possibilities" = every possibility is
**reachable and composable**, and the search can be **configured to prefer any region** — never that all
are executed.

Three invariants: **Reachable** (§3.W5) · **Navigable** (§3.W1) · **Accountable** (§3.W3).

**Surface (code-authoritative):** schedulable tasks across `DomainType` = vision, language, rl, graph,
tabular, memory, scientific; 6 axes — substrate, geometry, dynamics, plasticity, credit, update.

---

## 1. Principles (binding)

1. **Preserve invested work.** Prefer *wire* over delete. Delete only true duplicates and rot; when code
   is retired, its **plan survives in §5 (Readiness Ledger)**. Nothing we invested in is lost — at worst
   it becomes a ledger row with its readiness degree.
2. **Intelligible, not exhaustive.** No step enumerates the space.
3. **Architectural consistency.** One source per fact; declarations derived, not duplicated; the README
   is a *projection* of the code, never a second copy of its numbers.
4. **Config-driven.** Behaviour selected by a profile/config, not by editing code.
5. **GPU-first, CPU-complete.** `auto` → `cuda` when present; CPU stays fully functional (reconciles
   README "GPU optional" with "GPU default": prefer the accelerator *when present*).
6. **Truthful surfaces.** README, coverage, provenance state measured reality.
7. **Fast-First.** Per commit: `ruff format && ruff check --fix && pyright <changed> && pytest tests/unit/ -q` (≤60 s).

---

## 2. Built machinery (audit) — nothing overlooked

Decision: **W** = wire · **E** = expose via config · **K** = keep as-is · **R** = retire code, plan
kept in §5.

| Area | Module · key symbols | Decision |
|---|---|---|
| Loop + stages | `registry/loop.py::LoopDriver/LoopConfig`, `execution/pipeline.py`, `execution/stages_impl.py` (S1–S11) | **K** |
| Proposal policies (8) | `execution/policy.py`: Stratified/RoundRobin/Uniform/ModelBased(Optuna)/Evolution/Synthesis/StrategyProgression/TrainerDriven | **K** / E |
| DoE | `execution/contrast_design.py`: OFAT, fractional/full factorial, Plackett-Burman | **K** |
| Learnability metamodel | `learning/icu.py::ICUModel` | **K** (`--use-icu-guided`) / E |
| Search space + void cache | `kernel/search_space.py::SearchSpace`, `VoidCache`, `iter_candidates`, `narrow_domain` | **K** |
| Candidate stream + adaptive batch | `execution/stream.py::CellStream`, `execution/batch_sizer.py::BatchSizer` | **K** |
| Multi-objective | `optimization/multi_objective.py`: NSGA-II, crowding, hypervolume, scalarize | **K** |
| Promotion ladder | `execution/statistical_promotion.py::promote_with_stats` + gates + power | **K** |
| **Evidence-driven allocator** | `execution/allocator.py::EvidenceDrivenAllocator` | **W** — never instantiated; S10 always `[]` |
| Budget planning | `execution/adaptive_budget.py::BudgetPlanner` | E (CLI-only) |
| Baselines / ruler | `registry/baseline.py::BaselineRegistry/BaselineGate`; `compute_ruler_metrics`, `normalize_per_task_baseline` | **K** / **W** (two orphaned — F0b normalization) |
| Hypotheses · defects · legality | `design/hypothesis.py`; `registry/defect_registry.py`; `legality/{engine,classify,dsl}.py` | **K** |
| Evidence store/claims/models | `evidence/{store,artifacts,claims,limitations,failure,model_registry,significance,statistics,protocol}.py` | **K** |
| Three-tier status + procedures | `evidence/status.py`, `evidence/procedures.py` | **W** — `schema/record.py::Status` carries their `assessment_procedure_*` fields |
| **CEEC boundary** | `packages/ceec-core`; loop `Status.ceec_link` always `None` | **W** — populate `ceec_link` + export to the **standalone** ledger |
| Provenance / seeds / checkpoint | `registry/{provenance,seed,checkpoint}.py`, `ExperimentRegistry` | **K** |
| Reporting · coverage | `surface/report.py`, `reporters/{html,json}.py`, `templates/report/`, `registry/task_registry.py`, `comp coverage` | **K** |
| Question-first entry | `surface/profiles.py::question_first` | **W** — documented U1/WP11.5 kernel entry, test-locked; not dead |
| Store migration | `evidence/store.py::migrate_legacy_store`, `bootstrap_stores` | **R** (kept as ledger row: legacy-store migration) |
| Campaign queue | `execution/campaign_queue.py` | **R** (ledger row: multi-campaign resource sharing) |
| Dead CLI + runners | `experiment/cli/`, `experiment/runners/*` | **R** (ledger row: ablation/scaling/comparison/replay runners) |
| Orphaned analysis | `analysis/gradient_stats.py`, `weight_evolution.py` | **W** if cheap, else **R** (ledger row) |
| Orphaned schema | `schema/{builder,primitives,experiment_spec}.py` | **R** (ledger row) |
| Orphaned learning | `learning/reasoning.py`, `benchmark.py`, `SurrogatePolicy`/`create_*` | **R** (keep `GaussianProcessSurrogate`, wired via ICU) |
| Orphaned surface | `surface/{service,operations,codegen,evidence}.py` | **W** (service/ops) or **R** (codegen/evidence = dev tooling) |
| Cost trackers | `kernel/resources.py::CostTracker/CampaignCostTracker/estimate_campaign_cost` | **R** (ledger row) |

**R = retire the code, keep the plan.** Each R row appears in §5 with its readiness, so the investment
is preserved as intent even when the code leaves the tree.

---

## 3. Essential wiring (the gap to turn-key)

### W1 — One config surface (E)
Expose the built machinery through the profile/config: search `policy`, `use_icu_guided`,
`task_schedule`/domains (**remove the hardcoded `task="digits"`**), objectives, fidelity ladder, budget,
device. Two entries, one config: **single-question** (`question_first` → `RunSpec`, the documented U1
flow) and **continuous** (`LoopDriver`). They must not drift.

### W2 — Wire `EvidenceDrivenAllocator` (W)
Instantiate in the pipeline (`PipelineConfig.allocator`) so S10 produces real `S10_DECIDE.promotions` —
successive-halving allocation is the adaptive-search core; currently dead code.

### W3 — CEEC boundary: populate `ceec_link` + export (W) — *the publishable-result gap*
Export `StatisticalResult`s to `packages/ceec-core` and record the returned link in `Status.ceec_link`.
CEEC owns the decision; the package stays locked against importing computronium (`tests/test_ceec_boundary.py`).
**Export ≠ integrate** — this is the "future use" the README already reserves.

### W4 — Evidence status into the report (W)
Wire `evidence/status.py` + `procedures.py` so the record's `assessment_procedure_version`/`_hash`
fields are actually stamped — the WP5 three-tier model (observations → assessments → claims).

### W5 — Reachability locks (W) — the *intelligible* form of "cover all"
- **Composability:** generalize `tests/property/test_composer_registry_coverage_lock.py` to all six
  registries (`AXES_REGISTRIES`): every registered primitive composes.
- **Task resolvability:** every `SUPPORTED_TASKS` task resolves geometry + constructs.
- **Device:** `auto` → `cuda` on GPU; CPU parity on a cheap subset.
A registry key that cannot compose is a defect. No matrix of training runs.

### W6 — Ruler-relative normalization (W)
Wire `compute_ruler_metrics` + `normalize_per_task_baseline` into the Pareto path (TODO64 F0b).

### W7 — Architectural consistency & README repair (W)
Repair is mechanical: edit `docs/readme/*.md`, regenerate, lock passes. The conflicts to resolve are
**semantic, not numerical**:

| Conflict | Where | Resolution |
|---|---|---|
| README contradicts itself on measurement | `evidence.md` / `kernel.md` ("evaluator is a placeholder" vs "measurement is real") | State it once: `task.evaluate()` **is** called (`kernel/evaluate.py`; F0 landed). Delete the stale caveat. |
| Domain list disagrees with code | `cheatsheet.md` ("lm/timeseries") vs `DomainType` (`language/memory`); `domains/timeseries.py` exists but is unregistered | Make `DomainType` the single source; **register `timeseries`** (invested code) or document it as non-schedulable. README derives. |
| Measurement declarations disagree | `OBJECTIVES` vs `MEASURED_OBJECTIVES` vs `ObjectiveSpec.is_measured` vs generated `docs/generated/objectives.md` | One derives from the others; the generated doc agrees with code (§4). |
| "L" means three things | L1–L5 verification · L1–L7 property locks · L0/L1/L2 fidelity | Disambiguate the labels in `cheatsheet.md`/`validation.md`. |
| Volatile counts drift | `cheatsheet.md` hand-writes subcommands/objectives/priors/constraints/methods | **Move them into `<!-- gen:... -->` blocks** derived from the registries (§4). |
| Two documented entry flows | `question_first` (single) vs `loop` (continuous) | Document the relationship; both read one config (W1). |

---

## 4. Make the README self-consistent by construction

The cheatsheet hard-writes numbers that drift — the flaw, not the numbers. `build_readme.py` already
substitutes generated blocks (`cli_table`, `policy_table`, `demo_table`). **Add generators** for the
counts (`ontology_counts`, `kernel_counts`, `store_facts`) so the README is a *projection* of the
registries. Then no count is ever chased again, and `test_readme_build_lock` enforces consistency.

The one semantic knot to untie first: **what does "measured" mean?** `MEASURED_OBJECTIVES` says "has a
payload key"; `ObjectiveSpec.is_measured` / `objectives.md` say something stricter. Pick one definition,
make the other derived, and let README + the generated doc read from it. (Everything else in §3.W7 is
mechanical once this is decided.)

---

## 5. Readiness Ledger — everything invested, at its true readiness

Nothing developed is dropped without a row here. Tiers: **Live** (loop or `comp` command) ·
**Built-unwired** (code + tests, no user path → §3) · **Designed** (spec/partial) · **Planned** (intent) ·
**Retired** (tried; finding kept).

**Built-unwired → wire in §3** | allocator · status/procedures · question_first · CEEC bridge ·
ruler normalization (`compute_ruler_metrics`, `normalize_per_task_baseline`) · `adaptive_budget` ·
`campaign_queue` · store migration · `experiment/cli` + `runners/*` · `surface/{service,operations,
codegen,evidence}` · `analysis/{gradient_stats,weight_evolution}` · `learning/{reasoning,benchmark}` +
`SurrogatePolicy` · `schema/{builder,primitives,experiment_spec}` · `kernel/resources` cost trackers.

**Designed (spec'd, not built):** M1 gate-calibration · M2 drift detection · M3 metric-coverage
warnings · `capabilities` command · per-stage timing + over-threshold defect · repo-wide effect lock ·
silent-drop detector · C12 ruler-geometry fallback · `defect revoke` re-probe · policy-aware
compatibility-matrix sampling · `SystemConfig.validate` codegen from defects.

**Planned (intent, no code):** 7-domain task expansion (cifar100, svhn, wikitext2, penn_treebank,
mountain_car, lunar_lander, diabetes, california_housing, ett_h1, PDE suites) · physical-hardware
validation (memristive/neuromorphic/optical/quantum) · Ray/SLURM · DDP at scale · terminal TUI ·
`campaign_queue` as loop driver · full CEEC integration · `question_first` literature/reasoning store.

**Retired (finding kept):** E1 deep chaotic unfolding — **falsified** with a mechanism boundary
(composition-error compounding); older "ρ(J)=estimator" claims (see `docs/CORRECTIONS.md`); legacy
`experiment/cli` runners.

This ledger is the durable answer to "what could we eventually develop?" — updated, never summarized
away.

---

## 6. Trust & rigor (prerequisites for a claim)

**C0 — single-source the trust math.** `power_for_two_sample` (`core/statistics.py` vs
`validation/statistics.py`), `required_sample_size` (4 sites), Pareto (canonical
`optimization/multi_objective.py` vs private impls in `reporters/*`, `analysis/pareto_analysis.py`),
and stability: `packages/stability` is canonical, `computronium/stability/` is a **Rule-6 adapter**
(keep), but **`kernel/evaluate.py` re-derives ρ/σ_max locally** — repoint at the package.

**C1 — discovery/confirmation seed separation.** `registry/seed.py::SeedContext` exposes
`discovery_seeds`/`confirmation_seeds`; `loop.py` uses only `cycle_seed`. Promote **only on fresh
confirmation seeds**; **L2 requires every confirmation seed to beat baseline**; thresholds from the C0
power analysis, not fixed `2·SE`. A verdict reports `power_achieved`, so REJECTED means "no effect", not
"underpowered".

---

## 7. The exit test — a merge gate, not a ceremony

`tests/acceptance/test_v1_exit.py`, run **once** (<10 min; faster on GPU):
1. Config selects a cross-domain schedule + policy; the loop honours it.
2. Reachability locks pass (W5). 3. S10 promotions non-empty (W2).
4. A claim is exported to the standalone CEEC and `ceec_link` is recorded (W3).
5. Report artifacts: per-domain objectives, baseline-relative Pareto (one impl), evidence + limitations,
   three-tier status, enumerated provenance, recorded defects. 6. `test_readme_build_lock` green (W7).

Exhaustive whole-space training is never a gate; it is a scheduled campaign (`claim` profile, `--budget`).

---

## 8. Schedule (fast-first)

| Phase | Work | Daily gate | Once-gate |
|---|---|---|---|
| **W1** | config surface | profile-selection unit test | any domain/policy honoured |
| **W2** | allocator | allocator unit test | promotions non-empty |
| **W3** | CEEC export | export unit test | claim reaches CEEC, link recorded |
| **W4** | evidence status → report | report-section test | — |
| **W5** | reachability locks | composability + resolvability | all primitives compose |
| **W6** | ruler-relative Pareto | normalization unit test | — |
| **W7/§4** | consistency + generated README | `test_readme_build_lock` | README truthful |
| **C0/C1** | trust math + seeds | `test_seed_separation.py` | — |
| **R** | retire (§2 R → §5 rows) | suite green | — |
| **exit** | `test_v1_exit.py` | — | **run once, tag v1.0** |

Per commit: `ruff format && ruff check --fix && pyright <changed> && pytest tests/unit/ -q`. Long runs:
`nohup uv run python … > logs/<name>.log 2>&1 &`.

---

## 9. Definition of Done — v1.0

- [ ] One config selects domains, policy, budget, fidelity, objectives, hypothesis, device; the loop honours it.
- [ ] Every registered primitive composes; every task resolves; `auto` → GPU when present, CPU complete.
- [ ] `EvidenceDrivenAllocator` wired — S10 promotions real and evidence-driven.
- [ ] Governed claim exported to the standalone CEEC; `ceec_link` recorded; boundary intact.
- [ ] Evidence three-tier status stamped into records/report.
- [ ] `question_first` and the loop share one config surface; the relationship is documented.
- [ ] README self-consistent **by construction** (generated counts; one "measured" definition; one domain source).
- [ ] One power fn, one Pareto impl, one stability source; promotion on fresh seeds only; verdict reports power.
- [ ] §5 Readiness Ledger complete; every `R` row present; no complete-but-uncalled module unaccounted for.
- [ ] `test_v1_exit.py` green **once**.
- [ ] **This file is deleted when v1.0 is tagged.** There is no TODO66.

---

## 10. Stop conditions / anti-goals

- **Never** enumerate the space. If a step runs "every pair", the search machinery is being bypassed.
- **Never** lose invested work silently — retire to a §5 ledger row, never just delete.
- **Never** hand-write a count in README; generate it.
- **Never** exclude a registered primitive — make it compose or fix its loader.
- **Never** edit `README.md` directly; edit `docs/readme/*.md`.
- **Never** `pytest tests/`; never re-run a green shard; never `--lf`/`--ff`.
- **Never** hinge on a >10-min gate. **Never** open TODO66.
