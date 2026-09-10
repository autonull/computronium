# CEEC-Core v1.0 (Computronium Implementation)

CEEC — the Controlled Epistemic Evidence Chain — is the epistemic operating
system governing the Epistemic Foundry (TODO19). This document summarizes the
core chain and invariants as implemented in `computronium/ceec/`.

## The chain

```
Experiment → Artifact → Evidence → Derived → Belief → Status
           → Goal Priority → Next Experiment → Decision
```

## Core invariants (enforced by code, not convention)

| Invariant | Enforcement |
|---|---|
| No belief without evidence | `create_belief` requires evidence/derived refs; `update_belief` refuses revisions on evidence-less beliefs |
| No belief without scope | `Scope` is a required model field; audit flags incomplete scopes |
| No scalar-only primary evidence when structure exists | `Evidence` model rejects structured kinds without `axes` + `values_ref` |
| No promotion without gates | `change_status` requires gate outcome refs for promoted/boundary |
| No boundary without defect hunt | boundary gate `defect_hunt_passed` |
| No reopening without credible trigger | reopen requires a declared trigger; `boundary → open` refuses without one |
| No trusted use of quarantined dependencies | quarantine propagates; `no_quarantined_dependencies` hard constraint |
| No goal priority influencing belief probability | goal revisions and belief revisions are separate tables and APIs |
| No experiment selection overriding hard constraints | hard-constraint filter runs before scoring; overrides cannot target failed candidates |
| No status change without provenance | every transition is an append-only `status_changes` row |

## Object model

`models.py` — frozen Pydantic models: `Scope`, `Artifact`, `Evidence`,
`Derived`, `Belief`, `BeliefRevision`, `Goal`, `GoalRevision`, `Experiment`,
`Decision`, `GateOutcome`, `StatusChange`, `CalibrationRecord`,
`InstrumentNote`.

## Ledger

`store.py` — SQLite at `ceec/ceec.sqlite3`; append-only enforced with
database triggers; content-addressed artifacts under `ceec/artifacts/`.
See `LEDGER_POLICY.md`.

## Statuses

Belief statuses: `open`, `promoted`, `boundary`, `quarantined`.
Current status = latest `status_changes.to_status` (falling back to the
latest revision). Effective status additionally propagates quarantine and
stale dependency signals (`gates.effective_status`).

## Thresholds

Promotion `probability_low >= 0.95`; boundary
`rescue_probability_high <= 0.05`; reopen trigger rescue `> 0.10`.
Intervals preferred; method declaration required.
