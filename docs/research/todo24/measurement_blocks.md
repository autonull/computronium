# Measurement-Block Ledger Guide

A measurement block is a blocked or impossible *measurement* — recorded
as a lab `measurement_block` artifact with `missing` evidence and
mandatory explanatory notes. It is never a CEEC boundary belief (a
negative claim that passed the §19 boundary gates); the two live in
different compartments.

## Recording a block

```python
from computronium_lab.research import MeasurementBlock

block = MeasurementBlock(
    problem_class="sequence_parity",
    mechanism="ff_mlp",
    reason="at-chance ceiling at the recorded budget",
    detail="recorded TODO23 limitation, not a budget problem",
)
evidence_id = block.record(store, scope)
```

Corpus runners, benchmarks, and transfer campaigns file blocks
automatically when arms fail: unconstructible rows, export failures,
and non-constructible controls all land here with the exception type
and reason.

## Reading the ledger

Blocks aggregate into the failure manifesto alongside failed
candidates, failed mutations, and failed transfers:

```python
from computronium_lab.research import build_failure_manifesto

manifesto = build_failure_manifesto(
    evolution_reports=[report],
    corpus_reports=[corpus],
    transfer_reports=[transfer],
)
```

Every block carries `problem_class`, `mechanism`, `reason`, `tier`,
and `detail` — future work inherits institutional memory instead of
rediscovering dead ends.
