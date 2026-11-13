# TODO90 — Breadth, not depth (Successor to TODO89)

**Status:** 2026-11-13 · base `85f62aa3` · **B0–B5, B6a, B6c closed** · next
B6b. TODO89 is closed: T1–T10 carry measured numbers, and its remaining work is
two depth items (graph third credit, PROTEINS 0.7040), parked here with
explicit triggers.

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
the timeseries arm could not run at all until three defects were fixed. Every
row names its instrument.

| # | Ticket | Result | Evidence |
|---|---|---|---|
| B0 | Acceptance repair | **Green.** f2 reads its objective through `objective_metric`, not a literal; promotion earns L1 (maturity starts at L0, the ladder writes L1, `maturation`/`deep_tier` gate L2); `Promoted:` counts matured records. 13 passed, 0 failed. | `tests/acceptance/test_campaign_evidence_lock.py`, `test_promotion_lock.py`; `evaluate.py::_device_lock` |
| B1 | Corpus coverage | **Green.** `comp coverage report --corpus` reads 428 stores and prints the probe's numbers; unreadable stores are named. | `computronium/experiment/evidence/corpus.py`, `tests/property/test_corpus_coverage_lock.py` |
| B2 | Store-backed breadth | **Green.** nca 3, attention 3, spatial_lattice 3 from stores; each arm 3 seeds × 20 epochs on digits, task `digits` on every record. Rule narrowed: the stale gradient void now names only `tile`. | `experiments/experiment_20261112_b2.duckdb`; `seed_registries.py` |
| B3 | `role_split` | **Green.** Declared default (muon-on-readout + Euclidean elsewhere); 10 PASS cells across feedforward and conv. Update axis 12/12 measured. | `ontology/update/__init__.py`, `tests/property/test_role_split_update.py`, `experiments/experiment_20261112_b3.duckdb` |
| B4 | Three untouched tasks | **Green.** `kmnist` 0.6669 val_acc (chance/majority 0.100), `char_ngram` 3.9923 ppl (unigram 25.21), `tiny_shakespeare` 8.4394 ppl (unigram 27.19); 1 seed each, 2 PASS records per task. Corpus task list holds no `NOT TOUCHED` row. | `experiments/experiment_20261112_b4.duckdb`; `tests/property/test_lm_target_alignment_lock.py` |
| B5 | Substrate × geometry holes | **Green, with one defect named.** 32 runs, 63 PASS records, 0 fail. The pair instrument closed **18 undeclared pairs** (68 measured → 92; 60 coupled → 78) and refused 21 (14 hold 192 cells that cannot count). 0 undeclared remain. | `experiments/experiment_20261113_b5.duckdb`; `evidence/corpus.py`; `tests/property/test_corpus_coverage_lock.py`, `test_substrate_reaches_compute_lock.py` |
| B6a | Language claim | **Met.** `char_ngram` at L2 (5 seeds × 20 epochs, all PASS): val_ppl **2.4617 ± 0.0338** (SE), one-sided 95% upper bound **2.5337**, against a **5.0** threshold and a **23.77** unigram ruler on the same 1,024-item split — **9.66× below the ruler**, 75 SE clear of the threshold. claim-eligible cells **1**. | `experiments/experiment_20261113_b6a.duckdb`; `configs/preregistrations/b6a_language_char_ngram_ppl.json` |
| B6c | Timeseries claim | **Met, after three defects were fixed** (see below). `synthetic_forecast` at L2 (5 seeds × 20 epochs, all PASS): val_mae **0.08904 ± 0.00117** (SE), upper bound **0.09153**, against a **0.100** threshold, the **0.11459** naive last-value ruler and the **0.07979** noise floor — **1.287× below naive**, 73.4% of the 0.0348 headroom removed, 8.7 combined SE of separation. claim-eligible cells **1**. | `experiments/experiment_20261113_b6c.duckdb`; `configs/preregistrations/b6c_timeseries_synthetic_forecast_mae.json`; `tests/property/test_regression_target_lock.py` |

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

| Surface | At plan start | Now |
|---|---|---|
| Axis primitives exercised or declared | 56/57 (update 11/12) | **57/57** (update 12/12) |
| Geometries with store-backed ≥3 error-aware credits | 8/11 | **10/11** — graph has 2; T8's third credit is parked (marginal, not met) |
| Acceptance locks | 3 fail | **0 fail** |
| Corpus coverage instrument | probe only | **one command**, drift-locked, with a substrate × geometry pair section |
| Tasks measured or retired | 22/25 | **25/25** — every registered task is measured |
| Substrate × geometry pairs | 20 holes, 4 named by the plan | **92/99 hold a cell; 78 substrate-coupled; 21 refused; 0 holes** |
| Domains with one claim | 4/7 | **6/7** — language (B6a) and timeseries (B6c) closed; memory is B6b |
| Registered-vs-measured objectives | 12 unmeasured, 15 orphans | unchanged — B8 |
| Duplicate legality tables | 2 | 2 (plus a third `references_params` copy, §2 B9) |

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
| B6b | **Memory claim** | `copy_task` token accuracy over the copy-the-input baseline | 1 h | **open — next** |
| B6c | **Timeseries claim** | `synthetic_forecast` MAE over the naive last-value ruler | 1 h | **closed, met** |
| B7 | **Scientific domain** | one registered task with a loader and a cell, or a named retirement | 1 h | open |
| B8 | **Measurement breadth** | wire the cheap objectives; retire or register the orphan keys | 1–2 h | open |
| B9 | **Duplicate-rule cleanup** | nca `homeostatic`/`pc_alm` voids live in one table | 30 min | open |
| B10 | **Substrate reaches NCA/NTM** | thread the substrate operator through `NcaGeometry` and `NtmGeometry`, then re-measure 14 pairs | 2 h | open |

A session takes **B0–B2 first** unless they are already green. They are the
instrument; every later ticket's evidence depends on them.

**Progress (2026-11-13, second session):** B0, B1, B2, B3, B4, B5, **B6a and
B6c** are closed with the results in §0a; **B6b is the next ticket**, and it is
the only breadth item between the plan and its 7/7 domain target. B5 widened
under its own instrument: the plan named four coordinates, the pair section of
`comp coverage` named 20, and the sweep found that 14 pairs already held cells
which cannot count (B10). B6c widened the same way: a ticket whose whole
deliverable was one ruler needed three pipeline fixes before the ruler could be
computed (see §0a). B7, B8 and B9 are unchanged.

**B6b start state (2026-11-13, second session):** `copy_task` holds 55 PASS
cells, so the task trains; what is missing is the *ruler*, not the cell. Its
registry row declares `input_shape=(10,)`, `output_dim=2`,
`primary_objective="validation_accuracy"`, `geometry_hint="ntm"`, and the plan
registers a "copy-the-input baseline (token accuracy)". Before running:
1. Measure the baseline on the same val split the cell measures (copy the input
   one step, and all-zero, and report both — the trivial policy that beats
   "copy" is not the same one that beats "zero").
2. Read the 55 existing cells' `val_acc` distribution: if they straddle the
   baseline, the claim's schedule is the issue and the ticket is a schedule
   choice, not a new arm.
3. Pre-register, then run 5 seeds at L2 (the ladder default 5 × 20) with the
   `ntm` geometry and the credit that geometry accepts. `ntm` is inert w.r.t.
   substrate (B10) but it does train, so a digital claim is unaffected by B10.

**B6a/B6c start states are closed** and kept in §2 only for their measured
numbers and their defect list.

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
| B6b | memory | `copy_task` | copy-the-input baseline (token accuracy) | threshold on token accuracy, ≥3 seeds — **open, next** |
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

**Metric hygiene still owed (B8):** for a regression task the trainer's
`val_acc` is 0.0 by construction (argmax over a one-wide head) and `val_ppl` is
exp(MSE). Neither is a claim metric — `val_mae` comes from the task's own
`evaluate` — but both are numbers in the payload with no ruler. B8 owns that
row.

**Breadth arms (only after the three above close):**

| Domain | Task | Ruler | Target |
|---|---|---|---|
| vision (breadth) | `cifar10` (conv, 9 cells) | 10 classes, majority printed | pre-register from the reference arm, ≥ chance × 5 |
| RL (breadth) | `cartpole` (14 cells) | random-policy mean_reward | above random by >1 σ, 20 eval episodes |

**Acceptance per ticket:** a number with its ruler and pre-registration, met or
marginal — a task that already has 9+ cells is not "exploratory", and a claim
within 1 σ of its threshold is marginal, not met.

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

**Third copy found 2026-11-13 (B5):** `execution/stages_impl.py:636` defines a
local `_references_params` that differs from `legality/dsl.py`'s: it matches
only `params.*`, not `output_dim`. S4 Gate skips
`classification_requires_classifier_head` (which reads `output_dim`) as a
param rule, and S5 Compose's copy also skips it — so that constraint is enforced
by neither stage. The dsl helper is the one source now; S5 should import it and
the rule will land at compose time, where `output_dim` is known.

**Deliverable:** one table. Make `validate` consult the declared rows (or delete
the methods and route every legality check through composition). A lock deletes
the registry row and proves the coordinate is refused with that row's reason —
the same mechanism lock T7 uses.

**Acceptance:** one source per rule; the lock fails if a second copy returns.

---

### B10 — Substrate reaches NCA/NTM

**Start:** `NcaGeometry.forward` and `NtmGeometry.forward` accept a `substrate`
argument and never use it; the pair instrument refuses their 14 non-digital
pairs (`nca_ntm_substrate_inert`) and lists the 192 cells that cannot count.
The evidence is identical `train_loss` to six decimals across substrates
(`experiments/experiment_20261113_b5.duckdb`), while `conv`/`attention`/
`spatial_lattice`/`graph` change with the substrate as they should.

**Deliverable:** route NCA's cell MLP and readout through
`substrate.get_forward_operator()`, threading the substrate through `step`,
`rollout` and the settle path that calls them; do NTM only if the LSTM
controller can be written in substrate ops without a second forward path. Then
delete `nca_ntm_substrate_inert`, re-run the 14 pairs, and confirm the
`train_loss` now differs from digital.

**Acceptance:** `tests/property/test_substrate_reaches_compute_lock.py` asserts
the pair is refused **and** the geometry reproduces digital — the lock flips
with the fix, so the row cannot outlive the defect. A re-measured pair carries a
cell whose `train_loss` differs from the digital arm, and the corpus pair
section counts it as coupled.

---

## 3. Success criteria for TODO90 (breadth)

| Criterion | Start | Target | Now (2026-11-13) |
|---|---|---|---|
| Axis primitives exercised or declared | **56/57** (update 11/12) | **57/57** with a PASS cell or a named row | **57/57** |
| Tasks in `SUPPORTED_TASKS` measured or retired | 22/25 | **25/25**, each measured or absent from the registry | **25/25** (B4) |
| Geometries with store-backed ≥3 error-aware credits | 8/11 | **11/11** (B2 closes the 3 probe-only) | **10/11** — graph parked (T8) |
| Substrate × geometry pairs measured or refused | 18 undeclared | **0 undeclared**, each pair a coupled cell or a named rule | **0 undeclared** — 78 on a coupled cell, 21 refused (14 await B10) |
| Domains with one claim | 4/7 | **7/7** (language, memory, timeseries close the gap) | **6/7** — language (B6a) and timeseries (B6c) closed; memory is B6b |
| Acceptance locks | 3 fail | **0 fail** | **0 fail** |
| Corpus coverage instrument | probe only | **one command**, drift-locked | **one command**, locked, pairs included |
| Registered-vs-measured objectives | 12 unmeasured, 15 orphans | **0 unexplained** | 12 / 15 |
| Duplicate legality tables | 2 (nca homeostatic/pc_alm) | **0** | 2 (+ the S5 `references_params` copy) |

Measured 2026-11-12 at plan start: 6,925 PASS cells over 428 stores. Measured
after B2/B3: 7,319 over 430 stores, 0 unreadable. After B4: 7,325 over 431
stores, 0 unreadable. After B5: 7,388 over 432 stores, 0 unreadable, 99
substrate × geometry pairs all accounted for. After B6a/B6c: 7,401 over 435
stores, 0 unreadable, both claims at L2 with 5 achieved seeds. Each row above
names the instrument that would move it, and the target is a cell, a row, or a
claim — never a count of attempted work.

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
3. Everything TODO89 §5 lists as NO stays NO: paper figures, publishing,
   retrospectives, cycles > 30 min, repo-wide gates outside round close.

---

## 6. Fresh-session bootstrap

```bash
# state
uv lock --check && uv run python -c "import duckdb, torch; print(duckdb.__version__, torch.__version__)"
uv run python scripts/probes/t3_credit_breadth.py | tail -40
uv run comp coverage report --corpus
# substrate breadth: cells, refused pairs, and cells on a refused pair
uv run comp coverage report --corpus | sed -n '/Substrate x Geometry/,/Per-Task/p'

# the gate B0 repaired (green 2026-11-12)
uv run python -m pytest tests/acceptance/test_campaign_evidence_lock.py \
  tests/acceptance/test_promotion_lock.py -q -rf --tb=line > logs/b0.log 2>&1

# the lock B6c added: a regression target is a value, not a class index
uv run python -m pytest tests/property/test_regression_target_lock.py -q --tb=line
```

Read `TODO89.md` §2b before choosing a ticket; it owns the measured surface.
B0–B5, B6a and B6c are green (see §0a). **Start at B6b** (`copy_task`); B7, B8,
B9, B10 and the two breadth arms remain. B5's pair section is the
substrate-breadth instrument: read
`comp coverage report --corpus | sed -n '/Substrate x Geometry/,/Per-Task/p'`
to see every pair that holds a cell, every pair a rule refuses, and every
cell on a refused pair that cannot count.

**A claim needs the task's own loss.** B6c proved the pipeline could not train
a regression target until `loss_fn` was threaded from composition to every
loss site. Before claiming a *new* task trains poorly, check that its
`compute_loss` reaches the pipeline: compose one cell and assert the reported
`loss` equals the task's metric on the same batch
(`test_pipeline_trains_a_regression_cell_with_its_own_loss` is the pattern).

**Do not take B10 before B6b.** B10 is depth on one geometry family; B6 gives
the last domain its first claim, which is what the breadth mission asks for.
B10's trigger is a claim that cites substrate breadth for nca or ntm.
