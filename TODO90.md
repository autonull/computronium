# TODO90 — Breadth, not depth (Successor to TODO89)

**Status:** 2026-11-12 · base `e1243ed9` · **B0–B4 closed** · next B5. TODO89 is
closed: T1–T10 carry measured numbers, and its remaining work is two depth items
(graph third credit, PROTEINS 0.7040), parked here with explicit triggers.

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

## Progress ledger

Session 2026-11-12 (second): B0–B3 closed. Session 2026-11-12 (third): B4
closed. Every row names its instrument.

| # | Ticket | Result | Evidence |
|---|---|---|---|
| B0 | Acceptance repair | **Green.** f2 reads its objective through `objective_metric`, not a literal; promotion earns L1 (maturity starts at L0, the ladder writes L1, `maturation`/`deep_tier` gate L2); `Promoted:` counts matured records. 13 passed, 0 failed. | `tests/acceptance/test_campaign_evidence_lock.py`, `test_promotion_lock.py`; `evaluate.py::_device_lock` |
| B1 | Corpus coverage | **Green.** `comp coverage report --corpus` reads 428 stores and prints the probe's numbers; unreadable stores are named. | `computronium/experiment/evidence/corpus.py`, `tests/property/test_corpus_coverage_lock.py` |
| B2 | Store-backed breadth | **Green.** nca 3, attention 3, spatial_lattice 3 from stores; each arm 3 seeds × 20 epochs on digits, task `digits` on every record. Rule narrowed: the stale gradient void now names only `tile`. | `experiments/experiment_20261112_b2.duckdb`; `seed_registries.py` |
| B3 | `role_split` | **Green.** Declared default (muon-on-readout + Euclidean elsewhere); 10 PASS cells across feedforward and conv. Update axis 12/12 measured. | `ontology/update/__init__.py`, `tests/property/test_role_split_update.py`, `experiments/experiment_20261112_b3.duckdb` |
| B4 | Three untouched tasks | **Green.** `kmnist` 0.6669 val_acc (chance/majority 0.100), `char_ngram` 3.9923 ppl (unigram 25.21), `tiny_shakespeare` 8.4394 ppl (unigram 27.19); 1 seed each, 2 PASS records per task. Corpus task list holds no `NOT TOUCHED` row. | `experiments/experiment_20261112_b4.duckdb`; `tests/property/test_lm_target_alignment_lock.py` |

**Defect found in B0 and fixed with B0:** one CUDA device ran four cells and
three seeds concurrently, corrupting Inductor's static Triton launcher
(`CUDA_ERROR_INVALID_HANDLE`, `load_kernel() must be called before run()`) and
cuSOLVER's QR wrapper (`lazy wrapper should be called at most once`). One
process-wide per-device lock in `evaluate_cell` serializes CUDA training; the
campaign went from 15 failed records to 0, and walltime measures the cell rather
than contention. CPU evaluation still runs concurrently.

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

| Surface | At plan start | Now |
|---|---|---|
| Axis primitives exercised or declared | 56/57 (update 11/12) | **57/57** (update 12/12) |
| Geometries with store-backed ≥3 error-aware credits | 8/11 | **10/11** — graph has 2; T8's third credit is parked (marginal, not met) |
| Acceptance locks | 3 fail | **0 fail** |
| Corpus coverage instrument | probe only | **one command**, drift-locked |
| Tasks measured or retired | 22/25 | **25/25** — every registered task is measured |
| Domains with one claim | 4/7 | 4/7 — B6 remains |
| Registered-vs-measured objectives | 12 unmeasured, 15 orphans | unchanged — B8 |
| Duplicate legality tables | 2 | unchanged — B9 |

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

**Progress (2026-11-12):** B0, B1, B2, B3 and B4 are closed with the results in
§0a; **B5 is the next ticket**. B5's start narrowed (graph off `digital`; nca ×
`complex`/`neuromorphic`) because B2 closed the three probe-only credit counts.
B6–B9 are unchanged.

**B5 start state (2026-11-12):** four coordinates, each one cell with
`--epochs 2 --n-seeds 1 --device cuda` and all six axes pinned, as B4 did:
`graph × ternary`, `graph × sparse` (task `cora`, arm
`graph/instantaneous/null/gradient/adam`), `nca × complex`, `nca ×
neuromorphic` (task `digits`, arm `nca/instantaneous/null/gradient/adam`).
A tuple that refuses composes nothing; then it needs a `VOID` row whose
`unavailable_reason` is the measured failure — not a silent prune. Substrate
and geometry are the only axes that change: keep the credit error-aware so a
PASS cell also counts toward the ≥3-credits-per-geometry row.

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

| Criterion | Start | Target | Now (2026-11-12) |
|---|---|---|---|
| Axis primitives exercised or declared | **56/57** (update 11/12) | **57/57** with a PASS cell or a named row | **57/57** |
| Tasks in `SUPPORTED_TASKS` measured or retired | 22/25 | **25/25**, each measured or absent from the registry | **25/25** (B4) |
| Geometries with store-backed ≥3 error-aware credits | 8/11 | **11/11** (B2 closes the 3 probe-only) | **10/11** — graph parked (T8) |
| Domains with one claim | 4/7 | **7/7** (language, memory, timeseries close the gap) | 4/7 |
| Acceptance locks | 3 fail | **0 fail** | **0 fail** |
| Corpus coverage instrument | probe only | **one command**, drift-locked | **one command**, locked |
| Registered-vs-measured objectives | 12 unmeasured, 15 orphans | **0 unexplained** | 12 / 15 |
| Duplicate legality tables | 2 (nca homeostatic/pc_alm) | **0** | 2 |

Measured 2026-11-12 at plan start: 6,925 PASS cells over 428 stores. Measured
after B2/B3: 7,319 over 430 stores, 0 unreadable. After B4: 7,325 over 431
stores, 0 unreadable. Each row above names the
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

# the gate B0 repaired (green 2026-11-12)
uv run python -m pytest tests/acceptance/test_campaign_evidence_lock.py \
  tests/acceptance/test_promotion_lock.py -q -rf --tb=line > logs/b0.log 2>&1
```

Read `TODO89.md` §2b before choosing a ticket; it owns the measured surface.
B0–B4 are green (see §0a). **Start at B5**; B6–B9 remain. B2's rule
narrowing means B5 keeps only its substrate × geometry holes: graph off
`digital` and nca × `complex`/`neuromorphic`.
