# TODO30 — Mission Control: Autonomous Discovery Telemetry & Operational Dashboard

> **STATUS: DRAFT (2026-09-17).** Supersedes TODO29 Phase 6. Defines the final
> architecture for the continuous discovery system's operational interface.
>
> **Design Principle:** The AutoScientist is autonomous. The dashboard is a
> telemetry window, not a control surface for the science. The only human
> controls are operational lifecycle: **Run, Pause, Stop**. Everything else
> is observation.

---

## 0. Philosophy

Computronium's discovery loop must be smart enough to run unattended. If the
dashboard requires a scientist to steer, ban, fork, or intervene to produce
good results, the AutoScientist has failed—not the dashboard.

The dashboard's role is therefore:

1. **Prove liveness.** A scientist glancing at the screen must know within one
   second whether the system is working, sleeping, or dead.
2. **Show the work.** Expose what the system is doing *right now*—which cell,
   which axis combination, how far along, at what cost.
3. **Reveal the landscape.** Show what has been learned so far: coverage,
   Pareto evolution, negative results, diversity health.
4. **Alert on significance.** Notify the scientist only when something
   warrants human attention (breakthrough, cascade failure, diversity
   collapse).

No steering. No lasso. No fork/mutate. No interactive probes. The scientist
sets the campaign constraints at launch and walks away. The dashboard tells
them when to come back.

---

## 1. Architecture

```
comp daemon (headless, autonomous)          comp dashboard (read-only + lifecycle)
        │                                           │
        ▼                                           ▼
  ContinuousDaemon ◄── WebSocket/REST ──►     Control Room UI
  (state machine, sweep, CEEC,                (telemetry, charts,
   defect funnel, KB, budget)                  alerts, coverage)
        │
        ▼
  artifacts/<root>/
    kb.sqlite, ledger.sqlite,
    structural_voids.jsonl,
    runtime_defects.jsonl,
    heartbeat.json,
    maturation.jsonl
```

### 1.1 Separation of Concerns

| Component | Responsibility |
|---|---|
| `comp daemon` | Headless execution engine. Owns the sweep, CEEC ledger, defect funnel, budget enforcement, and KB. Exposes a WebSocket/REST API for telemetry and lifecycle commands. Survives UI disconnects. |
| `comp dashboard` | Read-only telemetry client with three lifecycle buttons (Run/Pause/Stop). Connects to the daemon via API. Renders live state, historical analysis, and alerts. Never modifies the search strategy. |
| `artifacts/<root>/` | Persistent state. Both daemon and dashboard read/write through this directory. The dashboard may read but never writes campaign data. |

### 1.2 Daemon State Machine

```
IDLE ──► PROPOSING ──► TRAINING ──► (loop) ──► SLEEPING ──► PROPOSING
  │            │              │                       │
  ◄────────────┴──────────────┴───────────────────────┘  (on PAUSE/STOP)
```

| State | Meaning |
|---|---|
| `IDLE` | Daemon initialized, awaiting start command. |
| `PROPOSING` | Generating next batch of coordinates via `StratifiedRandomDriver`. |
| `TRAINING` | Executing `SystemTrainer.fit()` on the current cell. |
| `SLEEPING` | Inter-burst cooldown (`--sleep N`). Interruptible via "Skip Sleep." |
| `PAUSED` | In-flight cell finishes; no new cells proposed. Daemon holds state. |
| `STOPPED` | Graceful shutdown. KB flushed, CEEC traces closed, checkpoint saved. |
| `HALTED` | Emergency stop. In-flight training aborted. State flushed. |

### 1.3 API Surface

| Endpoint | Method | Purpose |
|---|---|---|
| `/control/start` | POST | Transition IDLE → PROPOSING. |
| `/control/pause` | POST | Finish in-flight cell, then PAUSED. |
| `/control/resume` | POST | PAUSED → PROPOSING. |
| `/control/stop` | POST | Graceful STOP after in-flight cell. |
| `/control/halt` | POST | Emergency HALT. Abort immediately. |
| `/control/skip_sleep` | POST | Cancel current SLEEP, go to PROPOSING. |
| `/state` | GET | Full daemon state: PID, current cell, burst ID, progress, uptime. |
| `/ws/telemetry` | WS | Streaming per-step metrics for the active cell. |
| `/ws/events` | WS | Structured lifecycle events (cell_completed, defect_quarantined, burst_started). |
| `/history` | GET | Paginated KB query: cells, metrics, tags, maturity. |
| `/coverage` | GET | Viable cells total, measured, voids, defects, coverage %. |
| `/pareto` | GET | Current Pareto front + historical snapshots per burst. |
| `/costs` | GET | Per-axis walltime breakdown, projections, budget remaining. |
| `/diversity` | GET | Proposal entropy over last N bursts, stratum coverage. |

---

## 2. Phase 1 — Operational Controls (The Only Buttons)

### 2.1 Lifecycle Control Bar

A single, persistent bar at the top of the dashboard. Three states, three
buttons:

| Daemon State | Visible Buttons | Appearance |
|---|---|---|
| `IDLE` / `STOPPED` | **[▶ Start]** | Green. "Daemon ready. No campaign active." |
| `PROPOSING` / `TRAINING` / `SLEEPING` | **[⏸ Pause]** **[⏹ Stop]** | Pulsing green badge: "ACTIVE — Burst 14, Cell 12/50." |
| `PAUSED` | **[▶ Resume]** **[⏹ Stop]** | Yellow badge: "PAUSED — awaiting resume." |

No other controls. No parameter sliders. No search modifications. The
campaign configuration is set at launch via CLI flags and is immutable
during execution.

### 2.2 Liveness Indicator

A large, unmissable status badge that updates every poll cycle:

| Condition | Badge | Color |
|---|---|---|
| Heartbeat fresh (< 10s) and state active | `● RUNNING` | Green, pulsing |
| Heartbeat fresh, state sleeping | `● SLEEPING (12s remaining)` | Yellow |
| Heartbeat fresh, state paused | `● PAUSED` | Amber |
| Heartbeat stale (> 10s) | `● CONNECTION LOST` | Red |
| No heartbeat file / daemon unreachable | `● OFFLINE` | Grey |

The badge includes: PID, uptime, node hostname, and current operation
(e.g., "Training: `S:Digital × G:Recurrent × D:EnergyMin × C:Thermo × U:Muon`").

### 2.3 Graceful Shutdown Contract

When **Stop** is pressed:
1. In-flight cell completes (or is abandoned after `--halt-timeout`).
2. KB is flushed.
3. CEEC traces are closed (`record` or `record_failure`).
4. Checkpoint is saved.
5. Daemon transitions to `STOPPED` and remains reachable for queries.
6. Dashboard shows final summary: cells measured, defects, voids, uptime.

---

## 3. Phase 2 — Live Telemetry (The Work Itself)

### 3.1 Active Cell Inspector

When the daemon is in `TRAINING`, a dedicated panel shows:

| Element | Content |
|---|---|
| **Coordinate Card** | Full 6-axis string + hyperparameters. |
| **Proposal Rationale** | Why this cell was selected (e.g., "Balancing under-sampled triple: Diffusion × STDP × Muon. Stratum count: 2/5 target."). |
| **Live Loss Curve** | Per-batch `train_loss` and `val_loss`, streaming via WebSocket. |
| **Settling Trace** | Lyapunov energy descent per settle step (for `EnergyMinimization` / `PredictiveSettling` dynamics). |
| **Progress Bar** | Batch `42 / 150` (respects `--limit-batches`). Estimated time remaining for this cell. |
| **Resource Gauges** | CPU%, RAM, GPU VRAM/utilization of the daemon process (via `psutil` on the heartbeat PID). |

### 3.2 Structured Event Stream

Replaces the raw log ticker. The daemon emits typed events via `/ws/events`:

```
[14:02:01] 🚀 Burst 14 started (target: 50 cells)
[14:02:03] 🧠 Proposed 50 cells | 3 quarantined | 12 voids pruned
[14:02:04] ⚙️  Training: Digital × Recurrent × EqProp × Null × Thermo × Muon
[14:02:18] ✅  Completed: acc=0.942 | loss=0.187 | walltime=14.2s
[14:02:19] ⚠️  Defect: Shape mismatch in FA feedback (id: a3f2c1). Cell quarantined.
[14:02:20] ⚙️  Training: Memristive × TileMesh × EqProp × Null × Thermo × Euclidean
```

Color-coded by type. Scrollable. Filterable by severity. The last 30 events
are visible by default.

### 3.3 Per-Cell Outcome Badges

Every completed cell in the event stream gets an immediate visual badge:

| Badge | Meaning |
|---|---|
| 🟢 `LEARNED` | val_acc > threshold (task-specific, e.g., > 0.5 for MNIST). |
| 🟡 `MARGINAL` | val_acc between chance and threshold. |
| 🔴 `DIVERGED` | `nan_loss` flag set. |
| ⚫ `DEFECT` | Runtime crash. Quarantined. |
| ⬜ `VOID` | Gate-rejected before execution. |

---

## 4. Phase 3 — Landscape Awareness (What Has Been Learned)

### 4.1 Coverage Dashboard

A persistent panel answering: *"How much of the space have we explored?"*

| Metric | Visualization |
|---|---|
| Viable cells total | Number (from `enumerate_constraint_voids`). |
| Cells measured | Number + percentage of viable total. |
| Structural voids | Count, categorized by rejection reason. |
| Runtime defects | Open / resolved count. |
| Coverage by axis | Parallel-coordinates heatmap: each axis (S, G, D, P, C, U) colored by sample count. Instantly reveals under-sampled primitives. |
| Stratum coverage | Histogram of triple (D, C, U) coverage: how many triples have ≥1, ≥3, ≥5 cells. |

### 4.2 Pareto Evolution

The Pareto front is not static—it evolves over bursts.

| Element | Content |
|---|---|
| **Current Front** | Scatter: accuracy vs. walltime (or accuracy vs. 1−deficit). Top-3 cells labeled. |
| **Front History** | Small-multiples: the front at burst 1, 5, 10, 14. Shows whether discovery is progressing or plateaued. |
| **Breakthrough Markers** | Any cell that expanded the front is highlighted with a ★ and a timestamp. |

### 4.3 Negative Results Panel (The Graveyard)

Science is mostly failure. Make it visible.

| Section | Content |
|---|---|
| **Diverged Cells** | List of `nan_loss` cells with their coordinates. Grouped by axis primitive to reveal patterns (e.g., "80% of diverged cells use `PhotonicSubstrate`"). |
| **Chance-Level Cells** | Cells that trained successfully but achieved ≤ chance accuracy. |
| **Defect Clusters** | Grouped by `defect_id`: count, affected cells, error message. The bug-bounty board. |
| **Structural Voids Summary** | Why combinations are impossible (ontology constraints). Not failures—boundaries. |

### 4.4 Diversity Monitor

Detects premature convergence of the search.

| Metric | Alert Threshold |
|---|---|
| Proposal entropy (last 3 bursts) | < 0.5 × max entropy → ⚠️ "Search narrowing." |
| Stratum repeat rate | > 80% of recent cells in previously-sampled strata → ⚠️ "Exploration declining." |
| Novel-cell rate | < 10% of a burst is novel → ⚠️ "Mostly re-measuring known space." |

These are **alerts only**. The dashboard does not intervene. If the
AutoScientist collapses, that is a finding about the search strategy, not a
problem for the human to fix mid-run.

---

## 5. Phase 4 — Cost Awareness

### 5.1 Projection Bar

Always visible in the header:

```
Measured: 342 / 500 (68%) | Elapsed: 2h 14m | Projected remaining: 1h 03m
Mean walltime/cell: 12.4s | This burst: 8.7s avg | Budget: ∞ (loop mode)
```

### 5.2 Per-Axis Cost Breakdown

A horizontal bar chart showing mean walltime per primitive:

```
EnergyMinimization   ████████████████████  34.2s
PredictiveSettling   ███████████████       22.1s
SpikeIntegration     ████████              11.3s
InstantaneousPass    ██                     2.8s
```

And per credit assignment:

```
ThermodynamicContrast ██████████████████  28.4s
LocalGoodness         ████                  5.2s
RandomProjections     ███                   4.1s
BackpropCredit        ██                    3.0s
```

This makes the cost of physics-based learning visible and quantifiable.

### 5.3 Burst-Level Cost Summary

After each burst completes, log a one-line summary:

```
Burst 14: 50 cells | 47 measured | 3 defects | walltime 8m 32s | mean 10.9s/cell
```

Displayed in the event stream and aggregated in a cost-over-time line chart.

---

## 6. Phase 5 — Alerting & Asynchronous Notification

### 6.1 Breakthrough Alerts

When a cell expands the Pareto front by more than a configurable threshold
(default: 2% improvement over the previous best on any objective):

- 🟢 Toast notification in the dashboard.
- Optional webhook (Slack, Discord, email) with:
  - Coordinate string
  - Metrics (accuracy, walltime, deficit)
  - Link to dashboard cell view
  - CEEC ledger entry ID

### 6.2 Cascade Failure Alerts

If > 30% of a burst results in defects or divergences:

- 🔴 Toast notification.
- Webhook: *"⚠️ Cascade failure in Burst 14: 18/50 cells failed. Top defect: `a3f2c1` (shape mismatch). Consider halting."*

The dashboard does **not** auto-halt. The human decides.

### 6.3 Completion Alerts

When `--target-cells` is reached or budget expires:

- 🏁 Toast: *"Campaign complete: 500 cells measured in 6h 12m. Pareto front: 14 cells. Report ready."*

---

## 7. Phase 6 — Historical Analysis & Reporting

### 7.1 Cell Detail View

Click any cell in the history table to see:

| Field | Content |
|---|---|
| Full coordinate | 6-axis string + hyperparameters. |
| Metrics | train_loss, val_loss, val_acc, walltime_s, param_count. |
| Instruments | settle_horizon, σ_max proxy, credit_alignment (if measured). |
| Tags | `maturity:l0`, `burst:2026-09-17-003`, `nan_loss` (if applicable). |
| Provenance | Campaign ID, iteration, CEEC experiment ID, seed. |
| Training Curve | Static replay of the loss/accuracy trajectory. |
| Settling Trace | Static replay of energy descent (if applicable). |

### 7.2 Maturation Status

| Tag | Meaning | Count |
|---|---|---|
| `maturity:l0` | Mapping fidelity. 1 epoch, 1 seed. | N |
| `maturity:l1` | Promoted. 3 epochs. | N |
| `maturity:l2` | Claim-grade. 10 epochs, 3 seeds. | N |

The dashboard shows counts and allows filtering by maturity. Only `l2` cells
may back comparative claims (per CEEC governance).

### 7.3 Campaign Summary Report

A **Generate Report** button (read-only assembly, not intervention) that
produces a Markdown document:

- Campaign configuration (axes, constraints, budget, task).
- Total cells measured, defects, voids.
- Final Pareto front (table + scatter).
- Top-10 cells by accuracy.
- Negative results summary (top failure modes).
- Cost breakdown.
- CEEC ledger rollup (experiments, beliefs, gates).
- Verification levels achieved.

This is the artifact a scientist takes to a paper or a review.

---

## 8. Implementation Plan

| Phase | Deliverable | Key Files |
|---|---|---|
| **8.1** | Daemon extraction: `ContinuousDaemon` class with state machine, API server (FastAPI + WebSocket). Headless, survives UI disconnect. | `computronium/autoscientist/daemon.py` |
| **8.2** | Telemetry streaming: hook `SystemTrainer` callbacks to emit per-step metrics to an async queue → WebSocket. | `computronium/core/system_trainer/trainer.py` (callback hooks) |
| **8.3** | Control Room UI: lifecycle bar, liveness badge, active cell inspector, event stream. | `computronium/visualization/mission_control.py` |
| **8.4** | Landscape panels: coverage, Pareto evolution, graveyard, diversity monitor. | `computronium/visualization/landscape.py` |
| **8.5** | Cost module: per-axis walltime aggregation, projections, burst summaries. | `computronium/autoscientist/cost_model.py` |
| **8.6** | Alerting: breakthrough detection, cascade failure, completion. Webhook dispatch. | `computronium/autoscientist/alerts.py` |
| **8.7** | Historical analysis: cell detail view, maturation table, report generation. | `computronium/visualization/history.py` |
| **8.8** | CLI integration: `comp daemon` replaces `comp continuous` as the primary entry point. `comp dashboard` connects. | `computronium/cli/daemon.py`, `computronium/cli/dashboard.py` |

### Testing

| Gate | Test |
|---|---|
| Daemon lifecycle | Start → propose → train → pause → resume → stop. State transitions verified. |
| Telemetry integrity | WebSocket stream matches KB-recorded final metrics within tolerance. |
| UI liveness | Kill daemon process → dashboard shows `CONNECTION LOST` within 12s. |
| Graceful stop | Stop mid-burst → KB flushed, CEEC closed, checkpoint saved. |
| Emergency halt | Halt mid-training → no partial KB write, no dangling CEEC trace. |
| Cost accuracy | Projected remaining time within 20% of actual over a 50-cell run. |
| Alert correctness | Inject a Pareto-breaking cell → breakthrough alert fires. Inject 20 defects → cascade alert fires. |

---

## 9. What This Dashboard Is Not

| Not | Why |
|---|---|
| A steering wheel | The AutoScientist's search strategy is configured at launch. Human mid-run steering defeats the purpose of autonomous discovery. |
| A hyperparameter tuner | HPO is `comp hpo`. This is a discovery loop, not an optimizer. |
| An interactive debugger | If a cell needs manual probing, the scientist reproduces it offline via `comp lab` or a notebook. The daemon runs unattended. |
| A collaboration tool | Single-operator telemetry. Multi-user annotation is out of scope. |
| A campaign designer | Campaign configuration is CLI-driven (`comp daemon --config campaign.yaml`). The dashboard does not edit configs. |

---

## 10. Success Criteria

The dashboard is complete when a scientist can:

1. **Launch** a campaign with a single CLI command and walk away.
2. **Glance** at the dashboard from across the room and know: is it alive,
   what is it doing, how far along, at what cost.
3. **Sit down** and understand: what has been discovered, what has failed,
   what remains unexplored, whether the search is healthy.
4. **Receive an alert** on their phone when something significant happens.
5. **Generate a report** when the campaign completes, ready for review.
6. **Never need to open a terminal** during the campaign's lifetime.

If any of these require SSH-ing into the machine, reading raw logs, or
running a script—the dashboard is incomplete.

---

## 11. Migration Path

| Existing | Becomes |
|---|---|
| `comp continuous` | `comp daemon` (same flags, adds `--port` for the API server). Legacy alias preserved for one release. |
| `comp dashboard` | Rewritten as the Mission Control client. Connects to daemon API. |
| `comp continuous unquarantine` | Retained as a maintenance CLI command (not a dashboard feature). |
| `comp continuous deep-tier` | Retained as a maintenance CLI command. |
| `scripts/broad_mapping_sweep.py` | Deprecated. Superseded by `comp daemon`. |

---

## 12. Epistemic Rules (Unchanged)

1. **Voids ≠ defects.** Gate rejections are ontology boundaries. Runtime crashes are implementation failures. Neither is a measurement.
2. **Maturity gates claims.** `l0` maps the space. Only `l2` (multi-seed, cross-burst) backs a comparative claim.
3. **Instruments stay honest.** σ_max proxy is never labeled ρ(J_F). Sampled numerical is Level 4, never Level 1–3.
4. **The ledger only sees gate-passing cells.** The daemon adds no new CEEC pathways.
5. **The dashboard never writes to the KB or ledger.** It is a read-only observer with lifecycle authority only.

---

## 13. Immediate Next Actions

1. **Extract `ContinuousDaemon`** from `run_burst` with the state machine and API server.
2. **Wire telemetry hooks** into `SystemTrainer.fit()` (per-batch callback → async queue → WebSocket).
3. **Build the Lifecycle Control Bar** and Liveness Badge in the dashboard.
4. **Run the 500-cell shakedown** through the new daemon. Watch it on the dashboard. Verify: no terminal needed for the full run.
5. **Implement the Graveyard and Diversity Monitor** panels from the shakedown data.
6. **Wire breakthrough and cascade alerts.**
7. **Generate the first campaign summary report** from the completed 500-cell run.

