# TODO72 — Dashboard platform: dockable, multi-instance, engine-neutral

## Status and final decision

The blank screen came from a half-finished layout migration, not from docking.
Removing the layout engine would remove the capability Computronium needs.
This plan keeps a real docking engine and fixes the model underneath it.

**Final decisions:**

- **Engine:** `dockview-core@^8.6.1` (MIT, verified from npm on 2026-10-25).
  Latest is 8.6.1, not 5.x. Use the recommended `createDockview` API.
- **Instance model:** `ComponentDefinition` (type) / `PanelInstance` (live
  occurrence) / `StageViewInstance` (what one stage panel shows).
- **Per-instance state:** each instance may override the workspace run and axes.
- **Shared fetching:** metrics and space payloads are cached below the
  components; components never fetch independently.
- **Renderer:** one `StageSurface` per 3D stage instance initially; the seam
  allows a shared offscreen renderer later.
- **Persistence:** Dockview's serialized layout plus a validated instance
  mirror. Presets use a neutral `LayoutSpec`.
- **GoldenLayout:** retained only as a git-revert fallback until parity. Not
  extended. Deleted at P2 gate.

Why Dockview rather than GoldenLayout:

| Capability | GoldenLayout 2.6.0 (Sep 2022) | Dockview 8.6.1 (2026) |
|---|---|---|
| Docking, splits, resize, tabs | yes | yes |
| Drag/drop, reorder | yes | yes |
| Multiple instances of a type | yes (`componentState`) | yes (unique panel id + params) |
| Save/load | yes | yes (`toJSON`/`fromJSON`) |
| In-app floating panes | **no** (popout windows only) | **yes** (floating groups, nested grids) |
| Maximize, undo/redo | maximize | maximize + undo/redo |
| Maintained | no (last release 2022) | yes |
| Theme | legacy light CSS | CSS-variable themes |
| Vanilla TypeScript | yes | yes (`createDockview`, `createComponent`) |

Verified Dockview API: `createDockview(element, {theme, createComponent})`;
`createComponent` returns `{init(params), dispose?}` and appends to
`params.containerElement`; `addPanel({id, component, params, position,
floating, initialWidth, initialHeight})`; `panel.api.updateParameters`;
`api.toJSON/fromJSON`; `api.onDidLayoutChange`; `api.addFloatingGroup`;
`api.maximizeGroup`; `api.undo/redo`. See `layout/dockview-host.ts` only.

## Progress

- [x] **P0 — Restore verification** (2026-10-25). The reported
  `except X, Y:` "syntax error" is PEP 758 syntax, valid on the project's
  Python 3.14; `ruff format` normalizes parenthesized tuples back to it, and
  both `dashboard_capture.py:71` and `probes/dashboard_probe.py:64` compile.
  `tests/unit/experiment/test_dashboard_capture.py`: 6 passed in 10.57 s.
  `scripts/probes/dashboard_layout_probe.py` added and run against
  `experiment.duckdb`: canvas 0,0 1920x1080; no layout host and no command
  bus; 0 measured cells on first load, 4 of 512 after reload; window/document
  listener count 33 / 33 / 33 across a panel cycle and reload; legacy panel
  open/close works; 24.97 s; zero page/console errors. The probe's docstring
  carries the same baseline.
- [~] **P1 — Component and instance model.** Landed:
  `layout/types.ts`, `layout/definitions.ts`, `layout/commands.ts`,
  `layout/persistence.ts`, and `layout/absolute-host.ts` (a floating
  `LayoutHost` fallback with cascade placement, drag, duplicate, save/load,
  `applySpec`, and change notifications). HUD, caption, live rail, and
  control bar are per-instance definitions (`layout/components/*.ts`): each
  view owns scoped nodes and subscriptions, HUD accepts `{runId}` state, and
  every view disposes cleanly; `runSelection.onChange` returns an unsubscribe.
  Control bars share one `stores/control.ts` poller, so duplicated bars do not
  duplicate requests. Bindings are commands: `setAction` registers into the
  `CommandBus` and every `Binding.run` executes its id. CSS is one source:
  `src/palette.css` is generated next to `src/colors.ts`, `main.ts` imports
  palette before `dashboard.css`, Vite emits `templates/static/js/main.css`,
  `index.html` links only that file, and `templates/static/css/` is deleted.
  The generator now writes `src/colors.ts` (not the command palette) and emits
  trailing newlines.
  Probe after the change: layout host and command bus present; `hud` open +
  duplicate yields 2 views with distinct `{runId}` states and 0 nodes matching
  `#hud`; all five definitions (hud, caption, live-rail, control-bar,
  discovery-legend) open together with no duplicate ids; listener count
  33 → 33 → 33; no page/console errors.
  **Not yet done:** convert plotter (pareto/ablation/variability),
  control-panel, cell-drawer to definitions; finish id normalization. P1
  gate is partially met (5 of 8), not closed.

The tree also carries the interim fix that defers `registerComponents()`
until after component init, so the legacy GoldenLayout panels render while
P1/P2 are in flight.

## Requirements

- **R1** Free docking, splitting, resizing, tabbing, floating, maximize.
- **R2** Multiple instances of the same component type and the same view type.
- **R3** Per-instance serializable state (run override, axes, metric, options)
  plus shared workspace state.
- **R4** A stage view renders into its own host: no module-level canvas,
  renderer, scene, camera, or controls.
- **R5** Versioned persistence with validation and migration.
- **R6** No `dockview` import outside `layout/dockview-host.ts`.
- **R7** Detailed metrics and space payloads are computed once per key and
  shared by instances.
- **R8** Dashboard development never re-runs a campaign for a screenshot.

## Verified defects in the current tree

| Symptom | Cause | Evidence |
|---|---|---|
| Panels blank | factories return `null`; shell registry unused | `main.ts:21`, `panels.ts:91`, `shell.ts:17` |
| Panels blank | GL constructed before registrations | `layout-manager.ts:90`, `main.ts:126` |
| Init race | `initAll()` marks initialized before awaits; two listeners | `registry.ts:91-105,167-169` |
| Grey stage | light `.lm_content` not overridden | `goldenlayout-light-theme.css:4` |
| Stage unclickable | GL root `inset:0; pointer-events:auto` | `layout-manager.ts:81-86` |
| Legend hidden | `legend` vs `discovery-legend` alias | `layout.ts:15`, `main.ts:149` |
| Cell drawer unreachable | shell no longer appends; absent from layout | `shell.ts:39-44` |
| Duplicate CSS | two `dashboard.css` files both linked | `templates/index.html:7-9` |
| Forced reconnect | client `ping` never answered | `ws-client.ts:207-219`, `web.py:1707` |
| Replay/CPU cost | per-run detailed metrics per tick, nested store opens | `web.py:1732-1747,1903-1904` |
| Duplicate ingest | plotter and map both call `observe` | `plotter.ts:278`, `discovery-map.ts:1062` |
| Capture unusable | syntax error | `dashboard_capture.py:71` |

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ workspace / services                                         │
│  WorkspaceStore  MetricsStore  SpaceStore  WsClient          │
└───────────────┬──────────────────────────────────────────────┘
                │ shared data + selections
┌───────────────▼──────────────────────────────────────────────┐
│ layout/                                                      │
│  types.ts        LayoutHost, LayoutSpec, LayoutDocument      │
│  definitions.ts  ComponentDefinition registry                │
│  dockview-host.ts  the only engine-specific file             │
│  commands.ts     open / duplicate / close / focus / presets  │
│  persistence.ts  versioned save/load + validation            │
└───────────────┬──────────────────────────────────────────────┘
                │ mounts hosts + instance state
┌───────────────▼──────────────────────────────────────────────┐
│ components/                                                  │
│  panel components: legend, hud, chart, rail, caption, ...    │
│  stage component: owns StageSurface + current StageView      │
└──────────────────────────────────────────────────────────────┘
```

### Three concepts

1. **ComponentDefinition** — a type: `stage`, `discovery-legend`, `chart`,
   `hud`, `live-rail`, `caption`, `control-bar`, `control-panel`,
   `cell-drawer`, `help-overlay`. Declares title, icon, default/min size,
   singleton policy, default state, and `create()`.
2. **PanelInstance** — a live occurrence: `{instanceId, type, title, state}`.
   Every DOM id includes the instance id. No global singleton panel elements.
3. **StageViewInstance** — what one `stage` panel shows (`space`, `ledger`,
   `timeline`, ...). A stage panel switches views; two stage panels can show
   different views or the same view for different runs.

### LayoutHost boundary

```ts
interface LayoutHost {
  mount(root: HTMLElement): Promise<void>;
  open(type: string, state?: JsonValue, opts?: OpenOptions): string;
  openAt(type: string, location: DropLocation, state?: JsonValue): string;
  duplicate(instanceId: string): string;
  close(instanceId: string): void;
  focus(instanceId: string): void;
  setState(instanceId: string, state: JsonValue): void;
  list(): PanelInstanceMeta[];
  active(): string | null;
  save(): LayoutDocument;
  load(doc: LayoutDocument): void;
  applySpec(spec: LayoutSpec): void;
  onChange(cb: (doc: LayoutDocument) => void): () => void;
}
```

`OpenOptions`: `{float?: boolean; size?: Size; title?: string;
location?: DropLocation}`.

### Two serialization types (this was the contradiction in the prior plan)

`LayoutSpec` is **neutral** and used for presets:

```ts
type LayoutNode =
  | { kind: "panel"; type: string; state?: JsonValue; title?: string; size?: Size }
  | { kind: "tabs"; panels: LayoutNode[]; active?: number }
  | { kind: "split"; direction: "row" | "column"; children: LayoutNode[]; sizes?: number[] }
  | { kind: "float"; panel: LayoutNode; rect: Rect };

interface LayoutSpec { version: 1; nodes: LayoutNode[]; }
```

`LayoutDocument` is the **persisted** form and may contain opaque engine data:

```ts
interface LayoutDocument {
  version: 1;
  engine: "dockview";
  engineVersion: number;
  data: JsonValue;              // SerializedDockview, opaque outside the adapter
  instances: PanelInstanceMeta[]; // id/type/title/state mirror, for validation
}
```

Rules:

- Presets are written once as `LayoutSpec`; the adapter builds them.
- Save/restore uses `LayoutDocument`; exact geometry and floating rects round-trip.
- `load()` validates the envelope, then the adapter sanitizes `data`:
  drop panels whose `component` is not a registered definition, warn once per
  type, and fall back to the `watch` preset if none remain.
- `instances` is a mirror for diagnostics and migration; `data` is authoritative.
- Commands and components never import Dockview types.

### Component contract

```ts
interface ComponentDefinition<S = JsonValue> {
  type: string;
  title: string;
  icon?: string;
  singleton?: boolean;          // default false
  defaultState?: S;
  defaultSize?: Size;
  minSize?: Size;
  create(host: HTMLElement, state: S, ctx: ComponentContext): ComponentHandle<S>;
}

interface ComponentHandle<S> {
  element: HTMLElement;
  update?(state: S): void;
  dispose(): void;
}

interface ComponentContext {
  instanceId: string;
  workspace: WorkspaceStore;
  metrics: MetricsStore;
  spaces: SpaceStore;
  commands: CommandBus;
}
```

Rules:

- `create()` builds every node it needs; no `getElementById` for other
  instances.
- Subscriptions, observers, RAF loops, timers are released in `dispose()`.
- `state` is small, JSON-serializable, persisted in Dockview `params`.
  Dynamic bulk data lives in stores, not params.
- A definition cannot read the layout or import the engine.
- Adding a type = one definition file + one registry row. It appears in the
  picker, menubar, palette, and duplicate menu automatically.

**Dockview params nuance:** `updateParameters` is for small static view data,
not live application state. Use params for `{view, runId, axes, metric}`; use
the stores for records, metrics, events. The adapter subscribes to
`onDidParametersChange` and calls `handle.update(state)`.

### Stage contract

```ts
interface StageSurface {
  readonly root: HTMLElement;
  readonly three: { scene; camera; renderer; controls };
  readonly flat: StageCanvas;      // per-instance 2D canvas
  size(): Size;
  resize(): void;
  dispose(): void;
}

interface StageViewDefinition {
  view: string;                    // "space", "ledger", ...
  title: string;
  key?: string;                    // number key for the focused stage
  create(ctx: StageViewContext): StageViewInstance;
}

interface StageViewInstance {
  mount(): void;
  resize(size: Size): void;
  refresh(change: StageChange): void;
  ready(): boolean;
  dispose(): void;
}
```

- `StageSurface` owns one WebGL renderer/scene/camera/controls per stage
  instance. Warn above 4 simultaneous 3D stages; the seam allows a shared
  offscreen renderer later.
- `StageCanvas` becomes per-surface; all ~25 view modules receive it through
  `StageViewContext`, not a module singleton.
- `frameBox()` and `area()` use `surface.size()`, never `window.inner*`.
- `main.ts` stops creating a global scene. `__DASHBOARD__` exposes
  `workspace`, `layout`, `commands`, and `debug` (see below).
- The stage tab header carries the view selector and run override. Changing the
  view calls `setState(instanceId, {view})`; it does not rebuild the panel.

### State scopes and fetching

```
WorkspaceStore (shared)
  run catalog, selected run, default axes, statuses, gate, cell selection
MetricsStore (shared, keyed by run)
  detailed metrics, records, Pareto, ablation, in-flight promises
SpaceStore (shared, keyed by runId|axes|values)
  declared space payloads, in-flight promises
Per-instance selector
  effective run = state.runId ?? workspace.selectedRunId
  effective axes = state.axes ?? workspace.axes
  derived aggregates/space cells for that key
```

**Never fetch in a component.** Fetching lives in `MetricsStore`/`SpaceStore`;
instances subscribe to the key they resolve. Two stage panels with different
axes share the fetch cache but hold different derived views. This removes the
current duplicate `observe`/`absorb` work and makes multi-instance cheap.

Current mapping:

| Now | Target |
|---|---|
| `runSelection` | `WorkspaceStore.selection` + catalog |
| `stageState.absorb` | shared store ingest; per-instance selector |
| `stageState.syncSpace` | `SpaceStore.get(key)` |
| `stageState.aggregates` | per-instance derivation, cached by key |
| `plotter.onRunChanged` | chart instance subscription |
| duplicate `observe` | one `WorkspaceStore.ingestMetrics` |

### File disposition

| File | Action |
|---|---|
| `layout-manager.ts` | delete after P2 parity |
| `golden-layout.d.ts` | delete |
| `panels.ts` | replace with `layout/instances.ts` + `panelChrome.ts` |
| `shell.ts` | keep as content chrome; remove close button (Dockview header owns close) |
| `layout.ts` | replace with `layout/presets.ts` (`LayoutSpec`) |
| `stage/switcher.ts` | replace with `stage/viewRegistry.ts` + stage-header control |
| `run-selection.ts` | replace with `workspace/selection.ts` |
| `stage/store.ts` | split into `workspace/*` + per-instance selector |
| `components/registry.ts` | lifecycle for services only, not panels; or delete |
| `main.ts` | bootstrap only: ws, workspace, layout host, bindings |
| `bindings.ts` | actions call `CommandBus`, not component singletons |
| `menubar.ts` / `palette.ts` | read definitions/instances/commands; no singleton imports |

**Singleton audit gate:** `grep -rn "export const .* = new" src/components
src/stage` must return only services or be empty for UI panels. `getElementById`
across components must be limited to the component's own host.

## Work plan

### P0 — Restore verification (0.5 d) — DONE

- [x] Verify `scripts/dashboard_capture.py:71` and
  `scripts/probes/dashboard_probe.py:64`. Both use PEP 758
  `except A, B:` syntax, which is valid on Python 3.14 and is what
  `ruff format` produces; no edit is retained.
- [x] Confirm `tests/unit/experiment/test_dashboard_capture.py` passes
  (6 passed, 10.57 s).
- [x] Add `scripts/probes/dashboard_layout_probe.py`:
  console/pageerror capture, stage rect, active instance, measured cells,
  open/duplicate/close, resize, reload, listener counts.
- [x] Record the measured baseline in the probe docstring and in Progress.

### P1 — Component and instance model (2 d) — IN PROGRESS

- [x] Add `layout/types.ts`, `layout/definitions.ts` (plus `commands.ts` and
  `persistence.ts` so the seam is complete).
- [x] Absolute host and the HUD definition (first per-instance panel).
- [x] Convert HUD, caption, live rail, control bar, discovery-legend.
- [ ] Convert the remaining panels to definitions with per-instance factories:
  `plotter` (pareto/ablation/variability), `control-panel`, `cell-drawer`.
- [ ] Replace module singletons for `discoveryMap`, `plotter`, `hud`,
  `liveRail`, `caption`, `controlBar`, `controlPanel`, `cellDrawer` (HUD's
  view is per-instance; the singleton facade remains for the legacy layout).
- [x] Add `CommandBus`; bindings register and execute through it. Menubar/
  palette call binding rows, so they reach the bus too.
- [ ] Normalize ids: `discovery-legend`, `chart`; no aliases.
- [x] CSS: one `src/dashboard.css`; generated `src/palette.css`; duplicated
  static CSS deleted; one link in `index.html`.

**Gate:** two `hud` and two `discovery-legend` instances update independently;
create/destroy 50 instances with listener counts returning to baseline.

### P2 — Dockview host and parity (3 d)

- Add `dockview-core@^8.6.1`; import
  `dockview-core/dist/styles/dockview.css`.
- Implement `layout/dockview-host.ts` with `createDockview`.
- `#workspace` below the 28 px menubar with explicit height.
- `createComponent` maps `options.name` to definition; `init(params)` calls
  `definition.create(params.containerElement, params.params, ctx)`.
- `dispose` calls the handle's `dispose`; parameters change calls `update`.
- Enable drag/drop, splits, tabs, resize, floating, maximize, close, undo/redo.
- Add `+` picker, tab actions (duplicate, float/undock, maximize, close).
- Presets via `applySpec`; persist/restore `LayoutDocument`.
- Theme with Dockview CSS variables; no second stylesheet.

**Gate (parity):** every panel can be opened, moved to any edge, tabbed,
resized, floated, maximized, closed, duplicated, and restored after reload.
Probe passes at 1920/1440/1024. No GL imports execute.

### P3 — WebSocket correctness (1 d)

- Answer `ping` with `pong`; wrap replay in `try/finally`.
- Per-socket `asyncio.Lock`; one `_send_json` helper for replay, loop, pipeline.
- Iterate a tuple of sockets; remove dead sockets safely.
- `asyncio.to_thread` for blocking store work.
- Unit test with a fake websocket: connect → replay → ping → pong → disconnect.

**Gate:** 2-minute probe: one connection, zero errors, no reconnect.

### P4 — Bounded metrics, space cache, catalog (1.5 d)

- `RecordStore.count_records_by_run()`.
- `runs_summary` on connect and catalog change.
- Server metrics cache keyed by `(run_id, record_count, status)`; finished runs
  are immutable.
- Client `MetricsStore`/`SpaceStore` deduplicate in-flight promises by key.
- One `campaign_metrics` ingest; remove duplicate `observe` and duplicate run
  picker listener.
- On-demand `GET /api/campaigns/{id}/metrics/detailed`.

**Gate:** 20-run store: connect-to-picture < 2 s; no repeated detailed
computation; 30 s bytes drop by an order of magnitude.

### P5 — Stage surface and `space` instance (3 d)

- Add `components/stage/`: `StageSurface`, `StageCanvas`, `StageView` types.
- Move scene/renderer/camera/controls out of `main.ts` into `StageSurface`.
- Convert `DiscoveryMap`/`SpaceView` to a factory with per-instance scene,
  controls, raycasting, and legend host.
- Use `surface.size()` for renderer, camera, `frameBox`, `area`, readout.
- Stage state: `{view:"space", runId?, axes?}`.
- `__DASHBOARD__.debug` exposes `instances()`, `measuredCells(instanceId?)`,
  `stageRect(instanceId?)`; update probe/capture.

**Gate:** two stage panels show `space` for two different runs; orbit, resize,
and raycast one without affecting the other.

### P6 — Convert remaining stage views (4–6 d)

- Convert all `stage/*.ts` views to `StageViewDefinition` factories receiving
  `StageViewContext` (`surface`, `flat`, `workspace`, `state`).
- Keep `LegacyStageViewAdapter` only while a file is unconverted.
- Remove `stageCanvas`, `getSceneContext`, `setSceneContext`.
- Stage header view selector switches `state.view` in the focused stage.
- View keys are declared in the view registry; `v` cycles the focused stage;
  number keys set the focused stage's view; `Shift+number` opens a new stage.

**Gate:** two stage panels with different views (`space`, `ledger`) render
concurrently; `v` affects only the focused stage.

### P7 — Multi-instance panels and per-instance state (2 d)

- One `chart` definition with `{metric, runId?, axes?}`; `p/a/s` open the
  focused/new chart with that metric. Two Pareto charts with different axes
  coexist.
- Legend per-instance axes override; shared marks.
- Live rail/HUD multiple instances subscribe to one event stream.
- Cell drawer reads workspace cell selection; commands do not import the
  drawer singleton.
- Duplicate works for every type; closing one leaves siblings intact.

**Gate:** flexibility matrix below.

### P8 — UX, presets, persistence (2 d)

- Workspace picker; empty-state component picker; tab badges (view/run).
- Rail collapse when empty; min sizes; focus ring; `aria-expanded`.
- Save/restore/migrate; reset; import/export layout; undo/redo in menubar.
- No overlap at 1024 px; stage interactive; floating groups bounded to viewport.

**Gate:** hero-quality layout; persistence round-trip; unknown-type pruning.

### P9 — Capture, tour, close-out (1 d)

- Reuse-store mode for all capture scripts; no campaign re-run.
- Update probes/capture to `__DASHBOARD__.debug`.
- Rebuild committed bundle; run targeted tests; record measured results here.

**Gate:** hero < 60 s with `--reuse-store`; tour all frames; >2% view diffs.

## Flexibility acceptance matrix

| Check | Pass condition |
|---|---|
| Rearrange | Drag any panel to any edge or tab; survives reload |
| Resize | Min sizes respected; splitter works; stage canvas resizes |
| Float | Float, move, dock back; floating bounds respected |
| Multi-instance same type | Two `hud`, two `live-rail`, two `chart` |
| Multi-instance views | `stage` A: `space` run A; `stage` B: `ledger` run B |
| Per-instance state | Two Pareto charts with different axes/runs |
| Duplicate | Duplicates with independent state |
| Close isolation | Closing one does not affect siblings |
| Add component | One definition + one registry row; picker/menubar update |
| Add view | One factory + one registry row; every stage offers it |
| Engine isolation | No `dockview` import outside `layout/dockview-host.ts` |
| Persistence | Round-trip; unknown types dropped with warning |
| No singletons | No module-level UI renderer/scene/canvas/panel element |
| Leak check | 50 create/destroy cycles; listeners return to baseline |

## Verification commands

```bash
# P0
uv run python -m pytest tests/unit/experiment/test_dashboard_capture.py -q

# Targeted dashboard tests
uv run python -m pytest tests/unit/experiment/test_dashboard_events.py \
  tests/unit/experiment/test_dashboard_mirror.py \
  tests/unit/experiment/test_dashboard_run_status.py \
  tests/unit/experiment/test_dashboard_actions.py -q

# Frontend build
cd computronium/experiment/execution/dashboard && npm run build

# Probe
uv run python scripts/probes/dashboard_layout_probe.py --store experiment.duckdb

# Hero without a campaign
uv run python scripts/capture_dashboard_screenshot.py --reuse-store --port 8084
```

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Dockview bundle weight | Measure gzip at P2; tree-shake; core is zero-dep. `LayoutHost` keeps GL available. |
| Multi-WebGL context limit | Warn at 4 3D stages; `StageSurface` seam for shared offscreen rendering. |
| View conversion drags | `LegacyStageViewAdapter` keeps unmigrated views working per instance. |
| Per-instance subscriptions leak | Definition contract + 50-cycle probe + listener counts. |
| Persistence schema drift | Versioned envelope; sanitize unknown components; default preset fallback. |
| Data refactor breaks charts | Keep `RunMetrics` shape; stores return the same payloads; HTTP fallback. |
| Capture depends on old globals | Stable `__DASHBOARD__.debug` in P5; update scripts then. |
| Dockview update churn | Pin `^8.6.1`; adapter isolates API surface. |

## Definition of done

- [ ] Dockview host is the only engine import; GL removed after parity.
- [ ] Component, instance, and stage-view factories; no UI singletons.
- [ ] Multiple instances of any type/view with independent state.
- [ ] Docking, resize, tabs, floating, maximize, duplicate, undo/redo.
- [ ] One CSS source; generated palette in `src/`; Dockview CSS imported once.
- [ ] WS pong, no leaks, serialized sends, no reconnect.
- [ ] Metrics/space cached per key; catalog-driven selection; one ingest.
- [ ] Capture/tour reuse an existing store; no campaign re-runs.
- [ ] Flexibility acceptance matrix passes.

## Final verification notes

- `dockview-core` latest verified at **8.6.1**, MIT, zero dependencies
  (5.5 MB unpacked; bundle size must be measured, not assumed).
- GoldenLayout 2.6.0 is the last release (Sep 2022); in-app floating panels
  remain unsupported.
- Dockview API confirmed for vanilla TypeScript: `createDockview`,
  `createComponent` + `init(params.containerElement)`, `addPanel` with
  `params`/`floating`/`position`, `updateParameters`, `toJSON`/`fromJSON`,
  `onDidLayoutChange`, `addFloatingGroup`, `maximizeGroup`, `undo`/`redo`.
- The prior plan's persistence contradiction is resolved by separating
  `LayoutSpec` (neutral presets) from `LayoutDocument` (engine payload +
  validated instance mirror).
- The per-instance axes problem is resolved by shared `MetricsStore`/
  `SpaceStore` fetching with per-instance derivation, not per-instance fetches.
- Remaining implementation risk is effort, not architecture: P6 is the long
  pole (25 view modules), and P2 must measure bundle size before removal of GL.
