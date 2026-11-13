# TODO91 — Surface completion (successor to TODO90)

**Status:** 2026-11-13 · base `e226694a` · TODO90 closed (breadth instrument,
B0–B10) · **this plan writes no claims and runs no search.**

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
2. **The spec inventory and the runtime registry use different names.** The
   implementation matrix cannot be joined to `AXES_REGISTRIES` without an alias
   table that does not exist. "All architectures covered" is therefore
   unverifiable from either surface alone.
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
declared is not inferred). This plan adds one:

> **A surface ticket closes on a smoke path or a named declaration.**
> "Exists in the tree" is not coverage; "registered" is not coverage. A row is
> covered only when one command exercises it and a lock fails if the row is
> deleted. An undeclared entry is a defect.

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
| S0 | **Inventory instrument** | one `comp` command joins spec rows, runtime axes, packages, tasks, domains, objectives, capabilities; zero `unknown` rows | 1 h | open |
| S1 | **Algorithm surface** | every algorithm package is public or declared internal; spec ID → runtime constructor alias table | 1–2 h | open |
| S2 | **Architecture surface** | every geometry has a forward/step/param smoke; every spec geometry resolves through the alias table or is retired | 1 h | open |
| S3 | **Task surface** | planned tasks implemented or declared; `continual`/`multitask` gain one task each or a named retirement | 2 h | open |
| S4 | **Loss/objective surface** | declared loss inventory per task; continual objectives wired or retired | 1 h | open |
| S5 | **Capability surface** | all 21 unverified rows get a smoke test or `unavailable_reason` + trigger | 2 h | open |
| S6 | **Combination smoke** | legal-coordinate matrix composes and trains one step with zero failures | 1–2 h | open |
| S7 | **Vocabulary/docs lock** | generated docs read from the inventory; API-vocabulary drift locked | 30 min | open |

S0 is the instrument; S1–S2 make selection verifiable; S3–S4 complete the
content; S6 proves combinations; S5 is infrastructure readiness; S7 prevents
the second vocabulary from returning.

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
3. Build one alias table mapping spec IDs to runtime constructors:
   `primitive.substrate.photonic` → `optical`, `...noisy` → digital-noise
   config, `primitive.credit_assignment.reverse_mode` → `gradient`,
   `primitive.geometry.feedforward_dag` → `feedforward`,
   `...recurrent_attractor` → `recurrent`, `...spatial_lattice_3d` →
   `spatial_lattice`, `...fabric_pc` → `graph`, and so on.
4. Smoke: one compose + one train step per public algorithm (a small 3-class
   toy batch, CPU, no claims).

**Acceptance:** every package is `public` or `internal` with a preset path;
every spec ID resolves to a runtime constructor or an explicit
`not_a_primitive` row; an unknown ID fails the lock; 21/21 accounted for.

### S2 — Architecture surface

**Deliverable**

1. The alias table from S1 covers every geometry spec ID; report which spec
   geometries have **no runtime implementation** (`fabric_pc` vs `graph` is an
   alias, not a second implementation — decide which).
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
the S0 inventory, not hand-written counts; one alias table feeds the spec
matrix, the CLI, and the docs. A lock fails if a second vocabulary appears
(e.g. a new spec ID with no runtime row, or a task name with no registry row).

**Acceptance:** regenerate docs changes nothing; a deliberately renamed spec ID
fails the lock.

---

## 5. Success criteria

| Criterion | Start | Target |
|---|---|---|
| Inventory rows with `unknown` status | 11 planned names, 4 docs/runtime contradictions, 7 hidden algorithms, 4 docs-claimed architectures, 21 unverified capabilities | **0** |
| Algorithm packages accounted for | 14 public, 7 silent | **21/21 public or declared internal** |
| Spec IDs resolving to a runtime constructor | unverified (two vocabularies) | **64/64 rows resolved or `not_a_primitive`** |
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
different list. Then S1/S2 (algorithms + architectures), S3/S4 (tasks +
losses), S6 (combinations), S5 (capabilities), S7 (docs).
