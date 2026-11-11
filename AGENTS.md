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
**Principle:** *Be skeptical of low-performing experiments; this could indicate an implementation defect to fix. Be suspicious of any excluded possibilities that may actually be possible.*

**When to use:** Any time you're validating a system with multiple algorithm/architecture combinations and need to distinguish "this doesn't work" from "this is broken."

**The Cycle (≤30 min total):**

1. **RUN** (≤15 min) — `survey_cli` with focused axes, single fidelity, few seeds
   ```bash
   uv run python -m computronium.experiment.survey_cli 0.1 \
     --mode learn --policy tpe --device cuda \
     --tasks <task> --fidelity L0 \
     --axes '<focused_json>' --epochs 3 --n-seeds 1
   ```

2. **ANALYZE** (30s) — `comp report`, `comp coverage`, check for:
   - val_acc ≈ chance (forward/credit broken)
   - val_acc drops over epochs (optimizer/gradient issue)
   - "free settle telemetry failed" (geometry not layered)
   - Positive control FAIL (wrong geometry_hint)
   - NaN/Inf loss (energy clamp/init)
   - All credits fail on one geometry (missing dispatch)
   - Only one task appears in results (dedup key missing task_id)
   - L1/L2 measure 0 cells (budget sizing wrong)
   - Worker crashes / timeouts (process pool + single GPU)

3. **FIX** (≤15 min) — Infrastructure only; suspect low performance = defect
   - Check activation shapes match param shapes
   - Check credit pseudo-gradients are non-zero
   - Check geometry compatibility matrix
   - Check device placement (CPU vs CUDA)
   - Check for silent `.to(cpu)` calls
   - Check dedup key includes `task_id`
   - Check wave pricing uses measured per-seed cost × seed plan
   - Check positive control pinned to L0/60s cap

4. **VERIFY** (0.02h) — Quick re-run same config

5. **COMMIT + LOG** — Update TODO with session log

**Defect Patterns (Symptom → Likely Cause):**

| Symptom | Investigate |
|---------|-------------|
| val_acc ≈ chance | Forward pass, credit produces zeros, loss not flowing |
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

**Common Fixes (Expanded from TODO85/86/87):**

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

**Success Criteria (per domain):**
- Vision (MNIST/CIFAR): best val_acc > 0.95
- Graph classification: best val_acc > 0.70
- Node classification (Cora): best val_acc > 0.75
- RL (Pendulum): mean_reward > -200
- Tabular (Iris): best val_acc > 0.90
- ≥3 credits work per geometry
- Zero "free settle telemetry failed" warnings
- 100% positive control PASS rate
- 4+ claim-eligible cells per multi-task run (n_seeds × tasks)

**Session Log Template (append to TODO):**
```
## Session YYYY-MM-DD
**Experiment:** <command>
**Result:** <PASS/FAIL, key metrics>
**Defects Found:** <list>
**Fixes Applied:** <files changed>
**Next Experiment:** <planned command>
```

**Experiment Log Table (for multi-run tracking):**

| Run | Axes | Walltime | Crashes | Gate Failures | Worst Combo | Fix Applied |
|-----|------|----------|---------|---------------|-------------|-------------|
| N | <axis_json> | <s> | <n> | <n> | <combo> (val_acc) | <file/change> |

**Never:**
- Accept "this algorithm doesn't work" without verifying implementation
- Run experiments >15 min without a hypothesis
- Skip the positive control gate
- Commit without targeted tests passing
- Use `ProcessPoolExecutor` on single GPU
- Price waves from L0 positive control
- Hardcode task names in execution paths
- Let auxiliary NaNs discard valid cells
- Run with `convergence_threshold < 1e-3` for energy_min
- Accept `max_steps=30` default for energy_min
