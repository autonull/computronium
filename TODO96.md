# TODO96 — Truth, Then Capability

**Status:** 2026-11-19 · drafted after the 57-row screen (TODO95 §5), the
first external verification, and the test inventory below. This is the plan
between "the map records" and "the map decides".

**One sentence:** The primitive layer is a documented adapter with a large
contract suite; it is not a verified capability. Almost no test and no gate asks
whether a primitive learns, the published box measures 27 primitives that are
inert and 11 that sit at chance, and 235 "kernel parity" tests pass without
requiring a real kernel. TODO96 makes every row truthful, every
primitive runnable on a real task at its own box, and every comparison cheap
enough to decide.

---

## 1. What the artifacts actually say

### 1.1 The inventory

| Fact | Number |
|---|---:|
| Primitives | 75 |
| Axis split | credit 19, update 18, geometry 12, substrate 10, dynamics 8, plasticity 8 |
| Available (has a spec and an axis row) | 73 (2 declared gaps) |
| Screen status | 57 measured, 6 defect, 12 refused |
| Binding status | 30 bound, 27 inert |
| Bound rows below 0.5 | 11 |
| Bound rows 0.5–0.85 | 7 |
| Bound rows at or above 0.85 | 12 |
| Rows with no bound, usable result | 45 (27 inert + 12 refused + 6 defect) |
| Reference only | 62 |
| Kernel verified | 11 |
| Kernel unverified | 2 |
| Primitive task families screened | 1 (vision, on MNIST) |
| Declared task families | vision 67, sequence 31, continual 22, graph 10, tabular 9, rl 8, neuromorphic 6, scientific 4, lm 2 |
| Available tasks | 30 |
| Base boxes | 2 (vision, tabular) |
| Test files | 579 |
| Test functions | 3,479 |
| Test functions in duplicate clusters | 721 (21%) |
| Test files that never call `backward`, `optimizer.step`, or `fit` | 464 of 579 |
| Test files that assert a loss decrease | 9 |
| Test files that assert finiteness | 124 |
| Test files mentioning a primitive ID | 94 |
| Generated test files / tests | 96 / 182 |
| Algorithm test files / tests | 84 / 258 (21 directories × 4 files) |
| Lock/protocol tests | 987 |
| Kernel-parity tests that pass (a real kernel is not required) | 235 |
| Kernel-parity tests that fail | 2 (`hybrid`, a `computtronium` typo) |

The repository-wide 29,423 `.py` files are mostly `.venv` (26,187). The
source tree is 2,338 files; `build/` holds 898 stale copies. The test tree is
579 files. The count was never the evidence; the kind of test is.

### 1.2 The rows that matter

`comp verify` says "held (measured)" for these:

| primitive | val_acc | control | what the verifier checked |
|---|---:|---:|---|
| `credit.target_inversion` | 0.1195 | 0.8908 | box, ruler, control, replay hash |
| `geometry.conv` | 0.1217 | 0.8908 | box, ruler, control, replay hash |
| `credit.homeostatic` | 0.1348 | 0.8908 | box, ruler, control, replay hash |
| `substrate.digital` | 0.8943 | 0.8908 | box, ruler, control, replay hash |
| `update.adam` | 0.9080 | 0.8908 | box, ruler, control, replay hash |

`target_inversion` clears the published bar (0.1060) and is "held". It is
0.77 below the control (0.1195 vs 0.8908). `digital` is "held" while varying the base
substrate; the cell is the base. `homeostatic` is error-blind; chance is its
contract, not a defect. The verifier is doing exactly what it was written to
do: check that a row exists, not that it is useful.

### 1.3 The missing rows

- All 57 screens are on MNIST. No primitive declares `mnist`; 67 declare
  `vision`, and the family filter maps `mnist` to vision. That is legal, but
  it is one task family out of nine.
- `sequence` (31 primitives), `continual` (22), `graph` (10), `tabular` (9),
  `rl` (8), `neuromorphic` (6), `scientific` (4), `lm` (2) have zero screens.
- Only vision and tabular have a calibrated base box. The other seven
  families have no control, no bar, no cost model, and no claim.
- Eight refusals are task-family mismatches, not primitive failures:
  `eligibility_prop`, `rtrl_reference`, `unbiased_rtrl`, `bayesian_online`,
  `cascade_synapse`, `synaptic_intelligence`, `closed_form_ridge`, `quantum`.
- Two refusals are cost caps (`natural_gradient`, `diffusion`).
- Two refusals are declared no-ops (`rule_state`, `substrate_coupled`).
- Five of the six defects are parameter ceilings, not learning failures:
  `surrogate`, `attention`, `causal_transformer`, `routing`, `tile`.
- One defect is a real shape bug: `graph` feeds 32 node rows to a 2-node edge
  index.

---

## 2. Why thousands of tests did not catch it

A test can only see what it asserts. The suite asserts the contract; the
screen asserts existence; no gate asserts capability.

### 2.1 The nine causes

1. **The tests measure the contract, not the capability.** 464 of 579 files
   never call `backward`, `optimizer.step`, or `fit`. 124 assert finiteness;
   9 assert that loss decreases. A primitive that returns finite zeros passes.
2. **The kernel gate is self-referential.** For a stub, `kernel.step`
   calls `reference.step`; `test_kernel_parity` compares the reference to
   itself. For a wrapper, it compares an acceleration kernel. Either way, the
   gate never asserts that a kernel exists. `hybrid` fails only because its
   entrypoint spells `computtronium`. Several of the 11 `kernel_verified`
   statuses are unearned; the status is not a reliable indicator.
3. **The verifier checks fields, not viability.** `verify_row` requires a box,
   ruler, control, replay hash, and a measurement. `target_inversion` at 0.1195
   carries all five; it is held. A near-chance row and a useful row are the
   same status.
4. **The map counts inert rows as measured.** 27 of 57 measured rows are
   `inert`: all 9 substrates, all 14 updates, 2 error-blind credits, 1
   instantaneous dynamics, 1 null plasticity. The cell measures the
   companions, not the varied primitive. The headline says "57 measured".
5. **The published box is rung 1 only.** 1 epoch, 1 seed, batch 32, 375
   batches, 150k parameters. It answers "does it execute", not "does it
   learn". 11 bound rows are at chance; none of them had a 3-point ladder in the
   published map. Rung 1 is a survival check, not a verdict.
6. **One task family is measured.** Every screen is MNIST. A sequence
   primitive, a graph primitive, an RL primitive, and a spiking primitive
   cannot show their mechanism on a vision task. The 7 other families have no
   base box and no control.
7. **The tests are templated per name.** 96 generated files are the same two
   tests with the primitive name changed. 84 algorithm files are four
   templates across 21 algorithms. 987 lock tests repeat the same registry,
   legality, and surface predicates per axis. The count grows; the information
   does not.
8. **The reference layer is an adapter.** 56 of 75 `reference.py` files
   delegate directly to `computronium.ontology`; 8 more delegate through
   `make_reference_step`. The test validates the adapter and the ontology, not
   a standalone implementation. 75 `cases.py` files are
   "intentionally small" microbenchmarks (the common case is 2×4); they are
   not task cases.
9. **The ruler is wrong for three axes.** A substrate needs bitwidth, energy,
   or spike timing, not accuracy alone. An update needs its own step size. An
   error-blind credit cannot be judged by accuracy. The binding conditions
   say this; the published map uses one ruler for all six axes.

### 2.2 What a green test proves today

| Green result | It proves | It does not prove |
|---|---|---|
| `test_state_remains_finite` | Outputs are NaN/Inf-free | The output learns |
| `test_deterministic_under_fixed_seed` | Two calls match | The call is useful |
| `test_kernel_parity` | The fallback matches itself | A kernel exists |
| `test_reference_step_returns_dict` | A dict has a `loss` key | The loss moves |
| `comp verify` | The row has five fields | The row is viable |
| `test_legality_compile_lock` | A tuple compiles | The tuple trains |
| `test_registry_completeness_lock` | The registry lists the name | The mechanism acts |

The suite is a **contract conformance suite**. That is useful, but it cannot
answer the research question. The map was supposed to be the integration
measure; it became a second contract suite with a replay hash.

---

## 3. Is there massive redundancy? Yes — in templates, not only copies

**Verdict:** There is massive *template* redundancy and massive *misplaced*
coverage. It is not 3,000 copies of one test: most test bodies are
structurally unique. But 21% are exact structural duplicates, 96 generated
files contain only two test bodies, 84 algorithm files contain four, and 987
"lock" tests re-assert the same axis-level predicate per name. The deeper
redundancy is that the suite repeats the same contract question 75 times and
never asks the capability question once.

### 3.1 Where the redundancy is

| Layer | Files | Tests | Redundancy | Cause |
|---|---:|---:|---|---|
| `tests/property/generated` | 96 | 182 | Exact modulo the primitive name; two bodies | Generator copies a template per primitive |
| `tests/algorithms` | 84 | 258 | Four templates × 21 algorithms | One conformance suite copied per algorithm |
| `tests/property` (non-generated) | 195 | 1,566 | 987 lock tests; repeated registry/legality/surface predicates | Per-axis assertion repeated per primitive |
| `tests/unit` | 92 | 896 | Repeated schema, config, and wiring checks | Per-module copy |
| `tests/primitives` | 9 | 28 | 28 contract tests for 75 primitives | Contract is axis-level, not primitive-level |
| `tests/integration` | 57 | 249 | Demo variants repeat the same composition | One demo per axis, not one per primitive |
| `tests/acceleration` | 15 | 118 | The same parity/skip pattern | Ladder repeated |
| `computronium/primitives` | 300+ | — | 75 × (spec + cases + reference + kernel + init) | Wrapper per primitive |

The wrapper duplication is structural: 75 `reference.py` files of 20–90 lines,
75 `cases.py` files of 20–120 lines, 75 `kernel.py` files of 20–190 lines. 36
kernels are 20–30 lines; 0 primitive `kernel.py` files contain their own
`@triton.jit`; 73 import Triton, and at least three of the 11 "verified"
kernels fall back. The `spec.py` files are the one non-redundant layer:
every field is filled, and the equations/invariants are the reference.

### 3.2 What is useful and must survive

1. **Mechanism locks** — a test that fails when the mechanism is removed:
   legality compile, single-source inventory, binding condition, box identity,
   screen-has-no-verdict, registry completeness, extension path.
2. **Analytic checks** — gradient equivalence, energy descent, closed-form
   solution, conservation, settle convergence, one-step fingerprint.
3. **Capability checks** — beats chance / beats the trivial predictor, with a
   control and a seed count.
4. **Cross-axis composition** — one end-to-end demo per axis pair, not per
   primitive.
5. **Governance** — CEEC ledger, preregistration, schedule, budget, evidence
   store.

Everything else is a candidate for merge or deletion.

### 3.3 Consolidation plan

| Current | Target | Action |
|---|---|---|
| 96 generated files / 182 tests | 1 file / 75 parameterized cases | Delete 95 files; one `test_primitive_invariants.py` over `PRIMITIVES` |
| 84 algorithm files / 258 tests | 1 conformance file + 1 analytic test per algorithm where distinct | Merge the 4 templates into `test_algorithm_conformance.py`; keep 3–5 semantic tests per algorithm |
| 987 lock tests | 6 axis contract files / ~150 cases | One `test_axis_contract.py` with `@pytest.mark.parametrize` over the axis registry |
| 75 `cases.py` microbench files | 1 `cases/_common.py` + 1 `make_task_case` per primitive | Keep `make_unit_case` for parity; build task cases from the task registry |
| 75 `kernel.py` stubs | 1 `kernel_status` field + real kernels only where measured | Demote wrappers; add a kill test that makes the reference raise |
| 75 `reference.py` adapters | 75 real references with a source-of-truth docstring and `fingerprint` | Keep the delegation only where the ontology is the canonical source; add the contract test |
| 57 integration demos | ~20 axis/demo end-to-end tests | Delete duplicate demo variants; keep one per axis pair and one full six-axis |
| 75 per-primitive semantics tests | 75 × 3 tests | Keep: deterministic + analytic + one-step capability |

**Target:** 579 files → ~150; 3,479 tests → ~1,300; 0 exact duplicate bodies;
0 tests that pass with a stub; every kept test has a named decision and fails
when its mechanism is removed. The target is not a coverage number. The target
is "one test per mechanism per axis, plus the irreducible per-primitive core".

### 3.4 The five rules for a kept test

1. **Name the decision.** A test that cannot name the claim it decides is
   deleted. "It returns a dict" is not a decision.
2. **Remove the mechanism, the test must fail.** If replacing the reference
   with a stub still passes, the test is a comment. Add the kill check.
3. **One axis predicate, one parameterized test.** The data varies; the body
   does not. A second copy per primitive is deleted.
4. **A capability test needs a control and a seed count.** Finiteness is a
   precondition, not a capability.
5. **A test may be slow only if it buys a rung.** A 1-epoch screen is cheaper
   and stronger than 1,000 shape assertions.

### 3.5 The audit

Add `scripts/audit_tests.py` (or `comp audit tests`) with three checks:

- **Duplicate bodies:** normalize names/constants and fail on a cluster
  larger than 1 unless the file is on the allow-list (the per-primitive
  semantic core).
- **Stub kill:** monkeypatch the reference to raise; the kernel test must
  still pass only if a real kernel path is selected.
- **Empty test:** a test with no assertion or only `assert result is not None`
  is flagged; the allow-list names the intentional smoke tests.

The audit is a gate, not a report: exit 1 names the first duplicate or the
first stub-passing test.

---

## 4. What "fixed" means: the reference contract

A primitive is **ready** when all ten clauses hold. Ready is not SOTA; ready
means a user can import it, read it, run it on a declared task, and trust its
row.

1. **One source of truth.** `spec.py` owns the equations, invariants,
   capability card, task families, and accepted parameters. The ontology class
   is the canonical implementation or the spec names the adapter. No second
   table re-derives a field.
2. **A real reference.** `reference.py` is deterministic, documented, runs on
   CPU and GPU, and returns a typed `StepResult` (weights, activations,
   metrics, state). A 20-line adapter is allowed only when its docstring names
   the ontology source and a `fingerprint(case)` proves the call.
3. **Task-shaped cases.** `make_case(task_id, seed, box)` builds a case from
   the task's input shape. `make_unit_case(seed)` is the 2×4 parity case. The
   integration path never uses the microbenchmark case.
4. **Analytic invariants.** The tests check the equations: gradient
   equivalence, energy non-increase, closed-form solution, conservation,
   settle convergence, or a one-step parameter fingerprint. Shape/finiteness
   are preconditions, not the test.
5. **A one-step fingerprint.** A hash of the weights/activations after one
   step, with the seed and box, is reproducible across processes and devices.
6. **A capability floor.** On at least one declared task family, the
   primitive beats the majority/chance predictor with a control and a
   pre-registered n. The floor is recorded with the box, not as a global claim.
7. **A measured cost.** Walltime, parameter count, memory, and energy (when
   available), with the ceiling. A row over the ceiling is a capability gap
   with the larger box that closes it, not a defect of the mechanism.
8. **An honest status.** `kernel_status` is one of `implemented`, `wrapper`,
   `stub`, `absent`. `kernel_verified` requires `implemented` and a kill test.
   `measured` requires a bound cell, a rung, and a replay hash.
9. **A verdict.** A row carries `rung` (0–4) and `verdict` (`viable`,
   `near_chance`, `defect`, `capability_gap`, `contract`, `refused`). The
   screen may record; the assessment names the verdict.
10. **A method card.** `docs/primitives/<axis>/<name>.md` or the generated
    method card carries the equations, invariants, cost, task families, and
    one measured row.

### 4.1 The code surface

Small, consolidated additions; no second table.

```python
# computronium/acceleration/spec.py
class ImplementationSpec:
    ...
    kernel_status: Literal["implemented", "wrapper", "stub", "absent"] = "absent"
    task_families: tuple[str, ...] = ()
```

```python
# computronium/experiment/sec_census.py
@dataclass(frozen=True, slots=True)
class PrimitiveCensusEntry:
    ...
    rung: int = 0
    verdict: str = "unmeasured"
    kernel_status: str = "absent"
```

```python
# computronium/experiment/sec_extension.py
def _row_problems(row, status):
    ...
    if status == "measured":
        if row.get("binding") != "bound":
            problems.append("inert row cannot be a capability result")
        if row.get("verdict") in {"near_chance", "defect", "refused"}:
            problems.append(f"verdict {row['verdict']} is not a held row")
```

```python
# computronium/experiment/schema/task_registry.py
@dataclass(frozen=True, slots=True)
class TaskSpecEnriched:
    ...
    task_families: tuple[str, ...] = ()  # explicit; never inferred from domain
```

`_FAMILY_OF_DOMAIN` is deleted. `task_families` is the one source. A task may
serve vision and continual (`split_mnist`), or sequence and continual
(`copy_task`); the old table could not express that, so continual primitives
were refused on every task.

---

## 5. The repair program

### 5.1 P0 — Truth pass (cheapest, first)

**Work:** add `rung`, `verdict`, `kernel_status`; fix the `computtronium`
typo; demote every `kernel_verified` row whose kernel is a stub; audit the rest
with the kill test;
regenerate the map with both boxes (`--own-knobs` and base); make
`comp verify` distinguish "measured" from "viable".

**Gate:** `comp verify` exits 1 on `target_inversion` (0.1195) and
`conv` (0.1217); `comp verify` prints "measured (near chance)" and "measured
(inert)"; `comp verify` exits 1 on `graph`; 0 rows with `kernel_verified`
whose kernel calls `reference.step`; 0 rows with `measured` and no `rung`.

**Done:** the map has no false green row. This is a one-session change.

### 5.2 P1 — Reference contract (all 75)

**Work:** one protocol, one `make_task_case`, one `StepResult`, one
`fingerprint`; per-primitive: real `cases.py` task case, real `reference.py`
or a documented adapter, 3 semantic tests, 1 analytic invariant, 1 one-step
capability test on a cheap task.

**Gate:** 75/75 one-step deterministic; 75/75 analytic invariant; 75/75
`reference_step` returns a typed result; 75/75 a task case builds from the
task's input shape; 0 `cases.py` whose only case is 2×4.

**Done:** `uv run python -m pytest tests/primitives -q` is 75 × 3 tests, and
a stranger can import one primitive and run one step from the docstring.

### 5.3 P2 — Instruments (the 27 inert)

**Work:** publish two boxes. The **viability box** runs each varied axis at
its own declared defaults (`--own-knobs`), companions at the base. The
**comparison box** keeps one fixed knob for all. The map carries both; the
headline uses the viability box for the axis verdict, the comparison box for
the interaction.

For substrate, add a substrate-sensitive ruler: `bitwidth`, `energy_per_batch`,
`spike_timing`, `memory_mb`. The substrate row's ruler is a tuple, not
`val_acc`; the capability is "accuracy at a bitwidth/energy", a Pareto point.

For update, `--own-knobs` is already wired; run it. For error-blind credits,
the row is a `contract` row, not a capability row; run them on a label-free
task or remove them from the capability table.

**Gate:** 27 inert rows become 27 explicit rows: each is `bound` at its own
box, or `contract`, or `capability_gap` with the missing instrument named.
0 rows labeled "measured" while `inert`.

**Done:** the headline is "30 bound + 27 instrumented/contract", not
"57 measured".

### 5.4 P3 — Defect repair (the 6 defects + 11 near-chance bound)

**Work:** the defect probes, cheapest first:

| Row | Current | First probe | If it fails |
|---|---:|---|---|
| `geometry.graph` | crash | batch the node rows with `edge_index`/`batch`; add the screen-path test | fix the batched path |
| `credit.pc_alm` | 0.1224 | one-step gradient vs `credit.gradient`; check readout wiring | fix readout |
| `dynamics.error_predictive_coding` | 0.1242 | one-step settle vs `predictive_settling`; check target/error | fix settle |
| `geometry.conv` | 0.1217 | one-step gradient vs `feedforward`; check padding/stride | fix forward |
| `credit.target_inversion` | 0.1195 | 3-point ladder: target steps, lr, line search | tune or defect |
| `credit.random_projections` | 0.1333 | 3-point ladder: feedback scale, lr | tune or defect |
| `credit.forward_tangent` | 0.1653 | 3-point ladder: lr, JVP scale | tune or defect |
| `credit.zeroth_order` | 0.1665 | 3-point ladder: perturbations, epochs | tune or defect |
| `credit.local_contrastive` | 0.1989 | 3-point ladder: phases, lr | tune or defect |
| `credit.local_goodness` | 0.3403 | 3-point ladder: positive/negative passes | tune or defect |
| `plasticity.conflict_adaptive` | 0.2882 | run on a continual task, not MNIST | tune or defect |
| `dynamics.spike_integration` | 0.1324 | 3-point ladder: epochs 1/3/10, reset | tune or defect |

The five parameter-ceiling rows (`surrogate`, `attention`,
`causal_transformer`, `routing`, `tile`) are **capability gaps**, not
defects: record the smallest legal box that fits the declared budget
(600k/1M), measure it, and publish "requires N parameters at this task". A
primitive whose design needs 628k parameters is not broken at 150k; the
budget is the instrument.

**Gate:** every one of the 6 defects is closed or converted to a
`capability_gap` with a measured larger box; every one of the 11 near-chance
rows is triaged into `tuned`, `defect`, `capability_gap`, or `contract`, with
a named mechanism. A 1-seed failure is never an algorithm verdict.

### 5.5 P4 — Family bases (the 12 refusals + 7 missing families)

**Work:** add explicit `task_families` to the task registry; calibrate a base
box and a 3-seed control for every family.

| Family | Base task | Why | Status |
|---|---|---|---|
| vision | mnist | existing | calibrated |
| tabular | iris | existing | calibrated |
| graph | cora | cheapest graph task; 7 classes, bar 0.316 | add |
| sequence | char_ngram | cheapest sequence task; 27-way, bar 27.0 | add |
| continual | copy_task | memory domain; explicit family | add |
| rl | cartpole | cheap, bar 20.0 | add |
| scientific | lorenz_state | cheap, bar 67.415 | add |
| neuromorphic | spiking_mnist (new) | no task exists | add task + base |
| lm | tiny_shakespeare | expensive; pre-register | add, expensive |

`split_mnist` and `sequential_mnist` are vision tasks that also test a
continual/sequence protocol; they get `task_families=("vision","continual")`
and `("vision","sequence")`. The family is a task attribute, not a domain
inference.

The two gaps:

- `rule_state`: implement `modulate()` in the standard train step; test that
  the post-step geometry differs from `null` by one-step fingerprint. If the
  operator is intentionally not applied, retire the primitive from the
  capability inventory and keep it as a declared no-op.
- `substrate_coupled`: make the substrate carry a separate state through the
  joint transition; test the one-step fingerprint. Or retire.

The two cost caps:

- `natural_gradient`: reduce the model to a diagonal Fisher or a smaller
  parameter set; measure 1 step, then 1 epoch.
- `diffusion`: settle steps 30 → 10 (the measured optimum), then 1 epoch.

**Gate:** 9/9 families have a base box, a 3-seed control, a bar, and a measured
cost; 12/12 refusals either run on a declared family or carry a capability
gap with the primitive/feature that closes it.

### 5.6 P5 — Multi-family screen

**Work:** screen every primitive on every family it declares, cheapest first.
The row is `(primitive, family, box)`, not `(primitive)`. The map keeps the
vision row and adds the others; a primitive with 6 declared families has 6
rows, each with its own control and ruler.

Order: vision and tabular (existing) → graph (cora) → sequence (char_ngram) →
continual (copy_task) → rl (cartpole) → scientific (lorenz) → neuromorphic
(spiking_mnist) → lm (tiny_shakespeare).

**Gate:** every primitive has a bound measured row in a declared family, or a
contract/capability-gap row with the feature that closes it; every family with
at least 4 declared primitives has 4 measured (`lm` measures its 2); 0 rows
screened on a family the primitive does not declare; 0 rows with one ruler for
two different axes.

**Done:** `comp verify --primitive X --slice <family>` holds for every
declared family, and a user can ask "which primitive should I use for a
sequence task?" and get an answer.

### 5.7 P6 — Ladder and claims

**Work:** the 3-point ladder for every near-chance and mid row; 3-seed
confirmation for the 15 best; 5-seed paired claims for 5 primitives with a
pre-registered threshold and CI.

- Rung 0: conformance (P1).
- Rung 1: 1 seed, 1 epoch, does it train (loss or val_acc moves).
- Rung 2: 3-point ladder on the primary knob, 1 seed each, 1 confirmation.
- Rung 3: 5 paired seeds, fixed `n_max`, no peeking, CI.
- Rung 4: matched boxes and budgeted HPO; competitiveness only.

**Gate:** 0 claims from a 1-seed cell; 0 "viable" from a rung-1 failure; 5
claims with a CI and a pre-registration committed before the first seed.

### 5.8 P7 — Library polish

**Work:** method cards, examples, public API, `comp verify` docs. The
primitive is importable as:

```python
from computronium.primitives.credit_assignment.pepita import (
    SPEC, make_case, reference_step, kernel_step,
)
```

The docstring is the method card; the equations are in `SPEC.equations`; the
task families are in `SPEC.task_families`; the measured row is in the map.

**Gate:** 75/75 importable; 75/75 method card generated; 75/75 example runs
from the docstring; 0 docs table with a status the map does not carry.

---

## 6. The experimental process

### 6.1 The matrix

The unit is a **comparable cell**: `(primitive, family, box, ruler, seed,
control, replay)`. The map is a set of cells, not a set of primitives. A
primitive with 3 declared families has 3 rows; a family with 10 primitives
has 10 rows.

### 6.2 The two boxes

| Box | What varies | What it answers | Published as |
|---|---|---|---|
| Viability | The varied axis at its own declared defaults; companions at the base | Can this primitive act on this axis? | Headline row |
| Comparison | One fixed knob for all primitives | Is A better than B at a matched knob? | Interaction row |

The current map published the comparison box for every row and called it
viability. From TODO96, every screen publishes both: `map.json` carries
`viability` and `comparison` per row; the method card names which one the
claim reads.

### 6.3 The rungs and the stop rule

| Rung | Decision | Cost | Stop |
|---|---|---|---|
| 0 | Is it wired? | seconds | A defect or a conformance fail stops |
| 1 | Does it train? | 1 seed, 1 epoch | A crash or a flat loss is a defect probe |
| 2 | Is it viable across its knob? | 3 points × 1 seed + 1 confirmation | The best point above chance is a coordinate; all fail is a defect/gap |
| 3 | Is the effect real? | 5 paired seeds, fixed `n_max` | CI or `n_max` |
| 4 | Is it competitive? | Matched boxes, budgeted HPO | Threshold |

A 1-seed cell is a screen, not a result. A 3-seed confirmation is not a claim.
A 5-seed paired comparison with a pre-registered threshold is a claim. The map
carries the rung; the claim carries the CI.

### 6.4 The instruments

- `--own-knobs`: the viability box (already wired; publish it).
- Substrate ruler: `(val_acc, bitwidth, energy_per_batch, memory_mb,
  spike_timing)`; a Pareto point, not a scalar.
- Error-blind credits: `contract` rows, not capability rows.
- Task-family table: explicit `task_families`, no domain inference.
- Cost model: measured per-cell walltime; a 60s cap is a bootstrap cap, not a
  ranking. The watchdog is 2× the measured cell.

### 6.5 The commands

```bash
# One axis at its own defaults (the viability box)
uv run python -m computronium.experiment.sec_loop \
    --track P0 --out results/sec --own-knobs --axis update

# One family, full census
uv run python -m computronium.experiment.sec_loop \
    --track P0 --out results/sec --breadth full --axis credit

# The external check
uv run comp verify --primitive primitive.credit_assignment.target_inversion \
    --slice vision

# The targeted primitive tests
uv run python -m pytest tests/primitives -q

# The consolidated property suite
uv run python -m pytest tests/property -q
```

Promote the module to `comp sec` as one command tree; do not add a second CLI.
`comp verify` gets a `--verdict` flag: `measured` (fields only) or `viable`
(bound + rung + control-relative floor). The default is `viable`; the old
behavior is `--verdict measured` for a recorder.

### 6.6 The artifacts

- `results/sec/map.json` — one row per `(primitive, family, box)`, with
  `rung`, `verdict`, `viability`, `comparison`, `kernel_status`.
- `docs/sec/map.md` — generated from the map; no hand edits.
- `configs/preregistrations/<slug>.json` — committed before the first seed.
- `docs/primitives/<axis>/<name>.md` — the method card.

---

## 7. Sessions

| Session | Decision | Work | Gate | Stop |
|---|---|---|---|---|
| S1 | The suite tells the truth | P0 truth pass; add `verdict`/`rung`/`kernel_status`; fix `computtronium`; demote stub kernels; extend `comp verify` | 0 false green; 0 near-chance "held" | Any `comp verify` that holds a 0.1195 row |
| S2 | The test debt is paid | P1 reference contract; consolidate 96/84/987; add the audit | 579→~150 files; 0 duplicate bodies; 0 stub-pass | A duplicate cluster > 1 or a stub-pass |
| S3 | The 27 inert rows are instruments | P2; publish both boxes; substrate ruler; error-blind contract rows | 0 inert headline; 27 explicit rows | A row still labeled "measured" while inert |
| S4 | The 6 defects are named | P3; graph batch; conv/pc_alm/EPC; ceilings as capability gaps; 11 near-chance triaged | 6 closed/gap; 11 triaged; 0 algorithm verdicts from 1 seed | A defect with no named mechanism |
| S5 | The 7 missing families have a base | P4; explicit `task_families`; 7 base boxes; 2 gaps; 2 cost caps | 9/9 families calibrated; 12/12 refusals resolved | A family with no control or bar |
| S6 | The map answers across tasks | P5; multi-family screen; one row per family; every primitive at least one family | 75/75 bound/contract/gap; every family with ≥4 declared primitives has ≥4 measured | A primitive with only a vision row |
| S7 | The claims are earned | P6; 3-point ladder; 3-seed confirmation; 5 paired claims | 5 claims with CI; 0 1-seed claims | A claim without a pre-registered `n_max` |
| S8 | The library is ready | P7; method cards; examples; API; docs | 75/75 importable; 75/75 card; 75/75 example | A card that does not match the map |

S1 and S2 are cheap and unblock trust. S3 and S4 are the primitive repair.
S5 and S6 are the experiment. S7 is the science. S8 is the product.

---

## 8. Definition of done

1. **75/75 reference contract:** deterministic, documented, typed result,
   task-shaped case, analytic invariant, fingerprint.
2. **0 false green rows:** no `kernel_verified` row whose selected kernel path
   is a stub; no `measured` row with `binding=inert`; no `held` row at chance.
3. **30 bound rows triaged:** 11 near-chance → `tuned`, `defect`,
   `capability_gap`, or `contract`; 7 mid → ladder; 12 clear → confirmation.
4. **6 defects closed or converted:** 5 parameter ceilings → capability gaps
   with a measured larger box; `graph` → fixed batched path.
5. **12 refusals resolved:** 8 family → a declared family with a base box;
   2 gaps → implemented or retired; 2 cost caps → reduced step or larger
   budget.
6. **9/9 families calibrated:** a base task, a 3-seed control, a bar, a cost,
   and a replay.
7. **75/75 primitives carry a bound row, a contract row, or a capability gap
   in a declared family;** every family with ≥4 declared primitives has ≥4
   measured (`lm` measures its 2).
8. **5 claims:** 5 paired seeds, fixed `n_max`, pre-registration, CI, and a
   verdict (`superior`, `equivalent`, `inferior`, or `inconclusive`).
9. **Test debt:** 579→~150 files, 3,479→~1,300 tests, 0 exact duplicate
   bodies, 0 stub-pass, 0 test without a named decision.
10. **Map published:** `results/sec/map.json` and `docs/sec/map.md` regenerate
    from the same source; every row carries its box, ruler, control, rung,
    verdict, cost, and replay hash.

A ticket closes on a claim, a named verdict, or a capability that now works. A
session that lands a primitive or fixes a blocking defect closes it even when
no number moves. A session that only renames a status does not.

---

## 9. What we stop doing

- Calling a finite output a capability.
- Calling a kernel parity test evidence when the kernel calls the reference.
- Calling a 1-seed cell a result.
- Calling an inert cell a measurement of its axis.
- Calling a parameter ceiling a broken mechanism.
- Calling a task-family mismatch a refused primitive.
- Calling a near-chance row an algorithm verdict before the ladder.
- Calling a test count a coverage argument.
- Deleting tests for their own sake; the target is one test per mechanism,
  not fewer assertions.

**Excluded possibilities:** "the primitives are unfixable", "the tests are all
useless", "a bigger parameter budget is a fix", "one seed is enough", "MNIST
is the capability", "more tests will catch it". Each has a named test or a
measured box in this plan.

---

## Appendix A — primitive action register

Legend: **R** reference contract, **K** kernel truth, **I** instrument,
**E** execution repair, **CAP** capability gap with a measured larger box,
**L** ladder/triage, **F** family base, **G** gap implement/retire, **C**
claim-ready. Every row carries R+K.

### Credit (19)

| primitive | status | binding | val_acc | action |
|---|---|---|---:|---|
| `eligibility_prop` | refused | — |  | R+K+F |
| `forward_tangent` | measured | bound | 0.165 | R+K+L |
| `gradient` | measured | bound | 0.894 | R+K+C |
| `homeostatic` | measured | inert | 0.135 | R+K+I |
| `hybrid` | measured | bound | 0.737 | R+K+L |
| `local_contrastive` | measured | bound | 0.199 | R+K+L |
| `local_goodness` | measured | bound | 0.340 | R+K+L |
| `local_supervision` | measured | bound | 0.777 | R+K+L |
| `pc_alm` | measured | bound | 0.122 | R+K+L |
| `pepita` | measured | bound | 0.894 | R+K+C |
| `random_projections` | measured | bound | 0.133 | R+K+L |
| `rtrl_reference` | refused | — |  | R+K+F |
| `score_function` | measured | bound | 0.732 | R+K+L |
| `surrogate` | defect | bound |  | R+K+E/CAP |
| `target_inversion` | measured | bound | 0.119 | R+K+L |
| `temporal_trace` | measured | inert | 0.122 | R+K+I |
| `thermodynamic_contrast` | measured | bound | 0.782 | R+K+L |
| `unbiased_rtrl` | refused | — |  | R+K+F |
| `zeroth_order` | measured | bound | 0.167 | R+K+L |

### Geometry (12)

| primitive | status | binding | val_acc | action |
|---|---|---|---:|---|
| `attention` | defect | bound |  | R+K+E/CAP |
| `causal_transformer` | defect | bound |  | R+K+E/CAP |
| `conv` | measured | bound | 0.122 | R+K+L |
| `feedforward` | measured | bound | 0.894 | R+K+C |
| `graph` | defect | bound |  | R+K+E |
| `nca` | measured | bound | 0.896 | R+K+C |
| `ntm` | measured | bound | 0.876 | R+K+C |
| `recurrent` | measured | bound | 0.897 | R+K+C |
| `routing` | defect | bound |  | R+K+E/CAP |
| `spatial_lattice` | measured | bound | 0.914 | R+K+C |
| `tile` | defect | bound |  | R+K+E/CAP |
| `tile_mesh` | measured | bound | 0.690 | R+K+L |

### Dynamics (8)

| primitive | status | binding | val_acc | action |
|---|---|---|---:|---|
| `diffusion` | refused | — |  | R+K+F |
| `energy_minimization` | measured | bound | 0.879 | R+K+C |
| `error_predictive_coding` | measured | bound | 0.124 | R+K+L |
| `instantaneous` | measured | inert | 0.894 | R+K+I |
| `lazy` | measured | bound | 0.877 | R+K+C |
| `pc_alm` | measured | bound | 0.640 | R+K+L |
| `predictive_settling` | measured | bound | 0.724 | R+K+L |
| `spike_integration` | measured | bound | 0.132 | R+K+L |

### Plasticity (8)

| primitive | status | binding | val_acc | action |
|---|---|---|---:|---|
| `closed_form_ridge` | refused | — |  | R+K+F |
| `conflict_adaptive` | measured | bound | 0.288 | R+K+L |
| `fast_weights` | measured | bound | 0.892 | R+K+C |
| `null` | measured | inert | 0.894 | R+K+I |
| `routing` | measured | bound | 0.868 | R+K+C |
| `rule_state` | refused | — |  | R+K+G |
| `substrate_coupled` | refused | — |  | R+K+G |
| `temporal_psi` | measured | bound | 0.885 | R+K+C |

### Substrate (10)

| primitive | status | binding | val_acc | action |
|---|---|---|---:|---|
| `analog` | measured | inert | 0.887 | R+K+I |
| `complex` | measured | inert | 0.891 | R+K+I |
| `digital` | measured | inert | 0.894 | R+K+I |
| `memristive` | measured | inert | 0.889 | R+K+I |
| `neuromorphic` | measured | inert | 0.878 | R+K+I |
| `noisy` | measured | inert | 0.891 | R+K+I |
| `optical` | measured | inert | 0.890 | R+K+I |
| `quantum` | refused | — |  | R+K+F |
| `sparse` | measured | inert | 0.885 | R+K+I |
| `ternary` | measured | inert | 0.871 | R+K+I |

### Update (18)

| primitive | status | binding | val_acc | action |
|---|---|---|---:|---|
| `adafactor` | measured | inert | 0.933 | R+K+I |
| `adam` | measured | inert | 0.908 | R+K+I |
| `bayesian_online` | refused | — |  | R+K+F |
| `cascade_synapse` | refused | — |  | R+K+F |
| `elastic_consolidation` | measured | inert | 0.626 | R+K+I |
| `euclidean` | measured | inert | 0.894 | R+K+I |
| `lion` | measured | inert | 0.926 | R+K+I |
| `local_adam` | measured | inert | 0.796 | R+K+I |
| `mean_norm` | measured | inert | 0.887 | R+K+I |
| `muon` | measured | inert | 0.949 | R+K+I |
| `natural_gradient` | refused | — |  | R+K+F |
| `ortho_adam` | measured | inert | 0.947 | R+K+I |
| `quantized_adam` | measured | inert | 0.102 | R+K+I |
| `riemannian_orthogonal` | measured | inert | 0.949 | R+K+I |
| `role_split` | measured | inert | 0.901 | R+K+I |
| `schedule_free` | measured | inert | 0.919 | R+K+I |
| `spectral_constrained` | measured | inert | 0.626 | R+K+I |
| `synaptic_intelligence` | refused | — |  | R+K+F |

---

## Appendix B — test consolidation map

| Group | Files now | Tests now | Files target | Tests target | Keep |
|---|---:|---:|---:|---:|---|
| `tests/property/generated` | 96 | 182 | 1 | 75 | One parameterized invariants file |
| `tests/algorithms` | 84 | 258 | 22 | 80 | One conformance file + one semantic file per algorithm |
| `tests/property` (locks/meta) | 195 | 1,566 | 40 | 320 | Axis contracts, legality, inventory, screen, CI, preregistration |
| `tests/unit` | 92 | 896 | 30 | 300 | Schema, config, store, validation, stability |
| `tests/integration` | 57 | 243 | 20 | 70 | One per axis pair, one six-axis, one store |
| `tests/acceleration` | 15 | 118 | 8 | 50 | Ladder, parity, kernel isolation |
| `tests/primitives` | 9 | 28 | 6 | 225 | One file per axis, parameterized; 3 tests per primitive |
| `tests/acceptance` | 9 | 53 | 6 | 35 | Extension path, public API |
| `tests/ceec` | 14 | 109 | 14 | 109 | Governance; keep |
| `tests/platform` | 6 | 17 | 6 | 17 | Packaging; keep |
| Other (`probes`, root) | 2 | 9 | 2 | 9 | Keep the probes; fold the root |
| **Total** | **579** | **3,479** | **~150** | **~1,300** | |

The target is a shape, not a quota. A group may keep more if every test fails
when its mechanism is removed. The audit decides, not the table.

---

## Appendix C — first commands

```bash
# 1. Reproduce the false green, so the plan starts from evidence.
uv run comp verify --primitive primitive.credit_assignment.target_inversion --slice vision
uv run comp verify --primitive primitive.geometry.conv --slice vision
uv run comp verify --primitive primitive.geometry.graph --slice vision

# 2. Prove the kernel gate is vacuous.
uv run python -m pytest tests/primitives/test_primitive_kernel_parity.py -q

# 3. Publish the viability box for the update axis (the instrument exists).
uv run python -m computronium.experiment.sec_loop \
    --track P0 --out results/sec --own-knobs --axis update

# 4. Re-screen the near-chance bound rows at their own defaults.
uv run python -m computronium.experiment.sec_loop \
    --track P0 --out results/sec --own-knobs --axis credit

# 5. After the truth pass, the gate must fail for the old green rows.
uv run comp verify --primitive primitive.credit_assignment.target_inversion --slice vision
# expected: refused: measured but near chance (0.1195 vs control 0.8908)
```
