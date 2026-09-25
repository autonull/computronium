> **Historical record.** The web UI this document validates was removed on
> 2026-09-25 (`comp dashboard`, `computronium/ui/**`). Nothing here is
> runnable; retained as the design/validation record only. The surviving
> read path is `computronium/autoscientist/campaign_readers.py`, surfaced by
> `comp campaign report` and the daemon.

# V1 Dogfood Validation Rubric

**Scope**: End-to-end workflow validation for the Computronium Dashboard (`comp dashboard`).

**Workflow**: Compose → Configure → Launch → Insight → Diagnose → Audit

**Registers**: Explorer (plain language, FK ≤ 8) and Lab (technical)

---

## Rubric Scoring

| Score | Meaning |
|-------|---------|
| **4** | Exemplary — zero friction, delightful, exceeds expectations |
| **3** | Pass — works as intended, minor polish gaps only |
| **2** | Marginal — functional but confusing/slow/inconsistent |
| **1** | Fail — broken, misleading, or blocks the workflow |
| **0** | Missing — feature not implemented |

**Gate**: All stages must score ≥ 3 for V1 pass. Any 1 or 0 blocks release.

---

## Stage 1: Compose (Campaign Authoring)

**Goal**: User creates a campaign config that expresses their intent.

| Criterion | Explorer | Lab | Weight |
|-----------|----------|-----|--------|
| 1.1 YAML schema is discoverable (examples, comments, LSP) | ✓ | ✓ | Required |
| 1.2 `comp campaign validate` catches errors pre-launch | ✓ | ✓ | Required |
| 1.3 Objective presets documented and selectable | ✓ | ✓ | Required |
| 1.4 Multi-objective syntax (`accuracy,walltime,params`) works | ✓ | ✓ | Required |
| 1.5 Template gallery shows canonical coordinates | ✓ | ✓ | Nice |
| 1.6 Copy explains *why* each axis matters (not just *what*) | ✓ | — | Required |

**Pass threshold**: All Required = 3+, Nice ≥ 2

---

## Stage 2: Configure (Dashboard Launch)

**Goal**: User starts the dashboard pointed at their campaign root.

| Criterion | Explorer | Lab | Weight |
|-----------|----------|-----|--------|
| 2.1 `comp dashboard --root <path>` opens in ≤ 4 s (p95) | ✓ | ✓ | Required |
| 2.2 `--ui-mode explorer|lab|auto` respected immediately | ✓ | ✓ | Required |
| 2.3 Multi-root comma list shows root selector in header | ✓ | ✓ | Required |
| 2.4 `--daemon-url` enables Start/Pause/Stop bar + live badge | — | ✓ | Required |
| 2.5 `--no-open` works for headless/CI | — | ✓ | Required |
| 2.6 `--gamify off` / `--ui-actions off` kill switches work | — | ✓ | Required |
| 2.7 No console errors on clean launch (JS, WS, 404s) | ✓ | ✓ | Required |

**Pass threshold**: All Required = 3+

---

## Stage 3: Launch (First Paint → Interactive)

**Goal**: Dashboard becomes fully interactive with live data.

| Criterion | Explorer | Lab | Weight |
|-----------|----------|-----|--------|
| 3.1 Status chip shows "Running" + cell count within 2 s | ✓ | ✓ | Required |
| 3.2 Atlas UMAP renders (or t-SNE fallback) with loading state | ✓ | ✓ | Required |
| 3.3 Panel tabs (1–5 hotkeys) all render without error | ✓ | ✓ | Required |
| 3.4 Command palette (⌘K) opens and lists all actions | ✓ | ✓ | Required |
| 3.5 Pareto selector populates with objective presets | — | ✓ | Required |
| 3.6 WebSocket connects (if daemon) or polling starts | — | ✓ | Required |
| 3.7 No layout shift after first paint (CLS ≈ 0) | ✓ | ✓ | Required |

**Pass threshold**: All Required = 3+

---

## Stage 4: Insight (Pattern Recognition)

**Goal**: User spots meaningful patterns in the campaign data.

| Criterion | Explorer | Lab | Weight |
|-----------|----------|-----|--------|
| 4.1 **Map** — Islands/voids atlas shows clusters + outliers | ✓ | ✓ | Required |
| 4.2 **Map:Trade-offs** — Pareto strip updates on objective change | — | ✓ | Required |
| 4.3 **Map:Gallery** — Cell cards render with key metrics | ✓ | ✓ | Required |
| 4.4 **Repair:Defects** — Funnel shows quarantined vs voids | ✓ | ✓ | Required |
| 4.5 **Repair:Maturation** — L0→L1→L2 promotion visible | — | ✓ | Required |
| 4.6 **Console** — Live event feed + loss curve + field reports | ✓ | ✓ | Required |
| 4.7 **Record:History** — Chronological experiment log | ✓ | ✓ | Required |
| 4.8 **Record:Ledger** — Beliefs + gates + calibration | — | ✓ | Required |
| 4.9 **Record:Lessons** — Graveyard/voids → actionable lessons | ✓ | ✓ | Required |
| 4.10 Lens switching preserves scroll/selection state | ✓ | ✓ | Nice |

**Pass threshold**: All Required = 3+, Nice ≥ 2

---

## Stage 5: Diagnose (Root Cause)

**Goal**: User drills from pattern to cause.

| Criterion | Explorer | Lab | Weight |
|-----------|----------|-----|--------|
| 5.1 Click island → cell detail drawer opens | ✓ | ✓ | Required |
| 5.2 Cell drawer shows: coordinate, metrics, hyperparams, logs | — | ✓ | Required |
| 5.3 Defect card → traceback + "unquarantine" action | ✓ | ✓ | Required |
| 5.4 Pareto cell → deep link copies to clipboard | ✓ | ✓ | Required |
| 5.5 Status chip deep link navigates to correct panel/lens | ✓ | ✓ | Required |
| 5.6 Log tail loads without freezing UI (lazy/virtualized) | ✓ | ✓ | Required |
| 5.7 "Showing first N rows" badge on capped tables | ✓ | ✓ | Required |

**Pass threshold**: All Required = 3+

---

## Stage 6: Audit (Governance)

**Goal**: User verifies claims and exports evidence.

| Criterion | Explorer | Lab | Weight |
|-----------|----------|-----|--------|
| 6.1 `comp dashboard --rebuild-ui-state` replays event log | — | ✓ | Required |
| 6.2 CEEC ledger accessible via Record:Ledger lens | — | ✓ | Required |
| 6.3 Badge/quest/record criteria transparent (gamify on) | ✓ | ✓ | Nice |
| 6.4 Export snapshot (JSON/HTML) for sharing | — | ✓ | Nice |
| 6.5 "Copy deep link" preserves full panel/lens/filter state | ✓ | ✓ | Required |

**Pass threshold**: All Required = 3+, Nice ≥ 2

---

## Cross-Cutting Concerns (Apply to All Stages)

| Concern | Explorer | Lab | Weight |
|---------|----------|-----|--------|
| **A11y**: axe 0 critical/serious; keyboard crawl passes | ✓ | ✓ | Required |
| **Perf**: Panel switch p95 ≤ 500 ms; palette ≤ 1 s | ✓ | ✓ | Required |
| **Visual**: 4px grid, mono 14/12px, semantic colors, ≤150ms motion | ✓ | ✓ | Required |
| **Reduced motion**: `prefers-reduced-motion` disables transitions | ✓ | ✓ | Required |
| **High contrast**: `prefers-contrast: high` overrides colors | ✓ | ✓ | Required |
| **Quiet density**: Explorer=comfortable, Lab=compact | ✓ | ✓ | Required |
| **Copy clarity**: FK grade ≤ 8 (Explorer); precise terminology (Lab) | ✓ | — | Required |
| **Glossary**: Every technical term has explorer + lab definition | ✓ | ✓ | Required |
| **Error states**: Empty, loading, error, offline all have UI | ✓ | ✓ | Required |
| **Deep links**: URL hash restores panel/lens/selection | ✓ | ✓ | Required |

---

## Execution Checklist

```bash
# 1. Seed a campaign root
uv run comp continuous --target-cells 50 --limit-batches 10 --root /tmp/dogfood_v1

# 2. Launch dashboard (Explorer)
uv run comp dashboard --root /tmp/dogfood_v1 --ui-mode explorer --no-open

# 3. Launch dashboard (Lab)
uv run comp dashboard --root /tmp/dogfood_v1 --ui-mode lab --no-open

# 4. Run automated checks
uv run pytest tests/ui/test_dashboard_render.py -v
uv run pytest tests/a11y/test_ux_l5_a11y.py -v
uv run pytest tests/perf/test_dashboard_perf.py -v
uv run pytest tests/ui/test_ux_l6_grayscale.py -v

# 5. Manual walkthrough (this rubric)
#    Score each criterion, document gaps, file issues
```

---

## Sign-Off

| Role | Name | Date | Score Summary |
|------|------|------|---------------|
| Product | | | |
| UX | | | |
| Eng Lead | | | |

**V1 Pass**: All stages ≥ 3, all Required cross-cutting = 3+, no 0/1 scores.