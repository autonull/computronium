# TODO75 — Dashboard Remaining Work & Total Usability (Optimized)

**Status:** Created 2026-10-26 — Optimized 3-track, ~5 day plan. Pre-existing issues from TODO70–74 + usability gaps for "total usability."

---

## Pre-Existing Blockers (Must Fix — CI Gates)

### 1. Pyright Errors in `web.py` (7 errors) — **Track 1, Day 1**
**File:** `computronium/experiment/execution/dashboard/web.py`

| Line | Error | Fix |
|------|-------|-----|
| 303 | Lifespan return type mismatch | Add `from contextlib import asynccontextmanager`; return `AsyncIterator[None]` |
| 329 | `asynccontextmanager` overload mismatch | Fix signature to match FastAPI's `StatelessLifespan` |
| 330 | `AsyncIterator` undefined | Add `from collections.abc import AsyncIterator` |
| 758 | `FileResponse` not assignable to `JSONResponse` | Change return type to `Response` |
| 774 | `str` has no `filename` | Fix upload handling — use `UploadFile` |
| 787 | `str` has no `read` | Use `UploadFile.read()` |

**Gate:** `uv run pyright computronium/experiment/execution/dashboard/web.py` → clean

---

### 2. Keys Lock Test Failures (18 conflicts) — **Track 1, Day 1**
**File:** `src/bindings.ts` + view keys in `src/components/stage/views/*.ts`

| Key | Conflicts | Resolution |
|-----|-----------|------------|
| `w` | `control-step` + `preset-watch` | Preset → `shift+w` (chord) |
| `a` | `chart-ablation` + `preset-audit` | Preset → `shift+a` |
| `d` | `preset-drive` + `contrast` view | Preset → `shift+d`; view → `,` (punctuation) |
| `f` | `preset-free` + `flow` view | Preset → `shift+f`; view → `.` |
| `c` | `panel-caption` + `claim-cost`, `convergence` | Views → `/`, `'` |
| `r` | `panel-rail` + `terrain` | View → `shift+r` (chord) |
| `s` | `chart-variability` + `spread` | View → `shift+s` |
| `x` | `control-stop` + `matrix` | View → `shift+x` |
| `m` | `small-multiples` + `spectrum` | One → `shift+m` |
| `u` | `frontier` + `multirun` | One → `shift+u` |
| `y` | `layers` only | Keep `y` (no binding conflict) |

**Rule:** Presets lose direct keys → chords. Views take punctuation reserve (`,`, `.`, `/`, `'`), then chords. No letter claimed twice across bindings + views.

**Gate:** `uv run pytest tests/property/test_dashboard_keys_lock.py -q` → 100% pass

---

### 3. Picture Probe Geometry Failures at 1440×900 & 1024×768 — **Track 1, Day 1**
**Script:** `scripts/probes/dashboard_picture_probe.py`  
**Root cause:** Dockview layout ratios/clamping — side columns too narrow, stage <60% width.

**Fix:** In `src/layout.ts` (presets) and/or `layout/dockview-host.ts` (applySpec):
- Increase `minSize` for left/right columns at small viewports
- Ensure stage panel gets ≥60% width at 1024×768
- Clamp bottom bar height so it doesn't crowd stage

**Gate:** `uv run python scripts/probes/dashboard_picture_probe.py --store experiment.duckdb` → all 3 viewports pass CSS/Chrome/Geo/Stage

---

## First-Run + Core Polish (Acceptance Criteria) — **Track 2, Days 1–2**

All items independent — **run in parallel** once Track 1 unblocks keys.

| Item | File(s) | Description | Gate |
|------|---------|-------------|------|
| **B1** Void view CTA | `src/components/stage/views/space.ts` (void view) | Add "Start a run" button in empty state → opens control panel New Run section | First-run: dashboard → click CTA → sees results <60s |
| **B2** Quick Run progress | `src/control-bar.ts` | Spinner while POST in-flight; toast "Run complete" on done | First-run |
| **B3** Cells section disable | `src/control-panel.ts` (Cells section) | Replicate/Preregister/Quest disabled with inline reason "No cell selected" | Keyboard-only |
| **C5** Focus management | `src/palette.ts`, `src/shell.ts` | Palette → panel focuses first actionable; Escape closes consistently | Keyboard-only |
| **C3** Chart empty state hints | `src/plotter.ts` (3 chart panels) | Pareto: "Run with multiple credit arms" → link to profile picker; Ablation: "Add credit-axis groups"; Variability: "Add seeds in control panel" | First-run |

**Note:** View search (C1) **cut** — palette (`:`) already provides fuzzy search over all views.

---

## Dev Velocity (Accelerates All Frontend Work) — **Track 3, Day 1 Start**

| Item | Description |
|------|-------------|
| **F1** HMR | `vite.config.ts`: proxy `/api` + `/ws` to FastAPI. `npm run dev` → instant TS/CSS reload. |
| **F2** Config file | `scripts/config.yaml` for probe/capture: ports, store path, viewport, timeouts. |

---

## Deferred (Not in "Total Usability" Acceptance Criteria)

| Category | Items | Reason |
|----------|-------|--------|
| **Accessibility** | ARIA live regions, high contrast, reduced motion | Not in acceptance criteria; add later if needed |
| **Multi-instance/persistence** | Per-instance state save, floating bounds, tab overflow | Edge cases only |
| **Server reliability** | WS reconnection, queue push, store migration | Works today; not user-facing blockers |
| **Dev docs** | `__DASHBOARD__.debug` API docs | Low leverage |
| **Control bar trace hover** | CPU trace hover-expand | Nice-to-have |
| **Axis picker reset** | "Reset axes" button | Low priority |
| **Chart export parity** | Ablation/Variability PNG export | Low priority |

---

## Optimized Execution (5 Days)

```
Day 1:  Track 1 (A1 Pyright, A2 Keys, A3 Geometry) + Track 3 (F1 HMR)
Day 2:  Track 1 done → Track 2 (B1, B2, B3, C5, C3 all parallel) + Track 3 (F2 Config)
Day 3:  All tracks done → Full gate verification
Day 4:  Buffer for flakiness / integration
Day 5:  Final verification, update TODO75.md with results
```

---

## Acceptance Criteria (Minimal "Total Usability")

| Criterion | Command |
|-----------|---------|
| Zero Pyright errors | `uv run pyright computronium/experiment/execution/dashboard/web.py` |
| Keys lock passes | `uv run pytest tests/property/test_dashboard_keys_lock.py -q` |
| Picture probe 3 viewports | `uv run python scripts/probes/dashboard_picture_probe.py --store experiment.duckdb` |
| Tour <60s | `timeout 120 uv run python scripts/capture_dashboard_tour.py --skip-campaigns --port 8085` |
| First-run <60s no docs | Manual: open dashboard → CTA → Quick Run → results |
| Keyboard-only via palette | Manual: `:` → every verb reachable; focus ok; Escape works |
| Responsive 1024×768 | Covered by picture probe geometry gate |

---

## Quick Reference: Commands

```bash
# Track 1: Blockers
uv run pyright computronium/experiment/execution/dashboard/web.py
uv run pytest tests/property/test_dashboard_keys_lock.py -q
uv run python scripts/probes/dashboard_picture_probe.py --store experiment.duckdb

# Track 3: Dev velocity (start Day 1)
cd computronium/experiment/execution/dashboard
# Add to vite.config.ts: server: { proxy: { '/api': 'http://localhost:8080', '/ws': { target: 'ws://localhost:8080', ws: true } } }
npm run dev  # verify HMR

# Full verification (Day 3)
timeout 120 uv run python scripts/capture_dashboard_tour.py --skip-campaigns --port 8085
uv run python scripts/capture_dashboard_screenshot.py --reuse-store --port 8084

# Frontend build + typecheck
cd computronium/experiment/execution/dashboard && npm run build && npx tsc --noEmit
```

---

## Dependency Graph

```
Track 1 (Day 1)          Track 3 (Day 1)
  │                          │
  ├─ A1 Pyright              ├─ F1 HMR
  ├─ A2 Keys ────────────────┼──► (unblocks Track 2 key assignments)
  └─ A3 Geometry             └─ F2 Config
       │
       ▼
Track 2 (Days 1-2, parallel)
  ├─ B1 Void CTA
  ├─ B2 Quick Run progress
  ├─ B3 Cells disable
  ├─ C5 Focus mgmt
  └─ C3 Chart hints
       │
       ▼
Day 3: All Gates Verify
Day 4: Buffer
Day 5: Done
```

---

## Notes

- **Register C scope:** Keys lock, Pyright repo-wide, full pytest suite — hygiene passes, not feature gates.
- **Tour flakiness:** If it passes, the dashboard works. Investigate only if it blocks merges.
- **Baseline images:** Never commit. Extract at review: `git show 0dee1206:docs/readme/assets/...`.
- **Trained views:** Empty until profile produces trained dynamics data. Not a blocker.
- **Optimization principle:** If it's not in the 7 acceptance criteria above, defer it.