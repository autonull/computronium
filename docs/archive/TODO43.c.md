# Computronium Unified Experiment Framework — Design Specification

**Document class:** Design specification (discharges TODO43 §12 "Deferred to Design").
**Governing contract:** TODO43 Rev 3 — all MUST/SHOULD requirements, capabilities C1–C88, problems P1–P17, constraints K1–K10.
**Doctrine adopted:** Rev 3 abstractions **A–E** (§14) as structural spine; §5 renumbered under the six pillars (§14.2); §13 completeness gaps folded in as accepted scope.

---

## 0. Scope, Supersession, and Acceptance

### 0.1 What this document is
TODO43 is *requirements only*. This is the design those requirements deferred. It makes every §12 decision, resolves every Q1–Q16 where the abstractions allow, integrates the Rev 3 addendum as accepted scope, and specifies an implementation that is **effective** (kills P1–P17), **robust** (crash-safe, failure-isolated, fails closed), **rigorous** (every claim a query over governed records), and **elegant** (registries built by reflection, schemas synthesized, nothing hand-maintained that can drift).

### 0.2 Non-goals (inherited from TODO43 §1.3)
No reimplementation of Optuna internals; no change to ontology primitives or substrate physics; no algorithm preference; no re-measurement for its own sake; no CLI-verb backwards compatibility (records, capability registry, and flag inventory are the compatibility surfaces); the system makes validity *checkable*, never renders verdicts.

### 0.3 Acceptance
The specification is satisfied when the acceptance conditions of TODO43 §8 hold *by construction*: one schema expresses the Appendix-B + Appendix-C union; one run yields records at >1 lr/substrate/fidelity; any policy's records are queryable/claim-evaluable by the same code from one store; coverage survives policy substitution; allocation is evidence-driven with recorded waste; failures are machine-readable and never re-paid; kill/resume is duplicate-free under concurrency; every claim carries *n* + variance + matched-cost reference; every capability has a registry entry and passing test; a run is a versioned, diffable, portable spec; reasoning artifacts are linked records; acceleration is run-scoped with provenance.

---

## 1. Guiding Doctrine

Eight principles govern every decision below. They are the elegance contract.

1. **Registries are built, not written (Abstraction A).** Every axis, objective, capability, constraint, prior, and flag is a *spec* registered by reflection over decorated definitions. Hand-maintained tables (P4) are structurally impossible: there is no table to maintain, only a registry to query.
2. **One record schema, four identity sections (Abstraction B).** `identity = coordinate ∪ schedule ∪ provenance ∪ status`. This *resolves Q1*: "the same cell" = coordinate key; "the same measurement" = full identity.
3. **Legality is a predicate engine, not a dictionary (Abstraction C).** Constraints are data (predicate + recorded reason + scope), enforced at S4, re-checked at S6, queryable, globally suppressive. The compatibility matrix is *generated* from the engine (R63), so docs cannot drift from `validate()`.
4. **Obligations live on the pipeline, not the plugins (Abstraction D).** Policies/stages/evaluators/backends implement small Protocols; the *wrapper* emits coverage, void/defect classification, traceability, and stage fragments for *any* plugin. R18's coverage guarantee cannot be lost by swapping a sampler.
5. **Governance is stored predicates (Abstraction E).** Statuses/causes/verdicts are record fields; claims, promotions, alerts, and reports are *pure queries* over them. *Resolves Q9*: the CEEC ledger status is a record field with a provenance link; the chain stays in the ledger.
6. **Fail closed (K6).** A record that cannot be validated is not a result; a claim that cannot be derived from a predicate is not expressible.
7. **Run-scoped state, injected, never global (K10).** Kernels, caches, and device context ride a `SystemContext`, never module singletons (P16 is the cautionary example).
8. **Everything derives from the registries.** Docs, identity cards, the compatibility matrix, CLI help, "what-we-can-do" listings, and the conformance suite are *codegen over registries* (R63, R80). Drift is a build failure, not a habit.

---

## 2. Architecture Overview

### 2.1 Module map (one package, six pillars)

```
computronium/experiment/                 # the unified framework ("the Kernel")
├─ schema/        PILLAR 1 — coordinate, record identity, registries, hyperparam union
│   ├─ registry.py      the one Registry (Abstraction A)
│   ├─ axis.py          axis specs + primitive auto-registration
│   ├─ hyperparam.py    rule spaces + continuous union (Appendix C as B.9)
│   ├─ coordinate.py    Coordinate + CoordinateSchema synthesis
│   ├─ record.py        Record: four identity sections (Abstraction B)
│   └─ versioning.py    schema/spec versions + old-shape readers (R79, K4)
├─ execution/     PILLAR 2 — stages, policies, budget, determinism, allocation
│   ├─ stage.py         Stage Protocol, StageContext, StageFragment
│   ├─ pipeline.py      the runner — obligations live here (Abstraction D)
│   ├─ policy.py        Policy Protocol + shipped catalog (R17 preservation proof)
│   ├─ budget.py        Budget + learned CostModel (R21–R24)
│   ├─ allocator.py     multi-fidelity evidence-driven allocation (R46–R51)
│   └─ replay.py        replay hash, resume, checkpoint/restore (R26–R30)
├─ legality/      PILLAR 3 — constraint engine, voids, defects
│   ├─ constraint.py    Constraint specs + predicate composition
│   ├─ engine.py        evaluation + compatibility-matrix generation (R63)
│   └─ classify.py      void vs defect classification (R19, R38, R42)
├─ evidence/      PILLAR 4 — governance predicates, failure intelligence, claims
│   ├─ status.py        status fields (Abstraction E)
│   ├─ claims.py        claim/promotion/alert queries (R35, R64, R83)
│   ├─ failure.py       cause taxonomy, clustering, reproducers (R58–R62)
│   └─ ceec.py          CEEC ledger linkage (Q9)
├─ learning/      PILLAR 5 — priors, surrogates, I(C,U), reasoning records
│   ├─ prior.py         prior store (ruler/step-size tables as data, R52)
│   ├─ surrogate.py     surrogate-driven proposals (R54, Q10)
│   ├─ icu.py           I(C,U) metamodel warm-start (R53, R55)
│   └─ reasoning.py     hypothesis/literature records (R57)
└─ surface/       PILLAR 6 — store, reports, CLI, conformance, operations
    ├─ store.py         the one store (R13), evolution of the KB (K5)
    ├─ report.py        the one report (R14, R85)
    ├─ cli.py           thin front-ends over one library (Q8)
    ├─ conformance.py   capability registry + conformance harness (R76–R78)
    └─ operations.py    daemon, steering, record-predicate alerts (R81–R84)
```

### 2.2 Pillar ↔ requirement coverage (per TODO43 §7.2)

| Pillar | Satisfies (group-level) |
|---|---|
| 1 Schema | R1, R4–R9, R11, R67, R79; the coordinate/identity half of R22 |
| 2 Execution | R8, R16–R18, R21–R30, R39–R41, R44–R51, R72, R74–R75 |
| 3 Legality | R10, R19, R25, R29, R37, R38, R42, R66 |
| 4 Evidence | R10, R34–R36, R50, R51, R58–R65, R83, R84 |
| 5 Learning | R2, R6, R9, R15, R52–R57 |
| 6 Surface | R3, R5, R12–R14, R20, R31–R33, R63, R70–R71, R73, R76–R82, R85–R88 |

Every capability C1–C88 is carried by exactly one pillar and registered in the capability registry (R76), so §7.2's coverage becomes mechanically enforced rather than asserted.

### 2.3 The five abstractions, placed

| Abstraction | Realized in | Resolves |
|---|---|---|
| A — one registry pattern | `schema/registry.py` (+ one instance per kind) | R5, R31, R33, R70, R76–R78, R80 |
| B — one record schema | `schema/record.py`, `schema/coordinate.py` | Q1; R7–R9, R11, R67, R79 |
| C — one constraint engine | `legality/*` | Q2; R19, R25, R37, R38, R66; absorbs `apply_constraints` |
| D — pipeline obligations | `execution/pipeline.py` | R16–R18, R39–R40, R70–R72 |
| E — governance as predicates | `evidence/status.py`, `evidence/claims.py` | Q9; R10, R34–R36, R58–R59, R64, R83 |

---

## 3. Pillar 1 — Schema

### 3.1 The one registry (Abstraction A)

A single generic `Registry` is instantiated for *every* spec kind: axes, objectives, capabilities, constraints, priors, rule spaces, flags. This matches the existing doctrine (the 64-spec `ImplementationSpec` registry, `test_dynamics_wiring_lock`, registry-completeness locks) and puts **one conformance harness over all instances**.

```python
# experiment/schema/registry.py
from collections.abc import Iterator
from typing import Protocol, runtime_checkable

@runtime_checkable
class Spec(Protocol):
    @property
    def id(self) -> str: ...
    @property
    def schema_version(self) -> int: ...

class Registry[S: Spec]:                       # PEP 695 generic
    """Integrity-locked, codegen-ready registry (Abstraction A)."""
    def __init__(self, name: str) -> None:
        self._name, self._specs, self._locked = name, {}, False

    def register(self, spec: S) -> None:
        if self._locked:
            raise RegistryLocked(self._name)          # mutations go through migration
        if spec.id in self._specs:
            raise DuplicateSpec(self._name, spec.id)
        self._specs[spec.id] = spec

    def get(self, id: str) -> S:
        try: return self._specs[id]
        except KeyError: raise UnknownSpec(self._name, id) from None

    def all(self) -> tuple[S, ...]: return tuple(self._specs.values())
    def lock(self) -> None: self._locked = True
```

**Why this kills drift:** registries lock after import; the only way to add/remove a spec is an explicit, recorded migration (R78's "explicit retirement record"). One harness conformance-tests every registry instance (R77).

### 3.2 Axis specs + primitive auto-registration

Primitives self-register via `__init_subclass__` reflection — no hand-listed axis tables (Appendix B becomes a *view* of the registry, generated, not written).

```python
# experiment/schema/axis.py
AXES: Registry[AxisSpec] = Registry("axis")

class AxisPrimitive:
    axis: ClassVar[Axis]
    primitive_id: ClassVar[str]

    def __init_subclass__(cls, *, axis: Axis, primitive_id: str, **_) -> None:
        super().__init_subclass__()
        cls.axis, cls.primitive_id = axis, primitive_id
        AXES.register(AxisSpec(
            id=f"{axis.value}.{primitive_id}", axis=axis,
            primitive_id=primitive_id, config_schema=cls.config_schema(),
        ))

# A concrete primitive registers itself at class-definition time:
class EnergyMinimization(AxisPrimitive, axis=Axis.DYNAMICS, primitive_id="energy_minimization"):
    ...
```

Enumerating legal values per axis (R5) is now `AXES.all()` filtered by axis — **discoverable at runtime from a registry, not from source reading**, and matching Appendix B by construction.

### 3.3 The continuous hyperparameter union (Appendix C → B.9)

This is the direct fix for **§13.2**: the 37 unique continuous parameters currently living only in `hyperopt/search_space.py::RULE_SPACES` become registry data, and the union is **derived by reflection** so it cannot fall out of sync again.

```python
# experiment/schema/hyperparam.py
RULE_SPACES: Registry[RuleSpace] = Registry("rule_space")

@dataclass(frozen=True, slots=True)
class HyperparamField:
    name: str
    kind: HyperparamKind              # FLOAT | INT | BOOL | CATEGORICAL
    lo: float | None = None
    hi: float | None = None
    log: bool = False
    choices: tuple[str, ...] = ()
    default: float | int | bool | str | None = None

def rule_space(rule: str):
    def deco(cls):
        fields = frozenset(v for v in vars(cls).values() if isinstance(v, HyperparamField))
        RULE_SPACES.register(RuleSpace(rule=rule, fields=fields))
        return cls
    return deco

@rule_space("eqprop")
class EqPropSpace:                     # all 18 fields declared inline
    learning_rate = HyperparamField("learning_rate", HyperparamKind.FLOAT, 1e-5, 1.0, log=True)
    beta          = HyperparamField("beta",          HyperparamKind.FLOAT, 1e-3, 10.0, log=True)
    max_steps     = HyperparamField("max_steps",     HyperparamKind.INT,   1, 200)
    # … damping, tol, convergence_threshold, sparse_ratio, momentum, …

def continuous_union() -> frozenset[HyperparamField]:
    return frozenset(f for rs in RULE_SPACES.all() for f in rs.fields)
```

A **conformance lock** asserts `continuous_union()` matches Appendix C's 37-name enumeration — the union is now *counted and locked*, exactly as R1/R5 demand. This also absorbs the §13.2 gaps: `batch_size` (a schedule axis), per-update optimizer parameters (adam betas, muon momentum), and `SearchSpace.apply_constraints` (which becomes a constraint in Pillar 3).

**R4 (mixed spaces, one representation)** falls out: a `CoordinateSpace` is one object describing discrete axes *and* continuous fields together; there is no separate continuous mechanism.

### 3.4 Coordinate + schema synthesis

```python
# experiment/schema/coordinate.py
@dataclass(frozen=True, slots=True)
class CoordinateSchema:                # synthesized, never hand-written
    axes: tuple[AxisSpec, ...]
    hyperparams: frozenset[HyperparamField]
    schema_version: int

def synthesize_schema() -> CoordinateSchema:
    return CoordinateSchema(AXES.all(), continuous_union(), SCHEMA_VERSION)

@dataclass(frozen=True, slots=True)
class Coordinate:                      # the SYSTEM definition (Q1: "the cell")
    substrate: AxisValue
    geometry: AxisValue
    dynamics: AxisValue
    plasticity: AxisValue              # first-class axis (Q7 resolved §10)
    credit: AxisValue
    update: AxisValue
    hyperparams: HyperparamMap         # frozen name→value over applicable fields

    @property
    def cell_key(self) -> CellKey: ... # coordinate-only identity
```

Serialization, validation, and diffing (R41) are **derived from the schema** by reflecting over `axes` + `hyperparams` — no hand-written serializers, so a versioned, diffable run spec comes for free.

### 3.5 The record: four identity sections (Abstraction B)

```python
# experiment/schema/record.py
@dataclass(frozen=True, slots=True)
class Record:
    schema_version: int
    coordinate: Coordinate          # ─┐
    schedule: Schedule              #  ├ identity sections (Abstraction B)
    provenance: Provenance          #  │
    status: Status                  # ─┘
    payload: Payload                # metrics, telemetry, objectives, artifacts
    unknown: UnknownFields          # R79: preserved, labelled, never defaulted

    @property
    def identity(self) -> Identity:
        return Identity(self.coordinate, self.schedule, self.provenance, self.status)
```

Section contents and the requirements they discharge:

| Section | Fields | Discharges |
|---|---|---|
| `coordinate` | six axis values + hyperparams | R1, R2, R3, R7 |
| `schedule` | fidelity tier (L0/L1/L2), seed, epochs, batch limit | R8, R9, R22, R47 |
| `provenance` | env (device/dtype/workers/versions), dataset+split+version, code SHA, policy id + proposal state, reasoning/CEEC links | R11, R20, R57, R67 |
| `status` | gate verdict, defect ref, maturity tier, reproducibility, uncertainty, CEEC status+link | R10, R34, R64 |
| `payload` | objectives (resolved to one registry), settle telemetry, probes | R31, R50 |

**R8/R22/R67 become derived comparison guards:** any front/average/comparison *must* stratify by `schedule.fidelity`, label the mixture, or refuse (e.g. cross-data-version comparison refused or labelled). **R9** (repeats as distinct records sharing a coordinate key) is the store's index shape.

### 3.6 Versioning and evolution (R79, K4)

`versioning.py` keeps a **reader per schema version**. Old-shape records load through their version's reader; unknown fields are preserved as `UnknownFields` and *labelled*, never silently defaulted. Because axes/hyperparams are registry data, **adding an axis or knob is a registration + migration, not a core edit** — this is the framework's answer to "the ontology is a design abstraction": the coordinate schema is versioned so the abstraction itself may be re-cut without corrupting history.

---

## 4. Pillar 2 — Execution

### 4.1 The stage pipeline and obligations-on-the-wrapper (Abstraction D)

The eleven stages (S1 Frame … S11 Report) are a fixed sequence; each stage's *implementation* is a pluggable Protocol. The **pipeline runner**, not the plugin, carries the cross-cutting obligations.

```python
# experiment/execution/stage.py
@runtime_checkable
class Stage(Protocol):
    stage_id: ClassVar[StageId]
    def run(self, ctx: StageContext) -> StageFragment: ...

# experiment/execution/pipeline.py
class Pipeline:
    def run(self, spec: RunSpec) -> RunResult:
        ctx = StageContext(spec, store=self._store, budget=self._budget,
                           constraints=self._engine, context=self._sysctx)  # K10: injected
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

Consequences:
- **R39** — every stage exists for every run; a stage with nothing to say emits an explicit *no-op fragment*, so a stage-coverage report shows all eleven per run.
- **R40** — swapping a measurement or attribution implementation changes nothing about the record schema (the wrapper owns the fragment shape).
- **R29** — a failing evaluation is isolated; siblings, run, and store stay intact; the failure becomes a record with cause.
- **R18** — coverage/stratification statistics are emitted by the wrapper for *every* policy, including model-based, so substituting a TPE sampler cannot silently drop coverage guarantees.

### 4.2 Policy substitutability and the shipped catalog (R16, R17)

```python
# experiment/execution/policy.py
@runtime_checkable
class Policy(Protocol):
    def propose(self, ctx: SearchContext) -> Iterator[Proposal]: ...
```

The wrapper intercepts every proposal and applies, uniformly and in order: **constraint screening** (Pillar 3), **novelty suppression** (no re-measurement of known coordinates, C10), and **proposal-provenance stamping** (R20: which policy, what state/evidence). Policies therefore stay *small*.

**R17 is the shipped catalog — the preservation proof.** With Rev 3 §13.1 accepted, "today's union" is **six** implementations, so the catalog is:

| Policy | Preserved from | Character |
|---|---|---|
| `StratifiedRandom` | `broad_map.StratifiedRandomDriver` (C9) | stratified, objective-binned |
| `RoundRobinGrid` | `stack.grid_sampler` (C13) | deterministic ablation |
| `UniformRandom` | `stack._space_sampler` (C14) | baseline |
| `ModelBased` (TPE/NSGA-II + pruners) | `hyperopt/_finder.py` (C20) | continuous/mixed |
| `Evolution` (population/generations) | `computronium-lab` (§13.1) | budgeted evolution |
| `Synthesis` (spec→coordinate, constraint-screened) | `computronium-lab` (§13.1) | question-first |
| `StrategyProgression` | `execution/` (§13.1) | candidate progression |
| `TrainerDriven` (NAS/HPO) | `lightning_/` (§13.1) | trainer-loop search |

**R71** (third-party policies without forking) is satisfied because `ModelBased` wraps Optuna behind the same `Policy` Protocol via a storage adapter that reads/writes the *unified store* (not a private Optuna DB — closing P7).

### 4.3 Budget and learned cost model (R21–R24)

One `Budget` type governs every search, with soft/hard stop defined once and `consumed()/remaining()` exposed through one interface for every policy (R21). A `CostModel` estimates per-evaluation cost from `coordinate + schedule`, **learned from recorded per-stage walltime breakdowns** so estimates improve as records accumulate (R24); dry-run reports a cost estimate with stated uncertainty (R23). This unifies the four prior notions of duration (P5).

### 4.4 Multi-fidelity, evidence-driven allocation (R46–R51)

An `Allocator` replaces the fixed ladder (P12). It is a substitutable policy that decides, per coordinate in a population, **promote / abandon / continue** from *recorded interim evidence* (interim metrics, uncertainty, cost) — not tier position:

- **R46** — non-uniform allocation with early termination of clearly-inferior members; acceptance is the verbatim test *"measured cost-to-rank beats the uniform baseline."*
- **R47** — every promotion/abandonment references interim evidence present in the record.
- **R48** — compute spent before abandonment is recorded and attributable; a waste report flags repeatedly-measured-to-no-gain coordinates (the 1357 s / 1457-clamp case becomes detectable).
- **R49** — compute is appendable across sessions; an appended measurement is a new record of the same coordinate.
- **R50/R51** — divergence/stagnation signals (clamp storm, NaN, loss explosion, spectral radius, no-improvement) are first-class telemetry; a guard-kill record names the signal, its value, and the compute saved.

### 4.5 Determinism, resume, checkpointing (R26–R30)

- **R26** — same inputs + seed ⇒ same coordinates; resume skips recorded work (no duplicate, no reordered coverage).
- **R27** — determinism is *asserted*, not assumed: each run records and re-checks a **replay hash**.
- **R28** — environment nondeterminism (dataloader worker policy, daemon concurrency, device) is an explicit run property with recorded fallback (P15's forkserver race becomes attributable, not mysterious).
- **R30** — checkpoint/restore at run and evaluation granularity preserves remaining budget and evidence.

### 4.6 The run spec (R41, R45)

A run is fully described by one **versioned, serializable, diffable** spec — `(space, policy, schedule, evaluator, governance, budget, seed, provenance)` — synthesized from the registries (§3.4), from which the run reproduces. Space/evaluator are declarable independently of the store, so a spec re-runs against another store/code version and diffs (R45 portability).

### 4.7 Acceleration and run-scoped state (R75, K10)

Compiled-kernel caching is a **run-scoped object injected via `SystemContext`**, keyed by `(run, coordinate, device, dtype)` (Q13), carrying provenance and safe invalidation; no module-level singleton (K10). The **kernel ladder** (reference → `torch.compile` → Triton) and its parity + microbench evidence become a *record type* in the store (closing §13.3's note that the ladder's evidence trail was uncarried).

---

## 5. Pillar 3 — Legality

### 5.1 Constraints as data (Abstraction C)

```python
# experiment/legality/constraint.py
CONSTRAINTS: Registry[Constraint] = Registry("constraint")

@dataclass(frozen=True, slots=True)
class Constraint:
    id: str
    predicate: Predicate            # composable predicate over Coordinate
    reason: str                     # recorded, queryable
    scope: ConstraintScope          # GLOBAL (suppressive) | RUN
    enforced_at: tuple[StageId, ...]  # (S4, S6)

def constraint(id: str, *, reason: str, scope: ConstraintScope = ConstraintScope.GLOBAL):
    def deco(fn):
        CONSTRAINTS.register(Constraint(id, Predicate.of(fn), reason, scope, (StageId.S4, StageId.S6)))
        return fn
    return deco

@constraint("fence.sequence_on_feedforward",
            reason="sequence tasks require recurrent/external-memory geometry")
def _(c: Coordinate) -> bool:
    return not (is_sequence_task(c) and c.geometry.topology == "feedforward")
```

- **R37** — task-compatibility fencing is a first-class constraint with a recorded, queryable reason (not a hardcoded `TASK_COMPAT` dict); fenced tasks are excludable per run and the reason is visible in proposals (Q16).
- **R25** — fairness (param budget / FLOPs / walltime matching) is enforceable as a search constraint, not a post-hoc filter.
- **R66** — operating-point constraints (max latency/memory, min accuracy) are constraints.
- The §13.2 `apply_constraints` (`max_hidden`/`max_layers`/`max_steps`) becomes a constraint here.

### 5.2 Voids, defects, and propagation (R19, R38, R42)

`classify.py` applies one taxonomy to *every* policy's rejected/failed coordinates (R19): **ontology void** (infeasible-by-construction, declared via the constraint engine) vs **runtime defect** (discovered during evaluation). This *resolves Q2*: declared infeasibility is a space property; discovered infeasibility is an evaluation property; both flow through the same classifier. **R38** — known-infeasible coordinates are globally suppressive and never re-proposed by any policy. **R42** — a void found at S4 and one found at S6 appear identically in coverage, reports, and reference docs, *by construction* (both are constraint/classifier outputs feeding the same store).

### 5.3 The compatibility matrix is generated (R63)

```python
def compatibility_matrix(grid: Iterable[Coordinate]) -> CompatibilityMatrix:
    return CompatibilityMatrix(
        rows=grid,
        verdicts={(c, k): self._engine.check(c, k) for c in grid for k in ...},
    )
```

The reference compatibility matrix is produced by evaluating `CONSTRAINTS` over the grid, so it matches `validate()` behavior by test and **cannot drift** (P13/P11). This is codegen-over-registry doctrine applied to docs.

---

## 6. Pillar 4 — Evidence

### 6.1 Governance as stored predicates (Abstraction E)

`Status` fields are written by the producing stage; **claims, promotions, alerts, and reports are pure queries** over them:

```python
# experiment/evidence/claims.py
def claim_eligible(store: Store, *, task: Task) -> Iterator[Record]:
    """CAMPAIGN_PLAN §7 as one filter (R35). Fails closed (K6)."""
    for r in store.query(task=task):
        if (r.status.gate == Gate.PASSED
                and r.status.defect is None
                and r.status.maturity >= Tier.L2
                and r.status.uncertainty.seeds >= MIN_SEEDS
                and r.status.ceec.linked_and_gated()):
            yield r
```

- **R10** — a record cannot be presented as a result while carrying an open defect or failed gate, *computable from the record alone*, regardless of which implementation wrote it.
- **R34** — the full governance chain (dry-run gate, validation, defect quarantine/release, CEEC pre-registration, power pre-registration, replication gate, reproducibility) is available, and its outputs are record properties.
- **R35** — a claim is derived from a record predicate, never asserted by the producing run.
- **R36** — promotion is "select by predicate, re-evaluate at higher fidelity," applicable to any policy's output.
- **R64** — no claim is expressible without *n* and variance (enforced by the query shape).

### 6.2 CEEC linkage (Q9 resolved)

Per Abstraction E, the **CEEC status is a record field** (`status.ceec`) with a **provenance link** into the append-only CEEC ledger (`Experiment → Artifact → Evidence → Derived → Belief → Gated Status → Decision`). The record carries the *queryable status*; the ledger carries the *immutable chain*. Neither is a side artifact only its producer understands (P6).

### 6.3 Failure intelligence (R58–R62)

- **R58** — every failed/abandoned evaluation carries machine-readable `cause` (infeasible-by-construction, gate-rejected, guard-killed, defect, timeout, non-finite, user-stopped) and `severity` — **fields, not log text**.
- **R59** — automatic classification with an explicit `unclassified` bucket that has a count and an owner (a monitored signal).
- **R60** — from a defect, emit a minimal reproducer and, for implementation faults, a candidate regression test.
- **R61** — failure patterns cluster across runs so a systemic cause is found once.
- **R62** — a fix links to the defects it closes; post-fix verification is a query ("which defects does this change close?").

---

## 7. Pillar 5 — Learning

This is the pillar that turns a *search* into a system that **learns to search** — closing P9 (analytics unused by search) and P2/P4 (hardcoded priors).

### 7.1 Priors as data (R52, Q3, Q4, Q12)

The step-size override tables and the ruler-lr table become **records in a `prior` registry**, not code that silently biases runs. *Q4*: the ruler is an **input prior**, not an authoritative default. *Q12*: migrate the ~30 override-table entries to priors, retiring the rest with explicit records. *Q3*: the default lr search is **model-based, seeded from the ruler prior** (sample-efficient), with log-grid available as a policy. A search can start from priors and **exceed** them (R52).

### 7.2 Surrogates and the I(C,U) loop (R53–R55, Q10)

*Q10*: surrogates/causal capabilities **enter the search loop**, not just analysis.

- **R53** — new runs warm-start space and policy from prior records (including cross-task/cross-topology transfer), with transfer provenance in the spec.
- **R54** — surrogate models over records drive proposals (EI / expected-hypervolume-improvement); acceptance: a run logs surrogate-guided proposals and beats random on a held-out task.
- **R55** — learned quantities (per-task lr, per-combo stability) are transferable priors **with uncertainty**, applied only within that uncertainty and overridable.
- **I(C,U)** — the 0.944-accuracy learnability-interaction model (`fit_icu_model.py`, `icu_measurements.csv`) is registered as a surrogate/prior source feeding `ModelBased` and `Synthesis` policies. This is the framework's distinctive closed loop: *experiments train metamodels that guide future experiments.*

### 7.3 Lessons and reasoning records (R56, R57)

- **R56** — knowledge gained is queryable as lessons (what was learned, which change mattered), tied to code versions.
- **R57** — hypothesis chains (`reasoner`), LLM proposals (`local_llm`), and retrieved literature (`literature.py`) are **records with provenance, linked to the experiments they motivated** (closing P17). *Q15*: provenance-linked records are mandatory; active in-loop hypothesis generation is an opt-in S1 policy.

---

## 8. Pillar 6 — Surface

### 8.1 The one store (R13, K5)

**Decision (§12):** the store is an **evolution of the KB** — not a new silo, not a thin view. The KB becomes the unified store, preserving its vector/surrogate/causal/query assets (K5, R15). The four current stores consolidate:

| Today | Fate |
|---|---|
| `kb.sqlite` | **becomes** the unified store (evolved) |
| `campaign.db` | migrated in |
| `ledger.sqlite` | migrated in / becomes the CEEC reference |
| Optuna `*.db` | replaced by a storage adapter over the unified store (R71) |

- **R12** — WAL-mode, atomic, crash-safe writes; `kill -9` mid-write leaves the store queryable and consistent.
- **R13** — no implementation owns a private store; any record is queryable by all.
- **R74/K8** — concurrency is a policy/schedule parameter; store writes stay consistent under parallel evaluation, with no duplicate or reordered records.
- A `Store` **Protocol** keeps the backend substitutable (DuckDB/columnar later) without touching callers (supports R45).

### 8.2 The one report + CLI collapse (R14, R85, Q8)

*Q8*: **one library with thin front-ends.** `report.py` derives every report from the store alone; the many CLI/report paths (P11) collapse to scope arguments over one implementation.

- **R14** — reporting/analysis derivable from the store alone, one implementation per report; one command answers what today needs different tools.
- **R85** — every run emits, from the store alone, a report covering: objectives + fronts (by fidelity), axis coverage, budget consumed, failures by cause, promotion history, claim-eligible records.
- **R86** — axis attribution available for every run, comparable across runs.
- **R87/R88** — pinned auto-figures/manifests; narrative handoff summaries derivable from records.

### 8.3 Capability registry + conformance (R76–R78, R80)

```python
# experiment/surface/conformance.py
CAPABILITIES: Registry[Capability] = Registry("capability")

def capability(id: str, *, stage: StageId, test: str):
    def deco(cls):
        CAPABILITIES.register(Capability(id=id, stage=stage, test=test))
        return cls
    return deco
```

- **R76** — the capability inventory (C1–C88, plus §13.3 collectables and §13.4 procedures) is a machine-readable registry: id, stage, description, owner, verifying test.
- **R77** — a conformance suite asserts every registered capability works; CI fails if a capability loses its test. *Q5*: it **gates merges**, with an explicit, recorded waiver path.
- **R78** — every one-off flag, per-combination table, and subsystem report path maps to a registered capability or an explicit retirement record (Appendix A is the seed, kept current as a registry *view*).
- **R80** — a generated "what we can do" listing, documented-command conformance tests, and standard run profiles (quick-verify, production-map, maturation, claim) as data, each conformance-tested.

### 8.4 Objectives as one registry (R31–R33)

One objective registry (~39, with direction/weight/normalizer/axis tag); every stored metric resolves to it; multi-objective selections (fronts, portfolios, operating points) are computed from records so any policy's results are comparable (R32); new objectives add through an extension point without modifying core (R33). Because telemetry emitters *register* their objectives, the registry is reflection-built, not hand-listed.

---

## 9. Metaprogramming & Reflection Strategy

This is the cross-cutting layer that makes the design **future-proof and low-boilerplate**. Every technique below maps to a concrete requirement.

| # | Technique | Mechanism | Eliminates / Enables |
|---|---|---|---|
| 1 | **Auto-registration via `__init_subclass__`** | Primitives register into their axis registry at class-definition time | Hand-maintained axis tables (P4); R5 runtime discoverability |
| 2 | **Declarative hyperparameter spaces** | `@rule_space` classes; union derived by reflection | The §13.2 drift; Appendix B/C stay in sync by construction (R1, R5) |
| 3 | **Schema synthesis from registries** | `synthesize_schema()` walks registries | Hand-written coordinate schemas; R1 union is *derived*, not asserted |
| 4 | **Serialization/diff from schema** | to/from/diff generated from field specs | Boilerplate serializers; versioned, diffable run specs (R41) for free |
| 5 | **Constraints as data + matrix generation** | `@constraint` decorator; matrix by evaluation | Hardcoded `TASK_COMPAT`/void dicts; docs can't drift from `validate()` (R37, R63) |
| 6 | **`runtime_checkable` Protocols + structural conformance** | Plugins checked with `isinstance` at registration | Inheritance hierarchies; Protocol-over-ABC doctrine (K2); R16, R40, R70 |
| 7 | **Entry-point extension discovery** | `importlib.metadata.entry_points(group="computronium.policies")` | Forking to extend; out-of-tree policies/objectives/stages (R33, R70, R71) |
| 8 | **Codegen for docs/cards/listings** | Generate Appendix B, identity cards, compatibility matrix, "what-we-can-do" from registries | Documentation drift (P11, R63, R80) |
| 9 | **Capability conformance by reflection** | Harness walks `CAPABILITIES`, runs each `test` | Manual preservation checks; R76–R78 mechanically enforced |
| 10 | **Property-test generation from invariants** | Hypothesis tests generated from spec invariants (extends existing `generate_property_tests.py`) | Hand-written invariant tests; governance stays cheap (K9) |

**The invariant this buys:** the only hand-written artifacts are *definitions* (a primitive, a rule space, a constraint, a capability). Everything *derived* — the union, the schema, the matrix, the docs, the conformance — is regenerated from those definitions. Drift becomes a build failure. This is the structural answer to P4, P11, P14, and R63 simultaneously.

**Evolution posture:** new axes/knobs = registration; new policies/stages/objectives = Protocol implementation + optional entry point; schema changes = version bump + reader. Nothing requires editing the core. This satisfies R70 and makes "the ontology is a design abstraction" a *feature*, not a risk.

---

## 10. Open Questions — Disposition

| Q | Disposition | Basis |
|---|---|---|
| Q1 seeds/fidelity in coordinate? | **Resolved** — coordinate = system def; seeds/fidelity in `schedule`. "same cell" = coordinate; "same measurement" = full identity | Abstraction B |
| Q2 void: space or evaluation? | **Resolved** — declared infeasibility = constraint (space); discovered infeasibility = defect (evaluation); one classifier, identical propagation | Abstraction C |
| Q3 default lr search | Model-based, seeded from ruler prior; log-grid available as policy | R52 |
| Q4 ruler table role | **Input prior**, not authoritative default | R52 |
| Q5 conformance gating | **Gates merges** with recorded waiver path | R77/R78 |
| Q6 parallel in first release | In-scope as a policy/schedule param; phased rollout, store concurrency designed up front | R74/K8 |
| Q7 plasticity axis | **First-class coordinate axis** (README's ψ/frozen-θ/NTM/NCA emphasis mandates it); ψ objectives + frozen-θ gates attach | §13, README |
| Q8 reporting collapse | **One library, thin front-ends** | R14/R80 |
| Q9 CEEC ledger | **Resolved** — status is a record field with provenance link; chain stays in ledger | Abstraction E |
| Q10 surrogates in loop | **Enter the search loop** (EI/EHI); I(C,U) as prior/surrogate | R54 |
| Q11 robustness/matched-cost | Matched-cost (R65) **mandatory** for claims; robustness (R69) opt-in per study | R65/R69 |
| Q12 override-table migration | **Convert to priors**; retire the superseded with records | R52/R78 |
| Q13 kernel-cache scoping | Per **(run, coordinate, device, dtype)** | R75/K10 |
| Q14 alert routing | Record-predicate alerts; webhook w/ severity routing + dedup; **human decides** run/stop | R83 |
| Q15 literature/LLM depth | Provenance-linked records mandatory; active in-loop generation opt-in S1 policy | R57 |
| Q16 fenced tasks | Excludable per run via space constraints; fence reason visible in proposals | R37 |

---

## 11. §12 "Deferred to Design" — Decisions Made

| Deferred decision | Decision |
|---|---|
| One process / module / protocol | **One package** (`computronium/experiment`) with pillar submodules; pillar boundaries are Protocols, so a future process split is a transport change, not a redesign (R13, R16, K7) |
| Policy substitutability expression | Small `Policy` Protocol + obligations-on-wrapper; external policies satisfy stratification because the wrapper, not the sampler, reports coverage (R17, R18, R71) |
| Record identity representation | Four-section identity (Abstraction B); old records labelled by schema-version reader (R7–R9, R79, K4) |
| Store shape | **Evolution of the KB** into the unified store, preserving analytics (R13, R15, K5) |
| Stage model → call graph | Fixed S1–S11 sequence; pluggable stage Protocols; wrapper owns fragments (R39–R41) |
| Non-uniform allocation | Substitutable `Allocator` policy reading interim evidence; interacts with pruners/fidelity via the same budget interface (R46–R49) |
| Governance representation | **Always-on record fields** (statuses/causes/verdicts) + claim queries; gates are predicates, cheap enough to be always-on (R10, R34, R35, K6, K9) |
| CLI collapse | One report library, thin front-ends, documented-command conformance tests (R78, R80) |
| Prior representation | Prior registry (data), search supersedes (R52, Q3/Q4/Q12) |
| Capability registry structure | One generic `Registry` + decorator registration + reflection conformance harness (R76–R78) |
| Run-scoped state location | Injected `SystemContext`; kernel cache keyed `(run, coordinate, device, dtype)` (R75, K10, Q13) |

---

## 12. Rev 3 Integration (accepted scope)

| Rev 3 item | How it is absorbed |
|---|---|
| **§13.1** six implementations | Policy catalog extended to include `Evolution`, `Synthesis`, `StrategyProgression`, `TrainerDriven`; their capabilities rowed into the capability registry; P1 table corrected |
| **§13.2** continuous union missing | Appendix C → **B.9**: rule spaces as registry data; union derived by reflection + conformance-locked; `batch_size`, optimizer betas, and `apply_constraints` added |
| **§13.3** collectables | EMA-harvest, I(C,U) rows, recipe cards, frozen-θ ψ, claim records, ANOVA/Sobol, genealogy, microbench JSONL, distributed-fault records → registered as payload/record types |
| **§13.4** procedures | 5-level benchmark suites, MEP tournament, evolution campaigns, corpus certification, kernel-ladder promotion → registered as capabilities with conformance tests |
| **§13.5** minor gaps | Graph/tabular/time-series domains added to B.6; `stability`/`psi_peft`/`local_feedback` capabilities counted; model export as a post-promotion artifact path |
| **§14** abstractions A–E | Adopted as the structural spine (§2.3) |
| **§15** order | Followed: union fixed first → abstractions adopted → §5 renumbered under pillars |

---

## 13. Constraints Compliance (K1–K10)

| K | Compliance |
|---|---|
| K1 | Python 3.14+, uv, single lock; metaprogramming via stdlib (`typing`, `dataclasses`, `importlib`) — no new mandatory runtime dep |
| K2 | All sketches use Protocols (no ABC), PEP 695 generics, `slots=True`, no `Any` |
| K3 | Store writes async-safe (WAL); no blocking I/O in async paths |
| K4 | Old artifacts readable via per-version readers (R79) |
| K5 | KB vector/surrogate/causal preserved and reachable from every policy/report (R15) |
| K6 | Governance fails closed: unverifiable record ≠ result; underivable claim ≠ expressible |
| K7 | Per-evaluation overhead measured by a benchmark harness, not assumed; record cost budgeted |
| K8 | Concurrency cannot weaken R9/R26; store writes consistent under parallelism |
| K9 | Governance = record fields, always-on, cheap (property-test-generated checks) |
| K10 | No global singletons; run-scoped state injected via `SystemContext` |

---

## 14. Migration & Phasing (sequencing is a separate doc, but the shape)

1. **Fix the union** — audit `lab`/`lightning`/`execution`; add B.9 + missing domain rows; conformance-lock Appendix C. *(Consolidating on an incomplete union bakes gaps into the registry forever — §15.)*
2. **Lay the schema pillar** — registries, coordinate, record, versioning; KB evolves into the unified store with old-shape readers.
3. **Stand up the pipeline + legality** — stage runner, constraint engine, classification; migrate `broad_map`/`stack`/`hyperopt` behind the Protocols one at a time (strangler pattern; each keeps working until cut over).
4. **Wire evidence + learning** — governance predicates, failure intelligence, prior store, surrogate/I(C,U) loop.
5. **Collapse the surface** — one store, one report, thin CLIs, capability conformance gates merges.
6. **Retire** the four stores, the prior tables, and the duplicate report paths via explicit registry retirement records (R78).

Throughout, historical records are **read and labelled, never re-measured** (non-goal), and every step is guarded by the capability conformance suite so no C1–C88 capability is silently lost (R77).

---

## 15. Why this is elegant

- **Five abstractions carry eighty-eight requirements.** §14.1's merges hold: no MUST→SHOULD demotion, every verification clause survives; R17 stays the policy catalog (the preservation proof); global suppression stays distinct from per-run scoping; K5/K6/K9/K10 remain design invariants, not mergeable requirements.
- **Nothing hand-maintained that can drift.** Axes, hyperparameters, constraints, objectives, and capabilities are definitions; everything else is regenerated. P4, P11, P14, R63 die together.
- **The hard properties are structural, not disciplinary.** Coverage survives policy substitution because the *wrapper* reports it. Claims are governed because they are *queries*, not assertions. Failures are never re-paid because voids are *globally suppressive*. Acceleration is attributable because it is *run-scoped*. You cannot forget these; the architecture does them.
- **It evolves by registration.** A new axis, knob, policy, stage, objective, or constraint is an addition, not an edit — which is precisely what a framework whose ontology is "a design abstraction, not a law" must be able to do.

This specification discharges TODO43 §12, resolves Q1–Q16, integrates Rev 3 as accepted scope, and satisfies every MUST with a named, verifiable mechanism — leaving implementation, decomposition, and rollout sequencing to follow.
