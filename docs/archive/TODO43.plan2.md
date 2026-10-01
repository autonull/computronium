The next revision of `TODO43.plan.md` should **stop adding architectural pieces** and instead force the existing pieces to become one executable system. The plan already has most of the right abstractions; the remaining danger is declaring them complete while they are still only adjacent implementations.

The most important correction is that the current repository is slightly behind its own 2026-09-30 status log. In particular, the stage protocol is defined but `PipelineRunner` does not actually dispatch to `Stage.run()`, the policy interface still receives an empty candidate list, and the allocator hook is still a no-op. ([GitHub][1])

## 1. First: change the status model of TODO43

I would **not undo WP8–WP13**. Instead, add a short “integration reality correction” immediately before the remaining-work section:

> WP8–WP13 established the kernel primitives and most required functionality, but several completion bullets were satisfied structurally rather than end-to-end. These are not architectural reversions. The remaining work closes runtime integration seams and verifies that the individual components actually compose into the unified kernel described by abc3 §5.

Then explicitly reclassify:

| Area                       | Status to record                                                         |
| -------------------------- | ------------------------------------------------------------------------ |
| Axis/registry union        | Complete                                                                 |
| Legality                   | Complete                                                                 |
| Store/artifacts            | Complete, subject to atomicity clarification                             |
| Stage definitions          | **Complete definition; runtime dispatch incomplete**                     |
| Policy catalog             | **Complete catalog; canonical search-space interface incomplete**        |
| Optuna integration         | **Sampler machinery present; genuine AXES-driven suggestion incomplete** |
| Allocator                  | **Implementation exists; pipeline integration incomplete**               |
| Continuous round loop      | **Incomplete**                                                           |
| Learning/store integration | Mostly complete                                                          |
| Claim integrity            | Helper complete; **all callers not yet normalized**                      |
| Failure isolation          | **Incomplete end-to-end**                                                |
| E1                         | Complete                                                                 |
| E2                         | Complete as a mechanism validation                                       |
| E3/E4                      | Incomplete                                                               |
| Legacy deletion            | Incomplete                                                               |
| Full C1–C88 proof          | Incomplete                                                               |

That wording is important because the current plan says “ModelBased policy completed” and “EvidenceDrivenAllocator integration hook” even though the corresponding runtime paths still contain stubs. ([GitHub][2])

---

# 2. Add a new WP14: Canonical Search Space and Proposal Contract

This should be the **highest-priority correction**.

The abc3 architecture actually specifies:

```text
Policy.propose(SearchContext) -> Iterator[Proposal]
```

with the wrapper applying legality and novelty uniformly. The implementation instead uses:

```text
propose(candidates, records, budget, cost_model)
```

and `PipelineRunner` currently calls it with `candidates=[]`. ([GitHub][3])

That is the seam preventing the three systems from really becoming one.

### Make these first-class kernel abstractions

```text
SearchSpace
ProposalContext
Proposal
AllocationPlan
AllocationDecision
```

I would make the conceptual flow:

```text
RunSpec
  │
  ├── SpaceRef / AXES snapshot
  ├── CONSTRAINTS
  ├── OBJECTIVES
  ├── task set
  └── schedule policy
        │
        ▼
    SearchSpace
        │
        ▼
   ProposalContext
        │
   ┌────┼─────────────────────────────┐
   │    │              │              │
Random Optuna       Evolution     Synthesis
   │    │              │              │
   └────┼──────────────┴──────────────┘
        ▼
     Proposal
        │
        ▼
   Kernel wrapper
        │
   legality
   novelty
   provenance
        │
        ▼
 Coordinate + Schedule
```

### Critical rule

**No policy may require a pre-enumerated candidate list.**

A grid policy can enumerate.

A random policy can sample.

Optuna can construct distributions.

Evolution can mutate coordinates.

Synthesis can construct coordinates from reasoning.

They all consume the **same `SearchSpace`**.

A candidate list should become an optional optimization or seed mechanism, not the fundamental API.

### Required tests

Add a lock that instantiates every policy with:

```text
AXES snapshot
CONSTRAINTS
one task
Budget
no candidate list
empty store
```

and proves that it can produce legal proposals.

That single test will prevent the architecture from silently reverting to “some external subsystem generates candidates and Optuna chooses among them.”

---

# 3. Add WP15: Make the Stage abstraction real

This is the biggest implementation correction.

The plan says every stage implements:

```python
await stage.run(ctx) -> Fragment
```

and the pipeline wrapper invokes those implementations. That is the architectural contract in abc3. ([GitHub][3])

The current implementation instead loops through `StageSpec`s and executes generic candidate batches. There is a `Stage` protocol and `StageContext`, but `PipelineRunner` never calls `stage.run()`. ([GitHub][1])

### Change the architecture to

```text
Pipeline
  │
  ├── S1 FrameStage
  ├── S2 SpaceStage
  ├── S3 ScheduleStage
  ├── S4 GateStage
  ├── S5 ComposeStage
  ├── S6 TrainStage
  ├── S7 MeasureStage
  ├── S8 RecordStage
  ├── S9 AttributeStage
  ├── S10 DecideStage
  └── S11 ReportStage
```

with:

```text
STAGES: Registry[Stage]
```

or the equivalent existing registry structure.

`StageSpec` should describe the stage; the registered `Stage` object should execute it.

### Do not make every stage an evaluator

This is an important correction to the current generic runner.

These are fundamentally different:

```text
S1 Frame      planning
S2 Space      planning / validation
S3 Schedule   planning / allocation preparation
S4 Gate       validation
S5 Compose    construction
S6 Train      execution
S7 Measure    execution / observation
S8 Record     persistence
S9 Attribute  analysis
S10 Decide    control
S11 Report    presentation
```

The current `_run_stage()` treats every stage as essentially:

```text
generate candidates
→ execute candidates
→ persist records
```

That is not the intended experiment kernel.

### Gate semantics must move with this correction

Currently `_check_gate()` expects records and can stop the pipeline because a stage has no records. That is inappropriate for stages such as Frame, Space, Gate, Attribute, and Report.

Instead:

```text
Fragment
  └── transition = PASS | FAIL | QUARANTINE | SKIP | CONTINUE
```

or an equivalent typed stage result.

The wrapper should evaluate **stage transition semantics**, not “did this stage produce at least one evaluation record?”

---

# 4. Add WP16: Make Continuous/Campaign a real round loop

This is the central completion step for the third leg of the unification.

The design says allocation is separate from proposal and gives the reference promotion loop explicitly. ([GitHub][3])

But the actual runner currently executes the S1–S11 list once. It has a comment about “between rounds,” yet there is no actual repeat loop; `_run_allocator()` is only a logging hook. ([GitHub][4])

### Make the control flow explicit

I recommend:

```text
S1 Frame
S2 Space

┌──────────────────────────────────────────────┐
│                 ROUND N                      │
│                                              │
│ S3 Schedule                                  │
│ S4 Gate                                      │
│ S5 Compose                                   │
│ S6 Train                                     │
│ S7 Measure                                   │
│ S8 Record                                    │
│ S9 Attribute                                 │
│ S10 Decide ────────┐                         │
└────────────────────┼─────────────────────────┘
                     │
          CONTINUE ──┘
                     │
          COMPLETE ───────► S11 Report
          PAUSE    ───────► persisted paused run
          STOP     ───────► terminal run
```

I would make `S10 Decide` return something like:

```text
Decision:
    CONTINUE
    COMPLETE
    PAUSE
    STOP
```

plus:

```text
new_proposals
promotions
abandonments
replications
rationale
budget impact
```

Then **continuous execution is simply repeated rounds of the kernel**.

That is the point at which “Campaign” stops being a separate architecture.

---

# 5. Make Allocation genuinely independent of Proposal

The abc3 design explicitly says:

> Allocation is a separate Protocol from proposal, so any policy pairs with any allocator. ([GitHub][3])

Preserve that distinction rigorously.

### Policy answers

> What systems should we investigate next?

### Allocator answers

> Given what we have already investigated, where should additional budget go?

So:

```text
Policy
    NEW coordinate

Allocator
    EXISTING coordinate
       ├── promote fidelity
       ├── add replication
       ├── abandon
       └── defer
```

I would prohibit an `AllocationPolicy` from inventing new coordinates.

That gives you a very clean composition:

```text
TPE + successive promotion
Random + successive promotion
Evolution + successive promotion
Synthesis + successive promotion
TrainerDriven + successive promotion
```

That is exactly what the original unified design promises.

### Add a key invariant

```text
cell_key unchanged by allocation
measurement_key changes when schedule/seed changes
```

That gives promotion a clean semantic identity.

---

# 6. Fix Optuna properly rather than merely wrapping it

This deserves its own WP17.

The current `ModelBasedPolicy` has the Optuna samplers, but it still enters through a candidate list, calls `study.ask()`, and can receive an empty `trial.params`. Its reconstruction uses `distributions={}`. ([GitHub][5])

That means the implementation does not yet provide the thing the architecture actually needs:

> **Optuna sampling over the canonical `AXES` search space.**

### Replace the current mechanism with

```text
AxisSpec
   ↓
OptunaDistributionAdapter
   ↓
Trial.suggest_*
   ↓
Coordinate
```

For each active axis:

```text
STRUCTURAL
  → categorical suggestion

CONTINUOUS + LINEAR
  → suggest_float(...)

CONTINUOUS + LOG
  → suggest_float(..., log=True)

INTEGER
  → suggest_int(...)

CATEGORICAL
  → suggest_categorical(...)
```

Conditional parameters should be activated from the same `availability` expression used by legality/schema—not an Optuna-specific copy.

### Resume semantics

When rebuilding an Optuna study from records:

```text
Record
  ↓
FrozenTrial
  ├── exact params
  ├── exact distributions
  ├── objective values
  ├── state COMPLETE/FAIL/PRUNED
  ├── intermediate values
  └── record_id / measurement_key metadata
```

Then:

```text
study.add_trial(...)
```

is merely reconstruction of policy state.

There remains **no Optuna database**.

### Important correction

Unknown objectives should not silently become maximize. The current resolver still has a “fallback: assume maximize” path, and `ModelBasedPolicy` also defaults directions to maximize. ([GitHub][5])

The kernel should instead say:

```text
unknown objective id
    → RunSpec validation error
```

That is consistent with the registry-first architecture.

---

# 7. Put `RunSpec` back at the center

This is a subtle but important design correction.

abc3 defines a typed, serializable `RunSpec` as the durable description of a run. ([GitHub][3])

The actual `PipelineConfig` currently carries:

```python
run_spec: dict[str, Any]
```

which means the most important architectural object is still effectively an untyped dictionary at the execution boundary. ([GitHub][4])

I would make:

```text
RunSpec
```

the canonical public kernel object.

Then:

```text
CLI/Profile
      ↓
RunSpec
      ↓
Pipeline
      ↓
StageContext
```

`PipelineConfig` should either disappear or become a compiled/internal representation derived mechanically from `RunSpec`.

This also eliminates a lot of the loose dictionary plumbing currently visible in the runner.

---

# 8. Fix S3 experimental design rather than merely labeling proposals

This is an important scientific correction.

The current S3 implementation takes whatever proposals the policy produces, assigns them `exploration`, `calibration`, or `test`, and encodes the origin partly into `budget_id`. It then marks a subset as “contrast.” ([GitHub][4])

But **labeling a random subset “contrast” is not actually generating a matched contrast design**.

The plan says the contrast quota should make attribution identifiable by construction. ([GitHub][2])

### Replace this with an actual `ContrastDesign`

For example:

```text
ContrastDesign
    factors: selected AXES
    design: OFAT | fractional_factorial
    baseline_coordinate
    contrast_coordinates
    contrast_id
```

Then S3 actually constructs:

```text
baseline
  ├── + factor A
  ├── + factor B
  ├── + factor C
  └── ...
```

or the appropriate fractional-factorial design.

Every member gets:

```text
contrast_id
factor_assignments
matched_group
```

The resulting data can actually support S9 attribution.

This is a much stronger implementation of the scientific-design goal than the current percentage-based marking.

---

# 9. Make `data_origin` first-class

Do not encode:

```text
budget_id = "something:exploration:contrast"
```

as the current S3 code does. ([GitHub][4])

`budget_id` should mean what it says.

Add a first-class field such as:

```text
Provenance.data_origin
```

or a dedicated immutable selection/proposal provenance structure:

```text
DataOrigin =
    EXPLORATION
    CALIBRATION
    TEST
    CONTROL
    CONTRAST
```

I would distinguish:

```text
data_origin
```

from:

```text
design_role / contrast_id
```

because “exploration” and “contrast” answer different questions.

Most importantly:

**data origin should not accidentally change measurement identity.**

The measurement is the experimental fact; origin records why/how that measurement entered the evidence set.

---

# 10. Centralize claim eligibility

The plan correctly added `claim_eligible_by_achieved_seeds`, but `PipelineRunner._is_claim_eligible()` still checks:

```text
schedule.n_seeds >= 5
```

directly. ([GitHub][4])

That reintroduces exactly the bug WP10 was intended to remove.

There should be exactly one authoritative implementation:

```text
claim_eligible(records, run_policy, protocol) -> ClaimEligibility
```

The pipeline, report surface, SQL prefilter, and tests should all consume it.

The SQL prefilter can remain only a performance optimization.

The rule should be:

```text
planned replication count
    ≠
achieved replication count
```

and the latter governs claims.

---

# 11. Fix failure isolation at the backend/pipeline boundary

This is another place where the implementation currently overstates completion.

The code catches an `ExceptionGroup`, but then classifies the batch and re-raises the exception, which means it is not actually isolating independent failures while allowing successful siblings to continue. ([GitHub][4])

The actual contract should be:

```text
submit batch
    ├── cell A → Record
    ├── cell B → FailureEvent
    ├── cell C → Record
    └── cell D → Record
```

not:

```text
one exception
    ↓
classify everyone
    ↓
raise entire batch
```

### Make backend results per-item

Something like:

```text
EvaluationResult =
    Success(record)
  | Failure(failure_event)
```

Then the pipeline can guarantee:

```text
one cell failing
    does not destroy its siblings
```

Fatal process/store errors remain exceptional and run-level.

This also aligns much better with the failure taxonomy in abc3. ([GitHub][3])

---

# 12. Fix runtime provenance

The current pipeline constructs provenance containing hardcoded values such as:

```text
python = "3.14"
platform = "linux"
```

rather than capturing the actual runtime environment. ([GitHub][4])

That should become a kernel-owned `EnvironmentSnapshot`:

```text
python version
OS/platform
PyTorch version
CUDA version
GPU/device
dtype
worker configuration
relevant dependency versions
code SHA
```

and the snapshot should be generated once per run.

This should be immutable and referenced by records.

It would also make R11/R28 much more meaningful.

---

# 13. Add an explicit state machine for the Run

For continuous operation, pause/resume/steer and safe shutdown become much cleaner if run state is formalized.

I would define:

```text
RunState =
    CREATED
    RUNNING
    PAUSING
    PAUSED
    COMPLETING
    COMPLETED
    STOPPING
    STOPPED
    FAILED
```

and typed transitions:

```text
RUNNING → PAUSED
RUNNING → STOPPING
RUNNING → COMPLETING
PAUSED  → RUNNING
```

Operator intents then become requests for transitions, not arbitrary mutations of internal dictionaries.

This makes the existing `RunController` considerably more coherent with the experiment state machine. The current operations surface already persists operator intents, so this is a natural completion rather than a new subsystem. ([GitHub][2])

---

# 14. Add a policy-state provenance contract

For reproducibility, `policy + seed` isn't quite sufficient for learned/model-based policies.

A record should be attributable to:

```text
policy_id
policy_version
policy_seed
policy_state_digest
training_record_cutoff
training_record_ids / query signature
```

For example, a GP policy can say:

```text
I selected this proposal using records
[R123, R127, R130, ...]
under policy-state hash H.
```

The exact record IDs do not necessarily have to be embedded in every record if that is expensive; a content-addressed query snapshot/digest is sufficient.

This would make:

```text
replay
resume
audit
cross-run comparison
```

much more rigorous.

---

# 15. Clarify the record/artifact atomicity claim

There is a small but real semantic overstatement in the store design.

For an inline DuckDB BLOB:

```text
record + artifact
```

really can be atomic.

For an external artifact:

```text
upload bytes externally
+
commit manifest in DuckDB
```

the external upload itself cannot participate in the DuckDB transaction.

So the plan should say:

> **Atomic logical registration; external artifact bytes require orphan detection/garbage collection.**

A robust sequence is:

```text
1. content-address artifact
2. stage/upload artifact
3. verify checksum
4. transactionally register manifest + record
5. GC unreferenced staged artifacts
```

rather than claiming “no partial state” for the entire external side effect.

---

# 16. Finish the vector-search decision

The plan intentionally left embedding production as an open K1 decision. ([GitHub][2])

I would close that before final DoD rather than carrying it indefinitely.

For the kernel:

```text
384-d deterministic feature-hash embedding
```

gives you:

* zero network dependency
* reproducibility
* deterministic versioning
* optional vector acceleration

Then allow:

```text
semantic embedder plugin
```

as an optional capability.

That is particularly useful because AutoScientist/literature reasoning can use the same `vector_index` without making the scientific kernel depend on a model download or external service.

---

# 17. Make the final legacy deletion much stricter

WP12 should not be:

> “delete old directories.”

It should be:

```text
legacy capability
      ↓
new kernel capability
      ↓
specific conformance test
      ↓
end-to-end use
      ↓
delete legacy code
```

The existing plan already has the right basic principle—port then delete, with an import-graph lock. ([GitHub][2])

I would strengthen it with a **capability migration table**:

| Legacy surface           | New home                             | Verification               | Delete condition        |
| ------------------------ | ------------------------------------ | -------------------------- | ----------------------- |
| `autoscientist.proposer` | `Synthesis` / `Policy`               | proposal equivalence       | kernel test passes      |
| `hyperopt._finder`       | `ModelBasedPolicy`                   | Optuna integration         | no legacy imports       |
| `core.campaign`          | Pipeline + Allocator + Store         | multi-round test           | import graph clean      |
| `autoscientist.reasoner` | `ReasoningStore` + hypothesis source | provenance test            | records persisted       |
| daemon                   | `surface.service`                    | pause/resume test          | service test passes     |
| pareto                   | claims/report                        | multiobjective report test | legacy report removed   |
| robustness               | S7                                   | measurement test           | legacy harness removed  |
| NAS/Lightning            | `TrainerDriven`                      | adapter conformance        | legacy importer removed |

This gives WP12 a much stronger completion criterion.

---

# 18. Add the tests that actually prove the three-way unification

This is the most important addition I would make to WP13.

The existing E1/E2/E3/E4 work proves individual properties. It does **not by itself prove that AutoScientist, Optuna, and Continuous/Campaign have become different policies over one kernel.**

Add a dedicated **Unified-Kernel Acceptance Suite**.

### U1 — AutoScientist/Synthesis

```text
question
 → question_first()
 → RunSpec
 → Synthesis policy
 → unified SearchSpace
 → Pipeline
 → RecordStore
```

### U2 — Optuna

Same experiment framing:

```text
RunSpec
 → same SearchSpace
 → TPE
 → Pipeline
 → same Record schema/store
```

### U3 — Continuous

```text
RunSpec
 → same SearchSpace
 → Random/TPE/Evolution
 → Allocator
 → multi-round pipeline
 → pause
 → resume
 → report
```

### U4 — policy interchangeability

This is the strongest test.

Run:

```text
Round 1: StratifiedRandom
Round 2: TPE
Round 3: Evolution
Round 4: Synthesis
```

over the **same RunSpec / Space / Store**, without adapters or special-case state translation.

The only thing that changes should be the policy.

That demonstrates the architectural claim far more convincingly than individual unit tests.

### U5 — cross-policy evidence reuse

Run one policy, then initialize another from the existing records:

```text
Random
    ↓
RecordStore
    ↓
TPE
    ↓
RecordStore
    ↓
Evolution
```

and prove:

```text
no separate DB
no special migration
same measurement identity
same legality rules
same objective definitions
same claim machinery
```

That is the experiment-kernel equivalent of a real integration test.

---

# 19. Strengthen E2/E3/E4 semantics

The newly completed E2 result is useful, but I would change its interpretation in the plan.

The current log reports the GP-vs-random synthetic result as a successful result and notes that naïve learners lose. ([GitHub][2])

I would explicitly state:

> E2 validates that the acquisition machinery can recover a known synthetic signal. It is not evidence that GP/Optuna is generally superior to random search.

Then E3 should test:

```text
known ground-truth axis effects
      ↓
DOE-seeded records
      ↓
S9 attribution
      ↓
estimated effect
      ↓
known effect
```

including:

```text
bias
CI coverage
false discovery / false attribution
replication sensitivity
```

And E4 should test:

```text
learned evidence
    ↓
new task / topology / substrate
    ↓
transfer
```

with explicit held-out boundaries.

This separates:

```text
algorithmic efficacy
scientific attribution
generalization
```

rather than letting one synthetic benchmark stand in for all three.

---

# 20. Add one more binding invariant: “the kernel owns semantics; plugins own decisions”

I would add this directly to the plan's architectural invariants.

### Kernel-owned

```text
RunSpec
SearchSpace
AXES
CONSTRAINTS
OBJECTIVES
Schedule
measurement identity
legality
execution lifecycle
budget
artifact semantics
provenance
persistence
failure taxonomy
claims
reproducibility
round control
```

### Plugin-owned

```text
which coordinate to propose
which evidence to model
which hypothesis to generate
which candidates to prioritize
which acquisition function to use
which evolutionary operator to use
```

### Never plugin-owned

```text
whether a coordinate is legal
whether a measurement is duplicate
whether a claim is scientifically eligible
whether provenance is recorded
whether failures are isolated
whether store writes are atomic
```

That principle neatly prevents future re-fragmentation.

---

# 21. Suggested sequencing for the next revision

I would replace the current loose “remaining WPs” ordering with this:

```text
WP14  Canonical SearchSpace + Proposal API
  │
  ▼
WP15  Real Stage dispatch + typed RunSpec
  │
  ▼
WP16  Round controller + AllocationPolicy integration
  │
  ├───────────────┐
  ▼               ▼
WP17 Optuna       WP18 Evidence/design integrity
  │               │
  └───────┬───────┘
          ▼
WP19 Failure isolation + runtime provenance
          │
          ▼
WP20 Unified-kernel acceptance suite
          │
          ├── U1 AutoScientist/Synthesis
          ├── U2 Optuna
          ├── U3 Continuous
          ├── U4 policy interchange
          └── U5 evidence reuse
          │
          ▼
WP21 Legacy port/delete
          │
          ▼
WP22 E3/E4 + full C1–C88 audit
          │
          ▼
       TODO43 DONE
```

The important dependency is that **WP20 comes before WP21**. You want proof that the new kernel can really replace the old pillars before deleting them.

---

# 22. A few small plan corrections worth making now

### Schema version

The plan correctly says schema changes fail closed, but the `task_id` addition changed the physical DuckDB `STRUCT`. The plan/log should make the versioning rule explicit: **physical schema changes bump `schema_version`**, even when migration is forbidden. The current code records `SUPPORTED_SCHEMA_VERSIONS = {1}` while the schedule structure has changed. ([GitHub][2])

Since there are no external users yet, the clean solution is simply to declare the next physical schema version and rebuild local stores.

### Temporary complexity `noqa`

The current plan admits the newly ported `compose.py` functions have temporary complexity suppressions and should eventually be refactored or disappear with WP12. Keep that as an explicit WP12 cleanup acceptance criterion. ([GitHub][2])

### Prior single source

The latest work has already improved the prior path considerably. Continue to make the final WP12 criterion:

```text
PRIORS registry
      ↓
only source of prior values
```

with no fallback tables or legacy JSON.

### Documentation generation

The generated registry/config documentation should become a **projection of the actual registries**, not a parallel specification. The existing WP11 direction is correct. ([GitHub][2])

---

# What I would consider “TODO43 truly complete”

I would tighten the final definition to this:

```text
1. There is exactly one RunSpec model.

2. There is exactly one SearchSpace model derived from AXES + task +
   constraints.

3. Every proposal policy consumes that SearchSpace and emits the same
   Proposal type.

4. Every allocation policy consumes the same evidence and emits the same
   AllocationPlan type.

5. Every run executes the same S1–S11 stage graph.

6. S3–S10 can repeat for arbitrarily many rounds.

7. AutoScientist/Synthesis, Optuna, Evolution, Random, and TrainerDriven
   differ only in proposal policy, not lifecycle or evidence semantics.

8. Continuous/Campaign differs only in budget, allocator, service/control
   behavior, not in experiment representation.

9. There is one RecordStore and one measurement identity.

10. No policy can bypass legality, provenance, novelty, failure handling,
    budget accounting, or atomic persistence.

11. A run can pause, resume, replay, and continue with a different policy.

12. Claim eligibility is computed exclusively from achieved evidence.

13. E3 demonstrates known-effect recovery; E4 demonstrates held-out transfer.

14. Every C1–C88 capability either has real conformance evidence or an
    explicit retirement record.

15. The legacy pillars are physically gone and the import graph proves it.

16. The unified acceptance suite passes for all three historical modes.
```

That final list is substantially stronger than the current DoD because it tests the **architectural claim itself**, not just whether the individual modules exist.

The core insight is that the remaining work is now mostly **integration algebra**:

```text
AXES
  ×
RunSpec
  ×
SearchSpace
  ×
Policy
  ×
Allocator
  ×
Stage graph
  ×
RecordStore
```

must behave as one closed system.

Once that is true, the old names become implementation history:

```text
AutoScientist = Synthesis/reasoning policy
Optuna        = ModelBased policy
Campaign      = repeated kernel rounds + AllocationPolicy + service surface
```

That is the point at which I would regard the original unification goal as genuinely achieved rather than merely approximated. ([GitHub][3])

[1]: https://github.com/autonull/computronium/blob/main/computronium/experiment/execution/stage.py "computronium/computronium/experiment/execution/stage.py at main · autonull/computronium · GitHub"
[2]: https://github.com/autonull/computronium/blob/main/TODO43.plan.md "computronium/TODO43.plan.md at main · autonull/computronium · GitHub"
[3]: https://github.com/autonull/computronium/blob/main/TODO43.abc3.md "computronium/TODO43.abc3.md at main · autonull/computronium · GitHub"
[4]: https://github.com/autonull/computronium/blob/main/computronium/experiment/execution/pipeline.py "computronium/computronium/experiment/execution/pipeline.py at main · autonull/computronium · GitHub"
[5]: https://github.com/autonull/computronium/blob/main/computronium/experiment/execution/policy.py "computronium/computronium/experiment/execution/policy.py at main · autonull/computronium · GitHub"
