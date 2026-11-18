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

| Field | Correction 19 — the T6a refusal was measured at the OOM guard's box, not the claim's |
|---|---|
| Original claim | T6a's rung-2 screen refused the memory claim: at the registered L=4→8 point (W=512/B=2048/200 steps) the hybrid reads 0.167 against the 0.375 floor and 1.22× the checkpointed arm's activation set (103 vs 85 MB). |
| Original metric | `run_register` prices the claim at L=4→8 because the 4.5 GiB L=32 pilot exceeded the card; the memory ratio was therefore read where checkpointing has almost nothing to save. The claim's own ratio is stated at **L=32** (T6b's lock: 210 vs 437 MB, 0.48×). |
| Audited procedure | Same geometry, only depth moves (W=512/B=4096, seed 21, 4 steps): hybrid/ckpt = **1.25× (L=8), 0.72× (L=16), 0.48× (L=32)**; at B=2048: **1.22 / 0.75 / 0.53**. The root is cached, so the L=32 cell is 1.16 GB and fits. |
| Affected conclusions | T6a's `refuse` verdict only. T6b's lock and the pilot's `c` are untouched. |
| Replacement metric | The ratio is **depth-dependent** and must be stated at a declared depth (0.53× at L=32/B=2048, 0.48× at L=32/B=4096), never at L=4→8. |
| Status | corrected — T6a's verdict is `invalid-box`, not `refuse` |
| Commit | this commit |

| Field | Correction 20 — T6a's registered claim has an empty feasible set |
|---|---|
| Original claim | At one point, the hybrid reaches accuracy within δ of the checkpointed arm **and** uses ≤0.5× its activation bytes. |
| Original metric | The two conditions live in different depth regimes. Trainability ends at L=8 (plain 0.385 at 200 steps, LR 0.3); at L=16 and L=32 **every** arm reads 0.100, on both seeds, at B=2048 and B=4096. The memory ratio ≤0.5× needs L≈24–32. No declared point satisfies both, so the screen measured two different points and called it one refusal. |
| Audited procedure | `t93_t6a_box_triage.py`: L=16/B=2048/200 steps, seed 21 and 22, plain/ckpt/hybrid all 0.100 (chance, 10 classes); L=16/B=4096 the same. `depth_rung`'s L=8 0.385 is the last trainable depth at LR 0.3. |
| Affected conclusions | T6a's claim box and the W1 claim form. Not T6c's shelf (the stream-norm pass at 3e-2 trains L=32 at 0.314/0.326). |
| Replacement metric | The claim needs a **pass-carrying box**: L=32, `stream_norm=True` at LR 3e-2 (T6c's shelf), where the ratio is 0.53× and the arm is above chance; or the ratio curve itself as the claim, with accuracy read only at L=8. |
| Status | corrected — the claim was re-registered at the pass-carrying box and refused there (§2.14), so this is a box correction, not a verdict |
| Commit | this commit |

| Field | Correction 21 — the re-registration's box missed its own memory bar |
|---|---|
| Original claim | T6a's claim re-registers at L=32 with the stream-normalized pass at LR 3e-2, W=512/B=2048 (TODO93 v23, item 12b). |
| Original metric | The plan's own box triage reads the hybrid/checkpointed activation ratio **0.53× at L=32/B=2048** and **0.48× at L=32/B=4096** (4 steps, seed 21). A re-registration at B=2048 would therefore price a claim whose own measured arithmetic misses the 0.5× bar by 0.03×, whatever the screen reads. |
| Audited procedure | The box triage's six cells: 1.22/0.75/0.53 at B=2048 and 1.25/0.72/0.48 at B=4096 for L=8/16/32, same width and seed. The pass-carrying batch is 4096 (peak 1.12 GB, 17 % of the admission budget). |
| Affected conclusions | The re-registration's box only. The measured L=4→8 refusal (CORRECTION 19) and the empty feasible set (CORRECTION 20) are untouched. |
| Replacement metric | `RegistrationBox` states the point, the rung, the LR box, and its measured triage ratio; `build_registration` refuses a box whose own measured ratio misses the bar. The second box is L=32/B=4096 (`STREAM_BOX`), with its own committed path so it never overwrites the first. |
| Status | corrected — the claim re-registers at B=4096 |
| Commit | this commit |

| Field | Correction 22 — a chance-level learning control passed the relative floor |
|---|---|
| Original claim | The learning control passes when plain backprop at L=8 reaches the checkpointed arm's accuracy minus 1 pp. |
| Original metric | At a box where both arms sit at chance (0.100, 10 classes) the relative floor is 0.090, so the control passes degenerately: it reports "a memory number from a stack that does not learn is not a frontier" while the stack does not learn. |
| Audited procedure | The control's two arms at L=8, plain pass, the box's width/batch; the predicate is `backprop >= max(checkpointed − 0.01, 0.25)`. The registered control at 0.385 passes both; a chance pair (0.100 / 0.100) fails. |
| Affected conclusions | Only a control run at a chance box. T6a's registered control (0.385 vs 0.375) is unchanged. |
| Replacement metric | `learning_control_gate` is the one predicate, with `LEARNING_FLOOR = 0.25` as the task's declared learning floor. The control also stays the **plain** pass at the box's width/batch: a control for the claim's pass would share the defect it must catch. |
| Status | corrected — the control bars chance |
| Commit | this commit |

| Field | Correction 23 — the hybrid's box sensitivity was read against the control's cell |
|---|---|
| Original claim | The hybrid's accuracy is box-sensitive: 0.164 (W=64/B=128) and 0.167 (W=512/B=2048) against "the pilot's 0.419 (W=1024/B=8192)", while backprop moves 0.215 → 0.385 (BENCHMARKS §2.13). |
| Original metric | The 0.419 is the **plain backprop** arm's L=8 cell at the pilot's ladder (LR 0.3, W=1024/B=8192); the pilot's *hybrid* cell at the same point and LR is **0.163** (§2.4's ladder: `hybrid 0.100/0.163/0.100`). The comparison put one arm's cell against another arm's. |
| Audited procedure | The hybrid at L=8 reads 0.164 / 0.167 / 0.163 at W=64/B=128, W=512/B=2048, and W=1024/B=8192: flat across a 4× batch and a 16× width. Its parts at the same boxes read 0.215-0.419 (backprop) and 0.393-0.400 (local). |
| Affected conclusions | The "box-sensitive accuracy" suspicion only; the box triage's ratio table (1.22/0.75/0.53) is unaffected. |
| Replacement metric | The suspicion is the **level gap**, not the box: the composition reads ~0.16 at every box while both parts read 0.35-0.42, so the hybrid's own update is the mechanism and the trigger (T6d). |
| Status | corrected — the hybrid is box-insensitive; the gap is the update |
| Commit | this commit |

| Field | Correction 24 — the hybrid's gap is the split, not the trunk's update |
|---|---|
| Original claim | T6a₂'s refusal localized the 17 pp gap at "the hybrid's own update", and the trigger framed it as the trunk's knobs: `train_biases` and `feedback_scale` as the next rung (CORRECTION 23). |
| Original metric | The hybrid's accuracy against the checkpointed arm at one box while the trunk's knobs move. A 17 pp gap is equally consistent with the trunk's step, the trunk's rule, or the head's split; the knob grid cannot separate them. |
| Audited procedure | T6d at L=8/W=1024/B=8192, 200 steps, LR 0.3, seed 21 (confirmation 22): baseline 0.163/0.169; `train_biases` 0.167/0.175 (+0.5 pp); gamma 0.05/0.3/1.0 → 0.163/0.100/0.100; head-only (gamma=0) 0.149; **sibling `local`, the same trunk rule as a whole stack, 0.400/0.405/0.384**; reference `backprop+ckpt` 0.419/0.416 (floor 0.408). |
| Affected conclusions | T6a₂'s **mechanism attribution** only; its refusal at the pass-carrying box (memory 0.46× met, accuracy 17 pp below) stands, and CORRECTION 23's box-insensitivity stands — the level is the split's. |
| Replacement metric | The mechanism is the **split at the boundary**: the same rule trains as a whole stack and collapses only when a 2-layer exact-gradient head reads its boundary. The next rung is the split's position (`split_layer` on the last Linear, a readout-only head), not another trunk knob. The diagnostic also measures the hybrid's activation set at **1.06×** the reference's at L=8, so the pilot box cannot decide the memory half. |
| Status | corrected — T6d refused with the sibling control and the split as the mechanism |
| Commit | this commit |

| Field | Correction 25 — refusals are defect probes, not verdicts (capability-first) |
|---|---|
| Original claim | The plan recorded `refuse` / `⛔` verdicts for B1, D2, F1, T6a/T6a₂, T6c, and T6d — each from one box — and gated every queued primitive behind a measurement trigger produced by those verdicts (§19: "nothing is scheduled"). |
| Original metric | A screen or a pilot cell read as evidence about a mechanism, with "more primitives is not progress" making capability work a byproduct of the refusal loop. |
| Audited procedure | The plan's own §0.5 says *grow and stabilise the apparatus; do not adjudicate*, and the SEC loop says a low cell is a defect probe first. The sessions violated both: the queue could not move, and the primitives that would widen the system stayed in a table while the same boxes were measured again (T6a → T6a₂ → T6d). |
| Affected conclusions | The verdict words only, not the measurements. Every number stands at its box: 0.46× memory at L=32; hybrid 0.184/0.201; 0.163 against the sibling's 0.405; −0.31 pp at 2.09× walltime; STE gap 0.819→0.660; screen 0.669. |
| Replacement metric | **Defect probe**: a named defect candidate, the fix, and the capability it unlocks (TODO93 §0.6 defect ledger, §14 capability ledger). "Refused" is a box statement (infeasible, or over budget), never a mechanism verdict. The primitives are the work program, admitted by capability (§19). |
| Status | corrected — TODO93 is a capability program; no track is closed by a low cell |
| Commit | this commit |

| Field | Correction 26 — the split is priced; the direction is the fix queue |
|---|---|
| Original claim | T6d localized the 17 pp gap at "the split at the boundary" and framed the next rung as the split's position (`split_layer` on the last Linear) or a decoupled trunk learning rate (CORRECTION 24). |
| Original metric | A readout-only head and a trunk step were candidate mechanisms, but the refusal named "the split's position" without pricing it; a position that is never measured cannot be distinguished from a trunk whose update direction is wrong. |
| Audited procedure | T6e at L=8/W=1024/B=8192, 200 steps, LR 0.3, seeds 21/22: reference `backprop+ckpt` 0.419/0.416 (floor 0.408); baseline hybrid 0.163/0.169; **readout-only head (`split_layer`=14) 0.126/0.138 (−3.4 pp)**; **`trunk_lr` 0.3/1/3 → 0.105/0.126/0.103**; activation set 1.06× the reference's at L=8. |
| Affected conclusions | The split's position is no longer a candidate mechanism: moving the boundary to the last Linear **loses** 3.4 pp, and a decoupled trunk step buys nothing. The level is the trunk's **direction** (its first-order feedback matrix B and its geometry), not its step or its position. T6d's refusal stands; T6e's numbers stand as measurements. |
| Replacement metric | The fix queue is the trunk's **direction**: `learned_feedback` (a ridge-regressed B) or an orthogonal init at the readout split, or a residual/wider trunk. "The split's position" is retired as the trigger; the step and the position are priced at the pilot box. The measurement is a defect probe, not a verdict. |
| Status | corrected — T6e priced the position and the step; the direction is the fix queue |
| Commit | this commit |

| Field | Correction 27 — the direction is priced; the fix queue is the trunk's geometry |
|---|---|
| Original claim | T6e localized the 17 pp gap at the trunk's **direction** — the feedback matrix B or the trunk's geometry — and framed the next rung as `learned_feedback`'s ridge-regressed B, an orthogonal init at the readout split, or a residual/wider trunk (CORRECTION 26). |
| Original metric | The direction was named as the mechanism without pricing it, so "learned" and "orthogonal" were not distinguished from the geometry that the projection feeds. |
| Audited procedure | T6f at L=8/W=1024/B=8192, 200 steps, LR 0.3, seeds 21/22, confirmation 23, both directions at the registered draw's Frobenius norm: reference `backprop+ckpt` 0.419/0.416 (floor 0.408); draw 0.163/0.169; **orthogonal rotation 0.160/0.170 (−0.1 pp, sd 0.7 pp)**; **ridge-fitted B 0.145/0.144 (−2.1 pp, sd 0.03 pp at 1.17× walltime)**; confirmation 0.164; activations 515/516 MB (1.06× the reference's 485 MB). |
| Affected conclusions | The direction is priced at the box: the rotation is a no-op and the ridge fit is worse than the draw, so the input-level projection does not carry the head's δ into the trunk there. T6d's and T6e's numbers stand as measurements; nothing here closes the projection as a mechanism. |
| Replacement metric | The fix queue is the trunk's **geometry**: the hybrid's stack has one width and no residual on the projection's path, so the next variable is a residual or a wider trunk (12f), and the temporal axis is the next primitive. "The direction" is retired as the trigger; it is priced at the pilot box. |
| Status | corrected — T6f priced the direction; the fix queue is the trunk's geometry |
| Commit | this commit |

| Field | Correction 28 — the geometry is priced; the skip is the gain, the depth is the fix queue |
|---|---|
| Original claim | T6f localized the gap at the trunk's direction without pricing the geometry behind it, and its gate named the fix queue as "a residual trunk or a wider trunk" (CORRECTION 27). |
| Original metric | Two knobs named as candidate fixes, at one width and no residual, so "the geometry" could not be distinguished from the missing skip, and width was untested at its own price. |
| Audited procedure | T6g at L=8/B=8192, 200 steps, LR 0.3, seeds 21/22, confirmation 23: reference `backprop+ckpt` 0.419/0.416 (floor 0.408); registered hybrid 0.163/0.169; **residual skip 0.312/0.336 (+15.8 pp, sd 1.6 pp) at 1.06× activation bytes and 1.00× the weights**, confirmation 0.272; **wide trunk 0.199/0.210 (+3.9 pp) at 1.72× bytes and 3.33× weights**; **residual+wide 0.290/0.329 (+14.4 pp) at 1.72×**. |
| Affected conclusions | The geometry is priced: the skip is the mechanism's first real gain, width adds nothing, and the confirmation's seed spread (3.2σ) is wider than the screen's. The remaining 8.4 pp to the floor is the stack's **depth**, not another width. T6d/T6e/T6f stand as measurements. |
| Replacement metric | The fix queue is the trunk's **depth** (12g): a deeper residual stack (L=16, W=1024) and a third screen seed at the residual arm. "A wider trunk" is retired as the trigger; width is priced at the pilot box. |
| Status | corrected — T6g priced the geometry; the depth is the fix queue |
| Commit | this commit |

| Field | Correction 29 — a sequence task is schedulable, and the layout is one rule |
|---|---|
| Original claim | The temporal axis was wired (TODO93 §19 row 6): the geometry unrolled `x (time, batch, input)`, the loader yielded that layout, and the trainer folded it — so the axis was reachable. |
| Original metric | Reachability was measured from a fixture (`validation/temporal_ladder.py`), and the declared space counted a cell as legal from the task's shape and target kind alone. |
| Audited procedure | A smoke cell for `delayed_cue` from the declared space, and the space itself: `delayed_cue` was not in `SUPPORTED_TASKS` (no enriched row, so `geometry_hint` read `None` and the smoke trained the alphabetically-first geometry, `attention`), the space admitted 131,958 cells of which most could not read a time-major batch, it admitted a sequence credit on a flat task (which the composer then gave a time axis the loader does not emit), and the stability probe reshaped `(12, 64, 10)` into `(12, 640)` — a 768-row Jacobian at 25 s/cell, linearizing a state with no settled fixed point. |
| Affected conclusions | The axis's reachability, not its measurements: e-prop 0.355/0.356 vs floor 0.25 and the exact reference 0.285 stand. `batch_layout` is a task declaration (`DomainTask`, `TaskShape`) and `BATCH_LAYOUT_RULE` refuses both directions by name; the probe keeps the axis; the settle Jacobian refuses a time-major state. |
| Replacement metric | The declared space enumerates **7,938 cells** (all recurrent, all sequence credits) from 27,216 probes in 0.19 s; the smoke cell **PASSes** at val_acc 0.176 against bar 0.10 in 0.17 s; the flat tasks (iris, mnist) lose every sequence credit and their refusal names the rule. |
| Status | corrected — the axis is reachable from a run; the fixture was a rung-2 viability check, not the capability |
| Commit | this commit |
