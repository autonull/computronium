# The Invitation: an Evaluation Consortium

A consortium needs three shared artifacts, and none of them is a model.

- **A fairness contract** — <!-- gen:fairness_clause_count --> clauses that make a comparison legal before it is run. `docs/FAIRNESS_CONTRACT.md`
- **Identity cards** — <!-- gen:identity_card_count --> cards declaring reference, deviations, objective, pseudo-gradient, and symmetry; the admission ticket for a new algorithm. `docs/IDENTITY_CARDS.md`
- **A corrections log** — <!-- gen:corrections_count --> public entries recording what failed, why, and what changed. `docs/CORRECTIONS.md`

`uv run comp --help` is the instrument itself.

> The goal is not simply to build another model. It is to build the scientific instrument required to discover what makes learning systems work.

<!-- notes -->
Close on the ask, not on the architecture: bring one algorithm, card it, and let the contract compare it. The deposit is a YAML identity card and a run under a declared operating point.

End on the closing line, then stop. Offer the repository and a concrete next step — card an algorithm you already trust, and we will publish whether it survives.
<!-- /notes -->
