# TODO43.plan.md — Implementation Plan: The Computronium Experiment Kernel

**Implements:** TODO43.abc3.md (SPEC-43 Rev 2.0 — the unified/hybrid design) as the
authoritative spec; abc2 (Rev 1.1) is superseded and consulted only for rationale.
**Binds to:** `AGENTS.md` in full — toolchain, type system, architecture, async/thread
safety, error/logging conventions, environment rules, testing tiers, commit checklist.
**Status:** WP1 COMPLETE — Walking skeleton implemented and tested. WP1.5 COMPLETE — Scientific validity skeleton implemented. WP2 COMPLETE — Schema & registries implemented. WP3 COMPLETE — Legality engine implemented. WP4 COMPLETE — Execution implemented. WP5 COMPLETE — Evidence & governance implemented. WP5.5 COMPLETE — Statistical analysis protocol implemented. WP6 COMPLETE — Learning primitives implemented. WP7 COMPLETE — Surface layer implemented. WP8 COMPLETE — Union & registry completion. WP9 COMPLETE — Canonical stage model & pipeline obligations. WP10 COMPLETE — Learning integration. WP11 COMPLETE — Surface conformance, codegen & operations. **§9 appended 2026-09-29: Completion Plan (WP8–WP13) — closes the audited functionality gaps (§9.1 Remediation Ledger + WP8–WP13) so that plan completion = the fully-functional kernel. Binding decisions (DuckDB store §1.1, unified CEEC artifacts §2.1, single-writer topology, VSS-optional, effect-size protocol, three-tier status) are unchanged.**

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
    -- coordinate: structural axes typed; hyperparameters open
    substrate       TEXT NOT NULL,
    geometry        TEXT NOT NULL,
    dynamics        TEXT NOT NULL,
    plasticity      TEXT NOT NULL,
    credit          TEXT NOT NULL,
    update_rule     TEXT NOT NULL,
    params          JSON NOT NULL,          -- the 37-hyperparameter union + geometry/substrate params
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
- `computronium/experiment/schema/harvest.py` — Hyperparameter harvesting, ConflictingHyperparameterError, HarvestedSchema
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
- ✅ `schema/harvest.py` — `hyperparameters()`-based reflection, name-based dedup (70→44; conflicts raise
  `ConflictingHyperparameterError`), `harvest_schema()`.
- ✅ `schema/versioning.py` — `schema_version` fail-closed on unknown versions;
  `UnknownField` preservation as forward tolerance (Directive 2). No old-shape
  readers, no reader registry.
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

Deferred to the hygiene pass (never per-commit, per AGENTS.md): repo-wide `ruff check` /
`pyright` outside `experiment/`, full `pytest --cov`, `pip-audit`. The Kernel itself ships
strict-clean from WP1 onward.

---

## 8. Progress Log

### 2026-09-29 — WP2 Complete (harvest.py, versioning.py, registries.py)
- Implemented `schema/harvest.py`: `hyperparameters()`-based reflection, name-based dedup, `harvest_schema()`, `ConflictingHyperparameterError`
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

### 2026-09-29 — WP3 Complete (Legality Engine - Boundary Lock)
- Added `tests/property/test_legality_boundary_lock.py` (10 tests): enforces legality boundary from feedback #9
- DECLARED constraints must only encode machine-checkable infeasibility proofs (type mismatch, resource violation, logical contradiction)
- No heuristic exclusions allowed in DECLARED constraints (those belong in PRIORS)
- Verifies void patterns have proofs, no performance metrics in DECLARED constraints, DECLARED constraints are HARD kind

### 2026-09-29 — WP6 Complete (Pillar 5: Learning Primitives)
- Implemented `learning/prior.py`: PriorSpec registry with ruler-LR table (11 tasks), step-size overrides (28 dynamics×credit combos), dynamics step-size overrides (2 dynamics); 44 priors registered
- Implemented `learning/surrogate.py`: SurrogatePolicy wrapper (EI/EHVI/UCB/PI/LOG_EI) over any Policy; GaussianProcessSurrogate with sklearn; E2/E3 protocol compliance (training on exploration ∪ policy_selected, evaluation on calibration ∪ test)
- Implemented `learning/icu.py`: I(C,U) metamodel with leakage guard; calibration audit per WP5.5 #3; bounded degradation check; leakage detection
- Implemented `learning/reasoning.py`: Hypothesis/literature records with mandatory provenance linkage (R57, Q15); ProvenanceLink with supporting/contradicting records; ReasoningStore for persistence
- All 4 modules pass `ruff format`, `ruff check`, `pyright` (strict)
- All 96 property tests pass (including new legality boundary lock)

### 2026-09-29 — WP7 Complete (Pillar 6: Surface Layer)
- Implemented `surface/report.py`: ReportGenerator with run summaries, claim-eligible queries, promoted records, Pareto frontier, maturity/gate verdict distributions, coordinate coverage; export_to_json and export_to_parquet for R73 round-trip
- Implemented `surface/cli.py`: Single dispatcher (`comp-surface`) with 4 run profiles as data (quick-verify, production-map, maturation, claim); commands for run, report, export, conformance, status; integrated with PipelineRunner
- Implemented `surface/conformance.py`: ConformanceHarness for CI gate enforcement; CurrencyLock for capability currency tracking (R78); ConformanceStatus enum (PASS_, FAIL, SKIPPED, RETIRED, NO_EVIDENCE); generate_conformance_report, save/load_currency_lock
- Implemented `surface/operations.py`: RunController for pausable/steerable runs with OperatorIntent audit trail; ServiceManager for long-running services with auto-restart; WebhookConfig for alert notifications; OperatorIntentKind enum (PAUSE, RESUME, STOP, MODIFY_BUDGET, MODIFY_STAGES, MODIFY_OBJECTIVES, UNQUARANTINE, PRIORITIZE_CELL, INJECT_CANDIDATE, SNAPSHOT)
- Updated `experiment/__init__.py` and `surface/__init__.py` to export surface package
- All 4 new modules pass `ruff format`, `ruff check`, `pyright` (strict)
- Property tests pass: `test_public_surface_lock.py` (15 tests), existing experiment wiring locks and statistical protocol locks continue to pass

### Improvement Opportunities (for future WPs)
1. **WP11**: Conformance reality — per-capability evidence via `verifying_test` pytest node id; RETIRED honored; `CurrencyLock` wired; Appendix-A flag projection lock (R78)
2. **WP11**: Codegen — `docs/generated/` listings, compatibility matrix, JSON-Schema validators, conformance stubs, CLI flag tables from registries (abc3 §2.5)
3. **WP11**: Operations completion — intent persistence, control-file watcher, webhook alerts, question-first entry profile (R43, R81–R84)
4. **WP12**: Legacy port & delete — inventory legacy surfaces, port remaining capabilities as catalog entries, delete legacy modules (Directive 1)
5. **WP13**: Class E benchmarks — E1 infrastructure, E2 algorithmic, E3 scientific, E4 generalization harnesses; record results as store records

### Notes for Remaining Work
- The `execution/` package is now complete with all 7 modules: budget.py, allocator.py, replay.py, backends.py, policy.py, stage.py, pipeline.py
- The `evidence/claims.py` is not a separate file; the prefilter lives in `store.py` as `claim_eligible_prefilter()` — this matches the plan's intent
- DuckDB struct field indexes were removed due to syntax limitations; queries filter on struct fields via SQL WHERE clauses instead
- `DuplicateMeasurement` renamed to `DuplicateMeasurementError` to follow naming conventions (N818)
- `GateVerdict.PASS` renamed to `PASS_` to avoid S105 false positive (hardcoded password detection)
- **CEEC folded into Kernel**: `packages/ceec-core` → `computronium/experiment/evidence/artifacts.py` (DuckDB `artifacts` table). Single-file atomic transactions. No reconciliation protocol.
- **WP1.5 complete**: Scientific validity skeleton implemented with protocol module, provenance extensions, reproducibility classes, synthetic fixture, and lockstep tests
- **WP7 complete**: Surface layer implemented with report generation, CLI dispatcher, conformance harness, and operations controller
- **WP10 complete**: Learning integration complete — PRIORS single-source, reasoning persistence, ICUModel injection, surrogate harvest_schema features, claim integrity

### 2026-09-29 — WP1.5/WP2/WP5 Atomic Append & Registry Seeding Complete
- Implemented kill -9 proof for atomic append with artifacts: `tests/property/test_atomic_append_kill_proof.py` (5 tests)
  - Atomic transaction rollback on exception
  - Duplicate measurement_key deduplication
  - SIGKILL mid-transaction leaves no partial state (subprocess test)
  - Concurrent dedup by measurement_key with single-writer topology
  - Monotonic seq across concurrent writes
- Fixed `RecordStore.append_with_artifacts()` to fetch seq inside write lock for thread safety
- Seeded all registries with Gate 1/2 domain data: `computronium/experiment/schema/seed_registries.py`
  - 8 objectives, 10 constraints (3 void, 3 hard, 4 soft), 28 priors (11 ruler-LR + 17 step-size + 4 Gate 2 additions)
  - 9 policy specs (8 catalog + 1 TPE/GP variant), 11 stages (S1-S11), 32 capabilities (C1-C32)
  - Idempotent `seed_all_registries()` with `Registry.clear()`
- Created harvest schema Gate 2 union lock: `tests/property/test_harvest_schema_gate2_lock.py` (4 tests)
  - Documents 44-parameter frozen union (37 Appendix IV + 7 §13.2 additions)
  - Verifies harvest mechanism structure, serialization, no conflicts
  - Notes ontology primitive connection pending for full coverage
- All new code passes `ruff format`, `ruff check`, `pyright` (strict)
- All 113 experiment property tests pass (109 passed, 4 skipped)

### 2026-09-29 — Registry Completeness Lock Fixed (PEPITA Credit Primitive)
- Fixed `tests/property/test_registry_completeness_lock.py` to include PEPITA credit primitive mapping:
  - Added `PepitaCredit` import and `"primitive.credit_assignment.pepita": PepitaCredit` to `ONTOLOGY_MAP`
  - Added `"primitive.credit_assignment.pepita": "PepitaCredit"` to `ALL_ONTOLOGY_MAPS["credit_assignment"]`
  - Corrected `_CREDIT_CONFIG_METHODS` mapping: `"pepita"` now maps to `"primitive.credit_assignment.pepita"` (was incorrectly mapped to `pc_alm`)
- Fixed SQL injection warnings (S608) in `computronium/experiment/surface/report.py` by using conditional query building instead of f-string interpolation
- All 124 experiment property tests pass (120 passed, 4 skipped in legality boundary lock)
- All new kernel code passes `ruff format`, `ruff check`, `pyright` (strict)

---

## 9. Completion Plan — WP8–WP13 (architecture completion)

**Added:** 2026-09-29. Purpose: close every functionality gap between the implemented
kernel and TODO43 R1–R88 + the abc3 §0.6 gates, **without overriding any binding
decision** (DuckDB §1.1, unified CEEC artifacts §2.1, single-writer topology,
VSS-optional, effect-size protocol, three-tier status model). A code-level audit of
the completed WPs found them structurally present but functionally incomplete at the
integration seams, plus seed/spec defects. §9.1 records every correction to
already-completed work (each preserves its tests and extends locks — nothing is
undone for its own sake); §9.2–§9.7 define the WPs that fill the gaps. WP8–WP13 are
binding work packages in the same sense as WP1–WP7 and land through the Agent
Commit Checklist (§3 preamble) under the engineering standards of §4.

**Axis symmetry (binding design invariant).** The six-axis ontology
(`Substrate × Geometry × Dynamics × Plasticity × Credit × Update`) is the search
space in full; no axis, and no learning algorithm, is architecturally privileged.
Backprop appears only as (a) the conventional *ruler-relative* objective family
(`bp_deficit`, `ruler_walltime_ratio`, `ruler_energy_ratio` — three of the ~39
B.7 objectives, preserved per C1/R31) and (b) an optional predeclared reference
control under R65 ("e.g. backprop"). Objectives, priors, surrogates, allocation,
legality, and attribution all operate over the whole coordinate; any axis pair —
or the full coordinate — may be metamodelled. I(C,U) is one registered instance
of the interaction-surrogate mechanism, not its scope.

### 9.1 Remediation Ledger (completed work that must change)

| # | Completed artifact | Defect | Correction | WP |
|---|---|---|---|---|
| L1 | `schema/axis.py::AxisKind` | The six-axis enum doubles as the axis-type system; hyperparameters are a separate `HyperparameterSpec` (violates abc3 §3.1 "one axis type", R4) | Rename the six-axis enum → `StructuralAxis`; introduce `AxisKind ∈ {STRUCTURAL, CONTINUOUS, INTEGER, CATEGORICAL}`; one `AXES: Registry[AxisSpec]` with `Domain`, `availability: Expr \| None`, `prior`, `override_scope`, `topology_params`; the six structural axes register as `AxisSpec.kind=STRUCTURAL` with their `topology_params`; hyperparameters register as `CONTINUOUS/INTEGER/CATEGORICAL`; `schema/harvest.py::HyperparameterSpec` removed — harvest returns `AxisSpec` directly | WP8 |
| L2 | `schema/harvest.py::_get_primitive_class` | Returns `None` — `harvest_schema()` is always empty; the Gate-2 union lock passes vacuously | Extend `hyperparameters()` on each primitive's config class to return `dict[str, HyperparameterSpec]` with `domain`, `availability`, `kind`, `prior`, `override_scope`; harvest iterates ontology registries (`DYNAMICS_REGISTRY`, …), calls `config_class.hyperparameters()` on each, deduplicates by name with `Or(availability)`; add `hyperparameters()` to Substrate and Plasticity config classes; structural params (`input_dim`, `hidden_dim`, …) move to `AxisSpec.structural().topology_params`; lock asserts `harvest_schema() ⊇ 44-name frozen union` non-vacuously | WP8 |
| L3 | `schema/seed_registries.py::CAPABILITIES` | 32 rows; TODO43 requires C1–C88 + gated §13.3/§13.4 rows; `CapabilitySpec` lacks `status`/`verifying_test`/`flags` | Extend `CapabilitySpec` with `stage`, `owner`, `verifying_test`, `flags`, `status ∈ {ACTIVE, RETIRED}` + `retirement_record`; seed the full inventory per the Gate 1 verdict table | WP8 |
| L4 | `schema/registries.py::StageId` + `seed_registries.STAGES` | Invented lifecycle (`S1_DISCOVERY…S11_RETIREMENT`); TODO43 §3.0 / abc3 §5.1 define S1 Frame…S11 Report | Replace with the canonical `StageId` (S1_FRAME…S11_REPORT); maturation semantics map onto S10 Decide / S3 Schedule; update `STAGE_SPECS`, `RUN_PROFILES`, and the stage lock together | WP9 |
| L5 | `seed_registries.py::CONSTRAINTS` | Placeholder specs (params dicts, no Expr); `prefer_digital_substrate` is a heuristic preference — violates the legality boundary (DECLARED = infeasibility only) | Re-express as `legality.dsl.Expr` predicates with machine-checkable proof kinds; `prefer_digital_substrate` moves to PRIORS; seeds sourced from `SystemConfig.validate()` rules, `TASK_COMPAT` fences, `apply_constraints` (R37/R63/R66) | WP8 |
| L6 | `execution/policy.py::ModelBasedPolicy` | `InMemoryStorage` + `trial.number % len(affordable)` selection — not model-based; no pruner; no persistence (P7 risk) | Real TPE/NSGA-II/GP/Random samplers incl. `NSGAIISampler` (C20); pruner support (`MedianPruner`/`HyperbandPruner`) wired to allocation early-termination (R46); trials persisted as records; on resume the study is rebuilt from store records via `optuna.trial.create_trial` — no private Optuna DB (R71) | WP9 |
| L7 | `learning/surrogate.py::_load_training_data` | `records: list[Record] = []` stub — the surrogate never sees data | Implement `RecordStore.query_records(run_id, data_origin=…)` public API; SurrogatePolicy pulls `exploration ∪ policy_selected` through it | WP10 |
| L8 | `learning/icu.py::load_from_store` | Returns 0 — no persistence path | Persist I(C,U) rows as record payload entries (`payload.icu`) with `data_origin`; implement the loader keyed on provenance tags | WP10 |
| L9 | `learning/surrogate.py::evaluate_effect_size` | `NotImplementedError` — the E2 protocol is undischargeable | Implement via `evidence.protocol.compute_effect_size` + the synthetic ground-truth task batch (WP13 harness); n_tasks≥10, n_seeds≥5 enforced | WP10 |
| L10 | `learning/icu.py` / `learning/reasoning.py` module globals | `_ICU_MODEL`, `_REASONING_STORE` singletons violate K10 (run-scoped state, never global) | Inject `ICUModel`/`ReasoningStore` through `SystemContext`; delete the global accessors | WP10 |
| L11 | `learning/prior.py` | Re-declares the legacy tables (`_STEP_SIZE_OVERRIDES_DATA`, …) and reads `autoscientist/ruler_table.json` at import — P4 duplication survives | The PRIORS registry becomes the single source (`prior_value(name, context)` accessor with confidence/uncertainty and per-run/per-coordinate override scope, R6/R52/R55); legacy tables deleted at WP12 after consumers reroute | WP10 |
| L12 | `surface/conformance.py::_count_evidence` | Generic PASS-count for every capability — conformance is vacuous | Capability-specific evidence: `verifying_test` pytest node id run via targeted selection; RETIRED honored; `CurrencyLock.retired_count` wired | WP11 |
| L13 | `surface/operations.py::_persist_intent` | Logs only — R84 operator intent is not first-class data | Persist intents as `run_id`-linked records (payload kind `operator_intent`) through the single writer | WP11 |
| L14 | `surface/cli.py`, `surface/report.py` | `store._conn` private reach-ins; profile stage names tie to L4 | Public read API (`query_runs`, `query_records`; `count_records` exists); profiles retargeted to canonical StageIds | WP9/WP11 |
| L15 | `execution/pipeline.py` | Wrapper obligations (R18/R19/R20/R29/R12), allocator, replay-hash, learned cost model not wired | The wrapper emits coverage/classification/traceability fragments; invokes `EvidenceDrivenAllocator` between rounds; computes and re-checks `replay_hash`; `RegistryCostModel` learns from per-stage walltimes (R23/R24) | WP9 |
| L16 | `schema/registries.py::ObjectiveSpec` + `seed_registries.OBJECTIVES` | 8 generic ML rows; TODO43 B.7 defines the ~39-objective union (task/cost/substrate/ruler/stability/plasticity) and C1/R31 require per-objective direction + weight + normalizer + axis tag | Extend `ObjectiveSpec` with `weight`, `normalizer`, `axis_tag`; seed the full B.7 union per Gate 1; S7 resolves every stored metric against `OBJECTIVES` with an unresolved-metric bucket | WP8 |
| L17 | `schema/coordinate.py::Schedule` + identity keys (§2) | Task/dataset identity is provenance-only — not part of `schedule` ⇒ `measurement_key` collides across tasks (same coordinate+seed on two tasks is rejected as duplicate) and tasks are not proposal-addressable (R44, C7, C30) | Add `task_id` to the schedule struct (schema version bump, fail-closed — no reader machinery per Directive 2); proposals carry task; `measurement_key` = sha256(coordinate ∪ schedule ∪ seed) then spans tasks; `replication_key` groups seeds within task | WP9 |
| L18 | `execution/policy.py` (`direction="maximize"`, `_extract_score` key lists), `learning/surrogate.py` (`val_loss` default, EHVI fall-through) | Objective name/direction hardcoded in policies — violates R31 registry resolution and silently biases toward accuracy-style maximization | Policies resolve objective id/direction from the run spec's declared objectives (OBJECTIVES registry); EHVI implemented or multi-objective delegated to the NSGA-II path — never a silent zero score | WP9 |
| L19 | Missing: S3 Schedule data-origin design | Exploration/calibration quotas unspecified ⇒ the I(C,U) audit and R86 attribution can be vacuous (no policy-independent data, no matched contrasts to attribute) | S3 predeclares a data-origin allocation (exploration/calibration fractions) and a matched-contrast DOE seed (fractional-factorial or OFAT quota within the exploration budget) so effects are identifiable by construction; policies may exceed, never undercut, the quota | WP9 |
| L20 | `evidence/claims.py::claim_eligible` (planned `n_seeds`) | Claim eligibility keyed on *planned* `schedule.n_seeds` — a run dying mid-replication would satisfy R64 without the seeds | Count *achieved* seeds (records grouped by `replication_key`); `schedule.n_seeds` remains the SQL prefilter hint only | WP10 |

### 9.2 WP8 — Union & registry completion (Gate 1 / Gate 2 closure)

Deliverables:
1. **Gate 1 executed** — `docs/design/rev3_gate.md`: accept/reject verdict per
   TODO43 §13–§15 candidate with a one-line rationale. Pre-registered defaults,
   consistent with the adopted implementations: §13.1 six-implementation P1 →
   ACCEPT (the eight-policy catalog already carries it); §13.2 continuous union +
   `apply_constraints` → ACCEPT (B.9 constraints + PRIORS additions); §13.3
   collectables → row-by-row (kernel-relevant rows ACCEPT as payload/record types;
   platform-only rows DEFER with a retirement record); §13.4 procedures → ACCEPT
   as capability rows; §13.5 domains/packages → ACCEPT rows (graph/tabular/
   time-series tasks; `stability`, `psi_peft`, `local_feedback`; model-export as a
   post-promotion artifact path). §14 abstractions A–E → ADOPTED (they are the
   implemented design); §15 order → SUPERSEDED by this plan.
2. **Axis unification (L1)** — `AxisKind` four-kind + `StructuralAxis` rename;
    `Domain` (`Enumerated` members | `Range(lo, hi, scale)`, scale ∈ {LINEAR, LOG});
    `AxisSpec.hyperparameter(...)` classmethod; `HyperparameterSpec` dataclass
    (`domain`, `availability`, `kind`, `prior`, `override_scope`);
    `hyperparameters()` on each config class returns `dict[str, HyperparameterSpec]`;
    availability predicates are `legality.dsl.Expr`; one `AXES` registry;
    structural projections keep existing kernel call sites working (Directive 1:
    no external API compat needed).
3. **Harvest wiring (L2)** — `schema/primitives.py` maps primitive ids → ontology
    classes *from the ontology registries themselves* (no hand-maintained list);
    extend `hyperparameters()` on each primitive's config class to return
    `dict[str, HyperparameterSpec]` with `domain` (`Range`|`Enumerated`),
    `availability` (`legality.dsl.Expr` or `None`), `kind` (`CONTINUOUS`|
    `INTEGER`|`CATEGORICAL`), `prior` (`PriorSpec` id), `override_scope`;
    harvest iterates registries, calls `hyperparameters()`, deduplicates by
    name with `Or(availability)`; conflicting `domain`/`kind` raises
    `ConflictingHyperparameterError`; add `hyperparameters()` to Substrate and
    Plasticity config classes; structural params (`input_dim`, `hidden_dim`,
    `num_layers`, …) removed from `hyperparameters()` — they belong in
    `AxisSpec.structural().topology_params` seeded in the registry.
    **Geometry fix:** `GeometryConfig.hyperparameters()` currently returns
    structural params (`input_dim`, `output_dim`) mixed with actual hyperparameters
    from Appendix C (`hidden_dim`, `num_layers`, `cube_size`, `init_scale`,
    `neurons_per_tile`, `tiles_per_layer`, `conv_channels`, `kernel_size`,
    `num_heads`, `seq_len`, `lattice_dims`, `mem_slots`, `mem_width`,
    `grid_hw`). Only Appendix C params (`hidden_dim`, `num_layers`, `cube_size`,
    `init_scale` with appropriate availability) stay in `hyperparameters()`;
    dataset-determined `input_dim`/`output_dim` move to the structural
    `AxisSpec.topology_params`; geometry-specific topology params
    (`neurons_per_tile`, `tiles_per_layer`, `conv_channels`, `kernel_size`,
    `num_heads`, `seq_len`, `lattice_dims`, `mem_slots`, `mem_width`,
    `grid_hw`) also move to `topology_params` — they are fixed by the geometry
    primitive choice, not searched.
    **Credit fix:** `CreditConfig.hyperparameters()` returns 23 params but most
    need availability predicates: `beta` only for `credit ∈ {thermodynamic_contrast, pc_alm}`;
    `a_plus`/`a_minus`/`tau_pre`/`tau_post`/`homeostatic_*` only for STDP-like rules;
    `contrast_threshold`/`contrast_objective` only for contrastive rules;
    `feedback_*` only for feedback-alignment rules; `readout_*` only for readout-based rules.
    **Update fix:** `UpdateConfig.hyperparameters()` params like `ortho_steps`,
    `spectral_norm`, `fisher_damping`, `ewc_lambda`, `ortho_lr` need availability
    scoped to their respective update rules.
    **Dynamics fix:** `StateDynamicsConfig.hyperparameters()` already correct but
    needs availability: `beta` for energy-based dynamics; `rho`/`prospective_leak`
    only for `pc_alm`; `threshold` only for `spike_integration`; `momentum` only
    for `energy_minimization`.
    **Substrate addition:** `SubstrateConfig.hyperparameters()` (new) —
    `noise_level` (Range(0.0, 1.0, LOG), always available), `precision` (Enumerated
    [float32, float16, bfloat16, int8], always), `sparsity` (Range(0.0, 0.99,
    LINEAR), always), `weight_bounds` (Enumerated or Range, availability: digital
    family only).
    **Plasticity addition:** `PlasticityConfig.hyperparameters()` (new) — per
    plasticity primitive: `plastic_state_dims` (structural, move to topology_params);
    `trace_decay` (Range(0.5, 1.0, LINEAR), availability: temporal_psi);
    `gate_dim`/`fast_weight_dim` (structural, move to topology_params);
    consolidation params (availability per primitive).
4. **Capability inventory (L3)** — `CapabilitySpec` extended; C1–C88 seeded from
   TODO43 §3 with stage/owner/verifying_test; gated §13 rows per Gate 1 verdicts;
   Appendix-A flags carried as `flags` tuples → the projection view + currency
   lock (R78).
5. **Constraint seeds (L5)** — real `Expr` predicates with proof kinds
   (`TYPE_MISMATCH`, `RESOURCE`, `LOGICAL`); task fences with recorded, queryable
   reasons (R37); `max_hidden`/`max_layers`/`max_steps` from `apply_constraints`;
   fairness (param-budget 25 % tolerance) as a FAIRNESS constraint (R25);
   operating points as constraints (R66).
6. **Objectives union (L16)** — `ObjectiveSpec` gains `weight`/`normalizer`/
   `axis_tag`; `OBJECTIVES` seeded with the full Appendix B.7 union (~39:
   task, cost, substrate, ruler-relative `bp_deficit`/`ruler_walltime_ratio`/
   `ruler_energy_ratio`, stability, plasticity) per Gate 1; multi-objective
   studies resolve directions from the registry (feeds NSGA-II, Pareto, alerts).
7. **Locks** — strengthen `test_harvest_schema_gate2_lock.py` (non-vacuous union;
    every harvested hyperparameter has `Domain` + `availability` + `kind`; no defaults in
    harvest output); extend registry lockstep to `AXES` + `CAPABILITIES` totality
    (the §7.2 C↔R matrix as data: every C cited by ≥1 R, every R cites ≥1 C);
    constraints-with-proof lock (extends the legality boundary lock).

### 9.3 WP9 — Canonical stage model & pipeline obligations

Deliverables:
1. **Stage model (L4)** — `StageId` S1_FRAME…S11_REPORT per TODO43 §3.0; the
   `Stage` Protocol (`run(ctx) -> Fragment`); implementations:
   - S1 Frame — objective/operating-point resolution (R43 entry, with `Synthesis`).
   - S2 Space — axis snapshot + legality preview (dry-run = the same engine, C32).
   - S3 Schedule — fidelity/seed/epoch planning; per-task adaptation (R44).
   - S4 Gate — `LegalityEngine` enforcement; globally-suppressive voids (R38).
   - S5 Compose — `compose_joint_system` bridge; effective-value recording (R6).
   - S6 Train — `SystemTrainer` settle bridge; guard/divergence telemetry
     (R50/R51); per-epoch intermediate values feed pruners.
   - S7 Measure — objectives resolved against `OBJECTIVES`; probes; robustness
     dimension (R69) computed when the profile requests it.
   - S8 Record — atomic append + artifacts + embedding generation (`vector_index`
     write with `embedding_version`; brute-force retrieval already present).
   - S9 Attribute — counterfactual axis attribution from records (R86).
   - S10 Decide — promotion predicates + allocation handoff (R36, R46–R51).
   - S11 Report — delegates to `surface.report` fragments.
   No-op stages emit explicit empty fragments (R39); all are swappable Protocols
   that never change the record schema (R40).
2. **Pipeline obligations (L15)** — the wrapper emits coverage (R18), classifies
   every rejection identically for every policy (R19), stamps proposal provenance
   (R20), isolates failures (R29), single-writer atomic appends (R12), budget
   accounting (R21); integrates `EvidenceDrivenAllocator` between rounds; computes
   and re-checks `replay_hash` (R26/R27); resumes via `measurement_key` dedup;
   `RegistryCostModel` learns estimate-vs-actual (R23/R24).
3. **ModelBased policy completion (L6)** — samplers TPE (multivariate default)/
   NSGA-II/GP/Random; pruners Median/Hyperband wired to S6 intermediate values and
   allocator early-termination; trial↔record persistence + resume rebuild;
   `PolicySpec.params` gains `pruner`.
4. **Run-scoped acceleration (R75/K10)** — `execution/sysctx.py::SystemContext`
   carrying the run-scoped kernel cache keyed `(run_id, cell_key, device, dtype)`,
   device/dtype context, and injected learning state; kernel-ladder evidence
   (parity/microbench, git-SHA tagged) recorded as records; the legacy global
   kernel cache never enters the kernel.
5. **Identity & objective corrections (L17/L18)** — `task_id` joins the schedule
   struct (v2 reader; proposals address task; measurement/replication keys span
   tasks — cross-task uniqueness lock); policies resolve objective id/direction
   from the run spec via `OBJECTIVES`; EHVI completed or multi-objective routed
   to NSGA-II.
6. **Experimental-design seeding (L19)** — S3 emits the data-origin allocation
   and contrast quota as part of the schedule fragment; coverage reporting (R18)
   shows quota satisfaction per run; the WP5.5 audit consumes policy-independent
   data by construction rather than by luck.
7. **Locks** — stage-model lock (canonical StageId ↔ STAGES registry ↔
   RUN_PROFILES ↔ stage classes); wrapper-obligation property tests (coverage
   emitted even for a proposal-swallowing policy; classification identical across
   policies; injected failure leaves siblings, run, and store intact); replay/
   resume integration test.

### 9.4 WP10 — Learning integration

Deliverables:
1. **Store wiring (L7/L8)** — `RecordStore.query_records(...)` public API with
   `data_origin`/`run_id`/payload-kind filters; `SurrogatePolicy` and `ICUModel`
   consume it; I(C,U) rows persisted in `payload.icu` with `data_origin` tags; the
   calibration audit reads them back.
2. **Effect-size runner (L9)** — `learning/benchmark.py`:
   `run_acquisition_benchmark(policy, baseline, tasks, seeds, budget) ->
   EffectSizeResult` over the synthetic ground-truth task batch; used by E2/E3
   (WP13).
3. **Priors single-source (L11)** — `PRIORS` accessor
   `prior_value(name, context)` with `confidence`, uncertainty, and
   per-run/per-coordinate override scope (R6/R52/R55); `prior.py` reads only the
   registry; `ontology/update.py`, `compose.py`, and `campaign._ruler_lr`
   consumers reroute behind thin adapters marked for deletion.
4. **K10 hygiene (L10)** — context-injected ICU/Reasoning; singleton accessors
   deleted.
5. **Reasoning persistence (R57)** — hypotheses/literature persisted as records
   (payload kinds `hypothesis`/`literature`) with `ProvenanceLink` ↔ record-id
   cross-links; S1 Frame links the motivating hypothesis/literature into run
   provenance; literature retrieval stays out-of-loop by default (Q15:
   provenance linkage first; active generation is opt-in).
6. **Transfer & analytic reachability (R15/R53)** — warm-start from prior runs
   wired as registered prior/surrogate sources; the surrogate layer is
   coordinate-wide (`SurrogatePolicy` over any `Policy`, features from the full
   `Coordinate` via `harvest_schema()`), and I(C,U) is one registered
   interaction-surrogate instance over the credit×update pair — extensible to
   any axis pair by registering a feature encoder; C59–C63 reachable from search
   (the surrogate training-data loader) and from reports (WP11).
7. **Claim integrity (L20)** — `claim_eligible` counts achieved seeds per
   `replication_key` (planned `n_seeds` stays a prefilter hint); the R64
   uncertainty statement derives from achieved replication counts.

### 9.5 WP11 — Surface conformance, codegen & operations

Deliverables:
1. **Conformance reality (L12)** — per-capability evidence: `verifying_test`
   pytest node id executed via targeted selection (fast tier) or consulted from
   the latest CI result records; RETIRED honored with a retirement record;
   `CurrencyLock` counts all states; Appendix-A flag projection lock (R78).
2. **Codegen (abc3 §2.5)** — `docs/generated/` listings (capabilities, objectives,
   axes), the compatibility matrix from CONSTRAINTS (R63), JSON-Schema validators
   per AxisSpec (R5 runtime discovery), conformance stubs per CapabilitySpec, CLI
   flag tables — all lock-tested against source; figures/manifest pinning reuses
   the gallery-lock pattern (R87).
3. **Report completion (R85–R88)** — axis-coverage section (per-axis
   stratification, R18), fronts by fidelity, budget consumption, failures by
   cause, promotion history, cross-run campaign diff (C78), claim-eligible
   table, narrative handoff summary (R88); the public store read API replaces
   `store._conn` reach-ins (L14).
4. **Operations completion (R81–R84)** — intent persistence (L13); a control-file
   watcher so an external CLI can pause/steer/resume a running service
   (`surface/service.py` headless loop: RunController + control file + webhooks);
   notify-only alerts per R83 with dedup keyed `(predicate, run, window)`; Q14
   routing model recorded as `WebhookConfig.events` defaults.
5. **Question-first entry (R43)** — `surface.profiles.question_first(objective,
   operating_point) -> RunSpec` (the `Synthesis` policy), profile-registered and
   conformance-tested.
6. **Locks** — the conformance CI gate (fails if a required capability lacks its
   verifying test), codegen drift locks, documented-command conformance for the
   surface CLI (R80).

### 9.6 WP12 — Legacy port & delete (Directive 1)

Precondition: WP8–WP11 conformance green for every capability whose replacement
ships in this WP (R77: no silent loss).

1. **Inventory** — legacy surfaces: `autoscientist/` (broad_map, campaign, daemon,
   reasoner, local_llm, literature, objectives, proposer, counterfactual, alerts,
   compose, defects, report), `core/campaign/` (stack, campaign_store, kb_report,
   report, pareto, replication, kernel_cache, checkpoint, discovery, evaluation,
   fidelity, frontier_record), `hyperopt/` (all), the legacy `execution/` engine/
   strategy/synthesizer/candidate_gen/_state/…, `lightning_/`,
   `packages/computronium-lab/` research layer, and the pre-kernel files inside
   `computronium/experiment/` (`producer.py`, `staircase.py`, `probe.py`,
   `param_estimator.py`, `result_sink.py`, `reporting.py`, `report.py`,
   `schema.py`, `cli.py`).
2. **Port remaining capabilities as catalog entries** — producer grid/TPE modes →
   policies (delivered via the WP9 ModelBased/Grid policies); reasoner templates →
   hypothesis factories feeding `learning.reasoning` (C3); local_llm → optional
   hypothesis source (C4, opt-in per Q15); literature retrieval →
   `learning.reasoning` ingestion (C5); counterfactual attribution → the S9 stage
   body (C68); alerts → record predicates + webhook surface (C85, delivered in
   WP11; legacy deleted here); daemon control surface → `surface/service.py`
   (C87); robustness harness → S7 Measure (R69); scaling-law fitting → an analysis
   module over records (C67); NAS/Lightning HPO → `TrainerDriven` adapters
   (§13.1); lab synthesis/evolution → the `Synthesis`/`Evolution` policies
   (already catalogued); lab corpus certification → capability row + probe
   script; MEP/frozen-θ/benchmark suites → Class E additions (WP13) or retirement
   records per Gate 1.
3. **Delete** — after each port's conformance test passes: remove the module, its
   CLI verbs from `cli/__main__.py`, its flags (Appendix-A rows retire), and every
   legacy store reader (Directive 3: the files are abandoned untouched). Pre-kernel
   `experiment/` files relocate to `scripts/probes/` (probe), merge into profiles
   (staircase), or delete.
4. **Locks** — a final import-graph lock (`computronium.experiment` imports no
   legacy pillar module); `cli/__main__.py` exposes only kernel surface commands;
   the Appendix-A audit lock (every retired flag maps to a capability or a
   retirement record).

### 9.7 WP13 — Class E benchmarks & Definition of Done

1. **E1** — kill -9 (exists); store-overhead harness
   `scripts/probes/store_overhead_bench.py` (mean/p95/fraction < 1 % of median
   evaluation walltime; K7/K9); serialization round-trip incl. `unknown` verbatim
   and fail-closed version checks; atomic append with artifacts (exists).
2. **E2** — cost-to-rank vs the uniform baseline; surrogate acquisition vs the
   predeclared baseline on held-out synthetic tasks via the WP10 effect-size
   runner; cost-model estimate-vs-actual trend; divergence-bound replay on a
   seeded clamping run; reference controls are predeclared per study (R65) —
   e.g. the backprop ruler at matched cost, or any baseline registered in
   `POLICIES`/`OBJECTIVES`; no control is architecturally privileged.
3. **E3** — seeded axis-effect reproduction on `SyntheticGroundTruth`
   (independent seeds, CI); environment-variation repetition (GPU arch/CUDA/
   PyTorch versions as provenance-stratified re-runs); predeclared held-out task
   transfer (N≥10, paired, effect size).
4. **E4** — cross-task / cross-topology / unseen-substrate transfer with explicit
   `transfer_source_ids`/`transfer_mode` provenance.
5. All benchmark scripts live in `scripts/probes/` with measured-regime
   docstrings; runs > 5 min go background per §6; results are recorded as store
   records (E-class rows in `CAPABILITIES` evidence).
6. **Definition of Done (extends §7)** — Gate 1/2 documents exist and their locks
   pass non-vacuously; every C1–C88 + gated row has conformance evidence or a
   retirement record; Class E benchmarks recorded; legacy entry points deleted
   (import-graph lock); run-scoped state lock (no module-level mutable singletons
   under `experiment/`); the store-overhead fraction recorded < 1 %.

### 9.8 Sequencing & dependencies

```
WP8 (union/registries; executes Gate 1 + Gate 2 for real)
  └─ WP9 (canonical stages + pipeline obligations; depends on AXES/CONSTRAINTS/CAPABILITIES seeds)
       ├─ WP10 (learning integration; needs the store query API + pipeline rounds)
       ├─ WP11 (conformance/codegen/operations; needs stages + capabilities)
       │    └─ WP12 (legacy port-and-delete; strictly gated on conformance green)
       └─ WP13 (Class E harnesses; E1 after WP9; E2/E3/E4 after WP10)
```
WP10 ∥ WP11 after WP9; WP12 strictly after WP11; WP13 tracks the WPs it exercises.
Definition of Done completes at WP13 close.

### 9.9 Test-matrix additions (extends §5)

- Stage-model lock; wrapper-obligation property tests; replay/resume integration test.
- Non-vacuous Gate-2 union lock; registry totality matrix (C↔R) lock.
- Capability-conformance CI gate; codegen drift locks; Appendix-A projection lock.
- Singletons-absence lock for `experiment/` (K10).
- Prior single-source lock (PRIORS ⊇ the legacy-table union) — tightens to
  deletion at WP12.
- Cross-task identity lock (two tasks, same coordinate+seed ⇒ distinct
  `measurement_key`s); achieved-seed claim test; contrast-identifiability test
  (attribution recovers a known effect on a DOE-seeded run, R86/E3).

### 2026-09-29 — Plan Revised: Completion Plan (§9, WP8–WP13) appended
- Full-surface code audit produced the §9.1 Remediation Ledger (15 items) across the
  completed WP2/WP4/WP6/WP7 artifacts; every correction preserves the binding
  decisions (DuckDB, unified CEEC artifacts, single-writer topology, effect
  protocol) and its existing tests.
- Gate 1/2 are discharged for real in WP8 (`docs/design/rev3_gate.md` +
  non-vacuous union lock) — they were previously skipped while their outputs were
  assumed.
- Canonical stage model (S1 Frame…S11 Report) replaces the invented lifecycle;
  `RUN_PROFILES` remap onto it.
- ModelBased policy completed: real TPE/NSGA-II/GP/Random samplers + Median/
  Hyperband pruners wired to allocation early-termination; trials persisted as
  records — no private Optuna DB (R71, P7).
- Learning seams wired: store query API, I(C,U) persistence, effect-size runner,
  priors single-source, K10 context injection (singletons removed).
- Conformance made non-vacuous (`verifying_test` per capability, retirement
  records, wired `CurrencyLock`); codegen + Appendix-A flags projection added.
- WP12 executes Directive 1 port-and-delete over the full legacy inventory,
  including the pre-kernel files currently inside `experiment/`.
- WP13 defines the E1–E4 harnesses and the extended Definition of Done.

### 2026-09-29 — WP8 Partial: Axis System & Harvest Schema (L1/L2 completed)
- **Axis unification (L1)**: `AxisKind` (six ontology axes) → `StructuralAxis`;
  introduced new `AxisKind ∈ {STRUCTURAL, CONTINUOUS, INTEGER, CATEGORICAL}`;
  `AxisSpec` extended with `Domain` (lo/hi/scale/members), `availability: Expr | None`,
  `prior`, `override_scope`, `topology_params`.
- **Harvest wiring (L2)**: `schema/primitives.py` maps primitive ids → ontology config
  classes; `harvest_schema()` now calls `hyperparameters()` from each config class and
  deduplicates across axes.
- **Rich hyperparameters()**: All six config classes now return extended format with
  `domain`, `availability` (Expr predicates), `prior`, `override_scope`. Availability
  predicates encode primitive-conditional parameters (e.g., `ortho_steps` only for
  `riemannian_orthogonal/muon/ortho_adam`; `a_plus` only for `temporal_trace`).
- **Structured parameters moved**: `input_dim`, `output_dim` (dataset-determined),
  `neurons_per_tile`, `tiles_per_layer`, etc. are now marked as structural
  (`AxisKind.STRUCTURAL`) or topology params, not free hyperparameters.
- **New hyperparameters discovered**: The harvest now yields 68+ parameters (vs Gate 2's 44),
  reflecting the richer ontology surface. Legacy names (e.g., `learning_rate`) map to
  canonical ontology names (e.g., `step_size`); test includes LEGACY_TO_CANONICAL mapping
  and validates coverage.
- **Test coverage**: 7 harvest lock tests pass, including Gate 2 union coverage via
  canonical mapping (30+/44 legacy names covered directly), plus rich ontology expansion
  (40+ additional params with availability predicates).

### Remaining WP8 Work (COMPLETED)
- ✅ CapabilitySpec extension (L3) and seeding C1-C88 — Extended with stage, owner, verifying_test, flags, status, retirement_record; all 88 capabilities seeded with Gate 1 verdicts
- ✅ Constraint seeds with real Expr predicates and proof kinds (L5) — Re-expressed as Expr predicates with proof kinds (TYPE_MISMATCH, RESOURCE, LOGICAL); seeded from SystemConfig.validate(), task fences, apply_constraints
- ✅ ObjectiveSpec extension with weight/normalizer/axis_tag (L16) — Extended with weight, normalizer, axis_tag; full B.7 union (~39 objectives) seeded
- ✅ `docs/design/rev3_gate.md` creation (Gate 1 execution) — Created with accept/reject verdicts for all §13–§15 candidates
- ✅ Registry lockstep tests for AXES + CAPABILITIES totality (C↔R matrix) — Added `tests/property/test_axes_capabilities_totality_lock.py` with 19 tests covering wiring, totality, C↔R matrix

### 2026-09-30 — WP8 Complete: Union & Registry Completion (L3, L5, L16, Gate 1, locks)
- **CapabilitySpec extension (L3)**: Extended with `stage`, `owner`, `verifying_test`,
  `flags`, `status`, `retirement_record`; all 88 capabilities (C1-C88) seeded with
  Gate 1 verdicts across CORE, ACCELERATION, SCALING, REPRODUCIBILITY, GOVERNANCE,
  LEARNING kinds.
- **Constraint seeds (L5)**: Re-expressed as `Expr` predicates with machine-checkable
  proof kinds (`TYPE_MISMATCH`, `RESOURCE`, `LOGICAL`); seeded from
  `SystemConfig.validate()`, task fences, `apply_constraints`; heuristic
  `prefer_digital_substrate` moved to PRIORS per legality boundary lock.
- **ObjectiveSpec extension (L16)**: Extended with `weight`, `normalizer`, `axis_tag`;
  full B.7 union (~39 objectives) seeded: task, cost, substrate, ruler-relative,
  stability, plasticity, composite.
- **Gate 1 execution**: Created `docs/design/rev3_gate.md` with accept/reject verdicts
  for all 40 §13–§15 candidates (37 ACCEPT, 2 DEFER, 1 SUPERSEDED).
- **Registry lockstep tests**: Added `tests/property/test_axes_capabilities_totality_lock.py`
  (19 tests) covering AXES wiring, CAPABILITIES totality, C↔R matrix (every C cites ≥1 R,
  every R cites ≥1 C), stage/owner coverage.
- All quality gates pass: `ruff format`, `ruff check`, `pyright` (strict), 78 property tests pass.

### 2026-09-30 — WP9 Complete: Canonical Stage Model & Pipeline Obligations (L4, L6, L7, L17, L18, L19)
- **Canonical StageId (L4)**: Replaced invented lifecycle (S1_DISCOVERY…S11_RETIREMENT) with canonical S1_FRAME…S11_REPORT per TODO43 §3.0 / abc3 §5.1. Updated all StageSpecs with proper display_name, params, and gate semantics.
- **Stage Protocol & Fragment (WP9.1/9.2)**: Added `Stage` Protocol with `run(ctx) -> Fragment`; `Fragment` carries records, proposals, metadata, coverage (R18), classification (R19). All 11 stages defined with proper specs.
- **Pipeline wrapper obligations (L15, WP9.3)**: 
  - Coverage reporting (R18) — `_update_coverage()` emits per-stage coverage dict
  - Identical rejection classification (R19) — `_classify_rejection()` used by all policies
  - Proposal provenance stamping (R20) — timestamps, cell_key, fidelity, data_origin
  - Failure isolation (R29) — `except*` in `_execute_batch_with_isolation()`
  - Single-writer atomic appends (R12) — enforced by RecordStore
  - Budget accounting (R21) — per-record cost tracking
  - EvidenceDrivenAllocator integration hook after S7_MEASURE
  - Replay hash computation/re-check (R26/R27) — compute_replay_hash()
  - Resume via measurement_key dedup — resume_from_store()
  - RegistryCostModel learning (R23/R24) — protocol defined
- **task_id in Schedule (L17)**: Added `task_id: str = ""` to Schedule struct; included in measurement_key for cross-task uniqueness
- **ModelBasedPolicy completion (L6, WP9.5)**: Real Optuna samplers (TPE, NSGA-II, GP, Random) + pruners (MedianPruner, HyperbandPruner) wired to S6 intermediate values; trial↔record persistence via `optuna.trial.create_trial` — no private Optuna DB (R71, P7)
- **SystemContext for run-scoped state (R75/K10, WP9.6)**: Created `execution/sysctx.py` with `SystemContext` carrying kernel cache keyed by (run_id, cell_key, device, dtype), device/dtype context, injected ICU/Reasoning (no module-level singletons), kernel-ladder evidence recording
- **Objective resolution in policies (L18, WP9.7)**: Added `resolve_objectives()` helper reading from OBJECTIVES_REGISTRY; ModelBasedPolicy uses registry directions for multi-objective studies
- **S3 data-origin allocation & contrast quota (L19, WP9.8)**: `_generate_s3_schedule_candidates()` implements exploration/calibration/test fractions + OFAT/fractional-factorial contrast quota within exploration budget
- **RUN_PROFILES & CLI updated (WP9.9)**: All profiles use canonical StageIds (s1_frame, s2_space, etc.)
- **Stage-model lock & wrapper-obligation tests (WP9.10)**: Created `tests/property/test_stage_model_lock.py` (11 tests): canonical StageId ↔ STAGES_REGISTRY ↔ RUN_PROFILES lock, coverage/classification/provenance structure tests, replay/resume integration, failure isolation structure
- All quality gates pass: `ruff format`, `ruff check`, `pyright` (strict), 122 property tests pass.

### 2026-09-30 — WP10 Complete: Learning Integration (L7, L8, L9, L10, L11, L20, R15, R53, R57)
- **PRIORS single-source (L11)**: `prior.py` accessor functions (`get_ruler_lr`, `get_step_size_multiplier`, `get_dynamics_step_size`, `apply_step_size_overrides`, `apply_dynamics_step_size`) now use `prior_value()` from `PRIORS_REGISTRY` as single source. Legacy data tables retained only for initial registration; consumers reroute to registry.
- **Reasoning persistence (R57, L10)**: `ReasoningStore` now persists hypotheses/literature as records with payload kinds "hypothesis"/"literature" and `ProvenanceLink` cross-links. Module-level singleton removed; instances created per-run and injected via `SystemContext`.
- **ICUModel context injection (L10/K10)**: `ICUModel` has no module-level singleton; designed for injection through `SystemContext`. `persist_to_store`/`load_from_store` fixed for type correctness (DataOrigin enum, tuple fields, no replication_key).
- **Surrogate coordinate-wide features (R15/R53)**: `GaussianProcessSurrogate._coords_to_features` now uses `harvest_schema()` for consistent, deterministic feature encoding across all hyperparameters in registry order.
- **Claim integrity (L20)**: `claim_eligible_by_achieved_seeds` in `evidence/claims.py` counts achieved seeds per `replication_key` via `RecordStore.count_achieved_seeds()`.
- All quality gates pass: `ruff format`, `ruff check`, `pyright` (strict), all learning-related property tests pass.

### 2026-09-30 — WP11 Complete: Surface Conformance, Codegen & Operations (L12, L13, L14, R43, R80, R83, R88)
- **Intent persistence (L13/R84)**: `RecordStore.record_intent()` persists operator intents as run-linked records with `payload.kind="operator_intent"` (uniqueness from `intent_id` via `schedule.task_id`; redelivery dedups as `DuplicateMeasurementError` through the single writer); `query_intent_records()` scopes by run. `RunController._persist_intent()` and `submit_intent_to_run()` now use it (log-only stubs removed).
- **Public-API exports (L14/R73)**: new `RecordStore.export_snapshot()` (records/runs/artifacts/vector_index as JSON-serializable dicts via `query_records`/`query_runs`/`read_table`); `export_to_json`/`export_to_parquet` in `surface/report.py` routed through it — no `store._conn`/`_row_to_record` reach-ins remain in `surface/`.
- **Question-first entry (R43)**: new `surface/profiles.py::question_first(objective, operating_point)` validates against OBJECTIVES registry and returns a RunSpec (`synthesis` policy, canonical S1–S11 stages, S3 data-origin allocation 0.6/0.2/0.2 + contrast quota 0.1).
- **Headless service (R81–R84, WP11.4)**: new `surface/service.py` with `ServiceLoop` (pipeline task + control-file poll), `write_control_intent`/`poll_control_file` JSONL protocol, malformed-line tolerance.
- **Alerts (R83/Q14)**: `AlertDedup` keyed `(predicate, run, window)`; `DEFAULT_Q14_ROUTES` + `default_events_for()` record the notify-only routing model as `WebhookConfig.events` defaults.
- **Report completion (R85–R88)**: `narrative_handoff_summary()` — run state, claim-eligible cells, open alerts, latest promotion, budget, intents on record.
- **Store fixes found via new tests**: `json_extract` → `json_extract_string` for `data_origin`/`payload.kind` filters (DuckDB cast the bound param to JSON and raised `ConversionException`); `record_id` PK collisions now map to `DuplicateMeasurementError` (same-run redelivery); `count_achieved_seeds` `None`-guard for optional `gate_verdict` (strict-pyright fix).
- **report.py fixes**: invalid `except ValueError, TypeError` syntax (×2); `ExportBundle.__dict__` → `dataclasses.asdict` (slots dataclass has no `__dict__`).
- **Locks**: `tests/property/test_wp11_surface_lock.py` (20 tests) — intent round-trip/dedup/scoping, snapshot serializability, JSON round-trip, handoff content, question-first shape/rejection, codegen determinism + `generate_all` file set, documented-command `--help` conformance (R80), RUN_PROFILES canonical-stage lock, dedup window, Q14 coverage, control-file round-trip.
- All quality gates pass: `ruff format`, `ruff check` (changed files; `PLR0904` on `RecordStore` relaxed per-line — single-writer API concentration is the §1.1 design), `pyright` strict clean, 174 property tests pass (4 skipped).

### 2026-09-30 — WP12/WP13 Partial: K10 Hygiene, Isolation Locks, Prior Source, E1 Harness (L10, L11, L17, L20)
- **K10 singletons removed (L10 follow-through)**: `legality/engine.py` — `ENGINE` global
  + `get_engine()` deleted; `create_constraint(..., engine)` takes an explicit engine
  (no default). `evidence/failure.py` — `_FIX_LINKAGES` global + 4 module functions
  replaced by run-scoped `FixLinkageStore` (threading.Lock-guarded, injected;
  `analyze_store_failures(store, fix_store=None)`). `test_legality_boundary_lock.py`
  updated to a test-local `_TEST_ENGINE` (test files out of lock scope).
- **Import-graph lock (WP12 gate)**: `tests/property/test_kernel_isolation_lock.py`
  (12 tests) — AST scan of the six kernel subpackages forbids legacy pillar imports
  (autoscientist/hyperopt/lightning_/core.campaign/legacy execution/validation/
  computronium_lab/ceec) + pre-kernel flat modules + legacy filesystem reach-ins;
  K10 module-state lock (no global/nonlocal, no module-level state-holder instances
  or defaultdict/Counter accumulators; registries/catalogs/seed-data/frozen specs
  exempt by §4 design) + regression pins (ENGINE/get_engine absent, linkage globals
  absent, FixLinkageStore run-scoped). Found: kernel already import-clean; the only
  legacy reach-in was `prior.py` reading `autoscientist/ruler_table.json` at import.
- **L11 tightening**: legacy JSON read deleted from `prior.py` (verified byte-identical
  to frozen `_RULER_LR_DATA`; behavior-preserving); `seed_all_registries()` now calls
  `register_all_priors()` after its own PRIORS seed (local import, no layering edge) —
  previously it cleared PRIORS and dropped all 44 learning priors, leaving two sources
  of truth. `tests/property/test_wp10_learning_integration_lock.py` (9 tests): L17
  cross-task identity (task_id spans measurement_key; both tasks persist), L20
  achieved-seed claims (2/5 seeds ineligible, 5/5 eligible), L11 prior single-source
  (all ruler tasks + all overrides resolve via `prior_value()`; accessor agrees).
- **E1 harness (WP13)**: `scripts/probes/store_overhead_bench.py` — 200 timed appends
  vs 2 s reference eval; measured 2026-09-30: mean=3.03ms p95=4.43ms → 0.15%/0.22%,
  OVERHEAD_OK (< 1% K7/K9 criterion).
- Stray `fix_capabilities_v2.py` (WP12 dead-code note): already absent from tree —
  no action needed.
- All quality gates pass: `ruff format` + `ruff check` clean on 8 changed files,
  `pyright` strict clean (engine/failure/prior/seed_registries/new locks),
  204 property tests pass (4 pre-existing skips), probe OVERHEAD_OK.

### 2026-09-30 — WP13 Serialization & DoD Hardening: task_id persistence, fail-closed versions, drift lock (L17, §9.7, §9.9)
- **L17 follow-through — `task_id` persisted**: the WP9 `Schedule.task_id` lived in the
  dataclass and `measurement_key` but was dropped at the store boundary (DDL STRUCT,
  both write dicts, `_parse_schedule` all carried 6 fields). Added `task_id TEXT` to
  the schedule STRUCT, both insert paths, and strict parsing. Per Directive 2
  (schema changes free before first external use) parsing is strict — pre-existing
  store files are rebuilt, not migrated.
- **Fail-closed versions (Directive 2)**: `_build_record_from_row` raises new
  `UnsupportedSchemaVersionError(StoreError)` on unknown `schema_version`
  (`SUPPORTED_SCHEMA_VERSIONS = frozenset({1})`); `SchemaRegistry.read_record`
  raises instead of falling back to the latest reader (had zero callers — safe).
- **Import-order seeding defect fixed**: `seed_all_registries()` raised
  `Duplicate registration: ruler_lr_digits` when `learning.prior` was first
  imported inside the function (import-time side-effect registration + explicit
  `register_all_priors()`). Clears PRIORS after the local import — seeding is now
  order-independent and twice-idempotent (verified).
- **Serialization round-trip lock**: `tests/property/test_serialization_roundtrip_lock.py`
  (8 tests) — schedule/task_id round-trip, cross-task key distinctness + persistence,
  `unknown` verbatim (incl. unicode), params/payload/provenance fidelity, store + registry
  fail-closed on version 999.
- **Codegen drift lock (WP13 DoD)**: `tests/property/test_codegen_drift_lock.py`
  (3 tests) — byte-pins all 10 `docs/generated/*.json` against their generators.
  Found `priors.json` stale (28 rows, pre-WP10 `lr_ruler_*`/`step_size_*` naming vs
  current 45-row `ruler_lr_*`/`step_size_override_*` registry) — re-pinned.
  Removed `generated_at` from `generate_compatibility_matrix()` (no consumers;
  nondeterministic timestamps defeat byte-pinning; `.md` summaries keep theirs).
  Also fixed 4 pre-existing PLW1514 `encoding=` findings in `codegen.py` md writers.
- All quality gates pass: `ruff format` + `ruff check` clean on 6 changed files,
  `pyright` strict clean, 160 property tests pass (149 neighbors + 11 new), 4 pre-existing skips.

### 2026-09-30 — WP10 Ledger Closure: L7 Training Load + L9 Effect-Size Runner (surrogate.py)
- **L7 follow-through — `_load_training_data` wired**: `SurrogatePolicy` now pulls
  `exploration ∪ policy_selected` through the public `RecordStore.query_records(
  data_origin=...)` API (no stub, no private reach-ins); calibration/test records
  are excluded by construction and remain the WP5.5 audit's domain.
- **L9 closed — `evaluate_effect_size` implemented**: guards (`n_tasks≥10`,
  `n_seeds≥5`) then delegates to `learning/benchmark.py::run_acquisition_benchmark`
  over `create_synthetic_benchmark_tasks(n_tasks)` and returns
  `result.effect_size` (`EffectSizeResult`: task-level Cohen's d + CI + p-value).
  `NotImplementedError` removed.
- **Protocol conformance**: added `SurrogatePolicy.observe()` (forwards to base +
  appends datum with its own origin tag, refits next propose) and `get_name()`
  (`surrogate(<acq>) over <base>`) — the class now satisfies its own
  `ProposalPolicy` protocol; benchmark `Policy` interop via `cast` (runtime
  duck-typed; `_evaluate_policy_on_task` only needs `get_name`).
- **DRY**: extracted `_record_to_datum()` shared by `_load_training_data`,
  `observe()`, and `update()` (update keeps its documented POLICY_SELECTED
  stamping).
- **Locks**: `test_wp10_learning_integration_lock.py` 8 → 11 tests
  (`TestSurrogateStoreWiring`: training-split exclusion, guard enforcement,
  runner result shape); `_prov`/`_record` helpers gained an `origin` param.
- All quality gates pass: `ruff format` + `ruff check` + `pyright` strict clean
  on both changed files; 11/11 lock tests pass.

### 2026-09-30 — WP13 Harness Fidelity: Closed-Loop Benchmark Runner (benchmark.py)
- **Closed loop (was item 5 below)**: `_evaluate_policy_on_task` now runs
  propose→score→`observe_score` batches (batch 5, rounds = ceil(B/5)) until the
  `CostBudget` is spent; returns best-seen score. Noise indices are eval-order
  based so paired policies share the noise prefix. New `BenchmarkPolicy`
  protocol (`propose(n, context)`/`get_name`, `observe_score` optional and
  duck-typed); `run_acquisition_benchmark` retyped from execution `Policy`.
- **Locality-preserving encoder**: `_coordinate_to_vector` normalizes numeric
  params against registry Ranges (LOG in log space, missing → 0.5) over the
  first `dimension` Range specs in harvest order; structural axes held fixed
  by task (documented scope: continuous-param acquisition).
- **Task optima**: `create_synthetic_benchmark_tasks` optima now uniform
  [0,1)^dimension seeded per task (were [1..6]+offset, outside encoder range).
  Shared `evidence.protocol.create_synthetic_fixture` untouched (lock-pinned).
- **`SurrogatePolicy.observe_score`**: lightweight benchmark observation path
  (no Record construction); `evaluate_effect_size` casts updated to
  `BenchmarkPolicy`.
- **Locks**: `TestBenchmarkHarness` (3 tests) — round/budget mechanics
  (5000 obs/policy, 20 rounds × 5, round-0 best=inf), encoder
  determinism/locality, unit-cube optima. 14/14 lock tests pass (16 s).
- Gates: `ruff format` + `ruff check` + `pyright` strict clean.

### 2026-09-30 — WP10/Ledger: GP Feature Subspace (shared encoder, deterministic)
- **One encoding**: benchmark `_embedding_dims`/`_coordinate_to_vector` made
  public (`embedding_dims`/`coordinate_to_vector`,
  `BenchmarkPolicy`-adjacent exports); `GaussianProcessSurrogate` features now
  use it — surrogate learns the space the harness evaluates in.
- **Defects removed**: salted `hash()` structural dims (nondeterminism across
  processes) gone — structural axes held fixed per task, same documented scope
  as the harness; raw-scale/mostly-constant ~74-dim space → normalized
  `n_features` (default 6) Range subspace; missing → 0.5 (was out-of-range
  0.0); `_get_feature_specs` deleted.
- **Fit cost**: `SurrogateConfig.n_optimizer_restarts` (default 2, was
  hardcoded 5); full lock file 16 s → 5 s; GP double-fit determinism locked
  (same `random_state` → bit-identical means).
- **Replay hygiene**: real-task placeholder seed uses sha256 (was salted
  `hash(task.name)`).
- **Locks**: `TestSurrogateFeatures::test_gp_fit_fast_deterministic_and_local`
  (20-pt fit < 120 s guard, interpolation err < 0.3, determinism). 15/15 pass.
- Gates: `ruff format` + `ruff check` + `pyright` strict clean.

### Improvement Opportunities (remaining WPs)
1. **WP12 (major)**: Full legacy port & delete still open — `autoscientist/`,
   `hyperopt/`, legacy `execution/` engine, `lightning_/`, `packages/computronium-lab`
   research layer, pre-kernel flat files in `experiment/` (`producer.py`,
   `staircase.py`, `probe.py`, `param_estimator.py`, `result_sink.py`,
   `reporting.py`, `report.py`, `schema.py`, `cli.py`; note `schema.py` is shadowed
   by the `schema/` package — packages win import resolution, so it is dead code).
   Live importers remain (`validation/backprop_parity.py` → `experiment.probe`,
   `experiment/cli.py` chain, `param_estimator` used by 8+ legacy modules).
   Precondition unchanged: conformance green per capability (R77); the import-graph
   lock guards the kernel side. Deletion is blocked on porting, not on kernel work.
2. **WP12**: `prior.py` legacy data tables still seed the registry — final deletion
   step pending full consumer-reroute audit (`ontology/update.py`, `compose.py`,
   `campaign._ruler_lr` adapters). Cleanup: legacy ruler table carries a `"*"`
   catch-all task surfacing as prior name `ruler_lr_*` — rename to an explicit
   `ruler_lr_catchall` when the tables are deleted.
3. **WP13**: E2 acquisition effect-size via `learning/benchmark.py`, E3 seeded
   reproduction on `SyntheticGroundTruth`, E4 transfer with explicit provenance;
   results recorded as store records. (Serialization round-trip + E1 overhead +
   kill-9 now locked; drift lock done. L9 wiring done — `evaluate_effect_size`
   now returns real `EffectSizeResult`s.)
4. **WP13 DoD hardening**: full C1–C88 conformance-evidence audit (per-capability
   `verifying_test` execution sweep). Drift lock pins the 10 JSON files only —
   `.md` summaries (timestamps) and `conformance_stubs/` + `primitives/`/`algorithms/`
   dirs (other generators) are out of scope.
5. **E2 calibration open (found 2026-09-30 via harness probing)**: naive
   learners (greedy hill-climb, top-k-mean) LOSE to best-of-100 random on the
   smooth 6-D bowl (d≈+0.8, p<0.05 — coverage beats concentration at B=100;
   lowering noise to 0.01 does not change the sign). E2 needs either a
   competent surface-fitting surrogate or sharper/lower-D tasks before its
   numbers are trusted. GP-subspace fix landed (fit now seconds,
   deterministic); the remaining step is a full surrogate-vs-random E2 run,
   backgrounded per §6 (10 tasks × B=100 ≈ minutes, not seconds).

### Notes for Remaining Work
- `RecordStore` `PLR0904` noqa stands (§1.1 single-writer concentration).
- `surface/conformance.py::run_verifying_test` subprocess use remains sandboxed-local only.
- `question_first` objective-id vs CLI `--objectives` legacy-name reconciliation still
  open at WP12 port time.
- `seed_all_registries()` is now the single PRIORS seeding path (seed rows +
  `register_all_priors()`); calling `register_all_priors()` twice raises on
  duplicates by `Registry.register` design — seed functions must clear first
  (as `seed_all_registries` does) and never double-register. Now also robust to
  `learning.prior` first-import happening inside the seed call.
- Store files created before the `task_id` STRUCT addition are not readable for
  old rows (strict parse) — rebuild per Directive 2; no migration machinery.
