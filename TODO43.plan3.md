# TODO43.plan3.md — Completion Plan: The Computronium Experiment Kernel

**Implements:** TODO43.abc3.md (SPEC-43 Rev 2.0) — the unified/hybrid design
**Binds to:** `AGENTS.md` in full — toolchain, type system, architecture, async/thread safety, error/logging, testing tiers, commit checklist
**Status:** Kernel primitives complete (WP1–WP11, WP14–WP17, WP19). Remaining: WP12.1 → WP12 → WP18 → WP13 → WP20 → WP21 → WP22.

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

## Remaining Work Packages (Dependency-Ordered)

```text
WP12.1 Prior registry finalization        ──► WP12  Legacy pillar port & delete
                                                 │
                                                 ▼
                                          WP18  Evidence & design integrity
                                                 │
                                                 ▼
                                          WP13  Class E benchmarks (E3/E4)
                                                 │
                                                 ▼
                                          WP20  Unified-kernel acceptance (U1–U5)
                                                 │
                                                 ▼
                                          WP21  Legacy delete (blocked on WP20)
                                                 │
                                                 ▼
                                          WP22  Full C1–C88 audit + DoD
```

---

### WP12.1 — Prior Registry Finalization (blocks WP12)

**Must complete before WP12 bulk delete** — unblocks `ontology/update.py` reroute.

- Reroute `computronium/ontology/update.py::_apply_step_size_overrides()` to `PRIORS_REGISTRY.prior_value()` (currently reads local legacy table; circular import blocker: ontology → experiment → ontology)
- Delete legacy data tables in `prior.py` (`_RULER_LR_DATA`, `_STEP_SIZE_OVERRIDES_DATA`, `_DYNAMICS_STEP_SIZE_DATA`, JSON loader)
- Rename catch-all prior `ruler_lr_*` → `ruler_lr_catchall` on deletion
- Single seeding path: `seed_all_registries()` → `register_all_priors()` (idempotent, order-independent)

---

### WP12 — Legacy Port & Delete (Directive 1)

**Precondition:** Conformance green per capability (R77); import-graph lock guards kernel.

**Legacy pillars to delete:**

| Pillar | Path | Verification |
|---|---|---|
| AutoScientist | `computronium/autoscientist/` | Proposal equivalence (U1) |
| Hyperopt | `computronium/hyperopt/` | Optuna integration (U2) |
| Legacy execution engine | `computronium/execution/` (engine.py, strategy.py, synthesizer.py, candidate_gen.py, _state.py, _lifecycle.py, lifecycle.py, robustness.py, monitoring.py, interpretability.py, dashboard/) | Multi-round test (U3) |
| Core campaign | `computronium/core/campaign/` | Pipeline + Allocator + Store |
| Lightning | `computronium/lightning_/` | TrainerDriven adapter |
| Lab research layer | `packages/computronium-lab/` (research layer) | Synthesis/Evolution policies |
| CEEC (external) | `packages/ceec-core/` | Already folded into kernel artifacts table |

**Port-before-delete rule:** Each capability must have a kernel replacement with passing conformance test before its legacy code is removed.

**Import-graph lock:** `tests/property/test_kernel_isolation_lock.py` — kernel subpackages must not import any legacy pillar module.

---

### WP18 — Evidence & Design Integrity

- **ContrastDesign** (`experiment/execution/contrast_design.py`): OFAT / fractional-factorial DOE with `contrast_id`, `factor_assignments`, `matched_group` — replaces labeling random subsets as "contrast"
- **DataOrigin** first-class field on Provenance (EXPLORATION / CALIBRATION / TEST / CONTROL / CONTRAST) — not encoded in `budget_id`
- Measurement identity must not change with data origin
- S3 ScheduleStage emits data-origin allocation + contrast quota by construction
- **Lock**: `tests/property/test_contrast_design_identifiability_lock.py` — DOE recovers known effect on SyntheticGroundTruth
- **Schema change**: bump `schema_version` to 2 (fail-closed, no migration per Directive 2)

---

### WP13 — Class E Benchmarks & DoD Hardening

**Prerequisite:** WP18 complete (E3/E4 probes require ContrastDesign + DataOrigin)

| Class | Benchmark | Status |
|---|---|---|
| **E1** | Crash recovery (kill -9), store overhead (<1%), serialization round-trip, atomic append | ✅ Locked |
| **E2** | Surrogate acquisition vs random (effect-size protocol) | ✅ d=-1.52, p=0.00097 |
| **E3** | Seeded axis-effect reproduction on `SyntheticGroundTruth` | 🔄 Script ready (`scripts/probes/e3_seeded_axis_effect.py`) |
| **E4** | Cross-task / cross-topology / unseen-substrate transfer with provenance | 🔄 Script ready (`scripts/probes/e4_transfer_provenance.py`) |

**DoD hardening:**
- Execute full C1–C88 conformance sweep: `scripts/probes/conformance_evidence_audit.py` (verifying_test per capability)
- Record all results as store records (E-class rows in CAPABILITIES evidence)
- Background runs >5 min per AGENTS.md §6

---

### WP20 — Unified-Kernel Acceptance Suite (U1–U5)

**Harness:** `tests/acceptance/unified_kernel.py` (new directory)

| Test | Description |
|---|---|
| **U1** | Question → `question_first()` → RunSpec → Synthesis policy → SearchSpace → Pipeline → RecordStore |
| **U2** | Same RunSpec → SearchSpace → TPE (ModelBasedPolicy) → Pipeline → same Record schema/store |
| **U3** | Same RunSpec → SearchSpace → Random/TPE/Evolution → Allocator → multi-round pipeline → pause → resume → report |
| **U4** | Policy interchangeability: Round 1 StratifiedRandom, Round 2 TPE, Round 3 Evolution, Round 4 Synthesis — same RunSpec/Space/Store, only policy changes |
| **U5** | Cross-policy evidence reuse: Random → TPE → Evolution over same store — no separate DB, no migration, same measurement identity, same legality, same claims |

**All U1–U5 must pass before WP21 (legacy delete) proceeds.**

---

### WP21 — Legacy Delete (Stricter)

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

---

### WP22 — Full C1–C88 Audit + E3/E4 Completion

- Execute `conformance_evidence_audit.py` to completion (all 88 verifying tests)
- Run E3 and E4 probe scripts to completion, record results as store records
- Final Definition of Done checklist (from §9.19):

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
| WP12.1 | `ontology/update.py`, `experiment/schema/prior.py`, `seed_registries.py` |
| WP12 | Bulk delete of legacy pillars (see table) |
| WP18 | `experiment/execution/contrast_design.py`, `schema/coordinate.py` (DataOrigin enum + schema_version bump), `tests/property/test_contrast_design_identifiability_lock.py` |
| WP13 | Run `scripts/probes/e3_seeded_axis_effect.py`, `e4_transfer_provenance.py`, `conformance_evidence_audit.py` |
| WP20 | `tests/acceptance/unified_kernel.py` (new directory) |
| WP22 | Final DoD verification script |

---

## Notes

- **No new dependencies** — kernel metaprogramming stays stdlib (`typing`, `dataclasses`, `importlib`)
- **Kernel owns semantics** (§9.20): legality, measurement identity, provenance, persistence, claims, reproducibility, round control are kernel-owned; plugins only decide *which* coordinate/evidence/hypothesis
- **Registry reflection over hardcoding:** Derive grids from `AXES_REGISTRIES`, not parallel lists
- **Delete wholesale, don't patch:** WP12 is a bulk delete, not incremental migration
- **Store files pre-`task_id` STRUCT addition are unreadable** — rebuild per Directive 2
- **Complexity noqa** on `compose.py` is temporary — refactor or delete when WP12 removes last legacy importer
- **Schema version bump at WP18** (DataOrigin addition) — strict parsing, no migration; existing store files rebuilt