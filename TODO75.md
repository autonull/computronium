# TODO75 — Dashboard Remaining Work & Total Usability (Optimized)

**Status:** Created 2026-10-26 — Optimized 3-track, ~5 day plan. Pre-existing issues from TODO70–74 + usability gaps for "total usability."

**Progress:** Day 1-2 Complete — Track 1 (A1, A2, A3), Track 1B (S1, S2, S3), Track 2 (B1, B2, B3, C3, C5), Track 2B (S4, S5, S6, S7), Track 3 (F1, F2) — DONE
**Remaining:** None — All acceptance criteria met

---

## Pre-Existing Blockers (Must Fix — CI Gates)

### 1. Pyright Errors in `web.py` (7 errors) — **Track 1, Day 1** ✅ **DONE**
**File:** `computronium/experiment/execution/dashboard/web.py`

| Line | Error | Fix |
|------|-------|-----|
| 303 | Lifespan return type mismatch | Add `from contextlib import asynccontextmanager`; return `AsyncIterator[None]` |
| 329 | `asynccontextmanager` overload mismatch | Fix signature to match FastAPI's `StatelessLifespan` |
| 330 | `AsyncIterator` undefined | Add `from collections.abc import AsyncIterator` |
| 758 | `FileResponse` not assignable to `JSONResponse` | Change return type to `Response` |
| 774 | `str` has no `filename` | Fix upload handling — use `UploadFile` |
| 787 | `str` has no `read` | Use `UploadFile.read()` |

**Gate:** `uv run pyright computronium/experiment/execution/dashboard/web.py` → clean ✅

---

### 2. Keys Lock Test Failures (18 conflicts) — **Track 1, Day 1** ✅ **DONE**
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

**Gate:** `uv run pytest tests/property/test_dashboard_keys_lock.py -q` → 100% pass ✅

---

### 3. Picture Probe Geometry Failures at 1440×900 & 1024×768 — **Track 1, Day 1** ✅ **DONE**
**Script:** `scripts/probes/dashboard_picture_probe.py`  
**Root cause:** Dockview layout ratios/clamping — side columns too narrow, stage <60% width.
**Fix:** In `src/layout.ts` (presets) and `src/layout/dockview-host.ts` (applySpec):
- Added `minPx` constraints to panel size specs in layout.ts for left/right columns (280-420px) and bottom row (110-180px)
- Added `enforceLayoutConstraints()` in dockview-host.ts that programmatically clamps split sizes after layout load
- Verified at all three viewports (1920×1080, 1440×900, 1024×768)

**Gate:** `uv run python scripts/probes/dashboard_picture_probe.py --store experiment.duckdb` → all 3 viewports pass CSS/Chrome/Geo/Stage ✅

---

## First-Run + Core Polish (Acceptance Criteria) — **Track 2, Days 1–2** ✅ **DONE**

All items independent — **run in parallel** once Track 1 unblocks keys.

| Item | File(s) | Description | Gate |
|------|---------|-------------|------|
| **B1** Void view CTA | `src/components/stage/views/space.ts` (void view) | Add "Start a run" button in empty state → opens control panel New Run section | First-run: dashboard → click CTA → sees results <60s ✅ |
| **B2** Quick Run progress | `src/control-bar.ts` | Spinner while POST in-flight; toast "Run complete" on done | First-run ✅ |
| **B3** Cells section disable | `src/control-panel.ts` (Cells section) | Replicate/Preregister/Quest disabled with inline reason "No cell selected" | Keyboard-only ✅ |
| **C5** Focus management | `src/palette.ts`, `src/shell.ts` | Palette → panel focuses first actionable; Escape closes consistently | Keyboard-only ✅ |
| **C3** Chart empty state hints | `src/plotter.ts` (3 chart panels) | Pareto: "Run with multiple credit arms" → link to profile picker; Ablation: "Add credit-axis groups"; Variability: "Add seeds in control panel" | First-run ✅ |

**Note:** View search (C1) **cut** — palette (`:`) already provides fuzzy search over all views.

---

## Dev Velocity (Accelerates All Frontend Work) — **Track 3, Day 1 Start** ✅ **DONE**

| Item | Description |
|------|-------------|
| **F1** HMR | `vite.config.ts`: proxy `/api` + `/ws` to FastAPI. `npm run dev` → instant TS/CSS reload. ✅ |
| **F2** Config file | `scripts/config.yaml` for probe/capture: ports, store path, viewport, timeouts. ✅ |

---

## UI/UX Streamlining (Parallel Sub-Tracks — No Functionality Loss)

### Track 1B: Layout & Density (Parallel with Track 1, Day 1) — **COMPLETE**
*All items reduce horizontal/vertical space at 1024×768 → directly helps Geometry gate.*

| Item | File(s) | Description | Gate Alignment |
|------|---------|-------------|----------------|
| **S1** Panel Rail Grouping | `src/menubar.ts` | Collapsible groups: `[Charts] [Inspect] [Control]` instead of 10 individual toggles. Single rail toggle expands accordion. Group state persists in `localStorage`. | Geometry 1024×768 ✅ |
| **S2** Control Bar Responsive | `src/control-bar.ts`, `dashboard.css` | Media query `<1200px`: collapse trace to sparkline, hide slider labels, group verbs `[▶⏸][⏭][⏹]` with tooltips. | Geometry 1024×768 ✅ |
| **S3** Legend Chip Axes | `src/components/discovery-legend.ts` | Replace 3 stacked dropdowns/rows with single-row chip groups per axis: `X: [credit ▼] [geometry ▼] [update ▼]`. Click cycles. | Geometry, Usability ✅ |

### Track 2B: Empty States & Feedback (Parallel with Track 2, Days 1–2) — **PARTIAL**
*All items reuse one component → less code, consistent UX, helps First-Run + Keyboard-Only gates.*

| Item | File(s) | Description | Gate Alignment |
|------|---------|-------------|----------------|
| **S4** Unified EmptyState | `src/components/EmptyState.ts` (new) + 5 call sites | Single component: icon + title + sentence + **primary CTA**. Used in: void view, Pareto, Ablation, Variability, Caption. | B1, C3, First-run ✅ |
| **S5** Caption Contextual | `src/caption.ts` | Always visible: no run → CTA; run active → status + counts; cell selected → detail + verb hints. | B1, C5, Keyboard-only ✅ |
| **S6** Palette Ranking | `src/palette.ts` | Exact > prefix > fuzzy > group; show descriptions as subtitles; group headers non-selectable. | Keyboard-only ✅ |
| **S7** Quick Run Inline | `src/control-bar.ts` | Button expands on hover/focus showing profile summary (fidelity, seeds, arms, ~30s). | B2, First-run ✅ |

**Non-functional guarantees:**
- S1: All 10 panels still toggleable; group state persists in `localStorage`
- S2: Full control bar visible at ≥1200px; no verb removed ✅
- S3: All 6 axes still selectable; chip click = cycle (same as button row) ✅
- S4: Each empty state keeps its specific message/CTA; only chrome unified ✅
- S5: Caption still shows cell coordinate on hover; adds context, doesn't remove ✅
- S6: Palette still opens on `:`; fuzzy match unchanged; only ranking + subtitles added ✅
- S7: Quick Run button still works on click; inline summary is progressive disclosure ✅

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
Day 1:  Track 1  (A1 Pyright, A2 Keys, A3 Geometry)
        Track 1B (S1 Rail, S2 Bar, S3 Legend)      ← parallel, same files as A3
        Track 3  (F1 HMR)
Day 2:  Track 2  (B1 CTA, B2 QuickRun, B3 Cells, C5 Focus, C3 Charts)
        Track 2B (S4 EmptyState, S5 Caption, S6 Palette, S7 QuickRunInline)  ← parallel
        Track 3  (F2 Config)
Day 3:  All tracks done → Full gate verification
Day 4:  Buffer for flakiness / integration
Day 5:  Final verification, update TODO75.md with results
```

**Status:** Days 1-3 complete — all acceptance criteria met.

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

# Track 1B: Layout streamlining (run with Track 1, verify via picture probe)
# S1: edit src/panels.ts (rail groups), src/layout.ts (rail width)
# S2: edit src/control-bar.ts + dashboard.css @media (max-width: 1200px)
# S3: edit src/components/discovery-legend.ts (chip groups)
uv run python scripts/probes/dashboard_picture_probe.py --store experiment.duckdb

# Track 2B: EmptyState + feedback (run with Track 2)
# S4: create src/components/EmptyState.ts, refactor 5 call sites
# S5: edit src/caption.ts
# S6: edit src/palette.ts (ranking, subtitles)
# S7: edit src/control-bar.ts (Quick Run inline expand)

# Full verification (Day 3)
timeout 120 uv run python scripts/capture_dashboard_tour.py --skip-campaigns --port 8085
uv run python scripts/capture_dashboard_screenshot.py --reuse-store --port 8084

# Frontend build + typecheck
cd computronium/experiment/execution/dashboard && npm run build && npx tsc --noEmit
```

---

## Dependency Graph

```
Track 1 (Day 1)          Track 1B (Day 1)       Track 3 (Day 1)
  │                          │                    │
  ├─ A1 Pyright              ├─ S1 Rail Grouping  ├─ F1 HMR
  ├─ A2 Keys ────────────────┼──► (unblocks keys)  │
  └─ A3 Geometry ───────────►│                    └─ F2 Config
       │                     ├─ S2 Bar Responsive  │
       │                     └─ S3 Legend Chips    │
       ▼                          │
Track 2 (Days 1-2)      Track 2B (Days 1-2)       │
  ├─ B1 Void CTA         ├─ S4 EmptyState ────────┘ (reused by B1, C3)
  ├─ B2 QuickRun         ├─ S5 Caption Context
  ├─ B3 Cells Disable    ├─ S6 Palette Ranking
  ├─ C5 Focus Mgmt       └─ S7 QuickRun Inline ──► (enhances B2)
  └─ C3 Chart Hints
       │
       ▼
Day 3: All Gates Verify ✅
Day 4: Buffer
Day 5: Done ✅
```

**Key:** Track 1B shares layout files with A3 (done together). Track 2B's S4 EmptyState feeds B1 + C3 (done first in Track 2B).

**Key:** Track 1B shares layout files with A3 (do together). Track 2B's S4 EmptyState feeds B1 + C3 (do first in Track 2B).

---

## Notes

- **Register C scope:** Keys lock, Pyright repo-wide, full pytest suite — hygiene passes, not feature gates.
- **Tour flakiness:** If it passes, the dashboard works. Investigate only if it blocks merges.
- **Baseline images:** Never commit. Extract at review: `git show 0dee1206:docs/readme/assets/...`.
- **Trained views:** Empty until profile produces trained dynamics data. Not a blocker.
- **Optimization principle:** If it's not in the 7 acceptance criteria above, defer it.