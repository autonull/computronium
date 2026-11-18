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

## 1. What the record says (measured 2026-11-18)

| Fact | Evidence | Consequence |
|---|---|---|
| Three inventories disagree | `schema/primitives.py:ALL_PRIMITIVES` has 62 (credit 14, update 12); the axis registry has 19 and 18 → 73; README says 71 | 11 primitives (5 credits, 6 updates) are absent, and `sec_loop.py:416` screens from the same short list |
| The missing rows are all available | axis rows: `available=True` for the 11 | this is a stale hand list, not an unavailable set |
| 62 entries at 57 boxes | `map.json` box variants | the rows are not comparable: each "pass" is at its own nearest-legal box |
| One ruler for every primitive | all 62 rows say `val_acc on mnist` | wrong ruler for graph/tabular/sequence primitives; the box has no task key |
| 21 of 61 accuracies ≤ 0.20 | `map.json` best_coordinate | MNIST chance is 0.10; the "pass" label is inflated for a third of the map |
| The box carries no task, epochs, batch, seed | box = 6 axes only | the row cannot be reproduced, and the ruler is unstated |
| The screen is uncalibrated | all 5 controls at `0.09375`, `cause=divergence` on digits | PASS/DEFECT at that box is a coin flip |
| The P0 box was 32 batches | `P0_BATCH_LIMIT=32`; `adam` 0.198, `euclidean` 0.540 | at 375 batches: `adam` 0.927, `lion` 0.914, `euclidean` 0.894 — the box ranked by step size, not mechanism |
| The P0 box declared an impossible ceiling | `P0_PARAM_BUDGET=10000`; `hidden_dim=128` composes 118,282 parameters | the screen never checked the ceiling: every row was outside its own box |
| `mean_norm`'s default step was 10x too large | 0.01 → 0.101 (chance); 1e-3 → 0.887 at the same box | an absolute-displacement rule needs an absolute step, not an lr |
| The screen minted its own verdict | `chance = 0.1; PASS if val_acc > chance + 0.02` | a second bar, and a verdict from a 1-seed cell — the thing this plan forbids |
| Two implemented primitives cannot compose | `ClosedFormRidgePlasticity` and `NoisySubstrate` exist with specs, capability rows (C75) and acceleration specs, but the axis registry omits them | a capability that exists, is advertised in the README, and is unreachable from the space |
| Five update primitives "pass" at chance | `adam` 0.198, `lion` 0.198, `mean_norm` 0.129, `spectral_constrained` 0.161, `elastic_consolidation` 0.161 vs `euclidean` 0.540 | these are standard optimizers: a chance score is a **step-size defect**, not a coordinate |
| Every substrate lands in a 0.49–0.63 band | 9 substrate rows, one algorithm, one task | a 14 pp band answers "does the substrate perturb MNIST", not the substrate→algorithm question; that needs a substrate-sensitive metric/task |

The pattern: **the map is a legality report with numbers attached.**

---

## 2. The unit of knowledge: a comparable cell

A map row is a **cell** with five fields, and a row is only comparable when the
four fixed fields match the slice:

```
cell = (varied axis value, base box, task + ruler, control, resource vector)
```

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

## 3. Seven defect classes and their locks

| # | Class | Permanent fix | Lock |
|---|---|---|---|
| D1 | **Inventory drift.** Three lists of primitives. | `AXES_REGISTRIES` is the only inventory; census, map, README and method cards are projections. | `test_inventory_single_source`: count == sum of axes, every primitive has a map row |
| D2 | **Box unread.** Batch/steps/knobs are not checked against the claim. | `Schedule` **is** the box; add `batch_size`, `steps_per_task`; print it, store it, compare on claim. No parallel `Box` type. | `test_box_identity`: change `batch_size` alone → claim refuses |
| D3 | **Incomparable rows.** 57 boxes, one ruler. | One base per slice; a row differing elsewhere is `swapped`; the ruler is per task family. | `test_slice_comparability`: a non-base row cannot be treated as comparable |
| D4 | **Uncalibrated screen.** PASS at a box where the control is at chance. | Every slice publishes a control; below the bar → `chance`, no status. | `test_screen_power`: a constant arm yields `chance` |
| D5 | **The screen mints a verdict.** P0 computed `PASS` above a local `chance = 0.1` — a second bar, and a judgment from one seed. | A screen emits measurements and execution defects only; a bar is a gate floor and a comparison is pre-registered. | `test_screen_has_no_verdict`: no `PASS`/`viable` key from `run_p0_track` |
| D6 | **Untested extension path.** No acceptance test adds a primitive. | A fake credit through the documented ramp → a map row in ≤60 s. | `tests/acceptance/test_extension_path.py` |
| D7 | **Docs drift.** Recipes and numbers live in prose. | Every recipe runs at its declared box in `tests/docs/`. | `test_recipes_reproduce` |
| D8 | **An axis that does not bind.** 9 substrates "pass" on an MLP. | Every slice declares its binding condition; a non-binding axis is `inert`. | `test_binding_condition`: a substrate row on MNIST is `inert`, not `pass` |
| D9 | **Implemented but not composable.** 2 primitives exist outside the axis registry. | Registry derived from `primitives/*/spec.py`; every spec must compose. | `test_spec_composes`: every spec id resolves to an axis row |

D1–D3 cost no compute. They are the difference between a map and a table of
numbers.

---

## 4. Roadmap, in order

Order by dependency: a map of unread boxes is not a map (P0); a slice whose
control is at chance cannot label anything (P1); only then is a census meaningful
(P2); interactions require a fixed base (P3); the deep dive is chosen by the map
(P4); the external path and public artifacts follow (P5).

### P0 — One inventory, one box, one record (no training; 1 session)

**Decision:** can a map row be reproduced from itself? Today no.
**Deliverable:**
- `AXES_REGISTRIES` → the inventory; `ALL_PRIMITIVES` becomes a projection
  (or is deleted); census, map, `sec_loop` and the README counts are projections
  (73 rows, not 62).
- `Schedule` gains `batch_size`, `steps_per_task`, `seeds`; the CL runner and
  the kernel both build one; the map row stores it, task included.
- One record: the `sec_loop` JSONL line becomes a `Record` (or gains the same
  fields) — one schema, not two.
- Status vocabulary printed by the map, with `swapped` and `chance` as
  first-class states.
**Gate:** `pytest tests/property/test_inventory_single_source.py
tests/property/test_box_identity.py`.
**Done when:** 73 rows, each carrying task + box + ruler; changing the batch
alone makes the row non-comparable.

### P0.5 — The defect queue (before the census; ~1 h)

**Decision:** are the five chance-level update rows defects rather than results?
**Deliverable (measured 2026-11-18):** the 32-batch box was the first defect
(375 batches: `adam` 0.927, `lion` 0.914); the 10k ceiling was the second
(118,282 parameters, now 150k); `mean_norm`'s default step was the third
(0.01 → 0.887 at 1e-3). Re-measured, all six are `MEASURED` — no verdict.
`spectral_constrained` and `elastic_consolidation` measured 0.626 at their
defaults: a number, and a candidate for a step-size ladder, not a verdict.
**Also:** reconcile the inventory — add `closed_form_ridge` and `noisy` to their
axis rows (or delete their specs and capability rows), and give `split_mnist`
its domain.
**Gate:** `test_spec_composes`, `test_binding_condition`, and the five cells'
verdicts.
**Done when:** each near-chance row is a defect probe with a name, or a
measurement at its own declared default — never an unexamined label.

### P0.75 — Declare the binding conditions (no compute; 1 hour)

**Decision:** for each axis, what must be true for it to bind?
**Deliverable:** a binding condition per axis: substrate (substrate-sensitive
metric/task: bit-width, energy, spike timing), credit (label channel),
update (own step size), dynamics (a settle), plasticity (a ψ lifecycle),
geometry (a layer/cell/graph form). The map labels a slice whose condition is
unmet `inert`, and the substrate/credit slices are chosen to meet it.
**Done when:** no axis is "measured" by a box where it cannot act.

### P1 — Calibrate the box (pilot, ~30 min)

**Decision:** at which box does a published control clear the bar on each task
family, and what does a cell cost?
**Deliverable:** one base box per family (vision, tabular, graph, sequence):
`batch_size`, `steps/task`, `epochs`, chosen so the control is above chance
and the cell is ≤ ~2 min. Publish `cells/hour`, measured, not estimated.
**Box:** MNIST at 1 epoch, batch 32 (control ≈ 0.85–0.95 measured today);
digits and iris need more steps or they stay at chance — the pilot says how many.
**Gate:** the pilot prints control ± σ and the bar; a slice with a chance control
is refused.
**Done when:** each family has a calibrated base and a measured cost per cell.

### P2 — The census (the first real map; ~2 h)

**Decision:** of 73 primitives, which train at their slice's base, which need a
swap, which fail, and at what cost?
**Deliverable:** `map.json` v3: 73 rows with `status` ∈ {measured, defect,
refused, unmeasured}, base box, task, rule, control, resource vector.
Unmeasured rows are `unmeasured`, not absent. A short report: measured/defect/
refused counts per axis, and the defect list with mechanisms named.
**Box:** the P1 base for MNIST; a primitive that is illegal at the base is
measured at its nearest legal box and marked `swapped`; each primitive is also
measured at its own declared defaults and marked `own-knobs`.
**Gate:** every row reproducible; every `fail` names a mechanism; the report
prints the inventory count.
**Done when:** the first map with no missing rows and no inflated status.

### P3 — The interaction slice (the map's structure; ~2 h)

**Decision:** which axis pairs change each other at the fixed base?
**Deliverable:** a factorial slice on the two axes with the most census variance
(chosen by the census: credit × geometry, or **substrate × credit** when the
substrate rows carry the variance — the substrate→algorithm question in
`PURPOSE.md` §3 is exactly this pair). 1 seed each at the base, then the top
interactions at 3 seeds. Reported as interaction effects with intervals, not a
ranking.
**Box:** the P1 base, only the two varied axes changing.
**Gate:** the control clears the bar in every cell; a pair with no power is
marked, not reported.
**Done when:** the map has a measured interaction layer — the first evidence
about *which* axes matter together.

### P4 — The deep dive (the thesis, chosen by the map)

**Decision:** which region deserves a matched, tuned comparison?
**Deliverable:** the census's most surprising measurement (today the candidate
is local credit at low batch) gets: a 3-point ladder per arm on its primary knob,
then 5 paired seeds at matched boxes; pre-registered margin, fixed n, no peeking.
**Box:** the family's base; a batch ladder `{1, 10, 32}` only if the map has
measurements at batch 32.
**Gate:** the paired CI at `n_max`; the claim names its box.
**Done when:** a claim, a coordinate, or a defect — and the map row is updated.

### P5 — The external path and public artifacts (staged)

- `comp verify --primitive <name> --slice <family>` — the same scanner; a
  stranger adds a credit through the documented ramp and holds a map row.
- `tests/acceptance/test_extension_path.py` — the fake credit end to end.
- Method cards from the map (`comp method-card`), recipes as tests, seed + box +
  replay hash on every row.
- A public slice: one family, one base, all 73 primitives, published with the
  scanner and the records.

---

## 5. The scan protocol (one page)

1. **One base per slice.** Only the varied axis changes; any other difference is
   `swapped`.
2. **Control first.** The published control at the base must clear the bar; else
   `chance`, no status.
3. **Cheapest falsifier.** 1 seed screens; 3 seeds confirm an interaction; 5
   paired seeds carry a claim.
4. **Budget in cells and steps.** Walltime is reported, never used to rank.
5. **Price from a pilot.** The watchdog is 2× the measured cell.
6. **Every row reproducible.** Task + box + seed + ruler + replay hash.
7. **A negative is a row**; a fail names its mechanism; `refused` carries a
   trigger.

---

## 5.5 The research protocol (allocation)

1. **Cheap tasks first.** The registry has 14 cheap, 14 medium, 2 expensive
   tasks; the census uses cheap, the interaction slice cheap/medium, the deep
   dive medium. The expensive two need a declared budget and a stop rule.
2. **Screen at the viability box, compare at the comparison box.** A primitive
   that fails at its own defaults is a defect probe; a primitive that moves
   between slices is an interaction.
3. **Successive halving.** 1 seed for screening, promote the top fraction to 3,
   then 5 paired for a claim. Budget in cells and steps; walltime is reported.
4. **Price from a pilot.** The watchdog is 2x the measured cell; a slice whose
   control is at chance is refused before it is priced.
5. **The map allocates.** The census's variance decides the interaction pair;
   the interaction's strongest effect decides the deep-dive region. No plan
   order overrides the map's own ranking.
6. **Every refusal and every failure has a trigger and an owner.** The defect
   queue is the map's backlog, not a separate document.

## 6. What we stop doing

- Promoting one thesis before the map exists; adding legality rows without a
  measurement (the factory is green).
- Reporting a map with missing rows, one ruler for all families, or a
  near-chance cell called `pass`.
- Full sweeps (the census is the sweep, stratified by legality); 1-seed claims;
  walltime rankings; documents longer than 300 lines.

---

## 7. What could make this plan wrong

| Assumption | Falsifier | Then |
|---|---|---|
| The map is the product | no slice yields a viable region beyond the known ones; the map is a legality audit with cost | publish the legality + cost map; it is still the first of its kind |
| A common base exists per family | no box lets a control clear the bar within 2 min | shrink the task (subset, 3 classes) or accept a 10-min cell; the box is declared |
| 73 rows are affordable | the calibrated base costs >5 min/cell | 3 sessions, axis by axis; the map accumulates, it is not a sweep |
| The interaction slice is the next question | the census shows one axis dominates (no interaction) | the structure is "this axis dominates"; that is a result, and P4 uses it |

---

## 8. Definition of done

- One inventory (73) projected into census, map, README and method cards.
- Every map row carries its task, base box, ruler, control and cost.
- Each family has a calibrated base with a measured cells/hour.
- No `pass` below control + 2σ; no missing row; no `swapped` row labelled
  comparable.
- One interaction result about which axes matter together.
- One deep dive chosen by the map, with a pre-registered claim or coordinate.
- A stranger adds a primitive and holds a map row without reading internals.

