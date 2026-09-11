# Neuromorphic Edge Blueprint

How the platform's validated mechanisms map onto hardware-constrained
learning substrates.

> **Status: simulation only.** No physical hardware validation has been
> performed. Everything below is a design translation of digital simulation
> results; deployment claims would require hardware campaigns outside the
> validated scope.

## Mechanism → hardware mapping

| Mechanism | Edge property | Why it maps |
|---|---|---|
| Frozen backbone + ψ readout (`psi-peft`) | without weight transport; on-device adaptation | θ never changes after freezing; only a small readout accumulates trace-decayed ridge statistics — compatible with substrates that cannot backprop through the core |
| Adaptive feedback (`local-feedback`) | local credit without a global backward pass | hidden-layer credit is computed from projected output error (`e @ B`) and local activities; B drifts slowly toward the forward weight, an EMA update realizable with local accumulators |
| Role-split updates (`computronium-lab`) | heterogeneous update hardware | expensive orthogonalization (Muon-class) is confined to the readout weight; all other weights use cheap euclidean updates — a natural split between "smart" and "dumb" update circuitry |
| Stable amplification (`stability`) | noisy-substrate transient robustness | coordinates with ρ ≤ limit and σ_max > 1 give large transient signal gain without divergence (X-STA-001/002); useful where substrate noise is bursty and short-horizon recall matters |

## Calibration and guarding on-device

The `stability` guard (`attach(model)` → `StabilityVerdict`) is calibrated
via ROC on Ginibre harvests with a registered artifact
(`stability_guard_pr5.json`: τ=1.029, false-kill 0.0 in the validated
family). Its probe costs 2–13× a settling step, so it deploys at a
calibrated interval — the package ships `overhead_and_interval` for exactly
this budgeting decision.

## What is NOT claimed

- No analog/noisy-device weight-update results (all updates simulated in
  float32).
- No power/latency measurements on real neuromorphic chips (the MAC energy
  table in `stability.resources` is a static model, not a measurement).
- No claim that ψ readouts or local feedback *outperform* backprop on
  hardware; the validated results are relative to their matched baselines
  under the budgets stated in the recipe book.

## Suggested validation sequence (future, out of TODO20 scope)

1. Quantize ψ readout statistics to the target numeric format; re-run the
   task-switching benchmark with per-seed quantization noise.
2. Replace the EMA feedback blend with a device-realistic update; re-run
   X-ALI-002's short-trajectory protocol.
3. Inject substrate noise into the stable-amplification family and verify
   the X-STA-002 paired-replay predictions on hardware.