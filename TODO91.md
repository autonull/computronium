# TODO91 — Surface completion (successor to TODO90)

**Status:** 2026-11-13 · base `e226694a` · TODO90 closed (breadth instrument,
B0–B10) · **this plan writes no claims and runs no search.**
Progress: S0 closed, S1 closed, S2 half-closed (see §3a).

**Mission:** Make the *implemented surface of the library* complete enough that
a future experiment — including HPO — can select any declared algorithm,
architecture, task, loss, metric, or legal combination without hitting an
unimplemented path. Coverage here means **implementation coverage**, not
measurement coverage:

> A surface entry is covered when (a) the code path exists, (b) one smoke
> command exercises it end to end, and (c) a lock fails if the entry
> disappears. Otherwise it is **declared unavailable** with the reason and the
> trigger that would build it.

TODO90 proved the measurement apparatus cannot lie. TODO91 ensures there is
enough apparatus to select from. Performance, quality, and comparisons are
explicitly out of scope: with no search and no held-out protocol, any number
produced now would be noise. The plan's deliverable is a **complete, honest
inventory**, not a result.

---

## 1. Measured starting point (2026-11-13)

| Surface | State | Evidence |
|---|---|---|
| Axis primitives | 9 substrates, 11 geometries, 8 dynamics, 7 plasticities, 10 credits, 12 updates = **57/57 exercised** | `comp coverage report --corpus` |
| Tasks | **26 registered and measured**; docs name 11 planned names and 4 contradictions | `comp coverage tasks`; `docs/readme/stability-eval.md` |
| Domains | 8 effective domain values hold a task; `lm` is an alias with none; **`continual` and `multitask` hold none** | `DomainType` vs `TaskRegistry` |
| Algorithms (spec) | **21 spec rows**, 21 package directories | `docs/generated/IMPLEMENTATION_MATRIX.md`; `computronium/algorithms/` |
| Algorithms (public) | **14 exposed** by `computronium.algorithms`; 7 reachable only through presets | `algorithms/__init__.py::_ALGORITHMS` |
| Algorithm/spec vocabulary | 64 spec rows (43 primitive + 21 algorithm); runtime axis names differ from spec IDs (`feedforward_dag`/`feedforward`, `photonic`/`optical`, `reverse_mode`/`gradient`, …) | spec registry vs `AXES_REGISTRIES` |
| Capabilities | **88 rows: 67 active, 21 unverified** (checkpointing, KV cache, async, multiprocess, DDP/FSDP, P2P, pipeline parallelism, transfer, warm-start, Pareto, …) | `CAPABILITIES_REGISTRY` |
| Objectives | **54 measured = 54 declared**; 2 task rows deferred (continual) | `comp coverage unmeasured` |
| Losses | task-declared `compute_loss` exists; the shared fallback is CE, and MSE is wired — no declared inventory | `core/losses.py`, `domains/*.compute_loss` |
| Corpus | 7,424 PASS cells / 439 stores / 0 unreadable; 0 undeclared pairs; 346 refused cells named | `comp coverage report --corpus` |

### Inventory gaps this plan exists to close

1. **7 algorithm packages are invisible.** `diffusion_eqprop`, `directed_ep`,
   `finite_nudge_ep`, `holomorphic_ep`, `momentum_eqprop`, `sparse_eqprop`,
   `ternary_eqprop` exist and are reachable through `core/presets.py` and
   `models/native/`, but `computronium.algorithms` does not expose them. A user
   selecting "all algorithms" gets 14 of 21.
2. **The spec inventory and the runtime registry use different names, and the
   matrix is incomplete.** Ten primitives are spelled differently on the two
   surfaces (`feedforward_dag`/`feedforward`, `photonic`/`optical`,
   `reverse_mode`/`gradient`, …), so the matrix cannot be joined to
   `AXES_REGISTRIES`; 15 more runtime coordinates (`conv`, `attention`,
   `adam`, `local_contrastive`, …) have no spec row at all. Three hand
   translations exist today. "All architectures covered" is unverifiable from
   either surface alone.
3. **Two entire domain classes have no task.** `CONTINUAL` and `MULTITASK` are
   declared domain types with no loaders, so `forgetting`/`backward_transfer`
   cannot be measured and no continual experiment can be composed.
4. **Planned and claimed tasks are prose, not rows.** Eleven planned names
   (`wikitext2`, `penn_treebank`, `mountain_car`, `lunar_lander`, `diabetes`,
   `california_housing`, `ett_h1`, and the four PDE tasks), plus four
   docs/runtime contradictions: `cifar100` and `svhn` are listed as implemented
   but are absent from `SUPPORTED_TASKS`; the scientific list names `pendulum`
   (which is the RL task) and `lorenz` (which no task registers), while the
   implemented name is `pendulum_state`.
5. **Docs claim architectures that do not exist.** The scientific domain
   advertises PINO, DeepONet and FNO; the timeseries domain advertises an
   LSTM family; the only LSTM in the tree is NTM's controller. No geometry
   implements any of these, and no row declares them unavailable.
6. **21 capabilities are unverified.** Some are optional (P2P cluster, service
   manager); some are prerequisites for any serious experiment (checkpoint/
   resume, multiplexed loading, multi-GPU, warm-start, Pareto report). None
   currently carries a build/retire decision.
7. **Loss coverage is implicit.** A task's loss is whatever its
   `compute_loss` returns; there is no declared inventory of supported losses,
   so a new task can silently add an untested objective.
8. **Two vocabularies for one measurement already bit us** (`perplexity` vs
   `val_ppl`, B8). The same class of defect exists at the API surface and is
   not locked.

---

## 2. Rules

Carried by `AGENTS.md` (one source per rule, every number carries its ruler,
declared is not inferred). This plan adds two:

> **A surface ticket closes on a smoke path or a named declaration.**
> "Exists in the tree" is not coverage; "registered" is not coverage. A row is
> covered only when one command exercises it and a lock fails if the row is
> deleted. An undeclared entry is a defect.

> **One name per primitive.** A spec ID *is* its runtime coordinate. An alias
> table, a hand translation, or a second spelling for the same mechanism is a
> defect, not a convenience. A mechanism with no coordinate is declared once,
> with a reason.

Non-goals for every ticket in this plan:

- no tuning, no search, no HPO, no pre-registered threshold;
- no performance/SOTA comparison, no paper figure;
- no new breadth of *measurement* (TODO90 owns that and is closed);
- no architecture or algorithm invented solely to make a number look better.

A defect found while covering a row is fixed only if it blocks the smoke path;
otherwise it is filed with a measured reason and a trigger.

---

## 3. Priority order

Ordered by what makes the selection surface trustworthy first, not by interest.

| # | Ticket | Deliverable | Cost | State |
|---|---|---|---|---|
| S1b | **Alias removal** | one spelling: rename 10 spec IDs + package directories + entrypoints; delete the alias table and `status.py` hand tables; identity join | 3–4 h | **next session** |
| S1c | **Spec/runtime bijection** | each of the 15 runtime-only coordinates gains a same-named primitive spec package | 4–6 h | open; follows S1b |
| S0 | **Inventory instrument** | one `comp` command joins spec rows, runtime axes, packages, tasks, domains, objectives, capabilities; zero `unknown` rows | 1 h | **closed** |
| S1 | **Algorithm surface** | every algorithm package is public or declared internal | 1–2 h | **closed; alias table must be removed by S1b** |
| S2 | **Architecture surface** | every geometry has a forward/step/param smoke; every runtime geometry has a spec row | 1 h | blocked on S1b/S1c; docs rows + smoke open |
| S3 | **Task surface** | planned tasks implemented or declared; `continual`/`multitask` gain one task each or a named retirement | 2 h | open (declared rows landed) |
| S4 | **Loss/objective surface** | declared loss inventory per task; continual objectives wired or retired | 1 h | open |
| S5 | **Capability surface** | all 21 unverified rows get a smoke test or `unavailable_reason` + trigger | 2 h | open (inventory classifies all 21 as declared) |
| S6 | **Combination smoke** | legal-coordinate matrix composes and trains one step with zero failures | 1–2 h | open |
| S7 | **Vocabulary/docs lock** | generated docs read from the inventory; one vocabulary locked | 30 min | open (joins landed; alias-free lock follows S1b/S1c) |

S0 is the instrument; **S1b removes every alias and S1c makes the spec matrix
complete**; S1/S2 make selection verifiable; S3–S4 complete the content; S6
proves combinations; S5 is infrastructure readiness; S7 prevents a second
vocabulary from returning.

### 3a. Progress log

**S0 — closed.** `comp coverage inventory [--format json] [--strict]` joins
the spec registry, `AXES_REGISTRIES`, algorithm packages, `SUPPORTED_TASKS`,
`DomainType`, `TaskRegistry`, `OBJECTIVES_REGISTRY`, and
`CAPABILITIES_REGISTRY` into one classified table (`inventory.py`). Measured
2026-11-13: **287 rows — 234 implemented, 53 declared, 0 unknown** (21
algorithms, 59 primitives, 41 tasks, 11 domains, 63 objectives, 88
capabilities, 4 architectures). Classification is path-backed: a row whose
smoke file disappears becomes `unknown`; only a recorded reason makes it
`declared`. Lock:
`tests/property/test_surface_inventory_lock.py` (10 tests), which also joins
the docs task list and the generated implementation matrix.

**S1 — closed.** The seven EQ variants are declared internal with their preset
factory (`algorithms/__init__.py::INTERNAL_ALGORITHMS`); `PUBLIC_ALGORITHMS`
and `ALL_ALGORITHMS` are explicit. The spec→runtime alias table
(`experiment/schema/spec_aliases.py`) was a first pass and is **not the
target**: S1b deletes it in favour of one name per primitive. Do not build new
surface on it.

**S1b — next session, immediate.** Alias removal. The table is a second
vocabulary: `photonic`/`optical`, `feedforward_dag`/`feedforward`,
`reverse_mode`/`gradient` and seven more pairs name one mechanism twice, and
`acceleration/status.py::_primitive_to_axis` holds a third hand-maintained copy
of the same translation. Plan:

1. **Rename the spec IDs, package directories, and entrypoint strings**
   together (10): `photonic→optical`, `feedforward_dag→feedforward`,
   `recurrent_attractor→recurrent`, `spatial_lattice_3d→spatial_lattice`,
   `fabric_pc→graph`, `instantaneous_pass→instantaneous`,
   `lazy_state_dynamics→lazy`, `pc_alm_settling→pc_alm`,
   `fast_weight→fast_weights`, `reverse_mode→gradient`.
2. **Delete the alias resolution**: `experiment/schema/spec_aliases.py`; make
   the inventory resolve by identity (`spec.id.rsplit(".")[-1]` must be the
   runtime name). Keep only a declaration row for mechanisms with no
   coordinate (`noisy`, `closed_form_ridge`).
3. **Replace** `acceleration/status.py::_primitive_to_axis` (~60 hand lines)
   with the axis segment: `primitive.<axis_segment>.<runtime_name>`; share one
   `AXIS_SEGMENT` map with `coordinate_of` and the inventory.
4. **Update `uses_primitives`** in the 10 algorithm specs that cite old IDs,
   plus the hardcoded rung list in `acceleration/rungbench.py`.
5. **Regenerate** `tests/property/generated/test_primitive_*` and
   `docs/generated/{IMPLEMENTATION_MATRIX.md,primitives,algorithms}` from the
   registry; delete stale filename variants.
6. **Rename the 10 test directories and update the locks**:
   `tests/primitives/*`, `tests/acceleration/test_rung_parity.py`,
   `test_registry_completeness_lock.py`, `test_preset_audit_lock.py`, and
   `test_surface_inventory_lock.py`.
7. **S1c (bijection):** the 15 runtime-only coordinates (`analog`, `conv`,
   `attention`, `causal_transformer`, `tile`, `local_contrastive`,
   `error_predictive_coding`, `adam`, `lion`, `local_adam`, `mean_norm`,
   `ortho_adam`, `riemannian_orthogonal`, `role_split`, `conflict_adaptive`)
   each gain a same-named spec package delegating to its ontology class.
   `tile` and `tile_mesh` are two coordinates of one class; each keeps its own
   name and states the difference. Measure the count before/after and write it
   here.

Blast radius: 10 spec packages (IDs, directories, 20 entrypoints), 10 algorithm
specs, 3 acceleration modules, 10 test directories, 49 generated tests,
generated docs, plus 15 new packages in S1c. No measurement semantics change:
`coordinate_of` already emits the runtime value, so evidence coordinates stay
byte-identical. A fresh session starts with S1b and continues into S1c; close
S2/S7 only after both.

**S2 — blocked.** Alias resolution is deliberately not extended. The four
docs-claimed architectures (PINO/DeepONet/FNO/LSTM) are declared rows with a
trigger. Open after S1b/S1c: one forward/param smoke per **runtime** geometry
(11/11) and an explicit activation-layout/cell-mode declaration per geometry
row.

**S3 — declared half landed.** The 11 planned names and 4 docs contradictions
are now rows with a reason and trigger (`inventory.py::DECLARED_CLAIMS`), so
none is silence. Open: register the offline loaders (`diabetes`,
`lorenz_state`), and give `continual`/`multitask` one task each or a retirement
row.

**S5 — classification landed.** All 21 unverified capabilities are `declared`
with their registry reason; all 67 active rows resolve to an existing test
file. Open: the two lab rows cite package tests that are absent from this
repository — either ship the package tests or retire those rows.

**S7 — joins landed.** The inventory lock fails if a docs task name or a
generated implementation-matrix ID has no row. Open: generated docs counts must
be derived from the inventory rather than hand-maintained prose.

**Next session order:** S1b alias removal → S1c spec/runtime bijection → S2
geometry smoke → S3 offline loaders → S4 loss inventory → S5 capability
decisions → S6 legal-coordinate smoke → S7 generated counts.

---

## 4. Tickets

### S0 — Inventory instrument

**Deliverable:** one command (extend `comp coverage` or add
`comp capabilities inventory`) that joins, in one table:

- the plan of record (`docs/readme/stability-eval.md` implemented/planned
  entries);
- the spec matrix (`docs/generated/IMPLEMENTATION_MATRIX.md` IDs and status);
- runtime axis registries (`AXES_REGISTRIES`);
- algorithm package directories and `computronium.algorithms`;
- `SUPPORTED_TASKS`, `DomainType`, `_DOMAIN_REGISTRY`;
- `OBJECTIVES_REGISTRY`/`MEASURED_OBJECTIVES`;
- `CAPABILITIES_REGISTRY`.

Each row has: `id`, `kind`, `runtime_name`, `status`
(`implemented`/`declared`/`unknown`), `smoke_path`, `reason_or_trigger`.

**Acceptance:** the command reports **0 `unknown`** rows; deleting an
implemented row's smoke path makes it `unknown`; a lock compares the command to
the underlying registries (the TODO90 corpus-lock pattern).

### S1 — Algorithm surface

**Deliverable**

1. Decide each of the 21 packages: **public**, **internal** (reachable only
   through a named preset), or **retired**. The 7 unexposed EP variants are
   currently neither declared nor documented as internal.
2. Add the public ones to `computronium.algorithms` (lazy namespace), or add a
   `INTERNAL_ALGORITHMS` row naming the preset that reaches each.
3. ~~Build one alias table mapping spec IDs to runtime constructors.~~ **Do not
   build an alias table.** S1b makes the spec ID itself the runtime name.
4. Smoke: one compose + one train step per public algorithm (a small 3-class
   toy batch, CPU, no claims).

**Acceptance:** every package is `public` or `internal` with a preset path;
21/21 accounted for; no alias table is introduced.

### S1b — Vocabulary unification: remove every alias (immediate; blocks S2/S7)

**Problem.** Two names for one mechanism is the defect TODO91 §1 item 2
records, and an alias table institutionalizes it. A user selecting
`feedforward` and a docs page naming `feedforward_dag` are describing one
implementation; a third hand copy lives in
`acceleration/status.py::_primitive_to_axis`. Three tables, one fact.

**Deliverable — rename in lockstep (ID, package directory, entrypoints).**

| Old spec ID / directory | New spec ID / directory |
|---|---|
| `primitive.substrate.photonic` / `substrate/photonic` | `primitive.substrate.optical` / `substrate/optical` |
| `primitive.geometry.feedforward_dag` / `geometry/feedforward_dag` | `primitive.geometry.feedforward` / `geometry/feedforward` |
| `primitive.geometry.recurrent_attractor` / `geometry/recurrent_attractor` | `primitive.geometry.recurrent` / `geometry/recurrent` |
| `primitive.geometry.spatial_lattice_3d` / `geometry/spatial_lattice_3d` | `primitive.geometry.spatial_lattice` / `geometry/spatial_lattice` |
| `primitive.geometry.fabric_pc` / `geometry/fabric_pc` | `primitive.geometry.graph` / `geometry/graph` |
| `primitive.state_dynamics.instantaneous_pass` / `state_dynamics/instantaneous_pass` | `primitive.state_dynamics.instantaneous` / `state_dynamics/instantaneous` |
| `primitive.state_dynamics.lazy_state_dynamics` / `state_dynamics/lazy_state_dynamics` | `primitive.state_dynamics.lazy` / `state_dynamics/lazy` |
| `primitive.state_dynamics.pc_alm_settling` / `state_dynamics/pc_alm_settling` | `primitive.state_dynamics.pc_alm` / `state_dynamics/pc_alm` |
| `primitive.plasticity.fast_weight` / `plasticity/fast_weight` | `primitive.plasticity.fast_weights` / `plasticity/fast_weights` |
| `primitive.credit_assignment.reverse_mode` / `credit_assignment/reverse_mode` | `primitive.credit_assignment.gradient` / `credit_assignment/gradient` |

1. Rename the directory, the `SPEC.id`, and both
   `reference_entrypoint`/`kernel_entrypoint` strings together. The registry
   discovers packages by walking `computronium.primitives`, so no registration
   edit is needed.
2. **Delete `experiment/schema/spec_aliases.py`.** The inventory resolves by
   identity: the spec's last segment must equal a runtime coordinate. Keep
   exactly two no-coordinate declarations, beside the inventory:
   `noisy` (the digital substrate with noise configured) and
   `closed_form_ridge` (a plasticity object with no axis coordinate). Do not
   add runtime coordinates for them — that would create unmeasured breadth rows.
3. **Delete `acceleration/status.py::_primitive_to_axis`'s hand tables.** Parse
   `primitive.<axis_segment>.<name>` with one shared `AXIS_SEGMENT` map
   (`credit_assignment→credit`, `parameter_update→update`,
   `state_dynamics→dynamics`, identity otherwise) used by `coordinate_of`, the
   inventory, and any future selector. Delete the two docstring examples that
   still name old IDs (`acceleration/spec.py`, `acceleration/microbench.py`).
4. **Update `uses_primitives`** in every algorithm spec that cites a renamed ID
   (10 specs), and the hardcoded rung list in `acceleration/rungbench.py`.
5. **Regenerate** `tests/property/generated/test_primitive_*` and
   `docs/generated/{IMPLEMENTATION_MATRIX.md,primitives,algorithms}` from the
   registry; delete every stale filename variant. Do not hand-edit generated
   docs.
6. **Rename the test directories and update the locks/tests** that hardcode the
   old module paths or IDs: the 10 per-primitive test directories under
   `tests/primitives/`, `tests/acceleration/test_rung_parity.py`,
   `test_registry_completeness_lock.py`, `test_preset_audit_lock.py`, and
   `test_surface_inventory_lock.py`.

**Acceptance:** zero alias entries in the tree; the inventory resolves every
spec row by identity; `comp coverage inventory` reports 0 `unknown`; a
deliberately renamed spec ID makes its row `unknown`; the generated matrix and
the runtime registry share one vocabulary; no evidence coordinate changes
(`coordinate_of` already emits the runtime value).

**Cost:** 3–4 h. Files: 10 spec packages (30 files including tests),
10 algorithm specs, 3 acceleration modules, 10 test directories,
~10 generated tests, generated docs.

### S1c — Spec/runtime bijection: the 15 runtime-only coordinates

**Problem.** After S1b the two vocabularies have one spelling, but 15 runtime
coordinates still have no spec row: the matrix cannot describe what a user can
select. Each has a real implementation class, so each deserves a same-named
spec — not a "mode of X" alias.

**Deliverable.** One primitive package per coordinate, ID equal to the
coordinate, reference path delegating to the ontology class (the source of
truth). Groups and classes:

| Axis | Coordinates | Class |
|---|---|---|
| substrate | `analog` | `AnalogSubstrate` |
| geometry | `conv`, `attention`, `causal_transformer` | `ConvGeometry`, `AttentionGeometry`, `CausalTransformerGeometry` |
| geometry | `tile` | `TileGeometry` (graph-derived tile count; `tile_mesh` is the fixed-mesh variant of the same class — two coordinates, two specs, summaries must state the difference) |
| dynamics | `error_predictive_coding` | `ErrorPredictiveCodingDynamics` |
| plasticity | `conflict_adaptive` | `ConflictAdaptivePsiPlasticity` |
| credit | `local_contrastive` | `LocalContrastiveCredit` |
| update | `adam`, `lion`, `local_adam`, `mean_norm`, `ortho_adam`, `riemannian_orthogonal`, `role_split` | the seven `*Update` classes in `ontology/update/__init__.py` |

1. Each package gets `spec.py`, `reference.py`, `cases.py`; a `kernel.py` only
   when a kernel exists (otherwise `supported_backends=("reference",)` and no
   `kernel_entrypoint`). Reuse the axis harness case builder
   (`make_update_case`, etc.), as `parameter_update/euclidean` does.
2. Register the same axes/availability the runtime registry declares; do not
   add new runtime coordinates.
3. Regenerate property tests and docs; run the parity suite.

**Acceptance:** every runtime coordinate has a same-named spec;
`len(primitive specs) == len(runtime coordinates) + 2` no-coordinate
declarations; `comp coverage inventory` reports 0 `unknown` and 0
"runtime-only" rows; deleting one new package makes its coordinate row
`unknown`.

**Cost:** 4–6 h. 15 packages (~45 files), 15 generated tests, docs.

### S2 — Architecture surface

**Deliverable**

1. Every runtime geometry maps to exactly one spec row (S1b/S1c). No alias
   table.
2. A shape/parameter smoke per runtime geometry: build from `GeometryConfig`,
   forward a batch, one step/route, report parameter count and output shape.
3. Every geometry row declares its activation layout and cell/sample mode
   (NCA/NTM already do this).
4. **Docs-claimed architectures:** reconcile the scientific models
   (PINO/DeepONet/FNO) and the standalone LSTM family with the runtime. For
   each, either implement the minimum faithful form as a geometry/preset with a
   smoke path, or replace the docs claim with a declared `unavailable` row and
   a trigger. A docs claim with no code is the same defect as a silent hole.

**Acceptance:** 11/11 runtime geometries smoke; every spec geometry resolves
or carries a retirement; every architecture named in the README resolves to a
runtime row or a declared retirement; the lock fails if a geometry row loses
its smoke.

### S3 — Task surface

**Deliverable, in this order (offline first):**

1. **Implementable offline now:** `lorenz_state` (the `ScientificTask` loader
   already generates it), `diabetes` and `california_housing`
   (`sklearn.datasets`, offline), `ett_h1` only if an in-repo/offline CSV
   exists.
2. **Network/optional:** `cifar100`, `svhn`, `wikitext2`, `penn_treebank` —
   either a cached offline loader with a checksum lock, or a declared
   `network_required` row with the reason. Do not add a fetch that CI cannot
   run.
3. **Physics/Box2D:** `mountain_car`, `lunar_lander`, PDE suite
   (Heat/Wave/Burgers/Navier–Stokes) — implement only with an offline
   integration, else declare `dependency_unavailable` with the package and
   license.
4. **Continual/multitask:** one task each (e.g. a class-incremental split of
   `digits`, task sequence with a declared order) or a named retirement with
   the trigger (a claim needs forgetting/backward-transfer).
5. **Naming reconciliation:** the docs' scientific entries (`pendulum`,
   `lorenz`) and vision entries (`cifar100`, `svhn`) are rewritten to the
   registry's task names, or the registry gains those names with loaders.
   `pendulum_state` must not coexist with a docs task called `pendulum` that
   resolves to a different domain.

**Acceptance:** every task in the docs' implemented/planned list is
`implemented + one PASS cell` or `declared + reason`; `comp coverage tasks`
lists the new tasks; `continual`/`multitask` are no longer empty or carry a
retirement row.

### S4 — Loss/objective surface

**Deliverable**

1. Declare the supported loss inventory in one table: CE, MSE/MAE, and the
   domain-specific losses the tasks use. A task whose `compute_loss` is not in
   the table is a defect (B6c/B7's class of bug: the pipeline optimized the
   wrong objective).
2. Wire `forgetting`/`backward_transfer` when S3's continual task lands, or
   retire both rows with the trigger.
3. Every objective row names its payload key and its emitter path (the B8
   mapping, now locked) — no row returns without a key.

**Acceptance:** `comp coverage unmeasured` is 0, or every remaining row has a
declared trigger; a lock asserts each task's loss function is in the declared
inventory.

### S5 — Capability surface

**Deliverable:** for each of the 21 unverified rows, one of:

- a smoke test that exercises the mechanism (checkpoint/resume roundtrip, KV
  cache growth, multiprocess one-cell run, DDP/FSDP one-step, Pareto report on
  a store, warm-start from a prior store, cross-task transfer, …);
- `unverified_reason` + a `trigger` naming the ticket/experiment that needs it.

Group the rows by prerequisite: (a) long-run readiness (checkpoint/resume,
   batch vectorization), (b) multi-worker readiness (multiprocess, DDP/FSDP,
   pipeline, P2P), (c) selection readiness (warm-start, cross-task transfer,
   surrogate/Pareto), (d) optional services (FastAPI, lab packages).

**Acceptance:** 0 unverified rows without a reason; every "active" row has a
test that fails if the mechanism is removed.

### S6 — Combination smoke

**Deliverable:** generate the **legal** coordinate matrix from the constraint
engine (not the full Cartesian product), cap it at a declared budget, and for
each cell compose + one 1-epoch step + assert a PASS record. Failures are
either fixed (implementation defect) or declared (a legality rule that should
have refused the cell).

**Acceptance:** 0 legal-coordinate failures; every failure in the report names
its rule or its defect ticket; the matrix command is reproducible.

### S7 — Vocabulary/docs lock

**Deliverable:** `docs/generated/*` and the README tables are generated from
the S0 inventory, not hand-written counts. One vocabulary feeds the spec
matrix, the CLI, and the docs: a spec ID equals its runtime coordinate, or it
is a declared no-coordinate row. A lock fails if a second vocabulary appears
(e.g. a new spec ID with no runtime row, an alias table, or a task name with no
registry row).

**Acceptance:** regenerate docs changes nothing; a deliberately renamed spec ID
fails the lock.

---

## 5. Success criteria

| Criterion | Start | Target |
|---|---|---|
| Inventory rows with `unknown` status | 11 planned names, 4 docs/runtime contradictions, 7 hidden algorithms, 4 docs-claimed architectures, 21 unverified capabilities | **0** |
| Algorithm packages accounted for | 14 public, 7 silent | **21/21 public or declared internal** |
| Spec IDs resolving to a runtime constructor | unverified (two vocabularies) | **one vocabulary: every spec ID equals its runtime name or is `not_a_primitive`** |
| Alias tables mapping spec IDs to runtime names | 3 hand copies (`spec_aliases.py`, `status.py` tables, docs prose) | **0** |
| Runtime coordinates with a same-named spec row | 44 specs vs 59 coordinates (15 runtime-only) | **59/59; 2 no-coordinate declarations** |
| Runtime geometries with a smoke | 11 registered, no per-geometry smoke | **11/11** |
| Architectures named in docs with a runtime row | PINO/DeepONet/FNO and a standalone LSTM are unbacked | **every claim implemented or retired** |
| Planned tasks implemented or declared | prose only | **every docs entry is a row** |
| Domain values with a task | 8 have tasks; `continual`/`multitask` none; `lm` alias | **10/10 or retired with trigger** |
| Objectives measured or retired | 54/54 + 2 deferred | **54/54 + 2 wired or retired** |
| Unverified capabilities with a reason | 21 | **0 unexplained** |
| Legal-coordinate smoke failures | unknown | **0** |
| Loss functions declared per task | implicit | **every task's loss in one table** |

The instrument is S0's command plus its drift lock. A row is never "covered"
because a registry lists it; it is covered when the smoke path runs and the
lock protects it.

---

## 6. Explicit non-goals (parked)

1. **HPO, tuning, result claims.** No search, no thresholds, no winner. They
   need a held-out protocol and a measured cost model; neither is in this plan.
2. **Performance/SOTA.** Kernel parity is tracked by the existing
   implementation matrix; this plan does not chase speedups.
3. **New measurement breadth.** TODO90 closed at 0 undeclared pairs, 26/26
   tasks, 8/8 conformance arms; do not re-open it.
4. **Optional services** (P2P cluster, FastAPI server, lab packages) unless S5
   finds one is a prerequisite for a concrete experiment.
5. **Paper figures, publishing, retrospectives** — unchanged from TODO89 §5.

---

## 7. Fresh-session bootstrap

```bash
# state
uv lock --check
uv run python -c "import duckdb, torch; print(duckdb.__version__, torch.__version__)"
uv run comp coverage report --corpus
uv run comp coverage unmeasured

# the inventory S0 builds; until it exists, these are the three sources
uv run python - <<'PY'
from computronium.experiment.schema.seed_registries import seed_all_registries
seed_all_registries()
from computronium.algorithms import _ALGORITHMS
from computronium.domains.registry import SUPPORTED_TASKS
from computronium.experiment.schema.registries import CAPABILITIES_REGISTRY
print("algorithms", len(_ALGORITHMS), sorted(_ALGORITHMS))
print("tasks", len(SUPPORTED_TASKS), sorted(SUPPORTED_TASKS))
print("capabilities", len(list(CAPABILITIES_REGISTRY)))
PY

# the breadth locks from TODO90 (must stay green while the surface changes)
uv run python -m pytest \
  tests/property/test_corpus_coverage_lock.py \
  tests/property/test_objective_breadth_lock.py \
  tests/property/test_substrate_reaches_compute_lock.py -q --tb=line
```

Read `TODO90.md` §3 and §5 first: it owns the measured surface and the parked
depth items. This plan does not touch those; it completes the *selection*
surface.

**Order:** S0 first. Without the inventory, every later ticket argues from a
different list. Then **S1b (one vocabulary; remove the alias table)**, S1/S2
(algorithms + architectures), S3/S4 (tasks + losses), S6 (combinations), S5
(capabilities), S7 (docs).
