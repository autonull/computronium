# TODO74 — Dashboard: UI Polish, Progressive Disclosure & First-User Experience

**Status:** P11.0-P11.4 **COMPLETE (2026-10-26)** — All automated gates passing.

---

## Issues to Address

### 1. View/Parameter Update Reliability ✅ **FIXED**
- Stage view switch (toolbar select) sometimes doesn't rebuild view → **Fixed**: `update()` properly handles view/axes/runId changes
- Axis changes (from Discovery Legend) don't always propagate to stage → **Fixed**: `workspace.onChange()` → `ensureViewInstance()` chain works
- Space store subscription key includes `values` which changes on axes change - can cause duplicate fetches → **Fixed**: `SpaceStore` key now only uses `(runId, xAxis, yAxis, zAxis)`; held values come from payload
- Race conditions between `workspace.onChange()` and `spaceStore.subscribe()` → **Fixed**: Stable cache key eliminates duplicate fetches

### 2. Progressive Disclosure — Panels by Default ✅ **IMPLEMENTED**
**Before (all presets include everything):**
- Watch: Stage + Legend + Control Panel + HUD + Pareto + Ablation + Variability + Control Bar + Caption + Live Rail
- Audit: Same as Watch
- Drive: Stage + Control Panel + HUD + Live Rail (right column rearranged)
- Free: All floating

**After (progressive disclosure):**
- **Watch (default)**: Stage + Legend + Control Panel (left), Control Bar + Caption + Live Rail (bottom) — **NO right column** (6 panels)
- **Audit**: Watch + HUD (right column, single panel) (7 panels)
- **Drive**: Audit + Charts column (Pareto, Ablation, Variability) — right column with 4 panels (10 panels)
- **Free**: Everything, user-arranged + floating legend

**Charts (Pareto/Ablation/Variability):** Show empty state with clear hint; auto-show when run has relevant data

### 3. First-User Experience — Rapid Results ✅ **IMPLEMENTED**
- Added `quick-run` profile in experiment kernel: L0 fidelity, 1 seed, 1 epoch, multiple credit arms + geometries + updates (~30s)
- Added "Quick Run" button in Control Bar (gradient accent, disabled when run active)
- Button triggers `/api/runs` POST with `profile: "quick-run"`
- Shows "Started" feedback on success, "No Queue" when no campaign queue attached

### 4. View Switching & Parameter Flow ✅ **WORKING**
- Stage toolbar view select → `ctx.setState({ view })` → `update()` → `ensureViewInstance()`
- Discovery Legend axis buttons → `workspace.setAxes()` → `workspace.onChange()` → stage `ensureViewInstance()` → `resubscribe()` → `applyAxes()` → `spaceStore.get()` with stable key
- Space store key stabilized: `(runId, xAxis, yAxis, zAxis)` only

---

## Implementation Completed

### P11.0 — Fix View/Parameter Update Flow ✅
- [x] Stage component: `update()` properly handles view/axes/runId changes
- [x] Space store: stabilize cache key when axes change (ignore held values for key)
- [x] Discovery Legend: axis picker updates propagate correctly
- [x] Space view: cache held values separately, don't mutate `spaceValues` in place

### P11.1 — Progressive Disclosure Presets ✅
- [x] Redefined `PRESET_SPECS` in `layout.ts` with 4 tiers
- [x] Chart panels: show empty state with clear hint when no relevant data
- [x] Live Rail: starts collapsed (already did)

### P11.2 — Quick Run Profile & First-User Flow ✅
- [x] Added `quick-run` profile in `computronium/experiment/surface/_cli/_profiles.py`
- [x] Added "Quick Run" button in Control Bar
- [x] Button triggers `/api/runs` POST with `profile: "quick-run"`
- [x] Toast-like feedback on button (Started/No Queue/Error)

### P11.3 — Chart Panel Relevance & Empty States ✅
- [x] Pareto: relevant when `paretoFlags.some(f => f)` (Pareto cells exist)
- [x] Ablation: relevant when `ablationGroups.some(g => g.axis === "credit")`
- [x] Variability: relevant when any credit arm has >1 seed
- [x] Empty states: clear hint + status text indicating what's needed
- [x] Overrode `isRelevant()`, `updateStatus()`, and `refresh()` in each chart view

### P11.4 — Polish & Ergonomics ✅
- [x] Keyboard shortcuts: `W/A/D/F` for Watch/Audit/Drive/Free presets (added to `bindings.ts`)
- [x] `V` cycles stage views (already worked), `1-9` pick view (already worked)
- [x] Control Bar: Quick Run button + run status indicator
- [x] Caption: shows current cell coordinate + status when hovering (already worked via space view readout)

---

## Definition of Done
- [x] View switch + axis change work reliably (no stuck views, no duplicate fetches)
- [x] Default "Watch" preset is clean: 6 panels max, stage dominant
- [x] Charts appear progressively when relevant data exists
- [x] "Quick Run" generates diverse data in ~30s from cold start
- [x] All automated gates still pass (capture, tour) — verified 2026-10-26
- [x] No regression in multi-instance support

## Gate Verification (2026-10-26)
- **capture_dashboard_screenshot.py**: ✅ Hero shot 307 KB, stage ready with 4 measured cells
- **capture_dashboard_tour.py**: ✅ 4 presets + 25 stage views + 10 panels, no console/page errors, no duplicate DOM ids
- **probe_dashboard_views.py**: ⚠️ Uses legacy `#dashboard-canvas` selector (pre-docking architecture); not a gate