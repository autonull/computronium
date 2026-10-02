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

All items below were completed in the 2026-10-02c session (see the
"WHAT WAS DONE (2026-10-02c)" section for details):

- ~~Legend column widths~~ ✓ — now computed from label text widths via
  `text_w(label, STYLE.legend_font)`; swatch/gap/col geometry all driven by
  `Style` (`legend_swatch`, `legend_gap`, `legend_font`).
- ~~Edge label placement refinement~~ ✓ — `h-gap` labels moved from panel
  vertical-center into the horizontal gap channel above the source band
  (`s.y - 24`); pixel-verified (probe) that all 11 labels sit inside a band
  gap and overlap **zero** panels.
- ~~Edge-label-rect containment check in `--check`~~ ✓ — extracted
  `_verify_layout()`; now asserts every edge-label rect is within canvas
  bounds **and** does not intersect any panel rect (`_label_hits_panel`).
  `edge_label_placement()` centralizes the rect math shared by render + check.
- The script runs zero-error on fresh checkout with
  `uv run python docs/diagram_create.py [--check]`.

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

=== WHAT WAS DONE (2026-10-02c) ===

Both open improvement opportunities above were implemented, and all three
"REMAINING WORK" items are closed. No source file outside the diagram script
was touched.

- **Variable font sizing (centralized)** — Every hardcoded font size is now a
  `Style` constant. Added `legend_font` (8.5), `group_header_font` (9.5),
  `axis_header_font` (11.0), `axis_cfg_font` (9.0), `axis_field_font` (8.0).
  `Chip.w`/`draw_chip`/`draw_flow_step`/`draw_axis_box`/`box_natural_w`/
  `render_legend`/row-labels all read from `Style` instead of magic numbers.
  All values are **value-preserving** (identical pt sizes), so chip/step/panel
  metrics are unchanged — the only canvas growth comes from group padding.
- **Visual hierarchy / box grouping** — Each `Group` inside a
  `GroupedChipsRow` is now wrapped in a shaded, rounded, tinted container
  (`fill=<accent>14`, `stroke=<accent>40`, sw 0.8, rx 8) with symmetric
  `group_inset` (6.0) vertical padding, so the objectives/priors and per-domain
  task clusters read as contained boxes rather than a wall of chips. The
  container hugs the chip cluster (`span = max(cluster_right, name_w)`, 3px
  side pad) and does **not** reflow chips (chips still wrap at full content
  width), keeping the layout deterministic. `grouped_chips_h()` was updated to
  add `2 * group_inset` per group so panel heights stay consistent with the
  rendered containers.
- **Legend column widths** — `render_legend()` now computes each column width
  from `text_w(label, STYLE.legend_font)` (was a hardcoded `26.0 + text_w`
  estimate); swatch width and inter-column gap come from `Style`.
- **Edge label placement refinement** — `h-gap` edge labels were sitting at the
  source panel's vertical center (risking overlap with panel row content in the
  narrow 72px inter-panel gutter). `edge_label()` now places `h-gap` labels in
  the horizontal band-gap channel **above** the source band (`s.y - 24`).
  Verified by probe: all 11 labels land inside a `band_gaps` strip and
  intersect **zero** panels.
- **`--check` validation hardened** — Extracted `_verify_layout(ly)` from
  `main()`. It now asserts, per edge label: (a) the label rect is within canvas
  bounds (±6), and (b) the label rect does not intersect any panel
  (`_label_hits_panel`). `edge_label_placement(e, ly)` returns the exact
  (x, y, w, h, anchor) the renderer draws, so render and check share one source
  of truth (DRY). `main()`'s check block shrank to `ET.fromstring(svg);
  _verify_layout(ly)`.

**Files modified/created (2026-10-02c):**
- `docs/diagram_create.py` — font centralization, group containers, legend
  width fix, h-gap label channel, `_verify_layout`/`edge_label_placement`/
  `_label_hits_panel`; ~1950 → ~2030 lines
- `docs/diagram.svg` — regenerated (161 KiB, **2547px tall × 2511px wide**,
  303 `<title>` tooltips, 7 new group containers)
- `docs/infographic.txt` — regenerated (structure unchanged; data reflects live
  codebase)

**Gate status (2026-10-02c):** `ruff format` clean · `ruff check` all passed ·
`pyright` 0 errors/0 warnings · `uv run python docs/diagram_create.py
--check` → "check: svg parses, all panels/edges/labels within canvas".

=== NEW IMPROVEMENT OPPORTUNITIES (2026-10-02c) ===

All four items implemented in the 2026-10-02d session (details below):

- ~~Elbow label for `train→evidence`~~ ✓ — elbow lanes now snap to the
  band-gap midpoint via `_gap_y()`; `train→evidence` lane moved from
  y≈2126 to 2170 (exact gap midpoint 2134–2206). All four elbow labels
  verified at gap midpoints (464/1217/1789/2170).
- ~~Label-vs-label collision check~~ ✓ — `_verify_layout` now collects every
  edge-label rect and raises on any pairwise intersection
  (`_rects_overlap`). Proved its worth immediately: it caught a **real**
  pre-existing collision between the two left-rail labels
  (`entry→system` and `surface→entry` both rendered at the same
  gap-2 position, x-ranges 30–228 vs 50–213). Fixed by staggering the
  parallel-rail labels around the gap midpoint (`rail_label_offset` = ±18):
  outer rail above, inner rail below.
- ~~Legend additions~~ ✓ — LEGEND now carries item *kinds*: 8 panel swatches +
  a dashed purple arrow swatch ("dashed: evidence → next question") + a
  6-square axis-color strip ("axis colors S G D P C U"). 10 items in 5 cols ×
  2 rows (was 8 in 4×2). `_legend_metrics(kind)` centralizes swatch widths;
  the old "ontology (S G D P C U)" text shortened to "ontology" since the
  axis row now carries that.
- ~~High-DPI render~~ ✓ — root `<svg>` now carries
  `shape-rendering="geometricPrecision" text-rendering="geometricPrecision"`,
  and `--hd` writes `docs/diagram@2x.svg` (same vectors, 2× pixel size via
  `render_svg(scale=2.0)` — 5022×5094 px). The 2× file is **on-demand, not
  committed** (162 KiB duplicate); decide if it should be tracked.

=== WHAT WAS DONE (2026-10-02d) ===

All work in `docs/diagram_create.py` only (~2032 → ~2090 lines). No source
file outside the diagram script touched.

- **Elbow lane centering** — `edge_points()` default case now uses
  `lane = _gap_y(ly, s.bottom, d.y)` instead of the raw
  `(s.bottom + d.y) / 2.0` midpoint. `_gap_y` returns the containing
  band-gap's midpoint (or the nearest one), so elbow horizontals now pass
  through the true gap center even when the source panel is shorter than its
  band. Labels stay 8 px above the lane, as before.
- **Pairwise label-collision check** — extracted `_verify_edge()` (canvas
  bounds + panel intersection + edge-point bounds, returns the label rect;
  keeps `_verify_layout` under C901) and added a nested pairwise
  `_rects_overlap` pass over all 11 edge-label rects.
- **Left-rail label stagger** — new `Style.rail_label_offset` (18.0):
  `margin-left` labels render at gap-midpoint − 18, `margin-left-up` at
  + 18, so the two near-parallel rails' labels never share a y-band. Both
  remain inside the 72 px gap channel (rects 1190–1205 / 1226–1241 inside
  gap 1181–1253).
- **Legend kinds** — `LEGEND` entries became 3-tuples
  `(kind, key, label)` with kind ∈ {`panel`, `dash`, `axes`};
  `render_legend` dispatches on kind (dashed polyline with `arrp` marker /
  six 5 px axis-color squares / plain swatch). New Style constants:
  `legend_dash_w`, `legend_axis_sq`, `legend_axis_gap`.
- **Hi-DPI** — `render_svg(..., scale: float = 1.0)` scales only the
  `width`/`height` attributes (viewBox unchanged); `main()` gained `--hd`
  writing `OUT_SVG_HD = docs/diagram@2x.svg`. Module docstring updated.

**Gate status (2026-10-02d):** dev-env smoke · `ruff format`/`ruff check`
clean · `pyright` 0 errors/0 warnings · `uv run python
docs/diagram_create.py --check --hd` → "check: svg parses, all
panels/edges/labels within canvas" (now incl. pairwise label collisions).
`docs/diagram.svg` regenerated (162 KiB, same 2547×2511 canvas; legend grew,
elbow lanes re-centered); `docs/infographic.txt` re-pinned (only the
stale commit-hash line moved d89f34ff → 4cf655af).

**Commit hygiene note:** the tree also carries unrelated in-flight changes
from another workstream (`computronium/experiment/evidence/{claims,store}.py`,
`experiment/surface/report.py`, new `evidence/limitations.py` +
`tests/property/test_claim_report_lock.py`). They were left untouched and
excluded from the diagram commit; stage paths explicitly when committing.

=== NEW IMPROVEMENT OPPORTUNITIES (2026-10-02d) ===

- **Legend geometry is unverified** — `_verify_layout` checks panels, edges,
  and edge-labels, but the legend's right-anchored block (x0 derived from
  `canvas_w`, which is content-driven) is not containment-checked. If panel
  widths grow, the legend could drift onto a panel. Cheap to add: legend item
  rects vs canvas + band-0 top.
- **`_gap_y` nearest-gap fallback is silent** — a rail label can land in a
  gap its rail segment only grazes (currently benign: `entry→system`
  midpoint falls between gaps 1 and 2 and lands in gap 2, which the outer
  rail fully crosses). If bands get dense, assert the chosen gap actually
  intersects the label's rail/segment span in `_verify_edge`.
- **2× artifact policy** — `docs/diagram@2x.svg` is on-demand (`--hd`).
  Decide: keep untracked (current) or commit it for a hi-DPI preview out of
  the box. If committed, note it in the README's dev section.
- **Elbow lane vs destination panel** — lanes now sit at gap midpoints; a
  very short gap (`band_gap` < ~40) plus a wide label could push a label
  onto the destination panel's top edge. The panel-intersection check would
  catch it; no layout change needed, just a note for anyone tuning
  `band_gap`.

=== DOMAINS MERGED + SINGLE-GRID TABLES (2026-10-02l) ===

- **Tasks panel: one grouped box** — the separate flat "🧩 N domains"
  `ChipsRow` is gone. The `GroupedChipsRow` now lists *every* domain
  from the registry as its own tinted group (missing ones, `timeseries`
  and `scientific`, render as name-only groups suffixed
  `· via create_task()` instead of disappearing), with the row label
  carrying the totals:
  `🧩 7 domains · 28 SUPPORTED_TASKS — offline-resolvable subset`.
- **Tables are single-grid** — `_table_k` is now a constant 1, so
  OBJECTIVES / PRIORS / RunSpec / SystemTrainerConfig / Record fields
  each render as one column of rows with the border hugging the table's
  measured width (not the old duplicated two-sub-grid layout that
  stretched every border box ~2× past its content). `used_w` drives the
  border; `_table_preferred_w` uses the natural single-column width.
  Trade-off: panels get taller (SVG 149 KiB, 3263×2242) in exchange for
  much tighter, cleaner boxes; inner chips count 126.
- Gate: ruff format/check clean · pyright 0/0 · `--check` green.

=== EPOCH-LOOP ONE-LINER + TIGHTER BOXES (2026-10-02k) ===

- **Epoch loop renders as 5 stages in one row** — root cause was a
  floor/off-by-one in `flow_metrics`: `cols = int((w + step_gap) //
  stride)` comes out one short whenever `w` exactly equals the
  five-step ideal (and `Section`'s 12 px inset pushed `w` below it,
  wrapping 4+1 and dangling the loop-back polyline across rows).
  `cols` now rounds with a 0.5 bias, `_pw_section` reserves the 12 px
  inset in the section's preferred width, and the result is consistent:
  `FlowRow` pref → Section pref → panel content width → child `w` →
  same 5 columns when drawing. The loop-back return (dashed, last step →
  first step bottom, "next step / until convergence") now closes over a
  single row of steps.
- **Tables fill their row instead of hugging the left** — `TableRow` no
  longer hardcodes a two-grid split. `_table_k(row, w)` picks the grid
  count that fits `w` (grid ≈ single-column width + 24 px gutter,
  balanced row counts), `_rh_table` uses the same rule so heights and
  borders stay consistent, and the border rect spans `max(used_w, w)`.
  Side effect: wide single-column tables (SystemTrainerConfig, Record
  fields) now paginate into as many side-by-side grids as width allows,
  roughly halving their height and removing the empty right gutter of
  their border box.
- Geometry: SVG 149 KiB, 2957×2242, `--check` green, no label collisions.

=== TABLE BORDERS + SHARED HEADERS (2026-10-02j) ===

- **Every `TableRow` now has a border** — rounded rect
  (`fill=color+08`, `stroke=color+55`, rx 6) enclosing the header + rows,
  so Objectives / Priors / RunSpec / SystemTrainerConfig / Record fields
  read as five distinct boxes inside the `Columns` band. Border width uses
  the measured column widths (`used_w`), not the full panel width.
- **Split-grid header dedupe** — when a `TableRow` wraps into two
  side-by-side sub-grids (>12 rows), the column labels
  (`objective|status`, `prior`, `field`, …) are drawn once over the first
  sub-grid; the continuation grid reserves the same 13 px row so both
  halves stay vertically aligned instead of repeating the same labels.
- Incidental fixes: primary-spine edge width (2.6 vs 1.6) and the 15.0 pt
  panel title size from the 2026-10-02g pass had silently failed to apply
  (ruff re-wrap changed the source string, so the replace missed); both
  are now actually in effect.

Gate: ruff format/check clean · pyright 0/0 · `--check` green
(SVG 149 KiB, 2960×2242 — unchanged geometry, only table fills).

=== TABLES EVERYWHERE + COLUMN PACKING (2026-10-02i) ===

User-directed layout consolidation:

- **`Columns` row type** — `(rows, gap=20)` arranges child rows
  horizontally; `_pw_columns` sums preferred widths (capped at
  `max_content_w`), `_col_widths` scales children proportionally when the
  pack exceeds the panel width, `_rh_columns` = tallest child.
- **Kernel registry tables pack three-across** — `🎯 OBJECTIVES` ·
  `⚖️ PRIORS` · `🧾 RunSpec fields` now render side-by-side via
  `Columns` (objectives split into two sub-grids, priors/runspec are
  single-column mono lists split >12 rows). RunSpec's chip wall (20
  boxes) and the stacked objectives/priors tables are gone.
- **Ontology flow row removed** — the redundant `FlowRow` above the axis
  boxes was deleted; `AxesRow` is the only ontology row again.
- **SystemTrainerConfig & Record fields → `TableRow`** — both are now
  mono field lists (`("field",)` single-column, split two-across >12
  rows) instead of chip rows.

Gate: ruff format/check clean · pyright 0/0 · `--check` green
(SVG 149 KiB, 2960×2242 — smaller again; inner chips ~133 since table
contents no longer count as chips). No label collisions.

=== SECTION WRAPPERS + CLI/ONTOLOGY INSETS (2026-10-02h) ===

Implemented the three deferred items from the 2026-10-02g pass:

- **`Section` row type** — `(label, rows)` container rendered as a tinted,
  rounded sub-panel (`fill=color+0d`, `stroke=color+33`) with a bold small
  header and child rows inset by 6 px. `row_h` = 22 header + children +
  `row_gap` separators + padding; `row_preferred_w` = max(child widths).
  Wired into `_PREFERRED_W`/`_ROW_H`/`_DRAW_ROW_HANDLERS`; `main()` chip
  counting recurses through `Section` (`_row_chips`). Applied to system
  (🏗 Composition / ⚙️ Configuration), train (🔁 Epoch loop / 📈 Telemetry),
  evidence (🗃 Store & schema / 🏷 Discipline), surface (🖥 Surface / 📦
  Packages). tasks/kernel/ontology/entry left flat (already grouped via
  `GroupedChipsRow`/tables).
- **CLI subcommands grouped by destination** — entry row is now a
  `GroupedChipsRow` with three Groups: ▶ EXECUTION (run, benchmark),
  📊 REPORTING (report, export, status, conformance), 🔍 TRUST (validate,
  joint-validate, parity, repro). Mapping is curated (name → group), not
  reflected — the reflection layer still supplies the names/summaries.
- **Ontology internal flow** — the ontology panel now opens with a
  `FlowRow` of the six axes (🟧substrate → … → 🧊update), each step's sub
  naming its config class, making the axis composition order visible
  inside the panel instead of only in the title.

Gate: ruff format/check clean · pyright 0/0 · `--check` green
(SVG 165 KiB, 3099×2469; ~195 inner chips = 189 prior + 6 ontology flow
steps). No label collisions; legend and rail-gap checks still pass.

=== READABILITY PASS (2026-10-02g) ===

User feedback applied: (a) no zoom-hint footer — SVG is vector, readers zoom;
(b) keep the current architectural banded/circular high-level layout (no
single-spine reflow); (c) widen the font-size range so hierarchy reads at a
glance; (d) Objectives/Priors as *tables*, not chip boxes; (e) more emoji
mnemonics at the row-label level.

- **TableRow** — new presentation row type (`label`, `headers`, `rows`,
  `mono`): bold small-caps header row, mono 9pt cells, two side-by-side
  grids when >12 rows (kernel is the only >12 case: 35 objectives → two
  18-row halves ≈ halves the panel growth). Status cells auto-tint
  (`✓` → green, `🔬` → amber). `row_preferred_w`/`row_h` refactored into
  `_PREFERRED_W`/`_ROW_H` dispatch tables (ruff C901/PLR0911/PLR0913).
- **Objectives/Priors → tables** — `🎯 OBJECTIVES (35) — 4 measured ✓, 31
  research targets 🔬` and `⚖️ PRIORS (28 seeded)` are now `TableRow`s;
  the 63 chip boxes + `Group` containers they replaced are gone
  (inner chips 253 → 189). Per-row kernel chips for capabilities/constraints
  remain (small sets).
- **Verification levels → FlowRow** — surface panel's L1–L5 is now a
  left-to-right flow (stronger discipline left→right) instead of chips.
- **Font spread** — chip 10.5→11.0, row labels 10.5→**12.5**, step labels
  10.5→11.5, panel titles 13.5→15, secondary text shrunk instead
  (note 9.5→8.5, sub 8.5→7.5, mono 9.5→9.0, legend 8.5→8, group header
  9.5→8.5, axis fields/cfgs down ~0.5). Bigger primary, smaller secondary
  = larger usable range.
- **Primary-spine edge emphasis** — `Edge.primary` flag; spine edges
  (entry→tasks→kernel→ontology→system→train→evidence→surface) render
  darker (`#1e293b`) and thicker (2.6), secondary edges lighter
  (`#94a3b8`, 1.6). High-level layout unchanged; the main path now reads
  as the spine vs the dashed purple "next question" loop.
- **Row-label emoji + counts everywhere** — ⌨️/🗺/🧩/📋/▶/🧠/🧮/🧰/⚙/🔁/📈/🔗/🗃/🏷/🖥/📐/📦 prefix row labels; counts added
  (CLI subcommands, domains, supported tasks, history metrics, policies,
  RunSpec/Record/SystemTrainerConfig field counts, stages, store methods).

Gate: ruff format/check clean · pyright 0/0 · `--check` green
(SVG 157 KiB, 2771×2469 — taller from the objectives table but narrower;
no label collisions, legend verified). `docs/cheatsheet/cheatsheet.txt`
re-pinned.

**Notes for remaining ideas:** the within-panel `Section` wrapper (row-level
containment) is still unimplemented — `TableRow` plus zebra/section
tints would be the vehicle; CLI subcommand chips are still one flat row
(grouping by destination needs a curated command→panel map, not reflection);
verified rail spans and gap fall-back are now asserted, so adding edges is
safe.

=== GAP-INTERSECTION + LEGEND CHECKS (2026-10-02f) ===

Closed the two open verification items from the 2026-10-02d list:

- **`_gap_y` nearest-gap fallback now asserted** — extracted `_gap_at()`
  (returns the gap itself; `_gap_y` is now a 2-line midpoint wrapper).
  `_verify_edge` gains a rail-span check for every non-`h-gap` route: the
  label's gap must intersect the edge's full y-span (`min..max` of all
  `edge_points` y-values), else `RuntimeError`. A rail whose label gap is
  never actually crossed now fails loudly instead of silently landing in
  a neighbouring gap.
- **Legend containment checked** — `_legend_layout()` (shared x0/col_w math)
  and `_legend_block()` (whole-block bbox) extracted from
  `render_legend`; `_verify_layout` asserts the legend block is inside the
  canvas horizontally and intersects no panel.

Gate: `ruff format`/`ruff check` clean · `pyright` 0/0 · `--check` green
(SVG unchanged: 162 KiB, 2547×2511). No behavior change to the render —
all edits are verification hardening plus the render/verify DRY refactor.

**Remaining open item:** the "elbow lane vs destination panel" note from
2026-10-02d (documentation-only; `band_gap` tuning caveat). The 2×
artifact policy question is closed (no 2× artifact exists).

=== RENAME + 2x REMOVAL (2026-10-02e) ===

User feedback: SVG is inherently scalable — the 2× variant was unwanted.

- **2x removed** — `--hd` flag, `OUT_SVG_HD`, `render_svg(scale=...)` all
  deleted; `docs/diagram@2x.svg` deleted. The `geometricPrecision`
  shape/text-rendering hints on the root `<svg>` were kept (rendering
  quality, not duplication). The "2× artifact policy" opportunity from the
  2026-10-02d list is closed: no 2× artifact at all.
- **Files moved + standardized under `docs/cheatsheet/`** (via `git mv`,
  history preserved):
  - `docs/diagram_create.py` → `docs/cheatsheet/cheatsheet_create.py`
  - `docs/diagram.svg` → `docs/cheatsheet/cheatsheet.svg`
  - `docs/infographic.txt` → `docs/cheatsheet/cheatsheet.txt`
  - Script's `ROOT` is now `parent.parent.parent`; `OUT_SVG`/`OUT_TXT`
    resolve relative to the script's own dir (`HERE`).
- **In-script references updated**: module docstring (artifact paths +
  usage), SVG footer regenerate line, datafile header
  ("…CHEATSHEET DATAFILE", generator line, artifacts line), section
  comment 6. No other repo file referenced the old paths (grep-verified;
  no test lock covers the cheatsheet).
- **Regenerated** with `uv run python docs/cheatsheet/cheatsheet_create.py
  --check` — green; 162 KiB SVG, same 2547×2511 canvas.