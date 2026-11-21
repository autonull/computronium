# TODO98 — Prove It Works, Not That It Ran

**Status:** 2026-11-21 · replaces TODO97's acceptance rule. TODO97 closed rows:
every declared `(primitive, family, box)` carries `measured`, `refused`,
`defective`, `impossible`, or `unimplemented`. That rule answers *"did this
row run at its box and report a number?"*. It does not answer *"does the
primitive work?"*, and TODO97's progress notes read the first question as the
second one.

**One sentence:** TODO98 replaces the row-shaped definition of done with an
evidence ladder, states which rung every primitive actually reached, and pays
down the four debt classes that make the rest unprovable: real defects, rows
that never trained, kernels that do not exist, and reproducibility that has
never been checked.

---

## 0. The two questions that were conflated

| Question | TODO97's answer | What it needs |
|---|---|---|
| Did the row run at its declared box? | a state per row | E1 below |
| Does the primitive do the thing we claim? | not asked | E3 + E4 below |

The evidence ladder this plan uses. A primitive's claim is only as strong as
the highest rung it reached, and a row's rung is part of its result:

| Rung | Evidence | Who consumes it |
|---|---|---|
| **E0 wired** | one step composes, finite output, gates | rung-0 lock |
| **E1 trains** | 1 seed, bar verdict at the box | map row, screen |
| **E2 measured** | L2, n≥5 seeds, bar cleared | breadth exit |
| **E3 claim** | pre-registered margin, paired seeds, CI clears | claim pool |
| **E4 reproduced** | replay hash reproduces on a second machine/process | release claim |

**No rung may be silently upgraded.** A row measured at one seed is E1 even if
its number is high; a breadth row is E2 even if its effect looks large; only
E3 rows are "works", and only E4 rows are "works here and elsewhere".

---

## 1. The honest inventory (measured 2026-11-21)

Artifacts: `results/sec*/map.json` (9 family maps, 75 primitives each),
`results/sec*/ladders`, `experiments/*.duckdb` (465 stores), `docs/sec/map.md`.

| Item | Count | Source |
|---|---|---|
| Primitives registered (spec, task case, invariant, fingerprint) | **75/75** | `primitives/registry.py` |
| Declared family rows (`primitive × family`) | **675** | 9 maps |
| Rows measured | **255** | maps |
| Rows refused by a declared rule | **419** | maps |
| Rows defective | **1** (`nca`) | vision map |
| Primitives with ≥1 measured row | **65** | maps |
| Primitives with no measured row anywhere | **10** | below |
| Ladder records | 30: **18 `tuned` / 12 `unimplemented`** | `ladders` |
| Distinct primitives `unimplemented` | **11** | below |
| Claim-grade rows (E3) | **5** (2 claims, 1 CI, 2 no-power) | `results/sec_claims/claims.json` |
| Compiled kernels | **10/75**; 65 `kernel_status="absent"` | `primitives/kernels.py` |
| Primitives suite | 666 passed / 152 declared skips | `tests/primitives` |
| Capability suite at one priced cell | 62 passed / 14 skipped / 0 failed | `tests/primitives/test_primitive_capability.py` |
| Audit | 0 findings | `scripts/audit.py` |

**The ten primitives with no measured row:** `complex`, `conv`,
`eligibility_prop`, `nca`, `optical`, `quantum`, `rtrl_reference`,
`rule_state`, `substrate_coupled`, `unbiased_rtrl`.
3 of them (`eligibility_prop`, `rtrl_reference`, `unbiased_rtrl`) now hold
five-seed records in `experiments/breadth_*_delayed_cue.duckdb`; the map rows
stay `refused` because the map's row is the flat vision box. That asymmetry is
honest only while the docs say "record, not map row".

**The twelve `unimplemented` ladder records (11 distinct primitives):** `forward_tangent`, `pc_alm`
(vision), `target_inversion`, `conv`, `error_predictive_coding`,
`local_goodness` (vision + tabular), `diffusion` (vision),
`random_projections` (tabular), `zeroth_order` (tabular), `tile`,
`spike_integration` (neuromorphic).

**Why 419 rows are refused** (419 rows, 367 distinct trigger strings):
`RuleStatePlasticity` has no `modulate()` (9), `SubstrateCoupledPlasticity` is
a no-op (9), credit × batch-layout disagreement (12: the three temporal
credits on the four flat families), 60 s cost cap (8), token-lane
disagreement (`causal_transformer`, 3), then one declared per-family refusal
per row (`composes no <family> task family`, mostly 1–2 rows each). Each is a
declared box statement, not a proof of impossibility.

**What the vision map's numbers say.** 48 rows measured; 38 of them clear
twice chance, 10 sit inside the near-chance band. The other families use ppl
and reward rulers, so the same classification needs each family's ruler — the
audit's near-chance predicate, not a second table.

---

## 2. What is actually proven, and what each proof covers

| Claim | Coverage | What it does not cover |
|---|---|---|
| Every primitive composes and steps once | all 75, one box | behaviour over training |
| Every primitive trains one epoch | all 75 at their family box | learning over a schedule |
| 255 rows trained and reported | 255 of 675 boxes | the other 419 boxes |
| 17 error-aware credits hold two families | 17 credits | credits outside the table, and E3 |
| 5 rows carry a claim or a CI | 5 rows | 70 other primitives |
| 10 kernels pass parity + kill | 10 of 75 | 65 primitives with no kernel |

The plan's own sentence "no remaining row is open" is therefore true and not
useful: 419 rows are closed by refusal, 11 by a named missing mechanism, and
1 by a defect. The other 255 rows ran; none of them says at which rung, and
nothing matches a map row to the L2/5 record that would upgrade it. That is
T0's work: the maps cannot report their own evidence strength.

---

## 3. The debt classes, sorted by what they actually are

TODO97 calls every non-measured row a verdict. The artifacts say otherwise
once the trigger is read: a refusal whose trigger names a *missing mechanism*
is not a box statement, and a ladder's `unimplemented` is not a defect (no
cell has been shown to fail). The four classes below are worked in that order.

### D1 — a confirmed defect

| Defect | Mechanism | Failing test | Close |
|---|---|---|---|
| `geometry.nca` cannot read a flat feature task | its own `grid_hw` (16×16×3 = 768) vs mnist's 784 features | `tests/property/test_family_defect_locks.py::test_nca_refuses_a_flat_feature_task` (strict xfail) | `grid_hw` from the task's flattened width, or a declared refusal by name |

### D2 — missing mechanisms recorded as refusals (18 rows)

| Row | Trigger | What must be decided |
|---|---|---|
| `plasticity.rule_state` (9 families) | "`RuleStatePlasticity` has no `modulate()`: the standard train step evolves psi but never applies the rule state" | defect or capability gap: implement `modulate()` + a rule-state transition and re-run one cell; if no legal box admits it, refuse by name with a test |
| `plasticity.substrate_coupled` (9 families) | "`SubstrateCoupledPlasticity` is a no-op at the plasticity protocol level (psi = sigma)" | same: a device-coupled update, or a refusal test naming the missing substrate contract |

The test is cheap and decides the class: one cell at the family base, and the
row's own trigger becomes a failing test that flips when the mechanism lands.
A refusal is only valid with that test shown to fail without the refusal.

### D3 — `unimplemented` ladder records (12; 11 primitives)

`forward_tangent`, `pc_alm` (vision), `target_inversion`, `conv`,
`error_predictive_coding`, `local_goodness` (vision + tabular), `diffusion`
(vision), `random_projections` (tabular), `zeroth_order` (tabular), `tile`,
`spike_integration` (neuromorphic).

Each names a missing mechanism and has no ladder point outside its band.
They are **not** defects: no cell has been shown to fail. They close as a
coordinate (a point outside the band) or a refusal by name with the
mechanism that would close it.

### D4 — cost rows (9)

60 s L0 cap after 1/24 boxes (8 rows) and vision `diffusion` (declared 180 s at
2× its measured 76.9 s cell). A cost row is a box statement; it becomes work
only when its declared box is priced.

## 4. The plan (dependency order, no item starts before its predecessor's gate)

### T0 — Make the evidence visible (cheapest, first)

*The map must say which rung a row reached.* Today a row's only evidence field
is `status`; a one-seed screen and a five-seed breadth row look alike.

- Add `evidence_rung` (`E1`/`E2`/`E3`) and `n_seeds` to every row, derived
  from the record the row was written from — not a second table.
- `docs/sec/map.md` prints the rung beside the number; the method card's
  "result" line says "E1 screen" or "E2 measurement".
- Lock: a row's rung follows its record's `n_seeds`; removing the derivation
  fails the lock.
- **Price:** 0 (a projection of existing records). **Close:** every row carries
  a rung and the docs print it.

### T1 — Close the debt classes (D1, D2)

Each is a named mechanism and a failing test. A fix is only a fix if the cell
moves or the failing test flips; a refusal is only valid with a refusal test
shown to fail without the refusal.

- **Price per defect:** one Rung-1 cell at the family base (vision ≈ 12 s per
  mnist epoch + compose) plus the lock. D1's grid width is a code change, not
  a screen.
- **Close:** `defective == 0` in every map; every strict xfail that names a
  defect is gone; and no refusal's trigger names a missing mechanism without a
  test that fails today (the 18 D2 rows become 18 measured rows or 18 tested
  refusals).
- **Never:** mark a defect `refused` to clear the count without a refusal test.

### T2 — The eleven distinct `unimplemented` primitives (12 records)

Each is either a missing mechanism or a box that cannot train it. For each:

1. name the mechanism (the ladder's `_TRIAGE` entry, or replace it);
2. run the 3-point ladder at the primitive's own knob, 1 seed per rung, then
   1 confirmation seed at the best point (rung 2, the minimum fair chance);
3. either the primitive moves above the band and the row becomes `measured`,
   or it is refused by name with a test that fails today.
   `pc_alm` is the exception already filed: its gain ceiling refuses the ×10
   rung, so its ladder must run the ×2 rung inside
   `step_size * (1 + rho) < 2` first. Two declarations block that as written:
   `LADDER_FACTORS = (0.1, 1.0, 10.0)` has no ×2 rung, and
   `PRIMARY_KNOBS[pc_alm] = ("beta",)` names a different knob than the one
   the ceiling constrains (`step_size`). The ladder cannot find the admissible
   rung until both agree — one of the two is stale, and T2 must decide which.

- **Price:** one ladder = 3 rungs + 1 confirmation seed, at the row's box
  (measured: a mnist cell ≈ 12 s; the 4-claim run took ≈ 17 min for 4 rows).
- **Close:** 0 `unimplemented` ladder records; every one is `tuned` or refused
  by name with a failing test (12 records, 11 primitives).

### T3 — Upgrade the measured rows to their evidence rung

A map row is written by a P0 screen at L0/1 seed, so every one of the 255
measured rows is E1 by construction. The stores hold L2/n≥5 records for 17
credit rows (the breadth gate counts 10–250 keys per credit), but no map row
carries the rung, so "this row has an E2 record at its own coordinate" has
never been asked and cannot be answered from the artifacts.

- For each measured row: run L2/n=5 at `screen_coordinate(row.box)` and the
  family's base schedule, write the records to the family store.
- **Price:** `rows × base cell × 5` at the family's own base (measured unit
  prices: sequence base 1.0–89 s/seed depending on credit; mnist ≈ 12 s/seed;
  five-seed rows ran 12 concurrent with 2 threads per process on 16 cores).
  Price each family before starting it; do not open a family whose total
  exceeds the round's budget.
- **Close:** every measured row carries `n_seeds = 5`, and its rung is E2.
- **Then, not before:** promote E2 rows whose knob binds to E3 claims
  (registration committed before the first seed, paired seeds, fixed-n CI).

### T4 — Kernel coverage (the largest item, and the one nobody priced)

Only 10 of 75 primitives have a compiled kernel; 65 are reference-only. The
kill test and the parity test exist for the 10. A reference-only primitive is a
complete answer for correctness, but it is not the accelerated path the
capability claims name.

- Per acceleration module: land the primitive's step, then the kill test
  (patch `ReferenceAdapter.reference_step` to raise) and the parity test
  against the reference, then the microbench that prices the win.
- **Order:** the module whose primitive is E2 first; a kernel for an E1 row
  optimises an unproven cell.
- **Price:** measure the first module's parity + microbench cell, then price
  the rest from it; that measurement is this plan's next cost-model task, not
  a guess.
- **Close:** every `kernel_status="implemented"` passes kill + parity + has a
  measured speedup vs its reference; every `absent` row says so in the docs.

### T5 — Reproducibility (E4)

Every row carries a replay hash, and no row has been replayed on a second
machine or from a clean process.

- Re-run one family's base control and one earned claim on a second process
  and a second device profile; compare the replay hash and the CI.
- **Price:** one control (3 seeds) + one claim (10 cells); measured unit
  prices above.
- **Close:** the E4 rows name their second environment and their CI reproduces
  inside the registered margin.

---

## 5. Definition of done (replaces TODO97 §10)

1. Every row carries an evidence rung, and a rung is only claimed when the
   record supports it (T0).
2. **0 defects** in every map; every `unimplemented` row is either `tuned` or
   refused by name with a test that fails without the refusal (T1, T2).
3. Every `measured` row is E2 (L2/n≥5); every E3 row is pre-registered and its
   CI clears the margin (T3).
4. Every kernel row passes kill + parity, and every absent row is documented
   as reference-only (T4).
5. One control and one claim reproduce on a second process and device (T5).
6. The audit answers the same questions: no rung upgrade without a record, no
   refusal without a failing test, no kernel without parity.

**Not done because a row closed.** A refusal is a box statement; a screen is
E1; a width search is not a mechanism fix.

---

## 6. Cost model and stop rules

- **A cell's price is measured, never assumed.** One pilot cell per family,
  then `5 seeds × cell` for an E2 row, `3 rungs + 1 seed` for a ladder.
- **Watchdog = 2× the measured cost.** A rung killed past its watchdog is a
  cost-model defect or a bad box: record it, re-price, do not retry blind.
- **Parallel lanes:** 12 concurrent processes at 2 threads each (measured on
  16 cores). A 4-worker run's 300 s timeouts were CPU contention, not
  capability verdicts.
- **Stop when decided:** a defect closes on its failing test; a ladder closes
  when its best point is outside the band or the primitive is refused by name;
  an E2 row closes when the fifth seed is written.
- **Never** use a family-wide "30 minutes" as the goal; price the family first.

---

## 7. Locks this plan adds

| Lock | It must fail when |
|---|---|
| `test_a_row_carries_the_rung_its_record_supports` | a row claims E2/E3 from an E1 record |
| `test_a_refusal_has_a_failing_test` | a refusal exists without a test that fails without it |
| `test_a_defect_is_not_recorded_as_refused` | a defect is cleared by relabeling |
| `test_a_kernel_row_passes_kill_and_parity` | a kernel is claimed without both |
| `test_the_plan_counts_equal_the_artifacts` | the plan's inventory drifts from the maps |

---

## 8. First commands

```sh
# 0. The honest counts (this plan's §1), from the artifacts
uv run python - <<'PY'
import json, glob, collections
c = collections.Counter()
for p in glob.glob('results/sec*/map.json'):
    c.update(r['status'] for r in json.load(open(p))['primitives'].values())
print(dict(c))
PY

# 1. T0: the rung field, then regenerate the map doc
uv run python -m computronium.experiment.documentation.sec_map \
  --map results/sec/map.json --out docs/sec/map.md

# 2. T1: one defect, one cell, one lock
uv run python -m pytest tests/property/test_family_defect_locks.py -k nca -q

# 3. T2: one ladder at the row's own box (declared factors: 0.1, 1, 10)
uv run python -m computronium.experiment.sec_ladder \
  --map results/sec/map.json --only primitive.credit_assignment.pc_alm \
  --device cpu --dry-run

# 4. T3: one five-seed row (the probe that priced S11)
uv run python scripts/probes/s11_time_major_rows.py \
  --credit eligibility_prop --seeds 5 --write

# 5. The gates that must stay green while the work lands
uv run comp gate breadth          # 17/17, exit 0
uv run python scripts/audit.py --static   # 0 findings
```

---

## 9. What we stop calling "done"

- A row that ran once, at one box, is a screen. It is not a result.
- A refusal is a statement about a box, never about a primitive.
- "0 unaccounted rows" is bookkeeping, not capability. It was TODO97's
  definition of done, and it is why 65 primitives never trained on two
  families while the plan reported progress.
- A kernel that has never been priced is not a win.
