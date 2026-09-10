# Instrument Beliefs

Instrument beliefs are CEEC beliefs of type `instrument` (`I-` prefix) that
represent measurement machinery rather than claims. They carry evidence like
any other belief, and quarantine propagates to material dependents.

## Registry (configs/ceec/instruments.yaml)

| ID | Measures | Dependents |
|---|---|---|
| I-FROZEN-THETA-AUDIT | θ mutations (in-place, alias, restore, rebind) | ψ-only claims |
| I-JACOBIAN-SEPARATION | ρ and σ_max at audited coordinates | stability claims |
| I-VERTICAL-SLICE-PANEL | improvement_per_norm, credit quality | local credit claims |
| I-FLOPS-ESTIMATOR | effective operations | resource claims |
| I-RESOURCE-PROFILER | walltime/memory attribution | resource claims |
| I-KERNEL-EQUIVALENCE | fused-vs-reference equivalence | kernel claims |
| I-AUTOGRAD-PIPELINE | gradient correctness | autograd-dependent claims |
| I-VERIFICATION-LABELS | evidence strength labels | all evidence quality |

## Quarantine triggers

`known_defect_affects_measurement`, `estimator_mislabeled`, `audit_incomplete`,
`config_provenance_mismatch`, `dependent_artifact_stale`,
`correction_invalidates_measurement`, `live_patch_unverified`.

Quarantine of an instrument blocks promotion and boundary of dependent
beliefs and blocks selection of materially dependent experiments. Lifting
quarantine cascades back through dependents (`gates.unquarantine`).

## CLI

```
uv run python -m computronium.ceec.cli quarantine-report
uv run python -m computronium.ceec.cli status-history --belief I-FROZEN-THETA-AUDIT
```
