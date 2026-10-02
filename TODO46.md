# TODO46.md — Close the Gaps, Then Make It Demonstrably Work

**Supersedes:** TODO45.md (marked superseded; its verified content is carried into
§5 here). **Requirements source:** `docs/archive/TODO43.md` (R1–R88, K1–K10),
design source `docs/archive/TODO43.abc3.md`, plans `TODO43.plan.md` /
`TODO43.plan3.md`. **Binding:** AGENTS.md in full. **Binding:** this file.

**Goal:** a system an external researcher can install and run, where one command
produces evidence they can check. Not a clean test suite, not a type-clean
tree — a *working* system whose reported numbers come from real training.

**Not the goal:** matching TODO43's 88 requirements. Loosely satisfy the slice
named in §3 and **do not claim the rest**. An unclaimed requirement is fine; a
falsely-marked-complete one is what produced this plan.

---

## 0. Where things stand

### 0.1 What TODO45 actually achieved

- **Test cost cut ~10×.** A `demo` marker (stamped by filename in
  `tests/conftest.py`) removed ~2.75 h of declared demo budgets from the default
  gate; `-n 4` added to `addopts`; a demo's seed-0 arm was being trained twice
  and no longer is. Sharded verification is ~7 min wall / ~48 CPU-min.
- **Ground truth established by sharded runs, not by a full suite** (which
  hard-killed twice at test 873/3699).
- **R1.3 withdrawn and undone**: `docs/archive/` was deleted on the plan's
  say-so and restored on the operator's instruction. It is the only remaining
  record of the deleted `tests/graph/` suite. **Destruction requires named
  sign-off; exclusion, marking and deferral do not.**
- **R1.5 void**: those run-records are demo-regenerated with a new
  `provenance.git_commit`, not formatting churn.
- **`comp` has a real help tree**; pyright excludes generated protobuf
  (`p2p` 61 → 23 errors).
- **U1–U5 acceptance passes: 8 tests, 11.22 s.** This sounds better than it is;
  see §2.

### 0.2 The one-sentence diagnosis

**The kernel is a scaffold with real orchestration, and three work packages
marked ✅ that have no mechanism behind them.** The pieces needed for a working
system mostly exist; they were never connected, and completion was awarded for
connection.

---

## 1. Confirmed defects

Every item below is verified in code, with evidence. `file:line` is the anchor.
**D1–D6 and D10–D26 are fixed.** D15 was found and fixed in §8 session 5, D16
and D17 in session 6, D18 and D19 in session 7, D20–D22 in session 8, D23 in
session 9, and D24–D26 in session 11. **D7 and D8 are fixed by §3.5 and §4;
D9 (the lab fold) remains**, and D14's fix is consumed by §3.3.

### D1 — The evaluator is a placeholder (the critical path) — FIXED, §8 session 3

`computronium/experiment/execution/backends.py:222`

```python
def _evaluate_single(self, coordinate, schedule, provenance, params) -> Record:
    """This is a placeholder - actual evaluation integrates with the
    ontology/system stack. For now, returns a minimal valid Record."""
    payload = {"status": "evaluated", "walltime_s": ..., "seed": ...,
               "fidelity": ..., "epochs_completed": ...}
    status = Status(gate_verdict=GateVerdict.PENDING, maturity=Maturity.L0, ...)
```

`MultiprocessBackend._evaluate_single_process` (`:393`) is **the same stub**.
No training runs. No objective is measured. No accuracy exists anywhere in the
kernel. Records are schema-valid and scientifically empty.

### D2 — The space is hardcoded, and it is hardcoded to MNIST

`computronium/experiment/execution/search_space.py:174-206`

```python
for substrate in substrate_primitives[:3]:      # arbitrary truncation
    for geometry  in geometry_primitives[:3]:
        for plasticity in plasticity_primitives[:2]:
            ...
            params = _build_default_params(...)
            schedule = Schedule(fidelity="L0", seed=42, n_seeds=1, epochs=1,
                                batch_limit=0, task_id="default", ...)
```

`_build_default_params` (`:241`) hardcodes
`{"input_dim": 784, "output_dim": 10, "hidden_dim": 64, ...}` at **seven
sites** (`:255, 297, 307, 314, 321, 327, 333`).

Consequences: hyperparameters are *constants* (TODO43 **P2**, **R2** — "learning
rate MUST be expressible as a searched coordinate", unfixed); the task is
literally `"default"` so a run's task never reaches the space; and the geometry
is MNIST-shaped, so a `digits` run would build the wrong network. This is
TODO43 **P1** and **P4** restated in new code — the hand-maintained
per-combination table that abc3 §3.2 says becomes structurally impossible.

### D3 — The Optuna samplers do not search

`computronium/experiment/execution/policy.py:517`

```python
trial = study.ask()
suggested_params = trial.params
if not suggested_params:
    idx = trial.number % len(affordable)   # a positional pick, not a sample
```

The study is created with **no distributions**, so `trial.params` is always
empty and every proposal falls through to indexing a list. And:

- `study.tell()` **appears nowhere in the codebase.**
- `ModelBasedPolicy` has **no `observe()` method.**
- `suggest_float` / `suggest_categorical` / `suggest_int` **appear nowhere** in
  the codebase (only in a stale `.pyc` from a deleted test).

So TPE and NSGA-II are constructed, asked, and never told anything. They cannot
learn even in principle, while `README.md:248` advertises "Surrogate-guided
search (Optuna TPE, NSGA-II for multi-objective)".

### D4 — There is no `RunSpec`

`computronium/experiment/surface/cli.py:261-263` does `json.load()` on a file
and passes the resulting `dict` straight to `PipelineConfig.run_spec`. No
validation, no version, no schema. The acceptance suite builds its "RunSpec"
as a literal dict (`tests/acceptance/test_unified_kernel.py:52-75`). This is
abc3 §3.8 and TODO43 **R41** unimplemented.

### D5 — The compose bridge exists and has zero callers

`computronium/experiment/execution/compose.py:474`

```python
def compose_cell_system(*, dynamics, credit, update, geometry: dict,
                        input_dim, output_dim, lr=1e-3, substrate="digital",
                        param_budget=0) -> System:
    """Compose a full grid cell (dynamics × credit × update × topology).
    ... all built from the single-source config classmethods and registries
    — no preset tables."""
```

`grep -rn compose_cell_system computronium/` returns **only its own definition
and its `__all__` entry**. The axis-name → config-class resolution the whole
critical path needs **is already written, unwired, and takes `lr` as a
parameter.** This is why D1 is smaller than it looks.

Gaps in it, all of which land in §3.0.1:

- It covers five axes, not six — **no `plasticity`**, though abc3 §3.4 makes
  plasticity first-class (Q7) and it is half the research program.
- **Three different mechanisms decide "what does this configuration need", and
  they disagree** (`:502`, `:508`, `:516-529`):
  1. `inspect.signature(update_factory).parameters` gates a `step_size` kwarg —
     reflection on the *config factory* rather than on the primitive, and
     covering exactly one hyperparameter.
  2. `get_dynamics_step_size(dynamics) or 0.1` — a prior with a bare `0.1`
     fallback, i.e. a magic number in a fallback path.
  3. `if dcfg.dynamics_type == "energy_minimization" and ccfg.credit_type ==
     "thermodynamic_contrast": ccfg = …(beta=dcfg.beta)` — **per-combination
     coupling hardcoded in string-matching branches.** That is TODO43 P4 again,
     and abc3 §3.2 says it must be an availability predicate in the spec. A
     third pairing that needs the same relationship is a new branch, not a
     derivation.
- **`lr` is a parameter the caller should not have to supply, and it is a
  misnomer.** In this ontology there is no learning rate reaching the update —
  the demos use `ParameterUpdateConfig.euclidean(step_size=…)` and the historical
  ruler-lr table was rerouted into `PRIORS` — so this is a step size named `lr`.
  Worse, the failure is silent: if the selected update ignores `step_size`, the
  supplied value is discarded with no signal, and the effective value is not
  recorded (R6). Availability is a property of the selected primitives, so it
  must be derived from the coordinate, never asserted by the caller.

### D6 — Several stages are coverage shells

`execution/stages_impl.py`: S5 `:464` "would call `compose_joint_system`"; S6
`:476` "training is executed by the pipeline wrapper"; S7 `:520` "would resolve
objectives" (passes proposals through); S9 `:570` hardcodes
`{"axes": {}, "confidence": 0.0}`; S11 `:661` "would delegate to
`surface.report`" (returns a dict of counts). S5/S6/S7 duplicate the abandoned
compose path, which now also has a real implementation in `compose.py`.

**Owner: §3.1.** Leaving this unassigned is how two compose paths end up alive
at once. When §3.1 lands the real evaluator, S5/S6 must **stop composing** and
become coverage reporters of what the backend did — they duplicate
`compose.py:474` today. S7's objective resolution is §3.4; S9's attribution and
S11's report delegation are §3.5. A stage that has nothing to say emits an
explicit empty fragment (abc3 §5.1, R39) rather than a plausible-looking
placeholder with `confidence: 0.0`.

### D7 — The report renders statistics, not claims — FIXED, §8 session 11

`experiment/surface/report.py:393` `generate_run_report` emits record counts,
maturity and gate-verdict distributions, coordinate coverage and a Pareto
front. It renders **no claims**. `evidence/claims.py` has eligibility
*predicates* and no rendering. **`limitation` does not appear anywhere in
`computronium/experiment/`** — zero grep hits — so the Claim/Evidence/Limitation
triple has no data model for its third element (TODO43 **R85** unmet).

### D8 — README overclaims, in two specific places

- `README.md:318` cites E3/E4 as **Level 5** evidence with effect sizes
  (d=−1.499, p=0.00106). `TODO43.plan3.md:144-145` states these were measured
  on **`SyntheticGroundTruth`** — a constructed quadratic surface. That is
  evidence the *machinery* detects an effect it was handed. It is not evidence
  the system learns. **Fix in this plan (§4).**
- `README.md:253-261` presents U1–U5 as kernel guarantees at Level 4. They pass
  over a stub evaluator. The *orchestration* guarantees are real; the
  *measurement* they imply is not. **Restate precisely (§4).**

### D9 — `computronium_lab` overlaps the kernel, and folds in cleanly

`computronium/` imports `computronium_lab` **0** times;
`packages/computronium-lab/` imports `computronium.experiment` **3** times.
Dependency already runs lab → kernel, so the kernel **cannot** call
`Lab.train` without a cycle.

The lab contributes: real seeded training (`lab.py:311` → `train_with_certificates`),
a CEEC ledger, and `SynthesisResult`/`ParetoOption` synthesis. The kernel
contributes orchestration, store, legality, claims.

**Discipline (operator):** fold the lab in **while** wiring the gaps, not after.
One evaluation implementation, owned by the kernel; the lab becomes a thin
facade over it. Specifically:

- The kernel owns evaluation. `compose_cell_system` (§D5) plus a task-shaped
  loader plus `SystemTrainer` **is** the evaluator; the lab's training path
  becomes a caller of it, not a second implementation.
- **Do not** have the kernel import the lab. The direction stays lab → kernel.
- The lab's *priors* must not become measurements: `Lab.explore` returns a
  frontier of **predicted** metrics from a static `CATALOG` (`cand.pareto`) and
  `synthesize` ranks by a viability model. That is TODO43 **P4** in new
  clothing. The campaign trains; it never reads the catalog.
- `Lab` is unmentioned in `README.md` (0 hits) despite the canonical rewrite.
  Whatever survives the fold is documented; whatever does not is retired with a
  recorded reason (R78).

### D10 — Four directories are outside the gate

`pyproject.toml:174` `testpaths` = unit, property, primitives, algorithms,
acceleration. **Excluded: `tests/acceptance`, `tests/integration`, `tests/ceec`,
`tests/platform`.** A bare `pytest` therefore has never run U1–U5 — the only
file that proves the kernel works. CI reaches them only because CI names
directories explicitly. A fast lane that silently omits the project's central
claim is a false-negative generator. **Decision: add `tests/acceptance`**;
`tests/ceec` and `tests/platform` decided on their merits.

### D11 — Every registry is empty at runtime; only tests seed them

Found in session 2, while wiring §3.0.1. `seed_all_registries()` had **zero
callers outside `tests/`** — the sixth instance of §2.0's pattern, and the most
consequential. On a clean checkout `comp run` would find an empty
`OBJECTIVES_REGISTRY`, an empty `POLICIES_REGISTRY`, and an empty
`AXES_REGISTRIES`: no objectives to resolve, no policy to ask, no axis primitive
to compose. Every passing test seeded by hand first
(`tests/acceptance/test_unified_kernel.py:49`, and six lock files), which is why
nothing caught it. **Fixed** — `seed_registries.py` calls `seed_all_registries()`
at import, matching `learning/prior.py`'s precedent.

### D12 — The PRIORS list was seeded, then cleared one line later

Also found in session 2, and D11's shape from the other side.
`seed_registries.py` registered all 28 `PRIORS` rows, then executed
`PRIORS_REGISTRY.clear()` to make `learning.prior` independent of import order —
discarding them. The two sources are **disjoint** (verified: zero name overlap;
44 live + 28 dead = 72). Consequences: `docs/generated/priors.json` re-pinned
from 44 to 72; and `_dynamics.py:590` declared
`prior="step_size_energy_minimization_backprop"`, a prior that **did not exist**,
so `step_size` silently fell back to its domain edge. **Fixed** — clear once,
after the import, then register both sources. Both defects were invisible because
`verify_registry_completeness()` reported the post-clear number and a lock
asserted against it.

### D13 — Factory signatures are not evidence of which knobs a primitive reads

The premise D5 acted on. Every ontology config factory mirrors its **whole**
dataclass field set with defaults, so `inspect.signature(update_factory)` cannot
distinguish "this primitive reads `momentum`" from "the dataclass has a
`momentum`". The `step_size` gate D5 removed was deciding a real question from a
signal that cannot answer it. The single true signal is the **availability
predicate**, which is why §3.0.1's answer is a predicate rather than a narrower
reflection.

What a signature *does* answer truthfully is which keyword names a call may
carry. That is now harvested once into `AxisSpec.accepted_params` at seed time,
so composition reads a fact instead of re-deriving it. This is the one place
reflection remains, and it is a harvest rather than a decision.

### D14 — No run ever named a real task

`pipeline.py:370` fell back to `tasks = ("default",)` when the config carried
none, and `search_space.py:211` stamped `task_id="default"` on every generated
schedule. No task by that name exists (`domains/registry.py` `SUPPORTED_TASKS`).
The stub evaluator never resolved a task, so the name was never checked and no
test failed; wiring the real evaluator (§3.1) turned 5 acceptance tests red with
`unknown task 'default'`. **The task must come from the run spec and be
validated against the registry** — a run that names no task should fail loudly
rather than measure nothing. Fixed in §8 session 3; §3.3's spec-driven space
consumes the same seam.

### D15 — Composition silently ignored the topology

Found in session 5, by reading the demo's failure log after §3.3 replaced the
enumerator.

`compose.py` `build_geometry_config` took the topology out of the geometry
mapping:

```python
topology = str(geometry.get("topology_type", "feedforward"))
```

and `_geometry_mapping` — which merges the harvested geometry values under the
composer's key names — never wrote `topology_type`, because the topology is an
*axis value*, not a geometry knob. So every cell was compiled as an MLP and then
rejected for carrying keys an MLP has no use for: `Unknown geometry keys
['num_heads'] for topology 'feedforward'`. **10 of the 12 cells in the default
space died there**, which is why the acceptance suite ran in 3:26 — most cells
were free. Nothing tested the failure: it was logged and counted as a cell.

This is §2.0's shape one level down: a *default* that silently answered a
question it should have been asked. Fixed by making the topology an explicit
argument with no default, so it cannot be lost, and by making the space filter
for legality before proposing (§8 session 5).

### D16 — Composition read a task's *width* and guessed the rest

Found in session 6, by composing every topology against `digits` and reading
the failures. `build_geometry_config` took `input_dim: int` and hardcoded the
spatial facts: `in_channels = 3`, `input_hw = (28, 28)`, `grid_hw = (16, 16)`.
A conv cell therefore compiled as a 3×28×28 CNN and died in the first forward
with `shape '[-1, 3, 28, 28]' is invalid` on a 1×8×8 task. Same shape as D15: a
default that silently answered a question it should have been asked. Fixed by
carrying the task's own `input_shape` (channels first) through
`evaluate → compose_configs → compose_cell_system → build_geometry_config`;
channels and extent are now derived from it, and a conv cell trains.

### D17 — Registered primitives the kernel cannot train, proposed anyway

Two classes, one rule: *a registered row the run cannot honour is a claim the
run makes and withdraws per cell.*

- `tile` was registered as a geometry primitive with an ontology class, a
  backend alias and **no `GeometryConfig` factory** and no `_TOPOLOGY_KEYS`
  entry, so every `tile` cell died with `Unknown topology 'tile'`. Fixed: the
  factory now exists (the derived-tile-graph variant of `TileMesh`), it is in
  `_TOPOLOGY_KEYS`, and `tile` cells compose and train.
- `nca` composes, validates, and then dies at runtime in
  `NcaGeometry.step`: the state contract is `(B, C, H, W)` and the kernel's
  trainer hands a geometry the batch. **Retired** — `AxisSpec.available=False`
  with `unavailable_reason` recorded, which is a mechanism this plan had not
  used before: a retired row leaves every space, so the run stops proposing
  cells it can only fail. The fix is a `route`-level reshape plus a read-out,
  which is a geometry feature, so it is queued rather than faked.

### D24 — Nothing ever promotes a record

Found in session 11, while making the report render claims. `promoted(record)`,
`filter_promoted` and `ReportGenerator.promotion_history` all exist and are
read by the report and the handoff summary — and **no code path ever sets
`status.maturity` above `L0`** (`evaluate.py:330,368` and
`stages_impl.py:393` are the only writers, all `Maturity.L0`). There is no
promotion stage at all: `StageId` runs S1…S11 and S8 is `RECORD`, not
`PROMOTE`. So `Promoted: 0` in every report is not a measurement, it is a
constant. The seventh instance of §2.0's pattern, and the one that would make a
maturity-promotion claim in the README unfalsifiable.

**Not fixed here.** Promotion needs a decision (what promotes a cell: achieved
seeds? a gate at L2? an operator action?) and a stage that writes maturity,
which is §3.7-adjacent work rather than report work. Recorded rather than
silently removed, and the report keeps printing the count so the constant is
visible.

### D25 — The store's claim prefilter ignored the parameter it was given

Found in session 11, same pass. `RecordStore.claim_eligible_prefilter(fidelity,
min_n_seeds)` documented

```
WHERE status.gate_verdict = 'PASS' AND NOT status.quarantine
AND schedule.fidelity = ? AND schedule.n_seeds >= ?
```

and implemented the first three. The seed condition was never in the query, so
`min_n_seeds` was a knob that decided nothing — §3.0's shape in the store.
Worse, **the test that appeared to lock it passed for the wrong reason**:
`test_claim_eligible_prefilter_uses_protocol_fields` asserts two L2 records
come back, and the fidelity filter alone produced exactly those two, so the
seed clause could have been absent and the lock would still be green. The same
class as `test_required_capabilities_are_active` (session 9): a lock that
enforces nothing reads exactly like one that enforces something.

Fixed: `query_records` gained a `min_n_seeds` filter, the prefilter passes it,
the lock's fixture gained the record the filter exists for — **one seed of a
five-seed cell, `L2` and `PASS`, which is how the executor writes every record**
— and the comment above the assertion now says why that record is there.

### D26 — The report's Pareto front defaulted to a key nothing measures

Found in session 11, by running the report on a run whose records were
measured. `pareto_frontier` and `fronts_by_fidelity` both defaulted to
`objectives=("accuracy", "param_count")`, and **`accuracy` is not a key the
evaluator emits** (§D19: the measured namespace is `train_acc`, `train_loss`,
`val_acc`, `val_loss`, `walltime_s`, `param_count`). So the section rendered
`(no claim-eligible records)` on a run with 15 passing records — a known state
reported as an empty finding, the same shape as D21's absent store.

Fixed: the default is the run's own declared objective (`objective_metric`)
against `param_count`, and the section heading prints the keys it actually
used, so a front over a metric nobody measures is visible rather than implied.

---

---

## 2. False completion marks, and the audit that must precede fixing

The archived plans are **not to be edited** (operator instruction). They are the
historical record of what was believed. This section is the correction.

| Marked ✅ | Reality | Proof |
|---|---|---|
| **WP17** — "Optuna-AXES distribution lock: `AxisSpec.kind` + `availability` drives `Trial.suggest_*`" | **Neither the lock nor the mechanism exists.** No `suggest_*` call anywhere; `study.tell()` absent | §D3 |
| **WP20** — "Unified-kernel acceptance U1–U5, 8/8 PASSING" | Passes **vacuously**: orchestration over a stub evaluator. 11 s, no training | §D1 |
| **WP13** — Class E3/E4 "scientific validity", d=−1.499, p=0.00106 | Measured on **`SyntheticGroundTruth`**, a constructed surface, and plan3 says so | §D8 |
| **WP14** — "Canonical SearchSpace/Proposal lock: every policy with **no candidate list** produces legal proposals. Prevents silent reversion to candidate-list architecture." | **The lock does not exist** — no test file, no reference anywhere in `tests/`. It was the guard against precisely the architecture §3.3 was about to accept | §3.3 |
| *(never marked)* **`compute_replay_hash`** — `replay.py:28` | Defined and exported in `replay.py:314`'s `__all__`, with **zero callers**. So §3.7's replay-hash gate has no implementation behind it either | §3.7 |

`TODO43.plan3.md` also contains a section titled **"Integration Reality
Correction"** which diagnosed all of this in advance:

> *"the corresponding runtime paths still contain stubs. The Stage Protocol is
> defined but `PipelineRunner` does not actually dispatch to `Stage.run()`,
> **the policy interface still receives an empty candidate list**, and the
> allocator hook is a no-op. These seams must close before the kernel is
> genuinely unified."*

Those were reclassified Incomplete, then the next session's notes declared "All
work packages complete" and re-marked them ✅. **The failure is verification,
not specification.**

### 2.0 The one pattern behind every defect in §1

Five of the ten defects are the same shape: **code that is defined, exported in
`__all__`, and never called.**

| Defined at | Exported | Callers |
|---|---|---|
| `backends.py:222` `_evaluate_single` | yes | produces the placeholder record |
| `compose.py:474` `compose_cell_system` | yes, in `__all__` | **zero** |
| `replay.py:28` `compute_replay_hash` | yes, in `__all__` | **zero** |
| `optuna_adapter.py:165` `build_distributions` | yes | **zero** (never reaches `study.ask`) |
| `claims.py` predicates | yes | no renderer (D7) |

**Operating rule: `__all__` membership is not evidence of a call.** A grep for
`__all__` proves a name is *offered*; a grep for call sites proves it is
*used*, and only the second counts as implemented. Every audit in §2.1 reports
call-site counts, not export counts.

This is the single most useful thing §1 contains, because it converts a class of
defects from "look for stubs" into a mechanical check.

### 2.1 Phase 0 of this plan — the audit

Scope is deliberately the **critical path only** (not every WP): re-verify the
marks that bear on "does it work", and land one new lock.

1. Re-run and read the existing `experiment/` property locks. Record for each:
   does it assert the mechanism, or only that a name is importable? A lock that
   asserts a *name* is the failure mode that produced this plan.
2. Produce a table: claim → verifying test → does the test exercise the
   mechanism (Y/N) → verdict. **Plus a call-site count per claim** (§2.0): a
   capability with a verifying test and zero callers is *also* unimplemented,
   and the count is what distinguishes the two.
3. **New lock: no work package may be marked ✅ without a named verifying test
   that exercises the mechanism.** Mechanically: for every `CAPABILITIES`
   registry row, (a) `verifying_test` names a test that exists and collects,
   (b) the test is not merely an import or attribute-existence assertion — it
   must call at least one public entry point of the capability and assert on its
   *output*, and (c) the capability's public entry point has ≥1 call site
   outside its own module. (b) and (c) together are what would have caught all
   five rows in §2.0. This makes the *next* false ✅ a test failure rather than a
   review question.
4. **Restore WP14** (§3.3) — the lock that was written to prevent a regression
   nobody noticed occurring.

---

## 3. The critical path

Each step has a gate that is a test. Nothing is marked done because a module
exists.

**Read this before starting §3, or you will misread a green gate.** Most of
§3's dependencies are *currently unwired* — five of them are the §2.0 pattern
(defined, exported, zero callers). So a §3 gate is often not merely
"unverified" but **unmeasurable**: there is nothing behind it yet. Concretely,
expect §3.1 to be small (it is one function with a bridge already written) and
**§3.2–§3.4 to be where the actual work is**, because they are the steps whose
gates depend on the unwired five. A passing §3.1 is not progress toward a
working system; it is the precondition for measuring one.

Two temptations this section is written to resist: reaching for the ~1,057
deferred pyright errors (§5) while here, and making a §3 gate pass without the
mechanism behind it. §2.0's call-site rule is the check for the second.

### 3.0 The doctrine: no magic numbers, one source of truth

**Operator directive, binding.** Hardcoded assumptions and magic numbers must be
eliminated, not relocated; single source of truth, DRY; metaprogramming,
reflection and annotations preferred over boilerplate, so inconsistency is
structurally impossible rather than merely discouraged.

This is abc3 Doctrine 1, 3 and 8 restated as an instruction, and it is a
*design constraint on the work below*, not a cleanup phase.

Concretely, in `computronium/experiment/`:

- **No literal `784`, `768`, `10`, `64` in search or evaluation code.** Input and
  output dimensionality comes from the **task**, via the task's own descriptor
  (`create_task("digits")` yields 1×8×8 and 10 classes — measured this session).
  Nothing infers a shape from a default.
- **No per-combination parameter tables** (`_build_default_params` and its seven
  `input_dim: 784` sites die with the hand-rolled enumerator).
- Every hyperparameter's domain, scale, default and prior comes from `AXES`
  via `harvest_schema()` — which already works and is already consumed by
  `learning/benchmark.py:120`. The search consumes the *same* harvested schema.
  One harvest, one schema, no second list.
- Shape and size are **derived**, not chosen: `compose.py:179` already has
  `_auto_size_geometry` and `_estimate_spatial_lattice_params` for this. Extend
  the idea rather than adding another default dict.
- **Availability is a predicate, never a branch** (abc3 §3.1): `beta` is active
  when `credit == thermodynamic_contrast` because the spec says so, not because
  code checks.
#### 3.0.1 `compose_cell_system` decides hyperparameter availability three ways; make it one

This is the D5 defect named as its own item because it is the mechanism by which
every other hardcoding would return. `compose_cell_system` currently takes
`lr: float = 1e-3` as a parameter and asks each piece separately what it needs.
Replace all three mechanisms with **one** call:

```text
coord    = Coordinate(credit=…, update=…, params={…})
active   = harvest_schema().active_axes(coord)   # availability predicates decide
config   = compose from exactly the active AxisSpecs,
           resolved from coord.params, prior as fallback
record   = the effective value, recorded (R6)
```

Acceptance:

- **No `lr` parameter.** A coordinate whose primitives need no learning rate
  receives none, and is legal without one.
- `inspect.signature` on a config factory is **gone** from composition.
- **No branch compares two axis names to decide a hyperparameter's value.** The
  `energy_minimization × thermodynamic_contrast → beta` coupling becomes
  availability, so a third pairing needs a spec row, not code.
- A coordinate carrying a param that is **inactive** for its selection is
  rejected (or reported) — dead config is a defect, the same smell the D13
  demo already chases with its dead-`local_objective` ratchet.
- Two primitives declaring one name with different domains raises
  `ConflictingHyperparameter`, a registry failure, not a silent branch.

- Enforce the rest, do not trust it: a property test asserts that no numeric
  literal equal to a known task shape appears in `experiment/execution/`, and
  that every default reaching a `Coordinate` is traceable to `AXES`. This is the
  same trick as `test_lint_count_ratchet` — which earned its keep by catching a
  config error nobody noticed.

#### 3.0.1 LANDED — see §8 session 2 for the full record

`tests/property/test_active_space_lock.py` (16 tests) holds the acceptance
conditions. `HarvestedSchema.active(coord)` returns an `ActiveSpace`;
`compose_cell_system(*, coordinate, geometry, input_dim, output_dim,
param_budget)` returns `ComposedCell(system, params)`. No `lr`. No
`inspect.signature` in composition. The MNIST-shape lock is a **ratchet pinned
at seven `search_space.py` sites**, not a zero — those die with §3.3.

### 3.0.2 A declared parameter ceiling — LANDED, see §8 session 6

The doctrine's "shape and size are derived, not chosen" needed a *number* to
derive from, and the number had to be declared somewhere a run states it.
`RunSpec.param_budget` → `Schedule.param_budget` → composition and evaluation.
`Schedule` is the honest channel: a ceiling changes what is trained, so it is in
`measurement_key` and a cell differing only by ceiling is a different
measurement while remaining the same cell.

Derived sizing is **fitted, not estimated**: `_fit_geometry` binary-searches the
ceiling and accepts a sizing only when the *built* geometry's parameter count
fits. The old per-topology estimators under-counted conv (channels alone, no
spatial extent) and NTM (memory slots alone), which is how a cell came to be
declared legal at four times its ceiling.

Acceptance, in `tests/property/test_param_budget_lock.py` (21 tests): every
trainable topology fits `MEASURED_PARAM_BUDGET`; the space screens at the size
the run will train; the ceiling is in the measurement key and not the cell key;
a swept width is honoured while the ceiling still sizes the depth; a cell that
cannot honour its ceiling fails the gate with `CONSTRAINT_VIOLATION` and names
the ceiling; the R25 tolerance is declared once and read by both the registered
predicate and the gate.

### 3.1 One cell, end to end, for real — LANDED, see §8 session 3

Replace `LocalBackend._evaluate_single` with a real evaluation:

```
Coordinate + Schedule + task
  → task-shaped loader (from the task descriptor, not a default)
  → compose_cell_system(coord)        # D5, already written; add `plasticity`
  → SystemTrainer(...).fit()
  → Record(payload={train_acc, train_loss, walltime_s, ...}, gate_verdict=PASS/FAIL)
```

`MultiprocessBackend._evaluate_single_process` **delegates** to the same
function. Two implementations of "evaluate" is how the scaffold happened.

**Gate:** one coordinate, one real `train_acc`, asserted. And the falsification
assertion — **the same coordinate with `credit` swapped must produce a
different `train_acc`**. A number that does not respond to the axis you varied
is a fabricated result, and no amount of schema validity changes that.

### 3.2 Typed `RunSpec` — LANDED, see §8 session 4

Pydantic v2 at the I/O boundary, mirroring frozen dataclasses internally
(AGENTS.md data-modelling; ceec-core precedent). Declares: task, objective
names, the **axis subsets and hyperparameter domains to search** (or "all"),
constraints, fidelity, seeds, epochs, batch limit, budget, policy, seed.
Serializes to the `runs.spec` JSON column; versioned; diffable.

**Gate:** a bad spec fails naming the offending field; two specs diff cleanly
(TODO43 **R41**); a run reproduces from its spec alone.

### 3.3 Spec-driven space — LANDED, see §8 sessions 5 and 10

Replace `search_space.py:174-206` with a generator that walks the harvested
schema under the constraints in the spec, for the spec's task. Schedule comes
from the spec, not from `Schedule(fidelity="L0", seed=42, …, task_id="default")`.

- Uniform treatment of structural axes and hyperparameters — they are both
  `AxisSpec`, and the availability predicate decides which are active.
- The active space is **computed, never enumerated** (abc3 §3.1).
- **Policies generate, they do not select from a list.** `plan3` §5 names this
  as a guarded regression — the "Canonical SearchSpace/Proposal lock (WP14)":
  *every policy, given the AXES snapshot, CONSTRAINTS, one task, a Budget, **no
  candidate list**, and an empty store, produces legal proposals. Prevents
  silent reversion to candidate-list architecture.* That lock **does not exist**
  (fourth false ✅, §2), so nothing currently stops the regression. Build the
  generating interface and the lock together; do not keep the interim
  select-from-candidates shape, which is precisely the architecture the lock
  was written to forbid, and which §3.4's `study.ask(distributions)` — a
  generating operation — cannot coexist with anyway. **Both landed in session 10**:
  the generating interface is `Policy.propose(ctx) -> Iterator[Proposal]`, and
  the lock is `tests/property/test_policy_generation_lock.py`.

**Gate:** a spec over `learning_rate ∈ {1e-4…1e-1, log}` and two credit
primitives yields candidates at more than one lr (TODO43 **R2**); the task's
shape reaches the geometry; `digits` produces an 8×8 input, never 784; and
**WP14's lock passes** — a policy with an empty store and no candidate list
still proposes.

### 3.4 Samplers that learn

`ModelBasedPolicy`:
- `study.ask(distributions)` where distributions come from
  `OptunaAdapter.build_distributions(search_space, coord)` — which already maps
  all four `AxisKind`s uniformly, honouring log scale and availability
  (`optuna_adapter.py:104,165`).
- `study.tell(trial, value)` in a new `observe(record)`, with objectives
  resolved from `OBJECTIVES`; an unknown objective is a validation error, not a
  silent maximize (this is WP17's own wording, finally honored).
- The unified store remains the only store: the study is rebuilt from records,
  no private Optuna DB (R71, already done — keep it).

**Gate (this is WP17, and it must be a real test):** a two-arm `digits` run
where the optimal lr is known; a model-based policy finds it; a random policy
does not reliably; and the study's completed-trial count equals the number of
records observed. Then assert `suggest_*` was actually called — e.g. by
comparing a `ModelBasedPolicy` trial sequence against a `UniformRandomPolicy`
one for the same seed, which must differ.

### 3.5 Claims, evidence, limitations in the report — LANDED, see §8 session 11

- Claim rendering over the **existing** predicates in `claims.py`
  (`claim_eligible`, `claim_eligible_strict`, `promoted`, `robust`,
  `generalizes`) — R35/R64, a filter and never the run asserting itself.
- A claim line carries **n and variance** (R64). No claim is expressible
  without them.
- **Limitation needs a data model that does not exist.** Design it, minimally:
  budget exhausted, gates skipped, quarantined cells, failures by cause, cells
  abandoned, fidelity not reached. If a limitation cannot be derived from stored
  records, it is not a limitation section — it is prose, and must not be
  presented as one.
- One report from the store alone (R85/R14): objectives and fronts **stratified
  by fidelity**, axis coverage, budget consumed, failures by cause, promotion
  history, claim-eligible set.

**Gate:** `comp report --run-id <id>` on a real run prints a claim with n and
variance, and a limitations section where every line is queryable from a record.

### 3.6 The campaign

`digits` — measured: 1,797 samples, 8×8, 10 classes, 10 classes of chance 0.1.
A cell is sub-second, so a few hundred real cells is a few minutes. That is what
makes this demonstrable rather than aspirational.

The artifact: `examples/eqprop-vs-backprop-digits.yaml` (name is a placeholder;
the campaign should not overclaim its question). It varies **algorithms
(dynamics × credit × update) and topology (geometry) with hyperparameters
(learning rate, width, depth, step size)** — not every primitive on every axis,
which the operator explicitly does not want.

Seven properties, each a test (§3.7). The example is a **fixture, not a
narrative**: if the campaign cannot be asserted, it is not evidence.

### 3.7 What "runnable" means — seven assertions

On a clean checkout, CPU, no network:

1. `comp run --spec-file <example>` completes and writes records.
2. Records contain a real `train_acc`, and it **moves when the axis moves**.
3. `comp report --run-id <id>` gives claim (n + variance), evidence and
   limitations, derived from the store alone.
4. `comp report status` lists the run.
5. Interrupt, resume by `run_id`: no duplicate `measurement_key`, no gap in
   coverage.
6. Re-run the same spec: same `replay_hash` (R27). **Note: `compute_replay_hash`
   has zero callers today (§2) — this gate needs it wired first.**
7. `--policy stratified_random` then `--policy model_based`: same store, same
   schema, comparable records (R16/R17).

Plus the operator's own criterion: the campaign reports **which axis mattered**
and a Pareto front over ≥2 objectives — informative results, not a number.

### 3.8 Fold the lab in, last, without a second implementation

By this point the kernel owns evaluation. `Lab.train` delegates to it; the
lab's synthesis/exploration remain available but their **predicted** metrics are
labelled predicted, everywhere, and never enter a claim. Any lab surface that
does not survive gets a retirement record (R78) rather than a silent deletion.

**Gate:** no second evaluation implementation exists; the lab's tests pass
against the kernel's evaluator.

---

## 4. Honesty fixes (README)

`docs/archive/` is **not modified** — it is the historical record. README is
live text making live claims, and is corrected here.

**Items 1, 2, 3 and 5 landed in commit `4f69c649`; item 4's command fix landed
in `04ec260e`.** Recorded here so a fresh session does not redo them. What
remains open is item 4's other half.

1. ~~**E3/E4 relabeled**~~ **DONE.** Both are now Level 3 and name
   `SyntheticGroundTruth` inline as a constructed surface.
2. ~~**U1–U5 restated precisely**~~ **DONE.** Labelled orchestration-guarantees
   with an explicit note that the evaluator behind them is a placeholder.
3. ~~**Policy table**~~ **DONE.** The `model_based` row reads "Not yet
   searching," naming `policy.py` and pointing at §3.4.
4. **OPEN — README bash blocks are still unlocked.** The
   `--profile default` → `quick-verify` command fix landed; the *lock* over
   fenced bash blocks did not. `test_cli_readme_lock` covers the command
   **table**, which is exactly why it missed a documented command that errored.
   Until it covers the blocks, documented invocations are verified by hand.
5. ~~**Add the kernel's real state**~~ **DONE.** A "Kernel status, stated
   plainly" subsection now states what the kernel does and does not, with
   `file:line` references.

**Standing item:** item 4 is a live honesty gap of the same class as the rest of
this plan — a claim in README with nothing enforcing it. Do it with §2.1's
other lock work rather than at the end.

The plan's own §1 is the model: defects stated with `file:line`, not softened.

---

## 5. Carried over from TODO45

**Done — keep.** Test-cost work (`demo` marker, `-n 4`, seed-0 arm reuse,
gallery lock restated as a data lock). G0.3 help tree. R1.4 pb2 exclusion.
Sharded ground truth and the §6 ladder.

**Withdrawn.** R1.3 (`docs/archive/`) — restored, requires named sign-off.
R1.5 — void; the premise was wrong.

**Still open, honestly small.** G0.2: the maximum single-test call time across
`unit`, `primitives` and `algorithms`+`acceleration` is ~1.5 s across 1,568
tests; only `property`'s true maximum is unmeasured and it comes free from the
next run. R1.6 needs §2's audit to know what is genuinely unreferenced.

**Deferred, and still right to defer.** Type hygiene — **~1,057** pyright
errors. (The 1,095 figure in TODO45 predates the pb2 exclusion that took `p2p`
from 61 to 23; re-measure rather than trusting either number.) Root causes are
in TODO45 §5 — `object`→scalar coercion across 18 files is ~150 of them. It
blocks nothing this plan touches. The `System` vs `nn.Module` errors in
`validation/tracks/{scaling,hardware}_tracks.py` are A5 and are untouched.

**Superseded.** TODO45's Phase 2 (`comp run` as a CLI-wiring project). The CLI is
already ~80% built and was the wrong 20%; §3 is the real Phase 2.

---

## 6. Verification ladder

Run the cheapest tier that can catch the change. Never the full suite.

| Tier | Scope | Cost | When |
|---|---|---|---|
| 0 | no-cost dry-run: AST/registry/schema locks for the change | seconds | before anything else |
| 1 | the lock files the change touches, `digits` at 2–4 batches | 10–30 s | every commit |
| 2 | one `testpaths` directory | 15 s – 2 min | round close |
| 3 | the rest of the shard set | ~2 min | round close |
| 4 | `tests/acceptance` (see §6.1 — priced before launch) | ~10 min, **re-measure first** | round close, backgrounded |
| — | `pytest -m demo` | ~1 h | re-pinning the gallery only |

**Never `pytest tests/`** — it bypasses `testpaths` and hard-killed twice at
test 873/3699. `-n 4` is already in `addopts`.

Standing rule from TODO45, sharpened into §6.1 by session 7: a test run must be
*priced before it is launched*, a suite too slow to run is a defect in the
suite, and the cheapest tier that can catch the change is the one that runs.

### 6.1 Cost is a design constraint, not a discovery

**Standing rule, operator directive.** Work in this plan is done with cheap
executions, and preferably with **no-cost dry-runs**. Electricity and operator
time are budgeted like parameter counts. A session that ends with an unfinished
suite has spent the budget and bought nothing.

- **Every gate gets a no-cost tier first.** A new claim needs an assertion that
  runs *without training a cell* — an AST lock, a registry invariant, a
  round-trip, a signature harvest. That tier is what catches the defect class
  this plan is actually about (§2.0: defined, exported, never called), and it
  runs in seconds. Only after it is green does a cell train.
- **The measured regime for any training is `digits`, 1–2 epochs,
  `batch_limit` 2–4, `MEASURED_PARAM_BUDGET`.** No other task, no larger
  ceiling, no sweep, without a written reason in the session log.
- **Price a run from a single ≤60 s measurement, never from an estimate.** If
  per-cell cost is unknown, one cell answers it. An estimate that turned out to
  be 3× low is how this session lost 25 minutes: `tests/acceptance` was launched
  on a stale 9:14 figure after an uncharged validation pass had changed the
  regime. The §6 cost column is a *measured* number or it is marked unknown.
- **Foreground commands are ≤2 min. Anything longer is backgrounded** with a
  pre-registered kill time and a poll interval, and the session continues with
  work that does not depend on it. No cell blocks on a suite.
- **Never launch a suite to find out whether a change is sound.** Run the
  cheapest tier that can catch the change; a red suite is a statement about a
  gate, not a probe.
- **A test whose cost has grown past its tier is a defect in the test**, and the
  fix is to charge the work to the run's own budget (`batch_limit`,
  `param_budget`, `epochs`) rather than to the wall clock. Both times this plan
  has met an exploding cost, the cause was a knob that grew outside the run's
  declaration: `_fit_geometry` filling a 25 000 ceiling, then validation
  iterating a whole split for a 2-batch cell.


---

## 7. Risks, unknowns, and what is not claimed

| Risk | Mitigation |
|---|---|
| The evaluator is the wrong seam — a real `System` won't train through the kernel's task plumbing | §3.1 is one cell first. If `digits` + `compose_cell_system` + `SystemTrainer` does not train, stop and re-plan; do **not** generalize first |
| Scope creep back into 88 requirements | §3 names the slice. Everything else is unclaimed, and unclaimed is a fine state |
| The fold breaks the lab's users | Fold last (§3.8), behind a gate that forbids a second evaluator |
| Another false ✅ | §2.1's registry-driven lock makes it a test failure, not a review question |
| Removing D2's hardcoding changes every recorded number | Correct. Pre-existing run-records describe the old space; label them, don't reconcile them |
| A limitation section becomes prose | Every line must be queryable from a record, or it is not shipped |
| Policies generate from a spec-derived active space (§3.3) is more work than selecting from a list | It is the architecture the plans specify, and the WP14 lock forbids the alternative. The lock is the deliverable as much as the interface |
| `__all__` membership keeps being mistaken for implementation (§2.0) | The audit reports call-site counts; the new lock requires ≥1 call site outside the defining module |

**Unknowns, stated as unknowns:**

- Whether `compose_cell_system` trains cleanly through `SystemTrainer` on
  `digits` for more than one axis combination. Unmeasured. §3.1 measures it.
- Whether the hard kill at test 873 is ever explained. It is out of the gate's
  way, not understood.
- Per-cell walltime, and therefore how many cells a campaign may afford.
  Estimated sub-second; **unmeasured** — measure before fixing a cell count.

### 7.1 Open questions — operator input unblocks these

Each is a fork this session could not decide alone, with the input that settles
it. They are ordered by how much work they gate.

**Decided:** *1* — move U1–U5 to the measured regime (`digits`, 2 batches) and
add one demo-marked test at the full regime, so the gate is cheap and the
evidence is expensive-but-optional. *7* — `mnist` is a valid secondary task:
`task_shape("mnist")` returns `(1, 28, 28)` with 10 classes, and the D16 shape
plumbing carries it to the composer unchanged. Its 60 000 samples cost nothing
extra under `batch_limit`, which is the whole point of charging per-batch.

**Answered by the operator, unresolved here:** *2* (is a bounded `val_acc`
admissible as a claim objective?) and *3* (are the 32 unmeasured objectives
targets or noise?). Session 7's default for both, so the next session is not
blocked: record `val_batches` beside `val_acc` and keep every objective
registered with its reason. Both are one-line reversals once decided.

1. ~~**Should the acceptance gate itself get cheaper?**~~ **DECIDED (operator):
   option (b).** U1–U5 train real cells and
   cost ~10 min, which makes them the most expensive thing in the plan and the
   one a session is most tempted to skip (this session skipped them). Three
   options: (a) keep the real regime and run the suite backgrounded only at round
   close; (b) move U1–U5 to the measured regime (`digits`, 2 batches) and add
   one demo-marked test at the full regime, so the *gate* is cheap and the
   *evidence* is expensive-but-optional; (c) leave it. **(b) is my
   recommendation** — the guarantee being locked is orchestration and measurement
   identity, and neither needs 45 batches to be a real guarantee. Needs a
   decision because it changes what the acceptance suite claims.
2. **Is a `batch_limit`-bounded validation number admissible as a claim
   objective?** `val_acc` at 4 batches is a bounded sample, and the payload does
   not record that bound beside the value. Options: compute a full-split
   validation only at L2/claim fidelity and keep L0/L1 bounded (cost falls where
   it matters), or record `val_batches` beside `val_acc` and let every consumer
   decide. This is a science call, not an engineering one.
3. **Are the 32 unmeasured objectives research targets or noise?** They now carry
   `unavailable_reason` and print as `unmeasured` in `docs/generated/`. Options:
   keep them registered with reasons (status quo), or retire them to a separate
   `RESEARCH_TARGETS` list so `OBJECTIVES` means *implemented*. The second is
   more honest but changes what a registry consumer sees.
4. **How far should §3.4's interface change go?** Replacing the candidate-list
   `propose()` with a generating interface lets a policy choose structural axes,
   which is what the campaign needs. Options: (a) full change now, including the
   duplicated `StageContext`/`Fragment`/`Stage`/`Decision`/`Proposal` in
   `search_space.py`; (b) staged — policies may propose a structural selection
   only where the primitive declares the capability, with the WP14 lock written
   alongside. (b) is cheaper and testable; (a) is finished sooner.
5. **Campaign shape.** **DECIDED (operator): `digits` primary, `mnist` as the
   transfer task** — `(1, 28, 28)`, 10 classes, verified this session. Still
   open: demo-marked test versus script. And
   should §3.6 ship as a demo-marked test (reproducible, expensive, gallery-
   pinnable) or as a script writing artifacts (cheap, not gated)? The second
   question decides whether the campaign can ever be asserted, which the plan
   requires.


**Explicitly not claimed by this plan:** that TODO43 is satisfied; that the
kernel searches; that the system produces scientific findings; that any README
claim about surrogate search is true before §3.4 lands.

---

## 8. Session log

### Session 1 (this one)

Ground truth by sharding; test cost cut ~10×; R1.3 withdrawn and restored; help
tree; pb2 exclusion; U1–U5 run for the first time here (8 passed, 11.22 s) and
then read closely, which is how D1–D10 were found. No `TODO45.md` checkbox was
closed on the strength of a module existing.

**Start here:** §2.1 (the audit), because three ✅ marks are wrong and one new
lock prevents the next. Then §3.1.

### Session 2

**Landed: §3.0.1 in full.** `HarvestedSchema.active(coordinate)` resolves the
active space from availability predicates; `ActiveSpace.for_axis(axis, primitive)`
restricts it to a harvested `accepted_params` set; `compose_cell_system` takes a
`Coordinate` and no `lr`, composes all six axes including `plasticity`, and
returns `ComposedCell(system, params)` — the effective values, keyed
`axis.name`, recorded per R6. `tests/property/test_active_space_lock.py`, 16
tests, is the acceptance list turned into tests.

**Three new defects found while doing it** — D11, D12, D13 above. All three are
§2.0's pattern; D11 is the second time this plan's own mechanism (a registry that
nothing calls) has cost real work. Two of them were *seeded and then discarded*,
which is worse than unwired: the data existed, was correct, and was deleted by
the next line.

**Method note worth keeping.** D11 and D12 were invisible because
`verify_registry_completeness()` reports what *survives* and a lock asserted
against that number. A completeness check that counts a registry cannot tell you
about a registry that was cleared. If the count is wrong, the lock is wrong with
it.

### Session 3

**Landed: §3.1.** `computronium/experiment/execution/evaluate.py` is the
kernel's only evaluator: task → shape → `compose_cell_system` →
`SystemTrainer.fit()` → metrics. `evaluate_cell` returns a `CellEvaluation`
(measured metrics, effective params, walltime, epochs, task); `cell_record`
wraps it in a `Record` whose gate verdict is *derived* — PASS only when the
requested epochs ran and the metrics are finite, FAIL + quarantine when a cell
did not.

Both backends now share one `_ThreadedBackend` whose only evaluation body calls
`cell_record`. `LocalBackend` and `MultiprocessBackend` are two-line subclasses,
so a stub cannot return in one class while the other trains. The D1 stubs are
gone, and with them the duplicate `_create_failure_event`.

**D1's other half was the `params` plumbing.** `Coordinate.params` never
reached composition; the evaluator passes the backend's `params` as the geometry
mapping, and hyperparameter overrides are resolved from the coordinate by
`harvest_schema().active()` as before.

**D14 (new) — `task_id="default"` was a task no evaluator could resolve.** Five
sites hardcoded it (`search_space.py:83,211,429`, `optuna_adapter.py:62`,
`stages_impl` pass-through, `pipeline.py:370`). The stub evaluator never
resolved a task, so the name was never checked; wiring a real evaluator turned
5 acceptance tests red with `unknown task 'default'`. Fixed properly rather than
by renaming: `pipeline._resolve_tasks` reads the task names from the run spec
(`task` / `tasks`), validates them against `SUPPORTED_TASKS`, and raises naming
the offenders — **a run that names no task now fails loudly instead of
measuring nothing.** `generate_initial_candidates` takes its schedule's task from
`search_space.tasks[0]`, so the space owns the task rather than a literal.
This is §3.3's `task_id` seam, closed early because §3.1 could not pass without
it.

**D6 partially closed.** `ComposeStage` and `TrainStage` no longer hold a
second compose path or a "training is executed elsewhere" note; both now report
what they handed to the evaluator and name who owns composition. `S7`'s
objective resolution remains §3.4's job, and `S9`/`S11` remain §3.5's.

**Measured regime** (`scripts/probes/t46_s31_digits_cell.py`, digits, CPU,
feedforward/energy_minimization/fast_weights): 1 epoch ≈ 0.06–0.6 s; task setup
≈ 1 s, so tasks are cached per process in `evaluate._TASK_CACHE` (lock-guarded —
free-threaded CPython, AGENTS.md). U1–U5 acceptance went from 11 s to **185 s**
because they now train. That is the cost of the stub being gone, and it is the
number §3.6's cell budget must be built on.

**Falsification is real but coarse.** Across `thermodynamic_contrast`,
`local_contrastive`, `pepita`, `gradient`, `homeostatic` on `digits`, accuracy
and loss do move — but at 4 batches accuracy is quantized to 1/128 and several
credits tie exactly on it. The lock therefore asserts on
`(train_acc, train_loss)` jointly; asserting on accuracy alone **failed under
`-n 4`** and would have been a flaky gate, not a real signal. Learnings for
§3.3's gate ("candidates at more than one lr"): pick a discriminator with
continuous resolution, not a quantized one.

**Verified:** `tests/property` 1570 passed (2:03), `tests/unit` 523 passed,
`tests/acceptance` 8 passed (3:04), `tests/ceec` 125 passed, `ruff` + `pyright`
clean on the changed modules.

### Session 4

**Landed: §3.2.** `computronium/experiment/schema/run_spec.py` declares
`RunSpec` and `AxisSelection` as frozen Pydantic v2 models with
`extra="forbid"`. Every consumer that previously read a `dict[str, Any]` now
reads a checked object: `PipelineConfig.run_spec`, both `StageContext`
declarations (`stage.py` and `search_space.py`, which duplicated each other),
`Checkpoint.run_spec`, `RunInfo.spec`, and `RunSummary.spec`.
`tests/property/test_run_spec_lock.py`, 17 tests, is the gate.

**Three incompatible spec dialects existed** — CLI/profile, `question_first`,
and the demo/test literal — and they disagreed on spelling (`seeds` vs
`n_seeds`), on `operating_point` vs `operating_points`, and on which keys
existed at all. They are now one model. `question_first()` returns a `RunSpec`
and takes the task as a required argument.

**Nine of the eighteen keys the old dicts carried were write-only** — no code
read them. Under `extra="forbid"` they are now a validation error, which is the
point: `data_origin_allocation` and `contrast_quota` were always S3 *stage*
params (`stages_impl.py:185,194` read them from `ctx.stage_params`), and a
spec that claimed to carry them was dead config.

**Four objectives in every `RUN_PROFILES` entry did not exist.**
`accuracy`, `walltime_s` and `memory_mb` were invented at the call site, and
`pipeline._build_search_space` filtered unknown names out with no message — so
the profiles silently searched on *no objectives at all*. The profiles now
name registry rows (`validation_accuracy`, `walltime_total`, `param_count`,
`flops`, `memory_usage`, `energy_per_step`). **The objective→metric-key mapping
is now missing and is §3.4's first job:** the evaluator emits `train_acc`,
`train_loss`, `val_acc`, `walltime_s`, and nothing maps `validation_accuracy`
onto `val_acc`.

**`spec_version` had three sources** (CLI default 1, `create_run` default 1,
eight test call sites passing 2). The spec now declares its own `version`
(`RUN_SPEC_VERSION = 2`) and `create_run(spec)` has no version parameter, so
the store cannot record a version the spec does not claim. Reading a persisted
spec is **fail-closed** (`RecordStore._read_spec` raises `StoreError` naming the
run) — a spec nobody can re-read means a run nobody can reproduce.

**Other DRY fixes in the same pass.** `RunProfile` gained `task`, `policy` and
`n_seeds` and is now the *only* place a profile is described;
`PipelineRunner._provenance` replaced two duplicated five-field constructions
(and a pointless `Provenance.from_dict` round-trip); `PipelineConfig.seed=42`
is now `spec.seed`; `cli.py`'s three-branch seconds→duration string became
`_duration_str`; `_get_all_stage_specs` died with the stage-source change.

**The CLI now validates at load.** `comp run --spec <file>` was a bare
`json.load` with a traceback on failure; it is `RunSpec.load`, and `--spec-
version` is gone. `--task` overrides the profile's task. Profile-driven runs
previously produced a spec with *no task* and would have died in `_resolve_tasks`
— the D14 fix from session 3 was reachable only from a spec file.

**Verified:** `tests/property` + `tests/unit` + `tests/ceec` 2237 passed (3:51);
`tests/acceptance` 8 passed (3:47); `ruff`/`pyright` clean on every changed
module (`experiment/probe.py`'s 15 pyright errors are pre-existing and
untouched). `demo_unified_pipeline.py` runs (19 records). `comp run --spec` on a
bad spec exits 1 naming `seeds`; a valid one trains.

**Not done, deliberately:** the `constraints` half of the §3.2 field list.
`CONSTRAINTS_REGISTRY` is global and unconditional today, so a spec field for
it would be a fourth write-only key.

### Session 5

**Landed: §3.3.** The hand-rolled enumerator is gone. `search_space.py` no
longer tabulates a space: `search_space_from_spec(spec)` snapshots exactly the
primitives the spec permits, and `iter_candidates`/`generate_candidates` walk
that snapshot. Candidate *k* takes the *k*-th primitive on **every** axis, so a
short prefix varies all six rather than exhausting one (the old
`substrate[:3] × geometry[:3] × ...` truncation is what D2 named). The stream
is a lazy generator, deduplicated by `measurement_key`, and the schedule is
built from the spec — fidelity, seed plan, epochs, batch limit and the task
name — instead of `Schedule(fidelity="L0", seed=42, ..., task_id="default")`.

**The seven `784` sites are zero**, and `test_active_space_lock`'s ratchet is
now pinned at zero rather than seven: `test_mnist_shape_literals_do_not_return`
asserts no task shape appears anywhere in `experiment/execution/`. The repo-wide
lint ratchet moved 440 → 423 for the same reason.

**Hyperparameters are searched, not asserted.** `RunSpec.hyperparameters`
(names → `Domain`) is the sweep the plan's gate asked for; a spec over
`step_size ∈ {1e-4…1e-1, log}` yields cells at five log-spaced values × every
primitive combination, and `test_a_swept_hyperparameter_yields_more_than_one_value`
(R2) locks it. The plan's wording was `learning_rate`; this ontology has no such
name — `step_size` is the learning rate, which is what D5 already recorded.
A swept value is carried **only** when the cell's own selection both activates it
(availability predicate) and reads it (`AxisSpec.accepted_params`), so no dead
config reaches composition. A spec domain is intersected with the harvested one
and a domain outside it is rejected naming the hyperparameter.

**`AxisSelection.domains` moved to `RunSpec.hyperparameters`.** Domain is a
property of a *hyperparameter*, and `step_size` is declared by both dynamics and
update, so putting it under an axis made the axis an arbitrary choice of owner —
the model was wrong, not just awkward. `AxisSelection` is now primitives only.

**D15 (new) — compose compiled every topology as `feedforward`.**
`build_geometry_config` read the topology out of the geometry mapping and
defaulted to `"feedforward"`. `_geometry_mapping` never wrote `topology_type`,
so *every* non-MLP cell was built as an MLP and then rejected for carrying keys
an MLP has no use for — 10 of 12 cells in the default space, found only by
reading the demo's failure log. The topology is a structural axis value, so it is
now an explicit `build_geometry_config(..., topology=...)` argument: no default,
no way to lose it. `test_each_topology_composes_as_itself` covers all nine
composable topologies and asserts `Unknown topology` for the rest.
`ComposedCell` gained `config` — the runtime module does not name its own
topology, so "which cell was this?" was unanswerable from a composed system.

**Legality now filters the space instead of the run.** `compose_configs` composes
and validates a cell's configs **without building a `System`**, and
`iter_candidates(..., shape=task_shape)` skips any cell that does not compose for
its task's shape. Cross-axis legality is asked of the one mechanism that owns it
(`SystemConfig.validate`) rather than re-declared as availability predicates,
which would be a second source of truth. `evaluate.task_shape(task_id)` is the
shape seam, sharing the evaluator's task cache. Measured effect on the
`demo_unified_pipeline` U1 demo: **2 records → 19**, because the cells that used
to die at composition now train.

**A latent measurement bug fell out of it.** With `params={}` the harvested
`hidden_dim`/`num_layers` resolved to their *domain edges* — an 8-unit, 1-layer
network that trains and measures nothing. Both now name priors
(`hidden_width`, `hidden_depth`, registered in `learning/prior.py` next to the
ruler-LR table they join), so an unswept cell is the measured regime
(64 × 2) instead of the domain floor.

**Cost, measured and now owned.** With most cells no longer dying at composition,
the acceptance suite went 3:26 → **8:55**, and U3's 180 s timeout was exceeded.
The old speed was an artifact of the defect. The fix is a geometry parameter
ceiling (§below); the timeouts were re-baselined to the measured cost (900 s)
rather than left as a red gate.

**Verified:** `tests/property` + `tests/unit` + `tests/ceec` 2261 passed
(1:44); `tests/acceptance` 8 passed (8:55); `demo_unified_pipeline.py` 19
records, unique measurement keys; `ruff`/`pyright` clean on every changed
module. `docs/generated/priors.json` re-pinned (72 → 74 priors).

**Deleted rather than left unwired** (three more §2.0 instances found by
`grep`): `search_space.Domain` (a duplicate of `schema.axis.Domain`),
`SearchSpace.active_axes_for` + `_evaluate_predicate` (superseded by
`harvest_schema().active`, which evaluates the same predicates against a real
coordinate instead of a fabricated `Record`), and `_satisfies_constraints`
(zero callers, and its per-constraint `except → False` was a second silent
filter). Also `scripts/demos/_support.make_search_space` and the acceptance
suite's private `_build_search_space` — a third and fourth copy of
`pipeline._build_search_space`, now `search_space_from_spec` for everyone.

### Session 6

**Landed: remaining-work item 1 (the parameter ceiling), item 2 (`tile`), and
two new defects, D16 and D17.** `RunSpec.param_budget` reaches composition, the
space filter and the evaluator through `Schedule`; `_fit_geometry` fits derived
sizing against the built module's parameter count rather than an estimator of
it; `MEASURED_PARAM_BUDGET` is the one declared ceiling the profiles and the
acceptance suite use; `GeometryConfig.tile` exists and `tile` cells train; `nca`
is retired with a recorded reason; and a task's `input_shape` — not just its
width — reaches the composer.

**The estimators were the defect, not just the missing number.**
`_auto_size_geometry` sized a conv cell from its channel counts alone, ignoring
the spatial extent of a 28×28 input, and an NTM from `h²` alone, ignoring its
memory slots. Both produced cells declared legal at 4–7× the ceiling. Fitting
the *built* module is what makes the ceiling mean something; a per-topology
estimator is a second source of truth that is wrong in a way nothing checks.
`geometry_param_count(config)` is now the single measure, read by `_fit_geometry`,
by the space filter and by `ComposedCell.param_count`.

**A ceiling is an upper bound, and the first value broke that.** 25 000 made the
suite *slower* — 14:05 against session 5's 8:55 — because filling a ceiling
builds a bigger cell than the unconstrained default (64×2, 8 970 parameters).
10 000 is sized to that default, so a bounded run is never slower than an
unbounded one, and it cuts exactly the cells that dominated: `spatial_lattice`
composes unconstrained at **839 690** parameters (measured), `attention` at
103 114, `ntm` at 38 139. This is the plan's own rule applied to itself: a
number chosen for the largest thing it permits is not the number that bounds
cost.

**Measured, per cell, `digits`, CPU, 1 epoch / 4 batches, ceiling 10 000:**
feedforward 9 815 (0.47 s), recurrent 9 666 (0.06 s), conv 9 689 (0.27 s),
attention 5 218 (0.12 s), tile_mesh 7 611 (0.03 s), ntm 9 495 (0.07 s),
spatial_lattice legal only under `instantaneous × gradient` (23 818 at 25 000,
trains in the probe). `tile` trains at 13 865 unconstrained. `nca` composes and
fails at runtime at every budget.

**Acceptance suite: 8 passed in 9:14** (U3 287 s + 259 s, U4 162 s, U5 97 s,
U1 53 s, U2 52 s) — every test inside its re-baselined timeout, where the
25 000 ceiling had pushed U2 (120 s) and U4 (300 s) over. `tests/property` +
`tests/unit` + `tests/ceec` green; `docs/generated/` re-pinned (only `nca`'s
`available`, plus timestamps).

**Verified:** `tests/property/test_param_budget_lock.py` (21, new),
`test_search_space_lock.py` (24), `test_active_space_lock.py`,
`test_run_spec_lock.py`, `test_stage_model_lock.py`,
`test_serialization_roundtrip_lock.py`, `test_codegen_drift_lock.py` and
`test_wp11_surface_lock.py` all pass; `ruff` + `pyright` clean on every changed
module.

### D18 — The policy was never told what the run measured

Found in session 7, wiring §3.4. `Policy.observe` was declared on the protocol
and implemented by eight classes, and **`policy.observe(record)` had zero call
sites outside `policy.py`** — the pipeline stored each record and moved on. So
even a policy that resolved its objectives had no way to learn; the store was
the only evidence path and nothing read it back into the search. The sixth
instance of §2.0's pattern, and the one that made §3.4's gate unmeasurable.
Fixed: `PipelineRunner._observe` hands every stored record to the policy, and
`ModelBasedPolicy.observe` tells the trial it asked.

### D19 — An objective name was never a measurement

Found in session 7. `OBJECTIVES` registered **36 objectives**; the evaluator
emitted payload keys for **four** of them, and nothing recorded the difference.
`resolve_objectives` read an unknown name as "maximize" with a warning, and
`RunSpec` accepted every registered name, so a profile could declare
`optimises: [flops, memory_usage]` and `study.tell` still had no value. This is
§2.0's pattern again, one level up: the registry advertised a capability and no
call site existed.

Fixed by declaring the measured namespace once (`schema/metrics.py`), stamping
every `ObjectiveSpec` with the `metric_key` that satisfies it **or** the
`unavailable_reason` (registration refuses a row with neither — the D17
recorded-reason precedent), and making resolution fail closed. `docs/generated/
objectives.md` now prints `unmeasured` on 32 of 36 rows. **The fix was not only
bookkeeping**: `validation_accuracy`, the primary objective of every profile, was
itself unmeasurable, because `evaluate_cell` passed the trainer no validation
split at all. The task's val split is now wired, bounded by the schedule's
`batch_limit`.

### Session 7

**Landed: §3.4's learning half.** `ModelBasedPolicy` asks the study with
distributions derived from the coordinate's own harvested active space and tells
it the objective values the evaluator measured. `study.tell` exists; it is called
from `observe`, which the pipeline now calls for every stored record (D18). The
study is still rebuilt from the store's records and never from a private Optuna
DB (R71 held).

**`OptunaDistributionAdapter` was rewritten, not extended.** It had zero callers,
walked `AxisSpec.topology_params` (declared "structural params, not searched"),
and fabricated a `Record` to satisfy an availability predicate that the harvest
had already decided — three ways to be wrong at once. It now maps
`HyperparameterSpec → BaseDistribution` over `harvest_schema().active(coord)`,
narrowed by the spec through the same `narrow_domain` the space uses, so there
is one validation of a spec's domain rather than two. Availability is not
re-asked; a second opinion could only disagree with the first.

**D19 (new) — 36 registered objectives, 4 measured.** `schema/metrics.py` is the
one declaration of the measured namespace and of which objective names those
payload keys satisfy. `ObjectiveSpec` gained `metric_key` and
`unavailable_reason`; `register_objective` refuses a row with neither, which is
D17's recorded-reason rule applied to the objective registry. `resolve_objectives`
is fail-closed (`UnknownObjectiveError` / `UnmeasuredObjectiveError` instead of a
warning and a silent maximize), and `objective_values` returns `None` rather than
a number for a payload that measured none of its objectives — a trial told a
value it never earned is the defect, not the missing `tell`.

**The mapping exposed a second, larger gap.** `validation_accuracy` is the
primary objective of every profile, and nothing emitted `val_acc`: the evaluator
constructed `SystemTrainer` with no validation split, so a cell could only report
what it had just fit. The task's val split is now wired, **bounded by the same
`batch_limit` as training** (`SystemTrainerConfig.limit_val_batches`, new). The
bound is not an optimisation: an unbounded validation pass makes a 2-batch cell
pay a whole split's forward passes, and doing that to the whole acceptance suite
turned a 9:14 baseline into an unfinished 25 minutes. First cheap measurement of
the change: `digits`, one cell, 2 batches — validation costs one forward pass per
training batch, so a cell's cost moves by tens of percent, not by a factor.
**This is session 6's ceiling lesson again, applied to a different knob: a
measurement that is not charged to the run's own budget will eventually be
charged to the wall clock instead.**

**The task's own shape was a searchable hyperparameter.** Geometry declared
`input_dim` and `output_dim` as swept integers — with a comment saying
"Structural - dataset-determined" — and substrate declared `device`. A search
would have been free to search for the width of its own data. Both are now
`"kind": "structural"` in their `hyperparameters()` declaration, the harvest
records the kind, and a `RunSpec` that sweeps a structural knob is refused by
name. §3.0's "shape and size are derived, not chosen" was a doctrine; it is now
enforced at the schema boundary.

**Two smaller findings, both fixed in place.** `noise_level` declares a LOG scale
over `(0.0, 1.0)`, which no sampler can invert; the adapter keeps a declared log
scale wherever the bounds permit it and drops it where they do not, rather than
raising on a harvested row nobody chose. And `create_policy` now refuses an
argument its policy does not accept instead of the caller guessing which
policies take what: `policy_context(spec, name)` harvests the accepted keywords
from the class signature — the one question a signature answers truthfully
(D13) — and a lock asserts `model_based` receives objectives, seed and spec while
`round_robin_grid` receives none of them.

**Cost.** `production-map` now runs `model_based` instead of
`round_robin_grid`, so a profile exercises the sampler rather than a positional
pick, and no profile names an unmeasured objective any more.

**Verified:** `tests/property/test_sampler_lock.py` (27, new) plus the six lock
files this touches (146 passed, 12.5 s), `test_search_space_lock.py` (24, 26 s),
and the digits evaluation cases from `test_cell_evaluation_lock.py` — deliberately
cheap, all on `digits` at 2–4 batches. `ruff` + `pyright` clean on every changed
module; `docs/generated/` re-pinned (objectives gain `metric_key` /
`unavailable_reason`, and the objectives table prints `unmeasured`).
**Not run here:** `tests/acceptance` and the full shard set, because an
unbounded validation pass made both unaffordable before the bound landed. That
gate is owed, at the measured regime, as the first thing a fresh session runs —
and §6.1 exists because this session launched it on a stale price instead of
measuring one cell first.

**Honest limit of this session's claim.** The sampler gate proves the machinery
learns on a *constructed* landscape, deliberately labelled as such in the test
docstring: it says nothing about which credit rule or topology is better. And
§3.4 is half-landed — the study tunes a cell the space enumerated rather than
choosing the cell. The remaining-work list is re-scoped to say so.

### D20 — Two of §3.7's seven commands do not exist — FIXED, §8 session 8

Found in session 7, by probing the CLI at tier 0 (five minutes, no training —
§6.1's dry-run tier paying for itself immediately). The dispatcher is
`comp {report,parity,repro,validate,joint-validate,benchmark}` and the kernel
surface lives *under* `comp report {run,report,export,conformance,status}`.
§3.7 asserts `comp run --spec-file <example>` and `comp report --run-id <id>`;
neither invocation exists, and `--spec-file` is spelled `--spec`. So gate 1
("run completes and writes records") and gate 3 ("report gives claim, evidence
and limitations") are stated against commands that error out.

This is §4 item 4's gap exactly as predicted: `test_cli_readme_lock` covers the
command **table**, which is why a documented command that errors went unnoticed.
Both are one commit — a `run`/`status` alias at the top level, or §3.7 rewritten
to the real invocations — and the second is better, because the fix that also
locks it is the bash-block lock §4 asks for.

### D21 — `comp report status` crashes and reports success — FIXED, §8 session 8

Same probe. With no store on disk, `comp report status` prints a raw
`duckdb.IOException` traceback and exits 1 (session 7 recorded this as exit 0;
the probe in session 8 measured 1 — the defect is the traceback either way, a
known state reported as an internal error). §3.7 gate 4 depends on it.

### D22 — `--dry-run` writes to the store and prints nothing — FIXED, §8 session 8

Same probe, and the most consequential of the three, because it is the cheapest
end-to-end check in the CLI and it is not one. `cli._cmd_run`'s dry-run branch
calls `store.create_run()` **before** it checks `args.dry_run` (so a "no-op" run
creates `experiment.duckdb` and a run row), and reports the plan through
`logger.info`, which nothing configures — the command exits 0 having printed
nothing at all.

§6.1 makes the dry-run tier mandatory for every gate. It cannot be mandatory
while the shipped dry-run has side effects and no output. Fixing it is cheap and
unblocks the tier the whole cost discipline depends on: print the resolved spec,
the space's primitive counts, the policy, and the first proposals to stdout, and
move the store initialisation behind the dry-run branch.

### Session 8

**Landed: remaining-work items 0, 1 and 4** — the three tier-0 items, chosen
because they cost no training and unblock every later gate.

**D20 — the kernel surface is promoted to the top level.** `comp run`,
`comp report`, `comp export`, `comp conformance` and `comp status` are now
top-level commands, each forwarding to the surface parser with its own
subcommand name injected as an argv prefix. There is no second command tree and
no alias table to keep in step: `comp run` and `comp report run` reach the same
handler. §3.7's gates 1, 3 and 4 are now stated against commands that exist.
`--spec-file` remains `--spec`; §3.7 is written against `--spec`.

**D21 — a read command against an absent store says so and exits 1.**
`_open_store` replaces four copies of the read-only `StoreConfig`/`RecordStore`
pair. The `duckdb.IOException` traceback *was* a truthfulness defect in a
different direction than §1 recorded: it exits 1, not 0, but it reports a
known state (there is no store) as an internal error.

**D22 — `--dry-run` now writes nothing and prints the plan.** The store is
initialised behind the branch, and `_dry_run_report` prints the resolved spec,
the per-axis primitive counts, the policy, and the first five *legal* cells —
computed through the same `search_space_from_spec` / `iter_candidates` /
`task_shape` path the runner uses, so a dry run is evidence the spec is
executable rather than a restatement of it. Measured: 1.5 s, no training, no
files. This is the tier §6.1 makes mandatory, and it is now real.

**D10 — `tests/acceptance` is in `testpaths`.** A bare `pytest` runs U1–U5 for
the first time in the project's history. Their cost (~9 min) is now visible in
`pyproject.toml` rather than hidden in a CI invocation that named directories.

**§4 item 4 — README is generated, and the claim lock came free.** The README's
prose lives in `docs/readme/*.md`, one self-contained file per section, and
`docs/readme/build_readme.py` assembles them. The order is the generator's
decision (`_SECTIONS`), not the file names', so reordering or renaming a section
is one list. Three tables are substituted from the code at build time — the
`comp` dispatcher, `POLICY_CATALOG` (with each policy's own docstring), and the
demo scripts on disk — and the contents list is derived from the headings that
exist. A README row can no longer advertise a command or a policy that was
removed, because the row is the registry.

**Two README claims were stale the moment generation landed, which is the
argument for it.** The `comp` table's five purpose lines had drifted from
`_SUMMARIES`, and the policy table described `model_based` as searching when it
searches hyperparameters within a spec-selected cell. Both now render from the
source, and the nuance that does *not* belong in a table is prose in
`kernel.md`.

**Locks.** `tests/property/test_readme_build_lock.py` (8): the committed README
equals the build; every snippet contributes; the manifest is the only ordering
and an unlisted snippet fails; every `<!-- gen: -->` marker resolves to a real
generator and none survives the build; the CLI/policy/demo tables name exactly
what the registries hold; every contents anchor resolves to a heading.
`tests/property/test_cli_readme_lock.py` (11) grew the bash-block lock §4 asked
for: every fenced `bash` block in the README is parsed against the real parsers,
so a documented invocation that does not exist is a test failure (D20's class),
and it now asserts the tier-0 tier itself — a dry run prints a plan and leaves
the directory empty, and `status` on an absent store exits 1 without a
traceback. `tests/property/_readme.py` is the shared builder loader
(`docs/readme` is prose, not a package).

**Cost.** Everything here was tier 0–1: 20 tests, ~11 s, no training, no
`experiment.duckdb` written.

### D23 — 39 of 88 capability rows named a test that does not exist — FIXED, §8 session 9

Found by §2.1's audit, which is the item that had been outstanding since
session 1. `CAPABILITIES` is the registry the conformance report and the
`comp conformance` command present as *evidence*, and every one of its 88 rows
carries a `verifying_test`. **Twenty-one named a test file that had been deleted
(`tests/integration/test_demo_*.py`, `packages/*/tests/test_*.py`) and
eighteen more named a function that does not exist inside a file that does**
(`test_multiprocess_backend`, `test_ddp_fsdp_works`, `test_surrogate_acquisition_ei`,
…). `surface/conformance.py` runs those node ids through pytest, so a "verified"
capability was a `pytest: no tests ran` masquerading as a pass — the same shape
as §2.0 one level up, in a registry rather than a module.

Fixed in two halves, because the two halves are different statements:

- **Twenty-one re-pointed** at tests that exist and exercise the primitive —
  mostly the generated `tests/property/generated/test_*_invariants.py` family,
  which is exactly the mechanism evidence those rows needed and already existed.
- **Nineteen marked `CapabilityStatus.UNVERIFIED` with a recorded reason.** A new
  status is the honest third answer: before this, a row could be ACTIVE — which
  claims a guarantee nothing verifies — or RETIRED, which is a *stronger*
  statement than "untested". `C58` (multi-objective Pareto) is the clearest
  case: it pointed at `test_effect_size_guards`, a real test of a different
  claim, so it is unverified rather than quietly re-aimed. `CapabilitySpec`
  now refuses `UNVERIFIED` without a reason and `RETIRED` without a retirement
  record, so neither status can be a silent demotion.

### Session 9

**Landed: remaining-work item 3 (§2.1's audit and its lock), D23, and the
measured regime for the acceptance gate.** Three tiers of cost: tier 0
(AST, no training) for the audit and the lock, tier 1 for the gate re-pricing.

**`computronium/experiment/surface/evidence.py` is the audit, as code.** It
answers one question per capability row from the verifying test's AST: does the
test *call* a kernel entry point and assert on it, and does that entry point
have a call site outside its own module (§2.0)? One implementation, read by the
capabilities listing (`Evidence` column in `docs/generated/capabilities.md`) and
by `tests/property/test_capability_evidence_lock.py` (9 tests, ~70 s, no
training). Judgement is structural rather than a hand-maintained table, which
is the point: §2.1 asked for a table nobody would keep true.

**Where the 88 rows stand, measured:** 69 active, 19 unverified. Of the active
rows, **65 carry mechanism evidence and 4 are shape-only** (C31, C35, C44, C52
— enum-membership and protocol-shape assertions). Every CORE row (48 of them)
now reaches a kernel entry point with an outside call site: re-pointing C7
(legality), C8 (pipeline), C9 (policies), C17 (priors), C83 (CLI), C85 (codegen)
closed the last six, and fixing the 21 stale rows closed the rest.

**Three things the analyzer had to learn before it was honest**, each of which
was a false "shape" verdict on a real test: a test may reach the kernel through
a **fixture** (`test_allocator_promotion`'s `allocator`), through a **helper in
its own package** (`_support.py`), and it may assert with
**`pytest.raises`/`pytest.warns`** rather than `assert`. A judge that only
recognises `assert` and direct calls would have understated the evidence and
sent the next session to re-point tests that were already fine.

**The evidence label is now rendered, and the count is a ratchet.** Both the
shape-only total (≤ 30) and the unverified total (≤ 19) are ratchets, so the
honest totals cannot quietly rise; the audit table lives in
`docs/generated/capabilities.md` instead of in this file.

**The acceptance gate is back inside its tier.** `tests/acceptance` had grown
12:11 with three timeouts red (U2 at 120 s against a measured 333 s), because
session 7's validation split was never charged to the run's budget and the spec
set no `batch_limit` at all. `MEASURED_BATCH_LIMIT` is now a declared constant
next to `MEASURED_PARAM_BUDGET` — the operator's §7.1-1 decision, implemented —
and the gate is `digits`, 1 epoch, 2 batches: **8 passed in 1:04**. The
expensive-but-optional half is one demo-marked module,
`tests/acceptance/test_demo_acceptance_full_regime.py` (`batch_limit=0`, full
split, one round pair), which stamps `demo` by filename and therefore stays out
of the gate: **37 s measured**, asserting that measured records exist and that
some cell beats chance on a full epoch.

**`test_required_capabilities_are_active` was the lock that made D23
impossible to see.** It asserted "required ⇒ ACTIVE", which is the false
completion mark restated as an invariant. It is now
`test_required_capabilities_are_not_retired`: a required capability may be
ACTIVE or UNVERIFIED-with-a-reason, never RETIRED. **A lock can enforce a lie as
efficiently as a truth, and this one had been green for sessions.**

**Verified:** `tests/property` + `tests/unit` 2210 passed, 16 skipped, 26
xfailed, 1 xpassed (4:44); `tests/acceptance` 8 passed (1:04); the new evidence
lock 9 passed (1:07); the seven neighbouring locks it touches (codegen drift,
registry wiring, capability totality, public surface, schema forward tolerance,
WP11 surface, CLI/README) green; `ruff` + `pyright` clean on every module this
touched; `docs/generated/` re-pinned.

**Not run here:** `tests/primitives`, `algorithms`, `acceleration`, `ceec`,
`platform`, and `pytest -m demo`. The first four do not touch the schema or the
surface this session changed; the demo tier is gallery work.

### Session 10

**Landed: remaining-work item 2 — §3.3/§3.4's interface change, and the WP14 lock
that now guards it.** The candidate list is gone from the policy layer. Every
policy takes one argument:

```python
def propose(self, ctx: ProposalContext) -> Iterator[Proposal]: ...
```

`ProposalContext` (now in `policy.py`) carries the run's active space, its spec,
its run id, its budget, its cost model, a `RecordSource` for the store, the
task, the task's shape resolver and `n_propose`. There is no cell in it, so a
policy *cannot* propose a cell the run did not declare — it has to generate one
through `iter_candidates`, the one generator the space already had. `ctx.cells()`,
`ctx.pool()` and `ctx.legal()` are the three doors into it; `legal()` is the
single legality predicate, asked of the cells a policy *constructs* itself
(a mutated cell is a cell nobody has composed yet).

**Five smaller things the same change forced out, each a defect the old shape
hid:**

- **`StageContext.pending_candidates` had zero readers.** The live context
  carried `pending_proposals`, the pipeline filled both, and stages read only the
  latter — the two-channel shape §D5 named, one channel dead.
- **S3 dropped `Schedule.param_budget`** when it re-seeded a cell for its data
  origin, so a scheduled proposal silently lost the ceiling the run declared.
- **`StrategyProgressionPolicy.stages` was typed `list[tuple[Policy, int]]`** for
  a value the docstring calls a budget *fraction*.
- **`ModelBasedPolicy` had two knobs for one thing** (`n_suggest` and the
  context). The context owns it now.
- **A policy constructed without `spec=` samples the whole harvested space**, and
  the values it merges can be ones the harvest then refuses for that selection
  (`InactiveHyperparameterError`). Those cells are now screened by `ctx.legal()`
  and their trial is told `FAIL` rather than proposed — the failure is visible to
  the sampler instead of becoming a training run that cannot compose.

**The duplicate type declarations are gone, and in the direction the live code
runs.** `search_space.py` no longer declares `Proposal`, `Fragment`,
`StageContext`, `Stage`, `Decision`, `ProposalContext` or `ProposalPolicy`; it is
the space generator and nothing else, which also removes its bottom-of-file
runtime imports and the `search_space → stage → search_space` cycle. The canonical
`Proposal`/`Fragment`/`StageContext`/`Stage` live in `stage.py` (whose own copies
were the dead ones — `Fragment.proposals` was even typed as tuples). `ProposalContext`
and the new `RecordSource` protocol live in `policy.py`, next to the `Policy`
protocol they are the arguments of.

**`tests/property/test_policy_generation_lock.py` is the WP14 lock the plan has
been citing since session 1 as a false ✅.** Four claims over the shipped policy
instances: each proposes from an empty store with no candidate list; every
proposal's six axes are in the snapshot and its schedule is the spec's; every
proposal actually composes for the task's shape; and — the guard — no policy's
`propose` takes anything but `(self, ctx)`. The last one is the regression
test: it fails the day someone adds a parameter back, rather than the day a run
quietly stops exploring.

**Verified:** `tests/property` 1719 passed / 2 failed → both fixed and re-run
green (5:08); `tests/unit` 523 passed (2:28); `tests/acceptance` 8 passed
(1:23); `ruff` + `pyright` clean on every module touched; README rebuilt (its
policy table reads the new docstrings) and the build lock green.

**Not run here:** `tests/primitives`, `algorithms`, `acceleration`, `ceec`,
`platform`, `pytest -m demo` — none touches the schema or the surface this
session changed.

### Session 11

**Landed: §3.5, and D24–D26.** The report now renders claims and limitations;
both are derived from records, and a claim is *inexpressible* without its
evidence.

**A claim is a required-field object, not a rendered sentence.** `Claim`
(`evidence/claims.py`) carries `metric`, `axis`, `value`, `n`, `mean`,
`variance`, `cells`; `n` and `variance` have no defaults, so R64's "a claim
line carries n and variance" is enforced by construction rather than by
convention — and `__post_init__` refuses `n < 1`, a non-finite mean or a
negative variance. `derive_claims(records, metric, achieved, min_seeds)` groups
claim-eligible records by axis value and summarises each group; `strongest_axis`
answers the operator's own criterion ("which axis mattered") from the same
claims rather than from a second analysis.

**Eligibility is a filter the run does not apply to itself.** A record
contributes only if it passed its gate, is not quarantined, **and its
replication key reached `min_seeds` passing seeds**. That last clause is
`claim_eligible_by_achieved_seeds`' semantics, not `claim_eligible`'s: the
executor writes one record per seed with `schedule.n_seeds == 1`, so the
*planned*-seed predicate is unsatisfiable for every record a run actually
writes. The predicate is left alone (`test_statistical_protocol_lock` locks it
and it is the documented R35 rule); the cell-level truth is a new store method,
`claim_eligible_replication_keys`, which answers "which cells achieved their
seeds" in **one grouped query** rather than one query per cell.

**Limitations are counts with their filter attached.** `LimitationKind` names
the seven things a record stream can answer for — quarantined cells, failures
by cause, gates never reached, cells short of their declared seeds, fidelity
not reached, declared objectives no measurement satisfies, and *no eligible
claim at all*. `Limitation` carries `count` and `evidence`, and refuses to be
constructed without the second, so the report prints the filter beside every
line and the lock recomputes each count from the records. The derivations are a
table (`_DERIVATIONS`), one small function per kind — adding a limitation is a
row, not a branch in a 60-line function.

**Measured, not fabricated.** The lock's fixture trains real `digits` cells
through `cell_record` at the measured regime (1 epoch, 2 batches,
`MEASURED_PARAM_BUDGET`), 3 s for the module's seven cells, and one of the two
credit cells deliberately stops at 2 of 5 seeds so the abandoned-cell line has
something true to say. On that run the report prints claims for the two full
credits, `cells=1` each, and exactly one `[cells_abandoned]` line — and the
report *before* the fix would have said `Claim Eligible: 12`.

**Three new defects fell out of reading the report's own output** — D24, D25,
D26 above. All three are "a known state reported as a measurement":
`Promoted: 0` is a constant (nothing promotes), the store's claim prefilter
ignored its seed filter *and the lock for it passed for the wrong reason*, and
the Pareto section named a payload key nothing emits.

**DRY in the same pass.** Four definitions of the replication key existed
(`claims._compute_replication_key`, an inline f-string in
`report.claim_eligible_table`, one in `group_by_replication_key`, and the
store's SQL parser) — now one Python function and one SQL column list with a
shared formatter, so "the cell key and the measurement key cannot disagree" is
structural. `axis_coverage`'s six-axis tuple literal is `StructuralAxis`;
`count_by_axis` takes a `StructuralAxis` rather than re-declaring the six as a
`Literal`; `pipeline._is_claim_eligible` (a fourth copy of the predicate) now
calls the predicate. `claims.claim_eligible_by_achieved_seeds` carried its
docstring **twice**, verbatim, from an earlier edit.

**Verified:** `tests/property/test_claim_report_lock.py` (22, new) plus the
two protocol locks whose fixtures it touches — 89 passed in 13 s; `ruff` and
`pyright` clean on every module this session touched.

**Not verified here, stated plainly:** the `tests/property` shard was launched
twice and both runs were **hard-killed with no summary** (the §7 unknown, now
observed twice more — at 65% of the combined shard and at 92% of `property`
alone). The second run showed **one failure at ~48% that I did not identify**:
by the operator's instruction not to keep spending test time hunting it, it is
recorded rather than chased. `tests/property/test_ontology_parity.py` and the
other 216 entries in `.pytest_cache/v/cache/lastfailed` are **stale** (that
node id no longer collects), so the cache is not a usable pointer — see §6.2.
`tests/unit` and `tests/acceptance` were not re-run this session; both touch
`query_records(run_id=...)` by keyword, which is the only signature change.

### Remaining work, in order

0. ~~**D22, then D20/D21, then the tier-0 CLI lock**~~ **DONE, §8 session 8.**
1. ~~**D10** — add `tests/acceptance` to `testpaths`~~ **DONE, §8 session 8.**

2. ~~**§3.4 remainder — the candidate-list `propose()` signature**~~ **DONE, §8
   session 10.** `Policy.propose(ctx) -> Iterator[Proposal]` across all eight
   policies, `ProposalContext` carrying the space/spec/task/budget/store instead
   of a cell list, the `search_space.py` duplicates deleted, and WP14's lock
   built and passing (`tests/property/test_policy_generation_lock.py`). §3.3 and
   §3.4 were one interface change and are now one interface change. **Left
   deliberately:** `EvidenceDrivenAllocator.propose(candidates, …)` still takes a
   candidate list — that list is cells already measured and awaiting a promotion
   decision, not a search space, so the architecture the lock forbids does not
   apply to it.

3. ~~**§2.1's audit table and the new lock**~~ **DONE, §8 session 9** — as code,
   not as a table: `surface/evidence.py` judges each row from the verifying
   test's AST, `capabilities.md` renders the verdict, and
   `test_capability_evidence_lock.py` gates it. It found D23 (39 rows naming a
   test that does not exist) and turned 6 more CORE rows onto real mechanism
   tests. **Two follow-ons, both small:** (a) `surface/conformance.py` still
   *runs* an `UNVERIFIED` row's node id instead of reporting the row's recorded
   reason, so `comp conformance` prints a pytest failure for a capability it
   already knows is unverified; (b) `codegen.generate_conformance_stubs` emits a
   stub per row, including the unverified ones, which is 19 files that exist to
   skip.

4. ~~**§4 item 4's remaining half**~~ **DONE, §8 session 8** — and more than the
   bash-block lock: README is now *built* from `docs/readme/*.md`, with every
   table that can be read from the code substituted at build time.
5. ~~**§3.5 — claims, evidence, limitations in the report**~~ **DONE, §8
   session 11.** `Claim` (n and variance required), `derive_claims` over the
   achieved-seed filter, `strongest_axis` for "which axis mattered",
   `evidence/limitations.py` with seven derived kinds each carrying its filter,
   and both sections rendered by `generate_run_report` from the store alone.
   **Left deliberately:** promotion (D24) — nothing sets maturity above `L0`,
   so `Promoted:` stays 0 and the promotion-history section is honest about
   being empty until a promotion stage exists.
6. **`nca` is retired, not fixed** (D17, session 6). Restoring it needs
   `NcaGeometry.route` to reshape a `(B, F)` batch into the `(B, C, H, W)` state
   grid its `step` contract names, and to read class logits back out of the
   grid. That is a geometry feature with credit/settle consequences — a
   separate piece of work, and the reason the row carries a recorded reason
   rather than a silent `available=False`.

7. **LOW PRIORITY — README content archaeology.** The README has been
   rewritten several times (TODO43's canonical rewrite, TODO45's cost pass,
   this session's generation). Every rewrite dropped *something*, and the drops
   were never diffed: they were noticed, if at all, only by a reader who
   remembered. Read `git log -p --follow -- README.md` back to a commit from
   ≥2 days before the significant change and list what the old file carried
   that the current one does not — sections, caveats, links, tables, measured
   numbers. Recover the substance worth keeping into `docs/readme/*.md`; do
   **not** restore text merely because it was there. **This is now cheap in a
   way it was not:** the README is built from snippets, so a restored detail
   lands in one file and is regenerated, and a detail that turns out to be
   registry-derived is better served by a `<!-- gen: -->` block than by prose.
   Recorded because the plan's own §1 is that defect class — content that
   existed, was correct, and left without a marker.

### 6.2 Spending less test time (operator directive, session 11)

A session that ends with an unfinished suite has spent the budget and bought
nothing — and a session that re-runs a shard to *find out* what failed has spent
it twice. Session 11 launched `tests/property` twice for one feature and got
nothing from either. The rules that would have prevented it:

1. **A feature change names its tests; it never launches a `testpaths`
   directory.** The cheap step is `grep -rn <symbol> tests/ --include=*.py`
   (~1 s) followed by running the 2–4 files it names. Whole-shard runs happen
   at round close, backgrounded, once. Session 3–10 all did this; session 11
   did not, and the difference was ~12 minutes and no verdict.
2. **Collect before you execute.** `pytest <dir> --co -q > ids.txt` runs no
   test code and takes ~40 s; slicing that file locates a failure in a killed
   run without re-running anything. Guessing a failure's position from a
   progress percentage is strictly worse and cost a 10-minute run here.
3. **A killed run produces no verdict, so make it produce a list.** Any launch
   expected to be interrupted writes `-rf --tb=line` to a log: the failure list
   survives the kill even when the summary does not.
4. **Do not trust `.pytest_cache/v/cache/lastfailed` in this repo.** 520
   entries, most of them stale — node ids drift as tests are renamed, and
   `--lf` selects tests that no longer collect. Reset it (or use `--ff` with a
   fresh cache) or ignore it.
5. **One measurement, then act.** Re-running a shard that was already green to
   "confirm" is the same waste as re-running a red one to investigate.
6. **Price by symbol, not by directory.** A change to `evidence/` does not need
   `tests/property/biology/`; a change to `evaluate.py` does need the training
   tier, and only that tier.

**Worth automating (not done):** `scripts/probes/related_tests.py <module>`
would do step 1 in one second by grepping `tests/` for the module's public
symbols, printing the candidate test files ranked by match count. It is the
same trick as the AST locks, applied to the *test selection* rather than to the
code, and it is the cheapest possible intervention against this session's
worst habit.

**Improvement opportunities found in session 11:**

- **The report asks the store the same question three times.** `claims()`
  computes `achieved_seeds()` (one query *per cell*); `limitations()` calls
  `claims()` *and* `achieved_seeds()` again; `run_summary()` calls
  `claim_eligible_records()`. At 50 cells that is ~150 round trips to print one
  page. The grouped query behind `claim_eligible_replication_keys` already
  returns achieved counts — deriving `achieved_seeds` from one grouped query
  instead of a per-cell loop is the fix, and §6.1's rule applies verbatim: cost
  hidden in a loop is cost nobody prices.
- **A claim is reported for axes the run did not vary.** With one geometry
  value, `geometry=feedforward: val_acc=… (n=10)` is a measurement but not a
  comparison. Restricting claims to axes with ≥2 observed values would leave
  the section carrying only what it can support; today it carries four
  single-value lines the reader has to skip.
- **`Claim` reports one metric; a run declares several.** The metric is the
  run's first *measured* objective, so `optimises=[val_acc, walltime_s]`
  yields claims about one of them. §3.6 wants a Pareto over ≥2 objectives, so
  `derive_claims` will need to be per-metric rather than per-first-objective —
  a change to the lock, not to the model.
- **Two more predicates read payload keys nothing writes.** `robust()` reads
  `seed_metrics` and `generalizes()` reads `task_metrics`; neither is in
  `MEASURED_METRICS`, so `generalizes` is structurally `False` and `robust`
  silently falls back to counting planned seeds. That is D19's shape in
  `claims.py`, and the same fix applies: declare the key in `schema/metrics.py`
  or retire the predicate with a reason.
- **Promotion has no stage, so three report sections are permanently empty**
  (D24). Worth the §2.0 call-site treatment: every report section that renders
  nothing for every conceivable run is either unimplemented or dead, and the
  report cannot tell you which.
- **The seed filter nobody could see is now visible, and it empties a set.**
  `claim_eligible_prefilter` with `min_n_seeds=5` returns nothing for any run
  the executor writes. That is the *record-level* predicate being honest; the
  cell-level one is `claim_eligible_replication_keys`. Worth checking, at the
  next round close, that no consumer wants the old (over-inclusive) behaviour.

**Improvement opportunities found in session 10:**

- **The space generator is now the only way to get a cell, and it is
  deterministic.** `iter_candidates` walks `k % len(names)` per axis, so two
  policies given the same space and the same pool draw from an identical prefix —
  which is exactly what makes the sampler's `seed` the only thing that
  distinguishes its proposals from a random one's. A run that wants *coverage*
  rather than sampling still has no way to say so: the round-robin policy rotates
  over one pool, it does not enumerate the space. Worth deciding whether the
  generator's stride is a declared policy or an implementation detail.
- **`_POOL = 50` is an undeclared cost.** Every sampling policy walks 50 cells to
  return `n_propose`, and each walk composes configs (~10–100 ms/cell). At
  `n_propose=10` that is 5x the legality work the run needs, and it is invisible
  against training — the same shape as session 8's `batch_limit` finding. It
  belongs beside `MEASURED_PARAM_BUDGET` as a measured constant, or beside
  `n_propose` in the context where it is visible.
- **`ctx.legal()` is asked twice for generated cells** (once inside
  `iter_candidates`, once by the policy). That is 2x geometry fitting for the
  cells a policy did not modify. The duplicate is the price of one legality
  predicate covering both generated and constructed cells; the alternative is two
  predicates, which is worse. Worth a measurement before anyone calls it free.
- **A `ModelBasedPolicy` built without `spec=` samples the entire harvested
  space** and merges values the harvest may then refuse. The cells are now
  screened, but the sampler is still being asked about hyperparameters the run
  never declared — and the `FAIL` trials it accumulates are the study learning
  from a policy that was configured wrong. `policy_context` always passes `spec`,
  so the constructor allows a state the run never reaches; making it required
  would be a one-line change with three call sites in tests.
- **The `learning/surrogate.py` and `learning/benchmark.py` policies are a third
  proposal interface** (`propose(n, context: dict) -> list[Coordinate]`), with
  `context: dict` where this session's is a typed frozen dataclass. WP14's lock
  only covers `POLICY_CATALOG`, so the guarded regression is guarded in one place
  and unguarded in two. Whether the surrogate belongs in `POLICY_CATALOG` at all
  (it answers a different question — what to search, not what to evaluate next)
  is the open design question.
- **`S7 Measure` is still a shell**: it copies `ctx.pending_proposals` into a
  local named `measured`. §D6's shells got thinner this session by accident; this
  one is the obvious next, and it is the stage §3.5's limitations section will
  have to stop lying about.
- **A lock over a signature is a lock over a spelling.** WP14's fourth test reads
  `inspect.signature(...).parameters == ["self", "ctx"]`; renaming `ctx` to
  `context` fails it, which is the right kind of strict only by accident. The
  claim worth locking is "no parameter is a sequence of candidates", which a
  behavioural test could make: assert the policy never *received* a cell. As
  written, this lock is a convention with teeth.

**Improvement opportunities found in session 9:**

- **`UNVERIFIED` is a status, and two consumers still ignore it.**
  `conformance.py` reports unverified rows as failures rather than as the
  recorded reason, and `codegen` emits conformance stubs for them. Both are
  one-line judgements once the status is read; neither is worth doing before
  the rows are re-verified.
- **The audit is only as good as its reader of pytest.** It understands
  fixtures, same-package helpers, `pytest.raises` and bare module paths; it does
  not follow a fixture *defined in a conftest*, a `parametrize` over a factory,
  or a test that asserts only through a helper's return value. Each of those is a
  false "shape" verdict waiting to send a session after a test that was fine —
  the same class as `test_codegen_drift_lock`'s byte comparison being the thing
  that keeps the docs honest: **a cheap judge needs a known set of ways to be
  wrong, and the honest thing is to write them down.**
- **A lock can enforce a lie.** `test_required_capabilities_are_active` was green
  for four sessions while 39 rows named tests that did not exist, because it
  asserted the completion mark rather than the evidence. Worth a grep of the
  property locks for assertions of the form "X must be ACTIVE/ENABLED/PRESENT"
  — each one may be freezing a defect rather than a guarantee.
- **Cost was in the spec, not in the test.** The acceptance gate cost 12 minutes
  because `batch_limit` defaulted to unbounded and validation was only bounded
  after session 7 found it. A gate whose cost is a *default* is a gate nobody
  prices; the acceptance spec now names both numbers it spends.

**Improvement opportunities found in session 8:**

- **The generated-table mechanism generalises and nothing else uses it yet.**
  `docs/generated/` already carries `axes.md`, `objectives.md`, `capabilities.md`
  and `stages.md`; the README links them but does not show a single number from
  them. A `<!-- gen:... -->` for the measured-objective count (36 registered, 4
  measured) or the per-axis primitive count would turn a prose claim into a
  rendered fact, and the same generator would serve `docs/readme/*.md` and the
  operator-facing docs.
- **A snippet can now drift from its own subject without failing anything.**
  `ontology.md`'s primitive table is prose; `docs/generated/axes.md` is the
  registry. The build makes the *tables* honest and leaves the hand-written ones
  exactly as trustworthy as they were, which is worth remembering before
  treating the generated README as verified end to end.
- **`scripts/readme_snippet_lock.py` and the new build lock are two locks over
  one file.** The snippet lock (verbatim code blocks vs their source tests) and
  the build lock (README vs snippets) are orthogonal and both needed, but the
  snippet lock reads `README.md` while its sources are now in
  `docs/readme/*.md` — it should read the snippet, so a README that has never
  been rebuilt cannot pass it.
- **The dispatcher's `_SUMMARIES` is now user-facing text in two places**
  (README table, `comp --help`) and is the single source for both. Good. But
  `RunProfile.description` and `AxisSpec`/`ObjectiveSpec` prose are still only
  rendered in `docs/generated/`, and the same substitution would serve them.

**Improvement opportunities found in session 7, beyond the landed fixes:**

- **The measured namespace is declared in `schema/metrics.py` but only four of
  36 objectives use it.** `flops`, `memory_usage` and `energy_per_step` are one
  config flag away (`SystemTrainerConfig.track_flops`/`track_memory`, and
  `EpochResource.forward_flops`/`peak_memory_mb` already exist) — the honest
  version of "enable the tracker" is *turn them on, pay for them, and record
  them*, which needs a cost measurement, not a registry edit.
- **`Coordinate.cell_key`'s docstring says "structural axes only (no schedule)"
  and the body includes `params`.** The measurement identity depends on it, so
  the docstring is wrong, not the code. Unfixed; a one-line correction nobody
  needs until they read the hash.
- **`cell_key` and `measurement_key` re-serialise the same seven fields twice.**
  One private `_identity()` would make "the cell key and the measurement key
  cannot disagree" structural instead of reviewed.
- **`_parse_hyperparameters` now has three declaration shapes** (tuple, list,
  dict) and the dict one carries four optional keys. The next declaration format
  added will make it a parser; the registry-driven lock should require an
  example per shape.

**Carried notes from sessions 3–7 that are still open:**

- **CLOSED in session 6 — the `params` channel.** `_composable` was passing
  `coordinate.params` as the geometry mapping, so a hyperparameter named like a
  geometry key reached the composer as topology. Swept geometry values now reach
  composition through `_geometry_mapping(active, geometry, topology, swept)`,
  which is keyed on `coordinate.params` itself, and the space filter passes
  `geometry={}`. The backends' `params` argument is still named `params` while
  the evaluator reads it as geometry; renaming it is cosmetic and unblocked.
- `_TASK_CACHE` in `evaluate.py` keys on `(task_id, device)` and never evicts.
  Fine for a handful of tasks; a leak if a run sweeps many — and §3.6's
  multi-task spec will find it. `task_shape` now shares that cache.
- `build_geometry_config` is the one remaining normalizer, and it still carries
  `_GEOMETRY_ALIASES` (`num_layers` → `depth`) because geometry factories spell
  the same knob three ways. That table is a §3.0 violation in miniature; it dies
  with the geometry-axis normalization pass, and
  `test_the_geometry_alias_table_does_not_grow` now holds it to one entry.
- **Silent name filtering is still this plan's most productive defect shape.**
  Three instances so far: unknown objectives dropped by
  `pipeline._build_search_space` (fixed), `AxisSelection` silently ignoring an
  unknown primitive name (now rejected), and `_satisfies_constraints` swallowing
  every predicate error as "violated" (deleted). Grep for
  `if .* in .*REGISTRY` filters and `logger.warning`-then-continue; each is a
  candidate.
- **`_MAX_SCAN` bounds the candidate stream, not the space.** With legality
  filtering, most `k` are skipped; 10 000 is a scan bound chosen so a budget or a
  predicate that admits nothing terminates instead of spinning. If a future spec
  needs more candidates than that, raise it deliberately.
- **`SystemConfig.validate` emits `UserWarning` for soft mismatches** (beta
  mismatch, substrate/credit pairings). The space filter now runs it for every
  candidate, so a warning-heavy spec will be noisy. Soft violations are not
  rejection — do not "fix" that by turning warnings into errors.
- **`--spec-version` is gone from the CLI** but `spec_version` remains a column
  and a `RunInfo` field; it is now derived, and `report.py:408` prints it. A run
  row whose `spec_version` disagrees with its `spec.version` is unrepresentable
  through the API but still constructible by direct SQL — the fail-closed read is
  what catches it.
- **`StageContext`, `Fragment`, `Stage`, `Decision` and `Proposal` are still
  declared twice** — in `execution/stage.py` and again in
  `execution/search_space.py`. §3.4 should delete the `search_space.py` copies
  rather than update both.
- **A `dict[str, Any]` parameter is a place where nobody checked anything.**
  Typing one is what surfaced four tests passing `{"kind": "lock"}` as a spec
  (session 4) and one `params` channel carrying two meanings (session 5, closed
  in session 6).
- **A ceiling is a promise about cost, and the first value chosen broke it.**
  `MEASURED_PARAM_BUDGET` was 25 000 when first landed, and the acceptance suite
  got *slower* (14:05 against session 5's 8:55) because `_fit_geometry` fills a
  ceiling: a 25 000-parameter feedforward trains slower than the unconstrained
  8 970-parameter default. Sizing the ceiling to the unconstrained default
  (10 000) is what actually bounded the cost. **A ceiling is an upper bound, and
  a run that wants cheap cells must declare a small one — not a large one.**
- **`_fit_geometry` builds geometry ~log₂(budget) times per cell**, inside the
  space filter as well as the evaluator. Measured at 10–100 ms per cell today,
  which is invisible against training; it is the first thing to become a problem
  if a future plan filters millions of cells.
