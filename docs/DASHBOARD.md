# The Dashboard Guide

This guide documents the dashboard's chrome — the bindings, the docks, the workspaces, the palette, the registries, and the view taxonomy. It is the technical companion to the README's pictures.

---

## The Binding Layer

Every verb the reader can press is declared once, in `src/bindings.ts`. The table is the single source of truth for:

- The dispatcher (in `main.ts`)
- The panel rail (in `panels.ts`)
- The help overlay (in `help-overlay.ts`)
- The command palette (in `palette.ts`)
- The property lock test (in `tests/property/test_dashboard_keys_lock.py`)

### Binding Record

```typescript
interface Binding {
  id: string;              // unique identifier
  label: string;           // what the reader sees
  group: string;           // logical group
  key?: string;            // single key
  chord?: string;          // chord (e.g., "shift+r")
  when?: "always" | "cell-selected" | "run-active";
  run: () => void;         // what it does
}
```

### Groups (in display order)

| Group | Holds |
|-------|-------|
| Navigation | `V` (cycle view), `1–9` (pick view), `, . /` (punctuation views) |
| Panels | `h` (HUD), `r` (live rail), `c` (caption), `q` (legend) |
| Charts | `p` (Pareto), `a` (ablation), `v` (variability) |
| Run Control | `Space` (play/pause), `⏭` (step), `⏹` (stop) |
| Cell Actions | `Shift+R` (replicate), `Shift+P` (preregister), `Shift+Q` (quest) |
| Stage | `w` (space), `e` (effect), `f` (flow), `t` (timeline), `l` (ledger), `d` (contrast) |
| General | `?` (help), `:` (palette) |

The key budget is maintained in `src/keys.ts` — `PUNCTUATION_KEYS = [",", ".", "/", "'"]` (the `;` moved to the palette).

---

## The Layout Grammar

Five docks — top strip, bottom strip, left column, right column, and floating — and one `LayoutManager` in `src/layout.ts` that owns coordinates, z-order, and membership.

### Docks

| Dock | Region | Default Width/Height |
|------|--------|---------------------|
| top | Full-width strip at top | 4px padding |
| bottom | Full-width strip at bottom | 4px padding |
| left | Left column | 320px |
| right | Right column | 520px |
| floating | Over the canvas | Full viewport |

A panel declares its preferred dock and default openness via `createPanelShell()`. The default placement table reproduces today's screen exactly.

### Default Placement (Watch Workspace)

| Panel | Dock | Order | Default Open |
|-------|------|-------|--------------|
| control-bar | bottom | 0 | ✅ |
| live-rail | right | 0 | ✅ |
| caption | bottom | 1 | ✅ |
| legend | bottom | 2 | ✅ |
| hud | top | 0 | ❌ |
| plotter-pareto | right | 1 | ✅ |
| plotter-ablation | right | 2 | ❌ |
| plotter-variability | right | 3 | ❌ |
| cell-drawer | floating | 0 | ❌ |
| control-panel | floating | 1 | ❌ |
| help-overlay | floating | 2 | ❌ |

---

## Workspaces

A workspace is one row of layout data — `{the view on the stage, the panels that are open, their dock order}` — read by the same manager. Three ship, plus the reader's own:

| Workspace | For | Arrangement |
|-----------|-----|-------------|
| **watch** | "watch campaigns in real time" | Today's default screen exactly |
| **audit** | the evidence and the judgement | Ledger view + three charts open |
| **drive** | the instrument — the verbs, the queue | Flow view + control panel open |
| **free** | whatever the reader arranged | Remembered; any manual change moves here |

Switching is one action: a `watch · audit · drive` segmented control on the control bar, and entries in the palette. No letter keys — the alphabet is spent.

**Persistence**: `localStorage`, versioned (`computronium.layout.v1`: workspace, view, open panels, dock order). A version bump clears it. The tour calls `layout.reset()` before every shot set.

---

## The Command Palette

Opens on **`:`** (shift-`;`). It fuzzy-matches the binding table, the views, the panels, the cell verbs, and the workspaces. Enter runs; Esc closes. Focus-trapped, arrow-navigable.

### Groups (in order)

| Group | Holds |
|-------|-------|
| **the next question** | start a run · replicate the selected cell · preregister a claim · adopt a cell as a quest · the queue |
| **workspaces** | watch · audit · drive · free · reset |
| **views** | all 25, in the six sections |
| **panels** | all 11 |
| **verbs** | play/pause · step · stop · help |

A cell verb without a selected cell is disabled with the reason — the honesty rule applied to the palette.

**The first-run door**: When the store holds no run, the palette's top entry is *start a run*, pointing at the control panel's New run section.

---

## The Registries

### View Registry (`src/stage/registry.ts`)

Views self-register on import. The switcher consumes; the 25-constructor list is gone.

```typescript
// In each view file:
registerView(new MyView());
```

**Cheap arrival**: the next view is one file plus one registry row.

### Chart Registry (in `plotter.ts`)

The `ChartSpec` pattern already existed. Three charts ship through it; a chart is its file plus its row.

### Control Panel Sections (TODO: `control-panel.ts` → shell + five modules)

Each section registers itself; the panel is a shell hosting them.

### Cell Verbs (`src/verbs.ts` — TODO)

Typed calls replacing `window.dispatchEvent(new CustomEvent(...))`.

---

## The View Taxonomy

The toolbar's six groups are the README's own section names. A section of the README is a run of the toolbar.

| Group | Views | The README's words |
|-------|-------|-------------------|
| **the space** | space, terrain, frontier, matrix, convergence, layers, multirun, slices | "the space it is searching" · "the space cut into sheets" · "two runs in one space" |
| **the run** | multiples, spread, cost, uncertainty | "the same run, drawn four ways" |
| **the evidence** | timeline, ledger, contrast | "the run's evidence, four ways again" |
| **the process** | flow, effect | "the run's cells as they went through the pipeline" |
| **the judgement** | trajectory, spectrum, basin, landscape | "the run as a process, and as a judgement" |
| **the system** | trained-trajectory, trained-spectrum, trained-basin, trained-landscape | "the system itself, rather than its bookkeeping" |

The glyph grammar stays by *kind* (solids for 3D views, marks for flat ones) — a glyph says what a view is drawn with; a group says what it is for.

---

## The Store, Split

`src/stage/state.ts` (840 lines) became three modules:

| Module | Holds |
|--------|-------|
| `payloads.ts` | All interfaces + utility functions (`cellKey`, `mean`, `stddev`, `meanCurve`, `indexSpaceCells`, `aggregateRecords`, `measuredCells`, `varyingAxes`, `cellLabel`, `measuredValues`) |
| `store.ts` | `StageState` class: state, `onChange`/`notify`, `absorb`, `setAxes`, `recomputeEvidence`, `sync*` methods calling fetchers |
| `sources.ts` | Eight `fetch*` functions — the **only** code that knows how to ask the server |

**Key property**: Views import from `store.ts` and `payloads.ts`; **no view imports a fetcher**.

---

## Keyboard Shortcuts Reference

| Key | Action | When |
|-----|--------|------|
| `?` | Toggle help overlay | Always |
| `:` | Open command palette | Always |
| `V` | Cycle view | Always |
| `1–9` | Pick view by number | Always |
| `,` | Slices view | Always |
| `.` | (reserved) | — |
| `/` | (reserved) | — |
| `'` | (reserved) | — |
| `Space` | Play / pause | Run active |
| `⏭` | Step one batch | Run active |
| `⏹` | Stop at boundary | Run active |
| `h` | Toggle HUD | Always |
| `r` | Toggle live rail | Always |
| `c` | Toggle caption | Always |
| `q` | Toggle legend | Always |
| `p` | Toggle Pareto chart | Always |
| `a` | Toggle ablation chart | Always |
| `v` | Toggle variability chart | Always |
| `w` | Space view | Always |
| `2` | Terrain view | Always |
| `3` | Frontier view | Always |
| `4` | Matrix view | Always |
| `5` | Convergence view | Always |
| `6` | Small multiples | Always |
| `7` | Spread | Always |
| `8` | Claim cost | Always |
| `9` | Uncertainty | Always |
| `t` | Timeline | Always |
| `l` | Ledger | Always |
| `d` | Contrast | Always |
| `f` | Flow | Always |
| `e` | Effect | Always |
| `y` | Layers | Always |
| `j` | Trajectory | Always |
| `m` | Spectrum | Always |
| `b` | Basin | Always |
| `n` | Landscape | Always |
| `g` | Trained trajectory | Always |
| `i` | Trained spectrum | Always |
| `k` | Trained basin | Always |
| `o` | Trained landscape | Always |
| `u` | Multi-run | Always |
| `Shift+R` | Replicate selected cell | Cell selected |
| `Shift+P` | Preregister claim | Cell selected |
| `Shift+Q` | Adopt as quest | Cell selected |

---

## Endpoints

The dashboard reads from these server endpoints:

| Endpoint | Returns | Used by |
|----------|---------|---------|
| `GET /api/control` | Control plane state | Control bar polling |
| `POST /api/cells/{run_id}/space` | `SpacePayload` | Discovery map, terrain, matrix, layers, slices |
| `GET /api/runs/{run_id}/account` | `RunAccount` | Ledger, contrast, claim cost, uncertainty |
| `GET /api/events?run_id=...` | `RunTimeline` | Timeline, flow |
| `GET /api/runs/{run_id}/flow` | `RunFlow` | Flow view |
| `GET /api/runs/{run_id}/attribution` | `RunAttribution` | Effect view |
| `GET /api/runs/{run_id}/dynamics` | `CellDynamics` | Trajectory, spectrum, basin, landscape |
| `GET /api/runs/{run_id}/dynamics/trained` | `CellDynamics` | Trained trajectory, spectrum, basin, landscape |
| `POST /api/spaces` | `MultiRunSpace` | Multi-run view |
| `GET /api/narration` | `{ script: string }` | Caption, narration endpoint |

---

## Debug Handle

`window.__DASHBOARD__` exposes:

```typescript
{
  scene, camera, renderer, controls,
  discoveryMap, cellDrawer, plotter, liveRail, caption, hud, helpOverlay, viewSwitcher,
  controlBar, controlPanel, panels, layout, palette,
  wsClient, router,
  bindings: { list: () => [{ id, label, group, key }, ...] },
}
```

The tour and any agent can enumerate verbs without scraping prose.