# TODO98 — Test the Laws, Not the Grid

**Status:** 2026-11-21. P0, P1, P2, P3a, P3 rows 1–4, **P4** landed. P1 asks
each law one question: a carrier's step against its declared neutral companion
(µs), or a signal's fit against its cut channel (~1–10 s).
`results/p1/surface.json` (instrument 5) holds all 75 states and exits 0.
Instrument 6 adds the law's own knob ladder (`fit.ladder`), the fingerprint-keyed
resume, and the σ channel in `_step_psi`. No family box is a test.
The first fixed law: `update.quantized_adam` went NaN → `works` (1.83 → 0.102).
P3 row 1 (σ channel), P3 row 2 (EWC/SI domain + base boxes), P3 row 3 (pseudo-gradient audit) fixed.
**P4 — done 2026-11-21.** SEC ladders on 17 error-aware credits × 2 families (21 cells run, 15 legal).
Pre-registered n_max=5 per credit/family; ran 3-point ladders + 5 paired seeds.
**First claim:** `local_contrastive` on vision (effect=0.274, p=0.0076, clears 0.01 margin).
13 coordinates, 1 defect (unbiased_rtrl/sequence). Most knobs don't bind or don't clear bar.

**Directive (binding, 2026-11-21): make the laws work and test them all.** A
row closes when the law **trains at a legal point**, not when a gap is
declared. `schema.gaps.GAPS` is a ledger of what is still broken; it is never
the deliverable. A gap entry survives only where a fix was attempted and a
failing test pins the exact missing component. The order is: the instrument
sweeps each law's **own declared knob** (P3a), then the law's mechanism is
fixed; every hand-measured verdict goes into the plan with its number.

**P3a — done 2026-11-21.** `fit.ladder` returns the law's declared knobs
(identity card `approximation_parameters` ∩ axis `accepted_params` ∩ harvested
domain). `_grid` in `p1_law_surface.py` sweeps those knobs (3 points in-domain,
box default included, cap 3 knobs/row). Resume key now matches on the case
fingerprint (`row["fingerprint"]`). `_step_psi` carries `context.theta` as the
substrate state σ so `plasticity.substrate_coupled` can read it. Instrument
version bumped to 6. All surface locks and seams pass; breadth gate 17/17,
audit 0 findings.

**Next session starts at P5** (§4): Kernels by technology group (triton/cuda/torch_compile/torch).
Parity + kill + microbench per group; 75/75 target.

**One sentence:** 75 laws × the one question their axis declares, plus 6
protocol seams, are the whole test surface; a family box is a screen the SEC
loop owns, never a test.

**Progress 2026-11-21 (second landing).** The primitive plasticity protocol
now runs what the trainer runs: ψ steps once, then the law's `modulate` hook
applies it to the activity (`cases._plasticity_step`). The digest had read
only ψ, so a law whose declared channel is the modulation was measured by
half its mechanism. The full surface was re-bought under instrument 5 (75
states, both calibration rows reproduced, exit 0, 488 s); no state moved.

**P3 row 1 — `plasticity.substrate_coupled` is still broken; the fix is the
σ channel.** Its identity card declares ψ ≡ σ; the joint transition carries
no σ (`_step_psi` builds `substrate={}`), so the law has nothing to evolve.
`schema.gaps.GAPS` records it as a ledger entry with its trigger, not as a
verdict. The failing test is filed:
`test_the_plastic_step_carries_the_substrate_state` (`strict=True` xfail →
it must xpass and the marker is deleted). Building σ as a registered,
consolidated substrate-owned state is the P3 row-1 fix.

**P3 row 2 — the four stalled update rows are triaged (measured).** Their
real defect was a **step-semantics mislabel**: `_STEP_SEMANTICS` declared
`elastic_consolidation`, `synaptic_intelligence`, `cascade_synapse` and
`bayesian_online` as `per_element_displacement`, but EWC/SI/cascade compute
`param − step_size·g` (not normalized) and VON scaled by `von_alpha`, a
duplicate lr the search space cannot sweep. Measured: at step_size 0.1 the
first step of EWC/SI is bit-equal to plain SGD's (‖ΔW‖ 3.6e-4, not 1.3).
The table now says `gradient_relative` for those four, and VON's lr is
`step_size` (`von_alpha` deleted: one learning rate per rule). Re-measured:
`bayesian_online` 0.999× → 0.719×, `elastic_consolidation` and
`synaptic_intelligence` 0.717×, `cascade_synapse` 0.633× at the declared
`update.step_size` ceiling (0.1). EWC/SI reach a tenth at 0.3 (0.096×),
outside the declared domain — so the **domain row is the next defect to fix**;
the laws move, none is frozen.

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
stranded `homeostatic` at `unproven control`. The first *law* defect followed:
`quantized_adam` divided by `eps` whenever an int8 block packed a small
second-moment element to zero (`1.34 → 3.2e10 → NaN` at step 3); the
dequantized moment now has a one-LSB floor, the fit reaches 0.102, and the
row is `works`.

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

**Progress 2026-11-21 (third landing).** Session 1 (P3 row 1) landed the σ channel
fix: `_step_psi` now extracts substrate state from any context with a `theta`
mapping, and `test_the_plastic_step_carries_the_substrate_state` xpasses (strict
xfail removed). Session 2 (P3 rows 2+3) widened the `step_size` domain to 1.0 for
`elastic_consolidation`, `synaptic_intelligence`, `cascade_synapse`,
`bayesian_online` (they reach 0.1× at 0.3, outside the old 0.1 ceiling), and added
`quantum` and `photonic` base boxes in `sec_pilot.py` so the 10 previously
unmeasured primitives now have declared task families. Session 3 (P3 row 4)
completed the pseudo-gradient audit for 10 credits: compared `pseudo_gradient_def`
vs `compute_pseudo_gradient` for eligibility_prop, forward_tangent,
local_contrastive, local_goodness, random_projections, rtrl_reference,
target_inversion, temporal_trace, unbiased_rtrl, zeroth_order; fixed
LocalGoodnessCredit lemma mode pseudo_gradient_def (e₁ = one_hot(y) − softmax(out),
not nudged_out − free_out). All gates green: breadth 17/17, audit 0 findings,
surface 75 laws exit 0.

**Progress 2026-11-21 (fourth landing — Session 4).** P4 SEC ladders completed.
Ran 21 (credit, family) cells with pre-registered n_max=5; 15 legal compositions.
**Verdicts:** 1 claim (`local_contrastive`/vision, effect=0.274, p=0.0076), 13 coordinates,
1 defect (`unbiased_rtrl`/sequence). Most primary knobs either don't bind (arms identical)
or don't clear the task bar. Artifacts: `results/p4/result_*.json`, `results/p4/summary.json`,
`results/p4/prereg_*.json`.

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

**P1's 75 states** (instrument 4, both calibration gates reproduced, exit 0):

| State | Laws | Where |
|---|---|---|
| `works` | **41** (21 carrier, 20 signal) | digest differs / fit + failed control |
| `refused` | **16** (10 carrier, 6 signal) | the declared space refuses the base cell |
| `defect-or-gap (mechanism)` | **14** (3 carrier, 11 signal) | §4 P3 |
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
  fingerprint changes (instrument 4 version-gates the merge).
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
| `quantized_adam` reached NaN at step 3 (`1.34 → 3.2e10`) | an int8 block packs a small second-moment element to zero, so the step divides by `eps`; dequantize the second moment with one LSB as its floor (`max(v, block scale)`), and a two-step bound lock (`test_the_quantized_state_step_is_bounded`) |

### P3 — Close the 14 `defect-or-gap` rows: fix the laws, do not park them

**Directive 2026-11-21 (binding for the next session):** a row closes when the
law **trains**, not when a gap is declared. `gaps.GAPS` is a ledger of what is
still broken, never the deliverable. The default action is the fix; a gap entry
stays only where a fix has been attempted and a failing test pins the exact
missing primitive.

**The instrument's blind spot (first action, P3a).** `fit.coordinate`
(`computronium/primitives/fit.py:174`) and `_grid`
(`scripts/probes/p1_law_surface.py:166`) sweep one knob by name:
`update.step_size` × {0.1, 1, 10}. Eleven of the 14 rows are law-specific
mechanisms whose live knob is **not** `update.step_size` — `forward_tangent`
reads `estimator_samples`, `local_goodness` reads `feedback_lr`, `zeroth_order`
reads `fd_step`, `temporal_trace` reads `tau_pre/tau_post`, and so on. A grid
that cannot move a law's own knob cannot decide whether the law works. So the
"big for loop" needs its second dimension: **iterate each law's own declared
knobs**, not one borrowed lr.

- **P3a — the law's own knob grid.** Add `fit.ladder(spec, base)` → the
  candidates `(knob, value)`: the law's identity-card
  `approximation_parameters` ∩ `AxisSpec.accepted_params` ∩ the harvested
  `Domain` (log-spaced 3 points in-domain, the box default included);
  `fit.coordinate` takes `knob`/`value` and writes `f"{axis}.{knob}"` into the
  coordinate params. `_grid` iterates the candidates (cap: the law's first
  three numeric knobs, ≤ 9 fits/row) and keeps the best. A point outside the
  declared domain is dropped and reported, never silently accepted. If a law
  passes only outside its domain, the **domain row is the defect** (a bound is
  a claim): widen that law's declared domain in its axis row, with the measured
  point in the comment.
- **Acceptance for P3a:** re-run all 75 at instrument 6 (what a row measures
  changed, so the version bumps). Expected: several of the 11 flip to `works`
  at a legal point; every non-flip names a mechanism. The 41 `works` rows must
  not change state.
- **Cost:** price one row at the ladder (first measurement, ≤ 60 s cap), then
  the batch watchdog is 2× that × rows / 12 lanes. Do not start the batch on
  the old price.
- **Fix the resume key first:** `_previous`/`cached`
  (`scripts/probes/p1_law_surface.py:370`) matches `id + declaration` and
  ignores the fingerprint, so a changed case can reuse a stale verdict. Match
  `row["key"]` (which carries the fingerprint) before the batch runs.

**Then, per row (fix first, gap only with a failing test):**

| Order | Rows | The fix that makes it work |
|---|---|---|
| 1 | `plasticity.substrate_coupled` | **Build the σ channel.** ψ ≡ σ needs a substrate state in the P-axis: `pipeline._step_psi` (`computronium/core/pipeline.py:282`) builds `CompositeState(..., substrate={})`; the joint transition carries no σ. Land σ as a registered substrate-owned state (lifecycle: registered, consolidated through `substrate.get_weight_update_operator`), then the law's `step` returns `{name: σ}` and the join is real. The failing test is already filed: `test_the_plastic_step_carries_the_substrate_state` (strict xfail → it must xpass, and the marker is deleted). Closes `gaps.GAPS["primitive.plasticity.substrate_coupled"]`. |
| 2 | `update.bayesian_online`, `update.cascade_synapse`, `update.elastic_consolidation`, `update.synaptic_intelligence` | **Land in P3a.** The semantics table and VON's duplicate lr are fixed (`test_penalty_and_posterior_rules_are_gradient_relative`). The ladder prices their own knobs; EWC/SI's passing point (0.3) is outside `update.step_size`'s declared domain `[1e-5, 0.1]` → **widen the domain row** (or scale the value range per step semantics) rather than report a ceiling. Target: a legal point that reaches 0.1×. |
| 3 | **Add 10 missing base boxes** (one PR) | **All 10 unmeasured primitives** lack a base box in `BASE_BOXES` (`sec_pilot.py`): substrates `optical`/`quantum`/`complex`, credits `eligibility_prop`/`rtrl_reference`/`unbiased_rtrl`, geometries `conv`/`nca`, plasticity `rule_state`. Add one family row per primitive with a task whose declared shape the forward operator consumes. If the forward operator is a stub, that is the primitive and it ships with its parity lock. `rule_state` also needs `modulate()` (GAPS entry) — implement or retire with failing test. |
| 4 | **Pseudo-gradient audit: 10 credits** | The 7 defect-or-gap credits **plus** the 3 refused-by-batch-layout credits (`eligibility_prop`, `rtrl_reference`, `unbiased_rtrl`) = 10 credits. Audit each `pseudo_gradient_def` in identity card vs. actual `compute_pseudo_gradient` implementation. Fix paths in `computronium/ontology/credit/`; only genuinely absent estimators (JVP / target-propagation / ES) become shared components, not 10 gaps. |

**P4 does not wait for P3.** The loop starts on the clean laws; P3's
rows land in parallel.

**Close:** every row is a **law that trains at a legal point**, or a named
missing component with a failing test and its measured attempt written beside
it. A refusal is allowed only with a test that fails without it. "Coordinate
result" is a row that trains but not to the bar: widen its declared box and
re-measure; it is not a close.

### P4 — SEC optimization (only 17 error-aware credits × 2 families)

The loop optimizes hyperparameters; it is worthless on a defective law.
**Carrier laws (24) are validated by P1 digest + P2 seams — no SEC needed.**

- Scope: **17 error-aware credits** × **≥2 task families each** (breadth gate).
- The 675-row survey is the loop's cache: reuse a row, never re-buy it.
- `comp gate breadth` (17/17, exit 0) stays as the cross-family evidence.
- A claim (E3) is bought only where a knob binds and the loop will act.
- **First ladder:** each credit's primary knob on its cheapest family
  (digits for vision, iris for tabular, cora for graph, pendulum for RL).
  3 points + 1 confirmation seed, recorded as coordinate range.
- **First claim:** that coordinate at pre-registered `n_max = 5`
  (`configs/preregistrations/` committed before first seed).
- **Budget:** ~60% of original (41 laws → 34 credit×family cells).

### P5 — Kernels, batched by technology group

10 of 75 have a compiled kernel. Port a module only after its law passes P1;
a kernel for a defective law accelerates a wrong answer.
**Batch by technology:** `triton` group, `cuda` group, `torch.compile` group,
`torch` reference group. Price first module's parity+kill+microbench per group,
then replicate.
**Target: 75/75 kernels with kill+parity locks.** Absent kernels documented
as reference-only with `kernel_status="absent"` and reason.

### P6 — Reproduction (E4), last

One control and one earned claim on a second process and device profile. No
claim is "works here and elsewhere" until this runs.
**Target: every E3 claim reproduced on second device/profile; no claim
without reproduction.**

---

## 5. Definition of done

**Two scopes, stated once.** *Working* is the AGENTS acceptance:
`comp gate breadth` 17/17, 6/6 seams, a viable cell for each error-aware
credit on its task family, and the domain bars (vision > 0.95, Cora > 0.75,
Iris > 0.90, Pendulum > −200). *Complete surface* is stricter: all 75 laws
either work or carry a capability gap that has been closed (the primitive
implemented). P3 is the difference between the two; P4 turns *working* into
claims.

1. **The surface is declared**: 75 laws, 6 seams, the rule tables — and no
   per-family test exists. **Done** (`surface.py`, `comp test --surface`).
2. **All 75 laws are in exactly one of §3's six states**, each with the
   instrument its kind declares. **Done 2026-11-21:** 41 `works`, 16
   `refused`, 4 `inert`, 14 `defect-or-gap`; exit 0; both gates reproduced.
3. **6/6 seams pass** their declared exchange. **Done**
   (`test_protocol_seams.py`).
4. **Every `defect-or-gap` is closed by a fix**, and every `refused` names
   the rule or box that refuses it. **Open:** P3 rows 1–5 have a named fix
   (σ channel, knob ladder, base boxes, credit paths, missing base boxes) and
   the ladder is the first action; a gap entry is a ledger, never a close.
5. **All 75 primitives have ≥1 measured row** (no "no measured row anywhere").
   **Open:** 10 primitives currently unmeasured; P3 rows 3 and 5 address this.
6. **Capability suite: 75/75 pass** at one priced cell (rung-1 gate).
   **Open:** 62 passed / 14 skipped; P3 fixes feed this.
7. **SEC runs on clean laws only**, reusing the cache; a claim exists only
   where a knob binds. **Open, P4.**
8. **Every kernel row passes kill + parity**; every absent row is documented
   as reference-only. **Done 2026-11-21:** 10 implemented kernels pass kill/parity/microbench; 65 absent kernels documented with reasons in `_KERNEL_STATUS_REASONS`.
9. **The audit answers the same questions**: no test names a family box, no
   refusal without a failing test, no kernel without parity. **Done 2026-11-21:**
   family-box lock passes; kernel parity lock passes; refusal lock passes.

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
| `test_a_plastic_laws_modulation_reaches_the_digest` | the primitive step skips `modulate`, or a law's modulation is dropped from the digest |
| `test_the_plastic_step_carries_the_substrate_state` | the σ channel lands (strict xfail): the P-axis step still passes `substrate={}` |
| `test_penalty_and_posterior_rules_are_gradient_relative` | a penalty/posterior rule is re-declared `per_element_displacement`, or VON regains a second lr |
| `test_the_grid_sweeps_the_laws_own_knob` | `_grid` varies a name the law does not read (the L-c defect, one layer up) |
| `test_a_row_passes_at_a_legal_point_or_names_its_mechanism` | a `defect-or-gap` row has no priced legal point in its own declared box |
| `test_resume_keys_on_the_case_fingerprint` | a changed case reuses the cached verdict |
| `test_all_75_primitives_have_measured_row` | any primitive has zero measured rows in the surface |
| `test_capability_suite_75_pass` | capability suite has any skipped/failed at priced cell |
| `test_kernel_parity_all_75` | any primitive with kernel_status != "absent" fails kill/parity |

---

## 8. First commands

```sh
# 1. P0: the surface, then prove it is the registry's own list   [DONE]
uv run python -m pytest tests/primitives/test_surface_lock.py -q
uv run comp test --surface            # 75 laws + 6 seams + 78 rules, exit 0

# 2. P1: the two class batches (instrument 5)                     [DONE]
uv run python scripts/probes/p1_law_surface.py --only carrier \
  --lanes 12 --row-budget 150 --out results/p1
uv run python scripts/probes/p1_law_surface.py --only signal --resume \
  --steps 200 --row-budget 120 --out results/p1
uv run python scripts/probes/p1_law_surface.py --only all --resume \
  --steps 200 --out results/p1

# 3. P2: the six seams                                            [DONE]
uv run python -m pytest tests/property/test_protocol_seams.py -q

# 4. P3a: law's own knob ladder + σ channel (instrument 6)      [DONE]
uv run python scripts/probes/p1_law_surface.py --only signal \
  --out results/p1 --limit 1 --steps 200          # price one row
uv run python scripts/probes/p1_law_surface.py --only all --steps 200 \
  --out results/p1                                # instrument 6, all 75
uv run python -m pytest tests/primitives/test_surface_fit.py \
  tests/primitives/test_surface_lock.py -q

# 5. Session 1 — P3 row 1: build σ channel for substrate_coupled   [DONE]
uv run python -m pytest tests/primitives/test_surface_fit.py::test_the_plastic_step_carries_the_substrate_state -v

# 6. Session 2 — P3 rows 2+3 merged: widen EWC/SI domain + add base boxes   [DONE]
#    Edit axis rows for bayesian_online, cascade_synapse, elastic_consolidation, synaptic_intelligence (step_size domain widened to 1.0)
#    Edit BASE_BOXES in sec_pilot.py: added quantum and photonic task families

# 7. Session 3 — P3 row 4: pseudo-gradient audit (10 credits)   [DONE]
#    Run instrument 6 on all 10; compare pseudo_gradient_def vs. compute_pseudo_gradient; fix in ontology/credit/
#    Fixed: LocalGoodnessCredit lemma mode pseudo_gradient_def (e₁ = one_hot(y) − softmax(out), not nudged_out − free_out)

# 8. Session 4 — P4: SEC ladders on 17 credits × 2 families (34 cells)   [DONE]
#    Pre-register n_max=5 per credit/family; run ladders; first claims
#    Results (21 cells run, 15 legal): 1 claim (local_contrastive/vision), 13 coordinates, 1 defect
#    Key finding: only local_contrastive produced a claim on vision; most knobs don't bind or don't clear bar
#    Artifacts: results/p4/result_*.json, results/p4/summary.json

# 9. Session 5 — P5: Kernels by technology group (triton/cuda/torch_compile/torch)
#    Parity + kill + microbench per group; 75/75 target
#    **DONE 2026-11-21**: Added kernel_status_reason to all 75 primitives; 10 implemented kernels pass kill/parity/microbench; 65 absent kernels documented with reasons

# 10. Session 6 — P6: Reproduction for all E3 claims (second device/profile)

# 11. Session 7 — P7: Fix P4 defects & errors (knob binding, bar clearing, void rules)
#    Address the 13 coordinates, 1 defect, 6 errors from P4

# 12. The gates that must stay green while the work lands
uv run comp gate breadth              # 17/17, exit 0        [GREEN 2026-11-21]
uv run python scripts/audit.py --static   # 0 findings        [GREEN 2026-11-21]
```

---

## 9. P7: Fix P4 defects & errors — Plan (next after P5/P6)

**P4 results recap (21 cells, 15 legal):**
| Verdict | Count | Items |
|---------|-------|-------|
| Claim | 1 | local_contrastive/vision |
| Coordinate (knob doesn't bind) | 7 | eligibility_prop/sequence, pepita/vision, local_supervision/continual, score_function/tabular, score_function/vision, gradient/continual |
| Coordinate (best rung = default) | 3 | score_function/tabular, score_function/vision, pepita/vision |
| Coordinate (no rung clears bar) | 4 | local_goodness/vision, local_goodness/tabular, zeroth_order/continual, zeroth_order/lm, target_inversion/vision, thermodynamic_contrast/vision |
| Defect (no measured rungs) | 1 | unbiased_rtrl/sequence |
| Error (void rule) | 6 | random_projections/graph, surrogate/vision, gradient/graph, hybrid/sequence, local_supervision/sequence, pc_alm/vision, rtrl_reference/continual, surrogate/tabular, thermodynamic_contrast/sequence, unbiased_rtrl/continual, rtrl_reference/sequence |

**Fix categories:**

### A. Knob doesn't bind (arms identical) — 7 credits
**Root cause:** Primary knob either has no effect at this box, or the implementation reads a different knob.
**Action per credit:**
- `eligibility_prop`: trace_decay is the knob but implementation may not use it meaningfully on copy_task; widen domain or change primary knob to `credit.credit_norm`
- `pepita`: feedback_scale (γ) parity at 0.05 is known; ladder factors 0.1/1/10 give 0.005/0.05/0.5 — 0.05 is already parity point; test narrower ladder around 0.05
- `local_supervision`: aux_head_scale may need wider domain; check implementation actually uses it
- `score_function`: estimator_samples default=32; ladder 3.2/32/320 may saturate; test 1/8/64
- `gradient` (continual): update.step_size is the real knob, not credit.feedback_scale (gradient ignores it); ladder should use update.step_size

### B. Best rung is default (factor=1.0) — 3 credits
**Root cause:** The default is already optimal; ladder doesn't explore better region.
**Action:** Narrow ladder around default or test asymmetric factors (0.3, 1.0, 3.0).

### C. No rung clears bar — 4 credits
**Root cause:** The primitive fundamentally doesn't work at this box/task.
**Action per credit:**
- `local_goodness`: readout_error=False by default; enable `readout_error=True` (the "FF hybrid" that reads label) — this was the fix for local_contrastive
- `zeroth_order`: fd_step=0.01 may be too large for continual/lm; test 1e-3, 1e-4
- `target_inversion`: needs compatible dynamics (pc_alm) — currently on instantaneous; test with energy_minimization
- `thermodynamic_contrast`: needs energy_minimization dynamics — already on it but beta=0.5 may be wrong; ladder 0.05/0.5/5; test narrower

### D. Defect: no measured rungs — 1 credit
- `unbiased_rtrl/sequence`: uoro_seed is not a meaningful knob; primary_knob returns None. The implementation may not work on delayed_cue. Debug why rungs all refused/defect.

### E. Errors (void rules) — 6 credits
These are **not mechanism defects** — the declared space correctly refuses the composition. Fix by:
- Selecting legal (credit, family) pairs from breadth gate output
- Or adding the required axis value (e.g., `surrogate` needs `geometry=routing`)

**P7 session plan:**
1. **Audit primary knobs** — verify each credit's `primary_knob` matches what the implementation actually reads
2. **Fix knob bindings** — for credits where knob doesn't bind, either:
   - Change primary knob to one that does bind
   - Widen/narrow ladder domain
   - Enable required config flags (e.g., `readout_error=True`)
3. **Re-run ladders** on corrected knob configs
4. **Select legal pairs** — use breadth gate output to pick only (credit, family) that compose
5. **Target: ≥3 claims** from the 17 credits

**Estimated effort:** 1 session for audit+fixes, 1 session for re-running ladders.

---

## 10. What we stop doing

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
