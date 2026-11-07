# Credit × Update Comparison (A1 Artifact)

**Source Runs:**
- **H1 Ladder** (0.5h, TPE, L0→L1→L2): `experiment_20261107_083156.duckdb` — 62 cells (48 L0 + 9 L1 + 5 L2)
- **S1 Static** (0.5h, L0 only): `experiment_20261107_112806.duckdb` — 28 cells
- **S1 TPE** (0.5h, L0 only): `experiment_20261107_113630.duckdb` — 17 cells

---

## Key Finding: Only `gradient × euclidean` Reaches Claim Grade (L2)

| Credit | Update | L0 (n=1) | L1 (n=3) | L2 (n=5) | Notes |
|--------|--------|----------|----------|----------|-------|
| **gradient** | **euclidean** | 0.7625 | **1.0000** | **1.0000** | **Only L2 claim-eligible combo** |
| gradient | lion | 1.0000 | 1.0000 | — | L1 only (n=3) |
| homeostatic | elastic_consolidation | 0.5112 | — | — | |
| homeostatic | euclidean | 0.5058 | — | — | |
| homeostatic | natural_gradient | 0.5162 | — | — | |
| pc_alm | lion | 0.5817 | 0.5708 | — | Best non-gradient L1 |
| pc_alm | elastic_consolidation | 0.4900 | — | — | |
| pc_alm | euclidean | 0.5000 | — | — | |
| target_inversion | euclidean | 0.4725 | — | — | |
| thermodynamic_contrast | euclidean | 0.4962 | — | — | |

**Interpretation:** Standard backprop (`gradient`) + SGD (`euclidean`) is the only combination that consistently trains to perfect accuracy under replication (5 seeds at L2). All other credit/update pairs fail to reach L2 within the 0.5h budget.

---

## S1: Static vs TPE on Credit × Update (L0 Only)

### Static Survey (28 cells, diverse exploration)

| Credit | Update | Mean Val Acc | n | Notable |
|--------|--------|--------------|---|---------|
| thermodynamic_contrast | euclidean | **0.8125** | 2 | 2nd highest L0 |
| target_inversion | muon | **1.0000** | 1 | Single seed perfect |
| homeostatic | muon | **0.7544** | 2 | High variance |
| gradient | euclidean | 0.7625 | 1 | Baseline |
| pc_alm | euclidean | 0.4717 | 3 | |
| homeostatic | euclidean | 0.2830 | 5 | High variance, some failures |

**Static** explored 23 unique credit×update pairs, found occasional high performers but with high variance (n=1-2).

### TPE Survey (17 cells, adaptive)

| Credit | Update | Mean Val Acc | n |
|--------|--------|--------------|---|
| gradient | lion | **1.0000** | 1 |
| gradient | euclidean | 0.7625 | 1 |
| pc_alm | natural_gradient | 0.5125 | 1 |
| target_inversion | natural_gradient | 0.5125 | 1 |
| homeostatic | natural_gradient | 0.5075 | 1 |
| pc_alm | muon | 0.4900 | 2 |

**TPE** quickly focused on `gradient` and `pc_alm` regions but only evaluated 12 unique pairs before worker pool crashes terminated the run at ~17 cells.

### Comparison

| Metric | Static | TPE |
|--------|--------|-----|
| Cells evaluated | 28 | 17 |
| Unique credit×update pairs | 23 | 12 |
| Max val_acc found | 1.0000 (target×muon) | 1.0000 (gradient×lion) |
| gradient×euclidean found | ✅ (0.7625) | ✅ (0.7625) |
| Budget efficiency | Lower (random) | Higher (adaptive) |
| Worker crashes | 0 | 6 (at ~16 cells) |

---

## Recommendations

1. **Claim-Grade Baseline**: `gradient × euclidean` is the only combination with replicated L2 evidence (5 seeds, 1.0000 mean). Use as reference for all future comparisons.

2. **Ladder Budget**: 0.5h is insufficient for full L0→L1→L2 on 30 combos. Increase to 2h or reduce axis cardinality.

3. **Worker Pool Stability**: TPE crashes at ~16 cells due to "process terminated abruptly" (known deferred issue). Static is more stable for L0 exploration.

4. **High-Variance Signals**: `target_inversion × muon` and `thermodynamic_contrast × euclidean` showed single-seed 1.0/0.81 in Static — warrant dedicated L1 follow-up (3 seeds).

---

## Raw Data References

- H1 Ladder: `uv run comp report --store experiments/experiment_20261107_083156.duckdb --format text`
- S1 Static: `uv run comp report --store experiments/experiment_20261107_112806.duckdb --format text`
- S1 TPE: `uv run comp report --store experiments/experiment_20261107_113630.duckdb --format text`

Generated: 2026-11-07 | Commit: `088052cc`