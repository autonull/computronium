# TODO68: Hero Dashboard — Development Plan (Real Dashboard, three.js)

**Objective**: Build the real live monitoring dashboard with three.js WebGL visualization. Campaign queue, WebSockets, 3D fog-of-war, interactive plots. Take a hero screenshot and put it on the README front page.

**Source Vision**: TODO67.md — "Make the dashboard look incredible, take a screenshot, and put it on the front page."

**Key Decision**: No "demo mode." One dashboard that works for live campaigns. The backend (`web.py`, `CampaignQueue`) already exists — we build the three.js frontend.

---

## Current State Analysis

### What Exists ✅ (Backend — 90% Done)
| Component | Path | Status |
|-----------|------|--------|
| FastAPI + WebSocket server | `computronium/experiment/execution/dashboard/web.py` | Complete: `/ws`, `/api/queue`, `/api/resources`, `/api/campaigns`, broadcast loop |
| Campaign Queue | `computronium/experiment/execution/campaign_queue.py` | Complete: queue, running, completed, resource usage, cancel/preempt |
| CLI command | `comp dashboard --store experiment.duckdb` | Registered, launches server on port 8080 |
| Record Store | `computronium/experiment/evidence/store.py` | DuckDB, single-writer, full query API |
| Report Generator | `comp report` | Ablation, Pareto, limitations, claims |

### What's Missing ❌ (Frontend — 0% Done)
| Gap | Impact |
|-----|--------|
| No three.js frontend | The hero visual doesn't exist |
| Template is generic monitoring (876 lines) | Wrong mental model — needs 3D mission control |
| No 3D fog-of-war / discovery map | Core visual from TODO67 missing |
| No interactive 3D plots (Pareto, ablation, seed variability) | Static SVG can't do this justice |
| No WebGL screenshot pipeline | Hero image needs Playwright + Chromium GPU |
| No campaign launch for screenshot | Need real campaign running for live data |

---

## Architecture (Backend Ready, Frontend Needed)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  CampaignQueue                                                          │
│    ├─ _queue / _running / _completed                                    │
│    ├─ get_resource_usage() → {gpu, cpu, memory}                        │
│    └─ cancel/preempt endpoints                                          │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │ WebSocket push (2s interval)
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  WebDashboard (web.py)                                                  │
│    ├─ _connected_websockets: Set[WebSocket]                            │
│    ├─ _broadcast_update(status, queue)                                 │
│    ├─ REST: /api/queue, /api/resources, /api/campaigns/{id}            │
│    └─ Static file serving: /static/js/dashboard.js                     │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │ three.js frontend (new)
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Browser: three.js Scene + uPlot Canvases                                 │
│    ├─ Discovery Map: 3D grid (fog-of-war)                               │
│    │   ├─ Measured: glowing pillars (height=val_acc, color=arm)        │
│    │   ├─ Legal/unmeasured: wireframe cubes (hover=price)              │
│    │   └─ Void: red X markers                                          │
│    ├─ Cell Drawer: HTML overlay panel (detail on click)                │
│    ├─ Plotter: uPlot canvases (Pareto, Ablation, Variability)          │
│    │   ├─ Pareto: scatter (val_acc vs 1/walltime_s), Pareto highlighted│
│    │   ├─ Ablation: grouped bars + chance line                          │
│    │   └─ Seed Variability: box/violin plots per arm                   │
│    ├─ Live Rail: HTML overlay (bottom)                                  │
│    └─ HUD: 3D resource bars (top-right)                                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Phased Development Plan (Dependency-Ordered)

### Phase 0: Frontend Scaffold + Elegance Foundations (Day 1) ✅ COMPLETE
**Goal**: Build scaffold, backend fixes, AND elegance infrastructure (registries, codegen, serializers)

**Tasks**:
1. **Backend Critical Fixes** (web.py): ✅
   - Added `read_only` to `DashboardConfig`
   - Added `/api/campaigns/{id}/metrics` endpoint (thin wrapper around `ReportGenerator`)
   - Extended WebSocket broadcast: `campaign_metrics` + `pipeline_event`
   - All store access uses `read_only=True`

2. **Elegance Infrastructure** (New — Do First): ✅
   - **`scripts/generate_palette.py`** → generates `_palette.py` (Python), `palette.ts` (three.js), `palette.css` (HTML)
   - **`scripts/generate_axis_metadata.py`** → generates `axis-metadata.json` from Python registries
   - **`ReportGenerator.get_ablation_groups()`** → structured ablation data for API
   - **`RecordSerializer`** (`evidence/serializers.py`) → single serialization point
   - **`MessageRouter` base class** (`src/ws-client.ts`) → components self-register handlers
   - **`ComponentRegistry` base class** (`src/components/registry.ts`) → auto-discovery

3. **Frontend Scaffold**: ✅
   - `package.json` — deps: `three`, `three-stdlib`, `uplot` (fast, lightweight, Canvas 2D)
   - `tsconfig.json`, `vite.config.ts` (output to `../templates/static/js/dashboard.js`)
   - `src/main.ts` — three.js boilerplate, uses `ComponentRegistry` auto-init
   - `src/ws-client.ts` — `MessageRouter` with auto-reconnect
   - `src/style.ts` — imports generated `palette.ts`

4. **Rewrite `index.html`** — minimal: ✅
   ```html
   <canvas id="dashboard-canvas"></canvas>
   <div id="ui-overlay"></div>
   <script type="module" src="/static/js/dashboard.js"></script>
   ```

**Acceptance**: ✅ ALL MET
- `npm run build` produces `dashboard.js` (595KB, 163KB gzipped)
- `uv run comp dashboard` launches with WebSocket + 3 critical endpoints
- Palette/axis metadata generated from single Python source
- Components use registries from Day 1 (zero boilerplate additions later)

**Notes**:
- TypeScript strict mode required `@ts-ignore` for one property narrowing issue in HUD (known TS limitation with `this.property` access in callbacks)
- Frontend uses `ComponentRegistry` for auto-discovery and `MessageRouter` for WebSocket message routing
- All components register themselves on import via `registry.register(new Component())`

---

### Phase 1: Discovery Map — 3D Fog-of-War ✅ IMPLEMENTED
**Goal**: The core visual — 3D grid of cells showing measured/legal/void

**Data Source**: `/api/queue` → campaigns → `/api/campaigns/{id}` → records from store

**Implementation** (`src/discovery-map.ts`): ✅
1. **Grid layout**: 3 axes visible at once (configurable: credit × geometry × dynamics)
   - X: credit arms (gradient, pepita, random_projections, local_goodness, ...)
   - Y: geometry (feedforward, recurrent, ntm, nca, ...)
   - Z: dynamics (instantaneous, energy_minimization, predictive_settling, ...)
2. **Cell representation** (`CellMesh`):
   - **Measured**: Glowing pillars with height = val_acc (0.5-3.0 units), emissive material, pulse animation
   - **Legal/unmeasured**: `LineSegments` wireframe cubes, semi-transparent
   - **Void**: Red `X` marker (`Line`), no interaction
3. **Interaction**:
   - OrbitControls: rotate, zoom, pan
   - Raycaster on click → select cell → open Cell Drawer
   - Hover highlight (emissiveIntensity pulse)
4. **Legend**: HTML overlay showing arm colors, measured/legal/void key
5. **Axis labels**: Text sprites on grid edges

**Acceptance**: Discovery Map renders 4×1×1 grid for demo campaign; measured cells glow with correct heights; click opens Cell Drawer.

**Notes**: 
- Uses `THREE.Sprite` for axis labels (text rendering)
- Cell data updated via WebSocket `campaign_metrics` messages
- Pareto frontier cells get highlight ring

---

### Phase 2: Cell Drawer — Detail Panel ✅ IMPLEMENTED
**Goal**: Rich detail for selected cell (HTML overlay, not WebGL — easier for text)

**Implementation** (`src/cell-drawer.ts`): ✅
1. **Slide-in panel** (right side, 380px, animated)
2. **Content**:
   - Coordinate badges with credit arm color coding
   - Metrics: `val_acc = 0.444 ± 0.115 (n=5)` — large monospace
   - Chance line: `chance = 0.10` — progress bar with color gradient (red→amber→green)
   - Verdict: `INSUFFICIENT` amber / `PASSED` green / `REJECTED` red banner
   - Seeds to claim calculation (simplified)
   - Wall time and parameter count
   - **Mini 3D sparkline**: training curve (val_acc over epochs) with chance line — small three.js scene in panel
3. **Actions** (v1 visual only, disabled): `[queue rest] [preregister] [adopt as quest]`

**Acceptance**: Click any measured cell → panel slides in with correct data; sparkline renders.

**Notes**: 
- Uses `CustomEvent` for cell selection communication
- Sparkline uses `THREE.OrthographicCamera` for 2D-like rendering
- Verdict logic: PASSED (>chance+0.1), INSUFFICIENT (>chance), REJECTED (≤chance)

---

### Phase 3: Plotter — Charts First (uPlot), Custom 3D Later ✅ IMPLEMENTED
**Goal**: Working interactive charts NOW (uPlot), custom three.js 3D as v2 polish

**Chart Library**: **uPlot** — 25KB, 60fps, Canvas 2D, no deps, excellent for time-series/scatter/bars
- Pareto: scatter (val_acc vs 1/walltime_s), color=arm, Pareto points highlighted with Pareto color, frontier line dashed
- Ablation: grouped bars (credit arm × val_acc), error bars, chance line = horizontal dashed rule
- Seed Variability: box plots per arm (whiskers, box, median, outliers), chance line

**Implementation** (`src/plotter.ts`): ✅
- Three `<canvas>` elements (switched via tabs: Pareto / Ablation / Variability)
- uPlot instances per chart, data from WebSocket `campaign_metrics`
- Toolbar: download PNG, status indicator
- Custom draw hooks for Pareto frontier line, ablation bars, variability box plots
- Chance line at 0.10 (digits task) on all charts

**Custom 3D (Deferred to v2)**:
- Pareto: 3D scatter (val_acc, 1/walltime_s, 1/param_count)
- Ablation: 3D bars + chance plane
- Seed Variability: 3D violin plots

**Acceptance**: Three tabs render instantly with real data, interactive pan/zoom, tooltips show n/mean/std.

**Notes**:
- uPlot API uses `valToPos` for coordinate conversion in draw hooks
- Ablation chart uses `setTitle` workaround (direct opts mutation + redraw)
- Variability chart computes quartiles on-the-fly in draw hook

---

### Phase 4: Live Rail & HUD — Mission Control Feel ✅ IMPLEMENTED
**Goal**: The "alive" feeling — data flowing, resources burning

**Live Rail** (bottom, HTML overlay): ✅ (`src/live-rail.ts`)
```
[14:32:15] ✓ [s6_train] compose joint system
[14:32:13] ✓ [s5_compose] settle energy
[14:32:10] ⚠ [s4_gate] control at chance
```
- Source: WebSocket `pipeline_event` + `status_update` messages
- HTML overlay with animated pills, connection status indicator

**HUD** (top-right, 3D Sprites): ✅ (`src/hud.ts`)
- GPU/CPU/MEM: 3D bars with animated fill, labels, percentage values
- Pulse animation on active resources (emissiveIntensity)
- Burn rate: `34s / 120s` with pulse animation when running
- Claim price: `63 seeds/arm` (static for demo)

**Mode Chip** (top-left, 3D Sprite): ✅
- `EXPLORATORY` (amber) / `PREREGISTERED` (green) — static for demo

**Acceptance**: Dashboard feels alive — resources pulse, live rail scrolls, mode chip shows correct state.

**Notes**:
- Uses `THREE.Sprite` with `CanvasTexture` for all text (crisp, no WebGL font issues)
- Resource bars animate width smoothly via `THREE.MathUtils.lerp`
- Burn rate and claim price update via canvas texture regeneration

---

### Phase 5: Campaign Launch & Hero Screenshot ✅ COMPLETE
**Goal**: Real campaign running → authentic screenshot

**Tasks**:
1. **Created `scripts/launch_demo_campaign.py`** — launches campaign queue, submits demo campaign, waits for records
2. **Rewrote `scripts/capture_dashboard_screenshot.py`** (Playwright) — dashboard, campaign and capture in ONE process; waits for the records to land; captures 1920x1080 with `--use-gl=angle` + SwiftShader
3. **Updated `docs/readme/title.md`** — added hero image placeholder + tagline
4. **Regenerated README** — `uv run python docs/readme/build_readme.py`
5. **Added `playwright>=1.40.0`, `websockets>=13.0`, `aiohttp>=3.9` to dev dependencies** in `pyproject.toml`

**Acceptance**: ✅ ALL MET
- Backend: Campaign launch + dashboard data flow verified (20 records, 6 Pareto points, ablation groups broadcast via WS)
- Screenshot: `docs/readme/assets/dashboard-hero.png` (1920×1080) shows the live scene — four glowing pillars, the Pareto frontier and chance line, the mission-control panel with measured numbers, the legend and the live rail
- The built bundle is committed and shipped: `templates/static/js/dashboard.js` + `main.css`, with `pyproject.toml` package-data covering `dashboard/templates/**/*`

**Notes**:
- The dashboard, the campaign and the capture run in ONE process on purpose: DuckDB gives one writer the file, and a read-only connection cannot join a read-write one — not even in the same process. A dashboard in another terminal sees nothing until the writer lets go.
- Headless WebGL via `--use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader` (software rasterizer) for CI compatibility
- The capture polls the dashboard's `/api/runs` (new endpoint) for the record count rather than opening the store itself

---

### Phase 6: Polish, Test, Document ✅ COMPLETE
**Goal**: Zero-friction launch

**Tasks**:
1. **Added `dashboard` to `CORE_COMMANDS`** in `cli.py` — now visible in `comp --help`
2. **Updated README "Start here"** in `docs/readme/start-here.md` — added live dashboard launch instructions
3. **Verified end-to-end** — dashboard creation, route registration, palette/axis metadata generation
4. **Created `docs/DASHBOARD.md`** — comprehensive guide to 3D UI, controls, WebSocket types, architecture
5. **Added console dashboard** (`console.py`) — text-based live monitoring for debugging/headless environments
6. **Added `--console` flag** to `comp dashboard` command — run without browser

**Notes**: 
- Dashboard command was already registered in CLI, now promoted to core visibility
- All imports pass layering/isolation locks (`tests/property/test_full_import_isolation_lock.py`, `test_layering_lock.py`)
- Frontend builds: `npm run build` → `dashboard.js` (595KB, 163KB gzipped)
- Console dashboard uses `rich` for terminal UI, shows queue, resources, metrics (Pareto/ablation/variability), recent records

---

## Technical Specifications

### Files to Create/Modify

| File | Change |
|------|--------|
| `computronium/experiment/execution/dashboard/console.py` | **New** — console-based live monitoring dashboard (rich TUI) |
| `computronium/experiment/execution/dashboard/package.json` | **New** — three.js, three-stdlib, uPlot, vite, typescript |
| `computronium/experiment/execution/dashboard/tsconfig.json` | **New** |
| `computronium/experiment/execution/dashboard/vite.config.ts` | **New** |
| `computronium/experiment/execution/dashboard/src/main.ts` | **New** — three.js entry, uses ComponentRegistry |
| `computronium/experiment/execution/dashboard/src/discovery-map.ts` | **New** — 3D fog-of-war, registers with MessageRouter |
| `computronium/experiment/execution/dashboard/src/cell-drawer.ts` | **New** — HTML overlay panel |
| `computronium/experiment/execution/dashboard/src/plotter.ts` | **New** — uPlot charts (Pareto, Ablation, Variability) |
| `computronium/experiment/execution/dashboard/src/live-rail.ts` | **New** — bottom log, registers with MessageRouter |
| `computronium/experiment/execution/dashboard/src/hud.ts` | **New** — top-right resources, registers with MessageRouter |
| `computronium/experiment/execution/dashboard/src/ws-client.ts` | **New** — MessageRouter base class + auto-reconnect |
| `computronium/experiment/execution/dashboard/src/components/registry.ts` | **New** — ComponentRegistry for auto-discovery |
| `computronium/experiment/execution/dashboard/src/style.ts` | **New** — imports generated `palette.ts` |
| `computronium/experiment/execution/dashboard/templates/index.html` | **Rewrite** — minimal, loads dashboard.js |
| `computronium/experiment/execution/dashboard/web.py` | **Critical**: add 3 endpoints + WebSocket extensions + read_only |
| `computronium/experiment/evidence/serializers.py` | **New** — RecordSerializer (single source) |
| `computronium/experiment/surface/report.py` | Add `get_ablation_groups()` method |
| `scripts/generate_palette.py` | **New** — generates `_palette.py`, `palette.ts`, `palette.css` |
| `scripts/generate_axis_metadata.py` | **New** — generates `axis-metadata.json` from Python registries |
| `pyproject.toml` | Add `playwright` (dev extra) |
| `scripts/launch_demo_campaign.py` | **New** |
| `scripts/capture_dashboard_screenshot.py` | **New** — Playwright + WebGL |
| `docs/readme/title.md` | Hero image + tagline |
| `docs/DASHBOARD.md` | **New** — user guide |

### Critical Backend Changes (web.py) — **Must Do First**

```python
# 1. Add read_only to DashboardConfig
@dataclass(frozen=True, slots=True)
class DashboardConfig:
    ...
    read_only: bool = False  # NEW


# 2. Add RecordSerializer import and usage
from computronium.experiment.evidence.serializers import serializer


# 3. New REST endpoint for per-cell metrics (thin wrapper)
@app.get("/api/campaigns/{campaign_id}/metrics")
async def api_campaign_metrics(campaign_id: str) -> JSONResponse:
    if not config.store_path:
        return JSONResponse({"error": "No store path configured"})
    store_config = StoreConfig(path=Path(config.store_path), read_only=True)  # CRITICAL
    store = RecordStore(store_config)
    with store:
        generator = ReportGenerator(store)
        records = list(generator._store.query_records(run_id=campaign_id))

        # Reuse ReportGenerator logic
        pareto_points, _ = compute_pareto_frontier(records, ["val_acc", "walltime_s"])
        pareto_ids = {p["record_id"] for p in pareto_points}

        ablation_groups = generator.get_ablation_groups(campaign_id)

        return JSONResponse({
            "records": [serializer.to_api_dict(r) for r in records],
            "pareto": [r.record_id in pareto_ids for r in records],
            "ablation_groups": ablation_groups,
        })


# 4. Extend WebSocket broadcast in _update_loop()
async def _update_loop(self) -> None:
    while self._running:
        await asyncio.sleep(self.config.update_interval)
        ...
        # NEW: Broadcast per-campaign metrics for running campaigns
        campaigns = await self._get_all_campaigns()
        for campaign in campaigns.get("campaigns", []):
            if campaign["status"] == "running":
                metrics = await self._get_campaign_metrics(campaign["campaign_id"])
                await self._broadcast_update({
                    "type": "campaign_metrics",
                    "campaign_id": campaign["campaign_id"],
                    "data": metrics,
                    "timestamp": datetime.now().isoformat(),
                })
        # NEW: Broadcast pipeline events (mock for v1)
        await self._broadcast_update({
            "type": "pipeline_event",
            "stage": "s6_train",
            "message": "compose joint system",
            "level": "ok",
            "timestamp": datetime.now().isoformat(),
        })
```

### WebSocket Message Types (Extended) — Handled via MessageRouter

```typescript
// src/types/ws-messages.ts — Single source (manual for v1, codegen for v2)
export interface StatusUpdate {
  type: 'status_update';
  data: StatusData;
}

export interface QueueUpdate {
  type: 'queue_update';
  data: QueueData;
}

export interface CampaignMetrics {
  type: 'campaign_metrics';
  campaign_id: string;
  data: CampaignMetricsData;
}

export interface PipelineEvent {
  type: 'pipeline_event';
  stage: string;
  message: string;
  level: 'ok' | 'warn' | 'error';
}

export type WSMessage = StatusUpdate | QueueUpdate | CampaignMetrics | PipelineEvent;

// In components — self-register (no central switch):
// src/discovery-map.ts
router.register('queue_update', this.onQueueUpdate.bind(this));
router.register('campaign_metrics', this.onMetrics.bind(this));

// src/live-rail.ts
router.register('pipeline_event', this.onPipelineEvent.bind(this));

// src/hud.ts
router.register('status_update', this.onStatus.bind(this));
```

**Benefits**: Zero boilerplate in `ws-client.ts`, components declare dependencies explicitly, testable.

### Color Palette — Generated from Single Source

**Source**: `scripts/generate_palette.py` → reads `PALETTE_SOURCE` dict

**Outputs**:
- `computronium/visualization/_palette.py` — Python dict (for matplotlib backend)
- `src/palette.ts` — TypeScript const (for three.js)
- `templates/static/css/palette.css` — CSS variables (for HTML overlays)

```typescript
// src/style.ts — IMPORTS GENERATED PALETTE
import { PALETTE } from './palette.js';  // generated

export const PALETTE; // re-export

// CSS variables (in palette.css):
:root {
  --bg: #0a0e14;
  --grid: #1f2a3a;
  --measured: #d4a843;
  --arms-gradient: #58a6ff;
  --arms-pepita: #d4a843;
  /* ... */
}
```

**Benefits**: One source → Python/TS/CSS always in sync. New arm color = one dict entry.

### Data Flow Summary

```
CampaignQueue (global singleton)
    │
    ├─► WebDashboard._get_queue_status() → WebSocket queue_update (2s)
    │
    └─► CampaignQueue._run_campaign() → RecordStore.append() → DuckDB
                                          │
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

---

### Elegance Patterns (Active from Phase 0)

| Pattern | Implementation | Benefit |
|---------|----------------|---------|
| **MessageRouter** | `src/ws-client.ts` — components `router.register('type', handler)` | Zero boilerplate, explicit deps |
| **ComponentRegistry** | `src/components/registry.ts` — auto-discovery + `init`/`destroy` | No `main.ts` edits for new components |
| **Palette Codegen** | `scripts/generate_palette.py` → `_palette.py`, `palette.ts`, `palette.css` | Single source for Python/TS/CSS |
| **Axis Metadata Codegen** | `scripts/generate_axis_metadata.py` → `axis-metadata.json` | Python registries → frontend |
| **RecordSerializer** | `evidence/serializers.py` → `serializer.to_api_dict(record)` | One serialization logic |
| **ReportGenerator Reuse** | `get_ablation_groups()` + `compute_pareto_frontier()` | API = thin wrapper, zero logic dup |

These patterns are established in Phase 0 — components use them from Day 1 with zero boilerplate additions later.

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| three.js bundle size | Vite tree-shaking; ~150KB gzipped acceptable |
| WebGL not available in CI | Playwright with `--use-gl=angle` (software rasterizer) |
| Campaign + dashboard port conflict | Dashboard on 8080, campaign uses store only |
| Screenshot timing flaky | Poll `/api/queue` until `running > 0`, then wait 2s for render |
| Mobile performance | Desktop-only for v1; responsive not required |
| Font rendering in WebGL | Use HTML overlay for all text (Cell Drawer, HUD, Live Rail) — only geometry in three.js |
| **Custom 3D chart complexity** | **uPlot for v1 (25KB, Canvas 2D, instant)** — 3D deferred to v2 |
| **Store lock contention** | **`StoreConfig(read_only=True)` for ALL dashboard store access** |
| **Missing per-cell metrics endpoint** | **Add `/api/campaigns/{id}/metrics` in Phase 0** |
| **WebSocket missing campaign_metrics** | **Extend `_update_loop()` broadcast in Phase 0** |
| CampaignQueue doesn't emit pipeline events | Live Rail shows static mock for v1; extend queue in v2 |

---

## Definition of Done

- [x] `npm run build` in dashboard dir produces `dashboard.js` (< 500KB gzipped) — 163KB gzipped
- [x] `uv run comp dashboard --store experiment.duckdb` launches three.js dashboard
- [x] **Backend**: `/api/campaigns/{id}/metrics` returns records + Pareto flags + chance + required seeds + measured resources
- [x] **Backend**: `/api/runs` lists the store's runs with their record counts
- [x] **Backend**: WebSocket broadcasts `campaign_metrics` for running campaigns
- [x] **Backend**: All dashboard store access uses `read_only=True` (falling back to read-write only for an in-process writer)
- [x] `uv run comp run demo --store experiment.duckdb` populates live data
- [x] Discovery Map: 3D grid, measured cells glow, click → Cell Drawer
- [x] Cell Drawer: metrics, sparkline, verdict, seeds-to-claim
- [x] Plotter: 3 tabs (Pareto, Ablation, Variability) via uPlot, interactive pan/zoom/tooltips
- [x] Live Rail: scrolling pipeline events (mock for v1)
- [x] Mission control panel: device, memory, walltime, records, queue quota, seeds-to-claim
- [x] `scripts/capture_dashboard_screenshot.py` produces `dashboard-hero.png` (1920×1080) with real data on screen
- [x] `docs/readme/title.md` has hero image + tagline
- [x] `comp --help` shows `dashboard` command
- [x] `docs/DASHBOARD.md` explains the 3D UI

---

## Out of Scope (Explicitly Deferred)

- ❌ Write capability (queue/preregister buttons functional) — v2
- ❌ Multi-user / auth — v2
- ❌ Historical replay / time-travel — v3
- ❌ Mobile touch controls — v2
- ❌ Custom shader effects (bloom, SSAO) — v2 polish
- ❌ Custom three.js 3D charts (Pareto 3D scatter, Ablation 3D bars, Violin 3D) — v2, uPlot works for v1

---

## Quick Reference: Demo Campaign Contract

The demo profile (`RUN_PROFILES["demo"]` in `cli.py`) guarantees:
- **4 credit arms**: `gradient`, `random_projections`, `pepita`, `local_goodness`
- **5 seeds each**: n=5 per cell
- **Fixed axes**: substrate=digital, geometry=feedforward, dynamics=instantaneous, plasticity=null, update=adam
- **Task**: digits (10 classes, chance=0.10)
- **Fidelity**: L1, 3 epochs
- **Budget**: 120s (actual ~34s)
- **Verdict**: INSUFFICIENT (63 seeds needed for d=0.5)

This contract is locked by `tests/acceptance/test_demo_script.py` — the dashboard displays this live.
---

## Session Progress — Hero Screenshot Completion (2026-10-20)

The plan's phases 0–4 were implemented but never actually ran: the dashboard
served a blank page, and the hero screenshot was a white PNG. This session
made the dashboard real and produced the image.

### What was broken (and why the screenshot was blank)

| # | Defect | Cause |
|---|--------|-------|
| 1 | `/static/js/dashboard.js` 404 | `web.py` mounted `/static` from `dashboard/static` (no such directory); the build writes to `dashboard/templates/static/js/` |
| 2 | White page, no styles | `index.html` linked no stylesheet, and `src/style.ts` — which carried the global CSS — was imported by nothing, so it was dead code |
| 3 | Every cell stayed "legal" | The API returned the six axes flat; the frontend read `record.coordinate.credit`. `to_api_dict` now emits a nested `coordinate` (the shape `to_minimal_dict` and `console.py` already used) |
| 4 | No Pareto highlights | The frontier was computed over `["val_acc", "walltime_s"]` — payload keys, not objective names — so it was empty; and Pareto points are keyed by `measurement_key`, not `record_id` |
| 5 | Half the pillar underground | `createCell` overwrote the mesh's `y` after the geometry was positioned; the geometry is now translated so the base sits on the floor |
| 6 | Plotter showed an empty canvas | uPlot was handed a `<canvas>` target and builds its own DOM; the stray canvas took the space and the chart was pushed out of view. uPlot now gets a `<div>` |
| 7 | Every panel had two instances | Each component self-registered *and* `main.ts` registered its own copy, so every WebSocket message was handled twice — half by an uninitialized instance. Components now export one singleton |
| 8 | Legend and live rail overlapped | The legend sat under the 120px live rail; the axes were also set after the legend was built, so the legend's arm list was empty |
| 9 | Live rail read "Disconnected" over "Idle" | `childNodes[1]` was the dot, not the label (whitespace node); the label has its own element now |
| 10 | `router.unregister` never removed anything | `.bind(this)` makes a new function each call; the handlers are stable arrow properties now |
| 11 | A second store connection could not read | `RecordStore.__exit__` ran `CHECKPOINT` unguarded, which fails while another connection holds a write transaction; the checkpoint is best effort now |
| 12 | Two connections raced to create the schema | `_init_schema` ran on every read-write connection → "Catalog write-write conflict"; a connection now checks for the schema first |
| 13 | The HUD was a wall of giant sprites | 3D sprites scale with the camera, so HUD text was either unreadable or a slab across the screen. It is an HTML panel now — which is what the plan's own risk table asked for ("use HTML overlay for all text") |

### Design decisions worth keeping

- **One process for dashboard + campaign + capture.** DuckDB gives one writer
  the file, and a read-only connection cannot join a read-write one — not even
  in the same process, where DuckDB shares one instance per path. A dashboard
  in another terminal therefore shows nothing until the campaign finishes.
  The dashboard reads the store read-only, and falls back to read-write only
  when the writer is its own process. `docs/DASHBOARD.md` says so plainly.
- **Every number on screen is measured.** The mission-control panel reads
  `payload.memory_mb`, `payload.walltime_s`, `schedule.device` and the store's
  record count; the chance line comes from `chance_level(task_id, ...)`; the
  seeds-to-claim comes from `GateThresholds().required_seeds_per_group`; the
  per-cell accuracy is the mean ± std over that cell's seeds. Nothing is a
  placeholder constant any more.
- **`spec_from_profile` is public.** `comp run demo` and the capture pipeline
  now declare the same run through one function, so the screenshot cannot
  drift from the demo contract.

### Deviations from the plan

| Plan said | Now | Why |
|-----------|-----|-----|
| `src/style.ts` imports the generated palette | deleted; `templates/static/css/dashboard.css` carries the layout, `palette.css` the colors | `style.ts` was never imported — dead code — and a CSS file needs no runtime injection |
| HUD is 3D sprites | HUD is an HTML panel | sprites scale with the camera; the plan's risk table says to put text in the DOM |
| `read_only=True` everywhere | read-only first, read-write only for an in-process writer | DuckDB's single-writer lock makes read-only the only cross-process option, and the only in-process option is read-write |
| `scripts/launch_demo_campaign.py` drives the capture | the capture script owns the flow | one script, one process, no subprocess coordination |
| `Pareto` chart target is a canvas | a div | uPlot builds its own DOM |

### Remaining work (not part of this session)

- **Pipeline events are still mocked.** The live rail repeats "compose joint
  system" every 2s. The queue does not emit stage events; `CampaignQueue`
  would need to publish them and the dashboard would need to forward them.
- **The cell drawer has no sparkline data.** It renders the training curve
  from `payload.convergence_curve`, which the demo does not populate; the
  drawer shows an empty frame until a run records one.
- **Write capability.** The drawer's buttons (`queue rest`, `preregister`,
  `adopt as quest`) are still disabled, as planned for v1.
- **Multi-cell discovery.** The grid axes are hardcoded to the demo's four
  credit arms; the plan's "axes derived from data" is only partly true —
  `axis-metadata.json` carries the primitives, but the DiscoveryMap still
  seeds its axes from the demo profile.
- **Cross-process live monitoring** needs a store that tolerates a reader
  while a writer works (a copy-on-write snapshot, or the campaign writing
  through a service). Out of scope here; documented instead.
