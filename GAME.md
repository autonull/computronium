# Development Specification — Inclusive, Gamified Dashboard UX

**Working title:** TODO-UX1 · "Basecamp" — Plain-Language Discovery Dashboard
**Scope:** `comp dashboard` (and the `comp daemon` UI surface)
**Status:** Draft for review
**Verification posture:** UI-layer claims land at Level 4/5 per the repo taxonomy; deterministic-replay and readability locks are specified below as property tests.

---

## 1. Background

Today `comp dashboard --root artifacts/broad_map --port 8088` renders a read-only live window over continuous discovery: islands/voids UMAP atlas, defect funnel, health gauge with divergence count, Pareto strip with objective-pair selector, burst-log ticker, and an event stream with alert toasts. The daemon variant adds lifecycle API + WebSockets.

The dashboard is functionally rich but written for insiders: "Pareto strip," "quarantine," "deep-tier claim-grade L2 re-runs," "ρ(J_F)," "ψ capacity." Newcomers, domain scientists, and contributors without ML fluency hit a terminology wall. Meanwhile the underlying activity (exploration, repairs, re-checks, records) is inherently game-like and under-exploited for engagement.

This spec defines an upgrade with three coupled goals:

1. **Plain-language conceptual refactor** — not a rename pass; a new mental model with progressive disclosure back to expert terms.
2. **Inclusive UX** — usable by newcomers, domain scientists, ML researchers, systems engineers, and accessibility-first users, on equal footing.
3. **Honest gamification** — engagement mechanics wired to real epistemic events (CEEC ledger, KB coverage, maturation gates), never to hype.

---

## 2. Goals / Non-Goals

### Goals

- A first-time visitor understands the dashboard's purpose within **60 seconds** without external docs.
- Every panel answers three questions in plain language: *What am I looking at? Why does it matter? What changed recently?*
- Dual-register presentation: **Explorer** (plain language) and **Lab** (expert terminology), toggleable at any time, never lossy in either direction.
- Gamification that rewards evidence quality, reproduction, repair, and honest negative results — aligned with CEEC governance.
- WCAG 2.2 AA compliance across all dashboard surfaces.
- Zero change to measurement semantics: the upgrade changes presentation and derived engagement state only; no cell, objective, or gate definition is altered.

### Non-Goals

- No new measurement, promotion, or claim logic.
- No competitive leaderboards by default (opt-in team feature only, §8.6).
- No sound by default; no dark patterns, fake urgency, or engagement mechanics that pressure runtime decisions.
- No rewrite of the daemon/lifecycle API; UI consumes existing WebSocket/event streams.

---

## 3. Personas & Expertise Tiers

| ID | Persona | Needs | Primary panels |
|---|---|---|---|
| P1 | **Curious newcomer** — student, adjacent-field dev, first-time contributor | Meaning without math; guided tour; safe read-only exploration | Map, activity feed, progress |
| P2 | **Domain scientist** — physicist/biologist using the library; math-fluent, ML-unfamiliar | Energy/stability framing; objectives explained in physical terms | Trade-offs, stability goals, specimen cards |
| P3 | **ML researcher** | Density, expert terms, parallel coordinates, raw metrics, no friction from gamification | Lab mode, Pareto, campaign tables |
| P4 | **Systems/hardware engineer** | Defects, health, divergence, kernel/backends status | Repair bench, health, activity feed |
| P5 | **Accessibility-first user** — screen reader, keyboard-only, reduced motion, color-blind | Full non-visual parity; text alternatives for every chart | All panels, a11y contract in §9 |

**Tier model.** The UI does not hard-gate by persona. Instead:

- A global **view mode** switch: `Explorer ⇄ Lab` (§5.2), persisted per browser profile.
- Every technical term in Lab mode is hover-/focus-able for the plain-language equivalent, and vice versa.
- An optional **onboarding quiz** (3 questions, skippable) only sets the default mode and tour depth; it never restricts features.

---

## 4. Design Principles

1. **Plain language first, expert terms one gesture away.** Default copy targets ≤ grade-8 readability (Flesch–Kincaid enforced in CI, §11.4). Expert notation appears in tooltips, detail drawers, and Lab mode.
2. **Progressive disclosure over hiding.** Nothing is removed; depth is layered. Explorer mode must never lie or over-simplify a quantity's meaning.
3. **Rewards follow evidence.** Gamification events derive exclusively from recorded, auditable events (KB flushes, CEEC gates, quarantine lifecycle, maturation). No XP for unrecorded activity. Anti-Goodhart rules in §8.5.
4. **Read-only by default.** The dashboard stays a window. Actions that mutate state (`unquarantine`, maturation re-runs) surface as **copy-the-command** affordances; direct buttons are opt-in behind `--ui-actions on`.
5. **Calm technology.** No auto-playing sound, no blinking, no countdown pressure. Ticker is pausable; toasts are batchable; all motion respects `prefers-reduced-motion`.
6. **Deterministic derived state.** Gamification state must be a pure function of the event log + KB (replayable, resumable, idempotent) — mirroring continuous discovery's resume-safe philosophy. Property-locked (§11.3).
7. **Accessibility is a launch gate**, not a polish pass (§9).

---

## 5. Plain-Language Conceptual Model

### 5.1 The metaphor system: *Expedition*

The 6-axis ontology space is presented as a **map of an expedition**:

| Concept | Metaphor | Why |
|---|---|---|
| Ontology space (S×G×D×P×C×U) | The map / the territory | Spatial intuition already matches the UMAP atlas |
| Cell (one coordinate measured) | A **specimen** (or "candidate") | Concrete, collectible, neutral |
| Islands | **Explored regions** | Already half-metaphorical; make explicit |
| Voids | **Uncharted regions** | Neutral, invites curiosity rather than "gap = failure" |
| Pareto front | **Best trade-offs** | Exact plain-language semantics (§5.3) |
| Objectives | **Goals** | With units always rendered |
| Defect funnel / quarantine | **Repair bench** / "set aside for repair" | Removes punitive connotation |
| Maturation l0 → l1 → l2 | **Confidence levels**: first look → double-checked → careful re-check | Maps directly to maturity tiers |
| Burst / budget | **Work session** / **time allowance** | |
| AutoScientist | **Auto-explorer** | Keeps agency without anthropomorphic overclaim |
| Campaign | **Study** | Scientific without jargon |
| CEEC gate/belief | **Evidence check** / "what the record supports" | |
| Negative result | **Field note: what didn't work** | Honors `failure_manifesto` culture |

**Rule:** one metaphor per concept, globally consistent. Mixed metaphors are a review blocker. The term table (§5.3) is the single source of truth and is shipped as data (`ui/glossary.json`), rendered by a glossary service, so copy can be localized and linted.

### 5.2 View modes

- **Explorer mode** (default for new profiles): full metaphor system, plain units, guided annotations, gamification visible.
- **Lab mode** (default for returning users who opt in, or via quiz): original terminology (Pareto front, quarantine, ρ(J_F), ψ capacity), denser tables, gamification chrome hidden but stats still reachable via a "session stats" drawer.
- Mode switch is instant, persistent, and never reloads data. Deep links carry `?mode=` but user preference wins.

### 5.3 Master term table (canonical excerpt)

| Expert term | Explorer rendering | Tooltip / learn-more anchor |
|---|---|---|
| Pareto-optimal | Best trade-off — no other candidate beats it on every selected goal | `glossary#tradeoffs` |
| Pareto-near | Strong trade-off | same |
| Dominated | Outperformed on the selected goals | same |
| `accuracy` | How often it's correct (%) | `glossary#accuracy` |
| `walltime_s` | How long it takes (seconds) | `glossary#walltime` |
| `param_count` | Size — number of adjustable parts | `glossary#params` |
| `flops` | Work per step (operations) | `glossary#flops` |
| `energy_per_step` | Energy per step (simulated/estimated/measure labeled) | `glossary#energy` |
| `spectral_radius` ρ(J_F) | Stability margin — how quickly disturbances die out | `glossary#stability` |
| `psi_capacity` | Fast-adaptation capacity (learning without changing core weights) | `glossary#psi` |
| frozen-θ | Core weights locked | `glossary#frozen-theta` |
| `nan_loss` / divergence | Run blew up (numerically unstable) — set aside from rankings | `glossary#divergence` |
| quarantine | Set aside for repair | `glossary#repair` |
| `unquarantine` | Put back in service | same |
| deep tier / claim-grade L2 | Careful re-check (per-seed, claim-grade) | `glossary#confidence` |
| KB coverage | What we've already measured | `glossary#coverage` |
| breakthrough alert | New personal best on a goal | `glossary#records` |
| credit assignment | How the system learns from mistakes | `glossary#credit` |
| substrate | Hardware style (digital, memristive, optical, …) | `glossary#substrate` |
| 6-axis coordinate | Recipe — six choices that define a learning system | `glossary#axes` |
| UMAP atlas | Map of all tested recipes; nearby = similar | `glossary#map` |

**Units rule:** every number renders with a unit and, where available, a reference ("2.3× the reference method's time"; "chance level = 10%").

### 5.4 Writing rules (enforced in review + CI lint)

1. Active voice; sentences ≤ 25 words where possible.
2. One idea per sentence; no nested clauses in panel headers.
3. Explain anomalies without blame: "This run produced unusable numbers, so we set it aside" — never "failed/broken" without a next step.
4. Empty states teach: every empty panel ships with a one-sentence explanation + one suggested next action.
5. Every chart carries: a title in plain language, a one-sentence "what this shows," and a details drawer with the expert formulation.

**Before/after microcopy examples:**

| Before | After (Explorer) |
|---|---|
| "NaN-loss results are tagged `nan_loss` and excluded from Pareto fronts, promotion, and the deep tier." | "Some runs produced unusable results (numbers blew up). We set them aside so they don't skew the rankings. They stay in the log for inspection." |
| "Deep-tier promotes front-stable cells to claim-grade L2 re-runs." | "Promising candidates get a careful re-check: rerun per seed before we trust them." |
| "Quarantined until `comp continuous unquarantine --defect <id>`." | "Set aside for repair. When the fix lands, put it back with: `comp continuous unquarantine --defect d-123` [copy]." |
| "Objective-aware driver biases proposals toward under-explored regions of objective space." | "The auto-explorer focuses next on corners of the map we've measured least." |

---

## 6. Information Architecture

```
Dashboard shell
├── Header: study name · mode toggle (Explorer⇄Lab) · session status · help
├── Left rail (collapsible):
│   ├── Map            (was: living atlas)
│   ├── Trade-offs     (was: Pareto strip / radar)
│   ├── Repair bench   (was: defect funnel)
│   ├── Health         (was: health gauge)
│   ├── Progress       (NEW: quests, badges, records)
│   └── Glossary       (persistent drawer)
├── Main pane: selected panel
├── Bottom dock: activity feed (was: burst-log ticker), pausable
└── Toasts: field reports (was: alert toasts), batched, polite aria-live
```

Each panel gets a persistent **"What am I looking at?"** button opening a contextual explainer with: plain summary → why it matters → expert details → link to docs (e.g., `docs/IDENTITY_CARDS.md`, CEEC guide).

---

## 7. Component Specifications (current → upgraded)

### 7.1 Discovery Map (was: islands/voids UMAP atlas)

**Purpose unchanged:** 2-D projection of measured cells; islands = explored, voids = uncharted.

Upgrades:

- **Fog-of-war overlay:** uncharted regions render as soft fog; measured coverage lifts the fog as KB coverage grows. Coverage % shown as "You've charted 42% of the planned regions."
- **Region labels:** auto-generated plain names from dominant axis facets (e.g., "Spiking · Recurrent corner"), overridable by user naming (§8.7).
- **Specimen markers:** shape encodes outcome class (best trade-off ▲, strong ●, outperformed ○, set aside ⚠, blew up ✕) — never color alone (§9).
- **Hover card:** plain-language specimen summary: recipe (6 axes in plain words), goals measured, confidence level (l0/l1/l2), age.
- **Text alternative:** a sortable table view of the same cells (screen-reader parity; also serves color-blind and low-vision users).
- **Expert drawer:** raw UMAP coordinates, strata, objective vectors.

Acceptance:
- [ ] Fog overlay is derivable from KB coverage alone (no new measurement).
- [ ] All marker states distinguishable with color removed (grayscale screenshot test).
- [ ] Table view exposes 100% of information in the visual map.

### 7.2 Trade-offs Panel (was: Pareto strip / radar + objective-pair selector)

- **Selector renamed** "Compare two goals," with plain-labeled goal pairs ("correctness vs. speed," "correctness vs. size," "correctness vs. energy"). Full objective list remains in Lab mode and the drawer.
- **Plain semantics line** rendered permanently: *"A dot is a 'best trade-off' if nothing beats it on both goals."*
- **Reference anchors:** when a ruler table exists, show the reference method as a distinct marker and express `ruler_walltime_ratio`/`ruler_energy_ratio` as "× the reference."
- **Guided reading:** hovering the front shows a one-sentence narration ("These 7 candidates are the best trade-offs; picking one means giving up something on the other goal").
- **Radar/presets preserved** in Lab mode; Explorer shows at most 2 goals + optional 3rd via size encoding, with explicit legend.

Acceptance:
- [ ] Front recomputation identical to `pareto_top(df, objectives=...)` — byte-identical membership vs. backend (Level 4 lock).
- [ ] Narration strings pass readability lint.
- [ ] Selector usable end-to-end by keyboard only.

### 7.3 Repair Bench (was: defect funnel)

- Reframed from blame to workflow: **Arrived → Diagnosed → Fixed → Back in service**, plain statuses.
- Each defect card: what happened (plain), which region of the map it affects, the exact `unquarantine` command with **[copy]** button, link to `runtime_defects.jsonl` line.
- Gate rejections vs. runtime crashes are visually and verbally distinct: "set aside (crash — fixable)" vs. "uncharted boundary (the combination isn't allowed by design — not a bug)."
- Opt-in action button (behind `--ui-actions on`) calls the same lifecycle API as the CLI; confirmation dialog states the consequence in plain language.

Acceptance:
- [ ] Every card renders copy-pasteable CLI equivalent.
- [ ] Structural voids never labeled as defects/bugs.

### 7.4 Health Panel (was: health gauge)

- Three plain tiles: **Running smoothly / Needs attention / Unstable runs**, with counts and one-line explanations.
- Divergence count becomes: "N runs blew up since the last session — set aside from rankings."
- Session vitals (uptime, cells/hour, budget remaining) with plain labels and no raw timestamps without relative time ("12 minutes ago").

### 7.5 Activity Feed (was: burst-log ticker)

- Pausable, reverse-chronological, plain-language lines: "Measured a new candidate in the spiking corner," "Re-check finished: still a best trade-off," "Set aside for repair: crash in memristive region."
- Each line expandable to the raw log line + structured event (Lab mode shows raw first).
- `aria-live="polite"`, rate-limited to ≤1 announcement/2s; batch summary mode ("14 new measurements in the last 5 minutes") for screen readers.

### 7.6 Field Reports (was: event stream with alert toasts)

- Toasts retyped as **field reports**: icon + one sentence + [See it] deep link.
- Breakthrough alerts phrased as *new records on a goal*, always scoped: "New best correctness among candidates with similar size" — never bare "state of the art."
- Batched into a tray; unread count badge is the only persistent chrome.

---

## 8. Gamification System

### 8.1 Philosophy

The research loop already contains natural game verbs: explore, measure, repair, re-check, record. Gamification makes those verbs visible. It must never incentivize overclaiming: **XP and badges are granted only for events the CEEC ledger or KB already records.**

### 8.2 XP economy (event → points)

| Event (source of truth) | XP | Plain name |
|---|---|---|
| Cell measured & KB-flushed (l0) | +1 | "New specimen" |
| Cell re-run at l1 maturation | +3 | "Double-checked" |
| Deep-tier l2 claim-grade re-run completed | +10 | "Careful re-check" |
| Gate passed (CEEC promotion/boundary) | +15 | "Evidence check passed" |
| Calibration review completed (Brier within threshold) | +8 | "Honest forecaster" |
| Defect diagnosed (field note added) | +5 | "Diagnosed" |
| Quarantine released (`unquarantine`) | +6 | "Back in service" |
| Negative result documented (failure manifesto entry) | +12 | "Honest field note" |
| Reproduction confirmed (seed-agreement re-run) | +10 | "Reproduced" |
| Divergence correctly triaged (tagged, excluded) | +2 | "Triage" |

**Explicitly never rewarded:** raw accuracy alone, claim language, leaderboard position, speed of claiming.

### 8.3 Badges (verifiable, ledger-linked)

Badges are granted by deterministic rules over the event log and carry a "see the evidence" link to the underlying record.

- **First Steps** — first measured cell.
- **Mapmaker** — 50 / 250 / 1000 cells charted (tiers).
- **Double-Checker** — first l1 maturation.
- **Gold Standard** — first l2 claim-grade re-run.
- **Honest Broker** — documented a negative result.
- **Repair Crew** — released a quarantine.
- **Steady Hand** — 7 consecutive days with ≥1 measured session (daemon uptime; graceful freeze on gaps ≤1 day, no guilt copy).
- **Cartographer** — named 5 regions.
- **Open Book** — viewed 10 glossary entries (participation badge, trivially earnable, low XP).

### 8.4 Quests (mapped to real campaign mechanics)

Quests are opt-in checklists generated from campaign config; they never alter campaign behavior.

| Quest | Underlying mechanic |
|---|---|
| "Chart 100 new regions this week" | `--target-cells` / KB coverage delta |
| "Double-check 3 promising candidates" | `--maturation` l1 queue |
| "Send one candidate to careful re-check" | deep-tier promotion |
| "Clear one item from the repair bench" | `unquarantine` lifecycle |
| "Compare correctness against energy" | Pareto selector usage |
| "Forecast and check yourself" | CEEC calibration prompt |

Quest completion copy must state what was *learned or verified*, not just what was earned.

### 8.5 Anti-Goodhart & integrity rules (hard requirements)

1. XP/badges are **derived, append-only, replayable** from the event log; no separate mutable counters.
2. No metric shown in the gamification layer may be interpreted as scientific status; badges link to evidence and inherit CEEC gated status — a quarantined experiment's derived rewards are frozen, not deleted, with a visible "under review" flag.
3. Gamification visibility never changes measurement, promotion, or claim logic.
4. Global kill switch: `--gamify off` / env `COMPUTRONIUM_NO_GAMIFY=1`; Lab mode hides gamification chrome by default.
5. Quarterly self-audit: report correlation between XP-earning actions and CEEC gate-rejection rate; rising correlation with rejections triggers a redesign review.

### 8.6 Social / team features (opt-in, M3)

- Team progress wall (cooperative totals only), opt-in per team.
- Region naming with moderation queue; names stored as presentation metadata, never in measurement records.
- No individual competitive leaderboards in v1.

### 8.7 Naming & ownership

- Users may propose plain names for map regions; proposals are metadata-only, versioned, revertible.
- Specimen cards expose "discovered by campaign X on date Y" provenance.

---

## 9. Accessibility & Inclusion Contract

Binding requirements (launch gates per phase):

1. **WCAG 2.2 AA** across all dashboard routes (axe-core 0 critical/serious; manual audit each milestone).
2. **Color:** palettes from colorblind-safe families (e.g., viridis/cividis derivatives); every state encoded by color is also encoded by shape, pattern, or text. Contrast ≥ 4.5:1 for body, ≥ 3:1 for large text/UI components.
3. **Keyboard:** full operability; visible focus order matching DOM order; no keyboard traps in UMAP/canvas widgets; skip links to main panels.
4. **Screen readers:** every chart has a text alternative (summary + data table); ticker/toasts use `aria-live="polite"` with rate limiting and batch summaries; gamification toasts announce content, not animation.
5. **Motion:** `prefers-reduced-motion` disables fog animation, ticker scroll, toast slides; static equivalents provided. No motion is required to perceive state changes.
6. **Cognitive load:** ≤ 5 interactive elements above the fold per panel in Explorer mode; progressive disclosure drawers; consistent empty/error/loading states with plain copy.
7. **Text scaling:** layout intact at 200% zoom; reflow at 320px width without horizontal scrolling (except map canvas, which has the table alternative).
8. **i18n-ready:** all copy behind the glossary/string service from day one; no string concatenation of UI sentences; number/date/units locale-formatted. English plain-language is v1; architecture must not preclude translation.
9. **Neurodiversity:** pausable everything; predictable layout; no time-limited UI; quest/XP elements dismissible and permanently hidable.

---

## 10. Data Model, Events & Technical Integration

### 10.1 Stack fit

- UI remains the NiceGUI-based read-only window served by `comp dashboard` / `comp daemon` (ports 8088/8940), consuming the existing WebSocket event stream and `artifacts/broad_map` roots.
- No change to KB flush semantics, quarantine lifecycle, maturation gates, or objective definitions.

### 10.2 Event extensions (presentation-only)

Add a `gamify.*` namespace derived by a pure projector over existing events:

```
gamify.xp_granted      {event_ref, rule_id, xp, ts}
gamify.badge_awarded   {badge_id, evidence_ref, ts}
gamify.quest_progress  {quest_id, delta, ts}
gamify.region_named    {region_id, name, proposer, ts}
```

- `event_ref` must resolve to the originating KB/CEEC record.
- The projector is deterministic: `state = fold(event_log)`; no wall-clock-dependent logic except streak windows (documented exception with grace rules).

### 10.3 Persistence

- Gamification profile in a sidecar SQLite next to the root (`ui_state.sqlite`), append-only tables mirroring CEEC ledger ethos; rebuildable by replay (`comp dashboard --rebuild-ui-state`).
- User preferences (mode, dismissed tours, hidings) in browser-local storage; nothing personal required server-side.

### 10.4 CLI/config surface

```
comp dashboard --root R --port 8088 [--ui-mode explorer|lab|auto]
                [--gamify on|off] [--ui-actions on|off] [--rebuild-ui-state]
comp daemon    ... same flags ... --port 8940
```

Defaults: `--ui-mode auto` (first profile → explorer), `--gamify on`, `--ui-actions off`.

### 10.5 Performance budget

- Gamification projection runs async/debounced (≤1 Hz UI updates); dashboard time-to-interactive ≤ 2s on a laptop with a 50k-cell root; map renders ≤ 200ms interaction latency; tickers never block the WebSocket pump.

---

## 11. Verification, Testing & Locks

Aligned with the repo's lock culture and the 5-level taxonomy (UI work lands at **L4 sampled numerical / L5 empirical**; no L1–3 claims are implied).

| Lock | Property | Type |
|---|---|---|
| UX-L1 | Pareto membership rendered == `pareto_top(df, objectives)` membership for all objective presets | L4 equivalence test |
| UX-L2 | **Deterministic replay:** `fold(event_log)` yields identical XP/badge/quest state across shuffle-safe replays; idempotent on duplicate events | L4 property test (Hypothesis) |
| UX-L3 | **Glossary totality:** every UI string key resolves in `glossary.json` in both registers; no unregistered technical term in Explorer copy (term blocklist scan) | L4 lint lock |
| UX-L4 | **Readability lock:** all Explorer-mode strings ≤ Flesch–Kincaid grade 8 (allowlist for proper nouns/equations); sentence-length histogram gate | CI lint |
| UX-L5 | **A11y lock:** axe-core scan on all routes, 0 critical/serious; keyboard crawl reaches all interactive elements | CI + manual per milestone |
| UX-L6 | **Marker redundancy:** screenshot diff in grayscale preserves state distinguishability (shape/label check) | L4 snapshot test |
| UX-L7 | **Integrity lock:** no gamification rule reads or writes measurement/promotion/claim state; projector has zero imports from campaign/gate mutation paths | static import lock |
| UX-L8 | Gallery/demo lock compatibility: existing `comp gallery` artifacts remain renderable; dashboard changes do not alter gallery manifests | regression test |

User-facing evidence (L5): moderated usability studies per §12.

---

## 12. Success Metrics

| Metric | Target | Method |
|---|---|---|
| Time-to-first-insight (newcomer): correctly answers "which candidate is the best trade-off for correctness vs. speed?" | ≤ 3 min, ≥ 80% of P1 participants | Moderated study, n≥8/persona |
| Task success on 5 core tasks (find front, read health, interpret repair card, use glossary, toggle modes) | ≥ 90% | Same study |
| SUS | ≥ 75 across personas | Survey |
| A11y audit | 0 critical/serious; keyboard 100% | axe + manual |
| Gamification opt-out rate | ≤ 10% of sessions | Telemetry (opt-in, local-first) |
| Claim hygiene unchanged | CEEC gate-rejection rate stable pre/post | Ledger audit |
| Plain-language lint | 100% strings pass | CI |

Telemetry is opt-in, local-first, and contains no experiment data — only interaction counts.

---

## 13. Phased Delivery Plan

### M0 — Foundations (≈2 weeks)
- Glossary service + `ui/glossary.json` (term table §5.3 as data).
- Design tokens: palettes (colorblind-safe), type scale, iconography with shape redundancy, focus styles.
- Mode toggle scaffold (Explorer/Lab) with persistence; string service wired into all existing panels (copy still legacy behind flag).
- A11y baseline audit of current dashboard; fix critical keyboard/contrast issues.
- **Exit:** UX-L3/L5 harnesses green on scaffold; mode toggle ships dark.

### M1 — Plain-Language Component Refactor (≈3 weeks)
- All copy migrated through glossary service in both registers.
- Panels refactored per §7 (names, narrations, empty states, units/reference anchors).
- Text alternatives for map and Pareto; ticker/toast aria-live hardening; reduced-motion support.
- **Exit:** UX-L1/L4/L6 locks green; newcomer study round 1 shows ≥70% time-to-first-insight target.

### M2 — Gamification Layer (≈3 weeks)
- Event projector, `ui_state.sqlite`, replay/rebuild command.
- XP, badges, quests, fog-of-war, field reports tray; kill switches; Lab-mode hiding.
- Integrity locks UX-L2/L7; anti-Goodhart audit report scaffolding.
- **Exit:** replay property lock green on 100k synthetic events; opt-in pilot with 2 internal teams.

### M3 — Onboarding, Teams, i18n Hooks (≈2 weeks)
- Guided tour (3 steps, skippable, resumable), "What am I looking at?" system, comfort quiz.
- Region naming, cooperative team wall (opt-in), i18n string freeze + extraction audit.
- Final a11y certification, SUS study round 2, docs refresh (`docs/platform/`, gallery manifests).
- **Exit:** all §12 targets met or explicitly waived with recorded rationale (CEEC-tracked).

---

## 14. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Trivialization of science; newcomers misled by metaphors | Explorer copy reviewed against "does this change the meaning?" rule; expert drawer one gesture away; glossary anchors cite real docs; study checks comprehension, not just speed |
| Goodharting / gamification distorting research behavior | §8.5 hard rules; rewards bound to epistemic quality events; quarterly correlation audit vs. gate rejections |
| Performance regressions on large roots | Async projector, debounced UI, budgets in §10.5, table fallbacks for heavy canvases |
| Accessibility debt in canvas-heavy widgets | Text alternatives are mandatory siblings, not enhancements; UX-L6 lock |
| Scope creep into campaign logic | UX-L7 import lock; spec non-goals enforced in review |
| Copy drift post-launch | Readability + glossary lint as CI gates; copy changes require glossary PR |

---

## 15. Open Questions

1. Should Explorer mode surface the 6-axis recipe editor read-only ("why is this candidate built this way?") in v1, or defer to a later milestone?
2. Team features: cooperative-only forever, or revisit competitive leaderboards after one quarter of audit data?
3. Localization target language(s) for the first translation pass, and who owns plain-language review for non-English registers?
4. Does `comp gallery` adopt the same glossary service in this effort, or as a fast-follow (kept out of scope here to protect gallery locks)?

---

*Suggested file location:* `docs/research/todo-ux1/dashboard_ux_spec.md`, with `ui/glossary.json` seeded from §5.3 and locks registered alongside the existing property-lock suites.

----

# The Learning Atlas — Complete Dashboard Specification
**Revision 2 · Self-contained · Instrument first, open to everyone.**

---

## 1. What this document specifies

Computronium's discovery machinery — campaigns over the six-axis space of learning systems, the CEEC evidence ledger, the 64-spec registry, and the five-level verification taxonomy — already produces a rich stream of artifacts. The existing `comp dashboard` already renders part of it: living atlas, defect funnel, health gauge, Pareto strips, burst-log ticker, event stream.

This specification unifies two previously separate ideas — the **research instrument** and the **community participation layer** — into a single system, governed by one rule:

> **The dashboard is a tool. Participation is the same tool, made accessible. The game is the instrument, translated — never a parallel system built beside it.**

Public persona: **The Learning Atlas.** Command stays `comp dashboard`. Tagline: *"Every way a machine can learn — mapped, compared, and backed by receipts."*

---

## 2. Design principles

1. **Instrument first.** The primary user is still the person running campaigns. Monitoring, diagnosis, and control are specified in full (§5.3). Nothing in the public layer may degrade, hide, or slow the expert instrument.
2. **The Bijection Rule.** Every public-facing element must correspond to a real artifact, state, or action in the underlying system. If we cannot point at the artifact, we do not render the element. No invented game state, ever.
3. **Plain by default, precise on demand, expert-pinnable.** Two registers on every screen. Experts can pin the technical register as their permanent default.
4. **Read-only by default; interventions audited.** Visitors see a window. Any state-changing action is an explicit operator act, routed through existing CLI/API paths and stamped into the CEEC decision log.
5. **Receipts, not points.** Recognition is verification status, outcome badges, and evidence links — all pre-existing system facts. XP, streaks, and currencies are prohibited.
6. **Implemented-first.** Everything specified here runs on shipped machinery. Unimplemented proposals get a clearly labeled preview slot (§11), nothing more.
7. **Accessible by default.** WCAG 2.1 AA, keyboard-complete, i18n-ready, plain-language default, CPU/browser floor (§8).

---

## 3. The two-register language system

Every screen renders in two registers:

- **Simple register (default):** everyday words, one idea per view. Model copy in this spec is written in it.
- **Technical register:** exact ontology terms, configs, metrics, ledger queries — one click away via *"See the science,"* and pinnable as the user's default.

### The plain-language dictionary (load-bearing)

Every simple-register label draws from the left column. The right column is the internal referent.

| Screen says | System referent |
|---|---|
| A way to learn | a learning algorithm / model family |
| The six dials | the 6-axis ontology (S · G · D · P · C · U) |
| What it's built from | Substrate axis |
| Its shape / wiring | Geometry axis |
| How it thinks step by step | StateDynamics axis |
| How it can change itself | Plasticity axis |
| How it learns from mistakes | CreditAssignment axis |
| How it remembers what it learned | ParameterUpdate axis |
| The map | broad-map atlas (islands = what works, gaps = voids) |
| A big test / expedition | a campaign (`comp continuous` / `comp campaign`) |
| The best trade-offs | the Pareto front (`pareto_top`) |
| The record book / receipts | the CEEC ledger |
| How sure we are (proof level) | verification Levels 1–5 |
| What we learned from it not working | failure manifesto |
| The ground rules it can't break | property locks / stability guard |
| A quick try-out | an adaptation probe / benchmark cell |
| Set aside because it crashed | quarantined cell (`runtime_defects.jsonl`) |
| Speed-tested and checked | `kernel_verified` promotion |
| Family tree | genealogy / phylogeny |
| Keeps its body, changes its habits | frozen-θ ψ-only adaptation |
| The auto-explorer | the AutoScientist |

Terms not in the dictionary either get added or stay in the technical register only.

---

## 4. Architecture

**Stateless over artifacts.** The dashboard owns no state. It reads:
- Campaign roots (`artifacts/broad_map`, per-campaign roots) — cells, fronts, maturity
- `runtime_defects.jsonl` — the defect funnel
- The CEEC ledger (`ceec.sqlite3` and campaign ledgers) — experiments, evidence, beliefs, gates, calibration
- The registry — 64 `ImplementationSpec`s, identity cards, status ladder
- Live event streams (WebSocket) from `comp continuous` / `comp daemon`

**Campaign manifest** — campaigns are the unit of activity. Each campaign gets a plain-language description block alongside its existing config:

```yaml
id: broad_map_s1
title_simple: "Fill in the map of what works"
title_technical: "Stratified broad mapping sweep, accuracy/walltime/params"
description_simple: >
  We're testing combinations of the six dials nobody has tested yet.
  Each test lights up one spot on the map. Crashes are recorded too —
  they teach us where the map has cliffs.
objectives: [accuracy, walltime_s, param_count]
status: open            # proposed | open | closed | archived
entry_points: [watch, submit_cell, fix_defect]
```

Adding a campaign = dropping manifest + config. Zero dashboard code.

**No new databases, no new write paths.** All interventions route through existing machinery (`comp continuous unquarantine`, maturation flags, CEEC gates), so the audit trail is inherited, not invented.

---

## 5. The views

### 5.0 Shell
Nav: **Home · Map · Campaigns · Workshop · Lessons · Record book · Contribute**. Persistent: campaign switcher, live ticker, alert toasts (existing), register toggle, language selector. Read-only for anonymous users; operator session required for interventions.

### 5.1 Home
> *"There are many ways to teach a computer. We're mapping all of them, comparing them fairly, and writing down exactly what happens."*

Live status cards for open campaigns (health gauge, cells tested, front summary), the atlas thumbnail, and a plain-language event ribbon: *"Just now: a spiking learner beat the standard one on a memory test — receipt saved."*

### 5.2 The Map (atlas)
Existing islands/voids UMAP + parallel coordinates + Pareto radar, with a plain legend: *"Bright = learned well. Dark = didn't. Empty = nobody's tested it yet."* Click any cell → coordinate, status, evidence, and for voids: whether the gap is a **bug** (quarantined, fixable) or a **boundary** (structural, gate-rejected) — a distinction the defect funnel already makes and the public layer must preserve.

### 5.3 Campaign Control — the operator console
The tool core, specified in full. Tabs:

| Tab | Contents | Existing source |
|---|---|---|
| Live | Health gauge, divergence count, NaN tags, burst log, event stream with alerts | `comp dashboard` current |
| Front | Pareto strip with objective-pair selector; outcome badges `PARETO_OPTIMAL / NEAR / DOMINATED` | `pareto_top`, driver |
| Defects | `runtime_defects.jsonl` viewer; quarantine list; **unquarantine** action | defect funnel |
| Maturation | l0→l1→l2 promotion status; deep-tier claim-grade re-runs | `--maturation`, deep-tier |
| Objectives | Objective set configuration and rationale; presets | `--objectives` |
| Control | Budget, pause/resume, abort; loop/sleep settings | burst runner |
| Receipts | This campaign's ledger rollup: experiments, beliefs, calibration score | CEEC |

Every intervention is confirm-gated and lands in the CEEC decision log. Simple-register captions explain each control; technical register shows raw configs.

### 5.4 The Race (leaderboard)
Campaign fronts rendered as comparisons anyone can read: **how well it did · how much computer it needed · link to the receipt.** Nothing appears without a ledger entry and a verification level. This is the Pareto front with CEEC gating, presented — not a new scoring system. Ruler-relative columns (`bp_deficit`, `ruler_walltime_ratio`) render as *"vs. the standard method"* in the simple register.

### 5.5 The Workshop
Entry points for doing, mapped to shipped APIs:
- **Build your own** — six-dial composer with compatibility feedback from `SystemConfig.validate()`; maps to `compose_joint_system` / `Lab.specify` → `synthesize`.
- **Try a known recipe** — the 13 model factories as recipe cards (`recipe_cards.py`), each linking its identity card.
- **Fix a crash** — pick a quarantined cell, see the defect record, submit a fix (routes to `unquarantine` review).
- **Donate your computer** — one toggle; wraps the existing P2P gRPC worker; node ID stamped onto campaign artifacts it processes.

### 5.6 Lessons (the graveyard)
Failure manifestos rendered as plain-language lessons: what was tried, why it failed, partial successes, what it ruled out. Each ends with the takeaway. The E1 falsification (deep chaotic unfolding; composition-error compounding) is the flagship exhibit — proof from day one that this place records honest losses.

### 5.7 The Record Book (ledger console)
Chain viewer: Experiment → Artifact → Evidence → Belief → Gate → Decision. Quarantine reports, calibration reports, decision-quality audit. Simple register: *"Here's every claim, what evidence backs it, and how sure we are."* Auditor role required for write actions.

### 5.8 Contribute
Role cards (§7) with onboarding paths. No account to browse; pseudonymous handles for participation.

### 5.9 Preview (proposals)
A single, clearly labeled shelf for unimplemented research directions. Each entry states: what it proposes, its status (**Proposed — not implemented**), and its falsification plan. No live UI, no metrics, no creatures.

---

## 6. Gamification, strictly as presentation

The Bijection Rule, applied:

| Public element | System artifact it presents | New state? |
|---|---|---|
| Missions / seasons | campaigns + manifest | No |
| Leaderboard | Pareto front + CEEC gates | No |
| Score columns | telemetry objectives | No |
| Badges | status markers (`kernel_verified`, outcome badges, verification levels) | No |
| Progression ladder | audited contribution history (receipts) | No |
| Graveyard | failure manifestos | No |
| Map territory | atlas cells + maturity states | No |
| Adoption | seed coordinate/config from registry or campaign | No |

**Prohibited:** XP, points, streaks, leaderboards without evidence links, artificial scarcity, loot mechanics, and any metaphor stated as fact.

**Division of metaphor:** the instrument itself speaks plainly and literally. Outreach (video, posts) may use organism/expedition metaphors but must label them as metaphor and link receipts. The tool never borrows hype it can't cash.

---

## 7. Roles and progression

| If you like to… | Role | What you do | Writes through |
|---|---|---|---|
| Just watch | Looker | Spectate map, races, feed | nothing |
| Explore | Map-filler | Test unexplored cells | campaign runner |
| Compare | Racer | Enter coordinates on a task | campaign + ledger |
| Tinker | Builder | Compose six-dial systems | Lab API |
| Fix things | Fixer | Rescue quarantined cells | unquarantine review |
| Lend a hand | Donor | Donate idle CPU | P2P worker |
| Keep people honest | Auditor | Review claims, calibration | CEEC gates |
| Tell stories | Writer | Turn manifestos into posts | docs/CMS |
| Make it beautiful | Artist | New atlas/view lenses | component SDK |

Progression is **evidenced, not scored**: a user's standing is their linked receipts — cells tested, defects fixed, claims audited, kernels promoted.

---

## 8. Accessibility

- **Participation:** roles for non-coders; three entry doors (browser, notebook, CLI); spectating needs nothing; playing needs a browser; helping needs a laptop CPU. GPU never a gate.
- **Usability (WCAG 2.1 AA):** contrast, keyboard-complete flows (compose → submit achievable without a mouse), screen-reader chart summaries with data-table fallbacks, colorblind-safe palettes (never color-only meaning), `prefers-reduced-motion` honored.
- **Cognitive:** three depths per view (glance / explain / inspect); glossary tooltips linking identity cards and docs; empty states that teach ("This is where the map fills in — here's how to light up the first square").
- **Internationalization:** all simple-register strings in resource files from day one.
- **Privacy:** no PII beyond attribution handle; pseudonymity supported; donation is opt-in with an off switch.

---

## 9. Component library

**Reused as-is:** AtlasMap, ParallelCoordinates, ParetoStrip (+selector), HealthGauge, EventStream, AlertToasts, BurstLogTicker, DefectFunnel.

**New (each with props contract · data source · empty state · loading state · a11y requirements · simple/technical variants):** CampaignCard, LeaderboardTable, ReceiptLink, RecipeCard, DialComposer, QuarantineConsole, PromotionPanel, ObituaryCard, LedgerChainViewer, RoleCard, DictionaryTooltip, PreviewShelf.

Every new component reads existing artifacts only — the Bijection Rule enforced at the component level.

---

## 10. Trust, safety, moderation

- User-submitted content (cells, fixes, annotations) passes the same defect funnel: quarantine on crash, ledger-stamped on acceptance.
- Moderation is mostly mechanical: property locks, gates, and calibration do the policing; humans review quarantine releases and auditor escalations only.
- Rate limits on submissions per handle; all interventions confirm-gated and decision-logged.
- Public deployment serves the read-only layer; operator sessions are local or explicitly credentialed.

---

## 11. Policy on unimplemented proposals (AUTOTILE)

Constitutional self-modification of learning operators is **Proposed, not implemented**, and this spec treats it accordingly:

- It lives exclusively in the **Preview shelf** (§5.9) with its falsification plan (tier probes, kill criteria) summarized in plain language.
- It has no homepage presence, no leaderboard, no live UI, and no outreach dependency.
- If and when it ships, it joins as a new campaign kind (`manifest.kind: self_modification`) — one campaign among many, inheriting every view, gate, and receipt convention unchanged.
- Its load-bearing ideas (neutral birth, slope-based selection) are instrument features first; if they prove out, they surface in Campaign Control as probe diagnostics — tool features, not game features.

---

## 12. Build order

| Phase | Ship | Depends on |
|---|---|---|
| **1. Public read layer** | Two-register shell, Home, Map, Campaign Control (read tabs), Lessons page | existing `comp dashboard` + artifacts |
| **2. Operator interventions in UI** | Defect console, promotion panel, objective switcher, control tab | existing CLI paths |
| **3. Doing** | Workshop (recipe cards, dial composer, fix-a-crash, donor toggle) | Lab API, registry, P2P |
| **4. Ledger console + roles portal** | Record book viewer, calibration displays, role onboarding | CEEC package |
| **5. Browser entry** | WASM playground running a small benchmark cell in-tab | quickstart code |
| **6. Preview shelf** | AUTOTILE and future proposals, labeled | — |

Every phase is independently useful, independently demoable, and requires no unimplemented science.

---

## 13. Acceptance criteria

1. A first-time visitor understands the premise within 60 seconds, no account, simple register.
2. An expert can pin the technical register and lose nothing of the current `comp dashboard` capability — and gains the defect, promotion, and control surfaces.
3. Every leaderboard row resolves to a CEEC evidence chain in one click; every claim shows its verification level.
4. Every public element passes the Bijection Rule audit: point at its artifact, or remove it.
5. Compose → submit and the full operator flow are keyboard-complete.
6. Adding a campaign = manifest + config; zero dashboard code.
7. No view renders blank; empty states teach.
8. The Lessons page shows at least one real recorded failure before launch — the culture visible from day one.
9. Nothing in any register states as fact what the verification taxonomy labels hypothesis.

---

## 14. Summary

One system, two registers, zero fork. The Learning Atlas is the discovery instrument itself — atlas, funnel, fronts, ledger, controls — opened to nine kinds of participants through plain language and receipts-based recognition. Gamification adds no state, invents no scores, and never outruns the evidence; it translates the tool so that a spectator, a schoolkid, a hardware lab, and an auditor can all use the same instrument at their own depth. Unimplemented proposals wait on a labeled shelf. The dashboard remains what it has always been: a window on the work — now with the door open.
