# TODO68 Integration Review & Mental Simulation

**Purpose**: Exhaustive review of all integrations, development process simulation, UI walkthrough, flexibility analysis, and first-time user experience.

---

## 1. Integration Touchpoints Map

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        COMPLETE INTEGRATION GRAPH                                    │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  CLI: comp       │     │  CampaignQueue   │     │  RecordStore     │
│  dashboard       │────►│  (global singleton)     │  (DuckDB)        │
│  --store X       │     │                  │     │                  │
└────────┬─────────┘     └────────┬─────────┘     └────────┬─────────┘
         │                        │                        │
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           WebDashboard (web.py)                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Static Files│  │  REST API   │  │  WebSocket  │  │  Broadcast  │        │
│  │ /static/*   │  │ /api/*      │  │  /ws        │  │  Loop (2s)  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
│         │                │                │                │                 │
│         ▼                ▼                ▼                ▼                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Browser: three.js App                            │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │ Discovery│ │Cell Drawer│ │ Plotter  │ │Live Rail │ │   HUD    │  │   │
│  │  │   Map    │ │ (HTML)    │ │(three.js)│ │(HTML)    │ │(three.js)│  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Critical Integration Points

| # | Connection | Current State | Risk |
|---|------------|---------------|------|
| 1 | `comp dashboard` → `CampaignQueue` | `web.py:6196` gets global queue | ✅ Works |
| 2 | `CampaignQueue` → `RecordStore` | Queue runs campaigns, writes to store | ✅ Works |
| 3 | `WebDashboard` → `CampaignQueue` | `web.py:138` calls `queue.get_resource_usage()` | ✅ Works |
| 4 | `WebDashboard` → `RecordStore` | `web.py:248` opens store for metrics | ⚠️ **Lock contention** (see below) |
| 5 | `WebSocket` → `three.js` | `web.py:308-320` broadcasts status/queue | ✅ Works |
| 6 | `three.js` → REST `/api/campaigns/{id}/metrics` | **MISSING** - needs new endpoint | 🔴 **Gap** |
| 7 | `three.js` → Static `/static/js/dashboard.js` | `web.py:68-71` mounts `/static` | ⚠️ Build output path |
| 8 | `CampaignSpec` → Dashboard discovery map | Need to extract axis primitives from spec | 🔴 **Gap** |

---

## 2. Lock Contention Analysis (Critical)

### The Problem
```
Process A (comp run demo)          Process B (comp dashboard)
┌─────────────────────┐            ┌─────────────────────┐
│ RecordStore         │            │ RecordStore         │
│   _write_lock       │◄───BLOCK───│   _write_lock       │
│   (threading.RLock) │            │   (threading.RLock) │
└─────────────────────┘            └─────────────────────┘
       │                                    │
       ▼                                    ▼
  Writes records                      Reads for dashboard
  Every ~1-2s                         Every 2s (WebSocket)
```

**DuckDB single-writer**: Only one process can write. `RecordStore` uses `threading.RLock` for in-process safety, but **cross-process writes block each other at OS level**.

### Solution
```python
# In web.py _get_dashboard_view() and _get_campaign_metrics():
config = StoreConfig(path=Path(self.config.store_path), read_only=True)
store = RecordStore(config)
# read_only=True → DuckDB opens in read-only mode, no lock contention
```

**Must apply to ALL dashboard store accesses**.

---

## 3. Development Process Simulation (Step-by-Step)

### Phase 0: Frontend Scaffold

#### Step 0.1: Create package.json + Vite config
```bash
mkdir -p computronium/experiment/execution/dashboard/src
cd computronium/experiment/execution/dashboard
npm init -y  # → package.json
npm install three
npm install -D typescript vite @types/three
```

**Potential Issue**: Node.js not in environment.
**Fix**: `uv run` doesn't provide Node. Need system Node or `nvm`. Document in `docs/DASHBOARD.md`.

#### Step 0.2: Vite config output path
```typescript
// vite.config.ts
export default defineConfig({
  build: {
    outDir: '../templates/static/js',
    emptyOutDir: true,
    lib: {
      entry: 'src/main.ts',
      name: 'Dashboard',
      fileName: 'dashboard',
      formats: ['es']
    }
  }
})
```

**Potential Issue**: Vite lib mode + ES modules + three.js global.
**Fix**: Use `format: 'es'`, import three.js as `import * as THREE from 'three'`.

#### Step 0.3: TypeScript config
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src/**/*"]
}
```

#### Step 0.4: main.ts - Three.js boilerplate
```typescript
// src/main.ts
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { DiscoveryMap } from './discovery-map.js';
import { CellDrawer } from './cell-drawer.js';
import { Plotter } from './plotter.js';
import { LiveRail } from './live-rail.js';
import { HUD } from './hud.js';
import { WSClient } from './ws-client.js';
import { PALETTE } from './style.js';

const canvas = document.getElementById('dashboard-canvas') as HTMLCanvasElement;
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(PALETTE.bg, 1);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(10, 10, 10);
camera.lookAt(0, 0, 0);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// Grid helper
const grid = new THREE.GridHelper(20, 20, PALETTE.grid, PALETTE.grid);
scene.add(grid);

// Components
const discoveryMap = new DiscoveryMap(scene);
const cellDrawer = new CellDrawer();
const plotter = new Plotter();
const liveRail = new LiveRail();
const hud = new HUD(scene);

// WebSocket
const ws = new WSClient('ws://localhost:8080/ws');
ws.on('status_update', (data) => hud.updateResources(data));
ws.on('queue_update', (data) => discoveryMap.updateQueue(data));
ws.connect();

// Animation loop
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  discoveryMap.animate();
  hud.animate();
  renderer.render(scene, camera);
}
animate();

// Resize handler
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

**Potential Issue**: `OrbitControls` import path.
**Fix**: `import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';` — Vite handles this.

#### Step 0.5: Build integration
```bash
npm run build
# Output: ../templates/static/js/dashboard.js
```

**Potential Issue**: `web.py` mounts `/static` at `templates/static`. Vite outputs to `templates/static/js/`. ✅ Matches.

### Phase 1: Discovery Map

#### Data Flow
```
CampaignQueue.get_resource_usage() → WebSocket queue_update
    │
    ├─ queue.max_concurrent
    ├─ queue.queued (len)
    ├─ queue.running (len)
    ├─ queue.completed (len)
    └─ queue.resource_usage {used_gpus, max_gpus, ...}
```

**But Discovery Map needs**: Per-cell data (credit × geometry × dynamics × val_acc)
**Source**: `RecordStore.query_records(run_id)` for the running campaign.

**Gap**: WebSocket only sends queue status, not per-cell metrics.

#### Solution: Extend WebSocket Messages
```python
# In web.py _update_loop() - ADD:
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
```

**New message type**: `campaign_metrics` with per-cell records.

#### Discovery Map Implementation
```typescript
// src/discovery-map.ts
export class DiscoveryMap {
  private scene: THREE.Scene;
  private cells: Map<string, CellMesh> = new Map();
  private axes: AxesConfig = { x: 'credit', y: 'geometry', z: 'dynamics' };

  constructor(scene: THREE.Scene) {
    this.scene = scene;
    this.buildGrid();
  }

  buildGrid() {
    // Get unique values for each axis from campaign metrics
    // For demo: credit=[4], geometry=[1], dynamics=[1] → 4×1×1 grid
    // For production: dynamic from data
  }

  updateMetrics(metrics: CampaignMetrics) {
    // metrics.records[] → group by cell_key
    // For each cell: create/update CellMesh
  }
}

class CellMesh {
  mesh: THREE.Mesh;
  state: 'measured' | 'legal' | 'void';
  data: CellData;

  constructor(state: CellState, data: CellData) {
    if (state === 'measured') {
      // Glowing pillar
      const height = Math.max(0.5, data.val_acc * 3);
      const geo = new THREE.BoxGeometry(0.8, height, 0.8);
      const mat = new THREE.MeshStandardMaterial({
        color: PALETTE.arms[data.credit],
        emissive: PALETTE.arms[data.credit],
        emissiveIntensity: 0.5,
        transparent: true,
        opacity: 0.9,
      });
      this.mesh = new THREE.Mesh(geo, mat);
    } else if (state === 'legal') {
      // Wireframe cube
      const geo = new THREE.BoxGeometry(0.9, 0.9, 0.9);
      const edges = new THREE.EdgesGeometry(geo);
      const mat = new THREE.LineBasicMaterial({ color: PALETTE.legal, transparent: true, opacity: 0.3 });
      this.mesh = new THREE.LineSegments(edges, mat);
    } else {
      // Red X
      const geo = new THREE.BufferGeometry();
      // ... cross geometry
    }
  }

  animate() {
    if (this.state === 'measured') {
      // Pulse emissive
      this.mesh.material.emissiveIntensity = 0.5 + 0.3 * Math.sin(Date.now() * 0.003);
    }
  }
}
```

**Key Decision**: Grid axes are **dynamic** — derived from actual data, not hardcoded. The demo has 4 credit arms × 1 geometry × 1 dynamics = 4 cells. Production could be 10×5×3 = 150 cells.

---

### Phase 2: Cell Drawer (HTML Overlay)

```typescript
// src/cell-drawer.ts
export class CellDrawer {
  private panel: HTMLElement;
  private sparkline: Sparkline; // mini three.js scene

  constructor() {
    this.panel = document.createElement('div');
    this.panel.id = 'cell-drawer';
    this.panel.style.cssText = `
      position: fixed; right: 0; top: 0; bottom: 0; width: 350px;
      background: #0a0e14; border-left: 2px solid #d4a843;
      transform: translateX(100%); transition: transform 0.3s ease;
      z-index: 100; padding: 20px; overflow-y: auto;
      font-family: 'JetBrains Mono', monospace;
    `;
    document.body.appendChild(this.panel);
  }

  show(data: CellData) {
    this.panel.innerHTML = this.render(data);
    this.panel.style.transform = 'translateX(0)';
    // Init mini sparkline in #sparkline-canvas
  }

  hide() {
    this.panel.style.transform = 'translateX(100%)';
  }

  render(d: CellData): string {
    return `
      <h2 style="color: #d4a843; margin-top: 0;">${d.credit}</h2>
      <div class="coord-badge">
        ${Object.entries(d.coordinate).map(([k,v]) => 
          `<span class="tag">${k}=${v}</span>`).join('')}
      </div>
      <div class="metric-glow">val_acc: ${d.mean.toFixed(3)} ± ${d.std.toFixed(3)} (n=${d.n})</div>
      <div class="chance-line">chance: ${d.chance.toFixed(2)}</div>
      <div class="verdict ${d.verdict.toLowerCase()}">${d.verdict}</div>
      <div class="seeds-to-claim">${d.seedsToClaim} seeds to claim (d=0.5)</div>
      <canvas id="sparkline-canvas" width="300" height="150"></canvas>
      <div class="actions">
        <button disabled>[queue rest]</button>
        <button disabled>[preregister]</button>
        <button disabled>[adopt as quest]</button>
      </div>
    `;
  }
}
```

**Why HTML overlay**: Text rendering in WebGL is painful. HTML + CSS = accessible, selectable, responsive.

---

### Phase 3: Plotter (3D Charts)

#### Pareto Frontier (3D Scatter)
```typescript
// src/plotter.ts - ParetoScene
export class ParetoScene {
  private scene: THREE.Scene;
  private camera: THREE.OrthographicCamera;
  private renderer: THREE.WebGLRenderer;
  private points: THREE.Points[] = [];

  constructor(container: HTMLElement) {
    // Offscreen renderer for chart
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(this.renderer.domElement);

    this.camera = new THREE.OrthographicCamera(-5, 5, 5, -5, 0.1, 100);
    this.camera.position.set(0, 0, 10);
    this.scene = new THREE.Scene();
  }

  update(records: Record[]) {
    // Clear old
    this.points.forEach(p => { p.geometry.dispose(); p.material.dispose(); });
    this.points = [];

    // Axes: x=val_acc, y=1/walltime_s, z=1/param_count
    records.forEach(r => {
      const x = r.payload.val_acc;
      const y = 1 / (r.payload.walltime_s || 1);
      const z = 1 / (r.payload.param_count || 1);
      const color = PALETTE.arms[r.credit];

      const geo = new THREE.SphereGeometry(0.08, 16, 16);
      const mat = new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 0.3 });
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(x * 4, y * 4, z * 4);
      this.scene.add(mesh);
      this.points.push(mesh);

      // Pareto check: if non-dominated, make larger + glow
      if (r.isPareto) {
        mesh.scale.setScalar(1.5);
        mat.emissiveIntensity = 0.8;
      }
    });
  }

  render() {
    this.renderer.render(this.scene, this.camera);
  }
}
```

**Data Source**: Need `/api/campaigns/{id}/metrics` endpoint returning records with computed Pareto flags.

---

### Phase 4: Live Rail & HUD

#### Live Rail (HTML - not WebGL)
```typescript
// src/live-rail.ts
export class LiveRail {
  private container: HTMLElement;
  private messages: string[] = [];

  constructor() {
    this.container = document.createElement('div');
    this.container.id = 'live-rail';
    this.container.style.cssText = `
      position: fixed; bottom: 0; left: 0; right: 0; height: 60px;
      background: #0a0e14; border-top: 1px solid #d4a843;
      padding: 8px 20px; font-family: 'JetBrains Mono', monospace;
      font-size: 12px; color: #d4a843; overflow: hidden;
      display: flex; gap: 32px; align-items: center;
    `;
    document.body.appendChild(this.container);
  }

  addMessage(msg: string, level: 'ok' | 'warn' | 'error') {
    const color = level === 'ok' ? '#3fb950' : level === 'warn' ? '#d4a843' : '#f85149';
    const prefix = `[${level.toUpperCase()}]`;
    this.messages.unshift(`<span style="color:${color}">${prefix}</span> ${msg}`);
    if (this.messages.length > 20) this.messages.pop();
    this.render();
  }

  render() {
    this.container.innerHTML = this.messages.join('  │  ');
  }
}
```

**WebSocket message extension**:
```python
# In web.py _update_loop() - when campaign is running:
# Broadcast pipeline stage events
await self._broadcast_update({
    "type": "pipeline_event",
    "stage": "s6_train",
    "message": "compose joint system",
    "level": "ok",
    "timestamp": datetime.now().isoformat(),
})
```

---

## 4. UI Walkthrough (First-Time User Simulation)

### Scenario: New User Runs Dashboard

```bash
# Terminal 1
uv run comp dashboard --store experiment.duckdb
# Output:
# Starting dashboard on 0.0.0.0:8080
# Store: experiment.duckdb
# Dashboard started

# Terminal 2
uv run comp run demo --store experiment.duckdb
# Output: (34s of training logs)
# Run fe84cd97... completed with 20 records in 34.4s
```

### Browser Experience (http://localhost:8080)

| Time | What User Sees |
|------|----------------|
| 0s | Black canvas loads, three.js initializes, WebSocket connects (green dot top-left) |
| 0.5s | Grid appears (20×20), HUD shows GPU: 0/8, CPU: 0/64, MEM: 0/512GB |
| 1s | `queue_update` received: `queued=1, running=0` → Discovery Map shows 4 wireframe cubes (credit arms) |
| 2s | Campaign starts: `running=1` → wireframe cubes pulse amber |
| 5s | First records land → `campaign_metrics` WebSocket message |
| 5.5s | **Discovery Map transforms**: 4 wireframe → 4 **glowing pillars** (heights = val_acc) |
| 6s | HUD updates: GPU 1/8, CPU 4/64, burn 5s/120s |
| 10s | Live Rail: `[OK] compose joint system` `[OK] settle energy` `[OK] record appended` |
| 34s | Campaign completes → `running=0, completed=1` |
| 35s | All 4 pillars at final height, colors: blue/green/amber/purple |
| 36s | User clicks **pepita pillar** → Cell Drawer slides in from right |
| 37s | Cell Drawer shows: `val_acc: 0.444 ± 0.115 (n=5)`, chance: 0.10, `INSUFFICIENT`, `58 seeds to claim` |
| 38s | User clicks **Plotter tab: Pareto** → 3D scatter rotates, pepita point glowing |
| 39s | User clicks **Ablation** → 3D bars with gray chance plane at 0.10 |
| 40s | User takes screenshot → hero image captured |

### Pain Points to Fix

| Moment | Problem | Fix |
|--------|---------|-----|
| 0-1s | Blank screen, no feedback | Show "Connecting..." overlay until WebSocket opens |
| 1-5s | Wireframe cubes but no labels | Axis labels on grid edges (TextSprite) |
| 5s | Sudden pillar appearance | Animate height growth (tween) |
| Click | Cell Drawer appears but no close button | Add ✕ top-right, click outside to close |
| Plotter | No axis labels on 3D charts | Add axis helpers + labels |
| Mobile | Three.js canvas breaks layout | `touch-action: none` on canvas, responsive CSS |

---

## 5. Flexibility & Adaptability Analysis

### What If Requirements Change?

| Change | Current Design Handles It? | How |
|--------|---------------------------|-----|
| **New credit arm added** | ✅ Yes | Discovery Map derives axes from data; `PALETTE.arms` extensible |
| **New geometry type** | ✅ Yes | Grid Y-axis auto-expands |
| **New metric for Pareto** | ✅ Yes | Plotter uses dynamic axis mapping |
| **Campaign with 1000 cells** | ⚠️ Performance | Need instancing (InstancedMesh) for 1000+ pillars |
| **Multi-user dashboard** | ❌ No | Global queue singleton; need auth + per-user filter |
| **Historical replay** | ❌ No | WebSocket only live; need `/api/history` endpoint |
| **Custom shaders (bloom)** | ✅ Extensible | Three.js `EffectComposer` can be added |
| **Export to PNG/PDF** | ⚠️ Partial | `renderer.domElement.toDataURL()` for canvas; HTML panels need separate capture |

### Architectural Decisions for Flexibility

1. **Data-driven axes**: Discovery Map reads unique axis values from `campaign_metrics`, not hardcoded config
2. **Component registry**: `Plotter` registers chart types dynamically — add new chart = register component
3. **Message protocol versioning**: WebSocket messages include `protocol_version` for backward compat
4. **Theme system**: `PALETTE` object → swap for light mode, colorblind mode, high contrast
5. **Plugin architecture**: `src/plugins/` — custom cell renderers, chart types, HUD widgets

---

## 6. First-Time User Requirements Checklist

### Prerequisites (Document in `docs/DASHBOARD.md`)
- [ ] Node.js 18+ (for frontend build)
- [ ] Python 3.14+ with uv
- [ ] GPU optional (CPU works)
- [ ] `uv sync --dev --all-extras`

### Quick Start (3 Commands)
```bash
# 1. Build frontend (one-time)
cd computronium/experiment/execution/dashboard && npm install && npm run build

# 2. Start dashboard (terminal 1)
uv run comp dashboard --store experiment.duckdb

# 3. Run campaign (terminal 2)
uv run comp run demo --store experiment.duckdb
```

### What User Should See (Success Criteria)
- [ ] WebSocket connects (green indicator)
- [ ] Discovery Map renders grid with axis labels
- [ ] Campaign starts → wireframe → glowing pillars
- [ ] HUD shows live resource usage
- [ ] Live Rail shows pipeline events
- [ ] Click pillar → Cell Drawer with metrics
- [ ] Plotter tabs work (Pareto/Ablation/Variability)
- [ ] Campaign completes → INSUFFICIENT visible
- [ ] Screenshot script works

### Error Handling (User-Facing)
| Error | User Message |
|-------|--------------|
| WebSocket fails | "Connection lost. Retrying..." (auto-reconnect) |
| Store locked | "Store busy — waiting for writer..." (poll with backoff) |
| No campaigns | "No campaigns running. Run `comp run demo` in another terminal." |
| Build fails | "Run `npm install` in dashboard directory first." |
| Port 8080 in use | "Port 8080 busy. Use `--port 8081`." |

---

## 7. Missing Pieces Summary (Must Address Before Coding)

### Backend (web.py)
- [ ] **Add `/api/campaigns/{id}/metrics` endpoint** — returns records for Plotter
- [ ] **Extend WebSocket broadcast** — add `campaign_metrics` + `pipeline_event` types
- [ ] **Use `read_only=True`** for all dashboard store access
- [ ] **Serve static files correctly** — verify Vite output path matches mount

### Frontend (dashboard/src/)
- [ ] **WSClient** — auto-reconnect, message router, TypeScript types for all messages
- [ ] **DiscoveryMap** — dynamic grid from data, instanced rendering for scale
- [ ] **CellDrawer** — HTML overlay, mini sparkline (separate three.js scene)
- [ ] **Plotter** — 3 chart scenes, tab switching, axis helpers
- [ ] **LiveRail** — HTML overlay, animated message queue
- [ ] **HUD** — 3D resource bars, burn rate, claim price
- [ ] **Style** — centralized palette, theme support

### Screenshot Pipeline
- [ ] **launch_demo_campaign.py** — starts campaign, waits for first records
- [ ] **capture_dashboard_screenshot.py** — Playwright with WebGL support
- [ ] **CI integration** — headless Chromium with GPU (or software rasterizer)

### Documentation
- [ ] `docs/DASHBOARD.md` — user guide, controls, architecture
- [ ] `docs/readme/title.md` — hero image + tagline
- [ ] README "Start here" updated

---

## 8. Recommended Implementation Order (Risk-Adjusted)

```
Week 1:
  Day 1: Phase 0 (scaffold) + backend WebSocket extensions
  Day 2: Phase 1 (Discovery Map) - core visual
  Day 3: Phase 2 (Cell Drawer) - interaction
  Day 4: Phase 3 (Plotter) - 3D charts
  Day 5: Phase 4 (Live Rail + HUD) - polish

Week 2:
  Day 1: Screenshot pipeline + launch script
  Day 2: Integration testing + bug fixes
  Day 3: Documentation + README integration
  Day 4: Buffer for surprises
  Day 5: Final polish + hero screenshot
```

**Critical Path**: Phase 0 → Phase 1 → Phase 5 (screenshot). Phases 2-4 can be developed in parallel once Phase 1 data flow works.

---

## 9. Go/No-Go Decision Points

| Checkpoint | Criteria | If Fail |
|------------|----------|---------|
| **Phase 0 build** | `npm run build` produces `dashboard.js` < 500KB | Debug Vite config |
| **Phase 1 render** | 4 pillars visible, correct heights, colors | Check data flow from WebSocket |
| **Phase 1 interaction** | Click pillar → Cell Drawer opens | Check raycaster + event handling |
| **Live campaign** | `comp run demo` populates dashboard in real-time | Check lock contention (read_only) |
| **Screenshot** | Playwright captures 1920×1080 WebGL canvas | Use `--use-gl=angle` in CI |

---

## 10. Final Verdict

**The plan is solid but has 3 critical gaps that must be fixed in Phase 0:**

1. **`/api/campaigns/{id}/metrics` endpoint** — Plotter and Cell Drawer need per-cell data
2. **WebSocket `campaign_metrics` broadcast** — Discovery Map needs live per-cell updates
3. **`read_only=True` on all dashboard store access** — Prevents lock contention with running campaigns

**Once these are in web.py, the frontend can be built against a stable contract.**

The three.js architecture is flexible: data-driven axes, component registry, theme system. It handles the demo campaign (4 cells) and scales to production (100+ cells with instancing).

**Ready to implement.**