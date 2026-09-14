# Research Corpus Guide

The Certified Research Corpus v1 is a persistent, statistically
disciplined basis of problem classes, campaigns, controls, frontiers,
and measurement blocks.

## Problem classes

| Class | Basis | Arms |
|---|---|---|
| `flat_classification` | calibrated gaussian-blob quick tier | catalog mechanisms + `::permuted` controls |
| `sequence_last_symbol` | `sequence_task("last_symbol")` | catalog mechanisms + `::shuffled` controls |
| `sequence_threshold` | `sequence_task("threshold")` | same |
| `sequence_parity` | `sequence_task("parity")` | same (at chance at recorded budgets — recorded, never forced) |
| `nca_state_prediction` | `grid_transition_task` | catalog mechanisms + `::shuffled` controls |
| `continual_switch` | `Lab.adapt` ψ runtime | ψ modes + frozen/θ controls |
| `substrate_transfer` | deployment layer | digital/int8/ternary/memristive targets |

## Running a measurement

```python
from computronium_lab import Lab
from computronium_lab.research import BudgetTier, MeasurementRunner

lab = Lab(record_ledger="scratch/todo24.sqlite3")
runner = MeasurementRunner(lab, tier=BudgetTier.QUICK)
report = runner.run(
    "flat_classification",
    ("backprop_mlp", "ff_mlp"),
    seeds=(0, 1, 2),
    epochs=20,
    run_id="corpus-v1",
)
```

Every run writes per-seed `manifest.json` files under
`results/todo24/<problem_class>/<seed>/<timestamp>/`, records a
`research_corpus_summary` artifact with per-seed vector evidence and
bootstrap-CI `Derived` statistics, appends measured points to the
frontier archive, and files failures as measurement blocks.

## Re-measuring the catalog

```python
from computronium_lab.research import remeasure_catalog

reports = remeasure_catalog(
    lab,
    ["flat_classification", "sequence_last_symbol"],
    seeds=(0, 1, 2),
    epochs=20,
)
```

Rows without a valid construction path for a class fail into measurement
blocks — the corpus records them, never forces them.

## Statistics

Summaries are built on `computronium.validation.statistics` (bootstrap
percentile CI, permutation paired tests): mean, std, CI, paired p, and
effect size per arm. Certified claims additionally require the CEEC §18
gate family via `promote_mechanism` — never smoke-tier results.

## Adding a problem class, objective, or curriculum

New entries plug in through public registries — no core edits:

```python
from computronium_lab import (
    CurriculumSpec,
    register_curriculum,
    register_objective,
    register_problem_class,
)
from computronium_lab.research import objective_names, problem_class_defaults

class MyClass:
    name = "my_task"

    def __init__(self, spec):
        self.spec = spec

    def generate_task(self, seed: int) -> object: ...
    def default_metrics(self) -> tuple[str, ...]: ...
    def run_arm(self, lab, arm: str, seed: int, *, epochs: int) -> dict[str, float]: ...
    def control_arm(self, arm: str) -> str | None: ...

register_problem_class(
    "my_task", MyClass, task="my_task", dataset="my_data",
    input_dim=8, num_classes=2,
)
register_objective("my_metric", pareto_field="my_metric", maximize=True)
register_curriculum(CurriculumSpec(name="my_switch", max_episodes=10))

assert "my_metric" in objective_names()
assert problem_class_defaults("my_task")["dataset"] == "my_data"
```

The factory receives the `ProblemSpec` the runner builds from the
registered task/dataset/dims; statistical summaries, frontier appends,
and measurement blocks consume the new class generically.
