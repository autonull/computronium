# TODO56 — One Time-Boxed Loop: Make Experiments Spend Their Budget

**Status: WS-A/B/C/D code complete (incl. showcase.py tier retirement + CellStream/BatchSizer wiring). NOT yet validated end-to-end. CRITICAL BLOCKER FOUND (see §12): `run_experiment.py` routes through `run_campaign` (YAML), whose search-space startup is unbounded and ignores the deadline, so `--hours 0.001` never returns promptly. NEXT SESSION: rewire the runner to `PipelineRunner` directly, then run the §7 ladder.**

We have burned hours fixing bugs and still have not run a single meaningful
experiment. The deadline clock (`deadline.py`) is correct and stays correct — it
stopped a campaign at 116.5s of a 3600s budget (`showcase_1h.log`). The bug is
upstream: the runner is built around a *finite space to complete*, so it declares
"exhausted" when the *reachable* window is empty and stops. The ontology is not
exhausted — 15.4M declared cells, measured this session — and it never will be.
The harness must accept that and be rewritten around one invariant:

> **A campaign runs until the deadline. Nothing else stops it.**

---

## 1. Non-negotiable budget contract

Every run must satisfy, and be tested on, both bounds:

1. **Upper bound:** `elapsed <= budget + grace` (grace = 30s, already enforced).
   - A batch is started only if `remaining_soft > margin + estimated_batch_time`.
   - A report reserve (default 60s) is held back so reporting cannot overshoot.
2. **Lower bound:** `elapsed >= budget - epsilon` unless the operator interrupts.
   - The *only* legal terminations are (a) deadline, (b) SIGINT/SIGTERM.
   - Any other termination — empty stream, "fruitless" rounds, all-seen batch,
     single-round cap, 80% sub-budget — is a **defect**, not a feature, and is
     asserted against in tests.
3. **Yield:** `records > 0` and `distinct_cells > 0`. A run that spends the
   budget measuring nothing is a failure, not a success.

`budget_utilization = elapsed / budget` is written into every report. Target
`>= 0.90` for a clean run.

---

## 2. Confirmed root causes (evidence from this session — do not re-litigate)

The space is astronomically larger than any budget. The underrun is caused by
five independent ceilings/stops, any one of which ends the campaign early:

| # | Ceiling | Location | Effect |
|---|---------|----------|--------|
| C1 | `_MAX_SCAN = 50_000` is a terminal cap on `iter_candidates` | `search_space.py:47,798` | The walk never examines past the first 50k of 15.4M cells; there is **no paging**. |
| C2 | `n_propose` defaults to `10` and S3 never sets it | `policy.py:171`; `stages_impl.py:322-336` | Every round proposes ≤10 cells regardless of budget. |
| C3 | `_MAX_FRUITLESS_ROUNDS = 3` stops the loop | `pipeline.py:82,668-686` | Three rounds that measure nothing end the run. |
| C4 | `last_batch_was_all_seen` stops the loop | `pipeline.py:996,672-678` | An all-already-measured batch is read as "space exhausted". |
| C5 | Per-run `budget_seconds = 0.8 * deadline` | `showcase.py:364,451` → `campaign.py:168-172` | Pipeline deadline is 80% of the wall budget by construction. |

Supporting evidence:
- Reachable vs declared: first 3000 scanned → **168 (5.6%)** survive
  `_composable` (`SystemConfig.validate`); declared count for one task is
  768,768, for the full showcase **15.4M**.
- A tier driver (`showcase.py:510-535`) creates a **fresh runner per tier**,
  resetting the policy cursor and multiplying the early-stop surface.
- `adaptive_budget.py:229-241` hard-codes a `recurrent`/`recurrent_attractor`
  axis filter — a second source of truth for legality that must not exist.
- Invalid combos reach the trainer and are retried: the log shows
  `gradient+instantaneous+recurrent` failing at train, yet
  `_composable(recurrent, instantaneous, gradient)` was verified `False`. A
  producer bypasses the screen; failures are not stored, so they are re-proposed
  every round until C3 fires in ~3 rounds ≈ 2 min.

**Conclusion:** TODO55's previous TODO56 framing ("expand the search space",
"raise `n_trials`") attacks the wrong layer. The space is already huge. Fix the
runner, the pacing, and the stops.

---

## 3. Target architecture — the single time-boxed loop

Replace the tier cascade and the round-exhaustion FSM with **one** loop:

```python
deadline = Deadline.from_hours(hours)          # persisted, monotonic
stream   = CellStream(spec, space, policy)     # unbounded, advancing
sizer    = BatchSizer(deadline, timing)        # budget-sized n_propose
while not deadline.soft_expired() and not shutdown_requested:
    k = sizer.n_propose()                      # from remaining time × median cell time
    if not sizer.can_start(k):                 # not enough time for a safe batch
        break
    batch = stream.next(k)                     # screened; mints fresh cells in exploit mode
    run_and_record(batch)                      # admission-gated, failure-isolated
write_report()                                 # from the report reserve
```

Three supporting objects, each small and testable:

- **`CellStream`** — an unbounded, *advancing* generator of `(Coordinate, Schedule)`
  that pages past `_MAX_SCAN` and, when the structural grid is spent, ladders
  into hyperparameter-sweep steps → seeds → tasks → policy-minted fresh points.
- **`BatchSizer`** — turns measured cell time + remaining soft time into `k`.
- **Admission gate** — the last-mile `SystemConfig.validate` check at the batch
  boundary, with a durable rejected-key blacklist.

Legality has exactly **one** source: `SystemConfig.validate` reached through
`_composable` / `compose_configs`. Remove every other axis filter.

### 3.1 Explore → exploit is a policy mix *inside* one loop, never tiers

- **Regime A (explore, first ~40% of budget):** round-robin over the structural
  grid × the declared hyperparameter ladder. Broad, reproducible coverage.
- **Regime B (exploit, remainder):** `ModelBasedPolicy`/`EvolutionPolicy`
  minting *fresh* hyperparameter settings around the current best cells. This is
  an **unbounded** generator — it can always propose a coordinate the store has
  never seen — which is what makes "run until deadline" always achievable.
- Transition is driven by `budget_fraction_elapsed`, not by a tier boundary. If
  Regime A exhausts early, enter B immediately. **Never stop.**

---

## 4. Workstreams (each ends with tests + a runnable check)

### WS-A — `CellStream`: unbounded, advancing, resumable
- Add paging to `search_space.iter_candidates` (`search_space.py:722`): replace
  the terminal `_MAX_SCAN` guard (`:47,:798`) with a `cursor`/`page_size`
  parameter. `_MAX_SCAN` becomes `_PAGE_SIZE` (keep 50k as the page, not the cap).
- New `CellStream` (new module `computronium/experiment/execution/stream.py`):
  - `next(k) -> list[(Coordinate, Schedule)]`, always advancing a persisted
    `offset`; when a page yields nothing new, advance the regime ladder
    (ladder step → seed → task → exploit policy).
  - `is_fresh()` uses `ProposalContext.fresh` (store history) — the store stays
    the only history (R71).
  - `get_state()/set_state()` for checkpoint/resume so a relaunched run continues
    the stream instead of restarting it.
- Delete the `recurrent` axis filter in `adaptive_budget.py:229-241`; legality is
  the constraint engine's job.

### WS-B — `BatchSizer`: budget-sized batches
- New `BatchSizer(deadline, timing, *, min_k, max_k, safety, report_reserve_s)`.
  - `n_propose()`: `max_k` until a median exists (cold start), then
    `clamp(remaining_soft / (safety * median_cell_time), min_k, max_k)`.
    Default `safety=1.5`, `min_k=4`, `max_k=64`.
  - `can_start(k)`: `remaining_soft > report_reserve_s + safety * k * median`.
- Wire `k` into **every** `ProposalContext`: `stages_impl.py:322-336` (S3) and
  `:229-241` (S1). `n_propose=10` default (`policy.py:171`) is removed from the
  hot path; it becomes a hard fallback only.

### WS-C — One stop condition + last-mile admission gate
- `pipeline.py:590` `_run_round_loop`: the loop condition becomes
  `deadline`/`shutdown` only.
  - **Delete** C3 (`_MAX_FRUITLESS_ROUNDS`, `pipeline.py:82,668-686`) and C4
    (`last_batch_was_all_seen`, `:996`) as *stops*.
  - On an empty batch: log, call `stream.advance_regime()`, continue. If the
    stream genuinely cannot advance (bug), raise — do not silently stop.
- **Admission gate** in `pipeline.py:_fresh_batch_items` (`:966`): for each
  candidate, run the evaluator's own `compose_configs` → `SystemConfig.validate`.
  On failure, append a classification to `state.rejections`, add the key to a
  durable `rejected_keys` set that `fresh()` consults, and skip. Invalid cells
  **never** reach the trainer; failures are never retried.
- **Fail loud on uniform all-fail:** if `K>=3` consecutive batches produce zero
  successes with a single shared failure cause, abort with a diagnostic
  (`ZeroYieldError`) — a reviewable failure, not a silent 2-minute "success".

### WS-D — Retire the tiers; one entrypoint
- New canonical runner **`scripts/run_experiment.py`**:
  `--hours N --device auto|cpu|cuda --store results/exp.db [--axes ...] [--policy ...]`.
  It builds one `RunSpec`, one `Deadline`, one `PipelineRunner` with
  `max_rounds=None`, and calls `runner.run()` once. No tiers.
- Retire the tier driver in `showcase.py` (`:510-535`) and the per-run 0.8 factor
  (`:364`). `showcase.py` becomes a thin wrapper (or is deleted — no back-compat).
  `showcase_v2.py` is the reference skeleton and should be folded into
  `run_experiment.py`.
- `campaign.py:178-180`: keep `max_rounds=1` **only** when `S10_DECIDE` is truly
  absent, and log loudly when it fires; `production-map` includes S10
  (`cli.py:151`), so a normal run is `max_rounds=None`.

### WS-E — Utilization reporting + locks
- Report fields: `budget_s`, `elapsed_s`, `budget_utilization`, `records`,
  `distinct_cells`, `pareto_points`, `coverage`, `failure_taxonomy`,
  `termination_reason` (one of `deadline|interrupt` for a passing run).
- Report generation runs **inside** the report reserve and its cost is recorded.
- Locks:
  - `tests/property/test_budget_utilization_lock.py`: a 3s-budget run must have
    `termination_reason == "deadline"` and `budget - eps <= elapsed <= budget + grace`.
  - `tests/property/test_admission_gate_lock.py`: a `recurrent + instantaneous +
    gradient` proposal is rejected and never trained; the same key is not
    re-proposed.
  - `tests/property/test_stream_advances_lock.py`: the stream yields novel cells
    past one page boundary.

---

## 5. Anticipated problems & recovery playbook

**Overshoot (past budget).**
- Cause: a large batch started near the deadline; a hung cell; slow reporting.
- Recovery: `BatchSizer.can_start` refuses unsafe batches; per-cell epoch cap
  (`resources.max_epoch_time_sec`, default 120s) bounds one cell; hard deadline +
  30s grace is the backstop; report is reserved (60s). If a batch overruns, it is
  abandoned at the hard deadline and its cells are quarantined.
- **Resume overshoot:** persist `deadline_ts` (absolute monotonic → wall) in run
  metadata. On resume, `remaining = persisted_deadline - now`; never recompute a
  fresh full budget from `now`.

**Undershoot (early stop).**
- Cause: any of C1–C5, empty stream, uniform failure.
- Recovery: WS-A/WB/WC remove every stop except deadline/interrupt; the
  utilization lock fails the build if a run ends early. Empty stream → advance
  regime; uniform all-fail → abort loudly with diagnostics (not a silent stop).

**Invalid cells reaching the trainer.**
- Cause: an upstream producer path bypasses `check_composable`.
- Recovery: WS-C admission gate at the batch boundary uses the evaluator's own
  `compose_configs`, so *no* producer can leak. Repro to locate the original
  bypass: grep the failing cell key from a log, rebuild the `Coordinate`, and
  trace the producing stage; close it too, but the gate is the guarantee.

**Hung / pathologically slow cell.**
- `LocalBackend` uses `asyncio.to_thread`, which cannot be cancelled. Mitigation
  now: small `max_k`, per-cell epoch cap, and a deadline check between cells so a
  batch cannot exceed `k * max_epoch_time`. Follow-up: a process-based backend
  with `asyncio.wait_for` to hard-kill a single cell. Document the residual risk
  in the run report.

**GPU OOM / nondeterminism.**
- Existing per-cell failure isolation keeps siblings alive; OOM is classified and
  the key blacklisted. `param_budget`/`max_params` bound memory. Determinism via
  fixed `seed` + `deterministic` + captured env + replay hash.

**Checkpoint / resume integrity.**
- Persist `stream` cursor + policy state + `deadline_ts`. Write checkpoints
  atomically (temp + rename). On load, validate; if unreadable, fall back to
  store-derived `completed_measurement_keys` and restart the stream from offset 0
  (`fresh()` dedups measured cells, so this is wasteful but correct).

**Store concurrency / parallelism.**
- Keep `max_parallel=1` and `--cells-per-round` small for the *first* meaningful
  run — correctness before throughput. If raising workers later: single-writer
  `append` (already atomic) + a lock around `CellTiming` (PEP 703: do not rely on
  the GIL).

**"Meaningful results" is not defined → cannot review.**
- DoD (below) fixes concrete thresholds so the report is reviewable by
  construction.

**Tooling traps (binding, from AGENTS.md).**
- Tests only via `uv run python -m pytest`; never bare `pytest`; never
  `pytest tests/`; `-n 4` is already in `addopts`.
- Long runs go to background: `nohup uv run python scripts/run_experiment.py ... >
  logs/exp.log 2>&1 &`, polled at ≤2-min intervals with a pre-registered kill time.
- Never `pkill` (it hangs). Dev-env smoke before any gate:
  `uv run python -c "import optuna, scipy, torchvision, pytest"`.

---

## 6. Definition of done

A run of `scripts/run_experiment.py --hours H` is **done** when all hold:

1. `termination_reason == "deadline"` (or `interrupt` for operator stops).
2. `budget - eps <= elapsed <= budget + grace` (eps = 2% of budget, or 5s, whichever is larger).
3. `budget_utilization >= 0.90`.
4. `records > 0`, `distinct_cells > 0`, `pareto_points > 0`.
5. `failure_taxonomy` reflects *real* evaluator failures (empty is acceptable only
   if no cell failed); invalid combos appear as **rejections**, not trainer errors.
6. The HTML report renders: coverage matrix, Pareto table, failure taxonomy,
   termination/utilization line, and a repro command.
7. The three locks in WS-E pass.

---

## 7. Validation ladder (cheapest first; show output + walltime)

1. **Unit** (seconds): `CellStream` advances past a page; `BatchSizer` monotonic
   in remaining time and clamped; admission gate rejects the known-bad combo.
   `uv run python -m pytest tests/property/test_stream_advances_lock.py tests/property/test_admission_gate_lock.py -q`
2. **Budget smoke** (~3s budget, foreground):
   `uv run python scripts/run_experiment.py --hours 0.001 --device cpu --store /tmp/exp_smoke.db`
   Assert window + `records>0`.
3. **Short integration** (2 min, background): `--hours 0.0333`; confirm
   `termination_reason=deadline`, utilization ≥0.9, pareto >0.
4. **The real experiment** (§8).

---

## 8. The experiment we will finally run

**Hypothesis:** a broad balanced sweep over the full ontology, given one hour,
produces a Pareto frontier and axis-attribution signal that is stable and
reviewable — i.e., the harness works and the results are non-trivial.

**Command:**
```bash
nohup uv run python scripts/run_experiment.py \
  --hours 1 --device cuda --store results/exp_todo56_1h.db \
  > logs/exp_todo56_1h.log 2>&1 &
```

**Pre-registered checks on the resulting report:**
- utilization ≥ 0.90; elapsed ∈ [3540, 3630]s.
- `distinct_cells > 100`; `pareto_points > 20`.
- coverage matrix populated on ≥6 of the 7 axes.
- failure taxonomy dominated by *legal* residual failures, with invalid combos
  recorded as rejections.

**Post-run review items (what we actually look at):**
- Pareto table (accuracy vs param_count vs walltime).
- Per-axis attribution (which primitives move the objective).
- Stability atlas across dynamics families.
- Failure taxonomy ordering (is a single cause eating budget? → fix, rerun).

---

## 9. Anti-patterns — do NOT reintroduce these

- Completing the space, "exhaustion" detection, or fruitless-round limits.
- Fixed `n_propose=10`; fixed `max_rounds`; per-run budgets below the wall budget.
- Tiered runners that recreate the policy and reset its cursor.
- Axis filters in `adaptive_budget.py` or anywhere outside `SystemConfig.validate`.
- Silent early success. The only passes are deadline/interrupt with utilization ≥0.90.
- Retrying a cell the trainer already rejected.

---

## 10. Remaining TODO55 items (unchanged, post-fix)
- [ ] Phase F: Plugin API for custom objectives, substrates, dynamics (✅ Done)
- [ ] Phase F: Benchmark Contributions (✅ Done)
- [ ] Phase F: Tutorial Notebooks (✅ Done)
- [ ] Phase F2: Living Documentation — Catalog, Method Cards, FAQ (✅ Done)
- [ ] Phase F3: Community & Extensibility (✅ Done)

---

## 11. Progress Summary (this session)

### ✅ WS-A — CellStream: unbounded, advancing, resumable
- **search_space.py**: Replaced `_MAX_SCAN=50_000` terminal cap with paging via `offset`/`page_size` parameters. `_MAX_SCAN` → `_PAGE_SIZE` (50k page size, not cap).
- **Created stream.py**: New `CellStream` module with `next(k)` method, regime ladder (structural → sweep → seeds → tasks → exploit), `get_state()`/`set_state()` for checkpoint/resume, `add_rejected_key()` for admission gate integration.

### ✅ WS-A — Remove recurrent axis filter
- **adaptive_budget.py**: `_is_valid_combination()` now always returns `True` (legality single-sourced from `SystemConfig.validate`). Removed pre-filtering of recurrent geometries from BALANCED strategy.

### ✅ WS-B — BatchSizer: budget-sized batches
- **Created batch_sizer.py**: `BatchSizer` class with `n_propose()` (cold start → max_k, then `remaining_soft / (safety * median)` clamped to [min_k, max_k]) and `can_start(k)` (checks `remaining_soft > report_reserve + safety * k * median`).
- **pipeline.py**: Added `batch_sizer` to `PipelineState`, wired into `StageContext`, used in S3 Schedule stage via `ctx.batch_sizer.n_propose()`.

### ✅ WS-C — One stop condition + admission gate
- **pipeline.py**: 
  - Removed `_MAX_FRUITLESS_ROUNDS` and `last_batch_was_all_seen` as stop conditions.
  - `_run_round_loop` now only stops on deadline (soft/hard) or shutdown signal.
  - Added `ZeroYieldError` for uniform all-fail detection (K>=3 consecutive batches with same failure cause).
  - Added `rejected_keys` set to `PipelineState` for durable admission gate blacklist.
  - `_fresh_batch_items` now runs admission gate: calls `compose_configs` → `SystemConfig.validate` at batch boundary, adds rejected keys to `rejected_keys`, classifies as `ADMISSION_REJECTED`, skips invalid cells (never reach trainer).

### ✅ WS-D (core) — Canonical runner
- **Created scripts/run_experiment.py**: Single entrypoint with `--hours N --device auto|cpu|cuda --store path [--axes ...] [--policy ...]`. Builds one `RunSpec`, one `Deadline`, runs `run_campaign` once. No tiers.

### ✅ WS-D (cleanup) — showcase.py tier retirement (this session)
- **Rewrote `scripts/showcase.py`** as a thin single-loop wrapper: deleted `_run_tiered_campaign` (the tier driver that reset the policy cursor per tier) and deleted the `0.8 * deadline` sub-budget factor (`execution_seconds`); the YAML now passes the full `remaining_soft_seconds()`. Added `budget_utilization` + `termination_reason` fields to `ShowcaseReportData` and a new "Budget Utilization" HTML section. Advanced reporting (coverage matrix, Pareto, stability atlas, failure taxonomy, bias audit, notebook export, hypotheses) preserved.
- `showcase_v2.py` remains a stand-alone reference skeleton (candidate for later deletion; not on the critical path).

### ✅ CellStream wiring (this session)
- **pipeline.py**: `CellStream` created in `PipelineRunner.run()` after `_build_search_space`; stored on `PipelineState`; passed via `StageContext.cell_stream`. Checkpoint now serializes `cell_stream_state` (`_PipelineStateSnapshot` + `CheckpointData` gained the field); `_restore_from_checkpoint` rebuilds it.
- **stages_impl.py**: `FrameStage` (S1) and `ScheduleStage` (S3) now call `ctx.cell_stream.next(k)` instead of `ctx.policy.propose(...)`. S3 `k` still comes from `BatchSizer.n_propose()`.
- **Verified**: imports OK; `run_experiment.py --dry-run` OK; `showcase.py --dry-run` OK; `test_ontology_locks.py` 15 passed (14.3s). Dev-env smoke OK.

### ⏳ Remaining work (fresh session)
- **WS-E: three property locks (not yet written)**
  - `tests/property/test_budget_utilization_lock.py` — 3s-budget run: `termination_reason == "deadline"`, `budget - eps <= elapsed <= budget + grace`.
  - `tests/property/test_admission_gate_lock.py` — `recurrent + instantaneous + gradient` rejected, never trained, not re-proposed.
  - `tests/property/test_stream_advances_lock.py` — stream yields novel cells past one page boundary.
- **Validation ladder (not yet run end-to-end)**: unit (locks) → budget smoke (`--hours 0.001`, ~3s) → short integration (`--hours 0.0333`, 2 min background) → 1h experiment (§8).
- **Report fields**: `budget_s`, `elapsed_s`, `records`, `distinct_cells`, `pareto_points`, `coverage`, `failure_taxonomy` still need to be emitted from the canonical path (`run_experiment.py` currently delegates reporting to `run_campaign`; showcase.py emits its own summary). Reconcile so §6 DoD is machine-checkable.
- **Lint cleanup (non-blocking, register-C hygiene)**: `stream.py` (`next()` complexity, typing-only imports, stray bottom `islice` import), `pipeline.py` (admission-gate try-block size, `Proposal` import placement), `showcase.py` (too-many-statements/locals, `subprocess` partial path, unused locals), `batch_sizer.py` typing-only imports, `run_experiment.py` unused imports. `ruff format` clean; `ruff check` reports style findings only.

### Notes for next session
- `run_experiment.py` currently shells through `run_campaign` (YAML) rather than constructing `PipelineRunner` directly; the canonical single-loop path is the `PipelineRunner` wired in `showcase.py`/`showcase_v2.py`. Decide whether `run_experiment.py` should build `PipelineRunner` directly (cleaner DoD reporting) or keep the campaign YAML indirection.
- `CellStream._next_exploit` currently returns `[]` and defers to the pipeline; Exploit regime is **not** yet an independently-unbounded generator. Structural regime alone must keep the run alive for the first 1h run; verify it does not exhaust early (paging is 50k/page; declared showcase space ≈15.4M).
- `_is_fresh` in CellStream only checks the local rejected set; store-history dedup happens in `pipeline._fresh_batch_items`. Confirm no double-work/behavior drift.
- `rejected_keys` is persisted via CellStream state, not as a top-level store field — confirm resume reconstructs it (currently it does **not** re-load prior rejections across process restarts; only within the same checkpoint object).

---

## 12. NEXT SESSION — Do this first (blocker + ordered steps)

### 12.1 Confirmed blocker: the runner ignores its own deadline during startup
`scripts/run_experiment.py` does **not** use the single-loop `PipelineRunner`.
It builds a campaign YAML and calls `run_campaign(...)` (`scripts/run_experiment.py:169`),
whose `_execute_run` → `_run_pipeline` does startup work **before** the deadline
matters:
- `run_campaign` builds the run's `SearchSpace` from the full registry product
  (default profile selects *all* substrates/geometries/dynamics/credits/updates/
  plasticities → ≈15.4M declared cells).
- `search_space_from_spec` → `_filter_axes_for_validity` (`search_space.py:150`)
  scans that space (exact ≤100k, else per-primitive up to 500 checks each) — the
  "50s+ startup" path the module comment warns about, cached only per-process.
- Therefore `--hours 0.001` spends minutes in startup and the 3s deadline never
  bounds anything. The campaign→pipeline indirection is also the layer that
  WS-C/WS-D set out to retire.

**Fix:** make `run_experiment.py` construct `PipelineRunner` **directly**, exactly
as `scripts/showcase_v2.py` does (`showcase_v2.py:148-170`):
`RecordStore(...)` context → `store.create_run(spec)` → `PipelineRunner(PipelineConfig(run_id, run_spec, deadline=spec_deadline, policy=..., backend=LocalBackend(...), max_rounds=None), store)` → `await runner.run()`.
No campaign YAML, no `run_campaign`, no second store open. `showcase.py` already
routes through `run_campaign` too — decide whether it should call the same direct
helper so both entrypoints share one code path.

### 12.2 Verify startup is bounded on the direct path
Even wired directly, confirm `_build_search_space` is fast. If the default
(full-axes) profile still triggers the 50s scan, narrow the smoke's default axes
or seed `_filter_axes_cache`. Time `PipelineRunner.run()` entry explicitly.

### 12.3 Operational hygiene (these cost time last session)
- Kill stale runs before each attempt; they hold the DuckDB lock and the next
  attempt dies with `IOException: Conflicting lock`. Find PIDs with
  `ps aux | grep "[r]un_experiment"` and `kill -9 <pid>` (never `pkill` — it hangs).
- Never pipe a run through `tail`/buffering (AGENTS.md). Redirect to a log with
  `PYTHONUNBUFFERED=1 ... > logs/x.log 2>&1 &` and `cat` the log after.
- Always `rm -f` the store between retries.

### 12.4 Ordered acceptance sequence
1. Rewire `run_experiment.py` to `PipelineRunner` direct (§12.1).
2. Budget smoke, foreground, timed: `uv run python scripts/run_experiment.py --hours 0.001 --device cpu --store /tmp/exp_smoke.db`. Expect ~seconds total; assert `records > 0`, `termination_reason == deadline`, `elapsed ∈ [budget-eps, budget+grace]`.
3. If startup still dominates, fix §12.2 before anything else.
4. Write the three WS-E locks (still unwritten) and run them.
5. Short integration `--hours 0.0333` (2 min, background).
6. 1h run (§8).

### 12.5 Known-bad happened last session (do not repeat)
- `run_experiment.py` default objective `epoch_time_s` was invalid → `RunSpec`
  validation error. FIXED this session to `walltime_total`. Re-check any other
  objective names against `OBJECTIVES_REGISTRY`.
- `_build_run_spec`/`_resolve_spec` is ~6s (importable), not the bottleneck.
