# TODO75 — Dashboard Remaining Work & Total Usability

**Status:** Created 2026-10-26 — Capturing all pre-existing issues from TODO70–74 and new items for total usability.

---

## Pre-Existing Issues (Carried from TODO70–74)

### 1. Keys Lock Test Failures (18 failures) — Register C Hygiene
**File:** `tests/property/test_dashboard_keys_lock.py`  
**Root cause:** `src/bindings.ts` has duplicate letter claims:

| Key | Conflicting Bindings | Conflicting Views |
|-----|---------------------|-------------------|
| `w` | `control-step` + `preset-watch` | — |
| `a` | `chart-ablation` + `preset-audit` | — |
| `d` | `preset-drive` | `contrast` view |
| `f` | `preset-free` | `flow` view |
| `y` | — | `layers` view |
| `c` | `panel-caption` | `claim-cost`, `convergence` views |
| `r` | `panel-rail` | `terrain` view |
| `s` | `chart-variability` | `spread` view |
| `x` | `control-stop` | `matrix` view |
| `m` | — | `small-multiples`, `spectrum` views |
| `u` | — | `frontier`, `multirun` views |

**Plan:** Resolve in bindings.ts by:
- Moving preset keys to chords (e.g., `shift+w` for watch) or palette-only
- Reassigning view keys to punctuation reserve (`,`, `.`, `/`, `'`), then chords
- The lock test must parse both bindings AND view keys; a key claimed twice anywhere fails

### 2. Pyright Type Errors in `web.py` (7 errors)
**File:** `computronium/experiment/execution/dashboard/web.py`

| Line | Error | Fix |
|------|-------|-----|
| 303 | Lifespan return type mismatch | Add `from contextlib import asynccontextmanager`; return `AsyncIterator[None]` |
| 329 | `asynccontextmanager` overload mismatch | Fix signature to match FastAPI's `StatelessLifespan` |
| 330 | `AsyncIterator` undefined | Add `from collections.abc import AsyncIterator` |
| 758 | `FileResponse` not assignable to `JSONResponse` | Change return type to `Response` or `FileResponse` |
| 774 | `str` has no `filename` | Fix upload handling — `UploadFile` vs `str` |
| 787 | `str` has no `read` | Same — use `UploadFile.read()` |

### 3. Picture Probe Geometry Failures at Small Viewports
**Script:** `scripts/probes/dashboard_picture_probe.py`  
**Failure:** Geometry contract fails at 1440×900 and 1024×768 (CSS/Chrome/Stage pass)  
**Likely cause:** Dockview layout ratios/clamping not responsive enough; side columns too narrow or stage squeezed below 60% width threshold.

### 4. Dashboard Tour Timeout (Slow but Functional)
**Script:** `scripts/capture_dashboard_tour.py`  
**Symptom:** Times out at 180s default; completes in ~50s when run with longer timeout  
**Cause:** Sequential view switching + screenshot + diff for 25 views + 10 panels + 4 presets  
**Optimization:** Parallelize where possible; reduce wait_for_timeout calls; cache baseline images

### 5. Trained Views Show Empty State (Expected)
**Views:** `trained-trajectory`, `trained-basin`, `trained-landscape`, `trained-spectrum`  
**Status:** Demo profile doesn't produce trained dynamics data — views render empty grid  
**Not a bug:** Capture script handles this (doesn't wait for `ready=true` on trained views)

---

## Usability Gaps for "Total Usability"

### 6. First-Run Experience Gaps
| Gap | Description | Priority |
|-----|-------------|----------|
| Empty store onboarding | Void view shows "No run" but no inline "Start a run" CTA button | High |
| Profile picker discoverability | Control panel's New Run section hidden behind `z` / palette | High |
| Quick Run feedback | Toast shows "Started" but no progress indicator for ~30s run | Medium |
| Run completion notification | No visual/audio cue when quick-run finishes | Medium |

### 7. Control Bar & Panel Polish
| Item | Description | Priority |
|------|-------------|----------|
| Ceiling slider max | Currently machine cores; should be configurable or show "unlimited" | Medium |
| CPU trace visibility | Sparkline too small at default height; needs hover-to-expand | Medium |
| Control panel sections | "Cells" section verbs (replicate/preregister/quest) need selected-cell context | High |
| Panel rail density | 10 panel toggles in right rail; consider collapsible groups | Low |

### 8. View Toolbar & Discovery Legend
| Item | Description | Priority |
|------|-------------|----------|
| View search/filter | 25 views in toolbar; no way to filter by name | Medium |
| Axis picker UX | Three rows of buttons; no "reset to default axes" button | Medium |
| Slices view | Shows x×y, x×z, y×z but no indication which slice is active | Low |

### 9. Chart Panel Improvements
| Item | Description | Priority |
|------|-------------|----------|
| Pareto empty state | "No Pareto cells — run with multiple credit arms" hint is good but could link to profile picker | Medium |
| Ablation empty state | "No credit-axis ablation groups" — unclear what action creates them | Medium |
| Variability empty state | "No credit arm with >1 seed" — should explain how to add seeds | Medium |
| Chart export | Pareto has PNG export; ablation/variability lack it | Low |

### 10. Accessibility & Keyboard Navigation
| Item | Description | Priority |
|------|-------------|----------|
| Focus management | Opening panel via palette doesn't always focus first actionable element | High |
| ARIA live regions | Control bar meter updates not announced to screen readers | Medium |
| High contrast mode | No CSS media query for `prefers-contrast: high` | Low |
| Reduced motion | Animations (rail collapse, trace) don't respect `prefers-reduced-motion` | Low |

### 11. Multi-Instance & Persistence Edge Cases
| Item | Description | Priority |
|------|-------------|----------|
| Duplicate stage panel | Second stage panel opens but view selector doesn't sync | Medium |
| Layout persistence | `localStorage` saves layout but not per-instance state (runId, axes) | Medium |
| Floating panel bounds | Can drag floating panel off-screen at small viewports | Low |
| Tab overflow | Many tabs in one group → horizontal scroll but no scroll indicators | Low |

### 12. Server-Side Reliability
| Item | Description | Priority |
|------|-------------|----------|
| WebSocket reconnection | Client reconnects but doesn't re-request missed metrics | Medium |
| Control plane corruption | Handled (reads as "not paused") but no alert to user | Low |
| Campaign queue visibility | Queue shows in control panel but no WebSocket push on enqueue/cancel | Medium |
| Store migration | No migration path for DuckDB schema changes | Low |

### 13. Developer Experience
| Item | Description | Priority |
|------|-------------|----------|
| Dashboard dev server | No hot-reload for TypeScript/CSS changes (requires `npm run build`) | High |
| Probe/Capture scripts | Hardcoded ports, store paths; no config file | Medium |
| Debug API | `__DASHBOARD__.debug` useful but undocumented | Low |

---

## Proposed Phases for TODO75

### Phase A: Fix Blockers (1–2 days)
- [ ] **A1** Fix Pyright errors in `web.py` (7 errors)
- [ ] **A2** Resolve keys lock test — reassign bindings/view keys to eliminate all 18 conflicts
- [ ] **A3** Fix picture probe geometry at 1440×900 and 1024×768

### Phase B: First-Run Polish (2–3 days)
- [ ] **B1** Add "Start a run" CTA button in void view / empty caption
- [ ] **B2** Quick Run: add progress spinner + completion toast
- [ ] **B3** Control panel "Cells" section: disable verbs with inline reason when no cell selected

### Phase C: Usability Polish (3–4 days)
- [ ] **C1** View toolbar: add search/filter input (fuzzy match on view title)
- [ ] **C2** Axis picker: add "Reset axes" button
- [ ] **C3** Chart empty states: add actionable hints (links to profile picker / control panel)
- [ ] **C4** Control bar: ceiling slider "unlimited" option; CPU trace hover-expand
- [ ] **C5** Focus management: palette → panel first focus; Escape closes consistently

### Phase D: Accessibility & Responsive (2–3 days)
- [ ] **D1** ARIA live region for control bar meter
- [ ] **D2** `prefers-reduced-motion` support for rail/trace animations
- [ ] **D3** `prefers-contrast: high` CSS adjustments
- [ ] **D4** Picture probe: fix geometry at 1024×768 (stage ≥60% width, side cols ≥280px)

### Phase E: Multi-Instance & Persistence (2 days)
- [ ] **E1** Per-instance state persistence (runId, axes, view) in LayoutDocument
- [ ] **E2** Floating panel viewport clamping
- [ ] **E3** Tab overflow scroll indicators

### Phase F: Developer Experience (1–2 days)
- [ ] **F1** Dashboard dev server with Vite HMR (proxy to FastAPI)
- [ ] **F2** Config file for probe/capture scripts (ports, store path, viewport)
- [ ] **F3** Document `__DASHBOARD__.debug` API

---

## Acceptance Criteria for "Total Usability"

| Criterion | Measurement |
|-----------|-------------|
| **Zero Pyright errors** | `uv run pyright computronium/experiment/execution/dashboard/web.py` → clean |
| **Keys lock passes** | `uv run pytest tests/property/test_dashboard_keys_lock.py -q` → 100% pass |
| **Picture probe green at 3 viewports** | 1920×1080, 1440×900, 1024×768 all pass CSS/Chrome/Geo/Stage |
| **Tour completes <60s** | `capture_dashboard_tour.py --skip-campaigns` finishes in <60s wall time |
| **First-run success** | New user: open dashboard → click "Start a run" → sees results in <60s without docs |
| **Keyboard-only navigation** | Every verb reachable via palette (`:`); focus never trapped; Escape always works |
| **Screen reader compatible** | ARIA labels on all panels; live region for meter; focus visible |
| **Responsive down to 1024×768** | No horizontal scroll; stage dominant; side panels readable |

---

## Dependencies & Blockers

| Task | Blocks | Blocked By |
|------|--------|------------|
| A1 (Pyright) | — | — |
| A2 (Keys) | B3, C1, lock test | — |
| A3 (Geometry) | D4 | — |
| B1 (Void CTA) | First-run criterion | — |
| B2 (Quick Run progress) | First-run criterion | — |
| C1 (View search) | Usability | A2 (keys freed) |
| F1 (HMR) | Dev velocity | Vite config + FastAPI proxy |

---

## Notes

- **Register C scope:** Keys lock, Pyright repo-wide, full pytest suite — these are hygiene passes, not feature gates. Do not block feature work on them.
- **Tour flakiness:** The tour is the acceptance mechanism. If it passes, the dashboard works. Investigate flakiness only if it blocks merges.
- **Baseline images:** Never commit baseline references. Extract at review time via `git show 0dee1206:docs/readme/assets/...`.
- **Trained views:** Will remain empty until a profile produces trained dynamics data. Not a blocker.

---

## Quick Reference: Commands to Verify Gates

```bash
# Pyright (web.py only)
uv run pyright computronium/experiment/execution/dashboard/web.py

# Keys lock
uv run pytest tests/property/test_dashboard_keys_lock.py -q

# Picture probe (3 viewports)
uv run python scripts/probes/dashboard_picture_probe.py --store experiment.duckdb

# Tour (skip campaigns, reuse store)
timeout 120 uv run python scripts/capture_dashboard_tour.py --skip-campaigns --port 8085

# Hero screenshot (reuse store)
uv run python scripts/capture_dashboard_screenshot.py --reuse-store --port 8084

# Frontend build + typecheck
cd computronium/experiment/execution/dashboard && npm run build && npx tsc --noEmit
```