# TODO90 — Breadth, not depth (Successor to TODO89)

**Status:** 2026-11-13 · base `a0c4bb6c` · **B0–B9 closed, B10 closed for NCA**
· two named verdicts remain inside B10 (NTM controller, complex arithmetic).
TODO89 is closed: T1–T10 carry measured numbers, and its remaining work is
two depth items (graph third credit, PROTEINS 0.7040), parked here with
explicit triggers. All eight domains hold one claim (8/8), so the breadth
mission has a claim per domain.

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
| substrate × geometry | **18 pairs of 99 unmeasured and undeclared** — the plan named four |
| gates | **3 acceptance locks fail** (f2 payload key, promotion L1 ×2), reproduced on duckdb 1.5.6 and 2.0.0 |
| objectives | 12 registered without a payload key; 15 measured keys with no objective |

Full evidence: `TODO89.md` §2b; raw probe `scripts/probes/t3_credit_breadth.py`.

---

## Progress ledger

Session 2026-11-12 (second): B0–B3 closed. Session 2026-11-12 (third): B4
closed. Session 2026-11-13: B5 closed, and its instrument found a defect the
ticket did not predict. Session 2026-11-13 (second): B6a and B6c closed, and
the timeseries arm could not run at all until three defects were fixed. Session
2026-11-13 (third): B6b closed, and its ruler turned out to be the task's
ceiling. Session 2026-11-13 (fourth): B7–B10 closed or narrowed to named
verdicts. Every row names its instrument.

| # | Ticket | Result | Evidence |
|---|---|---|---|
| B0 | Acceptance repair | **Green.** f2 reads its objective through `objective_metric`, not a literal; promotion earns L1 (maturity starts at L0, the ladder writes L1, `maturation`/`deep_tier` gate L2); `Promoted:` counts matured records. 13 passed, 0 failed. | `tests/acceptance/test_campaign_evidence_lock.py`, `test_promotion_lock.py`; `evaluate.py::_device_lock` |
| B1 | Corpus coverage | **Green.** `comp coverage report --corpus` reads 428 stores and prints the probe's numbers; unreadable stores are named. | `computronium/experiment/evidence/corpus.py`, `tests/property/test_corpus_coverage_lock.py` |
| B2 | Store-backed breadth | **Green.** nca 3, attention 3, spatial_lattice 3 from stores; each arm 3 seeds × 20 epochs on digits, task `digits` on every record. Rule narrowed: the stale gradient void now names only `tile`. | `experiments/experiment_20261112_b2.duckdb`; `seed_registries.py` |
| B3 | `role_split` | **Green.** Declared default (muon-on-readout + Euclidean elsewhere); 10 PASS cells across feedforward and conv. Update axis 12/12 measured. | `ontology/update/__init__.py`, `tests/property/test_role_split_update.py`, `experiments/experiment_20261112_b3.duckdb` |
| B4 | Three untouched tasks | **Green.** `kmnist` 0.6669 val_acc (chance/majority 0.100), `char_ngram` 3.9923 ppl (unigram 25.21), `tiny_shakespeare` 8.4394 ppl (unigram 27.19); 1 seed each, 2 PASS records per task. Corpus task list holds no `NOT TOUCHED` row. | `experiments/experiment_20261112_b4.duckdb`; `tests/property/test_lm_target_alignment_lock.py` |
| B5 | Substrate × geometry holes | **Green, with one defect named.** 32 runs, 63 PASS records, 0 fail. The pair instrument closed **18 undeclared pairs** (68 measured → 92; 60 coupled → 78) and refused 21 (14 hold 192 cells that cannot count). 0 undeclared remain. | `experiments/experiment_20261113_b5.duckdb`; `evidence/corpus.py`; `tests/property/test_corpus_coverage_lock.py`, `test_substrate_reaches_compute_lock.py` |
| B6a | Language claim | **Met.** `char_ngram` at L2 (5 seeds × 20 epochs, all PASS): val_ppl **2.4617 ± 0.0338** (SE), one-sided 95% upper bound **2.5337**, against a **5.0** threshold and a **23.77** unigram ruler on the same 1,024-item split — **9.66× below the ruler**, 75 SE clear of the threshold. claim-eligible cells **1**. | `experiments/experiment_20261113_b6a.duckdb`; `configs/preregistrations/b6a_language_char_ngram_ppl.json` |
| B6b | Memory claim | **Met, on a re-derived ruler.** `copy_task` at L2 (5 seeds × 20 epochs, all PASS): val_acc **0.6552 ± 0.0280** (SE), lower bound **0.5956**, against a **0.50** threshold and the strongest fixed-policy ruler **0.12825** — **5.11× the ruler**, **60.4%** of the headroom to the task's **1.000** positional-copy ceiling, 5.55 SE clear. The ticket's named ruler (copy-the-input) *is* that ceiling, so the ruler was re-derived from fixed policies. claim-eligible cells **1**. | `experiments/experiment_20261113_b6b.duckdb`, `experiment_20261113_b6b_ntm_arm.duckdb`; `configs/preregistrations/b6b_memory_copy_task_token_accuracy.json`; `tests/property/test_copy_task_ruler_lock.py` |
| B6c | Timeseries claim | **Met, after three defects were fixed** (see below). `synthetic_forecast` at L2 (5 seeds × 20 epochs, all PASS): val_mae **0.08904 ± 0.00117** (SE), upper bound **0.09153**, against a **0.100** threshold, the **0.11459** naive last-value ruler and the **0.07979** noise floor — **1.287× below naive**, 73.4% of the 0.0348 headroom removed, 8.7 combined SE of separation. claim-eligible cells **1**. | `experiments/experiment_20261113_b6c.duckdb`; `configs/preregistrations/b6c_timeseries_synthetic_forecast_mae.json`; `tests/property/test_regression_target_lock.py` |
| B7 | Scientific domain | **Green, with a claim.** `pendulum_state` registered (`ScientificTask`, offline Euler ODE), 6 PASS records; claim at L2 (5 seeds × 20 epochs, all PASS): val_loss **1.7574e-5 ± 1.2386e-6** (SE), upper bound **2.02e-5**, against a **0.010** threshold and the **0.04302 ± 0.00088** identity ruler — **2,448× below the ruler**, 8 domains with a claim. The row matches the loader ((3,)→3, batch 32), and `SCIENTIFIC` maps its primary metric to `mse`. | `experiments/experiment_20261113_b7.duckdb`; `configs/preregistrations/b7_scientific_pendulum_state_mse.json`; `tests/property/test_scientific_task_lock.py`; `scripts/probes/b7_pendulum_state_ruler.py` |
| B8 | Measurement breadth | **Green.** 15 of 51 mapped objectives had no registry row and 9 registered rows had no measurement. The two surfaces now name the same **54** measured rows; `f1_score`/`bleu_score`/`test_*`/`ruler_*`/`bp_deficit`/`credit_efficiency` are retired with the measurement each would need. Four derived metrics are emitted from numbers the cell already measured (`training_time`, `convergence_steps`, `generalization_gap`, `stability_plasticity_ratio`); `mean_length` joins the declared key space; `perplexity` task rows point at `val_ppl`, not a second key. `comp coverage unmeasured` reads **2** rows (the deferred continual pair), down from 15. | `computronium/experiment/schema/{metrics,seed_registries}.py`, `kernel/_metrics.py`, `kernel/evaluate.py`, `registry/task_registry.py`; `tests/property/test_objective_breadth_lock.py` |
| B9 | Duplicate-rule cleanup | **Green.** `NCA_CELL_MODE_CREDITS` is the one table: `SystemConfig.validate` reads it at call time and the two constraint rows are generated from it, so a credit removed there stops being refused in both places. The S5-local `_references_params` copy is deleted; both stages import `legality/dsl.references_params`, which treats `output_dim` as a hyperparameter. | `computronium/ontology/system.py`, `experiment/schema/seed_registries.py`, `experiment/execution/stages_impl.py`; `tests/property/test_legality_single_source_lock.py` |
| B10 | Substrate reaches NCA/NTM | **Closed for NCA, narrowed for NTM, and a third defect named.** `NcaGeometry`'s cell MLP and readout run through `substrate.get_forward_operator()` (via `_substrate_linear`), threaded through `step`, `rollout`, `route` and `forward_with_intermediates`. Re-measured 8 NCA arms on `digits` (2 epochs, 1 seed): all PASS, 6 non-complex arms have distinct `train_loss` (digital 1.99038 vs analog 2.01361, ternary 2.03621, sparse 2.08250, memristive 2.00146, optical 1.99451, quantum 1.99591) and now count as substrate-coupled. Two verdicts: `ntm_substrate_inert` (the stock LSTM controller has no single-operator form) and the newly measured `complex_substrate_real_compute` (complex arithmetic on real weights bit-reproduces digital: 279 stored complex cells cannot count). | `computronium/ontology/geometry.py`, `experiment/schema/seed_registries.py`; `experiments/experiment_20261113_b10_nca.duckdb`; `tests/property/test_substrate_reaches_compute_lock.py`, `test_corpus_coverage_lock.py` |

**Defect found in B0 and fixed with B0:** one CUDA device ran four cells and
three seeds concurrently, corrupting Inductor's static Triton launcher
(`CUDA_ERROR_INVALID_HANDLE`, `load_kernel() must be called before run()`) and
cuSOLVER's QR wrapper (`lazy wrapper should be called at most once`). One
process-wide per-device lock in `evaluate_cell` serializes CUDA training; the
campaign went from 15 failed records to 0, and walltime measures the cell rather
than contention. CPU evaluation still runs concurrently.

**Three defects found in B6c and fixed with B6c.** The timeseries claim did not
exist because the domain could not train at all — not because it performed
poorly:

1. **A regression target was read as a class index.** `_align_target_rows`
   folded any target whose element count matched the logits' row count; for a
   `[B, 1]` float target that is `[B]`, and `nudged_output` then scattered it
   (`scatter(): Expected dtype int32/int64 for index`). Folding now requires a
   non-floating target; `_one_hot`/`nudged_output` reshape a float target of the
   logits' element count and refuse one that is neither.
2. **The pipeline had no way to receive the task's loss.** Every loss site ran
   cross-entropy, so a regression cell optimized (and validated with) class
   likelihood: `val_loss` was `0.0`/nonsense on the 26 pre-existing
   `synthetic_forecast` records. `loss_fn` is now declared on the composed
   system — composition hands it `DomainTask.compute_loss` — threaded through
   `_TrainStepContext`/`_PhaseContext` to all four loss sites, and used by
   `SystemTrainer.validate`.
3. **The positive control assumed a legal coordinate.** `synthetic_forecast`
   and `sequential_mnist` name a `recurrent` geometry hint, and
   `SystemConfig.validate` refuses `gradient` + `instantaneous` on a recurrent
   geometry, so the control cell could not compose and was silently skipped
   (`gate=N/A` in b6c's log). The control is now a declared two-arm ladder (the
   hint, then `feedforward` over the task's own shape); an arm that cannot
   compose writes no record, so the next arm runs. Verified: arm 1 skipped, arm
   2 PASS.

Lock: `tests/property/test_regression_target_lock.py` (6 tests: the fold, the
nudge, the declared-loss choice, one real regression step whose `free_loss`
equals the task's MSE, and the control ladder composing only on its fallback).

**Measured now (2026-11-12, after B2/B3):** this session's first `comp coverage
report --corpus` read **7,288 PASS cells over 428 stores**; after B2/B3 the same
command reads **7,319 PASS cells over 430 readable stores, 0 unreadable**. Axis
primitives are 57/57 exercised (update 12/12). Ten of eleven geometries hold
≥3 store-backed error-aware credits; **graph holds 2** (gradient,
random_projections) and its third credit is the parked T8 verdict, not a B2
gap.

**Measured after B4:** the same command reads **7,325 PASS cells over 431
readable stores, 0 unreadable**, and its task section ends with "every
registered task is measured" — the three `NOT TOUCHED` names are gone.

**Measured after B5 (2026-11-13):** the same command reads **7,388 PASS cells
over 432 readable stores, 0 unreadable**. Its new pair section reads **92 of 99
substrate × geometry pairs hold a PASS cell, 78 of them on a coordinate no rule
refuses, 21 refused by a rule, 0 undeclared**. Fourteen of the refused pairs
hold 192 cells; those cells cannot count as substrate breadth (B10).

**Measured after B6a/B6c (2026-11-13, second):** the same command reads **7,401
PASS cells over 435 readable stores, 0 unreadable** — the two claims added 13
PASS cells and 3 stores. `char_ngram` moves from 2 to **10** PASS cells and
`synthetic_forecast` from 31 to **36**, so both now carry a claim-grade cell
rather than a provenance cell.

**Measured after B6b (2026-11-13, third):** the same command reads **7,409 PASS
cells over 437 readable stores, 0 unreadable** — the claim store and the ntm
arm store added 8 PASS cells and 2 stores (the superseded feedforward pilot was
deleted, not counted). `copy_task` moves from 55 to **63** PASS cells. The pair
and task sections are unchanged: 92/99, 25/25.

**Measured after B7/B10 (2026-11-13, fourth):** the same command reads **7,424
PASS cells over 439 readable stores, 0 unreadable** — B7's claim store added 6,
B10's NCA sweep added 9, and the three superseded B7 pilot stores were deleted,
not counted. The pair section now reads **92/99 hold a cell, 75 on a
coordinate no rule refuses, 24 refused, 0 undeclared**; **17 refused pairs hold
346 cells** that cannot count (11 complex pairs, 6 NTM pairs). Tasks are
**26/26** measured. `comp coverage unmeasured` reads **2** rows.

| Surface | At plan start | Now |
|---|---|---|
| Axis primitives exercised or declared | 56/57 (update 11/12) | **57/57** (update 12/12) |
| Geometries with store-backed ≥3 error-aware credits | 8/11 | **10/11** — graph has 2; T8's third credit is parked (marginal, not met) |
| Acceptance locks | 3 fail | **0 fail** |
| Corpus coverage instrument | probe only | **one command**, drift-locked, with a substrate × geometry pair section |
| Tasks measured or retired | 22/25 | **26/26** — `pendulum_state` joins the registry (B7) |
| Substrate × geometry pairs | 20 holes, 4 named by the plan | **92/99 hold a cell; 75 substrate-coupled; 24 refused; 0 holes** |
| Domains with one claim | 4/7 | **8/8** — language, timeseries, memory, scientific |
| Registered-vs-measured objectives | 12 unmeasured, 15 orphans | **54 declared = 54 measured, 9 retired with reasons; 2 task rows unmeasured (continual)** |
| Duplicate legality tables | 2 | **0** — one credit table, one `references_params` |

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

| # | Ticket | Deliverable | Cost | State |
|---|---|---|---|---|
| B0 | **Acceptance repair** | promotion ladder and f2 number recompute are green; breadth evidence can reach L1/L2 | 30 min | **closed** |
| B1 | **Corpus coverage command** | one `comp coverage` invocation reports the 428-store table, drift-locked to the probe | 30 min | **closed** |
| B2 | **Store-backed breadth** | T3/T9/T10 probe arms become PASS records; no geometry's third credit is probe-only | 1 h | **closed** |
| B3 | **`role_split`** | a cell on two geometries, or a declared row with the composition reason | 30 min | **closed** |
| B4 | **Three untouched tasks** | `kmnist`, `char_ngram`, `tiny_shakespeare`: one PASS cell each, or retirement | 1–2 h | **closed** |
| B5 | **Substrate × geometry holes** | graph off digital; nca on `complex`/`neuromorphic`; or declared rows | 1 h | **closed** |
| B6a | **Language claim** | `char_ngram` val_ppl under a pre-registered threshold | 1 h | **closed, met** |
| B6b | **Memory claim** | `copy_task` token accuracy over the fixed-policy rulers, with the copy-the-input ceiling named | 1 h | **closed, met** |
| B6c | **Timeseries claim** | `synthetic_forecast` MAE over the naive last-value ruler | 1 h | **closed, met** |
| B7 | **Scientific domain** | one registered task with a loader and a cell, or a named retirement | 1 h | **closed, claim met** |
| B8 | **Measurement breadth** | wire the cheap objectives; retire or register the orphan keys | 1–2 h | **closed** |
| B9 | **Duplicate-rule cleanup** | nca `homeostatic`/`pc_alm` voids live in one table | 30 min | **closed** |
| B10 | **Substrate reaches NCA/NTM** | thread the substrate operator through `NcaGeometry` and `NtmGeometry`, then re-measure 14 pairs | 2 h | **closed for NCA; NTM and complex named** |

A session takes **B0–B2 first** unless they are already green. They are the
instrument; every later ticket's evidence depends on them.

**Progress (2026-11-13, fourth session):** B0–B10 are closed with the results in
§0a. **All eight domains hold one claim**, every registered task is measured,
the objective mapping and registry name the same 54 rows, the duplicate legality
tables are gone, and NCA's substrate path is measured. Two named verdicts stay
inside B10 rather than being silently dropped: `ntm_substrate_inert` (a stock
LSTM controller has no single-operator form) and `complex_substrate_real_compute`
(the complex operator is the digital matmul on real weights). B5 widened under
its own instrument; B6c and B6b each widened in a different direction; B7
widened into a pipeline defect (a multi-column regression target crashed every
loss site); B10 widened into the complex-substrate verdict.

**Remaining work is depth or a trigger, not breadth.** The breadth queue is
empty: no axis primitive, task, domain, objective row, or substrate × geometry
pair is undeclared. §5 lists the parked depth items and the breadth arms below
(with their pre-registered rulers) are the only optional spend.

**B6b start state (closed 2026-11-13, third session):** `copy_task` held 55 PASS
cells, so the task trained; the missing piece was the ruler. The three steps the
plan prescribed were followed and the first one found the defect: on the measured
split (20,000 rows) the fixed-policy rulers are at chance (all-zero 0.12585,
copy-one-step 0.12205, majority-token **0.12825**, uniform 0.125), but the
positional copy — emit the input token at the sample's own step index, which the
pad count reveals — reads every target and scores **1.000**. The
"copy-the-input baseline" the ticket names is therefore the ceiling, and no arm
can beat it; the claim registers the fixed-policy rulers instead and reports the
ceiling as the bound. Two stale declarations were fixed with the ticket: the
registry row declared `(10,)`/`2` where the loader emits `(21,)`/`8` and a batch
of 64, and `CopyTask` declared the timeseries domain while its registry row says
memory.

**B6a/B6c start states are closed** and kept in §2 only for their measured
numbers and their defect list.

**Remaining work (ordered, 2026-11-13):** every open ticket now closes on a
cell, a row or a named verdict; none needs a claim.

| # | What closes it | First command | Risk / note |
|---|---|---|---|
| B7 | one scientific task registered with an offline loader **or** the `ScientificTask` export retired with a named verdict | `uv run comp coverage tasks \| grep -i scientific` (empty today) | The pendulum generator already exists in `domains/timeseries.py`; a scientific row can reuse it, so the repair may be a registry row plus a baseline, not a new dataset. |
| B8 | `comp coverage unmeasured` shrinks by the rows wired; a lock asserts `MEASURED_OBJECTIVES == registered objective names ∪ documented internal keys` | `uv run comp coverage unmeasured` | Five sub-deliverables, cheapest first; `test_loss`/`test_accuracy`/`f1_score` need a real held-out split added to the evaluator once. `forgetting`/`backward_transfer` wait for a continual ticket. |
| B9 | one source per legality rule; the lock fails if a second copy returns | `grep -rn "def _references_params" computronium/` | Three copies named (§2 B9). The S5 copy must import `legality/dsl.py`'s helper so `classification_requires_classifier_head` lands at compose time. |
| B10 | `nca_ntm_substrate_inert` deleted, the 14 pairs re-measured, `train_loss` off digital | `uv run python -m pytest tests/property/test_substrate_reaches_compute_lock.py -q` | Depth; trigger is a claim that cites substrate breadth for nca/ntm. The lock currently asserts the defect, so it flips with the fix. |

**B10 start state (2026-11-13):** `NcaGeometry` and `NtmGeometry` call
`nn.Linear`/`nn.LSTM` directly; `get_forward_operator()` is never reached, so
every non-digital substrate reproduces the digital arm's `train_loss` to six
decimals (`experiments/experiment_20261113_b5.duckdb`). The row
`nca_ntm_substrate_inert` refuses the 14 pairs and
`tests/property/test_substrate_reaches_compute_lock.py` fails the moment a
geometry starts reading the substrate — delete the row in the same commit.

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

**Result (2026-11-12):** 13 passed in 124 s (plus `test_campaign_lock.py`: 7
passed). The payload key is now `objective_metric(campaign.spec.objectives[0])`;
the promotion test's 10 records all PASS and earn L1, history lists them, and
`Promoted:` is non-zero. The spec's budget moved 60 s → 300 s because serialized
CUDA training costs ~110 s for its ten records — the deadline, not the cell, was
deciding which seeds reached the store.

### B1 — Corpus coverage command

**Start:** `comp coverage report` defaults to one run (6 cells). The corpus
instrument is `scripts/probes/t3_credit_breadth.py` (428 stores).

**Deliverable:** `comp coverage report` reads every readable store (or gains a
`--corpus`/`--all-stores` mode), prints per-axis seen/declared, per-geometry
error-aware credits, unreadable stores, and the tasks never touched.

**Acceptance:** one command prints the same numbers as the probe; a lock fails
if the CLI and the probe disagree on total cells and per-geometry counts. A
stale-store read failure is reported, not silently skipped.

**Result (2026-11-12):** `comp coverage report --corpus` and
`scripts/probes/t3_credit_breadth.py` both report 7,288 PASS cells over 428
readable stores at the session's start, 0 unreadable, 11 geometries. Both call
`evidence.corpus.scan_corpus`; `tests/property/test_corpus_coverage_lock.py`
builds a small corpus (two readable stores, one FAIL record, one unreadable
store) and asserts the command and the probe agree on total, per-geometry
error-aware credits, tasks, untouched tasks, and the unreadable path.

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

**Result (2026-11-12):** `experiments/experiment_20261112_b2.duckdb` holds four
runs at the probe protocol (digits 8×8, seeds 0/1/2, 20 epochs, hidden_dim 64,
param_budget 0 so the grid is 8×8):

| Arm | Store mean ± SE (n=3) | Probe | Verdict |
|---|---|---|---|
| nca × random_projections | 0.8917 ± 0.0048 (CPU) | 0.8907 ± 0.0009 (t9, CPU) | matches |
| nca × target_inversion | 0.9389 ± 0.0058 (CUDA) | 0.9389 ± 0.0056 (t10, CPU) | matches |
| attention × gradient | 0.9787 ± 0.0009 | 0.9472 at 2 epochs (t3) | same arm, more training |
| spatial_lattice × gradient | 0.9824 ± 0.0009 | 0.9361 at 2 epochs (t3) | same arm, more training |

The nca arms were also measured on CUDA (random_projections 0.8778 ± 0.0089),
which is a device difference, not a credit difference; the CPU record is the
one compared with the CPU probe. Every record's task is `digits`; every cell
has three PASS seeds. The t3 gap probe measured at 2 epochs, so its number is a
lower bound, not the 20-epoch target (the ticket's non-goal). The declared void
`nonlayered_instantaneous_gradient_credit` named attention, spatial_lattice, nca,
ntm and others; stores now hold PASS gradient cells for all of them, so the row
names only `tile` (the one topology with none), with its measured reason in
`seed_registries.py`.

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

**Result (2026-11-12, option a):** `ParameterUpdateConfig.role_split()` now has
a declared default — `role_names=("readout",)`, Muon on the readout, Euclidean
elsewhere — and accepts the swept `step_size`/`momentum`/`grad_clip`, so the
axis row composes. A factory cannot know a parameter name before the geometry
exists, so `RoleSplitUpdate` resolves the `readout` token against the composed
geometry's `output_dim` at step time. `experiments/experiment_20261112_b3.duckdb`
holds 10 PASS role_split cells (5 feedforward, 5 conv) at a 3-epoch screening
schedule; the update axis is now 12/12 measured. Locks:
`tests/property/test_role_split_update.py::TestDeclaredDefault` and
`test_registry_completeness_lock.py` (which now catalogues role_split).

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

**Result (2026-11-12):** `experiments/experiment_20261112_b4.duckdb` holds three
runs, 2 PASS records each (the arm plus the run's positive control). Digits for
the ruler were computed from the split the cell measured.

| Task | Arm | Epochs × seed | Primary metric | Ruler | Walltime |
|---|---|---|---|---|---|
| `kmnist` | digital/conv/instantaneous/null/gradient/adam, CUDA | 3 × 1 | val_acc **0.6669** | chance = majority = 0.100 (balanced) | 37 s |
| `char_ngram` | digital/feedforward/instantaneous/null/gradient/adam, CUDA | 10 × 1 | perplexity **3.9923** (val_acc 0.5215) | unigram ppl 25.21; chance 0.037 | 6 s |
| `tiny_shakespeare` | digital/causal_transformer/instantaneous/null/gradient/adam, CUDA | 5 × 1 | perplexity **8.4394** (val_acc 0.3714) | unigram ppl 27.19; majority 0.1535 | 17 s |

`comp coverage report --corpus` now ends its task section with "every registered
task is measured"; tasks are 25/25. The probes are
`scripts/probes/`-class throwaways and are not committed; the store is the
evidence.

**Defects found in B4 and fixed with B4** — each one made the task
unmeasurable, not merely poor:

1. `LMTask` handed the trainer a bare token `DataLoader` whose items are single
   tensors; `SystemTrainer` unpacks `(x, y)` and died with "too many values to
   unpack (expected 2)" before the first step. The loader now yields
   `_NextTokenDataset` pairs `(tokens[i:i+T], tokens[i+1:i+T+1])`.
2. `LMTask.compute_loss` reshaped a second time after `TransformerGeometry`
   had already folded `[B, T]` into `[B*T, V]`, comparing 4096 logits against
   32 target rows. One `_flat` helper now folds both sides (the same
   `_align_target_rows` the pipeline uses).
3. `build_causal_transformer_config` took the vocabulary from `input_dim` (the
   *sequence length*, 128) and left `seq_len` at a fixed 32: a 65-char corpus
   composed a 128-class head under a 32-position embedding table. LM mode now
   reads vocabulary from `output_dim` and positions from the task's shape
   (D16's rule).
4. `_sample_inputs` stacked a collated `(x, y)` list into `[2, B, T]`, so the
   free-settle probe compared `B*T` logits to a `T`-wide positional table
   ("free settle telemetry failed"). A two-element collection is now the pair
   the provider contract declares.
5. `CharNGramTask` declared a 50-token causal-transformer row while
   implementing single-step prediction over a 3-token window, evaluated on a
   one-sample zeros loader, and had no `compute_loss` at all — the cell
   measured 0.0 accuracy by construction. It now has a seeded
   `_NextCharDataset` (train 4096 / val 1024 items), a real `compute_loss`, a
   perplexity metric, and a truthful registry row (`(3,) → 27`,
   `geometry_hint="feedforward"`).

Locks: `tests/property/test_lm_target_alignment_lock.py` gains
`test_causal_transformer_lm_takes_vocab_from_output_dim` (fails if the builder
reverts to `input_dim`/32) and `test_lm_dataloader_yields_next_token_pairs`
(fails if the loader returns bare tensors or loses the one-token shift).

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

**Result (2026-11-13):** the ticket widened under its own instrument. The pair
section added to `comp coverage report --corpus` reports the *declared* product
(9 substrates × 11 geometries = 99 pairs) instead of the four coordinates the
plan guessed, so the sweep covered all 18 undeclared pairs: 32 runs, 63 PASS
records, 0 fail, in `experiments/experiment_20261113_b5.duckdb`. Every run
pinned all six axes (`gradient`/`adam`, 2 epochs, 1 seed, CUDA) against the
task that geometry already uses: `digits` for conv/attention/spatial_lattice,
`cora` for graph, `tiny_shakespeare` for causal_transformer.

| Geometry | Task | Arm val_acc per substrate | Digital ruler |
|---|---|---|---|
| graph | cora | ternary **0.330**, sparse **0.226** | 0.274 (majority ≈ 0.30; 500 val nodes, 1σ ≈ 0.020) |
| conv | digits | quantum **0.622** | 0.653 |
| attention | digits | quantum **0.947**, sparse **0.947** | 0.944 (360 val rows, 1σ ≈ 0.012) |
| spatial_lattice | digits | analog **0.939** | 0.939 |
| causal_transformer | tiny_shakespeare | analog **0.279**, complex **0.307**, memristive **0.298**, optical **0.311**, quantum **0.307**, sparse **0.304**, ternary **0.272** | 0.307 (val ppl 10.7–12.0; unigram 27.19) |
| nca | digits | complex **0.425**, optical **0.419**, quantum **0.419** | 0.425 — **inert**, see B10 |
| ntm | digits | analog **0.783**, quantum **0.783**, ternary **0.783** | 0.783 — **inert**, see B10 |

The claim is provenance, not accuracy: at 2 epochs the graph arms sit within
1–3σ of the majority rate, and the ticket's non-goal is beating a ruler. The
corpus now reads **92/99 pairs with a cell, 78 substrate-coupled, 21 refused by
a rule, 0 undeclared**. `neuromorphic × {attention, causal_transformer, conv,
graph, spatial_lattice}` is refused on both sides of an empty intersection: the
geometry needs instantaneous dynamics and the substrate refuses it.

**Defect found in B5 and named, not fixed (B10):** three pairs reproduce the
digital arm's `train_loss` to six decimals — `ntm × {analog, quantum, ternary}`
and `nca × complex` — because `NcaGeometry` and `NtmGeometry` never call the
substrate's forward operator. A PASS cell existed; the substrate never entered
the computation. The row `nca_ntm_substrate_inert` now refuses those 14 pairs,
the pair section lists the 192 cells that cannot count, and
`tests/property/test_substrate_reaches_compute_lock.py` pins both directions
(row present ⇒ coordinate refused; geometry wired ⇒ assertion fails).

**Instrument (2026-11-13):** `CorpusCoverage` gained `pairs`, `pair_gaps` and
`pair_holes`; the pair verdict comes from the system's own void rules, pruned by
each rule's variable footprint (`referenced_names` in `legality/dsl.py`, the
one traversal `references_params` now also uses). The report names the
shallowest rule that explains a refusal, so a dynamics contradiction is not
blamed on a credit. Lock: `tests/property/test_corpus_coverage_lock.py` (five
tests: command ≡ probe, every pair accounted for, a void names its rule, a
reachable unmeasured pair is a hole, deleting a rule turns voids into holes).

### B6 — One claim per domain (split into three)

One ticket per domain, because each closes on its own pre-registered ruler and
a session that takes all three re-pays the harness cost three times. Take them
in this order: B6a is the cheapest ruler to compute, B6c the most independent.

| # | Domain | Task | Ruler | Pre-registration |
|---|---|---|---|---|
| B6a | language | `char_ngram` | unigram perplexity **23.77** on the measured split (vocabulary-uniform 27.0); B4 quoted 25.21 from another estimator | threshold on `val_ppl`, ≥3 seeds — **closed, met** |
| B6b | memory | `copy_task` | fixed-policy rulers: majority-token **0.12825**, all-zero 0.12585, copy-one-step 0.12205, uniform 0.125; the copy-the-input policy is the **1.000** ceiling | threshold on val_acc, ≥3 seeds — **closed, met** |
| B6c | timeseries | `synthetic_forecast` | naive last-value MAE **0.11459**; noise floor 0.07979 | threshold on MAE, ≥3 seeds, beat naive by >1 σ — **closed, met** |

Each: write `configs/preregistrations/<slug>.json` **before** the run
(`ThresholdRegistration` or the paired-comparison form), then run three seeds
through `survey_cli` with all six axes pinned and `--epochs` large enough to
beat the ruler at one seed first (a claim at a schedule that measures chance is
not a claim). Report the number with its ruler and its distance from it in σ.

**Result B6a (2026-11-13):** met. `configs/preregistrations/b6a_language_char_ngram_ppl.json`
registered a 5.0 val_ppl threshold before the confirmatory run; the arm ran at
L2 (5 seeds × 20 epochs, `digital/feedforward/instantaneous/null/gradient/adam`)
in `experiments/experiment_20261113_b6a.duckdb`, 68 s, 6 PASS records, 1
claim-eligible cell.

| Seed | val_ppl | val_acc |
|---|---|---|
| 42 | 2.5869 | 0.6475 |
| 43 | 2.4296 | 0.6475 |
| 44 | 2.3848 | 0.6963 |
| 45 | 2.4584 | 0.6973 |
| 46 | 2.4488 | 0.7021 |

Mean **2.4617**, sd 0.0755, SE 0.0338, one-sided 95% upper bound **2.5337 < 5.0**
(75 SE clear). Ruler: unigram perplexity **23.7720** over the same 1,024-item
validation split (24 distinct target classes, majority 0.0518), so the arm sits
**9.66× below the ruler**; in log space, 0.709 nats of margin = 51.7σ. The
task's ceiling is not 1.0: the deterministic cycle is a sawtooth in the raw
float coordinates, so val_acc plateaus at 0.65–0.70 while the perplexity keeps
falling — the claim is about the metric the registry names, not about solving
the sawtooth.

**Result B6c (2026-11-13):** met, and it took three pipeline fixes to make the
domain measurable at all (§0a). Registration:
`configs/preregistrations/b6c_timeseries_synthetic_forecast_mae.json`, 0.100
val_mae threshold; arm at L2 (5 seeds × 20 epochs) in
`experiments/experiment_20261113_b6c.duckdb`, 53 s, 5 PASS records, 1
claim-eligible cell.

| Seed | val_mae | val_loss (MSE) |
|---|---|---|
| 42 | 0.09071 | 0.01305 |
| 43 | 0.08783 | 0.01188 |
| 44 | 0.08586 | 0.01159 |
| 45 | 0.09254 | 0.01341 |
| 46 | 0.08826 | 0.01227 |

Mean **0.08904**, sd 0.00261, SE 0.00117, upper bound **0.09153 < 0.100**
(9.4 SE clear). Rulers: naive last-value **0.11459** (n = 994, SE 0.00268),
linear extrapolation 0.19950 (worse), and the generator's noise floor
**0.07979** = 0.1·√(2/π). The arm is **1.287× below naive**, removes **73.4%**
of the 0.0348 headroom above the floor, and separates from naive by 8.7
combined SE.

**Result B6b (2026-11-13, third session):** met, on a re-derived ruler.
Registration: `configs/preregistrations/b6b_memory_copy_task_token_accuracy.json`,
0.50 val_acc threshold. The arm is
`digital/feedforward/instantaneous/null/gradient/adam` at L2 (5 seeds × 20
epochs) in `experiments/experiment_20261113_b6b.duckdb`, 129 s, 6 PASS records
(the run's positive control plus 5 seeds), 1 claim-eligible cell.

| Seed | val_acc | val_loss |
|---|---|---|
| 42 | 0.6255 | 0.9043 |
| 43 | 0.7195 | 0.7736 |
| 44 | 0.5870 | 0.9598 |
| 45 | 0.6200 | 0.9006 |
| 46 | 0.7240 | 0.7507 |

Mean **0.6552**, sd 0.0625, SE 0.0280, one-sided 95% lower bound **0.5956 >
0.50** (5.55 SE clear). Rulers on the same 20,000-row split (2,000 sequences ×
10 steps): majority-token **0.12825**, all-zero 0.12585, copy-the-input one step
0.12205, vocabulary-uniform 0.125. The arm is **5.11×** the strongest ruler and
removes **60.4%** of the 0.87175 headroom between that ruler and the ceiling.

**Ruler defect found in B6b (the ticket's named ruler is the ceiling).**
`copy_task` puts `y = seq[t]` in the input vector at index `t`, and `t` is
recoverable as `non_pad_length - seq_len - 1`; a positional copy therefore reads
**every** target and scores exactly **1.0000**. The "copy-the-input baseline" the
ticket names is thus the task's ceiling, and a claim stated as beating it is
unattainable by construction — the ticket's own step 1 ("the trivial policy that
beats 'copy' is not the same one that beats 'zero'") anticipated this. The
registration keeps both numbers: the ceiling is declared as the bound, the
threshold is derived from the fixed-policy rulers, and the lock asserts the
bracket `max(fixed rulers) < threshold < ceiling`. A streaming copy — state
carried across steps so the input never holds the answer — is the repair that
would make "beat copy" meaningful; it is parked (§5) because it re-pins the 63
existing `copy_task` cells and is depth, not breadth.

**Two stale declarations found in B6b and fixed with B6b.** Each made the task's
declared identity disagree with what it measures:

1. **The registry row did not describe the loader.** It declared
   `input_shape=(10,)` ("binary"), `output_dim=2`, `typical_batch_size=16`; the
   loader emits a 21-wide float token vector (10 source + delimiter + up to 10
   copied prefix, pad 9) with 8 target classes at batch 64. The row now matches,
   and the batch size has one source (`CopyTask._batch_size`) instead of a
   ternary repeated in both loaders.
2. **The task class declared the wrong domain.** `CopyTask.domain_type` and
   `.spec` said `TIMESERIES` while its registry row says `MEMORY`, which routed
   the primary-metric lookup to `mse` — a key `CopyTask.evaluate` never returns.
   Both now say `MEMORY`.

Lock: `tests/property/test_copy_task_ruler_lock.py` (5 tests: the positional
copy reads every target at the pad-derived index, every fixed policy sits within
6.8 SE of the vocabulary-uniform rate, the registry row matches the loader's
shape and batch, the task class and row name the same domain, and the
registration brackets rulers and ceiling). 5 passed. Re-measured: this arm's
`ntm` cousin at the same schedule measures **0.2835** (train_acc 0.6366), so the
hint geometry underperforms the claimed arm by 2.3× and is reported as a
measured, worse arm — `experiments/experiment_20261113_b6b_ntm_arm.duckdb`.

**Metric hygiene still owed (B8):** for a regression task the trainer's
`val_acc` is 0.0 by construction (argmax over a one-wide head) and `val_ppl` is
exp(MSE). Neither is a claim metric — `val_mae` comes from the task's own
`evaluate` — but both are numbers in the payload with no ruler. B8 owns that
row.

**B8 settled that row.** `val_acc` is now the *declared* 0.0 regression
sentinel, not a by-product: `core.losses.accuracy_tensor` is the one accuracy
rule, a floating-point target returns 0.0 without an argmax, and every loss
site and the trainer's validation call it. The claim metrics remain the task's
own (`val_loss`, `val_mae`, `val_ppl`), and the objective registry says which
name reads which key.

**Defects found in B7–B10.**

1. **A multi-column regression target crashed every loss site.** `_accuracy`
   compared `argmax(logits)` against the full `[B, C]` target, so a 3-output
   scientific regression raised `size of tensor a (32) must match tensor b (3)`
   in both the pipeline and `SystemTrainer.validate`. The rule now lives in
   `core.losses.accuracy_tensor` and returns the 0.0 sentinel for a float
   target; classification accuracy is unchanged.
2. **The objective mapping and the objective registry were different sets.**
   `MEASURED_OBJECTIVES` named 51 objectives, the registry registered 48, and
   15 mapped names had no row, so `objective_metric("accuracy")` raised for a
   name the mapping claimed. 15 rows are now registered; 9 unmeasured rows name
   the measurement they need; the sets are equal (54). Four derived metrics are
   emitted (`training_time`, `convergence_steps`, `generalization_gap`,
   `stability_plasticity_ratio`). Two task rows carried a second key for a
   measured objective (`perplexity`) — they now point at `val_ppl`.
3. **`f1_score` and `bleu_score` were declared by 12 task rows and emitted by
   none.** Both are retired from the task rows with the missing measurement
   named (no prediction surface; no text generation). The unmeasured report
   drops from 15 rows to 2 (the deferred continual pair).
4. **`NcaGeometry` ignored its substrate argument.** B5 found it; B10 fixed it
   by routing the cell MLP and readout through `_substrate_linear` and threading
   the substrate through `step`/`rollout`/`route`/`forward_with_intermediates`.
   Re-measured: 6 non-complex NCA arms differ from digital.
5. **The complex substrate's operator is the digital matmul on real weights.**
   `(a+bi)(c+di)` with real `w` is `ac`; feedforward and NCA are bit-identical.
   279 stored complex cells cannot count as substrate breadth. The row
   `complex_substrate_real_compute` declares it; the NTM half of the old row is
   kept as `ntm_substrate_inert` with the stock-LSTM reason.
6. **The S5 stage carried a third `_references_params` copy** that ignored
   `output_dim`; S5 now imports the dsl traversal, and the two NCA voids are a
   projection of `NCA_CELL_MODE_CREDITS` rather than two hand-written pairs.

**Breadth arms (only after the three above close):**

| Domain | Task | Ruler | Target |
|---|---|---|---|
| vision (breadth) | `cifar10` (conv, 9 cells) | 10 classes, majority printed | pre-register from the reference arm, ≥ chance × 5 |
| RL (breadth) | `cartpole` (14 cells) | random-policy mean_reward | above random by >1 σ, 20 eval episodes |

**Acceptance per ticket:** a number with its ruler and pre-registration, met or
marginal — a task that already has 9+ cells is not "exploratory", and a claim
within 1 σ of its threshold is marginal, not met.

### B7 — Scientific domain

**Result (2026-11-13, closed):** `pendulum_state` is registered — an offline
Euler pendulum loader inside `ScientificTask` (`sin θ, cos θ, ω` →
next state, 5,000 rows, 80/20 split) with a feedforward geometry hint and an MSE
primary objective. The registry row matches the loader ((3,) → 3, batch 32,
domain SCIENTIFIC); `_primary_domain_metric_key` maps SCIENTIFIC to `mse`.

Ruler, from `scripts/probes/b7_pendulum_state_ruler.py` on the measured split
(n = 1,000): identity/persistence **0.04302 ± 0.00088** (SE); zero 1.33135,
val-mean 1.33123, sin/cos-only 1.00040. The ODE is deterministic and the input
determines the next state, so the noise floor is 0; the threshold is derived
from the ruler.

Claim (`configs/preregistrations/b7_scientific_pendulum_state_mse.json`,
threshold 0.010): arm `digital/feedforward/instantaneous/null/gradient/adam` at
L2 (5 seeds × 20 epochs) in `experiments/experiment_20261113_b7.duckdb`, 8 s per
seed, 6 PASS records, claim-eligible cells **1**. val_loss **1.7574e-5 ±
1.2386e-6** (SE), one-sided 95% upper bound **2.02e-5** — 568× below the
threshold, **2,448× below the identity ruler**, every seed PASS.

Bucket: the 4.3×-below-ruler threshold (0.010) is deliberately far above the
measured mean because it was derived before the confirmatory run; the margin is
reported, not used to re-pick the threshold. `val_acc` on this task is the
declared 0.0 regression sentinel (B8), so the claim metric is `val_loss`.

Lock: `tests/property/test_scientific_task_lock.py` (4 tests: the task is
supported and resolves, the registry row matches the loader, a float target
returns the 0.0 sentinel while class targets still score, and the registration
brackets its ruler and floor). 4 passed.

### B8 — Measurement breadth

**Result (2026-11-13, closed):** the two surfaces now name one set. Fifteen
mapped names had no `OBJECTIVES_REGISTRY` row (`accuracy`, `mean_reward`,
`std_reward`, `mean_length`, `energy_per_op`, `free_energy_final`,
`nonlinearity_error`, `settle_steps_used`, `synaptic_ops_per_sample`,
`thermal_noise_variance`, `val_acc_ci_{lower,upper,mean,std,n_seeds}`); each is
registered with its metric key. Nine registered rows still have no measurement
and each now names the measurement it needs:

| Retired row | What would have to exist |
|---|---|
| `f1_score` | a per-sample prediction surface (task.evaluate returns accuracy/loss only) |
| `bleu_score` | a generation task (no registered task emits text) |
| `test_accuracy`, `test_loss` | an independent hold-out (every loader aliases TEST to VAL) |
| `bp_deficit`, `ruler_{walltime,energy,param}_ratio` | a discovered baseline record for the task at this hardware/budget |
| `credit_efficiency` | a credit-alignment measurement (the payload has no alignment score) |

Four measurements are derived in one place (`kernel/_metrics.derived_metrics`,
called after the post-training probes) from numbers the cell already measured:
`training_time` (walltime per epoch), `convergence_steps` (global step of the
best `val_loss`), `generalization_gap` (final `val_loss - train_loss`), and
`stability_plasticity_ratio` (`spectral_radius / psi_capacity`). `mean_length`
joins `MEASURED_METRICS` (the RL evaluator already emits it), and the two task
rows that declared a second key for a measured objective now point at `val_ppl`.

`comp coverage unmeasured` reads **2 rows** (`sequential_mnist`'s
`forgetting`/`backward_transfer`, deferred with continual evaluation), down from
15. The mapping holds 54 measured names; the registry holds the same 54.
`val_acc` for a regression target is now the declared 0.0 sentinel rather than
an accidental argmax (`core.losses.accuracy_tensor` is the one rule), which is
what made `pendulum_state` trainable at all (B7).

Lock: `tests/property/test_objective_breadth_lock.py` (5 tests: mapping ≡
registry-measured, every retired row names its missing measurement, no task
declares an unmeasured payload key, the derived metrics are derivations, and a
real cell payload carries them). 5 passed.

### B9 — Duplicate-rule cleanup

**Result (2026-11-13, closed):** `NCA_CELL_MODE_CREDITS` in
`ontology/system.py` is the one table. `SystemConfig.validate` reads it at call
time through `_validate_nca_cell_mode_credits`, and the two constraint rows are
generated from it in `seed_registries` (`nca_instantaneous_{credit}`), so a
credit added or removed there changes both surfaces at once. The S5-local
`_references_params` is deleted; S4 Gate and S5 Compose both import
`legality/dsl.references_params`, which counts `output_dim` as a
hyperparameter — so `classification_requires_classifier_head` now discriminates
the same way at both stages.

Lock: `tests/property/test_legality_single_source_lock.py` (5 tests: the
registry is a projection of the tuple, the runtime refusal message is the row's
description, monkeypatching the tuple to drop `pc_alm` makes that coordinate
validate, a legal NCA control composes, and an AST scan finds no local
traversal while `output_dim` is classified as a param rule). 5 passed.

---

### B10 — Substrate reaches NCA/NTM

**Result (2026-11-13, closed for NCA; NTM and complex are named verdicts):**
`NcaGeometry`'s cell MLP (hidden + delta) and readout run through
`_substrate_linear` → `substrate.get_forward_operator()`, threaded through
`step`, `rollout`, `route`, `forward` and `forward_with_intermediates`; the
`distill_init` path keeps the digital default (it has no substrate argument).
`NtmGeometry` is not wired: its `nn.LSTM` controller has no single-operator
form, and a manual gate rewrite would be a second forward path — the plan's own
condition for deferring it. The old row is narrowed to `ntm_substrate_inert`.

A third defect surfaced while re-measuring: the **complex substrate's operator
is the digital matmul on real weights** (`(a+bi)(c+di)` with real `w` is `ac`).
Feedforward and NCA are bit-identical on complex, so 279 stored complex cells
cannot count as substrate breadth. The row `complex_substrate_real_compute`
declares that, and it refuses every complex pair.

Re-measurement (`experiments/experiment_20261113_b10_nca.duckdb`, `digits`,
2 epochs, 1 seed, 9 records, 9 PASS):

| Substrate | train_loss | Counts as coupled |
|---|---|---|
| digital | 1.99038 | reference |
| memristive | 2.00146 | yes |
| optical | 1.99451 | yes |
| quantum | 1.99591 | yes |
| analog | 2.01361 | yes |
| ternary | 2.03621 | yes |
| sparse | 2.08250 | yes |
| complex | 1.99038 (bit-identical) | **no** — `complex_substrate_real_compute` |
| neuromorphic | not run | refused (`neuromorphic_substrate_dynamics`) |

Corpus after the sweep: **92/99 pairs hold a cell, 75 on a coordinate no rule
refuses, 24 refused, 0 undeclared**; 17 refused pairs hold 346 cells that cannot
count (11 complex pairs, 6 NTM pairs). The six non-complex NCA pairs moved into
the coupled count.

Lock: `tests/property/test_substrate_reaches_compute_lock.py` (4 tests: only
NTM is refused off digital, NCA reads the substrate while NTM still reproduces
digital, feedforward still reads it, and complex is real arithmetic with its
row). `tests/property/test_corpus_coverage_lock.py` updated to the narrowed
row. 8 passed together.

---

## 3. Success criteria for TODO90 (breadth)

| Criterion | Start | Target | Now (2026-11-13) |
|---|---|---|---|
| Axis primitives exercised or declared | **56/57** (update 11/12) | **57/57** with a PASS cell or a named row | **57/57** |
| Tasks in `SUPPORTED_TASKS` measured or retired | 22/25 | **26/26**, each measured or absent from the registry | **26/26** (B4 + B7) |
| Geometries with store-backed ≥3 error-aware credits | 8/11 | **11/11** (B2 closes the 3 probe-only) | **10/11** — graph parked (T8) |
| Substrate × geometry pairs measured or refused | 18 undeclared | **0 undeclared**, each pair a coupled cell or a named rule | **0 undeclared** — 75 coupled, 24 refused, 17 refused pairs hold 346 cells |
| Domains with one claim | 4/7 | **8/8** (language, memory, timeseries, scientific) | **8/8** — B6a/B6b/B6c/B7 at L2 with 5 seeds each |
| Acceptance locks | 3 fail | **0 fail** | **0 fail** |
| Corpus coverage instrument | probe only | **one command**, drift-locked | **one command**, locked, pairs included |
| Registered-vs-measured objectives | 12 unmeasured, 15 orphans | **0 unexplained** | **54 = 54**; 9 retired with named measurements; 2 deferred (continual) |
| Duplicate legality tables | 2 (nca homeostatic/pc_alm) | **0** | **0** — one credit table, one `references_params` |

Measured 2026-11-12 at plan start: 6,925 PASS cells over 428 stores. Measured
after B2/B3: 7,319 over 430 stores, 0 unreadable. After B4: 7,325 over 431
stores, 0 unreadable. After B5: 7,388 over 432 stores, 0 unreadable, 99
substrate × geometry pairs all accounted for. After B6a/B6c: 7,401 over 435
stores, 0 unreadable, both claims at L2 with 5 achieved seeds. After B6b: 7,409
over 437 stores, 0 unreadable. After B7/B10: **7,424 over 439 stores, 0
unreadable**, 26/26 tasks, 8/8 domain claims, 54/54 objective rows. Each row
above names the instrument that would move it, and the target is a cell, a row,
or a claim — never a count of attempted work.

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
   0.0204 vs 0.6579 majority, +1.29 SE, marginal). This is also the corpus's
   last geometry below three store-backed error-aware credits (10/11). Trigger:
   a breadth claim cites graph credit breadth, or the graph energy settle is
   needed by another ticket. Then T8's acceptance applies (n=5 × 200 epochs,
   every seed >1 σ over majority).
2. **PROTEINS 0.7040.** Marginal until a claim cites that arm; then T6's
   pre-registered paired re-measure is the trigger.
3. **A streaming copy task.** `copy_task`'s input holds the answer at a
   pad-derived index, so a positional copy scores 1.0000 and "beat
   copy-the-input" cannot be stated (B6b). The repair is a copy the input cannot
   answer: carry state across steps so the source is seen once and never again,
   or withhold the source and score recall from a query. Trigger: a claim needs
   memory *capacity* rather than memory *addressing*, or a ticket wants the 63
   existing `copy_task` cells re-pinned. Then B6b's registration is re-derived —
   `tests/property/test_copy_task_ruler_lock.py` fails on the repair and names
   the three numbers to re-measure.
4. **NTM's LSTM controller in substrate ops.** `ntm_substrate_inert` is the one
   remaining geometry-side inertness (6 refused pairs hold cells). The repair is
   a gate rewrite of `nn.LSTM` as two substrate operators with the same state
   dict and no second forward path; routing only the key/add/erase projections
   would make the loss differ without making the controller physical, so it is
   not done. Trigger: a claim needs NTM substrate breadth. Then the row is
   deleted and the 6 pairs re-measured; `test_substrate_reaches_compute_lock`
   fails on the delete.
5. **Complex arithmetic at a real-valued model.** `complex_substrate_real_compute`
   refuses 11 pairs and leaves 279 cells uncounted. The repair is a model path
   that carries complex activations (or a declared phase-noise term that changes
   a real matmul); until then the substrate's declared physics does not enter a
   real-valued cell. Trigger: a claim cites complex-substrate breadth, or a
   complex-valued geometry lands.
6. **`test_accuracy` / `test_loss` need a real hold-out.** Every loader aliases
   TEST to VAL. A three-way split re-pins every existing validation number, so
   it is a corpus-wide re-measure, not a B8 wiring row. Trigger: a claim that
   must state out-of-sample error on a new split.
7. Everything TODO89 §5 lists as NO stays NO: paper figures, publishing,
   retrospectives, cycles > 30 min, repo-wide gates outside round close.

---

## 6. Fresh-session bootstrap

```bash
# state
uv lock --check && uv run python -c "import duckdb, torch; print(duckdb.__version__, torch.__version__)"
uv run comp coverage report --corpus
# substrate breadth: cells, refused pairs, and cells on a refused pair
uv run comp coverage report --corpus | sed -n '/Substrate x Geometry/,/Per-Task/p'
uv run comp coverage unmeasured

# the acceptance gate (green since B0; ~4 min)
uv run python -m pytest tests/acceptance/test_campaign_evidence_lock.py \
  tests/acceptance/test_promotion_lock.py -q -rf --tb=line > logs/b0.log 2>&1

# breadth locks added by B6-B10 (18 tests, ~45 s)
uv run python -m pytest \
  tests/property/test_regression_target_lock.py \
  tests/property/test_copy_task_ruler_lock.py \
  tests/property/test_scientific_task_lock.py \
  tests/property/test_objective_breadth_lock.py \
  tests/property/test_legality_single_source_lock.py \
  tests/property/test_substrate_reaches_compute_lock.py \
  tests/property/test_corpus_coverage_lock.py -q --tb=line
```

The breadth queue is empty (B0–B10 closed, §3). Read `TODO89.md` §2b and this
file's §5 before spending a session; the only optional breadth spend is the two
pre-registered arms below (vision `cifar10`, RL `cartpole`), and everything else
is depth with a trigger.

**A claim needs the task's own loss.** B6c proved the pipeline could not train
a regression target until `loss_fn` was threaded from composition to every
loss site. B7 then proved a multi-column regression target crashed `_accuracy`
until that rule had one source. Before claiming a *new* task trains poorly,
compose one cell and assert the reported `loss` equals the task's metric on the
same batch (`test_pipeline_trains_a_regression_cell_with_its_own_loss` is the
pattern).

**A claim needs a ruler the arm can beat.** B6b's ticket named a ruler (copy the
input) that the task's own framing satisfies exactly, so the ruler was the
ceiling. Before registering a threshold, compute the named policy's score on the
split the cell measures; if it is 1.0 (or 0.0 on a loss), the task's framing
leaks and the ruler must be re-derived from policies that address nothing.

**A primitive that "works" may not be in the computation.** B5/B10 found a
PASS cell whose substrate never entered the forward pass. A breadth cell must
show the axis changed the number, not merely that it ran: compare the arm to
its digital counterpart at the same schedule (`train_loss` to six decimals was
the tell).
