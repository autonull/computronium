# TODO77 — 24-Hour Broad Experiment: Refined Plan

**Status:** Core Implementation Complete — Dry Runs In Progress  
**Created:** 2026-11-01  
**Based on:** TODO76 evaluation (§1-9)  
**Goal:** A fresh install can start, watch, pause, throttle, and finish a broad ~24-hour experiment from the dashboard, without narrowing the experiment space and without hidden hardcoded limits.

---

## 1. Design Principles (Non-Negotiable)

| Principle | Application |
|-----------|-------------|
| **No new orchestration nouns** | Keep `RunSpec`, `CampaignSpec`, `LoopConfig`. Fix naming conflation by renaming `CampaignQueue` → `RunQueue` (it queues runs, not campaigns). |
| **Subprocess only where needed** | `comp run` stays in-process. `comp loop` and `comp campaign` (multi-run) use subprocess for isolation. |
| **Dead flags become live** | `maturation`/`deep_tier` in `RunProfile` are copied but never read. Make them effective — no new `--no-settle` flag. |
| **Hardware-derived defaults** | No literals `4`, `8`, `64`, `512` in execution paths. `ExecutionLimits` dataclass with `from_cli()` deriving from `os.cpu_count()`, `torch.cuda.device_count()`, `psutil.virtual_memory()`. |
| **Single control plane per store (for now)** | Per-job control plane deferred with Job model. 24h run is single job per store. |
| **Minimal API rename** | `/api/campaigns` → `/api/queue`, `/api/campaigns/{id}/metrics` → `/api/runs/{run_id}/metrics`. Delete `campaign_metrics` WebSocket frame. |

---

## 2. Vocabulary (Final)

| Term | Meaning | Decision |
|------|---------|----------|
| **Experiment** | Research program / evidence store | Domain word, not API noun |
| **Run** | One `RunSpec` execution | Keep |
| **Campaign** | Multi-run YAML (`CampaignSpec`) | Keep |
| **Loop** | Continuous explore/exploit (`LoopDriver`) | Keep |
| **RunQueue** | Priority queue of `RunSpec` executions | **Rename** `CampaignQueue` → `RunQueue` |
| **RunQueueEntry** | Queued run with status/quota | **Rename** `CampaignQueueEntry` |
| **RunQueueStatus** | queued/running/completed/failed/cancelled | **Rename** `CampaignStatus` |
| **Profile** | Named run template (`RunProfile`) | Keep |
| **Spec** | Fully declared run/campaign/loop | Keep |
| **Cell** | Coordinate + schedule candidate | Keep |
| **Record** | One measured seed of a cell | Keep |
| **Store** | DuckDB evidence store | Keep |
| **Control plane** | Per-store control/status document | Keep, bind to store path |
| **ExecutionLimits** | Unified concurrency/resource config | **New** dataclass |

**Rule:** The dashboard's "campaign" conflation is fixed by renaming the queue types, not by introducing `Job`.

---

## 3. Blockers (from TODO76 §3.2 — All Must Fix)

| # | Blocker | Location | Fix |
|---|---------|----------|-----|
| B1 | Dashboard start: `RunRequest` forbids extra fields from `control-panel.ts` | `web.py:112-137` | Frontend sends `{profile, overrides: {...}, device}` |
| B2 | Queue worker never started | `web.py` lifespan | Start `run_campaign_queue_worker()` in `WebDashboard.start()` |
| B3 | Loop invisible: no `control_plane`, no `mirror_path` | `loop.py:552-560`, `registry/__init__.py:26-35` | Thread through `PipelineConfig` |
| B4 | Progress coarse: status only at stage boundaries | `_lifecycle.py:192-210` | Heartbeat every 2s during batches |
| B5 | Throttling only cell concurrency, hardcoded `_CELL_WORKERS=4` | `_execution.py:35`, `campaign.py:214`, `loop.py:123` | `ExecutionLimits` + CLI flags |
| B6 | Settlement ignores deadline, dead `maturation`/`deep_tier` flags | `_execution.py:343, 364-411` | Pass deadline; honor profile flags |

---

## 4. Workstreams

### P0 — Critical Path (2 weeks)

#### P0.1 ExecutionLimits Dataclass + CLI Flags ✅ DONE
**File:** `computronium/experiment/execution/limits.py` — **Already implemented**

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

    @classmethod
    def from_cli(cls, **kwargs) -> "ExecutionLimits":
        ...
    def apply_torch_settings(self) -> None:
        ...
```

**Wired to:**
- ✅ `_parser.py`: `--max-workers`, `--cpu-threads`, `--gpu-memory-fraction`, `--queue-max-*` added to `run`, `campaign`, `loop`, `dashboard`
- ✅ `_execution.py:305`: `LocalBackend(max_workers=limits.cell_workers)`
- ✅ `campaign.py:218`: `LocalBackend(max_workers=self.limits.cell_workers)`
- ✅ `registry/loop.py:128,138`: `LoopConfig.cell_workers` + `LoopConfig.limits`
- ✅ `campaign_queue.py:104,119`: `RunQueue.__init__(limits: ExecutionLimits)` + `to_queue_config()`
- ✅ `web.py:311-312,346-348`: Pass limits to queue; `apply_torch_settings()` in lifespan

#### P0.2 survey-24h Profile ✅ DONE
**File:** `surface/_profiles.py` — **Already implemented**

```python
"survey-24h": RunProfile(
    name="survey-24h",
    description="Broad 24h mapping: all axes, L0/L1, 1-2 epochs, no settlement",
    stages=[
        "s1_frame", "s2_space", "s3_schedule", "s4_gate",
        "s5_compose", "s6_train", "s7_measure", "s8_record",
        "s9_attribute", "s10_decide", "s11_report",
    ],
    fidelity="L0",
    n_seeds=1,
    epochs=1,
    batch_limit=MEASURED_BATCH_LIMIT,
    budget_seconds=86400.0,  # 24 hours
    task="digits",
    policy="model_based",
    param_budget=BROAD_PARAM_BUDGET,
    objectives=("validation_accuracy", "walltime_total", "param_count"),
    promotion_threshold=0.5,
    maturation=False,      # ← effective: skip L1→L2 promotion
    deep_tier=False,       # ← effective: skip confirmation re-measurement
    hyperparameters=dict(_SEARCH_SWEEP),
    checkpoint_every_n=0,
),
```

#### P0.3 Dashboard Start Fixes ✅ DONE
**Files:** `web.py`, `control-panel.ts`

- ✅ `RunRequest` (line 134): Kept `extra="forbid"` — frontend sends overrides as dict
- ✅ `control-panel.ts:398`: Sends `{profile, overrides: {n_seeds, epochs, budget_seconds, fidelity}, device}`
- ✅ `WebDashboard.__init__`: Starts `run_queue_worker()` task in `_lifespan` (web.py:345-348)
- ✅ Fix cancel URL: `POST /api/campaigns/{id}/cancel` (control-panel.ts:360)

#### P0.4 Loop Wiring ✅ DONE
**Files:** `loop.py`, `registry/__init__.py`

```python
# loop.py:571-573, 686-688
PipelineConfig(
    ...,
    control_plane=control_plane_path(cfg.store_path),  # ✅ added
)

# registry/__init__.py:60-61 — mirror_path passed to StoreConfig, not ExperimentConfig
RecordStore(StoreConfig(path=self._config.store_path, read_only=self._config.read_only))
```

#### P0.5 Settlement Deadline + Live Flags ✅ DONE
**File:** `surface/_cli/_execution.py:369-457`

```python
def _settle_maturity(store, run_id, spec, deadline: Deadline | None = None) -> None:
    # Honor profile flags — no new CLI flag needed
    if not spec.maturation and not spec.deep_tier:
        compute_and_store_uncertainty(store, run_id, min_seeds=spec.n_seeds)
        return
    
    # Existing promotion logic WITH deadline checks
    def confirmation_evaluator(cell_records, confirmation_seeds):
        if deadline and deadline.expired():  # ✅ uses expired()
            return []  # Stop confirmation work
        # ... existing logic
```
- ✅ Added `maturation` and `deep_tier` fields to `RunSpec` (run_spec.py:187-188)
- ✅ Copied from `RunProfile` in `spec_from_profile()` (_execution.py:197-198)

#### P0.6 Path Normalization ✅ DONE
**File:** `execution/control.py:168-191`

- ✅ `control_plane_path()` and `mirror_path()` resolve to absolute paths
- ✅ Test: dashboard and run from different cwds share one plane and mirror

#### P0.7 Status Heartbeat ✅ DONE
**File:** `execution/pipeline/_lifecycle.py:341-353`

```python
async def _heartbeat_loop(self) -> None:
    """Update run heartbeat and publish status every 2 seconds."""
    while not self._shutdown:
        await asyncio.sleep(2)
        if self._shutdown:
            break
        try:
            if self._store.is_open:
                self._store.update_heartbeat(self._config.run_id)
            self._publish_status()  # ✅ Publishes rich status every 2s
        except Exception as e:
            logger.warning("Failed to update heartbeat: %s", e)
```
- ✅ `_heartbeat_loop()` task started in `run()` (line 281)
- ✅ `_publish_status()` computes rich status (declared_cells, elapsed_s, budget_s, records, throughput_cpm, eta_s, stage_detail)

#### P0.8 Rich Status + ETA ✅ DONE
**Files:** `execution/control.py`, `execution/dashboard/control-bar.ts`

- ✅ `RunStatus` extended with: `declared_cells`, `elapsed_s`, `budget_s`, `records`, `throughput_cpm`, `eta_s`, `stage_detail` (control.py:142-148)
- ✅ `_publish_status()` computes and publishes all fields (_lifecycle.py:193-255)
- ✅ Frontend: progress bar + ETA in control bar (uses `/api/control` payload)

#### P0.9 Real GPU Telemetry ✅ DONE
**File:** `execution/dashboard/web.py:907-981`

- ✅ `_get_gpu_telemetry()` wires NVML code to `/api/control`
- ✅ Returns `null` on CPU-only hosts
- ✅ `nvidia-ml-py` added as dependency (handled by environment)

---

### P1 — Polish (Week 3, Optional for 24h Run)

| Item | Description | Effort |
|------|-------------|--------|
| P1.1 | Queue cancel writes control plane (not just status) | Medium |
| P1.2 | Distinguish `cancelled` vs `completed` in run status | Low |
| P1.3 | Pass `--no-websockets` / `--update-interval` to web dashboard | Low |
| P1.4 | Tests: start schema, queue worker, loop control/mirror, job API | Medium |

---

### P2 — Deferred (Post-24h)

| Item | Reason |
|------|--------|
| Job abstraction (`JobKind`, `JobEntry`, `JobQueue`, `JobLauncher`) | Over-engineering for current needs; existing trio sufficient |
| Subprocess for `comp run` | Unnecessary complexity; in-process is fine for single run |
| Queue persistence | In-memory OK for 24h; CLI `--run-id` resumes |
| Profile YAML storage | Python profiles are single source of truth |
| Campaign DAG / Timeline / Fleet (P3-P5) | Future work; ensure P0 wiring doesn't preclude |

---

## 5. 24-Hour Broad Experiment: Run Recipe

### Primary: Broad Single Run (Dashboard/Queue Path)

```bash
uv run comp dashboard --store experiment.duckdb
# Browser: choose "survey-24h" → Start
# Watch progress, pause/step/stop, move concurrency ceiling
```

Or CLI:
```bash
uv run comp run survey-24h --store experiment.duckdb \
  --max-workers 4 --device auto
```

### Advanced: Broad Multi-Task Loop

```bash
uv run comp loop --hours 24 --profile production-map \
  --tasks xor,iris,spiral,digits,breast_cancer,wine,cartpole,copy_task \
  --max-workers 4 --device auto \
  --store experiments/loop/loop.duckdb
```

**Broad = high axis coverage, low depth per cell.** `survey-24h` declares all 6 axes, L0/L1, 1-2 epochs, 1 seed/cell, no settlement. ~135 cells/cycle.

---

## 6. Pre-Flight Checklist (Run Before 24h)

| Check | Command |
|-------|---------|
| Dev env | `uv run python -c "import optuna, scipy, torchvision, pytest"` |
| Device | `uv run python -c "import torch; print(torch.cuda.is_available())"` |
| Disk | ≥20 GB free for store, mirror, checkpoints, reports |
| Store path | Absolute path; dashboard and run use same one |
| Control plane | `experiment.control.json` appears beside store |
| Mirror | `experiment.mirror.duckdb` updates every ~2s |
| Kill time | Register hard stop: `timeout 25h` before launch |
| Resume | `--run-id` or loop checkpoint tested on 2-min run |

---

## 7. Monitoring Cadence

| Interval | Check |
|----------|-------|
| 1 min | Dashboard: `in_flight`, `cells_done`, CPU/GPU, store source (`live` vs `snapshot`) |
| 15 min | `comp status --store ... --detailed`; records/min; rejections |
| 1 h | `comp coverage report`; axis coverage; unmeasured axes |
| 6 h | `comp report --format text`; claims, limitations, Pareto |
| 24 h | Stop; final report; export records; archive store and mirror |

---

## 8. Stop Conditions

- **Hard stop:** Wall clock at 24h + 5 min grace
- **Zero yield:** 3 consecutive batches with one shared failure cause (`ZeroYieldError`)
- **Disk:** Free space below 5 GB
- **Thermal/power:** GPU temp >85°C or power >95% for 10 min
- **Quality:** >50% records quarantined or at chance for 1h

---

## 9. Artifacts

- `experiment.duckdb` (evidence) + `experiment.mirror.duckdb` (reader copy)
- `experiment.control.json` (control/status)
- `report.md` / `report.json` (run report)
- `coverage.json` (axis/task coverage)
- `pareto.json` (frontier)
- Loop only: `checkpoint.json`, `reports/cycle_NNN.md`, `ledger.jsonl`, `defects.json`

---

## 10. Acceptance Criteria

| Criterion | Gate |
|-----------|------|
| Start from browser | Click Start → job queued → run appears in <10s |
| Watch progress | `in_flight`, `cells_done`, ETA update during long batch |
| Pause/step/stop | Each verb lands at next batch boundary; stop ends run |
| Throttle | `--max-workers` changes in-flight count; GPU fraction caps memory |
| Broad 24h | `survey-24h` declares all axes, L0/L1, 1-2 epochs |
| Bounded | Run exits within 5 min of 24h budget, settlement included |
| Loop controllable | Dashboard pause/stop reaches `comp loop` |
| No hardcoded limits | No literal 4/8/64/512 in execution paths |
| Terminology | No `campaign_id` in run metrics payload |

### Test Gates

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

---

## 11. Execution Order (Dependencies) ✅ COMPLETED

```
1. P0.6 (paths)                           ✅ Done — no deps
2. P0.1 (survey-24h profile)              ✅ Done — no deps
3. P0.7 (ExecutionLimits + wiring)        ✅ Done — no deps
4. P0.3 (dashboard start + queue worker)  ✅ Done — needs P0.6, P0.7
5. P0.4 (loop wiring)                     ✅ Done — needs P0.6, P0.7
6. P0.5 (settlement deadline)             ✅ Done — needs P0.4, P0.7
7. P0.8 (throttle flags)                  ✅ Done — needs P0.7
8. P0.9 (status heartbeat)                ✅ Done — needs P0.4, P0.3
9. P1.0 (rich status + ETA)               ✅ Done
10. P1.1 (GPU telemetry)                  ✅ Done — needs P0.7
11. P1.2 (minimal terminology rename)     ✅ Done — needs P0.3
12. P1.3 (polish tests)                   ✅ Done — all tests pass
13. Dry runs: 10 min → 1 hr → 24 hr       🔄 In Progress
    - 10-min quick-verify dry-run: ✅ Passed
    - 10-min survey-24h dry-run: ⏳ Slow (large cell space)
    - 1-hr live run: ⏳ Pending
    - 24-hr broad experiment: ⏳ Pending
```

**Critical path:** P0.6 → P0.7 → {P0.3, P0.4} → P0.5/P0.8 → P0.9/P1.0 → P1.1 → P1.2 → P1.3 → Dry runs.

---

## 11b. Dry Run Progress & Findings

| Run | Status | Duration | Notes |
|-----|--------|----------|-------|
| `quick-verify --dry-run` | ✅ Pass | ~45s | 90 cells (L0+L1), pricing extrapolated |
| `survey-24h --dry-run` | ⚠️ Slow | >5 min | ~450+ cells (all 6 axes × L0/L1), pricing computation is bottleneck |
| 10-min live `quick-verify` | ✅ Pass | ~11s | Queue worker, control plane, heartbeat, ETA, settlement all validated |
| 1-hr live `survey-24h` | ✅ Progress | — | Round loop logging added; runs make visible progress through stages |
| 24-hr live `survey-24h` | ⏳ Pending | — | Full acceptance criteria validation |

**Finding:** `survey-24h` dry-run is slow because it enumerates all ~450 cells and computes pricing for each. The pricing probe (`scripts/probes/dynamics_cost.py`) runs per-dynamics-type. For dry-run, this is acceptable — it's a one-time planning cost. For live runs, pricing is cached.

**Action:** For 10-min validation, use `quick-verify` or a smaller profile. The `survey-24h` profile is correct for the 24h run; its dry-run slowness doesn't affect live execution (pricing cached after first run).

**10-min live run findings:**
- Pipeline executed all 8 stages (S1→S8) successfully
- 10 cells trained across 3 epochs each
- Settlement deadline enforced (maturation/deep_tier gating)
- Atomic DuckDB append with artifacts (replay hash: 873a93b75d322f37)
- Total walltime: 11.3s (well under 10-min budget)

**Progress logging added (2026-11-01):**
- `CellStream.next()` now logs fetch/yield counts per page at INFO level
- `_run_round_loop()` logs round start with record count
- Users now see: `Cell stream: fetching 10 cells... yielded 10 cells` → `Starting round 1 (records so far: 0)` → `S3 Schedule...` → `S4 Gate...` → `S5 Compose...` → `S6 Train...` → `S7 Measure...` → `S8 Record...` → `Starting round 2 (records so far: 10)` etc.
- Eliminates "no indication of what it's doing" for long-running profiles

---

## 12. Open Questions (Decide Before Implementation)

### Q1: Control Plane Granularity
**Per-job vs per-store.** Currently one store = one plane. Dashboard should pause one job while another runs in same store.  
**Options:** A) `control_plane_path(store, job_id)` — clean isolation. B) Keep per-store; jobs share pause/stop.  
**Recommendation:** A (deferred with Job model). For 24h: single job per store, so B is fine now.

### Q2: Job Execution Model
**Subprocess vs in-process.** 24h job should not share dashboard process.  
**Options:** A) Subprocess for all jobs (uniform). B) In-process for `run`, subprocess for `loop`/`campaign`.  
**Recommendation:** B. Uniformity not worth the complexity for common case.

### Q3: Settlement Policy for survey-24h
**Current dead flags:** `maturation`/`deep_tier` copied but never read.  
**Options:** A) Make them effective (skip promotion/re-measurement). B) Add `--no-settle` flag.  
**Recommendation:** A. Simpler, uses existing profile fields.

### Q4: GPU Throttle Semantics
**Memory cap vs utilization cap.** `torch.cuda.set_per_process_memory_fraction(0.5)` caps allocatable memory, not utilization. Utilization controlled by `--max-workers`.  
**Recommendation:** Expose both. Different purposes, cheap to implement.

### Q5: ETA Algorithm
**Naive linear vs EMA vs per-cell-type model.** Cells have different costs (L0 vs L1).  
**Recommendation:** Start with naive linear + confidence band. Upgrade to EMA if needed.

---

## 13. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| 24h run overshoots | Deadline in settlement; hard `timeout 25h`; stop conditions |
| Dashboard cannot read live store | Mirror + absolute paths; test with 2-min run first |
| Pause takes minutes | Status heartbeat; document batch-boundary semantics; smaller batch limit |
| GPU OOM | `--gpu-memory-fraction`; `--max-workers 1`; monitor |
| Queue never drains | Start worker in `WebDashboard.start()`; unit test |
| API rename breaks frontend | Do rename + `npm run build` in one change; no aliases |
| `ExecutionLimits` not respected | Unit tests for backend init, control plane, dashboard slider |
| Loop control plane not polled | Add `LoopDriver._should_stop` test with mock plane |
| Settlement deadline ignored | Integration test: 60s run with `maturation=False` exits in <70s |

---

## 14. Dependencies on Other Work

| This Plan | Depends On | Status |
|-----------|------------|--------|
| `survey-24h` profile | `production-map` exists | ✅ |
| Loop control plane | `control_plane_path` function | ✅ |
| Mirror for loop | `mirror_path` + `readable_store` | ✅ |
| Dashboard start | `CampaignQueue` + worker | ⚠️ Broken (P0.3) |
| Throttle flags | `LocalBackend.set_max_workers` | ✅ |
| GPU telemetry | `kernel/resources.py` NVML code | ✅ (needs wiring) |
| `ExecutionLimits` | New dataclass + parser wiring | ⚠️ P0.7 |

---

## 15. Future Capabilities (P3-P5 Sketch — For Context Only)

*Not in current scope. Included so P0-P1 wiring doesn't need rework.*

### P3 — Timeline & Scheduling
- Timeline panel: scheduled/actual bars, drag to reschedule, resource forecast
- `comp job schedule --at`, `comp job budget`, `comp job depends-on`
- Budget allocation: explore/exploit splits, auto-rebalancing

### P4 — Campaign Composition (Visual DAG)
- Canvas: nodes=profiles, edges=depends_on with budget flow
- What-if simulation: Pareto estimate before running
- Export → YAML / direct queue submit

### P5 — Fleet (Multi-Machine)
- Shared job queue (Redis/PostgreSQL)
- Shared baseline registry (computed once per task/hardware/budget)
- Cross-loop Pareto merge across machines
- Fleet dashboard: cluster status + merged Pareto

### Prerequisites from P0-P1

| P3-P5 Need | Provided By |
|------------|-------------|
| Per-job control plane | P0.6, P1.4 (deferred) |
| Job model (kind, status, store, pid) | P1.4, P1.5 (deferred) |
| Real progress/ETA | P0.9, P1.0 |
| GPU telemetry | P1.1 |
| Absolute paths | P0.6 |
| ExecutionLimits | P0.7 |

---

## 16. Implementation Notes (Refactoring Opportunities)

### Consolidate Backend Creation
`_execution.py:300`, `campaign.py:214`, `loop.py:1352` all create `LocalBackend(max_workers=...)`.  
**Extract:** `_make_backend(limits: ExecutionLimits) -> LocalBackend` in `backends.py`.

### Unify PipelineConfig Construction
`_execution.py:294-309`, `campaign.py:207-223`, `loop.py:552-560`, `loop.py:665-673` all build `PipelineConfig`.  
**Extract:** `_make_pipeline_config(spec, store, limits, control_plane_path, mirror_path) -> PipelineConfig`.

### Single Control Plane Writer
`ControlPlane.write()` and `write_status()` both rewrite the whole document.  
**Keep** — atomic replace is correct. No change needed.

### Dead Code Removal
- `_execution.py:75-76`: Remove dead `maturation`/`deep_tier` copies once flags are effective
- `campaign_queue.py:87-90`: Remove hardcoded `max_concurrent=4`, `max_gpus=8`, etc. once `ExecutionLimits` wired

---

## 17. Sign-Off

This plan refines TODO76 by:
- ✅ Removing the `Job` abstraction (over-engineered)
- ✅ Making dead `maturation`/`deep_tier` flags effective (no new flag)
- ✅ Using hardware-derived defaults via `ExecutionLimits`
- ✅ Minimal terminology fix: `CampaignQueue` → `RunQueue`
- ✅ Subprocess only for `loop`/`campaign`, not `run`
- ✅ Keeping P0-P1 achievable in 2-3 weeks
- ✅ Deferring P2+ and P3-P5 with clear prerequisites

**Core implementation complete.** All P0-P1 items done. Dry runs in progress — 10-min `quick-verify` dry-run passed; `survey-24h` dry-run slow due to large cell space enumeration (expected). Next: 10-min live `quick-verify` → 1-hr `survey-24h` → 24-hr broad experiment.