# Code Guidelines

- Elegant
- Consolidated
- Consistent
- Organized
- Deeply deduplicated: Don't repeat yourself (DRY)
- Abstract
- Modularized
- Parameterized
- Backwards compatibility: NONE
- Few comments: rely on self-documenting code.
- Purpose: professional, not explanatory/educational
- Don't obsess over test coverage and other linty tediums: Working functionality is more important than coverage and cosmetic lint issues.
- Prefer use of GPU over CPU where appropriate.
- Be skeptical of low-performing experiments; this could indicate an implementation defect to fix. 

## Toolchain
*   Language: **Python 3.14+**
*   **uv**: For dependency management, virtualenvs, and task running (`uv run`, `uv add`). Single lockfile (`uv.lock`); no `requirements.txt`.
*   **Ruff**: For formatting, linting, and import sorting. All config in `pyproject.toml`. Format always (cheap). Lint **changed files only** during development — findings in legacy modules are queued work (Register C / hygiene pass), never commit blockers.
*   **Pyright** (or mypy): **Strict on new/rewritten modules.** Repo-wide checking stays basic until the dedicated hygiene pass closes; type fixes in legacy modules ride that pass, not feature work.
*   **pre-commit**: Runs ruff format + lint on changed files only. No test suite in the hook.
*   **Line Length**: Ruff default (88). Relax per-line with `# noqa: <code>` and a reason, never globally.
*   Rules are enforced by tooling — if a rule can be a config or pre-commit hook, it is one.

## Type System
*   **Modern Syntax**: Built-in generics (`list[str]`), PEP 604 unions (`X | None`). Never import `List`, `Dict`, `Optional`, or `Union`.
*   **PEP 695**: Use `class Cache[T]: ...` and `type UserId = int` for generics and aliases.
*   **Interfaces & Narrowing**: Prefer `Protocol` over ABCs. Use `Self` for fluent returns. Use **`TypeIs`** for custom type narrowing to preserve original type context on failure.
*   **Value Sets**: Use `Literal` / `StrEnum` instead of bare strings.
*   **Data Modeling**:
    *   `@dataclass(frozen=True, slots=True)` for internal value objects.
    *   `TypedDict` for unvalidated structured dicts.
    *   **Pydantic v2** at I/O boundaries for runtime validation.
*   **No `Any`**: Replace with `object`, generics, or `Protocol`. If unavoidable, isolate and document why.

## Architecture & Control Flow
*   **Pattern Matching**: Use `match`/`case` for complex state/data routing, favoring it over chained `if/elif`.
*   **Complexity**: Let Ruff rules (`C901`, `PLR09xx`) enforce function size. Extract `_`-prefixed helpers rather than nesting deeper.
*   **Control Flow**: Flatten with guard clauses (`if not condition: return`). 
*   **Finally Blocks**: **Never** use `return`, `break`, or `continue` inside a `finally` block (PEP 765). This is a hard `SyntaxError` and silently swallows exceptions.
*   **Composition over Inheritance**: Favor small pure functions. Isolate side effects so core logic stays testable.
*   **One Source of Truth per Rule**: legality, pricing, measurement identity, dispatch and capability flags each live in exactly one place. A second table, filter or cache that re-derives one is a defect, not a fallback: feed the first or delete it, and count what the second one used to drop. Capability flags are declared (config field, `ClassVar`, registry row), never inferred by reflection or by shape.
*   **Immutability**: Default to immutable structures (`tuple`, `frozenset`, frozen dataclasses) unless mutation is strictly required.

## Async Concurrency & Thread Safety
*   **Structured Concurrency**: Use `asyncio.TaskGroup` for concurrent tasks. Avoid `asyncio.gather` for complex flows.
*   **Event Loop Hygiene**: Never mix blocking I/O/CPU tasks with `async` code. Use `asyncio.to_thread` for legacy blocking calls.
*   **Thread Safety (PEP 703)**: With free-threaded CPython, **do not rely on the GIL**. Use explicit locks (`threading.Lock`), thread-local storage, or immutable data for shared mutable state.

## Documentation & Modules
*   **Docstrings**: **Google-style** on all public APIs. Type hints replace argument type documentation — focus on behavior, side effects, and invariants.
*   **Comments**: Explain *why*, not *what*. Delete dead code; use `# TODO(name): ...` for deferred work.
*   **Import Hygiene**: Avoid heavy computations or I/O at the module level. Prevent circular imports via local imports or dependency injection.

## Errors, Logging & Resources
*   **Safe Interpolation**: Use **t-strings** (PEP 750) for logging and templating to enable safe, deferred interpolation. Never use f-strings for database queries (use driver parameterization) or untrusted log inputs.
*   **Logging**: Standard `logging` (or `structlog`). Never `print()`. Include context: `logger.error("msg", extra={"task_id": id})`.
*   **Exceptions**: Define a small custom hierarchy per domain. Always chain: `raise DomainError("msg") from original_exception`. Use `except*` (PEP 654) for concurrent independent failures.
*   **Resources**: Use context managers (`with` / `async with`) for all resource lifecycles.

## Environment (binding)
*   **Test invocation**: always `uv run python -m pytest` — never bare `pytest`
    (user-site pytest shadowing breaks collection on protobuf gencode skew).
*   **Env restore**: `uv sync --dev --all-extras` — bare `uv sync` strips dev
    extras and produces `ModuleNotFoundError` mid-landing.
*   **Dev-env smoke** (run before any gate): `uv run python -c "import optuna, scipy, torchvision, pytest"` —
    a stripped env fails here in seconds instead of mid-gate.
*   **`UV_LINK_MODE=copy`**: set in the shell env (or `.env`) on this
    filesystem layout — the uv cache hardlink falls back to copy with a
    warning on every `uv run` otherwise (cosmetic, R4.3).
*   **Cell walltime**: a single foreground command runs **≤5 min** with
    streaming output (never pipe a long run through `tail`/buffering).
    Longer cells go to background before launch:
    `nohup uv run python … > logs/<name>.log 2>&1 &` and are polled at
    ≤2-min intervals with a pre-registered kill time.

## Testing
*   **pytest + pytest-cov**: Coverage is opt-in (`--cov`); no floor until the API stabilizes.
*   **Test execution tiers** — run the cheapest tier that can catch your change; always show output + walltime (never truncate failures):
    1. **Targeted** (default): only tests touching changed modules (`uv run python -m pytest tests/<path> -k <signature> -q`).
    2. **Fast gate** (demo/gallery/lock-adjacent changes): demo gate (`pytest tests/integration/ -m demo -q`) + drift locks + property suite.
    3. **Directory shards**: one `testpaths` directory (`primitives` 14 s, `algorithms`+`acceleration` 88 s, `unit` 117 s, `property` 166 s under `-n 4`) — round close.
    4. **All shards + `tests/acceptance/`**: ~10 min — release candidate.
*   **Never `pytest tests/`.** It bypasses `testpaths` and pulls in every demo;
  two attempts hard-killed at test 873/3699 with no traceback (TODO45 §12.1).
*   **`-n 4` is already in `addopts`**; do not add `-n` by hand, and do not
  override it downward for small selections without reason (worker startup costs
  ~10 s, which exceeds some shards' entire runtime).
*   **Demos are artifact producers, not checks.** The `demo` marker is stamped in
  `tests/conftest.py` by filename; `pytest -m demo` is the only way to run them.
*   **Select tests by symbol, not by directory.** `grep -rn <symbol> tests/
  --include=*.py`, then run the 2-4 files it names. A whole `testpaths`
  directory is a round-close artifact, never a feature gate: it costs ~5x, is
  the only tier that gets hard-killed, and its cost is quoted stale.
*   **A run that may be interrupted writes `-rf --tb=line` to a log.** pytest
  writes its summary at session end, so a hard kill takes the run's only
  artifact — and recovering it means re-running it.
*   **A killed run yields no verdict: collect, do not re-run.**
  `pytest <dir> --co -q > ids.txt` runs no test code (~40 s) and locates a
  failure from the progress line. **Never `--lf`/`--ff` here**:
  `.pytest_cache/v/cache/lastfailed` holds 520 entries, most with node ids that
  no longer collect.
*   **A lock's fixture must contain the case the lock exists for.** If removing
  the mechanism cannot fail the fixture, the lock is a comment (TODO46 D25).
*   **One shard run per round close, never per commit** — and never a re-run of
  a shard already green "to confirm".
*   **hypothesis**: Use for property-based tests on pure logic.
*   **Mocking**: Prefer Dependency Injection over `unittest.mock`. Use `pytest-mock` when strictly required.
*   **Fixtures**: Use fixtures over setup/teardown; `@pytest.mark.parametrize` over duplicated tests.

## Security & Project Structure
*   **Dependency Scanning**: Run `pip-audit` in CI.
*   **Static Analysis**: Enable Ruff's `S` (bandit) rule set. Never hardcode secrets.
*   **Project Structure**: `pyproject.toml` is the single source of truth. `__init__.py` exposes only the public API via `__all__`; internal modules are `_`-prefixed.
*   **CI Gate Order** (what CI runs when adopted — agent per-commit duties are the scoped checklist below, not this list): `ruff format --check` → `ruff check` → `pyright` → `pytest --cov` → `pip-audit`.

## Agent Commit Checklist
**Per commit — scoped and fast:**
- [ ] Dev-env smoke (see Environment): `uv run python -c "import optuna, scipy, torchvision, pytest"`
- [ ] `ruff format` && `ruff check --fix` on changed files
- [ ] `pyright` on changed files (strict for new modules)
- [ ] Targeted tests for touched modules — output + walltime visible

**Deferred — hygiene pass / round close (never per-commit):**
- [ ] Repo-wide `ruff check` / `pyright` (Register C scope)
- [ ] Full `pytest` run; `--cov`; `pip-audit`

## Checklist: Adding a New Ontology Primitive

1. **Registry row** — add the class to the layer's single-source registry
   (`DYNAMICS_REGISTRY` in `computronium/ontology/dynamics/__init__.py` for
   StateDynamics). Two wiring edits total: class def + registry entry.
2. **Config classmethod** — `StateDynamicsConfig.<primitive>()` returns a
   config whose `dynamics_type` matches the registry key.
3. **Run the wiring lockstep lock** — `tests/property/test_dynamics_wiring_lock.py`
   proves registry ↔ config classmethods ↔ root `__all__`/`_LAZY` ↔ root
   `TYPE_CHECKING` imports stay in sync. Fix what it flags; never bypass it.
4. **Export surfaces** — root `__all__` + `_LAZY` (and the `TYPE_CHECKING`
   import block), `ontology/__init__.py` imports + `__all__`.
5. **Contract invariants** — read the `StateDynamics` Protocol docstring
   (activation layout, settle mutation/autograd contract, free/nudged
   semantics) before writing `settle`/`compute_energy`.
6. **Validation** — if `SystemConfig.validate()` needs a new compatibility
   branch, whitelist the new `dynamics_type` consistently in *all* credit/
   substrate branches (see R5.2 retro: the PC family divergence).
6b. **Target kind** — if the new law reads the target, declare
   `AxisSpec.target_kind` on its axis row. A law written over one-hot targets
   (a label channel, a centred one-hot residual, argmax agreement) must say
   `"class_index"`, so the declared space refuses it on a continuous-target
   task instead of raising inside the cell (TODO91 S9).
7. **Demo (if shipping one)** — demo test follows the static `_ARMS` table
   pattern (module scope, `_train_arm`/`_probe_arm` extracted, walltime
   printed never recorded), one `DEMOS` registry row in
   `computronium/visualization/gallery.py`, then re-pin
   `docs/figures/manifest.json` via the gallery lock.
8. **Probe conventions** — throwaway probe scripts live in `scripts/probes/`
   with their measured-regime numbers and a docstring citing the demo they
   informed.

## Documentation
- Don't edit README.md directly; in `docs/readme/*`, edit individual sections or the generator script

## Development Skill: Suspicious Experiment Cycle (SEC)

**Name:** SEC — Suspicious Experiment Cycle  
**Status:** working framework for a general validation methodology; this repo is the first case study.
**Principle:** Every run answers a decision. Be skeptical of low performance, but a defect is a claim that needs a named mechanism and a test; otherwise a low cell is a coordinate result, not an algorithm verdict. Spend the cheapest evidence that can decide the question, and stop when the decision is determined — not when an arbitrary clock expires.

**Capability first (binding amendment 2026-11-17).** The deliverable is the
system's ability to do something it could not do before: a new primitive, a
new task family, a constraint met. A measurement that ends in a negative is
not a deliverable; a **defect** is, because fixing it widens the system. A low
cell is therefore a **defect probe** first, and "refused" is only a statement
about a box (infeasible at this geometry, or over budget), never a verdict on
a mechanism. A mechanism may be parked as a **capability gap**: the primitive
or feature that closes it, its cost, and the task family it unlocks. That row
is work, not a conclusion. A measurement verdict is never final for a
mechanism; a fix attempt is the next rung. **Every rule here is a default:**
a named reason and a working capability override it; write the reason where the
number lives.

**When to use:** Any validation with multiple algorithm/architecture combinations where "doesn't work", "is broken", and "is unoptimized" are live possibilities.

**Scope: capability → tuning → comparison.** The validation phase produces a **capability map**, not a leaderboard. Tune each rule to its best declared box, then compare at matched boxes: an under-tuned comparison is not evidence, and a low cell is a defect probe first. A comparison is made after tuning, never instead of it.

**The SEC decision loop (no wall-clock target):**

0. **DECIDE** — Write the decision, the two actions, the error costs, and the stop rule. If the decision is "X beats Y", it is competitiveness and needs matched boxes; if it is "is this wired?", it is validation.
1. **FALSIFY CHEAPLY** — Start at the lowest rung that can decide. Climb only while ambiguous. Never run a more expensive rung to confirm a cheaper definitive result.
2. **TRIAGE** — Classify: **defect** (named mechanism + failing test), **capability gap** (the primitive/feature that closes it + its cost + the task family it unlocks), or **coordinate result** (record the box). A low number is none of these until triage says so. "Refused" is a box statement (infeasible, or over budget); it never closes a mechanism. For run-level symptoms (task count, L1/L2 cell count, worker crashes, dedup), use `comp report` / `comp coverage` and the Defect Patterns / Common Fixes tables.
3. **FIX** — Only a named defect. Correctness or infrastructure, never a knob sweep: tuning belongs to the ladder, not to the fix. If the cause is not found before the rung watchdog, file the symptom with a failing test and stop.
4. **VERIFY** — The fix must move the cell or the failing test. Moving neither is not a fix.
5. **RECORD** — Commit the decision, rung reached, stop reason, box, and cost; write the measured number where the mechanism lives (constraint comment, identity card, lock docstring), not only in the log. `unconcluded` is allowed only before a claim is staked; after a claim, a negative is a coordinate result or a capability gap.

**The rung ladder (cheapest falsifier first).**

| Rung | Decision | Test | Verdict / next | Cost model |
|---|---|---|---|---|
| 0 | Is it wired? | static checks + 1 step: positive control, shapes, label channel, non-zero update, compatibility | defect → triage; clean → rung 1 | seconds |
| 1 | Does it train? | 1 epoch / 1 seed | failure → defect; above chance → rung 2 | measured pilot × 1 |
| 2 | Is it viable across its knob? | 3-point ladder, 1 seed each + 1 confirmation seed at the best point | best point above chance → **provisional** coordinate; all fail → defect or capability gap | measured pilot × 4 |
| 3 | Is the effect real? | pre-registered `n_max`, paired CI | CI decision or `n_max` → claim/coordinate | measured per-seed × n |
| 4 | Is it competitive? | matched boxes at each arm's best declared point | pre-registered threshold → competitive verdict | budgeted HPO |

Rungs 0–2 are **mandatory** for a new rule **or a new composition** (a matched arm that changes which mechanism runs, even if every primitive exists): they are the minimum fair chance, not optional HPO. Rung 3 is the first rung that may carry a claim; it reports **equivalent / superior / inferior / inconclusive**, and `inconclusive` at `n_max` is a coordinate result, not a claim. Rung 4 is competitiveness and requires each arm at its best declared box. VoI decides promotion beyond rung 2, not whether a new rule gets rungs 0–2.

Repo example for a screening cell: `uv run python -m computronium.experiment.survey_cli 0.1 --mode learn --policy tpe --device cuda --tasks <task> --fidelity L0 --axes '<focused_json>' --epochs 1 --n-seeds 1`, or a focused probe for a single-cell check. The cell's `measurement_key` is its identity.

**Stopping rule.** Promote only while the decision is ambiguous and `P(next rung changes the decision) × cost of a wrong decision > cost of the rung`. The rung ladder is the cheap approximation of that rule. A definitive outcome (defect, capability gap, coordinate, or claim) stops the loop; otherwise promote. Record the stop reason: `verdict`, `watchdog`, `superseded`, or `n_max` — never the minutes.

**Watchdog, not timebox.** Rung cost is `fixed startup + pilot × rung size`; kill a rung 0–3 at `2 ×` that measured cost. A cell with no pilot uses the environment's 5-min foreground cap as a **bootstrap cap**: measure that first run, then set the 2× watchdog. A rung that exceeds its watchdog is a cost-model defect or a bad cell: kill, record, re-price. Rung 4 uses the pre-registered HPO budget, not a per-run clock. Do not use a global 5/10/25-minute budget as the primary control; the watchdog is a safety cap, not the methodology. A long run (rung 3+) needs a named claim, a box, a pre-registered `n_max`, and a stop rule; otherwise it is not a run, it is a budget leak.

**Error control.** Screening (rungs 0–2) may stop freely. A claim (rung 3) must use either a pre-registered `n_max` with a fixed-n CI and no peeking, or a sequential/always-valid confidence sequence. Never stop a fixed-n comparison early and report its CI as if it were sequential. Until a confidence-sequence helper exists, `paired_comparison` is fixed-n: fix `n_max` before the run and do not peek. A registration is committed **before** the first seed: a margin committed with its result is **post-hoc** and cannot carry a claim. A gate is a predicate the repository evaluates (`comp gate ...`), not a sentence a session asserts; if it cannot be run as a check with an exit code, it is not a gate.

**The tuning ladder (minimum fair chance).** Before a cross-credit comparison, each rule gets its best declared box:

- one legal completion on one cheap task;
- a **3-point ladder** on its primary knob (lr, γ, `readout_error`, settle steps), 1 seed each, plus one confirmation seed at the best point;
- its label channel declared (`error_blind`, `readout_error`, ...);
- a non-zero update and above-chance val_acc at the best ladder point
  (**error-blind credits are exempt**: chance is their contract; viability is
  a non-zero update, not accuracy).

No point above chance → triage as defect or capability gap, not an algorithm verdict. Best point above chance, confirmed on one more seed → that is the coordinate for a matched comparison. The ladder is **not** competitiveness HPO: 3 points, 2 seeds at the best point, one cell, recorded as a range, never as a claim.

**Defect triage (before a verdict).**

| Signal | Check | If it fails | If all pass |
|---|---|---|---|
| val_acc ≈ chance | label channel? pseudo-grad norm > 0? act/param counts match? | defect (name mechanism + test) | coordinate result (box) |
| No update | credit dispatch, shape, phase | defect, or the capability that removes it | — |
| Crash | shape/compatibility | defect + the primitive that removes it | — |
| High variance | settle convergence, seeds | coordinate result; n insufficient | — |
| Gate PASS at chance | gate has no metric bar | gate defect | — |

A defect is only a defect if fixing the named mechanism changes the cell or fails a test. Otherwise it is a coordinate result.

Error-blind credits (`homeostatic`, `temporal_trace`) never fail on accuracy: triage them on a non-zero update and their declared contract, not on val_acc.

**SEC invariants (universal).**

1. **Decision first.** No run without a stated decision and stop rule.
2. **Cheapest falsifier first.** A cheap rung that decides stops the climb.
3. **Stop when decided.** Evidence, not wall-clock, ends a rung; claims use sequential or fixed-n-with-no-peeking error control.
4. **Every negative names a defect, a capability gap, or a coordinate result.** A refusal is a box statement (infeasible or over budget), never an algorithm verdict; a mechanism that cannot train is a defect until a fix is tested.
5. **The box is part of the result.** No point estimate without its scope.
6. **Breadth before optimization.** Map viability first; HPO is successive halving/Hyperband under a total budget, not a per-run clock.
7. **A watchdog is a safety cap, not a budget.** It is priced from a measured pilot.
8. **Record the decision, rung, stop reason, and cost.** Time is an outcome.
9. **Error control scales with the claim.** Screening controls cost; claims control error.
10. **Measurement identity is reproducibility.** Seed, key, and replay hash travel with the number.

**Defect Patterns (Symptom → Likely Cause):**

| Symptom | Investigate |
|---------|-------------|
| val_acc ≈ chance | Forward pass, credit produces zeros, loss not flowing; check `error_blind` first — an error-blind credit (`homeostatic`, `temporal_trace`) measuring chance is its contract, not a bug |
| val_acc drops over epochs | Optimizer misconfigured, gradient explosion, weight decay |
| "free settle telemetry failed" | `forward_with_intermediates` act count ≠ param count |
| Positive control FAIL | Task's `geometry_hint` wrong, compatibility check |
| NaN/Inf loss | `max_energy` clamp, weight init, substrate noise |
| Credit fails on geometry | Missing `_<geometry>_path` in credit dispatch |
| Slow (>60s/epoch L0) | CPU-bound settle, no GPU kernel, `.to(cpu)` calls |
| Only last task in results | Store dedup key missing `task_id` |
| L1/L2 0 cells | Wave pricing uses L0 positive control, not measured cost |
| Worker hangs / CUDA OOM | ProcessPoolExecutor + single GPU (use sequential evaluator) |
| Run overruns budget | Deadline not injected into cell; no `kill_workers()` |
| Preview duplicates control | `_seen` shared between dry-run and real run |
| energy_min too slow | Default `max_steps=30`; measured optimum is 10 |
| Convergence never triggers | `convergence_threshold=1e-4` vs ~1e-3 plateau |

**Question Excluded Possibilities:**

| Assumption | Test |
|------------|------|
| "X is unfixable upstream" | Try version pins, config flags, workarounds |
| "Y is CPU-bound" | Profile; check for compiled kernels |
| "Z needs feature A" | Try alternative B (e.g., positional encoding vs patch embed) |
| "Substrate S doesn't support D" | Check settle kernel implementation |
| "Credit C fails on Geometry G" | Check compatibility matrix, add dispatch path |
| "Graph CUDA is unfixable" | Try `num_workers=0`, `pin_memory=False`, PyG version pin |
| "Energy min + recurrent = slow" | Check for GPU settle kernel (`_settle_compiled`) |
| "Transformer vision needs patch embed" | Try positional encoding on flattened patches |
| "Memristive no energy_min" | Check `SubstrateSettleKernel` for memristive |
| "Invalid combo in plan" | Verify compatibility in search space (see B2b, B2c, B3b) |
| "Registry populates itself" | Call `seed_all_registries()` at import (D11) |
| "Factory signature = knobs" | Use availability predicates, not `inspect.signature` (D13) |
| "Task comes from config fallback" | Task must come from run spec, validated against registry (D14) |
| "Composition knows topology" | Topology is axis value; merge from geometry mapping (D15) |
| "Spatial facts from width" | Carry task's `input_shape` through to geometry builder (D16) |
| "Registered = trainable" | Mark `available=False` with `unavailable_reason` if kernel can't train (D17) |

**Harness Reliability Patterns (from TODO85/86):**

| Pattern | Implementation |
|---------|----------------|
| Per-epoch heartbeat | `log_every_n_epochs=1` in every trainer; `epoch k/N: loss=… val_acc=… 17s/epoch, ~100s left` |
| In-cell deadline | `params={"deadline_check": ..., "deadline_check_every_n_steps": 1}`; `train_epoch` returns incomplete epoch without history on deadline |
| Positive control cap | Pinned to L0, 60s cap, 1 epoch/1 seed; marked `seen` so wave never re-proposes |
| Honest wave sizing | `n_wave = budget_remaining / (measured_per_seed_cost × seed_plan)` at run's fidelity |
| Bounded proposal scan | `ModelBasedPolicy` pages 400-cell pages; `scan_start` advances only while pages exist |
| Explicit depth survives | `n_seeds`/`epochs` = `int | None`; `None`=ladder, explicit `1`=literal |
| Run lifecycle closed | `finish_run(run_id, "completed", budget_consumed_s)` + `experiments/<store>.run.json` |
| Seed-plan expansion | `n_seeds=3` → 3 single-seed records; replication key includes `task_id` |
| Multi-task waves | Proposal context unscoped; each proposal keeps its own task |
| Serial evaluator | One in-process evaluator; no `ProcessPoolExecutor`, one CUDA context, one dataset cache |

**Foundational Defects (from TODO46/47):**

| Defect | Symptom | Root Cause | Fix |
|--------|---------|------------|-----|
| D11: Registries empty at runtime | No objectives/policies/axes compose | `seed_all_registries()` not called at import | Call at module import in `seed_registries.py` |
| D12: PRIORS seeded then cleared | 28 priors discarded; step_size falls back | Clear once after import, then register both sources | Order: import → clear → register all |
| D13: Factory signature ≠ knobs | `step_size` gate decided from dataclass fields | Availability predicates, not reflection | Harvest `accepted_params` at seed time |
| D14: No run named real task | `task_id="default"`; "unknown task" at eval | Task from run spec, validated vs registry | Fail loud if task not in registry |
| D15: Composition ignored topology | `topology_type` from geometry, not axis value | Merge axis topology into geometry mapping | `_geometry_mapping` includes topology |
| D16: Spatial facts guessed from width | `in_channels=3`, `input_hw=(28,28)` hardcoded | Derive from task's `input_shape` (channels first) | Pass `input_shape` through compose chain |
| D17: Registered ≠ trainable | `tile`/`nca` compose then die at runtime | `available=False` + `unavailable_reason` | Search space filters unavailable |
| D24: `comp report` crashes empty store | Raw traceback on no data | Handle empty store gracefully | Guard before query |
| D25: `--dry-run` writes store, silent | Creates `experiment.duckdb`, prints nothing | Dry-run before store create; print plan | Check `dry_run` first |
| D26: Capability rows name dead tests | "Verified" capability = `pytest: no tests ran` | Fixture must contain case lock exists for | Lock fixture exercises the mechanism |

**Testing / Execution Rules (from TODO47):**

| Rule | Mechanism |
|------|-----------|
| Select tests by symbol, not directory | `grep -rn <symbol> tests/ --include=*.py`; run 2–4 files |
| Kill destroys evidence → log | `pytest -rf --tb=line > log` on any launch that may be interrupted |
| Prices stale → measure once | Price from one ≤60s measurement, write in ticket |
| Fake gates indistinguishable | Fixture must fail when mechanism removed |
| Cheap work seductive → queue by deliverable | Order tickets by unblocking the runnable assertion |
| Context re-paid → file is the queue | Landed work leaves queue; does not enter it |
| Correction as interruption → rules in AGENTS.md | Permanent rules in AGENTS, not prose in TODOs |
| Nothing reports which gate runs | Ticket names gate, cost, dependencies |
| Killed run yields no verdict | `pytest <dir> --co -q > ids.txt` collects, do not re-run |
| One shard per round close | Never per commit; never re-run green shard |
| Lock fixture must contain the case | If removing mechanism cannot fail fixture, lock is a comment |

**Search Space / Compatibility Lessons (from TODO86):**

| Invalid Combo | Reason | Valid Alternative |
|---------------|--------|-------------------|
| conv geometry + graph node classification | Conv treats node features as spatial grid; shape mismatch | graph geometry |
| gradient credit + graph/instantaneous | Gradient unavailable for graph with instantaneous dynamics | random_projections, homeostatic, pc_alm, target_inversion, temporal_trace |
| gradient credit + recurrent/instantaneous | Gradient cannot compute recurrent weight grads with instantaneous | random_projections, temporal_trace, homeostatic, pc_alm, target_inversion |
| recurrent + energy_minimization | Works but ~120s/cell L0 (settle loop per env step) | Use instantaneous + compatible credit |

**Metric / Task-Aware Evaluation (from TODO85):**

| Issue | Fix |
|-------|-----|
| Validator metric mismatch | `_update_task_metrics` uses registry `payload_key` for primary metric |
| Cross-task claims mix raw `val_acc` | Normalized metric stored; claims should prefer it |
| wine/iris val_acc=0.0 | Investigate feature normalization / class mapping before treating as baseline |
| iris high seed variance | Treat as under-powered; rerun with more epochs/seeds |
| Task never cycled | Persistent `_task_cycle`/`_task_index` on `PolicyPlanner` |
| Progress hid tasks | Every cell logs `task=<id>` alongside axes |

**Budget / Fidelity Management:**

| Lesson | Practice |
|--------|----------|
| Adaptive L0 share | 30% for spaces <1000 primitives, 50% otherwise |
| Ladder starves L1/L2 | Stage budget = time actually left; cells priced from measured walltime × epoch ratio; unaffordable skipped |
| Serial budget arithmetic | Budget must cover sum of cell walltime; long-task sweeps need bigger budget or fewer epochs |
| Per-step logs opt-in | Per-epoch always on (`log_every_n_epochs=1`); per-step needs `log_every_n_steps > 0` |
| Killed runs not closed | SIGKILL leaves `running` + no manifest; SIGTERM closure deferred until needed |

**Common Fixes (Expanded from TODO85/86/87 + Foundational TODO46/47):**

| Symptom | Fix | File |
|---------|-----|------|
| Only one task in results | `task_id` in store dedup key | `evidence/store/_transactions.py` |
| Cell FAILs though training fine | Gate on core metrics only; drop auxiliary NaNs | `kernel/evaluate.py` |
| Worker crash mid-cell | Per-cell timeout + deadline check | `wave.py` |
| Run overruns budget | `kill_workers()` at deadline | `wave.py` |
| L1/L2 measure 0 cells | Size stage from measured cell cost + time left; skip unaffordable | `wave.py` |
| energy_min cells too slow | Default `max_steps=10` (measured optimum) | `dynamics/_dynamics.py` |
| Ternary fails gate | LR scaling by weight_bits; straight-through estimator | `substrate.py`, `update.py` |
| Ternary + energy_min crashes | TWN ternary thresholding (0.7*E[|W|]); energy uses kernel.effective_weights() | `substrate.py`, `_dynamics.py` |
| Neuromorphic + non-temporal crashes | Compatibility filter in search space | `search_space.py` |
| Jacobian SVD NaN | isfinite guard + fallback | `jacobian.py` |
| Search space too large | Filter incompatible at harvest | `search_space.py` |
| TPE stuck on one combo | `min_samples_per_combo=3` | `policy.py` |
| Planner yields 0 cells | Clear `_seen` between startup/wave | `wave.py` |
| Gate false negative | Fix validation logic | `system.py` |
| CUDA multi-worker hang | Sequential evaluator, single GPU context | `wave.py` |
| Positive control ran at run fidelity | Pin to L0, 60s cap, mark seen | `wave.py` |
| Tasks resolved after spec | Resolve task list before `_build_spec` | `survey_cli.py` |
| Budget enforced between cells | In-cell deadline, not between cells | `wave.py` |
| Preview-then-run shared `seen` | Previews only when `dry_run=True` | `wave.py` |
| Registries empty at runtime | Call `seed_all_registries()` at import | `seed_registries.py` |
| PRIORS seeded then cleared | Clear once after import, then register all | `seed_registries.py` |
| `step_size` gate from signature | Availability predicates, harvest `accepted_params` | `kernel/_geometry_builders.py`, `search_space.py` |
| Task = "default" | Task from run spec, validated vs registry | `wave.py`, `survey_cli.py` |
| Composition ignores topology | Merge axis topology into geometry mapping | `compose.py` |
| Spatial facts hardcoded (3, 28×28) | Derive from task `input_shape` (channels first) | `kernel/_geometry_builders.py` |
| Registered primitive dies at runtime | `available=False` + `unavailable_reason` | `search_space.py`, `task_registry.py` |
| `comp report` crashes on empty store | Guard before query | `surface/report.py` |
| `--dry-run` writes store, silent | Check `dry_run` before store create; print plan | `survey_cli.py` |
| Capability rows name dead tests | Fixture must fail when mechanism removed | `surface/conformance.py`, test files |
| Dataset ordered by class, tail-slice split | Stratify + report majority baseline | `domains/tabular.py` |
| Claim finer than the metric's granularity | Report the resolution; fold-mean or a larger split | `domains/tabular.py`, `domains/factory.py` |
| Credit needs an input channel the pipeline never adds | Mark the row unavailable with the reason | `schema/seed_registries.py` |
| Graph task proposed on node-mode geometry | Domain-exclusive geometry filter | `kernel/search_space.py` |
| Explicit `1` read as "unset" (`!= 1`) | Test `is not None`; ladder only on `None` | `kernel/search_space.py` |
| Budget cut recorded as `constraint_violation` | Cause `timeout`; admission-check the cell's measured cost | `kernel/evaluate.py`, `wave.py` |
| Dry-run gate scores RL with a supervised loss | Skip RL and one-class heads | `kernel/compose.py` |

**Breadth check (before a cross-credit claim; `uv run comp gate breadth` prints the gaps, exit 1 until green — a documentation check, not a permission gate):**
- every declared axis value is live / infeasible-at-its-box / unavailable, each with a trigger;
- every error-aware credit has ≥1 legal, above-chance cell on the task family
  it targets, with its label channel declared; ≥2 task families is this
  check's own gap, not a gate on exploration;
- every legal composition family has a cell that trains (no unexplained
  chance-level cell);
- the map is recorded in the plan's scoreboard, not a leaderboard.

A matched comparison is pre-registered with the compute case the map supports;
it does not wait for a complete map.

**Competitiveness HPO (after each arm's best point).** Use successive halving or
Hyperband: many configurations at 1 epoch, promote the top fraction to 5, then
20, and kill the rest. The budget is total compute, not per-run timeboxes;
pre-register the search space, the promotion rule, and the total budget.
Report the box and the cost beside the metric.

**Success Criteria (per domain):**
- Vision (MNIST/CIFAR): best val_acc > 0.95
- Graph classification: best val_acc > 0.70
- Node classification (Cora): best val_acc > 0.75
- RL (Pendulum): mean_reward > -200
- Tabular (Iris): best val_acc > 0.90
- ≥3 **error-aware** credits work per geometry (`homeostatic` and
  `temporal_trace` declare `error_blind=True`: they read no label, so they
  measure chance by contract — never count them toward this criterion)
- Zero "free settle telemetry failed" warnings
- Every positive control completes and reports its bar verdict (PASS, or a
  named `below bar` FAIL); a 1-epoch control on a hard task may be FAIL-by-bar
  without invalidating the run — `wave.py` logs the verdict and continues
- 4+ claim-eligible cells per multi-task run (n_seeds × tasks)
- **Every number carries its ruler.** State the metric's resolution beside it
  (held-out samples for a split, episodes for RL, folds for a fold-mean) and the
  chance/majority rate it is measured against.
- **A claim within 1 σ of its threshold is `marginal`, not met.** Re-measure it
  as a pre-registered paired comparison (`configs/preregistrations/<slug>.json`,
  `computronium.validation.preregistration.PairedComparison`) or state the arm it
  needs. Do not round it up.
- **A ticket closes on a claim, a named verdict, or a capability that now
  works.** A session that lands a primitive or fixes a blocking defect closes
  it, even when no number moves; a fix that does neither is hygiene and belongs
  to round close.
- **Every error-aware credit has a viable cell on its target task family**
  before a cross-credit claim; ≥2 families is the breadth check's own gap.
- **No cross-credit conclusion from a cell without a declared hyperparameter
  box and a viability ladder.** The box is part of the result.
- **A low cell is a named defect or a capability gap with the fix it needs —
  never "the algorithm fails". A measurement verdict is never final for a
  mechanism: the fix is the next rung.**

**Session Log Template (commit message body; never appended to the TODO):**
```
## Session YYYY-MM-DD
**Decision:** <question, actions, error costs>
**Experiment:** <command>
**Box:** <task, fidelity, seeds, knobs allowed>
**Rung / stop:** <0-4; why the rung stopped>
**Result:** <metric, ruler, cost>
**Triage:** <defect | capability gap | coordinate result; if defect, the failing test; if gap, the primitive that closes it>
**Fixes Applied:** <files changed>
**Next Experiment:** <planned command>
```

**Experiment Log Table (for multi-run tracking):**

| Run | Axes | Box (task/fidelity/seeds/knobs) | Rung / stop | Walltime | Crashes | Gate Failures | Verdict | Fix Applied |
|-----|------|----------------------------------|-------------|----------|---------|---------------|---------|-------------|
| N | <axis_json> | <task, fidelity, n_seeds, knobs> | <0-4; why> | <s> | <n> | <n> | defect / capability gap / coordinate | <file/change> |

**Never:**
- Accept "this algorithm doesn't work" without the tuning ladder, triage, and a tested fix
- Record a verdict that closes a mechanism: a low cell is a defect probe
- Gate a primitive behind a negative measurement: primitives are admitted by the capability they add
- Use a wall-clock budget as the primary stop rule (the watchdog is a safety cap)
- Run a cell without a measured cost model (the watchdog is 2× that model)
- Stop a fixed-n comparison early and report its CI as sequential
- Climb a rung after a cheaper rung has decided the question
- Report a result without its rung, stop reason, and cost model
- Skip the positive control gate
- Commit without targeted tests passing
- Commit a registration with its result and call it pre-registered (a post-hoc margin is not error control)
- Close a gate in prose when the repo has no check for it
- Use `ProcessPoolExecutor` on single GPU
- Price waves from L0 positive control
- Hardcode task names in execution paths
- Let auxiliary NaNs discard valid cells
- Run with `convergence_threshold < 1e-3` for energy_min
- Accept `max_steps=30` default for energy_min
- Close a ticket that landed a capability or fixed a blocking defect on "no number moved"
- Call a result "met" when it sits within 1 σ of its threshold
- Rank credit families on an under-tuned comparison: tune each arm to its best box first
- Call a low cell evidence for/against an algorithm before the defect probe and the fix
- Call something a defect without a named mechanism and a failing test
- Use "unconcluded" as a permanent verdict after the ladder has run
- Report a point estimate without the hyperparameter box it is conditional on
- Tune a knob to make a cell pass before the triage verdict

---

## 🔄 META: The Self-Stabilizing Loop

**The SEC methodology is a fixed point of the process it describes.**

| Computronium (system) | SEC Methodology (development) |
|----------------------|-------------------------------|
| 6 axes × primitives → search space | decision loop × rung ladder × defect triage → fix space |
| Positive control (gate) | Positive control PASS (100% target) |
| Energy minimization (settle to fixed point) | DECIDE→FALSIFY→TRIAGE→FIX→VERIFY (stop when decided) |
| Credit assignment (local learning signal) | Viability ladder (minimum fair chance before ranking) |
| Defect patterns (symptom → cause) | Defect triage (defect / capability gap / coordinate result) |
| Harness reliability (heartbeat, deadline) | Test selection by symbol, kill logging, measured pricing |
| Excluded possibilities (S/G/D/C/U/P) | Question excluded possibilities table |
| Normalized metrics (ruler-relative) | Per-domain success criteria + declared hyperparameter box |
| Claim eligibility (n≥5, replay hash) | Targeted tests + commit with evidence |
| Search space breadth | Every arm at its best declared box before any comparison |
| Time/effort control | Rung ladder + 2× measured-cost watchdog (no wall-clock budget) |
| Competitiveness HPO | Successive halving / Hyperband under a total budget |
| Statistical error control | Sequential/always-valid CI for claims; no optional stopping |

**Why it stabilizes:**

1. **Every anomaly is a triage question** — low val_acc ≠ "algorithm failure"; it is a defect, a capability gap, or a coordinate result, and the viability ladder gives every approach a minimum fair chance before any verdict.
2. **Every assumption is testable** — "unfixable upstream" gets a concrete test.
3. **Every fix has a file** — symptom → fix → file mapping prevents drift.
4. **Every run priced from reality** — no stale L0 positive control pricing.
5. **Context preserved in code** — AGENTS.md rules, not prose in TODOs.
6. **Every negative has an exit** — a named defect with a failing test, a capability gap with the primitive that closes it, or a boxed coordinate result. "Unconcluded" is not a permanent state.
7. **Tuning before ranking** — each arm reaches its best declared box before any comparison; the capability map is the artifact.
8. **Time is an outcome** — the rung ladder and the 2× measured-cost watchdog replace arbitrary clocks; a cheap decision stops cheap.
9. **Claims control error** — screening stops freely; claims use sequential or fixed-n CIs, never optional stopping.

**The meta-stabilization:** The SEC methodology was refined by the same cycle it describes:
> DECIDE (decision + box) → FALSIFY (smallest rung) → TRIAGE (defect/capability gap/coordinate) → FIX (integrate into AGENTS.md) → VERIFY (tests pass) → RECORD+COMMIT

This document *is* the fixed point. The methodology describes the process that produced it.
