# GAME.todo2.md — Remaining Work: Full Integration & Usability (TODO-UX2 "Summit")

**Status:** Draft for implementation
**Scope:** `computronium/ui/dashboard.py`, `computronium/visualization/live_atlas.py`, UI test automation, extensibility layer
**Predecessor:** GAME.todo.md (M0–M3 code complete; this plan closes the integration gap and lays foundation for ambitious evolution)
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

## 1. Architecture & Extensibility (Foundational)

Before fixing the gaps, introduce a small, typed extension layer so the dashboard can grow without rewiring.

| ID | Task | Acceptance |
|----|------|------------|
| **X1** | **Panel Registry** — `computronium/ui/panel_registry.py`: typed registry `PanelSpec(key, label_key, icon, factory, visible_predicate, order)`. `DashboardApp` builds nav and panel map from registry; panels self-register via `@panel_registry.register`. | Adding a panel = one decorator; no manual list edits. |
| **X2** | **Data Adapter Protocol** — `computronium/ui/data_adapters.py` defines `Protocol DataAdapter[PanelData]` with `adapt(snapshot: DashboardSnapshot, root: Path) -> PanelData`. Each panel declares its adapter; `DashboardApp` calls adapter before render. | Pure, testable, swappable; enables stub adapters for UI tests. |
| **X3** | **Reactive State Bus** — lightweight `asyncio`‑based `EventBus` (publish/subscribe) for artifact changes, mode switches, websocket events. Panels subscribe to relevant topics; `_refresh_cheap` becomes `bus.publish(ArtifactChanged(sig))`. | Decouples producers (poll/WS) from consumers (panels); enables future multi‑root, multi‑client. |
| **X4** | **Multi‑Root Support** — CLI `--root` accepts comma list or directory watch; registry holds per‑root `DashboardApp` instances behind a root selector in header. | Users compare campaigns side‑by‑side; no code change for new roots. |
| **X5** | **Campaign Config Hot‑Reload** — watch `campaign.yaml`; on change, re‑parse objectives, update Pareto presets, push `ConfigChanged` event. | Objective selector updates without dashboard restart. |

*These are P0 enablers — implement X1‑X3 before A2/A3 so adapters plug into a stable surface.*

---

## 2. Phased Delivery Plan

### A — Data Adapters & Crash Fixes (P0) — "panels see real data"

| ID | Task | Acceptance |
|----|------|------------|
| **A1** | Fix `diversity_stats` crash: guard `min(row.bursts)` with `default=0` (or skip empty); same audit for `front_history_rows`, `cost_stats`, `health_stats`, `maturation_rows`, `graveyard_rows` on sparse/missing artifacts. | `render_snapshot` never raises on any artifact-dir state (property test `test_ux_l12_snapshot_totality`). |
| **A2** | Implement `DataAdapter` protocol + concrete adapters for every panel dataclass (`MapSpecimen`, `ParetoCell`, `DefectRow`, `HealthTile`, `LineageNode/Edge`, `EpisodeEvent`, `ConstitutionInvariant`, `ProbeBatch`, `StagnationSnapshot`, `GenomeHealthPoint`, `MutationProposal`, `VetoEntry`, `FieldReport`, `FeedEvent`, `ProgressData`). Reuse `live_atlas` loaders (`_measured_cells`, `read_defects`, `pareto_strip_rows`, …). | Each adapter pure, unit‑tested; L4 equivalence: adapter output fields match source rows (spot‑checked). |
| **A3** | Wire adapters via Panel Registry: `DashboardApp._get_panel` fetches adapter, runs `adapt(snapshot, root)`, passes data to panel factory. DiscoveryMap receives `atlas_figure` from `EmbedCache.coords`. | Every panel renders populated state against `artifacts/broad_map` (smoke test). |
| **A4** | Fix `_refresh_cheap`: capture snapshot, publish `ArtifactChanged(sig)` on bus; panels re‑render on subscription. Implement `DiscoveryMap.update_atlas(figure, note, errors)` to swap figure container. | Artifact signature change → panels update within one poll cycle. |
| **A5** | Wire recognition: ProgressPanel receives `ProgressData` built by folding `RecognitionStateStore` events through `projector.fold`; `--rebuild-ui-state` replays root event log before first render. | Badges/quests/records render from replayed synthetic log (UX‑L2 already proves the fold). |

### B — Live Streams & Navigation Completeness (P0/P1) — "the dashboard is live"

| ID | Task | Acceptance |
|----|------|------------|
| **B1** | Route `events_consumer` → `EventBus` topic `ws.events`; ActivityFeed & FieldReports subscribe, batch ≤1/2 s per UX‑L5 aria‑live config. | Events visible in feed panel; toasts fire; pausable. |
| **B2** | Route `telemetry_consumer` → `EventBus` topic `ws.telemetry`; HealthPanel/ActiveCell card subscribe, render loss‑curve echart. | Loss history renders on HealthPanel. |
| **B3** | Register ActivityFeed, FieldReports, TradeoffsPanel in Panel Registry (add to nav). Add GlossaryDrawer (`ui.dialog` with searchable term table) as header action. | All components in `__all__` reachable via left rail + header. |
| **B4** | Mode‑switch re‑render: `set_mode` publishes `ModeChanged`; `DashboardApp` rebuilds drawer labels + re‑renders current panel. | Toggle Explorer⇄Lab flips copy + nav labels without reload. |

### C — UI/UX Test Automation (P1) — "usable is verified, not asserted"

| ID | Task | Acceptance |
|----|------|------------|
| **C1** | Add `nicegui[testing]` to dev deps; adopt NiceGUI `@ui_test` / `Screenshot` fixtures (or Playwright harness). | Test infra importable in `tests/ui/`. |
| **C2** | `tests/ui/test_dashboard_render.py` — headless render of every panel against synthetic root fixture (tiny KB sqlite + one defect row + one void row + empty‑root variants). Assert: no exception, panel content non‑empty where data exists, correct empty‑state copy where it doesn't. | 18 panels × {empty, populated} roots = deterministic pass. |
| **C3** | `tests/ui/test_dashboard_interactions.py` — click‑through: panel switch, mode toggle re‑render, table/map view toggle (DiscoveryMap), pause feed, "What am I looking at?" drawer opens. | Every interactive element reachable & functional headless. |
| **C4** | Replace skipped UX‑L5 axe tests with real Playwright+axe scan against running dashboard on synthetic fixture; keep manual crawl checklist for cert only. | `test_axe_no_critical_or_serious` runs in CI, not skipped. |
| **C5** | Unskip UX‑L9 `test_panel_renders_all_six_invariants` and UX‑L10 component‑integration tests using headless render from C2. | 0 skips in UX suite (42→54 passing). |
| **C6** | Screenshot regression baseline (reduced‑motion + grayscale per UX‑L6): capture all panels, store under `tests/ui/baselines/`, compare on CI. | UX‑L6 snapshot test implemented. |
| **C7** | UX‑L1 (Pareto equivalence) & UX‑L4 (readability script `scripts/lint_readability.py`) — referenced in GAME.todo.md §6 but no test files; create them. | All 11 UX locks have real test files; 0 dead references. |

### D — Observability, Performance & Polish (P1/P2)

| ID | Task | Acceptance |
|----|------|------------|
| **D1** | Structured logging (`structlog`) + OpenTelemetry metrics (render latency, WS message rate, adapter duration). Export `/metrics` endpoint for Prometheus. | Dashboards show p95 render <100 ms, WS lag <50 ms. |
| **D2** | Performance budgets as CI gates: DiscoveryMap ≤100 ms on 5k cells (measured in C2), WebSocket→UI debounce ≤1 Hz, panel virtualization for >1k rows. | Budgets enforced in `tests/perf/test_budgets.py`. |
| **D3** | `--rebuild-ui-state` end‑to‑end test: CLI flag → replay → sqlite → ProgressPanel round‑trip. | Flag demonstrably does something. |
| **D4** | `docs/platform/dashboard.md` — usage guide (flags, modes, panels, kill switches), architecture diagram, extension how‑to. | Doc exists, linked from README. |
| **D5** | Demo/gallery manifest: add one dashboard demo figure if gallery lock requires it (check `comp gallery` manifest rules). | UX‑L8 green with any new figure. |

---

## 3. Verification Locks (extends GAME.todo.md §6)

| Lock | Property | File |
|------|----------|------|
| UX‑L12 | `render_snapshot` total: never raises for any artifact‑dir state (Hypothesis) | `tests/property/test_ux_l12_snapshot_totality.py` |
| UX‑L13 | Every panel in PANELS renders populated on the synthetic root fixture | `tests/ui/test_dashboard_render.py` |
| UX‑L14 | Mode toggle re‑renders panel copy in both registers | `tests/ui/test_dashboard_interactions.py` |
| UX‑L15 (new) | Adapter output fields match source schema (L4 equivalence) | `tests/property/test_ux_l15_adapter_equivalence.py` |
| UX‑L16 (new) | EventBus delivers every WS message to subscribed panels within 2 poll cycles | `tests/property/test_ux_l16_eventbus_delivery.py` |

Existing UX‑L1..L11 unchanged; C4/C5/C7 convert skips and dead references to real tests.

---

## 4. Known Non‑Goals (carry over)

- No XP/points/streaks; no new measurement paths; read‑only dashboard; Preview Shelf only for Auto‑Evolve.
- Server‑runtime quirk (NiceGUI exits immediately under non‑TTY subprocess) is an environment artifact — headless UI tests (C1–C3) must run NiceGUI in‑process via its test fixtures, not subprocess, which sidesteps it.

---

## 5. Notes for Implementers

- `computronium/ui/dashboard.py` currently passes ruff/pyright but is a shell — the panel map instantiates components with **default/empty data**; do not mistake green gates for integration.
- Components are **data‑driven value objects** (frozen dataclasses); the single integration point is the **DataAdapter** protocol. Keep adapters pure and testable; no `Path` reading inside components.
- `live_atlas.py` owns artifact schemas (KB, defects, voids, heartbeat). Adapters should reuse its loaders (`_measured_cells`, `read_defects`, `pareto_strip_rows`, …) rather than re‑querying.
- NiceGUI version: 3.16.0 (check `nicegui[testing]` API compatibility).
- Cell walltime: dashboard render tests must stay <5 min (fast tier, not full suite).

---

## 6. Suggested Order (with enablers first)

1. **X1‑X3** (registry, adapter protocol, event bus) — one PR, ~2 days.
2. **A1** (crash fix) — trivial, unblocks everything.
3. **A2 + A3 + A4** (adapters + wiring) — core integration.
4. **C2** (headless render test proves A2/A3).
5. **B1‑B4** (live streams + nav completeness).
6. **C1 + C3 + C4 + C5** (automation expands to interactions + unskips).
7. **C6 + C7** (L1/L4/L6 locks).
8. **A5 + D3** (recognition wiring + rebuild flag test).
9. **X4‑X5** (multi‑root, config hot‑reload) — incremental, behind flags.
10. **D1‑D2, D4‑D5** (observability, perf budgets, docs).
11. **Commit per phase; targeted tests only.**

---

## 7. Future‑Horizon (Post‑Summit)

| Idea | Why it matters | Sketch |
|------|----------------|--------|
| **Plugin Panels** | Researchers add custom visualisations without touching core. | Panel registry reads entry‑points `computronium.ui.panels`. |
| **Real‑time Collaboration** | Multiple analysts watch same campaign, share annotations. | Yjs / CRDT over WebRTC; EventBus already multicast‑ready. |
| **Campaign Launch UI** | "Start burst" from dashboard, not CLI. | Thin wrapper over `comp continuous`/`daemon` REST API. |
| **Auto‑Evolve Live View** | When Auto‑Evolve lands, its probes/genomes stream here natively. | Same EventBus topics; panels already exist (MutationExplorer, ProbeAnalytics). |
| **Export/Share Snapshots** | Export current dashboard state as portable JSON + static HTML. | `DashboardSnapshot` already serialisable; add `to_html()`. |

These are **not in scope** for TODO‑UX2 but the registry/bus/adapter layer is designed to make them trivial later.

---

*End of GAME.todo2.md — ready for incremental, gated execution.*