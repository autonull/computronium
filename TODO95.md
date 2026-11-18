# TODO95 — The Map Is the Product

**Status:** 2026-11-18 · drafted from the README and `PURPOSE.md`, after TODO94
Session 12. The laboratory exists to map the 6-axis space of learning systems
(9 substrates × 12 geometries × 8 dynamics × 7 plasticities × 19 credits ×
18 updates = 73 primitives, 2M+ legal cells). Today the map is:
**62 of 73 primitives**, at **57 different boxes**, on **one ruler**, with
**47 labelled `pass`** of which **21 sit at or near chance**. The instrument
works; the map is not yet a map.

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

| Fact | Evidence | Consequence |
|---|---|---|
| Three inventories disagree | `ALL_PRIMITIVES` 62 vs the axis registry 73 vs README 71 | 11 available primitives absent; 2 implemented specs outside the registry |
| 62 rows at 57 boxes, one ruler | `map.json` box variants; all rows `val_acc on mnist`; 21 of 61 ≤ 0.20 | rows are neither comparable nor reproducible; a third of the `pass` labels are inflated |
| The box was 32 batches and a 10k ceiling | `P0_BATCH_LIMIT=32`; 118,282 parameters composed | ranked by step size; at 375 batches `adam` 0.198 → 0.927; every row was outside its own box |
| `mean_norm`'s default step was 10× too large | 0.01 → 0.101 at the same box; 1e-3 → 0.887 | an absolute-displacement rule needs an absolute step, not an lr |
| The screen was uncalibrated | 5 controls at `0.09375`, `cause=divergence` on digits | PASS/DEFECT at that box is a coin flip |
| The screen minted its own verdict | `chance = 0.1; PASS if val_acc > chance + 0.02` | a second bar, and a judgment from a 1-seed cell |
| Every substrate lands in a 0.49–0.63 band | 9 substrate rows, one algorithm, one task | a 14 pp band answers "does the substrate perturb MNIST", not the substrate→algorithm question |

The pattern: **the map is a legality report with numbers attached.**

---

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
by the map (P4); the external path follows (P5). P0a, P0.5, P0.75 are done.

### Queue (session 14; one table)

The base-box census is landed: 75 rows, 61 measured (31 bound, 30 inert), 8
defect, 6 refused, 0 missing; box `mnist`/375/150k/seed 0, control 0.8914.
The remaining work is one schema session, one calibration session and two claim
sessions. A row without a gate is prose; a session without a claim is a sweep.

| # | Session | Closes | Gate |
|---|---|---|---|
| S1 | **Schema + debt** (no GPU) | the record and the box (P0b); delete the P1 track and map `confirmation`; one `MAP_VERSION`; one gap table; extract `_screen_coordinate`; README counts from the generator (it reads the registry); the inventory: fix `noisy`/`closed_form_ridge` and retire `rule_state`/`substrate_coupled` → **73 available, 0 gaps** | `test_box_identity`, `test_loop_has_no_bar`, `test_init_then_update_keeps_a_row`, `test_gap_table_single_source`, `test_readme_counts_match_census`, `test_spec_composes`; `ruff` no PLR09/C901 |
| S2 | **Calibrate + bind** (~20 min GPU) | the bar (chance + 2σ at the ruler's resolution) and a 3-seed control per family; the `iris` base; the task-family filter (3 sequence credits become `refused`); the own-knobs pass (30 inert rows); the resource vector gains `memory_mb` and `energy_per_batch` | `test_control_power`, `test_task_family_filter`, `test_own_knobs`, `test_resource_vector` |
| S3 | **Interaction** (P3, ~10 min GPU) | rank only `binding=bound` rows; the pair with the most variance; 1 seed per cell, 3 for the top; intervals, not a ranking | `test_interaction_power` |
| S4 | **Claim + publish** (P4/P5) | ladder the surprising bound row to 3 points, then 5 paired at matched boxes; pre-registered margin; method cards, the committed `docs/sec/map.md`, `comp verify` | `test_paired_ci`, `test_map_summary_matches_census`, `test_extension_path` |

Stop rules: a slice whose control is at chance is refused before it is priced; a
pair with no power is marked, not reported; a claim is fixed-n, no peeking. The
detailed decisions and done conditions follow.

### P0a — One inventory (no training; done) ✅

**Landed:** `build_census` reads `AXES_REGISTRIES` (73) plus 2 spec-only rows;
the census prints 75. `noisy` and `closed_form_ridge` are `available=False`
with "no config classmethod — a capability gap". `ALL_PRIMITIVES` is deleted;
the axis registry is the only list.
**Gate:** `test_inventory_single_source` (75 total; every axis row an entry).
**Open:** the two spec-only rows have two honest ends — fix their classmethods and
add their axis rows, or retire their specs; the two no-op plasticities
(`rule_state`, `substrate_coupled`) have the same choice. S1 adopts the 73-row
target: fix the shipped two, retire the no-ops, and D9's `test_spec_composes`
passes with no permanent gaps.

### P0b — One box, one record (schema change; 1 session)

**Decision:** can a claim be checked against its run? Today no.
**Deliverable:** `Schedule` gains `batch_size`, `steps_per_task`; the CL runner
builds one; the `sec_loop` JSONL becomes a `Record` carrying the box and the
replay hash; `ThresholdRegistration` stops discarding box fields.
**Gate:** `test_box_identity`: changing `batch_size` alone refuses the claim.
**Done when:** one record schema, one box type, and a claim that names its box.

### P0.5 — The defect queue (before the census) ✅

**Landed:** the 32-batch box (`adam` 0.198) and the 10k ceiling (118,282
params) were defects, not results; at 375 batches / 150k they measure
(`adam` 0.927, `lion` 0.914); `mean_norm`'s default step was 10× too large
(0.01 → 0.887 at 1e-3); `spectral_constrained` and `elastic_consolidation`
measure 0.626 — a step ladder, not a verdict. `split_mnist` has its domain.

### P0.75 — Declare the binding conditions (no compute; 1 hour) ✅

**Landed:** `sec_binding.py` declares one condition per axis — substrate: a
substrate-sensitive ruler; credit: a label channel; update: its own step size;
dynamics: a settle; plasticity: a ψ lifecycle; geometry: a layer/cell/graph form.
Every cell carries `binding: bound|inert` and the reason.
**Done when:** an inert slice is never a result about its axis.

### P1 — Calibrate the box (pilot, ~30 min)

**Decision:** at which box does a published control clear the bar on each task
family, and what does a cell cost?
**Deliverable:** one base box per family (vision, tabular, graph, sequence):
`batch_size`, `steps/task`, `epochs`, chosen so the control is above chance
and the cell is ≤ ~2 min. Publish `cells/hour`, measured, not estimated.
**Box:** vision: `mnist`, 1 epoch, 375 batches, hidden 128, 150k, control
0.8914, 5–60 s/cell. The next base is `iris` (tabular); graph and sequence
follow.
**Gate:** the pilot prints control ± σ and the bar (chance/majority + 2σ at the
ruler's resolution); a slice with a chance control is refused.
**Done when:** each family has a calibrated base and a measured cost per cell.

### P2 — The census (the first real map; ~2 h) ▶

**Decision:** of 73 primitives, which train at their slice's base, which need a
swap, which fail, and at what cost?
**Deliverable:** `map.json` v3: 75 rows with `status` ∈ {measured, defect,
refused, unmeasured}, base box, task, rule, control, resource vector.
Unmeasured rows are `unmeasured`, not absent. A short report: measured/defect/
refused counts per axis, and the defect list with mechanisms named.
**Box:** the P1 base for MNIST; a primitive that is illegal at the base is
measured at its nearest legal box and marked `swapped`; each primitive is also
measured at its own declared defaults and marked `own-knobs`. The measured base:
375 batches, hidden 128, 150k ceiling, control 0.8914, 5–60 s/cell.
**Open:** the own-knobs pass (the varied axis at its config-classmethod
defaults, companions at the base); the task-family filter (a sequence credit on
MNIST is `refused`, not `defect`); `memory_mb` and `energy_per_batch` in the
resource vector; swap labels on defect rows; the replay hash (P0b).
**Gate:** every row reproducible; every `fail` names a mechanism; the report
prints the inventory count.
**Done when:** one map with no missing rows, no inflated status, and every inert
row named — the base-box map meets this; own-knobs extends it.

### P3 — The interaction slice (the map's structure; ~2 h)

**Decision:** which axis pairs change each other at the fixed base?
**Deliverable:** a factorial slice on the two axes with the most variance over
`binding=bound` rows (the substrate × credit pair is `PURPOSE.md` §3's
substrate→algorithm question; credit × geometry is the fallback). 1 seed each at
the base, the top interactions at 3 seeds; intervals, not a ranking.
**Box:** the P1 base, only the two varied axes changing.
**Gate:** the control clears the bar in every cell; a pair with no power is
marked, not reported.
**Done when:** the map has a measured interaction layer — the first evidence
about *which* axes matter together.

### P4 — The deep dive (the thesis, chosen by the map)

**Decision:** which region deserves a matched, tuned comparison?
**Deliverable:** the census's most surprising measurement (today's candidates
are defect probes: `diffusion` 0.116 at 136 s, `conv` 0.122 at 41 s): a 3-point
ladder on its primary knob, then 5 paired seeds at matched boxes; pre-registered
margin, fixed n, no peeking.
**Box:** the candidate's own base; its knob ladder only if the map has a
measurement there.
**Gate:** the paired CI at `n_max`; the claim names its box.
**Done when:** a claim, a coordinate, or a defect — and the map row is updated.

### P5 — The external path and public artifacts (staged)

- `comp verify --primitive <name> --slice <family>` — the same scanner; a
  stranger adds a credit and holds a map row; `test_extension_path.py` end to end.
- Method cards from the map; recipes as tests; seed + box + replay hash per row.
- A public slice: one family, one base, all 73 primitives, with the records.

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

- One inventory (73 available rows: 63 measured, 5 ceiling defects, 5 box
  refusals; no permanent gaps) projected into census, map, README and method
  cards.
- Every measured row carries its task, base box, ruler, control and cost.
- Each family has a calibrated base with a measured cells/hour.
- No `measured` row called viable; no missing row; no `swapped` row labelled
  comparable; an inert row is never a result about its axis.
- One interaction result about which axes matter together.
- One deep dive chosen by the map, with a pre-registered claim or coordinate.
- A stranger adds a primitive and holds a map row without reading internals.

