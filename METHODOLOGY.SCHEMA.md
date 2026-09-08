# Computronium Epistemic Experiment Calculus  
## CEEC-Core v1.0 — Final Core Specification

**Status:** Final core specification.  
**Scope:** This document defines the normative core of CEEC: a self-contained formal governance system for evidence, beliefs, goals, experiments, statuses, scheduling, and audit in an empirical research program.

CEEC-Core is intentionally compact. It defines the invariants and minimal object model required for capability, honesty, and auditability. Implementation details, mathematical methods, domain examples, and tooling conventions are outside the core and MAY be provided by profiles or appendices.

---

## 1. Interpretation

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as normative requirements.

An implementation is CEEC-Core compliant only if it satisfies all mandatory requirements in this specification.

---

## 2. Purpose

CEEC-Core governs:

1. **Evidence** — immutable, structured experimental observations.
2. **Derived objects** — summaries, contrasts, relations, and comparisons computed from evidence.
3. **Beliefs** — scoped, probabilistic claims supported by evidence.
4. **Goals** — valued objectives with utility, cost, and dependencies.
5. **Experiments** — pre-registered interventions chosen to reduce uncertainty or advance goals.
6. **Statuses** — governed transitions among epistemic states.
7. **Decisions** — auditable records of experiment selection and status changes.

The central design principle is:

> **Evidence is primary. Beliefs are derived. Statuses are gated. Goals are separate. Experiments are chosen by expected value per cost under hard constraints.**

---

## 3. Design Principles

A CEEC-Core implementation MUST respect the following principles.

### P1. Evidence before belief

A scientific belief MUST NOT exist without explicit evidence references.

A claim without evidence is a hypothesis, not a belief.

### P2. Structure before scalarization

Experimental results MUST NOT be reduced to a primary scalar when scientifically important structure exists.

If the underlying result is a curve, vector, tensor, relation, event, distribution, or frontier, that structure MUST be representable and preserved.

Scalar summaries are derived objects.

### P3. Scope before generality

Every belief MUST carry an explicit scope.

A local observation MUST NOT be treated as a general claim unless supported by explicit generality evidence.

### P4. Belief confidence is separate from goal desire

The probability of a claim MUST NOT be inflated because the claim is strategically valuable.

Belief probability answers:

> How strongly is this supported by evidence?

Goal priority answers:

> How valuable is it to pursue?

### P5. Hard gates are not negotiable by score

Some conditions are logical constraints, not weighted features.

A high expected value, priority, or utility score MUST NOT override a hard gate.

### P6. Progression and relationship are first-class

Learning curves, trajectories, factorial tensors, interaction surfaces, comparisons, dominance relations, and events MUST be representable without collapsing into isolated datapoints.

### P7. Efficient decisions use compact derived summaries

Schedulers and prioritizers MAY use scalar summaries, but those summaries MUST reference structured evidence and MUST be recomputable.

### P8. All important changes require provenance

Every promotion, boundary assignment, reopening, quarantine, override, and experiment selection MUST record:

- evidence or derived objects used;
- gates passed or failed;
- assumptions;
- decision rationale;
- relevant provenance, such as artifact hashes, config hashes, code versions, or equivalent identifiers.

---

## 4. Core Invariants

The following invariants are mandatory.

```text
No belief without evidence.
No belief without scope.
No scalar-only primary evidence when structure exists.
No promotion without gates.
No boundary without defect hunt and lever exhaustion.
No reopening without a credible trigger.
No trusted use of quarantined dependencies.
No goal priority influencing belief probability.
No experiment selection overriding hard constraints.
No status change or selection decision without provenance.
```

---

## 5. Object Model

CEEC-Core defines the following primary objects:

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
```

The epistemic flow is:

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

The system MUST support both directions:

1. **Scientific inference:** evidence updates beliefs.
2. **Experimental planning:** beliefs and goals select experiments.

---

## 6. Scope

A `Scope` defines the conditions under which evidence, beliefs, goals, or experiments apply.

A scope MUST be a non-empty map from dimension names to values, ranges, sets, or patterns.

Example:

```yaml
scope:
  architecture: transformer
  credit: local_contrastive
  update: muon
  task: next_token_probe
  budget: 600_steps
```

Requirements:

- Every belief MUST have an explicit scope.
- Every experiment SHOULD have an explicit scope.
- Every evidence object SHOULD have an explicit scope.
- Scope MUST be sufficient to prevent accidental overgeneralization.
- A scope MAY include dimensions such as architecture, task, substrate, optimizer, credit rule, budget, seed policy, evaluation policy, and code provenance.

A claim without scope is invalid as a CEEC belief.

---

## 7. Artifact

An `Artifact` is an immutable raw forensic object.

Artifacts are the lowest layer of provenance.

Minimal schema:

```yaml
artifact:
  id: string
  uri_or_hash: string
  type: log | tensor | curve | metrics | checkpoint | config | trace | other
  provenance:
    probe: optional string
    run_id: optional string
    code_commit: optional string
    config_hash: optional string
    timestamp: optional datetime
```

Requirements:

- Artifacts MUST be append-only.
- Artifacts MUST NOT be overwritten.
- Artifacts SHOULD be content-addressed or hash-linked where practical.
- Artifacts MUST be referenceable by evidence objects.
- Raw artifacts MUST remain accessible for audit, even if scheduling uses derived summaries.

Examples of artifacts:

- training logs;
- per-step curves;
- seed-wise metric tables;
- evaluation outputs;
- config files;
- code commit identifiers;
- resource measurements;
- probe outputs;
- error traces.

---

## 8. Evidence

An `Evidence` object is a structured scientific record referencing one or more artifacts.

Minimal schema:

```yaml
evidence:
  id: string
  kind: scalar | interval | vector | tensor | curve | event | distribution | frontier | inert | missing
  scope: {}
  axes: {}
  values_ref: string
  uncertainties: optional
  artifact_refs: []
  quality:
    seeds: optional integer
    controls: optional boolean
    instrument_valid: optional boolean
    freshness: optional string
    stale: boolean
  defects: []
  notes: optional string
```

### 8.1 Required evidence kinds

A CEEC-Core implementation MUST support at least the following evidence kinds:

| Kind | Meaning |
|---|---|
| `scalar` | A single value, ideally with uncertainty. |
| `interval` | A range with confidence, credibility, or uncertainty semantics. |
| `vector` | An ordered multi-metric result. |
| `tensor` | A multi-axis factorial or grid result. Matrices are rank-2 tensors. |
| `curve` | A value over a progression axis, such as step, time, budget, or sequence length. |
| `event` | A discrete occurrence, such as gate shutdown, divergence, plateau, or failure. |
| `inert` | An unrealizable or no-op condition. |
| `missing` | An absent, failed, or unrun condition. |

Optional but RECOMMENDED kinds:

| Kind | Meaning |
|---|---|
| `distribution` | A posterior, bootstrap, sampling, or empirical distribution. |
| `frontier` | A Pareto or multi-objective boundary. |

### 8.2 Evidence rules

- Evidence MUST reference at least one artifact or explicitly declare why no artifact exists.
- Evidence MUST NOT be mutable in a way that destroys prior recorded values.
- Evidence metadata MAY be versioned, but previous versions MUST remain recoverable.
- If structure exists, evidence MUST preserve or reference that structure.
- Missing or inert cells MUST be explicitly labeled.
- Missing or inert cells MUST NOT be silently zeroed.
- An inert or unrealizable cell MUST NOT be treated as negative capability evidence unless the claim is specifically about realizability.
- Evidence SHOULD record quality information, including seeds, controls, staleness, and instrument validity.
- Evidence quality SHOULD affect belief weighting.

### 8.3 Structured evidence requirement

If an experiment produces:

- a learning curve,
- a training trajectory,
- a factorial tensor,
- a multi-metric vector,
- a relation,
- an event sequence,
- a distribution,
- or a Pareto frontier,

then the primary evidence MUST NOT be only a final scalar summary.

Scalar summaries MAY exist as derived objects.

---

## 9. Derived

A `Derived` object is a compact derived summary or relation computed from evidence.

`Derived` unifies summaries and relations.

Minimal schema:

```yaml
derived:
  id: string
  type: summary | relation
  inputs: []
  left: optional
  right: optional
  operator: string
  parameters: {}
  value: scalar | interval | vector | tensor | distribution | boolean
  probability_positive: optional float
  probability_material: optional float
  assumptions: []
  checks: []
  scope: {}
  provenance:
    code_hash: optional string
    method: optional string
    timestamp: optional datetime
```

### 9.1 Summary objects

A summary is a derived reduction or analysis of evidence.

Examples:

- mean;
- median;
- variance;
- credible interval;
- confidence interval;
- contrast;
- interaction effect;
- slope;
- peak;
- peak time;
- asymptote;
- decay rate;
- area under curve;
- change point;
- realizability check.

### 9.2 Relation objects

A relation is a derived relationship between objects.

Relation inputs MAY include:

- evidence objects;
- other derived objects;
- beliefs;
- experiments;
- goals;
- scoped conditions.

Examples:

- greater than;
- less than;
- within epsilon;
- dominance;
- Pareto dominance;
- curve dominance;
- replication;
- contradiction;
- mechanism-for;
- generalization;
- control relation;
- sign interaction;
- magnitude interaction.

Relations are first-class scientific objects.

### 9.3 Required derived capabilities

A CEEC-Core implementation MUST support derived operations sufficient to express at least:

| Capability | Meaning |
|---|---|
| central tendency | mean, median, or equivalent |
| dispersion | variance, spread, interval, or uncertainty |
| contrast | difference between conditions |
| interaction | factorial or conditional interaction effect |
| progression summary | slope, peak, asymptote, change point, or equivalent |
| comparison | greater than, less than, or practical equivalence |
| dominance | pairwise or Pareto-style dominance |
| validity check | realizability, control validity, or instrument validity |

The operator vocabulary MAY be extensible.

### 9.4 Derived-object rules

- Every derived object MUST reference its input evidence or derived objects.
- Every derived object MUST identify its operator or method.
- Every derived object MUST be recomputable or include sufficient provenance to audit its computation.
- Derived objects MUST NOT replace structured evidence as the primary scientific record when structure matters.
- Derived objects MAY be used for scheduling, prioritization, and belief update.
- Assumptions and validity checks SHOULD be recorded.

---

## 10. Belief

A `Belief` is a scoped, probabilistic claim supported by evidence.

Minimal schema:

```yaml
belief:
  id: string
  statement: string
  type: capability | mechanism | boundary | instrument | generality | realizability | defect | hygiene | other
  scope: {}
  probability: float
  uncertainty: float | interval | enum
  evidence_weight: float | enum
  generality: float | enum
  evidence_refs: []
  derived_refs: []
  dependencies: []
  status: open | promoted | boundary | quarantined
  gates:
    gate_outcome_refs: []
  status_history: []
  posterior_method: optional string
```

### 10.1 Belief requirements

Every belief MUST have:

- a unique identifier;
- a statement or proposition;
- an explicit scope;
- a probability or probability estimate;
- an uncertainty representation;
- evidence weight;
- generality estimate;
- at least one evidence or derived reference;
- a status;
- status history;
- gate information when status is `promoted` or `boundary`.

A belief MUST NOT be stored as a bare scalar probability without scope and evidence references.

### 10.2 Belief probability

The probability of a belief MUST be a value in:

\[
[0,1]
\]

or an interval over that range.

If an implementation uses posterior distributions, bootstrap distributions, Bayes factors, or other methods, the method SHOULD be declared.

The implementation MUST declare at least one of:

- posterior method;
- update rule;
- evidence weighting policy;
- uncertainty representation.

A belief probability MUST NOT be set or modified by goal priority, strategic value, or desired outcome alone.

### 10.3 Confidence representation

Belief confidence MUST be represented using at least four components:

| Component | Meaning |
|---|---|
| `probability` | Probability that the proposition is true under scope. |
| `uncertainty` | Dispersion, credible range, or confidence uncertainty. |
| `evidence_weight` | Strength, quality, or effective support from evidence. |
| `generality` | Breadth of validated scope. |

A scalar confidence MAY be used for scheduling, but the four components MUST be preserved for audit.

### 10.4 Belief types

The belief type MUST be recorded.

Recommended vocabulary:

| Type | Meaning |
|---|---|
| `capability` | A system can do something under scope. |
| `mechanism` | A causal or explanatory structure exists. |
| `boundary` | A limitation holds under scope. |
| `instrument` | A measurement tool or method is valid. |
| `generality` | A claim transfers across scopes. |
| `realizability` | A contract, pathway, or configuration is executable. |
| `defect` | A known flaw exists. |
| `hygiene` | A cleanup, audit, or validity claim. |

Additional types MAY be used if documented.

### 10.5 Belief dependencies

A belief MAY depend on:

- other beliefs;
- instrument beliefs;
- evidence objects;
- derived objects;
- code/config provenance;
- measurement assumptions.

Dependencies MUST be explicit where known.

If a dependency becomes invalid, suspect, or stale, dependent beliefs MUST be re-evaluated, discounted, or quarantined.

### 10.6 Staleness and decay

Beliefs dependent on implementation details SHOULD decay or be quarantined when relevant code, configuration, instrumentation, or environment changes.

If an instrument belief is invalid or suspected invalid, dependent beliefs MUST NOT be used for promotion or boundary decisions until revalidated.

---

## 11. Goal

A `Goal` is a desired outcome with strategic value.

Goals are separate from beliefs.

Minimal schema:

```yaml
goal:
  id: string
  statement: string
  kind: terminal | instrumental | hygiene | infrastructure | boundary | promotion | audit | custom
  utility:
    dimensions: map<string, float>
  scalar_utility: optional float
  cost_estimate: float | interval
  prerequisites: []
  linked_beliefs: []
  priority: optional float
  status: active | blocked | completed | deferred
```

### 11.1 Goal requirements

Every goal MUST have:

- a unique identifier;
- a statement;
- a utility representation;
- a cost estimate or cost range;
- status.

Goals SHOULD have:

- dependencies or prerequisites;
- linked beliefs;
- priority;
- kind.

### 11.2 Utility

A goal MUST NOT be represented only by a bare scalar priority unless the scalar is derived from a documented utility model.

The goal utility MUST be stored as a structured map of dimensions or as an explicit documented scalarization.

Recommended utility dimensions:

| Dimension | Meaning |
|---|---|
| `science` | Epistemic value or knowledge gain. |
| `program` | Programmatic, flagship, or mission value. |
| `resource` | Resource, efficiency, or substrate value. |
| `optionality` | Future option value. |
| `urgency` | Time sensitivity or blocking impact. |

Additional dimensions MAY be used.

A scalar utility MAY be derived, but the underlying utility dimensions MUST be preserved.

### 11.3 Goal probability and feasibility

A goal MAY have a feasibility estimate derived from linked beliefs and prerequisites.

Goal feasibility MUST NOT alter belief probabilities.

Goal priority SHOULD depend on:

- utility;
- cost;
- feasibility;
- dependencies;
- urgency;
- epistemic debt;
- blocked downstream work.

### 11.4 Epistemic debt

Epistemic debt is unresolved risk in the measurement, instrument, or inference foundation.

Hygiene, audit, instrument-validation, and defect-resolution goals SHOULD receive priority increases proportional to epistemic debt.

---

## 12. Experiment

An `Experiment` is an action that generates evidence.

Minimal schema:

```yaml
experiment:
  id: string
  question: string
  rationale: string
  scope: {}
  target_beliefs: []
  target_goals: []
  design: {}
  prediction: string
  controls: []
  metrics: []
  budget: string
  cost_estimate: float | interval
  falsification_criterion: string
  overturn_criterion: string
  expected_value: optional float | interval
  hard_gates: []
  status: proposed | pre_registered | running | completed | abandoned
```

### 12.1 Experiment requirements

Every experiment MUST have:

1. a question;
2. a rationale or mechanism;
3. at least one target belief or target goal;
4. a design;
5. a pre-registered prediction;
6. metrics;
7. a budget or cost estimate;
8. a falsification criterion;
9. an overturn or promotion criterion.

Where applicable, every experiment MUST have at least one control or an explicit justification for absence of control.

### 12.2 Pre-registration

Before execution, an experiment MUST be recorded in a `pre_registered` or equivalent state.

Pre-registration MUST include:

- question;
- prediction;
- controls;
- metrics;
- budget;
- falsification criterion;
- overturn criterion.

### 12.3 Experiment execution

During execution, the system SHOULD record:

- seed or seed policy;
- config hash;
- code version;
- budget consumed;
- evaluation policy;
- runtime environment if relevant;
- deviations from the pre-registered design.

Deviations MUST be recorded if they affect interpretation.

### 12.4 Experiment evidence

Completed experiments MUST produce evidence records or a documented reason for absence of evidence.

If the experiment fails to run, the result SHOULD be recorded as `missing` or `inert` evidence, not as negative capability evidence unless realizability is the target claim.

---

## 13. Decision

A `Decision` records why an experiment was selected, rejected, overridden, or postponed.

Minimal schema:

```yaml
decision:
  id: string
  timestamp: datetime
  state_hash: string
  candidate_experiments: []
  scores: {}
  selected_experiment: string | null
  overrides: []
  constraints_checked: []
  rationale: string
```

### 13.1 Decision requirements

Decisions MUST be append-only.

Every selected experiment MUST have a decision record.

A decision record MUST include:

- candidate set or reference to candidate generation process;
- scores or ranking rationale;
- selected experiment;
- overrides, if any;
- rationale;
- state hash or equivalent snapshot identifier.

Manual overrides MUST be explicit and MUST NOT silently bypass hard gates.

---

## 14. StatusChange

A `StatusChange` records a change in belief status.

Minimal schema:

```yaml
status_change:
  id: string
  belief_id: string
  timestamp: datetime
  from_status: open | promoted | boundary | quarantined
  to_status: open | promoted | boundary | quarantined
  reason: string
  trigger: string
  gate_refs: []
  evidence_refs: []
  derived_refs: []
  actor: optional string
```

Status changes MUST be append-only.

A status change MUST NOT occur without gate evidence when moving into `promoted` or `boundary`.

---

## 15. GateOutcome

A `GateOutcome` records whether a gate passed, failed, or is unknown.

Minimal schema:

```yaml
gate_outcome:
  id: string
  gate: string
  belief_id: optional string
  experiment_id: optional string
  status: passed | failed | unknown | waived_with_justification
  evidence_refs: []
  derived_refs: []
  rationale: string
  timestamp: datetime
```

### 15.1 Gate rules

- Gates MUST be checkable against evidence, derived objects, or explicit declarations.
- A gate MUST NOT pass by assertion alone when evidence is required.
- Gate outcomes MUST be recorded for promotion and boundary decisions.
- Hard gates MUST NOT be overridden by priority, expected value, or utility.
- A gate MAY be waived only if the waiver is recorded, justified, and allowed by the governance profile.

---

## 16. Belief Status State Machine

CEEC-Core defines four primary belief statuses:

| Status | Meaning |
|---|---|
| `open` | Evidence exists but the claim is not yet promoted or bounded. |
| `promoted` | A positive claim has passed promotion gates. |
| `boundary` | A negative or limiting claim has passed boundary gates. |
| `quarantined` | The belief is suspect due to instrument, dependency, defect, or provenance risk. |

A belief MUST have exactly one primary status.

### 16.1 Reopening

Reopening is a transition, not a primary status.

A boundary belief that becomes doubtful MUST move to `open` with a recorded reopen trigger.

Example:

```yaml
status_change:
  belief_id: b_example
  from_status: boundary
  to_status: open
  reason: reopened
  trigger: strong_untested_mechanism
```

Valid reopen triggers include:

- strong untested rescue mechanism;
- new evidence materially raising rescue probability;
- instrument defect invalidating the previous boundary;
- provenance failure in supporting evidence;
- discovery of a decisive omitted control.

---

## 17. Hard Gates

CEEC-Core defines four mandatory gate families:

1. promotion gates;
2. boundary gates;
3. quarantine gates;
4. reopen gates.

Projects MAY define additional gates. Projects MUST NOT weaken mandatory gates.

Default thresholds are RECOMMENDED, but alternate thresholds MAY be used if explicitly declared.

Default values:

```text
τ_promote = 0.95
τ_boundary = 0.05
ε_reopen = 0.10
```

---

## 18. Promotion Gates

A positive belief MAY become `promoted` only if all required promotion gates pass.

Required promotion gates:

```text
Promoted(φ) requires:
    Probability(φ) ≥ τ_promote
    ∧ MultiSeed(φ)
    ∧ MatchedControl(φ)
    ∧ EvaluationPolicyValid(φ)
    ∧ DefectAudit(φ)
    ∧ Reproduction(φ)
    ∧ ScopeExplicit(φ)
```

### 18.1 MultiSeed

For empirical learning results, `MultiSeed` SHOULD require at least three seeds unless a formal justification is recorded.

Single-seed results MAY support `open` beliefs but MUST NOT normally support promotion.

### 18.2 MatchedControl

A promoted positive claim SHOULD have a matched control condition, unless absence of control is explicitly justified.

Examples of controls:

- gold-standard baseline;
- known-working configuration;
- negative control;
- instrument calibration control;
- matched training or evaluation condition.

### 18.3 EvaluationPolicyValid

Evaluation MUST be valid for the claim.

Where relevant, this includes:

- fixed-step or fixed-budget evaluation;
- fresh-draw evaluation;
- separated training and evaluation data;
- consistent metric definitions;
- no evaluation contamination.

### 18.4 DefectAudit

A promoted claim MUST pass a defect audit.

A defect audit SHOULD check:

- known defects;
- config errors;
- implementation mistakes;
- measurement issues;
- stale code or stale artifacts;
- suspicious instrument behavior.

### 18.5 Reproduction

A promoted claim SHOULD be reproduced under at least one independent or repeated condition, such as:

- additional seed;
- rerun;
- alternate config hash;
- alternate environment;
- independent probe.

### 18.6 ScopeExplicit

The promoted claim MUST state the scope in which it is promoted.

A promotion MUST NOT imply global truth beyond scope.

---

## 19. Boundary Gates

A negative or limiting belief MAY become `boundary` only if all required boundary gates pass.

Required boundary gates:

```text
Boundary(φ) requires:
    RescueProbability(φ) ≤ τ_boundary
    ∧ DefectHuntPassed(φ)
    ∧ IntegrityChecksPassed(φ)
    ∧ KnownLeversExhausted(φ)
    ∧ MatchedControl(φ)
    ∧ MultiSeedWhereFeasible(φ)
    ∧ ScopeExplicit(φ)
```

### 19.1 RescueProbability

`RescueProbability` is the estimated probability that a plausible rescue mechanism, configuration, or untested lever would materially change the negative result.

A boundary claim requires low rescue probability.

### 19.2 DefectHuntPassed

A boundary claim MUST pass a defect hunt.

A defect hunt is stronger than a defect audit. It SHOULD include active search for plausible failure causes, such as:

- broken gradients;
- dead gates;
- incorrect initialization;
- invalid state updates;
- measurement leakage;
- optimizer misconfiguration;
- numerical instability;
- accidental clipping;
- incorrect evaluation pairing;
- stale code or config.

### 19.3 IntegrityChecksPassed

Integrity checks SHOULD include, where relevant:

- signal integrity;
- state integrity;
- update integrity;
- measurement integrity;
- optimizer integrity;
- data integrity;
- evaluation integrity.

The specific checks MUST be appropriate to the claim and scope.

### 19.4 KnownLeversExhausted

A boundary MUST NOT be declared while known decisive levers remain untested.

Known levers MAY include:

- alternative optimizers;
- alternative learning rates;
- alternative schedules;
- alternative initializations;
- alternative architectures;
- alternative credit assignments;
- alternative controls;
- known rescue mechanisms.

If a strong lever is untested, the claim SHOULD remain `open` or be reopened.

### 19.5 Negative result rule

A negative result obtained without a known decisive control MUST NOT be promoted to `boundary`.

---

## 20. Quarantine Gates

A belief MUST be quarantined if a required instrument, measurement, dependency, or provenance element is suspected invalid.

Examples:

- instrument belief is stale;
- measurement defect suspected;
- patch not verified live;
- silent inert contract suspected;
- evaluation uses training data incorrectly;
- covariate pairing misalignment suspected;
- code/config provenance mismatch;
- dependent evidence is quarantined.

Quarantine rule:

```text
Quarantined(b) if:
    depends_on(b, i)
    AND NOT valid(i)
```

While quarantined:

- the belief MUST NOT be used to promote other claims;
- the belief MUST NOT be used to establish boundaries;
- dependent beliefs SHOULD be quarantined or discounted;
- experiments relying on the belief SHOULD be blocked or re-scored.

If instrument validity is unknown, dependent beliefs MUST NOT be used for promotion or boundary decisions until validity is restored.

Effective probability under quarantine MAY be computed as:

\[
P_{\text{effective}}(\phi)
=
P(\phi)
\cdot
P(\text{instrument valid})
\]

but this MUST NOT replace the requirement to quarantine or block dependent decisions when validity is unknown.

---

## 21. Reopen Gates

A boundary belief MUST be reopened if any of the following holds:

```text
there exists a strong untested mechanism
OR new evidence materially raises rescue probability
OR an instrument defect invalidates the old boundary
OR a decisive control was later found to be omitted or invalid
```

Recommended trigger threshold:

\[
P(\text{rescue} \mid \text{new evidence}) > \epsilon_{\text{reopen}}
\]

Default:

\[
\epsilon_{\text{reopen}} = 0.10
\]

A reopened belief MUST move to `open` with a recorded trigger.

---

## 22. Experiment Selection

Experiment selection MUST proceed in two phases:

1. hard-constraint validation;
2. ranking or selection among valid candidates.

### 22.1 Candidate generation

Candidate experiments MAY arise from:

- uncertain high-value beliefs;
- blocked goals;
- pending promotion gates;
- boundary challenges;
- suspected defects;
- untested overturn mechanisms;
- generality tests;
- resource or Pareto tests;
- hygiene or instrument-validation needs.

### 22.2 Hard constraints

Before scoring, candidate experiments MUST be checked against hard constraints.

Hard constraints include:

- missing required control;
- missing required seed plan;
- missing required evaluation policy;
- missing required defect audit for boundary-related claims;
- quarantined dependency;
- impossible or inert configuration without realizability framing;
- budget violation;
- dependency violation;
- missing pre-registration fields.

Candidates failing hard constraints MUST NOT be selected unless a recorded waiver is permitted by the governance profile.

Hard constraints MUST NOT be overridden by score.

### 22.3 Scoring

Valid candidate experiments SHOULD be ranked by expected value per cost.

A minimal scoring form is:

\[
\text{Score}(x)
=
\frac{
\text{ExpectedValue}(x)
}{
\text{Cost}(x)^\gamma
}
\]

where:

- `ExpectedValue(x)` estimates epistemic or goal value;
- `Cost(x)` estimates budget, compute, time, or resource cost;
- \(\gamma\) is a cost penalty parameter.

Expected value MAY include:

- value of information;
- goal utility;
- hygiene value;
- defect-reduction value;
- boundary-overturn value;
- promotion value;
- optionality value.

The scoring model MUST be documented.

### 22.4 Selection rule

The selected experiment SHOULD maximize score subject to budget and dependency constraints:

\[
x^*
=
\arg\max_{x \in \mathcal{X}_{\text{valid}}}
\text{Score}(x)
\]

subject to:

\[
\sum_x c_x \le B
\]

and dependency constraints.

For short sessions, greedy selection is acceptable.

For campaigns, portfolio optimization MAY be used.

### 22.5 Overrides

Manual overrides MUST be recorded.

An override MUST NOT silently bypass a hard gate.

If an override changes the normal ranking, the decision record MUST include:

- reason;
- responsible actor or process;
- affected constraints or scores;
- justification.

---

## 23. Operational Loop

A compliant CEEC-Core session MUST follow this lifecycle.

### Step 1 — Load epistemic state

Load:

- beliefs;
- goals;
- evidence summaries;
- derived objects;
- defects;
- quarantines;
- previous decisions;
- relevant provenance.

Verify staleness where practical.

### Step 2 — Check hygiene and quarantine

If any high-dependency instrument or measurement is invalid or suspected stale:

- quarantine or discount dependent beliefs;
- boost hygiene or audit goals;
- do not interpret dependent negative results as boundaries.

### Step 3 — Generate candidate experiments

Generate candidates from:

- uncertain beliefs;
- blocked goals;
- pending gates;
- boundary challenges;
- defect audits;
- untested strong mechanisms;
- generality tests;
- resource tests.

### Step 4 — Apply hard constraints

Reject or block candidates that fail hard constraints.

### Step 5 — Score valid candidates

Score valid candidates using a documented expected-value-per-cost method.

### Step 6 — Select and pre-register

Select an experiment and record:

- question;
- prediction;
- controls;
- metrics;
- budget;
- falsification criterion;
- overturn criterion.

### Step 7 — Execute

Run the experiment with explicit provenance.

Record deviations if they occur.

### Step 8 — Record evidence

Store artifacts and structured evidence.

Do not store only final scalar values when structure exists.

### Step 9 — Update derived objects

Compute:

- summaries;
- intervals;
- contrasts;
- interactions;
- curve summaries;
- relations;
- dominance checks;
- event detections.

### Step 10 — Update beliefs

Update belief probabilities, uncertainties, weights, and generality estimates.

Apply quarantine where needed.

### Step 11 — Update statuses

Apply the status state machine and gates.

No manual status change without recorded gate evidence.

### Step 12 — Update goals and priorities

Recompute goal priorities where relevant.

### Step 13 — Record decision

Append a decision record.

---

## 24. Calibration and Honesty

CEEC-Core requires mechanisms for calibration and self-review.

For pre-registered predictions with explicit probabilities, the system SHOULD record:

- prediction;
- probability or confidence;
- outcome;
- timestamp;
- scope;
- related belief or experiment.

Recommended scoring rules:

Brier score:

\[
\text{Brier}
=
(p-y)^2
\]

Log score:

\[
\text{LogScore}
=
y \log p + (1-y)\log(1-p)
\]

where:

- \(p\) is predicted probability;
- \(y \in \{0,1\}\) is the outcome.

The system SHOULD track:

- predicted confidence versus observed success rate;
- promotion durability;
- boundary durability;
- reopen rate;
- defect discovery rate;
- quarantine rate;
- override rate.

If calibration drifts materially, the system SHOULD review:

- priors;
- evidence weights;
- thresholds;
- gate definitions;
- cost estimates;
- expected-value models.

A full CEEC implementation SHOULD make calibration tracking mandatory. CEEC-Core requires that a calibration mechanism exist and be usable.

---

## 25. Provenance and Audit

Every important CEEC object MUST be auditable.

At minimum, auditability requires:

- stable identifiers;
- references from beliefs to evidence or derived objects;
- references from derived objects to evidence;
- references from evidence to artifacts;
- status history;
- gate outcomes;
- decision records;
- override records.

Provenance SHOULD include, where relevant:

- artifact hash;
- config hash;
- code commit;
- probe identifier;
- run identifier;
- seed;
- timestamp;
- environment descriptor.

A belief, status, or decision lacking required provenance SHOULD be treated as unverified.

---

## 26. Minimal Compliant Implementation

A minimal CEEC-Core implementation MUST include:

1. **Artifact ledger**
   - immutable raw artifacts;
   - hashes or URIs;
   - provenance metadata.

2. **Evidence ledger**
   - structured evidence;
   - evidence kind;
   - axes or scope;
   - artifact references;
   - quality and defect flags.

3. **Derived ledger**
   - summaries;
   - relations;
   - operators;
   - inputs;
   - assumptions;
   - checks.

4. **Belief ledger**
   - scoped claims;
   - probability;
   - uncertainty;
   - evidence weight;
   - generality;
   - status;
   - gates;
   - status history.

5. **Goal ledger**
   - utility dimensions;
   - cost estimates;
   - dependencies;
   - linked beliefs;
   - priority.

6. **Experiment ledger**
   - pre-registration;
   - controls;
   - predictions;
   - metrics;
   - falsification criteria;
   - overturn criteria;
   - execution status.

7. **Decision ledger**
   - candidate set;
   - scores;
   - selected experiment;
   - overrides;
   - rationale;
   - state hash.

A minimal implementation MAY use:

- YAML or JSON files;
- Markdown ledgers;
- SQLite databases;
- Parquet or CSV artifacts;
- plain-text logs.

The storage medium is not normative. The invariants are normative.

---

## 27. Anti-Patterns

The following are CEEC anti-patterns.

A compliant implementation SHOULD detect or prevent them.

```text
Storing only a final scalar when a curve or tensor exists.
Treating an unrealizable cell as negative capability evidence.
Promoting a single-seed result without justification.
Promoting a claim without a matched control.
Declaring a boundary without defect hunt.
Declaring a boundary while known levers remain untested.
Using goal priority to increase belief probability.
Using a high expected-value score to override a hard gate.
Allowing quarantined instruments to support promotion or boundary decisions.
Silently zeroing missing data.
Changing belief status without recording gate evidence.
Selecting an experiment without a decision record.
Overgeneralizing a local result beyond its scope.
```

---

## 28. Compliance Checklist

An implementation is CEEC-Core compliant if:

```text
✓ Artifacts are immutable and provenance-tagged.
✓ Evidence references artifacts.
✓ Structured evidence preserves available structure.
✓ Scalar summaries are derived, not primary, when structure exists.
✓ Inert and missing cells are explicitly labeled.
✓ Derived objects reference inputs and are recomputable.
✓ Relations are first-class derived objects.
✓ Every belief has explicit scope.
✓ Every belief references evidence or derived objects.
✓ Every belief stores probability, uncertainty, evidence weight, and generality.
✓ Belief confidence is separate from goal utility.
✓ Belief status is one of open, promoted, boundary, quarantined.
✓ Status changes are recorded.
✓ Promotions pass promotion gates.
✓ Boundaries pass boundary gates.
✓ Quarantine propagates to dependent beliefs.
✓ Reopenings are recorded with triggers.
✓ Goals have structured utility and cost estimates.
✓ Goal priority does not alter belief probability.
✓ Experiments are pre-registered.
✓ Experiments include prediction, controls, metrics, budget, falsification, and overturn criteria.
✓ Experiment selection applies hard constraints before scoring.
✓ Selection decisions are logged.
✓ Overrides are explicit and logged.
✓ A calibration mechanism exists.
```

---

## 29. Final Normative Statement

CEEC-Core is satisfied when the research process is represented as:

\[
\text{Artifact}
\rightarrow
\text{Evidence}
\rightarrow
\text{Derived}
\rightarrow
\text{Scoped Probabilistic Beliefs}
\rightarrow
\text{Gated Statuses}
\rightarrow
\text{Goal Priorities}
\rightarrow
\text{Expected-Value Experiments}
\rightarrow
\text{Auditable Decisions}
\]

and when the following invariants hold:

\[
\text{No belief without evidence.}
\]

\[
\text{No belief without scope.}
\]

\[
\text{No scalar-only primary evidence when structure exists.}
\]

\[
\text{No promotion without gates.}
\]

\[
\text{No boundary without defect hunt.}
\]

\[
\text{No boundary while decisive levers remain untested.}
\]

\[
\text{No reopening without a credible trigger.}
\]

\[
\text{No trusted use of quarantined dependencies.}
\]

\[
\text{No priority without cost and dependency awareness.}
\]

\[
\text{No scientific conclusion without explicit scope.}
\]

This core specification preserves the full epistemic capability of CEEC while remaining compact, implementable, and auditable.
