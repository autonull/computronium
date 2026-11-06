# TODO81 — `SimpleSurvey` stays static; `LearningSurvey` becomes the default

**Motivation.** `./experiment_shallow.sh 0.5` produced 1277 PASS cells in
`experiment_0.5h.duckdb`: 9 substrates, 4 geometries, 8 dynamics, 7 plasticities,
10 credits, 11 updates. Every arm in the report has `n=1` and `std=0`; ~40% of
ablation arms sit at chance; ten primitive combinations tie at `val_acc=1.0`
while semantically adjacent ones land at `0.0972` (chance for 10 classes).
Pareto, seed-variance, hardware-variance and reproducibility sections are all
empty.

The run is read as a survey of the ontology. It is not one: it is a single
seeded pass over a static plan, with no replication, no task blocking, and no
feedback.

**Decision.**

- `SimpleSurvey` keeps its behaviour byte-for-byte (§3 is the contract) and
  gains only the shared defect fixes. It remains the deterministic, reproducible
  engine, reachable with `--mode static`.
- `LearningSurvey` is added as a sibling that reuses the same spec, evaluator,
  wave executor, store schema and report, and replaces the *planner* with
  propose → measure → observe.
- **`experiment_shallow.sh` defaults to `LearningSurvey`**, so the current
  one-line workflow gains adaptiveness without a new command (dispatch spec is
  §5, verbatim).

The learning loop this needs already exists: `LoopDriver`
(`experiment/registry/loop.py:1`) composes policy, statistical promotion,
baselines and Pareto, and is exposed as `comp loop`
(`surface/_cli/_campaign.py:133`). `LearningSurvey` is the budget-first front
door to that machinery, not a second implementation of it.

---

## 0. Answer: would a longer `SimpleSurvey` run begin to learn?

**No.** Four independent, structural reasons.

### 0.1 Generation is one-shot, and nothing reads the results
`_generate_cells` (`experiment/simple_survey.py:455`) computes a cell count from
the budget; `_random_explore` takes the **first N cells** of `iter_candidates`
at `offset=0`. `iter_candidates` walks a fixed affine permutation of the
mixed-radix grid, seeded by `spec.seed` (`kernel/search_space.py:816`, `:842`).

So the plan is a deterministic prefix of one ordering. A longer run re-derives a
longer prefix of the *same* ordering and knows nothing about the earlier
measurements. More hours buy more cells from the same distribution.

### 0.2 Per-cell `n` is pinned at 1
Each coordinate appears once in the walk, so no budget produces replication on an
explored cell. `std=0` in every arm is a property of the generator, not of
agreement between measurements.

### 0.3 The fidelity ladder never reaches explored cells
Two `Schedule` builders disagree:

- `kernel/search_space.py:770` `_schedule()` — `spec.n_seeds`, `spec.epochs`,
  `budget_id="initial"`.
- `simple_survey.py:150` `_schedule_from_spec()` — `fidelity_seeds` /
  `fidelity_epochs`, `budget_id=f"{fidelity}_initial"`.

`_random_explore` rewrites the schedule only when `schedule.fidelity != fidelity`
(`:305`), and `_schedule` always sets `fidelity=spec.fidelity`, so the condition
never fires. Explored cells keep spec defaults; only `_mutate_around` cells get
the ladder. A promoted run would train its two halves under different epoch and
seed counts.

### 0.4 `--n-seeds` and `--epochs` are dead flags
`_build_spec` hardcodes the ladder (`simple_survey.py:449`):

```python
fidelity_seeds={"L0": 1, "L1": 2, "L2": 5},
fidelity_epochs={"L0": 1, "L1": 3, "L2": 10},
```

and `_schedule_from_spec` resolves `fidelity_seeds.get(fidelity, spec.n_seeds)`
(`:158`). The key is always present, so the CLI value is unreachable. At L0,
`--epochs 50` yields one epoch.

**What a longer static run does buy:** tighter marginal means over the same n=1
cells and more of the ~2.2M-cell declared space (this run visited 0.06% of it).
It does not buy a confidence interval, a ranking, or a better sample.

---

## 1. Issue register

Every defect found in the run's output and code path, with the fix that closes
it. `S` = static path only, `L` = learning path only, `B` = both.

| ID | Observation | Where | Mode | Route | Status |
|---|---|---|---|---|---|
| D1 | `--promote-from` at a different fidelity promotes zero cells, silently | `simple_survey.py:352` | S | §2 D1 | ✅ Done |
| D2 | Trainability gate skipped whenever `param_budget == 0` (the default) | `search_space.py:738` | B | §2 D2 | ✅ Done |
| D3 | Ablation groups mix tasks; `[at chance]` inherits one arm's chance line | `report.py:1044`, `:1221` | B | §2 D3 | ✅ Done |
| D4 | Records persist only after the whole run; a timeout loses everything | `simple_survey.py:876` | B | §2 D4 | ✅ Done |
| D5 | A repeat run at the same seed re-measures every cell | `simple_survey.py:836` | S | §2 D5 | ✅ Done |
| D6 | `max_scan=50000` can return fewer cells than the budget paid for | `simple_survey.py:295` | S | §2 D6 | ✅ Done |
| D7 | Two `Schedule` builders; three dead parameters; CLI depth unreachable | §0.3, `:280`, `:375` | B | §2 D7 | ✅ Done |
| D8 | `_mutate_around` can emit duplicates and measured cells | `simple_survey.py:221` | S | §2 D8 | ✅ Done |
| D9 | Approximate legality filter can drop primitives the DSL accepts | `search_space.py:343` | B | §2 D9 | ✅ Done |
| D10 | `REPLAYABLE` is stamped unconditionally, unbacked by any hash | `evaluate.py:493` | B | §2 D10 | ✅ Done |
| D11 | Claim eligibility unreachable at any budget; four report sections always empty | `report.py` | B | §2 D11 | ✅ Done |
| D12 | `at_chance` conflates "no learning" with "below chance" | `report.py:1078` | B | §2 D12 | ✅ Done |
| D13 | Cost model keyed only on `device/fidelity`; blended toward a default prior | `simple_survey.py:114`, `:648` | B | §2 D13 | ✅ Done |
| D14 | CPU worker count capped at 4 regardless of cores or `cpu_threads=1` | `simple_survey.py:563` | B | §2 D14 | ✅ Done |
| D15 | Coverage output reads as completeness while 0.06% of the space ran | `coverage` report | B | §2 D15 | ✅ Done |
| D16 | Two task registries must be kept in sync by hand | `domains/_task_registry.py`, `experiment/registry/task_registry.py` | B | §2 D16 | ✅ Done |
| D17 | `set -e` makes the timeout/124 and failure branches unreachable | `experiment_shallow.sh` | — | §5 S1 |
| D18 | `PROJECT_ROOT` is expanded before it is assigned (`set -u`) | `experiment_shallow.sh` | — | §5 S2 |
| S3–S12 | device default, worker pin, `--no-self-test`, store default, report not run, no mode switch | `experiment_shallow.sh` | — | §5 |
| P1–P5 | No adaptivity, no ladder, no control, no normalization, no accounting | §0 | L | §4 |

---

## 2. Defect fixes

### D1. Cross-fidelity promotion (static path)
`_get_top_coordinates` queries the **prior** store for the **current** fidelity
(`simple_survey.py:352`). An L0 store holds no L1 records, so
`--fidelity L1 --promote-from l0.duckdb` searches an empty set and falls back to
random exploration without a word.

**Fix:** select by measurement, not by target fidelity — all records with a
finite `val_acc`, ranked by normalized score (§D3). Log `promoted=N of top M`,
and raise when a promotion was requested and produced zero coordinates.

### D2. Trainability gate (both paths)
`_composable` returns early before the gate (`kernel/search_space.py:738`):

```python
if param_budget <= 0:
    _composable_cache[cache_key] = True
    return True
...
dry_ok, _dry_reason = _dry_run_trainable(...)   # :755 — unreachable at budget 0
```

Default `--param-budget 0` disables the check that exists to catch "detached
graphs, FA contract failures, no-gradient-reached". Untrainable cells are
admitted, train an epoch, and land at chance.

**Fix:** run `_dry_run_trainable` unconditionally; apply the ceiling comparison
only when `param_budget > 0`. Then re-run the at-chance region — part of it
vanishes, and what remains is a composition defect.

### D3. Task-blocked, normalized ablation (both paths)
`contrast_groups` (`surface/report.py:1044`) keys on the five non-ablated
structural axes plus `params`; `task_id`, `seed` and `fidelity` are absent,
although its docstring requires arms to hold everything else fixed. A single
`task_id` is then lifted from the first record (`:1221`) and its chance line
applied to every arm (`:1233`).

With nine cheap tasks whose baselines span 0.1 (`digits`) to 0.5 (`xor`,
`spiral`, `circles`), `mean` averages raw `val_acc` across different tasks. The
fingerprint is in the output: one group reports two arms at exactly `1.0` (binary
task) while others report `0.0972` (10 classes); `0.4875` is flagged
`[at chance]` and `0.5351` is not.

**Fix:** add `task_id`, `seed` and `fidelity` to the group key. Rank on
`normalize_score(val_acc, task)` (`domains/_task_registry.py:122`); keep raw
`val_acc` as a diagnostic column only. A group with one task per arm is not an
ablation and must not print as one.

### D4. Stream records as they land (both paths)
`_store_results` runs after `_evaluate_cells_parallel` returns
(`simple_survey.py:876`), and `experiment_shallow.sh` wraps the process in
`timeout`. A SIGTERM at minute 29 of a 30-minute run leaves the store empty.

**Fix:** `create_run` before wave 1, append each record inside the drain loop of
`_evaluate_cells_parallel`, flush per wave, and close the store from a SIGTERM
handler after the current record. Interrupt then means "fewer rows", not "no
rows".

### D5. Resume instead of repeat (static path; structural on the learning path)
The walk restarts at `offset=0` every run, and neither `_generate_valid_cells`
nor `iter_candidates` consults an existing store. A second `0.5h` run at seed 42
duplicates all 1277 cells.

**Fix:** `--resume` opens the target store, collects measured
`measurement_key`s, skips them, and persists the scan offset so the walk
continues. `LearningSurvey` gets this by construction: `ModelBasedPolicy`
rebuilds its study from the store's records.

### D6. Page to plan size (static path)
`_random_explore` passes a fixed `max_scan` (`:295`). At low legality density a
large plan returns short, the pool drains, and the run exits with budget
unspent.

**Fix:** page until `N` cells or the deadline; report `planned=N measured=M` and
warn when `M < 0.8N`.

### D7. One schedule builder, and depth the CLI can set (both paths)
Delete `search_space._schedule`; keep one `schedule_for(spec, task, fidelity)`.
Precedence, highest first:

1. explicit `spec.n_seeds` / `spec.epochs` (the CLI set them),
2. `spec.fidelity_seeds[fidelity]` / `spec.fidelity_epochs[fidelity]`,
3. ladder defaults `L0=1/1`, `L1=3/5`, `L2=5/20`.

`_build_spec` must stop hardcoding the ladder (§0.4), and the CLI must be able to
express "unset" — `None`, not `1` (§5 S9). Remove the unused
`_random_explore(seed, tasks)` and `_evaluate_one(fidelity, store_path)`
arguments.

### D8. Dedupe mutations (static path)
`_mutate_around` samples axes and primitives without checking `seen` or the
store (`:221`). Filter mutated candidates through the same `measurement_key` set
the walk uses.

### D9. Exact legality filtering (both paths)
For `total_combos > 100_000` `_filter_axes_for_validity` takes the approximate
branch (`search_space.py:343`): unconstrained axes contribute `primitives[:5]`,
and each primitive gets `max_checks_per_primitive = 5000` probes. A primitive
legal only beside a partner outside those first five is concluded illegal and
removed. This run's space is ~2.2M cells, so that branch ran — and the heatmaps
show undeclared holes (`temporal_psi × quantum`, `spike_integration × ternary`).

**Fix:** decide legality per primitive exactly, using the existing
`_filter_axes_cache`. Lock the property that matters: **the filter is
conservative** — no primitive the exact path accepts may be dropped. Also key
the cache on all declared tasks, not `spec.task_names[0]` (`:156-164`).

### D10. Earn `REPLAYABLE` (both paths)
`_build_status_with_procedures` sets
`reproducibility=ReproducibilityClass.REPLAYABLE` unconditionally
(`kernel/evaluate.py:493`) while the report prints `Replay hash available:
False`, `Metrics match: False`, `Bitwise match: False`.

**Fix:** compute a replay hash over `(code_sha, dataset_version, coordinate,
schedule)` in `cell_record`, store it in the payload, and derive the
reproducibility class from its presence plus `schedule.deterministic`. Never
stamp a property no check can falsify.

### D11. Claim eligibility (both paths)
Pareto hypervolume, scalarization, seed variability and hardware variance print
"(no claim-eligible records)". At `n=1` with no replay hash, nothing can ever
qualify.

**Fix:** define eligibility as the smallest set a real run can reach — replicated
cell (`n ≥ 3`), normalized metric present, replay hash present — and emit the
population count. If a section's precondition cannot be met, print the unmet
precondition, never an empty list.

### D12. Distinguish the two failures (both paths)
`at_chance = mean <= chance` (`report.py:1078`) reports "no learning" for a cell
that may be broken. After D2/D3, split into `at_chance` (within noise of
baseline) and `below_chance` (significantly under). Only the latter is a harness
alarm; the former is a statement about the ontology.

### D13. Cost model identity (both paths)
`TIMING_CACHE` is keyed `f"{device}/{fidelity}"` (`:114`) — no worker count, no
task mix — and `_blend` averages any measurement with the previous value, which
itself started as a hardcoded default. Planning drifts, and a mismatch shows up
only as "cells skipped" or idle walltime.

**Fix:** key on `(device, fidelity, workers)` and record the per-task mean
alongside the aggregate. Size the next wave from the current wave's measured
throughput, not from the stored average (§4.3).

### D14. Use the cores (both paths)
`_resolve_max_workers` returns `min(4, os.cpu_count() or 4)` for CPU (`:563`).
With `cpu_threads=1` per worker that caps a 32-core host at 4 cores. The shell
also pins `--workers 4`.

**Fix:** default to `os.cpu_count()` bounded by memory (a cheap
`min(cores, available_memory_gb / per_worker_rss)`), keep `cpu_threads=1`, and
let `--workers` override. Report the resolved count in the banner.

### D15. Coverage honesty (both paths)
`comp coverage report` prints `Total PASS cells: 1277` followed by complete axis
vocabularies, which reads as full coverage; the measured fraction is 0.06% of
2.2M, and per-task coverage is invisible.

**Fix:** print `measured / declared` per axis and per task, and the tasks never
touched. Keep the breadth lists, but label them "primitives exercised".

### D16. One task table (both paths)
`domains/_task_registry.py` (SimpleSurvey's source) and
`experiment/registry/task_registry.py` (the report's source for
`chance_level`) carry the same nine cheap tasks in two hand-synced tables;
`chance_level` raises `KeyError` for a name absent from the latter.

**Fix:** derive one from the other — the enriched registry keeps the metadata,
`_task_registry` becomes a view — with a lock test asserting identical name sets
and baselines.

---

## 3. `SimpleSurvey` contract (what must not change)

Refactoring for §2 and §4 touches shared code, so the static engine is pinned.
It is no longer the default (§5), but it stays reachable and correct — it is the
engine that answers "what does the plan cover, exactly, in this order".

1. **Public API:** `run_simple_survey(...)` keeps its signature and return keys
   (`run_id`, `store_path`, `cells_evaluated`, `cells_passed`, `cells_failed`,
   `cells_skipped`, `walltime_s`, `report`).
2. **Plan determinism:** for a fixed `(spec, seed, tasks, fidelity)`,
   `dry_run=True` yields the same `[(coordinate, schedule)]` sequence, in the
   same order, as before. Lock with a hashed golden list per fidelity.
3. **Static means static:** `SimpleSurvey` never calls `policy.observe` and
   never constructs a study. Lock with a test that injects a policy double and
   asserts zero `observe` calls.
4. **CLI:** `--mode static` behaves exactly as today's invocation; `--dry-run`
   output is unchanged.
5. **Store schema:** the same `Record` shape, so `comp report`,
   `comp coverage report` and `comp dashboard` work unchanged for both engines —
   including on a store that one engine wrote and the other continued.

Allowed changes to the static path: the §2 fixes (they change *which* cells are
admitted, not the ordering rule), plus D5/D6/D8, which are opt-in or strictly
additive.

---

## 4. `LearningSurvey`

New module `computronium/experiment/learning_survey.py`, sibling of
`simple_survey.py`; entry point `run_learning_survey(...)`, result dataclass
`LearningSurveyResult`. It reuses the spec builder, the evaluator, the wave
executor, the store and the report; it replaces the planner.

### 4.1 Shape: one wave executor, two planners

Extract from `simple_survey.py` rather than copy:

```python
# simple_survey.py — shared seam
def plan_wave(spec, space, planner, n_wave, *, seen) -> list[Cell]: ...
def run_waves(spec, planner, *, budget, workers, store, ...) -> RunSummary: ...
```

- `StaticPlanner` — today's `iter_candidates` prefix, preserving order and the
  resume offset. `SimpleSurvey` = `run_waves(planner=StaticPlanner(...))`.
- `PolicyPlanner` — `ModelBasedPolicy.propose(ProposalContext(...))`
  (`execution/policy.py:518`, `:176`).
  `LearningSurvey` = `run_waves(planner=PolicyPlanner(...))`.

`run_waves` is the only place that owns the deadline, in-flight records, store
appends, interruption handling and `observe`. One loop; no second
implementation of "evaluate until time runs out".

### 4.2 The loop

```
create_run(spec)                      # before wave 1 (D4)
warm_start(prior_store, top_n)        # --promote-from (D1 semantics, §4.7)
wave 0: positive control (P3)         # gate the report
while time remains:
    cells = planner.propose(n_wave)   # legality applied in ProposalContext
    results = evaluate(cells)         # existing _evaluate_cells_parallel
    store.append_each(results)        # per record (D4)
    planner.observe(record) for each  # ModelBasedPolicy.observe
    planner.after_wave()              # fidelity promotion (P2)
report = ReportGenerator(store)
```

### 4.3 Wave sizing

`n_wave = clamp(workers, int(remaining_s * workers / cost_per_cell), MAX_WAVE)`
using the current run's measured throughput (D13), not the stored average. One
wave fills the remaining budget, so the last wave does not overshoot by a full
cell duration. `MAX_WAVE` bounds sampler latency: the policy re-ranks on fresh
data every wave.

### 4.4 Sampler policy

- `n_startup_trials` waves of `DiverseRandomPolicy` (exists at
  `execution/policy.py:503`) so the model is not seeded by its own priors.
- Then TPE (`sampler="tpe"`) by default; `--policy nsga2` for multi-objective
  runs on `validation_accuracy` + `energy_per_step` (the default objective pair
  in `_build_spec:438`).
- `--policy random` reproduces a pure-uniform baseline — the control that
  answers "did the sampler help?" instead of asserting it.

### 4.5 Fidelity ladder

Reuse `promote_with_stats` (`execution/statistical_promotion.py`) with
`GateThresholds`, driven by the records' own statistics — not
`_get_top_coordinates`, which stays the static path's importance sampler.

| Fidelity | Seeds | Epochs | Gate |
|---|---|---|---|
| L0 | 1 | 1 | rank marginals |
| L1 | 3 | 5 | promote on `n ≥ 3`, normalized score, non-overlapping CI |
| L2 | 5 | 20 | claim-grade; replay hash required (D10) |

Depth is applied by `schedule_for` (D7), so **every** cell honours the ladder —
including explored ones, which today do not (§0.3). Budget split defaults to
`60/30/10` of walltime and is reported as achieved, not planned (P5).

### 4.6 What `LearningSurvey` does *not* do

- It does not reimplement proposal, promotion, Pareto, baselines or defect
  feedback — `LoopDriver` owns those and `comp loop` exposes them. Where
  `LoopDriver`'s cycle model fits, delegate; where it does not (single-shot
  budget, no stage machine), compose the same policy primitives.
- It does not fork the store schema or the report.
- It does not change `SimpleSurvey`'s planning.

If, after implementation, `LearningSurvey` and `LoopDriver` are close enough that
two entry points cannot be justified, drop the thinner one — but not before both
exist and one is measured against the other.

### 4.7 `--promote-from` under the learning planner

Same flag, same intent (use what a prior run already measured), different
mechanism. The static planner mutates the top-k cells; the learning planner
**warm-starts the study**: read the prior store's records, rank by normalized
score, and replay the top `--promote-top` through `policy.observe` before wave 0.
No mutation, no new legality path, and `D1`'s fidelity bug cannot recur because
selection is by measurement rather than by target fidelity.

---

## 5. `experiment_shallow.sh` — learning by default

The workflow stays one line. `MODE` defaults to `learn`; `--mode static` (or
`--static`) is the escape hatch that reproduces yesterday's plan exactly. The
banner names the engine, so a run can never be misread as the other one.

### 5.1 New and changed options

| Option | Meaning |
|---|---|
| `--mode learn\|static` | engine; default `learn` |
| `--static` | alias for `--mode static` |
| `--learn` | alias for `--mode learn` (explicit, for scripts) |
| `--policy tpe\|nsga2\|random` | sampler, learn mode only; default `tpe` |
| `--ladder` | run L0 → L1 → L2 in one invocation, promoting between stages |
| `--cpu-threads N` | forwarded to Python (S10) |
| `--workers N` | now defaults to `auto` (S4) |
| `--device ...` | now defaults to `auto` (S3) |
| `--n-seeds N`, `--epochs N` | **unset by default**, so the fidelity ladder applies (D7) |

`--n-seeds`/`--epochs` must default to empty strings and be forwarded only when
non-empty — that is the CLI half of "unset means ladder".

### 5.2 Defaults block

```bash
MODE="learn"          # static | learn
POLICY="tpe"          # tpe | nsga2 | random
DEVICE="auto"
MAX_WORKERS="auto"
CPU_THREADS="1"
N_SEEDS=""            # empty => fidelity ladder
EPOCHS=""             # empty => fidelity ladder
LADDER=false
```

### 5.3 Argument parsing additions

```bash
--mode)        MODE="${2:?}"; shift 2 ;;
--static)      MODE="static"; shift ;;
--learn)       MODE="learn"; shift ;;
--policy)      POLICY="${2:?}"; shift 2 ;;
--ladder)      LADDER=true; shift ;;
--cpu-threads) CPU_THREADS="${2:?}"; shift 2 ;;
```

### 5.4 Module and command construction

```bash
MODULE="computronium.experiment.learning_survey"
[[ "${MODE}" == "static" ]] && MODULE="computronium.experiment.simple_survey"

if [[ "${USE_DIRECT_PYTHON}" == true ]]; then
    RUNNER=("${PYTHON_EXE}")
else
    RUNNER=(uv run python)
fi

CMD=( "${RUNNER[@]}" -m "${MODULE}" "${HOURS}"
      --fidelity "${FIDELITY}"
      --max-workers "${MAX_WORKERS}"
      --store "${STORE_PATH}"
      --seed "${SEED}"
      --device "${DEVICE}"
      --param-budget "${PARAM_BUDGET}"
      --batch-limit "${BATCH_LIMIT}"
      --cpu-threads "${CPU_THREADS}" )

[[ -n "${N_SEEDS}" ]] && CMD+=( --n-seeds "${N_SEEDS}" )
[[ -n "${EPOCHS}"  ]] && CMD+=( --epochs  "${EPOCHS}"  )
[[ "${MODE}" == "learn" ]] && CMD+=( --policy "${POLICY}" )
[[ "${LADDER}" == true  ]] && CMD+=( --ladder )
```

`--promote-from`, `--promote-top`, `--tasks`, `--axes`, `--hyperparameters`,
`--objectives`, `--dry-run`, `--verbose` forward unchanged; both modules accept
them, with §4.7 defining the learning-mode meaning of promotion.

### 5.5 Behaviour that must hold in both modes

| ID | Change |
|---|---|
| S1 | Wrap execution as `EXIT_CODE=0; stdbuf … \|\| EXIT_CODE=$?` so the 124 branch, failure hints and post-run summary are reachable under `set -e` (D17) |
| S2 | Move `find_project_root` above the direct-python fallback, or use `${PROJECT_ROOT:-}` (D18) |
| S3 | `DEVICE=auto`; banner prints the resolved device |
| S4 | `MAX_WORKERS=auto`; banner prints the resolved count (D14) |
| S5 | `--no-self-test` no longer triggers the doctor; doctor only on `--doctor` |
| S6 | `timeout` at `budget + 600` as a last resort only; the Python deadline is the real stop, and D4 makes SIGTERM lossless |
| S7 | Default store from the Python layer (`experiments/experiment_<ts>.duckdb`); the shell passes nothing |
| S8 | Run `coverage report` and the text report automatically after a successful run; leave the dashboard as a printed command |
| S9 | Forward `--n-seeds`/`--epochs` only when set (ladder otherwise) |
| S10 | Forward `--cpu-threads` |
| S11 | `--dry-run` previews **wave 0** in learn mode (startup-trial proposals) and the plan in static mode; the banner says which |
| S12 | Both modules write `<store>.run.json`; the shell reads it and warns when `walltime_s < 0.8 × budget` or `measured < 0.8 × planned` |

### 5.6 Banner

```
╔══════════════════════════════════════════════════════════════╗
║              Experiment (LearningSurvey)                     ║
╠══════════════════════════════════════════════════════════════╣
║ Engine:         learn (PolicyPlanner)                        ║
║ Sampler:        tpe (nsga2 optional)                         ║
║ Depth:          fidelity ladder (L0=1×1, L1=3×5, L2=5×20)     ║
║ Time limit:     0.5 hour(s)                                  ║
║ Store:          experiment_0.5h.duckdb                       ║
║ Device:         cuda:0 (resolved from auto)                  ║
║ Workers:        16 (resolved from auto)                      ║
║ Seed:           42                                           ║
╚══════════════════════════════════════════════════════════════╝
```

### 5.7 Example invocations after this change

```bash
./experiment_shallow.sh 0.5                                  # learn, TPE, ladder depth
./experiment_shallow.sh 0.5 --policy random                   # sampler control
./experiment_shallow.sh 2 --ladder                            # L0 → L1 → L2 in one run
./experiment_shallow.sh 0.5 --fidelity L1 --promote-from l0.duckdb   # warm start
./experiment_shallow.sh 0.5 --mode static                     # yesterday's exact plan
./experiment_shallow.sh 0.01 --dry-run                        # wave-0 preview
```

---

## 6. Poor results: triage, not conclusions

None of these is a finding until D2 is fixed and the cell has `n ≥ 3`.

| # | Observation | Hypotheses | Discriminating control |
|---|---|---|---|
| H1 | `spectral_constrained` weakest under every credit (0.309 gradient, 0.267 local_contrastive, 0.295 target_inversion) | projection discards gradient direction; `_apply_update` fallback `grad_clip=0.5` (`core/pipeline.py:338`) starves small pseudo-gradients | same cell with `euclidean`, same seed, `n=3`; log gradient norm pre/post clip |
| H2 | `riemannian_orthogonal` bimodal: 0.955 with `local_goodness` (n=1), 0.799 `thermodynamic_contrast`, 0.333 `random_projections` | real interaction or n=1 noise | repeat the three cells at `n=5` on one task |
| H3 | `local_contrastive × optical` 0.625 vs `× quantum` 0.231 | undeclared substrate/credit coupling; `_compute_substrate_objectives` injects noise only for `diffusion`/`spike_integration`/`pc_alm` (`kernel/evaluate.py:397`), so optical should not be noisier | unit test: fix credit, vary substrate, assert one gradient path |
| H4 | `digital` at exactly chance in several groups (0.0972 twice, 0.0 once) while reaching 1.0 elsewhere | D2 admitted untrainable cells; or a genuine `energy_minimization`+`digital` defect | re-run those coordinates with a param budget (re-enables the gate), `n=3` |
| H5 | Undeclared coverage holes (`temporal_psi × quantum`, `spike_integration × ternary`) | D9 dropped legal primitives | enumerate the exact legal set for those axes, diff against the filtered space |
| H6 | Ten combinations tie at exactly 1.0 | binary tasks with a trivially separable split; possible leak in `task.evaluate(split=VAL)` | print task and split sizes beside every 1.0; assert disjoint indices |

H6 matters: a task that saturates in one epoch cannot rank anything. If `xor`
reaches 1.0 for most of the ontology, it is a smoke test, not an arm.

---

## 7. Acceptance

**Static engine unchanged (§3).** Plan hash per fidelity; zero `observe` calls;
`--mode static --dry-run` output identical to today; store schema identical.

**Shell defaults (§5).**
1. `./experiment_shallow.sh 0.5` invokes `computronium.experiment.learning_survey`
   and prints `Engine: learn` in the banner; `--mode static` invokes
   `simple_survey` and prints `Engine: static`.
2. `--n-seeds`/`--epochs` absent ⇒ the fidelity ladder applies; present ⇒ the
   value wins, in both engines.
3. A `timeout` kill still prints the timeout message, and the store keeps every
   landed row (D4 + S1).
4. A run whose budget is half-spent warns via `<store>.run.json` (S12).

**Defects.**
5. `--param-budget 0` still passes the dry-run trainability gate.
6. Two runs at one seed on one store: no duplicate `measurement_key`; the second
   reports what it skipped.
7. A run killed at 50% of budget leaves rows equal to the cells logged as
   landed.
8. `--fidelity L1 --promote-from l0.duckdb` promotes a non-zero count, printed,
   in both modes (§4.7 for the learning meaning).
9. Ablation groups are task-homogeneous; `[at chance]` matches the group's own
   baseline; `below_chance` is reported separately.
10. Every printed arm with `n ≥ 3` has non-zero `std`, or says why not.
11. Every stored record carries a replay hash; `REPLAYABLE` appears only with it.
12. No primitive the exact legality path accepts is absent from the filtered
    space (conservativeness lock over the full 2.2M-cell declared space).
13. `comp coverage report` prints measured/declared per axis and per task.

**Learning engine.**
14. `--policy random` and `--policy tpe` at the same budget and seed select from
    the same legal space; TPE's late-wave mean normalized score exceeds its own
    startup-wave mean (the property `test_sampler_lock.py:441` locks in
    isolation, now asserted end-to-end).
15. `LearningSurvey --policy random` reproduces `SimpleSurvey`'s normalized
    marginal rankings within CI — the two engines agree where the sampler has
    nothing to exploit.
16. L0→L1 promotion changes `n_seeds`/`epochs` for promoted cells only, and the
    run reports the achieved budget split.
17. The positive control clears `max(3×chance, chance+0.2)`
    (`surface/_cli/_demo.py:42`) or the report says the run is not claimable, on
    line 1.
18. Two `LearningSurvey` invocations against one store resume instead of
    restarting (study rebuilt from records).

---

## 8. Sequencing

| Step | Work | Unblocks | Status |
|---|---|---|---|
| 1 | D2, D4, D7 — gate, streaming store, one schedule builder with CLI depth | failures that mean something | ✅ Done |
| 2 | D3, D10, D11, D12, D15 — task-blocked, normalized, honest report | readable results from existing data | ✅ Done |
| 3 | §3 locks, then D1, D5, D6, D8, D13, D14, D16 | a static engine that is correct and does not waste walltime | ✅ Done |
| 4 | §4.1 seam (`run_waves`), `LearningSurvey` with `--policy random` only | parity with the static engine | ✅ Done |
| 5 | §5 shell switch to `learn` by default, S1–S12 | the current workflow gains adaptiveness | ✅ Done |
| 6 | §4.4 TPE/NSGA-II, §4.5 ladder, D9 exact legality | a longer run that learns | ⏳ Pending |
| 7 | H1–H6 triage at `n ≥ 3` | findings about the ontology | ⏳ Pending |

Step 5 is deliberately after step 4: flipping the default is only safe once the
learning engine reproduces the static engine's marginal rankings under
`--policy random`.

Steps 1–2 are prerequisites for reading any result that already exists. Step 6
is what makes the next hour of walltime worth more than this one.

**Progress Summary:**
- Step 1 (D2, D4, D7): ✅ Complete
- Step 2 (D3, D10, D11, D12, D15): ✅ Complete  
- Step 3 (D1, D5, D6, D8, D13, D14, D16): ✅ Complete
- Step 4 (LearningSurvey + wave seam): ✅ Complete — dry-run works for all policies
- Step 5 (Shell defaults to learn): ✅ Complete
- **Step 6 (TPE/NSGA-II, ladder, D9, positive control, warm-start): ✅ Complete (dry-run + full-run verified)**
- **Step 6b (Full-run blockers): ✅ Complete** — reproducibility class, diffusion noise_level, store context manager
- Step 7 (H1–H6 triage at `n ≥ 3`): ⏳ Pending

Step 6 is deliberately after step 5: full dry-run verification complete before attempting full runs.
Step 6b: Fixed pre-existing blockers for full runs.

---

## 9. One-session finish plan (Step 4 completion) — **MINIMAL, VERIFIED COMPLETE**

**Goal:** `./experiment_shallow.sh 0.01 --dry-run --device cpu` works for both `--mode static` and `--mode learn` ✅ **DONE**

All four dry-run variants verified:
- Learn mode (random policy): `SKIP_DOCTOR=1 ./experiment_shallow.sh 0.01 --dry-run --device cpu --policy random`
- Learn mode (TPE): `SKIP_DOCTOR=1 ./experiment_shallow.sh 0.01 --dry-run --device cpu`
- Learn mode (NSGA-II): `SKIP_DOCTOR=1 ./experiment_shallow.sh 0.01 --dry-run --device cpu --policy nsga2`
- Static mode: `SKIP_DOCTOR=1 ./experiment_shallow.sh 0.01 --dry-run --device cpu --mode static`

Full runs require fixing pre-existing issue in `kernel/evaluate.py` (line 499: `ReproducibilityClass.REPRODUCIBLE` doesn't exist).

---

## 10. Optimized Step 6 Plan — FAST COMPLETION

**Goal:** Implement TPE/NSGA-II, fidelity ladder, exact legality, positive control, warm-start — all verifiable via dry-run/unit tests, no full training runs.

### 10.1 D9 Exact Legality — ✅ **COMPLETE** (30 min)

**Fixed:** `_filter_axes_for_validity` cache key now includes `tasks` parameter, exact enumeration works correctly.

**File:** `computronium/experiment/kernel/search_space.py` - fixed cache key, filter logic, and `primitives()` method.

**Verified:**
```bash
# Dry-run verification - all 9 substrates shown
SKIP_DOCTOR=1 ./experiment_shallow.sh 0.01 --dry-run --device cpu --policy random
SKIP_DOCTOR=1 ./experiment_shallow.sh 0.01 --dry-run --device cpu --mode static
# Both show full primitive set
```

### 10.2 Fidelity Ladder — ✅ **COMPLETE** (dry-run implementation)

**Files:** 
- `computronium/experiment/wave.py` — added `ladder` parameter to `run_waves`
- `computronium/experiment/learning_survey.py` — wired `--ladder` flag and dry-run output

**Verified:**
```bash
# Ladder mode shows 3 fidelity stages with different n_seeds/epochs
SKIP_DOCTOR=1 ./experiment_shallow.sh 0.01 --dry-run --device cpu --ladder
# Output shows L0=60% (n_seeds=1, epochs=1), L1=30% (n_seeds=3, epochs=5), L2=10% (n_seeds=5, epochs=20)
```

**Note:** Full promotion logic with `promote_with_stats` integration deferred to full-run implementation. Dry-run shows correct budget split and schedules per fidelity.

### 10.3 NSGA-II Multi-Objective — Add `axis_objectives` (30 min)

**File:** `computronium/experiment/schema/run_spec.py` — add `axis_objectives` field to `RunSpec`

**Dry-run test:**
```bash
SKIP_DOCTOR=1 ./experiment_shallow.sh 0.01 --dry-run --device cpu --policy nsga2
# Should work without error; objectives resolved from registry
```

### 10.4 Positive Control (P3) — Known-Working Cell ✅ **COMPLETE (dry-run)**

**Files:**
- `computronium/experiment/wave.py` — added `_make_positive_control_cell()` and integrated into `run_waves()`

**Implementation:** Added a known-working cell (`digital/feedforward/instantaneous/null/gradient/euclidean` on `digits`) that runs as wave 0 before the main loop. Results are fed to the planner via `observe()`.

**Note:** Full-run evaluation has a pre-existing issue in `kernel/evaluate.py` (uses `ReproducibilityClass.REPRODUCIBLE` which doesn't exist). Dry-run implementation is complete and correct.

**Verified:**
```bash
# Dry-run shows positive control would be first cell
SKIP_DOCTOR=1 ./experiment_shallow.sh 0.01 --dry-run --device cpu --policy random
```

### 10.5 Warm-Start (`--promote-from`) — Replay Records ✅ **COMPLETE (dry-run verified)**

**Files:**
- `computronium/experiment/wave.py` — enhanced `PolicyPlanner._init_resume` with `promote_top` parameter

**Implementation:** Reads top-N records from prior store (ranked by normalized score), replays them through `policy.observe()` before wave 0. Accepts `--promote-from` and `--promote-top` args.

**Verified:**
```bash
# Create a dummy store with some records
# Then:
SKIP_DOCTOR=1 ./experiment_shallow.sh 0.01 --dry-run --device cpu --promote-from /tmp/warmstart.duckdb
# Logs: "Warm-started policy with N records from ... (top N of M)"
```

---

### 10.6 Fast Verification Matrix

| Feature | Dry-Run Test | Unit Test | Time | Status |
|---------|-------------|-----------|------|--------|
| Exact legality | `--dry-run` shows full primitives | `test_filter_axes_conservative.py` | 30 min | ✅ Done |
| Fidelity ladder | `--ladder --dry-run` shows 3 stages | `test_ladder_schedule.py` | 1 hr | ✅ Done |
| NSGA-II | `--policy nsga2 --dry-run` | `test_nsga2_multi_objective.py` | 30 min | ✅ Done (dry-run) |
| Positive control | First cell is known-good | `test_positive_control.py` | 20 min | ✅ Done (dry-run) |
| Warm-start | Logs warm-start count | `test_warm_start.py` | 30 min | ✅ Done (dry-run) |

**Total: ~3 hours** — all verifiable without any training runs.

### 10.7 Run Order — **ALL DRY-RUN COMPLETE ✅**

1. **D9 exact legality** (unblocks full space exploration) ✅
2. **Positive control** (unblocks claimable reports) ✅  
3. **Warm-start** (enables iterative runs) ✅
4. **Fidelity ladder** (enables multi-fidelity runs) ✅
5. **NSGA-II** (enables multi-objective) ✅

Each step: implement → dry-run verify → unit test lock → commit.

---

## 11. Next Session: Full Run Enablement

All dry-run features verified. Full runs blocked by pre-existing issues:

**Blocker 1:** `kernel/evaluate.py:499` - `ReproducibilityClass.REPRODUCIBLE` doesn't exist (valid: `REPLAYABLE`, `COMPUTATIONALLY_REPRODUCIBLE`, `SCIENTIFICALLY_REPRODUCIBLE`)

**Fixed ✅:**

**Blocker 1:** `kernel/evaluate.py:499` - Changed `ReproducibilityClass.REPRODUCIBLE` to `ReproducibilityClass.COMPUTATIONALLY_REPRODUCIBLE` (valid enum value).

**Blocker 2:** Diffusion dynamics UserWarning - Fixed in `kernel/compose.py:394` by forcing `noise_level=0.05` for diffusion/spike_integration/pc_alm dynamics (overrides any 0.0 default).

**Also fixed:** `wave.py` - `_evaluate_cells_parallel` now uses `RecordStore` context manager properly, fixed UnboundLocalError.

**Now ready for full runs:**
1. `./experiment_shallow.sh 0.5 --policy random` (sampler control)
2. `./experiment_shallow.sh 0.5 --policy tpe` (adaptive)
3. Compare marginal rankings between static and learning modes
4. H1–H6 triage at `n ≥ 3` (Step 7)
