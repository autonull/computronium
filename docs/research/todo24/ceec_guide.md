# CEEC Practitioner Guide (TODO25 Phase C)

The closed loop from question to certified outcome in five steps:
**pre-register → run → decide → boundary/promote → calibrate**. Every
step rides a builder or store API — no hand-assembled payloads. Worked
examples: the TODO25 ledgers (`scratch/todo25_parity.sqlite3`,
`scratch/todo24_h24.sqlite3`, both git-ignored).

Core rule: evolution/campaigns produce evidence; gates dispose; claims
only at certified tier. Nothing here widens a gate.

## 0. Setup

```python
from ceec import builders, models
from ceec.store import CEECStore

store = CEECStore("scratch/my_ledger.sqlite3", "scratch/my_artifacts")
scope = models.Scope(
    domain="research",
    substrate=("digital",),
    budget="certified",                      # or a lab tier: BudgetTier.CERTIFIED.value
    extra={"problem_class": "flat_classification_hard"},
)
```

## 1. Pre-register: `builders.experiment`

`experiment(...)` populates every required field (`created_at`,
`falsification_criterion`, `overturn_criterion`, `hard_gates`, and the
§22 design keys `seed_plan` / `evaluation_policy` / `evidence_kind`) and
maps a lab budget tier onto a ceec budget (`smoke→quick`,
`quick→standard`, `certified→nightly`).

```python
draft = builders.experiment(
    id_="X-MYHYP-001",                        # ids must carry the X prefix
    question="does mechanism M beat its matched control?",
    prediction="M clears the control by 2 seed-SE",
    scope=scope,
    tier="certified",
    prediction_probability=(0.5, 0.8, 0.7),   # (low, high, point) prior
    design={"decision_rule": "paired permutation p < 0.05"},
)
```

You never write the quality-flag dict by hand — that is step 2's job —
and you never call `pre_register_experiment` yourself when measuring
through step 3's runner.

## 2. Evidence: `builders.gate_evidence`

Assembles the §18/§19 `quality` dict with the exact flag spellings the
gate readers consume (`seeds`, `matched_control`, `evaluation_policy`,
`defect_audit`, `integrity_checks`, `known_levers_exhausted`,
`reproduction`, `multi_seed_infeasible`) and validates them against that
alphabet. With `values` + `axes` + `values_ref` it ingests the payload
artifact and records `vector` evidence; otherwise pass `artifact_refs` +
`axes` + `values_ref` for `event` evidence.

```python
evidence = builders.gate_evidence(
    store, scope,
    axes=["seed"], values=[0.469, 0.539, 0.531],
    values_ref="probe/accuracies",
    seeds=3, matched_control=True,
    evaluation_policy="certified_operating_point_120ep",
    known_levers_exhausted=True,
    notes="defect hunt: task pipeline shared with a passing task",
)
```

A `chance_verdict` (below) belongs in `notes`: it carries the verdict
rule string the evidence rides on.

## 3. Run: `ceec.run.run_experiment`

The closed loop makes "every certified measurement is pre-registered
with a recorded Decision" structural: pre-register (a draft) → §22
decision over the single-candidate pool → probe execution →
artifact/evidence ingestion → calibration outcome → optional
boundary/promotion evaluation. The probe callable runs *inside* the loop,
so the outcome is generated strictly after pre-registration. The
single-candidate selection is recorded as a non-override, so §24
`override_rate` keeps signal for real selections-with-alternatives.

```python
from ceec.run import ProbeResult, run_experiment

def probe(experiment) -> ProbeResult:
    ...                                    # the measurement (training, etc.)
    return ProbeResult(
        label="FOR", outcome_boolean=True,
        payload={"rho": 0.62, "n_rows": 10},
        axes=["mechanism"], values=accuracies, values_ref="probe/accs",
        quality={"seeds": 1, "matched_control": False,
                 "evaluation_policy": "certified_operating_point_20ep_hard"},
        notes="decision rule: rho > 0.5 at a non-saturating operating point",
    )

run = run_experiment(store, draft, probe)          # evaluate=None
# run.status "completed" | "failed"; failed probes record `missing`
# evidence and a failed calibration outcome instead of raising
```

A probe exception is a ledger event, not a traceback: the experiment is
marked `failed` with `missing` evidence and a scored-False calibration
record. A probe that measures an operating point its own decision rule
calls "not decisive" (e.g. saturation censoring) should *raise* rather
than return a verdict — see `scripts/probes/todo25_recal_record.py`.

## 4. Beliefs: boundary / promotion

Beliefs are created with evidence attached, revised with a probability,
then moved through the gated status machine. `chance_verdict` is the
certified at-chance statistic (2·binomial-SE band over the eval split +
across-seed mean rule — the parity-boundary B.1 rule):

```python
from ceec.gates import declare_boundary, promote

verdict = builders.chance_verdict(accuracies, n_eval=32)   # B.1 statistics
assert verdict.at_chance                                   # mean rule carries it

belief = store.create_belief("M is at chance <operating point>", "mechanism",
                             scope, evidence_refs=[evidence.id])
store.update_belief(belief.id,
                    models.Probability(low=0.0, high=0.05),
                    "low", "high", "narrow", "open",
                    "rescue probability capped at the boundary threshold")
evaluation = declare_boundary(store, belief.id, "certified chance boundary")
```

`declare_boundary`/`promote` evaluate the §19/§18 gates from the evidence
quality flags and refuse the status change unless all pass. Belief
`type_` ∈ {instrument, mechanism, generality, defect} — boundary is a
*status*, not a type. Reopening a boundary needs a `REOPEN_TRIGGERS`
trigger.

## 5. Calibrate and review: drift cadence

Completed experiments with a declared prediction probability are scored
automatically by step 3 (`record_experiment_outcome`). The §24 review
cadence flags beliefs whose Brier score drifts across rounds:

```python
from ceec.audit import audit_decisions
from ceec.calibration import belief_drift, review_belief, review_flags
from computronium_lab.research.reports import render_ledger

report = render_ledger(store)[1]           # full rollup, incl. review_flags
drift = belief_drift(store)                # {belief_id: {drift, flagged, ...}}
review_belief(store, belief_id, action="acknowledge", reason="watched")
review_belief(store, belief_id, action="reopen", reason="drift",
              trigger="new_evidence_raises_rescue_probability")
```

`acknowledge` records an instrument note (an open belief has no legal
status transition); `reopen`/`quarantine` move through the gated machine
and record the reviewed state as a `StatusChange`.

## 6. One-shot report

```python
lab = Lab(record_ledger="scratch/my_ledger.sqlite3")
report = lab.research_report(spec, tier="certified", path="scratch/reports")
```

Returns synthesis + evolution plan + corpus arm plan (trainable vs
expected measurement blocks) + the ledger rollup; with `path` it writes
`ledger_report.md`/`.json`.

## Worked examples

| Question | Ledger | Probe | Outcome |
|---|---|---|---|
| Is NTM parity stuck at chance? | `scratch/todo25_parity.sqlite3` | `todo25_parity_boundary.py` + `todo25_parity_record.py` | `B-PARITY-CHANCE-001` → boundary (§19 gates passed) |
| Does campaign fitness beat the surrogate? (H24.2) | `scratch/todo24_h24.sqlite3` | `todo25_recal_record.py` via `ceec.run` | round 2 censored→superseded; round 3 on `flat_classification_hard` scored FOR/AGAINST |

Both pass `run_ledger_audit` with zero hand-assembled payloads. The
parity ledger's belief/gates were recorded with `builders.gate_evidence`
(step 2); the H24 ledger's round 3 is a complete step-3 closed loop.

## Instrument checklist

- [ ] Experiment built by `builders.experiment` (no dict literals)
- [ ] Probe returns `ProbeResult` with quality flags via the
      `builders.gate_evidence` spelling (or raises when not decisive)
- [ ] Every certified measurement went through `ceec.run.run_experiment`
      (Decision recorded, calibration scored)
- [ ] Status changes only through `declare_boundary`/`promote`/
      `review_belief` — never raw `change_status`
- [ ] `lab.research_report(..., path=...)` or `render_ledger` reviewed
      before closing the session
