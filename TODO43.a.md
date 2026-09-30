# SPEC-43 — The Computronium Experiment Kernel
### Unified Search & Evidence System — Design Specification

**Rev 1.0 · 2026-09-29 · Status: DESIGN (resolves TODO43 §12 "Deferred to Design")**
**Implements:** TODO43 Rev 3 (all MUST requirements R1–R88; SHOULD unless waived), Constraints K1–K10, Rev 3 addendum (§13–§15, Appendix C), and the §14 abstractions A–E.

> This document is the design that TODO43 deferred. It names one architecture — **the Experiment Kernel** — built from five composable abstractions, driven by registries and reflection so that adding an axis, a hyperparameter, a policy, a constraint, or an objective is a *declaration*, never an edit to a central table.

---

## 0. Design Doctrine

### 0.1 Governing principles
1. **Single-source everything.** One coordinate schema, one store, one objective registry, one constraint engine, one report path. Every duplication in TODO43 §2 (P1, P7, P10, P11) is a symptom of a missing single source.
2. **Derive, don't duplicate.** Anything that can be *computed from a registry* must be computed, never hand-maintained. This is the structural cure for P4 (prior tables), P13.3 (drifting compatibility matrix), and the Appendix-C gap.
3. **Records are the API.** Search, governance, reporting, and learning are all *queries and projections over records* (R13, R14, R35). No subsystem owns a private view.
4. **Obligations live in the pipeline, not the plugin** (§14-D). A policy may be dumb; the wrapper guarantees coverage, classification, traceability, and crash-safety for *any* plugin.
5. **Governance fails closed** (K6) and is **cheap enough to be always-on** (K9). A record that cannot be validated is not a result.
6. **Preservation is mechanical** (R76–R78). Capabilities, flags, and behaviors are registry rows with conformance tests — deprecation is an explicit registry mutation, not a memory.

### 0.2 The five abstractions (the entire architecture)

| # | Abstraction | One-line definition | Subsumes |
|---|-------------|---------------------|----------|
| **A** | **Universal Registry** | A generic, lock-protected, reflectable `Registry[SpecT]`; every noun in the system is a spec in a registry | R5, R31, R33, R70, R76–R80 |
| **B** | **Identity Schema** | One record schema, four sections: `coordinate ∪ schedule ∪ provenance ∪ status` | R7–R9, R11, R67, R79 (resolves **Q1**) |
| **C** | **Legality Engine** | Serializable predicates over coordinates with recorded reasons; declared *and* discovered | R19, R25, R37, R38, R66 (resolves **Q2**) |
| **D** | **Execution Pipeline** | Small Protocols for policies/stages/evaluators/backends; the wrapper carries all cross-cutting obligations | R16–R18, R39–R40, R70–R72 |
| **E** | **Evidence & Governance** | Statuses/causes/verdicts are record fields; claims/promotion/alerts are pure queries | R10, R34–R36, R58–R59, R64, R83 (resolves **Q9**) |

Everything below is an *instance* or *composition* of A–E.

### 0.3 Metaprogramming stance (the boilerplate killer)

The Kernel deliberately uses Python 3.14's reflective machinery so that the *common case requires zero wiring*. Each technique is listed with the boilerplate it deletes and the requirement it serves:

| Technique | Mechanism | Deletes boilerplate for | Serves |
|-----------|-----------|------------------------|--------|
| **Auto-registration** | `__init_subclass__` + `@register` harvest concrete primitives into registries at import time | Hand-maintained "list of all X" tables | R5, R76, R1 |
| **Hyperparameter reflection** | Primitives declare `__hyperparameters__`; a harvester reflects them into the coordinate schema | `RULE_SPACES` duplication, `_STEP_SIZE_OVERRIDES`, `_ruler_lr` code tables (P2, P4, Appendix C) | R1, R2, R6, R52 |
| **Descriptor-driven validation** | `Hyperparameter`/`AxisSpec` descriptors generate validators, defaults, and override plumbing | Per-axis `validate()` boilerplate | R5, R6, R33 |
| **Serializable predicate DSL** | Constraints/claims are AST expressions, not lambdas — persistable, diffable, hashable | Hardcoded fence dicts (C8), unqueryable gates | R37, R38, R41, R66 |
| **Codegen from registries** | Docs, compatibility matrix, schema validators, and conformance tests are *generated*, then lock-tested against source | Drift between `validate()`, reference docs, and CLI help (P11, P13.3) | R63, R80 |
| **Versioned reader adapters** | Schema carries an explicit version; per-version readers materialize old shapes, unknown fields labeled | Silent re-defaulting of historical records (P3, P7) | R79, K4 |
| **Entry-point extension** | Third-party policies/objectives register via Python entry points into the same registries | Forking to add a sampler | R70, R71 |
| **Property-lock conformance** | Capability specs generate Hypothesis tests; a lock asserts registry↔test bijection | Manual capability bookkeeping (P14) | R77, R78 |

### 0.4 Module layout

```
computronium/experiment/
├─ registry/          # Abstraction A
│  ├─ base.py         # Registry[SpecT], @register, IntegrityLock
│  ├─ axes.py         # AxisRegistry (structural axes, Appendix B)
│  ├─ hyperparameters.py     # HyperparameterHarvester (Appendix C → B.9)
│  ├─ objectives.py   # ObjectiveRegistry (B.7, ~39)
│  ├─ capabilities.py # CapabilityRegistry (C1–C88 + §13 rows)
│  ├─ constraints.py  # ConstraintRegistry
│  ├─ priors.py       # PriorStore
│  ├─ policies.py     # PolicyCatalog (R17)
│  └─ stages.py       # StageCatalog (S1–S11)
├─ schema/            # Abstraction B
│  ├─ identity.py     # RecordIdentity (4 sections)
│  ├─ coordinate.py   # Coordinate, CoordinateSchema (reflected)
│  └─ versioning.py   # SchemaVersion, readers
├─ legality/          # Abstraction C
│  ├─ dsl.py          # predicate AST + evaluator + serializer
│  ├─ engine.py       # ConstraintEngine
│  └─ classify.py     # void vs defect taxonomy
├─ pipeline/          # Abstraction D
│  ├─ stage.py        # Stage Protocol, Fragment
│  ├─ policy.py       # ProposalPolicy Protocol + shipped catalog
│  ├─ allocator.py    # AllocationPolicy (multi-fidelity)
│  ├─ budget.py       # Budget, CostModel
│  ├─ wrapper.py      # PipelineWrapper (all obligations)
│  ├─ determinism.py  # ReplayHash, resume ledger
│  └─ backends.py     # ExecutionBackend Protocol (local/proc/cluster)
├─ evidence/          # Abstraction E
│  ├─ store.py        # RecordStore (single source of truth)
│  ├─ record.py       # Record, Fragment assembly
│  ├─ governance.py   # status predicates, Claim, Promotion, Alert
│  └─ ceec_bridge.py  # CEEC ledger linkage
├─ learning/
│  ├─ surrogates.py   # SurrogatePolicy (EI/EHVI), I(C,U) bridge
│  ├─ failure.py      # FailureEvent, DivergenceDetector, clustering
│  └─ reasoning.py    # hypothesis/literature records
└─ surface/
   ├─ report.py       # one report, all sections (R85)
   ├─ cli.py          # collapsed dispatcher (Q8)
   └─ conformance.py  # capability↔test lock (R77)
```

---

## 1. Abstraction A — The Universal Registry

### 1.1 The generic registry

Every noun — axis, objective, capability, constraint, prior, policy, stage, flag — is a frozen spec in a typed registry. One implementation, many instances (this is the existing `ImplementationSpec` doctrine generalized).

```python
@dataclass(frozen=True, slots=True)
class SpecMeta:
    id: str                     # stable, namespaced: "axis.credit", "objective.accuracy"
    owner: str                  # module / package that defines it
    version: int                # bumped on semantic change (R79)
    tags: frozenset[str] = frozenset()

@dataclass(frozen=True, slots=True)
class Registry[SpecT: SpecMeta]:
    kind: type[SpecT]
    _by_id: Mapping[str, SpecT]

    def get(self, id: str) -> SpecT: ...
    def all(self) -> tuple[SpecT, ...]: ...
    def where(self, **tag_filters) -> tuple[SpecT, ...]: ...
    def schema(self) -> dict: ...          # self-describing, for codegen + R5 discovery
```

### 1.2 Registration by reflection

Concrete primitives register themselves; no central list exists to drift.

```python
def register[SpecT](registry: Registry[SpecT]) -> Callable[[type], type]:
    """Class decorator: instantiate spec from class metadata, insert, return class."""

class CreditAssignment(Protocol):
    def __init_subclass__(cls, **kw) -> None:
        # Auto-harvest cls.__hyperparameters__, cls.__constraints__, cls.__identity_card__
        # into the axis/hyperparameter/constraint registries at class-creation time.
        ...
```

**Integrity locks** (executable, in CI): for each registry, a property test asserts *uniqueness of id*, *totality* (every concrete primitive has exactly one spec), and *no orphans* (every spec resolves to a live class). This is `test_registry_completeness_lock` generalized to all instances (R76, R78).

### 1.3 The seven registry instances

| Registry | Spec type | Seed content | Requirement |
|----------|-----------|--------------|-------------|
| `AxisRegistry` | `AxisSpec` | Appendix B (S,G,D,P,C,U + topology params) | R1, R5 |
| `HyperparameterRegistry` | `Hyperparameter` | **Reflected** from primitives (Appendix C, 37 params) + lr + step size + batch size + optimizer betas/momentum | R1, R2, R6, R52 |
| `ObjectiveRegistry` | `ObjectiveSpec` | B.7 (~39, with direction/weight/normalizer/axis tag) | R31, R33 |
| `CapabilityRegistry` | `CapabilitySpec` | C1–C88 + §13.3/§13.4 rows (stage, owner, verifying test) | R76, R77 |
| `ConstraintRegistry` | `Constraint` | `SystemConfig.validate()` rules + task fences + §13.2 `apply_constraints` | R37, R63, R66 |
| `PriorStore` | `Prior` | Ruler-LR table, step-size overrides — **as data** | R52, R55 |
| `PolicyCatalog` / `StageCatalog` | `PolicySpec` / `StageSpec` | R17 policy union; S1–S11 | R17, R39 |

**Flag inventory as a view (R78):** Appendix A's flags are not a separate artifact; they are a *projection* of the CapabilityRegistry (`capability → flags → tests`). A lock asserts the projection is current, so the inventory cannot drift.

### 1.4 Codegen from registries
Generated, then lock-tested against source (so drift fails CI):
- `docs/generated/` capability & objective listings (R80 "what we can do").
- The ontology **compatibility matrix** from the ConstraintRegistry (R63) — replacing hand-maintained reference docs.
- JSON-Schema validators per `AxisSpec`/`Hyperparameter` (R5 runtime discovery).
- Conformance test stubs per `CapabilitySpec` (R77).

---

## 2. Abstraction B — Coordinate & Record Identity Schema

### 2.1 Four identity sections (resolves **Q1**)

A **coordinate** defines *which system*; a **record identity** defines *which measurement of it*. Seeds, fidelity, epochs, and batch limits are **not** part of the coordinate — they are the schedule. This answers Q1 precisely: *"same cell"* = equal `coordinate`; *"same measurement"* = equal full `identity`.

```python
class IdentitySection(Enum): COORDINATE; SCHEDULE; PROVENANCE; STATUS

@dataclass(frozen=True, slots=True)
class RecordIdentity:
    coordinate:   Coordinate        # structural axes + hyperparameters  (§2.2–2.3)
    schedule:     Schedule          # fidelity_tier, seed, epochs, batch_limit, budget_id
    provenance:   Provenance        # device, dtype, workers, lib versions, code sha, dataset_id+version
    status:       StatusRef         # governance fields (Abstraction E) — content-addressed
```

R7/R8/R9 fall out: records differing only in `schedule.seed` or `schedule.fidelity_tier` are *distinct records sharing a coordinate key*; any front/average either stratifies by `fidelity_tier` or labels the mixture (a derived comparison guard, not a runtime check scattered across tools).

### 2.2 Structural axes (Appendix B, R1)

```python
@dataclass(frozen=True, slots=True)
class AxisSpec[ValueT]:
    meta: SpecMeta
    kind: AxisKind                     # STRUCTURAL_DISCRETE | STRUCTURAL_ENUM
    domain: Domain[ValueT]             # enumerated members (B.1–B.6)
    topology_params: tuple[Hyperparameter, ...] = ()   # B.2 per-topology keys
```

**Plasticity is a first-class axis (resolves Q7).** The README's P-axis program (ψ, frozen-θ, NTM/NCA, adaptation/migration) is central; `plasticity` is therefore a structural axis with its own hyperparameters and objectives (`psi_capacity`, `consolidation_cost`, `rewrite_rate`), not a credit/update concern.

### 2.3 Hyperparameter reflection — the Appendix-C cure (resolves P2/P4)

The 37 continuous hyperparameters, learning rate, step size, batch size, and optimizer parameters are **declared on the primitive that owns them** and harvested by reflection. There is no `RULE_SPACES` table to drift from, and no prior table in code.

```python
@dataclass(frozen=True, slots=True)
class Hyperparameter:
    meta: SpecMeta
    name: str
    kind: ParamKind                    # CONTINUOUS | DISCRETE | CATEGORICAL
    domain: Range | tuple              # Range(lo, hi, scale=LOG|LINEAR) for continuous
    default: Scalar | None
    section: IdentitySection = IdentitySection.COORDINATE
    prior: str | None = None           # PriorStore id (data, overridable) — R52

# Declared inline on the primitive — the ONLY place this knowledge lives:
class EqPropCredit:
    __hyperparameters__ = (
        Hyperparameter("beta",     CONTINUOUS, Range(0.01, 10.0, LOG), default=0.5),
        Hyperparameter("max_steps",DISCRETE,   Range(1, 200),          default=20),
        Hyperparameter("damping",  CONTINUOUS, Range(0.0, 1.0),        default=0.0),
        # … all 18 eqprop slots from Appendix C …
    )
```

```python
def harvest_schema(axes: Registry[AxisSpec], prims: Registry) -> CoordinateSchema:
    """Reflect structural axes + every primitive's __hyperparameters__ into one schema.
    Continuous and discrete share this representation (R4)."""
```

**Why this is the fix:** `hyperopt/search_space.py::RULE_SPACES`, `_STEP_SIZE_OVERRIDES`, `_DYNAMICS_STEP_SIZE_OVERRIDES`, and `_ruler_lr` all become *projections* of `HyperparameterRegistry ∪ PriorStore`. A lock asserts `harvest_schema() ⊇ Appendix B ∪ Appendix C` and that every hyperparameter has exactly one owner. Adding a primitive automatically extends the searchable space — "describable here, inexpressible there" (P1) is structurally impossible.

- **R2 (lr searchable):** `learning_rate` is a `Hyperparameter(section=COORDINATE)` on every trainable primitive; a run varies it like any axis.
- **R6 (override + record effective value):** overrides flow through the descriptor; the *effective* value is written to the record.
- **R3 (substrate comparable):** substrate `noise_level`/`precision` are hyperparameters on the substrate axis, so two substrates appear in one comparable set.

### 2.4 Coordinate instances & validation

```python
@dataclass(frozen=True, slots=True)
class Coordinate:
    values: Mapping[str, Scalar]       # axis/hyperparameter name -> value
    def schema(self) -> CoordinateSchema: ...
    def key(self) -> str: ...          # canonical hash of the COORDINATE section only
```

`CoordinateSchema.validate(coord)` is generated from the axis/hyperparameter descriptors (single source). Every numeric default is overridable per-run and per-coordinate; the effective value is recorded (R6).

### 2.5 Schema versioning (R79, K4)

`RecordIdentity` carries `schema_version`. Readers are registered per version (`READERS: dict[int, Reader]`); a historical artifact loads through its version's reader, and **unknown fields are labeled `UnknownField`, never silently defaulted**. This keeps old records readable for the life of the artifacts without freezing the schema.

---

## 3. Abstraction C — The Legality Engine

### 3.1 Serializable predicate DSL

Constraints and claims must be **stored, diffed, hashed, and queried** — so they are AST expressions, not lambdas.

```python
type Expr =
  | Field(path: str)                     # "credit" | "substrate.noise_level" | "schedule.fidelity"
  | Lit(value: Scalar)
  | Cmp(op, lhs: Expr, rhs: Expr)        # == != < <= > >=
  | In(field: Expr, values: tuple)
  | Between(field, lo, hi)
  | And(tuple[Expr,...]) | Or(...) | Not(Expr)
# serializable to dict/JSON; evaluable against a Coordinate; content-hashed for identity
```

### 3.2 Constraint model; declared vs discovered (resolves **Q2**)

```python
class ConstraintOrigin(Enum): DECLARED; DISCOVERED   # space-time vs run-time
class ConstraintScope(Enum): GLOBAL; RUN

@dataclass(frozen=True, slots=True)
class Constraint:
    meta: SpecMeta
    kind: ConstraintKind      # STRUCTURAL_VOID | TASK_FENCE | FAIRNESS | OPERATING_POINT | RUNTIME_DEFECT
    predicate: Expr
    reason: str               # recorded, queryable (R37)
    origin: ConstraintOrigin
    scope: ConstraintScope
```

- **Q2 answered:** a *void* is `DECLARED` (infeasible by construction; rejected at S4 before compute is paid; remembered by resume). A *defect* is `DISCOVERED` (infeasible at runtime; recorded at S6 and fed back as a `GLOBAL` suppression). Same engine, one `origin` field decides when cost is paid and what resume remembers.
- **R42 falls out by construction:** coverage, reports, and reference docs all read the same `ConstraintRegistry`, so a void found at S4 and one found at S6 appear identically downstream.
- **Global suppression vs run scoping** stay distinct (§14.3): `GLOBAL` constraints (known-bad coordinates, defects) are never re-proposed by *any* policy (R38); `RUN` constraints (operating point, fairness) scope a single run (R25, R66).

### 3.3 Void/defect classification (C11/C12, R19)

`classify.py` holds the taxonomy (`_VOID_CATEGORIES`, defect causes) as registry data. The wrapper applies classification to **every** policy's proposals — a model-based run's rejections are classified identically to a driver's (R19). The "unclassified" bucket is a counted, owned signal (R59).

### 3.4 Compatibility matrix generation (R63)

The ~30 rules of `SystemConfig.validate()` are reflected into the `ConstraintRegistry` at startup; the published compatibility matrix is *generated from* that registry and lock-tested to match `validate()` behavior. Reference docs can no longer drift from the validator (P13.3).

---

## 4. Abstraction D — The Execution Pipeline

### 4.1 Stage Protocol (S1–S11, R39/R40)

```python
@dataclass(frozen=True, slots=True)
class Fragment:
    stage: StageId
    payload: Mapping[str, Scalar | Nested]   # typed, serializable; {} for a no-op

class Stage(Protocol):
    stage_id: StageId
    def run(self, ctx: RunContext, inflow: Fragment) -> Fragment: ...
```

Every stage runs for every policy; a stage with nothing to say emits an **explicit empty fragment** (R39). Stages are swappable Protocols that never change the record schema (R40). The `StageCatalog` (registry) holds S1 Frame … S11 Report; capability rows C1–C88 map onto stage fragments.

### 4.2 ProposalPolicy Protocol + the preserved catalog (R16/R17)

```python
class ProposalPolicy(Protocol):
    def propose(self, state: PolicyState, space: CoordinateSpace,
                budget: Budget) -> Iterator[Coordinate]: ...
    def observe(self, record: Record) -> None: ...     # model-based policies learn
```

**R17 is the shipped catalog** (the preservation proof): `StratifiedRandom`, `RoundRobinGrid`, `UniformRandom`, `ModelBased(TPE|NSGA-II, pruners)`. Each is a registered `PolicySpec`; third-party samplers register via entry points (R71). Because policies implement only `propose/observe`, the *next-coordinate choice is substitutable without changing evaluation, record, or governance* (R16). A proposal carries its provenance — the policy id and the state/evidence it acted on (R20).

### 4.3 The Pipeline Wrapper — where the obligations live

The wrapper, not the plugin, guarantees the cross-cutting behavior for **any** policy/stage/evaluator/backend:

| Obligation | Emitted by wrapper | Requirement |
|-----------|--------------------|-------------|
| Axis-coverage statistics per run, regardless of policy | coverage fragment | R18 |
| Void/defect classification of every proposal/rejection | legality fragment | R19 |
| Proposal provenance (policy + evidence) | traceability fragment | R20 |
| Stage fragments for all S1–S11 (incl. no-ops) | stage assembly | R39 |
| Crash-safe, atomic store write | WAL transaction | R12 |
| Environment provenance capture | provenance section | R11, R28 |
| Budget consumption accounting | budget fragment | R21 |

This is the decisive structural move: **coverage guarantees can never be silently lost by a clever policy** (the §10 risk), because they are not the policy's job.

### 4.4 Budget & cost model (R21–R24)

```python
@dataclass(frozen=True, slots=True)
class Budget:
    soft: Duration; hard: Duration; target_cells: int | None
    # one concept governs every search; soft/hard stop defined once (P5 unified)

class CostModel(Protocol):
    def estimate(self, coord: Coordinate, schedule: Schedule) -> CostEstimate: ...
```

- One `Budget` interface exposes consumed/remaining for every policy (R21).
- `CostModel` is **learned from recorded per-stage walltime breakdowns** and improves as records accumulate (R24); a dry-run reports an estimate with stated uncertainty (R23).
- Walltime/throughput comparisons are guarded: valid only between records of comparable fidelity+budget, else refused or labeled (R22).

### 4.5 Multi-fidelity allocator (R46–R51)

Allocation is a **separate Protocol** from proposal, so any policy pairs with any allocator:

```python
class AllocationPolicy(Protocol):
    def allocate(self, population: tuple[Coordinate,...], evidence: RecordStore,
                 budget: Budget) -> AllocationPlan: ...   # promote | abandon | defer per member
```

**Reference implementation — evidence-driven successive promotion** (replaces the fixed ladder, P12): evaluate the population at L0; using interim metrics + uncertainty + cost, promote the promising subset to L1/L2 and early-terminate the clearly inferior; repeat. Acceptance is measured, not assumed: **cost-to-rank must beat the uniform baseline at equal ranking quality** (R46).

- Promotion decisions reference interim evidence stored in the record (R47).
- Compute spent before abandonment is recorded; a **waste report** flags repeatedly-measured-to-no-gain coordinates (R48) — the 1357 s / 1457-clamp case becomes a line item.
- Compute is appendable across sessions without losing prior evidence (R49).
- A **DivergenceDetector** stage watches telemetry (clamp storms, NaN, loss explosion, spectral radius, no-improvement) and raises a first-class signal within a bounded fraction of cost (R50); guard-kill records name the signal, its value, and the compute saved (R51).

### 4.6 Determinism, resume, replay (R26–R30)

- **Replay hash (R27):** a run records a hash of `(spec, seed, policy-state sequence)`; resume re-checks it. Determinism is *asserted*, not assumed from global seeding.
- **Resume ledger (R26):** recorded coordinates are skipped on resume; kill/resume yields no duplicates and no reordered coverage.
- **Environment nondeterminism (R28):** dataloader worker policy, daemon concurrency, and device nondeterminism are explicit run properties with recorded fallbacks (closes P15).
- **Failure isolation (R29):** each evaluation runs in an isolated context; an injected mid-run failure leaves sibling records and the store intact.
- **Checkpoint/restore (R30):** at run and evaluation granularity, preserving budget state and evidence.

### 4.7 Concurrency (R74, K8)

Parallelism is a schedule parameter. Store writes are serialized (WAL + optimistic concurrency); the wrapper dedupes by `identity` hash. A parallel run produces the *same records* as a serial one — no duplicates, no reordering.

### 4.8 Kernel-cache scoping (R75, resolves **Q13**)

Compiled-kernel cache is keyed by the **full identity needed for correctness**: `(run_id, coordinate.key, device, dtype)` — run-scoped, provenance-carrying, safely invalidating, inspectable as records. **No module-level singleton** (K10; P16 is the cautionary example). The kernel-ladder evidence trail (parity + microbench JSONL, git-SHA tagged — §13.3) is itself a record type.

---

## 5. Abstraction E — Evidence & Governance

### 5.1 The Record Store (R13, K5)

One append-only store, an **evolution of the KB** (preserving vector/surrogate/causal — K5, R15):

- **WAL-mode SQLite**, content-addressed artifacts → crash-safe, atomic (R12).
- Vector index (C59), `SurrogateManager` (C60), `CausalAnalyzer` (C61), query engine (C62) are **views over the same records**, reachable from every policy and report (R15).
- No implementation owns a private store; every record is queryable by all (R13). Reporting is derivable from the store alone, one implementation per report (R14).

### 5.2 Governance as stored predicates (resolves **Q9**)

Statuses, causes, and verdicts are **record fields** written by their producing stage. The CEEC ledger remains the authoritative append-only chain; the record carries the *status* plus a **content-addressed link** to the ledger entries. Q9 is settled: status is a field with a provenance link, not a side artifact only one path understands.

```python
@dataclass(frozen=True, slots=True)
class Status:
    gate_verdict: Verdict           # PASS | FAIL | PENDING
    defect: DefectRef | None
    fidelity_tier: Tier             # L0 | L1 | L2
    quarantine: bool
    reproducibility: ReproRef | None
    claim_eligible: bool            # DERIVED predicate, never asserted by the run
    ceec_link: str | None           # content-addressed ledger entry
```

**R10:** `claim_eligible` is computable from the record alone (no run-time context), and holds regardless of which implementation wrote it. **K6:** a record that fails validation is never a result.

### 5.3 Claims, promotion, alerts are pure queries

- **Claim (R35, R64):** a predicate over records — CAMPAIGN_PLAN §7 expressible as one filter excluding quarantined/gate-failed cells, and *no claim is expressible without `n_seeds` and variance*. A claim is derived, never asserted by the producing run.
- **Promotion (R36):** `select(predicate) → re-evaluate at higher fidelity`, applicable to any policy's output.
- **Matched comparison (R65):** comparisons against a reference control are enforced at matched params/FLOPs/walltime; unmatched pairs are refused.
- **Alerts (R83, resolves Q14):** defined over record predicates (breakthrough ≥2%, cascade >30% failures, completion); they **notify only** — run/stop stays human. Routing = predicate-signature → severity → webhook, with dedup by signature.

### 5.4 Dataset/data integrity (R67/R68/R69)

Dataset/split identity + version are provenance fields; cross-version comparisons are refused or labeled (R67). Leakage checks (R68) and robustness dimensions (R69: noise/quantization/shift) are expressible in the run spec and recorded.

---

## 6. Learning & Failure Intelligence

### 6.1 Priors as data (R52, resolves **Q4/Q12**)

The ruler-LR table and the ~30 step-size overrides are **migrated to `PriorStore` records** (value + uncertainty + provenance + code version), attached to their hyperparameter via `Hyperparameter.prior`. Search *starts from* and can *exceed* them; they are overridable and applied only within stated uncertainty (R55). The code tables are retired (Appendix A records the migration — R78). Q4: the ruler is an **input prior**, not an authoritative default. Q12: convert to priors, retire the code.

### 6.2 Surrogates in the loop (R54, resolves **Q10**)

`SurrogatePolicy` wraps any `ProposalPolicy` and steers it with models over records (EI / EHVI), including the **I(C,U) learnability model** and `hyperparameter_metamodel` (P9 closed). New runs warm-start space/policy from prior records with transfer provenance (R53); learned quantities transfer as priors with uncertainty (R55); lessons are queryable, tied to code versions (R56). Q10: surrogates **enter the search loop**, not just analysis.

### 6.3 Failure intelligence (R58–R62)

```python
class FailureCause(Enum):
    INFEASIBLE_BY_CONSTRUCTION; GATE_REJECTED; GUARD_KILLED; DEFECT;
    TIMEOUT; NON_FINITE; USER_STOPPED; UNCLASSIFIED

@dataclass(frozen=True, slots=True)
class FailureEvent:
    cause: FailureCause; severity: Severity
    signal: str | None; value: Scalar | None      # which detector, at what value
    identity: RecordIdentity
```

Causes/severities are **fields, not log text** (R58). `UNCLASSIFIED` is counted and owned (R59). A defect emits a **minimal reproducer** + candidate regression test (R60); failures **cluster across runs** to find systemic causes once (R61); a fix is **linkable to the failures it closes** (R62).

### 6.4 Reasoning records (R57, resolves **Q15**)

Reasoner chains, LLM proposals, and retrieved literature become **records with provenance**, linked to the experiments they motivated (P17 closed). Q15: provenance linkage is mandatory; active in-loop hypothesis generation is an opt-in capability that writes the same record type.

---

## 7. Surface

### 7.1 One report (R85–R88, resolves **Q8**)

One command, derived from the store alone, covering: objectives & fronts (by fidelity), axis coverage, budget consumed, failures by cause, promotion history, claim-eligible records, and **axis attribution** (R86) as a section. Figures/manifests are pinned (R87); narrative handoff summaries derive from records (R88). Q8: **one library, thin front-ends** — reporting logic lives in `surface/report.py`; CLI/dashboard are projections.

### 7.2 CLI collapse (R78/R80)

The many entry points (`continuous`, `campaign`, `frontier`, `search`, `verify`, `pareto`, …) collapse into one dispatcher with **scope arguments**. Root/task/scope conventions are implemented once. **Documented-command conformance tests** fail when a documented invocation drifts (P11); **run profiles** (`quick-verify`, `production-map`, `maturation`, `claim`) are data, each conformance-tested (R80).

### 7.3 Capability preservation & conformance (R76–R78, resolves **Q5**)

The `CapabilityRegistry` (C1–C88 + §13 rows) is machine-readable (id, stage, description, owner, verifying test). A **conformance suite asserts every registered capability**; CI fails if a capability loses its test. Q5: the suite **gates merges, with an explicit recorded waiver path** — retirement is only via an explicit registry change with rationale (R78). This is the enforcement point, not the test.

### 7.4 Human control & live operation (R81–R84)

A run is pausable/steerable/resumable mid-flight (change budget, add/remove constraints, pin/ban coordinates) without corrupting records (R81); long-running discovery runs as a **service that re-plans as evidence accumulates** (R82); alerts notify only (R83); **operator intent** is first-class data (R84).

---

## 8. Open-Question Resolutions (Q1–Q16)

| Q | Resolution | Basis |
|---|-----------|-------|
| **Q1** seeds/fidelity in coordinate? | No — they are **Schedule**; "same cell"=coordinate, "same measurement"=full identity | Abstraction B |
| **Q2** void = space or evaluation? | `DECLARED` (space) vs `DISCOVERED` (runtime), one engine | Abstraction C |
| **Q3** default lr search? | Both expressible; recommend **model-based seeded from the ruler prior** (sample-cost) | R2, R52 |
| **Q4** ruler table role? | **Input prior** (data), never authoritative default | §6.1 |
| **Q5** conformance gate? | **Gates merges** with recorded waiver path | §7.3 |
| **Q6** parallel in first release? | **Yes** — concurrency-safe store is foundational (R74, K8) | §4.7 |
| **Q7** plasticity an axis? | **Yes**, first-class structural axis (README P-axis program) | §2.2 |
| **Q8** reporting shape? | **One library, thin front-ends** | §7.1 |
| **Q9** CEEC ledger? | Status is a **record field + content-addressed link** to the authoritative ledger | Abstraction E |
| **Q10** surrogates? | **In the loop** as a policy wrapper | §6.2 |
| **Q11** matched-cost/robustness? | Matched-cost **mandatory for claims**; robustness **opt-in per study** | §5.3 |
| **Q12** override tables? | **Convert to priors**, retire code, record migration | §6.1 |
| **Q13** kernel-cache scope? | `(run, coordinate.key, device, dtype)` — full correctness identity | §4.8 |
| **Q14** alert routing? | predicate-signature → severity → webhook, dedup by signature | §5.3 |
| **Q15** literature/LLM depth? | Provenance linkage mandatory; active generation opt-in | §6.4 |
| **Q16** fenced tasks? | Excludable per run via `RUN` constraints; fence reason visible in proposals | §3.2 |

---

## 9. Constraint Compliance (K1–K10)

| K | How the Kernel respects it |
|---|---------------------------|
| **K1** | Python 3.14+, `uv`, single `uv.lock`; no new mandatory runtime dep (optuna/torch already required) |
| **K2** | Ruff format/lint; Pyright strict on all new modules; **Protocol over ABC, no `Any`** throughout |
| **K3** | No blocking I/O in async paths; wrapper store writes are the only I/O boundary |
| **K4** | Versioned readers materialize old shapes (R79); artifacts remain readable |
| **K5** | KB vector/surrogate/causal preserved as store views (R15) |
| **K6** | Governance fails closed; `claim_eligible` is a derived predicate |
| **K7** | Per-evaluation overhead measured, not assumed; registry/conformance cost budgeted (K9) |
| **K8** | Concurrency dedupes by identity hash; parallel ≡ serial records |
| **K9** | Evidence metadata is cheap and **always-on**; if recording is costly, that's a design defect |
| **K10** | **No module-level singletons**; all run-scoped state (incl. kernels) is identity-scoped |

---

## 10. Requirement Compliance Matrix (by pillar, §14.2)

| Pillar | Design component | Requirements covered |
|--------|------------------|----------------------|
| **Schema** | Abstraction A + B (registries, hyperparameter reflection, identity) | R1–R9, R11, R31–R33, R67, R79 |
| **Execution** | Abstraction D (stages, policies, wrapper, budget, allocator, determinism, concurrency, kernels) | R16–R30, R39–R45, R46–R51, R70–R75 |
| **Legality** | Abstraction C (DSL, engine, classification, suppression) | R19, R25, R37, R38, R42, R66 |
| **Evidence** | Abstraction E (store, governance predicates, claims, CEEC) | R10, R12–R15, R22, R34–R36, R58–R59, R64, R65, R83 |
| **Learning** | Priors, surrogates, failure intelligence, reasoning records | R52–R63 |
| **Surface** | Reports, CLI, conformance, operations | R14, R63, R76–R78, R80–R88 |

**Acceptance (§8 of TODO43) is met when** the system yields: one schema expressing Appendix B∪C; records at >1 lr/substrate/fidelity distinguishable and never averaged unlabeled; any policy's records queryable/claim-evaluable from one store; four policies traversing one space with coverage reported; non-uniform evidence-driven allocation with detectable waste; machine-readable, clustered, reproducer-yielding failures; kill/resume with no duplicates under every policy incl. parallel; every claim carrying n/variance/matched-cost; every capability registered and conformance-tested; a versioned diffable spec; reasoning records linked to experiments; and run-scoped, provenance-carrying kernels.

---

## 11. Migration & Sequencing (per §15)

1. **Fix the union first.** Audit `computronium-lab`, `lightning_`, `execution` (§13.1); add Appendix C as B.9; add the §13.3/§13.4 capability rows and §13.5 domains. *Consolidating on an incomplete union bakes the gaps in permanently.*
2. **Stand up Abstractions A–E** in the order A → B → C → D → E (each depends only on the prior).
3. **Migrate prior tables** to `PriorStore`; retire `_ruler_lr`/`_STEP_SIZE_OVERRIDES` with recorded migration (R78).
4. **Collapse the stores** into the RecordStore with versioned readers for `kb.sqlite`/`campaign.db`/`ledger.sqlite`/Optuna DBs.
5. **Collapse the CLI** behind one dispatcher + profiles; add documented-command conformance.
6. **Renumber** requirements under the pillar structure after review.

---

## 12. Risks & Invariants (carried from TODO43 §10, §14.3)

- **Coverage never delegated to plugins** — the wrapper owns it (mitigates the stratified-behind-model-based risk).
- **Non-uniform allocation bias** — mitigated by recorded allocation rationale (R47) + per-run coverage (R18).
- **Conformance as ceremony** — the registry, not the test, is the enforcement point; retirement requires an explicit change (R78).
- **One store tempting KB-feature removal** — K5/R15 forbid it; analytics are views, not casualties.
- **Serializable spec fossilizing assumptions** — the spec is a versioned contract, not a schema freeze (R79).
- **Singleton habits recreating P16** — K10 is enforced by a lock that fails on module-level run-scoped state.
- **No MUST→SHOULD demotion**; R17 remains the policy catalog; global suppression stays distinct from run scoping; K5/K6/K9/K10 are design invariants, not mergeable requirements.

---

### Closing statement

The Experiment Kernel reduces TODO43's 88 requirements to **five composable abstractions** — registries, identity, legality, pipeline, evidence — and uses **reflection and codegen** so that the system's knowledge (axes, hyperparameters, constraints, priors, capabilities) lives *exactly once*, on the thing it describes, and is harvested rather than hand-maintained. The result is a framework where adding a learning rule, a substrate, an objective, or a policy is a declaration; where every measurement is attributable and every claim is a query; and where the union of today's capabilities is preserved not by memory, but by lock.
