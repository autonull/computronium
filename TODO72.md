# TODO72 — Dashboard Fix Plan & Status (Screenshot-Verified)

## Summary

The dashboard was showing a blank screen because:
1. **WebSocket connection bug**: The WebSocket handler was sending periodic updates on its own connection, causing "Cannot call send once a close message has been sent" errors when the client disconnected.
2. **SpaceView not registered**: The discovery map view wasn't in the view switcher's registry, so key "1" didn't switch to it.
3. **Late-joining clients missed campaign_metrics**: The replay only sent the last 50 events, but campaign_metrics for completed runs were older than that.

## Fixes Applied

### 1. WebSocket Handler (web.py)
- **Changed**: `_handle_websocket` now just keeps connection alive with `receive_text()` instead of sending periodic updates
- **Update loop** (`_update_loop`) now broadcasts `status_update` and `queue_update` messages that frontend handlers expect
- **Added**: `_replay_events` sends campaign_metrics for all runs with records on new connection

### 2. View Switcher (switcher.ts)
- **Added**: SpaceView registration at module level with `registerView(new SpaceView())`
- **Modified**: `buildKeys()` prioritizes SpaceView as key "1"
- **Fixed**: Default view now "space" (was first view in list)

### 3. Discovery Map (discovery-map.ts)
- **Fixed**: `createRunPicker()` and `updateRunPicker()` called in `init()` so the run picker exists before replay messages arrive
- **Added**: `registerDisplayPanel("discovery-legend", ...)` so the legend panel is registered with the panel system

### 4. Shell (shell.ts)
- **Added**: `panelElementRegistry` Map to track panel elements before GoldenLayout appends them to DOM
- **Fixed**: `getPanelElement()` now checks registry first, then DOM

### 5. Main (main.ts)
- **Exposed**: `runSelection` on `window.__DASHBOARD__` for debugging

### 6. Build System
- Rebuilt TypeScript bundle with `npm run build`

## Status

| Priority | Task | Status |
|----------|------|--------|
| 1 | Debug campaign_metrics Replay | ✅ **DONE** - logs show "Sending initial campaign metrics on connect", WebSocket receives `campaign_metrics` on connect |
| 2 | Fix runSelection Auto-Select | ✅ **DONE** - `runSelection.selectedId` auto-set to newest run |
| 3 | Default to Space View | ✅ **DONE** - `activeView` is "space" |
| 4 | Optimize Capture Scripts | ⏳ Pending |
| 5 | Full Tour | ⏳ Pending |

## Current Blocker: GoldenLayout Panels Not Rendering
The `discovery-legend` panel element is created and registered, but GoldenLayout doesn't display it. The factory functions registered in `main.ts` return `null` because the elements aren't in the DOM yet (GoldenLayout creates them lazily). The `panelElementRegistry` in `shell.ts` tracks them, but GoldenLayout's component registration expects the factory to return the element immediately.

**Root cause**: GoldenLayout components are registered with factories that call `getPanelElement(id)` which returns `null` until the element is appended to DOM by GoldenLayout. This is a circular dependency - GoldenLayout calls the factory to get the element to append, but the factory expects the element to already exist.

**Next step**: Fix the factory functions to create elements on-demand, or register components with GoldenLayout after elements are created.

**Debug steps (no campaign re-run needed):**
```bash
# 1. Start dashboard with existing experiment.duckdb (already has 20 records)
uv run python -c "
from computronium.experiment.execution.dashboard.web import run_dashboard
import asyncio
asyncio.run(run_dashboard(host='127.0.0.1', port=8084, store_path='experiment.duckdb'))
" 2>&1 | tee /tmp/dash.log &

# 2. Check logs for "Sending initial campaign metrics on connect"
sleep 5
grep -E "(Sending initial|Could not send|Found.*runs|Run.*records)" /tmp/dash.log

# 3. Browser test - connect and verify stageState gets runId
uv run python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--no-sandbox', '--disable-dev-shm-usage', '--force-device-scale-factor=1'])
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})
    page.goto('http://127.0.0.1:8084/')
    page.wait_for_selector('#dashboard-canvas')
    page.wait_for_function('() => window.__DASHBOARD__.wsClient && window.__DASHBOARD__.wsClient.isConnected')
    page.wait_for_timeout(3000)  # Wait for replay
    ss = page.evaluate('() => window.__DASHBOARD__.stageState')
    print(f'runId: {ss.runId}')
    print(f'metrics.run: {ss.metrics?.run?.run_id}')
    print(f'space.counts: {ss.space?.counts}')
    print(f'aggregates.size: {ss.aggregates?.size}')
    browser.close()
"
```

**If replay still fails:** Add `logger.exception` in `_replay_events` catch block (already done), check `/tmp/dash.log` for stack trace. Likely cause: `_readable_store()` deadlocks or `_get_campaign_metrics_detailed` hangs.

**Fix if deadlock:** Move campaign_metrics fetch to a background task, or pre-fetch on startup and cache.

### Priority 2: Fix runSelection Auto-Select
When campaign_metrics arrives, `runSelection.observe()` is called but the legend's dropdown doesn't auto-select.

**Fix in `src/run-selection.ts`:** The `observe()` method already sets `selectedRunId = newestRunId()` when `!chosenByReader`. Verify `newestRunId()` works with the incoming metrics.

**Test:** After Priority 1 works, check if `legend-run-picker` shows the run auto-selected.

### Priority 3: Default to Space View
Dashboard starts on "basin" view (index 0). Should start on "space".

**Fix in `src/stage/switcher.ts` line 94:**
```typescript
// Change from:
this.show(this.views[0].id);
// To:
this.show("space");
```

### Priority 4: Optimize Capture Scripts (Avoid Re-running Campaigns)
Current `capture_dashboard_screenshot.py` clears store and re-runs demo campaign (30-60s waste). 

**Change:** Use existing `experiment.duckdb` with `--store experiment.duckdb` and `--no-clear-store` flag (add if needed). Or create a test mode that uses pre-existing data.

**Minimal fix:** Modify `dashboard_capture.py` `clear_store()` to be optional, and `run_demo_campaign()` to be skipped if store already has ≥20 records.

### Priority 5: Full Tour
Once hero shot works, run tour:
```bash
uv run python scripts/capture_dashboard_tour.py --port 8084
```

## Efficient Verification Workflow

### Quick Cycle (30s per iteration)
```bash
# Terminal 1: Dashboard with debug logging
cd /home/me/computronium && uv run python -c "
from computronium.experiment.execution.dashboard.web import run_dashboard
import asyncio, logging
logging.basicConfig(level=logging.DEBUG)
asyncio.run(run_dashboard(host='127.0.0.1', port=8084, store_path='experiment.duckdb'))
" 2>&1 | tee /tmp/dash.log &

# Terminal 2: Browser test (10s)
sleep 3
uv run python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--no-sandbox', '--disable-dev-shm-usage', '--force-device-scale-factor=1'])
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})
    page.goto('http://127.0.0.1:8084/')
    page.wait_for_selector('#dashboard-canvas')
    page.wait_for_function('() => window.__DASHBOARD__.wsClient && window.__DASHBOARD__.wsClient.isConnected')
    page.wait_for_timeout(3000)
    ss = page.evaluate('() => window.__DASHBOARD__.stageState')
    print('runId:', ss.runId)
    print('space:', ss.space?.counts)
    print('aggregates:', ss.aggregates?.size)
    dm = page.evaluate('() => window.__DASHBOARD__.discoveryMap.cellDataMap.size')
    print('cellDataMap:', dm)
    measured = page.evaluate('''() => {
        let m = 0;
        for (const c of window.__DASHBOARD__.discoveryMap.cellDataMap.values()) if (c.status === "measured" && c.metrics?.n_seeds) m++;
        return m;
    }''')
    print('measured cells:', measured)
    page.keyboard.press('1')
    page.wait_for_timeout(1000)
    page.screenshot(path='/tmp/verify.png')
    print('Screenshot: /tmp/verify.png')
    browser.close()
"
```

### Hero Shot (2min)
```bash
uv run python scripts/capture_dashboard_screenshot.py --port 8084 --min-records 20 --store experiment.duckdb
```

## Architecture Notes

### Key Files
| File | Purpose |
|------|---------|
| `web.py` | FastAPI + WebSocket server, campaign_metrics broadcast |
| `src/main.ts` | Three.js entry, component init, bindings |
| `src/discovery-map.ts` | 3D grid (measured/legal/void cells) |
| `src/stage/switcher.ts` | View switcher (25 views, 6 groups) |
| `src/stage/store.ts` | Shared state (space, aggregates, run) |
| `src/run-selection.ts` | Which run the dashboard shows |

### Data Flow
```
Campaign writes → DuckDB → Mirror → Dashboard reads → WebSocket → Browser
                              ↓
                         campaign_metrics message → runSelection.observe()
                                                    ↓
                                           stageState.absorb() → notify("space")
                                                    ↓
                                        discoveryMap.applyAxes() → buildGrid()
```

## Success Criteria

- [ ] Hero screenshot captures without timeout (measured cells visible)
- [ ] All 70+ tour screenshots capture
- [ ] Each view differs by >2% from others
- [ ] No WebSocket errors in logs
- [ ] Dashboard works on fresh browser (no cache)
- [ ] No unnecessary campaign re-runs during development