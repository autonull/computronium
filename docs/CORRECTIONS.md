# Corrections Log

Transparent record of superseded measurements, per the `CorrectionRecord`
schema (`computronium/core/correction_record.py`). Each row: original claim,
the audit that invalidated it, and the replacement metric.

| Field | Correction 1 — Jacobian ρ/σ_max conflation |
|---|---|
| Original claim | Power-iteration "spectral radius" ρ(J_F) estimates from `estimate_spectral_radius` were reported as the asymptotic stability margin of joint transitions (E1/E3 campaign logs, RESEARCH3.md §stability). |
| Original metric | `estimate_spectral_radius` (finite-difference power iteration on J·v, reported as ρ(J_F)). |
| Audited procedure | TODO18 2.1 audit + regression tests `tests/property/test_jacobian_amplification.py`: on nonnormal J ([[0.5,10],[0,0.5]]) the iteration converges to the dominant eigen-direction (≈0.5) while ‖J‖₂ ≈ 10.025 — the estimator is neither a certified ρ(J) nor σ_max(J). |
| Affected conclusions | E3 σ_max(J_F) frontier measurements labeled "spectral radius"; E1 composition-error boundary attributions that used ρ(J_F) > 1 as the stability criterion. |
| Replacement metric | Separated estimators: `estimate_directional_amplification` (sampled directional gain), `dominant_singular_value` (exact σ_max), `spectral_radius_from_jacobian` (exact ρ). Frontier claims must name which metric they use. |
| Status | corrected (campaign logs flagged `requires_rerun` for any quantitative frontier numbers quoted pre-TODO18) |
| Commit | this commit |

| Field | Correction 2 — J2 check strength |
|---|---|
| Original claim | `test_j2_theta_immutable_intra_episode` proved persistent θ is never mutated intra-episode. |
| Original metric | Clone-snapshot + `torch.allclose` comparison of `geometry.params` only. |
| Audited procedure | TODO18 2.2: naive clone comparison misses in-place mutate-then-restore patterns and storage rebinding; substrate state and optimizer moments were unaudited. |
| Affected conclusions | "Frozen-θ guaranteed" claims on coordinates validated only by the old check. |
| Replacement metric | `FrozenThetaAudit` (`computronium/core/frozen_theta.py`): bitwise equality + `Tensor._version` counters + `data_ptr` over geometry params, substrate state, and optimizer moments. Adversarial tests in `tests/property/joint/test_frozen_theta_audit.py`. |
| Status | corrected |
| Commit | this commit |
| Field | Correction 3 — step-size multiplier column |
|---|---|
| Original claim | The 29 `step_size_override_<dynamics>_<credit>` priors encoded measured per-combination attenuations, and the campaign compared learning rules through them. |
| Original metric | A multiplier applied to `ParameterUpdateConfig.step_size` after factory construction (`ontology/update.py::_apply_step_size_overrides`); one row composed `energy_minimization × thermodynamic_contrast` to 5e-7 against a rule that learns at 1e-3. |
| Audited procedure | `scripts/probes/step_size_multipliers.py --ladder` on `digits` at gate 2b's reference regime: `train_acc` 0.105 / 0.080 / 0.411 / 0.878 at composed lr 5e-7 / 1e-4 / 1e-3 / 5e-3. No row carried a measurement; every row could only attenuate. |
| Affected conclusions | Any ranking that read a starved arm as a property of its learning rule. The column was retired at 1.0 (TODO48b R4) and removed outright in TODO66 §15, together with the post-construction multiplier mechanism. |
| Replacement metric | The swept `update.step_size` is the only step scale; unswept defaults come from the schema's declared prior (`dynamics_step_size_default` and the two calibrated overrides). |
| Status | corrected — column deleted; the absence is locked by `test_no_step_size_multiplier_priors` |
| Commit | this commit |
