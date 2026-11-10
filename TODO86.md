# TODO86 — Scale & Coverage (Post-TODO85)

**Status:** System fixed and experimentally sound. Now: validate at scale, cover remaining task types.

**Baseline (Run 48):** 72 cells, 72 PASS, L0→L1→L2 working, best L2 0.9775 on mnist.

---

## 🎯 PHASE 1: GPU Scale Validation (Track C)

**Goal:** Prove GPU speedup at scale (hidden=256, batch=256, epochs=50) on best combos.

| Experiment | Axes | Budget | Purpose | Status |
|------------|------|--------|---------|--------|
| C1 | digital/ff/instant/null/grad/euclid (best L2) | 2h | GPU vs CPU baseline at scale | ✅ Done |
| C2 | digital/ff/energy_min/null/grad/adam (2nd best L2) | 2h | GPU with settling at scale | ⚠️ Partial (see open items) |
| C3 | digital/ff/instant/null/pepita/adam (best non-grad credit) | 1h | Credit variety at scale | Pending |
| C4 | memristive/ff/energy_min/null/grad/adam | 1h | Non-digital substrate at scale | Pending |

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
| Experiment | Axes | Budget | Purpose |
|------------|------|--------|---------|
| B3a | digital/ff/instant/null/grad/euclid | 0.5h | Copy task |
| B3b | digital/recurrent/instant/grad/euclid | 0.5h | Sequential MNIST |
| B3c | digital/causal_transformer/instant/grad/euclid | 1h | Tiny Shakespeare (needs patch embedding) |

---

## 🎯 PHASE 5: Tabular Baselines (Track B4)

**Tasks:** iris, wine, breast_cancer, digits (sklearn), covtype

**Experiments:**
| Experiment | Axes | Budget | Purpose |
|------------|------|--------|---------|
| B4a | digital/ff/instant/null/grad/euclid | 0.3h | Full tabular sweep |

---

## 🛠️ INFRASTRUCTURE IMPROVEMENTS (Parallel)

| Item | Description | Priority |
|------|-------------|----------|
| ✅ Compiled settle for energy_minimization | Move convergence check off hot path; batch horizon with `compiled=True` | High — enables GPU speedup |
| ~~RLSystemTrainer~~ | ~~Episode rollout + policy gradient~~ | ~~High — unblocks B1~~ ✓ |
| ~~GraphSystemTrainer~~ | ~~Masked node classification + graph readout~~ | ~~High — unblocks B2~~ ✓ |
| ✅ Experiment execution simplified | One sequential path; no process pool, no worker plumbing | High — runs are now bounded and observable |
| CausalTransformer patch embedding | ViT-style for vision; 1D token handling for sequence | Medium — unblocks B3 |
| Timing cache per (device, fidelity, task) | Already works; verify at scale | Low |
| Claim eligibility | n>=3, replay_hash, normalized_metric, PASS — currently 0; investigate | Medium |

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
- Wave sizing: `n_wave = budget_remaining / measured_cost` (serial).
- Previews only propose when `dry_run=True`; `_seen.clear()` deleted.
- Logging: one line per cell (`cell k/n:` start + `[k/n]` result). `log_every_n_steps`
  defaults to `0`, and the per-epoch trainer logs are gated on it.

**Verified:** 2 cells on xor/iris in 1.7 s (learning), 2 cells static, ladder
L0→L1→L2 on cheap tasks in 6.7 s, and a 20-epoch mnist cell stops at its deadline
(47 s wall for a 43 s budget) with a truthful FAIL.

---

## 🔄 EXPERIMENT LOOP (Same as TODO85)

```bash
# 1. RUN (short budgets; cells are serial, so budget ≈ sum of cell walltime)
./experiment_shallow.sh 0.25 --policy tpe --device cuda \
  --tasks <task_list> \
  --axes '<axis_json>' \
  --skip-doctor

# 2. ANALYZE (30s)
uv run comp report --store experiments/<latest>.duckdb --format text
uv run comp coverage report --store experiments/<latest>.duckdb

# 3. FIX (≤15 min) — infrastructure only, not preventive
# 4. VERIFY (0.02h, no ladder)
# 5. COMMIT + LOG
```

---

## 📋 PRIORITY ORDER

1. ~~**Execution path** — one sequential evaluator, in-cell deadline, honest gates~~ ✓
2. ~~**C1** — GPU scale on best combo~~ ✓
3. ~~**B1a** — RLSystemTrainer + Cartpole~~ ✓
4. ~~**B2a** — GraphSystemTrainer + Cora~~ ✓
5. **C3-C4** — Remaining GPU scale combos (0.25h each, serial)
6. **B1b-B1c, B2b-B2c** — RL/Graph variety
7. **B3, B4** — Sequence + Tabular coverage

## ⚠️ OPEN ITEMS

- **C2 evidence is thin.** `energy_minimization` + feedforward composes only for the five
  MNIST-family vision tasks; a single L2 cell needs ~285 s, so a short budget measures
  nothing beyond the positive control. Either raise the per-run budget for settling
  combos or lower `--epochs`, but decide before quoting a C2 number.
- **Claim eligibility is still 0.** `n>=3` requires three *records of the same cell*, and
  the survey evaluates each cell once per run. This is a real gap in the loop, not a bug
  in the gate; the next run needs `--n-seeds 3` at L0 or repeated runs into one store.
- **Serial budget arithmetic.** Because cells run one at a time, the time budget must
  cover the sum of cell walltime. Long-task sweeps need either a bigger budget or L1.
- **`log_every_n_steps=0`** is now the default; pass a positive `log_every_n_steps` in
  `SystemTrainerConfig.extra`-style callers to re-enable per-step/epoch chat. (No CLI
  flag exists yet — add one only if a caller needs it.)

---

## 🚫 NO (Same as TODO85)

- Paper figures
- Publishing artifacts
- Hypothesis backlogs
- Preventive fixes
- Meetings/retrospectives
- Cycles > 30 min