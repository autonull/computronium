# TODO76 — 24-Hour Broad Experiment: Entry Points, Control, and Vocabulary

**Status:** Draft — planning only. No implementation yet.
**Created:** 2026-11-01
**Goal:** A fresh install can start, watch, pause, throttle, and finish a broad ~24-hour experiment from the dashboard, without narrowing the experiment space and without hidden hardcoded limits.

---

## 1. Objective

Deliver one end-to-end path:

```bash
uv sync --dev --all-extras
uv run comp dashboard --store experiment.duckdb
# browser: choose "survey-24h" -> Start
# watch progress, pause/step/stop, move the concurrency ceiling
```

The run must be broad (all six axes, many tasks or at least many cells), shallow per cell (L0/L1, 1–2 epochs, small batch limit), and strictly bounded by a 24-hour wall budget including post-run settlement.

**Non-goals**

- No repo-wide rename of `RunSpec`, `Record`, `Coordinate`, `Schedule`, `Cell`, or `Store`.
- No new stage/view taxonomy.
- No control-capable TUI; the console dashboard stays read-only.
- No backward-compatibility shims. The repo policy is no backwards compatibility.

**Scope boundary**

This plan addresses the **orchestration layer** (dashboard, queue, loop, CLI flags) and the **profile/settlement defaults** that affect a 24 h run. It does not touch the kernel evaluation, the stage pipeline, or the ontology primitives — those are stable and orthogonal.

---

## 2. Vocabulary (proposed)

Keep the domain nouns. Fix the orchestration nouns.

| Term | Meaning | Decision |
|---|---|---|
| **Experiment** | The research program / a store of evidence | Keep as the domain word, not an API noun |
| **Run** | One declared `RunSpec` execution | Keep |
| **Campaign** | An ordered set of runs with dependencies (`CampaignSpec`) | Keep |
| **Loop** | A continuous driver that issues cycles of runs (`LoopDriver`) | Keep |
| **Cycle** | One loop iteration | Keep |
| **Job** | A queued unit of work: `run`, `campaign`, or `loop` | **Introduce at the orchestration boundary** |
| **Profile** | A named run template (`RunProfile`) | Keep |
| **Spec** | A fully declared run/campaign/loop | Keep |
| **Cell** | A coordinate + schedule candidate | Keep |
| **Record** | One measured seed of a cell | Keep |
| **Store** | The DuckDB evidence store | Keep |
| **Control plane** | The per-job control/status document | Keep, but bind it to a job id |

**Rule:** `CampaignQueue`, `CampaignQueueEntry`, and `CampaignStatus` describe **jobs**, not campaigns. Rename them at the orchestration layer to `JobQueue`, `JobEntry`, `JobStatus`, with `JobKind = RUN | CAMPAIGN | LOOP`. `CampaignSpec`/`CampaignRunner` remain the multi-run domain.

**Why this split:** The dashboard currently conflates "queue entry" (a job awaiting execution) with "measured run" (evidence in the store). They have different lifecycles, different APIs, and different concerns. The `Job` abstraction cleanly separates orchestration from evidence.

---

## 3. Current-state findings

### 3.1 Entry points

| Command | Shape | Dashboard-compatible today |
|---|---|---|
| `comp demo` | Seven beats, ~30 s | Yes (uses `comp run demo`) |
| `comp run <profile>` | One `RunSpec` | Yes: control plane + mirror |
| `comp campaign <yaml>` | Multi-run `CampaignSpec` | Yes: control plane + mirror |
| `comp loop --hours N` | Explore/exploit cycles | **No**: no control plane, no mirror |
| `comp dashboard` | Web monitor/control | n/a |
| `comp dashboard --console` | Rich TUI | Read-only |

The only built-in 24 h profile is `claim`: L2, 20 epochs, 10 seeds, narrow front cells. The broad profile `production-map` is L0, 1 epoch, batch limit 2, all axes — but only 3600 s. There is no broad 24 h profile.

### 3.2 Blockers

1. **Dashboard start is broken.**
   - `control-panel.ts:384-407` sends top-level `seeds`, `epochs`, `budget_seconds`, `fidelity`; `RunRequest` (`web.py:112-137`) forbids extra fields, so the request is 422.
   - `_cmd_dashboard` attaches `get_campaign_queue()` but never starts `run_campaign_queue_worker()` (`campaign_queue.py:428-433`). Queued jobs never run.
   - The queue panel cancels via `DELETE /api/campaign/{id}` (`control-panel.ts:357-363`); the server exposes `POST /api/campaigns/{id}/cancel` (`web.py:544-552`).

2. **`comp loop` is invisible to the dashboard.**
   - Both `PipelineConfig` constructions omit `control_plane` (`loop.py:552-560`, `:665-673`).
   - `ExperimentConfig` has no `mirror_path`; its `StoreConfig` is built without one (`registry/__init__.py:26-35`, `:60-62`). The writer holds the DuckDB lock, so the dashboard cannot read the live store.

3. **Progress is coarse and can look frozen.**
   - `RunStatus` carries only `run_id`, `stage`, `in_flight`, `cells_done`, `ceiling`, `at` (`control.py:114-155`).
   - `_publish_status` runs at stage boundaries and after batches (`_lifecycle.py:192-210`), not during a batch.
   - Measured: a 20 s `quick-run` paused at ~8 s still reported `cells_done=0, in_flight=0` for ~70 s while four cells trained. Pause lands at the next batch boundary.

4. **Throttling is only cell concurrency.**
   - `max_workers` is real (`_budget.py:111-124`, `backends.py:436-449`), but `_CELL_WORKERS = 4` is hard-coded (`_execution.py:35`) and there is no CLI flag.
   - No GPU memory fraction, GPU power cap, or CPU thread cap. The HUD "GPU" meter is queue allocation (`campaign_queue.py:381-396`), not hardware utilization.

5. **A 24 h run can overshoot.**
   - `comp run` always calls `_settle_maturity` (`_execution.py:343`), which re-measures L1-passing cells on confirmation seeds (`:395-411`) with no deadline.
   - `maturation` and `deep_tier` are copied (`:75-76`) but never read. The flags are dead.

---

## 4. Terminology and API refactor

### 4.1 The actual defect

The dashboard uses **"campaign"** for two different things:

- a queue entry (`CampaignQueueEntry.campaign_id`, 8 hex chars), and
- a run (`/api/campaigns/{campaign_id}/metrics` is called with a `run_id`; `metrics.ts:121`).

The WebSocket frame `campaign_metrics` carries `campaign_id: run.run_id` (`web.py:1814-1821`). The frontend reads it as a run id (`metrics.ts:39-49`). This works by accident and will break as soon as the dashboard can start a real campaign or loop.

### 4.2 Decision

Do **not** rename the domain nouns. Introduce one orchestration noun, **Job**, and fix the API names around it.

- `JobKind = RUN | CAMPAIGN | LOOP`
- `JobEntry`: id, kind, spec, status, priority, quota, timestamps, store, control-plane path, pid/result.
- `JobQueue`: priority scheduling, quotas, cancel/preempt, drain worker.
- `JobLauncher`: starts the process for a job and returns its handle.
- `JobStatus`: queued, running, paused, cancelling, completed, failed, cancelled.

### 4.3 API surface

| New endpoint | Replaces | Notes |
|---|---|---|
| `GET /api/jobs` | `GET /api/campaigns` | Queue entries of any kind |
| `GET /api/jobs/{job_id}` | `GET /api/campaigns/{id}` | Job lifecycle |
| `POST /api/jobs` | `POST /api/runs` | `{kind, profile|spec, overrides, device, budget, store}` |
| `POST /api/jobs/{job_id}/cancel` | `POST /api/campaigns/{id}/cancel` | Writes the job's control plane |
| `POST /api/jobs/{job_id}/preempt` | `POST /api/campaigns/{id}/preempt` | Requeue |
| `GET /api/runs/{run_id}/metrics` | `GET /api/campaigns/{id}/metrics` | Run evidence |
| `GET /api/runs/{run_id}/cost` | `GET /api/cost/{id}` | Run cost |

WebSocket messages: `run_metrics` carries `run_id`; `job_update` carries `job_id`. Delete `campaign_metrics`.

### 4.4 Migration order

1. Add `JobKind`/`JobEntry`/`JobStatus` and `JobQueue` as a thin wrapper over the current queue.
2. Add `JobLauncher` with `run`, `campaign`, `loop` strategies.
3. Move the dashboard routes and frontend to `/api/jobs` and `/api/runs/{run_id}/...`.
4. Delete the old names and the `campaign_metrics` frame.
5. Update docs and tests. No aliases.

### 4.5 Frontend migration notes

- `metrics.ts` currently subscribes to `campaign_metrics` and keys by `campaign_id` (which is a `run_id`). Rename the frame to `run_metrics` and the key to `run_id`.
- `control-panel.ts` and `queue-panel.ts` call `/api/campaigns` and `DELETE /api/campaign/{id}`. Change to `/api/jobs` and `POST /api/jobs/{id}/cancel`.
- `run-selection.ts` observes `campaign_metrics` as a run. Update the frame name; the logic stays the same.
- `palette.ts` entry "Show run queue" → "Show job queue".
- All TypeScript interfaces: `Campaign` → `JobEntry` where it represents a queue item; `RunSummary`/`RunMetrics` stay for runs.

---

## 5. Remove hardcoded parameters

### 5.1 Inventory

| Parameter | Current value | Location | Fix |
|---|---:|---|---|
| Cell concurrency (thread pool) | `4` | `_execution.py:35`; `campaign.py:214`; `loop.py:1352` | `--max-workers`, default from `ExecutionLimits` |
| Backend workers | `4` | `experiment/cli/__init__.py:71,185`; `runners/{ablation,comparison,replay,scaling}.py` | Shared `BackendConfig` |
| Queue concurrency | `4` | `campaign_queue.py:87` | `JobQueueConfig` |
| Queue GPUs | `8` | `campaign_queue.py:88` | Detect from hardware or config |
| Queue CPUs | `64` | `campaign_queue.py:89` | `os.cpu_count()` or config |
| Queue memory | `512.0` GB | `campaign_queue.py:90` | Detect or config |
| Loop hours | `8.0` | `loop.py:110`; `_parser.py:254-259` | Already a flag; make `survey-24h` explicit |
| Loop cell workers | `4` | `loop.py:123`; `_campaign.py:161` | `--max-workers` |
| Loop task schedule | 8 fixed tasks | `loop.py:96-105` | `--tasks`, default from registry |
| Loop epochs | 1 / 3 | `loop.py:119-120` | Expose `--epochs-explore/exploit` |
| Dashboard update | `2.0` s | `web.py:275`; not passed from CLI | Pass `--update-interval` to web |
| Control poll | `0.2` s | `control.py:51` | Keep as protocol constant, or `ControlPlaneConfig` |
| Dashboard port | `8080` | `web.py:274,2347` | Already `--port`; keep default |

### 5.2 Config surface

Add one dataclass, `ExecutionLimits`, and one CLI group:

```python
@dataclass(frozen=True, slots=True)
class ExecutionLimits:
    cell_workers: int
    cpu_threads_per_cell: int | None
    gpu_memory_fraction: float | None
    queue_max_concurrent: int
    queue_max_gpus: int
    queue_max_cpus: int
    queue_max_memory_gb: float
```

Defaults come from hardware and config, never from a literal in a function body:

- `cell_workers = min(4, os.cpu_count() or 1)` only as a **last-resort fallback**.
- `queue_max_gpus` from `torch.cuda.device_count()`.
- `queue_max_cpus` from `os.cpu_count()`.
- `queue_max_memory_gb` from `psutil.virtual_memory().total`.

Expose flags on `run`, `campaign`, and `loop`:

```text
--max-workers N
--cpu-threads N
--gpu-memory-fraction F
--queue-max-concurrent N
--queue-max-gpus N
--queue-max-cpus N
--queue-max-memory-gb F
```

### 5.3 Rule

No literal `4`, `8`, `64`, or `512` in an execution path. A default is either:

1. a named constant with a documented reason, or
2. derived from hardware/config, or
3. supplied by the caller.

### 5.4 `ExecutionLimits` wiring

- `run`, `campaign`, `loop` parsers collect flags into `ExecutionLimits`.
- `LocalBackend` and `DDPBackend` accept `ExecutionLimits` (or subset) instead of bare `max_workers`.
- `_apply_ceiling` and `control.py` receive the ceiling from the same source.
- `torch.set_num_threads(cfg.cpu_threads_per_cell)` called once per worker process (via `multiprocessing` init or `threadpoolctl`).
- `torch.cuda.set_per_process_memory_fraction(cfg.gpu_memory_fraction)` called once at process start.
- Control plane stores the effective limits so the dashboard can display them.

---

## 6. Workstreams

### P0 — make the 24 h path controllable and watchable

**P0.1 Add `survey-24h` profile**

- `_profiles.py`: `production-map` shape, `budget_seconds=86400`, L0, 1 epoch, `batch_limit=MEASURED_BATCH_LIMIT`, all axes, `maturation=False`, `deep_tier=False`.
- Note: `maturation`/`deep_tier` are dead today; P0.4 must make them effective, or the profile must use `--no-settle`.
- Appears automatically in `/api/profiles`.
- Gate: `comp run survey-24h --dry-run` prints the declared space and 24 h budget.

**P0.2 Wire the loop**

- `loop.py:552-560`, `:665-673`: pass `control_plane=control_plane_path(cfg.store_path)`.
- `LoopDriver._should_stop`: read the plane; return `True` on `cancel`.
- `registry/__init__.py`: add `mirror_path` to `ExperimentConfig`; pass it to `StoreConfig`.
- `loop.py`: pass `mirror_path(cfg.store_path)`.
- Gate: dashboard sees `in_flight`/`cells_done` from a live loop; pause/stop reaches it.

**P0.3 Fix start-from-dashboard**

- `control-panel.ts:384-407`: send `{profile, overrides: {n_seeds, epochs, budget_seconds, fidelity}, device}`.
- `WebDashboard.start()`: start `run_campaign_queue_worker()`; cancel it in `stop()`.
- Fix the cancel URL to `POST /api/campaigns/{id}/cancel`.
- Gate: browser Start -> job queued -> run appears in the run list -> control bar tracks it.

**P0.4 Make settlement budget-aware**

- `_execution.py:343`: pass the deadline to `_settle_maturity`.
- `_settle_maturity:364`: stop confirmation work when the deadline expires.
- Honor `maturation`/`deep_tier`, or delete them and add `--settle/--no-settle`.
- Gate: a 60 s `quick-run` with `--no-settle` exits within a small grace window.

**P0.5 Throttle flags**

- Add `--max-workers`, `--cpu-threads`, `--gpu-memory-fraction` to `run`, `campaign`, `loop`.
- Thread them through `ExecutionLimits` into `LocalBackend` and the control plane.
- Apply `torch.set_num_threads` per worker and `torch.cuda.set_per_process_memory_fraction` once per process.
- Gate: `--max-workers 1` halves observed in-flight cells; `--gpu-memory-fraction 0.5` caps CUDA memory.

**P0.6 Normalize paths**

- `control_plane_path` and `mirror_path` resolve to absolute paths.
- Gate: dashboard and run started from different cwds share one plane and one mirror.

**P0.7 ExecutionLimits dataclass and wiring**

- Add `ExecutionLimits` dataclass in a shared location (e.g., `execution/limits.py`).
- Parser functions (`_parser.py`) build `ExecutionLimits` from flags.
- `spec_from_profile` / `campaign_spec` / `LoopConfig` accept `ExecutionLimits`.
- `LocalBackend.__init__` takes `ExecutionLimits`; `DDPBackend` likewise.
- Dashboard control bar ceiling slider max = `cell_workers` from the active job's limits.

### P1 — progress, telemetry, and the job model

**P1.1 Status heartbeat**

- Publish `RunStatus` every 2 s during batches, not only at stage boundaries (`_lifecycle.py:192-210`).
- Gate: `in_flight` moves during a long batch.

**P1.2 Richer status**

- Extend `RunStatus` (`control.py`): `elapsed_s`, `budget_s`, `declared_cells`, `records`, `eta_s`, `throughput_cells_per_min`, `stage_detail`.
- `declared_cells` = total cells in the run's declared space (from `declared_cells(spec)`).
- `throughput_cells_per_min` = `cells_done / (elapsed_s / 60)`.
- `eta_s` = `(declared_cells - cells_done) / throughput * 60` when `throughput > 0`.
- Show a progress bar and ETA in `control-bar.ts`/`hud.ts`.
- Gate: a 5-minute run shows a non-zero ETA within 30 s.

**P1.3 Real GPU telemetry**

- Optional `pynvml` sampler in `web.py`: utilization, memory, power, temperature.
- Add `psutil` and `nvidia-ml-py` to the `dashboard` extra.
- Gate: `/api/control` reports GPU utilization on a CUDA host and `null` on CPU.

**P1.4 Job model**

- Add `JobKind`, `JobEntry`, `JobStatus`, `JobQueue`, `JobLauncher`.
- `JobLauncher` starts `comp run`, `comp campaign`, or `comp loop` as a subprocess, with its own store and control plane.
- Per-job control plane: `control_plane_path(store, job_id)`.
- Gate: one dashboard can start a run and a loop into different stores and control them independently.

**P1.5 JobQueue and JobLauncher detail**

- `JobQueue`: priority scheduling, resource quotas, cancel/preempt, drain worker. Wraps current `CampaignQueue` but keyed by `job_id` not `campaign_id`.
- `JobLauncher`: per `JobKind` strategy:
  - `RUN`: `asyncio.create_subprocess_exec("uv", "run", "comp", "run", ..., "--run-id", job_id, ...)`
  - `CAMPAIGN`: `asyncio.create_subprocess_exec("uv", "run", "comp", "campaign", ...)` with a generated YAML
  - `LOOP`: `asyncio.create_subprocess_exec("uv", "run", "comp", "loop", ...)`
- All subprocesses: `start_new_session=True`, detached from dashboard. PID tracked in `JobEntry`.
- Job's control plane = `control_plane_path(job_store, job_id)` so multiple jobs in the same store are independently controllable.
- Job completion updates `JobEntry.status`; result/artifact paths stored.

### P2 — polish

- Queue cancel writes `cancel` to the job's control plane; it does not just mark status.
- Distinguish `cancelled` from `completed` in run status.
- Pass `--no-websockets` and `--update-interval` through to the web dashboard.
- Add tests for the start schema, queue worker, loop control/mirror, and job API.

---

## 7. Preparation for the 24-hour broad experiment

### 7.1 Pre-flight checklist

| Check | Command / evidence |
|---|---|
| Dev env | `uv run python -c "import optuna, scipy, torchvision, pytest"` |
| Device | `uv run python -c "import torch; print(torch.cuda.is_available())"` |
| Disk | At least 20 GB free for store, mirror, checkpoints, reports |
| Store path | Absolute path; dashboard and run use the same one |
| Control plane | `experiment.control.json` appears beside the store |
| Mirror | `experiment.mirror.duckdb` updates every ~2 s |
| Kill time | Register a hard stop (e.g., `timeout 25h`) before launch |
| Resume | `--run-id` or loop checkpoint exists and is tested on a 2-minute run |

### 7.2 What "broad" means

| Dimension | `survey-24h` | `claim` (for contrast) |
|---|---|---|
| Axes varied | All 6 (all available primitives) | 1 (credit only) |
| Task | Single (default `digits`) | Single (`digits`) |
| Fidelity | L0 (1 epoch) | L2 (20 epochs) |
| Seeds/cell | 1 | 10 |
| Cells/cycle | ~135 (all axes) | 4 (front cells) |
| Settlement | None (or uncertainty only) | Full L1→L2 confirmation |

**Broad = high axis coverage, low depth per cell.** The goal is to map the Pareto frontier across the ontology, not to grade a single claim.

### 7.3 Run recipe

**Primary: broad single run (dashboard/queue path)**

```bash
uv run comp run survey-24h --store experiment.duckdb \
  --max-workers 4 --device auto
```

**Advanced: broad multi-task loop**

```bash
uv run comp loop --hours 24 --profile production-map \
  --tasks xor,iris,spiral,digits,breast_cancer,wine,cartpole,copy_task \
  --max-workers 4 --device auto \
  --store experiments/loop/loop.duckdb
```

Use one task for a single-run survey, or the loop for cross-task coverage. Do not use `claim` for a survey. `--max-workers` is an operator choice; the default is derived from hardware, not a literal.

### 7.4 Monitoring cadence

| Interval | Check |
|---|---|
| 1 min | Dashboard: `in_flight`, `cells_done`, CPU/GPU, store source (`live` vs `snapshot`) |
| 15 min | `comp status --store ... --detailed`; records/minute; rejections |
| 1 h | `comp coverage report`; axis coverage; unmeasured axes |
| 6 h | `comp report --format text`; claims, limitations, Pareto |
| 24 h | Stop; final report; export records; archive store and mirror |

### 7.5 Stop conditions

- **Hard stop:** wall clock at 24 h + 5 min grace.
- **Zero yield:** 3 consecutive batches with one shared failure cause (`ZeroYieldError`).
- **Disk:** free space below 5 GB.
- **Thermal/power:** GPU temperature above 85 C or power above 95% for 10 min.
- **Quality:** >50% of records quarantined or at chance for 1 h.

### 7.6 Artifacts

- `experiment.duckdb` (evidence) and `experiment.mirror.duckdb` (reader copy).
- `experiment.control.json` (control/status).
- `report.md` / `report.json` (run report).
- `coverage.json` (axis/task coverage).
- `pareto.json` (frontier).
- Loop only: `checkpoint.json`, `reports/cycle_NNN.md`, `ledger.jsonl`, `defects.json`.

---

## 8. Acceptance criteria

| Criterion | Gate |
|---|---|
| Start from browser | Click Start -> job queued -> run appears in <10 s |
| Watch progress | `in_flight`, `cells_done`, ETA update during a long batch |
| Pause/step/stop | Each verb lands at the next batch boundary; stop ends the run |
| Throttle | `--max-workers` changes in-flight count; GPU fraction caps memory |
| Broad 24 h | `survey-24h` declares all axes, L0/L1, 1–2 epochs |
| Bounded | Run exits within 5 min of the 24 h budget, settlement included |
| Loop controllable | Dashboard pause/stop reaches `comp loop` |
| No hardcoded limits | No literal 4/8/64/512 in execution paths |
| Terminology | No `campaign_id` in a run metrics payload |

### Test gates

```bash
# Unit: control plane, dashboard control, loop uses engine
uv run python -m pytest tests/unit/experiment/test_dashboard_control.py \
  tests/unit/experiment/test_control_plane.py \
  tests/property/test_loop_uses_engine_lock.py -q

# Unit: dashboard actions, space, websocket
uv run python -m pytest tests/unit/experiment/test_dashboard_actions.py \
  tests/unit/experiment/test_dashboard_space.py \
  tests/unit/experiment/test_dashboard_websocket.py -q

# Typecheck + build
cd computronium/experiment/execution/dashboard && npm run build && npx tsc --noEmit
```

### Execution order (with dependencies)

```
1. P0.6 (paths)                           # no deps
2. P0.1 (survey-24h profile)              # no deps
3. P0.7 (ExecutionLimits + wiring)        # no deps
4. P0.3 (dashboard start + queue worker)  # needs P0.6, P0.7
5. P0.2 (loop wiring)                     # needs P0.6, P0.7
6. P0.4 (settlement deadline)             # needs P0.2, P0.7
7. P0.5 (throttle flags)                  # needs P0.7
8. P1.1 (status heartbeat)                # needs P0.2, P0.3
9. P1.2 (rich status + ETA)               # needs P1.1
10. P1.3 (GPU telemetry)                  # needs P0.7
11. P1.4 (Job model)                      # needs P1.1, P1.2
12. P1.5 (JobQueue/Launcher)              # needs P1.4
13. P2 (polish)                           # needs all above
14. Dry runs: 10 min -> 1 hr -> 24 hr
```

**Critical path:** P0.6 → P0.7 → {P0.2, P0.3} → P0.4/P0.5 → P1.1 → P1.2 → P1.4 → P1.5 → P2.

---

## 9. Open questions (require decisions before implementation)

### 9.1 Control plane granularity

**Q1: Per-job vs per-store control plane.**  
Currently one store has one plane (`control_plane_path(store)`). A queue of independent jobs needs one plane per job.  
**Options:**
- A) `control_plane_path(store, job_id)` — plane file includes job id. Clean isolation.
- B) Keep per-store plane; jobs in the same store share pause/stop (current behavior).  
**Recommendation:** A. The dashboard should be able to pause one job while another runs in the same store.

**Q2: What identifies a job in the control plane?**  
The job id is the queue entry id (8 hex chars). The run id is the store's run id (UUID). They differ when a job resumes an existing run. The plane must carry `job_id` and `run_id` separately.

### 9.2 Job execution model

**Q3: Subprocess vs in-process jobs.**  
A 24 h job should not share the dashboard process (crash isolation, resource accounting, independent restart).  
**Options:**
- A) `JobLauncher` uses `asyncio.create_subprocess_exec` with `start_new_session=True` (detached process group). Dashboard tracks PID, writes control plane, reads status.
- B) In-process `asyncio.Task` for short jobs, subprocess for long jobs.  
**Recommendation:** A for all jobs. Uniformity simplifies the dashboard and avoids GIL/fork issues.

**Q4: How does the dashboard discover a job's store and control plane?**  
`JobEntry` stores `store_path` and `control_plane_path`. The dashboard reads `/api/jobs/{id}` and uses those paths for `/api/control`, `/api/runs/{run_id}/metrics`, etc.

### 9.3 Settlement policy

**Q5: Should `survey-24h` settle at all?**  
Settlement (`_settle_maturity`) re-measures L1-passing cells on fresh confirmation seeds (C1). This is for claim-grade depth. A broad survey wants breadth, not depth.  
**Options:**
- A) `--no-settle` flag: skip `_settle_maturity` entirely. Compute uncertainty/report from existing records only.
- B) `--settle-shallow`: run L1 statistical gates but no L2 confirmation re-measurement.
- C) Full settlement (current default) — not recommended for 24 h broad.  
**Recommendation:** A. Add `--settle/--no-settle` to `run`, `campaign`, `loop`. Default `--settle` for compatibility; `survey-24h` uses `--no-settle`.

### 9.4 Task breadth

**Q6: Single-task vs multi-task dashboard path.**  
A single run measures one task. The loop provides multi-task breadth.  
**Options:**
- A) `survey-24h` is single-task; use `comp loop` for multi-task.
- B) Add `--tasks` to `run` so a single run can sweep tasks (requires a new profile or overrides).  
**Recommendation:** A. Keep the run single-task; the loop is the multi-task primitive. This matches the ontology: a cell is one coordinate on one task.

### 9.5 GPU throttle semantics

**Q7: Memory cap vs utilization cap.**  
`torch.cuda.set_per_process_memory_fraction(0.5)` caps allocatable memory, not utilization. Utilization is controlled by concurrency (`--max-workers`).  
**Options:**
- A) Expose both: `--gpu-memory-fraction` for OOM prevention, `--max-workers` for throughput control.
- B) Only `--max-workers`; let the OOM killer handle it.  
**Recommendation:** A. Both knobs serve different purposes and are cheap to implement.

### 9.6 Profile storage

**Q8: Keep profiles in Python or move to YAML?**  
Current: `_profiles.py` dict. YAML would let the dashboard add profiles without code changes.  
**Options:**
- A) Keep Python. Profiles are code; changes are deliberate. `survey-24h` is one addition.
- B) Move to `configs/profiles/*.yaml`; load at startup.  
**Recommendation:** A for now. Python profiles are the single source of truth for CLI and dashboard. YAML adds a config format without clear benefit yet.

### 9.7 Queue persistence

**Q9: Should the job queue survive dashboard restart?**  
Current `CampaignQueue` is in-memory only.  
**Options:**
- A) In-memory only (current). Simple; jobs are re-submittable via CLI.
- B) Persist queue to a small JSON/DB file; recover on restart.  
**Recommendation:** A. 24 h runs are long-lived; the dashboard is not the system of record. CLI `comp run --run-id` resumes. Queue persistence is a separate feature.

### 9.8 Progress ETA algorithm

**Q10: How to compute ETA for a non-uniform cell stream?**  
Cells have different costs (L0 vs L1, different architectures). Simple `cells_done / elapsed * remaining` overestimates for hard cells.  
**Options:**
- A) Naive linear extrapolation (simple, optimistic).
- B) Exponential moving average of recent cell times, weighted by cell type.
- C) Per-cell-type timing model (from `CellTiming`).  
**Recommendation:** Start with A; show confidence band. Upgrade to B in P1.2 if needed.

## 10. Risks

| Risk | Mitigation |
|---|---|
| 24 h run overshoots | Deadline in settlement; hard `timeout`; stop conditions |
| Dashboard cannot read live store | Mirror + absolute paths; test with a 2-minute run |
| Pause takes minutes | Status heartbeat; document batch-boundary semantics; smaller batch limit |
| GPU OOM | `--gpu-memory-fraction`; `--max-workers 1`; monitor |
| Queue never drains | Start worker in `WebDashboard.start()`; test |
| API rename breaks frontend | Do the rename and `npm run build` in one change; no aliases |
| `ExecutionLimits` not respected | Unit tests for backend init, control plane, dashboard slider |
| Loop control plane not polled | Add `LoopDriver._should_stop` test with a mock plane |
| Settlement deadline ignored | Integration test: 60 s run with `--no-settle` exits in <70 s |
| Dashboard/WebSocket flakiness | `pytest -x` on dashboard tests; `capture_dashboard_tour` as smoke |

## 11. Dependencies on other work

| This plan | Depends on | Status |
|---|---|---|
| `survey-24h` profile | `production-map` profile exists | ✅ |
| Loop control plane | `control_plane_path` function | ✅ |
| Mirror for loop | `mirror_path` + `readable_store` | ✅ |
| Dashboard start | `CampaignQueue` + worker | ⚠️ broken (P0.3) |
| Throttle flags | `LocalBackend.set_max_workers` | ✅ |
| GPU telemetry | `kernel/resources.py` NVML code | ✅ (needs wiring) |
| Job model | `CampaignQueue` refactor | ⚠️ P1.4 |
| `ExecutionLimits` | New dataclass + parser wiring | ⚠️ P0.7 |

## 12. Rollout plan

| Phase | Deliverable | Gate |
|---|---|---|
| 1. Foundation | P0.6, P0.1, P0.7, P0.3 | `comp run survey-24h` from browser works |
| 2. Loop + settlement | P0.2, P0.4 | Dashboard pauses/stops a live loop |
| 3. Throttle + progress | P0.5, P1.1, P1.2 | `--max-workers` and ETA visible |
| 4. GPU + Job model | P1.3, P1.4, P1.5 | Multi-job dashboard; GPU meter real |
| 5. Polish + dry runs | P2, 10m/1h/24h | 24 h survey completes within 5 min of budget |
| 6. Scheduling (future) | P3: Timeline, calendar, budget allocation | Visual scheduling UI works |
| 7. Campaign composition (future) | P4: Visual DAG, Pareto budgeting | Drag-and-drop campaign builder |
| 8. Fleet (future) | P5: Multi-machine queue, shared baselines | Cross-machine loop coordination |

## 13. Future capabilities (P3–P5 sketch for consideration)

*Not in current scope. Included here so P0–P2 wiring doesn't need rework.*

### P3 — Timeline & scheduling

**Timeline panel** (new stage view):
- Left rail: jobs grouped by status (scheduled/running/waiting/paused/done)
- Center: horizontal bars — scheduled start/end, actual start/end, budget consumed
- Handles on bars: drag to reschedule, click to pause/resume, right-click → preempt/cancel
- Right rail: resource forecast — GPU hours available vs committed, per-machine

**Scheduling primitives** (CLI + API):
```
comp job schedule --at "2026-11-02 02:00" --job-id <id>
comp job budget --job-id <id> --gpu-hours 48 --cpu-hours 200
comp job depends-on <parent-job-id> <child-job-id>
comp job policy --preemptible --priority high
```

**Budget allocation**:
- Campaign-level budget splits (e.g., `explore: 40%`, `exploit: 60%`)
- Automatic rebalancing when a job finishes early/late
- Hard caps per job, soft caps per campaign

### P4 — Campaign composition (visual DAG)

**Canvas-based campaign builder** (new workspace):
- Nodes = profiles (`production-map`, `maturation`, `claim`, custom)
- Edges = `depends_on`, with budget flow annotations
- Properties panel: overrides, device, store, resource quota
- "What-if" simulation: Pareto frontier estimate before running
- Export → YAML / JSON / direct queue submit

**Pareto budgeting**:
- Target: N cells on frontier by hour H
- Allocate explore budget to axes with highest uncertainty
- Allocate exploit budget to cells near frontier
- Stop conditions: frontier stable, budget spent, quality gate

### P5 — Fleet (multi-machine)

**Shared job queue** (Redis/PostgreSQL backend):
- Central `JobQueue` service; dashboards connect as clients
- Jobs carry `affinity` (GPU type, memory, node labels)
- Scheduler matches affinity → node

**Shared baseline registry**:
- Baselines computed once per (task, hardware, budget) triplet
- Published to shared store; all machines read
- Eliminates redundant baseline runs across fleet

**Cross-loop Pareto**:
- Each loop exports its frontier to shared store
- Fleet dashboard merges frontiers across machines/tasks
- Global Pareto drives next-loop task/axis selection

**Dashboard fleet mode**:
- Top bar: cluster status (nodes, GPUs free, jobs running)
- Main pane: merged Pareto + per-machine job timelines
- Drill-down: click machine → single-machine dashboard

### Prerequisites from P0–P2

| P3–P5 need | Provided by |
|---|---|
| Per-job control plane | P0.6, P1.4 |
| Job model (kind, status, store, pid) | P1.4, P1.5 |
| Real progress/ETA | P1.1, P1.2 |
| GPU telemetry | P1.3 |
| Absolute paths | P0.6 |
| ExecutionLimits | P0.7 |

### Design questions for P3–P5

1. **Dashboard as scheduler vs separate service.** Should the timeline logic live in the dashboard (client-side) or a `comp scheduler` daemon? Recommendation: daemon for durability; dashboard as read/write UI.

2. **Campaign DAG in store vs YAML.** Store-native DAG enables live editing; YAML is portable. Recommendation: YAML as source of truth; store caches the parsed DAG for the UI.

3. **Multi-tenancy.** Fleet implies multiple users/projects. Current `CampaignQueue` has `project`/`user` fields; need RBAC on job control.

4. **Checkpoint migration.** Moving a paused 24 h job between machines requires store + checkpoint copy. Need `comp job migrate --to <node>`.

5. **Cost tracking.** Fleet needs per-job cost (GPU-hr, energy, carbon) aggregated to project. Extend `CostTracker` with project dimension.


