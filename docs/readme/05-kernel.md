## 5. The Experiment Kernel

`computronium.experiment` turns a question into governed evidence:

```text
Question ──► RunSpec ──► SearchSpace ──► ProposalPolicy ──► Stages S1–S11 ──► RecordStore ──► Claims
```

- **`schema/`** — `RunSpec`, `Coordinate`, `Schedule`, and the `AXES` / `OBJECTIVES` / `PRIORS` registries (single source of truth for every axis primitive, objective, and prior).
- **`legality/`** — an expression DSL + engine; measurements are only legal where the spec says they are, identically for every policy.
- **`execution/`** — `SearchSpace`, the policy catalog, `PipelineRunner` (stages S1–S11), and `ContrastDesign` (OFAT/factorial DOE with `DataOrigin` provenance).
- **`evidence/`** — `RecordStore` (DuckDB, single-writer under a threading lock), artifacts, failure linkage, three-tier claim status, fail-closed schema versioning with a forward-tolerant `unknown` column.
- **`learning/`** — surrogates, priors, ICU model, reasoning over accumulated evidence.
- **`surface/`** — the `report`/`export`/`conformance`/`status` CLI, run profiles, conformance audit.

**Policy catalog.** Experiments differ only in proposal policy; space, measurement identity, legality, store, and claims machinery are shared:

<!-- gen:policy_table -->

`model_based` asks its Optuna study with distributions harvested from the
coordinate's own active space and is told the objective values the evaluator
measured on return. It searches **hyperparameters**; the six structural axes
come from the spec-derived cell stream, so a run tunes the cell the spec
selected rather than choosing the cell.

**Kernel status, stated plainly.** The orchestration is real and locked by
U1–U5, and so is the measurement under it: `execution/evaluate.py` composes a
coordinate into a `System`, trains it with `SystemTrainer` on the run's own
task, and records measured `train_acc`/`val_acc`/`val_loss` with a gate verdict
*derived* from what happened. A cell's hyperparameters are searched (a
`RunSpec.hyperparameters` sweep, narrowed against the harvested domain), and the
model-based policy samples the same harvested space and learns from the values
told back. Four claims are worth stating rather than leaving to be discovered:

- **The search space is the spec, not a table.** `search_space_from_spec` walks
  the registries under the spec's constraints for the spec's task, and filters
  for legality at the size the run will train. The seven hardcoded MNIST-shape
  sites are gone (`test_active_space_lock`).
- **The samplers learn over hyperparameters only.** Structural axes are
  enumerated from the spec's permitted primitives; the sampler optimizes the
  continuous/integer/categorical knobs a cell's selection activates. Deleting
  the candidate-list `propose()` signature entirely is TODO46 §3.4's remainder.
- **Four of the 36 registered objectives are measured.** `schema/metrics.py`
  declares the measured namespace, and every objective row is stamped with the
  payload key that satisfies it or the reason nothing emits one —
  `docs/generated/objectives.md` shows which. `flops`, `memory_usage` and
  `energy_per_step` are registered research targets; a run that names one is
  refused rather than optimized against a number that does not exist.
- **No campaign has been run yet.** The measured regime is real, but nothing
  here is evidence about which credit rule or topology is better on a
  scientific question. TODO46 §3.6/§3.7 is that work.

The ML library above is unaffected: the §3 and §4 blocks compose and train real
six-axis systems and assert real accuracies.

**Kernel guarantees (locked in [`tests/acceptance/test_unified_kernel.py`](tests/acceptance/test_unified_kernel.py)):**
*These lock orchestration, evidence identity and measurement: every cell they run is composed and trained by `execution/evaluate.py`.*

| ID | Guarantee |
|---|---|
| U1 | Question → `question_first()` → RunSpec → Synthesis → pipeline → store: end-to-end |
| U2 | Same RunSpec under TPE (`ModelBasedPolicy`) → identical record schema/store |
| U3 | Multi-round allocation with pause/resume by `run_id` — no re-measurement |
| U4 | Policy interchangeability: swap policy per round, same RunSpec/Space/Store |
| U5 | Cross-policy evidence reuse: one store, no migration, same legality/claims |

**Measurement identity & provenance.** Every record carries a deterministic `measurement_key` (from coordinate + schedule), full provenance (code SHA, dataset, policy), a three-tier status (gate verdict / defect cause / maturity), and a schema version. Unsupported schema versions fail closed (`UnsupportedSchemaVersionError`); fields the current schema does not model survive bumps verbatim in the `unknown` column.

**ContrastDesign.** WP18 adds design-of-experiments (OFAT/factorial) with explicit `DataOrigin` labels, so contrasted arms carry known structure rather than incidental variation.

---
