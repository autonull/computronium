# Evaluation consortium — what a member gets, and what they accept

## What you get

- **A comparison stack you can cite.** An append-only fairness contract
  (`docs/FAIRNESS_CONTRACT.md`, F-1…F-6) that fixes data, budget, stopping rule,
  seeds and reporting; all comparisons unfiltered, or a correction named.
- **Pre-registered thresholds.** Declare the metric, superiority margin, error
  rate and seed budget before the run
  (`configs/preregistrations/*.json`); `paired_comparison` returns a bootstrap
  CI, a sign-flip permutation p, and Cohen's dz.
- **Your implementation's deviations, in writing.** Every primitive ships an
  `AlgorithmIdentityCard` with its paper citation and a *Deviations* column,
  generated and drift-locked (`docs/IDENTITY_CARDS.md`, `--strict`).
- **The shared memory.** A corrections log that records superseded measurements
  with the audit that invalidated them (`docs/CORRECTIONS.md`).

## What a member accepts

- Pre-register the comparison before running it.
- Report unfiltered, including the nulls.
- Publish the deviations your implementation declares from its paper.
- Let the corrections log record a refutation of any estimate, including ours.

## What this does not yet do

1. All credit rules here are the project's re-implementations with disclosed
   deviations — not the inventors' reference code, and not verified against it.
2. Equal-effort HPO is a protocol (`docs/hpo_protocol.md`, `biopl-hpo`), not an
   enforced invariant of `comp run`.
3. There is no blinding; the analyst sees arm identity.
4. An unregistered claim is **labelled**, not refused.
5. Coverage is one language and one task family so far (`digits`-class vision).

## The invitation

*Bring your algorithm and the paper whose deviations we must declare; we will
pre-register the comparison, publish the result unfiltered including the nulls,
and log our own corrections — and neither of us gets to choose the outcome.*

The argument is structural, not moral: an honest comparison has a price — 63
seeds per group for a d=0.5 effect, times every arm and every axis — and no
single participant can pay it. A consortium is the institution shaped like that
gap.
