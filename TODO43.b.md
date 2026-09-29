# Computronium Unified Experiment Framework — Design Specification

**Version:** 1.0 · **Status:** Design (resolves TODO43 Rev 3 §12 "Deferred to Design")
**Scope:** Architecture, interfaces, data model, and extensibility mechanisms satisfying R1–R88.
**Non-goals:** Implementation code, sequencing, effort estimates.

---

## 0. Design Philosophy

Five principles govern every decision below. They are the reason the system can satisfy 88 requirements without 88 mechanisms.

| Principle | Meaning | Primary beneficiary |
|---|---|---|
| **P1 — Declare once, derive everything** | A single declarative spec generates registries, validators, CLI flags, docs, test scaffolds, and serialization schemas. No hand-maintained parallel tables. | R5, R31, R63, R76–R80; kills P4, P11 |
| **P2 — Data over code** | Priors, constraints, objectives, and policies are *records and predicates*, not branches. Changing behavior = inserting a row, not editing a function. | R37, R38, R52; kills P4 |
| **P3 — Queries over side effects** | Claims, promotions, alerts, and reports are *pure queries* over stored record fields. No code path "asserts" a result. | R10, R34, R35, R83; kills P6 |
| **P4 — Obligations on the pipeline, not the plugin** | Coverage, traceability, and governance are emitted by the *wrapper* around any plugin. A plugin cannot forget them. | R16–R19, R39–R40; kills P1 |
| **P5 — Identity is the API** | Every object — coordinate, record, policy, capability — has a stable, versioned, content-derived identity. Comparison, caching, and governance all key on identity. | R7–R9, R75; kills P3, P16 |

These five principles map 1:1 onto the five consolidation abstractions (A–E) from TODO43 §14, which this specification adopts and refines.

---

## 1. The Five Abstractions (System Overview)

```
┌─────────────────────────────────────────────────────────────────────┐
│                     A. REGISTRY SYSTEM                               │
│   (axes, objectives, capabilities, constraints, priors, plugins)    │
│   One generic Registry[Spec] + declarative spec dataclasses          │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ resolves names → specs at runtime
        ┌──────────────────────┼──────────────────────────────────────┐
        ▼                      ▼                                      ▼
┌───────────────┐   ┌──────────────────────┐   ┌────────────────────────┐
│ B. RECORD     │   │ C. CONSTRAINT ENGINE │   │ D. STAGE PIPELINE      │
│ SCHEMA &      │◄──│ (legality predicates)│◄──│ (11 stages × plugins)  │
│ SINGLE STORE  │   └──────────────────────┘   └───────────┬────────────┘
└───────┬───────┘                                          │
        │ status/causes/verdicts = fields                  │ emits records
        ▼                                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│              E. GOVERNANCE AS STORED PREDICATES                      │
│   claims, promotion, alerts, reports = queries over B               │
└─────────────────────────────────────────────────────────────────────┘
```

Every requirement in §5 of TODO43 is satisfied by exactly one of these five abstractions or by their composition. §14 provides the full traceability matrix.

---

## 2. Abstraction A — The Registry System

### 2.1 Problem solved
TODO43 has at least seven things that need a registry: coordinate axes (R5), objectives (R31), capabilities (R76), flags (R78), constraints (R37, R66), priors (R52), and extension points (R33, R70). Today each is a separate mechanism. This abstraction provides **one**.

### 2.2 Core type: `Registry[SpecT]`

```python
from typing import TypeVar, Protocol, runtime_checkable
from dataclasses import dataclass, field

SpecT = TypeVar("SpecT", bound="RegistrySpec")

@runtime_checkable
class RegistrySpec(Protocol):
    """Every registrable thing is a frozen, hashable, versioned spec."""
    id: str                    # globally unique, namespaced: "axis.learning_rate"
    version: int               # monotonic; bumps are additive, never destructive
    stage: str | None          # lifecycle stage (S1..S11) or None
    owner: str                 # team / module responsible
    status: SpecStatus         # active | deprecated | retired

class Registry(Generic[SpecT]):
    """
    One implementation, many instances. Append-only, versioned,
    integrity-locked. Instances are created via @registry_type.
    """
    def register(self, spec: SpecT) -> None: ...
    def get(self, id: str, version: int | None = None) -> SpecT: ...
    def enumerate(self, **filters) -> tuple[SpecT, ...]: ...
    def diff(self, other: "Registry[SpecT]") -> RegistryDiff: ...
    def to_schema(self) -> dict: ...        # for codegen / docs
    def verify_integrity(self) -> None: ...  # the "lock"
```

**Metaprogramming mechanism.** Registration is declarative via a class decorator + `__init_subclass__`, so adding a new spec type requires zero registry code:

```python
@registry_type("axis")                      # creates Registry[AxisSpec] singleton
@dataclass(frozen=True, slots=True)
class AxisSpec:
    id: str
    version: int
    kind: AxisKind                          # categorical | ordinal | continuous
    domain: Domain                          # legal values / range / scale
    availability: Predicate | None          # when this axis is searchable (see §5)
    default: object | None
    override_scope: OverrideScope           # per_run | per_coordinate | both
    # --- derived automatically by the registry metaclass ---
    # validator, CLI flag, doc entry, serialization schema, test scaffold
```

The decorator generates, at import time:
1. A **validator** (type + domain check) — satisfies R5 "legal values discoverable at runtime."
2. A **CLI flag** in the `comp` dispatcher — satisfies R78 "flag maps to capability."
3. A **doc entry** rendered by `generate_docs.py` — satisfies R80 "documented-command conformance."
4. A **serialization schema** for the record store — satisfies R79.
5. A **property-test scaffold** (Hypothesis strategies over `domain`) — feeds R77 conformance.

This is the single most important metaprogramming move: **the flag inventory (Appendix A), the axis enumeration (Appendix B+C), and the objective registry (B.7) all become *views* over registries, not parallel files.** Drift is structurally impossible.

### 2.3 Registry instances

| Instance | Spec type | Satisfies |
|---|---|---|
| `axes` | `AxisSpec` | R1, R5, App B+C |
| `objectives` | `ObjectiveSpec` (direction, weight, normalizer, axis_tag) | R31, R33, C1 |
| `capabilities` | `CapabilitySpec` (id, stage, description, verifying_test) | R76, R77 |
| `constraints` | `ConstraintSpec` (predicate, reason, scope) | R37, R66, §5 |
| `priors` | `PriorSpec` (coordinate pattern → value, uncertainty, provenance) | R52, R55 |
| `plugins` | `PluginSpec` (policy / stage / evaluator / backend) | R70, R71, R72 |
| `flags` | *view* over other registries | R78 |

### 2.4 Integrity locks
Each registry instance is protected by a **conformance test** (R77) that:
- Asserts every registered spec resolves to a live implementation.
- Asserts every live implementation of that kind has a spec (completeness).
- Fails CI if a capability loses its test or a spec is silently removed.

Deprecation is only via an explicit `status: retired` + `migration_note`, never deletion (R78).

---

## 3. Abstraction B — The Record Schema & Single Store

### 3.1 Problem solved
Record identity does not disambiguate measurements (P3); four stores disagree (P7); fidelity is not first-class (P3, P12). This abstraction defines **one schema** and **one store**.

### 3.2 The four-section identity (resolves Q1)

A `Record` is the atomic unit of durable evidence. Its identity is the union of four **disjoint** sections:

```python
@dataclass(frozen=True, slots=True)
class Record:
    # ── Section 1: COORDINATE (what system) ─────────────────────────
    coordinate: Coordinate            # full Appendix B+C axis values

    # ── Section 2: SCHEDULE (how measured) ──────────────────────────
    schedule: Schedule                # fidelity tier, seed, epochs, batch limit

    # ── Section 3: PROVENANCE (context) ─────────────────────────────
    provenance: Provenance            # env, device, dtype, code version, data version

    # ── Section 4: STATUS (governance) ──────────────────────────────
    status: Status                    # gate verdict, defect, cause, severity

    # ── Payload (not identity) ──────────────────────────────────────
    metrics: MetricsBundle
    telemetry: Telemetry              # per-epoch, settle, clamp, spectral
    schema_version: int
    record_id: ContentHash            # sha256 over sections 1–3 + payload
```

**Resolution of Q1.** "The same **cell**" = same `coordinate`. "The same **measurement**" = same `(coordinate, schedule, provenance)`. Repeated measurements of one coordinate are **distinct records sharing coordinate identity** (R9). This is enforced by the store's uniqueness constraint on `record_id` but not on `coordinate`.

### 3.3 Coordinate

```python
@dataclass(frozen=True, slots=True)
class Coordinate:
    # Discrete structural axes (the 6-D ontology)
    substrate: SubstrateValue
    geometry: GeometryValue
    dynamics: DynamicsValue
    plasticity: PlasticityValue
    credit: CreditValue
    update: UpdateValue

    # Continuous / categorical knobs, keyed by axis id from the axes registry.
    # This is the Appendix C union (37 params) + geometry params + substrate params.
    params: FrozenDict[str, AxisValue]

    # Evaluation parameters that are part of identity (per Q1 resolution)
    # seed/epochs/batch live in Schedule, NOT here.

    def coordinate_key(self) -> str: ...   # stable hash of structural + params
```

**Key design decision:** `params` is a **registry-driven map**, not a fixed field set. The set of legal keys and their domains come from the `axes` registry (§2), filtered by each `AxisSpec.availability` predicate (§5). This means adding a new hyperparameter = registering one `AxisSpec`; no schema change, no code change. This is how the 37 Appendix-C parameters (and the next 37) are absorbed without hardcoding.

### 3.4 The single store (R13)

One logical store, physically a SQLite database in WAL mode (R12 crash-safety), with three coordinated components:

| Component | Content | Satisfies |
|---|---|---|
| `records` table | The `Record` rows (sections 1–4 + payload), schema-versioned | R7–R9, R13 |
| `vector_index` | Embeddings over record text/metrics for semantic retrieval | C59, R15, K5 |
| `artifacts` | Content-addressed blobs (configs, figures, reproducers, kernels) | CEEC parity, R60 |

**All four current stores collapse here.** `kb.sqlite` becomes the base; `campaign.db`, `ledger.sqlite`, and Optuna's DBs are *readers/importers* into it, never writers of private state (R13). Optuna studies are bridgeable via a `PolicyAdapter` (§7) that writes records, not a parallel store.

**Write path:** every write is a single transaction; `record_id` uniqueness prevents duplicates under concurrency (R74, K8). A `kill -9` mid-write leaves the WAL intact and the store queryable (R12).

### 3.5 Schema versioning (R79)

- Every `Record` carries `schema_version`.
- A `SchemaReader` registry maps `version → reader`. Readers are append-only; old versions are never removed.
- Unknown fields deserialize as `UnknownField(name, raw)` — **never silently defaulted** (R79).
- This replaces destructive migrations with additive readers, so historical artifacts remain loadable for the life of the system (K4).

---

## 4. Abstraction C — The Constraint Engine

### 4.1 Problem solved
Task-compatibility fences, void pre-classification, defect classification, fairness constraints, and operating-point constraints are today four different mechanisms (P14, R37, R25, R66). This abstraction makes them **one**: *predicates over coordinates with recorded reasons.*

### 4.2 Core type

```python
@dataclass(frozen=True, slots=True)
class Constraint:
    id: str
    predicate: Predicate              # (Coordinate, Context) -> bool
    reason: str                       # human-readable, stored on rejection
    scope: ConstraintScope            # global | per_run | per_policy
    suppressive: bool                 # True = globally suppressive (R38)
    source: ConstraintSource          # ontology | discovered | operator

class ConstraintEngine:
    def check(self, coord: Coordinate, ctx: Context) -> Verdict: ...
    def preclassify(self, space: Space) -> VoidMap: ...   # S4 preview (C11, C32)
    def record_violation(self, coord, verdict) -> Record: ...
```

`Predicate` is a **serializable, inspectable object** (not an opaque lambda), so reasons are queryable and the engine is testable:

```python
Predicate = (
    AxisInRange(...)          # numeric / categorical domain check
  | AxisPairCompatible(...)   # e.g. TASK_COMPAT fences (C8)
  | BudgetFairness(...)       # param/FLOPs/walltime matching (R25)
  | OperatingPoint(...)       # max latency / min accuracy (R66)
  | And(...) | Or(...) | Not(...)
)
```

### 4.3 Behavioral guarantees
- **Enforced at S4** (Gate), **re-checkable at S6** (Train) — a coordinate that becomes infeasible mid-run is caught (R42).
- **Globally suppressive:** a `suppressive=True` constraint (e.g. a discovered void) means *no policy* may re-propose that coordinate (R38). This is distinct from per-run scoping (§14.3 guardrail).
- **Dry-run is a preview** of the same engine (C32), not a separate code path.
- **Discovered infeasibility propagates identically** to coverage, reports, and reference docs (R42) because all read the same `ConstraintEngine` state.
- Absorbs `SearchSpace.apply_constraints` (the "fourth constraint mechanism" from §13.2) and resolves Q2: void pre-classification is a **space-level declaration** evaluated by the engine; runtime-discovered infeasibility is a **record** that the engine learns from.

### 4.4 The compatibility matrix is generated (R63)
The ontology compatibility matrix is **derived** by running the `ConstraintEngine` over the axis cross-product and serializing the result. It can never drift from `validate()` because it *is* `validate()` evaluated exhaustively.

---

## 5. The Unified Coordinate Space (Resolving Appendix B + C)

### 5.1 The completeness fix
TODO43 §13.2 identifies that the 37 continuous hyperparameters (Appendix C) live only in `hyperopt/` and are absent from R1's axis list. This specification resolves it: **every parameter in Appendix B and Appendix C is an `AxisSpec` in the `axes` registry (§2).** The union is:

- **B.1–B.6** structural axes (dynamics, geometry, credit, update, substrate, plasticity, tasks, objectives) — categorical.
- **Appendix C** per-rule continuous parameters (37) — continuous, with `availability` scoped to their rule.
- **Geometry parameters** (B.2 common + per-topology keys) — continuous/integer.
- **Substrate parameters** (noise_level, precision) — continuous/categorical.
- **§13.2 additions:** batch size (schedule axis), per-update optimizer parameters (adam betas, muon momentum).

### 5.2 Conditional availability (the elegant part)
The problem: `beta` only makes sense when `credit == thermodynamic_contrast`; `tau_mem` only when `dynamics == spike_integration`. Hardcoding this is the P4 trap.

**Solution:** each `AxisSpec` carries an `availability: Predicate | None`. The coordinate space is the set of axes whose availability predicate is satisfied by the current structural axes:

```python
AxisSpec(
    id="credit.beta",
    kind=CONTINUOUS, domain=LogRange(1e-3, 1e2),
    availability=AxisEquals("credit", "thermodynamic_contrast"),
)
AxisSpec(
    id="dynamics.tau_mem",
    kind=CONTINUOUS, domain=LinearRange(1e-3, 1.0),
    availability=AxisEquals("dynamics", "spike_integration"),
)
```

The **active space** for a coordinate is computed, not enumerated. This means:
- Adding a new rule + its hyperparameters = registering N `AxisSpec`s with availability predicates. Zero changes to the search, store, or schema.
- A mixed continuous/discrete space is one object (R4) because all axes are `AxisSpec`s regardless of `kind`.
- "Describable here, inexpressible there" (P1) is structurally impossible: there is one space, and every implementation reads it from the registry.

### 5.3 Learning rate and step size are just axes
R2 (lr as searched coordinate) and R6 (overridable defaults) fall out: `learning_rate` and `update_step_size` are `AxisSpec`s with `override_scope=both`. The ruler table (C19) and step-size overrides (C18) become **`PriorSpec` rows** (§9), not code.

---

## 6. Abstraction D — The Stage Pipeline & Policy Protocols

### 6.1 Problem solved
Policies, stages, evaluators, and backends are today entangled, so swapping one changes everything (P1). This abstraction makes them **small protocols** wrapped by a pipeline that emits the obligations.

### 6.2 The 11-stage pipeline
Every run executes stages S1–S11 (§3.0). Each stage is a **protocol**; a no-op stage emits an explicit empty fragment (R39):

```python
@runtime_checkable
class Stage(Protocol):
    stage_id: str                                    # "S1".."S11"
    def run(self, ctx: RunContext) -> StageFragment: ...
```

A `StageFragment` is a record-typed payload (hypothesis, space, schedule, gate verdict, metrics, attribution, decision, report section). All fragments append to the run's record set. **Stage behavior is substitutable without changing the record schema** (R40) because fragments are schema-versioned data.

### 6.3 Policy protocol (S2/S3)
```python
@runtime_checkable
class SearchPolicy(Protocol):
    def propose(self, space: ActiveSpace, history: RecordView,
                budget: Budget) -> Iterator[Coordinate]: ...
```

Shipped policies (the R17 preservation catalog): `StratifiedRandom`, `RoundRobinGrid`, `UniformRandom`, `ModelBased` (TPE/NSGA-II bridge). Each is a `PluginSpec` in the registry.

### 6.4 The wrapper emits the obligations (P4)
The pipeline wraps every policy/stage and **itself** produces:
- **Coverage/stratification statistics** for every run, regardless of policy (R18).
- **Void/defect classification** of every rejected coordinate (R19).
- **Proposal traceability** — each proposal records the policy + state that produced it (R20).
- **Stage fragments** even for no-op stages (R39).

A policy cannot forget coverage because it never implements coverage — the wrapper does. This is the mechanism by which "coverage guarantees are not lost when a model-based policy is used" (R18).

### 6.5 Evaluator & backend protocols (R72)
```python
class Evaluator(Protocol):
    def evaluate(self, coord: Coordinate, schedule: Schedule) -> Record: ...

class ExecutionBackend(Protocol):       # local | multiprocess | cluster
    def submit(self, jobs: list[EvalJob]) -> list[Record]: ...
```
Backends are substitutable with identical record shape (R72). Concurrency is a `schedule` parameter; the store's transactional writes keep records consistent under parallel evaluation (R74, K8).

### 6.6 Run specification (R41)
A run is fully described by one **versioned, serializable, diffable** object:

```python
@dataclass(frozen=True, slots=True)
class RunSpec:
    spec_version: int
    space: SpaceRef                    # reference to axis-registry snapshot
    policy: PluginRef
    schedule: ScheduleSpec
    evaluator: PluginRef
    governance: GovernanceSpec
    budget: BudgetSpec
    seed: int
    provenance: Provenance
```
`RunSpec` is the unit of reproducibility (R41), portability (R45, R73), and diffing. It references registry *snapshots*, so re-running against a different store/code version is well-defined.

---

## 7. Multi-Fidelity Compute Allocation (R46–R51)

### 7.1 Problem solved
Compute is allocated by a fixed L0→L1→L2 ladder (P12), wasting budget on cells that show no gain (the 1357s / 1457-clamp run). This design replaces the ladder with an **evidence-driven fidelity scheduler**.

### 7.2 The scheduler
A `FidelityScheduler` maintains a population of coordinates, each at a current fidelity, and iterates:

```
loop while budget.remaining:
    1. Score each candidate by  expected_improvement_per_cost(coord, history)
    2. Detect divergence/stagnation from telemetry (R50) → abandon
    3. Promote top-scoring to next fidelity; abandon bottom
    4. Record every promote/abandon decision with rationale (R47, R51)
```

- **Non-uniform by construction** (R46): cost concentrates on promising coordinates.
- **Evidence-driven** (R47): the scoring function reads interim metrics + uncertainty + cost from records, not a fixed tier.
- **Waste recorded & detectable** (R48): every abandon writes a `waste` record; a report aggregates "repeatedly measured-to-no-gain" coordinates.
- **Appendable** (R49): promoting a coordinate across sessions adds a new record at higher fidelity, same coordinate identity.

### 7.3 Divergence detection (R50)
Telemetry signals (clamp rate, NaN, loss explosion, spectral radius, no-improvement streak) are evaluated **during** training. When a signal crosses threshold, the scheduler emits a `DivergenceSignal` and abandons within a bounded fraction of the budget. The 1357s run is flagged long before it completes.

### 7.4 Guard-kill attribution (R51)
Every early-stop records `{signal, value, threshold, cost_saved}`. Guard-kills are attributable, not mysterious.

### 7.5 Cost model (R23, R24)
`expected_improvement_per_cost` uses a **learned cost model** fitted from per-stage walltime breakdowns in records. Estimates carry stated uncertainty and improve as records accumulate (R24). Dry-run reports a cost estimate before running (R23).

---

## 8. Abstraction E — Governance as Stored Predicates

### 8.1 Problem solved
Governance is split across two code paths and is a property of the path, not the record (P6). CEEC is a separate ledger (Q9). This abstraction makes governance **record fields** and claims **queries**.

### 8.2 Statuses are fields
The `Status` section of every record carries:
```python
@dataclass(frozen=True, slots=True)
class Status:
    gate_verdict: GateVerdict          # passed | failed | pending
    defect: DefectRef | None
    cause: FailureCause | None         # machine-readable (R58)
    severity: Severity | None
    quarantine: bool
    claim_eligible: bool               # derived, not asserted
    ceec_link: CeecRef | None          # provenance link to CEEC ledger
```

### 8.3 Claims are queries (R35)
A claim is **never asserted by the run that produced it.** It is a predicate over records:

```
claim_eligible(record) :=
       record.status.gate_verdict == passed
   and record.status.defect is None
   and record.status.quarantine is False
   and record.schedule.n_seeds >= MIN_SEEDS          # R64
   and record.metrics.uncertainty is not None        # R64
   and matched_control_exists(record)                # R65
```

CAMPAIGN_PLAN §7 becomes **one filter** over records (R35). This is the concrete meaning of "governance fails closed" (K6): a record that cannot satisfy the predicate is not a result.

### 8.4 CEEC integration (resolves Q9)
The CEEC ledger remains the **authoritative append-only provenance chain** (`Experiment → Artifact → Evidence → Belief → Decision`). Records carry a `ceec_link` referencing the ledger entry. So:
- The **status** lives on the record (queryable, always-on, cheap — K9).
- The **provenance chain** lives in CEEC (immutable, audited).
- Neither is collapsed into the other; they are linked by content hash.

This resolves Q9: ledger status is a **record field with a provenance link**, not a side artifact.

### 8.5 Alerts are queries (R83)
Breakthrough/cascade/completion alerts are predicates over record streams. They **notify only**; the run/stop decision stays with the human (R83). Operator intent is recorded (R84).

---

## 9. Learning from History (R52–R57)

### 9.1 Priors are records, not code (R52)
The ruler lr table (C19) and step-size overrides (C18) become **`PriorSpec` rows**:
```python
@dataclass(frozen=True, slots=True)
class PriorSpec:
    id: str
    coordinate_pattern: CoordinatePattern     # e.g. (task=mnist, topology=feedforward)
    axis: str                                  # "learning_rate"
    value: float
    uncertainty: float | None                  # R55
    provenance: PriorProvenance               # where it came from
    supersedable: bool = True                  # search may exceed it
```
A search **starts from** priors and can exceed them (R52). Priors are applied with stated confidence and are overridable (R55). This resolves Q4 (ruler is an input prior, not an authority) and Q12 (migrate override-table entries to `PriorSpec`s).

### 9.2 Warm-starting & transfer (R53)
A new run's space and policy are seeded from prior records (including cross-task / cross-topology), with the transfer's provenance recorded in the `RunSpec`.

### 9.3 Surrogates drive proposals (R54)
`SurrogateManager` over records drives proposal generation (expected improvement / expected hypervolume improvement). A run logs surrogate-guided proposals and must beat random on a held-out task. This resolves Q10 toward "surrogates enter the search loop."

### 9.4 The I(C,U) meta-model
The I(C,U) learnability model (0.944 held-out accuracy) is a **surrogate prior**: it warm-starts the credit×update region of the space. This closes P9 — store analytics are consumed by search.

### 9.5 Reasoning as records (R57)
Hypothesis chains (reasoner), LLM proposals, and retrieved literature become **records with provenance**, linked to the experiments they motivated. The loop learns from its own reasoning history. This resolves Q15 toward "active linkage, provenance-first."

---

## 10. Failure Intelligence (R58–R63)

### 10.1 Machine-readable causes (R58)
Every failed/abandoned evaluation carries:
```python
class FailureCause(Enum):
    INFEASIBLE_BY_CONSTRUCTION = ...
    GATE_REJECTED = ...
    GUARD_KILLED = ...
    DEFECT = ...
    TIMEOUT = ...
    NON_FINITE = ...
    USER_STOPPED = ...
    UNCLASSIFIED = ...            # monitored signal (R59)
```
Cause + severity are **fields**, not log text (R58).

### 10.2 The unclassified bucket is monitored (R59)
`UNCLASSIFIED` has a count and an owner; it is a first-class signal, not a dumping ground.

### 10.3 Reproducers, clustering, fix-linkage (R60–R62)
- From a defect record, emit a **minimal reproducer** and (for implementation faults) a candidate regression test (R60).
- Cluster failure patterns across runs so systemic causes are found once (R61).
- Link a fix to the failures it resolves; post-fix verification is a query "which defects does this change close?" (R62).

### 10.4 Negative results are globally suppressive (R38)
Voids, defects, and regressions are first-class, queryable, and prevent re-proposal by any policy.

---

## 11. Metaprogramming & Extensibility Layer

This section is the answer to "reduce hardcoding/boilerplate, enable future evolution." Every technique below is in service of Principle P1 (declare once, derive everything).

### 11.1 Declarative specs → generated artifacts
The `@registry_type` decorator + codegen pipeline produces, from one spec declaration:
- Registry entry + validator
- CLI flag (wired into `comp`)
- Doc page (via `generate_docs.py`)
- Serialization schema (for the store)
- Hypothesis test strategies (for R77 conformance)
- Identity-card entry (for algorithm/primitive specs)

**No parallel files.** Appendix A (flags), Appendix B (axes), and Appendix C (hyperparameters) become *generated views*, so they cannot drift (P11, R63, R80).

### 11.2 Structural subtyping over inheritance
All plugin boundaries (`SearchPolicy`, `Stage`, `Evaluator`, `ExecutionBackend`) are `Protocol`s (K2 "Protocol over ABC"). Third-party samplers satisfy the policy contract without importing the framework (R71). New stages/policies/evaluators are added through extension points without modifying the core (R70).

### 11.3 PEP 695 generics for composition
The existing `System[TS, TG, TD, TM, TC, TU]` generic composition is retained and extended: invalid axis combinations are caught at **type-check time**, and the coordinate schema is the runtime mirror of the static types.

### 11.4 `functools.singledispatch` for extensible operations
Operations that vary by axis kind (sampling, validation, serialization, normalization) are `singledispatch`ed on `AxisKind`. Adding a new axis kind = registering one handler, no switch statements.

### 11.5 Serializable predicates over lambdas
Constraints (§4) and availability predicates (§5) are **data** (serializable, inspectable, diffable), not closures. This makes them storable, queryable, and testable, and allows the constraint engine to be persisted and replayed.

### 11.6 Versioned readers over migrations
Schema evolution uses additive `SchemaReader`s (R79), never destructive migrations. The system can read any historical artifact for its lifetime (K4).

### 11.7 Content-addressed artifacts
Configs, reproducers, kernels, and figures are stored content-addressed (like CEEC). This gives free deduplication, provenance, and cache invalidation. It is the mechanism by which **kernel caching is scoped to run/record identity** (R75) and never lives in a global singleton (K10): the kernel cache is keyed by `(run_id, record_id, device, dtype)` and stored as artifacts.

### 11.8 Run-scoped state, no global singletons (K10)
All run-scoped state (kernel cache, budget counters, policy state) lives in a `RunContext` object threaded through the pipeline. Module-level singletons are banned; a conformance test asserts no mutable global state is touched during a run (P16 guardrail).

---

## 12. Resolution of Open Questions (Q1–Q16)

| Q | Resolution | Mechanism |
|---|---|---|
| **Q1** | Seeds/fidelity are properties of the **measurement**, not the coordinate. "Same cell" = coordinate key; "same measurement" = full identity. | §3.2 four-section identity |
| **Q2** | Void pre-classification is a **space-level declaration** evaluated by the constraint engine; runtime infeasibility is a learned record. | §4.4 |
| **Q3** | Default lr search is **model-based seeded from the ruler prior**, with a log-grid fallback for cold-start. | §9.1, FidelityScheduler |
| **Q4** | The ruler table is an **input prior**, not an authority; search may exceed it. | §9.1 |
| **Q5** | The conformance suite **gates merges**; waiver requires an explicit registry `retired` entry + rationale. | §2.4 |
| **Q6** | Parallel evaluation is **in scope** for the unified release; the store's transactional writes are designed for it. | §3.4, §6.5 |
| **Q7** | `plasticity` is a **first-class coordinate axis** (it is in the 6-D ontology and carries its own axes/objectives). | §3.3, §5 |
| **Q8** | Reporting collapses to **one library with thin front-ends**; one command answers a question across subsystems. | R14, §8 |
| **Q9** | CEEC ledger status is a **record field with a provenance link**, not a side artifact. | §8.4 |
| **Q10** | Surrogate/causal capabilities **enter the search loop** (surrogate-guided proposals). | §9.3 |
| **Q11** | Robustness (R69) is **opt-in per study**; matched-cost comparison (R65) is **mandatory for every claim**. | §8.3 |
| **Q12** | Migrate all ~30 override-table entries to `PriorSpec`s; none remain as code. | §9.1 |
| **Q13** | Kernel-cache scoping is **per (run, record, device, dtype)**. | §11.7 |
| **Q14** | Alert routing: webhook targets + severity routing + content-hash dedup, defined in `GovernanceSpec`. | §8.5 |
| **Q15** | Literature/LLM integration is **active hypothesis generation inside the loop**, with provenance-first records. | §9.5 |
| **Q16** | Fenced tasks are **excludable per run via space constraints**; the fence reason is user-visible in proposals. | §4, R37 |

---

## 13. Requirement Traceability Matrix

Every requirement R1–R88 maps to a design element. Grouped by abstraction:

| Abstraction | Requirements satisfied |
|---|---|
| **A. Registry** | R5, R31, R33, R70, R76, R77, R78, R80; R1 (axes), R37, R66 (constraints), R52/R55 (priors) |
| **B. Record & Store** | R7, R8, R9, R11, R12, R13, R67, R79; R22 (derived guard); K4, K5 |
| **C. Constraint Engine** | R19, R25, R37, R38, R42, R66; resolves Q2 |
| **D. Pipeline & Policies** | R16, R17, R18, R19, R20, R39, R40, R41, R44, R45, R70, R71, R72, R73, R74 |
| **E. Governance** | R10, R34, R35, R36, R58, R59, R64, R65, R83, R84; K6, K9 |
| **Unified Space (§5)** | R1, R2, R3, R4, R6; App B+C |
| **Fidelity Scheduler (§7)** | R46, R47, R48, R49, R50, R51; R23, R24 |
| **Learning (§9)** | R52, R53, R54, R55, R56, R57; R15 |
| **Failure Intelligence (§10)** | R58, R59, R60, R61, R62, R63 |
| **Reporting/Surface** | R14, R20, R63, R85, R86, R87, R88 |
| **Determinism/Resume** | R26, R27, R28, R29, R30 |
| **Claim strength** | R64, R65, R66, R67, R68, R69 |
| **Human control** | R81, R82, R83, R84 |
| **Budget** | R21, R22, R23, R24, R25 |

Every problem P1–P17 is addressed; every capability C1–C88 is preserved (R76–R78 enforce mechanically).

---

## 14. Acceptance (restated from TODO43 §8, now satisfiable)

The design is realized when a system exists in which:

1. One coordinate schema expresses the Appendix B+C union; a single run yields records at >1 lr, substrate, and fidelity. *(§3, §5)*
2. Records differing only in lr/seed/fidelity are distinguishable and never averaged unlabeled. *(§3.2)*
3. A record written by any policy is queryable, reportable, and claim-evaluable by the same code from the same store. *(§3.4, §8)*
4. Round-robin, stratified, random, and model-based policies traverse the same space, produce comparable records, and report coverage. *(§6)*
5. Compute allocation is non-uniform, evidence-driven, and its waste is recorded and detectable. *(§7)*
6. Failure causes are machine-readable, clustered, and convertible to reproducers; known-bad coordinates are never re-paid. *(§10, §4)*
7. Kill/resume produces no duplicate or reordered coverage under every policy, including parallel. *(§3.4, §6.5)*
8. Every claim carries n, variance, and a matched-cost reference; CAMPAIGN_PLAN §7 is one filter excluding quarantined/gate-failed cells. *(§8.3)*
9. Every capability has a registry entry and a passing conformance test; no registered capability is lost. *(§2)*
10. A run is fully described by a versioned, diffable, portable spec; stages are uniformly present, pluggable, and recorded. *(§6.6)*
11. Hypotheses, reasoning chains, and prior art are records linked to the experiments they motivated. *(§9.5)*
12. Kernel caching and all acceleration are scoped to run identity with provenance. *(§11.7)*

---

## 15. Migration & Compatibility

- **Stores:** `campaign.db`, `ledger.sqlite`, and Optuna DBs become read-only importers into the single store (§3.4). No new writes outside it.
- **Override tables:** `_STEP_SIZE_OVERRIDES`, `_DYNAMICS_STEP_SIZE_OVERRIDES`, `_ruler_lr`, `TASK_COMPAT` migrate to `PriorSpec` and `ConstraintSpec` rows (§9.1, §4). The code tables are retired via explicit registry entries (R78).
- **CLI:** flags become generated views over registries (§11.1). Existing verbs keep working until their capability is explicitly retired.
- **Records on disk:** readable for the life of the system via versioned readers (R79, K4).
- **Governance:** fails closed throughout (K6); a record that cannot be validated is not a result.

---

## Appendix — Why this is elegant

The design reduces 88 requirements to **five abstractions** and **five principles** without dropping a single verification clause. The leverage comes from:

- **One registry** instead of seven mechanisms (A).
- **One record schema** instead of four stores (B).
- **One constraint engine** instead of four legality mechanisms (C).
- **Obligations on the wrapper** so plugins can't forget them (D).
- **Claims as queries** so governance can't be bypassed (E).

And the metaprogramming layer (§11) ensures that **adding** a hyperparameter, objective, constraint, prior, policy, or stage is a *declarative registration*, not a code change — which is precisely what makes the system robust to the ontology's own future evolution.
