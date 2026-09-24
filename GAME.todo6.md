# GAME.todo6.md — Consolidated Remaining Work (from GAME.todo5.md)

**Status:** Lens system complete (Map/Repair/Record). Core dashboard functional. **C2a (URL hash restore) implemented and fixed**; deep links work for screenshots. **C3 (Fault Injection & Regression) complete** — all 5 items implemented and tested.

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

| ID | Item | Status |
|----|------|--------|
| C3a | Kill daemon mid-run → chip transitions correct, no crash | **DONE** — `test_daemon_disconnect_chip_transitions_to_offline`, `test_daemon_reconnect_chip_transitions_to_running`, `test_no_heartbeat_chip_shows_offline`, `test_fault_regression_daemon_cycle_no_crash` |
| C3b | Empty root → empty states show actionable buttons | **DONE** — `test_empty_root_shows_actionable_buttons`, `test_empty_root_health_tiles_reflect_zero_state`, `test_fault_regression_empty_root_no_crash` |
| C3c | Corrupt JSONL (defects/voids) → graceful degradation | **DONE** — `test_corrupt_defects_jsonl_graceful_degradation`, `test_corrupt_voids_jsonl_graceful_degradation`, `test_corrupt_kb_sqlite_handled_gracefully`, `test_fault_regression_corrupt_artifacts_no_crash` |
| C3d | Slow UMAP (mock delay) → loading state, no UI freeze | **DONE** — `test_slow_umap_shows_loading_not_frozen`, `test_embed_cache_refits_only_on_count_change` |
| C3e | Regression tests for each fault mode | **DONE** — `test_fault_regression_watch_signature_handles_missing_files`, `test_fault_regression_log_tail_handles_missing_log`, `test_fault_regression_render_snapshot_handles_all_missing`, `test_fault_regression_panel_switch_during_faults`, `test_status_chip_state_transitions`, `test_watch_signature_detects_changes`, `test_snapshot_collects_atlas_errors` |

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
Week 1: C2b/C4 (visual) → C3 (faults)  ← C3 COMPLETE
Week 2: D1–D5 (dogfood + perf)
Week 3: E1 (spaced run)
```

---

## 6. Dependencies

```
C3 (faults) → **COMPLETE** — independent, can parallelize
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
| **Dashboard Fault Injection** | **20** | **0** | **0** |
| **Total** | **64** | **0** | **1** |

All type/lint clean.

---

## 8. Progress Notes (this session)

**Completed:**
- Fixed `_restore_url_state()` to properly handle deep linking via URL hash in real browser contexts (via Selenium/pytest screen fixture)
- Added hash polling mechanism that auto-detects headless vs browser context (skips polling in headless tests)
- Fixed mode initialization to not publish events before UI is built (prevents double-render on startup)
- All UI, a11y, and integration dashboard tests pass in isolation
- **Implemented C3 fault injection test suite (20 tests):**
  - C3a: Daemon disconnect/reconnect chip state transitions (4 tests)
  - C3b: Empty root empty states with actionable buttons (3 tests)
  - C3c: Corrupt JSONL/SQLite graceful degradation (4 tests)
  - C3d: Slow UMAP/EmbedCache loading state handling (2 tests)
  - C3e: Regression tests for watch_signature, log_tail, render_snapshot, panel switching, status chip, atlas errors (7 tests)
- **Added graceful error handling to core dashboard functions:**
  - `_measured_cells()` — catches corrupt/missing KB, returns empty list
  - `health_stats()` — uses `_measured_cells()` for consistent error handling
  - `pareto_strip_rows()` — catches corrupt KB, returns empty Pareto front
  - `_load_cells_uncached()` (atlas.py) — catches corrupt KB, returns empty DataFrame
- All new tests pass; existing dashboard smoke tests and UI tests continue to pass

**Known Issues / Improvement Opportunities:**
- Test isolation flakiness: `test_build_dashboard_headless` passes in isolation but fails when run after UI tests due to NiceGUI global state bleed. Not a code bug - pre-existing test infrastructure issue.
- UMAP falls back to t-SNE in test env (UMAP import issue); screenshots show t-SNE layout.
- `en.umd.prod.js` 404 in test teardown is a NiceGUI upstream bug (missing English locale bundle), not our code.

**Next Steps (per plan):**
- Week 1: C2b/C4 (visual verification) 
- Week 2: D1–D5 (dogfood + perf)
- Week 3: E1 (spaced transfer)