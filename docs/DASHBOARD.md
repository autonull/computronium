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

**The core visual.** A 3D grid whose axes are **derived from the data**: every
coordinate axis the records carry, with the values the records actually used.

| Cell Type | Visual | Meaning |
|-----------|--------|---------|
| **Measured** | Glowing pillar (height = val_acc, color = credit arm) | At least one seed completed |
| **Legal/Unmeasured** | Semi-transparent wireframe cube | In search space, not yet run |
| **Void** | Red X marker | Outside declared search space |

**Axis picker** (in the legend): three selects — X, Y, Z — over the six
coordinate axes (credit, geometry, dynamics, substrate, plasticity, update).
The values shown are the ones the records used, ordered by the primitive
registry; the legend states how many of the known primitives were observed.

**Interactions:**
- **OrbitControls**: Left-drag = rotate, Right-drag = pan, Scroll = zoom
- **Click** a measured cell → opens Cell Drawer
- **Hover** highlights cell (emissive pulse)

**Axis labels:** sprites on the grid's edges — the values the row names, and
each axis's name at the end of its axis. A long value is wrapped at its
underscores so it fits the gap between two cells instead of painting over its
neighbours.

**Pillars grow** into the height they were measured at; they do not appear at
it.

**Legend** (top-left of map): Shows credit arm color coding and cell type key.

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

**Actions** (v1 visual only, disabled):
- `[queue rest]` — request more seeds for this cell
- `[preregister]` — promote to confirmatory protocol
- `[adopt as quest]` — mark for focused follow-up

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
```

**Critical — the store is read-only, and that has a consequence.** DuckDB
gives one writer the file, and a read-only connection cannot join a
read-write one — not even inside the same process, where DuckDB shares one
instance per path. So the dashboard opens the store read-only, and falls
back to read-write only when the writer is *this* process (an in-process
campaign). A campaign in another terminal therefore holds the file, and the
dashboard shows no records until it lets go. Run the campaign in the
dashboard's process, or wait for the run to finish.

REST endpoints: `/api/status`, `/api/queue`, `/api/resources`,
`/api/campaigns`, `/api/campaigns/{id}`, `/api/campaigns/{id}/metrics`,
`/api/runs` (the store's runs and their record counts), `/api/metrics/{id}`.

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
| No data appearing | Ensure campaign is running and writing to the same DuckDB file (`--store experiment.duckdb`) |
| Store locked | A campaign in another process holds the DuckDB file. The dashboard reads it once the writer releases it, or immediately when the campaign runs in the dashboard's own process. |
| Three.js errors in console | Check `npm run build` output. Vite bundles to `templates/static/js/dashboard.js` |

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
```

---

## Screenshot Pipeline (Hero Image)

```bash
# Generates docs/readme/assets/dashboard-hero.png (1920×1080)
uv run python scripts/capture_dashboard_screenshot.py
```

Requires: `playwright` (in `dev` extra), Chromium. Uses `--use-gl=angle`
with the SwiftShader rasterizer for headless WebGL.

The dashboard, the campaign and the capture run in **one process**: DuckDB
gives one writer the file, so a dashboard in another process would see
nothing until the campaign finished. The script starts the server on a
thread, runs the demo campaign on the main thread, and screenshots from a
third thread once the records have landed.

The screenshot is embedded in `docs/readme/title.md` and appears on the README front page.