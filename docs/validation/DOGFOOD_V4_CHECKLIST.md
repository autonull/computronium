> **Historical record.** The web UI this document validates was removed on
> 2026-09-25 (`comp dashboard`, `computronium/ui/**`). Nothing here is
> runnable; retained as the design/validation record only. The surviving
> read path is `computronium/autoscientist/campaign_readers.py`, surfaced by
> `comp campaign report` and the daemon.

# V4 Screenshot Checklist + §1.1 Conformance + Chip States

**Scope**: Visual regression checklist and design system conformance for the Computronium Dashboard.

**Reference**: `docs/platform/dashboard.md` §1.1 (Panel Registry), `computronium/ui/design_tokens.py`, `tests/ui/test_dashboard_screenshots.py::TestVisualVerification`

---

## Part 1: Screenshot Capture Matrix

**Command**: `uv run pytest tests/ui/test_dashboard_screenshots.py --capture-screenshots -v`

**Output**: `screenshots/dashboard/{panel}_{lens}_{register}_{state}.png`

### Required Combinations (20 panels × 2 registers × 2 states = 80 base + lens variants)

| Panel | Lenses | Registers | States | Count |
|-------|--------|-----------|--------|-------|
| **Map** | map, tradeoffs, gallery | explorer, lab | populated, empty | 12 |
| **Repair** | defects, maturation | explorer, lab | populated, empty | 8 |
| **Console** | (none) | explorer, lab | populated, empty | 4 |
| **Composer** | (none) | explorer, lab | populated, empty | 4 |
| **Record** | history, ledger, lessons | explorer, lab | populated, empty | 12 |
| **Overview** | (full dashboard) | explorer, lab | populated | 2 |

**Total**: 42 unique screenshots minimum

### CI Subset (Fast Gate)

Run on every PR. Full matrix on release tag.

| Priority | Screenshots | Rationale |
|----------|-------------|-----------|
| **P0** | `map_map_explorer_populated`, `map_tradeoffs_lab_populated`, `map_gallery_explorer_populated` | Core value prop |
| **P0** | `repair_defects_explorer_populated`, `repair_maturation_lab_populated` | Fault visibility |
| **P0** | `console_explorer_populated`, `record_history_explorer_populated` | Daily workflow |
| **P1** | All `_empty` variants | Empty state UX |
| **P1** | All `_lab` variants | Technical register |
| **P2** | Composer, Record:Ledger/Lessons | Advanced features |

---

## Part 2: §1.1 Conformance Checklist

**Source**: `docs/platform/dashboard.md` §1.1 (Panel Registry table)

### Panel Registry Completeness

| # | Key | Label | Visible | Implemented | Tested | Screenshot |
|---|-----|-------|---------|-------------|--------|------------|
| 0 | `discovery_map` | Atlas map + table | both | ✓ | ✓ | map_map_* |
| 1 | `tradeoffs` | Pareto trade-offs | both | ✓ | ✓ | map_tradeoffs_* |
| 2 | `repair_bench` | Defect funnel | both | ✓ | ✓ | repair_defects_* |
| 3 | `health` | Health gauge + loss curve | both | ✗ | — | — |
| 4 | `campaigns` | Campaign cards | both | ✗ | — | — |
| 5 | `preview` | Preview shelf | both | ✗ | — | — |
| 6 | `region_naming` | Region labels | both | ✗ | — | — |
| 7 | `team` | Team wall | both | ✗ | — | — |
| 8 | `activity_feed` | Live event feed | both | ✗ | — | — |
| 9 | `field_reports` | Field reports | both | ✗ | — | — |
| 10 | `constitution` | Constitution health | lab | ✗ | — | — |
| 11 | `lineage` | Lineage viewer | lab | ✗ | — | — |
| 12 | `episodes` | Episode timeline | lab | ✗ | — | — |
| 13 | `progress` | Badges/quests/records | gamify | ✗ | — | — |
| 14 | `workshop` | Workshop actions | ui-actions | ✗ | — | — |
| 15 | `probe_analytics` | Probe analytics | lab | ✗ | — | — |
| 16 | `stagnation` | Stagnation dashboard | lab | ✗ | — | — |
| 17 | `genome_health` | Genome health | lab | ✗ | — | — |
| 18 | `mutations` | Mutation explorer | lab | ✗ | — | — |
| 19 | `veto_log` | Veto log | lab | ✗ | — | — |

**Current Implementation**: 5 core panels (Map, Repair, Console, Composer, Record) with lenses.
**Gap**: 15 panels from §1.1 not yet implemented. Track as follow-up work.

### Current 5-Panel + Lens Mapping (Implemented)

| Panel Key | Label | Icon | Lenses | Default Lens | Adapter |
|-----------|-------|------|--------|--------------|---------|
| `map` | Map | map | map, tradeoffs, gallery | map | discovery_map |
| `repair` | Repair | build | defects, maturation | defects | repair_bench |
| `console` | Console | terminal | — | — | (WS + snapshot) |
| `composer` | Composer | tune | — | — | None |
| `record` | Record | history | history, ledger, lessons | history | (derived) |

---

## Part 3: Design Token Conformance (Automated)

**Tests**: `TestVisualVerification` in `tests/ui/test_dashboard_screenshots.py`

| Token Category | Test | Requirement | Status |
|----------------|------|-------------|--------|
| **Spacing** | `test_design_tokens_4px_grid` | All `SPACING` values multiples of 0.25rem (4px) | ✓ |
| **Typography** | `test_monospace_data_font_stack` | `mono`=0.875rem (14px), `mono_sm`=0.75rem (12px) | ✓ |
| **Semantic Colors** | `test_semantic_colors_defined` | success, warning, danger, info, neutral, secondary all `#...` | ✓ |
| **Transitions** | `test_transition_fast_150ms` | `fast` ≤ 150ms | ✓ |
| **Reduced Motion** | `test_reduced_motion_respects_preference` | `@media (prefers-reduced-motion: reduce)` → `transition-duration: 0.01ms` | ✓ |
| **High Contrast** | `test_high_contrast_media_query` | `@media (prefers-contrast: high)` exists | ✓ |
| **Quiet Density** | `test_quiet_mode_density` | Explorer=`comfortable`, Lab=`compact` | ✓ |

**All 7 automated checks passing.**

---

## Part 4: Status Chip State Matrix

**Component**: `computronium/ui/components/status_chip.py::StatusChipData`

### States

| State | Trigger | Chip Label | Icon | Color | Deep Link |
|-------|---------|------------|------|-------|-----------|
| **Running** | Daemon WS connected + recent heartbeat | `Running` | `play_circle` | success | `map:map` |
| **Idle** | No daemon, polling only | `Idle` | `pause_circle` | neutral | `map:map` |
| **Offline** | Daemon configured but WS disconnected > 30s | `Offline` | `cloud_off` | danger | `repair:defects` |
| **Stalled** | Heartbeat > 2× poll interval | `Stalled` | `hourglass_top` | warning | `console:base` |
| **Empty** | 0 cells in KB | `Empty` | `inventory` | info | `composer:base` |
| **Error** | KB corrupt / atlas failed | `Error` | `error` | danger | `repair:defects` |

### Quiet Mode (`--quiet`)

| State | Label | Detail |
|-------|-------|--------|
| Running | `●` | (dot only) |
| Idle | `○` | |
| Offline | `✕` | |
| Stalled | `◷` | |
| Empty | `○` | |
| Error | `!` | |

### Chip State Transitions (Tested in `test_dashboard_fault_injection.py`)

| From → To | Trigger | Test |
|-----------|---------|------|
| Running → Offline | Daemon WS disconnect | `test_daemon_disconnect_chip_transitions_to_offline` |
| Offline → Running | Daemon WS reconnect | `test_daemon_reconnect_chip_transitions_to_running` |
| Any → Offline | No heartbeat > 30s | `test_no_heartbeat_chip_shows_offline` |
| Running → Stalled | Heartbeat lag > 2× poll | (manual) |
| Empty → Running | First cell measured | (manual) |

---

## Part 5: Visual Regression Thresholds

### Perceptual Diff (Future: `pixelmatch` / `playwright-visual`)

| Metric | Threshold | Tool |
|--------|-----------|------|
| Pixel difference | ≤ 0.1% | `pixelmatch` |
| Structural similarity (SSIM) | ≥ 0.99 | `opencv` |
| Color histogram delta | ≤ 2% | `opencv` |

### Current: Automated Token Validation Only

No pixel baselines (per D4 lock hygiene — no pixel baselines in CI).
Visual verification = design token compliance + headless lens rendering + axe a11y.

---

## Part 6: Accessibility Screenshot Checklist

**Run**: `uv run pytest tests/a11y/test_ux_l5_a11y.py -v`

| Check | Automated | Manual |
|-------|-----------|--------|
| axe-core: 0 critical, 0 serious | ✓ | — |
| Keyboard crawl: all interactive reachable | ✓ | — |
| Focus visible on all buttons/links | — | ✓ |
| Color contrast ≥ 4.5:1 (AA) | — | ✓ |
| Color contrast ≥ 3:1 (AA large text) | — | ✓ |
| Reduced motion: no animation | ✓ | ✓ |
| High contrast: colors override | ✓ | ✓ |
| Screen reader: ARIA labels on icon buttons | — | ✓ |
| Screen reader: live region for toasts | — | ✓ |

---

## Part 7: Grayscale Distinguishability (UX-L6)

**Test**: `tests/ui/test_ux_l6_grayscale.py::test_populated_vs_empty_distinguishable_in_grayscale`

| Requirement | Status |
|-------------|--------|
| Populated vs empty dashboard distinguishable in grayscale | ✓ |
| Semantic colors (success/warning/danger) distinguishable in grayscale | ✓ |
| Chip states distinguishable in grayscale | ✓ |

---

## Part 8: Execution Checklist

```bash
# 1. Capture full screenshot matrix (local, ~25 min)
uv run pytest tests/ui/test_dashboard_screenshots.py --capture-screenshots -v

# 2. Run automated visual verification (CI fast gate)
uv run pytest tests/ui/test_dashboard_screenshots.py::TestVisualVerification -v
uv run pytest tests/ui/test_dashboard_screenshots.py::TestDashboardLensRendering -v
uv run pytest tests/ui/test_ux_l6_grayscale.py -v
uv run pytest tests/a11y/test_ux_l5_a11y.py -v

# 3. Manual chip state verification
#    - Start daemon, verify Running
#    - Kill daemon, verify Offline
#    - Restart daemon, verify Running
#    - Empty root, verify Empty
#    - Corrupt KB, verify Error

# 4. Manual §1.1 conformance review
#    - Compare implemented panels vs §1.1 table
#    - Document gaps in DOGFOOD_V4_GAPS.md

# 5. Grayscale check (manual)
#    - Enable OS grayscale filter
#    - Verify all states distinguishable
```

---

## Part 9: Known Gaps (Post-V4)

| Gap | Priority | Tracking |
|-----|----------|----------|
| 15 panels from §1.1 not implemented | P1 | Follow-up epic |
| Pixel-diff regression not in CI | P2 | Requires baseline mgmt |
| Composer panel empty state screenshot | P1 | Add to matrix |
| Record:Ledger/Lessons populated screenshots | P1 | Need seeded KB |
| Multi-root overview screenshots | P2 | Nice to have |

---

## Sign-Off

| Check | Reviewer | Date | Status |
|-------|----------|------|--------|
| Screenshot matrix captured (P0) | | | |
| §1.1 conformance documented | | | |
| Design tokens all passing | | | |
| Chip state matrix verified | | | |
| Accessibility (axe + keyboard) | | | |
| Grayscale distinguishability | | | |

**V4 Pass**: All P0 screenshots captured, all 7 token tests pass, chip states verified, axe 0 critical/serious, grayscale pass.