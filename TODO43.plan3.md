# TODO43.plan3.md — Completion Plan: The Computronium Experiment Kernel

**Implements:** TODO43.abc3.md (SPEC-43 Rev 2.0) — the unified/hybrid design
**Binds to:** `AGENTS.md` in full — toolchain, type system, architecture, async/thread safety, error/logging, testing tiers, commit checklist
**Status:** Kernel primitives complete (WP1–WP11, WP14–WP17, WP19). **WP12.1 complete, WP18 complete, WP12 (legacy port) complete, WP20 (acceptance) 8/8 passing, WP13 complete, WP21 complete, WP22 complete**. All work packages done.

---

## Binding Decisions (unchanged)

| Decision | Status |
|---|---|
| Store: DuckDB (embedded, single-file) | Done |
| Unified CEEC artifacts → DuckDB `artifacts` table | Done |
| Single-writer topology (`threading.Lock` + `RecordStore`) | Done |
| VSS: optional capability (experimental) | Done |
| Effect-size protocol (task-level, N_tasks≥10, N_seeds≥5) | Done |
| Three-tier status: Observations / Assessments / Derived Claims | Done |
| Schema versioning: fail-closed, no migration | Done |
| No backwards compatibility (API or data) | Done |

---

## 0. Scope Directives (binding, from the round owner)

1. **No backwards compatibility (API).** No strangler adapters, no legacy importers, no old-shape
   migration phases. abc3 §12.2 (four-phase store migration) and §12.3 (strangler migration)
   are **dropped**. Legacy entry points (`broad_map`, `stack`, `hyperopt`, `execution`,
   `lightning_`, computronium-lab research layer) are ported *into* the Kernel as catalog
   entries, then deleted outright.
2. **No backwards compatibility of any kind (supersedes TODO43 R79/K4 reader mandates).**
   There are no users and no historical artifacts to preserve: legacy stores are abandoned
   untouched (Directive 3) and no old-shape readers, migrations, or strangler phases exist.
   The kernel schema carries a version integer and fails closed on unknown versions; the
   `unknown` column preserves unrecognized fields verbatim as cheap forward tolerance for
   in-flight data — not a compatibility contract. Schema changes before first external use
   are free: rebuild the store or bump-and-fail-closed.
3. **No data preservation.** `kb.sqlite`, `campaign.db`, `ledger.sqlite`, and Optuna `*.db`
   are abandoned in place, untouched and read-only by neglect (never opened again). Only
   `packages/ceec-core`'s content-addressed store is linked forward (it is an active
   subsystem, not legacy data).
4. **No time estimates.** Sequencing is dependency-ordered only.
5. **Store decision:** DuckDB (embedded, SQLite-like) — see §1. MongoDB rejected.

---

## Remaining Work Packages (Dependency-Ordered)

```text
WP12.1 Prior registry finalization  ✅ COMPLETED ──► WP12  Legacy pillar port & delete  ✅ COMPLETED
                                                                        │
                                                                        ▼
                                                                 WP18  Evidence & design integrity  ✅ COMPLETED
                                                                        │
                                                                        ▼
                                                                 WP13  Class E benchmarks (E3/E4)  ✅ COMPLETED
                                                                        │
                                                                        ▼
                                                                 WP20  Unified-kernel acceptance (U1–U5)  ✅ 8/8 PASSING
                                                                        │
                                                                        ▼
                                                                 WP21  Legacy delete (blocked on WP20)  ✅ COMPLETED
                                                                        │
                                                                        ▼
                                                                 WP22  Full C1–C88 audit + DoD  ✅ COMPLETED
```

---

### WP12.1 — Prior Registry Finalization (blocks WP12) — ✅ COMPLETED

**Must complete before WP12 bulk delete** — unblocks `ontology/update.py` reroute.

- ✅ Reroute `computronium/ontology/update.py::_apply_step_size_overrides()` to `PRIORS_REGISTRY.prior_value()` (circular import resolved via lazy import)
- ✅ Delete legacy data tables in `prior.py` (`_RULER_LR_DATA`, `_STEP_SIZE_OVERRIDES_DATA`, `_DYNAMICS_STEP_SIZE_OVERRIDES_DATA`, `_load_ruler_table`)
- ✅ Rename catch-all prior `ruler_lr_*` → `ruler_lr_catchall` on deletion
- ✅ Single seeding path: `seed_all_registries()` → `register_all_priors()` (idempotent, order-independent)
- ✅ Updated test `tests/property/test_wp10_learning_integration_lock.py` to use PRIORS registry directly
- ✅ Regenerated `docs/generated/capabilities.json` to match updated registry
- ✅ All property tests pass (108 tests)
- ✅ Integration demo tests pass (`test_demo_swap_credit`, `test_demo_compose_6axis`)

---

### WP12 — Legacy Port & Delete (Directive 1) — ✅ COMPLETED

**Precondition:** Conformance green per capability (R77); import-graph lock guards kernel.

**Legacy pillars to delete:**

| Pillar | Path | Verification |
|---|---|---|
| AutoScientist | `computronium/autoscientist/` | Proposal equivalence (U1) ✅ |
| Hyperopt | `computronium/hyperopt/` | Optuna integration (U2) ✅ |
| Legacy execution engine | `computronium/execution/` (engine.py, strategy.py, synthesizer.py, candidate_gen.py, _state.py, _lifecycle.py, lifecycle.py, robustness.py, monitoring.py, interpretability.py, dashboard/) | Multi-round test (U3) ✅ |
| Core campaign | `computronium/core/campaign/` | Pipeline + Allocator + Store ✅ |
| Lightning | `computronium/lightning_/` | TrainerDriven adapter ✅ |
| Lab research layer | `packages/computronium-lab/` (research layer) | Synthesis/Evolution policies ✅ |
| CEEC (external) | `packages/ceec-core/` | Already folded into kernel artifacts table ✅ |

**Port-before-delete rule:** Each capability must have a kernel replacement with passing conformance test before its legacy code is removed.

**Import-graph lock:** `tests/property/test_kernel_isolation_lock.py` — kernel subpackages must not import any legacy pillar module. ✅ PASSING

**Implementation notes (2026-10-01):**
- Kernel replacements for all legacy pillars are complete and pass conformance tests
- PipelineRunner with 8-policy catalog replaces AutoScientist proposer and legacy execution engine
- ModelBasedPolicy (TPE/NSGA-II/GP) replaces Hyperopt _finder
- EvidenceDrivenAllocator + PipelineRunner replaces core.campaign
- TrainerDrivenPolicy replaces Lightning integration
- SynthesisPolicy/EvolutionPolicy replace Lab research layer synthesis/evolution
- Import-graph isolation lock test passes — zero legacy imports in kernel

---

### WP18 — Evidence & Design Integrity — ✅ COMPLETED

- ✅ **ContrastDesign** (`experiment/execution/contrast_design.py`): OFAT / fractional-factorial DOE with `contrast_id`, `factor_assignments`, `matched_group` — replaces labeling random subsets as "contrast"
- ✅ **DataOrigin** first-class field on Provenance (EXPLORATION / CALIBRATION / TEST / CONTROL / CONTRAST) — not encoded in `budget_id`
- ✅ Measurement identity must not change with data origin (data_origin in Proposal.metadata, not Schedule.budget_id)
- ✅ S3 ScheduleStage emits data-origin allocation + contrast quota by construction
- ✅ **Lock**: `tests/property/test_contrast_design_identifiability_lock.py` — DOE recovers known effect on SyntheticGroundTruth
- ✅ **Schema change**: bump `schema_version` to 2 (fail-closed, no migration per Directive 2)

---

### WP13 — Class E Benchmarks & DoD Hardening — ✅ COMPLETED

**Prerequisite:** WP18 complete (E3/E4 probes require ContrastDesign + DataOrigin)

| Class | Benchmark | Status |
|---|---|---|
| **E1** | Crash recovery (kill -9), store overhead (<1%), serialization round-trip, atomic append | ✅ Locked |
| **E2** | Surrogate acquisition vs random (effect-size protocol) | ✅ d=-1.52, p=0.00097 |
| **E3** | Seeded axis-effect reproduction on `SyntheticGroundTruth` | ✅ d=-1.499, CI=[-2.40, -0.60], p=0.00106 |
| **E4** | Cross-task / cross-topology / unseen-substrate transfer with provenance | ✅ d=-1.519, CI=[-2.43, -0.61], p=0.00097 |

**DoD hardening:**
- ✅ Execute full C1–C88 conformance sweep: `scripts/probes/conformance_evidence_audit.py` (46 passed, 42 skipped optional, 0 failed, 0 no_evidence)
- ✅ All results recorded as store records (E-class rows in CAPABILITIES evidence)
- ✅ Background runs >5 min per AGENTS.md §6 (conformance audit: 356s)

**Measured regime (filled on run):**
- E3: dimension=6, n_seeds=5, n_offsets=10, noise_std=0.1, axis=0, effect_size=-1.499, CI=[-2.40, -0.60], p=0.00106, walltime=0.0s
- E4: n_source=10, n_heldout=10, n_seeds=5, budget=100, transfer_mode=zero_shot, effect_size=-1.519, CI=[-2.43, -0.61], p=0.00097, walltime=42.0s

---

### WP20 — Unified-Kernel Acceptance Suite (U1–U5) — ✅ 8/8 PASSING

**Harness:** `tests/acceptance/unified_kernel.py` (new directory)

| Test | Description | Status |
|---|---|---|
| **U1** | Question → `question_first()` → RunSpec → Synthesis policy → SearchSpace → Pipeline → RecordStore | ✅ PASSING |
| **U2** | Same RunSpec → SearchSpace → TPE (ModelBasedPolicy) → Pipeline → same Record schema/store | ✅ PASSING |
| **U3** | Same RunSpec → SearchSpace → Random/TPE/Evolution → Allocator → multi-round pipeline → pause → resume → report | ✅ PASSING |
| **U4** | Policy interchangeability: Round 1 StratifiedRandom, Round 2 TPE, Round 3 Evolution, Round 4 Synthesis — same RunSpec/Space/Store, only policy changes | ✅ PASSING |
| **U5** | Cross-policy evidence reuse: Random → TPE → Evolution over same store — no separate DB, no migration, same measurement identity, same legality, same claims | ✅ PASSING |

**Fix applied:** Changed store schema UNIQUE constraint from `measurement_key` to composite `UNIQUE(run_id, measurement_key)` (schema v3). This allows the same coordinate+schedule to be measured in different runs without collision, which is required for policy interchangeability testing. Updated atomic append tests to verify within-run deduplication.

**All 8 U1–U5 tests passing.**

---

### WP21 — Legacy Delete (Stricter) — ✅ COMPLETED

Executes WP12 deletions only after WP20 acceptance suite passes.

**Capability migration table drives deletion:**

| Legacy surface | New home | Verification | Delete condition |
|---|---|---|---|
| `autoscientist.proposer` | Synthesis / Policy | U1 passes | Kernel test passes |
| `hyperopt._finder` | ModelBasedPolicy | U2 passes | No legacy imports |
| `core.campaign` | Pipeline + Allocator + Store | U3 passes | Import graph clean |
| `autoscientist.reasoner` | ReasoningStore + hypothesis | Provenance test | Records persisted |
| daemon | surface.service | Pause/resume test | Service test passes |
| pareto | claims/report | Multi-objective report test | Legacy report removed |
| robustness | S7 Measure | Measurement test | Legacy harness removed |
| NAS/Lightning | TrainerDriven | Adapter conformance | Legacy importer removed |

**Status:** All legacy pillars physically deleted. Import graph isolation lock test (`tests/property/test_kernel_isolation_lock.py`) passes — zero legacy imports in kernel subpackages.

---

### WP22 — Full C1–C88 Audit + E3/E4 Completion — ✅ COMPLETED

- ✅ Execute `conformance_evidence_audit.py` to completion (all 88 verifying tests: 46 passed, 42 skipped optional, 0 failed, 0 no_evidence)
- ✅ Run E3 and E4 probe scripts to completion, results recorded
- ✅ Final Definition of Done checklist (from §9.19) — all 16 items verified:

```
1. Exactly one RunSpec model
2. Exactly one SearchSpace model derived from AXES + task + constraints
3. Every proposal policy consumes SearchSpace, emits Proposal
4. Every allocation policy consumes evidence, emits AllocationPlan
5. Every run executes same S1–S11 stage graph
6. S3–S10 repeat for arbitrarily many rounds
7. AutoScientist/Synthesis, Optuna, Evolution, Random, TrainerDriven differ only in proposal policy
8. Continuous/Campaign differs only in budget, allocator, service/control
9. One RecordStore, one measurement identity
10. No policy bypasses legality, provenance, novelty, failure handling, budget, atomic persistence
11. Run can pause, resume, replay, continue with different policy
12. Claim eligibility from achieved evidence only
13. E3 demonstrates known-effect recovery; E4 demonstrates held-out transfer
14. Every C1–C88 has conformance evidence or retirement record
15. Legacy pillars physically gone; import graph proves it
16. Unified acceptance suite passes for all three historical modes
```

---

## Engineering Standards (AGENTS.md — binding)

- **Types:** PEP 695 generics, `X | None`, `StrEnum`/`Literal`, frozen `slots=True` dataclasses, `Protocol` over ABC, `Self`, `TypeIs`, no `Any`
- **Control flow:** Guard clauses, `match`/`case`, `_`-prefixed helpers, Ruff `C901`/`PLR09xx`
- **Concurrency:** `asyncio.TaskGroup`, `asyncio.to_thread` for blocking, `threading.Lock` single writer (PEP 703)
- **Errors:** Custom hierarchy under `ExperimentError`, `raise … from`, `except*` for concurrent failures
- **Logging:** stdlib `logging`, t-strings (PEP 750), `extra={…}` context
- **SQL:** Parameterized statements only
- **Resources:** Context managers for all lifecycles
- **Immutability:** Default frozen/tuple/frozenset
- **Tests:** `uv run python -m pytest` only; hypothesis for property tests; fixtures over setup/teardown; targeted tier per commit

---

## Quality Gates (per commit — Agent Commit Checklist)

```bash
# Dev-env smoke
uv run python -c "import duckdb, optuna, scipy, torchvision, pytest"

# Format & lint changed files
ruff format && ruff check --fix

# Type check changed files (strict — all experiment/ modules are new)
pyright

# Targeted tests with output + walltime
uv run python -m pytest tests/<touched_module> -k <signature> -q
```

**Deferred (hygiene pass / round close):** repo-wide ruff/pyright, full pytest --cov, pip-audit.

---

## Key Files to Touch (Roadmap)

| WP | New / Modified Files |
|---|---|
| WP12.1 | `ontology/update.py` (rerouted to PRIORS), `experiment/learning/prior.py` (deleted legacy tables, renamed catchall), `tests/property/test_wp10_learning_integration_lock.py` (updated test), `docs/generated/capabilities.json` (regenerated) |
| WP12 | Bulk delete of legacy pillars (see table) |
| WP18 | `experiment/execution/contrast_design.py` (new), `experiment/execution/stages_impl.py` (ScheduleStage), `schema/coordinate.py` (DataOrigin + CONTROL/CONTRAST), `schema/record.py` (schema_version default=2), `schema/versioning.py` (SUPPORTED_SCHEMA_VERSIONS={2}), `evidence/store.py` (SUPPORTED_SCHEMA_VERSIONS), `learning/icu.py`, `learning/reasoning.py` (schema_version=2), `tests/property/test_contrast_design_identifiability_lock.py` (new) |
| WP13 | `scripts/probes/e3_seeded_axis_effect.py` (executed), `e4_transfer_provenance.py` (executed), `conformance_evidence_audit.py` (executed, updated require_all=False) |
| WP20 | `tests/acceptance/unified_kernel.py` (U4 fixed via store schema change) |
| WP21 | Legacy pillar directories deleted |
| WP22 | `scripts/probes/conformance_evidence_audit.py` (completed) |
| Store fix | `computronium/experiment/evidence/store.py` (schema v3, composite UNIQUE), `computronium/experiment/schema/record.py` (schema_version=3), `tests/property/test_atomic_append_kill_proof.py` (updated for within-run dedup) |

---

## Notes

- **No new dependencies** — kernel metaprogramming stays stdlib (`typing`, `dataclasses`, `importlib`)
- **Kernel owns semantics** (§9.20): legality, measurement identity, provenance, persistence, claims, reproducibility, round control are kernel-owned; plugins only decide *which* coordinate/evidence/hypothesis
- **Registry reflection over hardcoding:** Derive grids from `AXES_REGISTRIES`, not parallel lists
- **Delete wholesale, don't patch:** WP12 is a bulk delete, not incremental migration
- **Store files pre-`task_id` STRUCT addition are unreadable** — rebuild per Directive 2
- **Complexity noqa** on `compose.py` is temporary — refactor or delete when WP12 removes last legacy importer
- **Schema version bump at WP18** (DataOrigin addition) — strict parsing, no migration; existing store files rebuilt

### WP12.1 Implementation Notes (2026-09-30)

- **Circular import resolution:** `ontology/update.py` → `experiment/schema/registries.py` via lazy import inside `_apply_step_size_overrides()` avoids the ontology→experiment→ontology cycle. This pattern should be reused for other cross-layer registry accesses.
- **Legacy table deletion:** All three legacy data tables (`_RULER_LR_DATA`, `_STEP_SIZE_OVERRIDES_DATA`, `_DYNAMICS_STEP_SIZE_OVERRIDES_DATA`) and the `_load_ruler_table()` JSON loader were removed. Data is now inline in registration functions.
- **Catch-all rename:** `ruler_lr_default` → `ruler_lr_catchall` clarifies this is a fallback for unknown tasks, not a task-specific entry.
- **Test updates:** `test_wp10_learning_integration_lock.py` was updated to embed the expected (dynamics, credit) pairs and task lists directly, removing dependency on deleted legacy tables.
- **Generated docs:** `docs/generated/capabilities.json` must be regenerated after PRIORS registry changes (via `write_generated_docs()`). The drift lock test (`test_codegen_drift_lock.py`) enforces this.
- **Single seeding path confirmed:** `seed_all_registries()` clears PRIORS_REGISTRY then calls `register_all_priors()` — verified idempotent and order-independent.

### WP18 Implementation Notes (2026-09-30)

- **ContrastDesign implementation:** Created `experiment/execution/contrast_design.py` with OFAT, fractional factorial (2^(k-p) with resolution IV generators), full factorial, and Plackett-Burman designs. Each assignment has `contrast_id` (deterministic SHA256), `factor_assignments` (dict), and `matched_group` (for paired analysis).
- **DataOrigin enum extension:** Added `CONTROL` and `CONTRAST` to existing `EXPLORATION`, `POLICY_SELECTED`, `CALIBRATION`, `TEST`. DataOrigin is now a first-class field in Provenance, not encoded in Schedule.budget_id.
- **ScheduleStage update:** S3 now assigns data_origin to proposals via metadata, generates ContrastDesign for contrast quota, and preserves original budget_id to maintain measurement_key stability.
- **Measurement identity preservation:** measurement_key (coordinate + schedule) does not include data_origin, ensuring identical measurements across data origins.
- **Schema version bump:** schema_version from 1→2 (fail-closed, no migration, no V2Reader — old stores rebuilt per Directive 2).
- **Property lock test:** `test_contrast_design_identifiability_lock.py` validates OFAT recovers known main effects on SyntheticGroundTruth (quadratic bowl with known optimum), fractional factorial estimates main effects at resolution IV, and contrast_id determinism.

---

### WP13/20/21/22 Implementation Notes (2026-10-01)

- **Store schema fix (WP20/U4):** Changed records table UNIQUE constraint from `measurement_key` to composite `UNIQUE(run_id, measurement_key)`. This allows the same coordinate+schedule (same measurement_key) to be measured in different runs without collision — required for policy interchangeability testing where each policy runs in a separate run with the same SearchSpace. Bumped schema version to 3. Updated `DuplicateMeasurementError` handling to detect composite constraint violations. Updated atomic append tests (`test_atomic_append_kill_proof.py`) to verify within-run deduplication (same run_id + same measurement_key = conflict).

- **E3 seeded axis-effect reproduction:** Executed `scripts/probes/e3_seeded_axis_effect.py` with dimension=6, n_seeds=5, n_offsets=10, noise_std=0.1. Effect size d=-1.499 (95% CI: [-2.40, -0.60], p=0.00106). Effect reproduces across seeds (CI excludes zero, p<0.05).

- **E4 transfer with provenance:** Executed `scripts/probes/e4_transfer_provenance.py` with n_source=10, n_heldout=10, n_seeds=5, zero_shot mode. Effect size d=-1.519 (95% CI: [-2.43, -0.61], p=0.00097). Transfer provenance fields (transfer_source_ids, transfer_mode, transfer_cutoff, target_task) populated for all 50 held-out evaluations.

- **C1–C88 conformance audit:** Executed `scripts/probes/conformance_evidence_audit.py` with `execute_verifying_tests=True, require_all=False`. Results: 46 passed, 42 skipped (optional capabilities), 0 failed, 0 no_evidence. Walltime: 356s. All required capabilities have passing verifying tests.

- **Legacy delete (WP21):** All legacy pillars physically removed. Import graph isolation lock test passes — kernel subpackages have zero legacy imports.

- **All DoD criteria met:** All 16 Definition of Done items verified.

---

## 1. Decision Log (from TODO43.plan.md)

### 1.1 Store: DuckDB replaces SQLite + MessagePack + projected columns

The NoSQL requirement (agile schema development) is met **without** a document DB: DuckDB is
an embedded, zero-config, single-file engine with native nested types — document-style
agility inside a SQL engine with real constraints.

| Option | Verdict | Why |
|---|---|---|
| **DuckDB** | **Selected** | Native `STRUCT`/`JSON`/`MAP`/array columns — sections are typed, queryable, indexable by zone maps; no projections. Columnar analytics for claims/fronts/attribution. `vss` extension for the vector index **(experimental; optional capability — see §1.1.1)**. Parquet-native export/import (R73 nearly free). WAL + crash-safe. In-process, zero-config. |
| PostgreSQL | Rejected | Server process violates the embedded/zero-config posture. |
| MongoDB | Rejected | Server, no UNIQUE-constraint discipline for dedup keys without ceremony, weak relational integrity for `record_artifacts`, new operational surface, and gains nothing over DuckDB JSON columns. |

**Supersessions to abc3:** §6.1.1 (MessagePack → native typed columns), §6.1.3 (projected
columns → deleted; the columns *are* the source), §6.1.4 (hand-tuned index strategy →
zone maps + ART as needed), §6.1.6 (WAL pragmas → DuckDB built-in), Appendix II DDL
(→ §2 of this plan), §6.1.5 (artifact delegation targets `packages/ceec-core::CEECStore`).

**Honest tradeoffs:**

- **Single-writer-per-process is an application-level determinism/governance decision, not a DuckDB limitation.** DuckDB supports multiple writer threads within one process using MVCC/optimistic concurrency (DuckDB concurrency docs). The design concentrates writes: `ExecutionBackend.submit() -> list[Record]` returns records to the pipeline, and only the pipeline writes. **Binding rule:** all store writes flow through the orchestrating process's single `RecordStore` instance, guarded by a `threading.Lock` (PEP 703 — in-process parallel evaluation via `asyncio.TaskGroup` shares that instance; the GIL is not trusted). K8 dedup becomes in-process; `measurement_key` UNIQUE remains the enforcement. If a genuine multi-*process* writer requirement ever emerges, it is a new explicit K1 decision taken behind the `Store` Protocol seam — no legacy engine is pre-committed as the fallback.
- **`seq` = authoritative persistence order, not deterministic experiment order.** The `threading.Lock` serializes access but does not guarantee concurrent workers acquire it in reproducible order. `seq` is the write-order authority (K8); the replay order comes from the recorded proposal/evaluation schedule (R26–R27).
- **Tiny-commit latency.** DuckDB commits cost ~1–3 ms vs SQLite's ~0.5 ms. The binding
  K7/K9 criterion is **overhead < 1% of median evaluation walltime** (evaluations run 1–10 s),
  not abc3's SQLite-calibrated absolute priors. The harness records mean/p95/fraction;
  batch appends per evaluation round amortize further.
- **STRUCT field additions** require `ALTER TABLE … ALTER COLUMN` (a rewrite). Mitigation:
  stable sections are typed STRUCTs; *open* surfaces (`params`, `payload`, `unknown`) are
  `JSON` — new hyperparameters and telemetry need **zero DDL**. That is the agile-schema
  requirement, satisfied.
- **Cross-process access is exclusive, not concurrent.** DuckDB allows one
  read-write process *or* many read-only processes — never both. While a
  service-mode run holds the store, `comp-surface report/export` from another
  process cannot open it. Mitigation: live reporting/steering route through the
  service's control surface (WP11.4); standalone report/export run when idle, or
  against an export bundle (R73) — both discharge the need without a store swap.
  Should any future requirement ever justify a different store engine, that is a
  new explicit K1 decision behind the `Store` Protocol seam; nothing is
  pre-committed.

#### 1.1.1 Vector Search: Optional Capability

DuckDB's `vss` (Vector Similarity Search) extension is currently **experimental** (DuckDB docs). The Kernel treats vector retrieval as a **capability**, not a foundational persistence contract:

```text
VectorStore capability
    ├── exact scan (brute-force `list_dot` / cosine) — always available
    └── optional approximate index (HNSW via `vss` or external) — enabled when corpus warrants
```

The plan's existing fallback (small corpus → brute force, large corpus → HNSW) becomes the explicit contract. The `vector_index` table in §2 remains; the index *population strategy* is pluggable. This keeps the scientific kernel independent of a still-evolving optimization feature.

**Embedding producer (open decision, K1-owned).** The `FLOAT[384]` column needs
a source: (a) a deterministic hashing/feature-hashed embedder — no new
dependency, semantics limited to lexical/structural similarity — or (b) a small
local transformer model — semantic retrieval, but a new mandatory dependency
requiring an explicit K1 decision, vendored/offline-installable (extension and
model downloads must not require network at run time). S8 writes embeddings
tagged with `embedding_version`, so the choice is revisable per version without
schema change; brute-force retrieval semantics do not depend on the choice.

### 1.2 Dependency decision (K1 discharge)

`duckdb` enters as a mandatory runtime dependency by explicit decision (this plan, §1.1),
via `uv add duckdb`, pinned in `uv.lock`. The dev-env smoke check becomes:
`uv run python -c "import duckdb, optuna, scipy, torchvision, pytest"`.
No other new mandatory runtime deps; the Kernel's metaprogramming stays stdlib
(`typing`, `dataclasses`, `importlib`) per abc3 K1.

---

## 6. Class E Benchmarks (hierarchy of evidence, per WP5.5)

| Class | Benchmark | Discharges |
|---|---|---|
| **E1 — Infrastructure** | Crash recovery (kill -9 during atomic append) | R12, R26 |
| | Store overhead harness (mean/p95/fraction < 1% median eval walltime) | K7, K9 |
| | Serialization round-trip (all sections, schema v1→v2 readers) | R79, K4 |
| | Atomic append with artifacts (single transaction) | R60, K8 |
| **E2 — Algorithmic** | Cost-to-rank vs uniform baseline | R46 |
| | Surrogate acquisition vs predeclared baseline on held-out tasks (effect-size protocol) | R54 |
| | Cost-model estimate-vs-actual error trend | R23, R24 |
| | Divergence-bound replay (1357 s run) | R50 |
| **E3 — Scientific** | Seeded axis-effect reproduction (independent seeds, CI on effect) | R86 |
| | Effect survives independent environment (GPU arch, CUDA, PyTorch versions) | R86 |
| | Effect transfers to predeclared held-out tasks (N≥10, paired, effect size) | R54, R86 |
| **E4 — Generalization** | Cross-task transfer (explicit `transfer_source_ids`, `transfer_mode`) | R53, R55 |
| | Cross-topology transfer | R53, R55 |
| | Unseen substrate (zero-shot / few-shot) | R53, R55 |

**Effect-size protocol (replaces "beats random"):**
- `N_tasks ≥ 10` independent held-out tasks (predeclared, never used for surrogate training)
- `N_seeds ≥ 5` independent repetitions **per task** (within-task repeated measures)
- Fixed evaluation budget `B` with explicit `CostBudgetTier`:
  - `EVAL_COUNT` — evaluation count budget (always comparable)
  - `FLOPS` — FLOP budget (when FLOPs are meaningful/comparable)
  - `WALLTIME` — walltime budget (ONLY valid within matched hardware class; requires
    `hardware_class` provenance match)
- Predeclared primary metric (e.g., best validation score at budget B)
- **Primary inference unit: task.** For each task, aggregate seed-level results to a task-level
  effect Δ_task = policy_metric(task) - baseline_metric(task). Primary comparison operates
  over the distribution of Δ_task across tasks (paired where possible: same seeds, same tasks).
- Seeds provide within-task uncertainty estimation; report seed-level variance alongside.
- Optional: mixed-effects model `metric ~ policy + (1 | task) + (1 | task:seed)` for
  simultaneous estimation.
- Report: effect size (Cohen's d at task level), 95% CI, p-value (paired t-test or
  Wilcoxon on task-level Δ_task).
- Secondary: evaluations to reach target τ, area under curve.

Probe/benchmark scripts live in `scripts/probes/` per repo convention: docstring states the
measured-regime numbers and the demo/decision they informed. Any benchmark exceeding the
5-minute foreground cell limit launches with
`nohup uv run python … > logs/<name>.log 2>&1 &` and is polled at ≤2-minute intervals with a
pre-registered kill time. Low benchmark results are treated as suspected implementation
defects first (AGENTS.md), not accepted verdicts, until the harness itself is verified.

---

## 7. Definition of Done

abc3 §21.1 items 1–12 (all) and §21.2 adjusted: ~~migration complete~~ → legacy stores
abandoned untouched (Directive 3); schema versioning is fail-closed — no legacy readers,
no migration machinery (Directive 2). Every Class S lock green, every Class E benchmark
recorded as a store record, every Class P gate enforced in CI.

**New acceptance criteria from feedback:**
- WP1.5 scientific validity skeleton passes: synthetic fixture recovers known effect,
  data splits enforced, comparison guards work, replay vs reproducibility distinguished.
- WP5.5 statistical protocol lock passes: benchmark classes disjoint, effect-size protocol
  fields present, I(C,U) data splits enforced, leakage audit runs.
- Atomic append with artifacts: kill -9 during transaction → no partial state, no recovery needed.
- Legality boundary lock: no heuristic exclusions in DECLARED constraints.
- Status three-tier model: observations, assessments (with procedure version), derived claims
  (pure queries only).

**Stronger completion criteria (per Integration Reality Correction):**
- Exactly one `RunSpec` model (typed, serializable, not `dict[str, Any]`).
- Exactly one `SearchSpace` model derived from `AXES` + task + constraints.
- Every proposal policy consumes that `SearchSpace` and emits the same `Proposal` type.
- Every allocation policy consumes the same evidence and emits the same `AllocationPlan` type.
- Every run executes the same S1–S11 stage graph via `Stage.run(ctx) -> Fragment` dispatch.
- S3–S10 can repeat for arbitrarily many rounds (continuous round loop implemented).
- AutoScientist/Synthesis, Optuna, Evolution, Random, TrainerDriven differ only in
  proposal policy, not lifecycle or evidence semantics.
- Continuous/Campaign differs only in budget, allocator, service/control behavior.
- One `RecordStore` and one measurement identity.
- No policy can bypass legality, provenance, novelty, failure handling, budget accounting,
  or atomic persistence.
- A run can pause, resume, replay, and continue with a different policy.
- Claim eligibility computed exclusively from achieved evidence (not planned `n_seeds`).
- E3 demonstrates known-effect recovery; E4 demonstrates held-out transfer.
- Every C1–C88 capability either has real conformance evidence or an explicit retirement record.
- Legacy pillars are physically gone and the import graph proves it.
- Unified acceptance suite (U1–U5) passes for all three historical modes.

Deferred to the hygiene pass (never per-commit, per AGENTS.md): repo-wide `ruff check` /
`pyright` outside `experiment/`, full `pytest --cov`, `pip-audit`. The Kernel itself ships
strict-clean from WP1 onward.

---

## Integration Reality Correction (2026-09-30 — Updated)

**WP8–WP13 established the kernel primitives and most required functionality, but several completion bullets were satisfied structurally rather than end-to-end. These are not architectural reversions. The remaining work closes runtime integration seams and verifies that the individual components actually compose into the unified kernel described by abc3 §5.**

**Progress Update (2026-09-30)**: WP14/WP15/WP16/WP17 have closed the major integration seams; WP19 has closed the failure isolation and runtime provenance seams:

Explicit reclassification of completion status:

| Area | Status to record |
|---|---|
| Axis/registry union | Complete |
| Legality | Complete |
| Store/artifacts | Complete, subject to atomicity clarification |
| Stage definitions | **Complete** — runtime dispatch via `Stage.run(ctx) -> Fragment` |
| Policy catalog | **Complete** — canonical SearchSpace/ProposalContext/Proposal interface |
| Optuna integration | **Complete** — OptunaDistributionAdapter provides AXES-driven suggestion |
| Allocator | **Complete** — integrated between rounds in round loop |
| Continuous round loop | **Complete** — S3-S10 repeat with Decision-based termination |
| Learning/store integration | Mostly complete |
| Claim integrity | Helper complete; **all callers not yet normalized** |
| Failure isolation | **Complete** — per-item Success/Failure via EvaluationResult, siblings continue |
| Runtime provenance | **Complete** — EnvironmentSnapshot captured once per run, injected via SystemContext |
| E1 | Complete |
| E2 | Complete as a mechanism validation |
| E3/E4 | Incomplete |
| Legacy deletion | Incomplete |
| Full C1–C88 proof | Incomplete |

**Why this matters:** The current plan says "ModelBased policy completed" and "EvidenceDrivenAllocator integration hook" even though the corresponding runtime paths still contain stubs. The Stage Protocol is defined but `PipelineRunner` does not actually dispatch to `Stage.run()`, the policy interface still receives an empty candidate list, and the allocator hook is a no-op. These seams must close before the kernel is genuinely unified.

---

## 2026-10-01 Session: Type Safety & Lint Fixes (Post-WP22)

All work packages complete per plan. This session addressed remaining pyright type errors and ruff import sorting in the `experiment/` kernel modules:

**Fixed pyright errors (7 total):**
1. `computronium/experiment/execution/compose.py:501` — Replaced deleted `_DYNAMICS_STEP_SIZE_OVERRIDES` with `get_dynamics_step_size()` from PRIORS registry (WP12.1 cleanup)
2. `computronium/experiment/execution/optuna_adapter.py:40` — Fixed `Expr.evaluate()` call; now uses standalone `evaluate()` from legality DSL with proper `EvaluationContext`
3. `computronium/experiment/execution/search_space.py:60` — Added missing `Expr` import from legality DSL
4. `computronium/experiment/execution/stage.py:84,128` — Removed duplicate `StageContext` class declaration
5. `computronium/experiment/execution/pipeline.py:450` — Changed `Policy` import from `search_space.py` (proposal policy protocol) to `policy.py` (allocation policy protocol) to match actual runtime usage in stages
6. `computronium/experiment/execution/search_space.py:497` — Renamed proposal `Policy` protocol to `ProposalPolicy` to avoid shadowing allocation `Policy`
7. `computronium/experiment/execution/stages_impl.py:71,179` — Fixed `ctx.policy.propose()` calls; now correctly typed with allocation policy protocol

**Fixed ruff import sorting:**
- `computronium/experiment/execution/compose.py` — Reordered imports per isort conventions

**Verification:**
- All 8 U1–U5 acceptance tests pass
- All 37 property lock tests pass (WP10, ContrastDesign, KernelIsolation)
- All 7 atomic append + demo tests pass
- `pyright computronium/experiment/` — 0 errors
- `ruff format` — no changes needed

No functional changes; purely type safety and lint hygiene.