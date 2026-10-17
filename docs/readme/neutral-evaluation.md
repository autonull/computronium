## Neutral evaluation — what this repository does, in its own voice

A comparison is only useful if a reader can check how it was run. This project
therefore publishes its procedure, not its motives:

- **Pre-registered thresholds.** A claim's metric, superiority margin, error
  rate and seed budget can be declared before the run
  (`configs/preregistrations/*.json`, `computronium.validation.preregistration`).
  A claim with no matching registration is labelled `[unpreregistered_claim]`
  beside the claim; the report does not imply otherwise.
- **Equal treatment of arms.** `docs/FAIRNESS_CONTRACT.md` (F-1…F-6,
  append-only) fixes data, budget, stopping rule, seeds and reporting. All
  comparisons are reported unfiltered, or a correction is named.
- **Declared deviations.** Every concrete credit, update and plasticity
  primitive ships an `AlgorithmIdentityCard` with its paper citation and a
  *Deviations* column (`docs/IDENTITY_CARDS.md`, generated; `--strict` is a
  gate). The defensible statement is "independent re-implementation with
  disclosed deviations", never "verified upstream".
- **A chance line and a positive control.** An ablation table is printed only
  when the other five structural axes and the swept hyperparameters are held
  fixed; every row carries `n` and `std`; an arm at chance is labelled
  `[at chance]`; and the run checks a known-good control arm before publishing
  the comparison.
- **A corrections log.** Superseded measurements are recorded with the audit
  that invalidated them (`docs/CORRECTIONS.md`), and claims are held in a
  ledger outside the engine that produced them (`packages/ceec-core`).

**What this does not claim.** All credit rules here are this project's
re-implementations, with deviations declared and cited — not the inventors'
reference code. Equal-effort HPO is a protocol (`docs/hpo_protocol.md`,
`biopl-hpo`), not enforced by `comp run`. There is no blinding. And no rule in
this repository is the author's invention; the comparison stack is the
contribution.
