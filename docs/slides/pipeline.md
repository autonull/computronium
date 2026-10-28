# From Question to Governed Evidence

```python
from computronium.experiment.schema.seed_registries import seed_all_registries
from computronium.experiment.surface.profiles import question_first

seed_all_registries()
spec = question_first(
    "validation_accuracy", "mnist",
    {"budget_seconds": 600, "fidelity": "L1", "n_seeds": 3},
)
```

`spec` is a `RunSpec`: the objective, the declared operating point, and the canonical stage list. No hidden default escapes into a result.

## <!-- gen:stage_count --> stages, none skippable

- **S1–S4 define** — frame the question, generate the search space, schedule fidelities, gate legality.
- **S5–S8 execute** — compose the coordinate, train at increasing fidelity, measure, record.
- **S9–S11 judge** — attribute variance, decide promotion, report.

<!-- include: diagrams/pipeline.svg -->

Every run writes one record (<!-- gen:record_field_count --> fields, schema v<!-- gen:schema_version -->) to an append-only DuckDB ledger through <!-- gen:store_method_count --> store methods. No silent drops, no lost seeds.

<!-- notes -->
The code is the whole entry point: an objective, a task, an operating point. The operating point is the fairness contract made executable — budget, fidelity, seed count are declared before a number exists.

Stress S4: the legality gate rejects a coordinate that the ontology does not compose, which is where most "surprising" results would have been caught. S8 is append-only so a failed seed stays in the record.
<!-- /notes -->
