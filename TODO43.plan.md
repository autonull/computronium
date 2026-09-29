# TODO43.plan.md — Implementation Plan: The Computronium Experiment Kernel

**Implements:** TODO43.abc3.md (SPEC-43 Rev 2.0 — the unified/hybrid design) as the authoritative spec; abc2 (Rev 1.1) is superseded and consulted only for rationale.
**Status:** PLAN — decomposes Gate 3 (work packages + sequencing) so implementation can start.

---

## 0. Scope Directives (binding, from the round owner)

1. **No backwards compatibility.** No strangler adapters, no legacy importers, no old-shape
   migration phases. abc3 §12.2 (four-phase store migration) and §12.3 (strangler migration)
   are **dropped**. Legacy entry points (`broad_map`, `stack`, `hyperopt`, `execution`,
   `lightning_`, computronium-lab research layer) are ported *into* the Kernel as catalog
   entries, then deleted outright.
2. **No data preservation.** `kb.sqlite`, `campaign.db`, `ledger.sqlite`, and Optuna `*.db`
   are abandoned in place, untouched and read-only by neglect (never opened again). Only
   `ceec-core`'s content-addressed store is linked forward (it is an active subsystem, not
   legacy data).
3. **No time estimates.** Sequencing is dependency-ordered only.
4. **Store decision:** DuckDB (embedded, SQLite-like) — see §1. MongoDB rejected.

---

## 1. Decision Log

### 1.1 Store: DuckDB replaces SQLite + MessagePack + projected columns

The user's NoSQL requirement (agile schema development) is met **without** a document DB:
DuckDB is an embedded, zero-config, single-file engine with native nested types, giving
document-style agility inside a SQL engine with real constraints.

| Option | Verdict | Why |
|---|---|---|
| SQLite + MessagePack BLOBs + projected columns (abc3 §6.1) | **Superseded** | Works, but the projection machinery (dual-write + CI lock) and MessagePack opaqueness exist only to work around SQLite's inability to query inside BLOBs. |
| SQLite + JSON1 + expression indexes | Fallback | Kills MessagePack, but JSON is parsed per query; analytics (fronts, attribution, clustering — the actual product) fight the row-store. |
| **DuckDB** | **Selected** | Native `STRUCT`/`JSON`/`MAP`/array columns — sections are typed, queryable, indexable by zone maps; no projections needed. Columnar analytics for claims/fronts/attribution. `vss` extension for the vector index. Parquet-native export/import (R73 for nearly free). WAL + crash-safe. In-process, K1-compliant. |
| libSQL/Turso | Rejected | SQLite fork; brings nothing DuckDB doesn't, adds a fork dependency. |
| PostgreSQL | Rejected | Server process violates the embedded/zero-config posture (K1, R13 spirit). |
| MongoDB | Rejected | Server, no UNIQUE-constraint discipline for dedup keys without ceremony, weak relational integrity for `record_artifacts`, new operational surface, and K1's stdlib-lean posture. Gains nothing over DuckDB JSON columns. |

**Supersessions to abc3:** §6.1.1 (MessagePack → native typed columns), §6.1.3 (projected
columns → deleted; the columns *are* the source), §6.1.4 (SQLite indexes → zone maps +
ART as needed), §6.1.6 (WAL pragmas → DuckDB built-in), Appendix II DDL (→ §2 of this plan).

**Honest tradeoffs:**

- **Single-writer-per-process.** DuckDB allows one writer process (file lock); SQLite WAL
  allows lock-serialized multi-process writes. The abc3 design already concentrates writes:
  `ExecutionBackend.submit() -> list[Record]` returns records to the pipeline, and only the
  pipeline writes (§5.8, §5.2). **New binding rule:** all store writes flow through the
  orchestrating process; workers never open the store. K8 dedup becomes in-process;
  `measurement_key` UNIQUE remains the enforcement. If a true multi-writer requirement ever
  emerges, the `Store` Protocol swaps back to SQLite WAL — the abc3 escape hatch, reversed.
- **Tiny-commit latency.** DuckDB commits cost ~1–3 ms vs SQLite's ~0.5 ms. The binding K7/K9
  criterion is **overhead < 1% of median evaluation walltime** (evaluations run 1–10 s), not
  abc3's SQLite-calibrated absolute priors. §5 harness records mean/p95/fraction; batch appends
  per evaluation round amortize further.
- **STRUCT field additions** require `ALTER TABLE … ALTER COLUMN` (a rewrite). Mitigation:
  stable sections are typed STRUCTs; *open* surfaces (`params`, `payload`, `unknown`) are
  `JSON` — new tunables and telemetry need **zero DDL**. That is the agile-schema requirement,
  satisfied.

---

## 2. Unified Store Schema (replaces abc3 Appendix II)

```sql
CREATE SEQUENCE record_seq;

CREATE TABLE runs (
    run_id            TEXT PRIMARY KEY,
    spec              JSON,                 -- RunSpec (§3.8)
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

CREATE TABLE record_artifacts (            -- bytes live in ceec-core (§6.1.5)
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

---

## 3. Work Packages (dependency-ordered)

### WP0 — Binding gates (before any Kernel code)
abc3 §0.6, minus what this plan already discharges.
- **Gate 1 — Rev 3 review:** accept/reject each TODO43 §13–§15 candidate; record the verdict
  table in `docs/design/rev3_gate.md`. Output feeds WP2 registry seeds and WP4 catalog rows.
- **Gate 2 — Fix the union:** audit the six implementations' hyperparameter surfaces; verify
  Appendix IV's 37-name union; add missing domain rows. Output: the frozen union table that
  WP2's harvest lock asserts against.
- ~~Gate 3~~ — discharged by WP1 below (walking skeleton is the first build, not a document).

### WP1 — Walking skeleton (vertical slice, proves the five abstractions compose)
abc3 §12.4. Package `computronium/experiment/` per abc3 §1.1.
- `schema/registry.py` — generic `Registry[SpecT]` (lock, diff, schema, integrity).
- `schema/axis.py` — `AxisSpec` with `AxisKind`, availability predicates; `AxisPrimitive`
  `__init_subclass__` auto-registration.
- `schema/coordinate.py`, `schema/record.py` — `Coordinate`, `Record`, three identity keys.
- `evidence/store.py` — DuckDB `RecordStore`: `append()` (single transaction: seq + record +
  artifacts), `DuplicateMeasurement` on UNIQUE violation, `Store` Protocol.
- `execution/pipeline.py` + `execution/stage.py` — S1–S11 runner with wrapper obligations
  (coverage, classification, traceability, atomic append); one real policy
  (`RoundRobinGrid`), most stages no-op.
- `evidence/claims.py` — one `claim_eligible` predicate + SQL prefilter.
- **End-to-end proof:** 100 records, one intentional duplicate (skip), one injected
  `EvaluationFailure` (isolated, becomes a record), one `kill -9` mid-write (store
  consistent after reopen).

### WP2 — Pillar 1 complete: schema & registries
- `schema/harvest.py` — `__tunables__` reflection, name-based dedup (70→37; conflicts raise
  `ConflictingTunable`), `harvest_schema()`.
- `schema/versioning.py` — `schema_version`, append-only reader registry, `UnknownField`
  preservation (R79, K4). Version 1 = this schema; no legacy readers needed (Directive 1).
- Registry instances: `AXES`, `OBJECTIVES`, `CONSTRAINTS`, `PRIORS`, `POLICIES`, `STAGES`,
  `CAPABILITIES` (abc3 §2.3 seeds, per Gate 1/2 outcomes).
- Locks (CI property tests): registry uniqueness/totality/no-orphans/lock;
  `harvest_schema() ⊇ Gate-2 union`; availability-predicate evaluation.

### WP3 — Pillar 3: legality engine
- `legality/dsl.py` — `Expr` AST + evaluator + Appendix III JSON wire format (content-hashed).
- `legality/engine.py` — `Constraint` model (origin/scope/enforced-at), S4/S6 enforcement,
  globally-suppressive semantics (R38); generated compatibility matrix (R63).
- `legality/classify.py` — void/defect taxonomy as registry data; unclassified bucket counted.
- Seed constraints from `SystemConfig.validate()`, task fences, `apply_constraints` (Q2, R37,
  R66). Migrate-and-delete the original validators (Directive 1).

### WP4 — Pillar 2: execution
- `execution/budget.py` — `Budget` + `CostModel` Protocol (R21–R24).
- `execution/allocator.py` — `AllocationPolicy` Protocol + evidence-driven successive
  promotion reference implementation (R46–R51, divergence/stagnation telemetry, waste report).
- `execution/replay.py` — replay hash, resume on `measurement_key`, checkpoint/restore
  (R26–R30).
- `execution/backends.py` — local/multiprocess backends; **workers return Records; the
  pipeline process is the sole writer** (§1.1 tradeoff).
- `execution/policy.py` — `Policy` Protocol + the eight-policy catalog (abc3 §5.3): port
  `StratifiedRandom`, `RoundRobinGrid`, `UniformRandom`, `ModelBased` (Optuna behind a
  storage adapter over the unified store — R71), `Evolution`, `Synthesis`, `StrategyProgression`,
  `TrainerDriven` (last four per Gate 1 verdicts). Delete the six legacy implementations'
  search paths as each port lands (Directive 1).

### WP5 — Pillar 4: evidence & governance
- `evidence/status.py` — primary-only `Status` fields (no stored derived verdicts).
- `evidence/claims.py` — full predicate suite: claims (R35), promotion (R36), alerts as
  record-stream predicates (R83/Q14), matched-cost comparison guard (R65), stratification
  guards (R8/R22/R67).
- `evidence/failure.py` — `FailureCause` taxonomy, clustering, reproducer emission,
  fix-linkage queries (R58–R62).
- `evidence/ceec.py` — artifact delegation to `ceec-core` (`put()` → digest →
  `record_artifacts`); ledger linkage via `status.ceec_link` (Q9).
- Vector retrieval over `vector_index` (`vss` HNSW once corpus warrants; brute-force
  `list_dot` first) — C59, R15, K5.

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
  passing test or explicit retirement record; CI gate (R76–R78).
- `surface/operations.py` — pausable/steerable runs, service mode, webhook alerts,
  operator-intent records (R81–R84).
- Codegen: docs listings, compatibility matrix, JSON-Schema validators, conformance stubs,
  CLI flags — all from registries, lock-tested (abc3 §2.5).

---

## 4. Locks & Test Matrix (CI-enforced)

abc3 §17.1 with these adjustments: **drop** migration-validation tests (no migration), **drop**
projection≡section lock (no projections), **add** single-writer topology test (parallel
backend + one store connection ⇒ no duplicate `measurement_key`, monotonic `seq`), **add**
DuckDB round-trip tests (typed sections survive write/read; `unknown` preserved verbatim).

Retained: registry integrity locks, schema-union lock, matrix lock, capability conformance,
documented-command tests, replay-hash assertion, kill/resume test, property-test generation
from spec invariants, policy-substitution test (four policies, identical record shape).

## 5. Class E Benchmarks (unchanged verdicts, new apparatus)

| Benchmark | Discharges |
|---|---|
| Cost-to-rank vs uniform baseline | R46 |
| Surrogate vs random on held-out task | R54 |
| Cost-model estimate-vs-actual error trend | R23/R24 |
| Divergence-bound replay (1357 s run) | R50 |
| Store overhead harness (§1.1: fraction < 1% of median eval walltime; mean/p95 recorded) | K7, K9 |
| Seeded axis-effect reproduction | R86 |

## 6. Definition of Done

abc3 §21.1 items 1–12 (all) and §21.2 adjusted: ~~migration complete~~ → legacy stores
abandoned untouched (Directive 2); schema evolution proven from v1 forward, not from legacy
records. Every Class S lock green, every Class E benchmark recorded as a store record, every
Class P gate enforced in CI.
