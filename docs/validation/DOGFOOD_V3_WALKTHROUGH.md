# V3 UX Walkthrough

**Scope**: Usability validation for the Computronium Dashboard across three personas and Nielsen's 10 heuristics.

**Registers**: Explorer (FK ≤ 8) and Lab (technical)

---

## Part 1: LLM Copy Clarity Audit

**Goal**: All user-facing text is clear, actionable, and register-appropriate.

### Method

1. Extract all glossary keys: `uv run python -m computronium.scripts.lint_readability`
2. For each key, verify:
   - Explorer copy: FK grade ≤ 8, active voice, ≤ 20 words
   - Lab copy: precise terminology, includes units, ≤ 30 words
   - No jargon in Explorer without glossary link
   - No ambiguous pronouns ("it", "this", "that" without antecedent)

### Checklist

| Area | Keys | Explorer FK | Lab Precision | Status |
|------|------|-------------|---------------|--------|
| Header / Status Chip | `status_running`, `status_idle`, `status_offline`, `cells_count`, `bursts_count` | | | |
| Panel Tabs | `map`, `repair`, `console`, `composer`, `record` | | | |
| Map Lenses | `map_lens_map`, `map_lens_tradeoffs`, `map_lens_gallery` | | | |
| Repair Lenses | `repair_lens_defects`, `repair_lens_maturation` | | | |
| Record Lenses | `record_lens_history`, `record_lens_ledger`, `record_lens_lessons` | | | |
| Pareto Selector | `pareto_label`, `pareto_accuracy_walltime`, `pareto_accuracy_params` | | | |
| Empty States | `empty_no_cells`, `empty_no_defects`, `empty_no_history` | | | |
| Error States | `error_kb_corrupt`, `error_umap_failed`, `error_daemon_unreachable` | | | |
| Actions | `action_unquarantine`, `action_retry`, `action_copy_deep_link` | | | |
| Tooltips | `tooltip_palette`, `tooltip_mode_toggle`, `tooltip_root_selector` | | | |
| Field Reports | `report_breakthrough`, `report_cascade`, `report_completion` | | | |
| Gamification | `badge_learner`, `quest_explorer`, `record_pareto_optimal` | | | |

### Automated Checks

```bash
# FK grade report (informational — short labels are known false-positives)
uv run python scripts/lint_readability.py

# Glossary completeness
uv run python -c "
from computronium.ui.glossary_service import get_glossary_service
gs = get_glossary_service()
for reg in ['explorer', 'lab']:
    missing = [k for k in gs.all_keys() if not gs.get(k, reg)]
    print(f'{reg}: {len(missing)} missing')
"
```

---

## Part 2: Three-Persona Walkthrough

### Persona 1: Maya — ML Researcher (Explorer Register)

**Background**: PhD student, runs experiments daily, knows ML but not infrastructure. Wants to "see what worked."

**Scenario**: Launched a 200-cell broad map overnight. Opens dashboard to find the best cells.

| Step | Action | Expected | Pain Points |
|------|--------|----------|-------------|
| 1 | `comp dashboard --root artifacts/broad_map` | Opens in <4s, shows "Running 200 cells" | |
| 2 | Scan Map panel | Sees islands (clusters) and voids (gaps) | |
| 3 | Click largest island | Cell drawer opens with metrics | |
| 4 | Click "Pareto: accuracy + walltime" | Strip updates, top cells highlighted | |
| 5 | Click top Pareto cell | Deep link copied, can share with advisor | |
| 6 | Switch to Repair tab (2) | Sees defect funnel: 3 quarantined, 12 voids | |
| 7 | Click quarantined defect | Traceback + "Unquarantine" button | |
| 8 | Switch to Record tab (5) → Lessons | Sees "avoid spike_integration+prediction" | |
| 9 | Close browser, reopen via deep link | Restores to exact panel/lens/cell | |

**Success Criteria**: Completes all steps without docs, < 5 min, zero "wait, what does this mean?"

---

### Persona 2: Dr. Chen — Algorithm Designer (Lab Register)

**Background**: Senior researcher, designs new credit assignment rules. Needs technical depth: σ_max(J), credit alignment, spectral radius.

**Scenario**: Testing a new `RoutingPlasticity` variant. Wants to compare Pareto fronts across objectives.

| Step | Action | Expected | Pain Points |
|------|--------|----------|-------------|
| 1 | `comp dashboard --root artifacts/broad_map --ui-mode lab` | Lab copy, all 20 panels visible | |
| 2 | Map → Trade-offs lens | Pareto strip with 7 preset pairs | |
| 3 | Select "stability + plasticity" | ρ(J_F) vs ψ_capacity frontier | |
| 4 | Hover Pareto cell | Tooltip: σ_max, credit_align, trace_var | |
| 5 | Console tab (3) | Live loss curve + event feed | |
| 6 | Record → Ledger lens | Beliefs with calibration scores | |
| 7 | Constitution panel (lab-only) | Frozen-θ audit status | |
| 8 | Lineage panel (lab-only) | Episode timeline with ψ diffs | |
| 9 | Export snapshot JSON | Complete state for paper appendix | |

**Success Criteria**: Finds technical data in ≤ 2 clicks, no Explorer copy pollution, exports work.

---

### Persona 3: Alex — Platform Engineer (Lab Register, `--ui-actions on`)

**Background**: Maintains the continuous pipeline. Needs to debug stalled bursts, check daemon health, manage multi-root.

**Scenario**: Daemon reports "stalled" — needs to diagnose and restart.

| Step | Action | Expected | Pain Points |
|------|--------|----------|-------------|
| 1 | `comp dashboard --root artifacts/map1,artifacts/map2 --daemon-url http://localhost:8940` | Multi-root selector + Start/Pause/Stop bar | |
| 2 | Switch to map2 root | All panels update, atlas refits | |
| 3 | Health panel (lab) | Gauge: "Stalled — no heartbeat 4m" | |
| 4 | Console → Field Reports | "Cascade: burst 3 proposals rejected" | |
| 5 | Click daemon badge | WS status: events connected, telemetry lag 12s | |
| 6 | Workshop panel (`--ui-actions on`) | "Restart burst" button enabled | |
| 7 | Click Restart → confirm | Daemon resumes, health → "Running" | |
| 8 | Veto Log panel | New veto entry with timestamp | |

**Success Criteria**: Diagnoses + resolves in < 3 min, all actions auditable, no silent failures.

---

## Part 3: Nielsen's 10 Heuristics Evaluation

### 1. Visibility of System Status

| Check | Explorer | Lab | Status |
|-------|----------|-----|--------|
| Status chip always visible (header) | ✓ | ✓ | |
| Live indicator (pulse/dot) on WS connect | ✓ | ✓ | |
| Polling timestamp "Updated Xs ago" | ✓ | ✓ | |
| Loading skeletons on atlas/panel switch | ✓ | ✓ | |
| Burst progress in Console ticker | ✓ | ✓ | |

### 2. Match Between System and Real World

| Check | Explorer | Lab | Status |
|-------|----------|-----|--------|
| "Islands/Voids" metaphor explained in glossary | ✓ | — | |
| "Pareto" → "Best trade-offs" in Explorer | ✓ | — | |
| "Maturation L0/L1/L2" → "Draft/Verified/Claim-grade" | ✓ | — | |
| Technical terms (σ_max, ψ) only in Lab | — | ✓ | |
| Units always shown (ms, MB, pp, ×) | ✓ | ✓ | |

### 3. User Control and Freedom

| Check | Explorer | Lab | Status |
|-------|----------|-----|--------|
| Panel tabs (1–5) always accessible | ✓ | ✓ | |
| Command palette (⌘K) global escape hatch | ✓ | ✓ | |
| Deep links bookmarkable + shareable | ✓ | ✓ | |
| "Reset view" on each panel | ✓ | ✓ | |
| Multi-root switch without reload | ✓ | ✓ | |
| Unquarantine / retry actions reversible | ✓ | ✓ | |

### 4. Consistency and Standards

| Check | Explorer | Lab | Status |
|-------|----------|-----|--------|
| 4px grid on all spacing | ✓ | ✓ | |
| Mono 14px / 12px for all data | ✓ | ✓ | |
| Semantic colors: success/warning/danger/info | ✓ | ✓ | |
| Transition ≤ 150ms (fast) | ✓ | ✓ | |
| Reduced motion respected | ✓ | ✓ | |
| High contrast mode works | ✓ | ✓ | |
| Quiet density: Explorer comfortable, Lab compact | ✓ | ✓ | |

### 5. Error Prevention

| Check | Explorer | Lab | Status |
|-------|----------|-----|--------|
| `--daemon-url` validated on launch | — | ✓ | |
| Config hot-reload warns on parse error | — | ✓ | |
| Empty states show actionable buttons | ✓ | ✓ | |
| Confirm dialog on destructive actions | ✓ | ✓ | |
| KB corruption → graceful degradation toast | ✓ | ✓ | |

### 6. Recognition Rather Than Recall

| Check | Explorer | Lab | Status |
|-------|----------|-----|--------|
| Glossary tooltip on every technical term | ✓ | ✓ | |
| Pareto presets labeled (not raw objectives) | ✓ | ✓ | |
| Lens icons + labels (not icons only) | ✓ | ✓ | |
| Cell cards show coordinate summary | ✓ | ✓ | |
| History/ledger/lessons separated by tab | ✓ | ✓ | |

### 7. Flexibility and Efficiency of Use

| Check | Explorer | Lab | Status |
|-------|----------|-----|--------|
| Hotkeys 1–5 for panels | ✓ | ✓ | |
| ⌘K command palette | ✓ | ✓ | |
| URL hash deep links | ✓ | ✓ | |
| Pareto selector keyboard navigable | ✓ | ✓ | |
| Table sort/filter (virtualized) | — | ✓ | |

### 8. Aesthetic and Minimalist Design

| Check | Explorer | Lab | Status |
|-------|----------|-----|--------|
| No decorative elements (pure function) | ✓ | ✓ | |
| Single primary action per panel | ✓ | ✓ | |
| Whitespace ≥ 4px grid | ✓ | ✓ | |
| No redundant labels (icon + text → icon w/ tooltip) | ✓ | ✓ | |
| Quiet mode removes chrome | ✓ | ✓ | |

### 9. Help Users Recognize, Diagnose, Recover from Errors

| Check | Explorer | Lab | Status |
|-------|----------|-----|--------|
| Error toasts: what + why + action | ✓ | ✓ | |
| KB corrupt → "Showing cached data" banner | ✓ | ✓ | |
| Daemon offline → chip shows "Offline" + retry | ✓ | ✓ | |
| UMAP fail → "Showing t-SNE fallback" notice | ✓ | ✓ | |
| Log tail empty → "No logs yet" not blank | ✓ | ✓ | |

### 10. Help and Documentation

| Check | Explorer | Lab | Status |
|-------|----------|-----|--------|
| Glossary searchable via ⌘K | ✓ | ✓ | |
| `comp dashboard --help` complete | ✓ | ✓ | |
| `docs/platform/dashboard.md` current | ✓ | ✓ | |
| Inline tooltips on all icon buttons | ✓ | ✓ | |
| "Showing first N rows" on capped tables | ✓ | ✓ | |

---

## Execution Checklist

```bash
# 1. Automated copy audit
uv run python scripts/lint_readability.py

# 2. Automated heuristic checks (subset)
uv run pytest tests/ui/test_ux_l6_grayscale.py -v
uv run pytest tests/a11y/test_ux_l5_a11y.py -v
uv run pytest tests/perf/test_dashboard_perf.py -v

# 3. Manual persona walkthroughs (3 × 15 min)
#    - Maya (Explorer)
#    - Dr. Chen (Lab)
#    - Alex (Lab + --ui-actions --daemon-url)

# 4. Document findings in DOGFOOD_V3_FINDINGS.md
```

---

## Sign-Off

| Persona | Walker | Date | Critical Issues | Score (1-5) |
|---------|--------|------|-----------------|-------------|
| Maya (Explorer) | | | | |
| Dr. Chen (Lab) | | | | |
| Alex (Platform) | | | | |

| Heuristic | Score (1-5) | Notes |
|-----------|-------------|-------|
| 1. Visibility | | |
| 2. Real World Match | | |
| 3. Control/Freedom | | |
| 4. Consistency | | |
| 5. Error Prevention | | |
| 6. Recognition | | |
| 7. Flexibility | | |
| 8. Aesthetics | | |
| 9. Error Recovery | | |
| 10. Help/Docs | | |

**V3 Pass**: All personas ≥ 4, all heuristics ≥ 3, zero critical issues.