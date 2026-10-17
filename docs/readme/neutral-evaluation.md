## Neutral evaluation — why a referee, and how this one works

A comparison of learning algorithms has a structural problem: the people best
placed to run it are usually the people who invented the algorithms. Inventors
carry publication, tenure and funding incentives; their hyperparameter search is
sized to their budget rather than to the question; and research code is not
always the code the paper describes. None of that requires bad faith. It is
enough that a protocol run by a participant can be disputed by whoever the
protocol ranks lower.

This project holds no credit rule of its own. That is a narrow, checkable
position, and it is the reason to trust a comparison produced here: the referee
has no arm in the race. What follows is the procedure the referee publishes,
not a claim about anyone else's motives.

- **Pre-registered thresholds.** A claim's metric, superiority margin, error
  rate and seed budget can be declared before the run
  (`configs/preregistrations/*.json`, `computronium.validation.preregistration`).
  A claim with no matching registration is labelled `[unpreregistered_claim]`
  beside the claim; the report does not imply otherwise.
- **Equal treatment of arms.** `docs/FAIRNESS_CONTRACT.md` (F-1…F-<!-- gen:fairness_clause_count -->,
  append-only) fixes data, budget, stopping rule, seeds and reporting. All
  comparisons are reported unfiltered, or a correction is named.
- **Declared deviations.** <!-- gen:identity_card_count --> concrete credit,
  update and plasticity primitives ship an `AlgorithmIdentityCard` with its paper
  citation and a *Deviations* column (`docs/IDENTITY_CARDS.md`, generated;
  `--strict` is a gate). The defensible statement is "independent
  re-implementation with disclosed deviations", never "verified upstream".
- **A chance line and a positive control.** An ablation table is printed only
  when the other five structural axes and the swept hyperparameters are held
  fixed; every row carries `n` and `std`; an arm at chance is labelled
  `[at chance]`; and the run checks a known-good control arm before publishing
  the comparison.
- **A corrections log.** <!-- gen:corrections_count --> superseded measurements
  are recorded with the audit that invalidated them (`docs/CORRECTIONS.md`), and
  claims are held in a ledger outside the engine that produced them
  (`packages/ceec-core`).

**What this does not claim.** All credit rules here are this project's
re-implementations, with deviations declared and cited — not the inventors'
reference code. Equal-effort HPO is a protocol (`docs/hpo_protocol.md`,
`biopl-hpo`), not enforced by `comp run`. There is no blinding. And no rule in
this repository is the author's invention; the comparison stack is the
contribution.

**Why a consortium.** An honest comparison has a price: 63 seeds per group for a
d=0.5 effect, times every arm, every axis, and each family's fair share of
hyperparameter trials. No single participant can pay it, and an inventor has no
reason to fund a comparison they might lose. The [Computronium
Consortium](docs/CONSORTIUM.md) is the institution shaped like that gap:
members contribute algorithms and implementations, and receive a comparison
stack they can cite — pre-registered, unfiltered, and open to correction,
including of the referee.
