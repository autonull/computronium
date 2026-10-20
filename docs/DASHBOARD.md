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

**The core visual.** A 3D grid where axes are configurable (default: credit × geometry × dynamics).

| Cell Type | Visual | Meaning |
|-----------|--------|---------|
| **Measured** | Glowing pillar (height = val_acc, color = credit arm) | At least one seed completed |
| **Legal/Unmeasured** | Semi-transparent wireframe cube | In search space, not yet run |
| **Void** | Red X marker | Outside declared search space |

**Interactions:**
- **OrbitControls**: Left-drag = rotate, Right-drag = pan, Scroll = zoom
- **Click** a measured cell → opens Cell Drawer
- **Hover** highlights cell (emissive pulse)

**Legend** (top-left of map): Shows credit arm color coding and cell type key.

---

### 2. Cell Drawer (Right Slide-In Panel)

Rich detail for a selected measured cell. HTML overlay (not WebGL) for crisp text.

**Content:**
- **Coordinate badges**: substrate/geometry/dynamics/plasticity/credit/update with credit arm color
- **Primary metric**: `val_acc = 0.444 ± 0.115 (n=5)` — large monospace
- **Chance line**: Progress bar with gradient (red→amber→green) showing distance from chance (0.10 for digits)
- **Verdict banner**: `PASSED` (green, >chance+0.1) / `INSUFFICIENT` (amber, >chance) / `REJECTED` (red, ≤chance)
- **Seeds to claim**: Simplified calculation (63 seeds for d=0.5 effect)
- **Wall time & param count**
- **Mini 3D sparkline**: Training curve (val_acc over epochs) with chance line — small three.js scene

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

**Toolbar** (per chart): Download PNG, connection status indicator.

---

### 4. Live Rail (Bottom Log)

Scrolling timeline of pipeline events. HTML overlay with animated pills.

**Event levels:**
- `✓ ok` — stage completed (green)
- `⚠ warn` — stage completed at chance / degraded (amber)
- `✗ error` — stage failed (red)

**Source:** WebSocket `pipeline_event` messages (mock in v1, real queue events in v2).

---

### 5. HUD (Top-Right, 3D Sprites)

Three.js `Sprite` with `CanvasTexture` for crisp text rendering.

| Element | Description |
|---------|-------------|
| **GPU/CPU/MEM bars** | 3D bars with animated fill, percentage labels, pulse on active |
| **Burn rate** | `34s / 120s` with pulse animation when campaign running |
| **Claim price** | `63 seeds/arm` (static for demo) |

---

### 6. Mode Chip (Top-Left, 3D Sprite)

Shows campaign mode:
- `EXPLORATORY` (amber) — default
- `PREREGISTERED` (green) — after preregistration

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `1` | Switch to Pareto tab |
| `2` | Switch to Ablation tab |
| `3` | Switch to Variability tab |
| `H` | Toggle HUD visibility |
| `L` | Toggle Live Rail visibility |
| `?` | Show help overlay |

---

## WebSocket Message Types

The dashboard consumes these message types (via `MessageRouter` auto-registration):

| Type | Payload | Consumers |
|------|---------|-----------|
| `status_update` | `{gpu, cpu, memory, ...}` | HUD |
| `queue_update` | `{queued, running, completed, resource_usage}` | Discovery Map, Live Rail |
| `campaign_metrics` | `{campaign_id, data: {records, pareto, ablation_groups}}` | Discovery Map, Cell Drawer, Plotter |
| `pipeline_event` | `{stage, message, level}` | Live Rail |

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
    WebDashboard._get_campaign_metrics() ──► RecordStore.query_records(read_only=True)
                                          │
                                          ▼
    WebSocket campaign_metrics ──► three.js DiscoveryMap.updateMetrics()
                                          │
                                          ▼
    User clicks cell ──► CellDrawer.show(cellData)
    User opens Plotter ──► Plotter.update(records)
```

**Critical:** All dashboard store access uses `StoreConfig(read_only=True)` to avoid lock contention with the campaign writer.

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
| Store locked | Dashboard uses `read_only=True`. Only one writer (campaign) allowed. |
| Three.js errors in console | Check `npm run build` output. Vite bundles to `templates/static/js/dashboard.js` |

---

## Development

```bash
cd computronium/experiment/execution/dashboard
npm install          # Install deps
npm run dev          # Vite dev server with HMR (proxies API to localhost:8080)
npm run build        # Production build → ../templates/static/js/dashboard.js
```

**Regenerate palette/axis metadata:**
```bash
uv run python scripts/generate_palette.py
uv run python scripts/generate_axis_metadata.py
```

---

## Screenshot Pipeline (Hero Image)

```bash
# Generates docs/readme/assets/dashboard-hero.png (1920×1080)
uv run python scripts/capture_dashboard_screenshot.py
```

Requires: `playwright` (in `dev` extra), Chromium. Uses `--use-gl=angle` for headless WebGL.

The screenshot is embedded in `docs/readme/title.md` and appears on the README front page.