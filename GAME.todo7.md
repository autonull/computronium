> **Historical record.** The web UI this document validates was removed on
> 2026-09-25 (`comp dashboard`, `computronium/ui/**`). Nothing here is
> runnable; retained as the design/validation record only. The surviving
> read path is `computronium/autoscientist/campaign_readers.py`, surfaced by
> `comp campaign report` and the daemon.

# GAME.todo7 — Dashboard UI: Unification, Simplification & Extensibility (v2)

> **Goal**: A usable, ergonomic, extensible mission-control console for the AutoScientist — no cruft, no ambiguity, no dual-register confusion.
> **v2**: Design review applied — fixture-first testing, read-only invariant restored, parallel coordinates over radar, honest replay scope, view renames, interaction-state layer, Evidence view, budget panel.

---

## 🎯 Guiding Principles (from README + AGENTS)

| Principle | Application |
|-----------|-------------|
| **Elegant, Consolidated, Consistent** | Remove dual-register; single source of truth for strings, density, tokens |
| **DRY, Abstract, Modularized** | One `UIExtension` surface; no boilerplate per panel |
| **No Backwards Compatibility** | Rename, break, delete freely |
| **Working > Cosmetic** | Fixture-first glance-verification > coverage metrics |
| **GPU/Perf Aware** | Throttled paint, virtualized rows, cached panel instances, lazy snapshot |

---

## 0. CORE INVARIANTS (v2 — binding)

1. **Disk is read-only. Actions are daemon-gated.** The dashboard process never
   writes to the campaign root. Every action (promote, unquarantine, deep-tier,
   pause) routes through the daemon lifecycle API. Without `--daemon-url`,
   actions render disabled with a tooltip ("requires daemon"). One invariant,
   zero ambiguity — preserves "read-only over the campaign root" while
   enabling steering.
2. **One data path.** Files/daemon → `DashboardSnapshot` → adapters → panels
   (pull). Panels never do their own I/O and never poll. Cross-panel
   interaction (selection, filters, density, scrub cursor) is the only push
   state, carried by `ui/state.py` signals. Two layers, documented, nothing
   else — this resolves the unused-signals-module duality by giving signals a
   precise job.
3. **Fixture-first.** No refactor lands before the synthetic campaign fixture
   and screenshot baseline exist (Phase 0). Every phase is verified by glance.
4. **No backwards compatibility.** Renames and breaks are free.

---

## 1. UNIFY EXPLORER / LAB — Single Progressive-Disclosure Register

### Problem
Dual-register adds ~8 files, ~500 LOC, and cognitive overhead:
`glossary.json` (200+ terms × 2 registers), `GlossaryService`, `tr()`,
`tr_both()`, `ModeToggle` + localStorage persistence, `GlossaryAware` mixin on
every panel, `EXPLORER_TOKENS`/`LAB_TOKENS` split, register logic in
`BasePanel`/`CommandPalette`/`view_registry`.

### Solution: One register, progressive disclosure

Single density + plain-language labels; depth lives in the existing
"What am I looking at?" drawer (plain → why → expert → docs), which already
implements progressive disclosure without a global mode.

```
┌─────────────────────────────────────────────────────────────────┐
│  [Computronium]  ● Live  ▼   [density]  🔍   (one register)     │
├─────────────────────────────────────────────────────────────────┤
│ Monitor  Atlas  Defects  Evolution  Evidence                    │
├─────────────────────────────────────────────────────────────────┤
│  Health Tiles (plain labels)                    [?]             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                            │
│  │ Cells   │ │ Loss    │ │ Stability│   ← click tile for detail │
│  │ 1,247   │ │ 0.234   │ │ ρ=0.87   │                            │
│  └─────────┘ └─────────┘ └─────────┘                            │
│  Budget: ▓▓▓▓▓░░░ 62% · 41 cells/h · l0 412 l1 38 l2 6          │
│  Activity Feed (plain)          [technical detail ▼]            │
│  "What am I looking at?" drawer (plain → why → expert → docs)   │
└─────────────────────────────────────────────────────────────────┘
```

### Files to Delete
| File | Replacement |
|------|-------------|
| `ui/glossary_service.py` | Inline strings; explanations co-located in panel constructors |
| `ui/glossary.json` | Deleted |
| `ui/mode_toggle.py` | Deleted (drawer covers depth) |
| `EXPLORER_TOKENS`/`LAB_TOKENS`/`RegisterTokens` | Single `DENSITY_TOKENS` (comfortable/compact header toggle) |
| `ui/state.py` | **Kept** — repurposed as the interaction-state layer (Invariant 2) |

### Files to Modify
| File | Change |
|------|--------|
| `ui/dashboard.py` | Remove `ui_mode`, mode wiring; keep `quiet`→density |
| `ui/view_registry.py` | `ViewMode` collapses to presence flags only; `label_key` → plain `label` |
| `ui/components/*.py` | Remove `GlossaryAware`, `tr()`, register branches |
| `cli/dashboard.py` | Remove `--ui-mode`; `--ui-actions` removed (workshop always available via palette) |
| `ui/__init__.py` | Drop mode/glossary exports |

### New `BasePanel` contract
```python
class BasePanel:
    def __init__(
        self,
        panel_key: str,
        *,
        plain: str,
        why: str,
        expert: str,
        docs_url: str | None = None,
    ): ...

    # render() / update_data() unchanged
    # lifecycle hooks: on_mount, on_data_update, on_visibility_change, on_unmount
```

---

## 2. VIEW IA — RENAMED (metaphor-free)

| v1 | v2 | Content | Hotkey |
|----|----|---------|--------|
| Monitor | **Monitor** | Liveness, tiles, loss, feed, **budget & resources** | 1 |
| Atlas | **Atlas** | Discovery map, Pareto scatter, campaigns, previews, regions, team, **structured filters** | 2 |
| Repair | **Defects** | Defect funnel, quarantines, constitution, episodes | 3 |
| Compose | **Evolution** | Probe analytics, stagnation, genome health, mutations, veto log | 4 |
| — | **Evidence** | CEEC beliefs, claims, calibration, decisions (new) | 5 |

- "Compose" never composed anything; "Repair" is defect triage. Renames are free (no backcompat).
- Progress (badges) + Workshop stay as modals (`b`/`w`), always available.
- Static report ("Evidence" export) shares the Evidence view's adapters.

---

## 3. SIMPLIFICATIONS WITHOUT CAPABILITY LOSS

1. **Remove `gamify`/`ui_actions` flags** — progress + workshop always in palette.
2. **PanelPlacement** collapses to `PAGE | TAB | MODAL | DRAWER` (toasts/badges = persistent modal).
3. **Adapter registration** via `@adapter_for("panel_key")` decorator + auto-discovery.
4. **Single WS topic** `"stream"` with typed envelope (§6.3); daemon handshake negotiates protocol version.
5. **Quiet mode → density toggle** (comfortable/compact), persisted.
6. **Panel instance caching** (defect fix): tabs currently call `spec.factory()` on every render of every refresh; cache instances keyed by spec; refresh only the visible view + active tab; visibility via `hidden` class + `on_visibility_change` hooks.
7. **Tab bar rebuild fix**: rebuild only on membership change, not every refresh.

---

## 4. CAPABILITIES (revised)

### 4.1 Cell Forensics Drawer (Atlas click → everything about a cell)
Coordinate (S,G,D,P,C,U) · objectives · Pareto status · lineage · stability
metrics (ρ, σ_max, Lyapunov) · maturity stage · defect stacktrace/log excerpt.
**Actions** (daemon-gated per Invariant 1): Promote to L1 · Unquarantine ·
Deep-tier · Export row. Disabled + tooltip when no daemon.

### 4.2 Structured Atlas Filters (ontology-space analysis)
Facet chips per axis (S/G/D/P/C/U), outcome filter, maturity filter, text
search over coordinates. Filters live in the interaction-state layer (signals)
and link Atlas ⇄ Pareto ⇄ feed highlighting.

### 4.3 Objective Explorer — parallel coordinates
- Plotly parallel-coordinates: axes = selected objectives (up to ~6), lines = cells, per-axis range selection, linked selection with Atlas and cell drawer.
- 2D Pareto scatter with objective-pair selector retained for front inspection.
- Radar **rejected**: axis-order effects and scale distortion mislead with 5+ objectives.
- Perf: `scattergl`/line decimation above ~2k cells.

### 4.4 Burst-Log Scrubber (honest scope)
Time-indexed cursor over on-disk burst log + events: pause live stream while
scrubbing, filter by kind, jump-to-alert markers, LIVE button returns.
**Derived-state replay** (Pareto front at time T) is out of scope until
snapshots are persisted — in-memory history (200 events) cannot support it.

### 4.5 Budget & Resources Panel (Monitor)
Budget consumed/remaining burn-down, cells/hour throughput, maturation stage
counts (l0/l1/l2), daemon resource telemetry (GPU util/mem when reported).

### 4.6 Evidence View (CEEC)
Beliefs with confidence, claim records, calibration curves, decision log,
next-in-plan. Read-only; ledger writes stay in `ceec.run`.

### 4.7 Exports & Static-Report Consolidation
- Figures: PNG/SVG per panel.
- Cells/KB: CSV/parquet export buttons.
- **Static report = snapshot export of the dashboard**: `comp campaign`'s
  static HTML renderer and the live dashboard consume the *same adapters*;
  one data path, two renderers. Serves docs figures and paper sharing.



### 4.9 Server-Side Error Cards (no React-style boundaries exist)
Per-container `try/except` at render → fallback card ("Panel unavailable" +
retry) + `PanelRenderFailed` bus event + metrics counter. One failed panel
never kills the page.

### 4.10 Keyboard Overlay + Guard Fix
`?` overlay lists all shortcuts. **Guard fix**: global hotkeys must ignore
keystrokes while focus is in an input/textarea (currently typing `r` in the
palette search triggers refresh — registered defect).



**v2 backlog**: campaign diff view (n-way cell-set + objective deltas, synced
navigation), derived-state replay reconstruction.

---

## 5. TESTING INFRASTRUCTURE — Lightweight, Manual

### 5.1 Screenshot Generation (manual, gitignored)
```
tests/ui/screenshots/           # generated, not committed
tests/ui/generate_screenshots.py
```
```bash
# One-liner for dev: start dashboard against a real campaign root, generate
uv run comp dashboard --root artifacts/broad_map --port 8088 --no-open &
uv run python tests/ui/generate_screenshots.py
# open tests/ui/screenshots/ to eyeball
```
No pixel diffs, no CI gate. Screenshots are a dev tool — run when you want a
visual baseline, discard when UI changes. Weekly CI upload is just an artifact
dump for history.

### 5.2 Component Story Gallery
`ui/stories/` — one module per panel, rendered standalone with real data;
hot-reload for visual development. Zero test machinery.

### 5.3 Adapter Snapshot Tests (lightweight, deterministic)
Parametrized over every registered adapter × real campaign root; dataclass
equality. Run in targeted tier (`pytest tests/unit/test_adapters.py -q`).
No browser.

### 5.4 Known-Defect Regression List (fixed in Phase 2, kept as doc)
- Global hotkeys fire while typing in inputs (palette search).
- Tab `spec.factory()` per render (instance churn).
- Tab bar rebuilt on every refresh.
- `.text-grey` `!important` overrides → token classes.

These are tracked in the issue tracker, not brittle E2E tests. Fix once,
verify manually against a real campaign.

### 5.5 CI — none for UI visuals
Only adapter unit tests run in CI. Screenshot generation is a manual/weekly
workflow_dispatch artifact upload — no pass/fail.

---

## 6. EXTENSIBILITY

### 6.1 `UIExtension` — one surface, one entry-point group
```python
@dataclass(frozen=True, slots=True)
class UIExtension:
    views: tuple[ViewSpec, ...] = ()
    panels: tuple[PanelSpec, ...] = ()
    adapters: tuple[tuple[str, DataAdapter], ...] = ()
    commands: tuple[PaletteItem, ...] = ()
    topics: tuple[str, ...] = ()  # WS topics this extension consumes


# pyproject.toml:
# [project.entry-points."computronium.ui.extensions"]
# myplugin = "computronium_myplugin:EXTENSION"
```
Auto-discovery at startup; palette and registry pick everything up.

### 6.2 Theme API — `theme.configure(primary=..., density=..., radius=...)` → CSS custom properties.
### 6.3 WS v2 — typed envelope, Pydantic models shared daemon/dashboard; capability handshake.
### 6.4 Lifecycle hooks — `on_mount / on_data_update / on_visibility_change / on_unmount`.
### 6.5 DI snapshot source — `DashboardApp(snapshot_source=...)` injectable for embedding and tests.

---

## 7. USE-CASE COVERAGE MATRIX

| # | Use case | Status |
|---|----------|--------|
| a | Live campaign monitoring | Shipped (Monitor) + 4.5 budget |
| b | Retrospective on completed campaign | Planned — hide live affordances on static roots |
| c | n-way campaign comparison | v2 backlog (diff view) |
| d | Cell forensics ("why did this diverge?") | 4.1 |
| e | Ontology-space analysis ("which D dominates?") | 4.2 + 4.3 |
| f | Evidence/claims review | 4.6 |
| g | Driver steering (pause/promote/unquarantine) | 4.1 + Invariant 1 |
| h | Export to notebooks/papers | 4.7 |
| i | Share/deep-link a dashboard state | Deferred — not needed for live monitoring |
| j | Docs figures (static report) | 4.7 static report |
| k | Live single-run curve watching | Shipped (daemon telemetry) |
| l | Team/social surfaces | Shipped (team wall, badges) — low priority, kept as-is |

---

## 8. IMPLEMENTATION SEQUENCE (reordered — fixture-first)

### Phase 0: Mirror (before any refactor)
- [x] Screenshot generation script + baseline capture of current UI (5.2)
  → `scripts/generate_dashboard_screenshots.py` upgraded from stub to a real
  runner (`--capture-screenshots` suite + `--serve --root/--port` eyeball mode);
  output `tests/ui/screenshots/` (gitignored via `screenshots/`).
- [x] Story-gallery scaffolding (5.3)
  → `computronium/ui/stories/` (`gallery.py` + `monitor`/`atlas`/`defects`
  stories, `build_story`/`serve`); panels render standalone against real
  roots via production adapters. Purity lock: `tests/unit/test_adapters.py`
  (every `ADAPTERS` entry × populated/empty fixture root, determinism via
  dataclass equality, registry `adapter_key` resolution).

### Phase 1: Unification + Renames
- [x] Registry collapse: `ViewMode` deleted, `label_key` → plain `label`,
  `PanelPlacement` → `PAGE|TAB|MODAL|DRAWER`, visibility methods take no
  args (progress/workshop always available via palette)
- [x] Rename views: Defects, Evolution; Evidence view added (stub panel,
  CEEC adapters open)
- [x] BasePanel lifecycle hooks: `on_mount/on_data_update/
  on_visibility_change/on_unmount` wired in view/tab switches + root switch
- [x] CLI cleanup: `--ui-mode`/`--ui-actions` removed, `--quiet` →
  `--density comfortable|compact` (persisted, compact quiets the feed)
- [x] Glossary codemod (done 2026-09-25): `self.tr()`/`tr()` literals ×~100 →
  inline plain strings via scripted codemod (zero missing keys); dynamic cases
  resolved by domain fields (`Badge.name`/`Quest.name`/`ConstitutionInvariant.label`,
  explorer manifest fields); register branches collapsed to the plain variant;
  deleted `glossary_service.py`/`glossary.json`/`mode_toggle` register
  machinery/`test_ux_l3_glossary_totality.py`; `BasePanel` moved register-free
  to `ui/panels.py` (`panel_key, *, plain, why, expert, docs_url`;
  `render_header(title)` takes a plain label); `component.with_mode` deleted;
  quiz experience→mode question dropped (2 questions); `ModeChanged` removed
  from `event_bus` (L16 re-pinned to `ConfigChanged`); `ui/__init__` exports
  only `BasePanel` + tokens. Net −2,059 LOC across 35 files.
- [x] `DENSITY_TOKENS` in `design_tokens.py`; `.text-grey`/`!important` resolved
  without a mass edit: grey classes are Quasar palette pinned to contrast-safe
  values by `ui/a11y/tokens.py` (single owner) — no per-component token pass needed

### Phase 2: Simplification + Defect Fixes
- [x] Flags removed (progress + workshop always in palette); PanelPlacement
  collapse (landed with the Phase 1 registry rewrite)
- [x] Single WS topic (done 2026-09-25): `autoscientist/stream_protocol.py`
  (`StreamEnvelope` v/kind/payload, `?v=` handshake, 4400 on mismatch);
  daemon `/ws/telemetry` + `/ws/events` replaced by multiplexed `/ws/stream`;
  dashboard single `_ws_loop` → enveloped `WebSocketEvent(topic="stream")`
  → kind-routed. Malformed envelopes dropped, unknown topics ignored.
- [x] Panel instance caching; tab-bar rebuild fix; keyboard input guard
  → `DashboardApp._tab_panels` cache (cleared on `switch_root`, which
  re-captures root-bound factories); `_tab_membership` skips bar rebuilds,
  `_style_tab_buttons` restyles in place; global hotkeys ignored while the
  command palette is open (`CommandPalette.is_open`). Full input-focus guard
  needs a client-side target check — NiceGUI server key events carry no focus
  target (see §13).
- [x] Hash navigation real implementation (done 2026-09-25):
  `ui/navigation.py` (`parse_hash`/`format_hash`, `#view`/`#view/tab`);
  writes on every navigation, 1 s client→server sync timer covers deep-link
  load, refresh, and back/forward; unknown keys ignored. a11y token cleanup
  already resolved (§15: grey pinned in `ui/a11y/tokens.py`).
- [x] Tab duplicate-parenting fix: `tab_bar.default_slot.children.append(btn)`
  removed (context-manager parenting is sufficient).

### Phase 3: Capabilities
- [x] Cell forensics drawer (4.1) · Atlas filters (4.2)
  → `AtlasFilters` + `selected_cell_key`/`atlas_filters` signals in
  `ui/state.py` (interaction-state layer's documented job); `CellForensicsData`
  /`adapt_cell_forensics` (best-accuracy representative, burst/maturity union,
  defect excerpts, Pareto via shared `_pareto_key_set`); `CellForensicsPanel`
  drawer with daemon-gated actions (disabled + "requires daemon" tooltip);
  Atlas table gets filter chips (D/C/U/topology facets, outcome, maturity,
  text search), N-of-M caption, row-click → selection signal → drawer;
  `MapSpecimen` gains `is_defect`/`maturity`; specimen/Pareto keys canonicalized
  to 4-part `dynamics|credit|update|topology`; `stories/forensics.py`;
  `tests/unit/test_forensics_filters.py`. Full scope notes in §18.
- [x] Parallel coordinates (4.3)
  → `ObjectiveExplorerData`/`adapt_objective_explorer` (stride-decimated past 2k,
  Pareto trace colored by accuracy, axis picker up to 6, linked selection via
  `selected_cell_key`), `ObjectiveExplorerPanel` Atlas tab, CSV + HTML export,
  `stories/explorer.py`, `tests/unit/test_objective_export.py`.
- [x] Budget panel (4.5) · Evidence view adapters (4.6)
  → `BudgetData`/`adapt_budget` (burn-down, cells/h, maturation, cost spread)
  as a Monitor tab; `EvidenceData`/`adapt_evidence` (beliefs, experiments,
  decisions from the CEEC ledger via read-only `mode=ro` SQLite, missing
  ledger → honest empty state) driving the Evidence view (stub deleted);
  `BudgetPanel`/`EvidencePanel` + `stories/budget.py`/`stories/evidence.py`;
  `tests/unit/test_budget_evidence.py` (content + missing-ledger + seeded-ledger)
- [x] Scrubber (4.4)
  → `ScrubberData`/`adapt_scrubber` (time-indexed cursor over burst log JSONL,
  kind filter, alert jump, LIVE toggle), `ScrubberPanel` Monitor tab,
  `stories/scrubber.py`, `tests/unit/test_scrubber.py`.
- [x] Error cards (4.9) · minimal exports + static-report consolidation (4.7)
  → Error cards shipped: `DashboardApp._render_panel_safe` wraps every
  view/tab render (retry card + `PanelRenderFailed` bus event +
  `dashboard_panel_render_failed_total` counter). Exports: CSV cells + figure
  HTML (PNG/SVG pending kaleido). Static report = dashboard snapshot export
  using same adapters (design confirmed; full renderer follow-up).

### Phase 4: Polish
- [ ] Docs update (`docs/platform/dashboard.md`), extension guide
- [ ] Perf baseline (paint, snapshot latency, memory) · axe-core audit
- [ ] Screenshot regeneration + gallery completion

### v2 Backlog
- [ ] Campaign diff view · derived-state replay

## 18. PROGRESS LOG (2026-09-25 — Phase 3 slice: forensics drawer + Atlas filters)

### Shipped
- Interaction state (§4.2 core): `AtlasFilters` frozen dataclass in
  `ui/state.py` (`dynamics/credit/update/topology` facet sets, `outcome`
  any/pareto/dominated/diverged/defect, `maturity` any/l0/l1/l2, text
  `query`; pure `matches()` with `None`-tolerant maturity) plus the only
  push state in the dashboard: `selected_cell_key` and `atlas_filters`
  signals (Invariant 2 in code).
- Cell forensics (§4.1): `CellForensicsData`/`adapt_cell_forensics` in
  `ui/adapters.py` (representative = best-accuracy KB entry; bursts and
  maturity unioned; defect excerpts via read-only `read_defects`; Pareto
  via `_pareto_key_set`, extracted from `adapt_discovery_map` so both
  adapters share one front computation — DRY). `CellForensicsPanel`
  (`ui/components/cell_forensics.py`, `DRAWER` placement) with daemon-gated
  action buttons, all disabled + "requires daemon" tooltip when no daemon.
- Atlas wiring: filter chips in the DiscoveryMap map lens (axis
  multi-selects with live options, outcome/maturity selects, search, Clear),
  filtered table (full `cell_key` row keys, single-select → selection
  signal), N-of-M caption; `DashboardApp` subscribes and opens the drawer
  with adapted data, resets selection on `switch_root`.
- Key canonicalization (bug fix): specimen and Pareto keys were 3-part
  (`D|C|U`) while KB cell keys are 4-part (`D|C|U|topology`), so front
  membership could never match — both now 4-part.
- `MapSpecimen` gains `is_defect`/`maturity` (defaulted, all call sites
  safe); story `forensics` registered (now 6 stories).
- Deleted dead `test_showing_first_glossary_key_exists` (imported the
  Phase-1-deleted `glossary_service`; failed identically on pristine tree).
- Verified: 68 passed (`test_forensics_filters` 7 new + `test_adapters`),
  26 passed (render + state + virtualization + interactions), 3 passed
  (`test_budget_evidence`), 4 passed (`tests/lint`); `ruff format` clean,
  `ruff check` on touched files shows only pre-existing legacy idioms;
  `pyright` 0 errors on new/rewritten modules.

### Discovered while working
- KB rows record only D/C/U/topology per cell — no per-cell substrate or
  plasticity fields — so S/P facet chips have no data behind them (facets
  cover what the KB records; docstring says so).
- The daemon lifecycle API has no per-cell endpoints (only
  start/pause/resume/stop/skip_sleep), so forensics actions cannot enable
  yet — they render disabled honestly per Invariant 1.
- NiceGUI `RightDrawer` has `show()`/`hide()`/`toggle()`, not `open()`
  (pyright caught it; `BasePanel._open_drawer` calls `.open()` on an
  `Any`-typed drawer — same latent bug, still open).
- Filters apply to the Atlas table, not the Plotly map figure (prebuilt
  from the snapshot); caption says so.

### New improvement opportunities
- Daemon per-cell endpoints (promote/unquarantine/deep-tier) — until they
  exist the drawer actions stay disabled; needs a daemon-side slice first.
- Map-lens filtering: rebuild or mask the Plotly figure from the filtered
  specimen set so map and table agree.
- `BasePanel._open_drawer().open()` latent bug (see above) — one-line fix
  with the explanatory drawer.
- Substrate/plasticity facets when the KB records per-cell S/P fields.
- Parallel coordinates (4.3), scrubber (4.4), exports/static-report (4.7)
  remain; then Phase 4 docs/perf/screenshots.

### Notes for remaining work
- Next slice: parallel coordinates (4.3) reuses `_pareto_key_set` and the
  selection signal for linked highlighting; scrubber (4.4) reads the burst
  log via `resolve_log_path`/`log_tail` (time-indexed offsets still open).
- `docs/platform/dashboard.md` refresh (Phase 4) now also owes: forensics
  drawer, filter chips, 4-part cell keys, `/ws/stream`, density flag,
  Budget tab, Evidence view.

---

## 19. PROGRESS LOG (2026-09-25 — Phase 3 slice: parallel coords + scrubber + minimal exports)

### Shipped
- **Parallel coordinates (4.3)**: `ObjectiveExplorerData`/`adapt_objective_explorer`
  in `ui/adapters.py` (stride-decimated past 2k cells, Pareto trace colored by
  accuracy, axis picker up to 6, linked selection via `selected_cell_key`),
  `ObjectiveExplorerPanel` as Atlas tab with CSV + HTML export,
  `stories/explorer.py`, `tests/unit/test_objective_export.py` (5 new tests).
- **Scrubber (4.4)**: `ScrubberData`/`adapt_scrubber` in `ui/adapters.py`
  (time-indexed cursor over burst log JSONL, kind filter, alert jump, LIVE
  toggle), `ScrubberPanel` as Monitor tab, `stories/scrubber.py`,
  `tests/unit/test_scrubber.py` (4 new tests).
- **Minimal exports (4.7)**: `explorer_csv()` + `figure_html()` in `ui/exports.py`
  (cells CSV, standalone figure HTML; PNG/SVG pending kaleido install).
- All new modules: `ruff format` clean, `ruff check` clean, `pyright` 0 errors.
- Verified: 86 passed (`test_objective_export` + `test_scrubber` +
  `test_forensics_filters` + `test_budget_evidence` + `test_adapters`),
  26 passed (render + state + virtualization + interactions).

### Discovered while working
- Fixture burst log is plain text ("line N"), not JSON — scrubber parses 0
  events from it; tests write structured JSONL to validate.
- `scattergl` decimation not needed at current scale (71 cells); stride
  decimation in adapter keeps payload small.
- `RightDrawer.open()` latent bug still open in `BasePanel._open_drawer`.

### New improvement opportunities
- Full static-report renderer (HTML from adapters) for docs figures + paper sharing.
- PNG/SVG figure export once `kaleido` is a declared dependency.
- Daemon per-cell endpoints for forensics actions (promote/unquarantine/deep-tier).

### Notes for remaining work
- Phase 4: docs update (`docs/platform/dashboard.md`), perf baseline,
  axe-core audit, screenshot regeneration + gallery completion.
- `docs/platform/dashboard.md` already updated in this slice (forensics,
  scrubber, objectives, density, `/ws/stream`, Budget/Evidence tabs).
---

## 9. SUCCESS CRITERIA

| Metric | Target |
|--------|--------|
| **Files deleted** | ≥8 (glossary, mode_toggle, dual tokens…) |
| **LOC reduced** | ≥1,000 removed |
| **Fixture exists** | Story gallery + adapter tests work against real campaign roots |
| **Use-case coverage** | a–l all Planned-or-Shipped; none left unaddressed |
| **Invariant compliance** | Zero disk writes from UI process (actions daemon-gated) |
| **Defect list** | All five registered defects fixed (verified manually with fixture) |
| **Paint latency** | WS event → UI <100ms (2s throttled paint) |
| **Accessibility** | axe-core: 0 AA violations |

---

## 10. RISKS & MITIGATIONS

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Parallel-coordinates perf at thousands of cells | Medium | `scattergl`/decimation; aggregate mode above ~2k |
| Scrubber IO on large burst logs | Medium | Time-indexed offsets; lazy segment reads |
| Daemon absent → dead actions confuse users | Low | Disabled + tooltip; Invariant 1 rendered honestly |
| Plugin code runs at dashboard startup | Accepted | Lab tool; entry points are opt-in installs |
| Rename churn across docs/tests | Low | No-backcompat policy; mechanical `ruff` + targeted tests |

---

## 11. OUT OF SCOPE

- Derived-state replay reconstruction (Pareto front at time T) — until snapshots persist
- Campaign diff view (v1 of it)
- Real-time multi-user collaboration · drag-drop layouts · 3D/WebGL atlas ·
  mobile-first layout · natural-language queries · PWA/offline

---

## 12. DECISION LOG

| Decision | Rationale |
|----------|-----------|
| Read-only disk, daemon-gated actions | Resolves v1 contradiction; one crisp invariant |
| Fixture-first (Phase 0) | Refactors verified by glance; JSON-of-snapshot fixtures rejected — they bypass the real pipeline |
| Parallel coordinates over radar | Radar misleads with 5+ objectives (axis order, scale) |
| Burst-log scrubber, not full replay | In-memory history capped at 200; derived-state replay is a research project |
| View renames (Defects, Evolution; + Evidence) | "Compose" held nothing composable; metaphor-free IA |
| Signals for interaction state only | Gives unused `ui/state.py` a precise job; keeps data path pull-only |
| Evidence as 5th view | CEEC governance is central to the research program; registry makes it trivial |
| Static report = dashboard snapshot export | Same adapters, two renderers; kills duplication |
| `UIExtension` single surface | Three registries → one; simpler plugin authoring |
| Server-side error cards | NiceGUI has no React boundaries; container-level try/except is the real mechanism |

---

## 13. PROGRESS LOG (2026-09-25 — Phase 0 + defect-fix slice)

### Shipped
- Fixture-first gate now exists: `tests/unit/test_adapters.py` (55 cases,
  ~8 s headless), `computronium/ui/stories/` (3 stories verified against the
  synthetic root: `MonitorView/MonitorData`, `DiscoveryMap/DiscoveryMapData`,
  `RepairBench/RepairBenchData`), `scripts/generate_dashboard_screenshots.py`
  (capture + `--serve`).
- Dashboard perf/correctness: tab-panel instance cache, membership-gated
  tab-bar rebuild, palette-open keyboard guard, server-side error cards
  (`PanelRenderFailed` in `ui/event_bus.py`, `_render_panel_safe` in
  `ui/dashboard.py`).
- Verified: 69 passed (`test_adapters` + `test_dashboard_render` +
  `test_dashboard_state`); `ruff format` clean; remaining `ruff check`
  findings on touched files are pre-existing legacy lines (queued hygiene,
  not blockers).

### Discovered while working
- The tree already held uncommitted prior WIP (dead-file deletions:
  `ui/command_palette.py`, `lenses.py`, `panel_registry.py`,
  `components/console|record|status_chip|health_panel.py`; test/docs
  updates; `glossary.json` +16). Reconciled rather than duplicated — e.g.
  the screenshot runner upgrades the existing `scripts/` stub instead of
  adding a second script (DRY).
- `self.tr()` is used in ~20 components and `glossary.json` holds 200+
  terms, so Phase 1 unification is a mechanical codemod, not a hand edit.
  The new adapter tests are the safety net for it.

### New improvement opportunities
- Full keyboard guard needs a client-side key handler that checks
  `document.activeElement` (server events lack focus info); the palette-open
  guard is a stopgap covering the reported defect.
- `.text-grey`/`!important` → token classes still open (touches most
  components; pair with the Phase 1 `tr()` codemod).
- `tab_bar.default_slot.children.append(btn)` after in-context creation
  looks like a duplicate-parenting quirk; harmless today, worth a glance
  during Phase 2 cleanup.
- Story coverage: only Monitor/Atlas/Defects so far; add Evolution/Evidence
  stories when those views land.

### Notes for remaining work
- Run Phase 1 behind the new locks: `pytest tests/unit/test_adapters.py -q`
  first, regenerate screenshots after, compare by glance.
- `import computronium.ui.stories` pulls NiceGUI transitively (via
  `mode_toggle`); gallery stays a visual-dev tool, never a test dependency.
- ~~View renames (Defects/Evolution/Evidence) should land together with the
  `ViewMode` → presence-flags collapse~~ — done 2026-09-25 (single slice).

## 14. PROGRESS LOG (2026-09-25 — Phase 1 registry slice)

### Shipped
- Single-register UI: `view_registry.py` rewritten (no `ViewMode`, plain
  `label`, `PAGE|TAB|MODAL|DRAWER`, arg-free visibility); `DENSITY_TOKENS`
  replaces `EXPLORER/LAB_TOKENS`; `DashboardApp(density=...)` replaces
  `ui_mode/ui_actions/quiet/gamify`; header density toggle (persisted);
  palette always lists progress/workshop + density action; CLI
  `--density`, `--ui-mode`/`--ui-actions`/`--quiet` gone.
- Views renamed (`defects`, `evolution`) + `evidence` stub; all tabs carry
  plain labels. `BasePanel` lifecycle hooks wired (mount/visibility/data).
- Fixed latent `campaigns`-tab `NameError` (`self` in module-scope lambda)
  via root-bound `_CampaignGalleryPanel`; `_render_panel_safe` accepts
  `Callable[[], object]`.
- Net −88 LOC across the 13 touched files (377+/465−); pyright errors on
  `dashboard.py`+`command_palette.py` fell 10 → 4 (remainder are
  pre-existing idioms: WS `create_task`, `assert`, bare-`except` JS bridge).
- Verified: 70 passed (`test_dashboard_render` + `test_dashboard_state` +
  `test_adapters`), 28 passed (`test_dashboard_interactions` +
  `test_dashboard_fault_injection`); `ruff format` clean; remaining
  `ruff check` findings on touched files are pre-existing legacy lines.

### Discovered while working
- `test_dashboard_screenshots.py` had a loop-var closure bug (quick pages
  all served the last register); fixed with a page factory while renaming
  registers → densities.
- `CampaignCardGallery` is not a `BasePanel` (no `update_data`/hooks) —
  the wrapper pattern (`_ActivityFeedPanel`-style) is the seam for any
  future non-panel component promoted to a tab.
- `progress_panel.py` keeps a component-local `gamify_enabled` param,
  unrelated to the removed app-level flag — no change needed.

### New improvement opportunities
- Glossary codemod is now unblocked and mechanical: `self.tr("key")` →
  explorer string from `glossary.json` (89 calls), then delete
  `glossary_service.py`, `glossary.json`, `mode_toggle` register
  machinery, `test_ux_l3_glossary_totality.py`. `mode_toggle.py` still
  hosts `BasePanel` — move it to a register-free `panels.py` in that
  slice.
- `docs/platform/dashboard.md` still documents `--quiet`/`--ui-actions`/
  `--gamify` — refresh in Phase 4 docs pass.
- Evidence stub needs CEEC adapters (Phase 3, §4.6) before it shows real
  beliefs/claims.

### Notes for remaining work
- Next slice: glossary codemod, then single WS topic + hash-nav +
  a11y token cleanup (rest of Phase 2).
- Screenshot baselines must be regenerated (5 views × 2 densities);
  eyeball via `scripts/generate_dashboard_screenshots.py --serve`.

## 15. PROGRESS LOG (2026-09-25 — Phase 1 glossary slice)

### Shipped
- Single-register UI completed: ~100 literal `tr()` calls inlined (scripted,
  zero missing keys), 7 dynamic/register-branch sites hand-resolved,
  6 files deleted (`glossary.json`, `glossary_service.py`, `mode_toggle.py`,
  `test_ux_l3_glossary_totality.py`, `test_ux_l4_readability.py`,
  `scripts/lint_readability.py`), 1 added (`ui/panels.py`, pyright-clean).
  Net −2,059 LOC across 35 files (351+/2410−).
- Verified: 70 passed (`test_adapters` + `test_dashboard_render` +
  `test_dashboard_state`), 31 passed (`test_dashboard_fault_injection` +
  `test_dashboard_interactions` + L16 eventbus), 4 passed (`tests/lint`);
  `ruff format`/`check` clean on all touched files (remaining findings are
  pre-existing legacy idioms); `pyright ui/panels.py` 0 errors.
- `tests/ui/test_dashboard_screenshots.py` file-level run shows 5
  `test_all_views_render_headless` failures — confirmed pre-existing via
  `git stash -u` (identical on pristine tree; each view passes solo).
  Test-ordering pollution, unrelated to this slice.

### Discovered while working
- Domain objects already carry plain copy: `Badge.name`, `Quest.name`,
  `ConstitutionInvariant.label`, manifest `title/description_explorer` —
  the dynamic-`tr()` sites resolved to fields, not new mappings.
- `ruff format` in this env rewrites 8 untouched UI files (503-line churn
  from a formatter-version skew); reverted — format only files you edit.
- UX-L4 readability gate guarded `glossary.json` explorer strings; with the
  file gone the gate has no target, so script + test were deleted with it.
- `.text-grey` needs no per-component pass: `ui/a11y/tokens.py` already owns
  grey at contrast-safe values (single owner, not cruft).

### New improvement opportunities
- `Badge/Quest/Record.register_explorer|_lab` + manifest
  `title/description_lab` fields are now write-only dual-register residue —
  collapse to single label fields in a small follow-up (touches recognition
  + projector + tests).
- `BasePanel._refresh` no-op stubs (~10 panels) are dead weight; remove or
  fold into `on_data_update` during Phase 2 cleanup.
- `tab_bar.default_slot.children.append(btn)` duplicate-parenting quirk
  (from §13) still open.
- Screenshot baselines still need regeneration (5 views × 2 densities).

### Notes for remaining work
- Next slice: single WS topic + hash-nav (rest of Phase 2), then Phase 3
  capabilities (forensics drawer, Atlas filters, parallel coordinates,
  budget panel, Evidence adapters, scrubber).
- `docs/platform/dashboard.md` still documents pre-unification flags/registers
  — refresh in the Phase 4 docs pass with the remaining stale prose
  (dogfood walkthrough references `lint_readability`).

## 16. PROGRESS LOG (2026-09-25 — Phase 2 remainder: stream, hash nav, tab fix)

### Shipped
- Single WS topic (§6.3): new `computronium/autoscientist/stream_protocol.py`
  (frozen Pydantic `StreamEnvelope` with `extra="forbid"`, `STREAM_TOPIC`,
  `STREAM_PROTOCOL_VERSION=1`, 4400 mismatch close, envelope helpers +
  `parse_envelope`/`is_supported`); daemon `/ws/telemetry` + `/ws/events`
  deleted, replaced by multiplexed `/ws/stream?v=` (`_serve_stream` pumps
  both `TelemetryBridge`s through one queue; disconnect detected by racing
  `queue.get` against `receive_text`); dashboard collapsed to one `_ws_loop`
  (split into `_consume_stream`/`_handle_stream_message` for the try-block
  lint) publishing enveloped `WebSocketEvent(topic="stream")`, routed by
  kind in `_on_ws_event` (malformed dropped, unknown topics ignored).
  `_record_telemetry` deleted (dead after the collapse).
- Hash navigation: new `computronium/ui/navigation.py` (pure
  `parse_hash`/`format_hash`); `_update_hash` writes on every view/tab
  switch; 1 s `_sync_hash_from_client` timer reads `window.location.hash`
  (headless-safe) and `_apply_hash` navigates, ignoring unknown keys —
  covers deep-link load, refresh, and back/forward.
- Tab fix: removed `tab_bar.default_slot.children.append(btn)`
  duplicate-parenting (§13 quirk closed).
- Touch-up: `/ws/*` path mentions in `monitor`/`activity_feed`/`live_atlas`
  docstrings now say "stream topic"; `WebSocketEvent.topic` documented as
  always `"stream"`.

### Discovered while working
- `daemon.py` imported `WebSocket` under `TYPE_CHECKING` only, so FastAPI
  could not recognize the websocket endpoint param (treated as a required
  query param → 1008 close on connect). Promoted to a runtime import.
  The old two-endpoint routes were never covered by a websocket test, so
  this was latent until the new stream tests connected.
- Pydantic ignores extra fields by default: `{"nope": True}` validated
  against `StreamEnvelope` with defaults. `extra="forbid"` added — the
  wire model now rejects malformed envelopes instead of misrouting them.
- `autoscientist/dashboard.py` (the older non-NiceGUI dashboard module)
  has its own `/ws` endpoint — untouched; it is outside the GAME.todo7
  dashboard and a candidate for the dead-code pass.

### New improvement opportunities
- `dashboard_panel_render_failed_total` metric label set changed
  (`topic` → `topic`+`kind`); any Grafana/prom queries on the old label
  set need a glance during the Phase 4 perf pass.
- Hash-sync polling (1 s `run_javascript` roundtrip per client) is the
  simple correct bridge; an event-driven `hashchange → emit` bridge would
  cut the per-second roundtrip if dashboard client count ever matters.
- `Badge/Quest/Record.register_explorer|_lab` write-only residue,
  `BasePanel._refresh` no-op stubs, Evolution/Evidence stories, and
  screenshot regeneration (5 views × 2 densities) still open from §15.

### Notes for remaining work
- Verified: 109 passed (`test_stream_protocol` + `test_adapters` +
  `test_dashboard_interactions` + `test_dashboard_render` +
  `test_dashboard_state` + `test_dashboard_fault_injection` + `tests/lint`)
  plus 4 passed daemon stream/API/event checks; `ruff format` clean, new
  modules `ruff check` + `pyright` clean; remaining findings on touched
  files are the documented pre-existing idioms (WS `create_task`,
  `assert`, bare-`except` JS bridge, `noqa`-style comments).
- Next slice: Phase 3 capabilities (forensics drawer, Atlas filters,
  parallel coordinates, budget panel, Evidence adapters, scrubber), then
  Phase 4 docs/perf/screenshots.
- `docs/platform/dashboard.md` still documents pre-unification flags/registers
  and now also the old `/ws/telemetry` + `/ws/events` endpoints — refresh
  in the Phase 4 docs pass.

## 17. PROGRESS LOG (2026-09-25 — Phase 3 slice: budget panel + Evidence adapters)

### Shipped
- Budget panel (§4.5): `BudgetData`/`adapt_budget` in `ui/adapters.py`
  (burn-down from `costs`, throughput as `3600/mean_walltime`, maturation
  counts, `cost_breakdown` rows), `BudgetPanel` in
  `ui/components/budget_panel.py`, registered as a Monitor tab
  (`adapter_key="budget"`); generic `_push_tab_data` needed no changes.
- Evidence view (§4.6): `EvidenceData`/`adapt_evidence` (beliefs with latest
  revision probability/status, experiments, decisions) reading
  `<root>/ledger.sqlite` (fallback `ceec.sqlite3`) over a read-only
  `mode=ro` SQLite URI — never creates or writes (Invariant 1); missing
  ledger → empty data with `empty_reason`, never an error. The
  `_EvidencePanel` stub in `ui/dashboard.py` is deleted; the view now uses
  `EvidencePanel` with `adapter_key="evidence"`.
- Stories: `ui/stories/budget.py` + `ui/stories/evidence.py`, registered in
  gallery `_ensure_registered` (now 5 stories).
- Tests: `tests/unit/test_budget_evidence.py` (budget content on the
  synthetic root, missing-ledger honesty, seeded-ledger round-trip via raw
  `sqlite3` DDL matching the CEEC schema); the generic adapter purity lock
  auto-covers both new `ADAPTERS` entries.
- Verified: 79 passed (`test_budget_evidence` + `test_adapters` +
  `test_dashboard_render` + `test_dashboard_state`), 9 passed
  (`test_dashboard_interactions`); new modules `ruff check` + `pyright`
  clean; remaining `ruff check` findings on `dashboard.py` are the
  documented pre-existing idioms.

### Discovered while working
- `FunctionAdapter` wraps `(snapshot, root)` fns, so the evidence adapter
  keeps the standard signature while reading the ledger off `root` — same
  pattern as existing adapters that reuse `live_atlas` loaders over `root`.
- CEEC belief status lives only in `belief_revisions` (latest by
  `created_at`); the adapter resolves it with a max-`created_at` pass.
- `DataAdapter` docstring says "pure functions — no I/O", but existing
  adapters already read `root` via loaders; the docstring overstates the
  invariant (adapters are deterministic-in-`root`, not I/O-free).

### New improvement opportunities
- Calibration curves (4.6 remainder): `calibration_records` table is
  unread by `adapt_evidence` — add a `CalibrationRow` + sparkline when the
  Evidence view needs it.
- `next-in-plan` (4.6): surface `decisions.candidate_experiments` top pick
  or open `experiments_by_status('pre-registered')` in the Evidence view.
- Cell forensics drawer (4.1) is the natural next slice: reuse
  `BeliefRow`-style row dataclasses + the read-only ledger pattern for the
  defect stacktrace/log excerpt, with daemon-gated action buttons.

### Notes for remaining work
- Next slices: forensics drawer (4.1) → Atlas filters (4.2, gives
  `ui/state.py` signals their documented job) → parallel coordinates (4.3)
  → scrubber (4.4); then Phase 4 docs/perf/screenshots.
- `docs/platform/dashboard.md` refresh (Phase 4) now also owes: Budget tab,
  Evidence view, `/ws/stream` envelope, density flag.
