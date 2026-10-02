Develop a python script, `docs/diagram_create.py`:
- generates a cheat-sheet infographic, `docs/diagram.svg`, showing a detailed directed graph, detailing all Computronium's: inputs, outputs, ontology components (algorithms/topologies/etc...), tasks, configuration options, entry-points, ... and any other category that helps explain the architecture
- preferably use code reflection/static code analysis to collect classes/annotations/metadata/etc... so that we can re-run it anytime and get precise results reflecting the actual codebase state.
- consider adding SVG/graph development dependencies to facilitate generation of the infographic, with good readable graph layout.
- consider other helpful details to include in the infographic
- use color-coding, styling, and emojis for visual mnemonics and aesthetic enhancement

Don't edit any of the source code, except the diagram script.  feel free to suggest any helpful changes that could facilitate this process, and we'll consider them.

Ask me for clarification about anything unclear/ambiguous before starting.

We'll review the result and provide feedback after producing a draft result.

=== PROGRESS (2026-10-02) ===

Plan overview: developing `docs/diagram_create.py` to generate `docs/diagram.svg` (architecture cheat-sheet SVG) and `docs/infographic.txt` (structured datafile) via code reflection.

=== WHAT HAS BEEN DONE ===

- Reflection module `collect()` gathers live architecture facts:
  - 6 axes with 57 primitives (substrate/geometry/dynamics/plasticity/credit/update) via `AXES_REGISTRIES`
  - Config field lists for 7 config classes (SubstrateConfig, GeometryConfig, StateDynamicsConfig, PlasticityConfig, CreditAssignmentConfig, ParameterUpdateConfig, SystemTrainerConfig)
  - 141 public API symbols from `computronium.__all__`
  - 10 CLI subcommands via AST-parse of `computronium/cli/__main__.py` (handles both Assign and AnnAssign)
  - 6 demo names + 21 gallery demos via AST-parse of `scripts/demos/demo_*.py` and `computronium/visualization/gallery.py`
  - Task grouping (7 domains, 28 SUPPORTED_TASKS) via text-parse of domains/registry.py
  - 11 kernel stages (S1–S11) via `STAGE_REGISTRY`; 8 policies via `POLICY_CATALOG`
  - 35 objectives (4 measured ✓, 31 research targets) + 28 priors via `seed_registries`
  - 5 verification levels (ANALYTICAL–EMPIRICAL); 5 workspace packages
  - Record fields, RecordStore methods, RunSpec fields, constraints/capabilities counts
- Presentation model defined: `Chip`, `FlowStep`, `AxisBox`, `ChipsRow`, `FlowRow`, `FieldsRow`, `TextRow`, `AxesRow`, `Panel`
- Hierarchical graph-within-graph design: coarse outer DAG flow (10 panels in 5 bands) whose each panel contains a small directed inset (primitive chips, stage flow, config fields, training loop)
- Content-driven geometry: `Style` dataclass centralizes all metrics (margin=60, header=96, footer=56, band_gap=72, panel_pad=14, title_h=36, row_gap=8, chip_gap=8, max_content_w=1440, flow_max_cols=6); all panel/edge dimensions computed from content via metric functions (`chip_positions`, `flow_metrics`, `row_preferred_w`, `row_h`, `panel_metrics`, `layout`)
- Panel arrangement (BANDS): band0=entry (centered), band1=tasks+kernel, band2=ontology (full-width 6-axis inset), band3=system+train, band4=surface+evidence; canvas width = 2*margin + max(band_widths); panels centered within bands
- Edge routing: `margin-left`, `margin-left-up`, `margin-right`, `h-gap`, `elbow`; labels placed in vertical gap channels with appropriate anchoring
- Color coding: panels = entry(slate), tasks(amber), kernel(violet), ontology(cyan), system(indigo), train(red), evidence(emerald), surface(gold); axes = S orange, G green, D blue, P purple, C pink, U teal; emojis in labels; legend on SVG right of subtitle
- SVG rendering: title + subtitle + legend + edges (solid/dashed purple back-edge) + panels + labels
- Both artifacts generated in one run: `docs/diagram.svg` (97 KiB, 2280px tall × 3128px wide) + `docs/infographic.txt` (12 KiB)

=== FIXES APPLIED (2026-10-02) ===

- Fixed `NameError: name 'prims' is not defined` in `build_panels` — genexpr iterates `for axis in b.axes` but references `prims`; changed to `for axis, prims in b.axes.items()`.
- Fixed `AttributeError: 'tuple' object has no attribute 'w'` in `layout()` — `panel_metrics()` returns `(w, h)` tuple, but code accessed `.w`; changed to `[0]` indexing.
- Removed dead code in `box_h()` (placeholder `bw` computation immediately `del`-ed); simplified to compute height directly from axis boxes.
- Refactored `build_panels()` (~280 lines, 21 locals) into per-panel row-builder helpers (`_entry_rows`, `_tasks_rows`, `_kernel_rows`, `_system_rows`, `_train_rows`, `_evidence_rows`, `_surface_rows`, `_axis_boxes`) + dispatch table `_ROW_BUILDERS` + title map `_TITLES`; `build_panels` now ~4 lines.
- Refactored `draw_row()` (14 complexity, 30 locals, 13 branches) into per-row-type handlers (`_draw_chips_row`, `_draw_flow_row`, `_draw_fields_row`, `_draw_text_row`, `_draw_axes_row`) + dispatch table `_DRAW_ROW_HANDLERS`.
- Refactored `render_txt()` (17 complexity, 60 statements, 17 branches) into per-panel text renderers (`_txt_entry`, `_txt_tasks`, `_txt_kernel`, `_txt_ontology`, `_txt_system`, `_txt_train`, `_txt_evidence`, `_txt_surface`) + dispatch table `_TXT_RENDERERS`.
- Renamed ambiguous variable `l` → `line`/`tier`/`raw` in all occurrences.
- Fixed `literal-membership` (ruff C405): tuple literals in `in` tests → set literals.
- Fixed `collection-literal-concatenation` (ruff RUF021): `tuple_a + (single,)` → `(*tuple_a, single)`.
- Added `check=False` to `subprocess.run`; resolved `git` via `shutil.which()` to avoid `S607` (partial executable path).
- Replaced `assert` in `--check` validation with `raise RuntimeError` (S101).
- Added `TYPE_CHECKING` block for `Callable` import (TCH003).
- Added `shutil` import for `shutil.which`.
- All `# noqa` → `# ruff: ignore[rule-name]` format per project convention.
- `_stage_label()` already wired into `Stage.label` via `collect()`; `STAGE_SHORT` map used for `FlowStep.sub` — both confirmed working (stages display as S1–S11).

=== LINT / TYPE STATUS ===

- `ruff format`: clean
- `ruff check`: **all checks passed** (refactored `row_preferred_w`/`row_h` to stay within C901 complexity ≤10 and PLR0911 return-count ≤6 by extracting `grouped_chips_h` + `_grouped_chips_preferred_w` helpers)
- `pyright` (strict): **0 errors, 0 warnings**
- Dev-env smoke (`import optuna, scipy, torchvision, pytest`): passes
- `tests/property/test_gallery_provenance_lock.py`: 85 passed

=== REMAINING WORK / IMPROVEMENT OPPORTUNITIES ===

- Legend column widths: compute from label text widths instead of hardcoded estimates; currently uses `text_w` with 8.5pt font and fixed col layout.
- Edge label placement refinement: ensure margin-edge labels fall in gap channels without overlapping panels; tested conceptually but not yet validated pixel-perfectly.
- Consider adding edge-label-rect containment check to `--check` validation (currently only checks panel bounds and edge endpoints).
- The script runs zero-error on fresh checkout with `uv run python docs/diagram_create.py [--check]`.

=== FEEDBACK FOR NEXT SESSION ===

All feedback items from (2026-10-02) have been addressed:.

1. **SUPPORTED_TASKS → grouped by 7 Domains** ✓ — Replaced flat `FieldsRow` with `GroupedChipsRow`: each domain is a `Group` with a colored emoji header and individual task-name chips. Tasks that are empty (timeseries, scientific) are omitted from the groups list. Each task chip has a `<title>` tooltip with the task name.

2. **Config classes → individual ConfigBox chips** ✓ — Converted all `FieldsRow` config displays to `ChipsRow` with individual field-name chips: `SystemTrainerConfig` (19 fields → 19 chips), `RunSpec` fields (20 → chips), `Record` fields (18 → chips). Each chip uses `mono=True` and has a `<title>` tooltip.

3. **Registries → labeled chip boxes** ✓ — Restructured `_kernel_rows()` registries from a single summary `ChipsRow` to:
   - `GroupedChipsRow` with two `Group`s: `OBJECTIVES` (35 chips, measured=green ✓, research=amber) and `PRIORS` (28 chips). Both with `⚖️` headers showing counts.
   - Separate `ChipsRow` for summary-only registries (CAPABILITIES, CONSTRAINTS, LEGALITY DSL, SearchSpace, ContrastDesign).
   - Each registry chip has a `<title>` tooltip.

4. **Emoji strategy** ✓ — Added discriminating icons: `🎯` for Objectives group, `⚖️` for Priors group, `⚙` for config names in axis boxes, `🧬` axis emoji prefix in axis box headers (🟧🟩🟦🟪🌸🧊 for S/G/D/P/C/U). Domain emojis retained in Tasks panel.

5. **Boxes not lists across ALL sections** ✓ — All `FieldsRow` instances with multi-item content have been converted to `ChipsRow` or `GroupedChipsRow`:
   - RunSpec fields → ChipsRow
   - SystemTrainerConfig fields → ChipsRow
   - Record fields → ChipsRow
   - Task names → GroupedChipsRow (grouped by domain)
   - Registry items → GroupedChipsRow / ChipsRow
   - Remaining `TextRow` instances are descriptive prose (single long strings), not item lists — kept as `TextRow`.

6. **Per-item tooltip text (SVG `<title>` tags)** ✓ — Added `tooltip: str | None` field to both `Chip` and `FlowStep` dataclasses. `draw_chip()` and `draw_flow_step()` wrap content in `<g><title>...</title>...</g>` when tooltip is set. 303 `<title>` elements in the final SVG covering: CLI commands, API symbols, demos, domain chips, task chips, stage flow steps, policies, objectives, priors, RunSpec fields, SystemTrainerConfig fields, record fields, store methods, claim tiers, surface CLI, verification levels, packages, and axis primitives (descriptions).

=== NEW DATA MODEL: Group + GroupedChipsRow ===

Added `Group` (name, chips, accent) and `GroupedChipsRow` (label, groups, gap) to the presentation model. Key rendering details:
- `Chip.tooltip` — when set, `draw_chip` wraps output in `<g><title>...</title>...</g>`
- `FlowStep.tooltip` — same wrapping in `draw_flow_step`
- `grouped_chips_h()` — computes height for `GroupedChipsRow`; extracts decision logic from `row_h` match case to satisfy ruff complexity limits (C901: complexity ≤10, PLR0911: ≤6 returns)
- `_grouped_chips_preferred_w()` — extracts preferred-width computation for `GroupedChipsRow` for the same reason
- `row_h` and `row_preferred_w` were refactored to use single-return-per-case and match-case dispatch, reducing complexity from 11→8 and returns from 7→6
- `_DRAW_ROW_HANDLERS` now includes `GroupedChipsRow: _draw_grouped_chips_row`
- `main()` chip counting updated to include `sum(len(g.chips) for g in getattr(r, "groups", ()))`

=== FILES MODIFIED / CREATED ===

- `docs/diagram_create.py` — implemented feedback items 1–6 (GroupedChipsRow model, tooltips, grouped registries, config field chips, task boxes by domain, axis emoji headers); refactored row_preferred_w/row_h for complexity limits; ~850 lines → ~930 lines
- `docs/diagram.svg` — regenerated (161 KiB, 2523px tall × 2511px wide, 303 `<title>` tooltips, 253 inner chips)
- `docs/infographic.txt` — regenerated (text datafile, unchanged structure — already grouped by domain)

=== NEW IMPROVEMENT OPPORTUNITIES (2026-10-02b) ===

- **Visual hierarchy / box grouping**: The chip boxes now sprawl across wide canvases. Wrap groups of related chips in visual containers (sub-panels, bordered `<g>` groups, or shaded background regions) and separate groups with whitespace/padding so the "boxes not lists" principle doesn't itself become a wall of boxes. Consider a two-level layout: each panel's rows are already grouped, but within ChipsRows the individual chips lack visual containment.
- **Variable font sizing**: Inner items consistently use the same font size (10.5pt chips, 9.5pt sub text). Smaller text for chip sub-labels, group headers, and config field names would improve zoom-in readability without sacrificing screen-fit. The current `text_w()` metric already supports variable sizes — parameterize font sizes per element type (e.g., group header 8.5pt, chip label 10.5pt, chip sub 8.0pt) via `Style` constants for centralized tuning.