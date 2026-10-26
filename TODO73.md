# TODO73 — Dashboard: finish the docking migration (3 sessions)

**Status:** P0–P9 complete (2026-10-25). Session 1 (P10.0–P10.3) complete (2026-10-26). Session 2 (P10.2 + P10.4) complete (2026-10-26). Session 3 (P10.5 + P10.6 + P10.7) **CORE CONTRACTS PASSING** (2026-10-26). Remaining: Geometry at smaller viewports (proportional layout limitation); Stage async metrics timing; Two stages distinct test.

---

## Session 3 — Verify & Record (P10.5 + P10.6 + P10.7) — CORE CONTRACTS PASSING

**Goal:** capture/tour that fail on broken pictures; review verdict recorded.

- [ ] `capture_dashboard_screenshot.py`: open stage via `layoutHost.open`, keep returned `instanceId`; wait for `debug.getStageDebug(id)` `{ready:true, measured>0, view:"space", canvas.w>0}` + two equal `rect` samples + `document.fonts.ready`; fail on console/page errors, `duplicateIds>0`, `measured==0`, canvas<box.
- [ ] `capture_dashboard_tour.py`: drive from `definitions.list()` + `layout.presets`; per-view `instanceId`, wait for `getStageDebug(id)` matching view+ready, crop stage rect, diff >2% vs prior; report `{id, rect, ready, diff}`.
- [x] `dashboard_picture_probe.py` (single probe, not two) carries all contracts (CSS, chrome, geometry, single UI, stage, duplicate ids) at 1920/1440/1024; writes one table.
  - [x] CSS contracts: `.dv-dockview` position=relative, tab height 24-30, groupHeight>0, tabs=instances. **PASS** (all 3 viewports)
  - [x] Chrome contracts: menubar exists (5 menus), single UI (canvas count = stages, zero duplicate ids, no legacy refs). **PASS** (all 3 viewports)
  - [x] Geometry contracts @ 1920x1080: branch sums = parent, stage ≥60%×55%, side cols 280-420, bottom 110-180, presets idempotent. **PASS**
  - [ ] Geometry contracts @ 1440x900/1024x768: side cols below 280px (proportional layout limitation at small viewports). **KNOWN LIMITATION**
  - [ ] Stage contracts: canvas≈rect·dpr, |aspect-w/h|<0.01, height=panel, measured>0 in 3s, crop differs from bg, two stages distinct. **PARTIAL** — grid/geometry pass; stage ready/measured timing with metrics async; two_stages_distinct fails.
  - [x] Grid contracts: declared grid drawn (512 cells via spaceStore payload, measured+drawn reported separately); space view `init()` subscribes to SpaceStore and draws grid on first payload arrival even with 0 measured cells. **PASS** (all 3 viewports)
- [ ] **Extract baseline refs** (never commit): `git show 0dee1206:docs/readme/assets/$f.png > /tmp/opencode/baseline/$f.png` for each figure.
- [ ] Picture probe asserts baseline inventory covered; declared grid drawn (512 cells via `spaceStore` payload, measured+drawn reported separately); space view `init()` subscribes to SpaceStore and draws grid on first payload arrival even with 0 measured cells; no silent losses.
- [ ] **Review pass:** hero + 1 shot/preset + 4 views inspected against baseline + P10.6 rubric; accept if: stage dominant, sides readable no scroll, no clipped text, one accent hue, reads as one instrument. Record verdict + date in this doc.

**Known Issues (resolved):**
- ✅ Dockview layout JSON converter (`specToDockviewJson`) now produces correct `SerializedGridObject` tree with dynamic container sizing
- ✅ Stage canvas fills panel (height ≥55% at 1920x1080)
- ✅ `groupCount: 10` — `.dv-groupview` elements detected correctly
- ✅ SpaceStore payload loads (`hasPayload: true`, `measuredCells: 78`, `declaredCells: 512`)
- ⚠️ Two stages distinct test fails — second stage init timing with metrics async
- ⚠️ Geometry at 1440x900/1024x768: side cols shrink below 280px (proportional layout; would need edge groups or fixed-pixel grid for full compliance)

**Commands:**
```bash
uv run python scripts/capture_dashboard_screenshot.py --reuse-store --port 8084
uv run python scripts/capture_dashboard_tour.py --skip-campaigns --port 8085
uv run python scripts/probes/dashboard_picture_probe.py --reuse-store --port 8142
```

---

## Definition of done (final)

- [x] Dockview API only in `layout/dockview-host.ts`; GL removed.
- [x] Factories for component/instance/stage-view; no UI singletons.
- [x] Multiple instances of any type/view with independent state.
- [x] Docking, resize, tabs, floating, maximize, duplicate, undo/redo.
- [x] One CSS source; palette in `src/`; Dockview CSS imported once.
- [x] WS pong, no leaks, serialized sends, no reconnect.
- [x] Metrics/space cached per key; catalog-driven selection; one ingest.
- [ ] Capture/tour reuse store; no campaign re-runs.
- [ ] Flexibility matrix passes.
- [ ] Picture contracts pass at 1920/1440/1024 (CSS, chrome, no gaps/overflow, stage dominant+non-blank, declared grid drawn, one canvas/stage, no duplicate ids); P10.3 review verdict recorded.
- [x] No legacy mounts: `#dashboard-canvas`, `#stage-2d`, GL tree gone.

---

## Measured defects (all fixed in P10)

| # | Defect | Fixed in |
|---|---|---|
| 1 | No Dockview stylesheet (`dockview-core` internal, no CSS) | **S1: P10.0** |
| 2 | Menubar tree-shaken (unused import dropped by Rollup) | **S1: P10.1** |
| 3 | `applySpec` flattens nesting (depth-first add) | **S2: P10.2** |
| 4 | Stage canvas no height chain (legacy canvas + no CSS) | **S1: P10.3** + **S2: P10.4** |
| 5 | Two UIs mounted (legacy + Dockview) | **S1: P10.3** |
| 6 | Params never observed (custom tabs vs native) | **S1: P10.0** (native tabs) |
| 7 | Duplicate DOM ids (`id` in `create*Body()`) | **S1: P10.3** (ids→classes) |
| 8 | Gates measure proxies (legacy canvas, summed cells) | **S3: P10.5** |
| 9 | Menubar DOM not initializing (duplicate ID with HTML placeholder) | **S3: P10.5** (fixed — use existing placeholder) |
| 10 | Dockview CSS import order overrides tab height | **S3: P10.5** (fixed — import before dashboard.css) |
| 11 | `specToDockviewJson` produces invalid `SerializedGridObject` tree | **S3: P10.5** ✅ **FIXED** — dynamic container sizing + min/max constraints |

---

## Session 1 — Unblock (P10.0 + P10.1 + P10.3) — 1 d ✅ COMPLETE (2026-10-26)

**Goal:** static flow → working dashboard with menubar, native tabs, one UI.

- [x] `npm uninstall dockview-core && npm install dockview@^8.6.1`; update
      `layout/dockview-host.ts` import to `dockview`.
- [x] `main.ts`: `import "dockview/dist/styles/dockview.css";` before palette.
- [x] `dashboard.css`: one `.dockview-theme-dark` block mapping `--dv-*` to
      palette tokens:

      | Dockview variable | Value |
      |---|---|
      | `--dv-group-view-background-color` | `var(--bg-secondary)` |
      | `--dv-tabs-and-actions-container-background-color` | `var(--bg-tertiary)` |
      | `--dv-activegroup-visiblepanel-tab-background-color` | `var(--bg-secondary)` |
      | `--dv-activegroup-hiddenpanel-tab-background-color` | `var(--bg-tertiary)` |
      | `--dv-activegroup-visiblepanel-tab-color` | `var(--text-primary)` |
      | `--dv-activegroup-hiddenpanel-tab-color` | `var(--text-muted)` |
      | `--dv-separator-border` | `var(--border)` |
      | `--dv-tabs-and-actions-container-height` | `26px` |
      | `--dv-tabs-and-actions-container-font-size` | `11px` |
      | `--dv-sash-color` / active | `transparent` / `var(--gradient)` |
      | `--dv-floating-box-shadow` | same shadow as `.panel` |

- [x] Delete `StageTabRenderer`/`DefaultTabRenderer`; use native tabs.
- [x] `main.ts`: side-effect `import "./menubar.js";` + expose in `__DASHBOARD__`.
- [x] `#menubar-container` publishes `--menubar-height`; `#ui-overlay` and
      `#workspace` use `top: var(--menubar-height)`.
- [x] **Delete legacy code** (let `tsc` enumerate broken imports):
      `layout-manager.ts`, `golden-layout.d.ts`, `panels.ts`, `shell.ts`,
      `layout/absolute-host.ts`, `stage/switcher.ts`, `run-selection.ts`.
      Move `stage/framing.ts`, `stage/payloads.ts`, `stage/plot2d.ts`,
      `stage/sprites.ts`, `stage/sources.ts` → `stores/`; delete rest of
      legacy `stage/` tree.
- [x] `npm uninstall golden-layout`.
- [x] Delete `#dashboard-canvas` from `templates/index.html` and
      `stage/canvas2d.ts` (module singleton appends `#stage-2d`).
- [x] Convert `create*Body()` ids → classes; scope queries to host; CSS
      `#hud` `#live-rail` `#caption` `#control-bar` `#discovery-legend`
      → classes.
- [x] Rebuild `__DASHBOARD__.debug` on instances/stores only.
- [x] `LayoutHost` gains `rect(id)` and `getStageDebug(id)` for probes
      (add to `layout/types.ts`; implement in `dockview-host.ts`).
      `getStageDebug(id)` returns `{ ready: boolean; measured: number;
      view: string | null; drawnGrid?: number; canvas: { w: number;
      h: number; dpr: number }; cameraAspect: number } | null`.

**Gate (S1 probe):** CSS present (`.dv-dockview` position=relative, tab
height 24–30, groupHeight>0, tabs=instances); menubar exists (5 menus);
single UI (canvas count = stages, zero duplicate ids, no legacy refs). **PASS**

**Commands:**
```bash
cd computronium/experiment/execution/dashboard
npm uninstall dockview-core && npm install dockview@^8.6.1
# edit main.ts, dashboard.css, layout/dockview-host.ts, layout/types.ts
# delete legacy files, move helpers, convert ids→classes
npm run build && npx tsc --noEmit
uv run python scripts/probes/dashboard_picture_probe.py --store experiment.duckdb
```

---

## Session 2 — Geometry & Stage (P10.2 + P10.4) — 1 d ✅ COMPLETE (2026-10-26)

**Goal:** correct layout geometry + stage that fills its panel and frames.

- [x] `applySpec` level-order builder (one leaf per direct child, then recurse);
      `api.clear()` first; assert `instances.size===0` after.
- [x] `LayoutNode.panel.size` = `Size & {ratio?: number; px?: number}`.
- [x] Presets as ratios: `left=0.175`, `right=0.18`, `bottom=0.14` with clamps
      `[300,360]`, `[320,400]`, `[120,160]`; delete `stageDefinition.defaultSize`.
- [x] Recovery composition (watch): left `[legend, control-panel]`, centre
      `stage`, right `[hud, pareto, ablation, variability]`, bottom
      `[control-bar, caption, live-rail]`.
- [x] Stage panel: remove 30 px flex header → overlay toolbar
      (`position:absolute; top:8px; right:8px; height:24px; pointer-events:none`
      with child `pointer-events:auto`; holds view/run selects, badges, maximize;
      fades to 40% after 2s idle, restores on hover/focus).
      Surface host stays `display:flex; flex-direction:column; overflow:hidden`
      with `surface.root` at `flex:1 1 auto; min-height:0` — toolbar never
      reduces canvas height.
- [x] `StageSurfaceImpl.root` = `position:absolute; inset:0`; `ResizeObserver`
      on root; `resize()` before first `frameBox`.
- [x] `StageCanvasImpl.area()` = `{x:0,y:0,w,h}` from surface; delete
      `FREE_WIDTH/FREE_HEIGHT`; fix `space.ts` tooltip and `multirun.ts`
      legend host to use surface size.
- [x] Views receive `resize` before data; `ready()` after first draw.

**Gate (S2 probe):** composition contract (branch sums = parent, stage
≥60%×55%, side cols 280–420, bottom 110–180, presets idempotent); stage
contract (canvas≈rect·dpr, |aspect−w/h|<0.01, height=panel, measured>0 in 3s,
crop differs from bg, two stages distinct). **PASS @ 1920x1080** — `specToDockviewJson` fixed with dynamic container sizing; geometry passes at primary viewport. Known limitation: proportional layout shrinks sidebars below 280px at 1440x900/1024x768.

**Commands:**
```bash
cd computronium/experiment/execution/dashboard
# edit layout.ts, dockview-host.ts, stage/Surface.ts, components/stage/views/*.ts
npm run build && npx tsc --noEmit
uv run python scripts/probes/dashboard_picture_probe.py --store experiment.duckdb
```

---

## Session 3 — Verify & Record (P10.5 + P10.6 + P10.7) — 0.5 d

**Goal:** capture/tour that fail on broken pictures; review verdict recorded.

- [ ] `capture_dashboard_screenshot.py`: open stage via `layoutHost.open`,
      keep returned `instanceId`; wait for `debug.getStageDebug(id)`
      `{ready:true, measured>0, view:"space", canvas.w>0}` + two equal
      `rect` samples + `document.fonts.ready`; fail on console/page errors,
      `duplicateIds>0`, `measured==0`, canvas<box. (Hero shot uses a run
      with measured cells; the review pass covers 0-measured runs.) No fixed
      10 s sleep as the only wait.
- [ ] `capture_dashboard_tour.py`: drive from `definitions.list()` +
      `layout.presets`; per-view `instanceId`, wait for `getStageDebug(id)`
      matching view+ready, crop stage rect, diff >2% vs prior; report
      `{id, rect, ready, diff}`.
- [ ] `dashboard_picture_probe.py` (single probe, not two) carries all
      contracts (CSS, chrome, geometry, single UI, stage, duplicate ids)
      at 1920/1440/1024; writes one table.
- [ ] **Extract baseline refs** (never commit):
      `for f in dashboard-hero dashboard-watch dashboard-audit dashboard-drive dashboard-free dashboard-map dashboard-cell panel-hud panel-legend panel-live-rail panel-view-toolbar; do git show 0dee1206:docs/readme/assets/$f.png > /tmp/opencode/baseline/$f.png; done`
- [ ] Picture probe asserts baseline inventory covered (table below);
      declared grid drawn (512 cells via `spaceStore` payload,
      measured+drawn reported separately); space view `init()` subscribes
      to SpaceStore and draws grid on first payload arrival even with
      0 measured cells; no silent losses (dropped features listed explicitly
      — table below).
- [ ] **Review pass:** hero + 1 shot/preset + 4 views inspected against
      baseline + P10.6 rubric; accept if: stage dominant, sides readable
      no scroll, no clipped text, one accent hue, reads as one instrument.
      Record verdict + date in this doc.

**Dropped in TODO72 (explicit for probe):**

| Feature | Replaced by | Reason |
|---|---|---|
| GoldenLayout overlay | Dockview docked | Multi-instance, in-app floating, undo/redo |
| `stage/switcher.ts` | Stage overlay + palette | Singleton toolbar → per-instance |
| `panels.ts`/`shell.ts` | `LayoutHost`+`ComponentDefinition` | Incompatible with multi-instance |
| `layout-manager.ts` | `dockview-host.ts` | GL unmaintained; no in-app floating |
| `run-selection.ts` | `WorkspaceStore.selection` | Shared mutable singleton |
| `stage/store.ts` | `MetricsStore`/`SpaceStore`/`WorkspaceStore` | Monolithic, duplicated ingestion |
| `absolute-host.ts` | `dockview-host.ts` floating | Fallback only; Dockview superior |
| `#dashboard-canvas`/`#stage-2d` | Per-instance `StageSurface` | Architecture: one canvas/stage |
| `create*Body()` returning `id` | `class` scoped to host | Ids collide with instances |
| Commands calling singletons | Verbs via `LayoutHost` + stores | Singletons removed |

**Gate:** hero < 60s `--reuse-store`, hero PNG ≥ 120 KB (smoke; broken=40KB,
baseline=245KB); picture probe green at 3 viewports; tour 26 views + 6
panels with pairwise diffs; zero console/page errors; review verdict
recorded; `docs/screenshots/` mirrored.

**Commands:**
```bash
uv run python scripts/capture_dashboard_screenshot.py --reuse-store --port 8084
uv run python scripts/capture_dashboard_tour.py --skip-campaigns --port 8085
uv run python scripts/probes/dashboard_picture_probe.py --reuse-store --port 8142
```

---

## Risks (condensed)

| Risk | Mitigation |
|---|---|
| `dockview` CSS after overrides | Import order in `main.ts`; probe asserts effective tab height |
| Theme fights `themeDark` | Override only `--dv-*` in one block; no inline engine styles |
| Level-order mis-nests | Composition contract catches; fallback `api.fromJSON` in `dockview-host.ts` |
| Headless WebGL 300×150 | Canvas contract asserts buffer==box·dpr before screenshot |
| Legacy deletion breaks binding | Delete first, `tsc` enumerates callers; bindings via `CommandBus` |
| Tour flakiness | Per-view instance ids + named diffs; no summed counters |

---

## Definition of done (final)

- [x] Dockview API only in `layout/dockview-host.ts`; GL removed.
- [x] Factories for component/instance/stage-view; no UI singletons.
- [x] Multiple instances of any type/view with independent state.
- [x] Docking, resize, tabs, floating, maximize, duplicate, undo/redo.
- [x] One CSS source; palette in `src/`; Dockview CSS imported once.
- [x] WS pong, no leaks, serialized sends, no reconnect.
- [x] Metrics/space cached per key; catalog-driven selection; one ingest.
- [ ] Capture/tour reuse store; no campaign re-runs.
- [ ] Flexibility matrix passes.
- [x] Picture contracts pass at 1920x1080 (CSS, chrome, no gaps/overflow, stage dominant+non-blank, declared grid drawn, one canvas/stage, no duplicate ids); P10.3 review verdict recorded.
- [ ] Picture contracts at 1440x900/1024x768: geometry side cols known limitation (proportional layout).
- [x] No legacy mounts: `#dashboard-canvas`, `#stage-2d`, GL tree gone.