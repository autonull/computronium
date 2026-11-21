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
not unroll from a composed cell. P1 is next and unstarted; its design blockers
are recorded in §4.

**One sentence:** 75 laws × a positive/negative control pair, 6 protocol
seams, and the declared composition rules are the whole test surface; a
tiny-batch fit whose mechanism-removed control must fail is the defect line;
a family box is a screen the SEC loop owns, never a test.

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

### P1 — Run L-a/b/c on all 75 (the decisive spend, ≤ 15 min wall) — **next**

Tiny fits: 200 steps × 16 samples ≈ 1 s each (measured cell ≈ 4.4 ms/step on
the 12×32 sequence box); 75 × 3 lr × 2 (fit + control) ≈ 450 runs ≈ 11 min
serial, 1–2 min with 12 lanes on 16 cores. L-a/L-c are negligible.

- **Output:** one table of 75 rows: `pass`, `defect (invariant)`,
  `defect-or-gap (mechanism)`, `declaration defect`, `works`.
- **Calibration (the check the harness must pass):** it must reproduce the
  known failures — `nca`, `rule_state`, `substrate_coupled` and `conv` — as
  non-pass. If a law the artifacts call defective fits, the harness is too
  weak (its grid, its control, or its sample size), and that is a test defect,
  not good news. If a law the artifacts call `refused` fits, the refusal is
  the defect.
- **Close:** every primitive is in one of the five states, each non-pass has
  the failing control that proves it, and the calibration set is reproduced.

**Measured before the harness (2026-11-21), three facts that shape it:**

1. The micro-case fit works: 200 `train_step`s on the case's 4-sample batch
   drop CE 1.33 → 0.004 in ~0.35 s on CPU (`gradient`, `feedforward`,
   `euclidean`, `digital`, `instantaneous` all measured). One fit is cheaper
   than the plan's budget, so a fit is not the expensive part.
2. That fit converges through geometry + credit on *every* axis, so a single
   uniform fit does not isolate a substrate, dynamics or plasticity law. A
   control that replaces those laws with a neutral companion still fits; the
   per-axis control is the P1 design work, not a grid sweep.
3. `case.config` is not read by the migrated references (`cases.step` rebuilds
   from `cell_config`), so `config_reads` is empty for all 75. L-c must vary
   the composed axis config (`CellConfig` / coordinate params), not the case
   dict; `AxisSpec.accepted_params` is the live knob declaration.

Per-axis fit/control pairs P1 still needs: credit (zero pseudo-gradient),
dynamics (instantaneous settle), geometry (frozen/zeroed weights), update
(unchanged parameters), plasticity (null psi), substrate (identity forward).
Each pair is a named check, not a grid point.

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
   presented as tuning. **Open, P1.**
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

- **The unit of cost is the law, not the row.** One law ≈ 1 s per fit; one
  family row ≈ 1–89 s per seed, ×5 for E2. Spend the first, buy the second
  only where the loop will act.
- **A tiny fit is deterministic**: no seed, no CI, no HPO. Its threshold is a
  factor off the untrained loss, so it needs no bar and no noise model.
- **A grid is capped by declared ceilings, not by luck**: 3 lr values inside
  the stability bound. If a law needs a 4th grid point to fit, the ceiling is
  the finding.
- **Watchdog = 2× the measured cost.** A fit killed past it is a compose or
  cost defect; record, re-price, do not retry blind.
- **Lanes:** 12 concurrent processes, 2 threads each (measured on 16 cores).
  A 4-worker run's 300 s timeouts were contention, not verdicts.
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

**Landed 2026-11-21:** family-box, surface-row, refusal, and both seam locks.
**Open:** the three fit/knob locks, which arrive with the P1 harness.

---

## 8. First commands

```sh
# 1. P0: the surface, then prove it is the registry's own list   [DONE]
uv run python -m pytest tests/primitives/test_surface_lock.py -q
uv run comp test --surface            # 75 laws + 6 seams + 78 rules, exit 0

# 2. P1: the decisive spend - 75 tiny fits, each with its negative control [NEXT]
uv run python scripts/probes/p1_law_surface.py --seeds 1 --lr-grid 0.1,1,10 \
  --samples 16 --steps 200 --lanes 12 --out results/p1

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
