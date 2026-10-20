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

### Phase 0: Frontend Scaffold + Elegance Foundations (Day 1)
**Goal**: Build scaffold, backend fixes, AND elegance infrastructure (registries, codegen, serializers)

**Tasks**:
1. **Backend Critical Fixes** (web.py):
   - Add `read_only` to `DashboardConfig`
   - Add `/api/campaigns/{id}/metrics` endpoint (thin wrapper around `ReportGenerator`)
   - Extend WebSocket broadcast: `campaign_metrics` + `pipeline_event`
   - All store access uses `read_only=True`

2. **Elegance Infrastructure** (New — Do First):
   - **`scripts/generate_palette.py`** → generates `_palette.py` (Python), `palette.ts` (three.js), `palette.css` (HTML)
   - **`scripts/generate_axis_metadata.py`** → generates `axis-metadata.json` from Python `StructuralAxis` registries
   - **`ReportGenerator.get_ablation_groups()`** → structured ablation data for API
   - **`RecordSerializer`** (`evidence/serializers.py`) → single serialization point
   - **`MessageRouter` base class** (`src/ws-client.ts`) → components self-register handlers
   - **`ComponentRegistry` base class** (`src/components/registry.ts`) → auto-discovery

3. **Frontend Scaffold**:
   - `package.json` — deps: `three`, `three-stdlib`, `uplot` (fast, lightweight, Canvas 2D)
   - `tsconfig.json`, `vite.config.ts` (output to `../templates/static/js/dashboard.js`)
   - `src/main.ts` — three.js boilerplate, uses `ComponentRegistry` auto-init
   - `src/ws-client.ts` — `MessageRouter` with auto-reconnect
   - `src/style.ts` — imports generated `palette.ts`

4. **Rewrite `index.html`** — minimal:
   ```html
   <canvas id="dashboard-canvas"></canvas>
   <div id="ui-overlay"></div>
   <script type="module" src="/static/js/dashboard.js"></script>
   ```

**Acceptance**: 
- `npm run build` produces `dashboard.js`
- `uv run comp dashboard` launches with WebSocket + 3 critical endpoints
- Palette/axis metadata generated from single Python source
- Components use registries from Day 1 (zero boilerplate additions later)

---

### Phase 1: Discovery Map — 3D Fog-of-War
**Goal**: The core visual — 3D grid of cells showing measured/legal/void

**Data Source**: `/api/queue` → campaigns → `/api/campaigns/{id}` → records from store

**Implementation** (`src/discovery-map.ts`):
1. **Grid layout**: 3 axes visible at once (configurable: credit × geometry × dynamics)
   - X: credit arms (gradient, pepita, random_projections, local_goodness, ...)
   - Y: geometry (feedforward, recurrent, ntm, nca, ...)
   - Z: dynamics (instantaneous, energy_minimization, predictive_settling, ...)
2. **Cell representation** (`CellMesh`):
   ```typescript
   // Measured: glowing pillar
   const geometry = new BoxGeometry(0.8, height, 0.8);
   const material = new MeshStandardMaterial({ 
     color: armColor, 
     emissive: armColor, 
     emissiveIntensity: 0.5,
     transparent: true, opacity: 0.9 
   });
   // Height = val_acc (0.0-1.0) scaled to 0.5-3.0 units
   ```
   - **Legal/unmeasured**: `WireframeBoxGeometry`, semi-transparent, hover → tooltip with price
   - **Void**: Red `X` marker (`Line2` cross), no interaction
3. **Interaction**:
   - OrbitControls: rotate, zoom, pan
   - Raycaster on click → select cell → open Cell Drawer
   - Hover highlight (emissiveIntensity pulse)
4. **Legend**: HTML overlay showing arm colors, measured/legal/void key
5. **Axis labels**: Text sprites on grid edges

**Acceptance**: Discovery Map renders 4×3×3 grid (36 cells) for demo campaign; measured cells glow with correct heights; click opens Cell Drawer.

---

### Phase 2: Cell Drawer — Detail Panel
**Goal**: Rich detail for selected cell (HTML overlay, not WebGL — easier for text)

**Implementation** (`src/cell-drawer.ts`):
1. **Slide-in panel** (right side, 350px, animated)
2. **Content**:
   - Coordinate badge: `credit=pepita, geometry=feedforward, dynamics=instantaneous, ...`
   - Metrics: `val_acc = 0.444 ± 0.115 (n=5)` — glowing monospace
   - Chance line: `chance = 0.10` — red dashed line on mini sparkline
   - Verdict: `INSUFFICIENT` amber banner / `PASSED` green / `REJECTED` red
   - Seeds to claim: `58 seeds to claim (d=0.5)`
   - **Mini 3D sparkline**: training curve (loss/acc over epochs) — small three.js scene in panel
3. **Actions** (v1 visual only): `[queue rest] [preregister] [adopt as quest]`

**Acceptance**: Click any measured cell → panel slides in with correct data; sparkline renders.

---

### Phase 3: Plotter — Charts First (uPlot), Custom 3D Later
**Goal**: Working interactive charts NOW (uPlot), custom three.js 3D as v2 polish

**Chart Library**: **uPlot** — 25KB, 60fps, Canvas 2D, no deps, excellent for time-series/scatter/bars
- Pareto: scatter (val_acc vs 1/walltime_s), color=arm, Pareto points = larger
- Ablation: grouped bars (credit arm × val_acc), chance line = horizontal rule
- Seed Variability: box plots or violin (uPlot hooks) per arm

**Implementation** (`src/plotter.ts`):
- Three `<canvas>` elements (or one, switched via tabs)
- uPlot instances per chart, data from `/api/campaigns/{id}/metrics`
- Toolbar: pan/zoom, reset, download PNG
- Tooltip: shows n, mean±std, chance line value

**Custom 3D (Deferred to v2)**:
- Pareto: 3D scatter (val_acc, 1/walltime_s, 1/param_count)
- Ablation: 3D bars + chance plane
- Seed Variability: 3D violin plots

**Acceptance**: Three tabs render instantly with real data, interactive pan/zoom, tooltips show n/mean/std.

---

### Phase 4: Live Rail & HUD — Mission Control Feel
**Goal**: The "alive" feeling — data flowing, resources burning

**Live Rail** (bottom, WebGL text):
```
[OK] compose joint system  [OK] settle energy  [WARN] control at chance  [OK] record appended
```
- Source: WebSocket `status_update` messages (extend `web.py` to broadcast pipeline events)
- three.js `TextGeometry` or HTML overlay with CSS animation

**HUD** (top-right, 3D bars):
- GPU: 3D bar, fill = utilization, color = blue
- CPU: green bar
- Memory: amber bar
- Burn rate: `34s / 120s` (glowing monospace)
- Claim price: `63 seeds/arm` (always visible)

**Mode Chip** (top-left):
- `EXPLORATORY` (amber) / `PREREGISTERED` (green)
- From run spec `preregistered` flag

**Acceptance**: Dashboard feels alive — resources pulse, live rail scrolls, mode chip shows correct state.

---

### Phase 5: Campaign Launch & Hero Screenshot
**Goal**: Real campaign running → authentic screenshot

**Tasks**:
1. **Extend `web.py`** — add `/api/campaigns/{id}/metrics` endpoint returning records for Plotter
2. **Create `scripts/launch_demo_campaign.py`**:
   ```python
   # Launch campaign queue in background
   # Submit demo campaign (4 credit arms, 5 seeds)
   # Wait for first records to land
   # Launch dashboard
   ```
3. **Create `scripts/capture_dashboard_screenshot.py`** (Playwright):
   ```python
   # 1. Start campaign (subprocess)
   # 2. Start dashboard (subprocess)
   # 3. Wait for WebSocket + first records
   # 4. Playwright: navigate, wait for three.js render
   # 5. Screenshot 1920x1080 → docs/readme/assets/dashboard-hero.png
   # 6. Kill both subprocesses
   ```
4. **Add to `docs/readme/title.md`**:
   ```markdown
   ![Computronium Dashboard](assets/dashboard-hero.png)
   
   *Computronium is a composable laboratory for learning mechanisms. Watch algorithms battle it out under a neutral, pre-registered evaluation protocol.*
   ```
5. **Regenerate README**: `uv run python docs/readme/build_readme.py`

**Acceptance**: Screenshot shows live campaign mid-run with INSUFFICIENT verdict visible, 3D Discovery Map glowing, resources burning.

---

### Phase 6: Polish, Test, Document
**Goal**: Zero-friction launch

**Tasks**:
1. **Add `dashboard` to `CORE_COMMANDS`** in `cli.py`
2. **Update README "Start here"**:
   ```bash
   uv run comp dashboard --store experiment.duckdb
   # In another terminal:
   uv run comp run demo --store experiment.duckdb
   ```
3. **Run full flow** — verify end-to-end
4. **Write `docs/DASHBOARD.md`** — guide to 3D UI, controls, reading the maps

---

## Technical Specifications

### Files to Create/Modify

| File | Change |
|------|--------|
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
        for campaign in campaigns.get('campaigns', []):
            if campaign['status'] == 'running':
                metrics = await self._get_campaign_metrics(campaign['campaign_id'])
                await self._broadcast_update({
                    "type": "campaign_metrics",
                    "campaign_id": campaign['campaign_id'],
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

- [ ] `npm run build` in dashboard dir produces `dashboard.js` (< 500KB gzipped)
- [ ] `uv run comp dashboard --store experiment.duckdb` launches three.js dashboard
- [ ] **Backend**: `/api/campaigns/{id}/metrics` returns records + Pareto flags
- [ ] **Backend**: WebSocket broadcasts `campaign_metrics` for running campaigns
- [ ] **Backend**: All dashboard store access uses `read_only=True`
- [ ] `uv run comp run demo --store experiment.duckdb` populates live data
- [ ] Discovery Map: 3D grid, measured cells glow, click → Cell Drawer
- [ ] Cell Drawer: metrics, sparkline, verdict, seeds-to-claim
- [ ] Plotter: 3 tabs (Pareto, Ablation, Variability) via uPlot, interactive pan/zoom/tooltips
- [ ] Live Rail: scrolling pipeline events (mock for v1)
- [ ] HUD: GPU/CPU/memory 3D bars, burn rate, claim price
- [ ] `scripts/capture_dashboard_screenshot.py` produces `dashboard-hero.png` (1920×1080)
- [ ] `docs/readme/title.md` has hero image + tagline
- [ ] `comp --help` shows `dashboard` command
- [ ] `docs/DASHBOARD.md` explains the 3D UI

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