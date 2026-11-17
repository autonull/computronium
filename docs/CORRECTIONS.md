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

| Field | Correction 9 — the continual runner's learning-rate field never reached an update |
|---|---|
| Original claim | `CLConfig.lr` (and `CLConfig.si_xi`) configured the arm's learning rate, so a ladder over it measured the arm at that point. |
| Original metric | `runner._create_arm` constructed every factory without `config.lr`; `create_backprop_arm`, `create_ewc_arm`, `create_local_arm` and the rest kept their factory defaults (`euclidean`/`elastic_consolidation` 1e-3). |
| Audited procedure | TODO93 C1's first ladder cell at `lr=1e-3` and a direct call at `lr=1e-2` produced the same update scale: read of `_create_arm` against every factory signature. `CLConfig.si_xi` was likewise unread. |
| Affected conclusions | Any continual-learning row whose config varied `lr` or `si_xi`; a ladder over those fields measured one rate three times. |
| Replacement metric | Every arm factory takes `lr` (and `create_si_arm` takes `xi`) and `_create_arm` passes `config.lr`/`config.si_xi`; `test_config_lr_reaches_every_credit_arm` fails if the thread is removed. |
| Status | corrected — the ladder now varies the rate it declares |
| Commit | this commit |

| Field | Correction 10 — the continual credit's second pass read task-local labels |
|---|---|
| Original claim | `PepitaCredit` trained the current SplitMNIST task, because the runner masks the loss to that task's two classes. |
| Original metric | `_run_settling_phases` built the credit-facing `SystemState` with `y = local_y` (0/1). `PepitaCredit` derives `one_hot(y) − softmax(logits)` and its own CE from that state, so on task 1 (classes 2/3) it trained the task-0 logits. The masked loss was correct only for the exact-gradient credit, which reads the loss rather than `y`. |
| Audited procedure | TODO93 C1 defect probe: local at `lr=1e-2` scored 0.405 / 0.426 / 0.445 / 0.652 / 0.030 per task, while the same arm on task 1 alone (task-offset labels) reached 0.964 after 800 steps. The task-1 collapse named the label channel, not the algorithm. |
| Affected conclusions | Every continual cell routed through a credit that reads `state.y` (`PepitaCredit`, `LocalGoodnessCredit`, `LemmaCredit`): tasks 1–4 trained the wrong output classes. |
| Replacement metric | The credit-facing state carries the **global** class index (`local_y + task_start`); the masked loss still uses the local label. `test_credit_state_carries_the_global_task_target` fails if the offset is removed. `_finalize_output` now stores the loss it computes, so a FREE-only credit returns a finite loss instead of raising `TypeError`. |
| Status | corrected — local learns task 1 at 0.964 after the fix |
| Commit | this commit |

| Field | Correction 11 — C1's identity card named an inert knob |
|---|---|
| Original claim | The C1 box fixed `ewc_lambda = 1000.0`, so the plasticity ladder ran at one consolidation strength. |
| Original metric | `run_plasticity_ladder` passed `ewc_lambda=1000.0` into `CLConfig`; the `local` and `backprop` arms are built by `create_local_arm`/`create_backprop_arm`, whose signatures have no `ewc_lambda`, so no cell read the field. |
| Audited procedure | Read each factory signature against the box: only the C2 arms (`create_local_ewc_arm`, `create_backprop_ewc_arm`) accept `ewc_lambda`. The C1 record therefore named a knob its arms could not vary. |
| Affected conclusions | The C1 box only. The measured cells, the floor gate, and the promotion verdict are unchanged (the knob was inert, not silently varied). |
| Replacement metric | The plasticity box carries only the knob the arms read (LR); `_run_cell`'s `ewc_lambda` defaults to 0 and the C2 box carries the λ ladder. |
| Status | corrected — the box names only the knobs its arms read |
| Commit | this commit |

| Field | Correction 12 — the task-start anchor erased every EWC importance estimate |
|---|---|
| Original claim | `ewc`, `local_ewc` and `backprop_ewc` train under the declared diagonal importance `F = (params − baseline)² + damping`, so the C2 ladder over `ewc_lambda` varies consolidation strength. |
| Original metric | `ElasticConsolidationUpdate.consolidate` computed F at the end of each task (drift over the task), but `runner._apply_task_boundary_setup` also called `consolidate` at the start of every task with unchanged parameters. That second call recomputed `F = 0 + damping` and overwrote the drift importance before a single training step used it. Direct probe: `consolidate(p0)` → `consolidate(p1)` gives `F=0.011`; `consolidate(p1)` again gives `F=0.001` (= `fisher_damping`). |
| Affected conclusions | Every continual cell routed through an EWC arm: the plasticity rows (C1) are untouched (their arms do not read EWC), but the C2 retention ladder measured a uniform L2 anchor, not EWC. The first C2 launch's two cells (`results/t93_c1/consolidation.inert.cells.jsonl`) are kept as the defect probe, not as a ladder. |
| Replacement metric | `ElasticConsolidationUpdate.anchor(params)` moves `_old_params` and `_baseline` without recomputing F; the runner uses it at task starts and keeps `consolidate` for the end-of-task drift. `test_task_boundary_anchors_without_erasing_importance` fails if the runner calls `consolidate` at the boundary. |
| Status | corrected — the C2 ladder was restarted on the fixed mechanism |
| Commit | this commit |
| Field | Correction 13 — the chained stack's joint gradient measured depth, not bias |
|---|---|
| Original claim | The B1 screen reads the STE surrogate's bias as the gap's rise across 1/2/4/8 stacked hard selections. |
| Original metric | The first apparatus chained the gated blocks (`h, _ = block(h)`), i.e. the plan's operator stack. At depth 8 the reference's joint gradient fell to ~2e-3 and the STE's to ~1e-1, so the "gap" read 232 (and 3×10¹¹ at another LR): both surrogates vanish through stacked soft mixtures, so their ratio measures the depth of the stack, not the bias on one selection. The depth-8 arm also diverged at LR 1e-2 (end-task accuracy 0.244 = chance). |
| Audited procedure | Per-block gaps at `LR=1e-2`: 0.999 / 1.0 / 0.999 / 232.6 for depths 1/2/4/8, with reference norms 0.0 / 0.0 / 0.177 / 0.002. The rise was the denominator collapsing, not the numerator. |
| Affected conclusions | Any B1 cell measured on the chained stack. No gate was closed on those cells; they are the defect probe. |
| Replacement metric | The stack runs **parallel and averaged**: `depth` selections read the same trunk state, their outputs are averaged (so the forward scale is depth-invariant and the joint gradient does not vanish with depth), and the gap is read **per selection** and averaged over the stack. `test_ste_gradient_differs_from_its_soft_reference` fails if the treatment collapses to the plain relaxation. |
| Status | corrected — the ladder was rerun on the parallel averaged stack |
| Commit | this commit |

| Field | Correction 14 — the end-of-training probe measured the one-hot limit |
|---|---|
| Original claim | The STE gap is read after training, so each cell's budget is its final state. |
| Original metric | With `lr=1e-2` over 2 epochs, both gradients had vanished at the end: STE norm and reference norm printed 0.000 at every depth, and the relative gap was one-hot noise (0.99 / 323869 / 5.7e11). A ratio of two vanishing gradients measures saturation, not the surrogate's bias. |
| Audited procedure | Probe norms per optimiser step: 6.9e-2 (step 4), 4.6e-2 (8), 3.0e-2 (16), 2.8e-3 (32), 1.4e-3 (64) at depth 1, and 2.7e-2 → 4.2e-4 at depth 8. The probe batch at the end reads the saturated router. |
| Affected conclusions | Every B1 cell measured at the end of training. The first ladder (`results/t93_b1/defect_probe/`, `lr=1e-2`) is kept as the defect probe, never as a ladder. |
| Replacement metric | The gap is probed at declared optimiser steps (`PROBE_STEPS = 8/16/32`) and averaged over those probes; the points are in the box, so they are part of the measurement, not a search. `LR = 1e-3` keeps every depth a trained arm (end-task accuracy 1.0 at depth 8). |
| Status | corrected — the ladder probes the training path, not the saturated end |
| Commit | this commit |

| Field | Correction 15 — the probe split drew its own task |
|---|---|
| Original claim | The held-out accuracy ruler and the gradient probe read the same 4-class blob task the arm trains on. |
| Original metric | `_blobs(seed)` drew **new centers** from `seed`, so training (`seed`) and the held-out split (`seed + 1000`) were two different tasks. Measured: the arm memorized its training set (loss 1e-6 by step 15) and read 0.0 / 0.244 end-task accuracy on the other task. |
| Audited procedure | Probe with shared centers: `_blobs(task_seed, n, seed)` draws the centers from `task_seed` and the samples from `seed`. The same arm then reads 1.000 on the held-out split. |
| Affected conclusions | The B1 learning control (the floor gate). No gate was closed on the old numbers. |
| Replacement metric | The task's centers are part of the task (`task_seed`); only the samples move between the train and held-out splits. The learning control now reads 1.000 on every depth. |
| Status | corrected — the rulers and the gap read one task |
| Commit | this commit |

| Field | Correction 16 — one shared learning rate measured the estimator's tuning, not its kind |
|---|---|
| Original claim | The E1 atlas can compare every estimator kind at one matched compute box, so one shared learning rate is the fair baseline. |
| Original metric | A single LR (1e-3) collapsed the FA default to 0.093 (its feedback scale makes the update ~500× smaller than the exact gradient), while a single LR (1e-1) made the hybrid's local trunk diverge to 0.097 with an exploding loss. Both cells look like algorithm verdicts and are tuning coordinates. |
| Audited procedure | Four-arm E-lite at LR 1e-3/1e-2/1e-1: FA 0.106 / 0.260 / 0.819; hybrid 0.416 / 0.809 / 0.097. The ladder's best point is per arm: gradient 1e-2, FA 1e-1, PEPITA 1e-2, hybrid 1e-2. |
| Affected conclusions | Any E1 cell measured at a single shared LR. No table row was published from the single-LR runs; they were the defect probe and are superseded by this correction. |
| Replacement metric | Each arm gets a 3-point LR ladder at a disjoint ladder seed, a confirmation at its best point, and claim seeds 61/62/63 at that LR. The selected LR is part of the row; compute stays matched. |
| Status | corrected — the atlas was rerun with the per-arm viability ladder |
| Commit | this commit |

| Field | Correction 17 — one shared learning rate measured the substrate's tuning, not its substrate |
|---|---|
| Original claim | The D1 substrate ladder can compare ternary, memristive, and digital at one shared learning rate, so the substrate is the only varied axis. |
| Original metric | The pilot at 600 batches, settle 10, read ternary **0.381** at LR 1e-2 while digital and memristive read **0.909 / 0.905**; ternary's best point is 3e-3 (**0.802**). A shared LR would have refused the ternary substrate for the learning rate's defect. |
| Audited procedure | Per-arm LR ladder 1e-3/3e-3/1e-2 at settle 10: digital 0.858 / 0.896 / **0.914**; memristive 0.856 / 0.894 / **0.911**; ternary 0.801 / **0.835** / 0.728. The best points differ, and the moving-scale probe rejected a frozen-alpha "fix" (0.452 vs 0.381 at 1e-2, ≤2 pp where the cell is alive), so no code change was made. |
| Affected conclusions | The single-LR probe cells only. No D1 verdict was recorded from them; the pilot is the defect probe, and the corrections rows are the ladder. |
| Replacement metric | Each arm gets a 3-point LR ladder at a disjoint ladder seed (59) and the middle settle (10), its best point is frozen, then the settle ladder 5/10/20 runs at that LR with a confirmation seed (60). The selected LR is part of the row and compute stays matched. |
| Status | corrected — the ladder ran with the per-arm viability ladder |
| Commit | this commit |

| Field | Correction 18 — a store-all free pass measured a rule that never reads it |
|---|---|
| Original claim | The composed pilot's arm decomposition measured each credit's composed path, so the hybrid's 3249 MB activation set at L=32/B=8192/W=1024 was read as the hybrid's memory. It read 1.98× the checkpointed arm's 1637 MB, which would have closed the memory frontier (MPU1) on a memory disadvantage. |
| Original metric | `EpochResource.activations_mb` with `core/pipeline._run_train_step_tensor_impl` materialising `forward_pass(...)` before the credit ran, and doing so with autograd enabled although `HybridCredit.requires_autograd` is `False`; the FREE settle and the post-update free-metrics pass materialised two more store-all sets. |
| Audited procedure | At the lock point (L=32/W=512/B=4096) the hybrid's credit-level trunk is flat at 81 MB and its `compute_pseudo_gradient` reads only `x`/`y`, so the pipeline's activation set is a tensor the rule never reads. Measured after delegating the free pass: **210 MB against the checkpointed arm's 437 MB (0.48×)**; at the claim point the row moves 3249 → **611 MB** (0.37×), forward-equivalents 5.50 → 4.27, walltime 45.5 → 34.6 s. |
| Affected conclusions | The T6b blocker row and the pilot's hybrid row in `docs/BENCHMARKS.md` §2.4; any memory comparison read from the composed path before the fix. The stop rule ("hybrid loses at matched memory") was never invoked. |
| Replacement metric | A credit may own its free pass: `free_activations(substrate, geometry, x)` is optional on `CreditAssignment`, and the pipeline calls it instead of the pre-forward, the FREE settle, and the free-metrics settle. Locks: `test_memory_frontier.py::test_the_hybrid_owns_its_free_pass`, `::test_the_plain_arm_reads_the_pipeline_forward` (the tripwire's positive control), and `::test_the_hybrid_activation_set_is_half_the_checkpointed_arms`. |
| Status | corrected — the pilot's hybrid row was re-measured at the claim point |
| Commit | this commit |
