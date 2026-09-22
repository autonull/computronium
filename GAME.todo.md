# GAME.todo.md — Development Plan: Inclusive Gamified Dashboard (TODO-UX1 "Basecamp")

**Status:** Draft for implementation  
**Scope:** `comp dashboard` / `comp daemon` UI surface  
**Alignment:** Synergized from GAME.md (both specs) + README.md codebase reality + AUTOTILE.md (Auto-Evolve) preview handling  
**Verification posture:** UI-layer claims at L4/L5 per repo taxonomy; deterministic-replay and readability locks as property tests.

---

## 0. Executive Summary

| Spec Section | Codebase Reality | Gap | Priority |
|--------------|------------------|-----|----------|
| **Glossary service + `ui/glossary.json`** | Not started | Full build | M0 (P0) |
| **Two-register mode toggle (Explorer ⇄ Lab)** | Dashboard exists, single register | Mode scaffold + string service wiring | M0 (P0) |
| **Plain-language component refactor** | Panels exist with expert copy | Copy migration, narrations, empty states, units | M1 (P0) |
| **Recognition layer (badges, quests, records, fog-of-war)** | Event stream exists, no gamification | Projector, SQLite, replay, UI chrome | M2 (P0) |
| **Accessibility (WCAG 2.2 AA)** | Baseline unknown | Audit + fixes | M0–M3 (P0) |
| **Auto-Evolve (Preview shelf)** | Proposed, not implemented | Preview shelf component only | M3 (P1) |
| **Auto-Evolve Instrumentation** | `computronium-stability`, `StabilityMonitor`, `comp scientist phylogeny` exist | Constitution health, genealogy, adaptation probes, stagnation, mutation explorer | M1–M2 (P1) |

**Key principle from GAME.md:** "The dashboard is a tool. Participation is the same tool, made accessible. The game is the instrument, translated — never a parallel system built beside it."  
**No XP. No points.** Recognition = verifiable badges (ledger-linked), quests (campaign-mapped), records (personal bests). Playing the game — measuring, repairing, reproducing, recording — *is* the reward.  
**Bijection Rule:** Every public element must correspond to a real artifact/state/action. No invented game state.

---

## 1. Codebase Mapping (Reality Check)

### 1.1 Existing Dashboard Components (from `comp dashboard` / `comp daemon`)

| GAME.md Panel | Current Implementation | Location (inferred) |
|---------------|------------------------|---------------------|
| Discovery Map (islands/voids UMAP) | `AtlasMap`, `ParallelCoordinates` | `computronium/visualization/` |
| Trade-offs (Pareto strip + selector) | `ParetoStrip` with objective-pair selector | `computronium/visualization/` |
| Repair Bench (defect funnel) | `DefectFunnel` viewer | `computronium/visualization/` |
| Health Gauge | `HealthGauge` with divergence count | `computronium/visualization/` |
| Activity Feed (burst-log ticker) | `BurstLogTicker`, `EventStream` | `computronium/visualization/` |
| Field Reports (alert toasts) | `AlertToasts` | `computronium/visualization/` |

### 1.2 Existing Data Sources (Read-Only)

| Source | Path | Used By |
|--------|------|---------|
| Campaign roots (cells, fronts, maturity) | `artifacts/broad_map/` | All panels |
| Runtime defects | `runtime_defects.jsonl` | Repair Bench |
| CEEC ledger | `ceec.sqlite3` + campaign ledgers | Record Book, gamification projector |
| Registry (64 specs) | `computronium/ontology/` | Workshop, Map |
| Live WebSocket events | `comp continuous` / `comp daemon` | Activity Feed, Field Reports |

### 1.3 CLI Surface (from README.md)

```bash
comp dashboard --root R --port 8088 [--ui-mode explorer|lab|auto] [--gamify on|off] [--ui-actions on|off] [--rebuild-ui-state]
comp daemon    ... same flags ... --port 8940
```

**Defaults per GAME.md:** `--ui-mode auto`, `--gamify on`, `--ui-actions off`

---

## 2. Phased Delivery Plan (Synergized from GAME.md §13 + README constraints)

### M0 — Foundations (≈2 weeks) — **P0 BLOCKERS**

| ID | Task | Acceptance | Owner |
|----|------|------------|-------|
| **M0.1** | Create `ui/glossary.json` from GAME.md §5.3 master term table (both registers) | File exists, all 29+ terms mapped, loads without error | |
| **M0.2** | Build `GlossaryService` (string service): lookup by key, register-aware, i18n-ready | `service.get("pareto_optimal", register="explorer") → "Best trade-off"` | |
| **M0.3** | Design tokens: colorblind-safe palettes (viridis/cividis), type scale, icon set with shape redundancy, focus styles | Token file + Storybook/visual regression baseline | |
| **M0.4** | Mode toggle scaffold: Explorer/Lab switch, persists to localStorage, wires GlossaryService into all existing panels (copy behind flag) | Toggle works, no reload, all panel text routes through service | |
| **M0.5** | A11y baseline audit of current dashboard (axe-core + manual keyboard crawl) | Report with 0 critical/serious or triaged fixes | |
| **M0.6** | Fix critical keyboard/contrast issues from audit | `axe-core` clean on shell routes | |
| **M0.7** | Verify harnesses: UX-L3 (glossary totality), UX-L5 (a11y) green on scaffold | CI gates pass | |

**Exit M0:** UX-L3/L5 harnesses green; mode toggle ships dark; glossary is single source of truth.

---

### M1 — Plain-Language Component Refactor (≈3 weeks) — **P0 CORE**

| ID | Task | Acceptance | Owner |
|----|------|------------|-------|
| **M1.1** | Migrate all panel copy through GlossaryService in both registers (Explorer/Lab) | No hardcoded strings in panel components; `grep -r "Pareto\|quarantine\|rho\|psi" ui/` returns 0 | |
| **M1.2** | Refactor panel names & headers per GAME.md §6 IA: Map, Trade-offs, Repair Bench, Health, Progress, Glossary | Left rail matches spec; deep links carry `?mode=` | |
| **M1.3** | Add "What am I looking at?" button to each panel → contextual explainer (plain → why → expert → docs link) | Button exists, drawer renders, links resolve | |
| **M1.4** | Discovery Map upgrades: fog-of-war overlay from KB coverage, region labels (auto-generated from dominant axes), specimen markers with shape encoding (never color-only), hover card (plain summary), sortable table alternative | Fog derivable from KB only; grayscale screenshot preserves state distinction; table = 100% map info | |
| **M1.5** | Trade-offs Panel: selector renamed "Compare two goals", plain semantics line permanent, reference anchors (ruler ratios as "× reference"), guided reading narration on hover | UX-L1 lock: front membership byte-identical to `pareto_top(df, objectives)` | |
| **M1.6** | Repair Bench: reframe statuses (Arrived → Diagnosed → Fixed → Back in service), defect cards with copy-pasteable `unquarantine` CLI, gate rejections vs. crashes visually distinct | Every card has [copy] button; structural voids never labeled bugs | |
| **M1.7** | Health Panel: three plain tiles (Running smoothly / Needs attention / Unstable runs), divergence as "N runs blew up", session vitals with relative time | No raw timestamps without relative | |
| **M1.8** | Activity Feed: pausable, reverse-chron, plain lines, expandable to raw, `aria-live="polite"` rate-limited ≤1/2s, batch summary mode | Screen reader announces batch summaries | |
| **M1.9** | Field Reports: retype toasts as field reports (icon + sentence + deep link), breakthrough alerts scoped ("New best correctness among similar size"), batched tray with unread badge | No bare "state of the art" language | |
| **M1.10** | Reduced-motion support: `prefers-reduced-motion` disables fog animation, ticker scroll, toast slides; static equivalents | UX-L6 lock: grayscale marker redundancy | |
| **M1.11** | Readability lint: all Explorer strings ≤ Flesch–Kincaid grade 8 (allowlist for proper nouns/equations), sentence-length histogram | UX-L4 lock passes in CI | |
| **M1.12** | **Constitution Health Panel** (AUTOTILE.md §4): 6 invariants status — Causality (DAG), Passivity, Lyapunov Bound, Resource Ceiling, Protocol Conformance, Recursion Invariant; plain + expert registers | Metrics match `StabilityMonitor` byte-identically (UX-L9); Explorer: "Stability check passed" / Lab: ρ(J_F)=0.847 | |
| **M1.13** | **Lineage Viewer** (AUTOTILE.md §6, §8.6): visualize Ω phylogeny from `comp scientist phylogeny` — nodes=genomes, edges=mutations, Tier color, slope tooltips | Reconstructs identical graph from event log replay (UX-L10) | |
| **M1.14** | **Episode Timeline** (AUTOTILE.md §3.1): visualize episode boundaries, consolidation events, genome changes per episode | Campaign event log; sleep/waking separation visible | |

**Exit M1:** UX-L1/L4/L6/L9/L10 locks green; newcomer study round 1 ≥70% time-to-first-insight target.

---

### M2 — Recognition Layer + Instrumentation (≈3 weeks) — **P0 ENGAGEMENT + P1 INSTRUMENT**

**No XP. No points. No streaks.** Playing the game — measuring, repairing, reproducing, recording — *is* the reward. Recognition = **verifiable badges** (ledger-linked), **quests** (campaign-mapped checklists), **records** (personal bests on goals), **fog-of-war** (KB coverage). Anti-Goodhart by design: nothing to optimize but evidence quality.

| ID | Task | Acceptance | Owner |
|----|------|------------|-------|
| **M2.1** | Event projector: pure function `fold(event_log) → recognition_state` emitting `recognition.badge_awarded`, `recognition.quest_progress`, `recognition.record_set`, `recognition.region_named` | Deterministic: identical state across shuffle-safe replays; idempotent on duplicates (UX-L2) | |
| **M2.2** | `ui_state.sqlite` sidecar (append-only, rebuildable via `comp dashboard --rebuild-ui-state`) | Replay from events reconstructs identical badges/quests/records | |
| **M2.3** | **Badges** (8, ledger-linked per GAME.md §8.3): First Steps, Mapmaker, Double-Checker, Gold Standard, Honest Broker, Repair Crew, Steady Hand, Cartographer, Open Book | Each badge resolves to CEEC/KB record with "see evidence" link | |
| **M2.4** | **Quests** (6, opt-in per §8.4): Chart 100 regions, Double-check 3 candidates, Send to careful re-check, Clear repair bench, Compare goals, Forecast & check | Quest completion copy states what was learned/verified | |
| **M2.5** | **Records** (personal bests): breakthrough alerts on any objective improvement, scoped ("New best correctness among similar size") | Derived from Pareto front + CEEC gates; no XP | |
| **M2.6** | Fog-of-war on Map: coverage % from KB, "You've charted X% of planned regions" | Derivable from KB alone (no new measurement) | |
| **M2.7** | Field Reports tray + Progress panel (left rail) with quests/badges/records | Lab mode hides recognition chrome by default | |
| **M2.8** | Kill switches: `--gamify off` / `COMPUTRONIUM_NO_GAMIFY=1`, Lab mode hides chrome | Recognition visibility never changes measurement/promotion/claim logic (UX-L7) | |
| **M2.9** | Integrity locks: UX-L2 (replay property test via Hypothesis), UX-L7 (static import lock: projector zero imports from campaign/gate mutation paths) | Both locks green in CI | |
| **M2.10** | Anti-Goodhart audit: quarterly correlation (badge/quest actions vs. CEEC gate-rejection rate) | Report generator exists, runnable | |
| **M2.11** | **Probe Analytics Panel** (AUTOTILE.md §3.2): show probe batches, current vs proposed slope, acceptance/rejection, forked-copy hygiene | Probe batches never touch production training data (UX-L11) | |
| **M2.12** | **Stagnation Dashboard** (AUTOTILE.md §2.4): per-campaign stagnation status (WindowedMean/EMA/StatTest/VetoRate), detector config, history | Campaign event log, `SystemContext` | |
| **M2.13** | **Genome Health Tracker** (AUTOTILE.md §5.4): |Ω| vs fitness, ontological cancer risk (GenomeSizePenalty λ), Resource Ceiling headroom | Campaign event log, `ResourceUsage` | |
| **M2.14** | **Mutation Explorer** (AUTOTILE.md §2.3): from current Ω, show valid `DuplicateAndPerturb`, `SpliceOperator`, `CoordinateSwap` proposals with Constitution pre-check | Registry, `SystemConfig.validate()`, `StabilityMonitor` fast-proxy | |
| **M2.15** | **Veto Log** (AUTOTILE.md §3.5): vetoed mutations with reason (Lyapunov fast-proxy fail, Passivity fail, Protocol conformance fail), veto rate trend | Campaign event log (veto events) | |

**Exit M2:** Replay property lock green on 100k synthetic events; opt-in pilot with 2 internal teams; UX-L11 green. No XP anywhere in the codebase.

---

### M3 — Onboarding, Teams, i18n Hooks, Auto-Evolve Preview (≈2 weeks) — **P1 POLISH**

| ID | Task | Acceptance | Owner |
|----|------|------------|-------|
| **M3.1** | Guided tour (3 steps, skippable, resumable), comfort quiz (3 questions, sets default mode/tour depth only) | Tour completes, quiz only affects defaults, never restricts features | |
| **M3.2** | Region naming: propose plain names for map regions, metadata-only, versioned, revertible | Names stored as presentation metadata, never in measurement records | |
| **M3.3** | Cooperative team wall (opt-in per team), no individual leaderboards | Team progress = cooperative totals only | |
| **M3.4** | i18n string freeze + extraction audit: all simple-register strings in resource files, no concatenation | `i18n` CLI extracts 100% of Explorer strings | |
| **M3.5** | Final a11y certification (axe + manual), SUS study round 2, docs refresh (`docs/platform/`, gallery manifests) | All §12 targets met or explicitly waived with CEEC-tracked rationale | |
| **M3.6** | **Preview Shelf component** (Auto-Evolve per GAME.md §5.9 / §11): clearly labeled shelf for unimplemented proposals, each entry states proposal, status "Proposed — not implemented", falsification plan in plain language | No live UI, no metrics, no creatures; Auto-Evolve entry present with its §8 kill criterion | |
| **M3.7** | Gallery/demo lock compatibility: existing `comp gallery` artifacts remain renderable | UX-L8 regression test passes | |

**Exit M3:** All §12 success metrics met or waived; Preview Shelf ships with Auto-Evolve entry.

---

## 3. Cross-Cutting Concerns (Continuous)

| Concern | Implementation | Lock |
|---------|----------------|------|
| **Deterministic replay** | Projector is pure fold; `comp dashboard --rebuild-ui-state` replays from event log | UX-L2 (Hypothesis property test) |
| **Glossary totality** | Term blocklist scan: no unregistered technical term in Explorer copy | UX-L3 (lint lock) |
| **Readability** | Flesch–Kincaid ≤ grade 8 + sentence length histogram on all Explorer strings | UX-L4 (CI lint) |
| **A11y** | axe-core 0 critical/serious; keyboard crawl reaches all interactive elements | UX-L5 (CI + manual per milestone) |
| **Marker redundancy** | Grayscale screenshot diff preserves state distinguishability (shape/label) | UX-L6 (snapshot test) |
| **Integrity** | Projector has zero imports from campaign/gate mutation paths | UX-L7 (static import lock) |
| **Gallery compatibility** | `comp gallery` manifests unchanged | UX-L8 (regression test) |

---

## 4. Auto-Evolve Handling (Per GAME.md §5.9, §11 & AUTOTILE.md)

**Terminology:** "AUTOTILE" = **Auto-Evolve** — the constitutional self-modification engine (AUTOTILE.md). It is an *evolutionary process*: asexual mutation (neutral birth) + slope-based selection + immutable Constitution. Not a game. Not a simulation. A self-modifying learning system governed by physics (stability, passivity, resources).

**Status:** Proposed, not implemented.  
**Dashboard treatment:** Preview Shelf only (M3.6).  

| Requirement | Implementation |
|-------------|----------------|
| No homepage presence | Preview Shelf only, not in main nav |
| No leaderboard/metrics | Static card with proposal summary |
| Falsification plan visible | Render AUTOTILE.md §8.5 kill criterion in plain language |
| Status label | "Proposed — not implemented" badge |
| If/when implemented | Joins as `manifest.kind: auto_evolve` campaign, inherits all views/gates/receipts unchanged |

**AUTOTILE.md amendments to track (from end of file):**
- Probe hygiene/forked copies (amendment 1)
- Cross-family slope comparability (amendment 2)
- Rollback/probation path (amendment 3)
- Oracle-rescue pilot before autonomous runs (amendment 4)
- Prior-art gate logged in DECISIONS.md (amendment 5)
- Constitution calibration scope audit (amendment 6)
- Ω in manifest/lineage for reproducibility (amendment 7)

---

## 4b. Auto-Evolve Instrumentation (Observability, Not Gamification)

**Principle:** Per GAME.md's "Instrument first" and Bijection Rule — these expose *real system state* for research/debugging. All correspond to existing artifacts: `computronium-stability` guard, `StabilityMonitor`, `comp scientist phylogeny`, campaign event logs. **No new write paths.**

| Auto-Evolve Concept | Dashboard Instrumentation | Data Source | Phase |
|---------------------|---------------------------|-------------|-------|
| **§4 Immutable Constitution** (6 invariants) | **Constitution Health**: real-time status of Causality (DAG), Passivity (Δℰ≤ℰ_in), Lyapunov Bound (ρ(J_F)≤τ), Resource Ceiling (||Z||+|Ω|), Protocol Conformance, Recursion Invariant | `StabilityMonitor` checks, `computronium-stability` guard | M1 |
| **§6 Genealogy/Phylogeny** (`comp scientist phylogeny`) | **Lineage Viewer**: visualize Ω evolution — nodes=genomes, edges=mutations, color=Tier (1=structural, 2=algorithmic, 3=meta), tooltip=slope/probe result | CEEC ledger, campaign event log | M1 |
| **§3.2 Adaptation Probes** (slope-based selection) | **Probe Analytics**: show probe batches, current vs proposed slope, acceptance/rejection, forked-copy hygiene | Campaign event log (probe events) | M2 |
| **§2.4 Stagnation Detectors** (4 protocols) | **Stagnation Dashboard**: per-campaign stagnation status (WindowedMean/EMA/StatTest/VetoRate), detector config, history | Campaign event log, `SystemContext` | M2 |
| **§5.4 Resource Ceiling / Genome Size** | **Genome Health**: |Ω| vs fitness, ontological cancer risk (GenomeSizePenalty λ), Resource Ceiling headroom | Campaign event log, `ResourceUsage` | M2 |
| **§2.3 Mutation Operators** (Tier 1/2) | **Mutation Explorer**: from current Ω, show valid `DuplicateAndPerturb`, `SpliceOperator`, `CoordinateSwap` proposals with Constitution pre-check | Registry, `SystemConfig.validate()`, `StabilityMonitor` fast-proxy | M2 |
| **§3.5 Constitution Vetoes** | **Veto Log**: vetoed mutations with reason (Lyapunov fast-proxy fail, Passivity fail, Protocol conformance fail), veto rate trend | Campaign event log (veto events) | M2 |
| **§3.1 Sleep/Waking Boundaries** | **Episode Timeline**: visualize episode boundaries, consolidation events, genome changes per episode | Campaign event log | M1 |

**Implementation Notes:**
- All read-only — consume existing `StabilityMonitor`, `computronium-stability`, CEEC ledger, campaign events
- No new write paths — aligns with GAME.md "read-only by default"
- Explorer mode: plain-language summaries ("Stability check passed", "Recipe grew 3 nodes")
- Lab mode: raw metrics (ρ(J_F)=0.847, τ=1.029, |Ω|=47, slope=0.023)
- Reuses `GlossaryService` for terms: "Lyapunov bound" → "Stability margin", "genome" → "recipe lineage", "mutation" → "recipe change"

**Verification Locks:**
- UX-L9: Constitution panel metrics match `StabilityMonitor` output byte-identically (L4 equivalence)
- UX-L10: Lineage viewer reconstructs identical graph from event log replay (L4 property)
- UX-L11: Probe analytics show forked-copy hygiene (probe batches never touch production training data)

---

## 4c. What Auto-Evolve Observability Enables (Summary)

With the 8 instrumentation panels (Constitution Health, Lineage Viewer, Probe Analytics, Stagnation Dashboard, Genome Health, Mutation Explorer, Veto Log, Episode Timeline), the dashboard becomes a **live observability suite for Auto-Evolve** — exposing the actual evolutionary engine, not a simulation.

**Domain-agnostic.** The Auto-Evolve engine is not language-model-specific. The same machinery grows/adapts systems for:
- **Language** (Envelope LM: growing depth under memory ceiling)
- **Vision** (tile-based architectures, spatial symmetries → weight sharing)
- **RL** (non-stationarity → adaptive credit axes, temporal symmetries → recurrence)
- **Any domain** where the 6-axis ontology applies — the task, Registry primitives, FitnessMetric, and resource envelope are inputs; the evolutionary engine (neutral birth + slope selection + Constitution) is the same.

| Capability | What You See | Why It Matters |
|------------|--------------|----------------|
| **Constitution Health** | 6 invariants in real time: DAG causality, passivity (Δℰ≤ℰ_in), Lyapunov bound (ρ(J_F)≤τ=1.029), resource ceiling, protocol conformance, recursion invariant | Proves the stability guard (`computronium-stability`) is active and calibrated; researchers verify safety boundaries live |
| **Lineage Viewer** | Phylogeny of Ω genomes: nodes=genomes, edges=mutations, colored by Tier (1=structural, 2=algorithmic, 3=meta), tooltips show adaptation probe slopes | Shows *which mutations survived selection* and *why* (slope evidence) — the genealogy of evolution |
| **Probe Analytics** | Forked-copy adaptation probes: current vs proposed slope, acceptance/rejection, budget K, statistical test result | Demonstrates slope-based selection (core insight): credit/optimizer swaps invisible to point eval, visible to slope |
| **Stagnation Dashboard** | Per-campaign detector status (WindowedMean/EMA/StatTest/VetoRate), config, history, veto rate trend | Shows the load-bearing gate: probes only fire when progress stalls; amortized overhead → zero in stable regimes |
| **Genome Health** | |Ω| vs fitness trajectory, ontological cancer risk (GenomeSizePenalty λ), resource ceiling headroom | Visualizes the resource ceiling invariant; selective pressure against unbounded growth |
| **Mutation Explorer** | From current Ω: valid `DuplicateAndPerturb` (new nodes/edges), `SpliceOperator` (swap Registry primitive), `CoordinateSwap` (axis change) — each with Constitution fast-proxy pre-check | Researchers see *what the system could try next* before it runs; `SystemConfig.validate()` + `StabilityMonitor` in action |
| **Veto Log** | Every vetoed mutation with reason: Lyapunov fast-proxy fail, passivity fail, protocol conformance fail, recursion invariant; veto rate trend | Audit trail of the Constitution at work; false-veto rate = first-class diagnostic (per amendment 6) |
| **Episode Timeline** | Sleep/waking boundaries: episode ticks, consolidation events, genome changes, probe batches per episode | Makes the evolutionary architecture visible: morphology only at boundaries, never mid-pass |

**For researchers:** This is the *instrument panel* for the evolutionary engine. You don't run it to "see what happens" — you watch Constitution Health, Lineage, and Probe Analytics to understand *why* it evolves (or falsifies), **in any domain**.

**For newcomers:** Explorer mode renders these as "Stability Check: Passed", "Recipe Family Tree", "Learning Speed Comparison", "Progress Monitor" — plain language, one gesture to expert view.

**All read-only. All existing artifacts. No new write paths. Bijection Rule satisfied.**

## 5. File/Module Structure (Target)

```
computronium/
├── ui/
│   ├── glossary.json              # M0.1 — single source of truth
│   ├── glossary_service.py        # M0.2 — register-aware string lookup
│   ├── mode_toggle.py             # M0.4 — Explorer/Lab persistence
│   ├── design_tokens.py           # M0.3 — palettes, type, icons, focus
│   ├── components/
│   │   ├── base_panel.py          # "What am I looking at?" mixin
│   │   ├── discovery_map.py       # M1.4 — fog, labels, shapes, table alt
│   │   ├── tradeoffs_panel.py     # M1.5 — selector, narration, refs
│   │   ├── repair_bench.py        # M1.6 — statuses, copy buttons
│   │   ├── health_panel.py        # M1.7 — plain tiles, relative time
│   │   ├── activity_feed.py       # M1.8 — pausable, aria-live, batch
│   │   ├── field_reports.py       # M1.9 — tray, scoped alerts
│   │   ├── progress_panel.py      # M2.7 — quests, badges, records
│   │   ├── preview_shelf.py       # M3.6 — Auto-Evolve entry
│   │   ├── glossary_drawer.py     # Persistent glossary access
│   │   ├── constitution_health.py # M1 — 6 invariants status (AUTOTILE.md §4)
│   │   ├── lineage_viewer.py      # M1 — Ω phylogeny (comp scientist phylogeny)
│   │   ├── probe_analytics.py     # M2 — adaptation probe slopes (AUTOTILE.md §3.2)
│   │   ├── stagnation_dashboard.py # M2 — stagnation detectors (AUTOTILE.md §2.4)
│   │   ├── genome_health.py       # M2 — |Ω| vs fitness, resource ceiling (AUTOTILE.md §5.4)
│   │   ├── mutation_explorer.py   # M2 — valid Tier 1/2 proposals (AUTOTILE.md §2.3)
│   │   ├── veto_log.py            # M2 — Constitution vetoes (AUTOTILE.md §3.5)
│   │   └── episode_timeline.py    # M1 — sleep/waking boundaries (AUTOTILE.md §3.1)
│   ├── recognition/
│   │   ├── projector.py           # M2.1 — pure fold(event_log)
│   │   ├── badges.py              # M2.3 — ledger-linked
│   │   ├── quests.py              # M2.4 — campaign-mapped
│   │   ├── records.py             # M2.5 — personal bests on objectives
│   │   ├── state_store.py         # M2.2 — ui_state.sqlite
│   │   └── integrity_locks.py     # M2.9 — UX-L2/L7 tests
│   ├── onboarding/
│   │   ├── tour.py                # M3.1 — guided, skippable
│   │   └── quiz.py                # M3.1 — comfort quiz
│   └── a11y/
│       ├── tokens.py              # M0.3 — contrast, motion, focus
│       └── audit.py               # M0.5/M3.5 — axe + keyboard crawl
```

---

## 6. Verification Locks (from GAME.md §11 + repo taxonomy)

| Lock | Property | Type | Implementation |
|------|----------|------|----------------|
| **UX-L1** | Pareto membership rendered == `pareto_top(df, objectives)` for all presets | L4 equivalence | `tests/property/test_ux_l1_pareto_equivalence.py` |
| **UX-L2** | Deterministic replay: `fold(event_log)` identical across shuffle-safe replays; idempotent on duplicates | L4 property (Hypothesis) | `tests/property/test_ux_l2_replay.py` |
| **UX-L3** | Glossary totality: every UI string key resolves in `glossary.json` both registers; no unregistered tech term in Explorer | L4 lint | `tests/lint/test_ux_l3_glossary_totality.py` |
| **UX-L4** | Readability: all Explorer strings ≤ FK grade 8; sentence-length histogram gate | CI lint | `ruff` rule + custom check in `scripts/lint_readability.py` |
| **UX-L5** | A11y: axe-core 0 critical/serious; keyboard crawl reaches all interactive | CI + manual | `tests/a11y/test_ux_l5_a11y.py` + manual checklist |
| **UX-L6** | Marker redundancy: grayscale screenshot diff preserves distinguishability | L4 snapshot | `tests/visual/test_ux_l6_marker_redundancy.py` |
| **UX-L7** | Integrity: projector zero imports from campaign/gate mutation paths | Static import | `tests/lint/test_ux_l7_import_lock.py` |
| **UX-L8** | Gallery compatibility: `comp gallery` artifacts renderable | Regression | `tests/integration/test_ux_l8_gallery_compat.py` |
| **UX-L9** | Constitution panel metrics match `StabilityMonitor` output byte-identically | L4 equivalence | `tests/property/test_ux_l9_constitution_equivalence.py` |
| **UX-L10** | Lineage viewer reconstructs identical graph from event log replay | L4 property (Hypothesis) | `tests/property/test_ux_l10_lineage_replay.py` |
| **UX-L11** | Probe analytics show forked-copy hygiene (probe batches never touch production training data) | L4 property | `tests/property/test_ux_l11_probe_hygiene.py` |

---

## 7. Risks & Mitigations (from GAME.md §14 + codebase reality)

| Risk | Mitigation |
|------|------------|
| Trivialization of science; metaphors mislead | Explorer copy reviewed against "does this change meaning?" rule; expert drawer one gesture away; study checks comprehension |
| Goodharting / gamification distorts research | §8.5 hard rules; rewards bound to epistemic quality; quarterly correlation audit vs. gate rejections |
| Performance regressions on large roots (50k cells) | Async projector, debounced UI (≤1 Hz), table fallbacks for heavy canvases, TTI ≤2s budget |
| A11y debt in canvas widgets | Text alternatives mandatory siblings (not enhancements); UX-L6 lock |
| Scope creep into campaign logic | UX-L7 import lock; spec non-goals enforced in review |
| Copy drift post-launch | Readability + glossary lint as CI gates; copy changes require glossary PR |
| Auto-Evolve confusion | Preview Shelf only; clear "Proposed — not implemented" label; falsification plan visible |

---

## 8. Open Questions (from GAME.md §15 + AUTOTILE.md)

| # | Question | Decision Needed By |
|---|----------|-------------------|
| 1 | Explorer mode: surface 6-axis recipe editor read-only ("why is this candidate built this way?") in v1 or defer? | M1 |
| 2 | Team features: cooperative-only forever, or revisit competitive leaderboards after quarterly audit? | M3 |
| 3 | Localization target language(s) for first translation pass; who owns plain-language review for non-English? | M3 |
| 4 | Does `comp gallery` adopt same glossary service in this effort, or fast-follow? | M0 |
| 5 | Auto-Evolve: probe hygiene (forked copies), cross-family slope comparability, rollback path — resolve before E-1 registration? | Post-M3 (separate track) |

---

## 9. Quickstart Commands (for implementers)

```bash
# Dev env smoke (required before any work)
uv run python -c "import optuna, scipy, torchvision, pytest"

# Run targeted tests for changed modules
uv run python -m pytest tests/<path> -k <signature> -q

# Format + lint changed files
uv run ruff format && uv run ruff check --fix

# Type check changed files (strict for new modules)
uv run pyright <changed_module>

# Full dashboard dev server
uv run comp dashboard --root artifacts/broad_map --port 8088 --ui-mode explorer --gamify on

# Rebuild UI state from event log (M2.2)
uv run comp dashboard --root artifacts/broad_map --rebuild-ui-state

# Gallery compatibility check (UX-L8)
uv run comp gallery --run
```

---

## 10. Sign-Off Checklist (Per Phase)

### M0 Exit
- [ ] `ui/glossary.json` seeded from §5.3, loads cleanly
- [ ] `GlossaryService` resolves all keys in both registers
- [ ] Design tokens defined + visual baseline
- [ ] Mode toggle persists, wires into all panels (behind flag)
- [ ] A11y baseline audit complete, critical issues fixed
- [ ] UX-L3, UX-L5 harnesses green

### M1 Exit
- [ ] All panel copy routes through GlossaryService (0 hardcoded strings)
- [ ] Panel names/headers match §6 IA
- [ ] "What am I looking at?" drawers on all panels
- [ ] Map: fog, labels, shapes, table alt all working
- [ ] Trade-offs: selector, narration, reference anchors working
- [ ] Repair Bench: statuses, copy buttons, crash vs. boundary distinction
- [ ] Health: plain tiles, relative time
- [ ] Activity Feed: pausable, aria-live, batch summaries
- [ ] Field Reports: tray, scoped breakthroughs
- [ ] Reduced-motion respected everywhere
- [ ] Readability lint (UX-L4) + marker redundancy (UX-L6) + Pareto equivalence (UX-L1) green
- [ ] Constitution Health: 6 invariants match `StabilityMonitor` (UX-L9)
- [ ] Lineage Viewer: reconstructs from event log replay (UX-L10)
- [ ] Episode Timeline: sleep/waking boundaries visible
- [ ] Newcomer study round 1 ≥70% target

### M2 Exit
- [ ] Event projector pure, deterministic replay (UX-L2 green on 100k events)
- [ ] `ui_state.sqlite` rebuildable via `--rebuild-ui-state`
- [ ] **8 badges** from §8.3 with evidence links (no XP)
- [ ] 6 quests from §8.4 opt-in, completion copy states learning
- [ ] Records: personal bests on objectives, scoped breakthrough alerts
- [ ] Fog-of-war from KB coverage
- [ ] Progress panel + field reports tray
- [ ] Kill switches work; Lab mode hides chrome
- [ ] UX-L7 import lock green
- [ ] Anti-Goodhart audit scaffolding runnable
- [ ] Opt-in pilot with 2 teams complete
- [ ] Probe Analytics: forked-copy hygiene verified (UX-L11)
- [ ] Stagnation Dashboard: 4 detector protocols visible
- [ ] Genome Health: |Ω| vs fitness, Resource Ceiling headroom
- [ ] Mutation Explorer: valid Tier 1/2 proposals with pre-check
- [ ] Veto Log: reasons + trend visible

### M3 Exit
- [ ] Guided tour + comfort quiz (skippable, non-restrictive)
- [ ] Region naming (metadata-only, versioned)
- [ ] Team wall (cooperative, opt-in)
- [ ] i18n extraction 100% on Explorer strings
- [ ] Final a11y cert + SUS study round 2
- [ ] Preview Shelf with Auto-Evolve entry (status + falsification plan)
- [ ] Gallery compatibility (UX-L8) green
- [ ] All §12 targets met or CEEC-tracked waivers recorded

---

## 11. Non-Goals (Explicit from GAME.md §2 + AUTOTILE.md)

- ❌ No new measurement, promotion, or claim logic
- ❌ No competitive leaderboards by default (opt-in team only, M3)
- ❌ No sound by default; no dark patterns, fake urgency
- ❌ No rewrite of daemon/lifecycle API; UI consumes existing WebSocket/events
- ❌ **No XP, no points, no streaks, no currencies** — playing the game is its own reward; recognition = badges + quests + records only
- ❌ Auto-Evolve: no live UI, no metrics, no creatures — Preview Shelf only
- ❌ Auto-Evolve: no open-field Tier 3 in v1 (fixed menu only per AUTOTILE.md §7.7)
- ❌ Auto-Evolve: no runtime code generation, no unverified primitives

---

*Generated from GAME.md (both specs) + README.md codebase mapping + AUTOTILE.md (Auto-Evolve) preview handling.  
This plan is the single source of truth for TODO-UX1 "Basecamp" implementation.*

---

## 12. Design Evaluation & Recommendations

### ✅ What Works (Keep)

| Aspect | Why It Works |
|--------|--------------|
| **Two-register system (Explorer/Lab)** | Serves P1–P5 personas without hard-gating; mode toggle is instant, persistent, never restricts |
| **Glossary as single source of truth** | Enables i18n, readability lint, term consistency; `ui/glossary.json` is data, not code |
| **Bijection Rule** | Gamification = pure presentation over existing events; no invented state; kills Goodhart risk |
| **Auto-Evolve as instrumentation (not game)** | Constitution Health, Lineage Viewer, Probe Analytics expose *real capabilities* for researchers — this is the strongest demo surface |
| **Deterministic replay locks (UX-L2, L9, L10, L11)** | Credibility with scientists; matches repo's L4/L5 verification culture |
| **A11y as P0 launch gate** | Not bolt-on; `prefers-reduced-motion`, shape redundancy, aria-live baked into component contracts |
| **Preview Shelf for unimplemented work** | Honest; falsification plan visible; no hype |

### ⚠️ Risks / Gaps (Fix Before Implementation)

| Risk | Severity | Fix |
|------|----------|-----|
| **M1/M2 scope too large** (14 + 15 tasks in 3w each) | High | **Ruthlessly prioritize:** M1 = core panels + Constitution Health + Episode Timeline only. Move Lineage Viewer, Probe Analytics, Stagnation Dashboard, Genome Health, Mutation Explorer, Veto Log to M2 or M3. |
| **Left-rail IA fragmentation** | Medium | **Unify by user intent:** Group as *Understand* (Map, Trade-offs, Constitution), *Diagnose* (Repair Bench, Health, Probe Analytics, Stagnation, Veto Log), *Explore* (Lineage, Genome, Episode Timeline), *Progress* (Quests, Badges, Records). One rail, not two parallel systems. |
| **Missing Workshop panel** (GAME.md §5.5) | High | Add **Workshop** to left rail: "Build your own" (DialComposer), "Try a known recipe" (RecipeCard), "Fix a crash" (links to Repair Bench), "Donate computer" (P2P toggle). This is the *doing* entry point for both audiences. |
| **6-axis recipe editor read-only** (Open Q #1) | Medium | **Defer to M2** as "Inspect Recipe" drawer on specimen cards (Map, Trade-offs, Lineage). Low effort, high researcher value. |
| **Campaign manifest UI** (GAME.md §5.4) | Medium | Add **Campaign Card** component: plain/technical title, description, objectives, status, entry points. Renders from YAML manifest — zero dashboard code per spec. |
| **Preview Shelf too passive** | Low | Enhance: show live Ouroboros Probe config (task, envelope, seed genome, kill criterion), link to `comp scientist phylogeny` for completed runs. |
| **Performance budget undefined for new panels** | Medium | Add per-panel budget: Constitution Health ≤50ms, Lineage Viewer ≤100ms (virtualized), Probe Analytics ≤100ms. Debounce all WebSocket→UI updates to ≤1Hz. |

### 🎯 Recommended Phasing (Adjusted)

| Phase | Core (Must) | Instrumentation (High Value) | Defer |
|-------|-------------|------------------------------|-------|
| **M0** | Glossary, Mode toggle, Design tokens, A11y baseline | — | — |
| **M1** | All 6 panel refactors (Map, Trade-offs, Repair, Health, Feed, Reports), "What am I looking at?", Readability lint | **Constitution Health** (uses existing `StabilityMonitor`), **Episode Timeline** (existing event log) | Lineage Viewer, Probe Analytics, Stagnation, Genome, Mutations, Veto Log |
| **M2** | Recognition (badges, quests, records, fog, progress, kill switches), Replay locks | **Lineage Viewer** (phylogeny), **Probe Analytics** (forked-copy hygiene), **Workshop panel** (DialComposer, RecipeCard) | Stagnation Dashboard, Genome Health, Mutation Explorer, Veto Log |
| **M3** | Onboarding, Team wall, i18n, Final a11y, Preview Shelf, Gallery compat | **Stagnation Dashboard**, **Genome Health**, **Mutation Explorer**, **Veto Log** (if Auto-Evolve runs exist) | — |

### 🔬 For Researchers: The Killer Demo Path

With this plan, a serious researcher sees:

1. **Map** → UMAP atlas with fog-of-war (KB coverage), Pareto fronts, shape-encoded outcomes
2. **Trade-offs** → Multi-objective Pareto with ruler-relative anchors, instant objective-pair switching
3. **Constitution Health** → Live ρ(J_F) vs τ=1.029, passivity, resource ceiling — *the stability guard in action*
4. **Lineage Viewer** → `comp scientist phylogeny` visualized: which mutations survived, slope evidence
5. **Probe Analytics** → Adaptation probes: forked copies, slope comparison, acceptance criteria
6. **Workshop** → DialComposer with `SystemConfig.validate()` compatibility feedback, RecipeCards for 13 factories
7. **Record Book** → CEEC ledger chain: Experiment → Evidence → Belief → Gate → Decision

This demonstrates: **6-axis ontology, multi-objective Pareto, stability guard, genealogy, slope-based selection, CEEC governance** — the full research framework.

### 👶 For Newcomers: The Onboarding Path

1. **Home** → "There are many ways to teach a computer. We're mapping all of them."
2. **Map** → Fog lifts as they watch; hover cards explain recipes in plain language
3. **Glossary drawer** → One gesture from any term to plain + expert definition
4. **Guided tour** → 3 steps: "Watch a measurement", "Read a trade-off", "See a repair"
5. **Workshop** → "Try a known recipe" → picks `eqprop_mnist` → sees it train → gets receipt link

### Decision

**Proceed with adjusted phasing above.** The design is sound; the instrumentation panels are the differentiator for researchers. Cut M1/M2 scope ruthlessly to hit dates. Add Workshop panel and Campaign Card per GAME.md §5.4–5.5.

**Next step:** If approved, create `scripts/init_ui_structure.py` to scaffold the module layout and `tests/property/test_ux_l9_constitution_equivalence.py` as the first lock.