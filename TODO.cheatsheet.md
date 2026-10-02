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