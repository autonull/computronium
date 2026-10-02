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

### D1 — The evaluator is a placeholder (the critical path)

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

### D7 — The report renders statistics, not claims

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

### 3.1 One cell, end to end, for real

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

### 3.2 Typed `RunSpec`

Pydantic v2 at the I/O boundary, mirroring frozen dataclasses internally
(AGENTS.md data-modelling; ceec-core precedent). Declares: task, objective
names, the **axis subsets and hyperparameter domains to search** (or "all"),
constraints, fidelity, seeds, epochs, batch limit, budget, policy, seed.
Serializes to the `runs.spec` JSON column; versioned; diffable.

**Gate:** a bad spec fails naming the offending field; two specs diff cleanly
(TODO43 **R41**); a run reproduces from its spec alone.

### 3.3 Spec-driven space

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
  generating operation — cannot coexist with anyway.

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

### 3.5 Claims, evidence, limitations in the report

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
| 0 | imports + `comp` exit codes | ~35 s | every commit |
| 1 | the shard you touched | ~2 min | every commit |
| 2 | gallery figure lock | 7 s | demo-adjacent |
| 3 | one `testpaths` directory | 15 s – 2 min | round close |
| 4 | all four + `tests/acceptance` | ~10 min | release candidate |
| — | `pytest -m demo` | ~1 h | re-pinning the gallery only |

**Never `pytest tests/`** — it bypasses `testpaths` and hard-killed twice at
test 873/3699. `-n 4` is already in `addopts`.

Standing rule from TODO45: a test run must be *priced before it is launched*,
and a suite that is too slow to run is a defect in the suite, not a discipline
problem.

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
