# Gate Calibration Specification (B5)

**Status**: Draft — based on H1/H2/H3 ladder run data (Nov 2026)

---

## Observed Gate Verdict Distribution

| Experiment | Total | PASS | FAIL | Quarantined | Failure Causes |
|------------|-------|------|------|-------------|----------------|
| H1 Ladder (credit×update) | 62 | 46 | 16 | 16 | Numerical (11), Runtime (5) |
| H2 Ladder (dynamics×substrate) | 78 | 59 | 19 | 19 | Numerical (14), Runtime (5) |
| H3 Ladder (plasticity×credit) | 70 | 66 | 4 | 4 | Numerical (4) |

---

## Failure Taxonomy

### 1. Numerical Failures (non-finite metrics)
**Pattern**: `non-finite metrics [...] for <cell_key>`
**Affected combos**: homeostatic/elastic_consolidation, thermodynamic_contrast/elastic_consolidation, pc_alm/muon on memristive, ternary combos
**Root cause**: Step size overshoot on per_element_displacement rules + substrate-specific numerical issues
**Frequency**: ~70% of failures

### 2. Dtype Mismatches (BFloat16 vs Float)
**Pattern**: `mat1 and mat2 must have the same dtype, but got BFloat16 and Float`
**Affected combos**: homeostatic×euclidean (digital), target_inversion×muon (digital)
**Root cause**: Mixed precision handling in homeostatic/target_inversion credit with certain substrates
**Frequency**: ~15% of failures

### 3. Bool Tensor Operations
**Pattern**: `"addmm_impl_cpu_" not implemented for 'Bool'`
**Affected combos**: homeostatic×natural_gradient (digital), pc_alm×euclidean (digital)
**Root cause**: Boolean mask tensors used in matmul without float conversion
**Frequency**: ~10% of failures

### 4. Type Cast Errors
**Pattern**: `result type Float can't be cast to the desired output type Char`
**Affected combos**: thermodynamic_contrast×elastic_consolidation (digital)
**Root cause**: Output type mismatch in elastic_consolidation update

---

## Gate Thresholds

### Current (Implicit)
- **PASS**: epochs_completed ≥ requested_epochs AND param_count ≤ param_budget × (1 + tolerance) AND all metrics finite
- **FAIL**: Any violation above
- **Quarantine**: FAIL verdict → quarantined

### Proposed Calibration
| Metric | Threshold | Action |
|--------|-----------|--------|
| `val_acc` NaN rate | > 10% per cell | Quarantine |
| `train_loss` divergence | > 100× initial | Quarantine |
| `walltime_s` per epoch | > 300s (L0) | Skip cell |
| `param_count` / `param_budget` | > 1.05 | FAIL |
| Dtype mismatch | Any | FAIL + alert |
| Non-finite metrics | Any | FAIL + alert |

---

## Per-Axis Failure Rates (H1 Ladder)

| Credit | Total | PASS | FAIL | Primary Cause |
|--------|-------|------|------|---------------|
| gradient | 12 | 11 | 1 | Bool tensor (pc_alm) |
| homeostatic | 14 | 8 | 6 | BFloat16, non-finite |
| pc_alm | 13 | 10 | 3 | Non-finite, Bool tensor |
| target_inversion | 7 | 5 | 2 | BFloat16, non-finite |
| thermodynamic_contrast | 16 | 12 | 4 | Non-finite, cast error |

| Update | Total | PASS | FAIL | Primary Cause |
|--------|-------|------|------|---------------|
| euclidean | 12 | 11 | 1 | BFloat16 (homeostatic) |
| lion | 11 | 11 | 0 | — |
| elastic_consolidation | 9 | 6 | 3 | Non-finite |
| natural_gradient | 8 | 5 | 3 | Bool tensor, non-finite |
| muon | 7 | 5 | 2 | BFloat16, non-finite |
| mean_norm | 5 | 4 | 1 | Non-finite |

---

## Calibration Actions

### Immediate (Code Fixes)
1. **Fix step_size domain** for per_element_displacement rules: split domain by step_semantics
   - `gradient_relative`: (1e-4, 0.5, log)
   - `per_element_displacement`: (1e-5, 0.05, log)

2. **Add dtype consistency check** in credit assignment before training
   - Ensure substrate precision matches credit computation dtype

3. **Add Bool→Float conversion** in homeostatic/target_inversion credit paths

### Monitoring (Alerts)
1. **Drift detection**: Alert when FAIL rate > 25% per axis combination
2. **Metric coverage**: Alert when non-finite metrics > 5% of cells
3. **Dtype mismatch**: Alert on any BFloat16/Float mixing

### Documentation
- Record known-bad combinations in `docs/specs/known_failures.md`
- Update availability predicates to exclude known-failing combos

---

## Acceptance Criteria for Calibrated Gate

- [ ] FAIL rate ≤ 15% on diverse 6-axis sweep (current: ~25%)
- [ ] Zero dtype mismatch failures
- [ ] Zero Bool tensor operation failures
- [ ] Non-finite metrics < 5% of cells
- [ ] All known-bad combos documented and excluded

---

## Related Tasks

- **B6**: Drift detection alert → implement FAIL rate monitoring
- **B7**: Metric coverage warnings → implement non-finite metrics alerting
- **B10**: Validation codegen → generate availability predicates from failure data

Generated: 2026-11-07 | From: H1/H2/H3 ladder runs