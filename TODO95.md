# TODO95 — The Map Is the Product

**Status:** 2026-11-19 · drafted from the README and `PURPOSE.md`, after TODO94
Session 12; session 14 landed the record, the box and two composable rows;
session 15 calibrated the bar, the 3-seed control and the own-knobs box;
session 16 re-screened the census at that box (S2b); session 17 seated and
measured the interaction slice (S3); session 18 laddered the map's most
surprising bound row and published the map document (S4/P5). The laboratory
exists to map the 6-axis
space of learning systems
(10 substrates × 12 geometries × 8 dynamics × 6 plasticities × 19 credits ×
18 updates = 75 primitives, 2M+ legal cells). Today the map is:
**73 of 75 primitives available** (2 declared gaps: the documented no-op
plasticities), all 75 rows at one base box (mnist, 32 samples/step, 375
batches, 1 epoch; control 0.8908 ± 0.0024, bar 0.1060), with the box and the
replay hash on every screened row: **57 measured, 6 defect, 12 refused**
(8 family refusals, 2 cost caps, 2 declared gaps). The interaction layer is
measured: credit × dynamics, 12 cells, 393 s, effect +0.0153 (95% CI
−0.0092…+0.0397) — the two axes are additive at this box. The deep dive is
measured: the surprising bound row `target_inversion` ladders flat on its
primary knob, so the pair is marked `no_power` and the verdict is a coordinate,
not a claim — a defect probe, as P3 predicted. The map is published in `docs/sec/map.md`;
`comp verify` holds any primitive's row for a stranger.

---

## 0. What the laboratory is for

`PURPOSE.md` lists 25 outcomes. They reduce to five questions a map can answer:

| Map question | Purpose rows it serves | What it needs |
|---|---|---|
| **Viability** — which combinations train at all? | discover untried systems, find new digital algorithms, substrate→algorithm pairings | a calibrated box per task family, a comparable cell |
| **Interaction** — which axes change each other? | co-design, trade-offs, the landscape, the empirical science | a factorial slice at a fixed base |
| **Failure** — where and why does it break? | implementation defects, irreproducibility, negative results | a crash/NaN record with the mechanism named |
| **Cost** — what does a capability cost? | compute efficiency, Pareto, hardware selection | resource vector beside every number |
| **Candidate** — what deserves a deep dive? | new mechanisms, local learning, growing architectures | the map's own surprise ranking |

The deep dive (a thesis such as "local credit at low batch") is a **consequence**
of the map, not its organiser. The map is useful to the reader who never runs a
local rule: it says which of 73 primitives train, where they fail, and what they
cost.

---

## 1. What the record said before P0a (measured 2026-11-18)

Three inventories disagreed (62/73/71), 62 rows sat at 57 boxes under one
ruler, the screen ran 32 batches with a 10k ceiling, and it minted its own
`chance + 0.02` verdict: a legality report with numbers attached. Sections
2–3 are the fixes.

## 2. The unit of knowledge: a comparable cell

A map row is a **cell** with five fields — `(varied axis value, base box,
task + ruler, control, resource vector)` — and a row is comparable only when
the four fixed fields match the slice.

- **Base box** — `Schedule` (task, batch_size, steps/task, epochs, seeds,
  device, dataset version). One base per slice; only the varied axes change.
- **Control** — a known-good arm at the same base. If it is at chance, the slice
  has **no power** and emits no status (defect class D4).
- **Ruler** — the task's own metric and resolution (held-out samples), with the
  chance/majority rate beside it.
- **No verdict from a screen.** A screen emits `measured` (the number, the box,
  the cost), `defect` (an execution fact: crash, non-finite metric, ceiling
  violation), `refused` (rule + reopen trigger), `unmeasured`. `pass`,
  `coordinate` and `viable` are **not** screen outputs: a judgment requires a
  pre-registered comparison at a calibrated box, in P4.
- **Resource vector** — accuracy, walltime_s, cell_peak_mb, plastic_state_bytes,
  forward-equivalents. Reported, never used to rank.
- **Binding condition** — what must be true for the varied axis to *bind*:
  a substrate needs a substrate-sensitive metric or task (bit-width, energy,
  spike timing), a credit needs its label channel, an update needs its own step
  size, a dynamics needs a settle. An axis that does not bind is recorded as
  `binding: false`, not as a result.

A **viability box** (each primitive at its own declared defaults) and a
**comparison box** (one fixed knob for all) are different instruments. The map
publishes both: viability tells a user "does this primitive train at its own
best"; comparison tells "does this axis change the outcome".

A row whose varied field is not the only difference from the base is
**`swapped`**; the map prints that label, it never hides it.

---

## 3. The defect classes and their locks

| # | Class | Permanent fix | Lock |
|---|---|---|---|
| D1 | **Inventory drift** ✅ Three lists of primitives. | `AXES_REGISTRIES` is the only inventory; census, map, README and method cards are projections. | `test_inventory_single_source`: count == sum of axes, every primitive has a map row |
| D2 | **Box unread.** Batch/steps/knobs are not checked against the claim. | `Schedule` **is** the box; add `batch_size`, `steps_per_task`; print it, store it, compare on claim. No parallel `Box` type. | `test_box_identity`: change `batch_size` alone → claim refuses |
| D3 | **Incomparable rows.** 57 boxes, one ruler. | One base per slice; a row differing elsewhere is `swapped`; the ruler is per task family. | `test_slice_comparability`: a non-base row cannot be treated as comparable |
| D4 | **Uncalibrated screen.** PASS at a box where the control is at chance. | Every slice publishes a control; below the bar → `chance`, no status. | `test_screen_power`: a constant arm yields `chance` |
| D5 | **The screen mints a verdict** ✅ P0 computed `PASS` above a local `chance = 0.1` — a second bar, and a judgment from one seed. | A screen emits measurements and execution defects only; a bar is a gate floor and a comparison is pre-registered. | `test_screen_has_no_verdict`: no `PASS`/`viable` key from `run_p0_track` |
| D6 | **Untested extension path.** No acceptance test adds a primitive. | A fake credit through the documented ramp → a map row in ≤60 s. | `tests/acceptance/test_extension_path.py` |
| D7 | **Docs drift.** Recipes and numbers live in prose. | Every recipe runs at its declared box in `tests/docs/`. | `test_recipes_reproduce` |
| D8 | **An axis that does not bind** ✅ 9 substrates "pass" on an MLP. | Every slice declares its binding condition; a non-binding axis is `inert`. | `test_binding_condition`: a substrate row on MNIST is `inert`, not `pass` |
| D9 | **Implemented but not composable** ✅ 2 primitives exist outside the axis registry. | Registry derived from `primitives/*/spec.py`; every spec must compose. | `test_spec_composes`: every spec id resolves to an axis row |

A debt row closes on its gate; an item without a gate is prose.

---

## 4. Roadmap, in order

Order by dependency: a row without its run is not reproducible (P0b); a slice
whose control is at chance cannot label anything (P1); only then is a census
meaningful (P2); interactions require a fixed base (P3); the deep dive is chosen
by the map (P4); the external path follows (P5). P0a through P5 are done; the
rows below are the map's backlog, ordered by the map.

### Queue (session 17; one table)

The census is the inventory: 75 rows, 73 available, 2 declared gaps (the two
no-op plasticities). The box fix and the calibration landed:
vision (`mnist`, 32/step, 375 batches, 1 epoch) control 0.8908 ± 0.0024, bar
0.1060; tabular (`iris`, 32/step, 20 epochs) control 0.7333 ± 0.0943, bar
0.5055. The own-knobs box ran the 18 update rows: 14 measured, 4 refused
(3 family refusals, 1 cost cap). S2b then re-screened all 75 rows at the
vision base: 57 measured, 6 defect, 12 refused, 19.7 min (12.0 s/cell mean
over 62 trained cells, 228 rows/h). S3 seated the map's top pair (credit ×
dynamics) and measured its 2×2: 12 cells, 393 s, effect +0.0153 (95% CI
−0.0092…+0.0397) — additive at this box. Queued next, in the map's order:
own-knobs boxes for the other five axes (credit, substrate, geometry, dynamics,
plasticity); declared bases for the graph and sequence families; the CL runner's
`Schedule` beside `CLConfig`; and the five other near-chance bound rows, each a
deep dive of its own. A row without a gate is prose; a session without a claim
is a sweep.

| # | Session | Closes | Gate |
|---|---|---|---|
| S1a ✅ | **Schema + debt** (no GPU) | `MAP_VERSION`; `schema.gaps.GAPS` (one gap table, reasons + triggers); `noisy`/`closed_form_ridge` compose their own rows; `Schedule` gains `batch_size`/`steps_per_task` (the box); `record_from_evaluation` + a `Record` in the P0 log; `_screen_coordinate` extracted; README regenerated from the registry | `test_box_identity`, `test_loop_has_no_bar`, `test_init_then_update_keeps_a_row`, `test_gap_table_single_source`, `test_readme_counts_match_census`, `test_spec_composes` |
| S1b ✅ | **The two parked rows** (no GPU; parked) | `rule_state`/`substrate_coupled` stay in the inventory (user decision: no deletion); make each a bounded contract that composes — `apply_operator` in the standard step, and a substrate state σ read back — or park them with the `GAPS` row as the snapshot of a capability the kernel still owes | the `GAPS` row fails when the row becomes available; `test_axis_liveness_lock` |
| S2a ✅ | **Calibrate + bind** (~10 min GPU) | the bar (chance + 2σ at the ruler's resolution); the 3-seed control per family; the `iris` base; the task-family filter (3 update rows `refused`); the own-knobs box (14/18 update rows `bound` and measured); `memory_mb` and `energy_per_batch` in the resource vector | `test_pilot_calibration` (`test_the_bar_is_the_floor_plus_2_sigma`, `test_a_constant_control_refuses_its_slice`, `test_the_family_filter_refuses_a_sequence_credit_on_vision`, `test_the_own_knobs_box_binds_an_update_row`, `test_the_resource_vector_carries_memory_and_energy`) |
| S2b ✅ | **Re-screen at the calibrated boxes** (~20 min GPU) | `map.json` v3 at 32/step: 57 measured, 6 defect (5 ceiling + graph's static edge index), 12 refused (8 family, 2 cost caps, 2 gaps); every screened row carries its box, rule and replay hash; the base schedule now derives from `BASE_BOXES` (one box), the control from `calibrate_control` (one rule); graph composes (cache round-trip) and `noisy` measures (device-model row); no row needed a swap, and no graph/sequence family has a declared base | `test_map_summary_matches_census`, `test_every_map_row_has_its_box` |
| S3 ✅ | **Interaction** (P3, 393 s GPU) | rank only `binding=bound` rows; the pair with the most variance (credit × dynamics); the largest legal 2×2 (`target_inversion` × `lazy`); 1 seed per cell, 3 for the pair; intervals, not a ranking | `test_interaction_power` (14 cases) |
| S4 ✅ | **Claim + publish** (P4/P5) | `sec_deep_dive.py` (candidate = smallest margin over the bar with a declared knob; 3 points on the knob; 5 paired seeds at the base box; margin 0.01, alpha 0.05, n_max 5 in `configs/preregistrations/sec_deep_dive.json`); `sec_extension.py` + `comp verify`; `documentation/sec_map.py` → `docs/sec/map.md` | `test_paired_ci`, `test_map_summary_matches_census`, `test_extension_path`, `test_sec_map_doc` |

Stop rules: a slice whose control is at chance is refused before it is priced; a
pair with no power is marked, not reported; a claim is fixed-n, no peeking. The
detailed decisions and done conditions follow.

### Done before S3 (sessions 12–16)

- **P0a — one inventory ✅** `build_census` reads `AXES_REGISTRIES` (73) plus 2
  spec-only rows; the census prints 75. `ALL_PRIMITIVES` is deleted; `noisy` and
  `closed_form_ridge` compose their own rows; the two no-op plasticities stay
  declared gaps in `schema.gaps.GAPS`. Gate: `test_inventory_single_source`.
- **P0b — one box, one record ✅ mostly** `Schedule` gains `batch_size` and
  `steps_per_task` (in the measurement key and the printed box);
  `record_from_evaluation` wraps a run (box + replay hash) and the log writes
  `{"screen", "record"}`; `ThresholdRegistration.box` refuses another box.
  Gate: `test_box_identity`. Open: the CL runner still builds its `Schedule`
  beside `CLConfig`, so the R-track cells carry no `Record`.
- **P0.5 — the defect queue ✅** The 32-batch box and the 10k ceiling were
  defects, not results (at 375 batches `adam` 0.927); `mean_norm`'s default step
  was 10× too large (1e-3 → 0.887); `spectral_constrained` and
  `elastic_consolidation` measure 0.626 — a step ladder, not a verdict.
- **P0.75 — binding conditions ✅** `sec_binding.py` declares one condition per
  axis and every cell carries `binding: bound|inert` with its reason. Gate:
  `test_binding_condition`.
- **P1 — calibrate the box ✅** Vision (`mnist`, 32/step, 375 batches, 1 epoch,
  hidden 128, 150k): control 0.8908 ± 0.0024, bar 0.1060, 8.3 s/cell. Tabular
  (`iris`, 32/step, 20 epochs): control 0.7333 ± 0.0943, bar 0.5055, 4.9 s/cell.
  Graph and sequence declare no base, so their slices are refused, not priced.
  Gate: `test_pilot_calibration` (2σ bar, 3-seed control, family filter,
  own-knobs box, resource vector).
- **P2 — the census ✅ base box** `map.json` v3: 75 rows, 73 available, 57
  measured / 6 defect / 12 refused at the vision base, 19.7 min (12.0 s/cell
  over 62 trained cells, 228 rows/h). The defects and refusals are in §2; the
  own-knobs box ran the 18 update rows (14 measured, 4 refused); every row
  carries its box, rule, control and replay hash. The 6 near-chance bound rows
  (`pc_alm`, `target_inversion`, `temporal_trace` inert, `conv`,
  `quantized_adam` inert, `error_predictive_coding`) are the deep dive's
  defect probes. Gates: `test_map_summary_matches_census`,
  `test_every_map_row_has_its_box`.

### P3 — The interaction slice (the map's structure) ✅

**Decision:** which axis pairs change each other at the fixed base?
**Deliverable:** a factorial slice on the two axes with the most variance over
`binding=bound` rows (the substrate × credit pair is `PURPOSE.md` §3's question,
but at the accuracy ruler substrate has no bound row; the ranking decided credit
× dynamics — credit × geometry was the predicted fallback). 1 seed each at the
base, the top pair at 3 seeds; intervals, not a ranking.
**Box:** the P1 base, only the two varied axes changing.
**Gate:** the control clears the bar in every cell; a pair with no power is
marked, not reported.

**Landed (session 17):** `sec_interaction.py` ranks the axes over measured,
non-swapped `binding=bound` rows; the top two are credit (variance 0.1017 over
13 rows) and dynamics (0.1014 over 6); geometry (0.0721) and plasticity
(0.0661) rank below, and substrate has no bound row at this ruler. The slice is
the largest 2×2 the validator seats: an arm that cannot compose with the other
axis's base level is not a factor level here, so the most displaced dynamics
arm (`error_predictive_coding`) is skipped and the seated levels are credit
`gradient → target_inversion`, dynamics `instantaneous → lazy`. The base
cell is the control (3 seeds, 0.8908); the other three screen at one seed and
confirm at three, declared before the number exists.
**Result:** 12 cells, 393 s (`lazy` is the cost: 45 s/cell); the interaction is
+0.0153, 95% CI [−0.0092, +0.0397] at 3 seeds — the pair is additive at this
box. Each cell's replay hash names its seed (a hash-repair re-run reproduced
the number, 422 s). The credit arm sits at the bar's edge (0.1195), so the null
also says a settle does not rescue a credit that reads no usable label: a coordinate
about the pair, and `target_inversion` joins S4's defect probes.
**Gate:** `test_interaction_power`: the pair is the top two by variance; a
swapped, refused or defect row never ranks; an inert base level is the
baseline, not a ranked row; the largest legal 2×2 seats the slice and a pair
with no legal 2×2 is refused; one seed carries no interval and three carry one;
a control inside the bar marks `no_power` without pricing a cell; the map keeps
the layer through a later axis-by-axis run.
**Open:** one pair at one box — a second pair waits for the map's next variance
ranking (the graph/sequence bases will change it); the four cells are
measurements, not a verdict (a claim needs the S4 ladder and paired seeds).

### P4 — The deep dive ✅ (session 18)

**Decision:** which region deserves a matched, tuned comparison?
**Deliverable:** the map's most surprising bound row — `target_inversion`,
0.1195 at the bar's edge (margin +0.0135) — laddered on its primary knob
(`credit.feedback_scale`, default 0.01) to 3 points (0.001/0.01/0.1), then 5
paired seeds at the matched base box against the primitive's own default. The
margin (1 pp at alpha 0.05, n_max 5) is pre-registered in
`configs/preregistrations/sec_deep_dive.json` before the first seed.
**Box:** the vision base; the candidate's own base level; only the knob varies.
**Result:** 3 rungs at 0.1195 each (`knob_binds=false`: the knob does not act
here); 5 paired seeds with identical arms (0.1908, 0.1181, 0.1300, 0.1533,
0.1195 in both): the difference is structurally zero, so the pair is
`no_power` and the verdict is **coordinate**, not a claim. `target_inversion`
is a defect probe: it clears the bar, its declared numeric knobs are inert and
its binding knob is structural (a feedback matrix) — as P3 predicted.
**Done when:** a claim, a coordinate, or a defect — and the map row is updated.

### P5 — The external path ✅ (session 18)

- `comp verify --primitive <name> --slice <family>`: the scanner reads only
  `map.json`; a stranger adds a credit and holds a row; `test_extension_path.py`
  runs the recipe end to end (≤60 s; exit 1 names the first problem).
- Method cards and the census are one document: `docs/sec/map.md`, generated
  by `documentation.sec_map`; seed + box + ruler + control + replay hash per
  row; recipes as tests (`test_sec_map_doc`).

---

## 5. The scan protocol (one page)

1. **One base per slice.** Only the varied axis changes; any other difference is
   `swapped`. A viability box (each primitive at its own defaults) and a
   comparison box (one fixed knob for all) are different instruments; publish
   both.
2. **Control first.** The published control at the base must clear the bar; else
   `chance`, no status. A slice whose control is at chance is refused before it
   is priced.
3. **Cheapest falsifier.** 1 seed screens; 3 seeds confirm an interaction; 5
   paired seeds carry a claim. Cheap tasks first (14 cheap, 14 medium, 2
   expensive; the expensive two need a declared budget and a stop rule).
4. **Budget in cells and steps.** Walltime is reported, never used to rank. The
   watchdog is 2× the measured cell, not a clock.
5. **Every row reproducible.** Task + box + seed + ruler + replay hash.
6. **A negative is a row**; a fail names its mechanism; `refused` carries a
   trigger and an owner. The defect queue is the map's backlog, not a separate
   document.
7. **The map allocates.** The census's variance decides the interaction pair;
   the interaction's strongest effect decides the deep-dive region. No plan
   order overrides the map's own ranking.

## 6. What we stop doing

- Promoting one thesis before the map exists; adding legality rows without a
  measurement (the factory is green).
- Reporting a map with missing rows, one ruler for all families, or a
  near-chance cell called `pass`.
- Full sweeps (the census is the sweep); 1-seed claims; walltime rankings;
  documents longer than 300 lines.

**What made this plan wrong once:** a retry chain spent a whole axis on one
primitive. The census now accumulates axis by axis and a 60 s cap refuses an
unpriceable cell. The remaining falsifier: a session that cannot name its claim
before the first cell is a budget leak.

## 7. Definition of done

- One inventory (73 available rows: 57 measured, 6 defects — 5 parameter
  ceilings and `graph`'s static edge index — and 10 box refusals; the 2 no-op
  plasticities stay declared gaps) projected into census, map, README and
  method cards.
- Every measured row carries its task, base box, ruler, control and cost.
- Each family has a calibrated base with a measured cells/hour.
- No `measured` row called viable; no missing row; no `swapped` row labelled
  comparable; an inert row is never a result about its axis.
- One interaction result about which axes matter together.
- One deep dive chosen by the map, with a pre-registered claim or coordinate
  ✅ (a coordinate: `target_inversion`'s knob is inert at this box).
- A stranger adds a primitive and holds a map row without reading internals
  ✅ (`comp verify`, `test_extension_path`).
- Remaining backlog: §4's open rows (other own-knobs boxes, graph/sequence
  bases, the CL runner's `Schedule`, the five other near-chance rows).

