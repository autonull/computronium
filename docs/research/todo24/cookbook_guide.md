# Cookbook Guide

The Mechanism Cookbook v1 holds certified practitioner entries. The gate
is absolute: **no campaign evidence or certified negative result, no
entry** — anything else is a recorded refusal, never an entry.

## Entry format

```text
Mechanism:
Problem class:
Constraints:
Coordinate:
Evidence:
Certificates:
Known limitations:
Deployment notes:
```

## Certifying an entry

Entries certify from promoted beliefs (the `promote_mechanism` §18-gate
pipeline) or from boundary beliefs (certified negative results via the
§19 boundary gates):

```python
from computronium_lab.research import attempt_promotion, certify_entry

belief, reason = attempt_promotion(lab, "backprop_mlp", [spec], epochs=20)
entry = certify_entry(
    belief,
    problem_class="flat_classification",
    constraints="digital, float32",
    coordinate={"credit": "bp", "update": "euclid"},
    known_limitations="saturates the quick tier; parity unmeasured",
    deployment_notes="onnx export verified; int8 transfer Δacc recorded",
)
```

`attempt_promotion` refuses without a ledger-backed Lab or when the
belief is not promoted; `certify_entry` returns a `CookbookRefusal`
with the reason. Promotion requires certified-tier campaigns
(3 seeds, task operating-point epochs, matched controls) — smoke and
quick tiers always refuse.

## Rendering

```python
from computronium_lab.research import render_cookbook

markdown = render_cookbook([entry_or_refusal, ...])
```

The rendered cookbook lists certified entries first, then refusals with
reasons, so missing evidence is visible instead of silent.
