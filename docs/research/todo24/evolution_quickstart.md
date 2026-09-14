# TODO24 Evolution Quickstart

Budgeted evolutionary search over existing 6-axis mechanism coordinates.
Evolution proposes; campaigns dispose; only certified mechanisms become
recommendations.

```python
from computronium_lab import (
    Constraints,
    EvolutionBudget,
    EvolutionSpec,
    Lab,
)

lab = Lab(record_ledger="scratch/todo24.sqlite3")

spec = lab.specify(
    task="flat_classification",
    dataset="gaussian_blob",
    constraints=Constraints(
        compute_budget="cpu_quick",
        latency_ms=50,
        memory_gb=2,
        continual=True,
        local_credit=False,
        precision="float32",
        substrate="digital",
    ),
    objectives=("accuracy", "adaptation_speed", "stability"),
)

plan = lab.plan_evolution(
    spec,
    EvolutionSpec(
        population=6,
        generations=3,
        seed_candidates=(
            "backprop_mlp",
            "temporal_psi_task_switcher",
            "role_split_muon_readout",
            "ntm_classifier",
        ),
        objectives=("accuracy", "adaptation_speed", "stability"),
        budget=EvolutionBudget(
            max_campaigns=12,
            max_epochs_per_campaign=20,
            max_seeds=3,
        ),
    ),
)

report = lab.run_evolution(plan)

report.best_candidates
report.frontier_archive
report.lineage
report.negative_results
report.cookbook_entries
```

Notes:

- `plan_evolution` is a dry run: genomes, constitutional checks, expected
  budgets — no training.
- Seed candidates must be catalog rows (`role_split_mlp` does not exist;
  the row is `role_split_muon_readout`).
- Budget tiers: `EvolutionBudget.smoke()` / `.quick()` / `.certified()`.
  Only `certified` supports cookbook entries or belief promotion.
- Every generation pre-registers as a ceec `Experiment`; candidate
  selection runs the §22 loop scoped to the generation.
- Measured Pareto points persist in
  `data/research/todo24/frontier/<spec>.json` and can re-enter synthesis
  via `lab.synthesize(spec, include_evolved=True)`.
