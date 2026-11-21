# TODO98 — Test the Laws, Not the Grid

**Status:** 2026-11-21. P0, P1 and P2 landed. P1 asks each law one question:
a carrier's step against its declared neutral companion (µs), or a signal's
fit against its cut channel (~1–10 s). `results/p1/surface.json` (instrument
3) holds all 75 states and exits 0. No family box is a test.

**One sentence:** 75 laws × the one question their axis declares, plus 6
protocol seams, are the whole test surface; a family box is a screen the SEC
loop owns, never a test.

**Progress 2026-11-21.** The surface and the seams landed first. P1 then
found and fixed three instrument defects before it could ask its question:
the substrate probe used the identity weight (every quantizer maps it to
itself, so `ternary`/`sparse`/`noisy` digested equal to `digital`), the
noisy law's declared `inject_state_noise` was never exercised, and L-a
rejected a plastic law whose case declares an empty state (`null`,
`substrate_coupled`). The substrate step now probes with a seeded dense
weight and applies the substrate's own state noise; L-a accepts a declared
empty plastic state. Two more fixes followed: a carrier digest now carries
the composed companion's cell (not the law's axis config), and a signal's
control runs on the fit's own criterion rather than on `reached`, which had
stranded `homeostatic` at `unproven control`.

**L-c is dropped (measured, not preferred).** Varying the "declared knob"
produced 12 `declaration defect` rows; all 12 were the *knob source*, not
the law. `fit.knob` read any numeric field the composed cell records, and
the composite records every config default. For `gradient` it picked
`credit.feedback_lr`, which the axis does not even declare
(`accepted_params` omits it) and `GradientCredit` cannot read
(`learned_feedback=False`; the law reads only `train_biases`). A knob that
moves no micro-reading at one box is a **coordinate**, and the search space
finds it at the cost it already pays (P4). No third reading replaces it.

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

The repository paid for this twice. `pc_alm`'s "instability" was an off-by-one
in `geometry/recurrent` (S5k): the law was wrong and the settle's
hyperparameters made it look like tuning. A ladder trained a box the declared
space refuses and published a `tuned` coordinate (S9). Both cost hours of
screen time to discover what a 1-second control would have said.

**Consequence:** the 675-row survey is not a test. It stays as the screen
cache the SEC loop reads, and `comp gate breadth` stays as evidence for the
17 credits already measured at L2/n≥5. No five-seed row is bought until P1
says the law it measures is clean.

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

**P1's 75 states** (instrument 3, both calibration gates reproduced, exit 0):

| State | Laws | Where |
|---|---|---|
| `works` | **40** (21 carrier, 19 signal) | digest differs / fit + failed control |
| `refused` | **16** (10 carrier, 6 signal) | the declared space refuses the base cell |
| `defect-or-gap (mechanism)` | **15** (3 carrier, 12 signal) | §4 P3 |
| `inert` | **4** (`feedforward`, `instantaneous`, `digital`, `null`) | the axis's declared neutral element |

**Named rows the surface must reproduce** (expected hits, not a second list):

| Class | Rows | Trigger |
|---|---|---|
| confirmed defect | 1: `geometry.nca` | `grid_hw` 16×16×3 vs mnist's 784 features |
| missing mechanism recorded as refusal | 18: `plasticity.rule_state` (9), `plasticity.substrate_coupled` (9) | no `modulate()`; no-op at the plasticity protocol |
| `unimplemented` ladder (12 records, 11 primitives) | `forward_tangent`, `pc_alm`, `target_inversion`, `conv`, `error_predictive_coding`, `local_goodness`, `diffusion`, `random_projections`, `zeroth_order`, `tile`, `spike_integration` | ladder's `_TRIAGE`, or no knob |
| no measured row anywhere | `complex`, `conv`, `eligibility_prop`, `nca`, `optical`, `quantum`, `rtrl_reference`, `rule_state`, `substrate_coupled`, `unbiased_rtrl` | 419 refusals |

The 419 refusals are box statements; the 10 primitives with no measured row
are the ones P1 prices explicitly. P1 reproduced the two calibration rows —
`substrate.complex` → `refused` and `credit_assignment.forward_tangent` →
`defect-or-gap` — so its states are the instrument's, not a green table.

---

## 2. The whole surface (this is what "tested" means)

Three units, one test per unit, all derived from declarations the registry
already holds. A new primitive adds one declaration row and inherits its
tests — no per-family test code, ever.

### A. 75 laws — one question each

| Test | Question | Cost |
|---|---|---|
| **L-a invariant** | does the law produce the shape, finiteness, sign, non-zero step its definition states, and change a parameter? | one step, µs |
| **carrier removal** | does the law's step differ from its declared neutral companion (`feedforward`, `instantaneous`, `digital`, `null`)? | two steps, µs |
| **signal fit** | can it drive a tiny problem to its floor under **some** legal lr? | ≤200 steps on 16 samples, ~1–10 s |
| **signal control** | with the learning channel cut (zeroed pseudo-gradient, frozen step), does the fit fail? | same cost |
| **L-d determinism** | same seed/same output (exists in `test_primitive_contract.py`) | µs |

**Not a test: knob binding.** A declared knob that moves no micro-reading at
one box is a coordinate; HPO finds it at the cost it already pays. The
measurement that retired it is in the header.

**Not a test: the neutral element's removal.** `feedforward`, `instantaneous`,
`digital` and `null` *are* their axes' declared companions. Their row is
`inert`: "this law is the baseline; there is no mechanism to remove." That is
a fact about the declaration, not a defect.

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

## 3. The six states (encoded, not argued in prose)

The defect line is: **a defect means the law's declared mechanism is absent
or cannot act; a bad hyperparameter means some legal setting works.** A tiny
fit whose mechanism-removed control must fail is the discriminator. There is
no fifth reading.

| State | Question | Decided by |
|---|---|---|
| `refused` | does the declared space refuse the law's base cell? | `_is_legal` + the void predicate, named on the row |
| `defect (invariant)` | does L-a fail? | `cases.invariant`, named invariant |
| `defect-or-gap (mechanism)` | carrier: does the step have nothing to transform? signal: does the fit fail at every legal lr, or has no control run? | the digest is silent / `fits=False` |
| `inert` | is the law its axis's declared neutral element, or does its step equal its companion's? | digest equality |
| `works` | carrier: digest differs; signal: fit reaches ≤0.1× untrained and the cut channel does not | the positive/negative pair |
| `test defect` | does a signal's cut channel still fit? | the control reaches |

Rules that follow:

- **One instrument per kind.** A carrier is never called `works` from a fit, a
  signal never from a digest. The fork is declared on the axes
  (`AXIS_KIND`: 4 carrier, 2 signal) and a law reads it; no per-law list.
- **A defect-or-gap is a result, not a missing row.** It names the primitive
  or the box that would close it (P3), and it does not block exit 0.
- **A retraction needs a test.** No class is removed from the table because
  the instrument is inconvenient; it is removed when the instrument is wrong
  and the fix is measured (the three case defects above), or when the
  question is not the instrument's (knob binding, §2).
- **Exit is the verdict.** 0: every selected law has a state and both
  calibration rows reproduce. 1: a `test defect`. 2: the surface disagrees
  with the registry. 3: an unfinished row or a missing law.

---

## 4. The program (dependency order, prices measured)

### P0 — Declare the surface (0 cost, first) — **done 2026-11-21**

- One `SURFACE` table: 75 laws (id + kind + knobs), 6 seams, 2 rule tables
  with their accept/refuse pairs. `comp test --surface` lists it; the harness
  parametrizes from the registry, not from a second list.
- **Delete** every per-family test that re-screens a box. The audit's
  duplicate-body predicate already forbids a second copy.
- **Fingerprint-keyed:** a law re-runs only when its declaration or its case
  fingerprint changes (instrument 3 version-gates the merge).
- Rung 1 stays: `test_primitive_capability.py` is the AGENTS one-family gate;
  the tiny fit does not replace it, it decides the defect line more cheaply.
- **Landed:** `computronium/primitives/surface.py`,
  `tests/primitives/test_surface_lock.py`, `comp test --surface`.

### P1 — One question per law (the decisive spend, ≤10 min) — **done 2026-11-21**

`scripts/probes/p1_law_surface.py` and `computronium/primitives/fit.py`:

- **T1** `AXIS_KIND` (6 rows: 4 carrier, 2 signal) and `Law.kind`, printed by
  `comp test --surface`; a law reads the axis's one declaration.
- **T2** `fit.control` dispatches on kind: carriers return the declared
  neutral companion (recomputed from axes, so its own structural params are
  not dead configuration); signals keep the zeroed pseudo-gradient and frozen
  step.
- **T3** `fit.decide` encodes §3's six states; a carrier reads its digest, a
  signal its fit and control; `test defect` means exactly one thing.
- **T4** `--only {all,signal,carrier}` runs a class; the two classes are two
  batches, not 75 prompts.
- **T5** locks: carrier-by-digest, signal-by-fit, digest-separation;
  retitled signal fit locks.

**Measured.** Carriers: 38 rows, 72–112 s. Signals: 37 rows, 353 s. The full
table recomputes from cache in 0 s. Both calibration gates reproduced. No
`test defect`, no `unproven control`, no `declaration defect`.

**Findings closed by the instrument (each a case/plumbing defect, with the
fix that flips it):**

| Finding | Fix |
|---|---|
| identity-weight substrate probe made quantizers digest equal to `digital` | seeded dense weight in `_substrate_step` |
| `noisy`'s `inject_state_noise` never exercised | applied in `_substrate_step` under the case seed |
| L-a rejected a declared empty plastic state (`null`, `substrate_coupled`) | empty declared state passes L-a |
| a carrier digest read the law's axis config, not the composed companion's | `build_case(cell=...)`; the case carries its composed cell |
| a signal control skipped when `best.reached` was false (error-blind laws) | the control runs on the fit's own criterion |

### P3 — Close the 15 `defect-or-gap` rows (next)

Each row names its mechanism and the fix that would flip it; a fix lands with
a failing test:

| Rows | Named mechanism / closing primitive |
|---|---|
| `plasticity.substrate_coupled` | the step has nothing to transform: the plasticity protocol never calls `modulate()`. Close with the `modulate()` hook and a failing test. |
| `substrate.optical`, `substrate.quantum` | no declared family base box: add one for the `photonic` / `quantum` families (and their priced cell). |
| `update.quantized_adam` | the fit reaches NaN: a defect (clamp/init), with a failing test. |
| `update.bayesian_online`, `update.cascade_synapse`, `update.elastic_consolidation`, `update.synaptic_intelligence` | the fit moves, but not to a tenth at 200 steps: a mechanism/implementation defect or a declared limit; name which. |
| `credit.forward_tangent`, `credit.local_goodness`, `credit.local_contrastive`, `credit.random_projections`, `credit.target_inversion`, `credit.zeroth_order`, `credit.temporal_trace` | the known ladder-`unimplemented` credits: the pseudo-gradient path is wrong or incomplete; fix or declare the primitive it needs. |

**Close:** every row is a fixed law, or a capability gap with the primitive
that closes it and the family it unlocks. A refusal is allowed only with a
test that fails without it.

### P4 — SEC optimization (after P3's fixes, reusing the cache)

The loop optimizes hyperparameters; it is worthless on a defective law.

- The 675-row survey is the loop's cache: reuse a row, never re-buy it.
- `comp gate breadth` (17/17, exit 0) stays as the cross-family evidence.
- A claim (E3) is bought only where a knob binds and the loop will act: 5
  rows today, not 255.
- **First ladder:** `update.adam` on `mnist` at `update.beta2` — 3 points
  plus 1 confirmation seed, recorded as a coordinate range.
- **First claim:** that coordinate at a pre-registered `n_max = 5`
  (`configs/preregistrations/` committed before the first seed).

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
   per-family test exists. **Done** (`surface.py`, `comp test --surface`).
2. **All 75 laws are in exactly one of §3's six states**, each with the
   instrument its kind declares. **Done 2026-11-21:** 40 `works`, 16
   `refused`, 4 `inert`, 15 `defect-or-gap`; exit 0; both gates reproduced.
3. **6/6 seams pass** their declared exchange. **Done**
   (`test_protocol_seams.py`).
4. **Every `defect-or-gap` names the mechanism or box that closes it**, and
   every `refused` names the rule or box that refuses it. **Partial:** the 15
   rows are named in §4 P3; P3 owes each a failing test.
5. **SEC runs on clean laws only**, reusing the cache; a claim exists only
   where a knob binds. **Open, P4.**
6. **Every kernel row passes kill + parity**; every absent row is documented
   as reference-only. **Open, P5.**
7. **The audit answers the same questions**: no test names a family box, no
   refusal without a failing test, no kernel without parity. **Partial:**
   the family-box lock passes; the other two are P3/P5.

**Not done because a row closed.** A refusal is a box statement; a screen is
E1; a width search is not a mechanism fix. A `works` row is the entry ticket
to SEC, not a claim.

---

## 6. Cost model and stop rules

- **The unit of cost is the law, not the row.** One carrier ≈ 1–3 s (two
  digests); one signal ≤3 fits + 1 control at ~1–10 s.
- **The measured batch price.** 38 carriers 72–112 s; 37 signals 353 s at 12
  lanes, 2 threads each (measured on 16 cores); the full table recomputes in
  0 s with `--resume`. The watchdog is 2× the measured price: 300 s per
  class batch, 900 s for the whole surface.
- **A tiny fit is deterministic:** no seed, no CI, no HPO. Its threshold is a
  factor off the untrained loss, so it needs no bar and no noise model.
- **The grid is capped by declared ceilings, not by luck:** 3 lr values
  inside the stability bound. A law that needs a 4th point is reported at its
  ceiling.
- **A green wave is not a verdict.** Exit 0 requires both calibration gates;
  a row without its reading is not a result.
- **Rows land before the summary.** A killed wave keeps its finished rows;
  `--resume` retries only `incomplete` rows.
- **Stop when decided:** a defect or gap closes on its named fix; a seam on
  its exchange; a claim on its fifth paired seed.

---

## 7. Locks this plan adds

| Lock | It must fail when |
|---|---|
| `test_a_carrier_law_is_tested_by_its_digest` | the digest is replaced by a fit, or a carrier is called `works` without one |
| `test_a_signal_law_is_tested_by_its_fit` | a signal is called `works` from a digest |
| `test_the_digest_separates_a_law_from_its_companion` | the digest never differs, or a baseline does |
| `test_a_signal_law_fit_fails_without_its_mechanism` | the cut-channel control passes |
| `test_a_signal_law_fit_passes_under_some_legal_setting` | a law with a passing grid point is called a defect |
| `test_the_kind_is_the_axis_declaration` | a law's kind disagrees with `AXIS_KIND` |
| `test_the_batch_calibration_gate_exits_nonzero` | a known non-pass fits and the batch still exits 0 |
| `test_the_batch_is_restartable` | a finished row re-runs, or a killed row reads as a verdict |
| `test_the_batch_reports_a_missing_law` | a selected law with no row exits 0 |
| `test_no_test_names_a_family_box` | a per-family screen returns as a test |
| `test_a_surface_row_is_registry_derived` | a second list disagrees with the registry |
| `test_a_refusal_has_a_failing_test` | a refusal exists without a test that fails without it |
| `test_every_seam_has_a_check` | a declared seam has no check |
| `test_seam_exchanges_what_it_declares` | the exemplar does not exchange what it declares |

---

## 8. First commands

```sh
# 1. P0: the surface, then prove it is the registry's own list   [DONE]
uv run python -m pytest tests/primitives/test_surface_lock.py -q
uv run comp test --surface            # 75 laws + 6 seams + 78 rules, exit 0

# 2. P1: the two class batches (prices measured)                 [DONE]
uv run python scripts/probes/p1_law_surface.py --only carrier \
  --lanes 12 --row-budget 150 --out results/p1
uv run python scripts/probes/p1_law_surface.py --only signal --resume \
  --steps 200 --row-budget 120 --out results/p1
# recompute the table from cache, with both gates:
uv run python scripts/probes/p1_law_surface.py --only all --resume \
  --steps 200 --out results/p1
# exit 0 is a verdict; exit 1 is a test defect; exit 3 is a partial run.
# Do not re-run a finished class to "check" a nonzero exit.

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
  The defect test is the mechanism's own reading, not the screen.
- **Calling a missing mechanism a refusal**: a trigger that names a missing
  mechanism is work, and it needs a test that fails without it.
- **Testing knob binding with a fit**: a knob that moves nothing at one box is
  a coordinate, and the config's dormant defaults are not the law's knobs.
  The search space owns it.
- **Treating a retraction as a test**: a class leaves the table only when the
  instrument is wrong and the fix is measured, or when the question belongs to
  another instrument.
- **Treating "0 unaccounted rows" as capability**: it was TODO97's definition
  of done, and it is why 65 primitives never trained on two families while
  the plan reported progress.
- **Reading a green table as a verdict** without the calibration gate.

---

## 10. Running a session in one batch

The unit of a session is one landing: one edit pass, one gate block, one
measurement, one commit.

```sh
# 1. edit in one pass (no intermediate runs)
# 2. gates, one block, streamed, walltime visible
uv run ruff format <changed files> && uv run ruff check --fix <changed files>
uv run pyright computronium/primitives/fit.py
uv run python -m pytest tests/primitives/test_surface_fit.py \
  tests/primitives/test_surface_lock.py -q
# 3. the measurement, background, polled at <=2 min, one log per run
nohup uv run python scripts/probes/p1_law_surface.py --only signal --resume \
  --steps 200 --row-budget 120 --out results/p1 > logs/p1_signal.log 2>&1 &
# 4. one ladder on the best works row, one pre-registered claim OR nothing
# 5. one commit: plan, instrument, locks, measurement
```

Rules for the session:

- **One shard run, once.** The fit locks plus the surface lock are the gate; a
  green run is not repeated "to confirm".
- **A nonzero exit is the verdict.** Record it and its named rows; do not
  re-run to see a different number.
- **Batch the edits, not the judgments.** Files change in one pass because
  they are one rule.
- **Leave the plan as the queue.** A landed ticket leaves §4; an open one
  stays with its file, its size and its command.
- **A session ends at the loop's door or inside it.** A green table is the
  entry ticket; the session's result is a ladder coordinate or a claim.
