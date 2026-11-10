# TODO86 — Scale & Coverage (Post-TODO85)

**Status:** Harness consolidated to one Python entry point; runs are observable and
close honestly. Next: finish scale/coverage combos.

**Baseline (Run 48):** 72 cells, 72 PASS, L0→L1→L2 working, best L2 0.9775 on mnist.

---

## 🎯 PHASE 1: GPU Scale Validation (Track C)

**Goal:** Prove GPU speedup at scale on the best combos. L2 depth is 20 epochs;
`hidden`/`batch` come from the harvested geometry defaults. (C3/C4 ran before the
seed-plan expansion landed, so each is a single-seed L2 measurement.)

| Experiment | Axes | Budget | Purpose | Status |
|------------|------|--------|---------|--------|
| C1 | digital/ff/instant/null/grad/euclid (best L2) | 2h | GPU vs CPU baseline at scale | ✅ Done |
| C2 | digital/ff/energy_min/null/grad/adam (2nd best L2) | 2h | GPU with settling at scale | ⚠️ Partial (see open items) |
| C3 | digital/ff/instant/null/pepita/adam (best non-grad credit) | 0.25h | Credit variety at scale | ✅ Done — 0.9746 @ L2 |
| C4 | memristive/ff/energy_min/null/grad/adam | 0.3h | Non-digital substrate at scale | ⚠️ 4/20 epochs in 1062 s (~208 s/epoch) |

**Prerequisites:** ✅ DONE
- Benchmark single cell: `hidden=256, batch=256, epochs=1` CPU vs CUDA
  - GPU: ~180s/cell (MNIST, hidden=256, epochs=1)
  - CPU: ~196s/cell (MNIST, hidden=256, epochs=1)
  - GPU ~8% faster — modest but positive
- If GPU not faster, investigate: settle loop sync, compilation, kernel launch overhead

**C1 Results:**
- Search space: 24 tasks compatible, 22 pass composability
- Evaluated 10 cells in 103s (budget exhausted on cheap tasks first)
- GPU ~8% faster than CPU on MNIST (hidden=256, epochs=1)
- L2 fidelity (epochs=20, n_seeds=5) walltime: ~30-110s/cell on cheap tasks
- Expensive tasks (mnist, cifar10) not reached due to task ordering in diverse permutation

**C2 Results:**
- Search space: 6 vision tasks pass composability (mnist, fashion_mnist, digits, usps, kmnist, cifar10)
- energy_minimization + feedforward: ~285s/cell at L2 on MNIST — the settling loop
  (iterative forward passes per step) dominates, so GPU gain is marginal
- A short budget measures only the positive control; C2 needs a settling-sized budget
- **Now measurable cheaply:** `--epochs N` is honored literally (see harness notes),
  so a settling cell can be priced at `--epochs 2` without waiting for the L2 default.

**C3 Results (this session):**
- `digital/feedforward/instantaneous/null/pepita/adam` on MNIST, L2 (20 epochs):
  **PASS, val_acc 0.9746**, 396s/cell, 416s run walltime (0.25h budget)
- Non-gradient credit reaches within 0.003 of the best gradient L2 (0.9775):
  credit variety is not buying accuracy, but it is not costing it at scale either.
- Per-epoch cost: 17–25s/epoch on CUDA (pepita's two forward passes per step).

**C4 Results (this session):**
- `memristive/feedforward/energy_minimization/null/gradient/adam` on MNIST, L2:
  **4 of 20 epochs in 1062 s**, val_acc 0.9737 at epoch 4 — **FAIL** (incomplete),
  deadline honoured truthfully.
- **~208–229 s/epoch on CUDA, CPU-bound** (98% CPU, 16% GPU): the memristive settle
  loop, not the accelerator, is the bottleneck. Digital instantaneous is ~17 s/epoch,
  so L2 depth needs ~70 min here, not 0.3 h.
- Accuracy is *not* the problem (0.9737 by epoch 4); throughput is. Rerun with
  `--epochs 4` for a like-for-like comparison, or give a settling-sized budget.
- The new per-epoch ETA showed this after epoch 1; previously the run was silent
  until the deadline.

---

## 🎯 PHASE 2: RL/Control Tasks (Track B1)

**Goal:** Full training loop for cartpole, pendulum, acrobot.

**Status:** ✅ COMPLETED - RLSystemTrainer implemented and tested

**Experiments:**
| Experiment | Axes | Budget | Purpose | Status |
|------------|------|--------|---------|--------|
| B1a | digital/ff/instant/null/grad/euclid | 0.5h | Cartpole baseline | ✅ Done |
| B1b | digital/ff/instant/null/grad/euclid | 0.5h | Pendulum baseline | ✅ Done |
| B1c | digital/recurrent/energy_min/null/grad/adam | 1h | Recurrent + energy_min on control | Pending |

---

## 🎯 PHASE 3: Graph Tasks (Track B2)

**Goal:** Full training for cora/citeseer/pubmed (node classification) + graph_classification.

**Status:** ✅ COMPLETED - GraphSystemTrainer implemented and tested

**Experiments:**
| Experiment | Axes | Budget | Purpose | Status |
|------------|------|--------|---------|--------|
| B2a | digital/graph/instant/random_projections/euclid | 0.5h | Cora baseline | ✅ Done |
| B2b | digital/conv/instant/homeostatic/euclid | 0.5h | Conv geometry on graph | Pending |
| B2c | digital/graph/instant/grad/euclid | 1h | Native graph geometry | Pending (needs compatible credit) |

---

## 🎯 PHASE 4: Sequence Tasks (Track B3)

**Tasks:** copy_task, sequential_mnist, tiny_shakespeare

**Metric:** perplexity (LM) or accuracy (classification)

**Experiments:**
| Experiment | Axes | Budget | Purpose | Status |
|------------|------|--------|---------|--------|
| B3a | digital/ff/instant/null/grad/euclid | 0.5h | Copy task | Pending |
| B3b | digital/recurrent/instant/grad/euclid | 0.5h | Sequential MNIST | Pending |
| B3c | digital/causal_transformer/instant/grad/euclid | 1h | Tiny Shakespeare (needs patch embedding) | Blocked on patch embedding |

---

## 🎯 PHASE 5: Tabular Baselines (Track B4)

**Tasks:** iris, wine, breast_cancer, digits (sklearn), covtype

**Experiments:**
| Experiment | Axes | Budget | Purpose | Status |
|------------|------|--------|---------|--------|
| B4a | digital/ff/instant/null/grad/euclid | 0.3h | Full tabular sweep | ✅ Done — 4 cells claim-eligible |

**B4a Results (L1, 3 seeds × 5 epochs, 9.5 s):**
| task | val_acc (seeds 42/43/44) | note |
|------|--------------------------|------|
| breast_cancer | 0.9737 / 0.9737 / 0.9649 | healthy |
| digits | 0.8444 / 0.8139 / 0.8306 | healthy |
| iris | 0.5333 / 0.0667 / 0.1667 | high seed variance — needs more epochs/seeds |
| wine | 0.0000 / 0.0000 / 0.0000 | **suspicious** — all seeds dead; investigate normalization |

---

## 🛠️ INFRASTRUCTURE IMPROVEMENTS (Parallel)

| Item | Description | Priority |
|------|-------------|----------|
| ✅ Compiled settle for energy_minimization | Move convergence check off hot path; batch horizon with `compiled=True` | High — enables GPU speedup |
| ~~RLSystemTrainer~~ | ~~Episode rollout + policy gradient~~ | ~~High — unblocks B1~~ ✓ |
| ~~GraphSystemTrainer~~ | ~~Masked node classification + graph readout~~ | ~~High — unblocks B2~~ ✓ |
| ✅ Experiment execution simplified | One sequential path; no process pool, no worker plumbing | High — runs are now bounded and observable |
| ✅ One Python entry point | `python -m computronium.experiment.survey_cli`; 541-line bash wrapper deleted | High — one flag surface, no shell drift |
| ✅ Per-epoch heartbeat | `log_every_n_epochs=1` in every trainer; long cells report progress and ETA | High — a 7-min cell no longer looks stuck |
| ✅ Run lifecycle closed | `finish_run` writes `completed` + budget, and `<store>.run.json` records the run | High — reports no longer show `running`/0 s |
| ✅ Bounded proposal scan | ModelBasedPolicy pages the space instead of walking a 50k page per call | High — pre-training work is bounded |
| ✅ Seed-plan expansion | One record per seed; `--n-seeds 3` satisfies the `n>=3` claim gate | High — claims become reachable |
| ✅ Task-aware replication key | Replication key carries `task_id`; four tasks no longer fuse into one n=12 group | High — claims count real cells |
| CausalTransformer patch embedding | ViT-style for vision; 1D token handling for sequence | Medium — unblocks B3 |
| Timing cache per (device, fidelity, task) | Already works; verify at scale | Low |
| ✅ Claim eligibility | Seed-plan expansion makes `n>=3` reachable; verified 1 eligible cell | Medium |

### ✅ Harness reliability (this session)

**Symptoms:** a 20-epoch MNIST cell printed one line and then went silent for 7–8
minutes; a killed run left its row at `status=running` with `budget_consumed_s=NULL`;
`--epochs 1` silently became the ladder's 20; an unpinned run spent minutes in
proposal before its first "Wave" line.

**Fixes:**

- **Per-epoch progress** (`core/system_trainer/_progress.py`, `log_every_n_epochs=1`):
  every trainer prints `epoch k/N: loss=… val_acc=… 17.0s/epoch, ~100s left`.
  Per-step chat stays opt-in via `log_every_n_steps`.
- **Honest wave sizing** (`wave.py`): a wave is priced from records at *its own*
  fidelity, not from the L0 positive control. The old arithmetic over-proposed an
  L2 wave by the fidelity ratio.
- **Bounded proposal scan** (`execution/policy.py`): `ModelBasedPolicy` walks a
  400-cell page per call (`scan_start` advances). Examining a 50k page before the
  first proposal was silent, minutes-long work.
- **Explicit depth survives** (`_build_spec`): `n_seeds`/`epochs` are `int | None`;
  `None` means ladder, an explicit `1` is now literal. The positive control is
  pinned to 1 epoch/1 seed regardless of `--epochs`, so it cannot fail by overrun.
- **Run lifecycle** (`wave._close_run`): `finish_run(run_id, "completed",
  budget_consumed_s=…)` plus `experiments/<store>.run.json`
  (`walltime_s`, `cells_planned/evaluated/passed/failed/skipped`, `budget_split`).
  The CLI's post-run check reads that manifest, not DuckDB + `bc`.
- **Planner count bug**: `PolicyPlanner.__iter__` compared `len(_seen)` to the wave
  size (already-seen cells from earlier waves made a wave under-yield). It now
  counts cells proposed in this wave.
- **Seed-plan expansion** (`wave._expand_replicates`): a schedule with `n_seeds=3` is
  three single-seed records, matching the store's identity model. The ladder's manual
  replicate loop is deleted; wave sizing prices a cell at `n_seeds × per-record cost`.
- **Task-aware replication key** (`evidence/store/_models.py`,
  `execution/dedup.py`): the key's sixth part was `budget_id` (a label identical for
  every cell), so four tasks' seeds fused into one n=12 "cell". It is now `task_id`.
  Verified: 4 tabular tasks × 3 seeds → **4 claim-eligible cells** (was 1).
- **Multi-task waves** (`wave.PolicyPlanner.__iter__`): the proposal context was
  scoped to `task_cycle[0]`, so a run declared with four tasks measured only the
  first. The context is now unscoped and each proposal keeps its own task.
- **Scan cursor** (`execution/policy.py`): the proposal page advanced by a fixed
  span even past a small space, so wave 2 onwards proposed nothing. It advances only
  while another page can exist.
- **One entry point**: `computronium/experiment/survey_cli.py` owns argparse, the
  banner, dry-run rendering, error hints and post-run checks for both engines.
  `experiment_shallow.sh` is deleted; its fractional-hours arithmetic and inverted
  `--skip-doctor` branch are gone with it. `learning_survey.py`/`simple_survey.py`
  keep only `run_*` (534→247 and 507→262 lines).

**Verified:** pepita/adam MNIST L2 PASS at 0.9746 in 396 s with 20 epoch lines;
xor L2 budget run stops at 179.1 s of a 180 s budget with 12 cells skipped and a
`completed` manifest; `--epochs 1` reaches the record as `epochs_requested=1`;
xor L1 `--n-seeds 3` writes seeds 42/43/44; tabular L1 measures all four declared
tasks (12 records) and reports **4 claim-eligible cells**.

### ✅ Execution-path fix (this session)

**Symptoms:** a run froze after `Evaluating up to N cells with M workers...`; 2h budgets burned by a single cell; almost no cells measured per run.

**Root causes, in order of impact:**

1. **Process-pool fan-out on one device.** `_evaluate_cells_parallel` spawned `max_workers`
   processes with `spawn` on a single GPU. Every child re-imported torch, built a CUDA
   context, and loaded the dataset (`_task(...).setup()`, MNIST via HF Hub → file-lock
   contention across 8 processes), while the parent held the only DuckDB writer. That
   combination has no failure signal: it stalls, silently.
2. **Positive control ran at the run's fidelity on `task_names[0]`.** With `--tasks mnist`
   at L2 that is one 20-epoch cell *before* any exploration, so a 0.05 h run was spent
   entirely inside the control.
3. **Tasks resolved after the spec was built** in both surveys → `spec.task_cycle=[]` →
   `PolicyPlanner` proposed nothing, `declared_cells` reported a fictional count.
4. **Budget enforced only between cells.** `n_wave` was sized as
   `budget × workers / cost`, so with 8 workers a 36 s budget planned cells that need
   300 s each; nothing interrupted them.
5. **Preview-then-run shared one `seen` set.** Both surveys proposed a wave for the
   dry-run preview, then either cleared `_seen` (learning) or re-planned into an empty
   space (static), so the preview either duplicated the control cell or blocked the run.

**Fixes:**

- `_evaluate_cells` — one sequential, in-process evaluator. Deleted `ProcessPoolExecutor`,
  `_init_worker`, the SIGTERM handlers, `max_workers`, `_resolve_max_workers`, and the
  worker factor in the cost model / timing-cache key. One store writer, one CUDA context,
  one dataset cache.
- Deadline injected into the cell (`params={"deadline_check": ...,
  "deadline_check_every_n_steps": 1}`). `SystemTrainer.train_epoch` now returns an
  incomplete epoch without appending history when the deadline hits, and `fit` stops —
  so a truncated cell reports `epochs_completed < epochs` → **FAIL**, not a false PASS.
- Positive control pinned to L0 with a 60 s cap; its cell is marked seen so the wave
  loop never re-proposes it.
- Task list resolved **before** `_build_spec` in both surveys.
- Wave sizing: `n_wave = budget_remaining / (measured per-seed cost × seed plan)`
  (serial, priced at the run's own fidelity).
- Previews only propose when `dry_run=True`; `_seen.clear()` deleted.
- Logging: one line per cell (`cell k/n:` start + `[k/n]` result, with seed and
  walltime). Per-epoch lines were added later; see Harness reliability above.

**Verified:** 2 cells on xor/iris in 1.7 s (learning), 2 cells static, ladder
L0→L1→L2 on cheap tasks in 6.7 s, and a 20-epoch mnist cell stops at its deadline
(47 s wall for a 43 s budget) with a truthful FAIL.

---

## 🔄 EXPERIMENT LOOP

```bash
# 1. RUN (short budgets; cells are serial, so budget ≈ sum of cell walltime)
uv run python -m computronium.experiment.survey_cli 0.25 \
  --policy tpe --device cuda \
  --tasks <task_list> \
  --axes '<axis_json>'

#   Long cells are observable: one line per epoch, plus one line per cell.
#   Pin depth with --epochs N / --n-seeds N; omit them to follow the ladder.
#   --mode static runs SimpleSurvey instead of LearningSurvey.

# 2. ANALYZE (30s)
uv run comp report --store experiments/<latest>.duckdb --format text
uv run comp coverage report --store experiments/<latest>.duckdb
cat experiments/<latest>.run.json      # budget spent, cells planned/measured

# 3. FIX (≤15 min) — infrastructure only, not preventive
# 4. VERIFY (0.02h, no ladder)
# 5. COMMIT + LOG
```

---

## 📋 PRIORITY ORDER

1. ~~**Execution path** — one sequential evaluator, in-cell deadline, honest gates~~ ✓
2. ~~**Harness** — one Python CLI, epoch heartbeat, closed runs, bounded proposals~~ ✓
3. ~~**C1** — GPU scale on best combo~~ ✓
4. ~~**B1a** — RLSystemTrainer + Cartpole~~ ✓
5. ~~**B2a** — GraphSystemTrainer + Cora~~ ✓
6. ~~**C3** — PEPITA scale~~ ✓ (0.9746 @ L2)
7. ~~**C4** — Non-digital substrate at scale~~ ⚠️ (4/20 epochs; 208 s/epoch is the finding)
8. ~~**B4a** — Tabular sweep~~ ✓ (4 claim-eligible cells; wine/iris flagged)
9. **B1c, B2b-B2c** — RL/Graph variety (needs task-compatible axes)
10. **B3** — Sequence coverage (B3c blocked on patch embedding)

## ⚠️ OPEN ITEMS

- **C2 evidence is thin.** `energy_minimization` + feedforward composes only for the five
  MNIST-family vision tasks; a single L2 cell needs ~285 s. `--epochs N` now pins depth
  literally, so price a settling cell at `--epochs 2` before committing an L2 budget.
- **Claim eligibility is now reachable.** A schedule's seed plan is expanded into one
  single-seed record per seed in `_evaluate_cells`, and the replication key includes
  `task_id`, so `--n-seeds 3` writes three records *per cell* and `comp report` counts
  them. Verified: tabular L1 4 tasks × 3 seeds → **4 claim-eligible cells**.
- **Cross-task claims mix raw `val_acc`.** Axis claims aggregate the payload's primary
  metric across tasks with different baselines (B4a reports `val_acc=0.514 ±0.123` over
  iris/wine/breast/digits). The normalized metric is stored; claims should prefer it.
- **`wine` returns 0.0 on every seed** (B4a). The run PASSes because the gate checks
  finite metrics, not task-learnability. Investigate feature normalization / class
  mapping before treating the tabular sweep as a baseline.
- **`iris` seed variance is large** (0.07–0.53 at 5 epochs). Treat as under-powered
  rather than a result; rerun with more epochs or more seeds before quoting it.
- **Serial budget arithmetic.** Because cells run one at a time, the time budget must
  cover the sum of cell walltime. Long-task sweeps need either a bigger budget, fewer
  epochs, or L1.
- **Per-step logs stay opt-in.** Per-epoch progress is always on
  (`log_every_n_epochs=1`); per-step chat needs `log_every_n_steps > 0`. No CLI flag
  exposes it yet — add one only if a caller asks.
- **Killed runs are not closed.** A SIGKILL/SIGTERM leaves the row `running` and writes
  no manifest. That is truthful (the run did not finish), but resume still needs
  `--resume`/`--promote-from`; closing on SIGTERM is deferred until an interrupted run
  is actually needed.

---

## 🚫 NO (Same as TODO85)

- Paper figures
- Publishing artifacts
- Hypothesis backlogs
- Preventive fixes
- Meetings/retrospectives
- Cycles > 30 min