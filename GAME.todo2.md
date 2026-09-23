# GAME.todo2.md — Remaining Work: Full Integration & Usability (TODO-UX2 "Summit")

**Status:** Draft for implementation
**Scope:** `computronium/ui/dashboard.py`, `computronium/visualization/live_atlas.py`, UI test automation
**Predecessor:** GAME.todo.md (M0–M3 code complete; this plan closes the integration gap)
**Verification posture:** All new locks at L4 (property/sampled numerical) per repo taxonomy.

---

## 0. Executive Summary

The components and the new `computronium/ui/dashboard.py` shell exist and pass all
UX locks (L2/L3/L5/L7/L8/L9/L10), but the dashboard is **not fully usable**:

| Gap | Severity | Why it blocks usability |
|-----|----------|------------------------|
| **D1. Panels render empty** — all data-driven panels are instantiated with default constructors (no data); no adapter from campaign artifacts to panel data | 🔴 Critical | Dashboard shows 18 empty panels |
| **D2. `diversity_stats` crash** — `min(row.bursts)` raises `ValueError` on empty bursts (live_atlas.py:585), kills the whole page | 🔴 Critical | Page 500s on roots with cells lacking burst data |
| **D3. No data refresh path** — `_refresh_cheap` discards the snapshot; `_load_atlas` probes `hasattr(panel, "update_atlas")` which no panel implements | 🔴 Critical | Live updates never reach the panels |
| **D4. ProgressPanel unwired** — instantiated with `gamify_enabled` only; `RecognitionStateStore` created but never fed to the projector/fold path | 🟠 High | Recognition layer invisible |
| **D5. WebSocket events not routed** — telemetry/events consumers append to lists nobody renders | 🟠 High | ActivityFeed/FieldReports show nothing live |
| **D6. No UI test automation** — no NiceGUI screenshot/interaction tests; skips in L5/L9/L10 | 🟠 High | "Usable" is unverified; regressions invisible |
| **D7. `ActivityFeed`/`FieldReports`/`TradeoffsPanel` not in nav** — imported but unused in `_get_panel`; ActivityFeed+FieldReports absent from PANELS list | 🟡 Medium | Components exist but unreachable |
| **D8. Reduced-motion/mode-change re-render** — panels register mode callbacks but drawer never re-renders on mode switch | 🟡 Medium | Explorer⇄Lab toggle doesn't update panel copy |

---

## 1. Phased Delivery Plan

### A — Data Adapters (P0) — "panels see real data"

| ID | Task | Acceptance |
|----|------|------------|
| **A1** | Fix `diversity_stats` crash: guard `min(row.bursts)` with empty-sequence default (`min(b, default=0)` or skip empty); same audit for `front_history_rows`, `cost_stats`, `health_stats`, `maturation_rows`, `graveyard_rows` on sparse/missing artifacts | Dashboard renders on `broad_map_smoke` roots and synthetic empty root without exception (property test: `render_snapshot` never raises over Hypothesis-generated artifact states) |
| **A2** | Create `computronium/ui/data_adapters.py`: pure functions `live_atlas` snapshot/data → panel dataclasses (`MapSpecimen`, `ParetoCell`, `DefectRow`, `HealthTile`, `LineageNode/Edge`, `EpisodeEvent`, `ConstitutionInvariant`, `ProbeBatch`, `StagnationSnapshot`, `GenomeHealthPoint`, `MutationProposal`, `VetoEntry`, `FieldReport`, `FeedEvent`, `ProgressData`) | Each adapter is a pure function, unit-tested; L4 equivalence: adapter output fields match source rows (spot-checked per field) |
| **A3** | Wire adapters into `DashboardApp._get_panel`: build panel instances with fresh data on every render (cheap enough — no UMAP on data-only panels); DiscoveryMap receives `atlas_figure` from `EmbedCache.coords` path | Each panel renders populated state against `artifacts/broad_map` (manual crawl + smoke test) |
| **A4** | Fix `_refresh_cheap`: capture snapshot, pass to `_render_current_panel`; implement `update_atlas` on DiscoveryMap (replace figure container content) instead of `hasattr` probe | Artifact signature change → panels re-render with new data within one poll cycle |
| **A5** | Wire recognition: ProgressPanel receives `ProgressData` built by folding `RecognitionStateStore` events through `projector.fold`; `--rebuild-ui-state` path actually replays `root` event log before first render | Badges/quests/records render from replayed synthetic log (UX-L2 already proves the fold; this proves the wiring) |

### B — Live Streams (P0/P1) — "the dashboard is live"

| ID | Task | Acceptance |
|----|------|------------|
| **B1** | Route `events_consumer` output into ActivityFeed (`FeedEvent`) and FieldReports (`FieldReport`) state, batched ≤1/2s per UX-L5 aria-live config | Events visible in feed panel; toasts fire; pausable |
| **B2** | Route `telemetry_consumer` losses into HealthPanel/active-cell card (loss curve echart from old dashboard) | Loss history renders on HealthPanel |
| **B3** | Add ActivityFeed + FieldReports to PANELS nav list (currently imported but unreachable); also add GlossaryDrawer (`ui/dialog` with searchable term table) | All components in `__all__` reachable via left rail |
| **B4** | Mode-switch re-render: register drawer+main-content re-render on `set_mode` callback; verify panel copy flips registers without reload | Toggle Explorer⇄Lab re-renders current panel + nav labels |

### C — UI/UX Test Automation (P1) — "usable is verified, not asserted"

| ID | Task | Acceptance |
|----|------|------------|
| **C1** | Add `nicegui[testing]` to dev deps; adopt NiceGUI's `@ui_test` / `Screenshot` fixtures (or playwright-based harness) | Test infra importable in tests/ |
| **C2** | `tests/ui/test_dashboard_render.py` — headless render of every panel against a synthetic root fixture (tiny KB sqlite + one defect row + one void row + empty-root variants); assert: no exception, panel content non-empty where data exists, correct empty-state copy where it doesn't | 18 panels × {empty, populated} roots = deterministic pass |
| **C3** | `tests/ui/test_dashboard_interactions.py` — click-through: panel switch, mode toggle re-render, table/map view toggle (DiscoveryMap), pause feed, "What am I looking at?" drawer opens | Every interactive element reachable & functional headless |
| **C4** | Replace skipped UX-L5 axe tests (lines marked SKIPPED) with real playwright+axe scan against the running dashboard on the synthetic fixture; keep manual crawl checklist for cert only | `test_axe_no_critical_or_serious` runs in CI, not skipped |
| **C5** | Unskip UX-L9 `test_panel_renders_all_six_invariants` and UX-L10 component-integration tests using headless render from C2 | 0 skips in UX suite (42→54 passing) |
| **C6** | Screenshot regression baseline (reduced-motion + grayscale per UX-L6): capture all panels, store under `tests/ui/baselines/`, compare on CI | UX-L6 snapshot test implemented (currently missing from tests/) |
| **C7** | UX-L1 (Pareto equivalence) and UX-L4 (readability script `scripts/lint_readability.py`) — referenced in GAME.todo.md §6 but no test files found; create them | All 11 UX locks have real test files; 0 dead references in §6 |

### D — Polish & Docs (P2)

| ID | Task | Acceptance |
|----|------|------------|
| **D1** | `docs/platform/dashboard.md` — usage guide (flags, modes, panels, kill switches), replacing the M3.5 docs-refresh placeholder | Doc exists, linked from README |
| **D2** | Demo/gallery manifest: add one dashboard demo figure if gallery lock requires it (check `comp gallery` manifest rules) | UX-L8 green with any new figure |
| **D3** | Performance budget: assert DiscoveryMap render ≤100ms on 5k cells (time in C2 test), debounce WebSocket→UI ≤1Hz | Budget measured in test output |
| **D4** | `--rebuild-ui-state` end-to-end: CLI flag → replay → sqlite → ProgressPanel round-trip test | Flag demonstrably does something |

---

## 2. Verification Locks (extends GAME.todo.md §6)

| Lock | Property | File |
|------|----------|------|
| UX-L12 (new) | `render_snapshot` total: never raises for any artifact-dir state (Hypothesis) | `tests/property/test_ux_l12_snapshot_totality.py` |
| UX-L13 (new) | Every panel in PANELS renders populated on the synthetic root fixture | `tests/ui/test_dashboard_render.py` |
| UX-L14 (new) | Mode toggle re-renders panel copy in both registers | `tests/ui/test_dashboard_interactions.py` |

Existing UX-L1..L11 unchanged; C4/C5/C7 convert skips and dead references to real tests.

---

## 3. Known Non-Goals (carry over)

- No XP/points/streaks; no new measurement paths; read-only dashboard; Preview Shelf only for Auto-Evolve.
- Server-runtime quirk (NiceGUI exits immediately under non-TTY subprocess here) is an environment artifact — headless UI tests (C1–C3) must run NiceGUI in-process via its test fixtures, not subprocess, which sidesteps it.

---

## 4. Notes for Implementers

- `computronium/ui/dashboard.py` currently passes ruff/pyright but is a shell — the panel map instantiates components with **default/empty data**; do not mistake green gates for integration.
- Components are **data-driven value objects** (frozen dataclasses in); the single integration point is A2's adapter module. Keep adapters pure and testable; no `Path` reading inside components.
- `live_atlas.py` owns artifact schemas (KB, defects, voids, heartbeat). Adapters should reuse its loaders (`_measured_cells`, `read_defects`, `pareto_strip_rows`, …) rather than re-querying.
- NiceGUI version: 3.16.0 (check `nicegui[testing]` API compatibility).
- Cell walltime: dashboard render tests must stay <5 min (they're in the fast tier, not full suite).

---

## 5. Suggested Order

1. **A1** (unblocks everything; trivial fix)
2. **A2 + A3 + A4** (core integration)
3. **C2** (headless render test proves A2/A3)
4. **B1–B4** (live streams + nav completeness)
5. **C1 + C3 + C4 + C5** (automation expands to interactions + unskips)
6. **C6 + C7** (L1/L4/L6 locks)
7. **A5 + D4** (recognition wiring)
8. **D1–D3** (docs + perf)
9. **Commit per phase; targeted tests only**
