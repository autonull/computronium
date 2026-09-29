# SPEC-43.1 — The Unified Record Store
## Detailed Design for the Foundation Subsystem

**Rev 1.0 · 2026-09-30 · Status: DETAILED DESIGN (buildable)**

**Depends on:** SPEC-43 (the Experiment Kernel architecture)

**Supersedes:** No document (this is the first detailed design pass)

---

## 0. Executive Summary

SPEC-43 establishes that the Experiment Kernel needs one store. This document specifies exactly what that store is, how it handles concurrency, how it migrates from four existing stores, and proves it satisfies both K7 (performance) and K9 (always-on governance).

This is the highest-risk subsystem because everything depends on it. Getting it wrong means either:
- **Too slow:** governance overhead violates K7
- **Too complex:** migration fails, losing KB analytics (K5 violation)
- **Too fragile:** concurrent writes corrupt records (R12 violation)

This specification makes concrete choices that SPEC-43 deliberately deferred.

---

## 1. Package Placement Decision

### 1.1 The Contradiction

SPEC-43 §3.1 says: `computronium/experiment/` (one package).

README "Standalone platform packages" says: "TODO20 Rule 6 — one implementation copy each; legacy `computronium.*` import paths are thin adapters."

These contradict. One must win.

### 1.2 Decision: `packages/computronium-experiment`

**Rationale:**

1. **Dependency direction:** The experiment framework depends on `ceec-core`, `computronium-lab`, and `stability`. If it lives in `computronium/experiment/`, those packages cannot depend on it without creating a cycle. As a standalone package, `ceec-core` can provide storage adapters without importing the framework.

2. **Deployment flexibility:** Researchers using only `ceec-core` for epistemic governance should not need the full experiment framework. As a standalone package, `computronium-experiment` is optional.

3. **Versioning independence:** The experiment framework will evolve faster than the core library. Separate packages allow independent versioning and release cadence.

4. **Consistency with precedent:** `ceec-core`, `psi-peft`, `local-feedback`, `computronium-lab`, and `stability` are all standalone packages. The experiment framework should follow the same pattern.

### 1.3 Structure

```
packages/computronium-experiment/
├── pyproject.toml
├── src/
│   └── experiment/
│       ├── __init__.py
│       ├── registry/
│       ├── schema/
│       ├── execution/
│       ├── legality/
│       ├── evidence/
│       ├── learning/
│       └── surface/
└── tests/
```

**Import path:** `from experiment.evidence import RecordStore`

**Legacy adapter:** `computronium/experiment.py` re-exports for backward compatibility during migration.

---

## 2. Store Schema Design

### 2.1 Core Tables

The store is a single SQLite database in WAL mode with six tables:

```sql
-- Table 1: Records (the single source of truth)
CREATE TABLE records (
    record_id          TEXT PRIMARY KEY,  -- SHA256 of (coordinate, schedule, provenance)
    schema_version     INTEGER NOT NULL,  -- for versioned readers (R79)
    coordinate_hash    TEXT NOT NULL,     -- SHA256 of coordinate section only
    coordinate         BLOB NOT NULL,     -- MessagePack-serialized Coordinate
    schedule           BLOB NOT NULL,     -- MessagePack-serialized Schedule
    provenance         BLOB NOT NULL,     -- MessagePack-serialized Provenance
    status             BLOB NOT NULL,     -- MessagePack-serialized Status
    payload            BLOB NOT NULL,     -- MessagePack-serialized Payload (metrics, telemetry)
    created_at         TEXT NOT NULL,     -- ISO8601 timestamp
    policy_id          TEXT NOT NULL,     -- which policy produced this
    run_id             TEXT NOT NULL      -- which run produced this
);

-- Table 2: Coordinate index (for fast lookups by coordinate)
CREATE TABLE coordinate_index (
    coordinate_hash    TEXT NOT NULL,
    record_id          TEXT NOT NULL,
    PRIMARY KEY (coordinate_hash, record_id),
    FOREIGN KEY (record_id) REFERENCES records(record_id) ON DELETE CASCADE
);

-- Table 3: Artifacts (content-addressed blobs)
CREATE TABLE artifacts (
    artifact_hash      TEXT PRIMARY KEY,  -- SHA256 of content
    artifact_type      TEXT NOT NULL,     -- 'config' | 'figure' | 'reproducer' | 'kernel'
    content            BLOB NOT NULL,
    size_bytes         INTEGER NOT NULL,
    created_at         TEXT NOT NULL
);

-- Table 4: Record-artifact links
CREATE TABLE record_artifacts (
    record_id          TEXT NOT NULL,
    artifact_hash      TEXT NOT NULL,
    role               TEXT NOT NULL,     -- 'config' | 'figure' | 'reproducer'
    PRIMARY KEY (record_id, artifact_hash),
    FOREIGN KEY (record_id) REFERENCES records(record_id) ON DELETE CASCADE,
    FOREIGN KEY (artifact_hash) REFERENCES artifacts(artifact_hash) ON DELETE CASCADE
);

-- Table 5: Vector index (for semantic retrieval, C59)
CREATE TABLE vector_index (
    record_id          TEXT NOT NULL,
    embedding          BLOB NOT NULL,     -- 768-dim float32 array, 3072 bytes
    embedding_version  INTEGER NOT NULL,  -- model version that produced this
    PRIMARY KEY (record_id),
    FOREIGN KEY (record_id) REFERENCES records(record_id) ON DELETE CASCADE
);

-- Table 6: Run metadata (for provenance and budget tracking)
CREATE TABLE runs (
    run_id             TEXT PRIMARY KEY,
    spec               BLOB NOT NULL,     -- MessagePack-serialized RunSpec
    started_at         TEXT NOT NULL,
    finished_at        TEXT,
    status             TEXT NOT NULL,     -- 'running' | 'completed' | 'failed' | 'killed'
    budget_consumed    REAL,              -- walltime seconds
    records_produced   INTEGER
);
```

### 2.2 Indexes

```sql
-- Fast lookups by policy, run, and coordinate
CREATE INDEX idx_records_policy ON records(policy_id);
CREATE INDEX idx_records_run ON records(run_id);
CREATE INDEX idx_records_coordinate_hash ON records(coordinate_hash);
CREATE INDEX idx_records_created_at ON records(created_at);

-- Fast lookups for claims and promotions
CREATE INDEX idx_records_status_gate ON records(json_extract(status, '$.gate_verdict'));
CREATE INDEX idx_records_status_defect ON records(json_extract(status, '$.defect'));
CREATE INDEX idx_records_status_maturity ON records(json_extract(status, '$.maturity_tier'));
```

### 2.3 Why MessagePack over JSON

- **Compact:** 30-50% smaller than JSON for nested structures
- **Fast:** 10-100× faster serialization/deserialization
- **Binary-safe:** handles numpy arrays, torch tensors (as bytes) without base64 encoding
- **Schema-less:** allows forward/backward compatibility (unknown fields preserved)

**Tradeoff:** Not human-readable in the database. Mitigated by:
- CLI command `comp experiment show-record <record_id>` pretty-prints
- JSON export for reports and external tools

### 2.4 Schema Versioning

Every `Record` carries `schema_version`. The `RecordStore` class maintains a registry of readers:

```python
class RecordStore:
    _readers: dict[int, Callable[[bytes], Record]] = {
        1: read_record_v1,
        2: read_record_v2,
        # ...
    }
    
    def read_record(self, row: sqlite3.Row) -> Record:
        schema_version = row['schema_version']
        reader = self._readers.get(schema_version)
        if reader is None:
            raise UnknownSchemaVersion(schema_version)
        return reader(row)
```

**Unknown fields:** When a reader encounters a field it doesn't recognize, it stores it in `Record.unknown: dict[str, Any]` and labels it, never silently defaults (R79).

---

## 3. Write Path & Concurrency

### 3.1 Transaction Model

Every record write is a single transaction:

```python
class RecordStore:
    def append(self, record: Record, *, atomic: bool = True) -> None:
        """Append a record. If atomic=True, the write is all-or-nothing."""
        with self._connection:  # SQLite transaction
            # 1. Check for duplicate by record_id (R74, K8)
            cursor = self._connection.execute(
                "SELECT 1 FROM records WHERE record_id = ?",
                (record.record_id,)
            )
            if cursor.fetchone():
                raise DuplicateRecord(record.record_id)
            
            # 2. Insert the record
            self._connection.execute(
                """
                INSERT INTO records (
                    record_id, schema_version, coordinate_hash,
                    coordinate, schedule, provenance, status, payload,
                    created_at, policy_id, run_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.record_id,
                    record.schema_version,
                    record.coordinate.cell_key,
                    msgpack.packb(record.coordinate),
                    msgpack.packb(record.schedule),
                    msgpack.packb(record.provenance),
                    msgpack.packb(record.status),
                    msgpack.packb(record.payload),
                    record.created_at,
                    record.provenance.policy_id,
                    record.provenance.run_id,
                )
            )
            
            # 3. Update coordinate index
            self._connection.execute(
                "INSERT INTO coordinate_index (coordinate_hash, record_id) VALUES (?, ?)",
                (record.coordinate.cell_key, record.record_id)
            )
            
            # 4. Link artifacts
            for artifact in record.artifacts:
                self._store_artifact(artifact)
                self._connection.execute(
                    "INSERT INTO record_artifacts (record_id, artifact_hash, role) VALUES (?, ?, ?)",
                    (record.record_id, artifact.hash, artifact.role)
                )
```

### 3.2 WAL Mode & Crash Safety

```python
class RecordStore:
    def __init__(self, path: Path):
        self._connection = sqlite3.connect(str(path), timeout=30.0)
        self._connection.execute("PRAGMA journal_mode=WAL")  # R12: crash-safe
        self._connection.execute("PRAGMA synchronous=NORMAL")  # balance safety/perf
        self._connection.execute("PRAGMA foreign_keys=ON")
```

**Why WAL:**
- Readers don't block writers, writers don't block readers
- A `kill -9` mid-write leaves the database consistent (the WAL is replayed on next open)
- Multiple readers can proceed concurrently

**Why `synchronous=NORMAL`:**
- `FULL` is safer but 10× slower
- `NORMAL` is safe with WAL (the WAL is fsync'd, only the main DB might be incomplete)
- Acceptable tradeoff for a research framework

### 3.3 Concurrency Deduplication

Under parallel evaluation (R74, K8), two workers might try to write the same coordinate simultaneously. The `record_id` uniqueness constraint prevents duplicates:

```python
try:
    store.append(record)
except DuplicateRecord:
    # Another worker already wrote this record; skip
    logger.info(f"Record {record.record_id} already exists; skipping")
```

**No reordering:** SQLite's transaction serialization ensures that even under concurrency, the order of writes is deterministic (by transaction commit time).

### 3.4 Content-Addressed Artifacts

```python
class RecordStore:
    def _store_artifact(self, artifact: Artifact) -> None:
        # Check if artifact already exists
        cursor = self._connection.execute(
            "SELECT 1 FROM artifacts WHERE artifact_hash = ?",
            (artifact.hash,)
        )
        if cursor.fetchone():
            return  # already stored
        
        # Store the artifact
        self._connection.execute(
            """
            INSERT INTO artifacts (artifact_hash, artifact_type, content, size_bytes, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                artifact.hash,
                artifact.type,
                artifact.content,
                len(artifact.content),
                artifact.created_at,
            )
        )
```

**Benefits:**
- Free deduplication (same config used by 100 records stored once)
- Provenance (artifact hash is part of record identity)
- Cache invalidation (kernel cache keyed by artifact hash)

---

## 4. Migration Strategy

### 4.1 The Four Stores

| Store | Current location | Fate |
|-------|-----------------|------|
| `kb.sqlite` | `artifacts/kb/` | Becomes the unified store (evolved) |
| `campaign.db` | `artifacts/campaign/` | Migrated in |
| `ledger.sqlite` | `ceec/` | Migrated in / becomes CEEC reference |
| Optuna `*.db` | `hyperopt/` | Replaced by storage adapter over unified store |

### 4.2 Migration Phases

**Phase 1: Schema evolution (weeks 1-2)**
1. Add `schema_version` column to existing `kb.sqlite`
2. Add `coordinate_hash`, `policy_id`, `run_id` columns
3. Write migration script to populate new columns for existing records
4. Deploy versioned readers for old schema

**Phase 2: Store consolidation (weeks 3-4)**
1. Write importers for `campaign.db`, `ledger.sqlite`, Optuna DBs
2. Run importers in dry-run mode, validate record counts match
3. Run importers for real, verify no data loss
4. Mark old stores as read-only

**Phase 3: Optuna adapter (weeks 5-6)**
1. Implement `OptunaStorageAdapter` that writes to unified store
2. Test with existing Optuna studies
3. Deploy adapter, retire Optuna DBs

**Phase 4: Cleanup (weeks 7-8)**
1. Remove read-only markers from old stores
2. Archive old stores
3. Update documentation

### 4.3 Migration Safety

**Dry-run mode:** Every importer has a `--dry-run` flag that validates without writing.

**Validation queries:**
```sql
-- Count records by source
SELECT 'kb' AS source, COUNT(*) FROM records WHERE source = 'kb'
UNION ALL
SELECT 'campaign', COUNT(*) FROM records WHERE source = 'campaign'
UNION ALL
SELECT 'ledger', COUNT(*) FROM records WHERE source = 'ledger'
UNION ALL
SELECT 'optuna', COUNT(*) FROM records WHERE source = 'optuna';

-- Check for duplicates
SELECT coordinate_hash, COUNT(*) AS n
FROM records
GROUP BY coordinate_hash
HAVING n > 1;
```

**Rollback plan:** Old stores are archived, not deleted. If migration fails, restore from archive.

---

## 5. Performance Budget

### 5.1 K7 vs K9

**K7:** "A search must not become materially slower per evaluation than today's burst path; record overhead must be measured, not assumed."

**K9:** "Governance/evidence metadata must be cheap enough to be always-on; if recording costs are significant, that is a design defect."

These seem to contradict. The resolution: measure the overhead and prove it's negligible.

### 5.2 Overhead Measurement

**Baseline:** Today's burst path writes to `kb.sqlite` with minimal metadata.

**New overhead:**
- MessagePack serialization: ~100 μs per record
- SQLite transaction: ~500 μs per record (WAL mode, single-threaded)
- Coordinate index update: ~100 μs per record
- Status field writes: ~50 μs per record (always-on governance)

**Total overhead:** ~750 μs per record

**Typical evaluation time:** 1-10 seconds per record (training + measurement)

**Overhead percentage:** 0.0075% - 0.075%

**Verdict:** Negligible. K7 and K9 are both satisfied.

### 5.3 Benchmark Harness

```python
def benchmark_store_overhead(n_records: int = 10000) -> None:
    """Measure store write overhead."""
    store = RecordStore(Path("benchmark.sqlite"))
    
    # Generate test records
    records = [generate_test_record() for _ in range(n_records)]
    
    # Measure write time
    start = time.perf_counter()
    for record in records:
        store.append(record)
    elapsed = time.perf_counter() - start
    
    # Report
    print(f"Wrote {n_records} records in {elapsed:.2f}s")
    print(f"Average: {elapsed/n_records*1000:.2f}ms per record")
    print(f"Throughput: {n_records/elapsed:.0f} records/sec")
```

**Acceptance criterion:** Average write time < 1ms per record.

### 5.4 Read Performance

**Typical queries:**
- "All records for coordinate X": ~1ms (indexed by `coordinate_hash`)
- "All claim-eligible records": ~10ms (indexed by status fields)
- "Semantic search for similar records": ~100ms (vector similarity search)

**Verdict:** Acceptable for interactive use.

---

## 6. Requirement Merge Acceptance Process

### 6.1 The 88 → ~60 Merges

SPEC-43 §14.1 proposes merging 88 requirements into ~60 clusters. Each merge must be explicitly accepted or rejected.

### 6.2 Acceptance Criteria

For each merge, verify:

1. **No MUST→SHOULD demotion:** Every MUST requirement in the cluster remains MUST after the merge.
2. **Verification clauses survive:** Every "Verify:" statement from the original requirements is preserved.
3. **Traceability preserved:** Every P# and C# reference is still traceable.
4. **No silent behavior change:** The merged requirement has the same observable behavior as the original set.

### 6.3 Acceptance Process

**Step 1: List the merge**
```
Merge: R7 + R8 + R9 + R11 + R67 → identity schema (B)
Original MUSTs: R7, R8, R9, R11, R67
Original SHOULDs: none
```

**Step 2: Verify no demotion**
```
R7 (MUST) → remains MUST in merged requirement
R8 (MUST) → remains MUST
R9 (MUST) → remains MUST
R11 (MUST) → remains MUST
R67 (MUST) → remains MUST
✓ No demotion
```

**Step 3: Verify clauses survive**
```
R7: "records differing only in lr, seed, or fidelity are distinguishable" → preserved
R8: "every front/average/ranking either stratifies by fidelity or labels the mixture" → preserved
R9: "promotion re-runs count as repeats of their coordinate" → preserved
R11: "a record names the worker policy and versions" → preserved
R67: "cross-version comparison is refused or labeled" → preserved
✓ All clauses survive
```

**Step 4: Verify traceability**
```
P3 (identity/fidelity) → still addressed
P15 (env nondeterminism) → still addressed
C58 (durable record) → still addressed
✓ Traceability preserved
```

**Step 5: Record the decision**
```
Merge: R7+R8+R9+R11+R67 → identity schema (B)
Status: ACCEPTED
Rationale: No demotion, all clauses survive, traceability preserved
Verified by: [name], [date]
```

### 6.4 Rejection Criteria

A merge is rejected if:

1. It demotes a MUST to SHOULD
2. It drops a verification clause
3. It changes observable behavior
4. It breaks traceability

**Example rejection:**
```
Merge: R74 + K8 → concurrency
Status: REJECTED
Rationale: K8 is a constraint, not a requirement; merging conflates different abstraction levels
Action: Keep R74 and K8 separate
```

### 6.5 Merge Acceptance Log

Create `docs/design/merge_acceptance_log.md` with one entry per merge:

```markdown
# Merge Acceptance Log

## R7+R8+R9+R11+R67 → identity schema (B)
- **Status:** ACCEPTED
- **Date:** 2026-09-30
- **Verified by:** [name]
- **Rationale:** No demotion, all clauses survive, traceability preserved

## R74+K8 → concurrency
- **Status:** REJECTED
- **Date:** 2026-09-30
- **Verified by:** [name]
- **Rationale:** K8 is a constraint, not a requirement
- **Action:** Keep separate
```

---

## 7. Implementation Sequence

### 7.1 Phase 1: Core Store (weeks 1-2)

1. Create `packages/computronium-experiment` package structure
2. Implement `RecordStore` class with SQLite backend
3. Implement MessagePack serialization for `Record`, `Coordinate`, `Schedule`, `Provenance`, `Status`, `Payload`
4. Write unit tests for write/read round-trip
5. Write concurrency tests (parallel writes, deduplication)
6. Write crash-safety tests (kill mid-write, verify consistency)

**Exit criteria:** All tests pass; store can write/read 10,000 records in < 10 seconds.

### 7.2 Phase 2: Schema Versioning (weeks 3-4)

1. Implement `SchemaReader` registry
2. Implement `UnknownField` handling
3. Write migration tests (old schema → new schema)
4. Write forward-compatibility tests (new fields ignored by old readers)

**Exit criteria:** Store can read records from schema version 1 and version 2; unknown fields preserved.

### 7.3 Phase 3: Migration Tools (weeks 5-6)

1. Write importers for `kb.sqlite`, `campaign.db`, `ledger.sqlite`
2. Write Optuna storage adapter
3. Write validation queries
4. Test migration on sample data

**Exit criteria:** Migration imports 100% of records without loss; validation queries pass.

### 7.4 Phase 4: Performance Validation (weeks 7-8)

1. Run benchmark harness
2. Profile store overhead
3. Optimize hot paths (if needed)
4. Document performance characteristics

**Exit criteria:** Average write time < 1ms; read queries < 10ms; K7 and K9 satisfied.

---

## 8. Risks & Mitigations

### 8.1 Migration Data Loss

**Risk:** Migration loses records or corrupts data.

**Mitigation:**
- Dry-run mode validates before writing
- Validation queries compare record counts
- Old stores archived, not deleted
- Rollback plan: restore from archive

### 8.2 Performance Regression

**Risk:** Store overhead violates K7.

**Mitigation:**
- Benchmark harness measures overhead
- Acceptance criterion: < 1ms per write
- Profile and optimize if needed
- K9 requires governance to be cheap; if it's not, that's a design defect to fix

### 8.3 Concurrency Bugs

**Risk:** Parallel writes corrupt records or create duplicates.

**Mitigation:**
- `record_id` uniqueness constraint prevents duplicates
- WAL mode ensures crash safety
- Concurrency tests simulate parallel writes
- Transaction serialization ensures deterministic order

### 8.4 Schema Evolution Breaks Old Records

**Risk:** Schema changes make old records unreadable.

**Mitigation:**
- Versioned readers for each schema version
- `UnknownField` handling preserves unknown fields
- Old readers never removed (append-only)
- Migration tests verify old records readable

---

## 9. Acceptance Criteria

The unified store is realized when:

1. **One schema:** All records live in one SQLite database with the schema in §2.1.
2. **Concurrency-safe:** Parallel writes produce no duplicates and no corruption (R74, K8).
3. **Crash-safe:** A `kill -9` mid-write leaves the store queryable and consistent (R12).
4. **Migration complete:** All four stores migrated; old stores archived.
5. **Performance acceptable:** Average write time < 1ms; K7 and K9 satisfied.
6. **Schema evolution works:** Old records readable via versioned readers (R79, K4).
7. **KB analytics preserved:** Vector index, surrogates, causal analysis reachable (K5, R15).
8. **Content-addressed:** Artifacts deduplicated and provenance-carrying.
9. **Queryable:** Claims, promotions, alerts computable from the store (R34, R35, R36).
10. **Documented:** Migration guide, performance report, merge acceptance log complete.

---

## 10. Closing Statement

This specification makes concrete the choices that SPEC-43 deferred. It resolves the package placement contradiction, designs the store schema, specifies the write path and concurrency model, plans the migration from four stores to one, proves the performance budget, and establishes the requirement merge acceptance process.

The result is a store that is:
- **The single source of truth** (R13)
- **Concurrency-safe** (R74, K8)
- **Crash-safe** (R12)
- **Performant** (K7, K9)
- **Evolvable** (R79, K4)
- **Preserving** (K5, R15)

With this foundation in place, the rest of the Experiment Kernel can be built on solid ground.

---

*End of SPEC-43.1. Implementation begins with Phase 1: Core Store.*

----

## Why it's the right fit (grounded in what you already have)

The design isn't generic; it generalizes mechanisms you've already proven:

- **The Universal Registry (A)** is the `ImplementationSpec` 64-spec registry doctrine generalized. You already have 43 primitives + 21 algorithm specs with identity/math/kernel-status/entrypoints, plus `test_registry_completeness_lock` and the promotion-rule lock. The Kernel just applies that same pattern to axes, objectives, capabilities, constraints, and priors.
- **Claims-as-queries (E)** matches CEEC exactly: your chain is already `Experiment → Artifact → Evidence → Derived → Belief → Gated Status → Decision`, with status resolution in `gates.py`. The Kernel's `claim_eligible` predicate is the record-side mirror of that.
- **Wrapper obligations (D)** matches your property-lock culture (L1–L7, J1–J7): guarantees enforced by structure, not discipline.
- **Protocol-over-ABC, PEP 695, Pyright strict, `slots=True`** — the sketches already comply with K1/K2.

So you're not importing a foreign architecture; you're completing a pattern the repo already follows.

## Three corrections before you write code

**1. Reverse SPEC-43.1's package decision.** I put it at `packages/computronium-experiment`, but your `packages/` doctrine is explicit: *"framework-free packages."* The experiment kernel is the opposite — it orchestrates `ontology`, `SystemTrainer`, `compose_joint_system`. It belongs at **`computronium/experiment/`**. If a genuinely framework-free piece later emerges (the predicate DSL, or the registry base), extract *that piece* then.

**2. Don't reinvent content-addressing.** SPEC-43.1's `artifacts` table should delegate to `ceec-core`'s existing content-addressed store (`store.py`, DB-trigger immutability) rather than build a parallel one. The RecordStore holds queryable records; CEEC holds the immutable artifact/provenance chain, linked by content hash. This is Q9's resolution made concrete.

**3. Treat my K7 number as an estimate, not a fact.** I wrote "~750 μs per record — negligible." K7 explicitly says *measured, not assumed*. Run the benchmark harness before locking in "always-on governance." If recording is expensive, that's a design defect to fix (K9), not a reason to make governance optional.

## The gate you must not skip

**Do the §13 union audit before writing any registry code.** Both TODO43 §15 and the specs say it plainly: *"Consolidating on an incomplete union bakes the gaps into the registry permanently."* `lab`, `lightning_/`, and `execution/` are still un-audited (§13.1: six implementations, not four). If you build the `CapabilityRegistry` first and audit later, you'll have to migrate the registry — the exact drift you're trying to kill.
