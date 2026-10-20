# TODO68 Gap Analysis — Mental Simulation of Development

**Purpose**: Discover functionality gaps, integration issues, and downstream surprises before implementation.

---

## Phase 1: Data Layer — Critical Gaps

### 1.1 `DashboardConfig` Missing `demo_mode`
**Location**: `computronium/experiment/execution/dashboard/web.py:29-39`
**Issue**: Dataclass has `campaign_queue` but no `demo_mode` or `store_path` for direct store access.
**Fix**: Add `demo_mode: bool = False` and ensure `store_path` is used when `demo_mode=True`.

### 1.2 No `RecordStore.latest_run_id()` Method
**Location**: `computronium/experiment/evidence/store.py`
**Issue**: Store has `runs` table but no public method to fetch latest run_id. Dashboard needs this for demo mode.
**Fix**: Add `def latest_run_id(self) -> str | None` method querying `SELECT run_id FROM runs ORDER BY started_at DESC LIMIT 1`.

### 1.3 `_get_dashboard_view()` Requires Reusing Internal Report Logic
**Location**: Multiple modules
**Issue**: Dashboard must replicate report generation logic but as API response. Key functions to reuse:
- `chance_level()` → `report.py:831` (needs task_registry)
- `_compute_ablation_table()` → `report.py:1304` (pure function, reusable)
- `compute_pareto_frontier()` → `analysis/pareto_analysis.py:44` (needs Record objects)
- `derive_limitations()` → `evidence/limitations.py:282` (needs achieved seed counts)
- `contrast_groups()` → `report.py:848` (for valid ablation groups)

**Gap**: These functions are not in a shared "dashboard data" module. They're scattered across `report.py`, `claims.py`, `limitations.py`, `pareto_analysis.py`.

### 1.4 Server-Side Chart Rendering — Matplotlib Dependency
**Issue**: `matplotlib` not in `pyproject.toml` dependencies. Dashboard needs it for SVG generation.
**Fix**: Add `matplotlib` to `pyproject.toml` (optional extra or core). Use `Agg` backend.

### 1.5 Demo Detection Logic — Store Path vs Run Profile
**Location**: `computronium/experiment/surface/cli.py:_cmd_dashboard()`
**Current**: Detects `demo.duckdb` by path string.
**Problem**: User could name store differently. Better: check if latest run has `spec.profile == "demo"`.
**Fix**: Query store for latest run, inspect `spec.profile`.

### 1.6 `--open-browser` Flag Implementation
**Location**: `cli.py` argument parser + `_cmd_dashboard()`
**Need**: Add argument, then `import webbrowser; webbrowser.open(f"http://{host}:{port}")` after server starts.
**Caveat**: Server runs blocking (`asyncio.run(run_dashboard())`). Browser open must happen before or in background thread.

### 1.7 Read-Only Store Access
**Issue**: Dashboard opens store in read-write mode by default. Concurrent with running experiment → lock contention.
**Fix**: `StoreConfig(read_only=True)` when `demo_mode=True`.

---

## Phase 2: Dashboard View — Template & Visualization Gaps

### 2.1 Complete Template Rewrite (876 lines → ~400 lines)
**Current**: Sidebar navigation, 6 panels (overview, queue, resources, campaigns, cost, modal)
**Target**: Single-page, 4-panel layout (Discovery Map, Cell Drawer, Plotter, Claims)
**Gap**: No existing CSS for:
- Fog-of-war grid (legal/measured/void cells)
- Progress bars per cell (████████░░)
- Cell drawer detail panel
- Plotter with embedded SVG
- Live rail (bottom log stream)

### 2.2 Fog-of-War / Discovery Map Visualization
**Requirement**: Show 6-axis primitive matrix with:
- ● measured (filled, n=5, VL1)
- ○ legal but unmeasured (show price)
- ▨ void (illegal combination)
- [wander][exploit][contrast][surprise-me] buttons (v1: visual only)

**Data needed**: `SearchSpace` from `kernel/search_space.py` to know legal combinations.
**Gap**: Dashboard only has store records, not the full search space. Need to reconstruct or query `search_space_from_spec()`.

### 2.3 HTMX Polling vs WebSocket
**Current**: WebSocket for real-time updates.
**Demo mode**: Static data → HTMX polling `/api/dashboard` every 2s is simpler.
**Gap**: Template JS needs rewrite — remove WebSocket, add `hx-get="/api/dashboard" hx-trigger="every 2s"`.

### 2.4 Server-Side SVG Embedding
**Approach**: `_get_dashboard_view()` returns base64 SVG strings in `figures_view`.
**Template**: `<img src="data:image/svg+xml;base64,{{ figures.pareto }}">`
**Gap**: Need to generate 3-4 charts per request. Performance: cache charts keyed by run_id.

### 2.5 Color Palette Alignment
**Current template**: `--accent-blue: #58a6ff`, `--accent-yellow: #d29922`, etc.
**Visualization/_style.py**: `COLOR_ARM = "#2f6f4f"`, `COLOR_CHANCE = "#888888"`
**Gap**: Two separate palettes. Dashboard should use centralized `_style.py` extended with dashboard-specific colors.

---

## Phase 3: Visual Polish — CSS/UX Gaps

### 3.1 Glowing Monospace Metrics
**CSS**: `text-shadow: 0 0 8px #d4a843` on `.font-mono` metric values.
**Gap**: Need to ensure contrast against near-black background.

### 3.2 Badge System
**Needed badges**:
- `VL1` (verification level) — green pill
- `[at chance]` — red pill
- `INSUFFICIENT` — amber banner
- `EXPLORATORY` / `PREREGISTERED` — mode chip

**Gap**: No existing badge components in template. Must design from scratch.

### 3.3 Live Rail (Bottom Log Stream)
**Content**: `[OK] compose joint system…` `[OK] settle energy…` `[WARN] control at chance`
**Source**: Pipeline stage logs from run. Not stored in records.
**Gap**: Demo mode has no live pipeline. Options:
- Static mock log (acceptable for v1)
- Query pipeline events if available (not implemented)

### 3.4 Footer: "Price of a Real Answer"
**Content**: `63 seeds/arm for d=0.5` — from pricing logic.
**Source**: `execution/pricing.py:price_plan()` → "63 seeds to a claim"
**Gap**: Need to expose pricing info in dashboard view.

---

## Phase 4: Screenshot & README — Automation Gaps

### 4.1 Playwright Dependency
**Not in pyproject.toml**. Need `playwright` + browser install (`playwright install chromium`).
**CI consideration**: Headless Chromium in CI for automated screenshots.

### 4.2 Screenshot Script Complexity
**Flow**:
1. Start dashboard server in background (subprocess)
2. Wait for `/api/dashboard` to return 200 with data
3. Launch Playwright, navigate to `http://localhost:8080`
4. Wait for HTMX polls to complete (charts rendered)
5. Screenshot at 1920×1080
6. Kill dashboard subprocess
7. Save to `docs/readme/assets/dashboard-hero.png`

**Gaps**:
- `docs/readme/assets/` directory may not exist
- Playwright async API vs sync script
- Dashboard server port conflict if already running

### 4.3 README Build Integration
**File**: `docs/readme/build_readme.py`
**Current**: Concatenates `title.md` + other sections.
**Need**: Ensure `title.md` references `assets/dashboard-hero.png` correctly (relative path from README root).

---

## Phase 5: Integration & Documentation Gaps

### 5.1 `CORE_COMMANDS` Update
**Location**: `cli.py:305-312`
**Current**: `{"run", "report", "status", "demo", "coverage", "gallery"}`
**Need**: Add `"dashboard"`

### 5.2 README "Start Here" Section
**Location**: `docs/readme/title.md` (generated into README)
**Current**: Shows 4 commands. Need 5th: `uv run comp dashboard --store demo.duckdb --open-browser`

### 5.3 `docs/DASHBOARD.md` Content
**Must explain**:
- What the Dashboard shows (Discovery Map, Cell Drawer, Plotter, Claims)
- How to read ablation tables, Pareto frontier, chance line
- INSUFFICIENT verdict meaning
- EXPLORATORY vs PREREGISTERED mode
- Keyboard shortcuts (if any)

---

## Cross-Cutting Technical Debt & Surprises

### A. Matplotlib in Headless Environment
**Risk**: `matplotlib.use('Agg')` must be called **before** `import matplotlib.pyplot`.
**Fix**: Set at module top in `web.py` or in chart rendering function.

### B. Single-Writer Lock Contention
**Scenario**: User runs `comp dashboard` while `comp run demo` is writing to same store.
**Result**: Dashboard blocks on `threading.RLock` in `RecordStore.__enter__`.
**Fix**: `StoreConfig(read_only=True)` for dashboard; catch `OperationalError` if DB locked.

### C. Record Payload Schema Variability
**Risk**: `record.payload` keys vary by objective. Dashboard assumes `val_acc`, `walltime_s`.
**Fix**: Use `OBJECTIVES_REGISTRY` to know measured metrics, or introspect payload keys dynamically.

### D. Demo Data Contract Stability
**Locked by**: `tests/acceptance/test_demo_script.py`
**Guarantees**: 4 credit arms, 5 seeds, L1, digits task, ~34s, INSUFFICIENT.
**Risk**: If demo profile changes, dashboard breaks. Dashboard must handle missing data gracefully.

### E. Colorblind-Safe Arm Palette
**Current**: No standardized palette for 4 credit arms.
**Need**: 4 distinct colors + chance line gray, works for deuteranopia/protanopia.
**Source**: `visualization/_style.py` has `COLOR_ARM`, `COLOR_CONTRAST` but only 2 colors.
**Fix**: Define 4-arm palette in `_style.py` (e.g., Okabe-Ito palette subset).

### F. Pricing Integration
**Function**: `execution/pricing.price_plan()` returns formatted lines.
**Gap**: Dashboard needs programmatic access to "63 seeds/arm" number, not just text.
**Fix**: Expose `PricePlan` dataclass with `seeds_per_arm` field.

### G. Verification Level (VL) Display
**Source**: `record.status.assessment_procedure_version` or `verification` module.
**Gap**: Dashboard shows `VL1` badge but records don't carry explicit VL. Derived from maturity + assessment procedure.
**Fix**: Map `maturity=l1` → `VL1`, `maturity=l2` → `VL4` (per verification taxonomy).

---

## Dependency Graph (Implementation Order)

```
1. pyproject.toml: add matplotlib, playwright (dev)
   │
   ├─→ 2. store.py: add latest_run_id()
   │
   ├─→ 3. visualization/_style.py: extend with dashboard palette
   │
   ├─→ 4. web.py: DashboardConfig.demo_mode, _get_latest_run_id(), _get_dashboard_view()
   │       └─→ Reuses: chance_level, _compute_ablation_table, compute_pareto_frontier,
   │            derive_limitations, contrast_groups, price_plan
   │
   ├─→ 5. cli.py: --open-browser, demo detection via spec.profile, CORE_COMMANDS
   │
   ├─→ 6. index.html: complete rewrite (HTMX polling, 4-panel, embedded SVG)
   │
   ├─→ 7. scripts/capture_dashboard_screenshot.py (Playwright)
   │
   ├─→ 8. docs/readme/title.md: hero image + tagline
   │
   ├─→ 9. docs/readme/build_readme.py: verify asset path
   │
   └─→ 10. docs/DASHBOARD.md
```

---

## Recommended Refactor Before Implementation

**Extract shared "dashboard data" module**:
```
computronium/experiment/surface/dashboard_data.py
  ├─ get_dashboard_view(store, run_id) → DashboardView
  ├─ _compute_ablation_table (from report.py)
  ├─ _get_chance_level (from report.py)
  ├─ _get_pareto_points (from pareto_analysis.py)
  ├─ _get_limitations (from limitations.py)
  └─ _render_charts (matplotlib → base64 SVG)
```

**Benefits**:
- Single source of truth for dashboard/report parity
- Testable in isolation
- Avoids circular imports (web.py → report.py → store.py)

---

## Estimated Effort by Gap Category

| Category | Count | Effort |
|----------|-------|--------|
| New methods in store.py | 1 | Low |
| New dashboard_data.py module | 1 | Medium |
| web.py modifications | 3 functions | Medium |
| cli.py modifications | 3 changes | Low |
| index.html rewrite | 1 complete | High |
| CSS/styling | 1 new system | Medium |
| Screenshot automation | 1 script | Medium |
| Documentation | 2 files | Low |
| Dependency additions | 2 packages | Low |

**Total**: ~10 focused changes, 1 major rewrite (template), 1 new module.