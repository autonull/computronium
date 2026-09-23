# GAME.todo3.md — Close-out: locks, honesty gaps, hygiene, human gates (TODO-UX3 "Ridgeline")

**Status:** Code complete T1–T7 (two commits) + H3 recorded. Human remainder: H1 manual keyboard crawl, H2 study-or-waiver.
**Scope:** `computronium/ui/`, `computronium/visualization/live_atlas.py` + `atlas.py`, `computronium/autoscientist/broad_map.py` (cell schema), dashboard tests/docs.
**Predecessors:** GAME.todo.md (M0–M3 code complete; one listed lock missing, human tasks pending) → GAME.todo2.md (X/A/B/C/D code complete; triage notes open).
**Out of scope (user directive 2026-09-23):** GAME.md is ignored — its Rev2 components (ledger console, role portal, WASM playground, Lessons view) and its §12/§13 acceptance numbers are not tracked here. No new panels, no new measurement paths, no XP/points/streaks (prohibition carries over).
**Verification posture:** L4 (property/sampled numerical) per repo taxonomy; behavioral checks with generous tolerances only — no pixel baselines.
**Test philosophy (carries over):** targeted tier only per change; never the full suite per commit.

## 1. Work items

| ID | Item | Acceptance | Size |
|----|------|------------|------|
| **T1** | **UX-L11 probe-hygiene lock** — `tests/property/test_ux_l11_probe_hygiene.py` (listed in GAME.todo.md §6, never written) proving probe batches never touch production training data; `probe_analytics.py` user copy already cites it | ✅ **Done Session A** — hygiene made structural (`ProbeBatch.__post_init__` rejects `forked_copy=False`, so the existing copy claim is now enforced, not asserted); 4-test lock green | S |
| **T2** | **`pareto_top` missing-column path fails loudly** (`atlas.py`) — today it logs a warning and returns the *unfiltered* df, rendering a fake "front" | ✅ **Done Session A** — raises `ValueError` naming the missing objectives + available columns; all shipped presets stay green (verified: L1/L15, smoke, budgets) | S |
| **T3** | **Preset coverage for front-history/strip** — `_CellRow` lacks `settle_horizon` / `stability_plasticity_ratio` / `credit_efficiency`, so stability/credit presets silently return unfiltered fronts (same T2 path) | ✅ **Done Session A** — the three columns now flow KB → `_CellRow`/`AtlasRow` loaders → `front_history_rows` df; UX-L1 extended to 8 presets (added `STABILITY_PLASTICITY_RATIO`, `CREDIT_EFFICIENCY_FULL`); fixtures carry varying values | S |
| **T4** | **Unify the two `build_dashboard`s** — legacy `live_atlas.build_dashboard` vs CLI `ui.dashboard.build_dashboard`; smoke test pins the legacy one | ✅ **Done Session A** — legacy page **deleted** (−665 lines incl. 18 page-only helpers); smoke test retargeted to `ui.dashboard.build_dashboard` (proven headless-direct) in the same commit | S |
| **T5** | **Perf numbers reconciled** — D1 acceptance said p95 render <100 ms but `render_snapshot` median measures 116 ms; gate is 3 s and green | ✅ **Done Session B — decision:** tighten `SNAPSHOT_BUDGET_S` 3.0 → 0.5 s (re-measured 124 ms @5k warm 2026-09-23; 4× headroom, still regression-sensitive) **and** amend D1 to the measured regime (snapshot <500 ms; DiscoveryMap adapter ≤100 ms stays the tight per-panel gate at 47.5 ms). D1 row + todo2 budget notes updated | S |
| **T6** | **Hygiene batch (Register C, one commit)** — dead `PANELS`/`LAB_ONLY_PANELS`/`_panel_label` lists; dashboard `PLW0717`; `live_atlas.py` noqa-style + 4 pre-existing pyright errors; readability-debt disposition (allowlist vs informational); `kb_load_cached` FIFO only if >16 roots ever matters (else wontfix note); UMAP tiny-n pin only if it gates a test | ✅ **Done Session B** — dead lists already gone (no-op); PLW0717 fixed via `_apply_atlas_result`/`_record_telemetry` extraction; noqa→`ruff: ignore[blind-except]` ×2; `_toast_for_alert` double-`message` TypeError fixed (match/case); readability = informational (doc overclaim corrected); FIFO/UMAP wontfix-noted below; ruff+pyright clean on touched files | M |
| **T7** | **Thin lab adapters disposition** — mutations/veto_log/genome/probe/stagnation return typed empty data; sources (Auto-Evolve event logs) aren't in `DashboardSnapshot` | ✅ **Done Session B — document disposition:** no Auto-Evolve event-log producer exists anywhere in the repo, so extending `render_snapshot` would invent a measurement path (prohibited) — each of the five adapters now carries an intentionally-empty-with-reason docstring naming the missing producer; `adapt_stagnation_dashboard` already consumes snapshot diversity/alerts | M |
| **H1** | **Human: final a11y cert** — axe against live dashboard + manual keyboard crawl per `ui/a11y/audit.py` checklist (C4 automation de-risks, does not replace) | **Half-green 2026-09-23:** axe re-verified 0 critical/serious both registers + tokens/render/interactions green (17 passed) after Sessions A+B; remainder is human — run the interactive `TestA11yKeyboardCrawl` against `comp dashboard` and record cert or CEEC-tracked waiver | calendar |
| **H2** | **Human: usability study or waiver** — SUS / time-to-first-insight per M3 exit rules | **Open, human-only:** no study artifacts and no waiver exist in the repo (only plan mentions) — needs a human study run or a recorded waiver; nothing automatable here | calendar |
| **H3** | **Maintainer decisions (not code)** — D5 figure re-pin (deliberate demo re-run vs accept drift); structlog/OTel ever-or-never (D1 stdlib deviation stands until ruled); 4 pre-existing property failures → route to owning tracks, not this plan | ✅ **Recorded 2026-09-23:** (1) D5 re-pin declined — accept drift, environmental not product (see todo2 D5 row); (2) structlog/OTel NEVER — stdlib `/metrics` shipped twice over, deferral documented in `ui/metrics.py`, revisit only on multi-process need; (3) known Tier-3 property backlog (TODO18 clusters) routes to owning tracks, never re-derived here | — |

## 2. Session plan

1. **Session A — integrity (≈1 session): T1 → T2 → T3 → T4.** ✅ **Complete 2026-09-23** — one commit; targeted tests: UX-L1 (8 presets)/L11/L12/L15, dashboard smoke, liveness, budgets (38 passed).
2. **Session B — close-out (≈1 session): T5 → T6 → T7.** ✅ **Complete 2026-09-23** — perf decision recorded (T5), hygiene batch green (T6), adapter disposition documented (T7); one commit.
3. **Human track (parallel, calendar-gated): H1 → H2 → H3.** H3 decisions unblock nothing in A/B; do not hold code sessions for them.
4. Fix the stale GAME.todo2.md §6 line ("C6 remaining" — C6 is green) inside Session A. ✅ **Done** — both §6 spots + the two T4 prescription lines updated.
5. On Session B green: mark todo3 complete, commit per phase as usual.

## 4. Session A retro — improvement opportunities & clarifiers for Session B

- **`_drain` survived T4 by test, not by grep.** The tested WS helper `live_atlas._drain` sat between two deleted page functions; the first deletion broke `test_telemetry_drain_extracts_loss` and it was restored verbatim. Lesson: for large deletions, enumerate *test imports* of the module first, not just production callers.
- **Duplicate dashboard fixtures** (`tests/ui/fixture.py::seed_campaign_root` vs `test_dashboard_smoke._seed_fixture`) must be edited in lockstep — the T3 metric additions touched both. Dedup (smoke imports the shared fixture) is a T6-hygiene candidate.
- **UX-L1 fixture contract is now load-bearing in a new way:** the strip renders top-3, so every L1 preset's fixture front must have ≤3 cells. T3 set `credit_efficiency=(0.2, 0.35, 0.65, 0.3)` (non-monotonic) so cell 3 is dominated on the full-credit preset. Any future preset/fixture change must re-check front sizes, not just column presence.
- **Promotion-path objective names don't match `_CellRow` fields** (`walltime_s` vs `walltime`, `param_count` vs `param_budget` → silent `getattr(..., 0.0)` ties in `_promotion_candidates`/`_deep_tier_candidates`). Pre-existing, out of Session A scope — candidate for Session B or the owning track.
- **`_CellRow.settle_steps_used` is likely always 0** (campaign KB metrics carry `settle_horizon`, not `settle_steps_used`); `settle_horizon` now reads `settle_horizon` with fallback. Flag for the owning track to confirm/remove.
- **Pyright delta:** `live_atlas.py` 4 → 3 errors (one died with the legacy page); `broad_map.py` promotion-dict errors are pre-existing. Both ride the T6 hygiene pass, not Session A.
- **T5 head start:** `render_snapshot` median 116 ms vs the D1 "p95 <100 ms" claim stands as the Session B decision; `SNAPSHOT_BUDGET_S`/budget-test constants live in `tests/perf/test_budgets.py` (green today).

## 5. Session B retro — one-line dispositions & notes for the human track

- **T6 wontfix (FIFO):** `kb_load_cached` clear-on-full stays — the 16-entry keyspace (path × mtime × size × family) only exhausts past 16 live roots; multi-root dashboard holds ≤ a handful. Revisit if root counts ever approach it.
- **T6 wontfix (UMAP tiny-n):** `atlas.embed` already scales perplexity below the 30-sample default and all dashboard tests pin the small-n path green — no extra pin.
- **T6 wontfix (`promote_candidates` complex-structure 12>10):** pre-existing, function untouched by this plan; rides Register C, not todo3.
- **T6 no-op:** dead `PANELS`/`LAB_ONLY_PANELS`/`_panel_label` lists were already removed before this plan — nothing to delete.
- **T6 real bug found:** `_toast_for_alert` passed `message` twice to `ui.notify` (guaranteed TypeError on the first alert toast); folded title+body into one message via match/case.
- **Readability disposition = informational:** FK heuristic scores short technical labels ("Continuous diffusion" → 20.6), so an allowlist would enshrine ~147 noise entries; the checker stays unit-tested, the script keeps auditing to JSON, and the dashboard doc no longer claims a ≤8 gate.
- **T7 note for Auto-Evolve owners:** when an event-log producer lands, the five documented adapters are the consumer surface — feed them via `DashboardSnapshot` extension (preferred), never per-adapter loaders.
- **H3 input (maintainer one-liners, ready to record):** ✅ recorded in the H3 row 2026-09-23 — D5 declined, structlog/OTel NEVER, Tier-3 backlog to owning tracks.
- **Completeness sweep 2026-09-23:** no code references the deleted legacy builder (only historical plan rows); docs `PANELS` hits are architecture-diagram labels, not the dead constant; GAME.todo.md UX-L11 row now points at a real test file; H1 automated half re-verified green post-change (axe + tokens + render + interactions).

## 3. Notes for implementers (carried, not re-derived)

- `render_snapshot` owns artifact schemas; adapters consume `DashboardSnapshot`, never re-query (see todo2 §5).
- `kb_load_cached` keys stay namespaced per loader family (`("cells", …)` vs `("measured", …)`).
- NiceGUI Screen mechanics: `@ui.page` inside the test, `main_file = ""`, 30 s source poller past the 4 s implicit wait, `screen.allowed_js_errors` for external teardown noise only.
- Never `uv add` a package shipping top-level `tests/` (shadows repo collection); always `uv run pyright` (bare binary reports phantom imports).
- `pareto_top` coordinate values are not locked — only front *membership* is (UX-L1).

*End of GAME.todo3.md — two code sessions + human track to certified done.*
