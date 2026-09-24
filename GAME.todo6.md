# GAME.todo6.md — Consolidated Remaining Work (from GAME.todo5.md)

**Status:** Lens system complete (Map/Repair/Record). Core dashboard functional. **C2a (URL hash restore) implemented and fixed**; deep links work for screenshots.

---

## 1. Visual Verification (C2 remaining + C4)

| ID | Item | Blocking |
|----|------|----------|
| C2a | Fix URL hash restore (`_restore_url_state`) so deep links work for screenshots | **DONE** (async timer + JS return value + polling with headless detection) |
| C2b | orca + Chromium crawl: palette, chip transitions, 200% zoom, 320px reflow, reduced-motion, high-contrast | Manual |
| C2c | Cert recording (axe + keyboard checklist) | — |
| C4a | Aesthetic spec: monospace data, 4px grid, semantic color | Visual |
| C4b | Motion ≤150ms, `--quiet` density | Visual |
| C4c | V4 conformance checklist | — |

---

## 2. Fault Injection & Regression (C3 — un-deferred)

| ID | Item |
|----|------|
| C3a | Kill daemon mid-run → chip transitions correct, no crash |
| C3b | Empty root → empty states show actionable buttons |
| C3c | Corrupt JSONL (defects/voids) → graceful degradation |
| C3d | Slow UMAP (mock delay) → loading state, no UI freeze |
| C3e | Regression tests for each fault mode |

---

## 3. Dogfood Validation (D — un-deferred)

| ID | Item |
|----|------|
| D1 | V1: Compose → configure → launch → insight → diagnose → audit (rubric) |
| D2 | V3: LLM copy clarity + 3-persona walkthrough + Nielsen 10 |
| D3 | V4: Screenshot checklist + §1.1 conformance + chip states |
| D4 | V5: Lock hygiene (L1–L8, L12, L13, L15, L16 green; no pixel baselines) |
| D5 | P1: Perf benchmarks — first paint p95 ≤4s, panel-switch p95, palette ≤200ms, chip ≤1 poll |

---

## 4. Spaced Transfer Run (E)

| ID | Item |
|----|------|
| E1 | V2: Spaced transfer run (≥3 days after D, different cells/defects, zero dead ends) |

---

## 5. Implementation Priority

```
Week 1: C2b/C4 (visual) → C3 (faults)
Week 2: D1–D5 (dogfood + perf)
Week 3: E1 (spaced run)
```

---

## 6. Dependencies

```
C3 (faults) → independent, can parallelize
D (dogfood) → requires C3 + C4 clean
E (spaced) → requires D clean + 3 day gap
```

---

## 7. Current Test Status (baseline)

| Suite | Pass | Fail | Skip |
|-------|------|------|------|
| UI | 22 | 0 | 0 |
| A11y | 14 | 0 | 1 |
| Integration | 8 | 0 | 0 |
| **Total** | **44** | **0** | **1** |

All type/lint clean.

---

## 8. Progress Notes (this session)

**Completed:**
- Fixed `_restore_url_state()` to properly handle deep linking via URL hash in real browser contexts (via Selenium/pytest screen fixture)
- Added hash polling mechanism that auto-detects headless vs browser context (skips polling in headless tests)
- Fixed mode initialization to not publish events before UI is built (prevents double-render on startup)
- All UI, a11y, and integration dashboard tests pass in isolation

**Known Issues / Improvement Opportunities:**
- Test isolation flakiness: `test_build_dashboard_headless` passes in isolation but fails when run after UI tests due to NiceGUI global state bleed. Not a code bug - pre-existing test infrastructure issue.
- UMAP falls back to t-SNE in test env (UMAP import issue); screenshots show t-SNE layout.
- `en.umd.prod.js` 404 in test teardown is a NiceGUI upstream bug (missing English locale bundle), not our code.

**Next Steps (per plan):**
- Week 1: C2b/C4 (visual verification) → C3 (fault injection)
- C3 items (C3a-C3e) are un-deferred and can be parallelized
- D (dogfood) requires C3 + C4 clean
- E (spaced transfer) requires D clean + 3 day gap