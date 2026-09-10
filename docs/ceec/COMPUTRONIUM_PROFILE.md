# Computronium CEEC Profile

Normative binding of CEEC-Core v1.0 to Computronium (TODO19 Epistemic Foundry).

## Thresholds

| Gate | Condition |
|---|---|
| Promotion | `probability_low >= 0.95` |
| Boundary | `rescue_probability_high <= 0.05` |
| Reopen trigger | estimated rescue probability `> 0.10` |

Interval probabilities are preferred; promotion requires the interval low bound to clear the threshold.

## Probability policy

- Point probabilities allowed; intervals preferred.
- `posterior_method` declaration is mandatory on every belief revision with a non-open status.
- Early Foundry work uses `heuristic_interval_based_on_gate_evidence` unless a calibrated posterior method exists.

## Cost model

```
Cost(x) = walltime + 0.25 * memory + 0.5 * human_review + 0.05 * storage   (normalized units)
Score(x) = ExpectedValue(x) / Cost(x)^gamma,  gamma = 1.0
```

The estimator is simple and documented here; it must not be tuned post hoc to justify a selection already made (decisions are append-only and auditable).

## Hard constraints (non-waivable)

`coordinate_valid`, `pre_registration_complete`, `no_quarantined_dependencies`,
`budget_within_limit`, `controls_present_or_justified`, `seed_plan_present`,
`evaluation_policy_present`, `structured_evidence_plan_present`,
`instrument_valid_for_claim`, `frozen_theta_audit_for_psi_only_claims`,
`identity_card_for_new_primitive`.

No override, manual or score-based, may bypass a hard constraint.

## Evidence kinds

`scalar`, `interval`, `vector`, `tensor`, `curve`, `event`, `distribution`, `frontier`, `inert`, `missing`.

Special rule: invalid coordinates produce `inert` evidence — never negative capability evidence. Infrastructure failures produce `missing`.

## Verification levels

| Level | Meaning | CEEC interpretation |
|---|---|---|
| 1 | analytical | strong weight, narrow scope |
| 2 | machine-checked | property-lock evidence |
| 3 | certified numerical | instrument-grade numerics |
| 4 | sampled numerical | empirical probe evidence |
| 5 | empirical observation | lowest weight |

Verification level contributes to `evidence_weight` but never determines belief status alone.

## Quarantine policy

Instrument beliefs (see `configs/ceec/instruments.yaml`) are quarantined when a known defect materially affects measurement, provenance is suspect, or a correction record invalidates prior outputs. Quarantine of an instrument blocks promotion/boundary of dependent beliefs and blocks selection of materially dependent experiments. Quarantine scope is material dependency only; rationale is recorded.

## Waiver policy

Only soft constraints may be waived, always via an explicit recorded override with rationale in the decision record. Hard constraints are never waivable.

## Calibration policy

See `docs/ceec/CALIBRATION_POLICY.md`. Required for all pre-registered predictions carrying explicit probabilities.
