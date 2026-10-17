# The Computronium Consortium

**An independent referee for the algorithm zoo.**

## The problem worth solving

Learning-rule research is fast, large, and almost impossible to compare across.
Every result arrives with its own dataset, budget, stopping rule, seed count and
hyperparameter effort. Those choices are not neutral: they decide the ranking.
And the people with the deepest knowledge of a rule are its inventors, who also
carry publication, tenure and funding incentives that no individual should have
to overcome alone.

The result is a gap that hurts everyone. Inventors cannot prove their rule was
given a fair shot. Practitioners cannot tell whether a reported win is the rule
or the tuning budget. Reviewers cannot check a protocol they cannot see. And the
field keeps re-litigating comparisons instead of building on them.

Computronium exists to close that gap. It is a six-axis laboratory with **no
credit rule of its own** — no horse in the race — and an evaluation kernel that
was built for exactly one purpose: to compare mechanisms under a protocol that
is declared before the result is known.

## What the referee already enforces

- **An append-only fairness contract** (F-1…F-6,
  [`FAIRNESS_CONTRACT.md`](FAIRNESS_CONTRACT.md)): identical data, budget,
  stopping rule, seeds and reporting for every arm; all comparisons published
  unfiltered, or a named correction.
- **Pre-registered thresholds** ([`preregistration.py`](../computronium/validation/preregistration.py)):
  metric, superiority margin, error rate and seed budget declared before the
  run; `paired_comparison` returns a bootstrap CI, a sign-flip permutation p,
  and Cohen's dz.
- **Algorithm Identity Cards** ([`IDENTITY_CARDS.md`](IDENTITY_CARDS.md)):
  every primitive ships its paper citation and a *Deviations* column stating
  where this implementation departs from the published algorithm — generated,
  `--strict`, drift-locked.
- **A phantom-knob detector** (`construction.phantom_knobs`): a search key that
  is sampled by a sweep and silently dropped at construction is a class of
  defect, not an accident.
- **A compute-matched HPO protocol** ([`hpo_protocol.md`](hpo_protocol.md)):
  the same patience tier for every family, so a tuning budget cannot be the
  explanation of a ranking.
- **A corrections log** ([`CORRECTIONS.md`](CORRECTIONS.md)): superseded
  measurements are recorded with the audit that invalidated them, including
  this project's own.
- **An epistemic ledger outside the engine** (`packages/ceec-core`): claim
  decisions are not held by the code that produced them.

None of this is marketing. Each line is a lock that fails when violated.

## What a member gets

- **A comparison you can cite**, with the contract version and the corrections
  log attached.
- **Your rule represented faithfully**, with deviations from your paper written
  down and checkable by you before publication.
- **A fair shot at a favourable result** — the documented compute-matched HPO
  protocol ([`hpo_protocol.md`](hpo_protocol.md)) gives every family the same
  patience tier, so a tuning-budget difference cannot explain a ranking.
- **A public null, if that is what the data say.** A null published under a
  pre-registered protocol is a credential, not a loss: it is the evidence that
  your result is real.

## What a member accepts

- Pre-register the comparison before running it.
- Report unfiltered, including the nulls.
- Publish the deviations your implementation declares from its paper.
- Let the corrections log record a refutation of any estimate, including yours
  and ours.

## What we do not yet do

Stated here so no member discovers it in the first meeting:

1. All credit rules in this tree are the project's re-implementations with
   disclosed deviations — not the inventors' reference code, and not verified
   against it.
2. Equal-effort HPO is a protocol and a separate CLI (`biopl-hpo`), not an
   enforced invariant of `comp run`.
3. There is no blinding; the analyst sees arm identity.
4. An unregistered claim is **labelled**, not refused.
5. Coverage is one language and one task family so far (`digits`-class vision).

## The invitation

*Bring your algorithm and the paper whose deviations we must declare. We will
pre-register the comparison, publish the result unfiltered including the nulls,
and log our own corrections — and neither of us gets to choose the outcome.*

The argument is structural, not moral. An honest comparison has a price: 63
seeds per group for a d=0.5 effect, times every arm, every axis, and each
family's fair share of hyperparameter trials. No single participant can pay it.
A consortium is the institution shaped like that gap — and every member who
joins is demonstrating, in public and in writing, that they want the truth about
learning mechanisms more than a favourable number.

The procedure is described in the README's [neutral
evaluation](../README.md#neutral-evaluation--why-a-referee-and-how-this-one-works)
section. The first step is a registered comparison, not a memorandum.
