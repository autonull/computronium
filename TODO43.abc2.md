# SPEC-43 — The Computronium Experiment Kernel

**Unified Search & Evidence System — Design Specification**

**Rev 1.1** · 2026-09-30 · Status: **DESIGN — ready for union-fix review**
Supersedes Rev 1.0. All changes itemized in Appendix IV.

Implements: TODO43 Rev 3 (all MUST requirements R1–R88; SHOULD unless waived), Constraints K1–K10, Rev 3 addendum (§13–§15, Appendix C) *as gated scope* (§15), and the §14 abstractions A–E.

---

## 0. Preamble

### 0.1 What this document is

TODO43 is requirements only. This is the design those requirements deferred. It makes every §12 decision, resolves Q1–Q16, and specifies an implementation that is:

- **Effective** — kills P1–P17 structurally, not disciplinarily.
- **Robust** — crash-safe, failure-isolated, fails closed.
- **Rigorous** — every claim a query over governed records.
- **Elegant** — registries built by reflection, schemas synthesized, nothing hand-maintained that can drift.
- **Evolvable** — new axes, policies, constraints, and objectives are declarations, never edits.

**Rev 1.1 scope.** This revision fixes four self-inconsistencies inherited from the source designs (dual tunable representation; stored-vs-derived `claim_eligible`; coordinate field-name drift; `record_id` instability under versioned readers), withdraws the blanket "by construction" acceptance claim in favor of a three-class requirement classification (§12), states the Rev 3 dependency as an explicit review gate (§15), and adds the implementable artifacts the design deferred (exception hierarchy, store DDL, predicate wire format — Appendices I–III).

### 0.2 Non-goals (inherited from TODO43 §1.3)

No reimplementation of Optuna internals; no change to ontology primitives or substrate physics; no algorithm preference; no re-measurement for its own sake; no CLI-verb backwards compatibility (records, capability registry, and flag inventory are the compatibility surfaces); the system makes validity checkable, never renders verdicts.

### 0.3 Acceptance *(rev 1.1 — overclaim withdrawn)*

The acceptance conditions of TODO43 §8 hold, **each by the means appropriate to its class** (§12):

- **Structural requirements** hold *by construction* and are verified by locks and property tests.
- **Empirical requirements** hold *by mechanism, confirmed by measurement* — the architecture provides the apparatus; a named benchmark provides the verdict (R46, R54, R23/R24, R50, R86). Architecture does not produce benchmark outcomes.
- **Process requirements** hold *by gated practice* — enforced at CI and review gates (R77, R78, R80, R56).

The twelve acceptance bullets of TODO43 §8 remain the acceptance surface; §12 states, for every requirement, which class it belongs to and what discharges it.

### 0.4 Terminology

| Term | Meaning |
|------|---------|
| Coordinate | The full set of structural-axis + tunable choices defining *which system* |
| Record | One durable, queryable measurement: coordinate ∪ schedule ∪ provenance ∪ status ∪ payload |
| Policy | How search chooses coordinates, allocates compute, or stops |
| Stage | A lifecycle phase S1–S11 |
| Fragment | The typed output of one stage execution |
| Prior | Recorded data that biases a search before it runs |
| Claim | A predicate over records, never an assertion by a run |
| Void / Defect | Declared infeasibility (space property) / discovered infeasibility (evaluation property) |
| Cell key / Measurement key / Record id | The three identity keys (§4.5) |

---

## 1. Design Doctrine

Eight principles govern every decision below. They are the elegance contract.

| # | Principle | Consequence |
|---|-----------|-------------|
| 1 | **Registries are built, not written** (A) | Every axis, objective, capability, constraint, prior, and flag is a spec registered by reflection. Hand-maintained tables (P4) are structurally impossible. |
| 2 | **One record schema, four identity sections** (B) | `identity = coordinate ∪ schedule ∪ provenance ∪ status`. Resolves Q1. |
| 3 | **Legality is a predicate engine, not a dictionary** (C) | Constraints are data (predicate + reason + scope), enforced at S4, re-checked at S6, queryable, globally suppressive. The compatibility matrix is generated (R63). |
| 4 | **Obligations live on the pipeline, not the plugins** (D) | Policies/stages/evaluators/backends implement small Protocols; the wrapper emits coverage, classification, traceability, and fragments for any plugin. |
| 5 | **Governance is stored predicates — and derived verdicts are never cached** (E) | Statuses/causes/verdicts are record fields; claims, promotions, alerts, and reports are pure queries. Any *derived* verdict (claim eligibility, promotion readiness) is recomputed from primary fields on every query. Caching a derived verdict is the P6 anti-pattern this design exists to kill. |
| 6 | **Fail closed** (K6) | A record that cannot be validated is not a result; a claim that cannot be derived is not expressible. |
| 7 | **Run-scoped state, injected, never global** (K10) | Kernels, caches, and device context ride a `SystemContext`, never module singletons. |
| 8 | **Everything derives from the registries** | Docs, identity cards, the compatibility matrix, CLI help, conformance suite are codegen over registries. Drift is a build failure, not a habit. |

---

## 2. Architecture Overview

### 2.1 Module map (one package, six pillars)

```
computronium/experiment/                  # "the Kernel"
 ├─ schema/          PILLAR 1 — one axis type, coordinate, record identity, registries
 │   ├─ registry.py       the one Registry (Abstraction A)
 │   ├─ axis.py           AxisSpec: structural axes AND tunables, one type (rev 1.1)
 │   ├─ harvest.py        tunable reflection + schema synthesis (Appendix C → union)
 │   ├─ coordinate.py     Coordinate + CoordinateSchema
 │   ├─ record.py         Record: four identity sections, three identity keys (rev 1.1)
 │   └─ versioning.py     schema/spec versions + old-shape readers (R79, K4)
 ├─ execution/       PILLAR 2 — stages, policies, budget, determinism, allocation
 │   ├─ stage.py          Stage Protocol, StageContext, Fragment
 │   ├─ pipeline.py       the runner — obligations live here (Abstraction D)
 │   ├─ policy.py         Policy Protocol + shipped catalog (R17 preservation proof)
 │   ├─ budget.py         Budget + learned CostModel (R21–R24)
 │   ├─ allocator.py      multi-fidelity evidence-driven allocation (R46–R51)
 │   ├─ replay.py         replay hash, resume ledger, checkpoint/restore (R26–R30)
 │   └─ backends.py       ExecutionBackend Protocol (local/multiprocess/cluster)
 ├─ legality/        PILLAR 3 — constraint engine, voids, defects
 │   ├─ dsl.py            serializable predicate AST + evaluator + wire format (App. III)
 │   ├─ engine.py         ConstraintEngine + compatibility-matrix generation (R63)
 │   └─ classify.py       void vs defect classification (R19, R38, R42)
 ├─ evidence/        PILLAR 4 — governance predicates, failure intelligence, claims
 │   ├─ store.py          the one RecordStore (R13, K5; DDL in App. II)
 │   ├─ status.py         primary status fields only — no derived verdicts (rev 1.1)
 │   ├─ claims.py         claim/promotion/alert queries (R35, R64, R83)
 │   ├─ failure.py        cause taxonomy, clustering, reproducers (R58–R62)
 │   └─ ceec.py           CEEC ledger linkage (Q9)
 ├─ learning/        PILLAR 5 — priors, surrogates, I(C,U), reasoning records
 │   ├─ prior.py          prior store (ruler/step-size tables as data, R52)
 │   ├─ surrogate.py      surrogate-driven proposals (R54, Q10)
 │   ├─ icu.py            I(C,U) metamodel warm-start (R53, R55)
 │   └─ reasoning.py      hypothesis/literature records (R57)
 └─ surface/         PILLAR 6 — reports, CLI, conformance, operations
     ├─ report.py         the one report (R14, R85)
     ├─ cli.py            thin front-ends over one library (Q8)
     ├─ conformance.py    capability registry + conformance harness (R76–R78)
     └─ operations.py     daemon, steering, record-predicate alerts (R81–R84)
```

Errors raised across pillars form one hierarchy (Appendix I).

### 2.2 Pillar ↔ requirement coverage (per TODO43 §7.2)

| Pillar | Satisfies (group-level) |
|--------|------------------------|
| 1 Schema | R1, R4–R9, R11, R67, R79; coordinate/identity half of R22 |
| 2 Execution | R8, R16–R18, R21–R30, R39–R41, R44–R51, R72, R74–R75 |
| 3 Legality | R10, R19, R25, R29, R37, R38, R42, R66 |
| 4 Evidence | R10, R34–R36, R50, R51, R58–R65, R83, R84 |
| 5 Learning | R2, R6, R9, R15, R52–R57 |
| 6 Surface | R3, R5, R12–R14, R20, R31–R33, R63, R70–R71, R73, R76–R82, R85–R88 |

R43 (question-first entry) is carried by the `Synthesis` policy (§6.3); R73 (export/import round-trip) by the run spec + content-addressed artifacts (§4.7). Every capability C1–C88 is carried by exactly one pillar and registered in the capability registry (R76), so coverage is mechanically enforced.

### 2.3 The five abstractions, placed

| Abstraction | Realized in | Resolves |
|-------------|-------------|----------|
| A — Universal Registry | `schema/registry.py` (+ one instance per kind) | R5, R31, R33, R70, R76–R78, R80 |
| B — Identity Schema | `schema/record.py`, `schema/coordinate.py`, `schema/axis.py` | Q1; R7–R9, R11, R67, R79 |
| C — Legality Engine | `legality/*` | Q2; R19, R25, R37, R38, R66 |
| D — Pipeline Obligations | `execution/pipeline.py` | R16–R18, R39–R40, R70–R72 |
| E — Governance as Predicates | `evidence/status.py`, `evidence/claims.py` | Q9; R10, R34–R36, R58–R59, R64, R83 |

### 2.4 System diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    A. UNIVERSAL REGISTRY SYSTEM                          │
│  (axes incl. tunables, objectives, capabilities, constraints, priors,  │
│   policies, stages, flags)                                              │
│  One generic Registry[SpecT] + declarative specs + reflection harvest   │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ resolves names → specs at runtime
          ┌──────────────────────┼──────────────────────────────────────┐
          ▼                      ▼                                      ▼
┌──────────────────┐  ┌───────────────────────┐  ┌────────────────────────┐
│ B. RECORD SCHEMA │  │ C. LEGALITY ENGINE    │  │ D. EXECUTION PIPELINE  │
│ & SINGLE STORE   │◄─│ (predicate DSL,       │◄─│ (11 stages × plugins,  │
│ (4-section id)   │  │  void/defect class.)  │  │  wrapper obligations)  │
└────────┬─────────┘  └───────────────────────┘  └───────────┬────────────┘
         │ primary statuses = fields                          │ emits records
         ▼                                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│         E. GOVERNANCE AS STORED PREDICATES (derived, never cached)      │
│  claims, promotion, alerts, reports = pure queries over B               │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Abstraction A — The Universal Registry

### 3.1 The generic registry

Every noun in the system is a frozen spec in a typed registry. One implementation, many instances.

```python
# experiment/schema/registry.py
from typing import Protocol, runtime_checkable

@runtime_checkable
class RegistrySpec(Protocol):
    @property
    def id(self) -> str: ...
    @property
    def schema_version(self) -> int: ...
    @property
    def owner(self) -> str: ...
    @property
    def status(self) -> SpecStatus: ...  # ACTIVE | DEPRECATED | RETIRED

class Registry[SpecT: RegistrySpec]:
    """Integrity-locked, codegen-ready, reflectable registry (Abstraction A)."""

    def register(self, spec: SpecT) -> None:
        if self._locked: raise RegistryLocked(self._name)
        if spec.id in self._specs: raise DuplicateSpec(self._name, spec.id)
        self._specs[spec.id] = spec

    def get(self, id: str) -> SpecT: ...
    def all(self) -> tuple[SpecT, ...]: ...
    def where(self, **tag_filters) -> tuple[SpecT, ...]: ...
    def diff(self, other: "Registry[SpecT]") -> RegistryDiff: ...
    def schema(self) -> dict: ...          # self-describing (R5 discovery, codegen)
    def lock(self) -> None: ...
    def verify_integrity(self) -> None: ...
```

Registries lock after import; adding or removing a spec is an explicit, recorded migration (R78's "explicit retirement record"). One harness conformance-tests every registry instance (R77).

### 3.2 Auto-registration via reflection

Primitives self-register via `__init_subclass__` — no hand-listed tables exist to drift:

```python
# experiment/schema/axis.py
AXES: Registry[AxisSpec] = Registry("axis")

class AxisPrimitive:
    def __init_subclass__(cls, *, axis: Axis, primitive_id: str, **_) -> None:
        super().__init_subclass__()
        AXES.register(AxisSpec.structural(
            id=f"{axis.value}.{primitive_id}", axis=axis,
            primitive_id=primitive_id, config_schema=cls.config_schema(),
        ))
        harvest_tunables(cls)      # §4.2 — registers cls.__tunables__ into AXES

class EnergyMinimization(AxisPrimitive, axis=Axis.DYNAMICS,
                         primitive_id="energy_minimization"): ...
```

Enumerating legal values per axis (R5) is `AXES.all()` filtered by axis — discoverable at runtime, matching Appendix B by construction.

### 3.3 The registry instances *(rev 1.1 — tunables unified into AXES)*

| Registry | Spec type | Seed content | Requirement |
|----------|-----------|--------------|-------------|
| `AXES` | `AxisSpec` | Appendix B structural axes **and** all tunables (Appendix C's 37, lr, step size, batch size, optimizer params) — one type, one registry | R1, R2, R4, R5, R6 |
| `OBJECTIVES` | `ObjectiveSpec` | B.7 (~39, direction/weight/normalizer/axis tag) | R31, R33 |
| `CAPABILITIES` | `CapabilitySpec` | C1–C88 + §13.3/§13.4 rows (stage, owner, verifying test) | R76, R77 |
| `CONSTRAINTS` | `Constraint` | `SystemConfig.validate()` rules + task fences + `apply_constraints` | R37, R63, R66 |
| `PRIORS` | `PriorSpec` | Ruler-LR table, step-size overrides — as data | R52, R55 |
| `POLICIES` / `STAGES` | `PolicySpec` / `StageSpec` | R17 policy union; S1–S11 | R17, R39 |

Rev 1.0's separate `TUNABLES` registry is abolished: a tunable *is* an `AxisSpec` (§4.1). This is what makes R4 ("mixed space, one representation") literally true.

**Flag inventory as a view (R78):** Appendix A's flags are a projection of `CAPABILITIES` (`capability → flags → tests`); a lock asserts the projection is current.

### 3.4 Integrity locks (executable, in CI)

For each registry, a property test asserts: uniqueness of id; totality (every concrete primitive has exactly one spec); no orphans (every spec resolves to a live class); lock (post-lock mutation requires a migration record). This is `test_registry_completeness_lock` generalized to all instances (R76, R78).

### 3.5 Codegen from registries

Generated, then lock-tested against source (drift fails CI):

- `docs/generated/` — capability & objective listings (R80).
- The ontology compatibility matrix from `CONSTRAINTS` (R63).
- JSON-Schema validators per `AxisSpec` (R5 runtime discovery).
- Conformance test stubs per `CapabilitySpec` (R77).
- CLI flag definitions wired into the dispatcher (R78).
- Identity-card entries for algorithm/primitive specs.

---

## 4. Abstraction B — Coordinate & Record Identity Schema

### 4.1 One axis type *(rev 1.1 — the tunable/AxisSpec unification)*

Structural axes and hyperparameters are one type. A tunable is an `AxisSpec` whose `kind` is continuous/integer/categorical rather than structural:

```python
# experiment/schema/axis.py
class AxisKind(Enum): STRUCTURAL; CONTINUOUS; INTEGER; CATEGORICAL

@dataclass(frozen=True, slots=True)
class AxisSpec:
    meta: SpecMeta
    kind: AxisKind
    domain: Domain                       # enumerated members | Range(lo, hi, scale)
    availability: Predicate | None       # when this axis is active for a coordinate
    default: Scalar | None = None
    prior: str | None = None             # PriorSpec id (data, overridable) — R52
    override_scope: OverrideScope = OverrideScope.BOTH   # per_run | per_coordinate | both
    topology_params: tuple[str, ...] = ()                # structural geometries only

    @classmethod
    def structural(cls, ...) -> "AxisSpec": ...
    @classmethod
    def tunable(cls, name, kind, domain, *, availability=None, default=None,
                prior=None) -> "AxisSpec": ...
```

**Conditional availability.** `beta` only makes sense when `credit == thermodynamic_contrast`; `tau_mem` only when `dynamics == spike_integration`. Hardcoding this is the P4 trap, so availability is a predicate and the active space is *computed*, never enumerated:

```python
AxisSpec.tunable("beta", CONTINUOUS, Range(1e-3, 1e2, LOG),
                 availability=AxisEquals("credit", "thermodynamic_contrast"))
AxisSpec.tunable("tau_mem", CONTINUOUS, Range(1e-3, 1.0),
                 availability=AxisEquals("dynamics", "spike_integration"))
```

Adding a new rule + its hyperparameters = registering N `AxisSpec`s with availability predicates. Zero changes to search, store, schema, or docs. "Describable here, inexpressible there" (P1) is structurally impossible.

### 4.2 Tunable reflection and deduplication — the Appendix-C cure

Primitives declare their tunables inline; the harvester registers them into `AXES`:

```python
class ThermodynamicContrast(CreditPrimitive, axis=Axis.CREDIT,
                            primitive_id="thermodynamic_contrast"):
    __tunables__ = (
        AxisSpec.tunable("beta", CONTINUOUS, Range(1e-3, 1e2, LOG), default=0.5),
        AxisSpec.tunable("max_steps", INTEGER, Range(1, 200), default=20),
        # … all eqprop slots from Appendix C …
    )
```

**Deduplication rule (70 slots → 37 unique).** Appendix C enumerates 70 per-rule slots collapsing to 37 unique names (`learning_rate` appears under 10 rules). The harvester deduplicates **by parameter name** into a single `AxisSpec` whose availability is the *disjunction* of the declaring primitives' selection predicates:

- `learning_rate` → one AxisSpec, available wherever any trainable primitive is selected (this is exactly R2: lr is a searched coordinate, one axis, not ten).
- `beta` → one AxisSpec, available under `credit ∈ {thermodynamic_contrast, pc_alm}`.

Conflicting declarations of the same name (different domain/scale/default) are a **conformance-lock failure**: ownership is joint, definition is singular. A lock asserts `harvest_schema() ⊇ Appendix B ∪ Appendix C` — the union is counted and locked, exactly as R1/R5 demand.

**What this kills.** `RULE_SPACES`, `_STEP_SIZE_OVERRIDES`, `_DYNAMICS_STEP_SIZE_OVERRIDES`, and `_ruler_lr` all become *projections* of `AXES ∪ PRIORS`. R6 (override + record effective value): overrides flow through the descriptor; the effective value is written to the record. R3 (substrate comparable): `noise_level`/`precision` are tunables on the substrate axis, so two substrates appear in one comparable set.

### 4.3 Schema synthesis

```python
def harvest_schema() -> CoordinateSchema:
    """Reflect structural axes + all tunables into one schema. Never hand-written.
    Continuous and discrete share this representation (R4)."""
    return CoordinateSchema(axes=AXES.all(), schema_version=SCHEMA_VERSION)
```

Serialization, validation, and diffing (R41) are derived from the schema by reflecting over `axes` — no hand-written serializers, so a versioned, diffable run spec comes for free.

### 4.4 Coordinate *(rev 1.1 — naming unified)*

```python
@dataclass(frozen=True, slots=True)
class Coordinate:
    # Discrete structural axes (the 6-D ontology; plasticity first-class, Q7)
    substrate: AxisValue
    geometry: AxisValue
    dynamics: AxisValue
    plasticity: AxisValue
    credit: AxisValue
    update: AxisValue
    # Continuous/categorical knobs, keyed by AxisSpec id from AXES.
    # This is the Appendix C union + geometry params + substrate params.
    # `params` is the ONE name for this field, everywhere.
    params: FrozenDict[str, Scalar]

    def active_axes(self) -> frozenset[AxisSpec]:
        """AXES filtered by availability predicates satisfied by this coordinate."""

    @property
    def cell_key(self) -> CellKey: ...   # canonical hash of the coordinate alone
```

`CoordinateSchema.validate(coord)` is generated from the axis descriptors (single source). Every numeric default is overridable per-run and per-coordinate; the effective value is recorded (R6).

**Plasticity is a first-class axis** (Q7). The README's P-axis program (ψ, frozen-θ, NTM/NCA, adaptation/migration) mandates it; `plasticity` carries its own tunables and objectives (`psi_capacity`, `consolidation_cost`, `rewrite_rate`).

### 4.5 Four identity sections, three identity keys *(rev 1.1)*

A **coordinate** defines *which system*; a **record identity** defines *which measurement of it*. Seeds, fidelity, epochs, and batch limits are the schedule, not the coordinate.

> **Q1 answered:** "same cell" = equal `coordinate`; "same measurement" = equal full `identity`.

```python
@dataclass(frozen=True, slots=True)
class Record:
    schema_version: int
    coordinate: Coordinate          # ─┐
    schedule: Schedule              #  ├ identity sections (Abstraction B)
    provenance: Provenance          #  │
    status: Status                  # ─┘ primary governance fields only (§7.2)
    payload: Payload                # metrics, telemetry, objectives, artifact refs
    unknown: UnknownFields          # R79: preserved, labelled, never defaulted

    # ── The three identity keys ─────────────────────────────────────────
    @property
    def cell_key(self) -> CellKey: ...
    @property
    def measurement_key(self) -> MeasurementKey: ...
    @property
    def record_id(self) -> ContentHash: ...
```

| Key | Definition | Purpose |
|-----|-----------|---------|
| `cell_key` | sha256(coordinate) | "Same cell" — groups repeats of one system (R9 index shape) |
| `measurement_key` | sha256(coordinate ∪ schedule) | "Same measurement spec" — resume/dedup authority (R26, K8); store UNIQUE constraint |
| `record_id` | sha256(**canonical serialization as written**, `schema_version`-bound) | Content hash for integrity and content-addressed artifact linkage |

**Hash-stability rule (fixes the Rev 1.0 trap).** `record_id` is computed once, at write time, over the canonical bytes of that schema version, and stored. Versioned readers (§4.6) provide normalized *query views* of old records but never re-hash; identity is therefore stable across schema evolution. Dedup of writes keys on `measurement_key`; integrity and artifact linkage key on `record_id`.

### 4.6 Section contents and the requirements they discharge

| Section | Fields | Discharges |
|---------|--------|------------|
| `coordinate` | six axis values + `params` | R1, R2, R3, R7 |
| `schedule` | fidelity tier (L0/L1/L2), seed, epochs, batch limit, budget_id | R8, R9, R22, R47 |
| `provenance` | env (device/dtype/workers/lib versions), dataset+split+version, code SHA, policy id + proposal state, reasoning/CEEC links | R11, R20, R57, R67 |
| `status` | primary governance fields (§7.2) | R10, R34, R64 |
| `payload` | objectives (resolved to one registry), settle telemetry, probes, artifact refs | R31, R50 |

R8/R22/R67 become **derived comparison guards**: any front/average/comparison must stratify by `schedule.fidelity`, label the mixture, or refuse. R9 (repeats as distinct records sharing a coordinate key) is the store's index shape: unique on `measurement_key`, indexed on `cell_key`.

### 4.7 Schema versioning (R79, K4)

`Record` carries `schema_version`. A `SchemaReader` registry maps `version → reader`; readers are append-only, old versions never removed. Unknown fields deserialize as `UnknownField(name, raw)` — never silently defaulted. Adding an axis or knob is a registration + migration, not a core edit: the coordinate schema is versioned so the abstraction itself may be re-cut without corrupting history.

### 4.8 The run spec (R41, R45, R43, R44, R73)

```python
@dataclass(frozen=True, slots=True)
class RunSpec:
    spec_version: int
    space: SpaceRef                    # reference to axis-registry snapshot
    policy: PluginRef
    schedule: ScheduleSpec             # includes per-task adaptation (R44)
    evaluator: PluginRef
    governance: GovernanceSpec
    budget: BudgetSpec
    seed: int
    provenance: Provenance
```

- A run is fully described by one versioned, serializable, diffable spec; space/evaluator are declarable independently of the store, so a spec re-runs against another store/code version and diffs (R45 portability).
- **R43** — the question-first entry (`objective + target operating point → space/policy/budget`) is the `Synthesis` policy producing this spec.
- **R44** — heterogeneous task families are a schedule property: per-task space/policy adaptation inside one spec.
- **R73** — export/import is `RunSpec + records + content-addressed artifacts` in one self-describing bundle; round-trip is a conformance test.

---

## 5. Abstraction C — The Legality Engine

### 5.1 Serializable predicate DSL

Constraints and claims must be stored, diffed, hashed, and queried — so they are AST expressions, not lambdas. Concrete JSON wire format in Appendix III.

```python
# experiment/legality/dsl.py
type Expr =
  | Field(path: str)                     # "credit" | "params.beta" | "schedule.fidelity"
  | Lit(value: Scalar)
  | Cmp(op: CmpOp, lhs: Expr, rhs: Expr)
  | In(field: Expr, values: tuple[Scalar, ...])
  | Between(field: Expr, lo: Scalar, hi: Scalar)
  | And(tuple[Expr, ...]) | Or(tuple[Expr, ...]) | Not(Expr)

# Serializable; evaluable against a Coordinate; content-hashed for identity.
```

### 5.2 Constraint model; declared vs discovered (resolves Q2)

```python
class ConstraintOrigin(Enum): DECLARED; DISCOVERED
class ConstraintScope(Enum): GLOBAL; RUN

@dataclass(frozen=True, slots=True)
class Constraint:
    meta: SpecMeta
    kind: ConstraintKind      # STRUCTURAL_VOID | TASK_FENCE | FAIRNESS | OPERATING_POINT | RUNTIME_DEFECT
    predicate: Expr
    reason: str               # recorded, queryable (R37)
    origin: ConstraintOrigin
    scope: ConstraintScope
    enforced_at: tuple[StageId, ...]  # (S4, S6)
```

**Q2 answered:** a void is `DECLARED` (infeasible by construction; rejected at S4 before compute is paid; remembered by resume). A defect is `DISCOVERED` (infeasible at runtime; recorded at S6 and fed back as a `GLOBAL` suppression). Same engine; one `origin` field decides when cost is paid and what resume remembers.

### 5.3 Registration by decorator

```python
@constraint("fence.sequence_on_feedforward",
            reason="sequence tasks require recurrent/external-memory geometry",
            scope=ConstraintScope.GLOBAL)
def _(c: Coordinate) -> bool:
    return not (is_sequence_task(c) and c.geometry.topology == "feedforward")
```

R37 — task-compatibility fencing is a first-class constraint with a recorded, queryable reason. R25 — fairness is enforceable as a search constraint. R66 — operating-point constraints are constraints. The §13.2 `apply_constraints` (`max_hidden`/`max_layers`/`max_steps`) becomes a constraint here.

### 5.4 Behavioral guarantees

- Enforced at S4 (Gate), re-checkable at S6 (Train) — mid-run infeasibility is caught (R42).
- **Globally suppressive:** a `scope=GLOBAL` constraint means no policy may re-propose that coordinate (R38) — distinct from per-run scoping (§19 guardrail).
- **Dry-run** is a preview of the same engine (C32), not a separate code path.
- **R42 falls out by construction:** coverage, reports, and reference docs all read `CONSTRAINTS`, so a void found at S4 and one found at S6 appear identically downstream.
- **Fenced tasks** are excludable per run via `RUN` constraints; the fence reason is visible in proposals (Q16).

### 5.5 Void/defect classification (R19, C11/C12)

`classify.py` holds the taxonomy as registry data. The wrapper applies classification to **every** policy's proposals — a model-based run's rejections are classified identically to a driver's (R19). The "unclassified" bucket is a counted, owned signal (R59).

### 5.6 The compatibility matrix is generated (R63)

```python
def compatibility_matrix(grid: Iterable[Coordinate]) -> CompatibilityMatrix:
    return CompatibilityMatrix(
        rows=grid,
        verdicts={(c, k): engine.check(c, k) for c in grid for k in CONSTRAINTS.all()},
    )
```

The reference matrix is produced by evaluating `CONSTRAINTS` over the grid; it matches `validate()` behavior by test and cannot drift (P13/P11). Codegen-over-registry doctrine applied to docs.

---

## 6. Abstraction D — The Execution Pipeline

### 6.1 Stage Protocol (S1–S11, R39/R40)

```python
@dataclass(frozen=True, slots=True)
class Fragment:
    stage: StageId
    payload: Mapping[str, Scalar | Nested]   # typed, serializable; {} for a no-op

@runtime_checkable
class Stage(Protocol):
    stage_id: ClassVar[StageId]
    def run(self, ctx: StageContext) -> Fragment: ...
```

Every stage runs for every policy; a stage with nothing to say emits an explicit empty fragment (R39). Stages are swappable Protocols that never change the record schema (R40).

### 6.2 The pipeline wrapper — where obligations live

```python
class Pipeline:
    def run(self, spec: RunSpec) -> RunResult:
        ctx = StageContext(spec, store=self._store, budget=self._budget,
                           constraints=self._engine, context=self._sysctx)  # K10
        for stage in STAGE_ORDER:                       # S1..S11
            impl = self._stages[stage]
            try:
                frag = impl.run(ctx)
            except EvaluationFailure as exc:            # R29: isolate, never corrupt
                frag = self._isolate(stage, ctx, exc)
            self._coverage.observe(frag)               # R18: coverage for EVERY policy
            self._classify(frag)                       # R19: void/defect classification
            self._store.append(frag, atomic=True)      # R12: crash-safe write
            ctx.record(frag)
        return ctx.result()
```

**The wrapper, not the plugin, guarantees:**

| Obligation | Emitted by wrapper | Requirement |
|------------|-------------------|-------------|
| Axis-coverage statistics per run, regardless of policy | coverage fragment | R18 |
| Void/defect classification of every proposal/rejection | legality fragment | R19 |
| Proposal provenance (policy + evidence) | traceability fragment | R20 |
| Stage fragments for all S1–S11 (incl. no-ops) | stage assembly | R39 |
| Crash-safe, atomic store write | WAL transaction | R12 |
| Environment provenance capture | provenance section | R11, R28 |
| Budget consumption accounting | budget fragment | R21 |

Coverage guarantees can never be silently lost by a clever policy, because they are not the policy's job.

### 6.3 Policy Protocol + the preserved catalog (R16/R17)

```python
@runtime_checkable
class Policy(Protocol):
    def propose(self, ctx: SearchContext) -> Iterator[Proposal]: ...
    def observe(self, record: Record) -> None: ...     # model-based policies learn
```

The wrapper intercepts every proposal and applies, uniformly and in order: constraint screening (Pillar 3), novelty suppression keyed on `measurement_key` (no re-measurement, C10), and proposal-provenance stamping (R20).

**R17 is the shipped catalog — the preservation proof:**

| Policy | Preserved from | Character |
|--------|---------------|-----------|
| `StratifiedRandom` | `broad_map.StratifiedRandomDriver` (C9) | stratified, objective-binned |
| `RoundRobinGrid` | `stack.grid_sampler` (C13) | deterministic ablation |
| `UniformRandom` | `stack._space_sampler` (C14) | baseline |
| `ModelBased` (TPE/NSGA-II + pruners) | `hyperopt/_finder.py` (C20) | continuous/mixed |
| `Evolution` (population/generations) | `computronium-lab` (§13.1)* | budgeted evolution |
| `Synthesis` (spec→coordinate, constraint-screened) | `computronium-lab` (§13.1)* | question-first (R43) |
| `StrategyProgression` | `execution/` (§13.1)* | candidate progression |
| `TrainerDriven` (NAS/HPO) | `lightning_/` (§13.1)* | trainer-loop search |

\* Rev 3 candidates — gated on review (§15).

R71 (third-party policies without forking): `ModelBased` wraps Optuna behind the same `Policy` Protocol via a storage adapter that reads/writes the unified store (not a private Optuna DB — closing P7).

### 6.4 Budget & learned cost model (R21–R24)

```python
@dataclass(frozen=True, slots=True)
class Budget:
    soft: Duration
    hard: Duration
    target_cells: int | None
    # One concept governs every search; soft/hard stop defined once (P5 unified).

class CostModel(Protocol):
    def estimate(self, coord: Coordinate, schedule: Schedule) -> CostEstimate: ...
```

One `Budget` interface exposes `consumed()/remaining()` for every policy (R21). `CostModel` is learned from recorded per-stage walltime breakdowns (R24); dry-run reports an estimate with stated uncertainty (R23). *Estimate quality is empirical-class (§12): measured, not assumed.* Walltime/throughput comparisons are guarded: valid only between records of comparable fidelity+budget, else refused or labeled (R22).

### 6.5 Multi-fidelity evidence-driven allocation (R46–R51)

Allocation is a separate Protocol from proposal, so any policy pairs with any allocator:

```python
class AllocationPolicy(Protocol):
    def allocate(self, population: tuple[Coordinate, ...], evidence: RecordStore,
                 budget: Budget) -> AllocationPlan: ...
    # Returns: promote | abandon | defer per member, with rationale.
```

**Reference implementation — evidence-driven successive promotion (replaces the fixed ladder, P12):**

```
loop while budget.remaining:
    1. Score each candidate by expected_improvement_per_cost(coord, history)
    2. Detect divergence/stagnation from telemetry (R50) → abandon
    3. Promote top-scoring to next fidelity; abandon bottom
    4. Record every promote/abandon decision with rationale (R47, R51)
```

- **R46** — non-uniform allocation. *Acceptance is empirical-class (§12): measured cost-to-rank must beat the uniform baseline. The architecture provides the scheduler and the recording; the benchmark provides the verdict.*
- **R47** — every promotion/abandonment references interim evidence in the record.
- **R48** — compute spent before abandonment is recorded; a waste report flags repeatedly-measured-to-no-gain coordinates (the 1357 s / 1457-clamp case becomes a line item).
- **R49** — compute is appendable across sessions; an appended measurement is a new record of the same `cell_key`.
- **R50/R51** — divergence/stagnation signals (clamp storm, NaN, loss explosion, spectral radius, no-improvement) are first-class telemetry; a guard-kill record names the signal, its value, and the compute saved. *R50's "bounded fraction of cost" is empirical-class: the detector is structural, the bound is measured.*

### 6.6 Determinism, resume, replay (R26–R30)

- **R26** — same inputs + seed ⇒ same coordinates; resume skips recorded work, keyed on `measurement_key` (no duplicate, no reordered coverage).
- **R27** — determinism is asserted, not assumed: each run records and re-checks a **replay hash** of `(spec, seed, policy-state sequence)`.
- **R28** — environment nondeterminism (dataloader worker policy, daemon concurrency, device) is an explicit run property with recorded fallback (P15 becomes attributable).
- **R29** — a failing evaluation is isolated; siblings, run, and store stay intact; the failure becomes a record with cause.
- **R30** — checkpoint/restore at run and evaluation granularity preserves remaining budget and evidence.

### 6.7 Concurrency (R74, K8)

Parallelism is a schedule parameter. Store writes are serialized (WAL + optimistic concurrency); the wrapper dedupes by `measurement_key`. A parallel run produces the same records as a serial one — no duplicates, no reordering. Write order is authoritative via a monotonic sequence number (Appendix II), independent of backend.

### 6.8 Evaluator & backend protocols (R72)

```python
class Evaluator(Protocol):
    def evaluate(self, coord: Coordinate, schedule: Schedule) -> Record: ...

class ExecutionBackend(Protocol):       # local | multiprocess | cluster
    def submit(self, jobs: list[EvalJob]) -> list[Record]: ...
```

Backends are substitutable with identical record shape (R72).

### 6.9 Acceleration and run-scoped state (R75, K10, resolves Q13)

Compiled-kernel cache is keyed by `(run_id, coordinate.cell_key, device, dtype)` — run-scoped, provenance-carrying, safely invalidating, inspectable as records, stored content-addressed. No module-level singleton (K10; P16 is the cautionary example). The kernel-ladder evidence trail (parity + microbench JSONL, git-SHA tagged — §13.3) is itself a record type in the store.

---

## 7. Abstraction E — Evidence & Governance

### 7.1 The Record Store (R13, K5) *(rev 1.1 — DDL and concurrency honesty)*

One append-only store, an **evolution of the KB** (preserving vector/surrogate/causal — K5, R15). Full DDL sketch in Appendix II.

| Component | Content | Satisfies |
|-----------|---------|-----------|
| `records` table | Record rows (sections 1–4 + payload), schema-versioned; UNIQUE on `measurement_key` | R7–R9, R13, R26 |
| `vector_index` | Embeddings for semantic retrieval | C59, R15, K5 |
| `artifacts` | Content-addressed blobs (configs, figures, reproducers, kernels) | R60, R73, R75 |

**Store consolidation:**

| Today | Fate |
|-------|------|
| `kb.sqlite` | becomes the unified store (evolved) |
| `campaign.db` | migrated in |
| `ledger.sqlite` | migrated in / becomes the CEEC reference |
| Optuna `*.db` | replaced by a storage adapter over the unified store (R71) |

- **R12** — WAL-mode, atomic, crash-safe writes; `kill -9` mid-write leaves the store queryable and consistent.
- **R13** — no implementation owns a private store; any record is queryable by all.
- **R14** — reporting/analysis derivable from the store alone, one implementation per report.
- A `Store` Protocol keeps the backend substitutable without touching callers (R45).

**Write-path honesty (K7/K8).** SQLite WAL supports concurrent readers and one writer. Record writes serialize on that single writer; this is acceptable because write cost is small relative to evaluation cost — *measured by the K7 benchmark harness, not assumed*. If write throughput ever becomes the bottleneck, the `Store` Protocol swaps in DuckDB/Postgres. The K8 invariants (no duplicates, no reordered records) are enforced by `measurement_key` uniqueness + monotonic sequence numbers regardless of backend.

### 7.2 Governance as stored predicates — primary fields only *(rev 1.1)*

Statuses, causes, and verdicts are record fields written by their producing stage. **Only primary fields are stored; derived verdicts are never cached:**

```python
@dataclass(frozen=True, slots=True)
class Status:
    gate_verdict: GateVerdict          # PASS | FAIL | PENDING
    defect: DefectRef | None
    cause: FailureCause | None         # machine-readable (R58)
    severity: Severity | None
    quarantine: bool
    maturity: Tier                     # L0 | L1 | L2
    uncertainty: Uncertainty | None    # seeds + variance (R64)
    reproducibility: ReproRef | None
    ceec_link: CeecRef | None          # content-addressed ledger entry
```

Rev 1.0's stored `claim_eligible: bool` is **removed**. A stored derived verdict must be refreshed whenever any input changes — which is exactly the side-effect discipline that produces governance drift (P6). Claim eligibility is computed, every time, as a pure function over the fields above (Doctrine principle 5).

**CEEC integration (Q9 resolved):** the CEEC ledger remains the authoritative append-only chain (`Experiment → Artifact → Evidence → Belief → Decision`). Records carry `ceec_link` referencing the ledger entry by content hash. The status lives on the record (queryable, always-on, cheap — K9); the provenance chain lives in CEEC (immutable, audited). Neither is collapsed into the other.

### 7.3 Claims, promotion, alerts are pure queries *(rev 1.1)*

```python
# experiment/evidence/claims.py
def claim_eligible(record: Record) -> bool:
    """CAMPAIGN_PLAN §7 as one predicate (R35). Pure, derived, fails closed (K6).
    Never stored, never asserted by the producing run."""
    return (record.status.gate_verdict == GateVerdict.PASS
            and record.status.defect is None
            and not record.status.quarantine
            and record.status.maturity >= Tier.L2
            and record.schedule.n_seeds >= MIN_SEEDS          # R64
            and record.status.uncertainty is not None         # R64
            and matched_control_exists(record)                # R65
            and ceec_linked_and_gated(record))

def claim_eligible_records(store: Store, *, task: Task) -> Iterator[Record]:
    return (r for r in store.query(task=task) if claim_eligible(r))
```

- **R10** — a record cannot be presented as a result while carrying an open defect or failed gate, computable from the record alone.
- **R35** — a claim is derived from a record predicate, never asserted by the producing run.
- **R36** — promotion is "select by predicate, re-evaluate at higher fidelity," applicable to any policy's output.
- **R64** — no claim is expressible without n and variance (enforced by the predicate shape).
- **R65** — matched comparison at matched params/FLOPs/walltime; unmatched pairs are refused.
- **R83/Q14** — alerts are predicates over record streams (breakthrough ≥2%, cascade >30% failures, completion); they notify only — run/stop stays human. Routing: predicate-signature → severity → webhook, with dedup by signature.

### 7.4 Dataset/data integrity (R67/R68/R69)

Dataset/split identity + version are provenance fields; cross-version comparisons are refused or labeled (R67). Leakage checks (R68) and robustness dimensions (R69: noise/quantization/shift) are expressible in the run spec and recorded.

---

## 8. Learning & Intelligence

### 8.1 Priors as data (R52, resolves Q3/Q4/Q12)

The ruler-LR table and the ~30 step-size overrides become `PriorSpec` records, attached to their axis via `AxisSpec.prior`:

```python
@dataclass(frozen=True, slots=True)
class PriorSpec:
    meta: SpecMeta
    coordinate_pattern: CoordinatePattern     # e.g. (task=mnist, topology=feedforward)
    axis: str                                  # "learning_rate"
    value: float
    uncertainty: float | None                  # R55
    provenance: PriorProvenance               # where it came from, code version
    supersedable: bool = True                  # search may exceed it
```

- **Q4:** the ruler is an *input prior*, not an authoritative default.
- **Q12:** convert to priors, retire the code, record migration (R78).
- **Q3:** default lr search is model-based, seeded from the ruler prior (sample-efficient), with log-grid available as a policy.
- **R52:** a search starts from priors and can *exceed* them. **R55:** priors apply with stated confidence, only within that uncertainty, and are overridable.

### 8.2 Surrogates in the loop (R54, resolves Q10)

`SurrogatePolicy` wraps any `Policy` and steers it with models over records (EI / EHVI). Q10: surrogates enter the search loop, not just analysis.

- **R53** — new runs warm-start space and policy from prior records (including cross-task/cross-topology transfer), with transfer provenance in the spec.
- **R54** — surrogate models over records drive proposals. *Acceptance is empirical-class (§12): a run logs surrogate-guided proposals and beats random on a held-out task — a benchmark verdict, not an architectural guarantee.*
- **R55** — learned quantities transfer as priors with uncertainty.

### 8.3 The I(C,U) closed loop

The I(C,U) learnability-interaction model (0.944 held-out accuracy, `fit_icu_model.py`, `icu_measurements.csv`) is registered as a surrogate/prior source feeding `ModelBased` and `Synthesis` policies. This is the framework's distinctive closed loop: **experiments train metamodels that guide future experiments** (P9 closed).

### 8.4 Reasoning records (R57, resolves Q15)

Reasoner chains, LLM proposals, and retrieved literature become records with provenance, linked to the experiments they motivated (P17 closed). Q15: provenance linkage is mandatory; active in-loop hypothesis generation is an opt-in S1 policy that writes the same record type.

### 8.5 Lessons (R56)

Knowledge gained is queryable as lessons (what was learned, which change mattered), tied to code versions. *Process-class (§12): enforced by the report requiring a lessons section derivable from records.*

---

## 9. Failure Intelligence (R58–R62)

### 9.1 Machine-readable causes (R58)

```python
class FailureCause(Enum):
    INFEASIBLE_BY_CONSTRUCTION
    GATE_REJECTED
    GUARD_KILLED
    DEFECT
    TIMEOUT
    NON_FINITE
    USER_STOPPED
    UNCLASSIFIED            # monitored signal (R59)

@dataclass(frozen=True, slots=True)
class FailureEvent:
    cause: FailureCause
    severity: Severity
    signal: str | None       # which detector fired
    value: Scalar | None     # at what value
    measurement_key: MeasurementKey
```

Causes/severities are **fields, not log text** (R58).

### 9.2 The unclassified bucket is monitored (R59)

`UNCLASSIFIED` has a count and an owner; it is a first-class signal, not a dumping ground.

### 9.3 Reproducers, clustering, fix-linkage (R60–R62)

- From a defect record, emit a minimal reproducer and (for implementation faults) a candidate regression test (R60).
- Cluster failure patterns across runs so systemic causes are found once (R61).
- Link a fix to the failures it resolves; post-fix verification is a query: "which defects does this change close?" (R62).

### 9.4 Negative results are globally suppressive (R38)

Voids, defects, and regressions are first-class, queryable, and prevent re-proposal by any policy.

---

## 10. Surface

### 10.1 One report (R85–R88, resolves Q8)

One command, derived from the store alone, covering: objectives & fronts (by fidelity), axis coverage, budget consumed, failures by cause, promotion history, claim-eligible records, and axis attribution (R86) as a section. Figures/manifests are pinned (R87); narrative handoff summaries derive from records (R88). Q8: one library, thin front-ends — reporting logic lives in `surface/report.py`; CLI/dashboard are projections.

### 10.2 CLI collapse (R78/R80)

The many entry points collapse into one dispatcher with scope arguments. Root/task/scope conventions are implemented once. Documented-command conformance tests fail when a documented invocation drifts (P11). Run profiles (`quick-verify`, `production-map`, `maturation`, `claim`) are data, each conformance-tested (R80).

### 10.3 Capability preservation & conformance (R76–R78, resolves Q5)

```python
CAPABILITIES: Registry[CapabilitySpec] = Registry("capability")

def capability(id: str, *, stage: StageId, test: str):
    def deco(cls):
        CAPABILITIES.register(CapabilitySpec(id=id, stage=stage, test=test))
        return cls
    return deco
```

- **R76** — the capability inventory (C1–C88 + §13 rows) is a machine-readable registry: id, stage, description, owner, verifying test.
- **R77** — a conformance suite asserts every registered capability works; CI fails if a capability loses its test. Q5: gates merges, with an explicit recorded waiver path.
- **R78** — every one-off flag, per-combination table, and subsystem report path maps to a registered capability or an explicit retirement record.

### 10.4 Objectives as one registry (R31–R33)

One objective registry (~39, with direction/weight/normalizer/axis tag); every stored metric resolves to it; multi-objective selections (fronts, portfolios, operating points) are computed from records so any policy's results are comparable (R32); new objectives add through an extension point without modifying core (R33). Because telemetry emitters register their objectives, the registry is reflection-built, not hand-listed.

### 10.5 Human control & live operation (R81–R84)

A run is pausable/steerable/resumable mid-flight (R81). Long-running discovery runs as a service that re-plans as evidence accumulates (R82). Alerts notify only (R83). Operator intent is first-class data (R84).

---

## 11. Metaprogramming & Reflection Strategy

Every technique maps to a concrete requirement and eliminates a specific class of boilerplate.

| # | Technique | Mechanism | Eliminates / Enables | Serves |
|---|-----------|-----------|---------------------|--------|
| 1 | Auto-registration via `__init_subclass__` | Primitives register at class-definition time | Hand-maintained axis tables (P4) | R5, R1 |
| 2 | Tunable reflection + dedup | `__tunables__` harvested into `AXES`, deduped by name (70→37) | `RULE_SPACES`, prior code tables (P2, P4, App C) | R1, R2, R4, R6, R52 |
| 3 | Schema synthesis from registries | `harvest_schema()` walks `AXES` | Hand-written coordinate schemas | R1, R4 |
| 4 | Serialization/diff from schema | `to/from/diff` generated from field specs | Boilerplate serializers | R41 |
| 5 | Serializable predicate DSL | Constraints/claims are AST expressions, not lambdas | Hardcoded fence dicts, unqueryable gates | R37, R38, R41, R66 |
| 6 | Constraints as data + matrix generation | `@constraint` decorator; matrix by evaluation | Hardcoded `TASK_COMPAT`/void dicts | R63 |
| 7 | `runtime_checkable` Protocols | Plugins checked with `isinstance` at registration | Inheritance hierarchies | K2, R16, R40, R70 |
| 8 | Entry-point extension discovery | `importlib.metadata.entry_points(group="computronium.policies")` | Forking to extend | R33, R70, R71 |
| 9 | Codegen for docs/cards/listings | Appendix B, identity cards, compatibility matrix from registries | Documentation drift (P11) | R63, R80 |
| 10 | Capability conformance by reflection | Harness walks `CAPABILITIES`, runs each `test` | Manual preservation checks | R76–R78 |
| 11 | Property-test generation from invariants | Hypothesis tests generated from spec invariants | Hand-written invariant tests | K9, R77 |
| 12 | `functools.singledispatch` on `AxisKind` | Operations varying by axis kind dispatched, not switched | Switch statements | R33, R70 |
| 13 | Content-addressed artifacts | Configs, reproducers, kernels stored by hash | Dedup, provenance, cache invalidation | R75, K10 |
| 14 | Versioned reader adapters | Per-version readers materialize old shapes; hashes stable (§4.5) | Destructive migrations | R79, K4 |

**The invariant this buys:** the only hand-written artifacts are *definitions* (a primitive, a tunable declaration, a constraint, a capability). Everything derived — the union, the schema, the matrix, the docs, the conformance — is regenerated from those definitions. **Drift becomes a build failure.** This is the structural answer to P4, P11, P14, and R63 simultaneously.

**Evolution posture:** new axes/knobs = registration; new policies/stages/objectives = Protocol implementation + optional entry point; schema changes = version bump + reader. Nothing requires editing the core (R70).

---

## 12. Requirement Classification *(rev 1.1 — new)*

Rev 1.0 claimed acceptance "by construction" for all requirements. That was an overclaim: some requirements are benchmark outcomes, not architectural properties. Every requirement belongs to exactly one class; its class states what discharges it.

**Class S — Structural.** Satisfied by construction; verified by locks, property tests, and conformance tests. The architecture makes them true.

> R1, R4, R5, R7–R13, R16–R22, R25–R42, R44, R45, R52, R57–R59, R63–R67, R70–R79, R81–R85, plus K1–K10 as design invariants.

**Class E — Empirical.** Satisfied by mechanism, *confirmed by measurement*. The architecture provides the apparatus; a named benchmark provides the verdict. Nobody should expect these from code review alone.

| Requirement | Mechanism (this spec) | Verdict comes from |
|-------------|----------------------|--------------------|
| R46 (cost-to-rank beats uniform) | `AllocationPolicy` + rationale records (§6.5) | Cost-to-rank benchmark vs uniform baseline |
| R54 (surrogate beats random) | `SurrogatePolicy` (§8.2) | Held-out-task benchmark |
| R23/R24 (cost estimates improve) | `CostModel` (§6.4) | Estimate-vs-actual error over time |
| R50 (divergence within bounded cost) | `DivergenceDetector` telemetry (§6.5) | Replay of the 1357 s run; bound measured |
| R86 (attribution reproduces known effect) | Attribution over stored records | Seeded axis-effect reproduction |
| K7 (overhead budgeted) | Wrapper design | Per-evaluation overhead harness |

**Class P — Process.** Satisfied by gated practice enforced at CI/review gates.

> R77 (conformance gates merges), R78 (inventory audits, retirement records), R80 (documented-command tests, profiles as data), R56 (lessons section derivable in every report), R68/R69 (checks available and reported where a study opts in).

**Consequence for acceptance (§0.3):** TODO43 §8 holds when Class S locks pass, Class E benchmarks pass, and Class P gates are enforced. A Class E requirement failing its benchmark is a *finding to act on*, not a design defect — provided the mechanism and its recording are intact.

---

## 13. Open Questions — Disposition

| Q | Disposition | Basis |
|---|-------------|-------|
| Q1 seeds/fidelity in coordinate? | **Resolved** — coordinate = system def; seeds/fidelity in `schedule`. "Same cell" = `cell_key`; "same measurement" = full identity | §4.5 |
| Q2 void: space or evaluation? | **Resolved** — declared infeasibility = constraint (space); discovered = defect (evaluation); one classifier, identical propagation | §5.2 |
| Q3 default lr search | Model-based, seeded from ruler prior; log-grid available as policy | §8.1 |
| Q4 ruler table role | Input prior, not authoritative default | §8.1 |
| Q5 conformance gating | Gates merges with recorded waiver path | §10.3 |
| Q6 parallel in first release | In-scope; store concurrency designed up front | §6.7, §7.1 |
| Q7 plasticity axis | First-class coordinate axis (README's ψ/frozen-θ/NTM/NCA emphasis mandates it) | §4.4 |
| Q8 reporting collapse | One library, thin front-ends | §10.1 |
| Q9 CEEC ledger | Primary status is record fields with content-addressed provenance link; chain stays in ledger | §7.2 |
| Q10 surrogates in loop | Enter the search loop (EI/EHVI); I(C,U) as prior/surrogate | §8.2 |
| Q11 robustness/matched-cost | Matched-cost mandatory for claims; robustness opt-in per study | §7.3, §7.4 |
| Q12 override-table migration | Convert to priors; retire the code with explicit records | §8.1 |
| Q13 kernel-cache scoping | Per `(run, coordinate.cell_key, device, dtype)` | §6.9 |
| Q14 alert routing | Record-predicate alerts; webhook w/ severity routing + dedup; human decides run/stop | §7.3 |
| Q15 literature/LLM depth | Provenance-linked records mandatory; active in-loop generation opt-in S1 policy | §8.4 |
| Q16 fenced tasks | Excludable per run via `RUN` constraints; fence reason visible in proposals | §5.4 |

---

## 14. §12 "Deferred to Design" — Decisions Made

| Deferred decision | Decision |
|-------------------|----------|
| One process / module / protocol | One package (`computronium/experiment`) with pillar submodules; pillar boundaries are Protocols, so a future process split is a transport change, not a redesign (R13, R16, K7) |
| Policy substitutability expression | Small `Policy` Protocol + obligations-on-wrapper; external policies satisfy stratification because the wrapper, not the sampler, reports coverage (R17, R18, R71) |
| Record identity representation | Four-section identity + three identity keys; old records labelled by schema-version reader; hashes stable across readers (R7–R9, R79, K4) |
| Store shape | Evolution of the KB into the unified store, preserving analytics (R13, R15, K5) |
| Stage model → call graph | Fixed S1–S11 sequence; pluggable stage Protocols; wrapper owns fragments (R39–R41) |
| Non-uniform allocation | Substitutable `AllocationPolicy` reading interim evidence; interacts with pruners/fidelity via the same budget interface (R46–R49) |
| Governance representation | Always-on primary record fields + derived claim queries, never cached; gates are predicates, cheap enough to be always-on (R10, R34, R35, K6, K9) |
| CLI collapse | One report library, thin front-ends, documented-command conformance tests (R78, R80) |
| Prior representation | Prior registry (data), search supersedes (R52, Q3/Q4/Q12) |
| Capability registry structure | One generic `Registry` + decorator registration + reflection conformance harness (R76–R78) |
| Run-scoped state location | Injected `SystemContext`; kernel cache keyed `(run, coordinate, device, dtype)` (R75, K10, Q13) |

---

## 15. Rev 3 Integration — Gated Scope *(rev 1.1)*

TODO43 §13–§15 are marked **"CANDIDATES / PROPOSALS, pending review; nothing here is accepted until reviewed."** This specification follows §15's recommended order and treats them as scope, **conditionally**. Consolidation must not precede the union fix: consolidating on an incomplete union bakes gaps into the registry permanently.

**Gate:** before Pillar 1 locks, a review pass must accept or reject each Rev 3 candidate. This spec's completeness is conditional on that review.

| If review rejects… | Sections affected |
|--------------------|-------------------|
| A §13.1 implementation | §6.3 policy catalog; capability registry seed rows |
| An Appendix-C parameter or rule | §4.2 union; the `harvest_schema() ⊇ App C` lock |
| A §13.3 collectable | §4.6 payload record types |
| A §13.4 procedure | §10.3 capability rows |
| A §13.5 domain | §4.1 task domain rows (B.6) |

| Rev 3 item | How it is absorbed (pending gate) |
|------------|-----------------------------------|
| §13.1 six implementations | Policy catalog extended (`Evolution`, `Synthesis`, `StrategyProgression`, `TrainerDriven`); capabilities rowed into the registry; P1 table corrected |
| §13.2 continuous union missing | Appendix C → union: tunables as `AxisSpec` registry data; union derived by reflection + conformance-locked; `batch_size`, optimizer betas, and `apply_constraints` added |
| §13.3 collectables | EMA-harvest, I(C,U) rows, recipe cards, frozen-θ ψ, claim records, ANOVA/Sobol, genealogy, microbench JSONL, distributed-fault records → registered payload/record types |
| §13.4 procedures | 5-level benchmark suites, MEP tournament, evolution campaigns, corpus certification, kernel-ladder promotion → capabilities with conformance tests |
| §13.5 minor gaps | Graph/tabular/time-series domains added to B.6; `stability`/`psi_peft`/`local_feedback` capabilities counted; model export as a post-promotion artifact path |
| §14 abstractions A–E | Adopted as the structural spine (§2.3) |
| §15 order | Followed: union fixed first → abstractions adopted → requirements renumbered under pillars |

**Requirement merges (TODO43 §14.1).** This spec keeps all 88 requirements traceable rather than merging to ~60, per the §14.3 guardrail that no verification clause may be lost; the §14.1 merges remain available as an optional post-acceptance simplification, applied only with the guardrails intact.

---

## 16. Constraint Compliance (K1–K10)

| K | Compliance |
|---|-----------|
| K1 | Python 3.14+, uv, single lock; metaprogramming via stdlib (`typing`, `dataclasses`, `importlib`) — no new mandatory runtime dep |
| K2 | All sketches use Protocols (no ABC), PEP 695 generics, `slots=True`, no `Any` |
| K3 | Store writes async-safe (WAL); no blocking I/O in async paths |
| K4 | Old artifacts readable via per-version readers (R79); hashes stable across readers (§4.5) |
| K5 | KB vector/surrogate/causal preserved and reachable from every policy/report (R15) |
| K6 | Governance fails closed: unverifiable record ≠ result; underivable claim ≠ expressible |
| K7 | Per-evaluation overhead measured by a benchmark harness, not assumed; record cost budgeted (Class E, §12) |
| K8 | Concurrency cannot weaken R9/R26; `measurement_key` uniqueness + monotonic sequence enforce no-duplicate/no-reorder regardless of backend |
| K9 | Governance = record fields, always-on, cheap; derived verdicts computed, never cached |
| K10 | No global singletons; run-scoped state injected via `SystemContext` |

---

## 17. Testing & Conformance Strategy

### 17.1 Layers

| Layer | Mechanism | Catches |
|-------|-----------|---------|
| Registry integrity locks | CI property tests: uniqueness, totality, no orphans per registry | Silent spec loss (P14) |
| Schema conformance lock | `harvest_schema() ⊇ Appendix B ∪ Appendix C`; same-name tunables agree | Union drift (P1, §13.2) |
| Compatibility matrix lock | Generated matrix ≡ `validate()` behavior | Doc/validator drift (P13) |
| Capability conformance | Harness walks `CAPABILITIES`, runs each test; CI fails on loss | Capability erosion (P14) |
| Documented-command conformance | Every documented CLI invocation is a test | CLI drift (P11) |
| Property-test generation | Hypothesis strategies generated from spec invariants | Governance cost (K9) |
| Replay hash assertion | Each run re-checks its determinism hash | Silent nondeterminism (P8) |
| Kill/resume test | `kill -9` mid-write; assert store consistent, no duplicate `measurement_key` | Crash safety (R12, R26) |
| Policy substitution test | One space, four policies; assert identical record shape + coverage | Coverage loss (R18) |
| **Class E benchmarks** | Cost-to-rank vs uniform; surrogate vs random; cost-model error; divergence-detection bound; overhead harness | Empirical verdicts (§12) |

### 17.2 The conformance harness

```python
# experiment/surface/conformance.py
def run_conformance() -> ConformanceReport:
    failures = []
    for cap in CAPABILITIES.all():
        if cap.status == SpecStatus.RETIRED:
            continue
        result = execute_test(cap.test)
        if not result.passed:
            failures.append((cap.id, result))
    if failures:
        raise ConformanceFailure(failures)  # CI gate
```

Retirement is only via an explicit `status: RETIRED` + `migration_note` in the registry (R78). The registry, not the test, is the enforcement point.

### 17.3 Performance budget (K7)

Per-evaluation overhead is measured, not assumed. A benchmark harness times the wrapper's obligations (coverage, classification, store write) per evaluation and asserts they remain below a budgeted fraction of the evaluation itself. If recording becomes costly, that is a design defect to fix, not a reason to make governance optional (K9).

---

## 18. Migration & Phasing

Sequencing is a separate document, but the shape:

1. **Review-gate Rev 3, then fix the union** — accept/reject §13–§15 candidates (§15); audit `lab`/`lightning`/`execution`; add the continuous union + missing domain rows; conformance-lock Appendix C. *(Consolidating on an incomplete union bakes gaps into the registry forever.)*
2. **Lay the schema pillar** — registries, one axis type, coordinate, record, versioning; KB evolves into the unified store with old-shape readers.
3. **Stand up the pipeline + legality** — stage runner, constraint engine, classification; migrate `broad_map`/`stack`/`hyperopt` behind the Protocols one at a time (strangler pattern; each keeps working until cut over).
4. **Wire evidence + learning** — governance predicates, failure intelligence, prior store, surrogate/I(C,U) loop.
5. **Collapse the surface** — one store, one report, thin CLIs, capability conformance gates merges.
6. **Retire** the four stores, the prior tables, and the duplicate report paths via explicit registry retirement records (R78).
7. **Run the Class E benchmarks** (§12) and record verdicts as records in the store.

Throughout: historical records are read and labelled, never re-measured (non-goal), and every step is guarded by the capability conformance suite so no C1–C88 capability is silently lost (R77).

---

## 19. Risks & Invariants (carried from TODO43 §10, §14.3)

| Risk | Mitigation |
|------|-----------|
| Custom policy objects may not satisfy third-party sampler contracts | Obligations on wrapper, not plugin (§6.2) |
| Non-uniform allocation can bias toward easy-to-evaluate coordinates | Recorded allocation rationale (R47) + per-run coverage (R18) |
| Conformance can become ceremony bypassed under deadline | Registry is the enforcement point; retirement only via explicit change (R78) |
| One store could tempt dropping KB analytics | K5/R15 forbid it; analytics are views, not casualties |
| Serializable run spec may fossilize assumptions | Spec is minimal and versioned (R79); a contract, not a freeze |
| Registry/conformance runtime cost could contradict K7 | Evidence metadata must be cheap (K9); measure, don't assume (Class E harness) |
| Global-singleton habits recreate P16 | K10 enforced by a lock that fails on module-level run-scoped state |
| Treating Class E requirements as architectural | §12 classification names the verdict source for each |

**Guard rails (what consolidation must not do):**
- No MUST→SHOULD demotion: every verification clause survives its merge.
- R17 stays a catalog — the policy union is the preservation proof.
- Global suppression (R38) stays distinct from per-run constraint scoping.
- K5/K6/K9/K10 are design invariants, not mergeable requirements.

---

## 20. Why This Is Elegant

**Five abstractions carry eighty-eight requirements** — each discharged by the means appropriate to its class (§12), no MUST→SHOULD demotion, every verification clause intact.

**Nothing hand-maintained that can drift.** Axes, hyperparameters, constraints, objectives, and capabilities are definitions; everything else is regenerated. P4, P11, P14, R63 die together.

**Derived verdicts are never cached.** Governance is primary fields plus pure queries — the side-effect discipline that produced P6 has no surface to grow on.

**The hard properties are structural, not disciplinary.** Coverage survives policy substitution because the wrapper reports it. Claims are governed because they are queries, not assertions. Failures are never re-paid because voids are globally suppressive. Acceleration is attributable because it is run-scoped. Identity is stable across schema evolution because hashes bind to the bytes as written. You cannot forget these; the architecture does them.

**It evolves by registration.** A new axis, knob, policy, stage, objective, or constraint is an addition, not an edit — which is precisely what a framework whose ontology is "a design abstraction, not a law" must be able to do.

**The closed loop is complete.** Experiments produce records. Records train surrogates and metamodels (I(C,U)). Surrogates guide future experiments. Reasoning generates hypotheses. Hypotheses motivate experiments. Results update priors. The system learns to search.

---

## Appendix I — Exception Hierarchy *(rev 1.1, new)*

```
ExperimentError
├─ SchemaError
│  ├─ UnknownSpec(registry, id)
│  ├─ DuplicateSpec(registry, id)
│  ├─ RegistryLocked(registry)
│  └─ ConflictingTunable(name, declarations)     # §4.2 dedup lock
├─ LegalityError
│  ├─ ConstraintViolation(constraint, coordinate, reason)
│  └─ InvalidCoordinate(schema, violations)
├─ ExecutionError
│  ├─ EvaluationFailure(stage, cause)            # isolated → becomes a record (R29)
│  ├─ GuardKilled(signal, value, cost_saved)     # R51
│  └─ BudgetExhausted(kind: SOFT | HARD)
├─ StoreError
│  ├─ DuplicateMeasurement(measurement_key)      # resume dedup (R26)
│  └─ StoreCorruption
└─ GovernanceError
   └─ ClaimNotDerivable(record_id, missing)      # K6 fails closed
```

`EvaluationFailure` and `GuardKilled` are *expected* control flow: the wrapper catches them, writes the corresponding record, and continues. Only `StoreCorruption` and `RegistryLocked`-class errors abort a run.

## Appendix II — Store DDL (sketch) *(rev 1.1, new)*

```sql
PRAGMA journal_mode = WAL;

CREATE TABLE records (
    record_id        TEXT PRIMARY KEY,      -- content hash of bytes as written (§4.5)
    schema_version   INTEGER NOT NULL,
    cell_key         TEXT NOT NULL,         -- hash(coordinate); repeat grouping (R9)
    measurement_key  TEXT NOT NULL UNIQUE,  -- hash(coordinate ∪ schedule); dedup (R26)
    coordinate_json  TEXT NOT NULL,
    schedule_json    TEXT NOT NULL,
    provenance_json  TEXT NOT NULL,
    status_json      TEXT NOT NULL,         -- primary fields only (§7.2)
    payload_json     TEXT NOT NULL,
    unknown_json     TEXT,                  -- R79 preserved fields, labelled
    seq              INTEGER NOT NULL,      -- monotonic write order (K8)
    written_at       TEXT NOT NULL
);
CREATE INDEX idx_records_cell  ON records(cell_key);
CREATE INDEX idx_records_seq   ON records(seq);

CREATE TABLE artifacts (
    digest  TEXT PRIMARY KEY,               -- sha256, content-addressed
    kind    TEXT NOT NULL,                  -- config | figure | reproducer | kernel
    bytes   BLOB NOT NULL
);

CREATE TABLE record_artifacts (
    record_id TEXT NOT NULL REFERENCES records(record_id),
    digest    TEXT NOT NULL REFERENCES artifacts(digest),
    role      TEXT NOT NULL,
    PRIMARY KEY (record_id, digest, role)
);

CREATE TABLE seq_counter (n INTEGER NOT NULL);   -- single row; write-order authority
```

Vector index and surrogate/causal views (K5, R15) attach over `records` without altering this core.

## Appendix III — Predicate DSL Wire Format *(rev 1.1, new)*

Every `Expr` serializes to one JSON object with exactly one operator key; content hash = sha256 of canonical JSON (sorted keys, no whitespace).

```json
{"and": [
  {"field": "credit", "eq": "thermodynamic_contrast"},
  {"field": "params.beta", "between": [1e-3, 100.0]},
  {"not": {"in": {"field": "geometry.topology",
                  "values": ["feedforward"]}}}
]}
```

Operator keys: `field`, `lit`, `eq`/`ne`/`lt`/`le`/`gt`/`ge`, `in`, `between`, `and`, `or`, `not`. Field paths address the coordinate (`credit`, `params.beta`) or, for claims, record sections (`schedule.n_seeds`, `status.gate_verdict`). Constraints and claims persist as this JSON plus their `reason`, so legality is diffable, hashable, and queryable.

## Appendix IV — Revision Changelog

**Rev 1.0 → Rev 1.1:**

1. **Unified tunable representation.** Abolished the separate `Tunable` type and `TUNABLES` registry; a tunable is an `AxisSpec` in `AXES` (§4.1). Added the name-deduplication rule (70 slots → 37 unique) with availability-as-disjunction, making `learning_rate` one searchable axis (R2) and `harvest_schema() ⊇ App C` lockable (§4.2).
2. **Removed stored `claim_eligible`.** `Status` now holds primary fields only; claim eligibility is a pure function recomputed on every query (§7.2, §7.3; Doctrine principle 5 strengthened: derived verdicts are never cached).
3. **Unified coordinate knob naming** to `params` throughout (§4.4).
4. **Defined the three identity keys** — `cell_key`, `measurement_key`, `record_id` — and the hash-stability rule: `record_id` hashes the canonical bytes as written and is never recomputed by versioned readers (§4.5). Resume/dedup keys on `measurement_key`.
5. **Withdrew the blanket "by construction" acceptance claim.** Added the structural / empirical / process requirement classification and named the verdict source for every empirical requirement (§0.3, §12).
6. **Made Rev 3 an explicit review gate** with an affected-section map (§15); migration step 1 now gates on it (§18).
7. **Store honesty:** added DDL sketch (App. II), stated the single-writer assumption and upgrade path, and added the monotonic-sequence write-order invariant (K8) (§7.1).
8. **Added implementable artifacts:** exception hierarchy (App. I) and predicate DSL wire format (App. III).
9. **Closed coverage gaps:** R43 (via `Synthesis`), R44 (per-task schedule adaptation), R73 (export bundle) now explicitly carried (§2.2, §4.8, §6.3).

---

*This specification discharges TODO43 §12, resolves Q1–Q16, integrates Rev 3 as gated scope, classifies and satisfies every requirement by the means appropriate to its class — leaving implementation, decomposition, and rollout sequencing to follow.*

----

## Why it's the right target

- It resolves every deferred §12 decision and every Q1–Q16, maps all R1–R88 to the five abstractions, and the four self-inconsistencies from Rev 1.0 (tunable/axis duality, stored `claim_eligible`, field-name drift, `record_id` instability) are fixed.
- The architecture is sound and matches the existing Computronium doctrine (the 64-spec `ImplementationSpec` registry, registry-completeness locks, Protocol-over-ABC) — so it extends the codebase rather than fighting it.
- Preservation is mechanical (R76–R78), which is the whole point of consolidating four overlapping systems without losing the C1–C88 union.

So as a *design target*, yes. But three things must be true before anyone writes implementation code.

## Gate 1 — Accept or reject Rev 3 first (blocking)

TODO43 §13–§15 and Appendix C are still marked **"CANDIDATES, pending review; nothing here is accepted until reviewed."** Rev 1.1 folds them in as *gated* scope (§15). If you start coding before that review, you risk baking an incomplete union into the registries permanently — exactly the failure §15 warns about. **Pass the review gate; accept/reject each candidate; then proceed.**

## Gate 2 — Fix the union before consolidating (blocking)

Migration Step 1 (§18) is non-negotiable: audit `lab`/`lightning`/`execution`, add the continuous hyperparameter union (Appendix C → B.9) and the missing domain rows, and conformance-lock it. Consolidating four systems onto an incomplete union locks the gaps in. **Union first, then Pillar 1.**

## Gate 3 — It's a spec, not code (structural)

Rev 1.1 explicitly defers decomposition and sequencing (§17: "sequencing is a separate document"). There is a required layer between this spec and working code:

- A **decomposition/sequencing doc** (work packages, dependencies, the strangler migration of `broad_map`/`stack`/`hyperopt`).
- A **minimal vertical slice** ("walking skeleton"): one registry + coordinate + record + store + one policy end-to-end, proving the five abstractions compose, before building out all six pillars.

## The one thing that will surprise you

§12 classifies requirements as **structural / empirical / process**. The empirical ones — **R46** (cost-to-rank beats uniform), **R54** (surrogate beats random), **R23/R24** (cost-model quality), **R50** (divergence bound), **R86** (attribution reproduces a known effect) — **cannot be implemented into existence.** The architecture provides the mechanism; a benchmark provides the verdict. Expect to *run* those, not *code* them. If R46 "fails," that's a finding, not a design bug — provided the mechanism and its recording are intact.
