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

| Field | Correction 4 — ruler learning rates never reached an optimizer |
|---|---|
| Original claim | The 23 `ruler_lr_*` priors gave the ruler (backprop) baseline a task-calibrated learning rate, and the standard baselines carried those rates. |
| Original metric | `learning.prior.get_ruler_lr(task)` looked up `ruler_lr_{task}`; `BaselineRegistry.STANDARD_BASELINES` wrote the chosen rate to `dynamics.step_size`. |
| Audited procedure | Repository grep: `get_ruler_lr` has no production caller (tests only). Every standard baseline selects `dynamics="instantaneous"`, whose `settle` never reads `config.step_size`; the optimizer reads `update.step_size`, which the baselines left at the factory default (`euclidean` 0.01, `adam` 1e-3). A baseline asking for 3e-4 therefore trained at 1e-3. |
| Affected conclusions | Any `bp_deficit` or `ruler_*_ratio` computed against a discovered baseline whose intended rate was not the factory default (CNN, language, RL, graph and memory arms); the ruler-LR table itself. |
| Replacement metric | Standard baselines declare `update.step_size`, the field the optimizer reads. The `ruler_lr_*` rows and `get_ruler_lr` are deleted; a baseline rate is now visible where it acts. |
| Status | corrected — locked by `test_ruler_lr_priors_stay_retired` and `test_standard_baselines_set_the_optimizer_step` |
| Commit | this commit |

| Field | Correction 5 — sampled settle step overridden at construction |
|---|---|
| Original claim | A sweep could choose `dynamics.step_size` for every dynamics primitive. |
| Original metric | `compose_configs` called `apply_dynamics_step_size` unconditionally, replacing the harvested (possibly sampled) value with the calibrated `dynamics_step_size_{diffusion,predictive_settling}` center. |
| Audited procedure | Read of `kernel/compose.py`: the override received `active.values["dynamics.step_size"]` and ignored `coordinate.params`; a sampled value was therefore a phantom knob for those two primitives. |
| Affected conclusions | Any diffusion or predictive-settling cell whose sweep varied the settle step: all trained at the calibrated center. |
| Replacement metric | The calibrated center fills only an unsampled value; an explicit `dynamics.step_size` wins. Locked by `test_a_sampled_dynamics_step_size_survives_composition`. |
| Status | corrected |
| Commit | this commit |

| Field | Correction 6 — `activations_mb: 0.0` was a claim, not a measurement |
|---|---|
| Original claim | Every kernel backend's `get_memory_stats()` reported `activations_mb: 0.0`, so the O(1)-memory classes were "verified" by the same call that produced the number. |
| Original metric | A hardcoded zero constant in 14 `get_memory_stats()` returns across `acceleration/*_kernels.py`; `KernelBackend.memory_complexity` had no field distinguishing a declared class from a measured one. |
| Audited procedure | TODO93 §1 read of the return sites against the tensors each kernel actually holds: `contrastive_kernels.contrastive_step` keeps `free_acts` **and** `nudged_acts` (≈2× a forward pass), so its O(1) declaration was false and its 0.0 would have poisoned every memory verdict. |
| Affected conclusions | Any memory claim or frontier read from a backend's self-reported stats; the O(1) declaration of the two-pass contrastive and PEPITA/FF families. |
| Replacement metric | `activations_mb` is `None` until measured; `KernelBackend.complexity_verified` (declaration, `False` until a measured ladder exists) travels with `memory_complexity` into `get_backend_info` and the export manifest. Locked by `test_no_backend_hands_back_a_fabricated_activation_measurement`. |
| Status | corrected — all 14 sites now report `None`; every backend declares `complexity_verified=False` until its ladder lands in `docs/BENCHMARKS.md` |
| Commit | this commit |

| Field | Correction 7 — the contrastive PEPITA nudge was a `pass` |
|---|---|
| Original claim | `PEPITAContrastiveKernel` trained by the standard/error-modulated contrastive rule. |
| Original metric | `contrastive_step` → `free_phase` + `nudged_phase`; the nudged pass ran the same forward with the error modulation replaced by `pass`, so `ΔW = (std_post − err_post)ᵀ pre / B` was identically zero. |
| Audited procedure | TODO93 §9.2 stub detector: a non-zero target error must move the update by more than tolerance. Measured before the fix: zero in both layers, `loss` fell only because the reported scalar is the free/nudged difference. |
| Affected conclusions | Every cell routed through `PEPITA_CONTRASTIVE` (and the SNN and FF contrastive kernels) — they trained nothing. |
| Replacement metric | The nudged pass backprojects `one_hot(target) − free_logits` through the fixed feedback matrix and replays the stack under `no_grad` semantics (PEPITA's published two-forward design). The SNN and FF contrastive kernels cannot support their algorithm (no target nudge; no label channel in the input) and are `available=False` with a reversal trigger; `KernelRegistry.get` refuses them. Locked by `test_pepita_nudged_pass_moves_the_update` and `test_free_and_nudged_phases_differ_under_error`. |
| Status | corrected — one kernel fixed, two marked unavailable with reasons |
| Commit | this commit |

| Field | Correction 8 — the activation coefficient is ≈4, not 1 |
|---|---|
| Original claim | Activation bytes are `c·L·B·W·4` with `c≈1` for a Linear+ReLU stack (c≈2 with LayerNorm), so the pilot appendix priced L=64, B=8192, W=1024 activations at 2.0 GiB. |
| Original metric | Analytic hand count of the *stored inputs* of each matmul. |
| Audited procedure | TODO93 T4a measured the decomposition on CUDA (`EpochResources._decomposition`): plain backprop, fp32, W=256, B=2048, depth 4/8/16. Activation growth per depth step implies **c = 4.1** on two independent deltas (spread < 1%). The peak carries the stored input, the layer output, and the two backward gradient buffers — four per-layer tensors, not one. |
| Affected conclusions | The absolute peak in the pilot appendix (2.0 GiB activations → ≈8.4 GiB at the same point) and any admission check priced from it. The **binding gate conclusion does not change**: the activation share rises with c (0.96 measured at B=2048/L=8), so the cell is memory-bound either way. |
| Replacement metric | The coefficient is measured, never assumed: `test_activation_growth_carries_one_measured_coefficient` locks self-consistency across depth deltas (the cuBLAS workspace floor cancels in the difference). The pre-registration's binding arithmetic must use the measured c. |
| Status | corrected — c measured at 4.1 on the Linear+ReLU claim geometry |
| Commit | this commit |
