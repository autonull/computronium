# TODO90 — Breadth, not depth (Successor to TODO89)

**Status:** 2026-11-12 · base `e1243ed9` · **no ticket started** · starts in a
fresh session. TODO89 is closed: T1–T10 carry measured numbers, and its
remaining work is two depth items (graph third credit, PROTEINS 0.7040), parked
here with explicit triggers.

**Mission:** TODO89 made the instrument trustworthy and spent it on four
domains. TODO90 spends it on **surface**: every axis primitive exercised or
declared with a measured reason, every registered task measured or retired, and
one claim per domain. Breadth wins ties: a 0.71 PROTEINS row is depth; a
working `role_split` cell is breadth.

**Measured starting point (2026-11-12, 428 stores, 6,925 PASS cells, duckdb
2.0, 0 unreadable):**

| Surface | State |
|---|---|
| substrate / geometry / dynamics / plasticity / credit | 9/9, 11/11, 8/8, 7/7, 10/10 exercised |
| update | **11/12** — `role_split` has zero cells |
| tasks | **22/25** — `kmnist`, `char_ngram`, `tiny_shakespeare` never ran; `cifar10` 9 cells, `usps` 2 |
| domains | vision/graph/tabular/RL have claims; language, memory, timeseries have none; `ScientificTask` has no registry row |
| credit breadth | probe-backed for 3 geometries (T9/T10 arms are not store records) |
| gates | **3 acceptance locks fail** (f2 payload key, promotion L1 ×2), reproduced on duckdb 1.5.6 and 2.0.0 |
| objectives | 12 registered without a payload key; 15 measured keys with no objective |

Full evidence: `TODO89.md` §2b; raw probe `scripts/probes/t3_credit_breadth.py`.

---

## 0. Rules

Carried by `AGENTS.md` — one source of truth per rule, every number carries its
ruler, marginal is not met, a ticket closes on a claim or a named verdict. This
file adds one breadth rule:

> **A breadth ticket closes on a cell, a declared row, or a retirement.**
> "Investigated" is not a result; a primitive with no cell and no `VOID` row is
> an undeclared hole, and an undeclared hole is a defect.

Dependencies are the latest resolvable set (`uv.lock`, duckdb 2.0.0). No
backwards compatibility is written.

---

## 1. Priority order

Ordered by what unblocks the next measurable thing, not by interest.

| # | Ticket | Deliverable | Cost |
|---|---|---|---|
| B0 | **Acceptance repair** | promotion ladder and f2 number recompute are green; breadth evidence can reach L1/L2 | 30 min |
| B1 | **Corpus coverage command** | one `comp coverage` invocation reports the 428-store table, drift-locked to the probe | 30 min |
| B2 | **Store-backed breadth** | T3/T9/T10 probe arms become PASS records; no geometry's third credit is probe-only | 1 h |
| B3 | **`role_split`** | a cell on two geometries, or a declared row with the composition reason | 30 min |
| B4 | **Three untouched tasks** | `kmnist`, `char_ngram`, `tiny_shakespeare`: one PASS cell each, or retirement | 1–2 h |
| B5 | **Substrate × geometry holes** | graph off digital; nca on `complex`/`neuromorphic`; or declared rows | 1 h |
| B6 | **One claim per domain** | language, memory, timeseries; plus CIFAR-10 and a second RL task | 2–3 h |
| B7 | **Scientific domain** | one registered task with a loader and a cell, or a named retirement | 1 h |
| B8 | **Measurement breadth** | wire the cheap objectives; retire or register the orphan keys | 1–2 h |
| B9 | **Duplicate-rule cleanup** | nca `homeostatic`/`pc_alm` voids live in one table | 30 min |

A session takes **B0–B2 first** unless they are already green. They are the
instrument; every later ticket's evidence depends on them.

---

## 2. Tickets

### B0 — Acceptance repair (gate)

**Start:** `test_campaign_evidence_lock::test_f2_the_campaigns_own_numbers_are_the_stores_numbers`
raises `KeyError: 'train_acc'`; `test_promotion_lock` reports every cell at L2
and `Promoted: 0`, so no cell earns L1. Both reproduce on duckdb 1.5.6 and
2.0.0.

**Diagnosis:** the evaluator's payload carries `accuracy` (plus `loss`,
`epochs_*`, cost keys), not `train_acc`; the promotion ladder never emits an L1
record. Find the payload key through `schema.metrics.objective_metric`, not a
literal. For promotion, trace the fidelity decision: all-L2 means the ladder
short-circuits or the promotion gate reads the wrong verdict.

**Acceptance:** the three tests green, no `xfail`, no loosened assertion; a
measured run shows L0→L1→L2 progression with the promotion count in the report.
**Gate:** `uv run python -m pytest tests/acceptance/test_campaign_evidence_lock.py tests/acceptance/test_promotion_lock.py -q -rf --tb=line`.

### B1 — Corpus coverage command

**Start:** `comp coverage report` defaults to one run (6 cells). The corpus
instrument is `scripts/probes/t3_credit_breadth.py` (428 stores).

**Deliverable:** `comp coverage report` reads every readable store (or gains a
`--corpus`/`--all-stores` mode), prints per-axis seen/declared, per-geometry
error-aware credits, unreadable stores, and the tasks never touched.

**Acceptance:** one command prints the same numbers as the probe; a lock fails
if the CLI and the probe disagree on total cells and per-geometry counts. A
stale-store read failure is reported, not silently skipped.

### B2 — Store-backed breadth

**Start:** the table counts nca 3 / attention 3 / spatial_lattice 3 from probes;
`comp coverage` reads nca 1 / attention 2 / spatial_lattice 2 from stores.

**Deliverable:** re-run through `survey_cli` at the probe protocol (digits 8×8,
**3 seeds × 20 epochs as explicit values**, not the fidelity ladder):
`nca × random_projections`, `nca × target_inversion`, `attention × gradient`,
`spatial_lattice × gradient`. Each arm writes PASS records.

**Acceptance:** the probe reads nca 3, attention 3, spatial_lattice 3 **from
stores**; each arm's record carries the same metric value as the probe (within
1 σ), and every record's task name is the run's task (not `default`).
**Non-goal:** beating the probe numbers; this ticket's claim is provenance.

### B3 — `role_split` (U-axis breadth)

**Start:** zero cells in 428 stores. `ParameterUpdateConfig.role_split` needs
`role_names` plus two sub-rules (`on_role`, `other`); no axis hyperparameter
supplies them, so the composed row cannot express the primitive.

**Deliverable:** either (a) a declared default in the update factory —
muon-on-readout + euclidean elsewhere, the X-USU-001 winner — so the axis row
composes, or (b) `available=False` in `_UNAVAILABLE` with that exact reason.
Prefer (a): it is functional breadth and the paper arm already exists.

**Acceptance:** (a) one PASS cell on feedforward and one on a non-FF geometry
(e.g. conv), or (b) the row unavailable and a lock proving the composed
coordinate is refused with the reason.

### B4 — Three untouched tasks

**Start:** `kmnist` (medium, conv), `char_ngram` (medium, causal transformer),
`tiny_shakespeare` (expensive, causal transformer) have zero cells.

**Deliverable:** one cell each at an explicit cheap schedule (≤10 epochs, 1
seed for provenance; 3 seeds only if the task becomes a claim), with the task's
primary metric and the **ruler** printed beside it (chance/majority for
classification; unigram perplexity for language). If a loader is offline or
broken, retire the task from `SUPPORTED_TASKS` with the measured reason —
leaving it registered and unmeasured is the defect.

**Acceptance:** 3 PASS cells (or 3 named retirements), each reporting its
metric, ruler, and walltime. `comp coverage tasks` lists no `NOT TOUCHED`
task: every listed task is measured or absent from the registry.

### B5 — Substrate × geometry holes

**Start:** graph has zero cells off `digital`; nca is on 6 of 9 substrates
(`complex`, `neuromorphic`, `quantum` absent). Some absences are declared
(`nca_ntm_fast_weight_plasticity`, `nonlayered_geometry_dynamics`); these two
are not.

**Deliverable:** graph × `ternary` + graph × `sparse`; nca × `complex` +
nca × `neuromorphic`. If a tuple fails, the failure names its constraint (row
added with a measured reason) — not a silent prune.

**Acceptance:** each tuple yields a PASS cell or a `VOID` row with the measured
failure; the planner's drop count names the row (no silent drops).

### B6 — One claim per domain

Pick one task per domain that has no claim — **language, memory, timeseries** —
and pre-register its target before the run
(`configs/preregistrations/<slug>.json`). Then extend two domains that have a
claim to a second task. Suggested first arms:

| Domain | Task | Ruler | Target |
|---|---|---|---|
| language | `char_ngram` (medium) | unigram perplexity | pre-registered at the task's context length |
| memory | `copy_task` | token accuracy vs copy-the-input baseline | pre-registered, ≥3 seeds |
| timeseries | `synthetic_forecast` | naive last-value MAE | beat naive at ≥3 seeds, >1 σ |
| vision (breadth) | `cifar10` (conv, 9 cells) | 10 classes, majority printed | pre-register from the reference arm, ≥ chance×5 |
| continual sub-domain | `sequential_mnist` | per-task accuracy after the sequence | `forgetting` ≤ the pre-registered bound (B8 item 4 emits it) |
| RL (breadth) | `cartpole` or `acrobot` | random-policy mean_reward | mean_reward above random by >1 σ, 20 eval episodes |

**Acceptance per row:** a number with its ruler and pre-registration, met or
marginal — a task that already has 9+ cells is not "exploratory".

### B7 — Scientific domain

**Start:** `ScientificTask` is exported and constructible but absent from
`SUPPORTED_TASKS`; the domain has no registry row and no cells.

**Deliverable:** register one scientific task with an offline loader (a physics
simulation the repo already generates, e.g. pendulum state prediction with an
MSE objective and a naive baseline) **or** retire the domain's export with a
named verdict. Do not leave a constructible domain that coverage cannot see.

**Acceptance:** `comp coverage tasks` lists the task and one PASS cell exists,
or the export is gone and the plan records the verdict.

### B8 — Measurement breadth

**Start:** 12 objectives registered without a payload key (`bleu_score`,
`bp_deficit`, `convergence_steps`, `credit_efficiency`, `generalization_gap`,
`ruler_{energy,param,walltime}_ratio`, `stability_plasticity_ratio`,
`test_accuracy`, `test_loss`, `training_time`); 15 measured keys with no
objective (`accuracy`, `mean_reward`, `val_acc_mean`, …); `f1_score` and
`forgetting`/`backward_transfer` are unmeasured.

**Deliverable, in this order (cheapest first):**
1. Ruler ratios from existing payload keys (`walltime_s`, `param_count`,
   energy keys) — pure derivation, no new training.
2. `training_time` / `convergence_steps` from history the trainer already keeps.
3. `test_accuracy` / `test_loss` / `f1_score` — a real held-out test split; add
   it to the evaluator once, not per task.
4. `forgetting` / `backward_transfer` — requires the continual evaluation B6
   needs; do it with that ticket, not before.
5. Orphan keys: register as objectives or delete from `MEASURED_OBJECTIVES` so
   the mapping and the registry name the same set.

**Acceptance:** `comp coverage unmeasured` shrinks by the wired rows; a lock
asserts `set(MEASURED_OBJECTIVES) == registered objective names ∪ documented
internal keys` (the 15 are the current violation).

### B9 — Duplicate-rule cleanup

**Start:** nca × instantaneous `homeostatic` and `pc_alm` voids exist both as
registry rows and as `SystemConfig.validate` methods; T10 had to delete both
copies of the `target_inversion` rule.

**Deliverable:** one table. Make `validate` consult the declared rows (or delete
the methods and route every legality check through composition). A lock deletes
the registry row and proves the coordinate is refused with that row's reason —
the same mechanism lock T7 uses.

**Acceptance:** one source per rule; the lock fails if a second copy returns.

---

## 3. Success criteria for TODO90 (breadth)

| Criterion | Start | Target |
|---|---|---|
| Axis primitives exercised or declared | **56/57** (update 11/12) | **57/57** with a PASS cell or a named row |
| Tasks in `SUPPORTED_TASKS` measured or retired | 22/25 | **25/25**, each measured or absent from the registry |
| Geometries with store-backed ≥3 error-aware credits | 8/11 | **11/11** (B2 closes the 3 probe-only) |
| Domains with one claim | 4/7 | **7/7** (language, memory, timeseries close the gap) |
| Acceptance locks | 3 fail | **0 fail** |
| Corpus coverage instrument | probe only | **one command**, drift-locked |
| Registered-vs-measured objectives | 12 unmeasured, 15 orphans | **0 unexplained** |
| Duplicate legality tables | 2 (nca homeostatic/pc_alm) | **0** |

Measured 2026-11-12: 6,925 PASS cells over 428 stores. Each row above names the
instrument that would move it, and the target is a cell, a row, or a claim —
never a count of attempted work.

---

## 4. Ledger template (append per session)

| # | Ticket | Result | Evidence |
|---|---|---|---|
| B? | … | claim / verdict / retirement | probe path, lock name, store records |

Session log goes in the commit message body:

```
## Session YYYY-MM-DD
Experiment: <command>
Result: <number + ruler, or verdict>
Defects Found / Fixes Applied:
Next Experiment:
```

---

## 5. Parked (depth — trigger only)

1. **Graph third credit.** T8's verdict stands (`target_inversion` 0.6842 ±
   0.0204 vs 0.6579 majority, +1.29 SE, marginal). Trigger: a breadth claim
   cites graph credit breadth, or the graph energy settle is needed by another
   ticket. Then T8's acceptance applies (n=5 × 200 epochs, every seed >1 σ over
   majority).
2. **PROTEINS 0.7040.** Marginal until a claim cites that arm; then T6's
   pre-registered paired re-measure is the trigger.
3. Everything TODO89 §5 lists as NO stays NO: paper figures, publishing,
   retrospectives, cycles > 30 min, repo-wide gates outside round close.

---

## 6. Fresh-session bootstrap

```bash
# state
uv lock --check && uv run python -c "import duckdb, torch; print(duckdb.__version__, torch.__version__)"
uv run python scripts/probes/t3_credit_breadth.py | tail -40
uv run comp coverage report

# the gate B0 repairs
uv run python -m pytest tests/acceptance/test_campaign_evidence_lock.py \
  tests/acceptance/test_promotion_lock.py -q -rf --tb=line > logs/b0.log 2>&1
```

Read `TODO89.md` §2b before choosing a ticket; it owns the measured surface.
Start at B0 unless it is green; then B1, then B2.
