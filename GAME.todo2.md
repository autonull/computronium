# GAME.todo2.md — Remaining Work: Full Integration & Usability (TODO-UX2 "Summit")

**Status:** In progress — Phase A + **X1–X5** + Phase B code complete; Phase C: **C1/C2/C3/C4/C5/C7 done (C4 axe 0 critical/serious in both registers)**, **C6 green** (static marker-redundancy + behavioral grayscale 6.10 > 5.0 floor); **D1–D4 code complete (D2 budgets still green)**, D5 gallery-compat green + figure-lock verdict recorded (pre-existing environmental drift, deliberately not re-pinned). **2026-09-23: front-history objective-column log spam fixed** (`walltime`→`walltime_s` + `param_count` from `param_budget`; 0 spam on default/3-obj/full-cost presets).
**Scope:** `computronium/ui/dashboard.py`, `computronium/visualization/live_atlas.py`, UI test automation, extensibility layer
**Predecessor:** GAME.todo.md (M0–M3 code complete; this plan closes the integration gap and lays foundation for ambitious evolution)
**Verification posture:** All new locks at L4 (property/sampled numerical) per repo taxonomy.
**Test philosophy (user directive 2026-09-23):** "Don't make overly brittle tests. We need agile flexible development." → no pixel-baseline screenshot locks; behavioral/property checks with generous tolerances only.

## Progress Log

**Done (2026-09-23: front-history objective alignment):**
- **`front_history_rows` objective-column spam ✅ FIXED** (`live_atlas.py`): the `pareto_top` df used column `"walltime"` but `DEFAULT_OBJECTIVES` wants `"walltime_s"` → `pareto_top` logged `"Objective column walltime_s not in DataFrame; skipping"` and returned the unfiltered df on every `render_snapshot` (5 cutpoints/render). Renamed to `"walltime_s"` + added `"param_count"` from `_CellRow.param_budget` (covers the accuracy+walltime+params preset; flops/memory_mb were already present so full-cost is clean too). Verified: 0 spam on default / 3-obj / full-cost presets, `test_dashboard_smoke -k "landscape or snapshot_render"` 2 passed. Note: `_CellRow` still lacks `settle_horizon`/`stability_plasticity_ratio`/`credit_efficiency` fields — presets using those still early-return unfiltered (same pre-existing `pareto_top` behavior, no crash).
- **Verification (this session):** dev-env smoke OK; `ruff format` clean; `ruff check` 2 findings + `pyright` 4 errors on `live_atlas.py` all verified identical on HEAD via `git stash` (Register C hygiene, not this round); targeted smoke 2 passed (21.7 s); no full-suite run per energy directive.

**Done (checkpoint: C4 green + C6 green + D5 verdict):**
- **C4 ✅ axe 0 critical/serious in BOTH registers** (explorer + lab), teardown clean:
  (a) `aria-label` on 3 header icon buttons (glossary/tour/quiz) + DiscoveryMap view switch (dynamic `tr("view")`); `language="en"` on `cli/dashboard.py`, `autoscientist/dashboard.py`, a11y + grayscale test pages.
  (b) **Page-load timeout 4 s → 30 s** in both Screen tests — NiceGUI's session driver default; dashboard first render (glossary + atlas + UMAP) exceeds 4 s. Flaky `Timed out receiving message from renderer` retries are gone.
  (c) **Contrast fixes:** `PRIMARY = "#1a5fa8"` + `SECONDARY = "#1c7d74"` in `design_tokens.py`, applied via `ui.colors()` in `DashboardApp.build()` (NiceGUI defaults #5898d4 3.06:1 / teal 2.99:1 both fail); `text-grey` → `text-grey-8` (#616161, 6.19:1) on the 3 flagged discovery_map captions + atlas_pending empty state; `.q-header .ellipsis` white CSS + `mode_toggle_select().style("color: white;")` for dark-text-on-primary selects.
  (d) Teardown noise allowlisted via `screen.allowed_js_errors`: `lang/en.umd.prod.js` 404 (English is built-in — NiceGUI ships no bundle for it).
  (e) **Drive-by fix:** `ui/__init__.py` `__all__` was missing 6 entries (`BasePanel`, `GlossaryAware`, `GlossaryService`, `Register`, `get_glossary_service`, `get_mode`) while the imports existed — restored in RUF022 sort order. **Watch out:** `ruff check` on `ui/__init__.py` is the canary; bare `pyright` reports phantom missing-imports (wrong interpreter) — always `uv run pyright`.
  (f) **Glossary `"atlas"` key added** (`Map`/`Atlas`) — `render_header("atlas")` warned on every render.
- **C6 ✅ behavioral grayscale green:** mean-abs-diff **6.10 > 5.0** floor (populated vs empty); Plotly `Resize must be passed a displayed plot div` teardown noise allowlisted (hidden containers at teardown — external).
- **D5 verdict:** gallery-compat **10/10 green** (`--root` comma-split intact, dashboard imports with gallery); `test_figure_lock` RED on `compose_6axis` — **pre-existing environmental drift, deliberately NOT re-pinned:** demo file + manifest unchanged since emit record (`19c84ebd`), UI changes cannot affect MNIST training numerics, and the dirty `run_records/*.json` predates this session. Re-pinning training figures masks real drift — needs a maintainer decision + deliberate demo re-run.
- **`screenshots/` gitignored** (Screen-fixture output; was untracked noise).
- **Verification (this checkpoint):** `ruff format`+`check` clean; `uv run pyright` **0 errors**; UI tier **21 passed**; a11y file **13 passed + 1 skipped (manual crawl) + axe green**; UX property (L1/L4/L12/L15/L16 + L6 markers) **23 passed**; perf budgets **3 passed** (D2 still green). Full property suite: 4 failed, all verified unrelated + pre-existing (axis certs, geometry wiring lock, memory-budget thermo, positive-control ceiling — none touch UI paths).

**Done (checkpoint: D2 close-out + X4/X5 + D1/D3/D4 + C1/C4-harness):**
- **D2 ✅ all five hotspots closed:**
  (a) **mtime-keyed KB cache** `kb_load_cached(path, loader, clone, key_extra=)` in `atlas.py` — key `(path, mtime_ns, size, key_extra)`, ≤16 entries (clear-on-full), callers get clones (`df.copy(deep=False)` / `list`). **Watch out:** key MUST be namespaced per loader (`("cells", task)` vs `("measured", task)`) or the two loaders poison each other's types (hit this: `TypeError: list.copy()` — fixed). Wrapped `load_cells` + `broad_map._load_measured_cells`.
  (b) **`_with_layout` vectorized** — column `astype(str)` concat (no iterrows) + **single blake2b digest split into x/y** (was salted pair = 2 hashes/label). Coordinate *values* changed (still deterministic; no lock on exact coords).
  (c) **`create_discovery_map_from_atlas` columnar** — `df.to_dict("records")` was 107 ms @5k (pandas-3 arrow `__iter__`); replaced with per-column `.tolist()` + index loop, new `_outcome_from_values`, `pareto_keys` param (adapter no longer rebuilds 5k specimens), `_generate_regions` now numpy masks + Counter. **Measured: adapter 319→48.4 ms warm @5k** (was 1021 ms pre-D2).
  (d) **One `render_snapshot` per refresh cycle** — `DashboardApp._snapshot_for(with_atlas=)` + `_snapshot_has_atlas` upgrade flag; `_clear_panel_data()` invalidates both panel data and snapshot.
  (e) **Dead `render_snapshot` call deleted** from `_refresh_cheap` (result was discarded); `_refresh_cheap` now clears the whole cycle cache up front.
  **Budgets (`tests/perf/test_budgets.py`, invoke BY PATH — not in `testpaths`):** DiscoveryMap adapter warm median **48.4 ms** ≤100 ms @5k (bulk seed 5k in 0.10 s via `kb._tx().executemany`); `render_snapshot` warm median **116 ms** ≤3 s (was 2235 ms); `_WS_PAINT_INTERVAL_S=2.0` ≥1.0; `MAX_RENDERED_ROWS` constant check. **All green.**
- **Row virtualization ✅** `MAX_RENDERED_ROWS = 1000` (`design_tokens.py`); `DiscoveryMap._table_rows()` cap + `showing_first` caption; `RepairBench.render` cap + caption; glossary key `showing_first` (explorer "Showing first rows" / lab "Rendered row cap"). Tests: `tests/ui/test_row_virtualization.py` (spies on `ui.table` / `_render_defect_row`) — green.
- **log-path bug ✅** `DashboardApp.__init__` now `self.log_path = resolve_log_path(root, log_path)` (+ `_explicit_log_path` re-resolved in `switch_root`).
- **AdapterContext formalized ✅** `data_adapters.py`: `AdapterContext(root, snapshot, recognition_store=None)`; `DataAdapter.adapt(ctx)`; `FunctionAdapter` unpacks `(ctx.snapshot, ctx.root)`; new `ContextAdapter`/`make_context_adapter`; progress registered via `_adapt_progress_from_ctx`; **`functools.partial` special-case + `make_adapter` import deleted from dashboard.py**. UX-L15 tests call plain `adapt_*` fns → unaffected.
- **D3 ✅ rebuild flag persists** — `persist_state(rebuild_from_events())` when `rebuild_state=True`. **Found real bug in `projector.fold`:** `check_badge_conditions` implements `honest_broker` for `measurement_recorded`+`is_void` but fold never called `_award_badges` for that kind → badge was unreachable. Added the call (UX-L2 strategies never draw `is_void` → replay lock unaffected). Test `test_rebuild_flag_persists_and_round_trips` green (gold_standard + honest_broker + progress panel round-trip + `get_last_rebuild_at`).
- **X4 ✅ multi-root** — CLI `--root` type=str comma-split via `parse_roots()` (unit-tested); `DashboardApp(roots=…)` kw-only; header `ui.select` when `len(roots)>1`; `switch_root()` resets EmbedCache/log_path/objectives/recognition_store(per-root `ui_state.sqlite`)/panels/snapshot/signature/config-sig + `_register_root_panels` + drawer + re-render; `_on_artifact_changed` drops foreign roots. Test green (note: after `switch_root` the current panel is *re-instantiated* by the re-render — assert instance *replacement*, not `_panels == {}`).
- **X5 ✅ config hot-reload** — `_poll` also stats `campaign.yaml`+`heartbeat.json`; `_reload_objectives()`: campaign.yaml `hpo.objectives` (list or str) → `parse_objectives`, **ValueError → keep current** (the `epoch_time_s` case), else `_objectives_from_heartbeat`; publish `ConfigChanged` only on actual name change → subscriber updates `pareto_state`, clears cycle, re-renders. 2 tests green.
- **D1 ✅ observability** — new `computronium/ui/metrics.py`: thread-safe counters (label maps) + reservoir histograms (Vitter R, 1024, seeded) → `render_prometheus()` summary text; idempotent `GET /metrics` route (`PlainTextResponse`); instrumented `dashboard_snapshot` / `dashboard_adapter` / `dashboard_render_panel` seconds + `dashboard_ws_events_total{topic}`. structlog/OTel still deferred (stdlib deviation noted per handoff #11).
- **D4 ✅ docs** — `docs/platform/dashboard.md` (flags incl. comma roots, kill switches, modes, 20-panel table, mermaid registry→adapter→bus, extension how-to, test map) + README link at the `docs/platform/` sentence (~line 534).
- **C1 ✅ fixed** — dropped nonexistent `nicegui[testing]` extra (dev + ui lines); `uv add --dev selenium` (→ 4.49.0, dependency-groups only — optional-deps copy removed); root `conftest.py` with `pytest_plugins = ["nicegui.testing.plugin"]`; **pyproject `main_file = ""`** (pytest ini) — NiceGUI's `get_path_to_main_file` would otherwise raise `FileNotFoundError` (no root `main.py`) on every Screen test.
- **C4 🔴 harness live, scan RED** — `tests/a11y/fixtures/axe.min.js` v4.10.3 vendored (553 KB, fetched from cdnjs — local-dir-only constraint); `_run_axe_scan` = inject axe + `execute_async_script` in-page (tags wcag2a/aa/21a/21aa), **with node target/html/failureSummary in output**. Replaced the axe-CLI skip. First real scan surfaced **genuine violations** (previously invisible behind the skip): `button-name` **critical ×3** (header icon-only buttons: glossary/tour/quiz — Quasar `q-tooltip` gives no accessible name), `aria-toggle-field-name` serious ×1 (DiscoveryMap view `ui.switch` with no label), `color-contrast` serious ×8 (targets not yet captured — re-run now prints them), `html-has-lang` **fixed** via `@ui.page(..., language="en")` (NiceGUI ≥3.14 per-page `language`). **Teardown ERROR:** screen fixture auto-fails on console SEVERE/ERROR logs — message not yet captured (get it next run; may need `screen.allowed_js_errors`).
- **C6 ⚙️ half done** — static lock `tests/property/test_ux_l6_marker_redundancy.py` (4 tests: totality, unique (icon,label), unique labels, unique icons — **green**); behavioral `tests/ui/test_ux_l6_grayscale.py` written (Screen pair, PIL grayscale, floor 5.0, `_wait_for_source` 30 s poll past the 4 s implicit wait) — **not yet run green** (was deselected while stabilizing the headless tier; earlier attempt errored at fixture).
- **Pre-existing bug fixed (found by X4 test):** `_rebuild_left_drawer` created a *nested* `LeftDrawer` (RuntimeError) — it had been silently swallowed by `event_bus.publish`'s `contextlib.suppress`, so B4 mode-rebuild was partially dead. `_build_left_drawer` now reuses+clears the existing drawer.
- **Verification (this checkpoint):** dev-env smoke OK; `ruff format` clean on touched files; `ruff check` **6 findings, all verified pre-existing on HEAD** (broad_map noqa+promote, dashboard try-clause ×2, projector fold noqa, atlas apply_bp_deficit — Register C); `pyright` **0 errors** on all touched/new files (5 broad_map errors pre-existing); targeted headless tier **85 passed** (tests/ui + UX-L1/L2/L6/L9/L10/L12/L15/L16 + tests/lint + dashboard smoke) + perf **3 passed** (adapter 48.4 ms, snapshot 116 ms) + row-virt green. **C4 axe RED, C6 grayscale not yet run, D5 not yet run** (below).

**Handoff notes for next session (implement, don't re-explore):**
1. **C4 remaining (ordered):** (a) add `aria-label` props to the 3 header icon buttons in `dashboard.py:_build_header` (glossary `menu_book`, tour `help_outline`, quiz `psychology`) — glossary keys? plain English OK if no key; (b) `aria-label` on DiscoveryMap view switch (`discovery_map.py` `ui.switch(value=self._show_table…)` — `.props('aria-label="…"')` reaches Quasar root/role); (c) re-run axe — the enhanced mapping now prints `targets`/`summary` per violation → fix the 8 `color-contrast` nodes (suspects: `text-white/80` subtitle, `text-grey` captions — adjust classes to tokens that pass; `meets_aa` helpers in `ui/a11y.tokens`); (d) same `language="en"` for `cli/dashboard.py` `@ui.page("/")` **and** the grayscale test page; (e) capture the teardown console-error text (run with `-s` / check `caplog`); if it's external noise (fonts/socket), whitelist via `screen.allowed_js_errors` — if it's ours, fix;    (f) re-run until 0 critical/serious in BOTH registers (the test scans explorer then lab).
   → ✅ FULLY DONE (this session): (a–b) aria-labels done; (c) contrast fixed via `PRIMARY #1a5fa8` + `SECONDARY #1c7d74` (`ui.colors`), `text-grey-8` captions, white `.ellipsis` CSS; (d) `language="en"` on all pages; (e) teardown noise allowlisted (`lang/en.umd.prod.js` 404); (f) **axe 0 critical/serious in BOTH registers, teardown clean**. Added: page-load timeout 4 s→30 s in both Screen tests (first render exceeds driver default).
2. **C6 ✅ DONE this session:** grayscale green (mean-abs-diff 6.10 > 5.0 floor); Plotly resize teardown noise allowlisted. Static marker-redundancy lock was already green.
3. **D5 verdict recorded:** gallery-compat 10/10 green; `test_figure_lock` RED on `compose_6axis` = pre-existing environmental drift (demo unchanged since emit `19c84ebd`) — deliberately NOT re-pinned.
4. **Also run before commit/close:** ✅ done — `test_ux_l8_gallery_compat.py` green, UX-L5 token/keyboard CSS classes green (13 passed + 1 manual skip), UI tier 21 passed, perf budgets 3 passed, `uv run pyright` 0 errors.
5. **Stage ONLY my files** (35 pre-existing dirty are NOT mine — continual/hyperopt/deployments/ceec/scripts/run_records + pre-existing noqa migrations). Mine: `conftest.py pyproject.toml uv.lock README.md GAME.todo2.md docs/platform/dashboard.md computronium/{cli,ui,visualization,autoscientist}/…` (exact list in commit) + `tests/{a11y,property,ui,perf}/…`. `tests/a11y/test_ux_l5_a11y.py` was pre-existing-dirty but was **rewritten this session** → stage it. Never stage `docs/figures/run_records/*.json` or `screenshots/` (screen-fixture output; consider gitignoring `screenshots/`).
6. **NiceGUI Screen mechanics (learned the hard way):** register `@ui.page` **inside the test** (the plugin's `nicegui_reset_globals` wipes routes before each test); `main_file=""` ini is required; driver implicit wait is 4 s — use the `_wait_for_page_source` poller (30 s) for atlas-dependent text; session-scoped shared Chrome; teardown auto-fails the test on console SEVERE/ERROR and saves `screenshots/<pid>/<test>.failed.png`.
7. **Cache gotcha:** `kb_load_cached` key must stay namespaced per loader family (`("cells", task)` / `("measured", task)`) — a shared key returns the wrong type.
8. **Opportunities found this session (not blocking):**
    - ~~`front_history_rows` builds a df with column `walltime` but DEFAULT objectives want `walltime_s` → `pareto_top` logs "Objective column walltime_s not in DataFrame; skipping" **on every `render_snapshot`** (5×/render). Align the column name (or rename the objective there) — cheap win, removes log spam + makes front-history actually objective-filtered. STILL OPEN.~~ ✅ FIXED 2026-09-23 (`walltime_s` + `param_count` from `param_budget`; 0 spam on default/3-obj/full-cost presets).
    - **New opportunities (2026-09-23 triage — none blocking, all small):**
      - `_CellRow` has no `settle_horizon` / `stability_plasticity_ratio` / `credit_efficiency` columns, so `front_history_rows` + `pareto_strip_rows` silently return unfiltered dfs under the stability/credit-efficiency presets (same `pareto_top` early-return). Either extend `_CellRow`/KB metrics or restrict the dashboard Pareto selector to supported presets.
      - `pareto_top`'s missing-column path `return df` (unfiltered) is a silent honesty hazard — consider returning `df.head(0)` or raising, at minimum a louder log level, so future column drift fails visibly instead of rendering a fake "front".
      - `live_atlas.build_dashboard` (legacy page) vs `ui.dashboard.build_dashboard` (CLI path) still coexist; the smoke test pins the legacy one. ✅ **Done in GAME.todo3 Session A (T4)** — legacy page deleted, smoke test retargeted to `ui.dashboard.build_dashboard` in the same commit.
      - ✅ Tightened `SNAPSHOT_BUDGET_S` 3.0 → 0.5 s in GAME.todo3 Session B (T5: 124 ms measured @5k warm, 4× headroom); `kb_load_cached` clear-on-full → FIFO if >16 roots ever matter.
   - ~~`render_header` passes key `"atlas"` missing from glossary.json~~ ✅ FIXED this session (`Map`/`Atlas`).
   - ~~`screenshots/` gitignore~~ ✅ DONE this session.
   - UMAP optional-import flakiness in this env ("issubclass() arg 2…" → t-SNE fallback, later runs succeed) + `n_neighbors` warnings on tiny fixtures — cosmetic; worth pinning `n_jobs`/`n_neighbors` for n<10 if the noise ever gates tests.
    - Two `build_dashboard`s still coexist (`ui.dashboard` = CLI, `live_atlas` = smoke) — ✅ unified in GAME.todo3 Session A (T4: legacy deleted).
   - `kb_load_cached` clear-on-full is coarse; FIFO eviction if 16 roots ever matter.
    - ✅ `SNAPSHOT_BUDGET_S` 3.0 → 0.5 s tightened in GAME.todo3 Session B (T5).
   - `screenshots/` from the Screen fixture should be gitignored.
   - Axe had NEVER actually run before this session — treat "0 critical/serious" as a *new* red-green signal, not a regression.
9. Prior handoff notes 1–14 above were **fully consumed this session** (implemented); anything not marked done in the tables is either done here or superseded.


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
6. **C6 done**: grayscale behavioral green (6.10 > 5.0 floor), no brittle pixel baselines per user directive.
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
| **C4** | Replace skipped UX‑L5 axe tests with real Playwright+axe scan against running dashboard on synthetic fixture; keep manual crawl checklist for cert only. | `test_axe_no_critical_or_serious` runs in CI, not skipped. ✅ **Done — 0 critical/serious in both registers.** |
| **C5** | Unskip UX‑L9 `test_panel_renders_all_six_invariants` and UX‑L10 component‑integration tests using headless render from C2. | ✅ 0 skips in UX-L9/L10 (was 7 skipped). |
| **C6** | Screenshot regression baseline (reduced‑motion + grayscale per UX‑L6): capture all panels, store under `tests/ui/baselines/`, compare on CI. | UX‑L6 snapshot test implemented. ✅ **Done — grayscale behavioral green (6.10 > 5.0 floor), no brittle pixel baselines per user directive.** |
| **C7** | UX‑L1 (Pareto equivalence) & UX‑L4 (readability script `scripts/lint_readability.py`) — referenced in GAME.todo.md §6 but no test files; create them. | ✅ All 11 UX locks have real test files; 0 dead references. |

### D — Observability, Performance & Polish (P1/P2)

| ID | Task | Acceptance |
|----|------|------------|
| **D1** | Structured logging (`structlog`) + OpenTelemetry metrics (render latency, WS message rate, adapter duration). Export `/metrics` endpoint for Prometheus. | ✅ **Amended to measured regime (GAME.todo3 T5, 2026-09-23: 124 ms @5k warm):** full-snapshot warm median <500 ms @5k; per-panel tight gate stays DiscoveryMap adapter ≤100 ms (47.5 ms); WS paint throttle ≥1 s. The old "p95 render <100 ms" line described pre-D2 hotspot numbers, not the snapshot path. |
| **D2** | Performance budgets as CI gates: DiscoveryMap ≤100 ms on 5k cells (measured in C2), WebSocket→UI debounce ≤1 Hz, panel virtualization for >1k rows. | Budgets enforced in `tests/perf/test_budgets.py`. |
| **D3** | `--rebuild-ui-state` end‑to‑end test: CLI flag → replay → sqlite → ProgressPanel round‑trip. | Flag demonstrably does something. |
| **D4** | `docs/platform/dashboard.md` — usage guide (flags, modes, panels, kill switches), architecture diagram, extension how‑to. | Doc exists, linked from README. |
| **D5** | Demo/gallery manifest: add one dashboard demo figure if gallery lock requires it (check `comp gallery` manifest rules). | UX‑L8 green (10/10 compat green, no DEMOS row needed). `test_figure_lock` RED on `compose_6axis` = pre-existing environmental drift — deliberately not re-pinned. |

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

Existing UX‑L1..L16 all have real test files. C4 (axe) + C6 (grayscale) are green — no UX‑L5/L6 skips remain (only the intentional manual keyboard crawl).

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
6. **C1 + C3 + C4 + C5** (automation expands to interactions + unskips). — ✅ all done (C4 axe green both registers)
7. **C6 + C7** (L1/L4/L6 locks). — **C7 done**; **C6 done**
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