# Computronium Epistemic Experiment Calculus  
## CEEC v1.0 — A Formal Specification for Belief, Goal, Evidence, and Experiment Governance

**Status:** Final specification.  
**Scope:** This document defines a self-contained, complete, and elegant formal system for planning, recording, analyzing, prioritizing, and promoting scientific experiments within Computronium or any comparable empirical research program.

The specification governs:

1. **Evidence** — structured, immutable, vector-, range-, curve-, tensor-, and relation-valued experimental results.
2. **Beliefs** — probabilistic, scoped, evidence-weighted claims about mechanisms, capabilities, boundaries, instruments, and generality.
3. **Goals** — utility-bearing objectives with priority, cost, dependencies, and strategic value.
4. **Experiments** — interventions selected to reduce important uncertainty or advance high-value goals.
5. **Statuses** — disciplined transitions among `Open`, `Promoted`, `Boundary`, `Reopened`, and `Quarantined`.
6. **Scheduling** — efficient selection of next experiments under budget, dependency, and integrity constraints.

The central design principle is:

> **Evidence is primary. Beliefs are derived. Statuses are gated. Goals are separate. Experiments are chosen by expected value per cost.**

---

## 1. Design Principles

A compliant implementation MUST respect the following principles.

### P1. Evidence before belief

No scientific belief may exist without explicit evidence references.

\[
\text{Belief} \Rightarrow \text{Evidence}
\]

A belief without evidence is a hypothesis, not a belief.

---

### P2. Structure before scalarization

Experimental results MUST NOT be reduced to a single scalar before structured evidence has been recorded.

Scalars such as accuracy, loss, priority, or confidence are derived objects.

The canonical order is:

\[
\text{Raw Evidence}
\rightarrow
\text{Structured Evidence}
\rightarrow
\text{Summaries / Relations}
\rightarrow
\text{Beliefs}
\rightarrow
\text{Priorities}
\]

---

### P3. Scope before generality

Every belief MUST carry an explicit scope.

A claim is never globally true merely because it was observed locally.

Example:

\[
P(
\text{local credit works}
\mid
\text{probe-scale transformer, tested schedules}
)
\]

is distinct from:

\[
P(
\text{local credit works}
\mid
\text{all transformer scales}
)
\]

---

### P4. Belief confidence is separate from goal desire

The probability of a claim MUST NOT be inflated because the claim is strategically valuable.

\[
P(\phi)
\neq
U(\phi)
\]

Belief confidence answers:

> How strongly is this supported by evidence?

Goal priority answers:

> How valuable is it to pursue?

---

### P5. Hard gates are not negotiable by score

Some conditions are logical constraints, not weighted features.

For example:

- A promoted result MUST have multi-seed confirmation.
- A boundary MUST pass defect hunt.
- A negative result MUST NOT be promoted to boundary if a known decisive control was omitted.
- An instrument under suspected defect MUST be validated before dependent claims are trusted.

---

### P6. Progression and relationship are first-class

Learning curves, optimization trajectories, factorial tensors, interaction surfaces, Pareto fronts, and mechanism events MUST be representable without collapsing into isolated datapoints.

---

### P7. Efficient decision-making uses compact derived summaries

The scheduler MAY use scalarized summaries, but those summaries MUST reference structured evidence and MUST be recomputable.

---

### P8. All status changes require provenance

Every promotion, boundary, reopening, or quarantine MUST record:

- evidence used;
- gates passed;
- assumptions;
- decision rationale;
- code/config hash or equivalent provenance.

---

## 2. Architecture Overview

CEEC is organized as a six-layer epistemic architecture.

```text
Layer 5: Decisions / Experiment Selection
Layer 4: Goals / Priorities
Layer 3: Beliefs / Statuses
Layer 2: Summaries / Relations
Layer 1: Structured Evidence
Layer 0: Immutable Raw Evidence
```

The operational loop is:

\[
\text{Experiment}
\rightarrow
\text{Raw Evidence}
\rightarrow
\text{Structured Evidence}
\rightarrow
\text{Summaries}
\rightarrow
\text{Beliefs}
\rightarrow
\text{Goals}
\rightarrow
\text{Next Experiment}
\]

The system MUST support both directions:

1. **Scientific inference:** evidence updates beliefs.
2. **Experimental planning:** beliefs and goals select experiments.

---

## 3. Core Objects

### 3.1 Scope

A `Scope` defines the conditions under which evidence, beliefs, goals, or experiments apply.

Formally:

\[
\text{Scope} : K \rightarrow V
\]

where \(K\) is a set of scope dimensions and \(V\) is a set of values or ranges.

Recommended scope dimensions include:

| Dimension | Examples |
|---|---|
| architecture | MLP, transformer, lattice, NCA, NTM |
| geometry | feedforward, recurrent, tile mesh, spatial lattice |
| credit | backprop, FA, FF, PEPITA, local contrastive |
| update | Euclid, Adam, Muon, OrthoAdam, Lion |
| task | MNIST, Fashion-MNIST, copy task, language modeling |
| budget | steps, tokens, episodes, batches |
| seed policy | single seed, 3 seeds, seed range |
| evaluation | fixed batch, fresh draw, validation window |
| code provenance | commit hash, config hash, probe ID |
| substrate | digital, memristive, photonic, simulated physical |

A belief without scope is invalid.

---

### 3.2 Raw Evidence

Raw evidence is the immutable forensic layer.

\[
E_{\text{raw}} =
\{
(x_i, y_i, \Sigma_i, c_i)
\}_{i=1}^n
\]

where:

- \(x_i\) = independent variables or coordinates;
- \(y_i\) = observed values;
- \(\Sigma_i\) = uncertainty, if known;
- \(c_i\) = context/provenance.

Raw evidence MUST be append-only.

Examples:

- per-step training curves;
- per-layer diagnostics;
- seed-wise final metrics;
- resource measurements;
- log excerpts;
- probe outputs;
- config hashes;
- run IDs.

Raw evidence MUST NOT be overwritten.

---

### 3.3 Structured Evidence

Structured evidence organizes raw datapoints into meaningful scientific objects.

A `StructuredEvidence` object is:

\[
E =
(
\text{id},
\text{kind},
\text{axes},
\text{values},
\text{uncertainties},
\text{provenance},
\text{quality},
\text{defects},
\text{staleness}
)
\]

Evidence kinds MUST include at least:

| Kind | Meaning |
|---|---|
| scalar | single value with uncertainty |
| interval | range with confidence/credibility |
| vector | ordered multi-metric result |
| matrix | two-axis factorial result |
| tensor | multi-axis factorial result |
| curve | value over progression axis |
| distribution | posterior, bootstrap, or sampling distribution |
| relation | comparison between evidence objects |
| frontier | Pareto or multi-objective boundary |
| event | discrete occurrence, e.g. gate shutdown |
| inert | no-op or unrealizable cell, not capability evidence |

The `inert` kind is mandatory. An unrealizable experiment is not evidence against a hypothesis unless it is evidence about realizability itself.

---

### 3.4 Summary

A `Summary` is a compact derived object used for belief update and scheduling.

\[
S =
(
\text{id},
\text{evidence refs},
\text{operator},
\text{parameters},
\text{value or distribution},
\text{assumptions},
\text{validity checks}
)
\]

Summary operators MUST include at least:

| Operator | Meaning |
|---|---|
| mean | central tendency |
| median | robust central tendency |
| variance / spread | seed or sample dispersion |
| credible_interval | range with posterior mass |
| confidence_interval | frequentist coverage estimate |
| contrast | difference between two conditions |
| interaction | factorial interaction effect |
| slope | local progression derivative |
| peak | maximum over progression |
| peak_time | time of maximum |
| asymptote | estimated limiting value |
| decay_rate | post-peak degradation rate |
| crossing_time | time when one curve overtakes another |
| change_point | detected regime transition |
| auc | integrated performance over progression |
| dominance | pairwise or Pareto dominance |
| realizability | whether a contract or pathway was live |

A summary MUST reference the evidence from which it was derived.

---

### 3.5 Relation

A `Relation` represents a relationship between evidence objects, summaries, or beliefs.

\[
R =
(
\text{id},
\text{left},
\text{right},
\text{operator},
\text{distribution},
\text{probability},
\text{scope},
\text{evidence refs}
)
\]

Relation operators MUST include at least:

| Operator | Meaning |
|---|---|
| greater_than | left exceeds right |
| less_than | left is below right |
| within_epsilon | left and right are practically equal |
| dominates | left dominates right on all relevant axes |
| pareto_dominates | left Pareto-dominates right |
| curve_dominates | one curve exceeds another over an interval |
| crosses_before | one curve crosses another before a threshold |
| monotone | relationship preserves order |
| sign_interaction | interaction has a given sign |
| magnitude_interaction | interaction has a given magnitude |
| generalizes | relation holds across scopes |
| replicates | relation repeats under new seed/config |
| contradicts | relation opposes another relation |
| mechanism_for | one event or relation explains another |
| controls | one condition acts as control for another |

Relations are first-class scientific objects.

---

### 3.6 Belief

A `Belief` is a probabilistic claim about the world, derived from evidence.

\[
B =
(
\text{id},
\phi,
\theta,
p(\theta \mid E),
P(\phi),
\text{scope},
\text{type},
\text{evidence refs},
\text{summary refs},
\text{relation refs},
\text{confidence vector},
\text{status},
\text{gates},
\text{dependencies}
)
\]

Where:

- \(\phi\) is the proposition.
- \(\theta\) is the parameter, vector, function, or relation about which the belief is formed.
- \(p(\theta \mid E)\) is the posterior or approximation.
- \(P(\phi)\) is the probability of the proposition.

The probability of a belief is:

\[
P(\phi)
=
\int
\mathbb{I}[\phi(\theta)]
p(\theta \mid E)
d\theta
\]

For discrete or binary claims, this reduces to posterior probability.

Belief types MUST include:

| Type | Meaning |
|---|---|
| capability | a system can do something |
| mechanism | a causal or explanatory structure exists |
| boundary | a limitation holds under scope |
| instrument | a measurement tool is valid |
| generality | a claim transfers across scopes |
| realizability | a contract or pathway is executable |
| defect | a known flaw exists |
| hygiene | a cleanup or audit claim |

A belief MUST NOT be stored as a bare scalar without scope and evidence references.

---

### 3.7 Confidence Vector

Belief confidence MUST be represented as a vector, not only as one scalar.

\[
C_B =
(
p,
u,
w,
g
)
\]

where:

- \(p\) = probability that the proposition is true under scope;
- \(u\) = uncertainty, e.g. posterior variance or credible volume;
- \(w\) = evidence weight, e.g. effective sample size or evidence quality;
- \(g\) = generality, i.e. breadth of validated scope.

A scalar confidence MAY be used for scheduling, but the full vector MUST be preserved for audit.

---

### 3.8 Goal

A `Goal` is a desired outcome with strategic value.

\[
G =
(
\text{id},
\psi,
\text{kind},
\mathbf{U},
c,
\text{prerequisites},
\text{linked beliefs},
\text{priority},
\text{status}
)
\]

Where:

- \(\psi\) is the desired proposition;
- \(\mathbf{U}\) is a utility vector;
- \(c\) is expected cost;
- priority is recomputed dynamically.

Goal kinds MUST include:

| Kind | Meaning |
|---|---|
| terminal | flagship or final objective |
| instrumental | enables other goals |
| hygiene | protects validity |
| infrastructure | improves tooling |
| boundary | establishes a true limit |
| promotion | upgrades evidence to stronger status |
| audit | checks instruments or defects |

Goals MUST be separate from beliefs.

---

### 3.9 Experiment

An `Experiment` is an action that generates evidence.

\[
X =
(
\text{id},
q,
\text{target beliefs},
\text{target goals},
\text{design},
\text{prediction},
\text{controls},
\text{falsification},
\text{overturn},
\text{cost},
\text{hard gates},
\text{expected value}
)
\]

Every experiment MUST have:

1. a question;
2. a mechanism or rationale;
3. a pre-registered prediction;
4. at least one control where applicable;
5. a budget;
6. metrics;
7. falsification criterion;
8. overturn or promotion criterion.

This matches the TODO14 probe discipline.

---

### 3.10 Decision

A `Decision` records why an experiment was selected.

\[
D =
(
\text{id},
\text{state hash},
\text{candidate experiments},
\text{scores},
\text{selected experiment},
\text{overrides},
\text{rationale}
)
\]

Decisions MUST be append-only.

---

## 4. Mathematical Foundations

### 4.1 Evidence Space

Let:

\[
\mathcal{X}
\]

be the space of experimental coordinates, e.g. architecture, credit, update, seed, step, task.

Let:

\[
\mathcal{Y}
\]

be the space of observations, e.g. accuracy, loss, resource usage, gate state.

An evidence-generating process is modeled as:

\[
Y : \mathcal{X} \rightarrow \mathcal{Y}
\]

Observed evidence is:

\[
\mathcal{D}
=
\{
(x_i, y_i, \Sigma_i)
\}_{i=1}^n
\]

---

### 4.2 Latent Scientific Parameters

Many claims are not about individual datapoints but about latent parameters.

Examples:

- mean performance difference;
- interaction strength;
- learning-curve asymptote;
- decay rate;
- peak time;
- Pareto dominance probability;
- causal effect of a mechanism intervention.

Let:

\[
\theta
\]

be the latent parameter or structured object.

The posterior is:

\[
p(\theta \mid \mathcal{D}, M)
\]

where \(M\) is the statistical or mechanistic model.

A proposition \(\phi\) is a measurable statement about \(\theta\).

The belief probability is:

\[
P(\phi \mid \mathcal{D}, M)
=
\int
\mathbb{I}[\phi(\theta)]
p(\theta \mid \mathcal{D}, M)
d\theta
\]

This allows beliefs to be about scalars, ranges, vectors, curves, tensors, or relations.

---

### 4.3 Binary Belief Update

For simple binary hypotheses, odds may be updated via Bayes factors.

Let:

\[
O(H)
=
\frac{P(H)}{1-P(H)}
\]

Given evidence \(e\) with quality \(q \in [0,1]\) and Bayes factor \(\text{BF}(e)\):

\[
O'(H)
=
O(H)
\cdot
\text{BF}(e)^q
\]

Then:

\[
P'(H)
=
\frac{O'(H)}{1 + O'(H)}
\]

Evidence quality SHOULD downweight evidence that is:

- uncontrolled;
- stale;
- single-seed;
- instrument-suspicious;
- non-reproducible;
- scope-mismatched.

---

### 4.4 Continuous and Structured Belief Update

For continuous or structured claims, the system SHOULD use one of:

1. hierarchical Bayesian models;
2. bootstrap distributions;
3. multivariate Normal or Student-t approximations;
4. Gaussian processes for curves;
5. Dirichlet or Beta models for categorical/binomial evidence;
6. log-normal models for positive resource quantities;
7. nonparametric credible intervals.

The exact method is not mandatory, but the implementation MUST declare:

- model assumptions;
- uncertainty representation;
- evidence weighting;
- update rule.

---

### 4.5 Belief Decay and Staleness

Beliefs dependent on implementation details SHOULD decay when relevant code, config, or instruments change.

Let:

\[
p_i(t+1)
=
p_i(t)
\cdot
\lambda_i
\]

where \(\lambda_i \in [0,1]\) is a persistence factor.

Recommended defaults:

| Belief dependency | Persistence \(\lambda\) |
|---|---:|
| formal invariant | 0.99–1.00 |
| replicated mechanism | 0.90 |
| probe-scale empirical result | 0.70 |
| instrument belief after patch | 0.40 |
| belief from suspected stale run | 0.10 |

If an instrument belief is invalidated, dependent beliefs MUST be quarantined or discounted until revalidated.

---

## 5. Representation of Ranges, Vectors, Curves, Tensors, and Relations

This section is normative. CEEC is not compliant if it only supports isolated scalar datapoints.

---

### 5.1 Scalars and Intervals

A scalar result MUST be accompanied by uncertainty whenever possible.

Minimal representation:

\[
y = \hat{y} \pm \delta
\]

Better representation:

\[
P(y \in [a,b] \mid E) = 1-\alpha
\]

A belief about a scalar range is:

\[
\phi =
a \leq y \leq b
\]

with confidence:

\[
P(\phi)
\]

Example:

\[
P(
\text{NTM fresh-draw accuracy} \in [0.65, 0.75]
)
= 0.80
\]

---

### 5.2 Vectors

A vector-valued result is:

\[
\mathbf{y}
=
(y_1, y_2, \dots, y_k)
\]

with optional covariance:

\[
\Sigma
\]

Examples:

\[
\mathbf{y}
=
(
\text{accuracy},
\text{loss},
\text{memory},
\text{energy},
\text{latency}
)
\]

A vector belief may assert:

\[
P(
\mathbf{y} \in R
)
\geq
\tau
\]

where \(R\) is a credible region.

Vector relations include:

- dominance;
- Pareto dominance;
- componentwise improvement;
- tradeoff detection.

---

### 5.3 Matrices and Tensors

Factorial experiments MUST be representable as matrices or tensors.

For example, the credit–update interaction is represented as:

\[
Y_{c,u}
\]

where:

- \(c\) = credit rule;
- \(u\) = update rule.

With geometry and seed:

\[
Y_{c,u,g,s}
\]

The canonical interaction contrast is:

\[
I(c,u)
=
Y_{c,u}
-
Y_{c,u_0}
-
Y_{c_0,u}
+
Y_{c_0,u_0}
\]

For geometry-dependent interactions:

\[
I(c,u,g)
=
Y_{c,u,g}
-
Y_{c,u_0,g}
-
Y_{c_0,u,g}
+
Y_{c_0,u_0,g}
\]

Beliefs about interaction tensors may include:

\[
P(I(c,u,g) > 0)
\]

\[
P(
\operatorname{sign}(I(c,u,g_1))
=
\operatorname{sign}(I(c,u,g_2))
)
\]

\[
P(
|I(c,u,g_1)|
\approx
|I(c,u,g_2)|
)
\]

This is the natural representation of TODO14’s \(I(C,U)\) law.

---

### 5.4 Curves and Progressions

A progression is a function:

\[
y(t)
\]

where \(t\) may be:

- training step;
- token count;
- episode;
- rollout length;
- depth;
- width;
- feedback scale;
- damage fraction;
- sequence length.

A curve evidence object MUST store at least:

\[
\{
(t_i, y_i, \sigma_i)
\}
\]

and SHOULD store derived events:

| Event | Meaning |
|---|---|
| peak | maximum value |
| peak_time | time of maximum |
| decay_onset | beginning of degradation |
| crossing | one curve passes another |
| plateau | stabilization |
| change_point | regime shift |
| gate_shutdown | mechanism-specific freeze or zero-gradient event |
| inversion | sign inversion or analogous diagnostic |

Curve summaries MUST include at least:

\[
\text{slope}(t_1,t_2)
=
\frac{
\mathbb{E}[y(t_2)] - \mathbb{E}[y(t_1)]
}{
t_2 - t_1
}
\]

\[
y_{\text{peak}}
=
\max_t y(t)
\]

\[
t_{\text{peak}}
=
\arg\max_t y(t)
\]

Beliefs about curves may include:

\[
P(
f_A(t) > f_B(t)
\text{ for } t \in [t_1,t_2]
)
\]

\[
P(
t_{\text{peak}} < T
)
\]

\[
P(
y(3000) > y(600)
)
\]

\[
P(
\text{curve still rising at cutoff}
)
\]

This is essential for W0 transformer decay, W8 NTM learning curves, and rollout-length NCA experiments.

---

### 5.5 Functional and Grid Approximations

Full functional inference is optional. Implementations MAY approximate functional beliefs using:

- discrete grids;
- parametric curve fits;
- Gaussian processes;
- bootstrap confidence bands;
- change-point detection;
- monotonicity tests.

If a functional claim is approximated on a grid, the grid resolution MUST be recorded.

---

### 5.6 Pareto Fronts and Resource Vectors

Resource claims MUST use vector representation.

The Computronium resource vector is:

\[
\mathcal{C}
=
(
\text{compute},
\text{memory},
\text{energy},
\text{latency},
\text{plastic-state capacity}
)
\]

Let:

\[
(Q_A, \mathcal{C}_A)
\]

and:

\[
(Q_B, \mathcal{C}_B)
\]

be two systems, where \(Q\) is capability or quality.

System \(A\) Pareto-dominates system \(B\) iff:

\[
Q_A \ge Q_B
\]

and:

\[
\mathcal{C}_A \le \mathcal{C}_B
\]

componentwise, with at least one strict inequality.

Beliefs may assert:

\[
P(A \succ B)
\]

or:

\[
P(A \text{ is Pareto-optimal in tested set})
\]

Energy terminology MUST remain strict:

- simulated energy;
- estimated energy;
- hardware-measured energy.

These MUST NOT be collapsed into a generic “energy efficiency” claim.

---

### 5.7 Efficient Storage Rules

To remain efficient:

1. Raw evidence MAY be large.
2. Structured evidence SHOULD be stored in vectorized formats, e.g. Parquet, Arrow, SQLite, HDF5, or equivalent.
3. Summaries MUST be compact.
4. The scheduler MUST operate primarily on summaries, relations, and belief states.
5. Raw evidence MUST be accessible for audit but need not be loaded for every scheduling decision.
6. Parametric fits MAY replace dense curves if residual diagnostics pass.
7. Missing or unrealizable cells MUST be marked as missing or inert, not silently zeroed.

---

## 6. Belief Status State Machine

CEEC defines five primary statuses:

| Status | Meaning |
|---|---|
| `Open` | evidence exists but is insufficient for promotion or boundary |
| `Promoted` | positive claim survives promotion gates |
| `Boundary` | negative or limiting claim survives boundary gates |
| `Reopened` | previous boundary or negative result is newly doubtful |
| `Quarantined` | belief is suspect due to instrument or defect risk |

A belief MUST have exactly one primary status.

---

### 6.1 Open

A belief begins as `Open` when:

\[
0 < w < w_{\text{min}}
\]

or:

\[
P(\phi)
\]

is not decisive, or required gates are incomplete.

---

### 6.2 Promoted

A positive belief MAY become `Promoted` only if:

\[
P(\phi) \ge \tau_{\text{promote}}
\]

and all hard promotion gates pass.

Default:

\[
\tau_{\text{promote}} = 0.95
\]

Promotion gates:

```text
Promoted(φ) requires:
    Probability(φ) ≥ τ_promote
    ∧ MultiSeed(φ)
    ∧ MatchedControl(φ)
    ∧ FixedStepEvaluation(φ)
    ∧ DefectAudit(φ)
    ∧ Reproduction(φ)
    ∧ ScopeExplicit(φ)
```

For empirical learning results, `MultiSeed` SHOULD require at least three seeds unless a formal justification exists.

---

### 6.3 Boundary

A negative or limiting belief MAY become `Boundary` only if:

\[
P(\text{rescue} \mid \text{known mechanisms}) \le \tau_{\text{boundary}}
\]

Default:

\[
\tau_{\text{boundary}} = 0.05
\]

Boundary gates:

```text
Boundary(φ) requires:
    DefectHuntPassed(φ)
    ∧ OptimizerMatrixComplete(φ)
    ∧ SignalIntegrity(φ)
    ∧ StateIntegrity(φ)
    ∧ UpdateIntegrity(φ)
    ∧ MeasurementIntegrity(φ)
    ∧ KnownLeversExhausted(φ)
    ∧ MatchedControl(φ)
    ∧ MultiSeed(φ)
    ∧ ScopeExplicit(φ)
```

A negative result obtained without a known decisive control MUST NOT be promoted to `Boundary`.

---

### 6.4 Reopened

A belief in status `Boundary` MUST be moved to `Reopened` if:

\[
\exists m \in \mathcal{M}_{\text{strong}}
:
\neg \text{Tested}(m,\phi)
\]

or if new evidence satisfies:

\[
P(\text{rescue} \mid \text{new evidence}) > \epsilon_{\text{reopen}}
\]

Recommended default:

\[
\epsilon_{\text{reopen}} = 0.10
\]

This formalizes the overturnability principle.

---

### 6.5 Quarantined

A belief MUST be quarantined if a required instrument, measurement, or dependency is suspected invalid.

Examples:

- stale process suspected;
- patch not verified live;
- silent inert contract detected;
- evaluation uses same generator draw as training;
- global clipping destroys learning-rate sensitivity;
- covariate pairing misalignment suspected.

While quarantined:

\[
P_{\text{effective}}(\phi)
=
P(\phi)
\cdot
P(\text{instrument valid})
\]

If instrument validity is unknown, dependent beliefs MUST NOT be used for promotion or boundary decisions.

---

## 7. Goal Model

### 7.1 Goal Utility Vector

A goal MUST carry a utility vector:

\[
\mathbf{U}_g
=
(
U_{\text{science}},
U_{\text{flagship}},
U_{\text{generality}},
U_{\text{resource}},
U_{\text{optionality}},
U_{\text{urgency}}
)
\]

A scalar utility MAY be derived:

\[
U_g
=
\mathbf{w} \cdot \mathbf{U}_g
\]

but the vector MUST be preserved.

---

### 7.2 Goal Probability

The probability of achieving a goal is derived from linked beliefs and prerequisites.

Let:

\[
\mathcal{B}_g
\]

be the set of beliefs that gate goal \(g\).

A simple lower-bound estimate is:

\[
P(g)
=
\prod_{b_i \in \mathcal{B}_g}
P(b_i)^{\rho_i}
\]

where \(\rho_i\) is the dependency strength.

For OR-style dependencies:

\[
P(g)
=
1 -
\prod_i
(1 - P(b_i))^{\rho_i}
\]

More sophisticated dependency models MAY be used.

---

### 7.3 Goal Priority

Goal priority is dynamic.

A canonical priority formula is:

\[
\pi_g
=
\frac{
\left[
U_g
+
\lambda_o V_{\text{option}}(g)
\right]
\cdot
P_{\text{progress}}(g)
\cdot
D_g
}{
c_g^\gamma
}
-
\lambda_r R_g
\]

where:

- \(U_g\) = utility;
- \(V_{\text{option}}(g)\) = future option value;
- \(P_{\text{progress}}(g)\) = probability that action makes progress;
- \(D_g\) = dependency/unblocking multiplier;
- \(c_g\) = estimated cost;
- \(\gamma\) = cost penalty;
- \(R_g\) = risk of misleading evidence or wasted budget.

Hard constraints MAY override priority.

---

### 7.4 Epistemic Debt

Epistemic debt is unresolved risk in the measurement or inference foundation.

\[
D_{\text{epi}}
=
\sum_i
w_i
\cdot
u_i
\cdot
\text{dependence}_i
\]

where:

- \(w_i\) = severity;
- \(u_i\) = uncertainty;
- \(\text{dependence}_i\) = number or weight of dependent beliefs/goals.

Hygiene and instrument-validation goals SHOULD receive priority boosts proportional to epistemic debt.

---

## 8. Experiment Selection

### 8.1 Candidate Experiments

Candidate experiments are generated from:

- uncertain high-value beliefs;
- blocked goals;
- untested overturn mechanisms;
- pending promotion gates;
- suspected defects;
- boundary challenges;
- generality tests;
- resource Pareto tests.

---

### 8.2 Expected Value of Information

For experiment \(x\), let \(o\) be a possible observation.

The utility-weighted value of information is:

\[
\text{UVOI}(x)
=
\mathbb{E}_{o \mid x}
[
V(B_{t+1}(o), G_t)
]
-
V(B_t, G_t)
\]

where \(V(B,G)\) is the value of the epistemic-goal state.

A practical value function is:

\[
V(B,G)
=
\sum_g
U_g
\cdot
P(g \mid B)
-
\lambda_d D_{\text{epi}}(B)
-
\lambda_s S_{\text{stale}}(B)
\]

---

### 8.3 Experiment Score

The scheduler SHOULD rank experiments by:

\[
\text{Score}(x)
=
\frac{
\text{UVOI}(x)
+
\lambda_h H(x)
+
\lambda_b B(x)
}{
c_x^\gamma
}
\]

where:

- \(H(x)\) = hygiene or defect-reduction value;
- \(B(x)\) = boundary-overturn value;
- \(c_x\) = expected cost;
- \(\gamma\) = cost penalty.

Hard constraints are applied before ranking.

---

### 8.4 Selection Rule

The next experiment is:

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

For short sessions, greedy selection by score is acceptable.

For campaigns, portfolio optimization MAY be used.

---

## 9. Logical Rule Language

CEEC MAY be implemented using a weighted or deterministic rule language.

Minimal predicates:

```text
belief(id)
goal(id)
experiment(id)
evidence(id)
summary(id)
relation(id)

supports(evidence, belief)
refutes(evidence, belief)
depends_on(belief, belief)
enables(goal, goal)
tests(experiment, belief)
serves(experiment, goal)
requires(status, gate)
passed(gate)
```

Status rules:

```text
Promoted(b) :-
    probability(b, p), p >= τ_promote,
    gate_passed(multi_seed, b),
    gate_passed(matched_control, b),
    gate_passed(defect_audit, b),
    gate_passed(reproduction, b).

Boundary(b) :-
    rescue_probability(b, p), p <= τ_boundary,
    gate_passed(defect_hunt, b),
    gate_passed(optimizer_matrix, b),
    gate_passed(signal_integrity, b),
    gate_passed(update_integrity, b),
    gate_passed(measurement_integrity, b),
    gate_passed(known_levers_exhausted, b).

Reopened(b) :-
    status(b, boundary),
    exists(mechanism, m),
    strong_mechanism(m),
    not tested(m, b).

Quarantined(b) :-
    depends_on(b, instrument),
    not valid(instrument).
```

Weighted rules MAY be used for soft prioritization, but MUST NOT override hard gates.

---

## 10. Canonical Schema

The following is a normative minimal schema. Implementations MAY use YAML, JSON, SQLite, Parquet, or equivalent.

---

### 10.1 Evidence Schema

```yaml
evidence:
  id: string
  kind: scalar | interval | vector | matrix | tensor | curve | distribution | relation | frontier | event | inert
  axes:
    name: values
  values_ref: string
  uncertainties: optional
  provenance:
    probe: string
    log: string
    config_hash: string
    code_commit: string
  quality:
    seeds: integer
    controls: boolean
    freshness: string
    instrument_valid: boolean
  defects: []
  stale: boolean
```

---

### 10.2 Summary Schema

```yaml
summary:
  id: string
  evidence_refs: []
  operator: mean | median | ci | contrast | interaction | slope | peak | auc | dominance | change_point | realizability
  parameters: {}
  value: scalar | interval | vector | tensor
  distribution: optional
  assumptions: []
  checks: []
```

---

### 10.3 Relation Schema

```yaml
relation:
  id: string
  left: string
  right: string
  operator: greater_than | within_epsilon | dominates | curve_dominates | sign_interaction | magnitude_interaction | replicates | contradicts | mechanism_for
  distribution: optional
  probability_positive: float
  probability_material: float
  scope: {}
  evidence_refs: []
```

---

### 10.4 Belief Schema

```yaml
belief:
  id: string
  statement: string
  type: capability | mechanism | boundary | instrument | generality | realizability | defect | hygiene
  scope: {}
  proposition: string
  probability: float
  uncertainty: float
  evidence_weight: float
  generality: float
  posterior_method: string
  evidence_refs: []
  summary_refs: []
  relation_refs: []
  dependencies: []
  status: open | promoted | boundary | reopened | quarantined
  gates:
    multi_seed: boolean
    matched_control: boolean
    defect_audit: boolean
    reproduction: boolean
    fixed_step_evaluation: boolean
```

---

### 10.5 Goal Schema

```yaml
goal:
  id: string
  statement: string
  kind: terminal | instrumental | hygiene | infrastructure | boundary | promotion | audit
  utility_vector:
    science: float
    flagship: float
    generality: float
    resource: float
    optionality: float
    urgency: float
  scalar_utility: optional
  cost_estimate: float
  prerequisites: []
  linked_beliefs: []
  priority: float
  status: active | blocked | completed | deferred
```

---

### 10.6 Experiment Schema

```yaml
experiment:
  id: string
  question: string
  mechanism: string
  target_beliefs: []
  target_goals: []
  design: {}
  prediction: string
  controls: []
  budget: string
  metrics: []
  falsification_criterion: string
  overturn_criterion: string
  cost_estimate: float
  expected_value: float
  hard_gates: []
  status: proposed | pre_registered | running | completed | abandoned
```

---

### 10.7 Decision Schema

```yaml
decision:
  id: string
  timestamp: datetime
  state_hash: string
  candidate_experiments: []
  scores: {}
  selected_experiment: string
  overrides: []
  rationale: string
```

---

## 11. Operational Protocol

A compliant CEEC session MUST follow this loop.

---

### Step 1 — Load epistemic state

Load:

- beliefs;
- goals;
- evidence summaries;
- defects;
- quarantine list;
- previous decisions.

Verify staleness and code/config hashes.

---

### Step 2 — Resolve hygiene first

If any high-dependency instrument belief is invalid or suspected stale:

\[
\text{Hygiene priority} \leftarrow \text{boost}
\]

Do not interpret dependent negative results until instruments are validated.

---

### Step 3 — Generate candidate experiments

Candidates arise from:

- uncertain beliefs;
- blocked goals;
- pending promotions;
- boundary challenges;
- defect audits;
- untested strong mechanisms.

---

### Step 4 — Apply hard constraints

Reject candidates missing mandatory controls.

Examples:

- no BPTT/gold-standard control where required;
- no matched control;
- no seed plan for promotion;
- no fresh-draw evaluation when required;
- no defect audit for boundary claims.

---

### Step 5 — Score candidates

Compute:

\[
\text{Score}(x)
\]

using UVOI, goal utility, hygiene value, overturnability, and cost.

---

### Step 6 — Pre-register selected experiment

Before execution, record:

- question;
- prediction;
- controls;
- metrics;
- falsification criterion;
- overturn criterion.

---

### Step 7 — Execute experiment

Run with explicit provenance:

- seed;
- config hash;
- code version;
- budget;
- evaluation policy.

---

### Step 8 — Record structured evidence

Store raw and structured evidence.

Do not store only final scalar values when progression or factorial structure exists.

---

### Step 9 — Update summaries and relations

Compute:

- intervals;
- contrasts;
- interactions;
- curve summaries;
- dominance relations;
- event detections.

---

### Step 10 — Update beliefs

Update:

\[
p(\theta \mid E)
\]

and:

\[
P(\phi)
\]

Apply quarantine if instruments are suspect.

---

### Step 11 — Update statuses

Apply state machine gates.

No manual status change without gate evidence.

---

### Step 12 — Update goals and priorities

Recompute:

\[
\pi_g
\]

for all affected goals.

---

### Step 13 — Record decision

Append a decision record.

---

## 12. Default Gates and Checklists

### 12.1 Promotion Gate

For positive claims:

```text
≥3 seeds
+ matched control
+ fixed-step or fixed-budget evaluation
+ defect audit
+ reproduction
+ explicit scope
+ structured evidence
```

---

### 12.2 Boundary Gate

For negative claims:

```text
defect hunt passed
+ signal integrity
+ state integrity
+ update integrity
+ measurement integrity
+ appropriate optimizer matrix
+ known levers exhausted
+ matched controls
+ multi-seed where feasible
+ explicit scope
```

---

### 12.3 Reopen Gate

A boundary is reopened if:

```text
there exists a strong untested mechanism
OR new evidence materially raises rescue probability
OR an instrument defect invalidates the old boundary
```

---

### 12.4 Quarantine Gate

Quarantine if:

```text
instrument may be stale
OR measurement defect suspected
OR silent inert contract suspected
OR dependent belief relies on invalid evidence
```

---

## 13. Calibration and Honesty

CEEC requires calibration.

For each pre-registered prediction with probability \(p\), record outcome \(y \in \{0,1\}\).

Use Brier score:

\[
\text{Brier}
=
(p-y)^2
\]

or log score:

\[
\text{LogScore}
=
y \log p + (1-y)\log(1-p)
\]

Over time, the system SHOULD track:

- predicted confidence vs observed success rate;
- boundary durability;
- promotion durability;
- reopen rate;
- defect discovery rate.

If calibration drifts, priors, evidence weights, or thresholds SHOULD be adjusted.

---

## 14. Integration with Computronium

CEEC is designed to integrate naturally with Computronium’s existing structures.

---

### 14.1 Six-Axis Ontology as Scope

The six axes:

\[
S \times G \times D \times P \times C \times U
\]

are scope dimensions.

Example:

```yaml
scope:
  substrate: digital
  geometry: transformer
  state_dynamics: instantaneous
  plasticity: null
  credit: local_contrastive
  parameter_update: muon
  task: next_token_probe
  budget: 600_steps
```

---

### 14.2 \(I(C,U)\) as Tensor Relation

The central TODO14 interaction:

\[
I(C,U)
\]

is represented as an interaction tensor.

Evidence:

\[
Y_{c,u,g,s}
\]

Summary:

\[
I_{c,u,g}
=
Y_{c,u,g}
-
Y_{c,u_0,g}
-
Y_{c_0,u,g}
+
Y_{c_0,u_0,g}
\]

Beliefs:

```text
I(C,U) is positive for degenerate credit under Muon.
I(C,U) sign-generalizes across tested geometries.
I(C,U) magnitude-generalizes across tested geometries.
```

These are separate beliefs with separate scopes and confidence vectors.

---

### 14.3 W0 Transformer Local Credit

W0 evidence includes:

- learning curve over steps;
- per-layer contrast curves;
- gate saturation events;
- component ablation contrasts;
- supervision-alignment contrasts.

Relevant structured objects:

| Object | Representation |
|---|---|
| performance trajectory | curve |
| degradation onset | event/change point |
| layer freeze | event |
| ablation effect | contrast vector |
| boundary claim | scoped belief |

Example belief:

\[
P(
\text{post-peak decay occurs under tested schedules at probe scale}
)
\]

is distinct from:

\[
P(
\text{local contrastive fails at all transformer scales}
)
\]

---

### 14.4 W8 NTM Copy Task

W8.5 evidence includes:

- learning curve over steps;
- BPTT control curve;
- local-factorization curve;
- seed distribution;
- fresh-draw eval distribution;
- length-generalization decay curve.

Promotion belief:

\[
P(
\text{local factorization fresh-draw accuracy} > 0.60
\text{ across 3 seeds}
)
\]

Goal:

```text
Promote NTM local factorization.
```

Experiment:

```text
Run 3 seeds with fresh-draw evaluation and matched BPTT control.
```

This is a canonical CEEC promotion loop.

---

### 14.5 Resource Pareto Work

For substrate/resource claims, evidence MUST be vector-valued:

\[
(Q, \mathcal{C})
\]

where:

\[
\mathcal{C}
=
(
\text{compute},
\text{memory},
\text{energy},
\text{latency},
\text{plastic-state capacity}
)
\]

Beliefs SHOULD be about Pareto dominance or frontier position, not scalar efficiency.

---

## 15. Minimal Compliant Implementation

A minimal compliant implementation consists of:

1. **Evidence ledger**
   - immutable raw artifacts;
   - structured evidence metadata;
   - provenance hashes.

2. **Summary ledger**
   - means, intervals, contrasts, interactions, curve summaries.

3. **Belief ledger**
   - scoped claims;
   - probability;
   - uncertainty;
   - evidence references;
   - status.

4. **Goal ledger**
   - utility vector;
   - cost;
   - dependencies;
   - priority.

5. **Experiment ledger**
   - pre-registration;
   - controls;
   - predictions;
   - falsification criteria.

6. **Decision log**
   - selected experiment;
   - score;
   - rationale.

This can be implemented initially in YAML/Markdown plus Parquet/CSV artifacts.

---

## 16. Full Implementation

A full implementation SHOULD add:

- automated posterior updating;
- Bayesian active experiment selection;
- tensor and curve fitting;
- calibration dashboards;
- dependency-aware belief propagation;
- Pareto frontier analysis;
- quarantine propagation;
- campaign portfolio optimization;
- CLI integration.

Suggested CLI surface:

```bash
comp epistemic list-beliefs
comp epistemic list-goals
comp epistemic list-evidence
comp epistemic summarize
comp epistemic rank-experiments
comp epistemic propose-next
comp epistemic update-belief
comp epistemic status-report
comp epistemic calibration
comp epistemic audit
```

---

## 17. Compliance Checklist

An implementation is CEEC-compliant if:

```text
✓ Every belief has explicit scope.
✓ Every belief references evidence.
✓ Every belief stores probability and uncertainty.
✓ Every positive promotion passes hard gates.
✓ Every boundary passes defect hunt and lever exhaustion.
✓ Raw evidence is immutable.
✓ Structured evidence preserves vectors, ranges, curves, tensors where present.
✓ Scalars are derived, not primary.
✓ Inert or unrealizable cells are labeled as such.
✓ Goals have utility vectors and dynamic priorities.
✓ Experiments are pre-registered.
✓ Decisions are logged.
✓ Quarantine propagates to dependent beliefs.
✓ Scheduler respects hard constraints.
✓ Calibration is tracked over time.
```

---

## 18. Canonical Example: W1 Interaction Tensor

A concise CEEC representation of the W1 credit ladder:

```yaml
evidence:
  id: e_w1_mlp_ladder
  kind: tensor
  axes:
    credit: [bp, ff, pepita, rp_weak, rp_ortho, rp_vweak]
    update: [euclid, muon, ortho]
    seed: [0, 1, 2]
  values_ref: artifacts/w1_mlp_ladder.parquet
  quality:
    seeds: 3
    controls: true
    instrument_valid: true

summary:
  id: s_w1_interaction_muon
  evidence_refs: [e_w1_mlp_ladder]
  operator: interaction
  parameters:
    baseline_credit: bp
    baseline_update: euclid
    target_update: muon
  value:
    pepita: +0.103
    rp_weak: +0.459
    rp_ortho: +0.446
    rp_vweak: +0.460

relation:
  id: r_w1_degenerate_credit_rescue
  left: rp_weak/muon
  right: rp_weak/euclid
  operator: greater_than
  probability_positive: 0.99
  probability_material: 0.99
  scope:
    geometry: mlp
    task: mnist
    budget: 150_batches

belief:
  id: b_w1_muon_rescues_degenerate_credit
  statement: >
    Muon rescues heavily weakened random-projection credit on MLP.
  type: capability
  scope:
    geometry: mlp
    credit: random_projection_weak
    update: muon
  probability: 0.97
  uncertainty: low
  evidence_weight: high
  generality: medium
  status: promoted

belief:
  id: b_w1_magnitude_generality
  statement: >
    The strong magnitude of I(C,U) generalizes across geometries.
  type: generality
  scope:
    geometries: [mlp, lattice]
  probability: 0.25
  uncertainty: high
  evidence_weight: medium
  generality: low
  status: open
```

This separates the local result from the generality claim.

---

## 19. Canonical Example: NTM Promotion

```yaml
belief:
  id: b_ntm_local_copy
  statement: >
    Zero-history local factorization learns NTM copy above chance under fresh-draw evaluation.
  type: capability
  scope:
    architecture: ntm_minimal
    task: copy_L6
    credit: local_factorized
    update: adam
    eval: fresh_draw
  probability: 0.60
  uncertainty: medium
  evidence_weight: low
  generality: low
  status: open

goal:
  id: g_promote_ntm_local
  statement: >
    Promote NTM local factorization to a robust positive result.
  kind: promotion
  utility_vector:
    science: 8
    flagship: 9
    generality: 7
    resource: 5
    optionality: 8
    urgency: 9
  cost_estimate: low
  linked_beliefs: [b_ntm_local_copy]
  priority: high

experiment:
  id: x_ntm_local_promotion
  question: >
    Is NTM local factorization seed-robust and fresh-draw robust?
  target_beliefs: [b_ntm_local_copy]
  target_goals: [g_promote_ntm_local]
  design:
    arms: [bptt_adam_control, local_factorized_adam]
    seeds: [0, 1, 2]
    eval: fresh_draw
    steps: 3000
  prediction: >
    Local factorization exceeds 0.60 fresh-draw mean and remains below BPTT control.
  controls: [bptt_adam_control]
  falsification_criterion: >
    Local factorization fresh-draw mean < 0.55.
  overturn_criterion: >
    If local × muon materially exceeds local × adam, reopen optimizer axis.
  cost_estimate: low
  expected_value: high
```

---

## 20. Final Normative Statement

The Computronium Epistemic Experiment Calculus is satisfied when the research process is represented as:

\[
\text{Evidence}
\rightarrow
\text{Structured Summaries}
\rightarrow
\text{Scoped Probabilistic Beliefs}
\rightarrow
\text{Gated Statuses}
\rightarrow
\text{Goal Priorities}
\rightarrow
\text{Expected-Value Experiments}
\]

and when the following invariants hold:

\[
\text{No belief without evidence.}
\]

\[
\text{No scalar without structured source.}
\]

\[
\text{No promotion without gates.}
\]

\[
\text{No boundary without defect hunt.}
\]

\[
\text{No reopening without untested strong mechanism.}
\]

\[
\text{No priority without cost and dependency awareness.}
\]

\[
\text{No scientific conclusion without explicit scope.}
\]

This specification preserves the richness of experimental trajectories while enabling efficient, honest, and elegant experiment selection.

