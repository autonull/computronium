# Experiment Pre-Registration Policy

An experiment must be fully pre-registered (status `pre_registered`) before execution. Required fields:

- `id` (`X-` prefix), `question`, `rationale`
- `scope` (structured, explicit)
- `target_beliefs`, `target_goals`
- `design`
- `prediction` plus `prediction_probability` (interval preferred, point allowed with declared method)
- `controls` (matched controls for positive claims; justification required if absent)
- `metrics`
- `budget` (`quick | standard | nightly`) and `cost_estimate`
- `falsification_criterion`, `overturn_criterion`
- `hard_gates`

## Controls policy

Positive claims require matched controls (matched norm/compute/seeds). Missing controls require explicit justification recorded at pre-registration; the hard constraint `controls_present_or_justified` is checked before scoring.

## Prediction probability policy

Every prediction that will feed a calibration record must carry an explicit probability (interval preferred). The declared method is stored.

## Falsification criterion style

Concrete, observable, and tied to the metrics: e.g. "No consistent improvement across 3 seeds, or improvement disappears after norm matching."

## Overturn criterion style

States what result would reopen a boundary belief: e.g. "A new mechanism raises rescue probability above 0.10 with defect-free evidence."

## Status flow

`draft → pre_registered → running → completed | failed(inert|missing)`. Only `pre_registered` experiments may execute; only completed experiments may feed belief revisions.
