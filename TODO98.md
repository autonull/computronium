# TODO98 — Test the Laws, Not the Grid

**Status:** 2026-11-21. Replaces TODO97's acceptance rule, and this plan's own
first draft (rows → evidence ladder). That draft still bought 255 five-seed
rows before anyone knew whether the laws work. This plan buys the cheapest
test that separates a defect from a bad hyperparameter, then hands the rest to
SEC as optimization.

**Progress 2026-11-21:** P0 and P2 landed. `comp test --surface` lists 75 laws,
6 seams and 78 rules (29 task-independent + 1 task-dependent + 48
availability). The P2 seams found and closed one composer defect: `recurrent`
never received `sequence` through the geometry builder, so the time axis could
not unroll from a composed cell. Its design facts and wave order are in §4.

**P1 landed 2026-11-21 (instrument + first measurement).**
`scripts/probes/p1_law_surface.py` ran all 75 laws in one process at 16
samples, 60 of the ≤200 steps, three learning rates, 12 lanes and a 150 s row
budget: 354 s, one row per law, exit 1. States: **9 `works`, 7 `test defect`,
12 `declaration defect`, 21 `defect-or-gap`, 17 `refused`, 7 `unproven
control`, 2 `defect (invariant)`**. Its pre-registered calibration gate fired
on that first run and is corrected in §4; the fork amendment below retracts its
two largest classes and sets P1's close.

**Fork amendment 2026-11-21 (binding, §3).** The six axes split into four
*carrier* laws — tested by a digest against their declared companion, µs — and
two *signal* laws — tested by the fit, ~0.3 s. The first run's 7 `test defect`
and 12 `declaration defect` rows are the instrument's blindness, retracted in
§3; P1's close is the five-ticket landing in §4.

**One sentence:** 75 laws × a positive/negative control pair, 6 protocol
seams, and the declared composition rules are the whole test surface; a
tiny-batch fit whose mechanism-removed control must fail is the defect line;
a family box is a screen the SEC loop owns, never a test.

**Batch-first (amendment 2026-11-21).** The unit of work is a program that
enumerates the surface, runs the fits and controls, writes one row per law,
and exits a verdict. Interactive per-law probing is debugging, not
measurement: it is how P1's three facts were found, and it is not how the 75
verdicts are bought. A program that cannot return "test defect" and exit
non-zero is not a batch; it is a green table.

---

## 0. Why the row count is the wrong unit

A row is `(primitive, family, box)`. Of those three, only the primitive's law
is mechanism, and only the law can be defective. **Family and box are
conditions**, and a box has free hyperparameters on purpose — its numbers move
when they change. Testing rows therefore multiplies hyperparameter choices,
not mechanism coverage:

| Unit | Count | What it can prove | What it cannot |
|---|---|---|---|
| Primitive law | 75 | the mechanism computes the thing it claims | its best hyperparameters |
| Protocol seam | 6 | two laws compose and exchange what they declare | every family's box |
| Declared rule | 2 tables + availability predicates | the rule refuses/accepts what it says | whether a cell trains |
| Family box row | 675 | this box ran once | the law, and the best box |

The repository already paid for this lesson twice. `pc_alm`'s "instability"
was an off-by-one in `geometry/recurrent` (S5k): the law was wrong and the
settle's hyperparameters made it look like a tuning problem. A ladder trained
a box the declared space refuses and published a `tuned` coordinate (S9). Both
cost hours of screen time to discover what a 1-second control would have said.

**Consequence:** the 675-row survey is retired as a test. It stays as the
screen cache the SEC loop reads, and `comp gate breadth` stays as evidence for
the 17 credits already measured at L2/n≥5. No new five-seed row is bought
until P1 says the law it measures is clean.

**The saving, stated as numbers.** The up-front spend was 255 five-seed rows
(255 × 5 seeds × 1–89 s ≈ 0.35–31.5 h serial) before any law was proven. The
surface spends ≤15 min wall (75 laws × 3 fits × ~1 s, 12 lanes) plus the
14 min rung-1 gate that already exists. A future primitive costs its five
derived tests (~15 s), not nine five-seed screens (~1–60 min).

---

## 1. The honest inventory (measured 2026-11-21)

Artifacts: `results/sec*/map.json` (9 family maps, 75 primitives each),
`results/sec*/ladders`, `experiments/*.duckdb` (465 stores), `docs/sec/map.md`.

| Item | Count | Source |
|---|---|---|
| Primitives registered (spec, task case, invariant, case fingerprint) | **75/75** | `primitives/registry.py` |
| Declared family rows (`primitive × family`) | **675** | 9 maps |
| Rows measured / refused / defective | **255 / 419 / 1** (`nca`) | maps |
| Primitives with ≥1 measured row | **65**; 10 have none | maps |
| Ladder records | 30: **18 `tuned` / 12 `unimplemented`** | `ladders` |
| Distinct primitives `unimplemented` | **11** | below |
| Claim-grade rows (E3) | **5** (2 claims, 1 CI, 2 no-power) | `results/sec_claims/claims.json` |
| Compiled kernels | **10/75**; 65 `kernel_status="absent"` | `primitives/kernels.py` |
| Capability suite | 62 passed / 14 skipped at one priced cell (14m11s) | `tests/primitives/test_primitive_capability.py` |
| Audit | 0 findings | `scripts/audit.py` |

**Named rows the surface must reproduce** (the expected hits, not a second
work list):

| Class | Rows | Trigger |
|---|---|---|
| confirmed defect | 1: `geometry.nca` | `grid_hw` 16×16×3 vs mnist's 784 features |
| missing mechanism recorded as refusal | 18: `plasticity.rule_state` (9), `plasticity.substrate_coupled` (9) | no `modulate()`; no-op at the plasticity protocol |
| `unimplemented` ladder (12 records, 11 primitives) | `forward_tangent`, `pc_alm`, `target_inversion`, `conv`, `error_predictive_coding`, `local_goodness` (vision+tabular), `diffusion`, `random_projections` (tabular), `zeroth_order` (tabular), `tile`, `spike_integration` | ladder's `_TRIAGE`, or no knob |
| no measured row anywhere | `complex`, `conv`, `eligibility_prop`, `nca`, `optical`, `quantum`, `rtrl_reference`, `rule_state`, `substrate_coupled`, `unbiased_rtrl` | 419 refusals, 10 primitives |

"0 unaccounted rows" is bookkeeping. The 419 refusals are box statements; the
10 primitives with no measured row are the ones §2's harness names explicitly.

---

## 2. The whole surface (this is what "tested" means)

Three units, one test per unit, all derived from declarations the registry
already holds. A new primitive adds one declaration row and gets its five
tests automatically — no per-family test code, ever.

### A. 75 laws

| Test | Question | Cost |
|---|---|---|
| **L-a invariant** | does the law produce the shape, finiteness, sign, non-zero step its definition states, and change a parameter? | one step, µs |
| **L-b fit** | can it drive a tiny problem to its floor under **some** legal setting? | ≤200 steps on 16 samples |
| **L-b⁻ control** | with the mechanism removed (zeroed pseudo-gradient, disabled settle, cut recurrent weight), does L-b fail? | same cost, run once |
| **L-c knob** | does the knob the law declares it reads move the fit? | 3 values × L-b |
| **L-d determinism** | same seed/same output (exists in `test_primitive_contract.py`) | µs |

### B. 6 protocol seams — one exemplar each, E1

| Seam | Exemplar | What it proves |
|---|---|---|
| label channel | one credit with `label_channel` on a classified task | the target reaches the credit |
| token lane | `causal_transformer` + a token task | ids/targets broadcast |
| time axis | `recurrent` + `delayed_cue` | `(time, batch, features)` unrolls |
| graph topology | `graph` + `cora` | edge_index reaches the topology |
| settle | `energy_minimization` + one geometry | the settle converges |
| joint plasticity | a non-null plasticity + update | both update paths run |

Each is one E1 cell (or a 1-batch run) plus a contract assertion. These are
the only cells in the plan that train a task.

### C. The declared rules

`compiled_void_rules` (2 tables) plus the axis availability predicates. Each
rule gets its accept/refuse pair — most already exist. A rule that cannot be
shown to refuse a concrete illegal cell is prose, not a rule.

**Not in this surface:** family boxes, screens, ladders, claims. Those are SEC
measurements; they are the loop's instrument, not its gate.

---

## 3. The defect line: three cheap discriminators

The fine line the plan must encode: **a defect means no legal setting works;
a bad hyperparameter means some legal setting works.** So the test is not
"does the default box clear the bar" — that confounds the two. It is:

### L-b, the tiny-batch fit

- 16 samples from the primitive's cheapest declared family, deterministic
  (fixed seed, no shuffle, no seed sweep).
- ≤200 optimizer steps.
- lr grid: `{default, ×10, ×1/10}`. A grid point outside a declared bound is
  **dropped and reported** (`PC_ALM_GAIN_CEILING` on the gain, a settle step
  cap, a ternary threshold), never clamped silently: "the admissible rung does
  not fit" is a finding, not a reason to widen the grid. No other
  hyperparameter is swept.
- Criterion: **train loss ≤ 0.1 × its untrained value** at ≥1 grid point.
  A magnitude, not a bar, so it works for classification, regression and LM.
  **Error-blind laws** (`homeostatic`, `temporal_trace`) have no fit
  criterion by contract: their L-b is "the output is bounded and not
  constant", and their control is a frozen state.
- If no grid point fits: the mechanism is wrong, or the law needs a primitive
  it does not have. That is the only ambiguity, and it is named, not swept.

### L-b⁻, the control that makes "fail" mean defect

Zero the mechanism's contribution (pseudo-gradient → 0, settle disabled,
recurrent weight → 0) and run the same fit. The control **must fail**. A
positive/negative pair is the lock: a fit that passes with the mechanism
removed is measuring the optimizer, not the law.

### L-c, the knob response

Run the fit at three values of the knob the law declares (`reads(config)`),
and require the fit loss/time to differ. Deterministic, so any difference is
the knob. An inert knob is a **declaration defect**: the law reads a value it
does not use (this is what S9g spent probe time discovering for three credits).

### The decision table (encoded, not argued in prose)

| L-a | L-b | L-b⁻ | L-c | Verdict |
|---|---|---|---|---|
| fail | — | — | — | **defect**, named invariant |
| pass | fail at every admissible grid point | fails (good) | — | **defect or capability gap**: fix, or name the primitive that closes it; a dropped grid point is reported with it |
| pass | pass | **passes** (bad) | — | **test defect**: the fit measures the optimizer, not the law |
| pass | pass | fails (good) | inert | **declaration defect**: the knob is declared but unread |
| pass | pass | fails (good) | responds | **works (E1)**; tuning belongs to SEC |

A row below its bar is then one of exactly: a defect (this table), a
capability gap (the table's second row, with the closing primitive), or
tuning (last row, SEC's job). No fifth reading.

`unproven control` is not a fifth reading: it is the harness declining to
measure a law on an axis whose control is not demonstrated. It is never a
verdict and never counts toward done. A program that reports it as `works`
has produced a test defect, not a result.

### Amendment 2026-11-21 (binding): the fork comes first

The first batch run measured the fork instead of assuming it. The six axes
split by what the law transforms, and that split — not a per-axis strategy
table — decides the instrument:

| Class | Axes | The law transforms | Removal (declared) | Test | Cost |
|---|---|---|---|---|---|
| **carrier** | substrate, geometry, dynamics, plasticity | a value that flows | the neutral companion: `digital`, `feedforward`, `instantaneous`, `null` | `digest(step(law)) != digest(step(companion))` | µs |
| **signal** | credit, update | the learning channel | zero pseudo-gradient, identity step | the fit must die | ~0.3 s |

The rules that follow supersede the table above where they differ:

- **L-b is the signal laws' test.** For a carrier law a fit is not a test: the
  companion reaches it by construction (measured 2026-11-21: `nca` control
  0.184; `energy_minimization`, `noisy`, `sparse`, `ternary`, `routing`,
  `closed_form_ridge`). A companion that reaches is not a defect of the law;
  it is the wrong instrument.
- **A carrier law's L-b⁻ is a digest inequality**, not a loss. Equal digests
  mean the law *is* its companion: a declaration defect, named.
- **L-c reads the digest first.** A knob is *read* when it changes the case's
  digest, inert when the digest is unchanged. The fit is L-c's second reading,
  for signal laws only. The first run's 12 `declaration defect` rows are
  **retracted**: `feedback_lr`, `hidden_dim`, `grad_clip` and `fisher_damping`
  are read, and the fit at one box does not bind them.
- **The corrected table:**

| L-a | carrier: digest vs companion | signal: fit | control | L-c | Verdict |
|---|---|---|---|---|---|
| fail | — | — | — | — | **defect**, named invariant |
| pass | differs | — | — | read | **works (E1)**, carrier law |
| pass | equal | — | — | — | **declaration defect**: the law is its companion |
| pass | — | fails everywhere | — | — | **defect or capability gap**, signal law |
| pass | — | passes | **passes** | — | **test defect**, signal law only |
| pass | — | passes | fails | inert | **declaration defect**, signal law |
| pass | — | passes | fails | responds | **works (E1)**, signal law |

`test defect` now means exactly one thing: a *signal* law's control still fits.
Exit 0 becomes reachable without inventing controls, and the 200-step box
applies to 26 laws instead of 75.

---

## 4. The program (dependency order, prices measured or explicitly priced first)

### P0 — Declare the surface (0 cost, first) — **done 2026-11-21**

- One `SURFACE` table: 75 laws (id + knobs), 6 seams (exemplar task + cell),
  2 rule tables with their accept/refuse pairs. `comp test --surface` lists
  it; the harness parametrizes from the registry, not from a second list.
- **Delete** every per-family test that re-screens a box: a family difference
  is a screen, not a test. The audit's duplicate-body predicate already
  forbids a second copy.
- **Fingerprint-keyed:** a law re-runs only when its canonical case
  fingerprint (`PrimitiveProtocol.fingerprint`, a deterministic hash of the
  law's output) or its declaration changes; unchanged laws read their cached
  surface result. That is the future saving: a new session pays for the
  fingerprints that moved, not for 75 laws.
- **Rung 1 stays.** `test_primitive_capability.py` (62 passed / 14 skipped,
  14 min) is the AGENTS one-family gate; the tiny fit does not replace it, it
  decides the defect line more cheaply. Both run once per law, never per
  family.
- **Close:** the surface count equals 75 + 6 + rules; no test names a family
  box; an unchanged fingerprint does not re-run.

**Landed:** `computronium/primitives/surface.py` derives laws (registry +
`AxisSpec.accepted_params`), seams, and rules (compiled void tables +
harvested availability predicates) on call — no second list.
`tests/primitives/test_surface_lock.py` proves registry derivation (a fake
row appears), six declared exemplars, the rule tables, no family-screen test,
and the refusal's failing test. `test_no_test_names_a_family_box` passes
with only `test_primitive_capability.py` declared. **Not landed:** the
fingerprint cache; it is the first P1 task, not a P0 row.

### P1 — Run the batch on all 75 (the decisive spend, ≤ 15 min wall) — **landed (instrument); close open**

The deliverable is one program, `scripts/probes/p1_law_surface.py`, with a
per-axis strategy table — not 75 interactive checks. It enumerates the
surface, runs L-a, then a tiny fit at the declared lr grid, then the
mechanism-removed control at the best passing point, then L-c, and writes
`results/p1/surface.json` + `surface.md`. One row per law:

```
id, axis, family, state, fit_loss, control_loss, knob, delta,
walltime_s, box, fingerprint, decided_by
```

| State | Meaning |
|---|---|
| `works` | L-b passes and the control fails (E1; tuning belongs to SEC) |
| `defect (invariant)` | L-a fails; the named invariant is the finding |
| `defect-or-gap (mechanism)` | no admissible grid point fits; P3 names the fix or the closing primitive |
| `declaration defect` | fit passes, control fails, but L-c moves nothing |
| `refused` | the declared space refuses every cell (the one `impossible` row) |
| `unproven control` | no demonstrated control on this axis; not measured, not done |

The exit is the verdict, not a log line:

| Exit | Meaning |
|---|---|
| 0 | measured rows all carry a failing control; calibration reproduced |
| 1 | test defect: a known non-pass fits, or a row has no control |
| 2 | the surface disagrees with the registry (wiring defect) |
| 3 | partial: `unproven control` remains (wave N is done) |

**Waves, cheapest axis pair first.** The program refuses to emit a verdict
for an axis whose control is not demonstrated. Each wave adds one strategy
row and a lock; the driver does not change.

| Wave | Axes | Laws | Control | Fits (≤4/law) |
|---|---|---|---|---|
| 1 | credit, geometry | 31 | zero pseudo-gradient; frozen/zeroed weights | 124 ≈ 43 s serial |
| 2 | dynamics, update | 26 | instantaneous settle; unchanged parameters | 104 ≈ 36 s serial |
| 3 | plasticity, substrate | 18 | null psi; identity forward | 72 ≈ 25 s serial |

- **Calibration is the gate, not the epilogue.** Wave 1 must reproduce `nca`
  and `conv` as non-pass before it writes a row; wave 3 must show
  `rule_state` and `substrate_coupled` as `unproven control` or
  `defect-or-gap`, never `works`. If a known non-pass fits, the program
  writes no table and exits 1.
- **Restart is a row.** Results are keyed by `(id, declaration hash, case
  fingerprint)`; `--resume` skips finished rows and retries only `incomplete`
  ones. A killed row is never read as `works`.
- **The ladder stays in the program.** L-a → fit → control → L-c; every row
  records `decided_by`. A law that needs a 4th lr point is reported at its
  ceiling, never retried.
- **Close:** wave 1 exits 0 or 1; all 75 rows after three waves; 0
  `unproven control`, 0 unexplained fits, and `validate()` clean.

**Measured before the driver (2026-11-21), three facts that shape it:**

1. The micro-case fit works: 200 `train_step`s on the case's 4-sample batch
   drop CE 1.33 → 0.004 in ~0.35 s on CPU (`gradient`, `feedforward`,
   `euclidean`, `digital`, `instantaneous` all measured). A fit is cheaper
   than the plan's budget, so cost is not what P1 spends.
2. That fit converges through geometry + credit on *every* axis, so a single
   uniform fit does not isolate a substrate, dynamics or plasticity law. A
   control that replaces those laws with a neutral companion still fits; the
   per-axis control is the P1 design work, not a grid sweep.
3. `case.config` is not read by the migrated references (`cases.step` rebuilds
   from `cell_config`), so `config_reads` is empty for all 75. L-c must vary
   the composed axis config (`CellConfig` / coordinate params), not the case
   dict; `AxisSpec.accepted_params` is the live knob declaration.

The three fit/control pairs that shaped the driver are in the wave table; the
measurement (below) resolved them: only credit and update keep a decisive
removal, and the four companion axes report `test defect` until a
mechanism-removing control exists for them.

**Landed 2026-11-21.** `computronium/primitives/fit.py` is the instrument and
`scripts/probes/p1_law_surface.py` is the batch. The design work the waves
named resolved into four rules:

- **The cell** is the family's base box with the law's own axis, at the
  family's declared input shape and parameter budget (`TaskRegistry` shape, no
  dataset, seeded composition), so the fit prices a law the screen could price.
- **L-b⁻ is per axis, and only two removals are decisive.** A credit's
  pseudo-gradient is zeroed and an update's step is identity; a geometry, a
  settle, a substrate and a plasticity law are replaced by their *declared*
  neutral companion (feedforward, instantaneous, digital, null). The companion
  reaches for every one of those four axes — 7 `test defect` rows — so the fit
  is **decisive for credit and update only**: §4's design fact 2, measured.
  Zeroing a geometry's parameters in place is not a removal: the pipeline
  rebuilds the weights at the first step (measured: a zeroed `nca` cell trained
  to the same loss).
- **L-c's knob is the composed cell's own active knob** (`axis.name` in
  `ComposedCell.params`), never a preference list: a declared-but-inactive knob
  is not L-c's, and the override that varies it is never refused as dead
  configuration.
- **A fit is seeded and priced by its row**: `cell()` seeds the composition, so
  two fits of one declaration start from one weight set, and a row that spends
  its budget is `refused` (over budget), never `works`.

**What the first measurement found** (box above; `results/p1/surface.md`):

| Finding | Rows | Evidence |
|---|---|---|
| the fit cannot test geometry, settle, substrate or plasticity (**retracted as a defect: this is the fork**) | 7 `test defect` | the companion reaches (`nca` control 0.184, `energy_minimization`, `noisy`, `sparse`, `ternary`, `routing`, `closed_form_ridge`) |
| declared knobs that move no fit (**retracted: the knobs are read, the fit does not bind them**) | 12 `declaration defect` | `feedback_lr` (4 credits), `hidden_dim` (2 geometry), `grad_clip` (5 updates), `fisher_damping` |
| no legal setting fits | 21 `defect-or-gap` | `forward_tangent`, `target_inversion`, `temporal_trace`, `rule_state`, `euclidean` at 60 steps |
| the declared space refuses the cell | 17 `refused` | 13 void constraints + 3 batch-layout disagreements + `complex` |
| the law's L-a fails | 2 `defect (invariant)` | `plasticity.null`, `substrate_coupled` — both return an empty plastic state by contract, so this is the *instrument's* L-a, not the law |
| no declared family base box | 5 `unproven control` | `optical`, `quantum`, and 3 substrates whose cell records no knob |

**The calibration gate fired on its first measurement, and is corrected.**
`geometry.nca` came out `works` and `geometry.conv` `declaration defect`; the
screen had priced them `defective` (a cross-config wiring defect: a
feedforward-shaped grid inside nca's cell) and `refused` (a 60 s cost cap). A
fit that composes one cell from one coordinate cannot reproduce either: nca's
law trains when its cell is built correctly, which **locates** the defect in
the screen's wiring (P3), and conv's cell trains at a cost the wave cannot pay
(P5). The gate now calibrates on classes a fit *can* price — `substrate.complex`
→ `refused` (declared void constraint) and `credit_assignment.forward_tangent`
→ `defect-or-gap` (a ladder `unimplemented` row) — and reproduces both.

**Open (P1 close) — the fork landing: five tickets, one session, one commit.**
Each names its file, its change and its size; the session runs them as one
edit pass, then one gate block, then one measurement (§10).

| # | Ticket | File | Size |
|---|---|---|---|
| T1 | declare `AXIS_KIND` (6 rows: 4 carrier, 2 signal) and expose `Law.kind` through `comp test --surface` | `experiment/schema/axis.py`, `primitives/surface.py` | +6 rows, +1 field |
| T2 | `fit.control` dispatches on `kind`: carriers return the companion cell, signals the zeroed channel. Delete the four-way companion match and the per-axis dispatch; the two signal proxies stay | `primitives/fit.py` | −60 / +40 |
| T3 | `fit.decide` gains the carrier verdict (`digest(law) != digest(companion)`); `test defect` only for a signal law; L-c reads digest, then fit | `primitives/fit.py`, `scripts/probes/p1_law_surface.py` | edit |
| T4 | `--only {all,unmeasured,signal,carrier}` selects a class: `unmeasured` reads the screen cache so the fit is bought only where no row exists | `scripts/probes/p1_law_surface.py` | +1 flag |
| T5 | locks: `test_a_carrier_law_is_tested_by_its_digest`, `test_a_signal_law_is_tested_by_its_fit`; retitle the two fit locks "signal" | `tests/primitives/test_surface_fit.py` | +2 tests |

**Allocation: the digest is free, the fit is priced.** 55 of the 75 laws
already carry a measured family row (§1); **20** carry no law-level evidence —
the 10 with no measured row ∪ the 11 ladder-`unimplemented`, less `conv`. The
batch spends accordingly:

| Applied to | Instrument | Cost |
|---|---|---|
| all 75 | the digest: L-a plus carrier-vs-companion equality | µs each |
| the 20 informative laws, plus any law whose digest fails | the fit, its control and L-c | ~0.3–1 s each |
| the 55 already measured | reuse the row; buy no new fit | 0 |

The 55 are not re-tested to confirm a number the repository published; a fit
adds evidence only where a law has none. The 200-step box therefore runs on
~20 laws, not 75 — measured, not guessed (26 laws at 60 steps cost 188 s, so
the box is minutes, not seconds).

**After T5 (expected):** 49 carrier rows from µs digests, 26 signal rows from
fits (of which ~20 are new evidence), 0 `test defect` from companions, 0
retracted declaration defects. Exit 0 requires every signal law to keep a
failing control and every carrier digest to differ.

**Do not** buy the 200-step box for all 75 first: it prices an instrument the
fork is about to replace (measured: 354 s for the 60-step box, and the fit is
idle for 49 of those laws).

**The one unknown, named so the session does not guess.** A carrier digest
needs the *companion's* case, and `cases.build_case` builds from the law's own
cell. T2/T3 add one helper (`fit.companion_case`) that composes the companion
cell and reuses `cases._payload`; the alternative is `cases.step` on the law's
case with the axis config replaced. Measure which composes; do not hand-roll a
second payload builder (that is the duplicate-body defect the audit forbids).

### P2 — The 6 seams (one E1 cell each, ≤ 10 min) — **done 2026-11-21**

Each seam's exemplar runs its 1-batch or 1-epoch cell and asserts the exchange
it declares (label reaches credit, ids broadcast, time axis unrolls,
edge_index reaches topology, settle converges, both update paths run).

- **Close:** 6/6 pass, or a named defect with a lock.

**Landed:** `tests/property/test_protocol_seams.py` runs all six exchanges,
keyed by the surface's seam declaration (a declared seam without a check
fails). **Defect closed:** `recurrent` + `sequence` was unreachable through
`compose_configs`; `sequence` is now a declared recurrent geometry key and
the builder passes it, so `(time, batch, features)` unrolls from a composed
cell (measured `(3, 4, 4) → (3, 4, 4)`).

### P3 — Close the defects the surface found

- Each defect: the named mechanism, a failing control, and the fix that
  flips it. A refusal is allowed only with a test that fails without it.
- A capability gap names the primitive that would close it and the family it
  unlocks. That row is work, not a verdict.
- **Close:** 0 defects; 0 `unimplemented` without a test; no refusal whose
  trigger names a missing mechanism without a failing test.

### P4 — Then, and only then, SEC optimization

The loop optimizes hyperparameters; it is worthless on a defective law. Its
instrument is the screen (1 seed) and the ladder (3 points + 1 confirmation
seed); its biggest-swing lever is the box, and P1 already proved the law.

- The 675-row survey is the loop's cache: reuse a row, never re-buy it.
- `comp gate breadth` (17/17, exit 0) stays as the cross-family evidence.
- A claim (E3) is bought only for a row where a knob binds and the loop will
  act on the answer: 5 rows today, not 255.
- **Never** use a screen as a capability gate: a screen is 1 seed, and the
  breadth exit already measures at L2/n≥5.
- **The search space is L-c's output**: HPO sweeps only the knobs that moved
  a fit (plus the declared availability predicates). A dead knob in the search
  space is wasted trials, and L-c names it for free.

**The first ladder and the first claim are named, not implied.** The loop's
first ladder runs on the highest-`works` signal law at its cheapest family —
`update.adam` on `mnist` is the current candidate — 3 points on
`update.step_size` plus 1 confirmation seed, recorded as a coordinate range.
The first claim is that coordinate at a pre-registered `n_max = 5`
(`configs/preregistrations/` committed before the first seed), using the
screen cache's row where it exists. Until it lands, the 5 existing E3 rows
(`results/sec_claims/claims.json`) are the branch's claim-grade evidence, and
`comp gate breadth` (17/17) is the cross-family one.

A session that ends without a named ladder target has not entered the loop:
the surface is the entry ticket, and one ladder plus one claim is the price of
admission.

### P5 — Kernels, priced per module, only for clean laws

10 of 75 have a compiled kernel. Port a module only after its law passes P1;
a kernel for a defective law accelerates a wrong answer. Price the first
module's parity + kill + microbench, then price the rest from it.

### P6 — Reproduction (E4), last

One control and one earned claim on a second process and device profile. No
claim is "works here and elsewhere" until this runs.

---

## 5. Definition of done

1. **The surface is declared**: 75 laws, 6 seams, the rule tables — and no
   per-family test exists. **Done 2026-11-21** (`surface.py`, `comp test
   --surface`, `test_surface_lock.py`).
2. **All 75 laws are in exactly one state** from §3's table, each with the
   control that proves it. 0 defects, 0 unexplained fits, 0 inert knobs
   presented as tuning, 0 `unproven control`. **Partial, P1 (batch landed):**
   all 75 are measured at 60 steps (§4). The fork amendment (§3) retracts the
   7 `test defect` and 12 `declaration defect` rows as instrument blindness; the
   five-ticket landing (§4) replaces the fit with a digest for the 49 carrier
   laws and keeps it for the 26 signal laws. The two `defect (invariant)` rows
   are the instrument's L-a on no-op plasticity and go with T5.
3. **6/6 seams pass** their declared exchange. **Done 2026-11-21**
   (`test_protocol_seams.py`).
4. **Every refusal carries a test that fails without it**; every refusal
   trigger names a rule, not a missing mechanism. **Partial:** the one
   declared refusal (`primitive.substrate.complex`) fails without its void
   constraint; the two gap rows (`rule_state`, `substrate_coupled`) name the
   mechanism that would close them, and P3 owes them their failing controls.
5. **SEC runs on clean laws only**, reusing the screen cache; a claim exists
   only where a knob binds. **Open, P4.**
6. **Every kernel row passes kill + parity**; every absent row is documented
   as reference-only. **Open, P5.**
7. The audit answers the same questions: no test names a family box, no
   refusal without a failing test, no kernel without parity. **Partial:** the
   family-box lock passes; the other two are P3/P5.

**Not done because a row closed.** A refusal is a box statement; a screen is
E1; a width search is not a mechanism fix.

---

## 6. Cost model and stop rules

- **The unit of cost is the law, not the row.** One signal law ≤4 fits (3 lr +
  1 control, ~0.3 s each); one carrier law one digest pair (µs); one family row
  ≈ 1–89 s per seed, ×5 for E2. Spend the first, buy the second only where the
  loop will act.
- **The fork is the measured price.** 75 laws at 60 steps cost 354 s at 12
  lanes; 26 of them (wave 2) cost 188 s. The digest decides 49 laws in µs, so
  the fit's 200-step box runs on the 20 laws with no measured row — and the
  other 55 reuse their row. A 200-step box over all 75 prices laws the digest
  already decides and rows the repository already published.
- **The batch is the unit of spend.** A wave is one process tree at 12 lanes;
  a single law is a debugging step, not a session. 300 fits ≈ 105 s serial,
  under a minute at 12 lanes.
- **A tiny fit is deterministic**: no seed, no CI, no HPO. Its threshold is a
  factor off the untrained loss, so it needs no bar and no noise model.
- **A grid is capped by declared ceilings, not by luck**: 3 lr values inside
  the stability bound. If a law needs a 4th grid point to fit, the ceiling is
  the finding.
- **The row budget, not the family price, is the watchdog.** A per-fit
  watchdog priced from the family's base fit killed legitimate laws (measured
  2026-11-21: half of wave 1); the batch now gives each row a wall budget
  (150 s measured) and refuses a row that spends it. A wave killed past it is
  a compose or cost defect: record, re-price, do not retry blind.
- **Lanes:** 12 concurrent processes, 2 threads each (measured on 16 cores).
  A 4-worker run's 300 s timeouts were contention, not verdicts.
- **A green wave is not a verdict.** Exit 0 requires the calibration gate;
  a row without a failing control is a test defect, not a result.
- **Rows land before the summary.** A killed wave keeps its finished rows;
  only `incomplete` rows are retried.
- **Stop when decided:** a defect closes on its failing control; a seam
  closes on its exchange; a claim closes on its fifth paired seed.

---

## 7. Locks this plan adds

| Lock | It must fail when |
|---|---|
| `test_a_law_fit_fails_without_its_mechanism` | the negative control passes (fit measures the optimizer) |
| `test_a_law_fit_passes_under_some_legal_setting` | a law with a passing grid point is called a defect |
| `test_an_inert_knob_is_a_declaration_defect` | a declared knob moves no fit and is called tuning |
| `test_no_test_names_a_family_box` | a per-family screen returns as a test |
| `test_a_surface_row_is_registry_derived` | a second list disagrees with the registry |
| `test_a_refusal_has_a_failing_test` | a refusal exists without a test that fails without it |
| `test_every_seam_has_a_check` | a declared seam has no check |
| `test_seam_exchanges_what_it_declares` | the exemplar does not exchange what it declares |
| `test_the_batch_refuses_a_verdict_without_a_control` | an axis with no proven control reports `works` |
| `test_the_batch_calibration_gate_exits_nonzero` | a known non-pass fits and the batch still exits 0 |
| `test_the_batch_is_restartable` | a finished row re-runs, or a killed row reads as `works` |
| `test_the_batch_marks_unproven_axes` | a law on an unproven axis is `works` instead of `unproven control` |
| `test_a_carrier_law_is_tested_by_its_digest` | a carrier law is called `works` from a fit, or `defect` without its digest |
| `test_a_signal_law_is_tested_by_its_fit` | a signal law is called `works` from a digest |

**Landed 2026-11-21:** family-box, surface-row, refusal, both seam locks, the
three fit/knob locks and the four batch locks (`test_surface_fit.py`).
**Open:** the two fork locks, which arrive with T5. A rule lands with its lock.

---

## 8. First commands

```sh
# 1. P0: the surface, then prove it is the registry's own list   [DONE]
uv run python -m pytest tests/primitives/test_surface_lock.py -q
uv run comp test --surface            # 75 laws + 6 seams + 78 rules, exit 0

# 2. P1: the fork landing, T1-T5 in one pass (§4)                    [NEXT]
uv run python -m pytest tests/primitives/test_surface_fit.py \
  tests/primitives/test_surface_lock.py -q
uv run comp test --surface            # Law.kind printed; 75 laws, 6 seams
# the digests first (µs each), then the fit only where no row exists
uv run python scripts/probes/p1_law_surface.py --only carrier \
  --lanes 12 --row-budget 150 --out results/p1
uv run python scripts/probes/p1_law_surface.py --only unmeasured --resume \
  --steps 200 --row-budget 120 --out results/p1
# 3. SEC admission: one ladder, one claim (§4 P4)
uv run python scripts/probes/a3_ladder_epc.py --help   # the ladder instrument
uv run comp gate breadth                             # 17/17 stays green
# exit 0 is a verdict; exit 1 is a test defect; exit 3 is a partial class.
# Do not re-run interactively to "check" a nonzero exit.
# --resume never re-runs a finished row, and a later run never erases an
# earlier one's verdicts. The 200-step box applies to the unmeasured class.

# 3. P2: the six seams                                            [DONE]
uv run python -m pytest tests/property/test_protocol_seams.py -q

# 4. The gates that must stay green while the work lands
uv run comp gate breadth              # 17/17, exit 0        [GREEN 2026-11-21]
uv run python scripts/audit.py --static   # 0 findings        [GREEN 2026-11-21]
```

---

## 9. What we stop doing

- **Surveying 675 family boxes** to answer a question about 75 mechanisms.
- **Buying five seeds before the mechanism is proven**: a CI on a defective
  law measures the defect precisely and uselessly.
- **Calling a low box a defect**: the default box is a hyperparameter choice.
  The defect test is the fit with its control, not the screen.
- **Calling a missing mechanism a refusal**: a trigger that names a missing
  mechanism is work, and it needs a test that fails without it.
- **Treating "0 unaccounted rows" as capability.** It was TODO97's definition
  of done, and it is why 65 primitives never trained on two families while the
  plan reported progress.
- **Verifying each law interactively** when the batch can enumerate it. A
  prompt is not a row, and a hand-run fit is not a result.
- **Reading a green table as a verdict** without the calibration gate. The
  gate is the reason the batch can be left alone.
- **Zeroing a law's parameters to remove its mechanism.** The pipeline rebuilds
  them at the first step; the removal is a declared companion, and a companion
  that still fits says the *fit* cannot test that axis — a test defect, never
  `works`.
- **Calibrating a fit on a row the screen priced.** A cross-config wiring
  defect and a cost cap are the screen's classes; a fit reproduces neither, and
  a gate made of them can only trip.
- **Running one instrument over six axes.** A fit is the signal laws' test; a
  carrier law's removal is its declared companion, and the digest decides it.
  One ladder for all six produces 7 test defects and 12 false declaration
  defects by construction.

---

## 10. Running a session in one batch

The unit of a session is one landing: one edit pass, one gate block, one
measurement, one commit. A per-ticket run is a prompt, not a result.

```sh
# 1. edit T1-T5 in one pass (no intermediate runs)
# 2. gates, one block, streamed, walltime visible
uv run ruff format <changed files> && uv run ruff check --fix <changed files>
uv run pyright computronium/primitives/fit.py
uv run python -m pytest tests/primitives/test_surface_fit.py \
  tests/primitives/test_surface_lock.py -q
# 3. the measurement, background, polled at <=2 min, one log per run
nohup uv run python scripts/probes/p1_law_surface.py --only carrier \
  --lanes 12 --row-budget 150 --out results/p1 > logs/p1_digest.log 2>&1 &
uv run python scripts/probes/p1_law_surface.py --only unmeasured --resume \
  --steps 200 --row-budget 120 --out results/p1
# 4. one ladder on the best works row, one pre-registered claim OR nothing
# 5. one commit: plan, instrument, locks, measurement
```

Rules for the session:

- **One shard run, once.** The fit locks plus the surface lock are the gate; a
  green run is not repeated "to confirm".
- **A nonzero exit is the verdict.** Record it and its named rows; do not
  re-run to see a different number.
- **Batch the edits, not the judgments.** Five files change in one pass because
  they are one rule (the fork); each ticket is not its own commit.
- **Leave the plan as the queue.** A landed ticket leaves §4; an open one stays
  with its file, its size and its command.
- **A session ends at the loop's door or inside it.** A green table is the
  entry ticket; the session's result is a ladder coordinate or a claim, and a
  session that stops at the table says so and names next session's ladder.
