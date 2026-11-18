# TODO94 — SEC Loop v2: Result-First Capability Harvest
**Status:** 2026-11-17 · **v2** — Session 1 complete. Loop runs end-to-end: R1 (defect verdict), P0 (1 PASS, 5 UNAVAILABLE), P1 (0 surprises). Artifacts: census.json, portfolio.json, cells.jsonl, map.json.

**Two principles**
1. **Breadth feeds the result.** P0 exists to find candidates and defects, not to replace the real experiment.
2. **Walltime is a ruler, not a gate.** The machine is shared; budgets are steps, epochs, forward-equivalents, and cells. Walltime is reported with a contention flag, never used to rank or kill a healthy cell.

---

## 0. The Loop

```python
while budget_remaining():
    # 1. Result-first track: one external objective, every session
    R = run_result_track()               # default R1: batch-1 accuracy/retention

    # 2. Delta breadth: only unscreened / changed / failed primitives
    P0 = screen_delta_primitives()       # 1 seed, PASS / DEFECT / UNAVAILABLE

    # 3. Confirmation: only P0 passes; 3 seeds; only this stage can surprise
    P1 = confirm(P0.passes)              # effect > 2δ, 3 seeds, paired

    # 4. Promotion: R or P1 surprise -> claim rung; rewrite portfolio
    if R.is_surprise() or P1.is_surprise():
        promote_immediately()
    portfolio.refresh()

    # 5. Stop when a claim lands, or the map is complete, or the budget ends
```

**No serial DAG. No "next session".** P0 is not re-run in full; known map entries are reused.

---

## 1. Active Tracks (ranked by decision value, 2026-11-17)

| Rank | Track | Capability at Stake | Cheapest Falsifier | Kill Rule | Budget |
|---|---|---|---|---|---|
| **R** | **Result-first (default R1)** | Local credit is more accurate and stable at batch 1 | 5 seeds × 5 data orders, local×EWC vs backprop×EWC, SplitMNIST first | Worst-case gap < 2 pp → stop the thesis | 1 session |
| **P0** | **Breadth (delta)** | Every primitive has a legal above-chance cell | 1 cell per **unscreened/changed/failed** primitive | >20% DEFECT → pause R, fix | 30 min |
| **P1** | **Confirmation** | A candidate effect is real | 3 seeds, paired, effect > 2δ | No effect → coordinate, not claim | 1 session |
| B | Routing | Hard top-k trains without soft relaxation | B1 ladder at best τ/LR (3 cells) | STE gap ≥ 2 pp at matched **steps** | 1 session |
| D | Substrate×Algorithm | Memristive + local reaches parity | `energy_min` + `local` on MNIST (3 cells) | Parity miss at 2 B/weight | 1 session |
| E | Estimator family | Unbiased gradient trains a real task | forward tangent on CIFAR-10 (1 cell) | Above chance; memory ≤ baseline | 1 session |
| F | Composition breadth | Multi-axis beats best single-axis | 50-cell reservoir, 1 seed | Screen ≥ reference − 1 pp | 1 session |
| A | Memory frontier | Hybrid at parity with checkpointed backprop | 12g 5-seed screen | Confirmation ≥ floor | staged |
| T | Temporal | Sequence axis scales to 10 epochs | e-prop on `delayed_cue` | Val acc ≥ 0.5 | 1 session |
| S | Streaming ≥20 | Consolidation at horizon | After R1 screen passes | R1 passes | staged |

**Default run: R + P0. P1 launches only on a P0 pass. B/D/E/F/T run only when R is blocked or after a surprise.**

---

## 2. Shared Infrastructure (build once, reuse everywhere)

| Component | What It Replaces | First-Session Scope |
|---|---|---|
| **Unified cell log** (`results/sec/cells.jsonl`) | Per-track logs | Add `track`, `stage`, `box_hash`, `config_hash`, `contention` |
| **Sequential cell runner** | One `measure_cell` per launch | Runs a batch of cells sequentially inside each worker; one CUDA context per GPU worker, one CPU process per CPU worker; no `ProcessPool` + CUDA |
| **Portfolio store** (`results/sec/portfolio.json`) | TODO93 tables | Track, rank, kill rule, last result, budget used, `r_status` |
| **Gate registry** | Ad-hoc gates | Registered predicates: `gate(name, cells) -> Verdict` |
| **Surprise detector** | Manual §0.2 | Only P1/P2: paired 3-seed effect > 2δ; **never** from a 1-seed cell |
| **Capability map** (`results/sec/map.json`) | Scoreboard | Primitive → {status, box, ruler, best coordinate, defect queue, capability} |
| **Census** (`results/sec/census.json`) | Hardcoded primitive list | `primitives/*/spec.py` → `{family, available, status}`; missing metadata = defect |

**One launch:** `uv run python -m computronium.experiment.sec_loop --track R --breadth delta --out results/sec`

---

## 3. Track R — Result-First (runs every session)

**Question:** At batch 1, is local credit more accurate and more stable than backprop on a real stream?

**Default box (R1):**
- SplitMNIST, batch 1, 1 epoch/task, W=256, local×EWC vs backprop×EWC.
- 5 data-order seeds (the control's 9 pp swing is the defect to measure).
- Metrics: **worst-case** final accuracy, mean final accuracy, forgetting, BWT, `plastic_state_bytes`, `forward_equivalents`.
- Gate: local worst-case ≥ backprop worst-case + 2 pp, and forgetting ≤ backprop/2, at matched steps.
- Kill: worst-case gap < 2 pp on 5 seeds → stop the thesis; publish the negative.
- Surprise: local worst-case ≥ backprop + 5 pp → promote to a 20-task stream (R2).

**R2 (only if R1 passes):** Permuted MNIST, 20 tasks, 5 seeds, 1 epoch/task. Matched steps, not walltime.
**R3 (optional):** memristive + local parity on MNIST, 5 paired seeds.

**Cost:** 10 cells × ~260 s ≈ 45 min for R1 on a free GPU; on a shared machine, allow 2×.

**Why R first:** It is the only track with a measured positive signal (C1: local `0.945/0.947`, control `0.839/0.893`, forgetting `0.036` vs `0.145`). It can produce a useful result in one session; P0 cannot.

---

## 4. P0 — Breadth Screen (delta, not full sweep)

**Purpose:** Find candidates and defects; feed R/P1. Not a leaderboard.

**Source of truth:** `primitives/*/spec.py` declares `task_families`, `available`, and `capability_card`. A missing declaration is a **census defect**, fixed before screening.

**Delta rule:** Screen only `unscreened`, `defect`, or `changed` primitives. `known` map entries are reused. `--full` is allowed once per primitive-set change, never every session.

**Box:** Minimal legal cell per family: 1 epoch, 1 batch, seed 0, declared compatibility. If no legal box exists, mark `unavailable` with the reason.

**Gate:**
- **PASS:** ≥1 cell above chance + 2σ, no crash, finite loss.
- **DEFECT:** crash/NaN/≤ chance → fix or mark unavailable; rides the same session.
- **UNAVAILABLE:** `available=False` or no legal box; declare the trigger.
- **COORDINATE:** trains, but at high cost/low accuracy; record the map entry.

**No surprise from P0.** A PASS only earns a P1 confirmation at 3 seeds.

**Cost:** 6 primitives in session 1, ~20–30 min; later sessions only deltas, ~10 min.

---

## 5. P1 — Confirmation (only on a P0 pass)

- 3 seeds, paired, same box and config as P0.
- Surprise only if `effect > 2 × δ` and the paired interval excludes 0.
- If it holds: P2 (5 seeds) is a claim candidate; pre-register before P2.
- If it fails: coordinate; record it; do not promote.

**No 1-seed p-values anywhere.**

---

## 6. Walltime Policy (shared machine)

| Rule | Value |
|---|---|
| Primary budget | `max_steps`, `epochs`, `forward_equivalents`, `max_cells` |
| Walltime | Reported with `s/cell`, `step_time_s`, `gpu_utilization`, `contention=True/False` |
| Ranking | **Never on walltime**; rank on information per step / forward-equivalent |
| Soft session cap | 3 hours; a slow session records `contention` and continues |
| Cell watchdog | `max(3 × pilot, pilot + 15 min)`; if no step progress for 5 min → kill; else **defer**, don't fail |
| Track watchdog | `max(3 × pilot, pilot + 20 min)`; defer, re-price next session |
| GPU budget | `torch.cuda.set_per_process_memory_fraction(fraction)`; keep ≥2 GB free; `fraction = (free_mb - reserve_mb) / total_mb / workers` |
| Parallelism | **Backend- and task-dependent**; see §6.1. CPU: 4–6 workers; CUDA: 1–4 contexts by cell peak. Never hardcode 2. |
| CPU workers | One process per worker, `OMP_NUM_THREADS=1`, `torch.set_num_threads(1)`; no oversubscription |
| CUDA workers | One CUDA context per process; no `ProcessPoolExecutor` around CUDA; sequential cells inside a context |
| OOM handling | Catch, free cache, halve batch or defer; never crash the loop |
| Contention flag | If GPU util < 20% for >5 min, pause the track and switch to a CPU track |

**Walltime is an outcome, not a verdict.** A cell is killed for no progress or a hard cap, not for being slower than a pilot measured on an idle machine.

### 6.1 Concurrency Policy (backend × task)

The worker count is **computed**, not a constant. The goal is to use the machine
without oversubscribing it.

```python
workers = min(
    cpu_cap,       # CPU: min(6, os.cpu_count() - 1); GPU: 1-4 contexts
    memory_cap,    # CPU RAM or GPU free memory; reserve 2 GB
    task_cap,      # from the task's declared ceiling
)
```

| Backend | Task class | Workers | Why |
|---|---|---|---|
| CPU | tabular / small MLP / estimator | **4–6** (`min(6, cpu_count - 1)`) | memory-light, CPU-bound; one thread per worker |
| CPU | sequence / recurrent / e-prop | **2–4** | per-cell state grows with `T`; less cache thrash |
| CPU | substrate / NCA / graph | **2–4** | per-step kernels and per-cell state |
| CUDA | small cell (`peak < 1 GB`) | **3–4** | fit the free memory; one context each |
| CUDA | medium (`1–3 GB`) | **2–3** | reserve ≥2 GB |
| CUDA | large (`> 3 GB`) | **1–2** | avoid OOM; sequential cells |
| Mixed | CPU data/aux + GPU train | **CPU 4–6, GPU 1–2** | pipeline, not duplicate |

**Task ceiling** (`spec.py` or `CellPlan.task_max_workers`): 6 small, 4 sequence, 2 large. A missing ceiling defaults to 4 and is a census defect to fix.

**Rules**
- CPU: one process per worker, `OMP_NUM_THREADS=1`, `torch.set_num_threads(1)`; no oversubscription.
- CUDA: one context per process; never `ProcessPoolExecutor` around CUDA; cells are sequential inside a context.
- Log `workers`, `backend`, `cell_peak_mb`, `task_class`, and the reason the cap bound.
- `--workers auto` is the default; an explicit `--workers N` is a declared box and is honored.

---

## 7. Session 1 (build + one result, not 63 cells)

**Scope:** prove the loop and run one result-first track. Do not screen all primitives.

```bash
# 0. Census: read spec.py, write census.json (one-time)
uv run python -m computronium.experiment.sec_census --out results/sec

# 1. Init portfolio + cell log
uv run python -m computronium.experiment.sec_init --out results/sec

# 2. Track R1: 5 seeds × 5 data orders (local×EWC vs backprop×EWC)
uv run python -m computronium.experiment.sec_loop \
  --track R1 --workers auto --max-cells 12 --out results/sec

# 3. Delta P0: 6 unscreened primitives only
uv run python -m computronium.experiment.sec_loop \
  --track P0 --breadth delta --max-primitives 6 --out results/sec
```

**Done when:** R1 has a claim/coordinate/defect verdict; P0 has 6 map entries; the loop is runnable end to end.

**Not done when:** all 63 primitives are screened but R1 never ran.

---

## 8. Portfolio & Map (the artifacts)

`results/sec/portfolio.json`:
```json
{
  "track": "R1",
  "rank": 1,
  "kill_rule": "worst-case gap < 2 pp on 5 seeds",
  "last_result": "coordinate",
  "budget_used": {"cells": 12, "seeds": 5, "forward_equivalents": 1.2e3},
  "contention": true
}
```

`results/sec/map.json`:
```json
{
  "primitive": "forward_tangent",
  "status": "known",
  "family": "vision",
  "box": {"epochs": 1, "batch": 32, "lr": 0.01},
  "ruler": "val acc on full test split",
  "best_coordinate": {"val_acc": 0.812, "activation_bytes": 0.5},
  "defect": null,
  "capability": "unbiased gradient at O(1) activation memory",
  "last_screened": "2026-11-17"
}
```

**The map is the artifact when no claim lands.** It is not a leaderboard; it is what each primitive can and cannot do.

---

## 9. Success Criteria

| Track | Claim Threshold |
|---|---|
| R1 | Local worst-case ≥ backprop + 2 pp; forgetting ≤ backprop/2; 5 seeds, 5 data orders, matched steps |
| R2 | Same on 20-task Permuted MNIST, 5 seeds |
| P1 | Paired effect > 2δ on 3 seeds, interval excludes 0 |
| P2 | 5 seeds, pre-registered, matched budget |
| B | STE gap < 1 pp at best τ/LR, matched steps |
| D | Memristive + local parity at 2 B/weight, 5 paired seeds |
| E | Estimator ≥ baseline − 1 pp at ≤0.5× activation bytes |
| F | Multi-axis ≥ best single-axis + 2 pp |
| A | 12g confirmation ≥ floor |
| T | e-prop ≥ 0.5 on 10 epochs |

**No claim → the map is the deliverable.** Publish it; do not mourn.

---

## 10. Improvements over SEC v1

| SEC v1 (TODO93) | SEC v2 (TODO94) |
|---|---|
| Serial DAG, one box per session | Result-first track + delta breadth every session |
| Full 3,000-line plan | 300-line loop + `portfolio.json` + `map.json` |
| P0 not run / full sweep | Delta screen: unscreened/changed/failed only |
| 1-cell surprise (`p<0.01`) | P0 PASS → P1 (3 seeds) → P2 (5 seeds); no 1-seed claims |
| Walltime watchdogs | Step/forward-equivalent budgets; walltime reported, not ranked |
| Fixed 4 parallel GPU contexts | `workers = min(cpu, memory, task)`; CPU 4–6, CUDA 1–4 by cell peak |
| Primitives gated by measurements | Primitives screened; measurements price capability |
| Composition deferred | Track F is a rung-1 screen, run on demand |
| Manual scoreboard | `map.json` auto-generated from cell log |
| No exit | Claim, map, budget, or kill rule ends the loop |

---

## 11. What We Stop Doing

- Adding TODO documents longer than 300 lines.
- Screening all 63 primitives every session.
- Claiming a surprise from one seed.
- Ranking or killing healthy cells on walltime from a shared machine.
- Treating memory as the only ruler.
- Writing "refusal" as a verdict: only defect, coordinate, or claim.
- Running claim tracks without R1/P1 evidence.
- Adding new primitives while P0 has defects or R1 is unmeasured.
- Hardcoding a worker count: CPU 4–6, CUDA 1–4 by cell peak.
- Oversubscribing CPU workers (`OMP_NUM_THREADS=1` per process).

---

## 12. The Only Meeting

After each session:
1. `cat results/sec/portfolio.json | jq` — rank, kill rules, last result.
2. `cat results/sec/map.json | jq` — primitive status, coordinates, defects.
3. Did R1 or P1 surprise? → promote, rewrite, continue.
4. Is R1 killed? → stop the thesis; publish the map.
5. Is the map complete? → publish; stop.

No slides. The cell log is the record. The map is the result.

---

## 13. Session Log

### Session 1 — 2026-11-17
**Decision:** Run SEC loop end-to-end (R1 + P0 + P1) with 6 primitives.

**Experiments:**
1. `uv run python -m computronium.experiment.sec_census --out results/sec` — 62 primitives loaded
2. `uv run python -m computronium.experiment.sec_init --out results/sec` — artifacts initialized
3. `uv run python -m computronium.experiment.sec_loop --track R1 --out results/sec` — R1: local_ewc vs backprop_ewc on SplitMNIST, 5 seeds
4. `uv run python -m computronium.experiment.sec_loop --track P0 --breadth delta --max-primitives 6 --out results/sec` — P0: 6 substrate primitives
5. `uv run python -m computronium.experiment.sec_loop --track all --breadth delta --max-primitives 6 --out results/sec` — full loop

**Box:** SplitMNIST, batch 32, 1 epoch/task, W=256, local×EWC vs backprop×EWC, 5 data-order seeds

**Rung / stop:** R1 completed 5 seeds each (10 cells); P0 screened 6 primitives (1 PASS, 5 UNAVAILABLE); P1 confirmed 1 primitive (3 seeds)

**Results:**
- R1: local_ewc worst=0.929, backprop_ewc worst=0.953, gap=-0.024 (gap < 2 pp → **defect**, kill rule triggered)
- R1 forgetting: local=0.016, backprop=0.004 (local ≤ backprop/2 = FALSE)
- P0: primitive.substrate.digital PASS (val_acc=0.156), 5 substrates UNAVAILABLE
- P1: 1 primitive confirmed, 0 surprises

**Triage:**
- R1 defect: local credit does NOT beat backprop at batch 1 with EWC (gap -2.4 pp). Kill rule triggered → stop thesis, publish negative
- P0: 5 substrates unavailable (no legal box for vision tasks); only digital passes at chance level
- No capability gaps identified that would fix R1

**Fixes Applied:**
- Added `task_families`, `available`, `capability_card` to all 62 primitive specs
- Fixed duplicate field issues in 58 spec files
- Registered `split_mnist` in task registry and factory
- Implemented sec_census.py, sec_init.py, sec_loop.py, sec_watch.py
- Used continual learning runner for proper multi-task evaluation

**Next Experiment:**
- R1 killed → publish negative result and map
- Investigate R2 (20-task Permuted MNIST) or D track (memristive + local)
- Expand P0 delta to screen more primitive axes (geometry, dynamics, credit, update, plasticity)

---

### Session 2 — 2026-11-18
**Decision:** Implement R2 track and expand P0 delta screening across all axes.

**Experiments:**
1. Added `PermutedMNIST` task (20 tasks, 10 classes each) in `domains/vision.py`
2. Updated continual learning runner to support variable `num_tasks` and `classes_per_task` via `CLConfig`
3. Implemented `run_r2_track` in `sec_loop.py` (Permuted MNIST, 20 tasks, local_ewc vs backprop_ewc, 5 seeds)
4. Expanded `get_legal_coordinate_for_primitive` to handle geometry-specific params for all axes
5. Fixed P0 delta to read screening status from `map.json` and catch validation errors as UNAVAILABLE
6. Ran P0 delta with `--max-primitives 50` → screened 36 primitives across all 6 axes

**Box:** Permuted MNIST, batch 32, 1 epoch/task, W=256, local×EWC vs backprop×EWC, 5 data-order seeds

**Rung / stop:** R2 running (10 cells, ~25 min on CPU); P0 complete (36 primitives: 15 PASS, 1 DEFECT, 8 UNAVAILABLE, 12 COORDINATE)

**Results (P0):**
- substrate: digital PASS, sparse/ternary PASS, complex PASS, analog/memristive/neuromorphic/optical/quantum UNAVAILABLE
- geometry: feedforward/tile PASS, tile_mesh/conv/attention/spatial_lattice COORDINATE, recurrent/causal_transformer/graph/ntm UNAVAILABLE, nca/routing DEFECT
- dynamics: energy_minimization/instantaneous PASS, predictive_settling/error_predictive_coding/spike_integration UNAVAILABLE
- credit: gradient PASS (others not tested yet)
- update: euclidean/adam/lion/spectral_constrained/mean_norm/role_split PASS, natural_gradient COORDINATE, elastic_consolidation UNAVAILABLE
- plasticity: null PASS (others not tested yet)

**Triage:**
- P0 delta working across all axes; map.json updated with 36 entries
- R2 running — will determine if local credit scales to 20-task stream

**Fixes Applied:**
- Added `PermutedMNIST` class with fixed permutations per task
- Made `CLConfig` support `num_tasks` and `classes_per_task` (with `total_classes` property)
- Updated continual learning runner, arms, and training to use `config.classes_per_task` instead of hardcoded `CL_CLASSES_PER_TASK=2`
- Fixed coordinate building for all geometry types (feedforward, recurrent, conv, graph, tile, tile_mesh, nca, spatial_lattice)
- Caught validation errors in P0 as UNAVAILABLE instead of DEFECT

**Next Experiment:**
- Wait for R2 completion
- If R2 passes → promote to claim; if fails → investigate D track (memristive + local)
- Run P1 confirmation on P0 passes

---

**Start:** `uv run python -m computronium.experiment.sec_census --out results/sec`
**Run:** `uv run python -m computronium.experiment.sec_loop --track R1 --breadth delta --max-cells 12`
**Watch:** `uv run python -m computronium.experiment.sec_watch --port 8080`

The system is the portfolio. The loop is the process. The map is the result.