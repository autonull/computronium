# Evaluation Consortium Research

<div class="research-header">
  <span class="research-badge">🤝 Community Collaboration</span>
  <h2>A consortium for governed, reproducible comparison of learning mechanisms</h2>
  <p class="research-lead">Fairness contracts · Identity cards · Corrections log · Independent review</p>
</div>

## The Problem

Research on learning mechanisms is difficult to compare across papers, implementations, tasks, and labs. A reported result reflects more than the learning rule itself:
- Dataset choices, preprocessing, implementation details
- Compute, hyperparameter search, stopping criteria
- Random seeds, metrics, and reporting decisions

These differences are not necessarily mistakes. Different studies may answer different questions. The problem arises when:
1. Conditions behind a result are difficult to inspect
2. Unlike results are treated as direct comparisons
3. The cost of careful replication is too high for any one group to bear

## Why a Consortium?

No single lab can reasonably carry every implementation, benchmark, replication, and audit. Nor should one team decide unilaterally what counts as a meaningful comparison for every research question.

A consortium could:
- Bring together people with different methods, expertise, resources, and incentives
- Coordinate work that is hard to sustain alone
- Make assumptions and disagreements visible
- Create a public record that improves as more people examine it

> The aim is **not** to declare one universally best algorithm, force every experiment into one protocol, or centralize independent research. It is to make claims easier to assess and comparisons more useful when comparison is the goal.

## Three Shared Artifacts

### 1. Fairness Contract
<!-- gen:fairness_clause_count --> clauses that make a comparison legal before it is run.
**`docs/FAIRNESS_CONTRACT.md`**

Declares budget, fidelity, seed count, and operating point before a number exists. The operating point is the fairness contract made executable.

### 2. Identity Cards
<!-- gen:identity_card_count --> cards declaring reference, deviations, objective, pseudo-gradient, and symmetry.
**`docs/IDENTITY_CARDS.md`**

The admission ticket for a new algorithm. Every experiment is a coordinate in the ontology.

### 3. Corrections Log
<!-- gen:corrections_count --> public entries recording what failed, why, and what changed.
**`docs/CORRECTIONS.md`**

A gate is not a one-way promotion. When a later campaign contradicts a belief, the belief is revoked and the evidence stays.

## Provisional Mission

**Help the research community produce evidence about learning mechanisms that is easier to inspect, compare where appropriate, reproduce, correct, and build on.**

### Working Principles
- **Transparency** — Describe method, implementation, task, metric, resources, tuning, limitations
- **Pluralism** — Different questions call for different tasks, metrics, budgets
- **Proportionate rigor** — Match claim strength to evidence strength
- **Faithful representation** — Document implementation choices and departures
- **Correction as normal practice** — Visible history of material corrections
- **Open criticism and shared governance** — Reviewable decisions, appeal paths
- **Useful negative findings** — Publish informative null/inconclusive results

## First Phase: Bounded Pilot

1. **Convene participants and draft a charter** — purpose, scope, decision-making, conflicts of interest
2. **Choose one bounded pilot** — important enough to matter, narrow enough to complete
3. **Agree on reporting requirements** — claim, implementation provenance, data, metrics, compute, randomization, uncertainty, exclusions, limitations
4. **Invite independent scrutiny** — review protocol or reproduce a defined part
5. **Publish result and lessons** — including inconclusive findings and process shortcomings

> The pilot should test the consortium's working process as well as the scientific question.

## Relationship to Computronium

**Computronium is a codebase and experimental framework. The Computronium Consortium is a proposed collaboration. They are related, but they are not the same thing.**

- Anyone may use Computronium independently of a consortium
- Using Computronium does not make a result independently verified or endorsed by the consortium
- The consortium may choose to use Computronium, other tools, or a combination

## Current Infrastructure (Starting Points)

- Algorithm Identity Cards: `docs/IDENTITY_CARDS.md`
- Corrections Log: `docs/CORRECTIONS.md`
- Preregistration Tooling: `computronium/validation/preregistration.py`
- HPO Protocol: `docs/hpo_protocol.md`
- Fairness Contract: `docs/FAIRNESS_CONTRACT.md`

## Decisions for Participants

- **Scope**: Which mechanisms, claims, tasks, communities first?
- **Governance**: Who proposes/changes standards? How are decisions made and appealed?
- **Participation**: What contributions are useful? What commitments are reasonable?
- **Evidence & Review**: What info for different claims? How to handle disputes, failed replications, corrections?
- **Services**: Core process vs. optional specialist services (HPO, implementation audits)?
- **Resources**: Costs, infrastructure, funding, credit, maintenance without exclusion?
- **Expansion**: What should a successful pilot demonstrate before widening scope?

## Existing Models to Consider

- **MLCommons** — Industry–academic consortium for shared benchmarks, reproducibility, measurement. AlgoPerf benchmark for training algorithms.
- **METR** — Independent evaluation research with public-interest mission (focused on advanced AI capabilities/risks).
- **Cochrane** — Distributed international community synthesizing evidence using shared methods, independent review, continual updating.

## The Invitation

Bring an algorithm, a research question, a benchmark concern, a critique, expertise in methodology or statistics, implementation work, data, compute, funding, or simply time to help shape the first steps.

> The first task is not to agree with every sentence. It is to identify the people, questions, and modest first experiment that could make a consortium worth having.

<!-- notes -->
This slide summarizes CONSORTIUM.md. The consortium is a proposal, not a settled charter. Its scope, governance, services, and standards should be shaped through participation. A strong objection paired with a better alternative is a useful contribution.
<!-- /notes -->