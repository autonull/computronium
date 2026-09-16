# TODO30 — Mission Control: Autonomous Discovery Telemetry & Operational Dashboard

> **STATUS: DRAFT rev 2 (2026-09-16).** Supersedes TODO29 Phases 1–5, which
> are **landed and verified** (library extraction, defect funnel, budgeted
> bursts, maturation, live window — see TODO29 §13). This revision absorbs
> TODO29's remaining work (§8 shakedown launch, §12 follow-ups, §13 session
> findings) and corrects the rev-1 plan against the codebase as it actually
> stands.
>
> **PROGRESS (2026-09-16).** Landed: **8.1** `ContinuousDaemon`
> (`computronium/autoscientist/daemon.py`) — full §1.2 state machine
> (IDLE/PROPOSING/TRAINING/SLEEPING/PAUSED/STOPPED), heartbeat.json writer
> (~2 s + on every transition), exclusive `<root>/continuous.lock`
> (O_EXCL; second daemon exits non-zero — TODO29 §12.5 absorbed),
> FastAPI surface for `/control/*` + `/state` + `/ws/telemetry` +
> `/ws/events`, drop-oldest `TelemetryBridge` (thread→asyncio,
> best-effort per §12.6), boundary-based pause/stop via a new
> `run_burst(gate=...)` hook, PROPOSING/TRAINING phase observation via
> `PhaseTrackingDriver` (driver wrapper; `run_burst` now takes a
> `BurstDriver` protocol). **8.2** landed: optional default-no-op
> `step_callback` on `SystemTrainer` (one `None` check on the hot path),
> forwarded by `AutoScientistCampaign.step_callback`; verified
> loss-identical with/without callback. **8.9** landed: `comp daemon`
> (shared flags via `_add_common_flags`, adds `--port`, default 8940);
> `comp continuous` stays as the legacy alias; budget construction
> consolidated into `broad_map.budget_from_args`. Tests:
> `tests/property/test_daemon_state.py` (lifecycle, boundary pause/stop,
> lockfile, heartbeat, REST controls, bridge drop-oldest, hook isolation).
> **8.3** landed: `liveness()` + `lifecycle_buttons()` + `DaemonClient`
> (urllib, 1 s timeout, never errors) in `live_atlas.py`; the Lifecycle
> Control Bar + Liveness Badge render inside `build_dashboard` when
> `--daemon-url` is passed to `comp dashboard` (poll-only stub otherwise).
> Dual-source badge per §2.2: fresh heartbeat drives the state even when
> the API is unreachable (artifact-polling degradation note in the badge
> detail); stale heartbeat → CONNECTION LOST; no file → OFFLINE. Tests:
> `tests/unit/test_live_atlas_liveness.py` (badge matrix, button table,
> unreachable-degradation, and a live-uvicorn REST round-trip).
> **8.4** landed: `StratifiedRandomDriver.propose_batch` now fills
> `justification` with the per-cell reason ("Balancing under-sampled triple
> D × C × U — stratum count N before this proposal; topology T drawn
> uniformly"). **8.5** landed: headless data functions in `live_atlas.py` —
> `coverage_by_axis`, `stratum_coverage`, `front_history_rows` (accuracy↑ /
> walltime↓ front at sampled burst cutoffs, ★ = front expansion shared with
> the §6.1 derivation), `graveyard_rows` (NaN cells grouped per axis
> primitive with divergence share), `void_summary_rows` (by rejection
> category), `diversity_stats` + `diversity_alerts` (§4.4 thresholds:
> novelty <10%, stratum repeat >80%, quarantine >20%) — all rendered as
> additive panels in `build_dashboard` via `DashboardSnapshot` (new fields
> default-empty, so the atlas-swap path is untouched). Tests:
> `tests/integration/test_dashboard_smoke.py::test_landscape_panels_headless`
> + `test_diversity_alerts_thresholds`.
> **8.7** landed: `computronium/autoscientist/alerts.py` (strict) —
> `breakthrough_alert` (≥2% accuracy margin over the KB best),
> `cascade_alert` (>30% of a burst's executed cells failed; suggests
> halting, never auto-halts), `completion_alert` (on
> `stop_reason == "target"`, human-readable elapsed time), and a
> best-effort `WebhookDispatcher` (Slack/Discord-style JSON, never
> raises). The daemon checks alerts after every burst (§6: daemon-side so
> they fire with no browser attached), publishes `{kind: "alert",
> alert_kind, title, body}` on `/ws/events` for dashboard toasts, and
> dispatches webhooks when `comp daemon --alert-webhook URL` is set.
> Tests: `tests/property/test_alerts.py` (threshold matrices, webhook
> post-capture + error swallowing).
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

**Transport reality (rev-2 correction).** The existing `comp dashboard`
(`computronium/visualization/live_atlas.py`) polls campaign artifacts on an
`(mtime, size)` signature and re-renders on change only. That design is
already daemon-crash-safe by construction: when the daemon dies, the
artifacts (and therefore the landscape panels) keep rendering. A pure
WebSocket client cannot make that claim. This revision therefore mandates a
**hybrid transport**:

| Panel family | Transport | Rationale |
|---|---|---|
| Landscape (coverage, Pareto, graveyard, costs, health) | Artifact polling (existing `DashboardSnapshot` pattern) | Read path already shipped and tested headless; survives daemon death |
| Live per-step telemetry (loss curve, settling trace) | WebSocket from the daemon | Only the daemon has this data |
| Lifecycle commands | REST to the daemon | Pull-based control |

The dashboard never depends on the WebSocket being up to show what has been
learned—only to show what is happening *right now*.

---

## 1. Architecture

```
comp daemon (headless, autonomous)           comp dashboard (read-only + lifecycle)
        │                                     ├─ polls artifacts/<root>/ (landscape)
        ▼                                     └─ REST + WebSocket (lifecycle, live)
  ContinuousDaemon ──uses──► run_burst()
  (state machine,                ├─► BroadMappingCampaign (dry-run gate, CEEC,
   budget, API)                  │    instruments, resume, defect funnel)
        │                        └─► StratifiedRandomDriver (quarantine-aware)
        ▼
  artifacts/<root>/
    kb.sqlite, ledger.sqlite,
    structural_voids.jsonl,
    runtime_defects.jsonl,
    heartbeat.json          (new — daemon-written liveness beacon)
    maturation.jsonl
```

### 1.1 Separation of Concerns

| Component | Responsibility |
|---|---|
| `comp daemon` | Headless execution engine. Owns the sweep, CEEC ledger, defect funnel, budget enforcement, and KB. Exposes a WebSocket/REST API for telemetry and lifecycle commands. Survives UI disconnects. Writes `heartbeat.json` every ~2 s. |
| `comp dashboard` | Read-only telemetry client with three lifecycle buttons (Run/Pause/Stop). Polls artifacts for landscape panels; connects to the daemon API for liveness and live telemetry. Never modifies the search strategy. |
| `artifacts/<root>/` | Persistent state. The daemon writes; the dashboard reads. Every daemon crash leaves the artifacts consistent—landscape panels are re-derivable from disk alone. |

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

**Rev-2 correction: no `HALTED` mid-training state.** `fit()` is a
synchronous loop; hard-cancelling it mid-flight risks exactly the partial
KB write / dangling CEEC trace that the testing gates forbid. All stop
semantics are boundary-based, matching `run_burst`'s existing budget
discipline (checks at proposal boundaries only; a soft stop loses at most
the in-flight cell's compute, never corrupts state):

| Command | Semantics |
|---|---|
| Pause | Finish in-flight **cell**, then hold. |
| Stop | Finish in-flight cell → flush → checkpoint → `STOPPED`. |
| Halt (CLI-only, not a dashboard button) | Abandon at the next **epoch boundary** inside `fit()` via a checked flag, then flush. No dashboard exposure—emergency stops are `kill -TERM`, which already routes through the uniform `_install_sigterm()` graceful path. |

### 1.3 API Surface

| Endpoint | Method | Purpose |
|---|---|---|
| `/control/start` | POST | Transition IDLE → PROPOSING. |
| `/control/pause` | POST | Finish in-flight cell, then PAUSED. |
| `/control/resume` | POST | PAUSED → PROPOSING. |
| `/control/stop` | POST | Graceful STOP after in-flight cell. |
| `/control/skip_sleep` | POST | Cancel current SLEEP, go to PROPOSING. |
| `/state` | GET | Full daemon state: PID, current cell, burst ID, progress, uptime. |
| `/ws/telemetry` | WS | Streaming per-step metrics for the active cell (see §3.1). |
| `/ws/events` | WS | Structured lifecycle events (cell_completed, defect_quarantined, burst_started). |
| `/history` | GET | Paginated KB query: cells, metrics, tags, maturity. |
| `/coverage` | GET | Viable cells total, measured, voids, defects, coverage %. |
| `/pareto` | GET | Current Pareto front + historical snapshots per burst. |
| `/costs` | GET | Per-axis walltime breakdown, projections, budget remaining. |
| `/diversity` | GET | Proposal entropy over last N bursts, stratum coverage. |

Note: the landscape endpoints (`/history`, `/coverage`, `/pareto`, `/costs`,
`/diversity`) are convenience wrappers over data the dashboard can already
read from disk. The daemon must own the *live* state; it need not own the
*historical* read path. If the daemon dies, the dashboard degrades to
polling-only and still renders §4 and §5 panels.

### 1.4 Disposition of Existing Surfaces (rev-2 correction)

| Existing | Disposition |
|---|---|
| `computronium/visualization/live_atlas.py` + `computronium/cli/dashboard.py` | **Evolved, not rewritten.** The polling panels, `DashboardSnapshot`, `EmbedCache`, and explicit `@ui.page("/")` are kept; lifecycle bar, liveness badge, and live-telemetry panel are added. No parallel `mission_control.py`/`landscape.py` modules. |
| `computronium/autoscientist/dashboard.py` | **Out of scope.** This is the NiceGUI/FastAPI approval workflow over `AutoScientistCampaign` (hypothesis proposals, annotate, approve/reject) — a *different* campaign mode with human-in-the-loop steering. It neither becomes Mission Control nor blocks it. TODO30 explicitly disclaims it; its fate is a separate decision. |
| `computronium/cli/continuous.py` | Becomes `comp daemon` (same flags, adds `--port`). `_deep_tier` and `_unquarantine` remain maintenance subcommands. |
| `scripts/broad_mapping_sweep.py` | Deprecated thin wrapper; superseded by `comp daemon`. |

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

A large, unmissable status badge that updates every poll cycle. Liveness is
**dual-source**: `heartbeat.json` freshness for daemon health, WS/REST
reachability for connection health.

| Condition | Badge | Color |
|---|---|---|
| Heartbeat fresh (< 10s) and state active | `● RUNNING` | Green, pulsing |
| Heartbeat fresh, state sleeping | `● SLEEPING (12s remaining)` | Yellow |
| Heartbeat fresh, state paused | `● PAUSED` | Amber |
| Heartbeat stale (> 10s) | `● CONNECTION LOST` | Red |
| No heartbeat file / daemon unreachable | `● OFFLINE` | Grey |

The badge includes: PID, uptime, node hostname, and current operation
(e.g., "Training: `S:Digital × G:Recurrent × D:EnergyMin × C:Thermo × U:Muon`").

`heartbeat.json` content: `{pid, state, burst, cell_index, started_at,
updated_at, log_path}`. Written by the daemon on every state transition and
on a ~2 s timer during long states. This is the only new artifact.

### 2.3 Graceful Shutdown Contract

When **Stop** is pressed:
1. In-flight cell completes (or is abandoned at the next epoch boundary —
   there is no hard abort; see §1.2).
2. KB is flushed.
3. CEEC traces are closed (`record` or `record_failure` — the never-limbo
   contract is untouched).
4. Checkpoint is saved.
5. Daemon transitions to `STOPPED` and remains reachable for queries.
6. Dashboard shows final summary: cells measured, defects, voids, uptime.

This is exactly the SIGTERM path `_install_sigterm()` already implements
(TODO29 session 3 fixed it to run in all modes) — the daemon formalizes it
as an API-callable transition, not a new mechanism.

---

## 3. Phase 2 — Live Telemetry (The Work Itself)

### 3.1 Active Cell Inspector

When the daemon is in `TRAINING`, a dedicated panel shows:

| Element | Content | Source |
|---|---|---|
| **Coordinate Card** | Full 6-axis string + hyperparameters. | Already in proposal dict. |
| **Proposal Rationale** | Why this cell was selected (e.g., "Balancing under-sampled triple: Diffusion × STDP × Muon. Stratum count: 2/5 target."). | **New daemon-side work**: `StratifiedRandomDriver.propose_batch` currently exposes no per-cell rationale; add a lightweight reason string to the proposal payload. |
| **Live Loss Curve** | Per-batch `train_loss` and `val_loss`, streaming via WebSocket. | **New trainer hook** (see below). |
| **Settling Trace** | Lyapunov energy descent per settle step (for `EnergyMinimization` / `PredictiveSettling` dynamics). | Same hook, settle-phase events. |
| **Progress Bar** | Batch `42 / 150` (respects `--limit-batches`). Estimated time remaining for this cell. | Hook + `limit_train_batches` (shipped TODO29 session 4). |
| **Resource Gauges** | CPU%, RAM, GPU VRAM/utilization of the daemon process (via `psutil` on the heartbeat PID). | `psutil` already a dependency. |

**Rev-2 correction: trainer hooks do not exist yet.**
`SystemTrainer.fit()` (`computronium/core/system_trainer/trainer.py`)
accumulates `history` per epoch and has no callback mechanism. The plan:

1. Add an **optional, default-no-op callback protocol** to `SystemTrainer`
   (e.g., `on_step(step_metrics: Mapping[str, float])` invoked per batch
   inside `train_epoch`). The hook is a dict emission on the hot path —
   no callback installed costs one `None` check.
2. The daemon installs a hook that pushes onto an `asyncio.Queue` bridged
   to `/ws/telemetry`. Backpressure: drop-oldest; telemetry is best-effort
   and must never slow training.
3. Fallback granularity: if per-batch proves too hot, degrade to per-epoch
   events first (still useful for a 10-epoch L0 cell at `--limit-batches 30`).

This is the **only change touching core training code** in TODO30. It is
isolated to an optional hook; everything else consumes results.

### 3.2 Structured Event Stream

Replaces the raw log ticker (which TODO29 session 3 made functional again by
fixing the deaf file logger). The daemon emits typed events via `/ws/events`:

```
[14:02:01] 🚀 Burst 14 started (target: 50 cells)
[14:02:03] 🧠 Proposed 50 cells | 3 quarantined | 12 voids pruned
[14:02:04] ⚙️  Training: Digital × Recurrent × EqProp × Null × Thermo × Muon
[14:02:18] ✅  Completed: acc=0.942 | loss=0.187 | walltime=14.2s
[14:02:19] ⚠️  Defect: Shape mismatch in FA feedback (id: a3f2c1). Cell quarantined.
[14:02:20] ⚙️  Training: Memristive × TileMesh × EqProp × Null × Thermo × Euclidean
```

Color-coded by type. Scrollable. Filterable by severity. The last 30 events
are visible by default. The existing log-tail ticker remains as the fallback
panel when the WS is down.

### 3.3 Per-Cell Outcome Badges

Every completed cell in the event stream gets an immediate visual badge:

| Badge | Meaning |
|---|---|
| 🟢 `LEARNED` | val_acc > threshold (task-specific, e.g., > 0.5 for MNIST). |
| 🟡 `MARGINAL` | val_acc between chance and threshold. |
| 🔴 `DIVERGED` | `nan_loss` flag set (shipped TODO29 session 4 — rides the KB passthrough and tags). |
| ⚫ `DEFECT` | Runtime crash. Quarantined. |
| ⬜ `VOID` | Gate-rejected before execution. |

---

## 4. Phase 3 — Landscape Awareness (What Has Been Learned)

This phase is largely **already shipped** in `live_atlas.py` (funnel, health
gauge, Pareto strip, islands atlas, ticker). The work below is *additive*.

### 4.1 Coverage Dashboard

A persistent panel answering: *"How much of the space have we explored?"*

| Metric | Visualization | Status |
|---|---|---|
| Viable cells total | Number (from `enumerate_constraint_voids`). | Data shipped; panel additive. |
| Cells measured | Number + percentage of viable total. | Additive. |
| Structural voids | Count, categorized by rejection reason. | Funnel panel has void data; categorize view additive. |
| Runtime defects | Open / resolved count. | Shipped (health gauge + funnel). |
| Coverage by axis | Parallel-coordinates heatmap: each axis (S, G, D, P, C, U) colored by sample count. Instantly reveals under-sampled primitives. | Additive; KB already stores full coordinates. |
| Stratum coverage | Histogram of triple (D, C, U) coverage: how many triples have ≥1, ≥3, ≥5 cells. | Additive; `StratifiedRandomDriver._reload_covered` already computes the coverage sets. |

### 4.2 Pareto Evolution

The Pareto front is not static—it evolves over bursts.

| Element | Content | Status |
|---|---|---|
| **Current Front** | Scatter: accuracy vs. walltime (or accuracy vs. 1−deficit). Top-3 cells labeled. | Shipped (Pareto strip). |
| **Front History** | Small-multiples: the front at burst 1, 5, 10, 14. Shows whether discovery is progressing or plateaued. | Additive; KB rows carry `burst:` tags for grouping. |
| **Breakthrough Markers** | Any cell that expanded the front is highlighted with a ★ and a timestamp. | Additive; derivation shared with the alert in §6.1. |

NaN-diverged cells are excluded from all front derivations (shipped
`promote_candidates`/`_deep_tier_candidates` behavior — reuse, don't
duplicate).

### 4.3 Negative Results Panel (The Graveyard)

Science is mostly failure. Make it visible.

| Section | Content |
|---|---|
| **Diverged Cells** | List of `nan_loss` cells with their coordinates. Grouped by axis primitive to reveal patterns (e.g., "80% of diverged cells use `PhotonicSubstrate`"). Data shipped; grouping view additive. |
| **Chance-Level Cells** | Cells that trained successfully but achieved ≤ chance accuracy. |
| **Defect Clusters** | Grouped by `defect_id`: count, affected cells, error message. **Shipped — the funnel is the bug-bounty board.** |
| **Structural Voids Summary** | Why combinations are impossible (ontology constraints). Not failures—boundaries. Data shipped; summary view additive. |

### 4.4 Diversity Monitor

Detects premature convergence of the search. The driver is stratified-random
with KB coverage seeding, so classical collapse is structurally unlikely —
these alerts catch *budget waste* (re-proposing near-measured space), not
strategy collapse.

| Metric | Alert Threshold |
|---|---|
| Proposal novelty rate (last 3 bursts) | < 10% of a burst is novel vs. KB coverage → ⚠️ "Mostly re-measuring known space." |
| Stratum repeat rate | > 80% of recent cells in previously-sampled strata → ⚠️ "Exploration declining." |
| Quarantine pressure | > 20% of viable cells quarantined → ⚠️ "Defect-driven starvation risk." |

These are **alerts only**. The dashboard does not intervene. If the
AutoScientist degrades, that is a finding about the search strategy, not a
problem for the human to fix mid-run.

---

## 5. Phase 4 — Cost Awareness

### 5.1 Projection Bar

Always visible in the header:

```
Measured: 342 / 500 (68%) | Elapsed: 2h 14m | Projected remaining: 1h 03m
Mean walltime/cell: 12.4s | This burst: 8.7s avg | Budget: ∞ (loop mode)
```

Inputs are already flowing: `walltime_s` rides the KB passthrough (TODO29
Phase 1) and `run_burst`'s summary dict reports completed/failed/stop-reason
and per-family walltime means per burst.

### 5.2 Per-Axis Cost Breakdown

A horizontal bar chart showing mean walltime per primitive (the per-family
means already logged per burst):

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
The TODO29 shakedown already demonstrated why: credit-trace cells measured
138–540 s vs ~12 s for plain L0 cells — a 40× spread the projection must
surface honestly (see §5.4).

### 5.3 Burst-Level Cost Summary

After each burst completes, log a one-line summary (the `run_burst` summary
dict already carries this):

```
Burst 14: 50 cells | 47 measured | 3 defects | walltime 8m 32s | mean 10.9s/cell
```

Displayed in the event stream and aggregated in a cost-over-time line chart.

### 5.4 Adaptive Scheduler Revisit (absorbed from TODO29 §12.2)

Deferred in TODO29 pending walltime data; the data now exists. With the cost
panel live, design the cost-compensated mixing (fold cheap
`InstantaneousPass` cells into settling-dominated queues to keep GPU
utilization even) **as a driver-level strategy on top of `run_burst`'s
summary dict** — still zero dashboard intervention, still launch-time
configurable. This is the natural follow-on experiment after the 500-cell
run; it is a daemon feature, not a dashboard feature, and ships as Phase 4.5.

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

The dashboard does **not** auto-halt. The human decides (via the Stop
button, or SSH for the halt case).

### 6.3 Completion Alerts

When `--target-cells` is reached or budget expires:

- 🏁 Toast: *"Campaign complete: 500 cells measured in 6h 12m. Pareto front: 14 cells. Report ready."*

Webhook dispatch is daemon-side (it must fire when no browser is attached);
toasts are dashboard-side (replayed from the event log on reconnect).

---

## 7. Phase 6 — Historical Analysis & Reporting

### 7.1 Cell Detail View

Click any cell in the history table to see:

| Field | Content |
|---|---|
| Full coordinate | 6-axis string + hyperparameters. |
| Metrics | train_loss, val_loss, val_acc, walltime_s, param_count, nan_loss. |
| Instruments | settle_horizon, σ_max proxy, credit_alignment (if measured). |
| Tags | `maturity:l0`, `burst:2026-09-17-003`, `nan_loss` (if applicable). |
| Provenance | Campaign ID, iteration, CEEC experiment ID, seed. |
| Training Curve | Static replay of the loss/accuracy trajectory (from the trainer history stored in the KB). |
| Settling Trace | Static replay of energy descent (if applicable). |

### 7.2 Maturation Status

| Tag | Meaning | Count |
|---|---|---|
| `maturity:l0` | Mapping fidelity. 1 epoch (or `--limit-batches N`), 1 seed. | N |
| `maturity:l1` | Promoted. 3 epochs. | N |
| `maturity:l2` | Claim-grade. 10 epochs, 3 seeds. | N |

The dashboard shows counts and allows filtering by maturity. Only `l2` cells
may back comparative claims (per CEEC governance). All machinery is shipped
(`promote_candidates`, `deep-tier`, `maturation.jsonl` with the
`seed_sensitivity` variance audit); this phase is the *view*.

### 7.3 Campaign Summary Report

A **Generate Report** button (read-only assembly, not intervention) that
produces a Markdown document:

- Campaign configuration (axes, constraints, budget, task).
- Total cells measured, defects, voids.
- Final Pareto front (table + scatter).
- Top-10 cells by accuracy.
- Negative results summary (top failure modes).
- Cost breakdown (per-family walltime, credit-trace premium).
- CEEC ledger rollup (experiments, beliefs, gates).
- Verification levels achieved.

This is the artifact a scientist takes to a paper or a review.

---

## 8. Implementation Plan

| Phase | Deliverable | Key Files |
|---|---|---|
| **8.1** | Daemon extraction: `ContinuousDaemon` class wrapping `run_burst` with the state machine, heartbeat writer, API server (FastAPI + WebSocket, both already dependencies). Headless, survives UI disconnect. | `computronium/autoscientist/daemon.py` (new) |
| **8.2** | Trainer telemetry hook: optional default-no-op per-batch callback protocol on `SystemTrainer`; daemon bridges hook → async queue → `/ws/telemetry` (drop-oldest backpressure). | `computronium/core/system_trainer/trainer.py` (isolated edit), `computronium/autoscientist/daemon.py` |
| **8.3** | Lifecycle bar + liveness badge in the dashboard: dual-source heartbeat/WS health, three buttons, REST wiring. | `computronium/visualization/live_atlas.py`, `computronium/cli/dashboard.py` |
| **8.4** | Proposal rationale: lightweight per-cell reason string on `StratifiedRandomDriver.propose_batch` payload. | `computronium/autoscientist/broad_map.py` |
| **8.5** | Landscape panels: coverage-by-axis, stratum coverage, front history, graveyard grouping, diversity monitor — built on the existing `DashboardSnapshot` headless render path. | `computronium/visualization/live_atlas.py` |
| **8.6** | Cost module: per-axis walltime aggregation from `run_burst` summaries + KB, projections, burst summaries, projection bar. | `computronium/autoscientist/daemon.py` (aggregation) + dashboard panel |
| **8.7** | Alerting: breakthrough detection (shared derivation with §4.2 markers), cascade failure, completion. Webhook dispatch daemon-side. | `computronium/autoscientist/alerts.py` (new) |
| **8.8** | History & reporting: cell detail view, maturation table, Markdown report generation. | `computronium/visualization/live_atlas.py` + report builder |
| **8.9** | CLI integration: `comp daemon` replaces `comp continuous` as the primary entry point (same flags, adds `--port`). `comp dashboard` connects. | `computronium/cli/daemon.py`, `computronium/cli/dashboard.py` |
| **8.10** | Adaptive scheduler experiment (post-500-cell, per §5.4). | `computronium/autoscientist/broad_map.py` |

### 8.11 Absorbed TODO29 Remaining Work

These TODO29 §12/§13 items are either prerequisites or ride-alongs:

| Item | Absorption |
|---|---|
| **500-cell shakedown launch** (TODO29 §8, §12.1) | Becomes the acceptance test for the daemon (§9.4): launch through `comp daemon`, watch on the dashboard, verify no terminal needed. Launch command per session-4 ready-state: `--target-cells 500 --limit-batches 30 --loop --sleep 15`, **no `--credit-trace`** unless multi-day walltime is acceptable (session-3 cost finding: 138–540 s/cell with trace). |
| **NaN policy** (session 4) | Landed. Dashboard surfaces it: `nan_loss` badge (§3.3), front exclusion (§4.2), graveyard grouping (§4.3). |
| **Defect ID hardening** (TODO29 §12.3) | Conditional ride-along: if the 500-cell run shows ID collisions on generic messages, add the first traceback frame to the `defect_id` hash. One-line change in `defects.py`. |
| **Optional root lockfile** (TODO29 §12.5) | The daemon makes concurrent-burst accidents *more* likely (a long-lived server invites second launches). Land `<root>/continuous.lock` (`O_EXCL`) with the daemon (8.1), not conditionally. |
| **`test_demo_ntm_local` faulthandler noise** (TODO29 §12.4, session 2b) | Unrelated to the dashboard but blocks operator trust in the suite; fix as hygiene during Phase 8.1 (raise the per-test timeout or trim the probe). |
| **Multi-task maturation `--task` filter** (TODO29 §12.6) | Unchanged deferral; per-task Pareto fronts are post-campaign work, orthogonal to the dashboard. |
| **Budget granularity: batch trimming** (session 3 finding) | Daemon phase (8.1): trim the proposal batch per proposal on soft expiry instead of finishing the whole iteration — cells are independent and KB-flushed, and the daemon makes the overshoot more visible. |

### Testing

| Gate | Test |
|---|---|
| Daemon lifecycle | Start → propose → train → pause → resume → stop. State transitions verified; heartbeat written throughout. |
| Telemetry integrity | WebSocket stream matches KB-recorded final metrics within tolerance. |
| UI liveness | Kill daemon process → dashboard shows `CONNECTION LOST` within 12s; landscape panels keep rendering from artifacts (hybrid-transport guarantee). |
| Graceful stop | Stop mid-burst → KB flushed, CEEC closed, checkpoint saved (reuses the SIGTERM contract test from TODO29). |
| Cost accuracy | Projected remaining time within 20% of actual over a 50-cell run. |
| Alert correctness | Inject a Pareto-breaking cell → breakthrough alert fires. Inject 20 defects → cascade alert fires. |
| Lockfile | Second daemon on the same root refuses to start, exit non-zero. |
| Hook isolation | `SystemTrainer` with no callback is bit-identical in behavior and within noise in walltime. |

Per-commit duties follow the AGENTS checklist (dev-env smoke → ruff on
changed files → pyright strict on new modules `daemon.py`, `alerts.py` →
targeted tests). New/changed targeted suites: extend
`tests/integration/test_continuous_burst.py` for daemon lifecycle;
`tests/integration/test_dashboard_smoke.py` for the new panels via the
headless `DashboardSnapshot` path; new `tests/property/test_daemon_state.py`
for the state machine with a fake clock. Fast gate (demo/gallery +
property suite) at round close; the dynamics wiring lockstep lock is
untouched (no new ontology primitives) but asserted green.

---

## 9. What This Dashboard Is Not

| Not | Why |
|---|---|
| A steering wheel | The AutoScientist's search strategy is configured at launch. Human mid-run steering defeats the purpose of autonomous discovery. (The `autoscientist/dashboard.py` approval workflow is a separate campaign mode, explicitly out of scope — §1.4.) |
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
running a script—the dashboard is incomplete. Landscape panels must degrade
gracefully to artifact-polling when the daemon dies (criterion 3 survives a
crash; criterion 1–2 do not require the WS to be up).

---

## 11. Migration Path

| Existing | Becomes |
|---|---|
| `comp continuous` | `comp daemon` (same flags, adds `--port` for the API server). Legacy alias preserved for one release. |
| `comp dashboard` | Evolved in place into Mission Control: existing polling panels kept, lifecycle bar + live telemetry added. Connects to daemon API when present, degrades to polling-only when not. |
| `computronium/autoscientist/dashboard.py` | Unchanged, out of scope (separate hypothesis-approval campaign mode — see §1.4). |
| `comp continuous unquarantine` | Retained as a maintenance CLI command (not a dashboard feature). |
| `comp continuous deep-tier` | Retained as a maintenance CLI command. |
| `scripts/broad_mapping_sweep.py` | Deprecated. Superseded by `comp daemon`. |
| `heartbeat.json` | New artifact, daemon-written, dashboard-read. |

---

## 12. Epistemic Rules (Unchanged)

1. **Voids ≠ defects.** Gate rejections are ontology boundaries. Runtime crashes are implementation failures. Neither is a measurement.
2. **Maturity gates claims.** `l0` maps the space. Only `l2` (multi-seed, cross-burst) backs a comparative claim. `--limit-batches` L0 cells are mapping-grade only — say so in the report.
3. **Instruments stay honest.** σ_max proxy is never labeled ρ(J_F). Sampled numerical is Level 4, never Level 1–3. The projection bar labels credit-trace-inclusive estimates explicitly (the 40× cost spread is a measurement, not a rounding detail).
4. **The ledger only sees gate-passing cells.** The daemon adds no new CEEC pathways; the telemetry hook is a side-channel, never a second record path.
5. **The dashboard never writes to the KB or ledger.** It is a read-only observer with lifecycle authority only.
6. **Telemetry is best-effort.** The hook never blocks or errors training; a dropped WebSocket event is a rendering gap, never a data gap (the KB is the only record of truth).

---

## 13. Immediate Next Actions (in order)

1. ~~**Extract `ContinuousDaemon`**~~ **DONE** (8.1 + lockfile + batch-trimming note: target-boundary batch trimming already shipped in `run_burst`; the daemon adds the boundary gate).
2. ~~**Add the trainer telemetry hook**~~ **DONE** (8.2, `step_callback`, behavior-identical verified).
3. ~~**Build the Lifecycle Control Bar and Liveness Badge**~~ **DONE**
   (8.3). The daemon REST/WS surface it uses: `GET /state` returns the
   heartbeat payload + uptime + `last_summary`;
   `POST /control/{start,pause,resume,stop,skip_sleep}`; `WS /ws/telemetry`
   streams `{metric: float}` dicts per training batch (drop-oldest);
   `WS /ws/events` streams `{kind, ...}` lifecycle events. The bar's
   buttons fire REST posts fire-and-forget (1 s timeout); badge refresh
   rides the existing 2 s artifact poll. **Not yet consumed: the WS
   streams** — the §3.1 Active Cell Inspector (8.5+) is their first UI.
4. **Run the 500-cell shakedown through the new daemon** (per §8.11 launch
   guidance: no `--credit-trace`, `--limit-batches 30`). Watch it on the
   dashboard. Verify: no terminal needed for the full run. Collect
   defect-ID collision evidence (§8.11) during the run.
5. ~~**Implement the Graveyard, Coverage, and Diversity Monitor** panels~~
   **DONE** (8.4–8.5, from shipped KB/voids/defects data — the shakedown
   will populate them with real 500-cell volume).
6. ~~**Wire breakthrough and cascade alerts**~~ **DONE** (8.7).
7. **Generate the first campaign summary report** from the completed
   500-cell run (8.8).
8. **Design the adaptive scheduler** from the accumulated per-family
   walltime data (8.10, post-campaign).

### 13.1 Improvement opportunities (from the 8.1/8.2 landing)

- **Per-iteration cell progress**: the heartbeat's `cell_index` only updates
  per burst (run_burst reports completion at iteration granularity). For the
  §2.2 "Cell 12/50" badge, either a light per-iteration callback on
  `run_burst` or a daemon-parsed ledger tail.
- **Event payload enrichment**: `burst_finished` should carry the full
  `run_burst` summary dict (means by family, completed/failed counts) so the
  §5 cost panels can be fed straight from `/ws/events` without KB queries.
- **Telemetry richness**: the hook currently forwards `train_step` metrics
  only; settle-phase energy traces (§3.1 settling trace) need a second
  emission point in the dynamics settle path or an epoch-level event.
- **Active Cell Inspector (§3.1) UI**: the data path exists (telemetry WS +
  proposal `justification`); the panel itself (coordinate card, live loss
  curve, progress bar, resource gauges via psutil) is the remaining 8.5+
  work and the first consumer of the WS streams.
- **Alert hardening from shakedown data**: breakthrough detection reads
  the KB best accuracy per burst (per-cell granularity, not per
  iteration); if the 500-cell run shows missed or noisy breakthroughs,
  move the check to a per-iteration callback. Cascade thresholds are
  derived from `failed/executed` — divergence (NaN) counts ride the KB
  tags and may need folding in after the run.
- **Front-history honesty**: `front_history_rows` uses (accuracy↑,
  walltime↓); when a ruler table exists, switch to (accuracy↑, deficit↓)
  per §4.2 and label which objective pair is shown.
- **Graceful-stop watchdog**: `ContinuousDaemon.stop()` from SIGTERM works,
  but a hard kill leaves the lockfile behind — document stale-lock recovery
  (already supported: delete `<root>/continuous.lock`) or add PID liveness
  check before refusing to start.
- **Dashboard readiness for 8.3**: `GET /state` intentionally returns the
  heartbeat payload verbatim; the UI can treat `updated_at` staleness
  (>10 s) as CONNECTION LOST per §2.2 without extra daemon work.
