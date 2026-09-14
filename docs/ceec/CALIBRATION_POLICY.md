# Calibration Policy

## When calibration is required

Calibration records are required for:

- pre-registered experiment predictions with explicit probability,
- promotion predictions,
- boundary rescue probability estimates,
- reopen trigger estimates,
- oracle expected-value predictions when explicit.

## Scores

With point probability `p` and binary outcome `y`:

```
Brier    = (p - y)^2
LogScore = y*log(p) + (1-y)*log(1-p)
```

With interval probabilities: store the interval; compute Brier/log only when a declared point reduction exists (e.g. interval midpoint with method recorded).

## Review thresholds

Review calibration when any of:

- promotion reversal rate > 20%,
- boundary reopen rate > 20%,
- mean Brier drifts upward over a rolling window of 10 records,
- override rate increases round-over-round,
- quarantine rate spikes (> 2 instruments in a round).

A `select_experiment` override on a single-eligible-candidate pool is vacuous (no alternative to select against) and is not recorded, so the override rate counts real selections only.

## Report

`ceec calibration-report` emits predicted vs observed success, mean Brier, promotion/boundary durability, reopen/quarantine/override rates.
