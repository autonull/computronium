# local-feedback

Adaptive feedback projections for local credit assignment — a standalone
PyTorch module extracted from the Computronium project (evidence: X-ALI-001,
belief B-H1-ADAPTIVE-LOCAL-INVERSES).

## What it does

Local learning rules need a way to push output errors back to earlier layers
without a global backward pass. The standard choice is a **fixed random
feedback** matrix. This package implements the validated alternative: a
feedback matrix that **slowly re-projects onto the normalized forward weight**
it feeds, holding the fixed arm's expected Frobenius norm so comparisons stay
matched-norm.

In the two-layer local trainer shipped here, the feedback projects the output
error back to the hidden layer. As it re-projects onto the (changing) readout
weight, the projected error approaches true backpropagation through that
weight — which is why descent quality improves.

## Install

```bash
pip install -e packages/local-feedback   # from the Computronium repo
```

## Usage

```python
from local_feedback import AdaptiveFeedback, FixedFeedback, LocalFeedbackTrainer

fb = AdaptiveFeedback(in_features=32, out_features=4, feedback_lr=1.0)
trainer = LocalFeedbackTrainer(model, fb, lr=0.05)
stats = trainer.train_step(x, y)   # StepStats: loss, displacement, improvement_per_norm
```

`feedback_lr=1.0` reproduces the X-ALI-001 re-projection exactly
(`B := scale * W / ||W|| * sqrt(numel)`); smaller values blend more slowly
(`feedback_lr=1e-2` is the "slow adaptation" setting; `update_frequency`
throttles how often the projection refreshes).

## Demo

```bash
python examples/local_feedback_demo.py
```

Runs the fixed vs adaptive arms on CPU in well under a second and prints
final loss, late-half improvement_per_norm, and feedback alignment per arm.

## Benchmark

```bash
python benchmarks/adaptive_vs_fixed.py --quick
```

3 seeds × 60 steps, mean±variance, matched norm. Quick-mode result (the
validated scope): adaptive beats fixed on late-half improvement_per_norm on
all seeds, with final feedback alignment → 1.0 (adaptive) vs ≈0.46 (fixed)
and descent quality ≈0.94 vs ≈0.75.

## Validated scope

- Two-layer local trainer (random hidden features + linear readout trained
  by feedback-projected error), cross-entropy task.
- Quick budget: 60-step trajectories, 3 seeds, matched-norm control.
- The X-ALI-001 verdict statistic (adaptive > fixed late-half
  improvement_per_norm on all seeds) holds in this standalone form.

## Known limitations

- Validated only on this quick-budget task family; no deep-network,
  convolutional, or hardware claims.
- The mechanism requires a nonzero forward weight (zero weights are skipped)
  and does not use per-activity information (the `activity` argument is
  reserved for future variants).
- Adaptive feedback converges toward the readout weight direction; where the
  readout itself is degenerate, the projected credit inherits that degeneracy.
- Not validated against internal Computronium EqProp systems end-to-end; the
  standalone trainer is a reduced equivalent (parity pinned in
  `tests/platform/test_local_feedback_parity.py` at the mechanism level).

## Evidence references

- Experiment X-ALI-001 (CEEC ledger): norm-matched fixed-vs-adaptive feedback,
  improvement_per_norm over 30-step trajectories, 3 seeds.
- Belief B-H1-ADAPTIVE-LOCAL-INVERSES.
- Verification level: mechanism-level parity + deterministic quick benchmark;
  no promotion gate executed for the package itself.