# TODO19 — Epistemic Foundry: CEEC-Governed Mechanism Discovery

**Status:** Phases A–F and H implemented; Phase G open — families 1 & 3–5 primary probes executed (rounds 2–3); temporal-ψ mechanism build outstanding
**Created:** 2026-09-11
**Supersedes:** TODO19 “Mechanism Foundry”
**Normative governance spec:** CEEC-Core v1.0
**Primary implementation target:** `computronium/ceec/`

---

## Progress log (updated 2026-09-10)

### Implemented (round 1)

- **Phase A (governance):** `docs/ceec/{COMPUTRONIUM_PROFILE,LEDGER_POLICY,EXPERIMENT_PRE_REGISTRATION,CALIBRATION_POLICY}.md`, `configs/ceec/{profile,gates}.yaml`.
- **Phase B (ledger):** `computronium/ceec/{models,ids,store}.py`. Append-only SQLite (DB-level triggers block UPDATE/DELETE on 17 tables); frozen Pydantic object models with CEEC validation (structured evidence requires axes+values_ref; inert/missing require notes; promotion/boundary require gate refs; reopen requires trigger); content-addressed artifacts (`sha256:`, `ceec/artifacts/<h[:2]>/<h>`); belief revision history; only `open` revisions via `update_belief` — gated statuses exclusively via `change_status`.
- **Phase C (gates/quarantine):** `gates.py` — promotion (8 gates) and boundary (7 gates) evaluation from evidence `quality` metadata; transitive quarantine propagation + cascading unquarantine; effective-status resolution incl. staleness (content-change-based, not status-flip-based).
- **Phase D (selection):** `selection.py` — hard-constraint filter (G-HARD-0..10) evaluated BEFORE scoring; documented EV/cost model (`EV = Σ goal_priority·(1−mid)·generality_mult`, `Score = EV/Cost^γ`); deterministic state hash; explicit overrides that cannot bypass constraints or target constraint-failed candidates; append-only decisions.
- **Phase E (evidence capture):** `probe_adapter.py` (probe contract → artifact/evidence/derived; inert/missing auto-documentation; scalar summaries always derived); `migrate/todo18_records.py` — all 3 claim records + corrections log migrated as Artifact+Evidence+Derived, never beliefs.
- **Phase F (bootstrap):** `configs/ceec/{instruments,beliefs,goals}.yaml` + 5 experiment YAMLs; `bootstrap.py` gives every belief provenance evidence (config artifact). Real ledger initialized at `ceec/ceec.sqlite3`: 8 instruments, 5 hypotheses, 5 goals, 5 pre-registered experiments, audit clean.
- **Phase H (calibration/audit/report):** `calibration.py` (outcome recording with Brier/log, report, review flags), `audit.py` (8 checks), `cli.py` (init, bootstrap, migrate, propose, decide, audit, calibration-report, status-history, quarantine-report, export). Bootstrap-round report: `docs/ceec/EPISTEMIC_FOUNDRY_REPORT.md`, `MECHANISM_SCHEMAS.md`, `INSTRUMENT_BELIEFS.md`, `CEEC_CORE.md`, `ceec/README.md`.

### Quality gates

- `tests/ceec/`: **110 passed** (models, store, gates, quarantine, selection, structured evidence, bootstrap, calibration, integration loop, families smoke) — ~1.3 s.
- `ruff format` + `ruff check` clean on all new files; `pyright` clean (0 errors).

### Open work (next round)

1. **Temporal-ψ mechanism build** (blocks X-TPC-001): implement a supervised/temporal ψ update (new Plasticity primitive) with AlgorithmIdentityCard (G-HARD-9) + FrozenThetaAudit (G-HARD-8). D22 root cause (ψ contract consumes target-free first-phase activity) is the design constraint: the new ψ law must consume a loss/target or trace term. Lever analysis recorded as derived `D-000005`; X-TPC-001 stays pre-registered.
2. Emit `mechanism_schema` derived objects once a first gated update lands (MECHANISM_SCHEMAS.md slots reserved).
3. Real `supersedes` relations on artifact correction (policy defined, not exercised).
4. Deeper TODO18 migration (per-test evidence for instrument beliefs) — Priority 1 instruments currently rely on bootstrap provenance only.
5. Follow-up probes from round-3 findings: X-RSE-002 (accuracy-preserving routing: mask tempering / trained gate readout) and X-USU-002 (why muon-on-forward degrades one-step descent — momentum/noise-floor defect hunt). X-STA-002 (noise robustness at the discovered coordinates) also unblocks B-H3 promotion.
6. Optional: `comp ceec` wrapper integration (§12), portfolio optimization, web dashboard.

### Round 3 — experiment execution record (2026-09-10)

- **X-STA-001 executed** (`scripts/probes/x_sta_001.py`, ~0.5 s CPU): stable
  transiently-amplifying coordinates found on **all 3 seeds** via
  W = Q·blkdiag(ρ(I+cK₄))·Qᵀ (4 size-4 Jordan blocks, rotated; nominal
  ρ=0.85, c-sweep {0, 0.5, 1, 2, 4}). Realized ρ ≤ 0.91 < 0.95 limit while
  σ_max reaches 4.06; settling time grows monotonically with σ_max
  (168→344 steps at tol 1e-4; budget 500). c=0 purely-contractive control
  matched. B-H3 updated [0.20, 0.55] → [0.30, 0.70]; only
  probability_threshold fails promotion; calibration CAL-000002; audit clean.
  Design note: single-Jordan-block families are float32-fragile (defect
  perturbation ~ε^(1/16) moved realized ρ to ~1.06); size-4 blocks bound
  the drift at ~ε^(1/4) ≈ 0.02.
- **X-RSE-001 executed** (`scripts/probes/x_rse_001.py`, ~0.5 s CPU): routing
  (RoutingPlasticity, gate_dim=16, backprop credit, sparse 3-informative-
  feature task, 30 steps, 3 seeds) cuts effective ops by **48–50%** with no
  gate collapse, but costs 0–4.7pt accuracy (seed-dependent) — the ≤1pt
  accuracy-loss clause of the pre-registered prediction fails on one seed,
  so verdict = no routing benefit *at this operating point*. B-H4 narrowed
  [0.25, 0.60] → [0.05, 0.35] (the accuracy clause fails; the ops win alone
  is recorded in the evidence values, not the belief). defect_audit gate
  flagged (dense seed-1 accuracy 0.203 ≈ chance — task barely learnable at
  quick budget). Calibration CAL-000003; audit clean.
- **X-USU-001 executed** (`scripts/probes/x_usu_001.py`, ~0.6 s CPU): role-
  split update beats uniform on all 3 seeds — **muon-on-readout +
  euclid-elsewhere** (hybrid_muon_out) is the best arm everywhere
  (ipn 0.52–0.60 vs uniform-euclid 0.45–0.54); muon-on-forward is
  destructive at matched norm (ipn 0.01–0.03), consistent with the
  RiemannianOrthogonal identity card's "orthogonalization amplifies the
  noise floor" deviation (single-batch pseudo-grads). Specialization
  supported. B-H5 updated [0.20, 0.55] → [0.25, 0.60] with
  hybrid_muon_out named winner; only probability_threshold fails; CAL-000004;
  audit clean. The hybrid rule is a per-name dispatcher (zero-momentum
  non-role grads → exactly zero displacement; no double-stepping).
- CEEC oracle selection after each ingest: X-RSE-001 → X-USU-001 →
  X-RSE-001 (follow-up), consistent with the narrowed beliefs.
- Wiring: `scripts/probes/x_*.py` added to ruff `per-file-ignores`
  (E402/I001 — sys.path bootstrap pattern); all three probes ruff + pyright
  clean; `tests/ceec` 110 passed (~1.4 s).

### Round 2 — experiment execution record (2026-09-10)

- **X-ALI-001 executed** (`scripts/probes/x_ali_001.py`, 2.2 s CPU): adaptive
  feedback (B ∝ W/‖W‖ re-projection, shape-safe, re-projected each step) beats
  fixed random feedback on late-half improvement_per_norm on **all 3 seeds**
  at matched ‖Δθ‖ ({0.863, 0.853, 0.694} vs {0.490, 0.459, 0.517}). B-H1
  updated [0.20, 0.60] → [0.45, 0.80]; promotion gate evaluated (only
  probability_threshold fails — one probe cannot promote); calibration
  CAL-000001 (Brier 0.25); audit clean.
- **X-TPC-001 lever analysis** (`scripts/probes/x_tpc_001_feasibility.py`):
  D22 falsified the instantaneous-ψ lever; temporal credit is the untested
  lever and requires a mechanism build (identity card + frozen-θ audit).
  B-H2 narrowed [0.15, 0.55] → [0.10, 0.45]; no boundary declared (the named
  lever is untested — boundary would be premature).

### Improvement opportunities

- Evidence-quality flags are convention-driven (probe `quality` dict keys documented in `gates.py` docstring); a Pydantic `QualityModel` would harden them.
- `_next_id` uses table COUNT — safe under single-writer CLI use; switch to AUTOINCREMENT-style sequencing if concurrent writers appear.
- `decide()` re-evaluates constraints on every call; cache keyed on `state_hash` if rounds grow large.
- Staleness detection compares revision content; consider recording per-belief dep-snapshot hashes for exactness.
- Defective-matrix construction is float32-fragile: a size-4 Jordan block drifts realized ρ by ~ε^(1/4); add a `stability/` helper that verifies constructed spectra before use (X-STA-001 learned this the hard way — see round 3 note).
- Probe `_ingest_ceec` blocks share ~40 lines of boilerplate (link evidence → update belief → gates → calibration → audit → decide); extract a shared `ceec.probe_adapter.ingest_verdict(...)` helper (DRY; three near-identical copies now exist).
- X-RSE-001's dense-arm accuracy sits near chance at the quick budget — before X-RSE-002, either lengthen the budget or simplify the task so the ≤1pt accuracy-loss clause is measured against a learnable baseline.

---

## 0. Executive Summary

This plan has two inseparable objectives:

1. **Implement CEEC-Core v1.0 inside Computronium** as the epistemic operating system for evidence, beliefs, goals, experiments, gates, statuses, decisions, quarantine, and calibration.

2. **Use CEEC to govern the next experimental phase**, previously called TODO19, now renamed **Epistemic Foundry**.

The Epistemic Foundry is not merely a campaign runner. It is a CEEC-compliant scientific reasoning engine that:

- stores immutable artifacts,
- preserves structured evidence,
- derives relations and summaries,
- maintains scoped beliefs,
- separates belief probability from goal utility,
- gates promotions and boundaries,
- quarantines suspect instruments,
- selects experiments by expected value per cost under hard constraints,
- records auditable decisions,
- tracks calibration.

The first CEEC-governed experiment families are:

1. **Adaptive Local Inverses** — can local credit become effective when feedback/inverse projections adapt?
2. **Temporal ψ Credit** — can frozen-θ writable-state adaptation scale to longer horizons with temporal credit?
3. **Stable Transient Amplification** — can asymptotically stable but transiently amplifying dynamics improve robustness?
4. **Routing × Sparsity Efficiency** — does routing produce measurable resource benefits?
5. **Update-Rule Specialization** — do different update rules serve different mechanistic roles?

The desired outcome is not only positive benchmark results. The desired outcome is **governed knowledge**:

- promoted claims with gates,
- boundaries with defect hunts,
- quarantines when instruments are suspect,
- reopenings when new mechanisms appear,
- decision logs explaining what was run and why,
- calibration records showing whether our confidence was honest.

---

## 1. Naming

The old name “Mechanism Foundry” described the experimental ambition.

The new name is:

> **Epistemic Foundry**

This is more accurate because the primary product is not just mechanisms, but **forged, audited, gated epistemic claims** about mechanisms.

Recommended file name:

```text
TODO19_EPISTEMIC_FOUNDRY.md
```

Optional short label:

```text
T19-EF
```

---

## 2. Scope

This plan covers:

1. Implementation of a minimal but normatively compliant CEEC-Core layer in Python.
2. Creation of the Computronium CEEC profile.
3. Bootstrap of the initial CEEC epistemic state.
4. Integration of the Epistemic Foundry campaign/probe system with CEEC.
5. Execution of the first CEEC-governed experiment families.
6. Calibration, audit, reporting, and CI enforcement.

---

## 3. Non-Goals

This plan deliberately avoids:

1. Building a full probabilistic programming system.
2. Building a distributed ledger or external database service.
3. Replacing PyTorch, the ontology, or existing trainer infrastructure.
4. Physical hardware validation.
5. Large-scale benchmarking before CEEC gates are implemented.
6. Automatic belief updating without declared method.
7. Allowing goal utility to modify belief probability.
8. Allowing score-based overrides of hard gates.
9. Treating invalid or unrealizable coordinates as negative capability evidence.
10. Collapsing structured evidence into scalar-only primary records.

---

## 4. Core Principle

The Epistemic Foundry obeys the CEEC-Core chain:

```text
Experiment
  → Artifact
  → Evidence
  → Derived
  → Belief
  → Status
  → Goal Priority
  → Next Experiment
  → Decision
```

and the core invariants:

```text
No belief without evidence.
No belief without scope.
No scalar-only primary evidence when structure exists.
No promotion without gates.
No boundary without defect hunt and lever exhaustion.
No reopening without credible trigger.
No trusted use of quarantined dependencies.
No goal priority influencing belief probability.
No experiment selection overriding hard constraints.
No status change or selection decision without provenance.
```

---

## 5. Relationship to Existing Computronium Infrastructure

CEEC does not replace existing infrastructure. It governs it.

| Existing Computronium object | CEEC role |
|---|---|
| `ClaimRecord` | Derived summary/export, not primary belief |
| `FrontierRecord` | Derived relation/frontier object |
| Vertical slice panel | Instrument belief + evidence generator |
| Mechanistic study | Evidence + derived relations |
| Stability × Memory campaign | Structured tensor evidence |
| FrozenThetaAudit | Instrument belief + hard gate |
| Verification taxonomy | Evidence quality / instrument strength |
| Identity cards | Realizability and hygiene gate |
| `SystemConfig.validate()` | Hard constraint gate |
| Property locks | Instrument evidence |
| Corrections log | Defect and quarantine provenance |

The key semantic upgrade:

> Existing records become artifacts and evidence.  
> They are not beliefs by themselves.

---

## 6. Deliverables

### 6.1 Code

Create:

```text
computronium/ceec/
  __init__.py
  models.py
  ids.py
  store.py
  gates.py
  selection.py
  calibration.py
  profile.py
  bootstrap.py
  cli.py
  migrate/
    __init__.py
    todo18_records.py
```

### 6.2 Configuration

Create:

```text
configs/ceec/
  profile.yaml
  gates.yaml
  goals.yaml
  beliefs.yaml
  instruments.yaml
  experiments/
    adaptive_local_inverses.yaml
    temporal_psi_credit.yaml
    stable_transient_amplification.yaml
    routing_sparsity_efficiency.yaml
    update_rule_specialization.yaml
```

### 6.3 Ledger Data

Create:

```text
ceec/
  ceec.sqlite3
  artifacts/
  exports/
  README.md
```

`ceec.sqlite3` is the primary ledger.  
`ceec/artifacts/` stores immutable artifact files, preferably content-addressed.  
`ceec/exports/` stores human-readable exports and reports.

### 6.4 Documentation

Create:

```text
docs/ceec/
  CEEC_CORE.md
  COMPUTRONIUM_PROFILE.md
  LEDGER_POLICY.md
  INSTRUMENT_BELIEFS.md
  EXPERIMENT_PRE_REGISTRATION.md
  CALIBRATION_POLICY.md
  EPISTEMIC_FOUNDRY_REPORT.md
  MECHANISM_SCHEMAS.md
```

### 6.5 Tests

Create:

```text
tests/ceec/
  test_models.py
  test_store.py
  test_gates.py
  test_quarantine.py
  test_selection.py
  test_calibration.py
  test_bootstrap.py
  test_integration_loop.py
  test_structured_evidence.py
  test_experiment_families_smoke.py
```

---

## 7. CEEC Object Model for Computronium

CEEC-Core objects are implemented as frozen Python dataclasses or Pydantic models, then persisted to SQLite.

### 7.1 Primary objects

```text
Scope
Artifact
Evidence
Derived
Belief
Goal
Experiment
Decision
StatusChange
GateOutcome
CalibrationRecord
InstrumentNote
```

### 7.2 Object flow

```text
Experiment is pre-registered.
Experiment executes.
Artifacts are written.
Evidence references artifacts.
Derived objects reference evidence.
Beliefs reference evidence and derived objects.
GateOutcomes gate status changes.
StatusChanges update beliefs.
Decisions record experiment selection.
CalibrationRecords compare predictions with outcomes.
```

---

## 8. Storage Policy

### 8.1 Ledger backend

Use SQLite.

Reasons:

- standard library,
- relational integrity,
- easy audit,
- no external service,
- sufficient for campaign scale.

Database file:

```text
ceec/ceec.sqlite3
```

### 8.2 Append-only policy

The following are append-only:

- artifacts,
- evidence,
- derived,
- decisions,
- gate outcomes,
- status changes,
- calibration records.

Beliefs and goals may have new revisions, but previous revisions must remain recoverable.

Implementation strategy:

- `belief` table stores immutable belief identity and statement scope.
- `belief_revision` table stores probability, uncertainty, evidence weight, generality, rationale, timestamp.
- current belief state is a view over latest revision.
- goals may use `goal_revision` similarly.

### 8.3 Artifact immutability

Artifacts must be content-addressed where practical.

Preferred artifact ID:

```text
sha256:<hash>
```

Artifact files stored under:

```text
ceec/artifacts/<hash-prefix>/<hash>
```

If an artifact is corrected or regenerated, do not overwrite. Create a new artifact and link it with a derived `supersedes` relation.

---

## 9. Minimal SQLite Schema

The implementation may refine this, but the following schema is the baseline.

```sql
CREATE TABLE artifacts (
    id TEXT PRIMARY KEY,
    sha256 TEXT,
    uri TEXT NOT NULL,
    type TEXT NOT NULL,
    provenance JSON NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE evidence (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    scope JSON NOT NULL,
    axes JSON,
    values_ref TEXT,
    uncertainties JSON,
    quality JSON,
    defects JSON,
    notes TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE evidence_artifacts (
    evidence_id TEXT NOT NULL REFERENCES evidence(id),
    artifact_id TEXT NOT NULL REFERENCES artifacts(id),
    PRIMARY KEY (evidence_id, artifact_id)
);

CREATE TABLE derived (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    operator TEXT NOT NULL,
    inputs JSON NOT NULL,
    left TEXT,
    right TEXT,
    parameters JSON,
    value JSON,
    probability_positive REAL,
    probability_material REAL,
    assumptions JSON,
    checks JSON,
    scope JSON NOT NULL,
    provenance JSON,
    created_at TEXT NOT NULL
);

CREATE TABLE beliefs (
    id TEXT PRIMARY KEY,
    statement TEXT NOT NULL,
    type TEXT NOT NULL,
    scope JSON NOT NULL,
    posterior_method TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE belief_revisions (
    id TEXT PRIMARY KEY,
    belief_id TEXT NOT NULL REFERENCES beliefs(id),
    probability_low REAL NOT NULL,
    probability_high REAL NOT NULL,
    probability_point REAL,
    uncertainty TEXT NOT NULL,
    evidence_weight TEXT NOT NULL,
    generality TEXT NOT NULL,
    status TEXT NOT NULL,
    rationale TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE belief_evidence (
    belief_id TEXT NOT NULL REFERENCES beliefs(id),
    evidence_id TEXT NOT NULL REFERENCES evidence(id),
    PRIMARY KEY (belief_id, evidence_id)
);

CREATE TABLE belief_derived (
    belief_id TEXT NOT NULL REFERENCES beliefs(id),
    derived_id TEXT NOT NULL REFERENCES derived(id),
    PRIMARY KEY (belief_id, derived_id)
);

CREATE TABLE belief_dependencies (
    belief_id TEXT NOT NULL REFERENCES beliefs(id),
    depends_on_belief_id TEXT NOT NULL REFERENCES beliefs(id),
    PRIMARY KEY (belief_id, depends_on_belief_id)
);

CREATE TABLE goals (
    id TEXT PRIMARY KEY,
    statement TEXT NOT NULL,
    kind TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE goal_revisions (
    id TEXT PRIMARY KEY,
    goal_id TEXT NOT NULL REFERENCES goals(id),
    utility JSON NOT NULL,
    scalar_utility REAL,
    cost_low REAL,
    cost_high REAL,
    priority REAL,
    status TEXT NOT NULL,
    rationale TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE goal_beliefs (
    goal_id TEXT NOT NULL REFERENCES goals(id),
    belief_id TEXT NOT NULL REFERENCES beliefs(id),
    PRIMARY KEY (goal_id, belief_id)
);

CREATE TABLE experiments (
    id TEXT PRIMARY KEY,
    question TEXT NOT NULL,
    rationale TEXT NOT NULL,
    scope JSON NOT NULL,
    target_beliefs JSON NOT NULL,
    target_goals JSON NOT NULL,
    design JSON NOT NULL,
    prediction TEXT NOT NULL,
    prediction_probability_low REAL,
    prediction_probability_high REAL,
    prediction_probability_point REAL,
    controls JSON NOT NULL,
    metrics JSON NOT NULL,
    budget TEXT NOT NULL,
    cost_low REAL,
    cost_high REAL,
    falsification_criterion TEXT NOT NULL,
    overturn_criterion TEXT NOT NULL,
    hard_gates JSON NOT NULL,
    status TEXT NOT NULL,
    pre_registered_at TEXT,
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE decisions (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    state_hash TEXT NOT NULL,
    candidate_experiments JSON NOT NULL,
    scores JSON NOT NULL,
    selected_experiment TEXT,
    overrides JSON NOT NULL,
    constraints_checked JSON NOT NULL,
    rationale TEXT NOT NULL
);

CREATE TABLE gate_outcomes (
    id TEXT PRIMARY KEY,
    gate TEXT NOT NULL,
    belief_id TEXT REFERENCES beliefs(id),
    experiment_id TEXT REFERENCES experiments(id),
    status TEXT NOT NULL,
    evidence_refs JSON NOT NULL,
    derived_refs JSON NOT NULL,
    rationale TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE status_changes (
    id TEXT PRIMARY KEY,
    belief_id TEXT NOT NULL REFERENCES beliefs(id),
    from_status TEXT NOT NULL,
    to_status TEXT NOT NULL,
    reason TEXT NOT NULL,
    trigger TEXT NOT NULL,
    gate_refs JSON NOT NULL,
    evidence_refs JSON NOT NULL,
    derived_refs JSON NOT NULL,
    actor TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE calibration_records (
    id TEXT PRIMARY KEY,
    experiment_id TEXT REFERENCES experiments(id),
    belief_id TEXT REFERENCES beliefs(id),
    prediction TEXT NOT NULL,
    predicted_probability_low REAL,
    predicted_probability_high REAL,
    predicted_probability_point REAL,
    outcome TEXT,
    outcome_boolean INTEGER,
    brier_score REAL,
    log_score REAL,
    scope JSON,
    notes TEXT,
    created_at TEXT NOT NULL
);
```

---

## 10. Computronium CEEC Profile

Create:

```text
docs/ceec/COMPUTRONIUM_PROFILE.md
configs/ceec/profile.yaml
```

The profile binds CEEC-Core to Computronium.

### 10.1 Thresholds

Default CEEC thresholds:

```yaml
thresholds:
  promote: 0.95
  boundary: 0.05
  reopen: 0.10
```

For interval probabilities:

- Promotion requires `probability_low >= 0.95`.
- Boundary requires `rescue_probability_high <= 0.05`.
- Reopen trigger requires estimated rescue probability > `0.10`.

### 10.2 Probability policy

Allowed probability representations:

```yaml
probability_policy:
  point: allowed
  interval: preferred
  method_declaration_required: true
```

For early Epistemic Foundry work, use intervals unless a calibrated posterior method exists.

Example:

```yaml
probability:
  low: 0.20
  high: 0.55
  method: heuristic_interval_based_on_gate_evidence
```

### 10.3 Cost model

Initial cost dimensions:

```yaml
cost_model:
  walltime_weight: 1.0
  memory_weight: 0.25
  human_review_weight: 0.5
  storage_weight: 0.05
  gamma: 1.0
```

The exact cost estimator may be simple, but it must be documented.

### 10.4 Hard constraints

The following hard constraints are non-waivable in the Computronium profile:

```yaml
hard_constraints_nonwaivable:
  - coordinate_valid
  - pre_registration_complete
  - no_quarantined_dependencies
  - budget_within_limit
  - controls_present_or_justified
  - seed_plan_present
  - evaluation_policy_present
  - structured_evidence_plan_present
  - instrument_valid_for_claim
  - frozen_theta_audit_for_psi_only_claims
  - identity_card_for_new_primitive
```

### 10.5 Evidence kinds

Required evidence kinds:

```text
scalar
interval
vector
tensor
curve
event
distribution
frontier
inert
missing
```

Special Computronium rule:

```text
Invalid coordinates are evidence kind `inert`, not negative capability evidence.
```

### 10.6 Verification levels

CEEC evidence quality should include verification level:

```yaml
quality:
  verification_level: 4 | 5
```

Mapping:

| Verification level | CEEC interpretation |
|---|---|
| 1 | analytical evidence |
| 2 | machine-checked evidence |
| 3 | certified numerical evidence |
| 4 | sampled numerical evidence |
| 5 | empirical observation |

Verification level contributes to `evidence_weight`, but does not automatically determine belief status.

---

## 11. Implementation Phases

---

# Phase A — CEEC Profile and Policy

## Objective

Make CEEC-Core concrete for Computronium before writing ledger code.

## Tasks

- [ ] **A.1 Write Computronium CEEC profile**
  - File:
    - `docs/ceec/COMPUTRONIUM_PROFILE.md`
  - Must define:
    - thresholds,
    - probability policy,
    - cost model,
    - hard constraints,
    - waiver policy,
    - quarantine policy,
    - calibration policy,
    - evidence kind usage.

- [ ] **A.2 Write ledger policy**
  - File:
    - `docs/ceec/LEDGER_POLICY.md`
  - Must define:
    - append-only rules,
    - artifact hashing,
    - retention,
    - correction procedure,
    - export procedure.

- [ ] **A.3 Write experiment pre-registration policy**
  - File:
    - `docs/ceec/EXPERIMENT_PRE_REGISTRATION.md`
  - Must define:
    - required fields,
    - controls policy,
    - prediction probability policy,
    - falsification criterion style,
    - overturn criterion style.

- [ ] **A.4 Write calibration policy**
  - File:
    - `docs/ceec/CALIBRATION_POLICY.md`
  - Must define:
    - when predictions require probabilities,
    - Brier/log score usage,
    - calibration review thresholds.

- [ ] **A.5 Define gate configuration**
  - File:
    - `configs/ceec/gates.yaml`
  - Must define:
    - promotion gates,
    - boundary gates,
    - quarantine gates,
    - reopen gates,
    - hard constraints.

## Acceptance Criteria

- [ ] Profile document exists.
- [ ] Thresholds are explicit.
- [ ] Hard constraints are explicit.
- [ ] Probability policy is explicit.
- [ ] Quarantine policy is explicit.
- [ ] Calibration policy is explicit.

---

# Phase B — Core Object Model and Ledger Store

## Objective

Implement the CEEC object model and append-only SQLite ledger.

## Tasks

- [ ] **B.1 Create CEEC package skeleton**
  - Files:
    - `computronium/ceec/__init__.py`
    - `computronium/ceec/models.py`
    - `computronium/ceec/ids.py`
    - `computronium/ceec/store.py`

- [ ] **B.2 Implement object models**
  - Required models:
    - `Scope`
    - `Artifact`
    - `Evidence`
    - `Derived`
    - `Belief`
    - `BeliefRevision`
    - `Goal`
    - `GoalRevision`
    - `Experiment`
    - `Decision`
    - `GateOutcome`
    - `StatusChange`
    - `CalibrationRecord`
  - Requirements:
    - frozen dataclasses or Pydantic models,
    - explicit validation,
    - typed scopes,
    - no bare scalar belief without scope/evidence.

- [ ] **B.3 Implement ID policy**
  - Recommended prefixes:
    - `A-` artifacts
    - `E-` evidence
    - `D-` derived
    - `B-` beliefs
    - `G-` goals
    - `X-` experiments
    - `DEC-` decisions
    - `GO-` gate outcomes
    - `SC-` status changes
    - `CAL-` calibration records
  - IDs must be stable and unique.

- [ ] **B.4 Implement SQLite store**
  - File:
    - `computronium/ceec/store.py`
  - Requirements:
    - initialize schema,
    - insert objects transactionally,
    - enforce referential integrity,
    - reject deletion or mutation of append-only tables,
    - support query by ID/status/type/scope.

- [ ] **B.5 Implement artifact ingestion**
  - Function:
    - `ingest_artifact(path_or_bytes, type, provenance) -> Artifact`
  - Requirements:
    - compute SHA-256,
    - copy file into `ceec/artifacts/`,
    - refuse overwrite of existing hash,
    - return artifact record.

- [ ] **B.6 Implement evidence ingestion**
  - Function:
    - `record_evidence(kind, scope, artifact_refs, quality, axes, values_ref, ...) -> Evidence`
  - Requirements:
    - require at least one artifact ref or explicit no-artifact justification,
    - reject scalar-only primary evidence when declared structure exists,
    - label `missing` and `inert` explicitly.

- [ ] **B.7 Implement derived ingestion**
  - Function:
    - `record_derived(type, operator, inputs, value, assumptions, checks, ...) -> Derived`
  - Requirements:
    - all inputs must exist,
    - operator must be declared,
    - assumptions and checks recorded.

- [ ] **B.8 Implement belief revisions**
  - Function:
    - `update_belief(belief_id, revision, rationale) -> BeliefRevision`
  - Requirements:
    - preserve previous revisions,
    - require rationale,
    - require evidence or derived refs before non-open status.

## Tests

- [ ] `tests/ceec/test_models.py`
  - valid/invalid object construction.
- [ ] `tests/ceec/test_store.py`
  - referential integrity,
  - append-only behavior,
  - artifact hashing,
  - revision history.

## Acceptance Criteria

- [ ] Ledger initializes.
- [ ] Objects can be inserted.
- [ ] Invalid references are rejected.
- [ ] Append-only tables cannot be mutated through public API.
- [ ] Artifact hashes are stable.
- [ ] Belief revisions preserve history.

---

# Phase C — Gate Engine, Status Machine, and Quarantine

## Objective

Implement CEEC status transitions as gated, auditable operations.

## Tasks

- [ ] **C.1 Implement gate outcome recording**
  - File:
    - `computronium/ceec/gates.py`
  - Function:
    - `record_gate_outcome(gate, status, evidence_refs, derived_refs, rationale, belief_id=None, experiment_id=None)`

- [ ] **C.2 Implement promotion gate evaluation**
  - Required gates:
    - probability threshold,
    - multi-seed,
    - matched control,
    - evaluation policy valid,
    - defect audit,
    - reproduction,
    - scope explicit,
    - no quarantined dependencies.

- [ ] **C.3 Implement boundary gate evaluation**
  - Required gates:
    - rescue probability threshold,
    - defect hunt passed,
    - integrity checks passed,
    - known levers exhausted,
    - matched control,
    - multi-seed where feasible,
    - scope explicit.

- [ ] **C.4 Implement quarantine logic**
  - A belief must be quarantined if:
    - a required instrument belief is quarantined,
    - evidence provenance is suspect,
    - defect is known and material,
    - dependent evidence is quarantined.
  - Quarantine must block:
    - promotion,
    - boundary declaration,
    - experiment selection if dependency is material.

- [ ] **C.5 Implement reopen logic**
  - Reopen triggers:
    - strong untested mechanism,
    - new evidence raising rescue probability,
    - instrument defect invalidating old boundary,
    - decisive omitted control discovered.
  - Reopen moves belief from `boundary` to `open` with recorded trigger.

- [ ] **C.6 Implement status change recording**
  - Function:
    - `change_status(belief_id, to_status, reason, trigger, gate_refs, evidence_refs, derived_refs)`
  - Requirements:
    - append-only,
    - require gate refs for `promoted` or `boundary`,
    - require trigger for reopening.

- [ ] **C.7 Implement effective status resolution**
  - Effective status must consider:
    - primary status,
    - quarantine propagation,
    - stale dependencies.

## Tests

- [ ] `tests/ceec/test_gates.py`
- [ ] `tests/ceec/test_quarantine.py`

Required test cases:

- [ ] Promotion fails without matched control.
- [ ] Promotion fails with single seed unless justified.
- [ ] Boundary fails without defect hunt.
- [ ] Boundary fails while known lever remains untested.
- [ ] Quarantined instrument blocks dependent promotion.
- [ ] Reopening requires recorded trigger.
- [ ] Status change without gate outcome is rejected.

## Acceptance Criteria

- [ ] Gate outcomes are recorded.
- [ ] Status changes are gated.
- [ ] Quarantine propagates.
- [ ] Reopening is auditable.
- [ ] No status can be promoted or bounded by assertion alone.

---

# Phase D — Experiment Selection and Decision Ledger

## Objective

Make the Epistemic Foundry Oracle CEEC-compliant.

## Tasks

- [ ] **D.1 Implement candidate generation**
  - File:
    - `computronium/ceec/selection.py`
  - Candidate sources:
    - uncertain high-value beliefs,
    - blocked goals,
    - pending promotion gates,
    - boundary challenges,
    - suspected defects,
    - untested overturn mechanisms,
    - generality tests,
    - resource tests,
    - instrument hygiene.

- [ ] **D.2 Implement hard-constraint filter**
  - Must run before scoring.
  - Must reject candidates failing:
    - coordinate validity,
    - pre-registration completeness,
    - quarantined dependencies,
    - missing controls,
    - missing seed plan,
    - missing evaluation policy,
    - missing structured evidence plan,
    - budget violation,
    - missing frozen-θ audit for ψ-only claims,
    - missing identity card for new primitives.

- [ ] **D.3 Implement scoring model**
  - Default score:

    ```text
    Score(x) = ExpectedValue(x) / Cost(x)^γ
    ```

  - Expected value may include:
    - value of information,
    - goal utility,
    - boundary overturn value,
    - promotion value,
    - hygiene value,
    - optionality.
  - The scoring model must be documented.

- [ ] **D.4 Implement decision recording**
  - Every selection must append a `Decision`.
  - Decision must include:
    - state hash,
    - candidate set,
    - scores,
    - selected experiment,
    - overrides,
    - constraints checked,
    - rationale.

- [ ] **D.5 Implement state hash**
  - State hash should summarize:
    - latest belief revision IDs,
    - goal revision IDs,
    - quarantine set,
    - active experiments,
    - gate outcomes relevant to candidates.
  - Exact algorithm may be simple but deterministic.

- [ ] **D.6 Implement manual override policy**
  - Overrides must be explicit.
  - Overrides must not bypass hard constraints.
  - Overrides must be stored in decision record.

## Tests

- [ ] `tests/ceec/test_selection.py`

Required test cases:

- [ ] Candidate with quarantined dependency is rejected before scoring.
- [ ] High score cannot override hard constraint.
- [ ] Decision record is written for selected experiment.
- [ ] Override without rationale is rejected.
- [ ] Scoring is deterministic under fixed state.

## Acceptance Criteria

- [ ] Oracle selection is CEEC-compliant.
- [ ] Hard constraints precede scoring.
- [ ] Decisions are append-only.
- [ ] Overrides are explicit.
- [ ] State hash is reproducible.

---

# Phase E — Evidence Capture from Probes

## Objective

Ensure existing and future probes emit CEEC-compliant evidence.

## Tasks

- [ ] **E.1 Define probe output contract**
  - Every probe must return:
    - artifacts,
    - evidence kind,
    - scope,
    - axes,
    - quality metadata,
    - defects,
    - structured values or reference to structured values.

- [ ] **E.2 Implement evidence adapter**
  - File:
    - `computronium/ceec/probe_adapter.py`
  - Convert probe outputs into:
    - artifacts,
    - evidence,
    - derived summaries.

- [ ] **E.3 Enforce structured evidence rule**
  - If probe result contains:
    - curve,
    - tensor,
    - vector,
    - frontier,
    - event sequence,
    - distribution,
  then evidence kind must preserve that structure.
  - Scalar summaries must be recorded as derived objects.

- [ ] **E.4 Handle missing and inert results**
  - Failed run due to invalid coordinate:
    - `inert`
  - Failed run due to infrastructure error:
    - `missing`
  - Negative capability evidence:
    - only when realizability is not the issue.

- [ ] **E.5 Link existing TODO18 records**
  - File:
    - `computronium/ceec/migrate/todo18_records.py`
  - Migrate or reference:
    - vertical slice claim record,
    - mechanistic study claim record,
    - memory stability claim record,
    - corrections log,
    - identity card generator output,
    - relevant property-lock summaries.

## Tests

- [ ] `tests/ceec/test_structured_evidence.py`

Required test cases:

- [ ] Curve result cannot be stored as scalar-only primary evidence.
- [ ] Tensor result preserves axes.
- [ ] Invalid coordinate produces `inert`, not negative capability evidence.
- [ ] Missing artifact justification is required if no artifact exists.

## Acceptance Criteria

- [ ] Probe outputs become CEEC evidence.
- [ ] Structured evidence is preserved.
- [ ] Scalar summaries are derived.
- [ ] Missing/inert results are explicit.
- [ ] Existing records are linked or migrated.

---

# Phase F — Bootstrap the Epistemic State

## Objective

Create the initial CEEC beliefs, goals, instruments, and experiments.

## Tasks

- [ ] **F.1 Create instrument beliefs**
  - File:
    - `configs/ceec/instruments.yaml`

Recommended initial instrument beliefs:

```text
I-FROZEN-THETA-AUDIT
I-JACOBIAN-SEPARATION
I-VERTICAL-SLICE-PANEL
I-FLOPS-ESTIMATOR
I-RESOURCE-PROFILER
I-KERNEL-EQUIVALENCE
I-AUTOGRAD-PIPELINE
I-VERIFICATION-LABELS
```

Example:

```yaml
- id: I-FROZEN-THETA-AUDIT
  statement: >
    FrozenThetaAudit detects in-place, alias, mutate-then-restore, and storage
    rebinding mutations of persistent θ within audited episode windows.
  type: instrument
  scope:
    audit_scope: intra_episode_theta
    code_commit: current
  evidence_refs:
    - TODO18 frozen-theta adversarial tests
  status: open
```

- [ ] **F.2 Create hypothesis beliefs**
  - File:
    - `configs/ceec/beliefs.yaml`

Initial beliefs:

```text
B-H1-ADAPTIVE-LOCAL-INVERSES
B-H2-TEMPORAL-PSI-CREDIT
B-H3-STABLE-TRANSIENT-AMPLIFICATION
B-H4-ROUTING-SPARSITY-EFFICIENCY
B-H5-UPDATE-RULE-SPECIALIZATION
```

Example:

```yaml
- id: B-H1-ADAPTIVE-LOCAL-INVERSES
  statement: >
    Slowly adapting feedback projections improve local credit descent quality
    relative to fixed feedback under matched norm and quick budget.
  type: mechanism
  scope:
    substrate: [digital, sparse]
    geometry: [feedforward, recurrent]
    credit: [random_projections, target_inversion]
    budget: quick
  probability:
    low: 0.20
    high: 0.60
  uncertainty: high
  evidence_weight: low
  generality: narrow
  status: open
```

- [ ] **F.3 Create goals**
  - File:
    - `configs/ceec/goals.yaml`

Recommended goals:

```text
G-LOCAL-CREDIT-VIABILITY
G-PSI-PROGRAM-ADAPTATION
G-STABLE-EXPRESSIVITY
G-RESOURCE-PARETO
G-EPISTEMIC-HEALTH
```

Goal utility dimensions:

```yaml
utility:
  science: 0.0
  program: 0.0
  resource: 0.0
  optionality: 0.0
  urgency: 0.0
```

- [ ] **F.4 Create initial experiments**
  - Files:
    - `configs/ceec/experiments/adaptive_local_inverses.yaml`
    - `configs/ceec/experiments/temporal_psi_credit.yaml`
    - `configs/ceec/experiments/stable_transient_amplification.yaml`
    - `configs/ceec/experiments/routing_sparsity_efficiency.yaml`
    - `configs/ceec/experiments/update_rule_specialization.yaml`

Each experiment must include:

```yaml
experiment:
  id: X-...
  question: ...
  rationale: ...
  scope: ...
  target_beliefs: []
  target_goals: []
  design: {}
  prediction: ...
  prediction_probability:
    low: ...
    high: ...
  controls: []
  metrics: []
  budget: quick | standard | nightly
  cost_estimate:
    low: ...
    high: ...
  falsification_criterion: ...
  overturn_criterion: ...
  hard_gates: []
```

- [ ] **F.5 Bootstrap ledger**
  - Command:

    ```bash
    uv run python -m computronium.ceec.cli init
    uv run python -m computronium.ceec.cli bootstrap --config configs/ceec/
    ```

## Acceptance Criteria

- [ ] Instrument beliefs exist.
- [ ] Hypothesis beliefs exist.
- [ ] Goals exist.
- [ ] Initial experiments are pre-registered.
- [ ] Ledger contains bootstrap records.
- [ ] No belief lacks scope or evidence references.

---

# Phase G — CEEC-Governed Experiment Families

This phase executes the first scientific experiments under CEEC.

All experiments obey the CEEC operational loop:

```text
Load state.
Check hygiene/quarantine.
Generate candidates.
Apply hard constraints.
Score valid candidates.
Select and record decision.
Pre-register.
Execute.
Record artifacts/evidence/derived.
Update beliefs.
Apply gates/statuses.
Update goals.
Record calibration.
```

---

## Experiment Family 1 — Adaptive Local Inverses

### Objective

Determine whether local credit improves when feedback/inverse projections adapt slowly.

### Target belief

```text
B-H1-ADAPTIVE-LOCAL-INVERSES
```

### Target goal

```text
G-LOCAL-CREDIT-VIABILITY
```

### Primary experiments

#### X-ALI-001 — One-step alignment probe

Question:

```text
Does slow feedback adaptation improve one-step improvement_per_norm relative to fixed feedback?
```

Prediction:

```text
Adaptive feedback increases improvement_per_norm by at least 10% relative to fixed feedback across 3 seeds.
```

Controls:

- fixed random feedback,
- matched norm,
- backprop reference where applicable.

Metrics:

- improvement_per_norm,
- pseudo-gradient alignment,
- feedback alignment,
- walltime.

Evidence kind:

```text
vector
```

Hard gates:

- coordinate_valid,
- seed_plan_3,
- matched_control,
- evaluation_policy_valid,
- no_quarantined_dependencies.

Falsification:

```text
No consistent improvement across seeds, or improvement disappears after norm matching.
```

#### X-ALI-002 — Short trajectory probe

Question:

```text
Does adaptive feedback improve 30-step descent quality?
```

Evidence kind:

```text
curve
```

Metrics:

- loss trajectory,
- descent quality,
- feedback alignment trajectory.

#### X-ALI-003 — Depth scaling probe

Question:

```text
Does adaptive feedback preserve descent quality better than fixed feedback as depth increases?
```

Evidence kind:

```text
tensor
```

Axes:

```text
depth × feedback_mode × seed
```

### Promotion condition

Belief may move toward `promoted` if:

```text
adaptive feedback consistently improves one-step and trajectory metrics
AND controls are matched
AND at least 3 seeds
AND no material defects
AND scope is explicit
```

### Boundary condition

Belief may move toward `boundary` only if:

```text
defect hunt passes
AND known levers exhausted
AND adaptive feedback fails consistently
AND rescue probability is low
```

---

## Experiment Family 2 — Temporal ψ Credit

### Objective

Determine whether frozen-θ ψ adaptation can extend algorithmic horizon using temporal credit.

### Target belief

```text
B-H2-TEMPORAL-PSI-CREDIT
```

### Target goal

```text
G-PSI-PROGRAM-ADAPTATION
```

### Primary experiments

#### X-TPC-001 — Frozen-θ horizon probe

Question:

```text
Does temporal ψ credit extend successful task horizon relative to instantaneous ψ update?
```

Prediction:

```text
Temporal ψ credit increases successful horizon by at least 50% relative to baseline under frozen θ.
```

Controls:

- instantaneous ψ update,
- NullPlasticity where appropriate,
- fixed θ audit.

Metrics:

- successful horizon,
- adaptation steps,
- composition error growth,
- ψ entropy,
- θ invariance.

Evidence kind:

```text
curve
```

Hard gates:

- frozen_theta_audit,
- theta_bitwise_invariant,
- coordinate_valid,
- seed_plan_3,
- no_quarantined_dependencies.

Falsification:

```text
Temporal credit does not extend horizon, or θ invariance fails, or composition error worsens materially.
```

#### X-TPC-002 — Trace-length ablation

Question:

```text
Does trace horizon affect composition error?
```

Axes:

```text
trace_length × task_horizon × seed
```

Evidence kind:

```text
tensor
```

#### X-TPC-003 — Migration probe

Question:

```text
Can temporal ψ credit support task migration A₀ → A₁ without changing θ?
```

Metrics:

- migration time,
- task loss,
- θ invariance,
- ψ entropy.

### Boundary condition

Boundary may be declared only if:

```text
trace-length, credit strength, task horizon, and wiring have been checked
AND ψ pathway is proven live
AND composition error remains superlinear
AND rescue probability is low
```

---

## Experiment Family 3 — Stable Transient Amplification

### Objective

Find coordinates where asymptotic stability and transient amplification coexist beneficially.

### Target belief

```text
B-H3-STABLE-TRANSIENT-AMPLIFICATION
```

### Target goal

```text
G-STABLE-EXPRESSIVITY
```

### Primary experiments

#### X-STA-001 — Stability separation probe

Question:

```text
Can we identify coordinates with ρ ≤ limit and σ_max > 1?
```

Metrics:

- spectral_radius_from_jacobian,
- dominant_singular_value,
- directional amplification,
- settling time.

Evidence kind:

```text
vector
```

Hard gates:

- jacobian_separation_instrument_valid,
- coordinate_valid,
- seed_plan_3.

#### X-STA-002 — Noise robustness probe

Question:

```text
Do stable transiently amplifying coordinates improve noise robustness relative to contractive baselines?
```

Evidence kind:

```text
tensor
```

Axes:

```text
rho_target × sigma_target × noise_level × seed
```

#### X-STA-003 — Expressivity probe

Question:

```text
Does transient amplification increase distinguishable attractors or task accuracy without destabilizing settling?
```

Metrics:

- attractor count,
- basin stability,
- task accuracy,
- settling failures.

### Boundary condition

Boundary may be declared only if:

```text
nonnormal initializations tested
AND spectral constraints tested
AND noise levels tested
AND settling pathology excluded
AND rescue probability low
```

---

## Experiment Family 4 — Routing × Sparsity Efficiency

### Objective

Determine whether routing produces measurable resource benefits.

### Target belief

```text
B-H4-ROUTING-SPARSITY-EFFICIENCY
```

### Target goal

```text
G-RESOURCE-PARETO
```

### Primary experiments

#### X-RSE-001 — Effective operations probe

Question:

```text
Does routing reduce effective operations relative to dense baseline on a sparse task?
```

Prediction:

```text
Routing reduces effective ops by at least 10% with accuracy loss ≤ 1 point.
```

Metrics:

- effective ops,
- active units,
- memory,
- walltime,
- accuracy,
- gate entropy.

Evidence kind:

```text
tensor
```

Hard gates:

- resource_profiler_instrument_valid,
- matched_compute_baseline,
- coordinate_valid,
- seed_plan_3.

Falsification:

```text
Routing overhead removes savings, or gates collapse, or task lacks exploitable sparsity.
```

#### X-RSE-002 — Matched-compute comparison

Question:

```text
At matched effective ops, does routed system maintain or improve task performance?
```

#### X-RSE-003 — Damage recovery probe

Question:

```text
Does routing improve recovery after unit or route damage?
```

Metrics:

- pre-damage accuracy,
- post-damage accuracy,
- recovery steps,
- route redistribution.

### Boundary condition

Boundary may be declared only if:

```text
routing overhead measured
AND task sparsity verified
AND gate collapse checked
AND substrate cost modeled
AND known routing levers exhausted
```

---

## Experiment Family 5 — Update-Rule Specialization

### Objective

Determine whether assigning different update rules to different parameter roles improves learning or stability.

### Target belief

```text
B-H5-UPDATE-RULE-SPECIALIZATION
```

### Target goal

```text
G-LOCAL-CREDIT-VIABILITY
```

### Primary experiments

#### X-USU-001 — Role ablation one-step probe

Question:

```text
Does role-specific update assignment improve one-step improvement_per_norm relative to uniform update?
```

Roles:

- forward weights,
- feedback weights,
- routing/ψ parameters,
- readout.

Evidence kind:

```text
tensor
```

Axes:

```text
credit × update_main × update_feedback × seed
```

#### X-USU-002 — Stability interaction probe

Question:

```text
Do spectral or orthogonal updates stabilize local credit coordinates?
```

Metrics:

- ρ,
- σ_max,
- loss descent,
- gradient norm.

#### X-USU-003 — Trajectory probe

Question:

```text
Do hybrid updates improve 30-step descent quality?
```

Evidence kind:

```text
curve
```

### Boundary condition

Boundary may be declared only if:

```text
norm matching checked
AND role assignment wiring checked
AND update instability excluded
AND multiple credit rules tested
AND rescue probability low
```

---

# Phase H — Calibration, Audit, and Reporting

## Objective

Ensure the Epistemic Foundry remains honest over time.

## Tasks

- [ ] **H.1 Implement calibration tracker**
  - File:
    - `computronium/ceec/calibration.py`
  - For pre-registered predictions with probabilities, record:
    - prediction,
    - probability or interval,
    - outcome,
    - Brier score where point probability exists,
    - log score where appropriate,
    - scope,
    - timestamp.

- [ ] **H.2 Implement calibration report**
  - Command:

    ```bash
    uv run python -m computronium.ceec.cli calibration-report
    ```

  - Report should include:
    - predicted versus observed success,
    - average Brier score,
    - promotion durability,
    - boundary durability,
    - reopen rate,
    - quarantine rate,
    - override rate.

- [ ] **H.3 Implement audit command**
  - Command:

    ```bash
    uv run python -m computronium.ceec.cli audit
    ```

  - Audit checks:
    - beliefs without evidence,
    - beliefs without scope,
    - scalar-only primary evidence where structure declared,
    - status changes without gate outcomes,
    - decisions without selected experiment rationale,
    - quarantined dependencies used in active experiments,
    - missing artifacts for evidence,
    - missing calibration outcomes for completed predicted experiments.

- [ ] **H.4 Generate Epistemic Foundry report**
  - File:
    - `docs/ceec/EPISTEMIC_FOUNDRY_REPORT.md`
  - Contents:
    - active beliefs,
    - promoted claims,
    - boundaries,
    - quarantines,
    - reopened beliefs,
    - experiment outcomes,
    - calibration summary,
    - mechanism schemas.

- [ ] **H.5 Generate mechanism schemas**
  - File:
    - `docs/ceec/MECHANISM_SCHEMAS.md`
  - Schemas are derived objects and/or generality beliefs.
  - Must include:
    - supporting scopes,
    - evidence refs,
    - failure boundaries,
    - verification levels.

## Tests

- [ ] `tests/ceec/test_calibration.py`
- [ ] `tests/ceec/test_integration_loop.py`

Required integration test:

```text
Initialize ledger.
Bootstrap beliefs/goals.
Select experiment.
Record decision.
Pre-register.
Simulate execution.
Record artifact/evidence/derived.
Update belief.
Evaluate gate.
Record calibration.
Run audit.
```

## Acceptance Criteria

- [ ] Calibration records exist.
- [ ] Audit detects violations.
- [ ] Reports can be generated.
- [ ] Integration loop passes.

---

## 12. CLI Design

Initial CLI commands:

```bash
# Initialize ledger
uv run python -m computronium.ceec.cli init

# Bootstrap from configs
uv run python -m computronium.ceec.cli bootstrap --config configs/ceec/

# Add objects manually
uv run python -m computronium.ceec.cli add-artifact --path <path> --type log
uv run python -m computronium.ceec.cli add-evidence --from-yaml <file.yaml>
uv run python -m computronium.ceec.cli add-derived --from-yaml <file.yaml>
uv run python -m computronium.ceec.cli add-belief --from-yaml <file.yaml>
uv run python -m computronium.ceec.cli add-goal --from-yaml <file.yaml>
uv run python -m computronium.ceec.cli add-experiment --from-yaml <file.yaml>

# Selection
uv run python -m computronium.ceec.cli propose --limit 16
uv run python -m computronium.ceec.cli decide --config configs/ceec/profile.yaml

# Status and gates
uv run python -m computronium.ceec.cli gate-evaluate --belief B-...
uv run python -m computronium.ceec.cli status-history --belief B-...
uv run python -m computronium.ceec.cli quarantine-report

# Audit and reports
uv run python -m computronium.ceec.cli audit
uv run python -m computronium.ceec.cli calibration-report
uv run python -m computronium.ceec.cli export --output ceec/exports/
```

Optional later integration:

```bash
comp ceec init
comp ceec decide
comp ceec audit
comp ceec report
```

---

## 13. Hard Gates for Computronium Experiments

The following hard gates apply before scoring.

### G-HARD-0 — Coordinate validity

```text
SystemConfig.validate(coordinate) must pass.
```

If invalid, result is `inert`, not negative capability evidence.

### G-HARD-1 — Pre-registration complete

Experiment must have:

- question,
- rationale,
- prediction,
- controls,
- metrics,
- budget,
- falsification criterion,
- overturn criterion.

### G-HARD-2 — No quarantined dependencies

Candidate must not depend on quarantined instrument beliefs or quarantined evidence.

### G-HARD-3 — Controls present or justified

Positive claims require matched controls.

### G-HARD-4 — Seed plan present

Empirical promotion normally requires at least 3 seeds.

### G-HARD-5 — Evaluation policy present

Must specify:

- task,
- split,
- budget,
- metric definitions,
- evaluation timing.

### G-HARD-6 — Structured evidence plan present

If structure exists, probe must emit structured evidence.

### G-HARD-7 — Budget within limit

No unapproved benchmark escalation.

### G-HARD-8 — Frozen-θ audit for ψ-only claims

ψ-only adaptation experiments require FrozenThetaAudit and θ invariance checks.

### G-HARD-9 — Identity card for new primitives

Any new Credit, Update, or Plasticity primitive must have an AlgorithmIdentityCard.

### G-HARD-10 — Instrument validity

Claims depending on an instrument require that instrument belief not be quarantined.

---

## 14. Promotion and Boundary Gates

### Promotion gates

A positive belief may become `promoted` only if:

```text
probability_low >= 0.95
AND MultiSeed
AND MatchedControl
AND EvaluationPolicyValid
AND DefectAudit
AND Reproduction
AND ScopeExplicit
AND NoQuarantinedDependencies
```

### Boundary gates

A negative belief may become `boundary` only if:

```text
rescue_probability_high <= 0.05
AND DefectHuntPassed
AND IntegrityChecksPassed
AND KnownLeversExhausted
AND MatchedControl
AND MultiSeedWhereFeasible
AND ScopeExplicit
```

### Defect hunt checklist

For learning probes, defect hunt should check:

- `requires_autograd` contract,
- detached settle graph,
- feedback matrices seeded/frozen as intended,
- optimizer parameter groups,
- ψ write path liveness,
- gate collapse,
- norm matching,
- evaluation pairing,
- label leakage,
- config digest mismatch,
- stale code or artifacts,
- numerical instability,
- accidental clipping,
- dead gradients,
- inactive routing,
- missing controls.

---

## 15. Quarantine Policy

### Instrument beliefs to monitor

```text
I-FROZEN-THETA-AUDIT
I-JACOBIAN-SEPARATION
I-VERTICAL-SLICE-PANEL
I-FLOPS-ESTIMATOR
I-RESOURCE-PROFILER
I-KERNEL-EQUIVALENCE
I-AUTOGRAD-PIPELINE
I-VERIFICATION-LABELS
```

### Quarantine triggers

Quarantine if:

- known defect affects measurement,
- estimator mislabeled,
- audit incomplete,
- config/provenance mismatch,
- dependent artifact stale,
- correction record invalidates previous measurement,
- live patch not verified.

### Quarantine effects

While quarantined:

- dependent beliefs cannot be promoted,
- dependent beliefs cannot establish boundaries,
- dependent experiments are blocked or deprioritized,
- derived objects using quarantined inputs are flagged.

---

## 16. Calibration Policy

### When calibration is required

Calibration records are required for:

- pre-registered experiment predictions with explicit probability,
- promotion predictions,
- boundary rescue probability estimates,
- reopen trigger estimates,
- oracle expected-value predictions when explicit.

### Scores

If point probability exists:

```text
Brier = (p - y)^2
LogScore = y log p + (1 - y) log(1 - p)
```

If interval probability exists:

- store interval,
- do not compute Brier unless a declared point reduction exists.

### Review triggers

Review calibration if:

- promotion reversal rate is high,
- boundary reopen rate is high,
- Brier score drifts upward,
- override rate increases,
- quarantine rate spikes.

---

## 17. Migration of Existing Evidence

Do not attempt to migrate everything at once.

Priority order:

### Priority 1 — Instruments

Migrate evidence supporting instrument beliefs:

- FrozenThetaAudit tests,
- Jacobian separation tests,
- verification label tests,
- vertical slice gate,
- kernel equivalence tests.

### Priority 2 — Existing campaign records

Migrate:

- `results/vertical_slice/claim_record.json`
- `results/mechanistic_study/claim_record.json`
- `results/memory_stability/claim_record.json`

As:

```text
Artifact + Evidence + Derived
```

Not as beliefs.

### Priority 3 — Corrections

Migrate:

- `docs/CORRECTIONS.md`

As:

- defect evidence,
- instrument quarantine or reopening triggers where relevant.

---

## 18. Definition of Done

The Epistemic Foundry plan is complete when all of the following are true.

### CEEC implementation

- [x] `computronium/ceec/` module exists.
- [x] Object models implemented.
- [x] SQLite ledger implemented.
- [x] Artifact ingestion implemented.
- [x] Evidence ingestion implemented.
- [x] Derived ingestion implemented.
- [x] Belief revisions implemented.
- [x] Gate engine implemented.
- [x] Quarantine propagation implemented.
- [x] Decision ledger implemented.
- [x] Calibration tracker implemented.
- [x] Audit command implemented.

### Governance

- [x] Computronium CEEC profile written.
- [x] Ledger policy written.
- [x] Pre-registration policy written.
- [x] Calibration policy written.
- [x] Instrument beliefs bootstrapped.
- [x] Hypothesis beliefs bootstrapped.
- [x] Goals bootstrapped.
- [x] Initial experiments pre-registered.

### Experiment execution

At least the following have CEEC records:

- [x] Adaptive Local Inverses probe (X-ALI-001, round 2).
- [ ] Temporal ψ Credit probe (blocked on temporal-ψ mechanism build).
- [x] Stable Transient Amplification probe (X-STA-001, round 3).
- [x] Routing × Sparsity Efficiency probe (X-RSE-001, round 3).
- [x] Update-Rule Specialization probe (X-USU-001, round 3).

Each produces at least one of:

- [ ] evidence and derived objects,
- [ ] gated belief update,
- [ ] boundary with defect hunt,
- [ ] quarantine,
- [ ] reopening,
- [ ] calibration record.

### Quality

- [x] CEEC tests pass.
- [x] Integration loop test passes.
- [ ] Existing Computronium test suite remains green.
- [x] Pyright passes under repository standard.
- [x] Ruff format and check pass.
- [ ] Verification label tests pass.
- [ ] Identity-card hook passes if new primitives introduced.

### Documentation

- [x] `docs/ceec/COMPUTRONIUM_PROFILE.md` exists.
- [x] `docs/ceec/LEDGER_POLICY.md` exists.
- [x] `docs/ceec/INSTRUMENT_BELIEFS.md` exists.
- [x] `docs/ceec/EPISTEMIC_FOUNDRY_REPORT.md` exists.
- [x] `docs/ceec/MECHANISM_SCHEMAS.md` exists.
- [x] README updated only if evidence gates pass.

---

## 19. Minimal Viable Implementation

If time is constrained, the minimum acceptable version is:

### Must have

1. CEEC profile.
2. SQLite ledger.
3. Core object models.
4. Gate engine for promotion/boundary/quarantine.
5. Decision ledger.
6. Bootstrap beliefs/goals/instruments.
7. One CEEC-governed experiment family: Adaptive Local Inverses.
8. One CEEC-governed experiment family: Temporal ψ Credit.
9. Audit command.
10. Basic calibration ledger.

### Deferred

- Stable Transient Amplification.
- Routing × Sparsity Efficiency.
- Update-Rule Specialization.
- Full migration of all TODO18 records.
- Advanced posterior probability models.
- Portfolio optimization.
- Web dashboard.

Even the minimal version is valuable if it produces gated beliefs and auditable decisions.

---

## 20. Recommended Execution Order

### Step 1 — Governance first

Complete Phase A.

Do not write ledger code before thresholds and hard gates are defined.

### Step 2 — Ledger core

Complete Phase B.

This is the foundation.

### Step 3 — Gates and quarantine

Complete Phase C.

This prevents epistemic regressions.

### Step 4 — Decision engine

Complete Phase D.

This makes the Oracle CEEC-compliant.

### Step 5 — Evidence adapter

Complete Phase E.

This connects probes to CEEC.

### Step 6 — Bootstrap

Complete Phase F.

This creates the initial epistemic state.

### Step 7 — Run first experiments

Prioritize:

1. Adaptive Local Inverses.
2. Temporal ψ Credit.

Then:

3. Routing × Sparsity Efficiency.
4. Stable Transient Amplification.
5. Update-Rule Specialization.

### Step 8 — Calibration and report

Complete Phase H.

This closes the loop.

---

## 21. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| CEEC becomes bureaucratic overhead | Use lightweight quick-mode records for probes; require minimal fields only |
| Fake probability precision | Prefer intervals and declared methods |
| Goal utility contaminates belief | Enforce module separation and tests |
| Hard gates bypassed by score | Hard-constraint filter before scoring; tests |
| Quarantine too aggressive | Scope quarantine to material dependencies; record rationale |
| Quarantine too weak | Instrument beliefs block dependent claims when invalid |
| Ledger grows unwieldy | SQLite indexes, exports, and artifact content addressing |
| Migration stalls experiments | Migrate only instruments and active hypotheses first |
| Boundary declarations premature | Require defect hunt and lever exhaustion |
| Promotion declarations premature | Require gates and multi-seed evidence |
| Oracle over-optimism | Calibration ledger and review triggers |
| Structured evidence lost | Probe adapter enforces evidence kind |
| Invalid coordinates treated as failures | Use `inert` evidence kind |
| Existing records overtrusted | Treat old records as artifacts/evidence, not beliefs |

---

## 22. Final Normative Statement

The Epistemic Foundry is complete only when the research process is represented as:

```text
Artifact
  → Evidence
  → Derived
  → Scoped Probabilistic Beliefs
  → Gated Statuses
  → Goal Priorities
  → Expected-Value Experiments
  → Auditable Decisions
```

and when the following hold:

```text
No belief without evidence.
No belief without scope.
No scalar-only primary evidence when structure exists.
No promotion without gates.
No boundary without defect hunt.
No boundary while decisive levers remain untested.
No reopening without credible trigger.
No trusted use of quarantined dependencies.
No priority without cost and dependency awareness.
No scientific conclusion without explicit scope.
```

This is the final actionable plan for implementing CEEC and using it to govern the next phase of Computronium experiments.

