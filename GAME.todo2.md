# GAME.todo2.md — Remaining Work: Full Integration & Usability (TODO-UX2 "Summit")

**Status:** In progress — Phase A + X1–X3 + Phase B code complete (2026-09-23); Phase C: C2/C3/C5/C7 done, C1 dep-only, C4/C6 remaining; D/X4–X5 remaining.
**Scope:** `computronium/ui/dashboard.py`, `computronium/visualization/live_atlas.py`, UI test automation, extensibility layer
**Predecessor:** GAME.todo.md (M0–M3 code complete; this plan closes the integration gap and lays foundation for ambitious evolution)
**Verification posture:** All new locks at L4 (property/sampled numerical) per repo taxonomy.

## Progress Log

**Done (commit: C5/C7 UX locks + constitution/lineage wiring + adapter hygiene):**
- **C7 ✅** UX‑L1 `tests/property/test_ux_l1_pareto_equivalence.py` (6 presets: rendered membership == `pareto_top(df, objectives)`); UX‑L4 `scripts/lint_readability.py` (self‑contained FK grade, no `textstat` — that package ships a top‑level `tests/` that shadows the repo and breaks collection) + `tests/lint/test_ux_l4_readability.py` (6 tests). All 11 UX locks now have real test files.
- **C5 ✅** UX‑L9 `TestConstitutionPanelIntegration` (3 tests) + UX‑L10 `TestLineageViewerIntegration` (4 tests) unskipped and green.
- **ConstitutionHealthPanel**: added `ConstitutionHealthData`/`ConstitutionMetrics` dataclasses + `compute_constitution_metrics` (matches reference stability path byte‑identically) + `update_data`. Fixed stability API misuse: `StabilityGuard(threshold=...)`/`LyapunovEstimator(num_steps=...)` take kwargs, not Config objects.
- **UX‑L10 LineageViewer**: adapter now builds nodes/edges from `snapshot.event_history` via `_build_lineage_from_events` (idempotent replay). `DashboardSnapshot` gained `event_history: list[dict]` + `objectives: tuple[ObjectiveSpec, ...]`; `render_snapshot(..., event_history=)`; `DashboardApp._get_panel_data` passes `list(self.event_history)`.
- **UX‑L1 Tradeoffs**: `adapt_tradeoffs_panel` now reads `snapshot.pareto_rows` (respects preset‑switched objectives) + `snapshot.objectives` instead of hardcoding `DEFAULT_OBJECTIVES`. Panel `update_data` converts adapter `ParetoCell` → component `ParetoCell` (metrics dict).
- **Panel `update_data` gaps closed**: Tradeoffs (cells), RepairBench (rows), Constitution (invariants), ActivityFeed/FieldReports (from `snapshot.event_history`), EpisodeTimeline (maps adapter `EpisodeEvent` → component `episode` field), Stagnation (explicit no‑op hook). Previously these silently dropped adapter data via `BasePanel.update_data` no‑op.
- **Adapter hygiene**: module‑level `_coerce_float`/`_coerce_str` (removed 4 duplicate `_row_float` defs); `ProgressData` reuses recognition `Badge/Quest/Record` (deleted duplicate dataclasses); `adapt_episode_timeline`/`adapt_activity_feed`/`adapt_field_reports` consume `snapshot.event_history` (were empty/`for ev in []`).
- **C1 ⚠️ dep added**: `nicegui[testing]>=3.16.0` in dev+ui extras — uv warns NiceGUI 3.16.0 has **no `testing` extra**; C2/C3 don't need it (in‑process headless). Verify before relying on `@ui_test`.
- **Verification (this commit):** dev‑env smoke OK; `ruff format`+`check` clean on touched files; `pyright` 0 errors on new modules; targeted suite **77 passed, 4 skipped** (4 skips = UX‑L5 axe CLI + keyboard crawl) in ~37s.

**Done (commit: Phase B + C locks + integration fixes):**
- **B1 ✅** `DashboardApp._route_ws_events` — `/ws/events` payloads flow bus → classified `DashboardEvent` → `ActivityFeed.add_event` + `FieldReports.add_report` + `_toast_for_alert`. WS consumers slimmed to raw publish (dedupe: routing now lives in one handler).
- **B2 ✅** Telemetry → `loss_history` (capped 60) → `HealthPanel.update_data(loss_history=...)`; new `_render_loss_curve` echart on HealthPanel. Paint throttled ≤1/2s via `_last_ws_paint` (`_WS_PAINT_INTERVAL_S`).
- **B3 ✅** Glossary header action (`_open_glossary`): searchable dialog over `GlossaryService.all_entries()`, both registers shown. `loss_curve` glossary key added.
- **B4 ✅** `set_mode` publishes `ModeChanged` on the bus (lazy import avoids cycle); `DashboardApp._on_mode_changed` rebuilds drawer + re-renders. Coverage: `tests/ui/test_dashboard_interactions.py::test_mode_toggle_publishes_and_rerenders`.
- **C2 ✅ (partial)** `tests/ui/` created: `test_dashboard_render.py` (UX-L13: all 20 panels render populated AND on empty root; registry totality; explorer nav hiding; panel switch). Found & fixed real integration bugs (see Fixes below).
- **C3 ✅ (partial)** `tests/ui/test_dashboard_interactions.py`: mode toggle publish/re-render, WS fan-out to feed+reports, telemetry throttle, bus→dashboard delivery, glossary keys.
- **UX-L12 ✅** `tests/property/test_ux_l12_snapshot_totality.py` (Hypothesis, 25 examples): malformed defect/void lines, missing files, malformed heartbeat → `render_snapshot` never raises.
- **UX-L15 ✅** `tests/property/test_ux_l15_adapter_equivalence.py`: repair-bench↔funnel_rows, health tiles↔health dict, discovery-map specimens↔cells, tradeoffs accuracies⊆pareto front.
- **UX-L16 ✅** `tests/property/test_ux_l16_eventbus_delivery.py`: sync/async delivery, type isolation, unsubscribe, handler isolation.
- **Progress adapter smell fixed (X2 note #5):** `_get_panel_data` now wraps `adapt_progress_panel` with `functools.partial(recognition_store=...)` — the 3-arg `FunctionAdapter.adapt` call (a latent TypeError) is gone.
- **Fixes surfaced by the new tests (proof C-suite earns its keep):**
  - `Register(ui_mode)` — instantiating `typing.Literal` raised TypeError whenever `--ui-mode lab|explorer` (pre-existing); replaced with `set_mode(ui_mode)`.
  - `spec.adapter.adapt(snapshot, root, store)` 3-arg call → partial (above).
  - `CampaignCardGallery` registered as bare class (returns class, not instance) and not a `BasePanel` — registry now types factories as `PanelLike` Protocol (render-only); `PanelRegistry.register` is upsert; root-dependent campaigns factory re-registered in `DashboardApp.__init__`.
  - `adapt_discovery_map` crashed: `pareto_top` output has no `key` column (now synthesized 3-part key) and `cells_df` lacks `x`/`y` (`_with_layout` adds deterministic blake2b-hash coordinates — pure stand-in for UMAP).
  - `_generate_regions` degenerate bounds (all cells same primitives) yielded zero regions — epsilon padding added.
  - Missing ICONS keys (`circle`, `award`, `flag`, `history`, `trending_up`) crashed FieldReports/LineageViewer/ProgressPanel renders — added to `design_tokens.ICONS`.
  - `read_defects` / `load_voids` / `void_summary_rows` now skip malformed JSONL lines (UX-L12 totality).
  - `EventBus` handler types generalized (PEP 695 generic `EventHandler[E]`, loose internal storage, cast at dispatch) — fixes contravariance errors for subscribed panel-specific handlers.
  - `BasePanel.update_data(data=None, **kwargs)` no-op hook + all 5 data panels accept their typed data positionally; `DashboardApp._push_data` duck-typed push replaces hasattr probes.

**Done (commit: Phase A + X1–X3):**
- **X1** ✅ `computronium/ui/panel_registry.py` — `PanelSpec`/`PanelRegistry` with `register`, `get`, `all_specs`, `visible_specs(context)`, `keys`; global `panel_registry` instance. Dashboard registers all 20 panels at module import (`_register_panels()` in dashboard.py). Note: `register_panel` class-decorator exists but DashboardApp uses `panel_registry.register(...)` directly (factory is an arg, not the decorated class).
- **X2** ✅ `computronium/ui/data_adapters.py` — `DataAdapter[PanelDataT]` Protocol, `FunctionAdapter`, `make_adapter(fn)`. PEP 695 generics.
- **X3** ✅ `computronium/ui/event_bus.py` — frozen dataclass events (`ArtifactChanged`, `ModeChanged`, `ConfigChanged`, `WebSocketEvent`, …); sync + async pub/sub with `contextlib.suppress` isolation; global `event_bus`.
- **A1** ✅ `diversity_stats` guards empty `row.bursts` (hasattr + list guard); `front_history_rows` cumulative filter guarded via walrus. Sparse-artifact audit done — other loaders (health_stats, graveyard_rows, cost_stats, maturation_rows) already empty-safe.
- **A2** ✅ `computronium/ui/adapters.py` — concrete adapters for all 20 panels; DiscoveryMap adapter reuses `create_discovery_map_from_atlas` + `pareto_top` (Pareto flags set properly); HealthPanel tiles derived from snapshot.health; stagnation uses snapshot.diversity/alerts. Lab-instrumentation panels (lineage/episodes/mutations/veto_log/genome/probe) return typed empty data — their sources aren't computed in `render_snapshot` yet (see Remaining Work notes).
- **A3** ✅ DashboardApp rewritten on registry: `_get_panel` from spec factory; `_get_panel_data` runs adapter with cached results; nav built from `panel_registry.visible_specs`; ActivityFeed + FieldReports now registered and in nav (D7 partially done). Glossary keys `activity_feed`/`field_reports` added.
- **A4** ✅ `_refresh_cheap` clears cached panel data + pushes via `update_data`; publishes `ArtifactChanged` on the bus; `_load_atlas` calls `panel.update_data(atlas_figure=...)` (DiscoveryMap has no `update_atlas` — `update_data` is the real API).
- **A5** ✅ `adapt_progress_panel` accepts optional `recognition_store`; `_get_panel_data` passes `self.recognition_store` for the progress panel; store rebuilds via `projector.fold`. NOTE: `FunctionAdapter.adapt` signature is 2-arg — the 3-arg call works only because the adapter dict stores the raw function path; if this breaks, wrap progress adapter specially or add a store-aware adapter class.

**Verification:** ruff clean on all touched files; 25 targeted tests pass (dashboard smoke ×9, UX-L2 ×7, UX-L3 ×6, UX-L7 ×4).

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

### Remaining Work Notes (for next session)

1. **X4/X5** (multi-root, config hot-reload) untouched — the EventBus topics (`ConfigChanged`) already exist, wire the file watcher.
2. **B1–B2/B4**: done (see Progress Log) — WS routed via bus, mode toggle publishes `ModeChanged`, panels push via `update_data`.
3. **Lab panels thin**: mutations/veto_log/genome/probe/stagnation adapters return typed empty data — their sources (Auto-Evolve event logs) aren't in `DashboardSnapshot` yet. Lineage/episodes/activity_feed/field_reports now consume `snapshot.event_history`. Prefer extending `render_snapshot` over impure per-adapter loaders.
4. **Known smell**: `adapt_progress_panel` store arg still special-cased via `functools.partial` in `_get_panel_data` — formalize with `AdapterContext` (exists in `data_adapters.py`, unused).
5. **C4 remaining**: UX-L5 axe tests still skip (need `npm i -g @axe-core/cli` or Playwright+axe against a running dashboard on the synthetic fixture). Keyboard-crawl test is intentionally manual.
6. **C6 remaining**: screenshot regression baseline (`tests/ui/baselines/`, reduced-motion + grayscale per UX-L6).
7. **C1 caveat**: `nicegui[testing]` extra does not exist on NiceGUI 3.16.0 (uv warning) — either pin a version that ships it or drop the extra; current C2/C3 tests don't need it (in-process headless render).
8. `PANELS`/`LAB_ONLY_PANELS`/`_panel_label` legacy lists in dashboard.py are dead code superseded by the registry — remove in hygiene pass.
9. **Glossary readability debt**: `scripts/lint_readability.py` reports 147 Explorer strings > FK grade 8 (mostly short technical labels where the FK heuristic over-rates; wire an allowlist or accept the lint as informational until copy is reworked).
10. **Do not `uv add textstat`** (or any package shipping top-level `tests/`): it shadows the repo `tests/` namespace and breaks all test collection. FK grade is implemented inline in `scripts/lint_readability.py`.
11. **Dashboard `PLW0717`** (try-clause statement count) in `_load_atlas`/`_telemetry_consumer` pre-exists on HEAD — Register C hygiene, not this round.

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
| **C1** | Add `nicegui[testing]` to dev deps; adopt NiceGUI `@ui_test` / `Screenshot` fixtures (or Playwright harness). | ⚠️ dep added; **extra missing on 3.16.0** — C2/C3 don't need it. |
| **C2** | `tests/ui/test_dashboard_render.py` — headless render of every panel against synthetic root fixture (tiny KB sqlite + one defect row + one void row + empty‑root variants). Assert: no exception, panel content non‑empty where data exists, correct empty‑state copy where it doesn't. | 18 panels × {empty, populated} roots = deterministic pass. |
| **C3** | `tests/ui/test_dashboard_interactions.py` — click‑through: panel switch, mode toggle re‑render, table/map view toggle (DiscoveryMap), pause feed, "What am I looking at?" drawer opens. | Every interactive element reachable & functional headless. |
| **C4** | Replace skipped UX‑L5 axe tests with real Playwright+axe scan against running dashboard on synthetic fixture; keep manual crawl checklist for cert only. | `test_axe_no_critical_or_serious` runs in CI, not skipped. **Remaining.** |
| **C5** | Unskip UX‑L9 `test_panel_renders_all_six_invariants` and UX‑L10 component‑integration tests using headless render from C2. | ✅ 0 skips in UX-L9/L10 (was 7 skipped). |
| **C6** | Screenshot regression baseline (reduced‑motion + grayscale per UX‑L6): capture all panels, store under `tests/ui/baselines/`, compare on CI. | UX‑L6 snapshot test implemented. **Remaining.** |
| **C7** | UX‑L1 (Pareto equivalence) & UX‑L4 (readability script `scripts/lint_readability.py`) — referenced in GAME.todo.md §6 but no test files; create them. | ✅ All 11 UX locks have real test files; 0 dead references. |

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
| UX‑L1 | Pareto membership rendered == `pareto_top(df, objectives)` for all presets | `tests/property/test_ux_l1_pareto_equivalence.py` |
| UX‑L4 | Explorer strings ≤ FK grade 8 (CI lint) | `scripts/lint_readability.py` + `tests/lint/test_ux_l4_readability.py` |
| UX‑L12 | `render_snapshot` total: never raises for any artifact‑dir state (Hypothesis) | `tests/property/test_ux_l12_snapshot_totality.py` |
| UX‑L13 | Every panel in PANELS renders populated on the synthetic root fixture | `tests/ui/test_dashboard_render.py` |
| UX‑L14 | Mode toggle re‑renders panel copy in both registers | `tests/ui/test_dashboard_interactions.py` |
| UX‑L15 (new) | Adapter output fields match source schema (L4 equivalence) | `tests/property/test_ux_l15_adapter_equivalence.py` |
| UX‑L16 (new) | EventBus delivers every WS message to subscribed panels within 2 poll cycles | `tests/property/test_ux_l16_eventbus_delivery.py` |

Existing UX‑L1..L16 all have real test files. Remaining C4 (axe) + C6 (screenshots) convert the last UX‑L5/L6 skips.

---

## 4. Known Non‑Goals (carry over)

- No XP/points/streaks; no new measurement paths; read‑only dashboard; Preview Shelf only for Auto‑Evolve.
- Server‑runtime quirk (NiceGUI exits immediately under non‑TTY subprocess) is an environment artifact — headless UI tests (C1–C3) must run NiceGUI in‑process via its test fixtures, not subprocess, which sidesteps it.

---

## 5. Notes for Implementers

- Dashboard panels are **data‑driven value objects**; the integration point is the **DataAdapter** protocol → `panel.update_data(data)`. Panels without `update_data` silently drop adapter payloads (`BasePanel.update_data` is a no‑op) — check before adding a panel.
- Components are **data‑driven value objects** (frozen dataclasses); keep adapters pure and testable; no `Path` reading inside components.
- `live_atlas.py` owns artifact schemas (KB, defects, voids, heartbeat, event_history, objectives). Adapters should consume `DashboardSnapshot` fields rather than re‑querying (`adapt_tradeoffs_panel` was fixed for this — do not regress).
- Stability API: `StabilityGuard`/`LyapunovEstimator` take keyword fields directly (`threshold=`, `num_steps=`), **not** `GuardConfig`/`LyapunovConfig` objects — the Config-object form type-checks as `threshold: float = GuardConfig(...)` and silently misconfigures.
- Never `uv add` a package that ships a top‑level `tests/` package (e.g. `textstat`) — it shadows the repo `tests/` and breaks all collection.
- NiceGUI version: 3.16.0 (no `testing` extra despite the pin).
- Cell walltime: dashboard render tests must stay <5 min (fast tier, not full suite).

---

## 6. Suggested Order (with enablers first)

1. **X1‑X3** (registry, adapter protocol, event bus) — one PR, ~2 days.
2. **A1** (crash fix) — trivial, unblocks everything.
3. **A2 + A3 + A4** (adapters + wiring) — core integration.
4. **C2** (headless render test proves A2/A3).
5. **B1‑B4** (live streams + nav completeness).
6. **C1 + C3 + C4 + C5** (automation expands to interactions + unskips). — C3/C5 done; C1 dep-only; **C4 remaining**
7. **C6 + C7** (L1/L4/L6 locks). — **C7 done**; **C6 remaining**
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