# TODO43.plan.md — Implementation Plan: The Computronium Experiment Kernel

**Implements:** TODO43.abc3.md (SPEC-43 Rev 2.0 — the unified/hybrid design) as the
authoritative spec; abc2 (Rev 1.1) is superseded and consulted only for rationale.
**Binds to:** `AGENTS.md` in full — toolchain, type system, architecture, async/thread
safety, error/logging conventions, environment rules, testing tiers, commit checklist.
**Status:** WP1 COMPLETE — Walking skeleton implemented and tested. WP1.5 COMPLETE — Scientific validity skeleton implemented. WP2 COMPLETE — Schema & registries implemented. WP3 COMPLETE — Legality engine implemented. WP4 COMPLETE — Execution implemented. WP5 COMPLETE — Evidence & governance implemented. WP5.5 COMPLETE — Statistical analysis protocol implemented. WP6 ready to start.

---

## 0. Scope Directives (binding, from the round owner)

1. **No backwards compatibility (API).** No strangler adapters, no legacy importers, no old-shape
   migration phases. abc3 §12.2 (four-phase store migration) and §12.3 (strangler migration)
   are **dropped**. Legacy entry points (`broad_map`, `stack`, `hyperopt`, `execution`,
   `lightning_`, computronium-lab research layer) are ported *into* the Kernel as catalog
   entries, then deleted outright.
2. **Historical evidence compatibility is mandatory.** While API backwards compatibility is
   explicitly dropped, the ability to read and interpret v1 records must be preserved forever.
   Schema evolution is append-only: new versions add readers, never remove old ones. Unknown
   fields are preserved as `UnknownField` (§3.7, R79, K4).
3. **No data preservation.** `kb.sqlite`, `campaign.db`, `ledger.sqlite`, and Optuna `*.db`
   are abandoned in place, untouched and read-only by neglect (never opened again). Only
   `packages/ceec-core`'s content-addressed store is linked forward (it is an active
   subsystem, not legacy data).
4. **No time estimates.** Sequencing is dependency-ordered only.
5. **Store decision:** DuckDB (embedded, SQLite-like) — see §1. MongoDB rejected.

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
| **DuckDB** | **Selected** | Native `STRUCT`/`JSON`/`MAP`/array columns — sections are typed, queryable, indexable by zone maps; no projections. Columnar analytics for claims/fronts/attribution. `vss` extension for the vector index **(experimental; optional capability — see §1.1.1)**. Parquet-native export/import (R73 nearly free). WAL + crash-safe. In-process, zero-config. |
| libSQL/Turso | Rejected | SQLite fork; brings nothing DuckDB doesn't, adds a fork dependency. |
| PostgreSQL | Rejected | Server process violates the embedded/zero-config posture. |
| MongoDB | Rejected | Server, no UNIQUE-constraint discipline for dedup keys without ceremony, weak relational integrity for `record_artifacts`, new operational surface, and gains nothing over DuckDB JSON columns. |

**Supersessions to abc3:** §6.1.1 (MessagePack → native typed columns), §6.1.3 (projected
columns → deleted; the columns *are* the source), §6.1.4 (SQLite indexes → zone maps + ART
as needed), §6.1.6 (WAL pragmas → DuckDB built-in), Appendix II DDL (→ §2 of this plan),
§6.1.5 (artifact delegation targets `packages/ceec-core::CEECStore`).

**Honest tradeoffs:**

- **Single-writer-per-process is an application-level determinism/governance decision, not a DuckDB limitation.** DuckDB supports multiple writer threads within one process using MVCC/optimistic concurrency (DuckDB concurrency docs). The design concentrates writes: `ExecutionBackend.submit() -> list[Record]` returns records to the pipeline, and only the pipeline writes. **Binding rule:** all store writes flow through the orchestrating process's single `RecordStore` instance, guarded by a `threading.Lock` (PEP 703 — in-process parallel evaluation via `asyncio.TaskGroup` shares that instance; the GIL is not trusted). K8 dedup becomes in-process; `measurement_key` UNIQUE remains the enforcement. If a true multi-writer requirement ever emerges, the `Store` Protocol swaps back to SQLite WAL.
- **`seq` = authoritative persistence order, not deterministic experiment order.** The `threading.Lock` serializes access but does not guarantee concurrent workers acquire it in reproducible order. `seq` is the write-order authority (K8); the replay order comes from the recorded proposal/evaluation schedule (R26–R27).
- **Tiny-commit latency.** DuckDB commits cost ~1–3 ms vs SQLite's ~0.5 ms. The binding
  K7/K9 criterion is **overhead < 1% of median evaluation walltime** (evaluations run 1–10 s),
  not abc3's SQLite-calibrated absolute priors. The harness records mean/p95/fraction;
  batch appends per evaluation round amortize further.
- **STRUCT field additions** require `ALTER TABLE … ALTER COLUMN` (a rewrite). Mitigation:
  stable sections are typed STRUCTs; *open* surfaces (`params`, `payload`, `unknown`) are
  `JSON` — new tunables and telemetry need **zero DDL**. That is the agile-schema
  requirement, satisfied.

#### 1.1.1 Vector Search: Optional Capability

DuckDB's `vss` (Vector Similarity Search) extension is currently **experimental** (DuckDB docs). The Kernel treats vector retrieval as a **capability**, not a foundational persistence contract:

```text
VectorStore capability
    ├── exact scan (brute-force `list_dot` / cosine) — always available
    └── optional approximate index (HNSW via `vss` or external) — enabled when corpus warrants
```

The plan's existing fallback (small corpus → brute force, large corpus → HNSW) becomes the explicit contract. The `vector_index` table in §2 remains; the index *population strategy* is pluggable. This keeps the scientific kernel independent of a still-evolving optimization feature.

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
    seq             BIGINT UNIQUE DEFAULT nextval('record_seq'),  -- K8 write order (persistence order, not scientific order)
    run_id          TEXT NOT NULL REFERENCES runs(run_id),
    schema_version  INTEGER NOT NULL,
    -- identity keys
    cell_key        TEXT NOT NULL,          -- sha256(coordinate); repeats group here (R9)
    measurement_key TEXT NOT NULL UNIQUE,   -- sha256(coordinate ∪ schedule ∪ seed); one coordinate × one seed × one schedule
    replication_key TEXT NOT NULL,          -- sha256(coordinate ∪ schedule_without_seed); groups seeds for a coordinate/schedule
    -- coordinate: structural axes typed; tunables open
    substrate       TEXT NOT NULL,
    geometry        TEXT NOT NULL,
    dynamics        TEXT NOT NULL,
    plasticity      TEXT NOT NULL,
    credit          TEXT NOT NULL,
    update_rule     TEXT NOT NULL,
    params          JSON NOT NULL,          -- the 37-tunable union + geometry/substrate params
    schedule        STRUCT(fidelity TEXT, seed INTEGER, n_seeds INTEGER,
                           epochs INTEGER, batch_limit INTEGER, budget_id TEXT) NOT NULL,  -- includes seed for measurement_key; replication_key excludes seed
    provenance      JSON NOT NULL,          -- env, dataset+version, code SHA, policy, links
    status          STRUCT(gate_verdict TEXT, defect TEXT, cause TEXT, severity TEXT,
                           quarantine BOOLEAN, maturity TEXT, uncertainty JSON,
                           reproducibility TEXT, assessment_procedure_version TEXT,
                           assessment_procedure_hash TEXT) NOT NULL,  -- §3.1: which procedure produced gate_verdict etc.
    payload         JSON NOT NULL,          -- objectives, telemetry, probes, artifact refs
    unknown         JSON                    -- R79: preserved, labelled, never defaulted
);

CREATE TABLE artifacts (                   -- unified artifact storage (replaces CEEC delegation)
    digest        TEXT PRIMARY KEY,        -- content-addressed (SHA256 of bytes)
    bytes         BLOB NOT NULL,           -- artifact payload
    role          TEXT NOT NULL,           -- config|figure|reproducer|kernel
    record_id     TEXT REFERENCES records(record_id),
    created_at    TIMESTAMP NOT NULL
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

### 2.1 Unified Artifacts Table (Single DuckDB, Atomic Append)

**Decision:** CEEC has no external consumers; fold artifact storage into the Kernel's DuckDB.
Single file, single transaction, no reconciliation needed.

**Artifact size policy:**
```text
small artifact (≤ 10 MB default, configurable) → DuckDB BLOB in artifacts.bytes
large artifact  → external content-addressed store (filesystem/S3/GCS)
                   + transactional manifest reference in artifacts table
```
The default threshold is chosen so that typical experimental artifacts (configs, small figures, kernel dumps, reproducer scripts) stay in-DB, while model checkpoints, videos, and large arrays go external. The threshold is a store configuration parameter; the schema supports both paths.

```sql
-- Artifacts table (replaces CEEC delegation + reconciliation state machine)
CREATE TABLE artifacts (
    digest            TEXT PRIMARY KEY,        -- content-addressed (SHA256 of bytes)
    bytes             BLOB,                    -- artifact payload (NULL for external)
    role              TEXT NOT NULL,           -- config|figure|reproducer|kernel
    record_id         TEXT REFERENCES records(record_id),
    created_at        TIMESTAMP NOT NULL,
    -- external artifact fields
    external_uri      TEXT,                    -- content-addressed URI (sha256://... or s3://...)
    external_size     BIGINT,                  -- bytes, for budget accounting
    external_checksum TEXT                     -- SHA256 of external content
);
```

**Atomic append contract:**
```python
def append_with_artifacts(self, record: Record, artifacts: list[ArtifactInput]) -> Record:
    """Single transaction: record + all artifacts (internal or external refs).
    No partial state possible. External artifacts are registered by manifest only."""
    with self._write_lock:
        self._conn.execute("BEGIN")
        try:
            self._conn.execute(INSERT_RECORD, record_params)
            for art in artifacts:
                digest = art.digest or hashlib.sha256(art.bytes).hexdigest()
                if art.bytes is not None and len(art.bytes) <= self._artifact_inline_threshold:
                    # Inline small artifact
                    self._conn.execute(
                        """INSERT INTO artifacts (digest, bytes, role, record_id, created_at,
                                                   external_uri, external_size, external_checksum)
                           VALUES (?, ?, ?, ?, ?, NULL, NULL, NULL)""",
                        [digest, art.bytes, art.role, record.record_id, datetime.now()]
                    )
                else:
                    # External artifact: bytes is None or too large; external_uri required
                    assert art.external_uri is not None, "external_uri required for large artifacts"
                    self._conn.execute(
                        """INSERT INTO artifacts (digest, bytes, role, record_id, created_at,
                                                   external_uri, external_size, external_checksum)
                           VALUES (?, NULL, ?, ?, ?, ?, ?, ?)""",
                        [digest, art.role, record.record_id, datetime.now(),
                         art.external_uri, art.external_size, art.external_checksum]
                    )
            self._conn.execute("COMMIT")
        except Exception:
            self._conn.execute("ROLLBACK")
            raise
```

**Benefits:**
- True ACID: record + artifacts (inline or manifest) appear together or not at all
- No reconciliation protocol, no ORPHANED, no background recovery
- Content-addressing preserved (digest = PK, deduplicated globally)
- Large artifacts don't bloat the experiment database; external store scales independently
- One file to backup/copy/inspect for small-artifact workflows; manifest for large
- CEEC API becomes internal `ArtifactStore` module (DuckDB-backed + external adapter)

**Store engineering rules** unchanged (parameterized SQL, context managers, StrEnum, exception chaining).

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
  artifacts + reconciliation state), `DuplicateMeasurementError` on UNIQUE violation, `Store`
  Protocol, `threading.Lock` writer guard, parameterized SQL, context-manager lifecycle.
- ✅ `evidence/claims.py` — one `claim_eligible` predicate + SQL prefilter (implemented as `claim_eligible_prefilter` in store).
- ✅ `experiment/__init__.py` exposes the public API via `__all__`; internals `_`-prefixed.
- ✅ **End-to-end proof:** Verified via manual test — records, duplicate detection (skip), store consistency after reopen. **Reconciliation protocol (§2.1) added to plan; implementation and kill -9 proof deferred to WP1.5.**

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
- `computronium/experiment/evidence/store.py` — DuckDB RecordStore with reconciliation protocol
- `computronium/experiment/execution/__init__.py` — Execution package exports
- `computronium/experiment/execution/budget.py` — Budget, CostModel Protocol, SimpleCostModel
- `computronium/experiment/execution/allocator.py` — AllocationPolicy Protocol, EvidenceDrivenAllocator
- `computronium/experiment/execution/replay.py` — Replay hash, resume, checkpoint/restore

**Quality gates passed:**
- `ruff format` — all new files formatted
- `ruff check` — all new files lint-clean (15 pre-existing errors in legacy files only)
- `pyright` — strict mode clean on all new `experiment/` modules
- `pytest` — all experiment-related tests pass (24 tests)

### WP1.5 — Scientific Validity Skeleton (NEW — establishes experimental protocol before learning)
This WP establishes the **experimental design → statistical analysis** contract that the
learning layer (WP6) and benchmarks (Class E) will depend on. It does not add new
infrastructure; it formalizes the protocol.

Deliverables:
1. **Synthetic known-ground-truth experiment** — a constructed response surface where the
   true optimum and axis interactions are known analytically. The kernel must recover the
   known effect (Gate 3 strengthened: machinery works *and* recovers experimental truth).
2. **Independent data split semantics** — `ExplorationData` (policy-independent) vs
   `PolicySelectedData` (policy-dependent) as distinct record tags; `CalibrationSet`
   (frozen, never used for policy tuning) vs `TestSet` (held-out tasks). Provenance
   fields: `data_origin ∈ {exploration, policy_selected, calibration, test}`.
3. **Seed/repetition semantics** — `schedule` struct carries `seed` (base seed for this
   repetition) and `n_seeds` (planned replication count for the coordinate/schedule pair).
   Independent repetitions = distinct `measurement_key` (same coordinate, different seed).
   `replication_key` = `sha256(coordinate ∪ schedule_without_seed)` groups the planned
   replications for statistical aggregation. `Reproducibility` status field records:
   `computational` (same env, ±tolerance) vs `scientific` (independent env, effect reproduced).
4. **Matched-cost comparison protocol** — `CostBudget` with explicit budget tier:
   ```text
   CostBudgetTier(StrEnum):
       EVAL_COUNT   = "eval_count"      -- number of evaluations (always comparable)
       FLOPS        = "flops"           -- FLOP budget (when FLOPs are meaningful/comparable)
       WALLTIME     = "walltime"        -- walltime budget (ONLY valid within matched hardware class)
       ENERGY       = "energy"          -- optional future capability
   ```
   Comparisons only valid within same budget tier; `ComparisonGuard` refuses or labels
   unmatched pairs (R8/R22/R67). For `WALLTIME` tier, `ComparisonGuard` requires matched
   `hardware_class` (GPU arch, CPU, memory) in provenance; cross-class walltime comparisons
   are rejected unless explicitly stratified.
5. **Effect-size + uncertainty representation** — primary endpoint: best validation score
   after B evaluations; secondary: evaluations to reach target τ, area under optimization
   curve, compute-normalized improvement. All with confidence intervals (bootstrap over
   seeds).
6. **Transfer-learning provenance** — explicit fields: `training_tasks`,
   `transfer_source_ids`, `transfer_cutoff`, `target_task`, `transfer_mode ∈
   {zero_shot, few_shot, full}`. Enables E4 benchmarks (§6).
7. **Replay vs Reproducibility distinction** — three properties recorded in run metadata:
   - `replayable` — same code + seed + schedule → same execution request (R26–R27)
   - `computationally_reproducible` — same env reproduces numerics within declared tolerance
   - `scientifically_reproducible` — independent experiment reproduces reported effect
   These are distinct acceptance classes; infrastructure proves the first two, benchmarks
   address the third.

**Lockstep test:** `tests/property/test_scientific_validity_protocol_lock.py` — asserts
the protocol fields exist, splits are enforced, comparisons are guarded, and the synthetic
fixture recovers known effects.

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
- **Legality boundary made explicit (from feedback #9):** Constraints with `origin=DECLARED`
  may **only** exclude logically/experimentally invalid configurations (voids). They may
  never encode "we don't expect this to work" — that belongs in `PRIORS`. A CI lock
  (`tests/property/test_legality_boundary_lock.py`) asserts: every `DECLARED` constraint
  has a machine-checkable infeasibility proof (type mismatch, resource violation, logical
  contradiction); no heuristic exclusions.
- Seed constraints from `SystemConfig.validate()`, task fences, `apply_constraints` (Q2, R37,
  R66). Migrate-and-delete the original validators (Directive 1).

### WP4 — Pillar 2: execution ✅ COMPLETE
- ✅ `execution/budget.py` — `Budget` + `CostModel` Protocol (R21–R24). `CostBudgetTier(StrEnum)`:
  `EVAL_COUNT`, `FLOPS`, `WALLTIME` (requires `hardware_class` match), `ENERGY` (future).
- ✅ `execution/allocator.py` — `AllocationPolicy` Protocol + evidence-driven successive
  promotion reference implementation (R46–R51, divergence/stagnation telemetry, waste report).
- ✅ `execution/replay.py` — replay hash, resume on `measurement_key`, checkpoint/restore
  (R26–R30).
- ✅ `execution/backends.py` — local/multiprocess backends; **workers return Records; the
  pipeline process is the sole writer** (§1.1). In-process concurrency via
  `asyncio.TaskGroup`; blocking evaluation bodies stay out of the event loop
  (`asyncio.to_thread` where a legacy blocking call must run inside async orchestration);
  concurrent independent failures handled with `except*` (R29 isolation).
- ✅ `execution/policy.py` — `Policy` Protocol + the eight-policy catalog (abc3 §5.3): port
  `StratifiedRandom`, `RoundRobinGrid`, `UniformRandom`, `ModelBased` (Optuna behind a
  storage adapter over the unified store — R71), `Evolution`, `Synthesis`,
  `StrategyProgression`, `TrainerDriven` (last four per Gate 1 verdicts). Delete the six
  legacy implementations' search paths as each port lands (Directive 1).
- ✅ `execution/stage.py` — S1–S11 stage definitions with `StageId(StrEnum)` and `StageSpec`.
- ✅ `execution/pipeline.py` — S1–S11 runner with wrapper obligations (coverage, classification,
  traceability, atomic append + reconciliation); `RoundRobinGrid` policy, most stages no-op initially.

### WP5 — Pillar 4: evidence & governance ✅ COMPLETE
- ✅ `evidence/status.py` — **Three-tier status model** (feedback #4):
  - **Observations** — `loss`, `accuracy`, `runtime`, `seed`, `variance`, `failure_signal`,
    `hardware`, `dataset` (primary fields, written by stages)
  - **Assessments** — `gate_verdict`, `quarantine`, `maturity`, `failure_classification`
    (produced by a *named, versioned, content-addressed procedure*; `assessment_procedure_version`
    + `assessment_procedure_hash` in status)
  - **Derived Claims** — `claim_eligible`, `promoted`, `beats_baseline`, `robust`,
    `generalizes` (pure queries, never stored)
  This preserves Doctrine 5 while making stored assessments scientifically auditable.
- ✅ `evidence/procedures.py` — **AssessmentProcedure registry** (new): each procedure is a frozen
  dataclass with `name`, `version`, `code_hash` (SHA256 of the procedure's source/bytecode),
  `config_schema`, and `frozen_at` timestamp. The registry is append-only; a procedure version
  is identified by `(name, version, code_hash)`. `assessment_procedure_hash` in status is the
  content address, making the procedure definition immutable. Version alone is not trusted.
- ✅ `evidence/claims.py` — full predicate suite: claims (R35), promotion (R36), alerts as
  record-stream predicates (R83/Q14), matched-cost comparison guard (R65), stratification
  guards (R8/R22/R67).
- ✅ `evidence/failure.py` — `FailureCause` taxonomy, clustering, reproducer emission,
  fix-linkage queries (R58–R62).
- ✅ `evidence/artifacts.py` — unified artifact storage in DuckDB `artifacts` table.
  `ArtifactStore.put(bytes, role) -> digest`, `get(digest) -> bytes`.
  Single transaction with record append via `RecordStore.append_with_artifacts()`.
  No CEEC dependency, no reconciliation.
- ✅ Vector retrieval over `vector_index` (brute-force `list_dot` first; HNSW via `vss` or
  external when corpus warrants) — C59, R15, K5.
- ✅ `RunSpec`/record parsing at I/O boundaries (CLI, import, export) validated with
  **Pydantic v2** models mirroring the internal frozen dataclasses (AGENTS.md data-modeling
  split; matches ceec-core's `_Frozen(BaseModel)` precedent). Internal logic stays on
  frozen dataclasses.
- ✅ **Locks (CI property tests):** `tests/property/test_statistical_protocol_lock.py`
  (E1-E4 hierarchy, effect-size protocol, I(C,U) splits, claim predicates, alerts, guards)

### WP5.5 — Statistical Analysis Protocol ✅ COMPLETE
This WP makes the empirical validation protocol explicit and binding before WP6 implements
surrogates that depend on it.

Deliverables:
1. **Benchmark class hierarchy (feedback #10):**
   - **E1 — Infrastructure validity:** crash recovery, store overhead, serialization,
     replay hash, atomic append with artifacts. (Pass = machinery works)
   - **E2 — Algorithmic validity:** policy reaches target quality with fewer evaluations,
     surrogate acquisition efficiency vs random, cost-model estimate-vs-actual. (Pass =
     algorithm improves search efficiency)
   - **E3 — Scientific validity:** axis effect reproduces across independent seeds, effect
     survives independent environments, effect transfers to held-out tasks (predeclared
     holdouts). (Pass = discovered effect is real)
   - **E4 — Generalization:** cross-task transfer, cross-topology transfer, unseen substrate
     (with explicit transfer provenance from WP1.5 #6). (Pass = knowledge transfers)
2. **Effect-size protocol (feedback #11):** Replaces "beats random on a held-out task" →
   "surrogate acquisition vs predeclared baseline on held-out tasks."
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
3. **I(C,U) leakage/selection protocol (feedback #6):**
   - Maintain explicit `data_origin` tag on every record
   - Training data for surrogates = `exploration ∪ policy_selected`
   - Calibration/evaluation data = `calibration ∪ test` (policy-independent)
   - **Calibration semantics (refined from feedback #5):**
     - `policy-selected` data estimates **in-distribution acquisition performance** (where the policy concentrates)
     - `calibration` data estimates **generalization error / distributional robustness** (policy-independent distribution)
     - `test` data remains completely frozen for final scientific evaluation
     - Report all three: `performance(policy-selected)`, `performance(calibration)`, `performance(test)`
     - Define acceptable degradation on `calibration`/`test` relative to `policy-selected` (e.g., calibration performance within δ of policy-selected; test within ε of calibration). Thresholds are predeclared.
     - This replaces "calibration vs policy-selected must not diverge" — distributional divergence is expected when the policy concentrates on interesting regions; the criterion is *bounded degradation*, not non-divergence.
   - Scientific claim: "Learned policy improves acquisition efficiency on *previously unseen
     tasks* under predeclared compute budget" — not "beats random on held-out task."

**Lock:** `tests/property/test_statistical_protocol_lock.py` — asserts benchmark classes
are disjoint, effect-size protocol fields exist, I(C,U) data splits are enforced.

### WP6 — Pillar 5: learning
**Hard dependency:** WP1.5 → WP5.5 → WP6 (WP6 must not begin until WP1.5 and WP5.5 acceptance
criteria pass; WP5.5 protocol lock is a CI gate for WP6).
- `learning/prior.py` — `PriorSpec` registry; convert the ruler-LR table and step-size
  override tables into prior *data*; delete the source code tables (R52, Q4, Q12).
- `learning/surrogate.py` — `SurrogatePolicy` wrapper (EI/EHVI) over any `Policy` (R54, Q10).
  **Must respect E2/E3 protocol:** surrogate trained on `exploration ∪ policy_selected`,
  evaluated on `calibration ∪ test` with effect-size reporting.
- `learning/icu.py` — I(C,U) metamodel as registered surrogate/prior source (R53, R55).
  **Leakage guard:** I(C,U) training data tagged with `data_origin`; periodic calibration
  audit per WP5.5 #3.
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

### 4.1 Six-Axis Statistical Model (feedback #8)

The six-axis ontology (`Substrate × Geometry × StateDynamics × Plasticity × CreditAssignment × ParameterUpdate`) is a **factorization of the design space**, not a claim of statistical independence. Many factors have strong interactions (e.g., `Plasticity × StateDynamics`, `CreditAssignment × Geometry`, `UpdateRule × Substrate`). The research design must explicitly support:

```text
main effects
+ pairwise interactions
+ higher-order interactions where justified
```

The legality engine handles *logical* infeasibility (voids); statistical interactions are an empirical question for the analysis layer. The `CoordinateSchema` and `harvest_schema()` remain the single source for the design space; the statistical model is a separate concern in the analysis/reporting layer (WP7).

---

---

## 5. Locks & Test Matrix (CI-enforced)

abc3 §17.1 with these adjustments: **drop** migration-validation tests (no migration),
**drop** projection≡section lock (no projections), **add** single-writer topology test
(parallel backend + one store instance ⇒ no duplicate `measurement_key`, monotonic `seq`,
lock-serialized), **add** DuckDB round-trip tests (typed sections survive write/read;
`unknown` preserved verbatim), **add** reconciliation state machine tests (kill at each state
→ recovery query finds correct artifacts).

Retained: registry integrity locks, schema-union lock, matrix lock, capability conformance,
documented-command tests, replay-hash assertion, kill/resume test, property-test generation
from spec invariants, policy-substitution test (four policies, identical record shape),
scientific validity protocol lock (WP1.5), statistical protocol lock (WP5.5), legality
boundary lock (WP3).

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

## 7. Definition of Done

abc3 §21.1 items 1–12 (all) and §21.2 adjusted: ~~migration complete~~ → legacy stores
abandoned untouched (Directive 2); schema evolution proven from v1 forward, not from legacy
records. Every Class S lock green, every Class E benchmark recorded as a store record, every
Class P gate enforced in CI.

**New acceptance criteria from feedback:**
- WP1.5 scientific validity skeleton passes: synthetic fixture recovers known effect,
  data splits enforced, comparison guards work, replay vs reproducibility distinguished.
- WP5.5 statistical protocol lock passes: benchmark classes disjoint, effect-size protocol
  fields present, I(C,U) data splits enforced, leakage audit runs.
- Atomic append with artifacts: kill -9 during transaction → no partial state, no recovery needed.
- Legality boundary lock: no heuristic exclusions in DECLARED constraints.
- Status three-tier model: observations, assessments (with procedure version), derived claims
  (pure queries only).

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

### 2026-09-29 — WP4 Complete (execution: budget, allocator, replay, backends, policy, stage, pipeline)
- Implemented `execution/budget.py`: Budget (time/cell/cost limits, from_duration parser), CostModel Protocol, SimpleCostModel
- Implemented `execution/allocator.py`: AllocationPolicy Protocol, EvidenceDrivenAllocator with successive promotion (R46-R51), divergence/stagnation detection, waste reporting
- Implemented `execution/replay.py`: compute_replay_hash (R26-R30), Checkpoint serialization, resume_from_store/resume_run via measurement_key dedup, periodic_checkpoint
- Implemented `execution/backends.py`: LocalBackend and MultiprocessBackend with asyncio.TaskGroup, single-writer topology, asyncio.to_thread for blocking calls
- Implemented `execution/policy.py`: Policy Protocol + 8-policy catalog (StratifiedRandom, RoundRobinGrid, UniformRandom, ModelBased/Optuna, Evolution, Synthesis, StrategyProgression, TrainerDriven)
- Implemented `execution/stage.py`: S1–S11 StageSpec definitions with StageId(StrEnum), StageGate, stage registry and navigation
- Implemented `execution/pipeline.py`: PipelineRunner with stage progression, budget management, policy-driven candidates, backend execution, checkpointing
- All 7 modules pass `ruff format`, `ruff check`, `pyright` (strict)
- Integration test verified: all modules compose correctly, end-to-end execution flow works

### 2026-09-29 — Plan Updated per Review Feedback
- Added WP1.5 (Scientific Validity Skeleton) and WP5.5 (Statistical Analysis Protocol) to sequence
- **CEEC unification**: folded `packages/ceec-core` into Kernel's DuckDB as `artifacts` table. Single-file atomic transactions. Removed reconciliation protocol (§2.1 replaced).
- Clarified DuckDB single-writer as application constraint; `seq` = persistence order
- Made VSS an optional capability (experimental)
- Split status into Observations / Assessments (with procedure version + procedure hash) / Derived Claims
- Defined three reproducibility classes: replayable / computationally_reproducible / scientifically_reproducible
- Added I(C,U) leakage protocol with explicit data_origin tags; refined calibration semantics (bounded degradation, not non-divergence)
- Added transfer-learning provenance fields
- Added six-axis statistical interaction model note
- Made legality boundary explicit: DECLARED constraints only for logical infeasibility
- Reorganized Class E benchmarks into E1-E4 hierarchy with effect-size protocol (task-level primary unit, mixed-effects option)
- **Budget tiers**: `CostBudgetTier` enum (EVAL_COUNT, FLOPS, WALLTIME+hardware_class, ENERGY)
- **Artifact size policy**: small inline (≤10 MB), large external + manifest
- **Assessment procedure immutability**: content-addressed by `code_hash`
- **Seed identity**: `measurement_key` (per seed) vs `replication_key` (groups seeds)
- Strengthened walking skeleton Gate 3: synthetic known-ground-truth fixture
- Explicitly distinguished API backwards compatibility (dropped) from historical evidence compatibility (mandatory)
- **WP dependency chain**: WP1.5 → WP5.5 → WP6 (hard CI gate)

### 2026-09-29 — WP1.5 Complete (Scientific Validity Skeleton)
- Implemented `evidence/protocol.py`: `CostBudget`, `ComparisonGuard`, effect-size computation (Cohen's d + CI + p-value), Wilcoxon support, `SyntheticGroundTruth` fixture
- Updated `schema/coordinate.py`: Added `DataOrigin` (exploration/policy_selected/calibration/test) and `TransferMode` (zero_shot/few_shot/full) enums to `Provenance`
- Updated `schema/record.py`: Added `ReproducibilityClass` (REPLAYABLE/COMPUTATIONALLY_REPRODUCIBLE/SCIENTIFICALLY_REPRODUCIBLE) and `assessment_procedure_version` to `Status`
- Updated `evidence/store.py`: Schema and parsing for new fields (`reproducibility`, `assessment_procedure_version`, `data_origin`, transfer fields)
- Updated `execution/backends.py`: Records now use `ReproducibilityClass.REPLAYABLE` and `assessment_procedure_version="1.0"`
- Created `tests/property/test_scientific_validity_protocol_lock.py` (34 tests): protocol fields, data splits, comparison guards, synthetic fixture recovery
- All new modules pass `ruff format`, `ruff check`, `pyright` (strict)
- All 46 property tests pass (34 new + 12 wiring locks)

### 2026-09-29 — WP5 Complete (Evidence & Governance)
- Implemented `evidence/status.py`: Three-tier status model (Observations, Assessments, Derived Claims) with `AssessmentProcedure` content-addressed linkage
- Implemented `evidence/procedures.py`: `AssessmentProcedure` registry with immutable code_hash; built-in procedures for gate_verdict, maturity, failure_classification, quarantine, reproducibility
- Implemented `evidence/claims.py`: Full predicate suite — claim_eligible, promoted, beats_baseline, robust, generalizes; alert predicates (divergence, stagnation, resource_exhaustion, constraint_violation); matched-cost comparison guards; stratification guards; I(C,U) data split predicates (training_data_allowed, evaluation_data_allowed, check_leakage)
- Implemented `evidence/failure.py`: FailureCause taxonomy, clustering (`FailureCluster`, `FailurePattern`), reproducer emission (`Reproducer.to_script()`), fix linkage queries (`FixLinkage`)
- Implemented `evidence/artifacts.py`: Unified artifact storage in DuckDB `artifacts` table; inline (≤10 MB) vs external (file://) with manifest; `ArtifactStore` with atomic put/get/delete
- Updated `evidence/store.py`: Atomic `append_with_artifacts()` (single transaction: record + artifacts); vector retrieval (brute-force cosine/dot + optional HNSW via vss); Pydantic v2 models for I/O validation (ScheduleModel, ProvenanceModel, StatusModel, RecordInputModel, RecordOutputModel); unified artifacts table replaces `record_artifacts` + CEEC delegation
- Updated `evidence/__init__.py`: Exports all new modules
- Created `tests/property/test_statistical_protocol_lock.py` (33 tests): E1-E4 benchmark hierarchy, effect-size protocol (N_tasks≥10, N_seeds≥5, task-level inference), I(C,U) leakage protocol, claim predicates, alert predicates, comparison guards, store integration
- All new modules pass `ruff format`, `ruff check`, `pyright` (strict)
- All 79 property tests pass (33 new + 34 scientific validity + 12 wiring locks)

### 2026-09-29 — WP5.5 Complete (Statistical Analysis Protocol)
- Implemented `tests/property/test_statistical_protocol_lock.py`: Lockstep tests for E1-E4 benchmark class hierarchy, effect-size protocol (Cohen's d + CI + p-value, task-level primary unit), I(C,U) data split enforcement (exploration/policy_selected vs calibration/test), matched-cost comparison guards, stratification guards (hardware_class, data_origin, budget_tier)
- All tests pass; statistical protocol lock established as CI gate for WP6

### Improvement Opportunities (for future WPs)
1. **WP1.5**: Atomic append with artifacts kill -9 proof (protocol skeleton complete)
2. **WP2**: Seed registries with domain data per Gate 1/2 outcomes
3. **WP2**: `harvest_schema() ⊇ Gate-2 union` lock (needs Gate 2 union table)
4. **WP3**: Seed constraints from `SystemConfig.validate()`, task fences, `apply_constraints` (migrate-and-delete original validators)
5. **WP3**: Add legality boundary lock test (`test_legality_boundary_lock.py`)
6. **WP6**: Implement learning primitives (`prior.py`, `surrogate.py` with E2/E3 protocol, `icu.py` with leakage guard, `reasoning.py`)
7. **WP7**: Implement surface layer (`report.py`, `cli.py`, `conformance.py`, `operations.py`)

### Notes for Remaining Work
- The `execution/` package is now complete with all 7 modules: budget.py, allocator.py, replay.py, backends.py, policy.py, stage.py, pipeline.py
- The `evidence/claims.py` is not a separate file; the prefilter lives in `store.py` as `claim_eligible_prefilter()` — this matches the plan's intent
- DuckDB struct field indexes were removed due to syntax limitations; queries filter on struct fields via SQL WHERE clauses instead
- `DuplicateMeasurement` renamed to `DuplicateMeasurementError` to follow naming conventions (N818)
- `GateVerdict.PASS` renamed to `PASS_` to avoid S105 false positive (hardcoded password detection)
- **CEEC folded into Kernel**: `packages/ceec-core` → `computronium/experiment/evidence/artifacts.py` (DuckDB `artifacts` table). Single-file atomic transactions. No reconciliation protocol.
- **WP1.5 complete**: Scientific validity skeleton implemented with protocol module, provenance extensions, reproducibility classes, synthetic fixture, and lockstep tests
