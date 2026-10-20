# Computronium Dashboard — 3D Mission Control

The live monitoring dashboard is a **three.js WebGL application** that visualizes running campaigns in real time. It connects to the campaign queue via WebSocket and renders a 3D "fog-of-war" discovery map alongside interactive analytics.

## Launch

```bash
# Terminal 1: Start the dashboard (port 8080)
uv run comp dashboard --store experiment.duckdb

# Terminal 2: Run a campaign to populate live data
uv run comp run demo --store experiment.duckdb
```

Open <http://localhost:8080> in a browser.

---

## UI Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  MODE CHIP (top-left)          DISCOVERY MAP (center, 3D)          HUD (top-right)  │
│  ─────────────────            ─────────────────────────           ──────────────  │
│  EXPLORATORY (amber)          3D grid: credit × geometry ×        GPU ████████░░ 67%  │
│  PREREGISTERED (green)        dynamics                              CPU ██████░░░░ 42%  │
│                                Measured: glowing pillars            MEM ███████░░░ 58%  │
│                                Legal: wireframe cubes               BURN: 34s / 120s   │
│                                Void: red X markers                  CLAIM: 63 seeds    │
│                                Click cell → Cell Drawer             │
│                                                                      │
│  ──────────────────────────────────────────────────────────────────────       │
│  PLOTTER (tabs, below map)                                             │
│  ┌──────────┬──────────┬──────────────┐                                │
│  │ PARETO   │ ABLATION │ VARIABILITY  │                                │
│  │ Scatter  │ Bars     │ Box plots    │                                │
│  │ val_acc  │ val_acc  │ val_acc      │                                │
│  │ vs       │ by arm   │ by arm       │                                │
│  │ 1/walltime│ + chance │ + chance     │                                │
│  └──────────┴──────────┴──────────────┘                                │
│  ──────────────────────────────────────────────────────────────────────       │
│  LIVE RAIL (bottom)                  CELL DRAWER (right slide-in)      │
│  ─────────────────                   ─────────────────────────        │
│  [14:32:15] ✓ s6_train compose       Coordinate: credit=gradient      │
│  [14:32:13] ✓ s5_compose settle      geometry=feedforward             │
│  [14:32:10] ⚠ s4_gate control        dynamics=instantaneous           │
│       at chance                          val_acc = 0.444 ± 0.115     │
│                                            chance = 0.10  ████░░░░░░   │
│                                            VERDICT: INSUFFICIENT       │
│                                            Sparkline: ▁▂▃▅▆▇        │
│                                            [queue rest] [preregister]  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Discovery Map (3D Fog-of-War)

**The core visual.** A 3D grid that shows a *slice* of the ontology's
declared space: three axes are free and the other three are held at one value
each, so every cell on the grid is a whole coordinate and the system can judge
it. The backend judges each cell — the grid draws what it is told.

| Cell Type | Visual | Meaning |
|-----------|--------|---------|
| **Measured** | Glowing pillar (height = val_acc, color = credit arm) | At least one seed completed |
| **Legal/Unmeasured** | Semi-transparent wireframe cube | The system would measure it and nobody has — a gap |
| **Void** | Red X marker | The system's own rules refuse the combination |

**Where the space comes from.** The primitive registry says which values an
axis may take; the system's void rules (`CONSTRAINTS_REGISTRY`, the same ones
the gate applies to a proposal) say which combinations of them mean anything.
Both are read on the server, so the picture and the run cannot disagree about
what is possible.

**What the grid shows.** The values an axis takes are the run's own evidence
first, then the run's declaration, then the rest of the axis in registry
order — up to eight per axis, because a wider grid stops being readable. The
run's evidence is never among the things left out, and the legend says how
many of the axis's values are on screen (`8 of 10`).

**The held axes.** The three axes the grid does not show are held at the
value the run used, so the run's evidence lies inside the slice. The legend
names them (`held: substrate=digital · plasticity=null · update=adam`).

**Axis picker** (in the legend): three selects — X, Y, Z — over the six
coordinate axes (credit, geometry, dynamics, substrate, plasticity, update).
Changing one asks the backend for that slice's space and redraws the grid.

**Interactions:**
- **OrbitControls**: Left-drag = rotate, Right-drag = pan, Scroll = zoom
- **Click** a cell → opens the Cell Drawer (measured, legal or void)
- **Hover** highlights the cell (a pillar glows, a cage brightens) and names it
  in a readout that follows the cursor: the cell's coordinate, what it is, and
  — for a void cell — the rule that refuses it

**The evidence wins the click.** The grid is dense and every gap carries an
invisible pick target (a wireframe cube is hollow, so a ray through its middle
hits nothing, and a gap nobody can click is a gap nobody can act on). The
nearest cell along the ray is therefore often a gap standing in front of a
pillar. A measured cell the ray met wins: the evidence is what the researcher
was aiming at, and a gap is picked when nothing measured is in the way.

**Void cells are nameable.** The void markers are one mesh, drawn and never
picked, so the cursor cannot pick one: the point the ray met says which cell
the marker belongs to, and the readout says what refuses it.

**Axis labels:** sprites on the grid's edges — the values the row names, and
each axis's name at the end of its axis. A long value is wrapped at its
underscores so it fits the gap between two cells instead of painting over its
neighbours.

**Pillars grow** into the height they were measured at; they do not appear at
it.

**Framing:** the camera frames the grid into the part of the window the
panels leave free, so the map is not half hidden behind the legend.

**Legend** (bottom-left of the map): the cell-type key, the credit arm
colours, the run picker, the axis picker, and the tally — how many cells are
measured, legal and void, and which rules refuse the void ones.

**The run the picture shows.** A store holds several runs — the run, and the
runs its own answers spawned — and each of them reports its own metrics. A
picture can only show one at a time, so the choice is made once, in
`src/run-selection.ts`: the run that started last until the reader picks
another, and the map, the charts and the mission-control panel all read the
same answer. The legend's **Run** picker names the runs the dashboard knows
about (`307e2baf · demo · 5`) and says which one the picture shows
(`run 307e2baf · EXPLORATORY · 5 records`).

---

### 2. Cell Drawer (Right Slide-In Panel)

Rich detail for a selected measured cell. HTML overlay (not WebGL) for crisp text.

**Content:**
- **Coordinate badges**: substrate/geometry/dynamics/plasticity/credit/update with credit arm color
- **Primary metric**: `val_acc = 0.444 ± 0.115 (n=5)` — large monospace
- **Chance line**: Progress bar with gradient (red→amber→green) showing distance from chance (0.10 for digits)
- **Verdict banner**: `REJECTED` (red, at or below chance) / `INSUFFICIENT`
  (amber) / `PASSED` (green). A cell with fewer seeds than the gate asks for
  is `INSUFFICIENT` however good its mean looks: 5 seeds cannot carry a
  claim that 63 seeds are needed for.
- **Seeds to claim**: the seeds still missing for a claim
  (`GateThresholds().required_seeds_per_group` minus the seeds measured)
- **Wall time & param count**
- **Mini 3D sparkline**: the cell's **recorded** training curve
  (`payload.convergence_curve`, averaged over the cell's seeds) with the
  chance line. A cell that recorded no curve says so instead of drawing one.

`Escape` closes the drawer; the mission-control panel and the plotter step
aside while it is open.

**Actions** — the drawer can act on the cell it shows:

| Button | What it does | When it applies |
|--------|--------------|-----------------|
| `[Queue Rest]` | Queues the measurements the cell still owes: the run's seed plan grows, and the pipeline measures only the seeds the store does not hold | a measured cell (a legal one is labelled `[Queue]` and measures the cell) |
| `[Preregister]` | Writes a registration for the confirmation: the threshold is the effect the cell showed | a measured cell |
| `[Adopt as Quest]` | Writes a registration for the question — the threshold is the material effect the gate asks for, in the run's own units — **and queues the run that would answer it** | a cell with no measurement |

The threshold field overrides the derived one. The buttons post to
`/api/cells/{run_id}/{replicate,preregister,quest}` and the drawer's status
line says what happened — the campaign that was queued, or the file that was
written.

**A quest is answered by a new run.** The quest writes the protocol down
first and queues the measurement second, and the run it queues is a *new*
one: a threshold written now cannot confirm a run that has already begun,
and the run the question came from began long before. The cell holds no
evidence to join either — every seed in the plan is new. The answering run
declares exactly that one cell, with the seed count the registration names,
and a budget measured from the run's own seeds.

Without a campaign queue the question is still registered, and the status
line says that nothing was scheduled: a dashboard built without a queue
answers `409` for the verbs that need one, and says so rather than
pretending the work was queued.

**A cell the system refuses cannot be acted on.** The void rules that mark a
cell on the grid also refuse it at the verbs: a replication or a registration
about an impossible combination is answered with `409` and the rule that
refuses it. The mark on the picture and the behaviour of the dashboard agree.

**Where the registrations go.** `configs/preregistrations/<run>_<kind>_<cell>.json`,
the same directory the report reads, in the shape
`computronium.validation.preregistration.ThresholdRegistration` defines. The
file also names the cell it is about, so it is readable without the dashboard
that wrote it. Commit it: it is a governance artifact, and the repository is
where registrations live.

**What a registration can and cannot confirm.** A threshold written *after* a
run began was written with that run's data in hand, so it cannot confirm that
run. The mode chip and the report both compare the registration's timestamp
with the run's start: the run that produced the observation stays
`EXPLORATORY`, and the run that follows the registration can be confirmatory.

**And a registration speaks about a cell.** A registration the dashboard
writes names the cell it is about, and it confirms only a run that measured
that cell. Without that rule one click on one cell would make every run in
the repository confirmatory — the same failure the timestamp rule stops, one
level down. A registration written by hand, naming no cell, is a protocol
about the metric itself, and counts as it always did.

---

### 3. Plotter (Three Tabs, uPlot)

Interactive Canvas 2D charts (uPlot, 25KB, 60fps). Data updates via WebSocket `campaign_metrics`.

| Tab | Chart | Details |
|-----|-------|---------|
| **Pareto** | Scatter: val_acc vs 1/walltime_s | Points colored by credit arm. Pareto frontier points highlighted (purple ring). Dashed frontier line. |
| **Ablation** | Grouped bars | Credit arm × val_acc with error bars. Horizontal dashed chance line at 0.10. |
| **Variability** | Box/violin plots | Per credit arm: whiskers, box (IQR), median, outliers. Chance line. |

**Axis labels**: every chart says what its axes are (`1 / walltime_s
(faster →)`, `credit arm`, `accuracy`); the ablation and variability charts
name the arms on the x axis rather than numbering them.

**Tooltips**: hovering a point or a bar says what it is — the arm, the value,
the spread and the seed count.

**Toolbar** (per chart): Download PNG (the whole chart, axes included),
record and Pareto counts, and the axes the ablation chart holds fixed.

---

### 4. Live Rail (Bottom Log)

Scrolling timeline of pipeline events. HTML overlay with animated pills.

**Event levels:**
- `✓ ok` — stage completed (green)
- `⚠ warn` — something degraded (amber)
- `✗ error` — stage or campaign failed (red)

**Source:** the process-wide event bus
(`computronium/experiment/execution/events.py`). The pipeline publishes a
stage event for every stage it runs and a measurement event for every cell it
records; the campaign queue publishes the campaign's own lifecycle. The
dashboard subscribes and forwards each event as a `pipeline_event` message.

A campaign running in *another* process cannot publish into this process's
bus, so the dashboard derives the only progress it can honestly report there:
records landing in the store. A run that reports itself on the bus is never
also counted by the store.

---

### 5. Mission Control (Top-Right)

HTML overlay panel. Text belongs to the DOM, not to WebGL: the plan's own
risk table says so, and a 3D sprite's size depends on where the camera
stands.

| Element | Source | Description |
|---------|--------|-------------|
| **DEVICE** | `schedule.device` | `auto`, `cpu` or `cuda` |
| **MEMORY** | measured `payload.memory_mb` | peak resident memory of the campaign |
| **WALLTIME** | measured `payload.walltime_s` | seconds burned so far |
| **RECORDS** | store | records measured |
| **GPU / CPU** | `queue.get_resource_usage()` | `—` when no campaign queue is attached |
| **PICTURE** | the store the dashboard read | `live`, or `snapshot <time>` when it read the writer's mirror |
| **SEEDS TO CLAIM** | `GateThresholds().required_seeds_per_group` | seeds still missing for a claim |

Every number is measured or derived from a registry — none is a placeholder.

---

### 6. Mode Chip (Top-Left)

HTML overlay chip showing the run's registration status, read from the run
rather than asserted:
- `EXPLORATORY` (amber) — the run's claim has no pre-registered threshold
- `PREREGISTERED` (green) — every metric the run claims has one, in
  `configs/preregistrations/`
- `NO RUN` (grey) — nothing has reported yet

The chip's second line names the run (`demo · digits · L1`).

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `1` | Switch to Pareto tab |
| `2` | Switch to Ablation tab |
| `3` | Switch to Variability tab |
| `H` | Toggle HUD visibility |
| `L` | Toggle Live Rail visibility |
| `Escape` | Close the Cell Drawer |

---

## WebSocket Message Types

The dashboard consumes these message types (via `MessageRouter` auto-registration):

| Type | Payload | Consumers |
|------|---------|-----------|
| `status_update` | `{gpu, cpu, memory, ...}` | Mission Control, Live Rail |
| `queue_update` | `{queued, running, completed, resource_usage}` | Discovery Map, Live Rail |
| `campaign_metrics` | `{campaign_id, data: {records, pareto, ablation_groups, chance, required_seeds, resources, run}}` | Discovery Map, Cell Drawer, Plotter, Mission Control |
| `pipeline_event` | `{stage, message, level, run_id, timestamp}` | Live Rail |

`run` names the run the metrics are about — its profile, tasks, fidelity,
objectives, claim metrics and registration status.

---

## Architecture

```
CampaignQueue (singleton)
    │
    ├─► WebDashboard._get_queue_status() → WebSocket queue_update (2s)
    │
    └─► CampaignQueue._run_campaign() → RecordStore.append() → DuckDB
                                          │
                                          ▼
PipelineRunner ──► event bus ─────────────┤
                                          ▼
    WebDashboard._get_campaign_metrics() ──► RecordStore.query_records(read_only=True)
                                          │
                                          ▼
    WebSocket campaign_metrics ──► three.js DiscoveryMap.updateMetrics()
                                          │
                                          ▼
    User clicks cell ──► CellDrawer.show(cellData)
    User opens Plotter ──► Plotter.update(records)
    User presses a verb ──► CellDrawer.runAction()
                              │
                              ├─ replicate ──► CampaignQueue.enqueue()
                              │                  └─ CampaignRun(run_id=…):
                              │                     the run continues, so the
                              │                     seeds join its evidence
                              ├─ preregister ──► configs/preregistrations/
                              └─ quest ────────► configs/preregistrations/
                                                 + CampaignQueue.enqueue()
                                                    (a NEW run: a threshold
                                                    written now cannot confirm
                                                    a run that has begun)
```

**Critical — the store's lock is exclusive, and the writer publishes a
mirror.** DuckDB gives one writer the file, and a read-only connection cannot
join a read-write one — not even inside the same process, where DuckDB shares
one instance per path. Across processes it is worse: a reader cannot open a
file a writer holds at all, and a writer cannot open a file a reader holds.

So the writer publishes a **mirror**: a copy of the whole database, taken by
DuckDB inside the writer's own transaction and swapped in atomically, next to
the store (`experiment.mirror.duckdb`). A dashboard in another terminal reads
the mirror while the campaign runs, and the store itself once the campaign
lets go. The Mission Control panel says which it is reading (`live` or
`snapshot <time>`), because a snapshot lags the run by the writer's publish
interval.

The mirror is a copy, not a second truth: the store remains the record of
account, and a reader that can open it always prefers it.

**A queued replication needs the queue.** The dashboard attaches the process's
campaign queue, so `comp dashboard` can queue work; a dashboard built without
one answers `409` and says so, rather than pretending the work was queued.

REST endpoints: `/api/status`, `/api/queue`, `/api/resources`,
`/api/campaigns`, `/api/campaigns/{id}`, `/api/campaigns/{id}/metrics`,
`/api/runs` (the store's runs and their record counts), `/api/metrics/{id}`.

Write endpoints (the drawer's actions): `/api/cells/{run_id}/replicate`,
`/api/cells/{run_id}/preregister`, `/api/cells/{run_id}/quest`. Each takes
`{"coordinate": {...}}` and answers with what it did, or with an `error` and a
status that says why not.

The map's own endpoint: `POST /api/cells/{run_id}/space` with
`{"axes": ["credit", "geometry", "dynamics"]}`. It answers with the slice —
the values each free axis takes, the value each held axis is fixed at, the
run's declaration per axis, and every cell with the system's verdict on it.

---

## Color Palette

Single source: `scripts/generate_palette.py` → generates:
- `computronium/visualization/_palette.py` (Python)
- `dashboard/src/palette.ts` (TypeScript/three.js)
- `dashboard/templates/static/css/palette.css` (HTML overlays)

**Key semantic colors:**
- `--measured` `#d4a843` — glowing pillars
- `--legal_unmeasured` `#58a6ff` — wireframe cubes
- `--void` `#f85149` — red X markers
- `--pareto` `#a371f7` — Pareto frontier highlight
- `--chance_line` `#f85149` — chance level
- `--passed` `#3fb950`, `--insufficient` `#d29922`, `--rejected` `#f85149`

---

## Extending the Dashboard

### Add a New Component

1. Create `src/my-component.ts`
2. Extend `BaseComponent` (or just implement `init()`/`destroy()`)
3. Register with `MessageRouter`:
   ```typescript
   router.register('campaign_metrics', this.onMetrics.bind(this));
   ```
4. Export and import in `src/main.ts` (or rely on `ComponentRegistry` auto-discovery)

### Add a New Chart Tab

1. Add canvas element in `index.html` or dynamically in `plotter.ts`
2. Create uPlot instance in `Plotter.init()`
3. Add tab button and switch logic
4. Implement `update(data)` to consume `campaign_metrics.records`

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Blank canvas / WebGL not working | Browser needs WebGL2. Try Chrome/Edge/Firefox. In headless CI: `--use-gl=angle` |
| WebSocket connection fails | Check dashboard port (default 8080). Firewall? |
| No data appearing | Ensure campaign is running and writing to the same DuckDB file (`--store experiment.duckdb`). The dashboard reads the writer's mirror while the writer holds the file. |
| Store locked | A campaign in another process holds the DuckDB file. The dashboard reads the mirror it publishes (`<store>.mirror.duckdb`), or the store itself once the writer lets go. |
| Three.js errors in console | Check `npm run build` output. Vite bundles to `templates/static/js/dashboard.js` |

---

## Console Dashboard (no browser)

```bash
uv run comp dashboard --store experiment.duckdb --console
```

The same picture in the terminal, for a headless machine: the campaign queue,
the resources, the metrics, the recent records — and the **declared space**,
drawn as a grid of marks. `█` is a cell the run measured, `·` a gap nobody has
measured, `×` a cell the system refuses, with the rule that refuses it. The
space is read through the same rules the browser uses, so the two cannot
disagree about what is possible. The header names the run the console shows,
for the same reason the browser's legend does: a store holds several runs,
and a picture that does not say which one is a picture of nothing in
particular.

---

## Development

```bash
cd computronium/experiment/execution/dashboard
npm install          # Install deps
npm run dev          # Vite dev server with HMR (proxies API to localhost:8080)
npm run build        # Production build → templates/static/js/dashboard.js
```

**Regenerate palette/axis metadata:**
```bash
uv run python scripts/generate_palette.py
uv run python scripts/generate_axis_metadata.py
```

**Without a GPU.** The dashboard detects a software rasterizer (SwiftShader,
llvmpipe) and drops shadows, antialiasing and the pixel ratio, and caps the
frame rate at 12 fps. A software-rendered scene otherwise starves the
browser's event loop: the WebSocket frames that carry the data stop being
processed, and the dashboard looks frozen while the server is fine.

**Probes** (headless measurements, `scripts/probes/`):
```bash
uv run python scripts/probes/probe_ws_delivery.py          # message latency
uv run python scripts/probes/probe_plot_scale.py            # axes cover the data
uv run python scripts/probes/probe_dashboard_plot_drawer.py # drawer + plot state
uv run python scripts/probes/probe_dashboard_space.py        # the gap is visible and actionable
uv run python scripts/probes/probe_dashboard_void.py         # the void cell says why
uv run python scripts/probes/probe_dashboard_actions.py      # the verbs act
uv run python scripts/probes/probe_dashboard_quest.py       # the quest is answered by a run
uv run python scripts/probes/probe_quest_run.py             # the answering run, end to end
```

The probes share `scripts/probes/dashboard_probe.py`: the Chromium flags that
make WebGL work without a GPU, the wait for the server, and the store they
read.

---

## Screenshot Pipeline (Hero Image)

```bash
# Generates docs/readme/assets/dashboard-hero.png (1920×1080)
uv run python scripts/capture_dashboard_screenshot.py
```

Requires: `playwright` (in `dev` extra), Chromium. Uses `--use-gl=angle`
with the SwiftShader rasterizer for headless WebGL.

The dashboard, the campaign and the capture run in **one process**: the
campaign holds the store, and the capture wants the records the campaign has
just written. (A dashboard in another process would see them too, through the
mirror the writer publishes — but one process has no such gap to fall
through.) The script starts the server on a thread, runs the demo campaign on
the main thread, and screenshots from a third thread once the records have
landed.

The screenshot is embedded in `docs/readme/title.md` and appears on the README front page.