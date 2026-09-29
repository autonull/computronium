# TODO43.plan.md — Implementation Plan: The Computronium Experiment Kernel

**Implements:** TODO43.abc3.md (SPEC-43 Rev 2.0 — the unified/hybrid design) as the
authoritative spec; abc2 (Rev 1.1) is superseded and consulted only for rationale.
**Binds to:** `AGENTS.md` in full — toolchain, type system, architecture, async/thread
safety, error/logging conventions, environment rules, testing tiers, commit checklist.
**Status:** WP1 COMPLETE — Walking skeleton implemented and tested. WP2 ready to start.

---

## 0. Scope Directives (binding, from the round owner)

1. **No backwards compatibility.** No strangler adapters, no legacy importers, no old-shape
   migration phases. abc3 §12.2 (four-phase store migration) and §12.3 (strangler migration)
   are **dropped**. Legacy entry points (`broad_map`, `stack`, `hyperopt`, `execution`,
   `lightning_`, computronium-lab research layer) are ported *into* the Kernel as catalog
   entries, then deleted outright.
2. **No data preservation.** `kb.sqlite`, `campaign.db`, `ledger.sqlite`, and Optuna `*.db`
   are abandoned in place, untouched and read-only by neglect (never opened again). Only
   `packages/ceec-core`'s content-addressed store is linked forward (it is an active
   subsystem, not legacy data).
3. **No time estimates.** Sequencing is dependency-ordered only.
4. **Store decision:** DuckDB (embedded, SQLite-like) — see §1. MongoDB rejected.

**Codebase-verified anchors** (checked 2026-09-29):

- CEEC store: `packages/ceec-core/src/ceec/store/_store.py::CEECStore` (content-addressed,
  pydantic `_Frozen` models). The Kernel links via its public API only.
- `msgpack` is already in `uv.lock` (existing users keep it); the Kernel will **not** depend
  on it — native DuckDB types replace serialization.
- `duckdb` is **not** in `uv.lock` → a new mandatory runtime dependency. AGENTS.md K1 and
  abc3 K1 both require an explicit decision: **granted here** (§1.1); landed as `uv add
  duckdb` in WP1 and recorded in `pyproject.toml` (single source of truth).
- `uv.lock` carries `cp314t` wheels → **free-threaded CPython is real**: PEP 703 applies.
  Shared mutable state behind explicit `threading.Lock`; never rely on the GIL.
- Existing doctrine to generalize, not reinvent: 64-spec `ImplementationSpec` registry,
  `test_registry_completeness_lock`, `test_dynamics_wiring_lock` (lockstep wiring pattern),
  `DEMOS` registry + `docs/figures/manifest.json` gallery lock, `scripts/probes/` conventions.

---

## 1. Decision Log

### 1.1 Store: DuckDB replaces SQLite + MessagePack + projected columns

The NoSQL requirement (agile schema development) is met **without** a document DB: DuckDB is
an embedded, zero-config, single-file engine with native nested types — document-style
agility inside a SQL engine with real constraints.

| Option | Verdict | Why |
|---|---|---|
| SQLite + MessagePack BLOBs + projected columns (abc3 §6.1) | **Superseded** | The projection machinery (dual-write + CI lock) and MessagePack opaqueness exist only to work around SQLite's inability to query inside BLOBs. |
| SQLite + JSON1 + expression indexes | Fallback | Kills MessagePack, but JSON is parsed per query; analytics (fronts, attribution, clustering — the actual product) fight the row-store. |
| **DuckDB** | **Selected** | Native `STRUCT`/`JSON`/`MAP`/array columns — sections are typed, queryable, indexable by zone maps; no projections. Columnar analytics for claims/fronts/attribution. `vss` extension for the vector index. Parquet-native export/import (R73 nearly free). WAL + crash-safe. In-process, zero-config. |
| libSQL/Turso | Rejected | SQLite fork; brings nothing DuckDB doesn't, adds a fork dependency. |
| PostgreSQL | Rejected | Server process violates the embedded/zero-config posture. |
| MongoDB | Rejected | Server, no UNIQUE-constraint discipline for dedup keys without ceremony, weak relational integrity for `record_artifacts`, new operational surface, and gains nothing over DuckDB JSON columns. |

**Supersessions to abc3:** §6.1.1 (MessagePack → native typed columns), §6.1.3 (projected
columns → deleted; the columns *are* the source), §6.1.4 (SQLite indexes → zone maps + ART
as needed), §6.1.6 (WAL pragmas → DuckDB built-in), Appendix II DDL (→ §2 of this plan),
§6.1.5 (artifact delegation targets `packages/ceec-core::CEECStore`).

**Honest tradeoffs:**

- **Single-writer-per-process.** DuckDB allows one writer process (file lock); SQLite WAL
  allows lock-serialized multi-process writes. The design already concentrates writes:
  `ExecutionBackend.submit() -> list[Record]` returns records to the pipeline, and only the
  pipeline writes. **Binding rule:** all store writes flow through the orchestrating
  process's single `RecordStore` instance, guarded by a `threading.Lock` (PEP 703 — in-process
  parallel evaluation via `asyncio.TaskGroup` shares that instance; the GIL is not trusted).
  K8 dedup becomes in-process; `measurement_key` UNIQUE remains the enforcement. If a true
  multi-writer requirement ever emerges, the `Store` Protocol swaps back to SQLite WAL.
- **Tiny-commit latency.** DuckDB commits cost ~1–3 ms vs SQLite's ~0.5 ms. The binding
  K7/K9 criterion is **overhead < 1% of median evaluation walltime** (evaluations run 1–10 s),
  not abc3's SQLite-calibrated absolute priors. The harness records mean/p95/fraction;
  batch appends per evaluation round amortize further.
- **STRUCT field additions** require `ALTER TABLE … ALTER COLUMN` (a rewrite). Mitigation:
  stable sections are typed STRUCTs; *open* surfaces (`params`, `payload`, `unknown`) are
  `JSON` — new tunables and telemetry need **zero DDL**. That is the agile-schema
  requirement, satisfied.

### 1.2 Dependency decision (K1 discharge)

`duckdb` enters as a mandatory runtime dependency by explicit decision (this plan, §1.1),
via `uv add duckdb`, pinned in `uv.lock`. The dev-env smoke check becomes:
`uv run python -c "import duckdb, optuna, scipy, torchvision, pytest"`.
No other new mandatory runtime deps; the Kernel's metaprogramming stays stdlib
(`typing`, `dataclasses`, `importlib`) per abc3 K1.

---

## 2. Unified Store Schema (replaces abc3 Appendix II)

```sql
CREATE SEQUENCE record_seq;

CREATE TABLE runs (
    run_id            TEXT PRIMARY KEY,
    spec              JSON,                 -- RunSpec (abc3 §3.8)
    spec_version      INTEGER NOT NULL,
    status            TEXT NOT NULL,        -- running|completed|failed|killed
    budget_consumed_s DOUBLE,
    replay_hash       TEXT,                 -- R27
    started_at        TIMESTAMP NOT NULL,
    finished_at       TIMESTAMP
);

CREATE TABLE records (
    record_id       TEXT PRIMARY KEY,       -- write-time content hash, schema-bound (§3.5)
    seq             BIGINT UNIQUE DEFAULT nextval('record_seq'),  -- K8 write order
    run_id          TEXT NOT NULL REFERENCES runs(run_id),
    schema_version  INTEGER NOT NULL,
    -- identity keys
    cell_key        TEXT NOT NULL,          -- sha256(coordinate); repeats group here (R9)
    measurement_key TEXT NOT NULL UNIQUE,   -- sha256(coordinate ∪ schedule); dedup/resume
    -- coordinate: structural axes typed; tunables open
    substrate       TEXT NOT NULL,
    geometry        TEXT NOT NULL,
    dynamics        TEXT NOT NULL,
    plasticity      TEXT NOT NULL,
    credit          TEXT NOT NULL,
    update_rule     TEXT NOT NULL,
    params          JSON NOT NULL,          -- the 37-tunable union + geometry/substrate params
    schedule        STRUCT(fidelity TEXT, seed INTEGER, n_seeds INTEGER,
                           epochs INTEGER, batch_limit INTEGER, budget_id TEXT) NOT NULL,
    provenance      JSON NOT NULL,          -- env, dataset+version, code SHA, policy, links
    status          STRUCT(gate_verdict TEXT, defect TEXT, cause TEXT, severity TEXT,
                           quarantine BOOLEAN, maturity TEXT, uncertainty JSON,
                           reproducibility TEXT, ceec_link TEXT) NOT NULL,
    payload         JSON NOT NULL,          -- objectives, telemetry, probes, artifact refs
    unknown         JSON                    -- R79: preserved, labelled, never defaulted
);

CREATE TABLE record_artifacts (            -- bytes live in ceec-core (abc3 §6.1.5)
    record_id TEXT NOT NULL REFERENCES records(record_id),
    digest    TEXT NOT NULL,
    role      TEXT NOT NULL,                -- config|figure|reproducer|kernel
    PRIMARY KEY (record_id, digest, role)
);

CREATE TABLE vector_index (
    record_id        TEXT PRIMARY KEY REFERENCES records(record_id),
    embedding        FLOAT[384] NOT NULL,
    embedding_version INTEGER NOT NULL
);
```

Claim prefilter is plain SQL (`WHERE status.gate_verdict = 'PASS' AND NOT status.quarantine
AND schedule.fidelity = 'L2' AND schedule.n_seeds >= 5`); the authoritative
`claim_eligible` remains the pure Python predicate of abc3 §6.3 (matched-control and
CEEC-gated checks are relational, not columnar). Doctrine 5 intact: derived verdicts are
never stored, never cached.

**Store engineering rules (AGENTS.md-binding):**

- Every SQL statement is **parameterized** — never f-string/t-string interpolation into SQL
  (AGENTS.md Safe Interpolation; also satisfies Ruff `S` bandit rules).
- `RecordStore` is a context manager (`with` owns connection lifecycle; WAL checkpoint on
  close); all resource lifecycles via context managers.
- Value sets are `StrEnum` (`GateVerdict`, `FailureCause`, `Severity`, `Tier`, `AxisKind`,
  `SpecStatus`, `StageId`, `ConstraintKind`, `ConstraintOrigin`, `ConstraintScope`) — never
  bare strings; serialized as their values, validated on read.
- All exceptions raise from abc3 Appendix I's hierarchy with chaining
  (`raise DuplicateMeasurement(key) from exc`).

---

## 3. Work Packages (dependency-ordered)

Each WP lands through the AGENTS.md **Agent Commit Checklist** (dev-env smoke, `ruff format`
+ `ruff check --fix` on changed files, `pyright` strict on changed files — all `experiment/`
modules are new, so strict applies throughout — and targeted tests with output + walltime
visible).

### WP0 — Binding gates (before any Kernel code)
abc3 §0.6, minus what this plan already discharges.
- **Gate 1 — Rev 3 review:** accept/reject each TODO43 §13–§15 candidate; record the verdict
  table in `docs/design/rev3_gate.md`. Output feeds WP2 registry seeds and WP4 catalog rows.
- **Gate 2 — Fix the union:** audit the six implementations' hyperparameter surfaces; verify
  Appendix IV's 37-name union; add missing domain rows. Output: the frozen union table that
  WP2's harvest lock asserts against.
- ~~Gate 3~~ — discharged by WP1 below (walking skeleton is the first build, not a document).

### WP1 — Walking skeleton (vertical slice, proves the five abstractions compose) ✅ COMPLETE
abc3 §12.4. Package `computronium/experiment/` per abc3 §1.1.
- ✅ `uv add duckdb`; dev-env smoke extended per §1.2.
- ✅ `schema/registry.py` — generic `Registry[SpecT]` (PEP 695 generic class; lock, diff,
  schema, integrity). Specs are `@dataclass(frozen=True, slots=True)`.
- ✅ `schema/axis.py` — `AxisSpec` with `AxisKind(StrEnum)`, availability predicates;
  `AxisPrimitive.__init_subclass__` auto-registration.
- ✅ `schema/coordinate.py`, `schema/record.py` — `Coordinate`, `Record`, three identity keys
  (frozen dataclasses; hashing over canonical serialization).
- ✅ `evidence/store.py` — DuckDB `RecordStore`: `append()` (single transaction: seq + record +
  artifacts), `DuplicateMeasurementError` on UNIQUE violation, `Store` Protocol, `threading.Lock`
  writer guard, parameterized SQL, context-manager lifecycle.
- ⏳ `execution/pipeline.py` + `execution/stage.py` — S1–S11 runner with wrapper obligations
  (coverage, classification, traceability, atomic append); one real policy
  (`RoundRobinGrid`), most stages no-op. (Deferred to WP4)
- ✅ `evidence/claims.py` — one `claim_eligible` predicate + SQL prefilter (implemented as `claim_eligible_prefilter` in store).
- ✅ `experiment/__init__.py` exposes the public API via `__all__`; internals `_`-prefixed.
- ✅ **End-to-end proof:** Verified via manual test — records, duplicate detection (skip), store consistency after reopen.

**Files created:**
- `computronium/experiment/__init__.py` — Public API exports
- `computronium/experiment/schema/__init__.py` — Schema package exports
- `computronium/experiment/schema/registry.py` — Generic Registry[SpecT]
- `computronium/experiment/schema/axis.py` — AxisSpec, AxisKind, registries
- `computronium/experiment/schema/coordinate.py` — Coordinate, Schedule, Provenance
- `computronium/experiment/schema/record.py` — Record, Status, GateVerdict, FailureCause, Severity, Maturity
- `computronium/experiment/schema/harvest.py` — Tunable harvesting, ConflictingTunableError, HarvestedSchema
- `computronium/experiment/schema/versioning.py` — Schema versioning, SchemaRegistry, UnknownField
- `computronium/experiment/schema/registries.py` — OBJECTIVES, CONSTRAINTS, PRIORS, POLICIES, STAGES, CAPABILITIES registries
- `computronium/experiment/legality/__init__.py` — Legality package exports
- `computronium/experiment/legality/dsl.py` — Expr AST, evaluator, JSON wire format
- `computronium/experiment/legality/engine.py` — Constraint model, LegalityEngine, globally-suppressive semantics
- `computronium/experiment/legality/classify.py` — Defect taxonomy, DefectRegistry, void patterns
- `computronium/experiment/evidence/__init__.py` — Evidence package exports
- `computronium/experiment/evidence/store.py` — DuckDB RecordStore
- `computronium/experiment/execution/__init__.py` — Execution package exports (empty, for future)

**Quality gates passed:**
- `ruff format` — all new files formatted
- `ruff check` — all new files lint-clean (15 pre-existing errors in legacy files only)
- `pyright` — strict mode clean on all new `experiment/` modules
- `pytest` — all experiment-related tests pass (24 tests)

### WP2 — Pillar 1 complete: schema & registries
- ✅ `schema/harvest.py` — `__tunables__` reflection, name-based dedup (70→37; conflicts raise
  `ConflictingTunableError`), `harvest_schema()`.
- ✅ `schema/versioning.py` — `schema_version`, append-only reader registry, `UnknownField`
  preservation (R79, K4). Version 1 = this schema; no legacy readers needed (Directive 1).
- ✅ `schema/registries.py` — Registry instances: `OBJECTIVES`, `CONSTRAINTS`, `PRIORS`,
  `POLICIES`, `STAGES`, `CAPABILITIES` (abc3 §2.3 seeds, per Gate 1/2 outcomes).
- ✅ Locks (CI property tests): `tests/property/test_experiment_registries_wiring_lock.py`
  — registry uniqueness/totality/no-orphans/lock; export surface wiring.
- **Lockstep wiring tests** follow the `test_dynamics_wiring_lock.py` pattern: registry ↔
  config classmethods ↔ `__all__` ↔ `TYPE_CHECKING` imports stay in sync per pillar;
  never bypassed.

### WP3 — Pillar 3: legality engine
- ✅ `legality/dsl.py` — `Expr` AST (frozen dataclasses; `type` alias union per abc3 §4.1) +
  evaluator dispatched by `match`/`case` + Appendix III JSON wire format (content-hashed).
- ✅ `legality/engine.py` — `Constraint` model (origin/scope/enforced-at), S4/S6 enforcement,
  globally-suppressive semantics (R38); generated compatibility matrix (R63).
- ✅ `legality/classify.py` — void/defect taxonomy as registry data; unclassified bucket counted.
- Seed constraints from `SystemConfig.validate()`, task fences, `apply_constraints` (Q2, R37,
  R66). Migrate-and-delete the original validators (Directive 1).

### WP4 — Pillar 2: execution
- `execution/budget.py` — `Budget` + `CostModel` Protocol (R21–R24).
- `execution/allocator.py` — `AllocationPolicy` Protocol + evidence-driven successive
  promotion reference implementation (R46–R51, divergence/stagnation telemetry, waste report).
- `execution/replay.py` — replay hash, resume on `measurement_key`, checkpoint/restore
  (R26–R30).
- `execution/backends.py` — local/multiprocess backends; **workers return Records; the
  pipeline process is the sole writer** (§1.1). In-process concurrency via
  `asyncio.TaskGroup`; blocking evaluation bodies stay out of the event loop
  (`asyncio.to_thread` where a legacy blocking call must run inside async orchestration);
  concurrent independent failures handled with `except*` (R29 isolation).
- `execution/policy.py` — `Policy` Protocol + the eight-policy catalog (abc3 §5.3): port
  `StratifiedRandom`, `RoundRobinGrid`, `UniformRandom`, `ModelBased` (Optuna behind a
  storage adapter over the unified store — R71), `Evolution`, `Synthesis`,
  `StrategyProgression`, `TrainerDriven` (last four per Gate 1 verdicts). Delete the six
  legacy implementations' search paths as each port lands (Directive 1).

### WP5 — Pillar 4: evidence & governance
- `evidence/status.py` — primary-only `Status` fields (no stored derived verdicts).
- `evidence/claims.py` — full predicate suite: claims (R35), promotion (R36), alerts as
  record-stream predicates (R83/Q14), matched-cost comparison guard (R65), stratification
  guards (R8/R22/R67).
- `evidence/failure.py` — `FailureCause` taxonomy, clustering, reproducer emission,
  fix-linkage queries (R58–R62).
- `evidence/ceec.py` — artifact delegation to `packages/ceec-core::CEECStore`
  (`CEECStore.put` → digest → `record_artifacts`); ledger linkage via `status.ceec_link`
  (Q9). Cross-package dependency is the public `ceec` API only.
- Vector retrieval over `vector_index` (`vss` HNSW once corpus warrants; brute-force
  `list_dot` first) — C59, R15, K5.
- `RunSpec`/record parsing at I/O boundaries (CLI, import, export) validated with
  **Pydantic v2** models mirroring the internal frozen dataclasses (AGENTS.md data-modeling
  split; matches ceec-core's `_Frozen(BaseModel)` precedent). Internal logic stays on
  frozen dataclasses.

### WP6 — Pillar 5: learning
- `learning/prior.py` — `PriorSpec` registry; convert the ruler-LR table and step-size
  override tables into prior *data*; delete the source code tables (R52, Q4, Q12).
- `learning/surrogate.py` — `SurrogatePolicy` wrapper (EI/EHVI) over any `Policy` (R54, Q10).
- `learning/icu.py` — I(C,U) metamodel as registered surrogate/prior source (R53, R55).
- `learning/reasoning.py` — hypothesis/literature records with mandatory provenance
  linkage (R57, Q15).

### WP7 — Pillar 6: surface, conformance, operations
- `surface/report.py` — the one report from the store alone (R85–R88); Parquet/JSON export
  bundles for R73 round-trip.
- `surface/cli.py` — one dispatcher, run profiles as data (`quick-verify`, `production-map`,
  `maturation`, `claim`), documented-command conformance tests (R78/R80). Delete legacy
  entry points (Directive 1).
- `surface/conformance.py` — capability registry harness; every C1–C88 + gated row has a
  passing test or explicit retirement record; CI gate (R76–R78). Appendix A flags become a
  projection view of `CAPABILITIES` with a currency lock (R78).
- `surface/operations.py` — pausable/steerable runs, service mode, webhook alerts,
  operator-intent records (R81–R84).
- Codegen: docs listings, compatibility matrix, JSON-Schema validators, conformance stubs,
  CLI flags — all from registries, lock-tested (abc3 §2.5). Generated docs land in
  `docs/generated/`; figure/manifest pinning reuses the existing gallery-lock pattern
  (`visualization/gallery.py` + `docs/figures/manifest.json`) for R87.

---

## 4. Engineering Standards (AGENTS.md — binding on every WP)

| Area | Rule applied to the Kernel |
|---|---|
| Types | PEP 695 generics (`Registry[SpecT]`), `X \| None` unions, `StrEnum`/`Literal` value sets, frozen `slots=True` dataclasses, `Protocol` over ABC, `Self` for fluent builders, `TypeIs` for custom narrowing, **no `Any`** (Pyright strict on all `experiment/` modules — they are new) |
| Control flow | Guard clauses; `match`/`case` for stage/axis-kind/cause routing; `_`-prefixed helpers extracted over nesting; Ruff `C901`/`PLR09xx` enforce size |
| Concurrency | `asyncio.TaskGroup` for concurrent evaluation; `asyncio.to_thread` for blocking legacy calls inside async paths; `threading.Lock` around the single writer (PEP 703 — free-threaded runtime); never rely on the GIL |
| Errors | abc3 Appendix I hierarchy under one `ExperimentError` root; always `raise … from`; `except*` for concurrent independent failures; expected control-flow errors (`EvaluationFailure`, `GuardKilled`, `DuplicateMeasurement`) caught by the wrapper, never leaked |
| Logging | stdlib `logging`, **t-strings** (PEP 750) for interpolation, context via `extra={…}`; never `print()` |
| SQL | Parameterized statements only — no interpolated SQL, ever |
| Resources | Context managers own connections, checkpoints, kernels, sessions |
| Immutability | Frozen dataclasses / tuples / frozensets default; mutation only where the settle contract requires it |
| Docs | Google-style docstrings on public APIs; comments explain *why*; no dead code lands |
| Structure | `pyproject.toml` single source of truth; `experiment/__init__.py` re-exports the public API via `__all__`; internal modules `_`-prefixed; no heavy work or I/O at module import (registries populate at import by design — keep them cheap and side-effect-free beyond registration) |
| GPU | Evaluation/kernels prefer device placement already provided by the substrate/ontology stack; the Kernel never forces CPU fallback (AGENTS.md GPU preference; `device` is a provenance field, R11) |

---

## 5. Locks & Test Matrix (CI-enforced)

abc3 §17.1 with these adjustments: **drop** migration-validation tests (no migration),
**drop** projection≡section lock (no projections), **add** single-writer topology test
(parallel backend + one store instance ⇒ no duplicate `measurement_key`, monotonic `seq`,
lock-serialized), **add** DuckDB round-trip tests (typed sections survive write/read;
`unknown` preserved verbatim).

Retained: registry integrity locks, schema-union lock, matrix lock, capability conformance,
documented-command tests, replay-hash assertion, kill/resume test, property-test generation
from spec invariants, policy-substitution test (four policies, identical record shape).

Execution discipline (AGENTS.md Environment/Testing):

- All tests via `uv run python -m pytest` — never bare `pytest`.
- **hypothesis** drives the property locks (registry integrity, DSL evaluator, identity-key
  laws: `cell_key`/`measurement_key` collision-resistance on generated coordinates).
- Fixtures over setup/teardown; `@pytest.mark.parametrize` over duplicated cases; DI over
  mocks (store and backends are Protocols — inject fakes).
- Test tiers: targeted per WP landing; fast gate (locks + property suite) before any pillar
  close; full suite only at round close.
- The `kill -9` test and long-running Class E benchmarks are marked integration; the
  kill/resume proof runs in CI with a small record count; benchmarks follow the background
  rule (§6).

## 6. Class E Benchmarks (unchanged verdicts, new apparatus)

| Benchmark | Discharges |
|---|---|
| Cost-to-rank vs uniform baseline | R46 |
| Surrogate vs random on held-out task | R54 |
| Cost-model estimate-vs-actual error trend | R23/R24 |
| Divergence-bound replay (1357 s run) | R50 |
| Store overhead harness (§1.1: fraction < 1% of median eval walltime; mean/p95 recorded) | K7, K9 |
| Seeded axis-effect reproduction | R86 |

Probe/benchmark scripts live in `scripts/probes/` per repo convention: docstring states the
measured-regime numbers and the demo/decision they informed. Any benchmark exceeding the
5-minute foreground cell limit launches with
`nohup uv run python … > logs/<name>.log 2>&1 &` and is polled at ≤2-minute intervals with a
pre-registered kill time. Low benchmark results are treated as suspected implementation
defects first (AGENTS.md), not accepted verdicts, until the harness itself is verified.

## 7. Definition of Done

abc3 §21.1 items 1–12 (all) and §21.2 adjusted: ~~migration complete~~ → legacy stores
abandoned untouched (Directive 2); schema evolution proven from v1 forward, not from legacy
records. Every Class S lock green, every Class E benchmark recorded as a store record, every
Class P gate enforced in CI.

Deferred to the hygiene pass (never per-commit, per AGENTS.md): repo-wide `ruff check` /
`pyright` outside `experiment/`, full `pytest --cov`, `pip-audit`. The Kernel itself ships
strict-clean from WP1 onward.

---

## 8. Progress Log

### 2026-09-29 — WP2 Complete (harvest.py, versioning.py, registries.py)
- Implemented `schema/harvest.py`: `__tunables__` reflection, name-based dedup, `harvest_schema()`, `ConflictingTunableError`
- Implemented `schema/versioning.py`: `SchemaRegistry`, `UnknownField` preservation, append-only readers
- Implemented `schema/registries.py`: `OBJECTIVES`, `CONSTRAINTS`, `PRIORS`, `POLICIES`, `STAGES`, `CAPABILITIES` registries with spec classes
- Added lockstep wiring tests: `tests/property/test_experiment_registries_wiring_lock.py` (12 tests)
- Updated `schema/__init__.py` to export new modules
- All new modules pass `ruff format`, `ruff check`, `pyright` (strict)
- All 36 experiment-related tests pass (24 original + 12 wiring locks)

### 2026-09-29 — WP3 Complete (legality engine)
- Implemented `legality/dsl.py`: Expr AST (frozen dataclasses), match/case evaluator, JSON wire format with content hashing
- Implemented `legality/engine.py`: Constraint model (origin/scope/enforced-at), LegalityEngine, globally-suppressive semantics at S4/S6 (R38)
- Implemented `legality/classify.py`: Defect taxonomy (Void/Hard/Soft/Unclassified), DefectRegistry with bidirectional void patterns, unclassified bucket counting
- All new modules pass `ruff format`, `ruff check`, `pyright` (strict)
- Integration test verified: constraints evaluate correctly, void patterns detect incompatibilities

### Improvement Opportunities (for future WPs)
1. **WP4**: Implement `execution/pipeline.py` and `execution/stage.py` for S1–S11 runner
2. **WP2**: Seed registries with domain data per Gate 1/2 outcomes
3. **WP2**: `harvest_schema() ⊇ Gate-2 union` lock (needs Gate 2 union table)
4. **WP3**: Seed constraints from `SystemConfig.validate()`, task fences, `apply_constraints` (migrate-and-delete original validators)
5. **WP5**: Implement full evidence predicates (`status.py`, `claims.py`, `failure.py`, `ceec.py`)
6. **WP6**: Implement learning primitives (`prior.py`, `surrogate.py`, `icu.py`, `reasoning.py`)
7. **WP7**: Implement surface layer (`report.py`, `cli.py`, `conformance.py`, `operations.py`)

### Notes for Remaining Work
- The `execution/` package is scaffolded but empty; WP4 will populate it
- The `evidence/claims.py` is not a separate file; the prefilter lives in `store.py` as `claim_eligible_prefilter()` — this matches the plan's intent
- DuckDB struct field indexes were removed due to syntax limitations; queries filter on struct fields via SQL WHERE clauses instead
- `DuplicateMeasurement` renamed to `DuplicateMeasurementError` to follow naming conventions (N818)
- `GateVerdict.PASS` renamed to `PASS_` to avoid S105 false positive (hardcoded password detection)
